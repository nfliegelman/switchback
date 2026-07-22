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


# plain-language difficulty buckets by grade magnitude, for the
# calibration sheet and any surface that describes a day's terrain.
# Gentle grades (under 10%) feel the same up or down, so they share one
# bucket; steeper grades split by direction, because a steep descent is
# its own kind of hard and must never be counted as a climb (owner catch
# 2026-07-22: a -20% descent was landing in the same "steep (20-30%)"
# bucket as a +20% climb, so steep downhill was invisible on the sheet).
_MAG_BUCKETS = (("easy (under 10%)", 0, 10),
                ("moderate (10-20%)", 10, 20),
                ("steep (20-30%)", 20, 30),
                ("very steep (30%+)", 30, None))

# canonical output order: gentle to steep, uphill before downhill, so a
# terrain line always reads as one consistent progression.
_BUCKET_ORDER = (
    "easy (under 10%)",
    "moderate uphill (10-20%)", "moderate downhill (10-20%)",
    "steep uphill (20-30%)", "steep downhill (20-30%)",
    "very steep uphill (30%+)", "very steep downhill (30%+)",
)


def _bucket_label(grade_pct):
    """Direction-aware difficulty label for one signed grade. Gentle
    grades stay direction-neutral; 10%+ grades carry uphill/downhill."""
    g = abs(grade_pct)
    for label, lo, hi in _MAG_BUCKETS:
        if g >= lo and (hi is None or g < hi):
            if lo == 0:
                return label
            base, paren = label.split(" (")
            side = "uphill" if grade_pct >= 0 else "downhill"
            return f"{base} {side} ({paren}"
    return _MAG_BUCKETS[0][0]


def bucket_miles(sections):
    """{direction-aware difficulty label: miles}, zero buckets omitted,
    ordered gentle to steep so a steep descent is never lumped with a
    steep climb (owner catch 2026-07-22)."""
    out = {}
    for s in sections:
        label = _bucket_label(s["grade_pct"])
        out[label] = out.get(label, 0.0) + s["len_mi"]
    rounded = {k: round(v, 1) for k, v in out.items() if round(v, 1) > 0}
    return {k: rounded[k] for k in _BUCKET_ORDER if k in rounded}


def _turning_points(elev_ft, tol_ft):
    """Indices of local peaks and valleys, ignoring wiggles smaller
    than tol_ft. Always includes the first and last sample."""
    n = len(elev_ft)
    out = [0]
    direction, ext = 0, 0
    for i in range(1, n):
        if direction == 0:
            if elev_ft[i] - elev_ft[0] > tol_ft:
                direction, ext = 1, i
            elif elev_ft[0] - elev_ft[i] > tol_ft:
                direction, ext = -1, i
        elif direction == 1:
            if elev_ft[i] >= elev_ft[ext]:
                ext = i
            elif elev_ft[ext] - elev_ft[i] > tol_ft:
                out.append(ext)
                direction, ext = -1, i
        else:
            if elev_ft[i] <= elev_ft[ext]:
                ext = i
            elif elev_ft[i] - elev_ft[ext] > tol_ft:
                out.append(ext)
                direction, ext = 1, i
    if out[-1] != n - 1:
        out.append(n - 1)
    return out


def climb_profile(mi, elev_ft, min_climb_ft=200, tol_ft=80):
    """Distinct climbs in a day (owner ask 2026-07-20: repeated
    up-down-up-down must be visible, not smeared into one gain
    number). A climb runs until the trail drops more than tol_ft from
    its high point; climbs smaller than min_climb_ft are ignored.
    Returns [{gain_ft, len_mi, avg_grade_pct}] in trail order."""
    if not mi or len(mi) < 2:
        return []
    tp = _turning_points(elev_ft, tol_ft)
    climbs = []
    for a, b in zip(tp, tp[1:]):
        gain = elev_ft[b] - elev_ft[a]
        length = mi[b] - mi[a]
        if gain >= min_climb_ft and length > 0:
            climbs.append({"gain_ft": int(round(gain)),
                           "len_mi": round(length, 1),
                           "avg_grade_pct": round(
                               gain / (length * FT_PER_MI) * 100, 1)})
    return climbs


def ascent_descent(elev_ft):
    """(total ft up, total ft down) across a profile."""
    up = sum(max(0.0, b - a) for a, b in zip(elev_ft, elev_ft[1:]))
    dn = sum(max(0.0, a - b) for a, b in zip(elev_ft, elev_ft[1:]))
    return int(round(up)), int(round(dn))


def describe_trace(mi, elev_ft, pace=None, n_sections=40,
                   include_time=True, include_updown=True):
    """One objective plain-language line for a day's profile: miles by
    grade bucket first, then the distinct climbs (so rolling
    up-down-up terrain is visible), then total up and down, and the
    time estimate LAST, deliberately (owner 2026-07-20: mileage,
    elevation, and grade are the focus; time is a nice end result).
    The calibration sheet passes include_time=False and
    include_updown=False: no time there at all, and up/down lives on
    the day line from graph figures, so one row never shows two
    slightly different totals. Empty string if the trace is
    unusable."""
    sections = grade_sections(mi, elev_ft, n_sections=n_sections)
    if not sections:
        return ""
    parts = [", ".join(f"{v} mi {k}"
                       for k, v in bucket_miles(sections).items())]
    climbs = climb_profile(mi, elev_ft)
    if len(climbs) == 1:
        c = climbs[0]
        parts.append(f"one climb of {c['gain_ft']:,} ft at about "
                     f"{c['avg_grade_pct']:g}%")
    elif climbs:
        detail = ", ".join(f"{c['gain_ft']:,} ft at {c['avg_grade_pct']:g}%"
                           for c in climbs[:4])
        more = f" and {len(climbs) - 4} more" if len(climbs) > 4 else ""
        parts.append(f"{len(climbs)} separate climbs: {detail}{more}")
    if include_updown:
        up, dn = ascent_descent(elev_ft)
        parts.append(f"+{up:,} ft up, -{dn:,} ft down")
    if include_time:
        pace = pace or DEFAULT_PACE_MPH
        hours = hours_for_sections(sections, pace)
        parts.append(f"about {format_hours(hours)} at a typical pace")
    return "; ".join(parts)


def format_hours(h):
    """2.74 -> '2 h 45 min'; 0.4 -> '25 min'."""
    m = int(round(h * 60))
    if m < 60:
        return f"{m} min"
    return f"{m // 60} h {m % 60:02d} min" if m % 60 else f"{m // 60} h"


def leg_updown(g, path):
    """(total ft climbed, total ft descended) along a node path,
    from the graph's directional edge gains; the reverse adjacency
    entry carries each edge's descent. Offline and instant."""
    up = down = 0.0
    for a, b in zip(path, path[1:]):
        fwd = next(((m, gn) for o, m, gn, _e, _k in g.adj.get(a, [])
                    if o == b), None)
        if not fwd:
            continue
        up += fwd[1] or 0
        down += next((gn for o, _m, gn, _e, _k in g.adj.get(b, [])
                      if o == a), 0) or 0
    return int(round(up)), int(round(down))


def direction_word(up_ft, down_ft):
    """A day's character in two words: a mostly-downhill hike must
    never read as a climb (owner catch, Sunrise to Mystic 2026-07-20).
    Empty string when the day has no meaningful relief."""
    if max(up_ft, down_ft) < 400:
        return "gentle"
    if down_ft > 1.5 * up_ft:
        return "mostly downhill"
    if up_ft > 1.5 * down_ft:
        return "mostly climbing"
    return "rolling, real climbing both directions"


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
