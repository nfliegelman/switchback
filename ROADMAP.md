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
- Web UI ships as v2.1, immediately after the engine (2026-07-07 round-two decision). A thin Find Trips trigger in the tkinter GUI is in scope at M6; deep tkinter trip UI is rejected as throwaway.
- Effort limits: one saved default profile (profile.json), overridable per run. Miles and gain only; grade returns after the DEM pass.

## Milestones

### M0. Repo restructure (2-3 h) [DONE, v1.1.0]
- [x] Split engine from GUI: switchback/ package (api, config, CLI), GUI imports it
- [x] requirements.txt, package entry point (python -m switchback)
- Done when: CLI availability query returns the same rows the GUI shows. Verified live 2026-07-07 against Glacier ELF.

### M1. Park extractor (2 h) [DONE, v1.2.0]
- [x] permitcontent to parks/<park>.json: camps, entrances, parking flags
- [x] Division filters per park as recorded flags (Administrative, Hitch Rail, Spike)
- Done when: rainier.json and glacier.json generate cleanly. Landed 2026-07-08: Rainier 190 camps (186 coords) + 60 entrances; Glacier 213 camps (158 included after filters, 0 coords) + 53 entrances. Finding: entrance division_ids is permission data, not proximity; edges still come from M3 mileage tables.

### M2. Coordinates and feature tags (8-12 h) [DONE, v1.3.0]
- [x] Coordinate fill: payload > OSM name-join > manual queue (NPS GIS pass never needed)
- [x] USGS NHD hydrography joins: lake_within_400m, lake_name, lake_acres, creek_within_200m (ftype-filtered waterbodies and flowlines)
- [x] Elevation per camp and entrance (Copernicus GLO-90 batched; 3DEP along-edge sampling arrives with the M3/DEM gain pass); straight-line trailhead distance as an explicit placeholder M3 replaces with trail distance
- Done when: every active camp in both parks has coords and a lake flag; spot-check ELF is lake=true. Landed 2026-07-08: Rainier 186/186 coords, 50 lake camps; Glacier 62/66 coords (4 in parks/manual_coords.json queue), 41 lake camps, ELF lake=true at 192 acres. Exclusion filters grew to 16 reasons; Glacier's included set now matches its real ~65 designated backcountry camps.

### M3. Route graphs (7-11 h) [DONE, v1.4.0]
- [x] Rainier: Wonderland corridor plus Spray Park alternate plus Northern Loop, 33 edges transcribed from Where The Road Forks camp guide, cross-checked against Wonderland Guides day sums (11.5 and 9.7 match exactly) and Visit Rainier cumulatives; variances flagged in src per edge
- [x] Glacier: Belly River corridor folded from belly_river_graph.json, 13 edges, 2 sourced gains; remaining Glacier corridors (Gunsight, Highline, Dawson-Pitamakan, North Circle west) queued
- [x] Every edge carries miles and src; gains sourced where known, else endpoint-delta est from M2 elevations
- Done: 5-plus spot checks per park passed 2026-07-08: Longmire>Devils Dream 5.8, Longmire>Golden Lakes 24.3, Longmire>Klapatche 16.7 vs 16.8 GPS-logged, Sunrise>Summerland 11.0, Mowich>Carbon 8.3 via Spray Park beating 8.7 via Ipsut, ELF>IPE 9.8 exact, BRE>MOJ 13.4 matching PNTA. CAUTION: endpoint-delta gains understate passes about 40 percent (est 3658 vs GPS 6450 on Longmire>Klapatche); gain limits are soft on Rainier until the DEM pass. Glacier's big climbs are sourced and real.

### M4. Solver core (6-10 h) [DONE, v1.5.0]
- [x] Dijkstra day-legs between sleeps with pass-throughs and direction-aware gain (graph.leg)
- [x] DP over (night, camp) with party availability, stay-limit hook, basecamp self-loop (switchback/solver.py)
- [x] endings() completion counts for M6 frontier cards
- [x] trip_type classifier via mirrored-hop stem stripping: empty remainder out_and_back, unique remainder loop or lollipop by stem, else mixed
- Done: parity proven twice on 2026-07-08. Synthetic oracle in tests/test_solver.py passes deterministically, and the LIVE run reproduces the single bookable Belly River chain on real inventory: Sept 22, BRE, GAB > GLF > GAB, out_and_back, days 6.2 / 4.2 / 4.2 / 6.2. CLI: python -m switchback trips <slug>.

### M5. Scoring (4-6 h)
- [ ] day_fit vs pref miles/gain; camp percentile within park; lake term; crowd term stubbed until data exists
- [ ] computed_prior coefficients in a config file, hand-set
- Done when: batch output is ranked and the weights are editable without code changes.

### M6. Adventure mode CLI + thin GUI trigger (3-5 h)
- [ ] Find Trips button in switchback_gui calling the engine with the saved profile
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

Web/map UI (scheduled as v2.1, immediately after the engine), freehand routing, Archetype B parks, shuttle logistics, automated ratings research, GH Actions poller, real trail geometry in GPX. All tracked in BACKLOG.md.
