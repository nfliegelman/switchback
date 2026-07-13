"""
switchback.dem: the v2.4 gain pass.

The standing caution since M3: endpoint-delta gains understate passes by
roughly 40 percent (Longmire to Klapatche benchmarked 3,658 estimated
against 6,450 from a GPS log), because a pass edge climbs and descends
far more than its endpoints reveal. This pass replaces endpoint deltas
with a route-sampled figure: densify the line between edge endpoints at
about 100 m spacing, look up real terrain elevations from the Open-Meteo
DEM (the same source as the M2 elevations), and accumulate gain and loss
with 5 m hysteresis so sensor-scale noise never counts as climbing.

Honesty note, recorded here and in the edge files: the sampled path is
the straight line between nodes, not the trail, so contouring trails
around ridges can still differ. Edges keep est_gain true and gain a
gain_method field ("dem_line_v1"); truly sourced numbers still outrank
this. The benchmark against the GPS log is printed by the CLI so the
improvement is a measured claim, not a hoped one.
"""
import json
import math
import os
import urllib.parse
import urllib.request

API = "https://api.open-meteo.com/v1/elevation"
EDGE_DIR = os.path.join("parks", "edges")


def _haversine_m(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371000 * 2 * math.asin(math.sqrt(h))


def sample_line(a, b, step_m=100, max_pts=400):
    dist = _haversine_m(a, b)
    n = min(max_pts, max(2, int(dist / step_m) + 1))
    return [(a[0] + (b[0] - a[0]) * i / (n - 1),
             a[1] + (b[1] - a[1]) * i / (n - 1)) for i in range(n)]


def fetch_elevations(coords):
    """Open-Meteo elevation lookups, 100 points per call, meters."""
    out = []
    for i in range(0, len(coords), 100):
        chunk = coords[i:i + 100]
        q = urllib.parse.urlencode({
            "latitude": ",".join(f"{c[0]:.5f}" for c in chunk),
            "longitude": ",".join(f"{c[1]:.5f}" for c in chunk)})
        req = urllib.request.Request(f"{API}?{q}",
                                     headers={"User-Agent": "switchback"})
        with urllib.request.urlopen(req, timeout=30) as r:
            out.extend(json.load(r)["elevation"])
    return out


def gain_loss_ft(elevs_m, hysteresis_m=5.0):
    """Accumulate climb and descent, ignoring wiggles under the
    hysteresis band. Returns integer feet (up, down)."""
    up = down = 0.0
    anchor = elevs_m[0]
    for e in elevs_m[1:]:
        d = e - anchor
        if d >= hysteresis_m:
            up += d
            anchor = e
        elif d <= -hysteresis_m:
            down += -d
            anchor = e
    return int(round(up * 3.28084)), int(round(down * 3.28084))


def dem_edges(slug, elev_fn=None, dry=False):
    """Fill DEM gains for every estimated edge whose endpoints both have
    coordinates. Returns (updated, skipped, report_lines)."""
    from .graph import Graph
    path = os.path.join(EDGE_DIR, f"{slug}_edges.json")
    with open(path) as fh:
        spec = json.load(fh)
    g = Graph(slug)
    elev = elev_fn or fetch_elevations
    updated, skipped, lines = 0, [], []
    for e in spec["edges"]:
        sourced = e.get("gain_ab") is not None and not e.get("est_gain")
        if sourced or e.get("dem_exempt"):
            continue
        a, b = g._resolve(e["a"]), g._resolve(e["b"])
        ca = (g.nodes[a].get("lat"), g.nodes[a].get("lon")) if a else (None, None)
        cb = (g.nodes[b].get("lat"), g.nodes[b].get("lon")) if b else (None, None)
        if None in ca or None in cb:
            skipped.append(f"{e['a']} <> {e['b']} (missing coords)")
            continue
        pts = sample_line(ca, cb)
        el = elev(pts)
        up, down = gain_loss_ft(el)
        peak_over = max(el) - max(el[0], el[-1])
        suspect = peak_over > 365  # a ridge 1,200+ ft above both endpoints
        before = e.get("gain_ab")
        lines.append(f"  {e['a']} > {e['b']}: gain "
                     f"{before if before is not None else 'endpoint'} -> {up}"
                     f" ft, loss -> {down} ft ({len(pts)} samples)")
        if not dry:
            e["gain_ab"], e["loss_ab"] = up, down
            e["est_gain"] = True
            e["gain_method"] = "dem_line_v1"
            if suspect:
                e["dem_flag"] = "ridge_suspect"
        if suspect:
            lines[-1] += "  RIDGE SUSPECT: line crosses terrain far above both endpoints; verify or use pass arithmetic"
        updated += 1
    if not dry:
        with open(path, "w") as fh:
            json.dump(spec, fh, indent=1)
    return updated, skipped, lines
