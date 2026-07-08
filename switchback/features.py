"""
switchback.features: M2 coordinate fill and feature tags.

Coordinate fallback chain per ROADMAP: payload > NPS GIS > OSM name-join >
manual (parks/manual_coords.json). This build implements payload, OSM, and
manual; an NPS GIS pass is a recorded upgrade path. Water joins use OSM
water geometry (USGS NHD is the recorded upgrade); elevation uses the
Open-Meteo elevation API (Copernicus GLO-90 terrain), batched 100 points
per request. trailhead_dist_mi_straightline is a placeholder that M3's
graph replaces with trail distance.

CLI: python -m switchback features <slug> [--bbox S,W,N,E]
"""
import difflib
import json
import math
import os
import re
import urllib.parse
import urllib.request

from .extract import load_park, save_park

BBOXES = {
    "rainier": (46.70, -122.05, 47.06, -121.35),
    "glacier": (48.20, -114.60, 49.01, -113.15),
}
OVERPASS = "https://overpass-api.de/api/interpreter"
ELEV_API = "https://api.open-meteo.com/v1/elevation"
UA = {"User-Agent": "switchback/1.3 (personal permit planning tool)"}
LAKE_M, CREEK_M = 400, 200
MANUAL_PATH = os.path.join("parks", "manual_coords.json")

_STOP = {"campground", "camp", "camps", "backcountry", "trailhead", "trail",
         "site", "sites", "the", "area", "no", "campfires"}
# foot, head, lower, upper stay: they disambiguate paired camps


# ------------------------------ geometry ---------------------------------
def _mxy(lat, lon, lat0):
    return (lon * 111320 * math.cos(math.radians(lat0)), lat * 111320)


def haversine_mi(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def _seg_dist(p, a, b):
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _line_dist_m(pt, coords, lat0):
    p = _mxy(*pt, lat0)
    xs = [_mxy(c[0], c[1], lat0) for c in coords]
    return min(_seg_dist(p, xs[i], xs[i + 1]) for i in range(len(xs) - 1))


def _inside(pt, coords, lat0):
    p = _mxy(*pt, lat0)
    xs = [_mxy(c[0], c[1], lat0) for c in coords]
    n, inside = len(xs), False
    for i in range(n):
        (x1, y1), (x2, y2) = xs[i], xs[(i + 1) % n]
        if (y1 > p[1]) != (y2 > p[1]):
            if p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside


def _area_acres(coords, lat0):
    xs = [_mxy(c[0], c[1], lat0) for c in coords]
    s = sum(xs[i][0] * xs[(i + 1) % len(xs)][1]
            - xs[(i + 1) % len(xs)][0] * xs[i][1] for i in range(len(xs)))
    return abs(s) / 2 / 4046.86


# ------------------------------ sources ----------------------------------
MIRRORS = ("https://overpass-api.de/api/interpreter",
           "https://overpass.kumi.systems/api/interpreter",
           "https://lz4.overpass-api.de/api/interpreter")


CACHE_DIR = os.path.join("parks", ".osm_cache")


_REQ_N = [0]


def _overpass(query, tries=3):
    import time, hashlib
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = os.path.join(CACHE_DIR, hashlib.md5(query.encode()).hexdigest() + ".json")
    if os.path.exists(key):
        with open(key) as fh:
            return json.load(fh)
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    _REQ_N[0] += 1
    for i in range(tries):
        url = MIRRORS[(_REQ_N[0] + i) % len(MIRRORS)]
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                els = json.load(r).get("elements", [])
            with open(key, "w") as fh:
                json.dump(els, fh)
            return els
        except Exception as e:
            last = e
            time.sleep(8 if i == 0 else 20)
    raise RuntimeError(f"overpass failed after {tries} mirrors: {last}")


def _tiles(bbox, n):
    s, w, no, e = bbox
    dy, dx = (no - s) / n, (e - w) / n
    for i in range(n):
        for j in range(n):
            yield (s + i * dy, w + j * dx, s + (i + 1) * dy, w + (j + 1) * dx)


def _tiled(selector, bbox, n):
    seen, out = set(), []
    for t in _tiles(bbox, n):
        b = f"({t[0]:.4f},{t[1]:.4f},{t[2]:.4f},{t[3]:.4f})"
        for el in _overpass(f'[out:json][timeout:150];{selector}{b};out geom;'):
            key = (el.get("type"), el.get("id"))
            if key not in seen:
                seen.add(key); out.append(el)
    return out


def _query_plan(bbox):
    s, w, n, e = bbox
    b = f"({s},{w},{n},{e})"
    grid = 3 if (n - s) * (e - w) > 0.5 else 2
    fine = grid + 2 if grid >= 3 else grid
    water_sel = 'way["natural"="water"]["water"!~"^(river|canal|stream|riverbank)$"]'
    plan = [("camps", f'[out:json][timeout:150];nwr["tourism"="camp_site"]{b};out center;'),
            ("trailheads", f'[out:json][timeout:150];nwr["highway"="trailhead"]{b};out center;')]
    for t in _tiles(bbox, fine):
        tb = f"({t[0]:.4f},{t[1]:.4f},{t[2]:.4f},{t[3]:.4f})"
        plan.append(("water", f'[out:json][timeout:120];{water_sel}{tb};out geom;'))
    for t in _tiles(bbox, fine):
        tb = f"({t[0]:.4f},{t[1]:.4f},{t[2]:.4f},{t[3]:.4f})"
        plan.append(("creeks", f'[out:json][timeout:120];way["waterway"~"^(stream|river)$"]{tb};out geom;'))
    return plan


def _cached(query):
    import hashlib
    return os.path.exists(os.path.join(
        CACHE_DIR, hashlib.md5(query.encode()).hexdigest() + ".json"))


NHD_BASE = "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer"
_NHD_LAYERS = {}


def _http_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def _cached_json(url):
    import hashlib
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = os.path.join(CACHE_DIR, hashlib.md5(url.encode()).hexdigest() + ".json")
    if os.path.exists(key):
        with open(key) as fh:
            return json.load(fh)
    data = _http_json(url)
    with open(key, "w") as fh:
        json.dump(data, fh)
    return data


def _nhd_layer(name_contains):
    if not _NHD_LAYERS:
        svc = _http_json(NHD_BASE + "?f=json")
        for lyr in svc.get("layers", []):
            _NHD_LAYERS[lyr["name"].lower()] = lyr["id"]
    for n, i in _NHD_LAYERS.items():
        if name_contains in n and "label" not in n:
            return i
    raise RuntimeError(f"NHD layer {name_contains!r} not found")


def _nhd_query(layer_id, bbox, where):
    s, w, n, e = bbox
    feats, offset = [], 0
    while True:
        params = urllib.parse.urlencode({
            "where": where, "geometry": f"{w},{s},{e},{n}",
            "geometryType": "esriGeometryEnvelope", "inSR": 4326, "outSR": 4326,
            "spatialRel": "esriSpatialRelIntersects", "outFields": "gnis_name",
            "returnGeometry": "true", "geometryPrecision": 5, "f": "geojson",
            "resultRecordCount": 1000, "resultOffset": offset})
        page = _cached_json(f"{NHD_BASE}/{layer_id}/query?{params}")
        if "features" not in page:
            raise RuntimeError(f"NHD error: {str(page)[:120]}")
        got = page["features"]
        feats.extend(got)
        if len(got) < 1000:
            return feats
        offset += 1000


def _rings(geom):
    t, c = geom.get("type"), geom.get("coordinates", [])
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in c]
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return list(c)
    return []


def fetch_hydro_nhd(bbox):
    """Returns (lakes [(name, ring)], streams [line]) with (lat, lon) coords."""
    wb, fl = _nhd_layer("waterbody"), _nhd_layer("flowline")
    try:
        wfeats = _nhd_query(wb, bbox, "ftype IN (390,436)")
    except RuntimeError:
        wfeats = _nhd_query(wb, bbox, "1=1")
    try:
        sfeats = _nhd_query(fl, bbox, "ftype IN (460)")
    except RuntimeError:
        sfeats = _nhd_query(fl, bbox, "1=1")
    lakes, streams = [], []
    for f in wfeats:
        props = {k.lower(): v for k, v in (f.get("properties") or {}).items()}
        nm = (props.get("gnis_name") or "").strip() or None
        for ring in _rings(f.get("geometry") or {}):
            lakes.append((nm, [(p[1], p[0]) for p in ring]))
    for f in sfeats:
        for line in _rings(f.get("geometry") or {}):
            streams.append([(p[1], p[0]) for p in line])
    return lakes, streams


def prefetch(bbox, budget_s=300):
    """Fill the OSM cache in a time box. Returns (done, total)."""
    import time
    t0 = time.time()
    plan = _query_plan(bbox)
    done = sum(1 for _, q in plan if _cached(q))
    for label, q in plan:
        if _cached(q):
            continue
        if time.time() - t0 > budget_s:
            break
        try:
            n = len(_overpass(q))
        except RuntimeError:
            print(f"  skip {label} (server busy)", flush=True)
            continue
        done += 1
        print(f"  cached {label} ({n} elements) [{done}/{len(plan)}]", flush=True)
        time.sleep(2.5)
    return done, len(plan)


def fetch_osm(bbox):
    results = {"camps": [], "trailheads": [], "water": [], "creeks": []}
    seen = set()
    for label, q in _query_plan(bbox):
        for el in _overpass(q):
            key = (label, el.get("type"), el.get("id"))
            if key not in seen:
                seen.add(key)
                results[label].append(el)
    return (results["camps"], results["trailheads"],
            results["water"], results["creeks"])


def _pt(el):
    if "lat" in el:
        return (el["lat"], el["lon"])
    c = el.get("center")
    return (c["lat"], c["lon"]) if c else None


def elevations_ft(points):
    """Batched terrain lookups, 100 points per request."""
    out = []
    for i in range(0, len(points), 100):
        chunk = points[i:i + 100]
        url = (f"{ELEV_API}?latitude={','.join(f'{p[0]:.5f}' for p in chunk)}"
               f"&longitude={','.join(f'{p[1]:.5f}' for p in chunk)}")
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            meters = json.load(r)["elevation"]
        out.extend(round(m * 3.28084) if m is not None else None for m in meters)
    return out


# ------------------------------ matching ---------------------------------
def norm(name):
    s = (name or "").lower()
    s = re.sub(r"^[a-z0-9]{2,5} - ", "", s)          # strip "ELF - " codes
    s = re.sub(r"\(.*?\)", " ", s)                    # drop parentheticals
    s = s.replace("/", " ").replace("-", " ").replace("'", "")
    s = s.replace("trail head", "trailhead")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in _STOP]
    return " ".join(toks)


def match_names(targets, candidates):
    """targets: {id: name}. candidates: [(name, (lat, lon))].
    Returns ({id: (lat, lon, matched_name)}, [unmatched names])."""
    cnorm = {}
    for name, pt in candidates:
        cnorm.setdefault(norm(name), []).append((name, pt))
    matched, unmatched = {}, []
    keys = list(cnorm)
    for tid, tname in targets.items():
        tn = norm(tname)
        if not tn:
            unmatched.append(tname); continue
        if tn in cnorm:
            name, pt = cnorm[tn][0]
            matched[tid] = (pt[0], pt[1], name); continue
        tset = set(tn.split())
        subs = [k for k in keys
                if (tset <= set(k.split()) or set(k.split()) <= tset)
                and len(tset & set(k.split())) >= 2]
        if len(subs) == 1:
            name, pt = cnorm[subs[0]][0]
            matched[tid] = (pt[0], pt[1], name); continue
        scored = sorted(((difflib.SequenceMatcher(None, tn, k).ratio(), k)
                         for k in keys), reverse=True)
        if scored and scored[0][0] >= 0.90 and \
                (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.05):
            name, pt = cnorm[scored[0][1]][0]
            matched[tid] = (pt[0], pt[1], name)
        else:
            unmatched.append(tname)
    return matched, unmatched


# ------------------------------ pipeline ---------------------------------
def _load_manual(slug):
    try:
        with open(MANUAL_PATH) as fh:
            return json.load(fh).get(slug, {})
    except (OSError, ValueError):
        return {}


def annotate(slug, bbox=None):
    park = load_park(slug)
    bbox = bbox or BBOXES.get(slug)
    if not bbox:
        raise SystemExit(f"no bbox known for {slug}; pass --bbox S,W,N,E")
    lat0 = (bbox[0] + bbox[2]) / 2
    manual = _load_manual(slug)

    plan = _query_plan(bbox)
    camps_osm = _overpass(plan[0][1])
    ths_osm = _overpass(plan[1][1])
    osm_camp_cands = [(el["tags"]["name"], _pt(el)) for el in camps_osm
                      if el.get("tags", {}).get("name") and _pt(el)]
    osm_th_cands = [(el["tags"]["name"], _pt(el)) for el in ths_osm
                    if el.get("tags", {}).get("name") and _pt(el)]
    try:
        lakes_raw, streams_raw = fetch_hydro_nhd(bbox)
        hydro_src = "usgs-nhd"
    except Exception as ex:
        print(f"  NHD unavailable ({ex}); falling back to OSM water")
        water = [el for lbl, q in plan if lbl == "water" for el in _overpass(q)]
        creeks = [el for lbl, q in plan if lbl == "creeks" for el in _overpass(q)]
        lakes_raw = [((w.get("tags") or {}).get("name"),
                      [(g["lat"], g["lon"]) for g in w.get("geometry", [])])
                     for w in water]
        streams_raw = [[(g["lat"], g["lon"]) for g in w.get("geometry", [])]
                       for w in creeks]
        hydro_src = "osm"

    # 1. coordinates: payload > osm > manual
    need_c = {c["id"]: c["name"] for c in park["camps"]
              if c["lat"] is None and c["included"]}
    got_c, un_c = match_names(need_c, osm_camp_cands)
    need_e = {e["id"]: e["name"] for e in park["entrances"]
              if e["lat"] is None and e.get("included", True)}
    got_e, un_e = match_names(need_e, osm_th_cands + osm_camp_cands)

    for c in park["camps"]:
        if c["lat"] is not None and "coord_source" not in c:
            c["coord_source"] = "payload"
        if c["lat"] is None and c["id"] in got_c:
            c["lat"], c["lon"], _ = got_c[c["id"]]; c["coord_source"] = "osm"
        if c["lat"] is None and c["id"] in manual:
            c["lat"], c["lon"] = manual[c["id"]]; c["coord_source"] = "manual"
        c.setdefault("coord_source", None)
    for e in park["entrances"]:
        if e["lat"] is not None and "coord_source" not in e:
            e["coord_source"] = "payload"
        if e["lat"] is None and e["id"] in got_e:
            e["lat"], e["lon"], _ = got_e[e["id"]]; e["coord_source"] = "osm"
        key = f"entrance:{e['id']}"
        if e["lat"] is None and key in manual:
            e["lat"], e["lon"] = manual[key]; e["coord_source"] = "manual"
        e.setdefault("coord_source", None)

    # 2. water joins for located camps
    def _bb(coords):
        las = [q[0] for q in coords]; los = [q[1] for q in coords]
        return (min(las), min(los), max(las), max(los))

    lakes = [(nm, p, _bb(p)) for nm, p in lakes_raw if len(p) >= 3]
    streams = [(sl, _bb(sl)) for sl in streams_raw if len(sl) > 1]
    mlat = LAKE_M / 111320.0
    mlon = LAKE_M / (111320.0 * math.cos(math.radians(lat0)))
    klat = CREEK_M / 111320.0
    klon = CREEK_M / (111320.0 * math.cos(math.radians(lat0)))

    for c in park["camps"]:
        if c["lat"] is None:
            continue
        pt = (c["lat"], c["lon"])
        best = None
        for nm, poly, bb in lakes:
            if not (bb[0] - mlat <= pt[0] <= bb[2] + mlat
                    and bb[1] - mlon <= pt[1] <= bb[3] + mlon):
                continue
            d = 0 if _inside(pt, poly, lat0) else _line_dist_m(pt, poly, lat0)
            if d <= LAKE_M and (best is None or d < best[0]):
                best = (d, nm, round(_area_acres(poly, lat0), 1))
        c["lake_within_400m"] = best is not None
        c["lake_name"] = best[1] if best else None
        c["lake_acres"] = best[2] if best else None
        c["creek_within_200m"] = any(
            (bb[0] - klat <= pt[0] <= bb[2] + klat
             and bb[1] - klon <= pt[1] <= bb[3] + klon
             and _line_dist_m(pt, sl, lat0) <= CREEK_M)
            for sl, bb in streams)

    # 3. elevation for every located node
    located = [c for c in park["camps"] if c["lat"] is not None] + \
              [e for e in park["entrances"] if e["lat"] is not None]
    if located:
        for node, ft in zip(located, elevations_ft([(n["lat"], n["lon"])
                                                    for n in located])):
            node["elevation_ft"] = ft

    # 4. straight-line trailhead distance (M3 replaces with trail distance)
    th_pts = [(e["lat"], e["lon"]) for e in park["entrances"]
              if e["lat"] is not None and e.get("included", True)]
    for c in park["camps"]:
        c["trailhead_dist_mi_straightline"] = (
            round(min(haversine_mi((c["lat"], c["lon"]), t) for t in th_pts), 1)
            if c["lat"] is not None and th_pts else None)

    park["schema"] = 2
    inc = [c for c in park["camps"] if c["included"]]
    park["feature_run"] = {
        "osm_camp_candidates": len(osm_camp_cands),
        "osm_trailhead_candidates": len(osm_th_cands),
        "water_polygons": len(lakes), "streams": len(streams),
        "hydro_source": hydro_src,
        "coords_filled_osm": len(got_c) + len(got_e),
        "unmatched_camps": sorted(un_c), "unmatched_entrances": sorted(un_e),
        "included_with_coords": sum(1 for c in inc if c["lat"] is not None),
        "included_total": len(inc),
        "lake_camps": sum(1 for c in inc if c.get("lake_within_400m")),
    }
    save_park(park)
    return park


def feature_summary(park):
    f = park["feature_run"]
    lines = [f"{park['slug']}: coords {f['included_with_coords']}/{f['included_total']} "
             f"included camps ({f['coords_filled_osm']} filled from OSM this run)",
             f"  lake camps: {f['lake_camps']}   "
             f"water polys: {f['water_polygons']}   streams: {f['streams']}",
             f"  OSM candidates: {f['osm_camp_candidates']} camps, "
             f"{f['osm_trailhead_candidates']} trailheads"]
    if f["unmatched_camps"]:
        lines.append(f"  unmatched camps ({len(f['unmatched_camps'])}): "
                     + "; ".join(f["unmatched_camps"][:8])
                     + (" ..." if len(f["unmatched_camps"]) > 8 else ""))
    if f["unmatched_entrances"]:
        lines.append(f"  unmatched entrances ({len(f['unmatched_entrances'])}): "
                     + "; ".join(f["unmatched_entrances"][:8])
                     + (" ..." if len(f["unmatched_entrances"]) > 8 else ""))
    return "\n".join(lines)
