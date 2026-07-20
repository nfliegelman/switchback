"""
switchback.pace: grade-aware hiking speed and duration estimates.

Owner-requested 2026-07-20: one mile at 45 percent grade can dominate
an otherwise flat day, so duration and difficulty must come from
grade, not distance alone. Two data paths:

1. Trail-true: an elevation trace (the parallel mi/elev_ft arrays
   day_toughness already produces) is split into equal-length
   sections (default 20, the owner's number), each section gets an
   average grade, and time is the sum of section length over the
   banded speed for that grade. This is the accurate view and powers
   the day-profile panel.

2. Edge fallback, fully offline: the graph knows each edge's miles,
   climb, and descent. The edge is modeled as a climbing portion and
   a descending portion sharing one characteristic grade,
   total relief / distance. This smooths out short walls inside long
   edges (the trace view does not), but it is instant, needs no
   network, and still flags edges whose whole character is steep.

Speeds are a banded table of miles per hour by grade, defaulted for a
loaded backpacker and informed by Tobler's hiking function (fastest
slightly downhill, slowing toward both extremes). The user can scale
the whole table with a single factor or override any band, per search
or via a "pace" object in profile.json.
"""

# (band key, lower grade pct exclusive, upper inclusive), top-down.
# Grade is rise over run in percent; negative is descent.
BANDS = (
    ("up_30_plus", 30, None),
    ("up_20_30", 20, 30),
    ("up_10_20", 10, 20),
    ("up_3_10", 3, 10),
    ("flat", -3, 3),
    ("down_3_10", -10, -3),
    ("down_10_20", -20, -10),
    ("down_20_30", -30, -20),
    ("down_30_plus", None, -30),
)

# Loaded-pack defaults, mph. A fit unloaded pair (the owner's own
# numbers) runs faster; scale with speed_factor or override bands.
DEFAULT_PACE_MPH = {
    "up_30_plus": 1.0,
    "up_20_30": 1.4,
    "up_10_20": 1.8,
    "up_3_10": 2.1,
    "flat": 2.3,
    "down_3_10": 2.5,
    "down_10_20": 2.1,
    "down_20_30": 1.6,
    "down_30_plus": 1.2,
}

FT_PER_MI = 5280.0


def band_for(grade_pct):
    for key, lo, hi in BANDS:
        if (lo is None or grade_pct > lo) and (hi is None or grade_pct <= hi):
            return key
    return "flat"


def normalize_pace(spec=None):
    """User pace spec -> full band table. Accepts None (defaults), a
    bare number (factor scaling every band, 0.5 to 1.5), or a dict of
    band overrides in mph plus an optional speed_factor. Returns
    (table, errors)."""
    table = dict(DEFAULT_PACE_MPH)
    errors = []
    if spec is None:
        return table, errors
    if isinstance(spec, (int, float)):
        spec = {"speed_factor": spec}
    if not isinstance(spec, dict):
        return table, ["pace must be a number or a table of speeds"]
    factor = spec.get("speed_factor", 1.0)
    try:
        factor = float(factor)
    except (TypeError, ValueError):
        errors.append("pace speed_factor must be a number")
        factor = 1.0
    if not 0.5 <= factor <= 1.5:
        errors.append("pace speed_factor must be between 0.5 and 1.5")
        factor = min(max(factor, 0.5), 1.5)
    for k in table:
        table[k] = round(table[k] * factor, 2)
    for k, v in spec.items():
        if k == "speed_factor":
            continue
        if k not in DEFAULT_PACE_MPH:
            errors.append(f"unknown pace band: {k}")
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            errors.append(f"pace band {k} must be miles per hour")
            continue
        if not 0.3 <= v <= 6.0:
            errors.append(f"pace band {k} must be between 0.3 and 6 mph")
            continue
        table[k] = v
    return table, errors


def speed_for(grade_pct, pace):
    return pace[band_for(grade_pct)]


# --------------------- trail-true trace analysis ---------------------------
def grade_sections(mi, elev_ft, n_sections=20):
    """Split a profile (parallel cumulative-miles and elevation-ft
    arrays) into up to n_sections equal-length sections. Returns
    [{start_mi, len_mi, grade_pct}]. Sections shorter than 50 ft of
    trail are merged forward."""
    if not mi or len(mi) < 2 or mi[-1] <= 0:
        return []
    total = mi[-1]
    n = max(1, min(n_sections, len(mi) - 1))
    step = total / n
    sections = []
    j = 0
    for i in range(n):
        lo, hi = i * step, (i + 1) * step
        while j < len(mi) - 1 and mi[j + 1] <= lo:
            j += 1
        k = j
        while k < len(mi) - 1 and mi[k + 1] < hi:
            k += 1
        e0 = _elev_at(mi, elev_ft, lo)
        e1 = _elev_at(mi, elev_ft, hi)
        length = hi - lo
        grade = (e1 - e0) / (length * FT_PER_MI) * 100 if length else 0.0
        sections.append({"start_mi": round(lo, 2),
                         "len_mi": round(length, 3),
                         "grade_pct": round(grade, 1)})
    return sections


def _elev_at(mi, elev_ft, x):
    """Linear interpolation of elevation at cumulative mile x."""
    if x <= mi[0]:
        return elev_ft[0]
    for i in range(1, len(mi)):
        if mi[i] >= x:
            span = mi[i] - mi[i - 1]
            if span <= 0:
                return elev_ft[i]
            t = (x - mi[i - 1]) / span
            return elev_ft[i - 1] + t * (elev_ft[i] - elev_ft[i - 1])
    return elev_ft[-1]


def hours_for_sections(sections, pace):
    return round(sum(s["len_mi"] / speed_for(s["grade_pct"], pace)
                     for s in sections), 2)


def steep_summary(sections, threshold_pct=30):
    """(steepest_grade_pct, miles at or above the uphill threshold)."""
    if not sections:
        return 0.0, 0.0
    steepest = max(s["grade_pct"] for s in sections)
    steep_mi = sum(s["len_mi"] for s in sections
                   if s["grade_pct"] >= threshold_pct)
    return round(steepest, 1), round(steep_mi, 2)


# ------------------------- edge-level fallback ------------------------------
def edge_hours(miles, up_ft, down_ft, pace):
    """Duration for one edge modeled as a climb portion and a descent
    portion sharing the characteristic grade relief/distance. Returns
    (hours, characteristic_up_grade_pct)."""
    if not miles or miles <= 0:
        return 0.0, 0.0
    up_ft = max(up_ft or 0, 0)
    down_ft = max(down_ft or 0, 0)
    relief = up_ft + down_ft
    if relief <= 0:
        return miles / speed_for(0, pace), 0.0
    grade = relief / (miles * FT_PER_MI) * 100
    d_up = miles * up_ft / relief
    d_dn = miles - d_up
    hours = 0.0
    if d_up:
        hours += d_up / speed_for(grade, pace)
    if d_dn:
        hours += d_dn / speed_for(-grade, pace)
    return hours, round(grade, 1)


def format_hours(h):
    """2.74 -> '2 h 45 min'; 0.4 -> '25 min'."""
    m = int(round(h * 60))
    if m < 60:
        return f"{m} min"
    return f"{m // 60} h {m % 60:02d} min" if m % 60 else f"{m // 60} h"


def leg_hours(g, path, pace):
    """Duration and steepness for a day's node path through the graph.
    Returns (hours, steepest_up_grade_pct) from per-edge climb and
    descent figures; the reverse adjacency entry carries the descent."""
    total, steepest = 0.0, 0.0
    for a, b in zip(path, path[1:]):
        fwd = next(((m, gn) for o, m, gn, _e, _k in g.adj.get(a, [])
                    if o == b), None)
        if not fwd:
            continue
        m, up = fwd
        down = next((gn for o, _m, gn, _e, _k in g.adj.get(b, [])
                     if o == a), 0)
        h, grade = edge_hours(m, up, down, pace)
        total += h
        steepest = max(steepest, grade)
    return round(total, 2), steepest
