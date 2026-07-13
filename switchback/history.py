"""
switchback.history: M8 scan logger.

Every successful availability month-fetch appends its raw cells to
SQLite (parks/history.sqlite, gitignored), tagged with a UTC scan
timestamp. The hook lives inside api.fetch_division_month, the single
choke point every caller passes through (GUI, CLI, solver, watch), so
the demand dataset grows on every run without anyone thinking about it.
Logging must never break a fetch: every operation is wrapped and fails
silent. Set SWITCHBACK_NO_HISTORY=1 to disable.

derive_demand turns the log into parks/demand.json, which the M5 crowd
term already knows how to read. v1 demand is a fullness-rate proxy
(share of observed future-date cells that were sold out); sellout
velocity and cancellation rates come later, once the log has weeks of
depth. The Permit Difficulty Index feeds on the same table.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("SWITCHBACK_HISTORY_PATH",
                         os.path.join(_ROOT, "parks", "history.sqlite"))
DISABLED = bool(os.environ.get("SWITCHBACK_NO_HISTORY"))
_conn = None


def set_db_path(path):
    global DB_PATH, _conn
    if _conn is not None:
        _conn.close()
    DB_PATH, _conn = path, None


def _db():
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        _conn = sqlite3.connect(DB_PATH)
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("""CREATE TABLE IF NOT EXISTS scans(
            permit_id TEXT, division_id TEXT, date TEXT,
            remaining INTEGER, total INTEGER, walkup INTEGER,
            hidden INTEGER, scanned_at TEXT)""")
        _conn.execute("CREATE INDEX IF NOT EXISTS ix_scans "
                      "ON scans(division_id, date, scanned_at)")
    return _conn


def record_month(permit_id, division_id, per_date):
    """Append one month-fetch. Returns rows written, 0 on any failure."""
    if DISABLED or not per_date:
        return 0
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [(str(permit_id), str(division_id), str(d)[:10],
             c.get("remaining"), c.get("total"),
             1 if c.get("walkup") else 0, 1 if c.get("hidden") else 0, ts)
            for d, c in per_date.items()]
    try:
        db = _db()
        db.executemany("INSERT INTO scans VALUES (?,?,?,?,?,?,?,?)", rows)
        db.commit()
        return len(rows)
    except Exception:
        return 0


def stats():
    try:
        db = _db()
        out = ["scan history: " + DB_PATH]
        for pid, n, lo, hi, scans in db.execute(
                "SELECT permit_id, COUNT(*), MIN(scanned_at), MAX(scanned_at),"
                " COUNT(DISTINCT scanned_at) FROM scans GROUP BY permit_id"):
            out.append(f"  permit {pid}: {n} cells across {scans} scan "
                       f"batches, {lo[:10]} to {hi[:10]}")
        if len(out) == 1:
            out.append("  empty; run any availability fetch and it starts")
        return "\n".join(out)
    except Exception as ex:
        return f"history unavailable: {ex}"


def _slug_map():
    import glob
    m = {}
    for p in glob.glob(os.path.join(_ROOT, "parks", "*.json")):
        if os.path.basename(p) in ("manual_coords.json", "ratings.json",
                                   "demand.json"):
            continue
        try:
            d = json.load(open(p))
            m[str(d.get("permit_id"))] = d.get("slug")
        except Exception:
            continue
    return m


def derive_pdi(min_samples=30, out_path=None):
    """v1 Permit Difficulty Index, 0 to 100 per camp: how hard is this
    permit to get. Fullness-driven today, with a weekend premium
    component once a camp has 10+ weekend observations; sellout velocity
    joins when the log spans weeks (it needs the same cell watched
    across days). Honest by design: camps below the sample floor are
    excluded rather than guessed."""
    out_path = out_path or os.path.join(_ROOT, "parks", "pdi.json")
    today = datetime.now(timezone.utc).date().isoformat()
    slugs = _slug_map()
    db = _db()
    pdi = {}
    q = ("SELECT permit_id, division_id, "
         "SUM(CASE WHEN remaining <= 0 THEN 1 ELSE 0 END), COUNT(*), "
         "SUM(CASE WHEN strftime('%w', date) IN ('0','6') "
         "AND remaining <= 0 THEN 1 ELSE 0 END), "
         "SUM(CASE WHEN strftime('%w', date) IN ('0','6') THEN 1 ELSE 0 END) "
         "FROM scans WHERE total > 0 AND hidden = 0 AND date >= ? "
         "GROUP BY permit_id, division_id")
    for pid, div, full, n, wfull, wn in db.execute(q, (today,)):
        if n < min_samples:
            continue
        slug = slugs.get(str(pid))
        if not slug:
            continue
        fullness = full / n
        entry = {"pdi": round(100 * fullness), "samples": n,
                 "fullness": round(fullness, 3),
                 "weekend_premium": (round(100 * (wfull / wn - fullness))
                                     if wn and wn >= 10 else None),
                 "sellout_velocity": None}
        pdi.setdefault(slug, {})[div] = entry
    with open(out_path, "w") as fh:
        json.dump(pdi, fh, indent=1)
    return out_path, sum(len(v) for v in pdi.values())


def derive_demand(out_path=None, min_samples=30):
    """Fullness-rate demand proxy per camp; only future-dated cells with
    real quota count. Returns (path, camps_written)."""
    out_path = out_path or os.path.join(_ROOT, "parks", "demand.json")
    today = datetime.now(timezone.utc).date().isoformat()
    slugs = _slug_map()
    db = _db()
    demand = {}
    q = ("SELECT permit_id, division_id, "
         "SUM(CASE WHEN remaining <= 0 THEN 1 ELSE 0 END), COUNT(*) "
         "FROM scans WHERE total > 0 AND hidden = 0 AND date >= ? "
         "GROUP BY permit_id, division_id")
    for pid, div, full, n in db.execute(q, (today,)):
        if n < min_samples:
            continue
        slug = slugs.get(str(pid))
        if not slug:
            continue
        demand.setdefault(slug, {})[div] = {
            "demand_pct": round(full / n, 3), "samples": n}
    with open(out_path, "w") as fh:
        json.dump(demand, fh, indent=1)
    return out_path, sum(len(v) for v in demand.values())
