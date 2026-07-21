"""Grade-aware pace invariants (owner-requested 2026-07-20): banded
speeds by grade, 20-section trace analysis that catches a short 45
percent wall inside an otherwise flat day, edge-level fallback math,
and the user pace controls."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.pace import (DEFAULT_PACE_MPH, band_for, edge_hours,
                             format_hours, grade_sections,
                             hours_for_sections, leg_hours,
                             normalize_pace, speed_for, steep_summary)


def check_bands():
    assert band_for(45) == "up_30_plus"
    assert band_for(30) == "up_20_30", "band edges are lower-exclusive"
    assert band_for(0) == "flat"
    assert band_for(-5) == "down_3_10"
    assert band_for(-45) == "down_30_plus"
    assert speed_for(0, DEFAULT_PACE_MPH) > speed_for(45, DEFAULT_PACE_MPH)
    assert speed_for(-5, DEFAULT_PACE_MPH) >= speed_for(0, DEFAULT_PACE_MPH), \
        "gentle descent is the fastest band, per Tobler"


def check_normalize():
    table, errs = normalize_pace(None)
    assert not errs and table == DEFAULT_PACE_MPH
    table, errs = normalize_pace(0.5)
    assert not errs and table["flat"] == round(DEFAULT_PACE_MPH["flat"] * 0.5, 2)
    table, errs = normalize_pace({"up_30_plus": 1.0, "flat": 2.0})
    assert not errs and table["up_30_plus"] == 1.0 and table["flat"] == 2.0
    _t, errs = normalize_pace({"warp_speed": 9})
    assert errs and "unknown pace band" in errs[0]
    _t, errs = normalize_pace({"flat": 25})
    assert errs
    _t, errs = normalize_pace(3.0)
    assert errs, "a 3x speed factor is out of range"


def check_wall_dominates_flat_day():
    """One mile at 45 percent grade then four flat miles: the wall must
    dominate the estimate, not average away."""
    mi = [0, 1, 2, 3, 4, 5]
    wall = [0, 2376, 2376, 2376, 2376, 2376]
    flat = [0, 0, 0, 0, 0, 0]
    ws = grade_sections(mi, wall, n_sections=20)
    fs = grade_sections(mi, flat, n_sections=20)
    assert len(ws) == 5, "20 sections cap at trace resolution"
    steepest, steep_mi = steep_summary(ws)
    assert steepest == 45.0 and abs(steep_mi - 1.0) < 0.01
    pace = DEFAULT_PACE_MPH
    wall_h = hours_for_sections(ws, pace)
    flat_h = hours_for_sections(fs, pace)
    assert abs(flat_h - 5 / pace["flat"]) < 0.05
    assert wall_h > flat_h + 0.4, \
        f"the wall must cost real time: {wall_h} vs {flat_h}"
    assert abs(wall_h - (1 / pace["up_30_plus"]
                         + 4 / pace["flat"])) < 0.05


def check_sections_fine_resolution():
    """A dense trace splits into 20 sections and interpolation finds
    the wall even when it spans section boundaries."""
    n = 200
    mi = [i * 5 / n for i in range(n + 1)]
    elev = [min(x, 1.0) * 2376 for x in mi]
    s = grade_sections(mi, elev, n_sections=20)
    assert len(s) == 20 and all(abs(x["len_mi"] - 0.25) < 0.001 for x in s)
    steepest, steep_mi = steep_summary(s)
    assert steepest == 45.0 and abs(steep_mi - 1.0) < 0.01


def check_edge_fallback():
    pace = DEFAULT_PACE_MPH
    h, g = edge_hours(0.8, 791, 502, pace)
    assert abs(g - 30.6) < 0.1, "characteristic grade is relief over run"
    d_up = 0.8 * 791 / 1293
    want = d_up / pace["up_30_plus"] + (0.8 - d_up) / pace["down_30_plus"]
    assert abs(h - want) < 0.01
    h_flat, g_flat = edge_hours(2.0, 0, 0, pace)
    assert g_flat == 0 and abs(h_flat - 2 / pace["flat"]) < 0.01
    slower, _ = edge_hours(0.8, 791, 502, normalize_pace(0.5)[0])
    assert abs(slower - 2 * h) < 0.02, "half speed doubles the estimate"


def check_leg_hours_real_graph():
    from switchback.graph import Graph
    from switchback.pace import direction_word, leg_updown
    g = Graph("rainier")
    box = [e for e in g.entrances() if "Box Canyon" in g.name(e)][0]
    nickel = [c for c in g.camps() if "Nickel" in g.name(c)][0]
    path = g.leg(box, nickel)[2]
    hours, steepest = leg_hours(g, path, DEFAULT_PACE_MPH)
    assert hours > 0.5, "0.8 steep miles cannot be a 20 minute stroll"
    assert steepest >= 25, "Box Canyon to Nickel Creek reads sustained steep"
    up, down = leg_updown(g, path)
    assert (up, down) == (791, 502), "descent comes from the reverse edges"
    assert direction_word(600, 2500) == "mostly downhill", \
        "a big-descent day must never read as a climb (owner catch)"
    assert direction_word(2500, 600) == "mostly climbing"
    assert direction_word(100, 200) == "gentle"
    assert "rolling" in direction_word(1983, 2854), \
        "Sunrise to Mystic: net downhill but 2,000 ft of real climbing"


def check_buckets_and_description():
    from switchback.pace import bucket_miles, describe_trace
    mi = [0, 1, 2, 3, 4, 5]
    wall = [0, 2376, 2376, 2376, 2376, 2376]
    s = grade_sections(mi, wall, n_sections=20)
    b = bucket_miles(s)
    assert b.get("very steep (30%+)") == 1.0
    assert b.get("easy (under 10%)") == 4.0
    d = describe_trace(mi, wall)
    assert "very steep" in d and "easy" in d
    assert "one climb of 2,376 ft" in d, d
    assert d.endswith("at a typical pace"), \
        "time is listed LAST; objective terrain leads (owner 2026-07-20)"
    assert describe_trace([], []) == ""


def check_rolling_terrain_visible():
    """Owner ask: up-down-up-down must not smear into one number.
    A sawtooth of five 400 ft climbs reads as five separate climbs."""
    from switchback.pace import ascent_descent, climb_profile, describe_trace
    mi, elev = [], []
    x = 0.0
    e = 0.0
    mi.append(x); elev.append(e)
    for _ in range(5):
        for _ in range(10):          # up 400 ft over 0.5 mi
            x += 0.05; e += 40
            mi.append(round(x, 3)); elev.append(e)
        for _ in range(10):          # back down 400 ft over 0.5 mi
            x += 0.05; e -= 40
            mi.append(round(x, 3)); elev.append(e)
    climbs = climb_profile(mi, elev)
    assert len(climbs) == 5, f"five sawtooth climbs, got {len(climbs)}"
    assert all(c["gain_ft"] == 400 for c in climbs)
    up, dn = ascent_descent(elev)
    assert up == 2000 and dn == 2000
    d = describe_trace(mi, elev)
    assert "5 separate climbs" in d and "+2,000 ft up, -2,000 ft down" in d
    flat = climb_profile([0, 1, 2], [100, 110, 105])
    assert flat == [], "wiggles under the thresholds are not climbs"


def check_format_hours():
    assert format_hours(0.4) == "24 min"
    assert format_hours(2.0) == "2 h"
    assert format_hours(2.74) == "2 h 44 min"


def main():
    check_bands()
    check_normalize()
    check_wall_dominates_flat_day()
    check_sections_fine_resolution()
    check_edge_fallback()
    check_leg_hours_real_graph()
    check_buckets_and_description()
    check_rolling_terrain_visible()
    check_format_hours()
    print("PACE OK: bands, 45 percent wall detection, edge fallback, "
          "user pace controls")


if __name__ == "__main__":
    main()
