"""M10 invariants: classifier correctness on known Rainier shapes,
day bounds respected across every returned itinerary, and endings
monotonicity (more availability never means fewer completions)."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.solver import Solver

D0 = date(2026, 9, 14)


def by_name(g, name):
    for nid, n in g.nodes.items():
        if n["name"] == name:
            return nid
    raise AssertionError(name)


def open_all(camps, days, party=2):
    return {c: {(D0 + timedelta(days=i)).isoformat(): party
                for i in range(days)} for c in camps}


def main():
    g = Graph("rainier")
    ent = by_name(g, "Sunrise Trailhead")
    berkeley = by_name(g, "Berkeley Park Camp")
    james = by_name(g, "James Camp")
    mystic = by_name(g, "Mystic Camp")
    granite = by_name(g, "Granite Creek Camp")

    # classifier truth: the Northern Loop from Sunrise is a LOLLIPOP,
    # because the trailhead connector to Sunrise Camp is walked twice.
    av = open_all([berkeley, james, mystic, granite], 4)
    s = Solver(g, av, party=2, nights=4, max_mi=13.0, max_gain=4000)
    assert s.classify(ent, (berkeley, james, mystic, granite)) == "lollipop"

    # a pure loop needs the entrance ON the circuit: White River on the
    # full Wonderland, every edge walked exactly once
    wr = by_name(g, "White River Campground Trailhead")
    circuit = [by_name(g, n) for n in (
        "Summerland Camp", "Indian Bar Camp", "Nickel Creek Camp",
        "Maple Creek Camp", "Paradise River Camp", "Pyramid Creek Camp",
        "Devil's Dream Camp", "So. Puyallup River Camp",
        "Klapatche Park Camp", "No. Puyallup River Camp",
        "Golden Lakes Camp", "So. Mowich River Camp", "Mowich Lake Camp",
        "Ipsut Creek Camp", "Carbon River Camp", "Dick Creek Camp",
        "Mystic Camp", "Granite Creek Camp", "Sunrise Camp")]
    s_loop = Solver(g, open_all(circuit, len(circuit)), party=2,
                    nights=len(circuit), max_mi=13.0, max_gain=4000)
    assert s_loop.classify(wr, tuple(circuit)) == "loop"

    # classifier: same circuit with a stem is a lollipop
    s3 = Solver(g, open_all([mystic, james, berkeley], 3),
                party=2, nights=3, max_mi=13.0, max_gain=4000)
    assert s3.classify(ent, (mystic, james, berkeley)) == "lollipop"

    # classifier: a pure spur is an out_and_back
    s1 = Solver(g, open_all([berkeley], 1), party=2, nights=1,
                max_mi=13.0, max_gain=4000)
    assert s1.classify(ent, (berkeley,)) == "out_and_back"

    # bounds respected across every itinerary the solver returns
    rows = s.batch([ent], D0, D0)
    assert rows, "loose availability must yield itineraries"
    for r in rows:
        for mi, gain in r["days"]:
            assert mi <= 13.0 and gain <= 4000, f"bound violated: {r}"

    # endings monotonicity: superset availability never shrinks endings
    d2 = (D0 + timedelta(days=1)).isoformat()
    av_a = {granite: {d2: 2}}
    av_b = {granite: {d2: 2}, berkeley: {d2: 2}}
    # gain cap at 6000 so both candidate camps stay feasible under
    # DEM-corrected gains; the invariant under test is monotonicity
    e_a = Solver(g, av_a, party=2, nights=2, max_mi=13.0,
                 max_gain=6000).endings(ent, D0, 1, mystic)
    e_b = Solver(g, av_b, party=2, nights=2, max_mi=13.0,
                 max_gain=6000).endings(ent, D0, 1, mystic)
    assert e_b >= e_a and (e_a, e_b) == (1, 2), (e_a, e_b)

    print("SHAPES OK: Wonderland loop, Northern Loop lollipop, spur out_and_back; "
          f"{len(rows)} itineraries all within bounds; endings {e_a} -> {e_b} monotone")


if __name__ == "__main__":
    main()
