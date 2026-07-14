"""M5 invariants: day_fit shape, prior monotonicity, ranking prefers
lakeside high-percentile camps, and weights are config-driven."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.scoring import Scorer


def main():
    g = Graph("glacier")
    s = Scorer(g)
    assert s.day_fit(9, 2200, 9, 2200) == 1.0
    assert s.day_fit(0, 0, 9, 2200) == 0.0
    assert s.day_fit(13, 2200, 9, 2200) < 1.0

    def cid(code):
        for nid, n in g.nodes.items():
            if n["kind"] == "camp" and n["name"].startswith(code + " - "):
                return nid
        raise AssertionError(code)

    elf, gab = cid("ELF"), cid("GAB")
    assert s._rating[elf] > s._rating[gab], "lakeside deep camp must out-prior valley junction camp"
    days = [(9.0, 2200), (9.0, 2200)]
    row_lake = {"seq": [elf, elf], "days": days}
    row_dry = {"seq": [gab, gab], "days": days}
    assert s.score(row_lake, 9, 2200)["score"] > s.score(row_dry, 9, 2200)["score"]

    cfg = {"weights": {"day_fit": 1.0, "camp": 0.0, "lakes": 0.0, "solitude": 0.0},
           "prior": s.cfg["prior"]}
    s2 = Scorer(g, cfg)
    a = s2.score(row_lake, 9, 2200)["score"]
    b = s2.score(row_dry, 9, 2200)["score"]
    assert abs(a - b) < 1e-9, "with camp weight zeroed, identical days must tie"
    dh = s.day_hikes(elf, 9, 2200, limit=10)
    assert any(o["rt_mi"] == 3.2 and o["rt_gain"] > 0 for o in dh), \
        "ELH out-and-back from ELF must be 3.2 mi RT (gain floats with the DEM pass)"
    hel = [o for o in dh if o["name"].startswith("HEL")]
    assert hel and hel[0]["rt_mi"] == 8.4, "Helen Lake RT from ELF must be 8.4 mi (leg corrected 2026-07-13)"
    ent = next(nid for nid, n in g.nodes.items()
               if n["kind"] == "entrance" and "Belly River" in n["name"])
    row_base = {"entrance": ent, "seq": [elf, elf],
                "days": [(9.5, 400), (0.0, 0), (9.5, 1000)]}
    sc = s.score(row_base, 9, 2200)
    assert sc["day_fit"] > 0, "layover day must be credited via best day hike"
    notes = s.layover_notes(row_base, 9, 2200)
    assert len(notes) == 1 and "day 2 layover" in notes[0] and "RT" in notes[0]
    print("SCORING OK: ELF prior", s._rating[elf], "pct", round(s._pct[elf], 2),
          "| GAB prior", s._rating[gab], "pct", round(s._pct[gab], 2))


if __name__ == "__main__":
    main()
