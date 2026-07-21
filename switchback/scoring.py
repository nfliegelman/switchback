"""
switchback.scoring: M5 ranking layer.

score = w_day * mean(day_fit) + w_camp * mean(camp_percentile)
        + w_lakes * lake_night_share + w_solitude * (1 - demand_pct)

Every coefficient lives in scoring.json (repo root), editable without
code changes. Camp quality is a percentile WITHIN its park, computed
from a hand-set feature prior (lake, creek, elevation band, trail depth
from the graph) that a personal rating in parks/ratings.json overrides
permanently. The crowd term is a stub: it reads parks/demand.json and
contributes nothing until the M8 scan history creates that file.

Cold-start guarantee per SPEC section 4: with zero personal ratings and
zero demand history, ranking works on computed priors alone.
"""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORING_PATH = os.path.join(_ROOT, "scoring.json")
RATINGS_PATH = os.path.join(_ROOT, "parks", "ratings.json")
DEMAND_PATH = os.path.join(_ROOT, "parks", "demand.json")

DEFAULT_SCORING = {
    "weights": {"day_fit": 0.4, "camp": 0.6, "lakes": 0.15, "solitude": 0.0},
    "prior": {
        "base": 2.8,
        "lake_within_400m": 0.9,
        "creek_within_200m": 0.15,
        "elevation_bands_ft": [[0, 4000, 0.0], [4000, 5500, 0.3],
                               [5500, 99999, 0.55]],
        "per_3_trail_miles_from_trailhead": 0.12,
        "trail_depth_cap": 0.5,
    },
    "note": "Hand-set guesses. Recalibrate after 20+ personal ratings. "
            "day_fit is asymmetric since 2026-07-20: easier than the "
            "preferred day is good, only harder is penalized.",
}


def _merged(path, defaults):
    out = json.loads(json.dumps(defaults))
    try:
        with open(path) as fh:
            user = json.load(fh)
    except (OSError, ValueError):
        return out
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def load_scoring():
    return _merged(SCORING_PATH, DEFAULT_SCORING)


def load_ratings(slug):
    try:
        with open(RATINGS_PATH) as fh:
            return json.load(fh).get(slug, {})
    except (OSError, ValueError):
        return {}


def load_demand(slug):
    try:
        with open(DEMAND_PATH) as fh:
            return json.load(fh).get(slug, {})
    except (OSError, ValueError):
        return {}


class Scorer:
    def __init__(self, graph, cfg=None):
        self.g = graph
        self.cfg = cfg or load_scoring()
        self.ratings = load_ratings(graph.slug)
        self.demand = load_demand(graph.slug)
        self._camp_feats = {c["id"]: c for c in graph.park["camps"]
                            if c["included"]}
        self._trail_depth = self._trail_depths()
        self._rating = {}
        for cid, feats in self._camp_feats.items():
            personal = (self.ratings.get(cid) or {}).get("personal_rating")
            self._rating[cid] = (float(personal) if personal is not None
                                 else self.computed_prior(feats))
        self._pct = self._percentiles(self._rating)
        self._dh_raw = {}

    # ------------------------------------------------------------------
    def _trail_depths(self):
        """Trail miles from each graph camp to its nearest entrance.
        Replaces the M2 straight-line placeholder wherever edges exist."""
        depths = {}
        ents = self.g.entrances()
        for c in self.g.camps():
            best = None
            for e in ents:
                got = self.g.leg(c, e)
                if got and (best is None or got[0] < best):
                    best = got[0]
            depths[c] = best
        return depths

    def computed_prior(self, feats):
        p = self.cfg["prior"]
        score = p["base"]
        if feats.get("lake_within_400m"):
            score += p["lake_within_400m"]
        if feats.get("creek_within_200m"):
            score += p["creek_within_200m"]
        elev = feats.get("elevation_ft")
        if elev is not None:
            for lo, hi, bonus in p["elevation_bands_ft"]:
                if lo <= elev < hi:
                    score += bonus
                    break
        depth = self._trail_depth.get(feats["id"])
        if depth is None:
            depth = feats.get("trailhead_dist_mi_straightline")
        if depth:
            score += min(depth / 3.0 * p["per_3_trail_miles_from_trailhead"],
                         p["trail_depth_cap"])
        return max(0.0, min(5.0, round(score, 2)))

    @staticmethod
    def _percentiles(rating):
        ordered = sorted(rating.values())
        n = len(ordered)
        if n <= 1:
            return {k: 0.5 for k in rating}
        return {k: ordered.index(v) / (n - 1) for k, v in rating.items()}

    # ------------------------------------------------------------------
    @staticmethod
    def day_fit(mi, gain, pref_mi, pref_gain):
        """Asymmetric by owner directive 2026-07-20 (supersedes the old
        symmetric effort-fit): a day at or easier than the preference
        is a GOOD day, never penalized just for being easier. Perfect
        fit from 40 percent of preference up to preference; below that
        cushion the credit tapers (a near-zero day is not a great use
        of a day); above preference the old linear penalty applies, so
        limit-matching trips no longer beat comfortable ones."""
        def f(e, pref):
            cushion = 0.4 * pref
            if e > pref:
                return max(0.0, 1 - (e - pref) / pref)
            if e >= cushion:
                return 1.0
            return e / cushion if cushion else 1.0
        return (f(mi, pref_mi) + f(gain, pref_gain)) / 2

    def demand_pct(self, cid):
        d = self.demand.get(cid)
        return d.get("demand_pct") if isinstance(d, dict) else None

    # ---------------------- basecamp day hikes -----------------------
    def _dh_options(self, camp):
        """Out-and-back day-hike candidates from a basecamp: every other
        graph camp with a route. Availability is deliberately ignored;
        you can day-hike to a sold-out camp. That is the whole point of
        basing at the camp that has quota."""
        if camp not in self._dh_raw:
            opts = []
            for dest in self.g.camps():
                if dest == camp:
                    continue
                out = self.g.leg(camp, dest)
                back = self.g.leg(dest, camp)
                if not out or not back or not out[0]:
                    continue
                opts.append({"dest": dest, "name": self.g.name(dest),
                             "rt_mi": round(out[0] + back[0], 1),
                             "rt_gain": out[1] + back[1],
                             "pct": self._pct.get(dest, 0.5),
                             "lake": bool(self._camp_feats.get(dest, {})
                                          .get("lake_within_400m"))})
            self._dh_raw[camp] = opts
        return self._dh_raw[camp]

    def best_layover_fit(self, camp, pref_mi, pref_gain):
        return max((self.day_fit(o["rt_mi"], o["rt_gain"], pref_mi, pref_gain)
                    for o in self._dh_options(camp)), default=0.0)

    MIN_DH_RT_MI = 1.0

    def day_hikes(self, camp, pref_mi, pref_gain, limit=5):
        """Ranked day-hike options: 60 percent destination quality,
        40 percent effort fit against the preferred day."""
        opts = []
        for o in self._dh_options(camp):
            o = dict(o)
            o["fit"] = self.day_fit(o["rt_mi"], o["rt_gain"],
                                    pref_mi, pref_gain)
            o["appeal"] = round(0.6 * o["pct"] + 0.4 * o["fit"], 3)
            opts.append(o)
        walkable = [o for o in opts if o["rt_mi"] <= 2 * pref_mi
                    and o["rt_gain"] <= 2 * pref_gain]
        opts = walkable or opts
        opts.sort(key=lambda o: o["appeal"], reverse=True)
        return opts[:limit]

    def layover_notes(self, row, pref_mi, pref_gain, limit=2):
        ent = row.get("entrance")
        if ent is None:
            return []
        stops = [ent] + list(row["seq"]) + [ent]
        notes = []
        for i, (mi, _g) in enumerate(row["days"]):
            if mi:
                continue
            camp = stops[i]
            short = self.g.name(camp).split(" - ")[0]
            top = self.day_hikes(camp, pref_mi, pref_gain, limit=limit)
            if top:
                alts = "; or ".join(
                    f"{o['name'].split(' - ')[0]} {o['rt_mi']} mi RT, +{o['rt_gain']} ft"
                    + (" (lake)" if o["lake"] else "") for o in top)
                notes.append(f"day {i + 1} layover at {short}, day hike: {alts}")
            else:
                notes.append(f"day {i + 1} layover at {short}, no day-hike routes in graph")
        return notes

    def score(self, row, pref_mi, pref_gain):
        w = self.cfg["weights"]
        ent = row.get("entrance")
        stops = ([ent] + list(row["seq"]) + [ent]) if ent is not None else None
        fits = []
        for i, (mi, gain) in enumerate(row["days"]):
            if mi and mi > 0:
                fits.append(self.day_fit(mi, gain, pref_mi, pref_gain))
            elif stops is not None:
                fits.append(self.best_layover_fit(stops[i], pref_mi, pref_gain))
        day_term = sum(fits) / len(fits) if fits else 0.0
        pcts = [self._pct.get(c, 0.5) for c in row["seq"]]
        camp_term = sum(pcts) / len(pcts)
        lakes = [self._camp_feats.get(c, {}).get("lake_within_400m", False)
                 for c in row["seq"]]
        lake_share = sum(lakes) / len(lakes)
        crowd = 0.0
        if w.get("solitude"):
            ds = [self.demand_pct(c) for c in row["seq"]]
            ds = [d for d in ds if d is not None]
            if ds:
                crowd = w["solitude"] * (1 - sum(ds) / len(ds))
        total = (w["day_fit"] * day_term + w["camp"] * camp_term
                 + w["lakes"] * lake_share + crowd)
        return {"score": round(total, 3), "day_fit": round(day_term, 2),
                "camp_pct": round(camp_term, 2), "lake_share": round(lake_share, 2),
                "lake_nights": sum(lakes)}

    def rank(self, rows, pref_mi, pref_gain):
        scored = []
        for r in rows:
            r = dict(r)
            r.update(self.score(r, pref_mi, pref_gain))
            scored.append(r)
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored

    def camp_card(self, cid):
        f = self._camp_feats.get(cid, {})
        return {"rating": self._rating.get(cid), "pct": self._pct.get(cid),
                "lake": f.get("lake_name") or bool(f.get("lake_within_400m")),
                "trail_depth_mi": self._trail_depth.get(cid)}
