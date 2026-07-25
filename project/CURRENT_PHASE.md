# CURRENT_PHASE.md

Updated 2026-07-25. The active implementation phase under
project/MASTER_COURSE_CORRECTION.md.

## Phase: the Mount Rainier end-to-end vertical slice

Goal: one destination where a real person can plan a real trip
through the interface without interpreting internal codes or raw
solver output.

## Landed this phase (2026-07-20 session)

- switchback/plans.py: TripRequest and TripPlan contract, validation
  with plain-language errors, the complete-night invariant checker,
  and the availability and confidence vocabularies.
- switchback/planner.py: orchestration above the untouched solver.
  Request-scoped hard limits (profile.json is a visible default,
  never a silent input), complete nightly records including arrival
  and recovery frontcountry stays, honesty labels, booking actions,
  freshness stamps, quantified relaxation suggestions on zero
  results, and a warning when an all-zero window may be a failed
  fetch rather than a sellout.
- switchback/frontcountry.py plus parks/frontcountry/rainier.json:
  curated arrival and recovery campgrounds (Cougar Rock, White River,
  Ohanapecosh, Mowich Lake) keyed to graph entrances with drive
  times, policies, and booking guidance. Live campground inventory is
  NOT fetched; reservation campgrounds honestly read unknown.
- Web API: POST /api/plan (structured plans with geometry),
  POST /api/plan/gpx (GPX for a selected plan), GET /api/plan/defaults.
- Web UI: "Plan trips" is the primary flow in the map app: a
  progressive form with effort presets and a plain-English summary,
  recommendation cards without raw scores, a night-by-night trip
  detail with booking links and warnings, route drawn on the existing
  map, GPX download. The old list and adventure modes remain as
  secondary buttons.
- Golden tests: tests/test_planner.py (12 scenarios) and
  tests/test_plan_api.py, all offline, discovered by the standard
  `python3 -m pytest -q` command with the rest of the suite.
- Fixed in passing: a latent JavaScript syntax error in the map app's
  quit link that would have blanked the whole app in a real browser.

## Repaired 2026-07-20 after the post-alignment audit

The independent audit of this phase found the primary form crashed on
submit (it destroyed itself before reading its own values), the
complete-night checker validated only the observed records instead of
the declared trip window, plans were free-form dicts, policy and
availability were conflated, and the Rainier frontcountry data was
wrong for 2026 (Ohanapecosh is closed for construction; White River
is first-come). All fixed: the constraint form now lives in its own
persistent container, plans/days/nights/booking/warnings are typed
dataclasses, the invariant validates the declared window, policy and
availability are separate vocabularies, closures are date-aware and a
closed campground can never be recommended for a closed date, the
first-come tolerance now also governs frontcountry selection, the
internal codes/via/shape controls moved behind Classic mode, and a
real-browser test drives the whole flow (and provably fails against
the pre-fix page).

## Landed since (v3.6.x and v3.7.0)

- v3.6.1 to v3.6.3: direction honesty, calibration display fixes, and
  the first calibration fold-in to scoring weights.
- v3.6.4: the Maroon Zone anchor bug fixed, the long-standing P0.
- v3.7.0: curated trail conditions (tread) as a difficulty axis
  orthogonal to grade, and the difficulty ladder recalibrated down to
  a 6 mi / 1500 ft comfortable day with an Extreme tier added.

## Gate 2 PASSED 2026-07-25: live-network verification

Run against real rec.gov inventory for permit 4675317, through both
plan_trips and the actual browser path (POST /api/plan, POST
/api/plan/gpx). Five plans returned with real per-night remaining
counts, the complete-night invariant held on every plan, both booking
links resolved HTTP 200, a same-day window honestly returned zero
plans plus a quantified relaxation, and the GPX parsed as valid GPX
1.1 inside the Rainier bbox. Three defects were found and fixed the
same session: seasonal frontcountry closures were not enforced (White
River was offered for December 25), the "Easiest option" badge was
picked on totals rather than the hardest day, and the GPX disclaimer
claimed straight lines while emitting real trail geometry. See the
2026-07-25 HANDOFF entry for the full record.

## Landed 2026-07-25: the controlled edit subset (v3.8.0)

switchback/edit.py, four operations on a selected recommendation:
swap the camp on one night, add a layover, remove a layover, reverse
direction. Every edit is re-validated from scratch against the
request's own limits and freshly fetched availability, then rebuilt
through the same planner code path as a searched plan, so the
complete-night invariant and the honesty labels hold identically. A
broken edit is refused with the specific reason and the trip is left
alone. edit_options computes what is offerable by actually attempting
each edit, so the interface cannot offer a change the engine will then
reject. Wired as POST /api/plan/edit and /api/plan/edit/options, and
into the trip detail as an "Adjust this trip" panel that keeps the
original recommendation recoverable. Covered by tests/test_edit.py (9
scenarios), the plan API suite, and the real-browser test.

## Remaining before the phase is complete

1. Owner browser test drive of the Plan trips flow (OWNER.md items 9a
   and 9c). This is now the ONLY gate left before Rainier can be
   promoted out of VERIFICATION BLOCKED (project/COVERAGE_STATUS.md).
2. Frontcountry policy data must be revalidated against nps.gov each
   season (revalidate_after fields in parks/frontcountry/rainier.json).
   The season_window bounds added 2026-07-25 are a plain reading of
   the published season prose, not park-confirmed exact dates, so
   shoulder-season nights near the bounds deserve a second look.

## Not in this phase

New destinations, live frontcountry inventory, cross-destination
search, route repair beyond relaxation suggestions, Campflare API
integration, personalization. See project/PARKED_FEATURES.md.
