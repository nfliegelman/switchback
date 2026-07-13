"""
switchback.areas: dispersed, permit-free landscapes as first-class map
citizens. v2.9, after the owner chose "all of Colorado."

A trail area has no rec.gov inventory and no camps (yet). What ships is
the official wilderness boundary from the USFS EDW service plus the
full trail network inside it, synthesized OSM-first with government
lines added only where OSM has nothing nearby, written to
docs/areas/<slug>.json for lazy loading by both map frontends.

Itineraries for these areas are a queued experiment (FUTURE.md): auto
generated campsite candidates from named lakes and basins, synthetic
always-open availability through the existing overlay machinery.
"""
import json
import os
import time
import urllib.parse
import urllib.request

from .geometry import (ATTRIBUTION, CACHE_DIR, TrailNet, _geojson_to_elements,
                       _haversine_m, _overpass_once, fetch_gov, simplify)

BOUNDARY_URL = ("https://apps.fs.usda.gov/arcx/rest/services/EDW/"
                "EDW_Wilderness_01/MapServer/0/query")
AREAS_DIR = os.path.join("docs", "areas")
MIRRORS_FLOOR = 25
GOV_ADD_M = 120
MIN_WAY_MI = 0.15


def _atlas_row(slug):
    data = json.load(open("parks/colorado_atlas.json"))
    for r in data["rows"]:
        if r.get("slug") == slug and r.get("official"):
            return r
    raise SystemExit(f"no atlas entry with an official wilderness name "
                     f"for slug {slug!r}")


def fetch_boundary(official_name, slug):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"bnd_{slug}.json")
    if os.path.exists(cache):
        with open(cache) as fh:
            return json.load(fh)
    params = {"f": "geojson", "where": f"WILDERNESSNAME='{official_name}'",
              "outFields": "WILDERNESSNAME", "returnGeometry": "true",
              "outSR": "4326", "geometryPrecision": "5"}
    req = urllib.request.Request(
        BOUNDARY_URL + "?" + urllib.parse.urlencode(params),
        headers={"User-Agent": "switchback-areas"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    feats = data.get("features", [])
    if not feats:
        raise SystemExit(f"boundary service returned nothing for "
                         f"{official_name!r}")
    geo = feats[0]["geometry"]
    polys = [geo["coordinates"]] if geo["type"] == "Polygon" \
        else geo["coordinates"]
    rings = []
    for poly in polys:
        for ring in poly:
            pts = [(c[1], c[0]) for c in ring]
            spts = simplify(pts, tol_m=150.0)
            if len(spts) >= 12:
                rings.append([[round(p[0], 5), round(p[1], 5)]
                              for p in spts])
    with open(cache, "w") as fh:
        json.dump(rings, fh)
    return rings


def _fetch_area_osm(bbox, slug):
    """Mirror-walked OSM fetch for a display layer. No graph nodes exist
    to coverage-validate against, so the guard is a way-count floor plus
    the government layer as an independent complement."""
    import hashlib
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = hashlib.sha1(json.dumps(bbox).encode()).hexdigest()[:16]
    cache = os.path.join(CACHE_DIR, f"trails_area_{slug}_{key}.json")
    if os.path.exists(cache):
        with open(cache) as fh:
            return json.load(fh)
    from .geometry import MIRRORS
    last = None
    for attempt, url in enumerate(MIRRORS * 2):
        try:
            data = _overpass_once(url, bbox)
            if len(data.get("elements", [])) < MIRRORS_FLOOR:
                last = f"only {len(data.get('elements', []))} ways"
                time.sleep(6)
                continue
            with open(cache, "w") as fh:
                json.dump(data, fh)
            return data
        except Exception as ex:
            last = ex
            time.sleep(8 + attempt * 6)
    raise RuntimeError(f"OSM mirrors failed for {slug}: {last}")


def _polyline_mi(pts):
    return sum(_haversine_m(a, b) for a, b in zip(pts, pts[1:])) / 1609.34


def build_area(slug):
    row = _atlas_row(slug)
    rings = fetch_boundary(row["official"], slug)
    lats = [p[0] for r in rings for p in r]
    lons = [p[1] for r in rings for p in r]
    pad = 0.02
    bbox = (min(lats) - pad, min(lons) - pad, max(lats) + pad, max(lons) + pad)
    print(f"{row['official']}: boundary {len(rings)} ring(s), bbox "
          f"{tuple(round(x, 3) for x in bbox)}")

    osm = _fetch_area_osm(bbox, slug)
    net = TrailNet(osm)
    trails, miles = [], 0.0
    for el in osm.get("elements", []):
        pts = [(p["lat"], p["lon"]) for p in el.get("geometry") or []]
        if len(pts) < 2:
            continue
        spts = simplify(pts, tol_m=20.0)
        mi = _polyline_mi(spts)
        if mi < MIN_WAY_MI:
            continue
        trails.append([[round(p[0], 5), round(p[1], 5)] for p in spts])
        miles += mi
    osm_count = len(trails)

    gov_els, gov_src = fetch_gov(bbox, f"area_{slug}")
    gov_added = 0
    for el in gov_els:
        pts = [(p["lat"], p["lon"]) for p in el["geometry"]]
        if len(pts) < 2:
            continue
        samples = [pts[0], pts[len(pts) // 2], pts[-1]]
        if any(net.snap_candidates(p, GOV_ADD_M, k=1) for p in samples):
            continue
        spts = simplify(pts, tol_m=20.0)
        mi = _polyline_mi(spts)
        if mi < MIN_WAY_MI:
            continue
        trails.append([[round(p[0], 5), round(p[1], 5)] for p in spts])
        miles += mi
        gov_added += 1

    os.makedirs(AREAS_DIR, exist_ok=True)
    out = {"slug": slug, "name": row["name"], "manager": row["cat"],
           "permit": row["permit"], "attribution": ATTRIBUTION,
           "generated": time.strftime("%Y-%m-%d"),
           "boundary": rings, "trails": trails,
           "stats": {"osm_ways": osm_count, "gov_added": gov_added,
                     "trail_miles": round(miles, 1)}}
    path = os.path.join(AREAS_DIR, f"{slug}.json")
    with open(path, "w") as fh:
        json.dump(out, fh)
    kb = os.path.getsize(path) // 1024
    print(f"  {osm_count} OSM ways + {gov_added} gov-only additions, "
          f"{miles:.0f} trail miles, {kb} KB -> {path}")
    _write_manifest()
    return out


def _write_manifest():
    import glob
    entries = []
    for p in sorted(glob.glob(os.path.join(AREAS_DIR, "*.json"))):
        if p.endswith("index.json"):
            continue
        d = json.load(open(p))
        entries.append({"slug": d["slug"], "name": d["name"],
                        "permit": d["permit"],
                        "trail_miles": d["stats"]["trail_miles"]})
    with open(os.path.join(AREAS_DIR, "index.json"), "w") as fh:
        json.dump({"areas": entries}, fh)
