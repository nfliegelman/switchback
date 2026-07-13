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
- Basecamp day hikes landed v1.6.2 (2026-07-12): layover days get ranked day-hike suggestions; scoring credits layovers with their best achievable day.

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

### M5. Scoring (4-6 h) [DONE, v1.6.0]
- [x] day_fit vs pref miles/gain; camp percentile within park; lake term; crowd term stubbed (engages automatically when parks/demand.json exists and weights.solitude is above 0)
- [x] computed_prior coefficients hand-set in scoring.json; personal overrides in parks/ratings.json; trail-depth term uses real graph distance to the nearest entrance, replacing the M2 straight-line placeholder
- Done when: batch output is ranked and weights are editable without code changes. Landed 2026-07-08: live Rainier run ranked 35,777 bookable itineraries across 641 distinct routes with route-level date dedup; the leaderboard correctly surfaces the Northern Loop lakeside triangle (Mystic, James, Dick Creek) that stays open all season. Priors sanity-checked: feature prior lands ELF 4.53 vs the 4.6 hand rating and GAB 3.5 vs 3.2. Invariant tests in tests/test_scoring.py.

### M6. Trips in the GUI plus route steering (1-2 h) [DONE, v1.7.0]
- [x] Find Trips button in switchback_gui: runs the engine with the saved profile over the GUI's date range, streams progress through the existing queue, opens the ranked report in a results window
- [x] Shared renderer (switchback/report.py) so GUI and CLI output can never drift apart
- [x] --via flag on trips: only itineraries that sleep at or pass through a named camp; Graph.find resolves codes, names, and unique substrings; pass-throughs count
- Done: --via verified live 2026-07-12 (COS as a pass-through filter returns exactly the Sept 22 chain that never sleeps there) and in tests. The GUI button compiles and follows the file's existing worker/queue pattern but this sandbox has no display, so the click itself is an owner smoke test.
- RESHUFFLE (2026-07-12): adventure mode (frontier cards, pick-by-number, live re-verify, the Elizabeth Lake walkthrough) moved to the v2.1 web UI. A terminal is the wrong medium for a spatial interaction. The engine side (endings, camp_card, negative-remaining clamp) shipped with M4/M5 and waits fully tested; only the interaction layer is deferred.

### M7. GPX and CalTopo export (2-3 h) [DONE, v1.8.0]
- [x] Itinerary to GPX (switchback/gpx.py): waypoints per stop with elevations in meters, one track per moving day following graph node paths, layovers noted in metadata; straight node-to-node lines by design (real geometry is backlog)
- [x] trips --gpx N exports the Nth listed route; standalone export command works with no availability fetch; TripFinder.bat prompts for both via and GPX
- [x] caltopo_export.py gains rating properties (prior plus percentile) and optional --window START END open-night counts whenever a park dataset exists; verified live on Rainier
- Done when: a generated GPX imports into AllTrails and CalTopo without edits. Sandbox verification: GPX 1.1 parses with correct waypoint and per-day track counts, layover handling, and zero coordinate-less points (tests/test_gpx.py); the sample file glacier_2026-09-22_BRE_GAB-GLF.gpx ships with this release for the owner's import smoke test.

### M8. Scan history logger (2-3 h) [DONE, v1.9.0]
- [x] Every availability fetch appends raw cells (permit, camp, date, remaining, total, walkup, hidden, scanned_at UTC) to SQLite; the hook lives in api.fetch_division_month, the choke point every caller passes through, so GUI, CLI, solver, and watch all feed it without knowing
- [x] Fail-silent by design (logging can never break a fetch); SWITCHBACK_NO_HISTORY=1 disables; parks/history.sqlite is gitignored state
- [x] history stats and history demand commands; demand is a fullness-rate proxy (30-sample minimum) written to parks/demand.json, which the M5 solitude term already reads; the Permit Difficulty Index feeds on the same table
- Done: the dataset grows on every run, proven live 2026-07-12 (one ordinary ELF fetch appended 30 cells) and by tests/test_history.py.

### M9. Watch mode and Telegram alerts (4-6 h) [DONE, v1.10.0]
- [x] WatchState pure state machine (closed, candidate, alerted): alerts only on Full-to-Reservable transitions at party size, one re-check flicker filter, exactly one alert per opening until the cell closes again, restart-safe via parks/.watch_state.json
- [x] Jittered polling loop; every poll feeds the M8 log for free
- [x] Telegram via env vars or telegram.json (example file committed, real file gitignored); message carries camp, date, remaining, booking URL
- [x] --inject manufactures a transition, --once bounds the loop, --no-send prints instead
- Done: the manufactured transition produced exactly one message, on the persistence cycle, through the real fetch path (2026-07-12); the state machine's blip, re-alert, restart, and party-threshold behavior is pinned by tests/test_watch.py.

### M10. Docs and invariants (2-3 h) [DONE, v2.0.0]
- [x] README rewritten around a measured quickstart: fresh copy to first ranked result in about a minute (the command itself: one second on a one-month window), far under the 10-minute bar
- [x] Invariant tests: endings monotonicity (superset availability grew endings 1 to 2), day bounds held across all 178 itineraries of a loose synthetic run, classifier correctness on known shapes
- [x] Classifier insight worth recording: the Northern Loop from Sunrise is a LOLLIPOP (the 1.2 mi trailhead connector is walked twice); the pure loop test is White River around the full Wonderland, every edge exactly once. The initial test expectation was wrong and the classifier was right.
- Done: v2.0.0. The engine ladder is complete.

## Totals and order

38-55 h estimated; ladder completed 2026-07-12 at v2.0.0. Order was M0 through M10, with one exception allowed: pull M9 forward immediately after M0/M1 if there is a live trip that needs cancellation alerts now.

## Out of scope before v2.0.0

Web/map UI (scheduled as v2.1, immediately after the engine, now including adventure mode interaction), freehand routing, Archetype B parks, shuttle logistics, automated ratings research, GH Actions poller, real trail geometry in GPX. All tracked in BACKLOG.md.


## After the ladder: the v2.x line (planned 2026-07-13)

Sequenced for the current reality: the owner is phone-only until at least July 19, so Claude-heavy builds come first and anything needing the owner's desktop lands behind them. Park additions interleave freely per the BACKLOG expansion plan.

- v2.1.0 [SHIPPED same day]: the map. Local FastAPI server plus a single-file Leaflet frontend: park picker, camps colored by live open nights, route graph drawn, Find Trips with ranked routes and day-path highlighting, the FILTER ACTIVE warning carried over, and adventure mode in its natural medium at last: tap a trailhead, pick each night from the live frontier ranked by how many ways the trip can still finish. SwitchbackMap.bat launches it.
- v2.1.x: calibration and polish. The owner's desktop test drive reactions tune scoring.json; GPX download button on routes; day-hike cards; region overlay groundwork.
- v2.2 [SHIPPED same day]: regions plus Olympic. The Lena cross-boundary pilot proved live (first-come Lower Lena chaining to real open Upper Lena inventory); Olympic dataset extracted, features pass and proper corridors queued.
- v2.3 [SHIPPED same day]: phone-native board. Daily Actions job computes board.json for relative windows and commits it with the durable history snapshot; static Leaflet board on GitHub Pages at /docs/board.
- v2.4 [SHIPPED same day]: DEM gain pass benchmarked 43 percent low to 7 percent high on the GPS log; Teton Crest ships as the second region with pass-arithmetic gains after the DEM line method self-diagnosed its Teton limits.
- v2.6 [SHIPPED same day]: the Colorado wave. Maroon Bells-Snowmass, Indian Peaks, and Great Sand Dunes trips-ready; RMNP Tier 1 plus the Wild Basin corridor; Black Canyon recorded as a holdout (no rec.gov permit). Coverage stands at eleven entries.
- v2.7 [SHIPPED same day]: trail-true geometry from OpenStreetMap across all nine graphed parks; map, board, and GPX draw real trails; coverage-validated fetching, component snapping, gap bridging; ODbL attribution everywhere.
- v2.8 [SHIPPED same day]: government trail synthesis. TNM and USFS official centerlines as a lazy, provenance-tagged rescue layer under the same sanity gates; Summerland rescued; multi-dataset confirmation for the honest straights.
- v2.9 [SHIPPED same day]: Colorado statewide. The 49-entry atlas and COLORADO.md, trail areas as a first-class entity, the San Juan wave live with about 2810 mapped miles, explore-areas pickers in both frontends.
- v2.10 [SHIPPED same day]: installable PWA. Manifest, icons, service worker with offline shell and cached areas; add to home screen on iOS.
- v2.11 [SHIPPED same day]: San Juans complete (7 areas, ~3670 mi), routable junction graphs in area files, rubber band phases 1 and 2 live (drag-routing with the green and amber boundary split on the phone board).
- v2.13 [SHIPPED same day]: national atlas, 80 tracked landscapes across CO and WA, WASHINGTON.md, Goat Rocks proof build.
- Beyond: dispersed itineraries experiment (auto camp nodes from named lakes and basins, synthetic availability, pilot one Weminuche drainage); GPX patch channel (owner traces win over everything); dem_trail_v1 (elevation along real polylines); Archetype B trailhead-quota parks (Yosemite, SEKI); RMNP corridor buildout; scoring calibration when the owner can react.
