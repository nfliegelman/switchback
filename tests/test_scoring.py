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
    print("SCORING OK: ELF prior", s._rating[elf], "pct", round(s._pct[elf], 2),
          "| GAB prior", s._rating[gab], "pct", round(s._pct[gab], 2))


if __name__ == "__main__":
    main()
