"""
switchback.plans: the canonical trip request and result contract.

This is the consumer-facing vocabulary layer mandated by
project/MASTER_COURSE_CORRECTION.md, hardened per the 2026-07-20
post-alignment audit: plans, days, nights, booking actions, and
warnings are typed dataclasses (serialized to dicts only at the API
boundary), and booking POLICY is a separate concept from current
AVAILABILITY. Stdlib only, like the rest of the engine.

The load-bearing rule is the complete-night invariant, validated
against the DECLARED trip window (the trip_window a plan commits to),
never against whatever night records happen to be present: every
calendar night in the declared window carries exactly one stay
record, which may be an explicit unplanned gap, but never silence.
"""
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta

# Vocabulary. Interfaces render these; never invent new strings inline.
# POLICY says how a stay is booked; AVAILABILITY says what the data
# shows for the requested date. "Reservable" is a policy, not a state.
STAY_TYPES = ("frontcountry_campground", "backcountry_camp", "zone",
              "first_come_site", "permit_free", "unplanned")
POLICIES = ("reservable", "first_come", "walk_up", "permit_free", "unknown")
AVAILABILITY = ("available", "limited", "full", "not_released", "unknown")
CONFIDENCE = ("live_inventory", "official_policy_verified", "curated",
              "derived", "experimental", "unknown")
SHAPES = ("loop", "out and back", "basecamp", "any")

# Weakest-link ordering for a plan's overall confidence.
_CONF_RANK = {"live_inventory": 5, "official_policy_verified": 4,
              "curated": 3, "derived": 2, "experimental": 1, "unknown": 0}


@dataclass
class TripRequest:
    slug: str
    start: date
    latest_start: date
    nights: int
    party: int
    pref_mi: float
    max_mi: float
    pref_gain: int
    max_gain: int
    shapes: list = field(default_factory=list)   # empty means any
    first_come_ok: bool = True
    arrival_night: bool = False
    recovery_night: bool = False
    limit: int = 8
    pace: dict = None      # normalized band->mph table; None = defaults

    def to_dict(self):
        d = asdict(self)
        d["start"] = self.start.isoformat()
        d["latest_start"] = self.latest_start.isoformat()
        return d


@dataclass
class BookingAction:
    action: str            # book_permit, check_availability, arrive_early,
    label: str             # none_needed, plan_yourself
    url: str = None

    def to_dict(self):
        return {"action": self.action, "label": self.label, "url": self.url}


@dataclass
class TripWarning:
    code: str              # unplanned_night, campground_closed,
    message: str           # invariant_violation, data_suspect
    date: str = None       # ISO night the warning refers to, when it does

    def to_dict(self):
        return {"code": self.code, "message": self.message,
                "date": self.date}


@dataclass
class NightStay:
    date: date
    night: int
    name: str
    stay_type: str
    policy: str
    availability: str
    confidence: str
    remaining: int = None
    booking: BookingAction = None
    source: str = None
    fetched_at: str = None
    notes: list = field(default_factory=list)

    def __post_init__(self):
        assert self.stay_type in STAY_TYPES, self.stay_type
        assert self.policy in POLICIES, self.policy
        assert self.availability in AVAILABILITY, self.availability
        assert self.confidence in CONFIDENCE, self.confidence

    def to_dict(self):
        return {"date": self.date.isoformat(), "night": self.night,
                "name": self.name, "stay_type": self.stay_type,
                "policy": self.policy, "availability": self.availability,
                "remaining": self.remaining,
                "booking": self.booking.to_dict() if self.booking else None,
                "source": self.source, "fetched_at": self.fetched_at,
                "confidence": self.confidence, "notes": list(self.notes)}


@dataclass
class TripDay:
    day: int
    date: date
    kind: str              # travel, hike, layover
    from_name: str
    to_name: str
    miles: float
    gain_ft: int
    est_hours: float = None          # grade-aware duration estimate
    steepest_grade_pct: float = None  # characteristic grade of the
                                      # steepest edge on the day
    note: str = None                  # e.g. packs-off day hikes on layovers

    def to_dict(self):
        return {"day": self.day, "date": self.date.isoformat(),
                "kind": self.kind, "from": self.from_name,
                "to": self.to_name, "miles": self.miles,
                "gain_ft": self.gain_ft, "est_hours": self.est_hours,
                "steepest_grade_pct": self.steepest_grade_pct,
                "note": self.note}


@dataclass
class TripPlan:
    id: str
    title: str
    destination: dict
    trailhead: dict
    shape: str
    party: int
    start: date            # first hiking day
    end: date              # checkout morning after the last night
    first_night: date      # first calendar night the plan commits to
    alternate_starts: list = field(default_factory=list)
    nights: list = field(default_factory=list)     # [NightStay]
    days: list = field(default_factory=list)       # [TripDay]
    totals: dict = field(default_factory=dict)
    fit: dict = field(default_factory=dict)
    availability_summary: str = ""
    confidence: str = "unknown"
    data_quality: list = field(default_factory=list)
    warnings: list = field(default_factory=list)   # [TripWarning]
    checked_at: str = None
    gpx: dict = field(default_factory=dict)
    day_paths: list = None
    badge: str = None

    def to_dict(self):
        d = {"id": self.id, "title": self.title,
             "destination": self.destination, "trailhead": self.trailhead,
             "shape": self.shape, "party": self.party,
             "start": self.start.isoformat(), "end": self.end.isoformat(),
             "trip_window": {"first_night": self.first_night.isoformat(),
                             "checkout": self.end.isoformat()},
             "alternate_starts": list(self.alternate_starts),
             "nights": [n.to_dict() for n in self.nights],
             "days": [x.to_dict() for x in self.days],
             "totals": self.totals, "fit": self.fit,
             "availability_summary": self.availability_summary,
             "confidence": self.confidence,
             "data_quality": list(self.data_quality),
             "warnings": [w.to_dict() for w in self.warnings],
             "checked_at": self.checked_at, "gpx": self.gpx}
        if self.day_paths is not None:
            d["day_paths"] = self.day_paths
        if self.badge:
            d["badge"] = self.badge
        return d


def _parse_date(v, name, errors):
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v))
    except (TypeError, ValueError):
        errors.append(f"{name} must be a date like 2026-08-14")
        return None


def validate_request(raw, profile=None):
    """dict in, (TripRequest or None, [plain-language errors]) out.

    Effort limits fall back to the saved profile as visible defaults;
    they are echoed back on every response, never used silently.
    """
    profile = profile or {}
    errors = []
    slug = str(raw.get("slug") or "").strip()
    if not slug:
        errors.append("pick a destination")
    start = _parse_date(raw.get("start"), "start", errors)
    latest = raw.get("latest_start")
    latest = _parse_date(latest, "latest_start", errors) if latest else start
    if start and latest and latest < start:
        errors.append("latest_start cannot be before start")

    def num(key, default, lo, hi, what):
        v = raw.get(key)
        if v is None:
            v = default
        try:
            v = float(v)
        except (TypeError, ValueError):
            errors.append(f"{what} must be a number")
            return default
        if v < lo or v > hi:
            errors.append(f"{what} must be between {lo} and {hi}")
        return v

    pref = profile.get("daily_pref") or {}
    mx = profile.get("daily_max") or {}
    nights = int(num("nights", 2, 1, 10, "backcountry nights"))
    party = int(num("party", profile.get("party_size", 2), 1, 12,
                    "party size"))
    pref_mi = num("pref_mi", pref.get("miles", 9.0), 1, 30,
                  "preferred daily miles")
    max_mi = num("max_mi", mx.get("miles", 13.0), 1, 40,
                 "maximum daily miles")
    pref_gain = int(num("pref_gain", pref.get("gain_ft", 2200), 0, 12000,
                        "preferred daily gain"))
    max_gain = int(num("max_gain", mx.get("gain_ft", 4000), 100, 15000,
                       "maximum daily gain"))
    if max_mi < pref_mi:
        errors.append("maximum daily miles is below your preferred miles; "
                      "raise the maximum or lower the preference")
    if max_gain < pref_gain:
        errors.append("maximum daily gain is below your preferred gain; "
                      "raise the maximum or lower the preference")

    shapes = raw.get("shapes") or []
    if isinstance(shapes, str):
        shapes = [s.strip() for s in shapes.split(",") if s.strip()]
    shapes = [s.lower() for s in shapes]
    bad = [s for s in shapes if s not in SHAPES]
    if bad:
        errors.append(f"unknown trip shape(s): {', '.join(bad)}; "
                      f"choose from {', '.join(SHAPES)}")
    if "any" in shapes:
        shapes = []
    limit = int(num("limit", 8, 1, 25, "result limit"))

    from .pace import normalize_pace
    pace_spec = raw.get("pace")
    if pace_spec is None:
        pace_spec = profile.get("pace")
    pace, pace_errors = normalize_pace(pace_spec)
    errors.extend(pace_errors)

    if errors:
        return None, errors
    return TripRequest(
        slug=slug, start=start, latest_start=latest, nights=nights,
        party=party, pref_mi=pref_mi, max_mi=max_mi, pref_gain=pref_gain,
        max_gain=max_gain, shapes=shapes,
        first_come_ok=bool(raw.get("first_come_ok", True)),
        arrival_night=bool(raw.get("arrival_night", False)),
        recovery_night=bool(raw.get("recovery_night", False)),
        limit=limit, pace=pace), []


def overall_confidence(nights):
    """Weakest link across NightStay objects or serialized dicts."""
    if not nights:
        return "unknown"
    def conf(n):
        return n["confidence"] if isinstance(n, dict) else n.confidence
    worst = min(nights, key=lambda n: _CONF_RANK.get(conf(n), 0))
    return conf(worst)


def complete_night_problems(plan):
    """Invariant violations for a TripPlan or its serialized dict,
    validated against the DECLARED trip window: every calendar night
    from trip_window.first_night up to (not including) checkout must
    carry exactly one stay record; no out-of-window stays; every
    unplanned night carries a warning. The declared window is the
    authority; a plan cannot pass by simply omitting records."""
    d = plan.to_dict() if hasattr(plan, "to_dict") else plan
    nights = d.get("nights") or []
    problems = []
    win = d.get("trip_window") or {}
    try:
        first = date.fromisoformat(win.get("first_night") or d["start"])
        checkout = date.fromisoformat(win.get("checkout") or d["end"])
    except (KeyError, TypeError, ValueError):
        return ["plan declares no usable trip window"]
    n_expected = (checkout - first).days
    if n_expected < 1:
        return ["declared trip window contains no nights"]
    expected = [(first + timedelta(days=i)).isoformat()
                for i in range(n_expected)]
    by_date = {}
    for n in nights:
        by_date.setdefault(n["date"], []).append(n)
    for iso in expected:
        got = by_date.get(iso, [])
        if not got:
            problems.append(f"no stay record for the night of {iso}")
        elif len(got) > 1:
            problems.append(f"{len(got)} stay records for the night of {iso}")
    for iso in by_date:
        if iso not in expected:
            problems.append(f"stay record on {iso} falls outside the "
                            f"declared window {expected[0]} to {expected[-1]}")
    warnings = d.get("warnings") or []
    wtexts = " ".join((w.get("message", "") if isinstance(w, dict)
                       else str(w)) for w in warnings)
    for n in nights:
        if n.get("stay_type") == "unplanned" and not wtexts:
            problems.append(f"unplanned night {n['date']} carries no warning")
    return problems
