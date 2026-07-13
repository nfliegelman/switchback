"""v2.2 invariants: a region merges permits and permitless overlays into
one graph, fetches group once per permit, synthetic availability never
masquerades as a reservation, and the report labels first-come nights."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.solver import Solver, fetch_for_graph
from switchback.scoring import Scorer
from switchback.report import format_trips

D0 = date(2026, 9, 21)


def main():
    g = Graph("lena")
    assert not g.unresolved, g.unresolved
    lll = g.find("LLL")
    ull = g.find("Upper Lena Lake")
    assert g.nodes[lll]["policy"] == "none" and g.nodes[lll]["permit_id"] is None
    assert g.nodes[ull]["policy"] == "reservation"
    assert g.nodes[ull]["permit_id"] == "4098362"
    assert abs(g.nodes[ull]["lat"] - 47.6386) < 1e-6, "curated override must win"

    calls = []
    def fetch(pid, divs, start, end):
        calls.append((pid, tuple(sorted(divs))))
        return {d: {(D0 + timedelta(days=i)).isoformat(): (2 if i == 1 else 0)
                    for i in range(4)} for d in divs}

    av = fetch_for_graph(g, g.camps(), D0, D0 + timedelta(days=3), fetch_fn=fetch)
    assert calls == [("4098362", (g.nodes[ull]["division_id"],))], calls
    assert all(v == 99 for v in av[lll].values()), "permitless = synthetic open"
    assert av[ull][(D0 + timedelta(days=1)).isoformat()] == 2

    s = Solver(g, av, party=2, nights=2, max_mi=13.0, max_gain=4000)
    rows = s.batch(g.entrances(), D0, D0)
    assert rows, "LLL always-open must guarantee itineraries"
    seqs = {r["seq"] for r in rows}
    assert (lll, ull) in seqs, "the cross-boundary chain LLL then ULL must exist"

    scorer = Scorer(g)
    ranked = scorer.rank(rows, 8.0, 1500)
    text, _ = format_trips(g, scorer, ranked, 8.0, 1500, 2, 2, 13.0, 4000)
    assert "first-come" in text, "permitless nights must be labeled"
    assert "Reservable" not in text
    print("REGIONS OK: one fetch for permit 4098362, LLL synthetic-open, "
          f"cross-boundary chain present, first-come labeled; {len(rows)} itineraries")


if __name__ == "__main__":
    main()
