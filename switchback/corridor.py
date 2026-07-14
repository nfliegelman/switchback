"""
switchback.corridor: long-trail corridors as areas. v2.24, built to the
design recorded in EXPERIMENTS.md on 2026-07-14.

The boundary is the trail centerline buffered 1.5 km per side (owner
default, standing veto open). Trails come from 0.3 degree tiles fetched
short-leash against the disk cache, deduped by way id, clipped to 3 km
of the centerline, then run through the same junction-graph machinery
every other area uses. Builds are RESUMABLE: each invocation fetches a
bounded number of missing tiles and only assembles when all are cached.
"""
import hashlib
import json
import math
import os
import time
import urllib.parse
import urllib.request

from .areas import (AREAS_DIR, _bridge_components, _junction_graph,
                    _prune_dust, _write_manifest)
from .geometry import ATTRIBUTION, CACHE_DIR, FOOT_WAYS

MIRRORS_SHORT = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
TILE_DEG = 0.3
CLIP_KM = 3.0
M_PER_DEG_LAT = 110540.0


def _atlas_row(slug):
    data = json.load(open("parks/atlas.json"))
    for r in data["rows"]:
        if r.get("slug") == slug and (r.get("boundary") or {}).get("src") \
                == "corridor":
            return r
    raise SystemExit(f"no corridor atlas row for {slug!r}")


def _scale(lat0):
    return M_PER_DEG_LAT * math.cos(math.radians(lat0)), M_PER_DEG_LAT


def _centerline(slug):
    path = os.path.join(CACHE_DIR, f"corridor_{slug}_centerline.json")
    if not os.path.exists(path):
        raise SystemExit(f"centerline cache missing: {path}; fetch the "
                         f"route relation first")
    d = json.load(open(path))
    return [[(p["lat"], p["lon"]) for p in w["geometry"]]
            for w in d["ways"] if len(w.get("geometry", [])) >= 2]


def _buffer_rings(lines, buffer_km):
    from shapely.geometry import MultiLineString
    from shapely.ops import unary_union
    lat0 = sum(p[0] for l in lines for p in l) / \
        sum(len(l) for l in lines)
    sx, sy = _scale(lat0)
    ml = MultiLineString([[(p[1] * sx, p[0] * sy) for p in l]
                          for l in lines])
    poly = unary_union(ml.buffer(buffer_km * 1000.0)).simplify(150.0)
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    rings = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            pts = [[round(y / sy, 5), round(x / sx, 5)]
                   for x, y in ring.coords]
            if len(pts) >= 12:
                rings.append(pts)
    return rings, poly, (sx, sy)


def _tiles(poly, sx, sy):
    from shapely.geometry import box
    minx, miny, maxx, maxy = poly.bounds
    w, s = minx / sx, miny / sy
    e, n = maxx / sx, maxy / sy
    out = []
    la = math.floor(s / TILE_DEG) * TILE_DEG
    while la < n:
        lo = math.floor(w / TILE_DEG) * TILE_DEG
        while lo < e:
            b = box(lo * sx, la * sy, (lo + TILE_DEG) * sx,
                    (la + TILE_DEG) * sy)
            if poly.intersects(b):
                out.append((round(la, 2), round(lo, 2),
                            round(la + TILE_DEG, 2),
                            round(lo + TILE_DEG, 2)))
            lo += TILE_DEG
        la += TILE_DEG
    return out


def _tile_cache(slug, t):
    """Tiles are pure bbox fetches, so the cache is slug-independent
    and corridors share coverage; the legacy per-slug path still reads."""
    key = hashlib.sha1(json.dumps(t).encode()).hexdigest()[:16]
    shared = os.path.join(CACHE_DIR, f"trails_tile_{key}.json")
    legacy = os.path.join(CACHE_DIR, f"trails_area_{slug}_{key}.json")
    return legacy if os.path.exists(legacy) and not         os.path.exists(shared) else shared


def _fetch_tile(t):
    s, w, n, e = t
    q = (f'[out:json][timeout:25];'
         f'way["highway"~"^({FOOT_WAYS})$"]({s},{w},{n},{e});out geom;')
    err = None
    for url in MIRRORS_SHORT:
        try:
            req = urllib.request.Request(
                url, data=urllib.parse.urlencode({"data": q}).encode(),
                headers={"User-Agent": "switchback-corridor"})
            with urllib.request.urlopen(req, timeout=35) as r:
                return json.load(r)
        except Exception as ex:
            err = str(ex)[:50]
            time.sleep(2)
    raise RuntimeError(f"tile {t} failed: {err}")


def build_corridor(slug, max_tiles=8):
    row = _atlas_row(slug)
    bspec = row["boundary"]
    lines = _centerline(slug)
    os.makedirs(CACHE_DIR, exist_ok=True)
    bcache = os.path.join(CACHE_DIR, f"bnd_{slug}.json")
    rings, poly, (sx, sy) = _buffer_rings(
        lines, bspec.get("buffer_km", 1.5))
    if not os.path.exists(bcache):
        json.dump(rings, open(bcache, "w"))
    tiles = _tiles(poly, sx, sy)
    missing = [t for t in tiles if not os.path.exists(_tile_cache(slug, t))]
    print(f"{row['name']}: {len(rings)} boundary ring(s), "
          f"{len(tiles)} tiles, {len(missing)} to fetch")
    fails = []
    for t in missing[:max_tiles]:
        try:
            data = _fetch_tile(t)
        except RuntimeError as ex:
            fails.append(str(ex))
            print(f"  tile {t}: TRANSIENT FAIL, will retry next run")
            continue
        json.dump(data, open(_tile_cache(slug, t), "w"))
        print(f"  tile {t}: {len(data.get('elements', []))} ways")
    missing = [t for t in tiles if not os.path.exists(_tile_cache(slug, t))]
    if missing:
        print(f"  RESUMABLE: {len(missing)} tiles remain; run again")
        return None

    from shapely.geometry import Point
    from shapely.prepared import prep
    clip = prep(poly.buffer((CLIP_KM - bspec.get("buffer_km", 1.5))
                            * 1000.0))
    seen, raw = set(), []
    for t in tiles:
        data = json.load(open(_tile_cache(slug, t)))
        for el in data.get("elements", []):
            if el["id"] in seen or not el.get("geometry"):
                continue
            seen.add(el["id"])
            pts = [(round(p["lat"], 5), round(p["lon"], 5))
                   for p in el["geometry"]]
            if len(pts) < 2:
                continue
            probe = pts[:: max(1, len(pts) // 6)]
            if any(clip.contains(Point(p[1] * sx, p[0] * sy))
                   for p in probe):
                raw.append(pts)
    nodes, edges = _junction_graph(raw)
    nodes, edges = _bridge_components(nodes, edges)
    nodes, edges = _prune_dust(nodes, edges)
    miles = sum(e[2] for e in edges)
    os.makedirs(AREAS_DIR, exist_ok=True)
    out = {"slug": slug, "name": row["name"], "manager": row["cat"],
           "permit": row["permit"], "attribution": ATTRIBUTION,
           "generated": time.strftime("%Y-%m-%d"),
           "corridor": {"relation": bspec.get("relation"),
                        "buffer_km": bspec.get("buffer_km", 1.5)},
           "boundary": rings, "nodes": nodes, "edges": edges,
           "stats": {"osm_ways": len(raw), "gov_added": 0,
                     "trail_miles": round(miles, 1),
                     "graph_nodes": len(nodes),
                     "graph_edges": len(edges)}}
    path = os.path.join(AREAS_DIR, f"{slug}.json")
    json.dump(out, open(path, "w"))
    kb = os.path.getsize(path) // 1024
    print(f"  {len(raw)} clipped ways, {miles:.0f} trail miles, {kb} KB "
          f"-> {path}")
    _write_manifest()
    return out
