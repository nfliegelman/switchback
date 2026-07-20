"""
switchback.frontcountry: curated frontcountry stays for the vertical
slice destinations.

Data lives in parks/frontcountry/<slug>.json, hand-curated per the
course correction: campground name, coordinates, reservation policy,
booking guidance, and drive minutes to the graph's entrance nodes.
This is deliberately NOT a national campground ingester; it exists so
a recommended trip can honestly account for the arrival night before
hiking and the recovery night after walking out.

Honesty rules: live frontcountry inventory is not fetched here, so a
reservation campground's availability is reported unknown, never
reservable; first-come campgrounds are first-come with no guarantee.
"""
import json
import os

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


def options_for_entrance(slug, entrance_node_id):
    """Curated campgrounds serving a graph entrance node, nearest
    first by drive minutes. Empty list when nothing is curated."""
    data = load_frontcountry(slug)
    if not data:
        return []
    out = []
    for cg in data.get("campgrounds", []):
        drives = cg.get("drive_minutes") or {}
        if entrance_node_id in drives:
            rec = dict(cg)
            rec["drive_min"] = drives[entrance_node_id]
            out.append(rec)
    out.sort(key=lambda c: c["drive_min"])
    return out
