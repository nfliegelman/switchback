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
    "note": "Hand-set guesses. Recalibrate after 20+ personal ratings.",
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
        f_mi = max(0.0, 1 - abs(mi - pref_mi) / pref_mi)
        f_g = max(0.0, 1 - abs(gain - pref_gain) / pref_gain)
        return (f_mi + f_g) / 2

    def demand_pct(self, cid):
        d = self.demand.get(cid)
        return d.get("demand_pct") if isinstance(d, dict) else None

    def score(self, row, pref_mi, pref_gain):
        w = self.cfg["weights"]
        fits = [self.day_fit(mi, gain, pref_mi, pref_gain)
                for mi, gain in row["days"] if mi and mi > 0]
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
