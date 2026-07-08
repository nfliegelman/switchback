"""
switchback.extract: M1 park extractor.

Pulls a permit's full content and writes parks/<slug>.json with two node
lists the rest of the engine builds on:

  camps      every division, with normalized coordinates (0,0 becomes null),
             the default inclusion filter applied as a recorded flag (never a
             silent drop), and lake/trail parsing
  entrances  every trailhead with coordinates, parking flag, entry/exit
             flags, and division_ids. Caution: division_ids is park-specific
             PERMISSION data, not proximity (near-global at Glacier, sparse
             1:1 at Rainier). Graph edges come from mileage tables, not this.

Filters: divisions whose name or type contains "administrative",
"hitch rail", or "spike" are marked included=false with a reason. Nothing
is deleted; the solver simply respects the flag.
"""
import json
import os
import re
from datetime import datetime, timezone

from .api import get_permit_content, parse_description

EXCLUDE_PATTERNS = ("administrative", "hitch rail", "spike", "other accommodation",
                    "ranger station", "cabin", "lookout", "picnic", "auto cg",
                    "auto camp", "permit center", "chalet", "shelter",
                    "placeholder", "cdt site", " - winter", "camping zone")
_CODE_RE = re.compile(r"^[A-Z0-9]{2,5}$")


def _coord(v):
    """Payload coordinates: floats, strings, zeros, or garbage. 0,0 is null."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f != 0 else None


def _code(div):
    c = (div.get("code") or "").strip()
    if _CODE_RE.match(c):
        return c
    prefix = (div.get("name") or "").split(" - ")[0].strip()
    return prefix if _CODE_RE.match(prefix) else ""


def _exclusion(div):
    nm = (div.get("name") or "").lower()
    hay = f"{nm} {div.get('type') or ''}".lower()
    for pat in EXCLUDE_PATTERNS:
        if pat in hay:
            return pat
    if re.fullmatch(r"zone \d+( - .*)?", nm):
        return "undesignated zone"
    return None


def extract_park(permit_id, slug=None):
    payload, err = get_permit_content(permit_id)
    if err:
        raise RuntimeError(f"couldn't load permit {permit_id}: {err}")
    name = payload.get("name") or str(permit_id)
    slug = slug or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    camps = []
    for v in (payload.get("divisions") or {}).values():
        on_trail, water = parse_description(v.get("name"), v.get("description"))
        reason = _exclusion(v)
        camps.append({
            "id": str(v.get("id")),
            "code": _code(v),
            "name": v.get("name") or "",
            "type": v.get("type") or "",
            "district": v.get("district") or "",
            "lat": _coord(v.get("latitude")),
            "lon": _coord(v.get("longitude")),
            "size": v.get("size"),
            "is_group": "(Group Site)" in (v.get("name") or ""),
            "is_active": bool(v.get("is_active", True)),
            "is_hidden": bool(v.get("is_hidden", False)),
            "included": reason is None,
            "exclude_reason": reason,
            "water_lake_flag": water,
            "on_trail": on_trail,
        })
    camps.sort(key=lambda c: (c["type"], c["name"]))

    raw_ents = payload.get("entrances") or {}
    raw_ents = raw_ents.values() if isinstance(raw_ents, dict) else raw_ents
    entrances = []
    for e in raw_ents:
        ename = e.get("name") or ""
        entrances.append({
            "id": str(e.get("id")),
            "name": ename,
            "included": "field issue" not in ename.lower(),
            "lat": _coord(e.get("latitude")),
            "lon": _coord(e.get("longitude")),
            "has_parking": bool(e.get("has_parking")),
            "is_entry": bool(e.get("is_entry", True)),
            "is_exit": bool(e.get("is_exit", True)),
            "division_ids": [str(x) for x in (e.get("division_ids") or [])],
        })
    entrances.sort(key=lambda e: e["name"])

    counts = {
        "camps": len(camps),
        "camps_included": sum(c["included"] for c in camps),
        "camps_with_coords": sum(1 for c in camps if c["lat"] is not None),
        "entrances": len(entrances),
        "entrances_with_coords": sum(1 for e in entrances if e["lat"] is not None),
        "by_type": {},
        "excluded_by_reason": {},
    }
    for c in camps:
        counts["by_type"][c["type"]] = counts["by_type"].get(c["type"], 0) + 1
        if c["exclude_reason"]:
            r = c["exclude_reason"]
            counts["excluded_by_reason"][r] = counts["excluded_by_reason"].get(r, 0) + 1

    return {"schema": 1, "permit_id": str(permit_id), "name": name,
            "slug": slug, "extracted_at":
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "counts": counts, "camps": camps, "entrances": entrances}


def save_park(park, out_dir="parks"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{park['slug']}.json")
    with open(path, "w") as fh:
        json.dump(park, fh, indent=1)
    return path


def load_park(slug, out_dir="parks"):
    with open(os.path.join(out_dir, f"{slug}.json")) as fh:
        return json.load(fh)


def summary(park):
    c = park["counts"]
    lines = [f"{park['name']} (permit {park['permit_id']}) -> {park['slug']}.json",
             f"  camps: {c['camps']} total, {c['camps_included']} included, "
             f"{c['camps_with_coords']} with coordinates",
             f"  entrances: {c['entrances']} "
             f"({c['entrances_with_coords']} with coordinates)"]
    for t, n in sorted(c["by_type"].items()):
        lines.append(f"    {t or '(untyped)'}: {n}")
    if c["excluded_by_reason"]:
        ex = ", ".join(f"{k}: {v}" for k, v in sorted(c["excluded_by_reason"].items()))
        lines.append(f"  excluded ({ex})")
    return "\n".join(lines)
