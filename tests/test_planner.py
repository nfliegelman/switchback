"""Golden scenarios for the course-correction planner layer
(project/MASTER_COURSE_CORRECTION.md section 13), fully offline via an
injected fetcher. Covers: valid plans inside preferred limits, stretch
labeling, hard-limit rejection with quantified relaxations, arrival
frontcountry nights, first-come and unknown honesty, the complete-night
invariant, flexible dates, geometry, and request validation."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.planner import plan_trips, _backcountry_night
from switchback.plans import (TripRequest, validate_request,
                              complete_night_problems)

D0 = date(2026, 8, 14)


def open_fetch(first_open=None):
    """Every division open (4 sites) from first_open (default: window
    start) through the requested end."""
    def fetch(pid, divs, start, end):
        lo = first_open or start
        out = {}
        for dv in divs:
            out[dv] = {}
            d = start
            while d <= end:
                if d >= lo:
                    out[dv][d.isoformat()] = 4
                d += timedelta(days=1)
        return out
    return fetch


def req(**kw):
    base = dict(slug="rainier", start=D0, latest_start=D0, nights=2,
                party=2, pref_mi=9.0, max_mi=13.0, pref_gain=2500,
                max_gain=4500, shapes=[], first_come_ok=True,
                arrival_night=False, recovery_night=False, limit=8)
    base.update(kw)
    return TripRequest(**base)


def assert_complete(plan):
    probs = complete_night_problems(plan)
    assert not probs, f"night invariant broken: {probs}"


def scenario_within_preferred():
    res = plan_trips(req(pref_mi=12.0, pref_gain=3500),
                     fetch_fn=open_fetch())
    assert res["plans"], "open inventory must yield plans"
    great = [p for p in res["plans"] if p["fit"]["within_preferred"]]
    assert great, "a comfortable itinerary must exist and be labeled"
    assert great[0]["fit"]["label"] == "Great fit"
    for p in res["plans"]:
        assert_complete(p)
        assert p["availability_summary"] == "Bookable now"
        assert p["confidence"] == "live_inventory"
        for n in p["nights"]:
            assert n["booking"]["url"], "reservable nights carry a link"
            assert n["fetched_at"], "freshness must be stamped"


def scenario_stretch_labeled():
    res = plan_trips(req(pref_mi=6.0, pref_gain=1000),
                     fetch_fn=open_fetch())
    stretch = [p for p in res["plans"] if not p["fit"]["within_preferred"]]
    assert stretch, "days beyond preference must still appear"
    p = stretch[0]
    assert p["fit"]["label"] == "Stretch"
    assert any("above your comfortable" in t for t in p["fit"]["tradeoffs"])


def scenario_reject_over_max_miles():
    res = plan_trips(req(max_mi=0.4), fetch_fn=open_fetch())
    assert not res["plans"], "0.4 mi hard max must reject everything"
    rx = res["relaxations"]
    assert rx, "zero results must come with relaxation suggestions"
    mi = [r for r in rx if r["change"] == "max_daily_miles"]
    assert not mi, "no modest mileage bump rescues a 0.4 mi max"
    res2 = plan_trips(req(max_mi=0.7), fetch_fn=open_fetch())
    assert not res2["plans"]
    mi2 = [r for r in res2["relaxations"] if r["change"] == "max_daily_miles"]
    assert mi2 and mi2[0]["to"] == 0.8 and mi2[0]["plans"] > 0, \
        "the minimum quantified bump is 0.7 to 0.8 miles (Nickel Creek)"


def scenario_reject_over_max_gain():
    res = plan_trips(req(max_gain=150), fetch_fn=open_fetch())
    assert not res["plans"], "150 ft hard max must reject everything"
    g = [r for r in res["relaxations"] if r["change"] == "max_daily_gain"]
    assert g and g[0]["to"] == 225 and g[0]["plans"] > 0, \
        "150 to 225 ft opens the Sunrise Camp basecamp (214 ft round trip)"


def scenario_arrival_frontcountry_and_unknown():
    res = plan_trips(req(arrival_night=True), fetch_fn=open_fetch())
    assert res["plans"]
    for p in res["plans"]:
        assert_complete(p)
        first = p["nights"][0]
        assert first["date"] == (D0 - timedelta(days=1)).isoformat()
        assert first["stay_type"] in ("frontcountry_campground", "unplanned")
        if first["stay_type"] == "frontcountry_campground":
            if first["policy"] == "reservation":
                assert first["availability"] == "unknown", \
                    "unfetched inventory must read unknown, never available"
            else:
                assert first["availability"] == "first_come"
            assert first["confidence"] == "curated"
        else:
            assert p["warnings"], "unplanned nights must carry a warning"
        assert p["days"][0]["kind"] == "travel"


def scenario_backcountry_only():
    res = plan_trips(req(), fetch_fn=open_fetch())
    assert res["plans"]
    for p in res["plans"]:
        assert_complete(p)
        assert all(n["stay_type"] in ("backcountry_camp", "zone")
                   for n in p["nights"])
        assert p["nights"][0]["date"] == D0.isoformat()


def scenario_first_come_honesty():
    class StubG:
        nodes = {"X": {"name": "Windy Camp", "policy": "fcfs"}}
        park = {"permit_id": "999"}
    n = _backcountry_night(StubG(), {}, "X", D0, 0, 2, "now")
    assert n["availability"] == "first_come"
    assert n["stay_type"] == "first_come_site"
    assert n["booking"]["action"] == "arrive_early"

    lreq = req(slug="lena", nights=2, shapes=["basecamp"])
    res = plan_trips(lreq, fetch_fn=open_fetch())
    for p in res["plans"]:
        for n in p["nights"]:
            if n["name"].startswith("LLL"):
                assert n["availability"] == "permit_free"
                assert n["availability"] != "reservable"


def scenario_flexible_dates():
    r = req(latest_start=D0 + timedelta(days=3))
    res = plan_trips(r, fetch_fn=open_fetch(first_open=D0 +
                                            timedelta(days=2)))
    assert res["plans"], "later starts inside the window must be found"
    for p in res["plans"]:
        assert p["start"] >= (D0 + timedelta(days=2)).isoformat(), \
            "no plan may start on a closed night"
    assert any(p["alternate_starts"] for p in res["plans"]), \
        "the other open start should surface as an alternate"


def scenario_date_shift_relaxation():
    res = plan_trips(req(), fetch_fn=open_fetch(first_open=D0 +
                                                timedelta(days=2)))
    assert not res["plans"]
    sh = [r for r in res["relaxations"] if r["change"] == "shift_dates"]
    assert sh and sh[0]["to"] == (D0 + timedelta(days=2)).isoformat()
    assert sh[0]["plans"] > 0 and "later" in sh[0]["detail"]


def scenario_geometry():
    res = plan_trips(req(), fetch_fn=open_fetch(), include_geometry=True)
    p = res["plans"][0]
    assert "day_paths" in p and len(p["day_paths"]) == len(p["days"])
    moving = [d for d in p["days"] if d["kind"] == "hike"]
    assert moving
    for d, path in zip(p["days"], p["day_paths"]):
        if d["kind"] == "hike":
            assert len(path) >= 2 and path[0][0] is not None


def scenario_sellout_honesty_note():
    def dead_fetch(pid, divs, start, end):
        return {dv: {} for dv in divs}
    res = plan_trips(req(), fetch_fn=dead_fetch)
    assert not res["plans"]
    assert any("failed availability fetch" in n for n in res["notes"]), \
        "an all-zero window must warn it may be a network failure"


def scenario_validation():
    _r, errs = validate_request({})
    assert any("destination" in e for e in errs)
    assert any("date" in e for e in errs)
    _r, errs = validate_request({"slug": "rainier", "start": "2026-08-14",
                                 "max_mi": 6, "pref_mi": 10})
    assert any("below your preferred miles" in e for e in errs)
    _r, errs = validate_request({"slug": "rainier", "start": "2026-08-14",
                                 "shapes": ["teleport"]})
    assert any("unknown trip shape" in e for e in errs)
    r, errs = validate_request({"slug": "rainier", "start": "2026-08-14",
                                "shapes": "loop,basecamp", "nights": 2})
    assert not errs and r.shapes == ["loop", "basecamp"]
    assert r.latest_start == r.start


def main():
    scenario_within_preferred()
    scenario_stretch_labeled()
    scenario_reject_over_max_miles()
    scenario_reject_over_max_gain()
    scenario_arrival_frontcountry_and_unknown()
    scenario_backcountry_only()
    scenario_first_come_honesty()
    scenario_flexible_dates()
    scenario_date_shift_relaxation()
    scenario_geometry()
    scenario_sellout_honesty_note()
    scenario_validation()
    print("PLANNER OK: 12 golden scenarios green (complete-night "
          "invariant, honesty labels, relaxations, geometry)")


if __name__ == "__main__":
    main()
