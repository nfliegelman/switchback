"""Tread (trail-surface difficulty) invariants, owner-directed 2026-07-22:
rough ground adds effective effort on top of grade, curated per edge from
AllTrails plus owner ground truth, and untread parks are untouched."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.tread import (DEFAULT_TREAD_SURCHARGE, describe_tread,
                              normalize_tread, path_tread)
from switchback.graph import Graph
from switchback.scoring import Scorer


def check_surcharge_table():
    assert DEFAULT_TREAD_SURCHARGE["smooth"] == 0
    assert DEFAULT_TREAD_SURCHARGE["moderate"] == 0, "typical trail is baseline"
    assert DEFAULT_TREAD_SURCHARGE["rough"] > 0
    assert DEFAULT_TREAD_SURCHARGE["very_rough"] > DEFAULT_TREAD_SURCHARGE["rough"]
    table, errs = normalize_tread({"rough": 500})
    assert not errs and table["rough"] == 500
    _t, errs = normalize_tread({"gravel": 9})
    assert errs and "unknown tread" in errs[0]


def check_describe():
    assert describe_tread({"rough": 3.5}) == "3.5 mi rough footing, rock and roots"
    assert describe_tread({"smooth": 3.2}) == "", "smooth tread is not called out"
    assert describe_tread({}) == ""


def check_lena_curated_and_scored():
    """Lena is the curated pilot: lower leg smooth, upper leg rough. The
    rough upper leg must add effort and score lower than its raw gain."""
    g = Graph("lena")
    assert g.tread, "Lena must load curated tread"
    lll, upper = g.find("LLL"), g.find("Upper Lena Lake")
    th = g.entrances()[0]
    miles_by, sur_low, _ = path_tread(g, g.leg(th, lll)[2])
    assert miles_by.get("smooth") and sur_low == 0, "smooth leg adds no effort"
    miles_by, sur_up, worst = path_tread(g, g.leg(lll, upper)[2])
    assert worst == "rough" and sur_up > 0, "the upper Lena leg is rough"
    sc = Scorer(g)
    raw = sc.day_fit(3.5, 2500, 6.0, 1500)
    withtread = sc.day_fit(3.5, 2500 + sur_up, 6.0, 1500)
    assert withtread < raw, "rough ground must make the day fit lower"


def check_untread_park_unchanged():
    """A park with no curated tread must score exactly as before (the
    fast-path guard), so the feature is purely additive."""
    g = Graph("glacier")
    assert not g.tread, "glacier carries no curated tread yet"
    sc = Scorer(g)
    ent = next(nid for nid, n in g.nodes.items()
               if n["kind"] == "entrance" and "Belly River" in n["name"])
    camp = next(c for c in g.camps() if g.name(c).startswith("ELF"))
    # effective gain equals raw gain when the park has no curated tread
    assert sc._effective_gain(1000, [ent, camp, camp, ent], 2) == 1000


def main():
    check_surcharge_table()
    check_describe()
    check_lena_curated_and_scored()
    check_untread_park_unchanged()
    print("TREAD OK: curated per edge, rough ground adds effort, "
          "untread parks untouched")


if __name__ == "__main__":
    main()
