"""
switchback.edit: the controlled edit subset on a selected recommendation.

Per project/MASTER_COURSE_CORRECTION.md section 8 the editor grows out
of a chosen trip, not a separate drawing mode. Four operations,
deliberately narrow: swap the camp on one night, add a layover night,
remove a layover night, and reverse the direction of travel.

Every edit is re-validated from scratch against the same request limits
and the same availability the search used. An edit that would break the
trip is REFUSED with the specific reason, never quietly accepted and
never silently repaired into something else. What comes back is a full
TripPlan built by the same planner code path as a searched one, so the
complete-night invariant, the policy and availability separation, and
the freshness labels all hold identically.

Options are computed by actually attempting the edit rather than by a
parallel set of rules, so what the interface offers and what the engine
accepts cannot drift apart.
"""
from datetime import date, timedelta

from .graph import Graph
from .planner import (_build_plan, _copy_req, _short, _solver_for,
                      availability_window)
from .scoring import Scorer
from .solver import fetch_for_graph

OPS = ("swap_camp", "add_layover", "remove_layover", "reverse")


def _as_date(v):
    return v if isinstance(v, date) else date.fromisoformat(str(v))


def route_of(plan):
    """The stable route identity of a plan: the same {entrance, seq,
    start} block the GPX export already round-trips."""
    gpx = plan.get("gpx") or {}
    return {"entrance": gpx.get("entrance"), "seq": list(gpx.get("seq") or []),
            "start": gpx.get("start")}


def _edited_sequence(g, seq, op, night, camp):
    """(new_seq, plain sentence) for an operation, or ValueError with a
    plain reason the interface can show as is."""
    seq = list(seq)
    if op == "reverse":
        if len(seq) < 2:
            raise ValueError("A one night trip has no direction to reverse.")
        if seq == seq[::-1]:
            raise ValueError(
                "This trip sleeps in the same order either way, so "
                "reversing it would give you the same trip.")
        return seq[::-1], "Reversed the direction of travel."

    if night is None or not (0 <= night < len(seq)):
        raise ValueError(f"There is no night {night} on this trip; it has "
                         f"{len(seq)} backcountry night(s).")

    if op == "swap_camp":
        if not camp:
            raise ValueError("Pick a camp to move that night to.")
        if camp not in g.nodes:
            raise ValueError("That camp is not on the map for this trip.")
        if camp == seq[night]:
            raise ValueError(f"Night {night + 1} is already at "
                             f"{_short(g.name(camp))}.")
        was = _short(g.name(seq[night]))
        seq[night] = camp
        return seq, (f"Moved night {night + 1} from {was} to "
                     f"{_short(g.name(camp))}.")

    if op == "add_layover":
        stay = seq[night]
        return (seq[:night] + [stay] + seq[night:],
                f"Added a second night at {_short(g.name(stay))}, so the "
                f"trip is now {len(seq) + 1} nights.")

    if op == "remove_layover":
        stay = seq[night]
        same = [i for i in (night - 1, night + 1)
                if 0 <= i < len(seq) and seq[i] == stay]
        if not same:
            raise ValueError(
                f"Night {night + 1} at {_short(g.name(stay))} is not a "
                f"layover; you sleep somewhere else the night before and "
                f"the night after, so removing it would leave a gap.")
        if len(seq) < 2:
            raise ValueError("A trip needs at least one backcountry night.")
        return (seq[:night] + seq[night + 1:],
                f"Dropped one night at {_short(g.name(stay))}, so the trip "
                f"is now {len(seq) - 1} nights.")

    raise ValueError(f"Unknown edit: {op}.")


def _walk_problems(g, solver, req, ent, seq, start):
    """Plain-language reasons an edited trip does not work, in trip
    order: unwalkable or over-limit days first, then closed nights."""
    problems = []
    stops = [ent] + list(seq) + [ent]
    for i, (a, b) in enumerate(zip(stops, stops[1:]), 1):
        if a == b:
            continue
        mi, gain, _ = solver._leg(a, b)
        an, bn = _short(g.name(a)), _short(g.name(b))
        if mi is None:
            problems.append(f"Day {i}: there is no mapped trail from {an} "
                            f"to {bn}.")
            continue
        if mi > req.max_mi:
            problems.append(f"Day {i} would be {mi} miles from {an} to "
                            f"{bn}, past your {req.max_mi:g} mile limit.")
        if gain > req.max_gain:
            problems.append(f"Day {i} would climb {gain:,} ft from {an} to "
                            f"{bn}, past your {req.max_gain:,} ft limit.")
    for i, c in enumerate(seq):
        d = start + timedelta(days=i)
        if not solver.open_night(c, d):
            problems.append(f"{_short(g.name(c))} has no open site for "
                            f"{req.party} on {d.isoformat()}.")
    return problems


def _prepare(req, route, graph, availability, fetch_fn, nights):
    """(graph, availability, request pinned to this trip) for a
    sequence of the given length."""
    pinned = _copy_req(req, nights=nights, start=_as_date(route["start"]),
                       latest_start=_as_date(route["start"]))
    g = graph or Graph(pinned.slug)
    av = availability
    if av is None:
        fs, fe = availability_window(pinned)
        av = fetch_for_graph(g, g.camps(), fs, fe, fetch_fn=fetch_fn)
    return g, av, pinned


def apply_edit(req, route, op, night=None, camp=None, fetch_fn=None,
               availability=None, graph=None, now=None,
               include_geometry=False):
    """Apply one edit to a selected trip.

    Returns {"ok": True, "plan": ..., "change": sentence} or
    {"ok": False, "reason": sentence, "problems": [...]}. A refusal is
    a real answer: it names what broke, so the interface never has to
    invent an explanation."""
    from datetime import datetime, timezone
    if op not in OPS:
        return {"ok": False, "reason": f"Unknown edit: {op}.",
                "problems": []}
    ent, seq = route.get("entrance"), list(route.get("seq") or [])
    if not ent or not seq:
        return {"ok": False, "reason": "That trip has no route to edit.",
                "problems": []}
    start = _as_date(route["start"])

    probe = graph or Graph(req.slug)
    try:
        new_seq, change = _edited_sequence(probe, seq, op, night, camp)
    except ValueError as ex:
        return {"ok": False, "reason": str(ex), "problems": []}

    g, av, pinned = _prepare(req, route, probe, availability, fetch_fn,
                             len(new_seq))
    solver = _solver_for(g, av, pinned)
    problems = _walk_problems(g, solver, pinned, ent, new_seq, start)
    if problems:
        return {"ok": False, "problems": problems,
                "reason": "That change does not work: " + problems[0]}

    when = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    row = {"start": start, "entrance": ent, "seq": tuple(new_seq),
           "type": solver.classify(ent, new_seq),
           "days": solver.day_stats(ent, new_seq)}
    plan = _build_plan(pinned, g, av, solver, {"best": row, "dates": [start]},
                       when, include_geometry, scorer=Scorer(g))
    plan["edited"] = {"op": op, "change": change}
    return {"ok": True, "plan": plan, "change": change,
            "request": pinned.to_dict(), "checked_at": when}


def edit_options(req, route, fetch_fn=None, availability=None, graph=None,
                 limit=8):
    """What this trip can be changed into, night by night.

    Each option is one the engine has already accepted, because the
    only test applied here is the edit itself."""
    ent, seq = route.get("entrance"), list(route.get("seq") or [])
    if not ent or not seq:
        return {"nights": [], "can_reverse": False,
                "reverse_reason": "That trip has no route to edit."}
    start = _as_date(route["start"])
    g, av, pinned = _prepare(req, route, graph, availability, fetch_fn,
                             len(seq))
    solver = _solver_for(g, av, pinned)
    stops = [ent] + seq + [ent]

    def works(candidate_seq):
        return not _walk_problems(g, solver, pinned, ent, candidate_seq,
                                  start)

    nights = []
    for i, camp in enumerate(seq):
        d = start + timedelta(days=i)
        swaps = []
        for c in solver.camps:
            if c == camp:
                continue
            trial = list(seq)
            trial[i] = c
            if not works(trial):
                continue
            mi_in, gain_in, _ = solver._leg(stops[i], c)
            mi_out, gain_out, _ = solver._leg(c, stops[i + 2])
            node = g.nodes.get(c) or {}
            swaps.append({
                "id": c, "name": _short(g.name(c)),
                "miles_in": mi_in, "gain_in": gain_in,
                "miles_out": mi_out, "gain_out": gain_out,
                "remaining": (av.get(c) or {}).get(d.isoformat()),
                "policy": node.get("policy", "reservation"),
                "lake": bool(node.get("lake"))})
        swaps.sort(key=lambda s: ((s["miles_in"] or 0)
                                  + (s["miles_out"] or 0)))
        add = seq[:i] + [camp] + seq[i:]
        drop = seq[:i] + seq[i + 1:]
        nights.append({
            "night": i, "date": d.isoformat(), "camp": camp,
            "name": _short(g.name(camp)),
            "swap_to": swaps[:limit], "swap_count": len(swaps),
            "can_add_layover": works(add),
            "can_remove_layover": bool(drop) and works(drop)
            and any(seq[j] == camp for j in (i - 1, i + 1)
                    if 0 <= j < len(seq))})

    can_reverse, reverse_reason = False, None
    try:
        rev, _ = _edited_sequence(g, seq, "reverse", None, None)
        can_reverse = works(rev)
        if not can_reverse:
            reverse_reason = _walk_problems(g, solver, pinned, ent, rev,
                                            start)[0]
    except ValueError as ex:
        reverse_reason = str(ex)
    return {"route": {"entrance": ent, "seq": seq,
                      "start": start.isoformat()},
            "nights": nights, "can_reverse": can_reverse,
            "reverse_reason": reverse_reason}
