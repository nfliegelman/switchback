# ROADMAP.md

The Switchback engine build tracker. Design rationale lives in SPEC.md and SCOPE.md; this file is only what we are building, in order, with done-criteria. Last updated 2026-07-07.

## Version scheme

v1.0.0 is the state at the first GitHub upload: GUI availability finder, CalTopo exporter, Belly River adventure demo, and the design docs. Each completed milestone below bumps the minor version (M0 lands as v1.1.0, M1 as v1.2.0, and so on). Completing all ten is v2.0.0, the Switchback engine proper. Patch numbers are for fixes.

## Target: v2.0.0, the Switchback engine

A working loop for camp-night permit parks: the engine recommends bookable itineraries within effort bounds, adventure mode walks the frontier interactively in the CLI, and results export to GPX and CalTopo. Two parks at launch: Mount Rainier (4675317) and Glacier (4675321).

Locked decisions (2026-07-07):
- Trip types in the engine: loop, out_and_back, lollipop. Shuttle is DEFERRED to a future toggle.
- Same-trailhead return is the only start/end model until the shuttle toggle ships.
- Walk-up inventory excluded from bookable results by default; planning mode (availability relaxed) available as a flag.
- A route is an ordered camp list; geometry and GPX are always derived.

## Milestones

### M0. Repo restructure (2-3 h)
- [ ] Split engine from GUI: permit_engine/ package (fetch, classify, models), GUI imports it
- [ ] requirements.txt, package entry point
- Done when: CLI availability query returns the same rows the GUI shows.

### M1. Park extractor (2 h)
- [ ] permitcontent to parks/<park>.json: camps, entrances, parking flags, entrance-to-division links
- [ ] Division filters per park (exclude Administrative, Hitch Rail, Spike unless flagged wanted)
- Done when: rainier.json and glacier.json generate cleanly. (Validated live: Rainier 186/190 coords; Glacier ships 0,0.)

### M2. Coordinates and feature tags (8-12 h)
- [ ] Coordinate fill fallback chain: payload > NPS park GIS > OSM name-join > manual
- [ ] USGS hydrography spatial join: lake_within_400m, creek_within_200m, waterbody name/acres
- [ ] Elevation band per camp; distance-to-nearest-trailhead from graph
- Done when: every active camp in both parks has coords and a lake flag; spot-check ELF is lake=true.

### M3. Route graphs (7-11 h)
- [ ] Rainier edges from official NPS Wonderland mileage tables (3-5 h)
- [ ] Glacier full-park edges from park tables plus PNTA planner; fold in belly_river_graph.json (4-6 h)
- [ ] Every edge carries miles, gain_ab, loss_ab, src; est flag where gains are topo estimates
- Done when: 5 edges per park spot-checked against a map; est count reported.

### M4. Solver core (6-10 h)
- [ ] Dijkstra day-legs between sleeps (pass-throughs allowed), direction-aware gain
- [ ] DP over (night, camp) with party-size availability, per-camp stay limits, basecamp self-loop
- [ ] Backward feasibility from the exit; endings_remaining per option
- [ ] trip_type classifier on the closed walk: no repeated edges = loop; full retrace = out_and_back; repeats forming one contiguous stem = lollipop; filter results by requested type
- Done when: reproduces the belly_river_adventure.py live results, including the single Sept chain found 2026-07-07.

### M5. Scoring (4-6 h)
- [ ] day_fit vs pref miles/gain; camp percentile within park; lake term; crowd term stubbed until data exists
- [ ] computed_prior coefficients in a config file, hand-set
- Done when: batch output is ranked and the weights are editable without code changes.

### M6. Adventure mode CLI (2-3 h)
- [ ] Numbered frontier cards, pick-by-number, layover card, endings counts
- [ ] Live availability re-verify on pick; clamp negative remaining to 0 (known rec.gov quirk)
- Done when: the Elizabeth Lake walkthrough runs interactively.

### M7. GPX and CalTopo export (2-3 h)
- [ ] Itinerary to GPX: waypoints per camp, track as node-to-node lines in the first cut (real geometry is backlog)
- [ ] caltopo_export.py gains rating and availability properties
- Done when: a generated GPX imports into an AllTrails custom map and CalTopo without edits.

### M8. Scan history logger (2-3 h)
- [ ] Every availability fetch appends (camp, date, remaining, total, scanned_at) to SQLite
- Done when: the demand dataset grows on every run. Start this early; it only pays with time.

### M9. Watch mode and Telegram alerts (4-6 h)
- [ ] Diff last scan vs current, alert only on Full-to-Reservable transitions, jittered polling
- [ ] Telegram via the existing digest bot token; message carries camp, date, remaining, booking URL
- [ ] Flicker filter: require the opening to persist across one re-check before alerting
- Done when: a manufactured transition produces exactly one Telegram message.

### M10. Docs and invariants (2-3 h)
- [ ] README with quickstart; tests: endings monotonicity, bounds respected, classifier correctness on known shapes
- Done when: fresh clone to first result in under 10 minutes.

## Totals and order

38-55 h. Order is M0 through M10, with one exception allowed: pull M9 forward immediately after M0/M1 if there is a live trip that needs cancellation alerts now.

## Out of scope before v2.0.0

Map UI, freehand routing, Archetype B parks, shuttle logistics, automated ratings research, GH Actions poller, real trail geometry in GPX. All tracked in BACKLOG.md.
