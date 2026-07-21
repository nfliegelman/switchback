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

from .geometry import (ATTRIBUTION, CACHE_DIR, TrailNet, _haversine_m, _overpass_once, fetch_gov, simplify)

BOUNDARY_URL = ("https://apps.fs.usda.gov/arcx/rest/services/EDW/"
                "EDW_Wilderness_01/MapServer/0/query")

# v2.20 boundary source registry. Every entry is an ArcGIS query endpoint
# plus a where-builder taking the atlas row's boundary dict. Probed live
# 2026-07-14; field names and quirks recorded in HANDOFF. usfs_wild stays
# the default for rows that carry only an official wilderness name.
BOUNDARY_SOURCES = {
    "usfs_wild": {
        "url": BOUNDARY_URL,
        "where": lambda b: f"WILDERNESSNAME='{b['name']}'",
        "out": "WILDERNESSNAME"},
    "nps": {
        "url": ("https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/"
                "services/NPS_Land_Resources_Division_Boundary_and_Tract_"
                "Data_Service/FeatureServer/2/query"),
        "where": lambda b: f"UNIT_CODE='{b['code']}'",
        "out": "UNIT_CODE"},
    "wildnet": {
        "url": ("https://services1.arcgis.com/ERdCHt0sNM6dENSD/arcgis/rest/"
                "services/Wilderness_Areas_in_the_United_States/"
                "FeatureServer/0/query"),
        "where": lambda b: f"NAME='{b['name']}'",
        "out": "NAME"},
    "blm_wsa": {
        "url": ("https://gis.blm.gov/arcgis/rest/services/lands/"
                "BLM_Natl_NLCS_WLD_WSA/MapServer/1/query"),
        "where": lambda b: f"NLCS_NAME='{b['name']}'",
        "out": "NLCS_NAME"},
    "usfs_ond": {
        "url": ("https://apps.fs.usda.gov/arcx/rest/services/EDW/"
                "EDW_OtherNationalDesignatedArea_01/MapServer/0/query"),
        "where": lambda b: (f"areaname='{b['name']}' AND "
                            f"areatype='{b['type']}'"),
        "out": "areaname"},
    "padus": {
        "url": ("https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/"
                "services/PADUS_Management_Areas/FeatureServer/0/query"),
        "where": lambda b: (f"Unit_Nm='{b['name']}' AND "
                            f"State_Nm='{b['state']}' AND "
                            f"Des_Tp='{b['des']}'"),
        "out": "Unit_Nm"},
}
AREAS_DIR = os.path.join("docs", "areas")
MIRRORS_FLOOR = 25
GOV_ADD_M = 120
MIN_WAY_MI = 0.15


def _atlas_row(slug):
    data = json.load(open("parks/atlas.json"))
    for r in data["rows"]:
        if r.get("slug") == slug and (r.get("official") or r.get("boundary")):
            return r
    raise SystemExit(f"no atlas entry with a boundary source (official "
                     f"wilderness name or boundary dict) for slug {slug!r}")


def fetch_boundary(row, slug):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, f"bnd_{slug}.json")
    if os.path.exists(cache):
        with open(cache) as fh:
            return json.load(fh)
    bspec = row.get("boundary") or {"src": "usfs_wild",
                                    "name": row["official"]}
    src = BOUNDARY_SOURCES[bspec["src"]]
    base = {"where": src["where"](bspec), "outFields": src["out"],
            "returnGeometry": "true", "outSR": "4326",
            "geometryPrecision": "5"}
    polys = []
    for fmt in ("geojson", "json"):
        req = urllib.request.Request(
            src["url"] + "?" + urllib.parse.urlencode(dict(base, f=fmt)),
            headers={"User-Agent": "switchback-areas"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
        for feat in data.get("features", []):
            geo = feat.get("geometry") or {}
            if geo.get("type") == "Polygon":
                polys.append(geo["coordinates"])
            elif geo.get("type") == "MultiPolygon":
                polys.extend(geo["coordinates"])
            elif geo.get("rings"):
                polys.append(geo["rings"])
        if polys:
            break
    if not polys:
        raise SystemExit(f"boundary source {bspec['src']} returned nothing "
                         f"for {slug!r} ({base['where']})")
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
    last, best = None, None
    for attempt, url in enumerate(MIRRORS * 2):
        try:
            data = _overpass_once(url, bbox)
            n = len(data.get("elements", []))
            if best is None or n > len(best.get("elements", [])):
                best = data
            if n < MIRRORS_FLOOR:
                last = f"only {n} ways"
                time.sleep(4)
                continue
            with open(cache, "w") as fh:
                json.dump(data, fh)
            return data
        except Exception as ex:
            last = ex
            time.sleep(5 + attempt * 3)
    if best is not None and best.get("elements"):
        print(f"  floor not met ({last}); keeping best response, "
              f"sparse area accepted")
        with open(cache, "w") as fh:
            json.dump(best, fh)
        return best
    raise RuntimeError(f"OSM mirrors failed for {slug}: {last}")


def _polyline_mi(pts):
    return sum(_haversine_m(a, b) for a, b in zip(pts, pts[1:])) / 1609.34


def build_area(slug):
    row = _atlas_row(slug)
    rings = fetch_boundary(row, slug)
    label = row.get("official") or row["name"]
    lats = [p[0] for r in rings for p in r]
    lons = [p[1] for r in rings for p in r]
    pad = 0.02
    bbox = (min(lats) - pad, min(lons) - pad, max(lats) + pad, max(lons) + pad)
    print(f"{label}: boundary {len(rings)} ring(s), bbox "
          f"{tuple(round(x, 3) for x in bbox)}")

    osm = _fetch_area_osm(bbox, slug)
    net = TrailNet(osm)
    raw, miles = [], 0.0
    for el in osm.get("elements", []):
        pts = [(round(p["lat"], 5), round(p["lon"], 5))
               for p in el.get("geometry") or []]
        if len(pts) < 2:
            continue
        raw.append(pts)
    osm_count = len(raw)

    gov_els, gov_src = fetch_gov(bbox, f"area_{slug}")
    gov_added = 0
    for el in gov_els:
        pts = [(round(p["lat"], 5), round(p["lon"], 5))
               for p in el["geometry"]]
        if len(pts) < 2:
            continue
        samples = [pts[0], pts[len(pts) // 2], pts[-1]]
        if any(net.snap_candidates(p, GOV_ADD_M, k=1) for p in samples):
            continue
        raw.append(pts)
        gov_added += 1

    nodes, edges = _junction_graph(raw)
    nodes, edges = _bridge_components(nodes, edges)
    nodes, edges = _prune_dust(nodes, edges)
    miles = sum(e[2] for e in edges)
    os.makedirs(AREAS_DIR, exist_ok=True)
    out = {"slug": slug, "name": row["name"], "manager": row["cat"],
           "permit": row["permit"], "attribution": ATTRIBUTION,
           "generated": time.strftime("%Y-%m-%d"),
           "boundary": rings, "nodes": nodes, "edges": edges,
           "stats": {"osm_ways": osm_count, "gov_added": gov_added,
                     "trail_miles": round(miles, 1),
                     "graph_nodes": len(nodes), "graph_edges": len(edges)}}
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


def _junction_graph(trails):
    from .geometry import simplify
    """Collapse display polylines into a routable junction graph the
    client can Dijkstra over: nodes at way endpoints and shared
    vertices, edges carrying their real geometry, plus straight
    connectors bridging endpoint gaps under 30 m so tiny digitization
    seams do not fragment the network."""
    key = lambda p: (round(p[0], 5), round(p[1], 5))
    count = {}
    for line in trails:
        for i, p in enumerate(line):
            k = key(p)
            w = 2 if i in (0, len(line) - 1) else 1
            count[k] = count.get(k, 0) + w
    node_id, nodes = {}, []
    def nid(p):
        k = key(p)
        if k not in node_id:
            node_id[k] = len(nodes)
            nodes.append([k[0], k[1]])
        return node_id[k]
    edges = []
    for line in trails:
        seg = [line[0]]
        for p in line[1:]:
            seg.append(p)
            if count[key(p)] > 1 or p is line[-1]:
                if len(seg) >= 2:
                    mi = _polyline_mi(seg)
                    geo = simplify(seg, tol_m=20.0)
                    edges.append([nid(seg[0]), nid(seg[-1]), round(mi, 3),
                                  [[round(q[0], 5), round(q[1], 5)]
                                   for q in geo]])
                seg = [p]
    deg = {}
    for e in edges:
        deg[e[0]] = deg.get(e[0], 0) + 1
        deg[e[1]] = deg.get(e[1], 0) + 1
    grid = {}
    for i, (la, lo) in enumerate(nodes):
        grid.setdefault((int(la * 200), int(lo * 200)), []).append(i)
    linked = {(e[0], e[1]) for e in edges} | {(e[1], e[0]) for e in edges}
    for i, (la, lo) in enumerate(nodes):
        if deg.get(i, 0) != 1:
            continue
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((int(la * 200) + dx, int(lo * 200) + dy), []):
                    if j == i or (i, j) in linked:
                        continue
                    d = _haversine_m((la, lo), tuple(nodes[j]))
                    if d <= 30 and (best is None or d < best[0]):
                        best = (d, j)
        if best:
            j = best[1]
            edges.append([i, j, round(best[0] / 1609.34, 3),
                          [nodes[i], nodes[j]]])
            linked |= {(i, j), (j, i)}
    return nodes, edges


def _prune_dust(nodes, edges, min_component_mi=0.3):
    """Keep only components with real trail mileage; parking stubs and
    fragments in the bbox pad go. Reindexes nodes compactly."""
    parent = list(range(len(nodes)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b, _, _ in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    comp_mi = {}
    for a, b, mi, _ in edges:
        comp_mi[find(a)] = comp_mi.get(find(a), 0.0) + mi
    keep = {r for r, m in comp_mi.items() if m >= min_component_mi}
    new_id, out_nodes, out_edges = {}, [], []
    for a, b, mi, geo in edges:
        if find(a) not in keep:
            continue
        for x in (a, b):
            if x not in new_id:
                new_id[x] = len(out_nodes)
                out_nodes.append(nodes[x])
        out_edges.append([new_id[a], new_id[b], mi, geo])
    return out_nodes, out_edges


def _bridge_components(nodes, edges, max_m=200.0):
    """Heal micro-gaps: OSM trails that cross or nearly touch without
    sharing a node. Merges any component pair within max_m via one
    straight connector at the closest point; kilometre-scale islands
    are real geography and stay islands."""
    parent = list(range(len(nodes)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b, _, _ in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    grid = {}
    for i, (la, lo) in enumerate(nodes):
        grid.setdefault((int(la * 400), int(lo * 400)), []).append(i)
    added = 0
    for _ in range(5):
        best = {}
        for i, (la, lo) in enumerate(nodes):
            ri = find(i)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for j in grid.get((int(la * 400) + dx,
                                       int(lo * 400) + dy), []):
                        if j <= i:
                            continue
                        rj = find(j)
                        if ri == rj:
                            continue
                        d = _haversine_m((la, lo), tuple(nodes[j]))
                        if d <= max_m:
                            k = (min(ri, rj), max(ri, rj))
                            if k not in best or d < best[k][0]:
                                best[k] = (d, i, j)
        if not best:
            break
        for d, i, j in best.values():
            if find(i) == find(j):
                continue
            edges.append([i, j, round(d / 1609.34, 3),
                          [list(nodes[i]), list(nodes[j])]])
            parent[find(i)] = find(j)
            added += 1
    return nodes, edges
