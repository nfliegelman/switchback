"""Dispersed itineraries experiment (owner approved 2026-07-13).
Phase A shipped here: auto camp candidates for a permit-free area from
named waters plus 3-way-or-better junctions, routed over the shipped
area graph, with a 400 m snap gate. Phase B (synthetic availability and
solver integration) proceeds only because phase A graded within the
published bands; see EXPERIMENTS.md."""
import json, heapq, math, urllib.request, urllib.parse

SNAP_GATE_M = 400.0

def _hav(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (*p, *q))
    return 2 * 6371000 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2 +
        math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))

def candidates(slug, th_pt, bbox):
    d = json.load(open(f"docs/areas/{slug}.json"))
    N, E = d["nodes"], d["edges"]
    adj = {}
    for a, b, mi, _ in E:
        adj.setdefault(a, []).append((b, mi))
        adj.setdefault(b, []).append((a, mi))
    def nearest(pt):
        bi, bd = -1, 1e12
        for i, n in enumerate(N):
            dd = _hav(pt, n)
            if dd < bd:
                bd, bi = dd, i
        return bi, bd
    q = (f'[out:json][timeout:60];(way["natural"="water"]["name"]'
         f'({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
         f'node["natural"="water"]["name"]'
         f'({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}););out center;')
    lakes = []
    for m in ("https://overpass-api.de/api/interpreter",
              "https://overpass.kumi.systems/api/interpreter"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                m, data=urllib.parse.urlencode({"data": q}).encode(),
                headers={"User-Agent": "switchback"}), timeout=70)
            for el in json.load(r).get("elements", []):
                c = el.get("center") or el
                if "lat" in c:
                    lakes.append((el["tags"]["name"], c["lat"], c["lon"]))
            break
        except Exception:
            continue
    th, _ = nearest(th_pt)
    dist = {th: 0.0}
    pq = [(0.0, th)]
    while pq:
        dd, u = heapq.heappop(pq)
        if dd > dist.get(u, 1e9):
            continue
        for v, w in adj.get(u, []):
            nd = dd + w
            if nd < dist.get(v, 1e9):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    out = []
    for name, la, lo in sorted(set(lakes)):
        i, snap = nearest((la, lo))
        if snap <= SNAP_GATE_M and dist.get(i) is not None:
            out.append({"name": name, "node": i,
                        "mi_from_th": round(dist[i], 1)})
    for i in dist:
        if len(adj.get(i, [])) >= 3 and            bbox[0] <= N[i][0] <= bbox[2] and bbox[1] <= N[i][1] <= bbox[3]:
            out.append({"name": f"junction {i}", "node": i,
                        "mi_from_th": round(dist[i], 1)})
    return sorted(out, key=lambda r: r["mi_from_th"])
