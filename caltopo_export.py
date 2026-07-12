#!/usr/bin/env python3
"""
caltopo_export.py: Switchback's CalTopo feed, v0 of the map layer.

Pulls a recreation.gov permit's camps/zones and trailhead entrances and writes
a GeoJSON file you can import straight into CalTopo (Import > pick the file).
Colors: green trailside camps, orange cross-country zones, red alpine,
gray winter, blue trailheads. Descriptions carry type, district, and parking.

Usage:
    python caltopo_export.py            (defaults to Mount Rainier, 4675317)
    python caltopo_export.py 4675321    (any other permit id)
"""
import json
import sys
import urllib.request

UA = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/124.0.0.0 Safari/537.36"),
      "Accept": "application/json"}

TYPE_COLORS = {
    "Trailside Camps": "#2E8B57",
    "Cross-Country Zones": "#E67E22",
    "Alpine Camps and Zones": "#C0392B",
    "Winter Camps and Zones": "#7F8C8D",
}
TRAILHEAD_COLOR = "#1F6AA5"


def _f(val):
    try:
        v = float(val)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def _engine_extras(permit_id, window):
    """Rating properties (and optional open-night counts) when this permit
    has a park dataset plus a route graph. Returns {division_id: props}."""
    import glob
    import os
    slug = None
    for p in glob.glob(os.path.join("parks", "*.json")):
        if os.path.basename(p) in ("manual_coords.json", "ratings.json",
                                   "demand.json"):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if str(d.get("permit_id")) == str(permit_id):
            slug = d.get("slug")
            break
    if not slug:
        return {}, None
    try:
        from switchback.graph import Graph
        from switchback.scoring import Scorer
        g = Graph(slug)
        sc = Scorer(g)
    except Exception as ex:
        print(f"note: engine extras unavailable for {slug}: {ex}")
        return {}, None
    extras = {}
    for cid in sc._camp_feats:
        card = sc.camp_card(cid)
        extras[cid] = {"rating": card["rating"],
                       "rating_percentile": (round(card["pct"], 2)
                                             if card["pct"] is not None else None)}
    if window:
        from datetime import date
        from switchback.solver import fetch_availability
        start, end = (date.fromisoformat(window[0]),
                      date.fromisoformat(window[1]))
        print(f"fetching availability {start} to {end} for open-night counts...")
        av = fetch_availability(str(permit_id), list(extras), start, end)
        key = f"open_nights_{start}_{end}"
        for cid in extras:
            extras[cid][key] = sum(1 for v in av.get(cid, {}).values() if v >= 1)
    return extras, slug


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    window = None
    if "--window" in sys.argv:
        i = sys.argv.index("--window")
        window = (sys.argv[i + 1], sys.argv[i + 2])
    permit_id = args[0] if args else "4675317"
    url = f"https://www.recreation.gov/api/permitcontent/{permit_id}"
    req = urllib.request.Request(url, headers=UA)
    payload = json.load(urllib.request.urlopen(req, timeout=30)).get("payload", {}) or {}

    features = []
    skipped = 0

    extras, slug = _engine_extras(permit_id, window)
    if slug:
        print(f"engine extras attached from parks/{slug}.json")

    for d in (payload.get("divisions") or {}).values():
        lat, lon = _f(d.get("latitude")), _f(d.get("longitude"))
        if lat is None or lon is None:
            skipped += 1
            continue
        dtype = d.get("type") or "Camp"
        name = d.get("name") or "(unnamed)"
        desc = f"{dtype} | {d.get('district') or 'no district'}"
        ex = extras.get(str(d.get("id")))
        if ex:
            desc += f" | rating {ex['rating']} (p{ex['rating_percentile']})"
            for k, v in ex.items():
                if k.startswith("open_nights_"):
                    desc += f" | {k.replace('_', ' ')}: {v}"
        if d.get("is_active") is False:
            desc += " | INACTIVE"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "title": name,
                "description": desc,
                "marker-color": TYPE_COLORS.get(dtype, "#2E8B57"),
                "marker-symbol": "point",
            },
        })

    for e in (payload.get("entrances") or {}).values() if isinstance(payload.get("entrances"), dict) \
            else (payload.get("entrances") or []):
        lat, lon = _f(e.get("latitude")), _f(e.get("longitude"))
        if lat is None or lon is None:
            skipped += 1
            continue
        parking = "parking: yes" if e.get("has_parking") else "parking: unknown/none"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "title": e.get("name") or "(trailhead)",
                "description": f"Trailhead | {parking}",
                "marker-color": TRAILHEAD_COLOR,
                "marker-symbol": "point",
            },
        })

    safe = "".join(c if c.isalnum() else "_" for c in (payload.get("name") or permit_id))[:40]
    out = f"caltopo_{safe}.geojson"
    with open(out, "w") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)
    print(f"{out}: {len(features)} features written, {skipped} skipped (no coords)")


if __name__ == "__main__":
    main()
