"""
switchback.solver: M4 itinerary engine.

Given a park graph, live (or injected) availability, and effort limits,
enumerates every bookable camp sequence: start at an entrance, sleep
NIGHTS nights at open camps with each day's shortest trail leg within
max miles and gain (pass-throughs allowed), return to the same entrance.

Trip type is classified on the closed walk per ROADMAP M4: strip mirrored
hop pairs from the ends (the stem); an empty remainder is out_and_back,
a unique-edge remainder is a loop (no stem) or lollipop (stem), anything
else is mixed. Backward feasibility guarantees every frontier option has
at least one valid ending; endings() counts completions for M6 cards.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from functools import lru_cache

from .api import fetch_division_month


# ------------------------- availability -----------------------------------
def fetch_availability(permit_id, division_ids, start, end, workers=6,
                       progress=None):
    """{division_id: {iso_date: remaining}} with hidden dates as 0."""
    yms = sorted({(d.year, d.month)
                  for d in (start + timedelta(days=i)
                            for i in range((end - start).days + 1))})
    jobs = [(div, y, m) for div in division_ids for (y, m) in yms]
    out = {div: {} for div in division_ids}
    done = 0

    def work(j):
        div, y, m = j
        per, err = fetch_division_month(permit_id, div, y, m)
        return div, per or {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(work, j) for j in jobs]):
            div, per = fut.result()
            done += 1
            for ds, cell in per.items():
                rem = cell.get("remaining") or 0
                out[div][ds[:10]] = 0 if cell.get("hidden") else max(rem, 0)
            if progress:
                progress(done / len(jobs))
    return out


# ------------------------------ solver -------------------------------------
def fetch_for_graph(g, camps, start, end, fetch_fn=None, workers=6):
    """Region-aware availability: reservation camps fetch from their own
    permit, grouped so each permit is hit once; permitless and first-come
    camps (policy none or fcfs) get a synthetic always-open series, since
    no reservation system exists to ask. Callers label those nights
    honestly; the solver just sees open.

    Dual-inventory camps (v2.21): a camp may list extra inventories
    (permit_id, division_id pairs, e.g. the IPW 3-days-in-advance permit
    mirroring the full-season zones). Every inventory is fetched and the
    per-date values are MAX-merged, never summed: a party books within
    one inventory, so the bookable count for the night is the best any
    single inventory offers."""
    fetch = fetch_fn or fetch_availability
    groups, synth = {}, []
    for c in camps:
        n = g.nodes[c]
        if n.get("policy", "reservation") != "reservation" or not n.get("division_id"):
            synth.append(c)
            continue
        pid = n.get("permit_id") or g.park.get("permit_id")
        groups.setdefault(pid, {})[n["division_id"]] = c
        for inv in n.get("inventories") or []:
            groups.setdefault(inv["permit_id"], {})[inv["division_id"]] = c
    out = {}
    for pid, divmap in groups.items():
        raw = fetch(pid, list(divmap), start, end)
        for d, days in raw.items():
            if d in divmap:
                cur = out.setdefault(divmap[d], {})
                for ds, v in days.items():
                    cur[ds] = max(cur.get(ds, 0), v)
    if synth:
        dates = []
        d = start
        while d <= end:
            dates.append(d.isoformat())
            d += timedelta(days=1)
        for c in synth:
            out[c] = {ds: 99 for ds in dates}
    return out


# Trip-shape selection (v3.1). Accepts a set/list of shapes, the legacy
# single string, or None. Toggle vocabulary is user-facing: loop,
# out_and_back (gathers the lollipop stem-and-loop variant), basecamp,
# point_to_point. "any"/"all"/empty means no filter. Returns a set of
# internal classify() labels, or None for no filtering.
_TOGGLE_MAP = {"loop": {"loop"},
               "out_and_back": {"out_and_back", "lollipop"},
               "out and back": {"out_and_back", "lollipop"},
               "basecamp": {"basecamp"},
               "point_to_point": {"point_to_point"},
               "lollipop": {"lollipop"}}


def _normalize_types(trip_types, trip_type="any"):
    raw = trip_types if trip_types is not None else trip_type
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = [p.strip() for p in raw.split(",")]
    picks = [p.lower() for p in raw if p]
    if not picks or any(p in ("any", "all") for p in picks):
        return None
    allow = set()
    for p in picks:
        allow |= _TOGGLE_MAP.get(p, {p})
    return allow



class Solver:
    def __init__(self, graph, availability, party=2, nights=3,
                 max_mi=13.0, max_gain=4000, basecamp_ok=True,
                 max_stay=None):
        self.g = graph
        self.av = availability
        self.party, self.nights = party, nights
        self.max_mi, self.max_gain = max_mi, max_gain
        self.basecamp_ok, self.max_stay = basecamp_ok, max_stay
        self.camps = [c for c in graph.camps() if c in availability]
        self._leg = lru_cache(maxsize=None)(self._leg_raw)

    def _leg_raw(self, a, b):
        got = self.g.leg(a, b)
        return got if got else (None, None, None)

    def day_ok(self, a, b):
        if a == b:
            return True
        mi, gain, _ = self._leg(a, b)
        return mi is not None and mi <= self.max_mi and gain <= self.max_gain

    def open_night(self, camp, d):
        return self.av.get(camp, {}).get(d.isoformat(), 0) >= self.party

    # -------------------------------------------------------------------
    def itineraries(self, entrance, start):
        """All feasible camp sequences of length nights from/to entrance."""
        out = []

        def rec(pos, night, seq, streak):
            if night == self.nights:
                if self.day_ok(pos, entrance):
                    out.append(tuple(seq))
                return
            d = start + timedelta(days=night)
            for c in self.camps:
                if c == pos:
                    if not self.basecamp_ok:
                        continue
                    if self.max_stay and streak + 1 > self.max_stay:
                        continue
                elif not self.day_ok(pos, c):
                    continue
                if not self.open_night(c, d):
                    continue
                rec(c, night + 1, seq + [c],
                    streak + 1 if c == pos else 1)

        rec(entrance, 0, [], 0)
        return out

    def endings(self, entrance, start, night, pos, streak=1):
        """Feasible completions from sleeping at pos on night index night-1."""
        if night == self.nights:
            return 1 if self.day_ok(pos, entrance) else 0
        d = start + timedelta(days=night)
        total = 0
        for c in self.camps:
            if c == pos:
                if not self.basecamp_ok or (self.max_stay and streak + 1 > self.max_stay):
                    continue
            elif not self.day_ok(pos, c):
                continue
            if self.open_night(c, d):
                total += self.endings(entrance, start, night + 1, c,
                                      streak + 1 if c == pos else 1)
        return total

    def route_nodes(self, entrance, seq):
        """Every node the trip touches: sleeps, the entrance, and all
        pass-throughs on each day's shortest leg. Powers --via."""
        stops = [entrance] + list(seq) + [entrance]
        nodes = set()
        for a, b in zip(stops, stops[1:]):
            if a == b:
                nodes.add(a)
                continue
            _, _, path = self._leg(a, b)
            nodes.update(path or (a, b))
        return nodes

    # -------------------------------------------------------------------
    def classify(self, entrance, seq):
        stops = [entrance] + [c for c in seq] + [entrance]
        hops = []
        for a, b in zip(stops, stops[1:]):
            if a == b:
                continue
            _, _, path = self._leg(a, b)
            hops.extend(self.g.leg_edges(path))
        if not hops:
            return "basecamp"
        stem = 0
        h = list(hops)
        while len(h) >= 2 and h[0] == h[-1]:
            h = h[1:-1]
            stem += 1
        if not h:
            return "out_and_back"
        if len(set(h)) == len(h):
            return "loop" if stem == 0 else "lollipop"
        return "mixed"

    def day_stats(self, entrance, seq):
        stops = [entrance] + list(seq) + [entrance]
        days = []
        for a, b in zip(stops, stops[1:]):
            mi, gain, _ = (0.0, 0, None) if a == b else self._leg(a, b)
            days.append((mi, gain))
        return days

    def batch(self, entrances, start, end, trip_type="any", trip_types=None):
        allow = _normalize_types(trip_types, trip_type)
        rows = []
        d = start
        while d <= end:
            for ent in entrances:
                for seq in self.itineraries(ent, d):
                    t = self.classify(ent, seq)
                    if allow is not None and t not in allow:
                        continue
                    rows.append({"start": d, "entrance": ent, "seq": seq,
                                 "type": t,
                                 "days": self.day_stats(ent, seq)})
            d += timedelta(days=1)
        return rows
