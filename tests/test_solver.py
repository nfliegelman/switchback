"""Synthetic parity test: reconstructs the 2026-07-07 live finding
(exactly one bookable Belly River chain: Sept 22 from Belly River TH,
Gable > Glenns Foot > Gable, out_and_back) with injected availability,
so M4 parity holds regardless of live inventory drift."""
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.solver import Solver


def node_by_code(g, code):
    for nid, n in g.nodes.items():
        if n["kind"] == "camp" and n["name"].startswith(code + " - "):
            return nid
    raise AssertionError(code)


def entrance_by_name(g, sub):
    for nid, n in g.nodes.items():
        if n["kind"] == "entrance" and sub in n["name"]:
            return nid
    raise AssertionError(sub)


def main():
    g = Graph("glacier")
    gab, glf = node_by_code(g, "GAB"), node_by_code(g, "GLF")
    av = {c: {} for c in g.camps()}
    av[gab] = {"2026-09-22": 2, "2026-09-24": 2}
    av[glf] = {"2026-09-23": 2}
    s = Solver(g, av, party=2, nights=3, max_mi=13.0, max_gain=4000)
    rows = s.batch(g.entrances(), date(2026, 9, 20), date(2026, 9, 24))
    assert len(rows) == 1, f"expected 1 itinerary, got {len(rows)}: {rows}"
    r = rows[0]
    assert r["start"] == date(2026, 9, 22)
    assert r["entrance"] == entrance_by_name(g, "Belly River")
    assert [g.name(c)[:3] for c in r["seq"]] == ["GAB", "GLF", "GAB"]
    assert r["type"] == "out_and_back", r["type"]
    assert s.endings(r["entrance"], r["start"], 1, r["seq"][0]) == 1
    cos = node_by_code(g, "COS")
    rn = s.route_nodes(r["entrance"], (gab,))
    assert gab in rn and "BELLY_JCT" in rn and cos not in rn
    rn2 = s.route_nodes(r["entrance"], (glf,))
    assert cos in rn2, "pass-through camps must count for --via"
    assert g.find("GAB") == gab and g.find("Glenns Lake Foot") == glf
    print("PARITY OK:", r["start"], ">".join(g.name(c)[:3] for c in r["seq"]),
          r["type"], "days:", [(round(m,1), gn) for m, gn in r["days"]])


if __name__ == "__main__":
    main()
