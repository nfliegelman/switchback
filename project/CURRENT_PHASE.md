# CURRENT_PHASE.md

Updated 2026-07-20. The active implementation phase under
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

## Remaining before the phase is complete

1. Owner browser test drive of the Plan trips flow (OWNER.md item 9a);
   no real browser has rendered it yet because this container cannot
   reach the map CDN. Verified headlessly instead.
2. Live-network verification against real rec.gov inventory.
3. Rainier's COVERAGE_STATUS.md classification moves to complete-trip
   supported once 1 and 2 pass.
4. Then the controlled edit-trip subset (camp swap, layover, reverse)
   from a selected recommendation, per the directive's editor scope.

## Not in this phase

New destinations, live frontcountry inventory, cross-destination
search, route repair beyond relaxation suggestions, Campflare API
integration, personalization. See project/PARKED_FEATURES.md.
