"""v2.1 API invariants, fully offline via an injected fetcher: park layer
has coords and edges, availability colors compute, trips returns ranked
routes with drawable day paths, frontier steps and finishes."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from switchback.graph import Graph
from switchback.web import create_app

D0 = date(2026, 9, 22)


def make_fetch():
    g = Graph("glacier")
    want = {}
    for code in ("GAB", "GLF", "COS"):
        nid = g.find(code)
        want[g.nodes[nid]["division_id"]] = code
    def fetch(permit_id, division_ids, start, end):
        out = {}
        for d in division_ids:
            if d in want:
                out[d] = {(D0 + timedelta(days=i)).isoformat(): 2
                          for i in range(6)}
            else:
                out[d] = {}
        return out
    return fetch


def main():
    client = TestClient(create_app(fetch_fn=make_fetch()))

    parks = client.get("/api/parks").json()
    assert any(p["slug"] == "glacier" for p in parks)

    park = client.get("/api/park/glacier").json()
    assert park["edges"] and any(n["lat"] for n in park["nodes"])
    lakes = [n["id"] for n in park["nodes"] if n["lake"]]
    assert lakes, "feature flags must reach the map layer"

    av = client.get("/api/availability/glacier",
                    params={"start": D0.isoformat(),
                            "end": (D0 + timedelta(days=4)).isoformat(),
                            "party": 2}).json()
    opens = {c["id"]: c["open_nights"] for c in av["camps"]}
    assert max(opens.values()) >= 4 and min(opens.values()) == 0

    trips = client.post("/api/trips", json={
        "slug": "glacier", "start": D0.isoformat(),
        "end": (D0 + timedelta(days=1)).isoformat(), "nights": 3,
        "party": 2, "trip_type": "any"}).json()
    assert trips["routes"], "synthetic availability must yield routes"
    r0 = trips["routes"][0]
    assert r0["day_paths"] and all(len(p) >= 1 for p in r0["day_paths"])
    assert len(r0["days"]) == 4 and r0["score"] > 0

    f0 = client.post("/api/frontier", json={
        "slug": "glacier", "entrance": "Belly River Trail",
        "start": D0.isoformat(), "seq": [], "nights": 3, "party": 2}).json()
    assert f0["options"], "night one must offer camps"
    assert all(o["endings"] > 0 for o in f0["options"])
    first = f0["options"][0]["id"]

    f_end = client.post("/api/frontier", json={
        "slug": "glacier", "entrance": "Belly River Trail",
        "start": D0.isoformat(), "seq": [first, first, first],
        "nights": 3, "party": 2}).json()
    assert "finish" in f_end and f_end["finish"]["ok"] is not None

    print(f"WEB OK: {len(park['nodes'])} nodes, {len(park['edges'])} edges, "
          f"{trips['routes_total']} routes, frontier offers "
          f"{len(f0['options'])} camps night one, finish check present")


if __name__ == "__main__":
    main()
