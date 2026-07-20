# MASTER COURSE-CORRECTION DIRECTIVE

Adopted 2026-07-20 from the owner's directive, dash-sanitized on ingest
per the house rule. This is the newest product source of truth. It
supersedes conflicting priorities in project/PRODUCT.md (both parts),
older roadmaps, and release-sequencing habits. It does not override
HANDOFF.md on technical facts. The roadmap that implements it lives in
project/ROADMAP.md; the live status lives in project/CURRENT_PHASE.md;
the parked list lives in project/PARKED_FEATURES.md; destination
classifications live in project/COVERAGE_STATUS.md. Do not duplicate
those documents here.

## 1. Core product definition

Switchback is an availability-aware backpacking trip recommendation
and itinerary-construction product. The promise: given my destination
or search region, dates, party size, physical limits, trip
preferences, and logistical constraints, show me complete backpacking
trips I can realistically take, explain why each fits, account for
where I sleep every night, and help me understand what must be booked.

Switchback answers "where can I actually go, and what complete trip
should I take?" It does not primarily answer "is one individual
campsite available?" Campflare and rec.gov surface availability;
Switchback turns availability, routes, camps, constraints, and
preferences into complete feasible trips. Campflare is a complement,
not a competitor; never build on an unauthorized Campflare
integration. Acceptable early behavior: explain that Campflare can
watch a missing camp, link out, let the user mark a stay as
externally monitored, and show when one unavailable stay blocks an
otherwise valid trip.

## 2. Primary user journey

Describe the trip; receive multiple complete recommendations; compare
them; open one; inspect its night-by-night itinerary and route;
understand availability and booking; modify or repair it; save,
share, monitor, or export. This journey is the organizing structure
for the codebase, roadmap, terminology, and interface.

## 3. Definition of a complete trip

A trip distinguishes total dates, an optional frontcountry arrival
night, backcountry nights, an optional recovery night, hiking days,
and travel days. It may mix reservable camps, first-come camps,
permit-free or dispersed stays, and explicitly identified unresolved
gaps.

THE COMPLETE-NIGHT INVARIANT: for every night between the trip's
beginning and end, the plan contains exactly one of a planned stay, a
clearly labeled optional stay, or an explicit unresolved-gap warning.
Never silently omit a night. A night cannot be implied only through
route geometry or an encoded campsite string. Enforced by
switchback/plans.py complete_night_problems and the golden tests.

## 4. Required user inputs

Essential: destination or region; exact or flexible dates; backcountry
nights; party size; preferred and maximum daily mileage; preferred
and maximum daily elevation gain; acceptable trip shapes (loop, out
and back, moving point-to-point when it truly exists, basecamp);
first-come tolerance; arrival-night and recovery-night toggles.
Important preferences to leave design room for: lakes, alpine
scenery, forest, swimming, solitude, iconic scenery, easier first or
final day, shuttle tolerance, dogs, permit-free preference, drive
limits. Internal camp codes, node ids, solver vocabulary, and raw
scoring weights are never primary user inputs.

## 5. Required recommendation output

Every recommendation is a structured TripPlan (switchback/plans.py):
stable id, destination, trailhead, dates, party, shape, total mileage
and gain, hardest day, complete nightly itinerary, daily route
segments, per-night stay type and policy and availability status with
freshness, booking action and official link where available, route
geometry, fit explanation, tradeoffs, confidence, data-quality
status, and unresolved warnings. Never describe a stay as available
or reservable unless the data actually supports it.

## 6. What to preserve

Do not scrap or broadly rewrite the working foundation: the solver,
graph data, permit and inventory integrations, availability history,
watch foundations, camp sequencing, mileage and elevation work, route
geometry, trail-following GPX, the trip-shape concepts, dual-inventory
merging, mixed permit-policy logic, existing destination datasets,
dispersed and cross-boundary experiments, and the offline tests.
Orchestration and presentation sit ABOVE these systems
(switchback/planner.py). Replacing any subsystem requires a written
case: what it does, why it cannot support the product, why an adapter
is insufficient, and the regression risk.

## 7. Honesty and coverage rules

Every destination carries a classification from
project/COVERAGE_STATUS.md; never describe all mapped areas as fully
supported. First-come is labeled first-come, unknown is labeled
unknown, freshness is visible, and an all-zero availability window is
flagged as possibly a failed fetch, never silently presented as sold
out. When no exact trip exists, return quantified relaxation
suggestions (the minimum change that makes a trip feasible), never a
bare "no results".

## 8. UI principles

Consumer language, progressive disclosure, strong defaults, one
primary action per screen, honest uncertainty, visible freshness, no
dead ends, no unexplained codes or scores, no silent assumptions, no
hidden gaps, no false precision. Constraint entry reads like booking
a trip, not configuring a graph algorithm; presets translate into
editable numbers; a plain-English summary precedes the search.
Recommendation cards carry names, status, dates, effort, stays,
reasons, tradeoffs, and confidence instead of raw decimal scores;
scoring translates into labels (best overall fit, easiest option,
most available, and similar). The route editor grows out of a
selected recommendation, not a separate drawing mode.

## 9. Git and release rules

Confirm the branch, use a dedicated branch, never force-push over
unrelated work, never push directly to main, small coherent commits,
tests before each implementation commit. Versioning: no version bump
for routine or documentation-only work; bump only for a meaningful,
user-testable milestone; no major version for internal course
corrections. This section supersedes the old version-per-PR habit and
CLAUDE.md has been updated to match.

## 10. Definition of success

One coherent product direction; horizons in ROADMAP.md reflect this
directive; scope creep explicitly parked; foundations preserved; a
user can enter real constraints and receive structured complete
trips with every night accounted for; Rainier has a tested
end-to-end flow with frontcountry arrival support in narrow useful
form; cards are understandable without internal knowledge; the map
and GPX are connected to recommendations; availability and
uncertainty are honest; one standard test command runs the whole
suite; work proceeds beyond documentation into functioning behavior.
