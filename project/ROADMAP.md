# ROADMAP.md

The active plan, and only the active plan. Rewritten 2026-07-20 around
the strategic horizons in project/MASTER_COURSE_CORRECTION.md, which
supersedes the previous phase-numbered roadmap (its Phase 0 shipped as
v3.3.0; its Phases 1 to 3 are absorbed into the short-term horizon
below; its Phases 4 and 5 map to the medium and long term). Product
definition lives in MASTER_COURSE_CORRECTION.md; live status in
CURRENT_PHASE.md; parked work in PARKED_FEATURES.md; shipped history
in CHANGELOG.md.

## SHORT-TERM: make one destination genuinely useful

Not broad coverage; proving the complete product loop on Mount
Rainier (chosen for its mature graph, live permit wiring, and real
frontcountry campgrounds). The milestone is complete only when a user
can plan a realistic Rainier trip through the interface without
interpreting internal codes or raw solver output.

Required and status as of v3.5.0:

- Structured trip request with user-entered physical limits: DONE.
- Multiple Rainier recommendations with complete nightly stay
  records and no silent overnight gaps: DONE, invariant-tested.
- Curated frontcountry arrival and recovery stays: DONE (curated
  dataset, honest unknown-availability labels).
- Availability, booking actions, and freshness on every stay: DONE.
- Honest first-come and unknown handling: DONE.
- Recommendation cards and complete trip detail in the app,
  connected to the existing map (inspection, not editing) and GPX:
  DONE, repaired 2026-07-20 after the post-alignment audit caught the
  submit crash.
- Automated golden-scenario tests under one standard command: DONE,
  plus a real-browser workflow test (form to cards to detail).
- Date-aware frontcountry closures and corrected Rainier campground
  policies: DONE (Ohanapecosh closed for 2026, White River
  first-come).
- Owner browser test drive and one live-network verification:
  REMAINING; Rainier stays classified VERIFICATION BLOCKED until
  they pass (project/COVERAGE_STATUS.md).
- Controlled edit-trip subset from a selected recommendation (camp
  swap, layover add or remove, reverse): REMAINING.

## MEDIUM-TERM: make the recommendation engine differentiated

After the slice is verified: three to five trip-ready regions (RMNP
and Lena first; Indian Peaks when dual-permit correctness deserves a
showcase); cross-destination search; flexible-date and drive-radius
search; saved preference profiles; trip-level availability
monitoring on the existing watch substrate; route repair, camp
substitution, direction reversal, basecamp conversion; deeper
quantified relaxation; permit-free and mixed-policy fallbacks using
the corridor and dispersed assets; better frontcountry arrival and
recovery options with live inventory; improved confidence and
freshness reporting; calibration from the owner's reaction sheets.
Target outcome: "I have these dates and limits; Switchback found
several complete trips I would not have identified on my own."

Data-integrity precondition carried forward: the Maroon Zone anchor
relocation and Elks edge re-audit before any Elks-adjacent
destination is promoted.

## LONG-TERM: the planning layer across availability systems

Larger regional coverage and national portfolio search;
road-corridor backpacking discovery (a logistical wrapper around
outdoor-trip discovery, never a generic road-trip planner);
frontcountry and backcountry vacation orchestration; condition-aware
recommendations (snow, fire, water, road access, season); robust
permit-free and cross-boundary routing; personalized ranking; group
constraint reconciliation; paid trip-level monitoring; formal
partner integrations; mobile-specific experience; user-submitted
corrections.

## Owner gates on the critical path

The Plan trips browser test drive (OWNER.md item 9a). The calibration
half hour (scaffold ready; P1 scoring work waits on reactions). The
two stuck release taps (OWNER.md phone item 5).
