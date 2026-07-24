"""
switchback.tread: trail-surface difficulty, the half of "how hard" that
grade does not capture.

Grade (steepness) is modeled by pace.py. Tread is the other axis: a mile
of smooth graded trail and a mile of rock, roots, talus, or scree at the
SAME grade are very different days. OpenStreetMap does not carry this for
US wilderness trails (probed empty 2026-07-22: sac_scale and surface are
blank or uniform, and the Upper Lena grind is tagged like a flat path),
so tread is CURATED per edge from AllTrails difficulty and review color
plus owner ground truth, recorded with a src like every other edge fact.
Unknown tread contributes nothing, the honest default.

Owner framing (2026-07-22): rough ground makes a day effectively harder,
"2,000 ft on a rooty trail counts like more". So each rough mile adds
effective climb, which flows into the comfortable-day fit exactly like
real gain does. The per-mile surcharges are hand-set and tunable (like
the pace bands), anchored to the owner's Lena report: Lower to Upper Lena
is about 3.5 mi over rock and roots that he calls brutal, so at "rough"
its ~2,500 ft of real climb reads closer to 3,700 ft of effort.
"""

# ordinal, easy to hard
TREAD_CLASSES = ("smooth", "moderate", "rough", "very_rough")

TREAD_LABELS = {
    "smooth": "smooth tread",
    "moderate": "typical tread",
    "rough": "rough footing, rock and roots",
    "very_rough": "very rough, talus or scramble",
}

# effective feet of climb ADDED per mile of this tread, on top of the real
# grade. "moderate" is the baseline the pace and effort model already
# assumes, so it and "smooth" add nothing; only rough ground is a penalty.
DEFAULT_TREAD_SURCHARGE = {
    "smooth": 0,
    "moderate": 0,
    "rough": 350,
    "very_rough": 750,
}


def normalize_tread(spec=None):
    """User tread-surcharge spec -> full table. Accepts None (defaults) or
    a dict of class overrides in ft per mile. Returns (table, errors)."""
    table = dict(DEFAULT_TREAD_SURCHARGE)
    errors = []
    if spec is None:
        return table, errors
    if not isinstance(spec, dict):
        return table, ["tread must be a table of feet-per-mile surcharges"]
    for k, v in spec.items():
        if k not in DEFAULT_TREAD_SURCHARGE:
            errors.append(f"unknown tread class: {k}")
            continue
        try:
            table[k] = max(0, int(v))
        except (TypeError, ValueError):
            errors.append(f"tread {k} must be feet per mile")
    return table, errors


def path_tread(g, path, table=None):
    """(miles_by_tread, effective_gain_surcharge_ft, worst_tread) for a
    node path, from each edge's curated tread. Edges with unknown tread
    count as typical (no surcharge). Cheap: one adjacency scan per hop."""
    table = table or DEFAULT_TREAD_SURCHARGE
    tread_map = getattr(g, "tread", None) or {}
    miles_by, surcharge, worst_idx = {}, 0.0, -1
    for a, b in zip(path, path[1:]):
        entry = next((e for e in g.adj.get(a, []) if e[0] == b), None)
        if not entry:
            continue
        miles, key = entry[1], entry[4]
        tread = tread_map.get(key)
        if not tread:
            continue
        miles_by[tread] = miles_by.get(tread, 0.0) + miles
        surcharge += miles * table.get(tread, 0)
        if tread in TREAD_CLASSES:
            worst_idx = max(worst_idx, TREAD_CLASSES.index(tread))
    worst = TREAD_CLASSES[worst_idx] if worst_idx >= 0 else None
    return ({k: round(v, 1) for k, v in miles_by.items()},
            int(round(surcharge)), worst)


def describe_tread(miles_by):
    """Plain-language tread note for a day, roughest first. Empty string
    when the day is all smooth, typical, or unknown."""
    parts = []
    for cls in reversed(TREAD_CLASSES):
        if cls in ("smooth", "moderate"):
            continue
        if miles_by.get(cls):
            parts.append(f"{miles_by[cls]} mi {TREAD_LABELS[cls]}")
    return ", ".join(parts)
