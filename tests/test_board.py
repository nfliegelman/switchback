"""v2.3 invariants: relative windows resolve from today, regions build on
the board, first-come policy survives into the JSON, and the file writes."""
import sys, os, json, tempfile
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.board import build_board, resolve_window, write_board

D0 = date(2026, 9, 20)


def make_fetch():
    g = Graph("lena")
    ull_div = g.nodes[g.find("Upper Lena Lake")]["division_id"]
    def fetch(pid, divs, start, end):
        assert pid == "4098362"
        out = {}
        for d in divs:
            out[d] = {(start + timedelta(days=i)).isoformat():
                      (2 if d == ull_div and i % 2 else 0)
                      for i in range((end - start).days + 1)}
        return out
    return fetch


def main():
    s, e = resolve_window({"start_in_days": 3, "span_days": 21}, D0)
    assert (s, e) == (D0 + timedelta(days=3), D0 + timedelta(days=23))
    s2, e2 = resolve_window({"start": "2026-09-21", "end": "2026-09-23"}, D0)
    assert s2.isoformat() == "2026-09-21"

    cfg = {"windows": [{"title": "Lena test", "slug": "lena",
                        "start_in_days": 1, "span_days": 4,
                        "nights": 2, "party": 2}]}
    board = build_board(cfg, fetch_fn=make_fetch(), today=D0)
    w = board["windows"][0]
    assert not w.get("error") and w["routes"], w
    assert any(s["policy"] == "none" for r in w["routes"] for s in r["stops"]), \
        "first-come policy must reach the board JSON"
    fc_camp = [c for c in w["camps"] if c["policy"] != "reservation"]
    assert fc_camp, "overlay camp must appear in the marker list"

    tmp = tempfile.mkdtemp()
    cfgp = os.path.join(tmp, "cfg.json")
    json.dump(cfg, open(cfgp, "w"))
    # write_board fetches live if no fetch_fn is passed; inject here too
    out, b2 = write_board(cfgp, os.path.join(tmp, "board"),
                          fetch_fn=make_fetch(), today=D0)
    assert os.path.exists(out) and b2["windows"][0]["routes"]
    print(f"BOARD OK: relative windows resolve, {w['itineraries']} itineraries "
          "on a region window, first-come survives to JSON, file written")


if __name__ == "__main__":
    main()
