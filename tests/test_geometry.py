"""v2.7 invariants: routing follows the network not the crow, snapping
respects its radius, simplification keeps endpoints, sanity gate rejects
mis-routes, day_path falls back straight without breaking the line."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.geometry import TrailNet, simplify, edge_key, day_path

def L(pts):  # one OSM way
    return {"geometry": [{"lat": a, "lon": b} for a, b in pts]}

def main():
    # an L-shaped trail: straight-line distance is the hypotenuse, the
    # routed distance must be the two legs
    net = TrailNet({"elements": [
        L([(47.0, -113.0), (47.0, -112.9), (47.0, -112.8)]),
        L([(47.0, -112.8), (47.1, -112.8)]),
    ]})
    pts, meters = net.route((47.0, -113.0), (47.1, -112.8))
    assert pts is not None and len(pts) >= 4
    import math
    kx = 111320 * math.cos(math.radians(47.0))
    legs = 0.2 * kx + 0.1 * 110540
    crow = math.hypot(0.2 * kx, 0.1 * 110540)
    assert meters > 1.25 * crow, "must route the L, not the crow"
    assert abs(meters - legs) / legs < 0.05, "routed length must equal the legs"

    assert net.snap((48.5, -100.0)) is None, "snap radius must bound"

    ridge = [(47.0, -113.0 + i * 0.001) for i in range(50)]
    simp = simplify([(a, b) for a, b in ridge], tol_m=12)
    assert simp[0] == ridge[0] and simp[-1] == ridge[-1] and len(simp) < 10

    assert edge_key("B", "A") == edge_key("A", "B") == "A|B"

    class FakeG:
        park = {"slug": "nope"}
        nodes = {"x": {"lat": 47.0, "lon": -113.0},
                 "y": {"lat": 47.1, "lon": -112.8}}
        def leg(self, a, b): return (1.0, 0, [a, b])
    line = day_path("nope", FakeG(), ["x", "y"])
    assert line == [[47.0, -113.0], [47.1, -112.8]], "clean straight fallback"
    print("GEOMETRY OK: routes the L not the crow, snap bounded, "
          "simplify anchored, fallback unbroken")

if __name__ == "__main__":
    main()
