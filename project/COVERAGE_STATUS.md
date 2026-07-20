# COVERAGE_STATUS.md

Updated 2026-07-20. The classification policy for every destination,
per project/MASTER_COURSE_CORRECTION.md. The generated inventory of
areas lives in coverage/COVERAGE.md (written by the app); this file
defines the ladder and pins the classifications that matter. The
public interface must distinguish reliable from experimental
recommendations.

## The ladder

1. MAPPED ONLY: boundary and trail lines draw on the map, nothing else.
2. ROUTE DATA AVAILABLE: a trail network exists for drawing or
   corridor work; no camp graph.
3. SOLVER SUPPORTED: camp graph plus edges; itineraries enumerate.
4. AVAILABILITY SUPPORTED: live rec.gov inventory wired per camp;
   bookable sequences are real.
5. COMPLETE-TRIP SUPPORTED: the full planner journey works, including
   nightly records, frontcountry arrival curation, honesty labels,
   and golden tests.
6. FULLY VERIFIED: a human has taken or fully dry-run a recommended
   trip and the data survived contact.
7. EXPERIMENTAL: any destination whose data is oracle-gated or
   suspect, whatever else it has.

## Current classifications

- Mount Rainier (rainier): SOLVER SUPPORTED plus planning layer
  implemented, VERIFICATION BLOCKED (reclassified 2026-07-20 by the
  post-alignment audit; the earlier complete-trip-supported label was
  premature). The automated golden scenarios and a real-browser
  workflow test now pass, the form-crash and frontcountry data
  defects the audit found are fixed, but promotion to COMPLETE-TRIP
  SUPPORTED still requires: an owner browser walkthrough, one
  live-network run against real rec.gov inventory, and a live check
  that the booking links resolve. The gates live in
  project/CURRENT_PHASE.md.
- Glacier (glacier), Rocky Mountain NP (rmnp), Teton Crest
  (tetoncrest), Indian Peaks (indianpeaks), Maroon Bells
  (maroonbells), Sand Dunes (sanddunes), Enchantments
  (enchantments), Olympic region (olympic996 area set), Lena (lena):
  AVAILABILITY SUPPORTED. Lena is the mixed-policy showcase; Maroon
  Bells is additionally EXPERIMENTAL until the Maroon Zone anchor
  relocation lands (known open bug, see CLAUDE.md).
- Dispersed pilots (vestalpilot and successors): EXPERIMENTAL by
  construction, oracle-gated.
- Long-trail corridors (CT, CDT-CO, PCT-WA): ROUTE DATA AVAILABLE.
- Everything else in the 72-area atlas: MAPPED ONLY.

Promotion to level 5 requires the golden-scenario suite passing for
that destination plus curated frontcountry arrival data. Promotion to
level 6 requires an owner-verified trip.
