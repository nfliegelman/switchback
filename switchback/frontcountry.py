"""
switchback.frontcountry: curated frontcountry stays for the vertical
slice destinations.

Data lives in parks/frontcountry/<slug>.json, hand-curated per the
course correction: campground name, coordinates, booking policy,
booking guidance, drive minutes to the graph's entrance nodes, and,
per the 2026-07-20 audit, temporal operational status: closures with
date ranges and reasons, when the policy was last checked, and when
it must be revalidated. This is deliberately NOT a national
campground ingester.

Honesty rules: live frontcountry inventory is not fetched here, so a
reservable campground's availability is reported unknown, never
available; first-come campgrounds are first-come with no guarantee;
and a campground closed for a requested date is NEVER offered as a
stay for that date.
"""
import json
import os
from datetime import date

FRONTCOUNTRY_DIR = os.path.join("parks", "frontcountry")


def load_frontcountry(slug):
    """The curated dataset for a destination, or None when the
    destination has no frontcountry curation yet."""
    p = os.path.join(FRONTCOUNTRY_DIR, f"{slug}.json")
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def closure_reason(cg, on_date):
    """The reason string if the campground is closed on that date,
    else None. Closures are [{from, through, reason}] with inclusive
    ISO date bounds; an open-ended closure may omit 'through'."""
    if on_date is None:
        return None
    iso = on_date.isoformat() if isinstance(on_date, date) else str(on_date)
    for c in cg.get("closures", []):
        lo = c.get("from", "0000-01-01")
        hi = c.get("through", "9999-12-31")
        if lo <= iso <= hi:
            return c.get("reason", "closed")
    return None


def options_for_entrance(slug, entrance_node_id, on_date=None,
                         allow_first_come=True):
    """(options, excluded) for a graph entrance node on a given night.

    options: curated campgrounds open that night and allowed by the
    first-come tolerance, nearest first by drive minutes.
    excluded: [{name, reason}] for campgrounds that serve this
    entrance but were ruled out, so the planner can explain honestly
    instead of silently having nothing."""
    data = load_frontcountry(slug)
    if not data:
        return [], []
    options, excluded = [], []
    for cg in data.get("campgrounds", []):
        drives = cg.get("drive_minutes") or {}
        if entrance_node_id not in drives:
            continue
        reason = closure_reason(cg, on_date)
        if reason:
            excluded.append({"name": cg["name"],
                             "reason": reason})
            continue
        if cg.get("policy") == "first_come" and not allow_first_come:
            excluded.append({"name": cg["name"],
                             "reason": "first-come only, and this search "
                                       "excludes first-come stays"})
            continue
        rec = dict(cg)
        rec["drive_min"] = drives[entrance_node_id]
        options.append(rec)
    options.sort(key=lambda c: c["drive_min"])
    return options, excluded
