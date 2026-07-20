"""
switchback.plans: the canonical trip request and result contract.

This is the consumer-facing vocabulary layer mandated by
project/MASTER_COURSE_CORRECTION.md. The solver keeps its internal
row shapes; everything the interface consumes goes through these
models instead. Stdlib only, like the rest of the engine.

The load-bearing rule is the complete-night invariant: every calendar
night between a plan's first and last night carries exactly one stay
record, which may be an explicit unplanned gap, but never silence.
"""
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta

# Vocabulary. Interfaces render these; never invent new strings inline.
STAY_TYPES = ("frontcountry_campground", "backcountry_camp", "zone",
              "first_come_site", "permit_free", "unplanned")
POLICIES = ("reservation", "first_come", "walk_up", "permit_free", "unknown")
AVAILABILITY = ("reservable", "first_come", "walk_up", "permit_free",
                "not_available", "unknown")
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

    def to_dict(self):
        d = asdict(self)
        d["start"] = self.start.isoformat()
        d["latest_start"] = self.latest_start.isoformat()
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

    if errors:
        return None, errors
    return TripRequest(
        slug=slug, start=start, latest_start=latest, nights=nights,
        party=party, pref_mi=pref_mi, max_mi=max_mi, pref_gain=pref_gain,
        max_gain=max_gain, shapes=shapes,
        first_come_ok=bool(raw.get("first_come_ok", True)),
        arrival_night=bool(raw.get("arrival_night", False)),
        recovery_night=bool(raw.get("recovery_night", False)),
        limit=limit), []


def night_stay(d, index, name, stay_type, policy, availability,
               confidence, remaining=None, booking_action=None,
               booking_label=None, booking_url=None, source=None,
               fetched_at=None, notes=None):
    assert stay_type in STAY_TYPES, stay_type
    assert policy in POLICIES, policy
    assert availability in AVAILABILITY, availability
    assert confidence in CONFIDENCE, confidence
    return {"date": d.isoformat(), "night": index, "name": name,
            "stay_type": stay_type, "policy": policy,
            "availability": availability, "remaining": remaining,
            "booking": {"action": booking_action, "label": booking_label,
                        "url": booking_url},
            "source": source, "fetched_at": fetched_at,
            "confidence": confidence, "notes": notes or []}


def overall_confidence(nights):
    if not nights:
        return "unknown"
    worst = min(nights, key=lambda n: _CONF_RANK.get(n["confidence"], 0))
    return worst["confidence"]


def complete_night_problems(plan):
    """Returns a list of invariant violations for a plan dict: every
    calendar night from the first stay through the last must carry
    exactly one record. Empty list means the plan is honest."""
    nights = plan.get("nights") or []
    if not nights:
        return ["plan has no night records at all"]
    problems = []
    dates = [date.fromisoformat(n["date"]) for n in nights]
    if sorted(dates) != dates:
        problems.append("night records are out of date order")
    seen = set()
    for d in dates:
        if d in seen:
            problems.append(f"two stay records for the night of {d}")
        seen.add(d)
    d = dates[0]
    while d <= dates[-1]:
        if d not in seen:
            problems.append(f"no stay record for the night of {d}")
        d += timedelta(days=1)
    for n in nights:
        if n["stay_type"] == "unplanned" and not plan.get("warnings"):
            problems.append(f"unplanned night {n['date']} carries no warning")
    return problems
