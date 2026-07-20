"""
switchback.planner: orchestration above the solver.

Turns a validated TripRequest into complete, structured TripPlan
dicts per project/MASTER_COURSE_CORRECTION.md. The solver stays
untouched and keeps producing feasible backcountry camp sequences;
this layer adds everything a person needs to act on one: a record for
every calendar night (arrival campground, backcountry camps, recovery
campground, or an explicit unplanned gap), availability status with
freshness, booking actions, plain-language reasons and tradeoffs, and
quantified relaxation suggestions when nothing fits.

Hard limits come from the request, never silently from profile.json.
"""
from datetime import datetime, timedelta, timezone

from .frontcountry import options_for_entrance
from .graph import Graph
from .plans import night_stay, overall_confidence
from .report import dedupe_routes
from .scoring import Scorer
from .solver import Solver, fetch_for_graph

_SHAPE_LABEL = {"loop": "Loop", "out_and_back": "Out and Back",
                "lollipop": "Lollipop", "basecamp": "Basecamp",
                "mixed": "Route"}
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


def _policy_of(node):
    return node.get("policy", "reservation")


def _solver_for(g, av, req, basecamp_ok=None, max_mi=None, max_gain=None):
    if basecamp_ok is None:
        basecamp_ok = not req.shapes or "basecamp" in req.shapes
    if not req.first_come_ok:
        av = {c: d for c, d in av.items()
              if c not in g.nodes or _policy_of(g.nodes[c]) == "reservation"}
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
    policy = _policy_of(n)
    name = _short(n["name"])
    if policy == "reservation":
        remaining = (av.get(camp) or {}).get(d.isoformat())
        pid = n.get("permit_id") or g.park.get("permit_id")
        return night_stay(
            d, i, name,
            "zone" if "zone" in name.lower() else "backcountry_camp",
            "reservation", "reservable", "live_inventory",
            remaining=remaining, booking_action="book_permit",
            booking_label="Book on the wilderness permit",
            booking_url=f"https://www.recreation.gov/permits/{pid}",
            source="recreation.gov live inventory", fetched_at=fetched_at,
            notes=[f"{remaining} site(s) open for your party when checked"]
            if remaining is not None else [])
    if policy == "fcfs":
        return night_stay(
            d, i, name, "first_come_site", "first_come", "first_come",
            "official_policy_verified", booking_action="arrive_early",
            booking_label="First-come: arrive early",
            source="official park policy", fetched_at=fetched_at,
            notes=["No reservation system exists; availability assumed, "
                   "arrive early."])
    return night_stay(
        d, i, name, "permit_free", "permit_free", "permit_free",
        "official_policy_verified", booking_action="none_needed",
        booking_label="No permit needed",
        source="official land-manager policy", fetched_at=fetched_at,
        notes=["Permit-free area; follow dispersed camping rules."])


def _frontcountry_night(req, g, ent, d, i, which, fetched_at, warnings):
    opts = options_for_entrance(req.slug, ent)
    label = "arrival" if which == "arrival" else "recovery"
    if not opts:
        warnings.append(
            f"No curated {label} campground is mapped near "
            f"{_short(g.name(ent))} yet; that night is unplanned. "
            f"Book lodging or a campground on your own for {d.isoformat()}.")
        return night_stay(d, i, f"Unplanned {label} night", "unplanned",
                          "unknown", "unknown", "unknown",
                          booking_action="plan_yourself",
                          booking_label="Arrange this night yourself",
                          fetched_at=fetched_at,
                          notes=["Switchback has no curated frontcountry "
                                 "option for this trailhead yet."])
    cg = opts[0]
    if cg["policy"] == "reservation":
        avail, conf = "unknown", cg.get("confidence", "curated")
        action, blabel = "check_availability", "Check campground availability"
        note = ("Reservation campground; live campground inventory is not "
                "checked yet, so verify a site before counting on it.")
    else:
        avail, conf = "first_come", cg.get("confidence", "curated")
        action, blabel = "arrive_early", "First-come: arrive early"
        note = "First-come campground; no reservation system, arrive early."
    return night_stay(
        d, i, cg["name"], "frontcountry_campground", cg["policy"], avail,
        conf, booking_action=action, booking_label=blabel,
        booking_url=cg.get("booking_url"), source=cg.get("source"),
        fetched_at=fetched_at,
        notes=[note, f"About {cg['drive_min']} min drive to the "
               f"{_short(g.name(ent))}.",
               f"Season: {cg.get('season', 'check current dates')}."])


# ------------------------------ fit text -----------------------------------
def _fit(req, r, plan_nights, g):
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
    if all(n["availability"] == "reservable" for n in plan_nights
           if n["stay_type"] in ("backcountry_camp", "zone")):
        reasons.append("Every backcountry night is reservable right now.")
    shape = _SHAPE_LABEL.get(r["type"], r["type"])
    reasons.append(f"{shape} returning to your starting trailhead, "
                   "so one car works.")
    for k, (mi, gain) in enumerate(r["days"], 1):
        if mi and (mi > req.pref_mi or gain > req.pref_gain):
            tradeoffs.append(
                f"Day {k} is {mi:g} miles with {gain:,} ft of climbing, "
                f"above your comfortable day but inside your maximum.")
    fc = [n["name"] for n in plan_nights if n["availability"] == "first_come"]
    if fc:
        tradeoffs.append("First-come night(s) at " +
                         ", ".join(dict.fromkeys(fc)) +
                         ": no reservation is possible, arrive early.")
    unk = [n["name"] for n in plan_nights if n["availability"] == "unknown"]
    if unk:
        tradeoffs.append("Availability is unverified for " +
                         ", ".join(dict.fromkeys(unk)) + ".")
    return {"label": "Great fit" if within else "Stretch",
            "within_preferred": within,
            "reasons": reasons[:3], "tradeoffs": tradeoffs[:3]}


def _availability_summary(plan_nights):
    stats = [n["availability"] for n in plan_nights]
    if all(s == "reservable" for s in stats):
        return "Bookable now"
    if any(s == "unknown" for s in stats):
        return "Partly unverified"
    if any(s == "first_come" for s in stats):
        return "Includes first-come night(s)"
    if any(s == "permit_free" for s in stats):
        return "Includes permit-free night(s)"
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
        days.append({"day": 0,
                     "date": (start - timedelta(days=1)).isoformat(),
                     "kind": "travel", "from": None,
                     "to": _short(g.name(ent)), "miles": 0.0, "gain_ft": 0})
    for i, (mi, gain) in enumerate(r["days"]):
        a, b = stops[i], stops[i + 1]
        days.append({"day": i + 1,
                     "date": (start + timedelta(days=i)).isoformat(),
                     "kind": "layover" if a == b else "hike",
                     "from": _short(g.name(a)), "to": _short(g.name(b)),
                     "miles": round(mi, 1), "gain_ft": int(gain)})
    moving = [(d["miles"], d["gain_ft"]) for d in days
              if d["kind"] == "hike" and d["miles"]]
    hardest = None
    if moving:
        hd = max((d for d in days if d["kind"] == "hike" and d["miles"]),
                 key=lambda d: d["miles"] / req.max_mi
                 + d["gain_ft"] / req.max_gain)
        hardest = {"day": hd["day"], "miles": hd["miles"],
                   "gain_ft": hd["gain_ft"]}

    shorts = list(dict.fromkeys(_short(g.name(c)) for c in seq))
    shape = _SHAPE_LABEL.get(r["type"], r["type"])
    title = " / ".join(shorts[:3]) + f" {shape}"
    pid = str(g.park.get("permit_id", ""))
    plan_id = "-".join([req.slug, start.isoformat(),
                        _short(g.name(ent)).lower().replace(" ", "_")]
                       + [s.lower().replace(" ", "_") for s in shorts[:3]])
    fit = _fit(req, r, nights, g)
    dq = _data_quality(g, ent, seq, solver)
    plan = {
        "id": plan_id,
        "title": title,
        "destination": {"slug": req.slug, "name": g.park["name"],
                        "permit_id": pid},
        "trailhead": {"id": ent, "name": _short(g.name(ent))},
        "shape": shape,
        "party": req.party,
        "start": start.isoformat(),
        "end": (exit_day + timedelta(days=1) if req.recovery_night
                else exit_day).isoformat(),
        "alternate_starts": sorted(d.isoformat() for d in view["dates"]
                                   if d != start),
        "nights": nights,
        "days": days,
        "totals": {
            "miles": round(sum(m for m, _ in r["days"]), 1),
            "gain_ft": int(sum(gft for _, gft in r["days"])),
            "hardest_day": hardest,
        },
        "fit": fit,
        "availability_summary": _availability_summary(nights),
        "confidence": overall_confidence(nights),
        "data_quality": dq,
        "warnings": warnings,
        "checked_at": fetched_at,
        "gpx": {"entrance": ent, "seq": seq, "start": start.isoformat()},
    }
    if include_geometry:
        from .geometry import day_path
        plan["day_paths"] = [day_path(req.slug, g, [a, b])
                             for a, b in zip(stops, stops[1:])]
    return plan


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
def _relaxations(req, g, av):
    out = []
    for f in (1.1, 1.2, 1.35, 1.5):
        cand = round(req.max_mi * f, 1)
        _s, rows = _rows(g, av, req, max_mi=cand)
        if rows:
            out.append({"change": "max_daily_miles", "from": req.max_mi,
                        "to": cand, "plans": len(dedupe_routes_len(rows)),
                        "detail": f"Raise your maximum day from "
                        f"{req.max_mi:g} to {cand:g} miles and "
                        f"{len(rows)} itineraries open up."})
            break
    for f in (1.1, 1.25, 1.5):
        cand = int(req.max_gain * f)
        _s, rows = _rows(g, av, req, max_gain=cand)
        if rows:
            out.append({"change": "max_daily_gain", "from": req.max_gain,
                        "to": cand, "plans": len(dedupe_routes_len(rows)),
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


def dedupe_routes_len(rows):
    return {(r["entrance"], r["seq"]) for r in rows}


def _copy_req(req, **changes):
    from dataclasses import replace
    return replace(req, **changes)


# ------------------------------- entry -------------------------------------
def plan_trips(req, fetch_fn=None, availability=None, graph=None,
               now=None, include_geometry=False):
    """TripRequest in, complete structured result out:
    {"request": ..., "checked_at": ..., "plans": [...],
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
                 if _policy_of(g.nodes[c]) == "reservation"]
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
        plan = _build_plan(req, g, av, solver, view, when, include_geometry)
        result["plans"].append(plan)
    _badges(result["plans"])
    return result
