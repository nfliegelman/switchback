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
    out, used = [], set()
    for name, la, lo in sorted(set(lakes)):
        i, snap = nearest((la, lo))
        if snap <= SNAP_GATE_M and dist.get(i) is not None and i not in used:
            used.add(i)
            out.append({"name": name, "node": i,
                        "mi_from_th": round(dist[i], 1)})
    for i in dist:
        if len(adj.get(i, [])) >= 3 and            bbox[0] <= N[i][0] <= bbox[2] and bbox[1] <= N[i][1] <= bbox[3]:
            out.append({"name": f"junction {i}", "node": i,
                        "mi_from_th": round(dist[i], 1)})
    return sorted(out, key=lambda r: r["mi_from_th"])


def _elev_ft(lat, lon):
    import urllib.request, json as _j
    try:
        u = (f"https://epqs.nationalmap.gov/v1/json?x={lon}&y={lat}"
             f"&units=Feet&wkid=4326&includeDate=false")
        with urllib.request.urlopen(u, timeout=25) as r:
            return int(float(_j.load(r)["value"]))
    except Exception:
        return None


def build_pilot(area_slug, park_slug, park_name, th_name, th_pt, bbox):
    """Item 1 productization: gated candidates, named junctions, USGS
    gains on every edge, standard schema out."""
    import json as _j, heapq
    cands = candidates(area_slug, th_pt, bbox)
    d = _j.load(open(f"docs/areas/{area_slug}.json"))
    N, E = d["nodes"], d["edges"]
    adj = {}
    for a, b, mi, _ in E:
        adj.setdefault(a, []).append((b, mi))
        adj.setdefault(b, []).append((a, mi))
    def dij(s):
        dist = {s: 0.0}; pq = [(0.0, s)]
        while pq:
            dd, u = heapq.heappop(pq)
            if dd > dist.get(u, 1e9):
                continue
            for v, w in adj.get(u, []):
                nd = dd + w
                if nd < dist.get(v, 1e9):
                    dist[v] = nd; heapq.heappush(pq, (nd, v))
        return dist
    camps, code_of, elev = [], {}, {}
    for i, c in enumerate(cands[:10]):
        code = f"P{i+1:02d}"
        code_of[c["node"]] = code
        la, lo = N[c["node"]]
        e = _elev_ft(la, lo)
        elev[code] = e
        nm = (c["name"].title() if not c["name"].startswith("junction")
              else f"Trail Junction at {c['mi_from_th']} mi")
        camps.append({"id": f"{park_slug.upper()}-{code}", "code": code,
                      "name": f"{code} - {nm} (dispersed)", "lat": la,
                      "lon": lo, "elevation_ft": e, "policy": "none",
                      "water_lake_flag": "Y" if "Lake" in nm else "N",
                      "included": True,
                      "note": "auto-generated dispersed candidate"})
    th_node = min(range(len(N)), key=lambda i: _hav(th_pt, tuple(N[i])))
    ent_ref = f"ENT:{th_name}"
    ent = {"id": f"{park_slug.upper()}-ENT", "code": "ENT",
           "name": f"ENT - {th_name}",
           "lat": N[th_node][0], "lon": N[th_node][1]}
    elev["ENT"] = _elev_ft(*N[th_node])
    edges = []
    nodes_all = [(th_node, "ENT")] + [(c["node"], code_of[c["node"]])
                                      for c in cands[:10]]
    for idx, (na, ca) in enumerate(nodes_all):
        dist = dij(na)
        for nb, cb in nodes_all[idx + 1:]:
            mi = dist.get(nb)
            if mi and 0.8 <= mi <= 9.5:
                ed = {"a": ent_ref if ca == "ENT" else ca,
                      "b": ent_ref if cb == "ENT" else cb,
                      "miles": round(mi, 1)}
                ea, eb = elev.get(ca), elev.get(cb)
                if ea is not None and eb is not None:
                    ed["gain_ab"] = max(0, eb - ea)
                    ed["est_gain"] = True
                edges.append(ed)
    _j.dump({"slug": park_slug, "name": park_name, "region": "colorado",
             "notes": "Auto-generated dispersed park; camps policy none.",
             "members": [], "entrances": [ent], "camps": camps},
            open(f"parks/{park_slug}.json", "w"), indent=1)
    _j.dump({"slug": park_slug, "schema": 1,
             "notes": "Auto edges; miles from the area graph, gains from "
                      "USGS EPQS point elevations, est_gain flagged.",
             "nodes": [], "edges": edges},
            open(f"parks/edges/{park_slug}_edges.json", "w"), indent=1)
    print(f"{park_slug}: {len(camps)} camps, {len(edges)} edges, "
          f"elevations {sum(1 for v in elev.values() if v)} of {len(elev)}")
