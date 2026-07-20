# ROADMAP.md

The active plan, and only the active plan. As of v3.3.0 (2026-07-17).
Product truth lives in PRODUCT.md (Part 1 adjusts Part 2);
shipped history lives in CHANGELOG.md; deferred items live in
BACKLOG.md with priority labels. This file holds outcomes, not feature
archaeology.

## Vertical-slice destinations (recommended, owner veto open)

Mount Rainier, Rocky Mountain NP, and Lena. Rainier is the brief's own
worked example on a mature graph; RMNP has 86 live camps after the
v2.26 buildout plus real rec.gov frontcountry campgrounds; Lena is the
mixed-policy honesty scenario in miniature. Indian Peaks is the fourth
when dual-permit correctness deserves a showcase.

## Phase 0, product and documentation reset: DONE v3.3.0

PRODUCT.md adopted, this roadmap rewritten, README rewritten, BACKLOG
triaged with priority labels, PARKS.md regenerated with honest support
tiers, standard pytest discovery runs all twelve suites, the false
shuttle option removed, version number visible in every surface the
owner tests.

## Phase 1, request and result contract

Outcome: an API test submits destination, dates, party, visible
preferred and maximum effort, and style toggles, and receives complete
structured TripPlan objects with explicit nights, per-night
availability and booking actions, fit components, confidence labels,
and zero silent profile.json dependence. New planner.py orchestration
above the untouched solver; models per SPEC.md; the complete-night
invariant enforced. Includes the Maroon anchor relocation and edge
re-audit, which is a data-integrity precondition for any Elks-adjacent
work and one focused session.

## Phase 2, coherent UI vertical slice

Outcome: the three-surface workflow (describe, browse, inspect) on the
slice destinations. Constraint form with effort presets and plain
language, grouped recommendation cards without raw decimal scores,
night-by-night trip detail, booking steps, zero-result repair ladder
with quantified relaxations, mobile-first because the owner is.

## Phase 3, frontcountry and integrated editing

Outcome: complete vacation shells. Curated arrival and recovery
campgrounds for the slice destinations with honest policy labels, the
frontcountry-basecamp trip style, and the route editor opening FROM a
selected recommendation with camp swap, layover, reverse, undo, reset,
and live feasibility, built on the camp-list principle in SPEC.md Part 2.

## Phase 4, discovery and repair

Outcome: the market wedge. Cross-destination and flexible-date search,
route repair with quantified suggestions, permit-free and
cross-boundary fallbacks drawing on the corridor and dispersed assets,
saved trip profiles, complete-trip alerts on the existing watch
substrate, Campflare handoff.

## Phase 5, expansion, only after P0 metrics are healthy

Road-corridor search, multi-stop vacations, true point-to-point with
shuttle logistics, broader frontcountry inventory, group planning,
monetization experiments per the archived gates in project/archive/FUTURE.md.

## Owner gates on the critical path

The calibration half hour (P1 scoring work waits on reactions; the
scaffold is ready). The manual UX test script in PRODUCT.md section
18.3 when Phase 2 lands. Smoke tests remain listed in OWNER.md.

## Parked, do not build without new evidence

Everything in PRODUCT.md section 5's parked list, plus Archetype B
Sierra trailhead-quota parks (moved from the old horizon by the
decision filter) and solitude modeling despite its newly unlocked data
source.
