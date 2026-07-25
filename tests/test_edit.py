"""The controlled edit subset: swap a camp, add or remove a layover,
reverse direction. Fully offline via an injected fetcher. Covers that
an accepted edit rebuilds a complete plan with the invariant intact,
that a broken edit is refused with the specific reason instead of
being quietly repaired, and that the offered options are exactly the
ones the engine accepts."""
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.edit import apply_edit, edit_options, route_of
from switchback.planner import plan_trips
from switchback.plans import TripRequest, complete_night_problems

D0 = date(2026, 8, 14)


def open_fetch(closed=None):
    """Every division open (4 sites), except any (division, iso date)
    pair listed in closed, which reads zero."""
    closed = closed or set()

    def fetch(pid, divs, start, end):
        out = {}
        for dv in divs:
            out[dv] = {}
            d = start
            while d <= end:
                out[dv][d.isoformat()] = 0 if (dv, d.isoformat()) in closed \
                    else 4
                d += timedelta(days=1)
        return out
    return fetch


def req(**kw):
    base = dict(slug="rainier", start=D0, latest_start=D0, nights=2,
                party=2, pref_mi=9.0, max_mi=13.0, pref_gain=2500,
                max_gain=4500, shapes=[], first_come_ok=True,
                arrival_night=False, recovery_night=False, limit=8,
                pace=None)
    base.update(kw)
    return TripRequest(**base)


def a_trip(r=None, fetch=None):
    """The top plan for a request, and its route identity."""
    r = r or req()
    res = plan_trips(r, fetch_fn=fetch or open_fetch())
    assert res["plans"], "fixture needs at least one plan to edit"
    p = res["plans"][0]
    return r, p, route_of(p)


def assert_complete(plan):
    problems = complete_night_problems(plan)
    assert not problems, f"edited plan broke the invariant: {problems}"


def scenario_swap_camp():
    """A legal swap rebuilds a complete plan that actually sleeps at
    the requested camp, with the day math recomputed, not carried."""
    r, plan, route = a_trip()
    opts = edit_options(r, route, fetch_fn=open_fetch())
    night = next(n for n in opts["nights"] if n["swap_to"])
    target = night["swap_to"][0]

    out = apply_edit(r, route, "swap_camp", night=night["night"],
                     camp=target["id"], fetch_fn=open_fetch())
    assert out["ok"], out.get("reason")
    edited = out["plan"]
    assert_complete(edited)
    assert edited["nights"][night["night"]]["name"] == target["name"], \
        "the swapped night must sleep at the camp that was asked for"
    assert len(edited["nights"]) == len(plan["nights"])
    assert target["name"] in out["change"]

    day = edited["days"][night["night"]]
    assert day["miles"] == target["miles_in"], \
        "day miles must be recomputed for the new camp, not inherited"
    assert edited["totals"]["miles"] == round(
        sum(d["miles"] for d in edited["days"]), 1)


def scenario_swap_refused_over_limit():
    """A camp too far to walk to is refused, naming the day, the
    distance, and the limit it broke, and no plan comes back."""
    r = req(max_mi=13.0)
    _, _, route = a_trip(r)
    g_far = None
    from switchback.graph import Graph
    g = Graph("rainier")
    prev = route["entrance"]
    for c in g.camps():
        leg = g.leg(prev, c)
        if leg and leg[0] > 13.0:
            g_far = c
            break
    assert g_far, "fixture needs a camp beyond the mile limit"

    out = apply_edit(r, route, "swap_camp", night=0, camp=g_far,
                     fetch_fn=open_fetch())
    assert not out["ok"], "an over-limit camp must be refused"
    assert "plan" not in out, "a refused edit must not return a plan"
    assert "mile limit" in out["reason"], out["reason"]
    assert any("Day 1" in p for p in out["problems"]), out["problems"]


def scenario_swap_refused_when_full():
    """A camp with no open site that night is refused on availability,
    not silently swapped for a different one."""
    r, _, route = a_trip()
    opts = edit_options(r, route, fetch_fn=open_fetch())
    night = next(n for n in opts["nights"] if n["swap_to"])
    target = night["swap_to"][0]
    from switchback.graph import Graph
    div = Graph("rainier").nodes[target["id"]].get("division_id")
    full = open_fetch(closed={(div, night["date"])})

    out = apply_edit(r, route, "swap_camp", night=night["night"],
                     camp=target["id"], fetch_fn=full)
    assert not out["ok"], "a full camp must be refused"
    assert "no open site" in out["reason"], out["reason"]
    assert night["date"] in out["reason"]


def scenario_add_and_remove_layover():
    """Adding a layover lengthens the trip by exactly one night and
    keeps every night accounted for; removing it puts the trip back."""
    r, plan, route = a_trip()
    before = len(plan["nights"])

    out = apply_edit(r, route, "add_layover", night=0,
                     fetch_fn=open_fetch())
    assert out["ok"], out.get("reason")
    longer = out["plan"]
    assert_complete(longer)
    assert len(longer["nights"]) == before + 1
    assert longer["nights"][0]["name"] == longer["nights"][1]["name"], \
        "a layover means two nights at the same camp"
    assert any(d["kind"] == "layover" for d in longer["days"])
    assert longer["end"] > plan["end"], "the trip must end a day later"

    back = apply_edit(r, route_of(longer), "remove_layover", night=1,
                      fetch_fn=open_fetch())
    assert back["ok"], back.get("reason")
    assert len(back["plan"]["nights"]) == before
    assert_complete(back["plan"])


def scenario_remove_layover_refused_when_not_a_layover():
    """Removing a night that is not a layover would leave a gap, so it
    is refused and says why rather than dropping the night."""
    r, plan, route = a_trip()
    if len(set(route["seq"])) < 2:
        return
    night = next(i for i, c in enumerate(route["seq"])
                 if all(route["seq"][j] != c
                        for j in (i - 1, i + 1)
                        if 0 <= j < len(route["seq"])))
    out = apply_edit(r, route, "remove_layover", night=night,
                     fetch_fn=open_fetch())
    assert not out["ok"]
    assert "not a layover" in out["reason"], out["reason"]


def scenario_reverse():
    """Reversing rebuilds the trip in the other direction, and because
    gains are direction dependent the day math must change with it, not
    ride along from the original."""
    r = req(nights=3)
    res = plan_trips(r, fetch_fn=open_fetch())
    asym = None
    for p in res["plans"]:
        seq = route_of(p)["seq"]
        if len(set(seq)) > 1 and seq != seq[::-1]:
            asym = p
            break
    if asym is None:
        return
    route = route_of(asym)
    out = apply_edit(r, route, "reverse", fetch_fn=open_fetch())
    assert out["ok"], out.get("reason")
    rev = out["plan"]
    assert_complete(rev)
    assert route_of(rev)["seq"] == route["seq"][::-1]
    assert [n["name"] for n in rev["nights"]] == \
        [n["name"] for n in asym["nights"]][::-1]

    # The domain trap: gains are direction dependent, and an unoriented
    # consumer grades every descent as a climb. The reversed trip walks
    # out to the LAST camp on day 1, so its climb must be the graph's
    # climb in that direction, recomputed, not the original day 1's.
    from switchback.graph import Graph
    g = Graph("rainier")
    ent, seq = route["entrance"], route["seq"]
    out_to_last = g.leg(ent, seq[-1])[1]
    back_from_last = g.leg(seq[-1], ent)[1]
    assert rev["days"][0]["gain_ft"] == out_to_last, \
        (f"reversed day 1 climbed {rev['days'][0]['gain_ft']} ft but the "
         f"graph says {ent} to {seq[-1]} climbs {out_to_last} ft")
    if out_to_last != back_from_last:
        assert rev["days"][0]["gain_ft"] != asym["days"][-1]["gain_ft"], \
            ("the same leg walked the other way must not report the same "
             "climb; that is the unoriented-geometry bug")


def scenario_reverse_refused_when_symmetric():
    """An out and back reads the same either way; say so plainly
    instead of handing back an identical trip as a change."""
    r, _, route = a_trip()
    seq = route["seq"]
    if seq != seq[::-1]:
        sym = dict(route, seq=[seq[0]])
        out = apply_edit(r, sym, "reverse", fetch_fn=open_fetch())
    else:
        out = apply_edit(r, route, "reverse", fetch_fn=open_fetch())
    assert not out["ok"]
    assert "no direction" in out["reason"] or "same trip" in out["reason"], \
        out["reason"]


def scenario_options_match_what_is_accepted():
    """Every option offered must actually apply, and the structural
    flags must agree with the engine. Offering an edit that then fails
    is the dead end the directive forbids."""
    r, _, route = a_trip()
    opts = edit_options(r, route, fetch_fn=open_fetch(), limit=3)
    assert opts["nights"], "a trip must expose its nights as editable"
    checked = 0
    for n in opts["nights"]:
        for cand in n["swap_to"]:
            out = apply_edit(r, route, "swap_camp", night=n["night"],
                             camp=cand["id"], fetch_fn=open_fetch())
            assert out["ok"], \
                f"offered {cand['name']} for night {n['night']} but the " \
                f"engine refused: {out.get('reason')}"
            assert_complete(out["plan"])
            checked += 1
        lay = apply_edit(r, route, "add_layover", night=n["night"],
                         fetch_fn=open_fetch())
        assert lay["ok"] == n["can_add_layover"], \
            f"night {n['night']} add_layover offered as " \
            f"{n['can_add_layover']} but engine said {lay['ok']}"
    assert checked, "the fixture must offer at least one swap"


def scenario_bad_input_is_refused_plainly():
    """Out of range nights, unknown camps, and unknown operations get a
    sentence a person can read, never a traceback."""
    r, _, route = a_trip()
    for kw, expect in (
            (dict(op="swap_camp", night=99, camp=route["seq"][0]),
             "no night"),
            (dict(op="swap_camp", night=0, camp="not_a_node"), "not on the map"),
            (dict(op="teleport", night=0), "Unknown edit"),
            (dict(op="swap_camp", night=0, camp=route["seq"][0]),
             "already at")):
        out = apply_edit(r, route, fetch_fn=open_fetch(), **kw)
        assert not out["ok"], kw
        assert expect.lower() in out["reason"].lower(), \
            f"{kw} gave {out['reason']!r}, wanted {expect!r}"


def main():
    scenario_swap_camp()
    scenario_swap_refused_over_limit()
    scenario_swap_refused_when_full()
    scenario_add_and_remove_layover()
    scenario_remove_layover_refused_when_not_a_layover()
    scenario_reverse()
    scenario_reverse_refused_when_symmetric()
    scenario_options_match_what_is_accepted()
    scenario_bad_input_is_refused_plainly()
    print("EDIT OK: 9 scenarios green (swap, layover add and remove, "
          "reverse with direction-correct gains, honest refusals, and "
          "offered options that the engine actually accepts)")


if __name__ == "__main__":
    main()
