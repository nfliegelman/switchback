"""The /api/plan surface, offline via an injected fetcher: structured
TripPlans with complete nights and geometry come back over HTTP, invalid
requests get plain-language errors, and the plan GPX export round-trips
through the existing exporter."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from switchback.plans import complete_night_problems
from switchback.web import create_app

D0 = date(2026, 8, 14)


def make_fetch():
    def fetch(pid, divs, start, end):
        out = {}
        for dv in divs:
            out[dv] = {}
            d = start
            while d <= end:
                out[dv][d.isoformat()] = 3
                d += timedelta(days=1)
        return out
    return fetch


def main():
    client = TestClient(create_app(fetch_fn=make_fetch()))

    defs = client.get("/api/plan/defaults").json()
    assert defs["max_mi"] and defs["pref_mi"], "form defaults must exist"

    r = client.post("/api/plan", json={
        "slug": "rainier", "start": D0.isoformat(), "nights": 2,
        "party": 2, "pref_mi": 9, "max_mi": 13, "pref_gain": 2500,
        "max_gain": 4500, "shapes": ["loop", "out and back", "basecamp"],
        "arrival_night": True})
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["plans"], "open inventory must yield plans over HTTP"
    assert res["request"]["max_mi"] == 13, "request must be echoed"
    p = res["plans"][0]
    assert not complete_night_problems(p)
    assert p["trip_window"]["first_night"] < p["start"], \
        "an arrival-night plan declares its window from the night before"
    assert p["nights"][0]["stay_type"] in ("frontcountry_campground",
                                           "unplanned")
    for n in p["nights"]:
        assert n["policy"] in ("reservable", "first_come", "walk_up",
                               "permit_free", "unknown")
        assert n["availability"] in ("available", "limited", "full",
                                     "not_released", "unknown")
    assert p["day_paths"], "the map needs geometry for the selection"
    assert p["checked_at"] and p["availability_summary"]
    assert "score" not in p, "raw solver scores stay internal"

    bad = client.post("/api/plan", json={
        "slug": "rainier", "start": D0.isoformat(),
        "pref_mi": 12, "max_mi": 8})
    assert bad.status_code == 400
    assert "below your preferred miles" in bad.text

    gx = client.post("/api/plan/gpx", json={
        "slug": p["gpx"]["entrance"] and "rainier",
        "entrance": p["gpx"]["entrance"], "seq": p["gpx"]["seq"],
        "start": p["gpx"]["start"], "title": p["title"]})
    assert gx.status_code == 200 and gx.text.startswith("<?xml")
    assert "<trk>" in gx.text and "Switchback" in gx.text

    print(f"PLAN API OK: {len(res['plans'])} plans, first has "
          f"{len(p['nights'])} night records and GPX export works")


if __name__ == "__main__":
    main()
