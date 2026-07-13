"""
switchback.geometry: real trail polylines. v2.7, at the owner's order:
"I need these lines to actually track the paths of trails."

Pipeline per park: one Overpass fetch of every foot-travel way in the
park's bounding box (cached to parks/.osm_cache so reruns are free),
stitch the ways into a routable network, snap each graph edge's
endpoints to the nearest trail vertex, Dijkstra along the network, and
store the simplified polyline in parks/geometry/<slug>.json keyed by
node pair. Renderers (map, board, GPX) look paths up and fall back to
straight lines wherever routing honestly failed, with the reason
recorded in the harvest report rather than hidden.

Sanity gate: a routed path whose length disagrees wildly with the
edge's curated mileage (outside 0.6x to 1.8x) is rejected as a
mis-route and falls back straight; better no geometry than wrong
geometry. Cluster spokes and same-zone twins (under 0.3 mi) stay
straight by design.

Licensing: geometry is derived from OpenStreetMap via the Overpass API,
(c) OpenStreetMap contributors, ODbL 1.0. The attribution string ships
inside every geometry file and on every map surface.
"""
import heapq
import json
import hashlib
import math
import os
import time
import urllib.parse
import urllib.request

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
CACHE_DIR = os.path.join("parks", ".osm_cache")
GEOM_DIR = os.path.join("parks", "geometry")
ATTRIBUTION = ("Trail geometry derived from OpenStreetMap via the "
               "Overpass API, (c) OpenStreetMap contributors, ODbL 1.0")
FOOT_WAYS = "path|footway|steps|track|bridleway"
SNAP_M = 300
MIN_ROUTED_MI = 0.3
RATIO_LO, RATIO_HI = 0.6, 1.8


def _haversine_m(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371000 * 2 * math.asin(math.sqrt(h))


def _overpass_once(url, bbox):
    s, w, n, e = bbox
    q = (f'[out:json][timeout:180];'
         f'way["highway"~"^({FOOT_WAYS})$"]({s},{w},{n},{e});'
         f'out geom;')
    req = urllib.request.Request(
        url, data=urllib.parse.urlencode({"data": q}).encode(),
        headers={"User-Agent": "switchback-geometry"})
    with urllib.request.urlopen(req, timeout=200) as r:
        return json.load(r)


def fetch_validated(bbox, cache_tag, probe_pts, min_coverage=0.7):
    """Walk the mirror list until a response actually covers the graph:
    a response is accepted only if a trail vertex sits within 800 m of
    at least min_coverage of probe_pts. Partial mirror extracts pass
    size checks but fail this one, which is the point. Validated
    responses are cached with their coverage stamped in."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = hashlib.sha1(json.dumps(bbox).encode()).hexdigest()[:16]
    cache = os.path.join(CACHE_DIR, f"trails_{cache_tag}_{key}.json")
    if os.path.exists(cache):
        with open(cache) as fh:
            data = json.load(fh)
        if data.get("_coverage", 0) >= min_coverage:
            return data, data["_coverage"]
        os.remove(cache)
    best, best_cov = None, -1.0
    for attempt, url in enumerate(MIRRORS):
        try:
            data = _overpass_once(url, bbox)
        except Exception:
            time.sleep(8 + attempt * 7)
            continue
        net = TrailNet(data)
        near = sum(1 for p in probe_pts
                   if net.snap_candidates(p, 800, k=1))
        cov = near / max(1, len(probe_pts))
        if cov > best_cov:
            best, best_cov = data, cov
        if cov >= min_coverage:
            break
        time.sleep(6)
    if best is None:
        raise RuntimeError("all Overpass mirrors failed")
    best["_coverage"] = round(best_cov, 3)
    with open(cache, "w") as fh:
        json.dump(best, fh)
    return best, best_cov


class TrailNet:
    def __init__(self, overpass_json):
        self.coord = {}
        self.adj = {}
        self.grid = {}
        for el in overpass_json.get("elements", []):
            geom = el.get("geometry") or []
            pts = [(p["lat"], p["lon"]) for p in geom]
            for a, b in zip(pts, pts[1:]):
                ka, kb = self._vk(a), self._vk(b)
                d = _haversine_m(a, b)
                self.adj.setdefault(ka, []).append((kb, d))
                self.adj.setdefault(kb, []).append((ka, d))
        # heal micro-gaps: OSM ways that visibly meet but share no node
        # (bridge crossings, mapping seams) get a bridge edge under 30 m
        ends = [v for v, lst in self.adj.items() if len(lst) == 1]
        by_cell = {}
        for v in ends:
            by_cell.setdefault((round(v[0], 3), round(v[1], 3)), []).append(v)
        bridged = 0
        for v in ends:
            cy, cx = round(v[0], 3), round(v[1], 3)
            for dy in (-0.001, 0.0, 0.001):
                for dx in (-0.001, 0.0, 0.001):
                    for u in by_cell.get((round(cy + dy, 3),
                                          round(cx + dx, 3)), []):
                        if u is v:
                            continue
                        d = _haversine_m(v, u)
                        if 0 < d <= 30:
                            self.adj[v].append((u, d))
                            self.adj[u].append((v, d))
                            bridged += 1
        self.bridged = bridged // 2
        # union-find component ids, so snapping can see past fragments
        parent = {v: v for v in self.coord}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, lst in self.adj.items():
            for v, _w in lst:
                ru, rv = find(u), find(v)
                if ru != rv:
                    parent[ru] = rv
        self.comp = {v: find(v) for v in self.coord}
        sizes = {}
        for c in self.comp.values():
            sizes[c] = sizes.get(c, 0) + 1
        self.comp_size = sizes

    def _vk(self, pt):
        k = (round(pt[0], 6), round(pt[1], 6))
        if k not in self.coord:
            self.coord[k] = k
            self.grid.setdefault((round(pt[0], 2), round(pt[1], 2)),
                                 []).append(k)
        return k

    def snap(self, pt, max_m=SNAP_M):
        c = self.snap_candidates(pt, max_m, k=1)
        return c[0] if c else None

    def snap_candidates(self, pt, max_m=SNAP_M, k=5):
        """Nearest trail vertex per connected component within max_m,
        best components first. Parking-lot fragments can no longer
        shadow the actual trail."""
        ring = int(max_m / 1000) + 1
        found = []
        cy, cx = round(pt[0], 2), round(pt[1], 2)
        for dy in range(-ring, ring + 1):
            for dx in range(-ring, ring + 1):
                for v in self.grid.get((round(cy + dy * 0.01, 2),
                                        round(cx + dx * 0.01, 2)), []):
                    d = _haversine_m(pt, v)
                    if d <= max_m:
                        found.append((d, v))
        found.sort()
        out, seen_comp = [], set()
        for _d, v in found:
            c = self.comp.get(v)
            if c in seen_comp:
                continue
            seen_comp.add(c)
            out.append(v)
            if len(out) >= k:
                break
        return out

    def route(self, a_pt, b_pt, max_m=SNAP_M):
        """Dijkstra between snapped endpoints, trying up to three snap
        candidates per side so disconnected fragments cannot strand a
        route. Returns (pts, meters) or (None, reason)."""
        cas = self.snap_candidates(a_pt, max_m, k=5)
        cbs = self.snap_candidates(b_pt, max_m, k=5)
        if not cas or not cbs:
            return None, "no trail within snap radius"
        targets = set(cbs)
        for a in cas[:5]:
            dist = {a: 0.0}
            prev = {}
            pq = [(0.0, a)]
            hit = None
            while pq:
                d, u = heapq.heappop(pq)
                if u in targets:
                    hit = u
                    break
                if d > dist.get(u, 1e18):
                    continue
                for v, w in self.adj.get(u, []):
                    nd = d + w
                    if nd < dist.get(v, 1e18):
                        dist[v] = nd
                        prev[v] = u
                        heapq.heappush(pq, (nd, v))
            if hit is None:
                continue
            path = [hit]
            while path[-1] != a:
                path.append(prev[path[-1]])
            path.reverse()
            pts = [a_pt] + [self.coord[k] for k in path] + [b_pt]
            return pts, dist[hit]
        return None, "endpoints on disconnected trail segments"


def simplify(pts, tol_m=12.0):
    """Douglas-Peucker in a local planar approximation."""
    if len(pts) < 3:
        return pts
    lat0 = math.radians(pts[0][0])
    kx, ky = 111320 * math.cos(lat0), 110540

    def dseg(p, a, b):
        ax, ay = (a[1] - p[1]) * kx, (a[0] - p[0]) * ky
        bx, by = (b[1] - p[1]) * kx, (b[0] - p[0]) * ky
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            return math.hypot(ax, ay)
        t = max(0.0, min(1.0, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
        return math.hypot(ax + t * dx, ay + t * dy)

    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        worst, wd = -1, tol_m
        for k in range(i + 1, j):
            d = dseg(pts[k], pts[i], pts[j])
            if d > wd:
                worst, wd = k, d
        if worst >= 0:
            keep[worst] = True
            stack.extend([(i, worst), (worst, j)])
    return [p for p, k in zip(pts, keep) if k]


def edge_key(a, b):
    return "|".join(sorted((str(a), str(b))))


def harvest(slug, net=None, dry=False):
    """Route every substantial graph edge along real trails. Returns
    (routed, fallbacks, report_lines)."""
    from .graph import Graph
    g = Graph(slug)
    lats = [n["lat"] for n in g.nodes.values() if n.get("lat")]
    lons = [n["lon"] for n in g.nodes.values() if n.get("lon")]
    pad = 0.04
    bbox = (min(lats) - pad, min(lons) - pad, max(lats) + pad, max(lons) + pad)
    probe = [(n["lat"], n["lon"]) for n in g.nodes.values() if n.get("lat")]
    if net is None:
        data, cov = fetch_validated(bbox, slug, probe)
        net = TrailNet(data)
        lines_cov = f"  network coverage: {cov:.0%} of graph nodes"
    else:
        lines_cov = None
    seen, paths = set(), {}
    routed, fallbacks, lines = 0, [], ([lines_cov] if lines_cov else [])
    for a, lst in g.adj.items():
        for b, mi, gain, est, _k in lst:
            key = edge_key(a, b)
            if key in seen:
                continue
            seen.add(key)
            na, nb = g.nodes[a], g.nodes[b]
            if mi is not None and mi <= MIN_ROUTED_MI:
                continue
            if not (na.get("lat") and nb.get("lat")):
                fallbacks.append((key, "missing coords"))
                continue
            pts, res = net.route((na["lat"], na["lon"]), (nb["lat"], nb["lon"]))
            if pts is None:
                pts, res = net.route((na["lat"], na["lon"]),
                                     (nb["lat"], nb["lon"]), max_m=800)
            if pts is None:
                fallbacks.append((key, res))
                lines.append(f"  FALLBACK {g.name(a)} <> {g.name(b)}: {res}")
                continue
            geom_mi = res / 1609.34
            coarse = bool(mi and geom_mi / mi < RATIO_LO)
            if mi and geom_mi / mi > RATIO_HI:
                fallbacks.append((key, f"detour: routed {geom_mi:.1f} "
                                       f"vs curated {mi}"))
                lines.append(f"  REJECT {g.name(a)} <> {g.name(b)}: routed "
                             f"{geom_mi:.1f} mi vs curated {mi} mi looks "
                             "like a wrong-way detour")
                continue
            spts = simplify(pts)
            if str(a) > str(b):
                spts = list(reversed(spts))
            rec = {"pts": [[round(p[0], 5), round(p[1], 5)] for p in spts],
                   "geom_mi": round(geom_mi, 2)}
            if coarse:
                rec["coarse"] = True
                lines.append(f"  coarse {g.name(a).split(' (')[0]} <> "
                             f"{g.name(b).split(' (')[0]}: OSM digitizes "
                             f"{geom_mi:.1f} mi where guides say {mi}; "
                             "shape kept, mileage NOT trusted")
            paths[key] = rec
            routed += 1
            lines.append(f"  routed {g.name(a).split(' (')[0]} <> "
                         f"{g.name(b).split(' (')[0]}: {geom_mi:.1f} mi along "
                         f"trail (curated {mi}), {len(spts)} pts")
    if not dry:
        os.makedirs(GEOM_DIR, exist_ok=True)
        out = {"slug": slug, "attribution": ATTRIBUTION,
               "generated": time.strftime("%Y-%m-%d"), "paths": paths}
        with open(os.path.join(GEOM_DIR, f"{slug}.json"), "w") as fh:
            json.dump(out, fh)
    return routed, fallbacks, lines


_GEOM_CACHE = {}


def _load(slug):
    if slug not in _GEOM_CACHE:
        try:
            with open(os.path.join(GEOM_DIR, f"{slug}.json")) as fh:
                _GEOM_CACHE[slug] = json.load(fh).get("paths", {})
        except (OSError, ValueError):
            _GEOM_CACHE[slug] = {}
    return _GEOM_CACHE[slug]


def path_for(slug, a, b):
    """Trail polyline for a node pair, oriented a to b, or None."""
    rec = _load(slug).get(edge_key(a, b))
    if not rec:
        return None
    pts = rec["pts"]
    return pts if str(a) <= str(b) else list(reversed(pts))


def day_path(slug, g, stops):
    """Concatenated trail polyline for one day's walk along node stops;
    straight-line fallback per hop keeps the line unbroken."""
    out = []
    for x, y in zip(stops, stops[1:]):
        leg = g.leg(x, y)
        hop_nodes = leg[2] if leg else [x, y]
        if len(hop_nodes) < 2:
            n = g.nodes[hop_nodes[0] if hop_nodes else x]
            out.append([n.get("lat"), n.get("lon")])
            continue
        for p, q in zip(hop_nodes, hop_nodes[1:]):
            seg = path_for(slug, p, q)
            if seg is None:
                pa, pb = g.nodes[p], g.nodes[q]
                seg = [[pa.get("lat"), pa.get("lon")],
                       [pb.get("lat"), pb.get("lon")]]
            if out and seg and out[-1] == seg[0]:
                out.extend(seg[1:])
            else:
                out.extend(seg)
    return [p for p in out if p[0] is not None]
