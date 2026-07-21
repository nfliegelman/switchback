"""
switchback.planner: orchestration above the solver.

Turns a validated TripRequest into complete, structured TripPlans
per project/MASTER_COURSE_CORRECTION.md. The solver stays untouched
and keeps producing feasible backcountry camp sequences; this layer
adds everything a person needs to act on one: a record for every
calendar night in the declared trip window (arrival campground,
backcountry camps, recovery campground, or an explicit unplanned gap),
booking policy separated from current availability, freshness,
booking actions, plain-language reasons and tradeoffs, and quantified
relaxation suggestions when nothing fits.

Hard limits come from the request, never silently from profile.json.
A campground closed for a requested night is never offered for it.
Every built plan is checked against the complete-night invariant
before it leaves this module.
"""
from datetime import datetime, timedelta, timezone

from .frontcountry import options_for_entrance
from .graph import Graph
from .pace import (DEFAULT_PACE_MPH, format_hours, leg_hours, speed_for)
from .plans import (BookingAction, NightStay, TripDay, TripPlan,
                    TripWarning, complete_night_problems,
                    overall_confidence)
from .report import dedupe_routes
from .scoring import Scorer
from .solver import Solver, fetch_for_graph

_SHAPE_LABEL = {"loop": "Loop", "out_and_back": "Out and Back",
                "lollipop": "Lollipop", "basecamp": "Basecamp",
                "mixed": "Route"}
# graph node policy -> consumer booking policy
_POLICY_MAP = {"reservation": "reservable", "fcfs": "first_come",
               "none": "permit_free"}
# at or below this many open sites a night reads "limited"
_LIMITED_AT = 2
# extra days fetched past the window so date-shift relaxations can be
# quantified without a second network pass
_SHIFT_DAYS = 3


class PlannerError(Exception):
    pass


def availability_window(req):
    """(start, end) of the availability fetch a request needs."""
    return (req.start,
            req.latest_start + timedelta(days=req.nights + _SHIFT_DAYS))


def _short(name):
    return name.split(" - ")[0].strip()


def _node_policy(node):
    return _POLICY_MAP.get(node.get("policy", "reservation"), "unknown")


def _solver_for(g, av, req, basecamp_ok=None, max_mi=None, max_gain=None):
    if basecamp_ok is None:
        basecamp_ok = not req.shapes or "basecamp" in req.shapes
    if not req.first_come_ok:
        av = {c: d for c, d in av.items()
              if c not in g.nodes
              or g.nodes[c].get("policy", "reservation") == "reservation"}
    return Solver(g, av, party=req.party, nights=req.nights,
                  max_mi=max_mi or req.max_mi,
                  max_gain=max_gain or req.max_gain,
                  basecamp_ok=basecamp_ok)


def _rows(g, av, req, start=None, latest=None, **overrides):
    s = _solver_for(g, av, req, **overrides)
    return s, s.batch(g.entrances(), start or req.start,
                      latest or req.latest_start,
                      trip_types=req.shapes or None)


# ------------------------- night construction ------------------------------
def _backcountry_night(g, av, camp, d, i, party, fetched_at):
    n = g.nodes[camp]
    policy = _node_policy(n)
    name = _short(n["name"])
    if policy == "reservable":
        remaining = (av.get(camp) or {}).get(d.isoformat())
        if remaining is None:
            availability = "unknown"
        elif remaining <= 0:
            availability = "full"
        elif remaining <= _LIMITED_AT:
            availability = "limited"
        else:
            availability = "available"
        pid = n.get("permit_id") or g.park.get("permit_id")
        notes = []
        if remaining is not None:
            notes.append(f"{remaining} site(s) open for your party "
                         "when checked")
        return NightStay(
            date=d, night=i, name=name,
            stay_type="zone" if "zone" in name.lower()
            else "backcountry_camp",
            policy="reservable", availability=availability,
            confidence="live_inventory", remaining=remaining,
            booking=BookingAction(
                "book_permit", "Book on the wilderness permit",
                f"https://www.recreation.gov/permits/{pid}"),
            source="recreation.gov live inventory", fetched_at=fetched_at,
            notes=notes)
    if policy == "first_come":
        return NightStay(
            date=d, night=i, name=name, stay_type="first_come_site",
            policy="first_come", availability="unknown",
            confidence="official_policy_verified",
            booking=BookingAction("arrive_early",
                                  "First-come: arrive early"),
            source="official park policy", fetched_at=fetched_at,
            notes=["No reservation system exists; capacity is not "
                   "guaranteed, arrive early."])
    return NightStay(
        date=d, night=i, name=name, stay_type="permit_free",
        policy="permit_free", availability="unknown",
        confidence="official_policy_verified",
        booking=BookingAction("none_needed", "No permit needed"),
        source="official land-manager policy", fetched_at=fetched_at,
        notes=["Permit-free area; no inventory system exists, follow "
               "dispersed camping rules."])


def _frontcountry_night(req, g, ent, d, i, which, fetched_at, warnings):
    opts, excluded = options_for_entrance(
        req.slug, ent, on_date=d, allow_first_come=req.first_come_ok)
    label = "arrival" if which == "arrival" else "recovery"
    if not opts:
        why = "; ".join(f"{x['name']}: {x['reason']}" for x in excluded)
        msg = (f"No usable {label} campground near "
               f"{_short(g.name(ent))} for {d.isoformat()}"
               + (f" ({why})" if why else
                  "; none is curated for this trailhead yet")
               + ". That night is unplanned; book lodging or a "
               "campground on your own.")
        warnings.append(TripWarning(
            code="campground_closed" if excluded else "unplanned_night",
            message=msg, date=d.isoformat()))
        return NightStay(
            date=d, night=i, name=f"Unplanned {label} night",
            stay_type="unplanned", policy="unknown",
            availability="unknown", confidence="unknown",
            booking=BookingAction("plan_yourself",
                                  "Arrange this night yourself"),
            fetched_at=fetched_at,
            notes=[x["reason"] for x in excluded] or
                  ["Switchback has no curated frontcountry option for "
                   "this trailhead yet."])
    cg = opts[0]
    if cg["policy"] == "reservable":
        booking = BookingAction("check_availability",
                                "Check campground availability",
                                cg.get("booking_url"))
        note = ("Reservable campground; live campground inventory is not "
                "checked yet, so verify a site before counting on it.")
    else:
        booking = BookingAction("arrive_early",
                                "First-come: arrive early",
                                cg.get("booking_url"))
        note = "First-come campground; no reservation system, arrive early."
    return NightStay(
        date=d, night=i, name=cg["name"],
        stay_type="frontcountry_campground", policy=cg["policy"],
        availability="unknown", confidence=cg.get("confidence", "curated"),
        booking=booking, source=cg.get("source"), fetched_at=fetched_at,
        notes=[note,
               f"About {cg['drive_min']} min drive to the "
               f"{_short(g.name(ent))}.",
               f"Season: {cg.get('season', 'check current dates')}.",
               f"Policy last checked {cg.get('policy_checked_at', '?')}."])


# ------------------------------ fit text -----------------------------------
def _is_backcountry(n):
    return n.stay_type in ("backcountry_camp", "zone")


def _fit(req, r, plan_nights, shape):
    moving = [(mi, gain) for mi, gain in r["days"] if mi and mi > 0]
    within = all(mi <= req.pref_mi and gain <= req.pref_gain
                 for mi, gain in moving)
    reasons, tradeoffs = [], []
    if within:
        reasons.append(f"Every hiking day stays inside your comfortable "
                       f"{req.pref_mi:g} miles and {req.pref_gain:,} ft.")
    if r.get("lake_nights"):
        reasons.append(f"{r['lake_nights']} of {len(r['seq'])} nights are "
                       "at lakeside camps.")
    if all(n.policy == "reservable"
           and n.availability in ("available", "limited")
           for n in plan_nights if _is_backcountry(n)):
        reasons.append("Every backcountry night has open sites right now.")
    if shape == "Basecamp":
        reasons.append("Hike in once and stay put; day hikes come from "
                       "camp, and one car works.")
    else:
        reasons.append(f"{shape} returning to your starting trailhead, "
                       "so one car works.")
    for k, (mi, gain) in enumerate(r["days"], 1):
        if mi and (mi > req.pref_mi or gain > req.pref_gain):
            tradeoffs.append(
                f"Day {k} is {mi:g} miles with {gain:,} ft of climbing, "
                f"above your comfortable day but inside your maximum.")
    fc = [n.name for n in plan_nights if n.policy == "first_come"]
    if fc:
        tradeoffs.append("First-come night(s) at " +
                         ", ".join(dict.fromkeys(fc)) +
                         ": no reservation is possible, arrive early.")
    unk = [n.name for n in plan_nights
           if n.policy == "reservable" and n.availability == "unknown"]
    if unk:
        tradeoffs.append("Availability is unverified for " +
                         ", ".join(dict.fromkeys(unk)) + ".")
    return {"label": "Great fit" if within else "Stretch",
            "within_preferred": within,
            "reasons": reasons[:3], "tradeoffs": tradeoffs[:3]}


# characteristic edge grade at or above this reads as sustained steep
_STEEP_TRADEOFF_PCT = 25


def _steep_tradeoffs(fit, days, pace):
    """Grade-aware honesty: a day whose steepest edge runs at a
    sustained hard grade gets a tradeoff naming the grade and the
    realistic speed there, even when its mileage looks easy."""
    for x in days:
        if x.kind != "hike" or not x.steepest_grade_pct:
            continue
        if x.steepest_grade_pct >= _STEEP_TRADEOFF_PCT:
            mph = speed_for(x.steepest_grade_pct, pace)
            fit["tradeoffs"].append(
                f"Day {x.day} holds sustained grades around "
                f"{x.steepest_grade_pct:g} percent; expect roughly "
                f"{mph:g} mph there and about "
                f"{format_hours(x.est_hours)} for the day.")
    return fit


def _availability_summary(plan_nights):
    if any(n.stay_type == "unplanned" for n in plan_nights):
        return "One night needs your own plan"
    if any(n.policy == "reservable" and n.availability == "unknown"
           for n in plan_nights):
        return "Partly unverified"
    if any(n.policy == "first_come" for n in plan_nights):
        return "Includes first-come night(s)"
    if any(n.policy == "permit_free" for n in plan_nights):
        return "Includes permit-free night(s)"
    if all(n.availability in ("available", "limited")
           for n in plan_nights):
        return "Bookable now"
    return "Check each night"


def _data_quality(g, ent, seq, solver):
    notes = []
    est = False
    for a, b in zip([ent] + list(seq), list(seq) + [ent]):
        if a == b:
            continue
        leg = solver._leg(a, b)
        path = leg[2] or []
        for x, y in zip(path, path[1:]):
            for other, _mi, _gain, e, _k in g.adj.get(x, []):
                if other == y and e:
                    est = True
    if est:
        notes.append("Some elevation gains on this route are model-graded "
                     "estimates, not surveyed figures.")
    return notes


# ------------------------------ plan build ---------------------------------
def _build_plan(req, g, av, solver, view, fetched_at, include_geometry):
    r = view["best"]
    ent, seq, start = r["entrance"], list(r["seq"]), r["start"]
    warnings = []
    nights = []
    idx = 0
    if req.arrival_night:
        nights.append(_frontcountry_night(
            req, g, ent, start - timedelta(days=1), idx, "arrival",
            fetched_at, warnings))
        idx += 1
    for i, camp in enumerate(seq):
        nights.append(_backcountry_night(
            g, av, camp, start + timedelta(days=i), idx, req.party,
            fetched_at))
        idx += 1
    exit_day = start + timedelta(days=req.nights)
    if req.recovery_night:
        nights.append(_frontcountry_night(
            req, g, ent, exit_day, idx, "recovery", fetched_at, warnings))
        idx += 1

    stops = [ent] + seq + [ent]
    days = []
    if req.arrival_night:
        days.append(TripDay(day=0, date=start - timedelta(days=1),
                            kind="travel", from_name=None,
                            to_name=_short(g.name(ent)),
                            miles=0.0, gain_ft=0))
    pace = req.pace or DEFAULT_PACE_MPH
    for i, (mi, gain) in enumerate(r["days"]):
        a, b = stops[i], stops[i + 1]
        hours, steepest = (None, None)
        if a != b:
            path = solver._leg(a, b)[2]
            if path:
                hours, steepest = leg_hours(g, path, pace)
        days.append(TripDay(day=i + 1, date=start + timedelta(days=i),
                            kind="layover" if a == b else "hike",
                            from_name=_short(g.name(a)),
                            to_name=_short(g.name(b)),
                            miles=round(mi, 1), gain_ft=int(gain),
                            est_hours=hours,
                            steepest_grade_pct=steepest))
    hikes = [x for x in days if x.kind == "hike" and x.miles]
    hardest = None
    if hikes:
        hd = max(hikes, key=lambda x: x.est_hours
                 if x.est_hours is not None
                 else x.miles / req.max_mi + x.gain_ft / req.max_gain)
        hardest = {"day": hd.day, "miles": hd.miles, "gain_ft": hd.gain_ft,
                   "est_hours": hd.est_hours}

    shorts = list(dict.fromkeys(_short(g.name(c)) for c in seq))
    # Presentation shape comes from the STAYING pattern first: sleeping
    # every night at one camp IS a basecamp trip to a human, whatever
    # shape the walk in and out traces (owner catch, 2026-07-20).
    if len(seq) >= 2 and len(set(seq)) == 1:
        shape = "Basecamp"
    else:
        shape = _SHAPE_LABEL.get(r["type"], r["type"])
    plan_id = "-".join([req.slug, start.isoformat(),
                        _short(g.name(ent)).lower().replace(" ", "_")]
                       + [s.lower().replace(" ", "_") for s in shorts[:3]])
    first_night = start - timedelta(days=1) if req.arrival_night else start
    end = exit_day + timedelta(days=1) if req.recovery_night else exit_day
    plan = TripPlan(
        id=plan_id,
        title=" / ".join(shorts[:3]) + f" {shape}",
        destination={"slug": req.slug, "name": g.park["name"],
                     "permit_id": str(g.park.get("permit_id", ""))},
        trailhead={"id": ent, "name": _short(g.name(ent))},
        shape=shape, party=req.party,
        start=start, end=end, first_night=first_night,
        alternate_starts=sorted(d.isoformat() for d in view["dates"]
                                if d != start),
        nights=nights, days=days,
        totals={"miles": round(sum(m for m, _ in r["days"]), 1),
                "gain_ft": int(sum(gft for _, gft in r["days"])),
                "hiking_hours": round(sum(x.est_hours for x in hikes
                                          if x.est_hours), 2) or None,
                "hardest_day": hardest},
        fit=_steep_tradeoffs(_fit(req, r, nights, shape), days, pace),
        availability_summary=_availability_summary(nights),
        confidence=overall_confidence(nights),
        data_quality=_data_quality(g, ent, seq, solver),
        warnings=warnings,
        checked_at=fetched_at,
        gpx={"entrance": ent, "seq": seq, "start": start.isoformat()})
    if include_geometry:
        from .geometry import day_path
        plan.day_paths = [day_path(req.slug, g, [a, b])
                          for a, b in zip(stops, stops[1:])]
    out = plan.to_dict()
    problems = complete_night_problems(out)
    if problems:
        plan.warnings.append(TripWarning(
            code="invariant_violation",
            message="This plan failed its own completeness check: "
                    + "; ".join(problems)))
        out = plan.to_dict()
    return out


def _badges(plans):
    if not plans:
        return
    plans[0]["badge"] = "Best overall fit"
    if len(plans) > 1:
        easiest = min(plans[1:], key=lambda p: (p["totals"]["gain_ft"],
                                                p["totals"]["miles"]))
        easiest.setdefault("badge", "Easiest option")
        lakes = max(plans, key=lambda p: sum(
            1 for n in p["fit"]["reasons"] if "lakeside" in n))
        if any("lakeside" in x for x in lakes["fit"]["reasons"]):
            lakes.setdefault("badge", "Best lake itinerary")
        avail = max(plans, key=lambda p: len(p["alternate_starts"]))
        if avail["alternate_starts"]:
            avail.setdefault("badge", "Most available")


# ----------------------------- relaxations ---------------------------------
def _distinct(rows):
    return {(r["entrance"], r["seq"]) for r in rows}


def _relaxations(req, g, av):
    out = []
    for f in (1.1, 1.2, 1.35, 1.5):
        cand = round(req.max_mi * f, 1)
        _s, rows = _rows(g, av, req, max_mi=cand)
        if rows:
            out.append({"change": "max_daily_miles", "from": req.max_mi,
                        "to": cand, "plans": len(_distinct(rows)),
                        "detail": f"Raise your maximum day from "
                        f"{req.max_mi:g} to {cand:g} miles and "
                        f"{len(rows)} itineraries open up."})
            break
    for f in (1.1, 1.25, 1.5):
        cand = int(req.max_gain * f)
        _s, rows = _rows(g, av, req, max_gain=cand)
        if rows:
            out.append({"change": "max_daily_gain", "from": req.max_gain,
                        "to": cand, "plans": len(_distinct(rows)),
                        "detail": f"Raise your maximum daily climb from "
                        f"{req.max_gain:,} to {cand:,} ft and "
                        f"{len(rows)} itineraries open up."})
            break
    if req.shapes and "basecamp" not in req.shapes:
        req2_shapes = req.shapes + ["basecamp"]
        s = _solver_for(g, av, req, basecamp_ok=True)
        rows = s.batch(g.entrances(), req.start, req.latest_start,
                       trip_types=req2_shapes)
        if rows:
            out.append({"change": "allow_basecamp", "from": req.shapes,
                        "to": req2_shapes, "plans": len(rows),
                        "detail": f"Allow a basecamp (repeat nights at one "
                        f"camp) and {len(rows)} itineraries open up."})
    if not req.first_come_ok:
        req2 = _copy_req(req, first_come_ok=True)
        _s, rows = _rows(g, av, req2)
        if rows:
            out.append({"change": "accept_first_come", "from": False,
                        "to": True, "plans": len(rows),
                        "detail": f"Accept first-come night(s) and "
                        f"{len(rows)} itineraries open up."})
    for shift in range(1, _SHIFT_DAYS + 1):
        s0 = req.start + timedelta(days=shift)
        s1 = req.latest_start + timedelta(days=shift)
        _s, rows = _rows(g, av, req, start=s0, latest=s1)
        if rows:
            out.append({"change": "shift_dates", "from":
                        req.start.isoformat(), "to": s0.isoformat(),
                        "plans": len(rows),
                        "detail": f"Start {shift} day(s) later "
                        f"({s0.isoformat()}) and {len(rows)} itineraries "
                        f"open up."})
            break
    if not out:
        out.append({"change": "monitor", "from": None, "to": None,
                    "plans": 0,
                    "detail": "Nothing opens up under modest relaxations. "
                    "Try a different window, or monitor the permit for "
                    "cancellations with a service like Campflare and "
                    "search again when inventory moves."})
    return out


def _copy_req(req, **changes):
    from dataclasses import replace
    return replace(req, **changes)


# ------------------------------- entry -------------------------------------
def plan_trips(req, fetch_fn=None, availability=None, graph=None,
               now=None, include_geometry=False):
    """TripRequest in, complete structured result out:
    {"request": ..., "checked_at": ..., "plans": [serialized TripPlan],
     "relaxations": [...], "notes": [...]}"""
    try:
        g = graph or Graph(req.slug)
    except Exception as ex:
        raise PlannerError(
            f"{req.slug} does not have solver-ready route data yet: {ex}")
    fs, fe = availability_window(req)
    av = availability
    if av is None:
        av = fetch_for_graph(g, g.camps(), fs, fe, fetch_fn=fetch_fn)
    when = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    notes = []
    res_camps = [c for c in g.camps()
                 if g.nodes[c].get("policy", "reservation") == "reservation"]
    if res_camps and not any((av.get(c) or {}).get(d) for c in res_camps
                             for d in (av.get(c) or {})):
        notes.append("Every reservable camp came back zero. That can mean "
                     "a sold-out window, but it is also exactly what a "
                     "failed availability fetch looks like; do not book "
                     "or give up based on this result alone.")

    solver, rows = _rows(g, av, req)
    result = {"request": req.to_dict(), "checked_at": when,
              "destination": {"slug": req.slug, "name": g.park["name"]},
              "plans": [], "relaxations": [], "notes": notes}
    if not rows:
        result["relaxations"] = _relaxations(req, g, av)
        return result
    ranked = Scorer(g).rank(rows, req.pref_mi, req.pref_gain)
    for view in dedupe_routes(ranked)[:req.limit]:
        result["plans"].append(
            _build_plan(req, g, av, solver, view, when, include_geometry))
    _badges(result["plans"])
    return result
