"""
switchback.api: recreation.gov data layer.

Everything here is stdlib-only and UI-free. Moved verbatim from
switchback_gui.py at M0 (v1.1.0); the GUI imports from here now.
fetch_availability_rows is new: the shared row builder used by the CLI
today and the GUI trigger and web UI later.
"""
import json
import re as _re
import html as _html
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://www.recreation.gov"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
PLACEHOLDER_THRESHOLD = 100_000


# ============================ network layer ===============================
def _get_json(url, retries=3, timeout=30, backoff=0.6):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r), None
        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}"
        except Exception as e:
            last = str(e)
            time.sleep(backoff * (attempt + 1))
    return None, last


def search_permits(query, size=15):
    url = (f"{BASE}/api/search?q={urllib.parse.quote(query)}"
           f"&entity_type=permit&size={size}")
    data, err = _get_json(url)
    if err:
        return [], err
    out = []
    for r in data.get("results", []):
        if r.get("entity_type") != "permit":
            continue
        out.append({"permit_id": str(r.get("entity_id")),
                    "name": r.get("name") or "",
                    "park": r.get("parent_name", "") or ""})
    out.sort(key=lambda r: (0 if "permit" in r["name"].lower() else 1, r["name"]))
    return out, None


# --- description parsing: trail + lake info out of the HTML blurb ----------
_ON_TRAIL_RE = _re.compile(r"on the ([^.]+)\.", _re.I)
_ON_TRAIL_FALLBACK = _re.compile(r"on the ([^.]+?Trail[s]?)\b", _re.I)
_LAKE_RE = _re.compile(r"\b(lakes?|tarns?)\b", _re.I)


def _strip_html(s):
    s = _re.sub(r"<[^>]+>", " ", s or "")
    return _html.unescape(_re.sub(r"\s+", " ", s)).strip()


def parse_description(name, desc):
    text = _strip_html(desc)
    if not text:
        return "", ("Y" if _LAKE_RE.search(name or "") else "")
    m = _ON_TRAIL_RE.search(text) or _ON_TRAIL_FALLBACK.search(text)
    on_trail = m.group(1).strip().replace(" and ", "; ") if m else ""
    feature = _re.split(r"closest\s+trailhead", text, flags=_re.I)[0]
    water = "Y" if _LAKE_RE.search((name or "") + " " + feature) else ""
    return on_trail, water


def get_permit_content(permit_id):
    """Full permitcontent payload: divisions, entrances, and everything else.

    get_divisions below returns the GUI's slimmed view; the extractor (M1)
    and graph builder (M3) need the raw payload.
    """
    data, err = _get_json(f"{BASE}/api/permitcontent/{permit_id}")
    if err:
        return None, err
    return data.get("payload", {}) or {}, None


def get_divisions(permit_id):
    data, err = _get_json(f"{BASE}/api/permitcontent/{permit_id}")
    if err:
        return None, err
    payload = data.get("payload", {}) or {}
    divs = payload.get("divisions") or {}
    out = []
    for v in divs.values():
        on_trail, water = parse_description(v.get("name"), v.get("description"))
        out.append({"id": v.get("id"), "name": v.get("name"),
                    "type": v.get("type"),
                    "is_group": "(Group Site)" in (v.get("name") or ""),
                    "district": v.get("district") or "",
                    "on_trail": on_trail, "water_lake_flag": water})
    return {"permit_name": payload.get("name", ""), "divisions": out}, None


def fetch_division_month(permit_id, division_id, year, month):
    url = (f"{BASE}/api/permititinerary/{permit_id}/division/{division_id}"
           f"/availability/month?month={int(month)}&year={int(year)}"
           f"&commercial=false")
    data, err = _get_json(url)
    if err:
        return None, err
    payload = data.get("payload", {}) or {}
    per_date = {}
    for _qt, datemap in (payload.get("quota_type_maps") or {}).items():
        for d, cell in datemap.items():
            cur = per_date.setdefault(d, {"remaining": 0, "total": 0,
                                          "hidden": True, "walkup": False})
            cur["remaining"] += cell.get("remaining", 0)
            cur["total"] += cell.get("total", 0)
            cur["hidden"] = cur["hidden"] and cell.get("is_hidden", False)
            cur["walkup"] = cur["walkup"] or bool(cell.get("show_walkup"))
    if not per_date:
        for d, avail in (payload.get("bools") or {}).items():
            per_date[d] = {"remaining": 1 if avail else 0, "total": None,
                           "hidden": not avail, "walkup": False}
    return per_date, None


def classify_status(remaining, total, walkup, hidden):
    """Primary disposition of a camp-night. walkup is tracked separately too."""
    if hidden:
        return "Hidden"
    if remaining and remaining > 0:
        return "Reservable"
    if (total == 0 or total is None) and walkup:
        return "Walk-up only"
    if total and total > 0 and (remaining or 0) == 0:
        return "Full"
    if (total == 0 or total is None) and not walkup:
        return "Not released"
    return ""


def daterange(s, e):
    d = s
    while d <= e:
        yield d
        d += timedelta(days=1)


# ===================== shared availability row builder =====================
HEADERS = ["camp_or_zone", "type", "district", "date", "status",
           "remaining", "total", "percent_remaining", "walkup",
           "water_lake_flag", "on_trail"]


def fetch_availability_rows(permit_id, divisions, start, end,
                            only_available=False, workers=6, progress=None):
    """Fetch and classify availability for the given divisions and date range.

    Returns (rows, errors, njobs). Row tuple order matches HEADERS and the
    GUI's result table exactly. progress, if given, is called with a float
    0..1 after each completed request.
    """
    want_dates = [d.isoformat() for d in daterange(start, end)]
    yms = sorted({(d.year, d.month) for d in daterange(start, end)})
    jobs = [(d, y, m) for d in divisions for (y, m) in yms]

    results, errors, done = {}, 0, 0

    def work(job):
        d, y, m = job
        per, e = fetch_division_month(permit_id, d["id"], y, m)
        return d, y, m, per, e

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(work, j) for j in jobs]
        for f in as_completed(futs):
            d, y, m, per, e = f.result()
            done += 1
            if e:
                errors += 1
            else:
                results[(d["id"], y, m)] = per
            if progress:
                progress(done / max(len(jobs), 1))

    rows = []
    for d in divisions:
        for ds in want_dates:
            y, m = int(ds[:4]), int(ds[5:7])
            cell = results.get((d["id"], y, m), {}).get(ds)
            if cell is None:
                remaining = total = None; hidden = True; walkup = False
            else:
                remaining, total = cell.get("remaining"), cell.get("total")
                hidden = cell.get("hidden", False)
                walkup = cell.get("walkup", False)
            if remaining is not None and remaining >= PLACEHOLDER_THRESHOLD:
                continue
            status = classify_status(remaining, total, walkup, hidden)
            if status == "Hidden":
                continue
            if only_available and status not in ("Reservable", "Walk-up only"):
                continue
            pct = (remaining / total) if (remaining is not None and total) else None
            rows.append((d["name"], d["type"], d.get("district", ""), ds,
                         status, remaining, total, pct,
                         "Y" if walkup else "", d.get("water_lake_flag", ""),
                         d.get("on_trail", "")))
    rows.sort(key=lambda r: (r[1] or "", r[0] or "", r[3]))
    return rows, errors, len(jobs)
