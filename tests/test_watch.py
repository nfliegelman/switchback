"""M9 invariants: flicker filter holds one cycle, exactly one alert per
opening, re-alert only after a close, restarts do not duplicate."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.watch import WatchState, load_config
import json, tempfile

K = ("DIV1", "2026-09-22")


def main():
    st = WatchState(party=2)
    assert st.observe({K: 0}) == []            # full
    assert st.observe({K: 2}) == []            # opens: candidate, no alert yet
    assert st.observe({K: 2}) == [K]           # persists: exactly one alert
    assert st.observe({K: 3}) == []            # still open: silent
    assert st.observe({K: 0}) == []            # closes: reset
    assert st.observe({K: 2}) == []            # reopens: candidate again
    assert st.observe({K: 2}) == [K]           # persists: second alert allowed

    st2 = WatchState(party=2)
    assert st2.observe({K: 0}) == []
    assert st2.observe({K: 2}) == []           # blip appears...
    assert st2.observe({K: 0}) == []           # ...and vanishes: flicker
    assert st2.observe({K: 0}) == []           # never alerted

    st3 = WatchState(party=2)
    st3.observe({K: 2})
    revived = WatchState.from_json(st3.to_json())
    assert revived.observe({K: 2}) == [K], "state must survive a restart"
    assert revived.observe({K: 2}) == [], "and not double-fire after it"

    assert WatchState(party=4).observe({K: 3}) == [] , "3 spots is closed for a party of 4"

    d = tempfile.mkdtemp()
    p = os.path.join(d, "cfg.json")
    json.dump({"enabled": False, "slug": "glacier"}, open(p, "w"))
    assert load_config(p) is None, "disabled config must return None"
    json.dump({"enabled": True, "slug": "glacier", "start": "2026-09-18",
               "end": "2026-09-26"}, open(p, "w"))
    assert load_config(p)["slug"] == "glacier"
    assert load_config(os.path.join(d, "missing.json")) is None
    print("WATCH OK: flicker filtered, exactly-once per opening, restart-safe")


if __name__ == "__main__":
    main()
