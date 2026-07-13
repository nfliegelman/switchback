# CHANGELOG

Versioning per ROADMAP.md: milestones bump the minor version; v2.0.0 is the full Switchback engine.

## v2.5.0 (2026-07-13)

Enchantments and the Permit Difficulty Index machinery. Enchantments (advanced lottery permit 233273; the daily lottery 445863 is noted for a future dual-permit region) ships trips-ready: 4 zones, 5 edges covering the classic Stuart TH to Snow Lakes thru-line plus the Stuart spur, pass-arithmetic gains including Aasgard's +2,250 over 2.2 miles, and curated coordinates after rec.gov's zone centroids proved junk (Snow Zone placed 14 miles north, Stuart cloned onto Colchuck). Live September run returned an honest zero: post-lottery Enchantments is sold out, as it should be. New history pdi command derives a 0 to 100 Permit Difficulty Index per camp with a 30-sample floor and honest null components (weekend premium needs 10+ weekend observations, sellout velocity needs multi-day depth); 28 camps qualified from day one of scanning, and the daily board job now refreshes pdi.json. Two tests that had pinned pre-DEM gain values were unpinned to their real invariants.

## v2.4.0 (2026-07-13)

The DEM gain pass, Grand Teton, and the Teton Crest region. New switchback/dem.py samples the line between edge endpoints at 100 m spacing against the Open-Meteo DEM and accumulates gain with 5 m hysteresis. BENCHMARK: Longmire to Klapatche went from 3,658 ft (43 percent under the GPS log's 6,450) to 6,870 ft (7 percent over, the safe direction). Rainier's 33 edges, Glacier's Belly edges (the junction got coordinates), all filled. Then the Tetons found the method's boundary: straight lines cross 11,000 ft peaks that canyon trails contour around, so dem now self-flags ridge_suspect results and respects dem_exempt, and a gain-method tier exists: sourced beats alltrails_derived and pass_arithmetic beats dem_line beats endpoint. Teton Crest ships as the second cross-boundary region (GTNP zones, permit 4675342, zero payload coords so all curated, plus permitless Alaska Basin from Caribou-Targhee NF) with pass-arithmetic gains from named pass elevations; live proof: 118 bookable September itineraries across 23 routes. Lena's AllTrails-derived gains were restored and exempted. Two Rainier edges (Maple Creek to Paradise River, White River to Summerland) carry DEM overshoot flags for per-edge QA.

## v2.3.0 (2026-07-13)

The phone-native trip board. New switchback/board.py computes ranked trips for the relative windows in board_config.json (start_in_days plus span_days, so a standing config never goes stale) and writes docs/board/board.json; the static docs/board/index.html renders it with the map, availability-colored camps, first-come labels, and tappable routes. New .github/workflows/board.yml runs it daily, snapshots history.sqlite into data/ for durability, derives demand.json, and commits only when something changed. Enable GitHub Pages on main /docs and the board lives at a URL your phone can open. Live build: Lena 66 itineraries, Rainier 9,766 across 641 routes, Glacier Belly honestly zero because mid-August Belly River is genuinely full.

## v2.2.0 (2026-07-13)

Cross-boundary regions, the Lena pilot, and Olympic. load_park now merges region files: member-park camps carry their own permit_id and policy reservation, permitless overlay camps default to policy none, and curated region coords override rec.gov's (whose Upper Lena point sits 18 miles off). New solver.fetch_for_graph groups availability fetches by permit and gives permitless camps a synthetic always-open series; the report, map, frontier, and board all label those nights first-come, never Reservable. parks/lena.json plus lena_edges.json (AllTrails-derived figures, est flags) make the owner's actual trip solvable, proven live: Lower Lena night one first-come, Upper Lena night two on real open ONP inventory. Olympic (permit 4098362) extracted: 297 included camps, 146 payload coords, features pass queued.

## v2.1.0 (2026-07-13)

The map. New switchback/web.py FastAPI server and switchback/web_index.html single-file Leaflet frontend: park picker from live coverage, camps colored by open nights for the chosen window and party, the trail graph drawn, Find Trips rendering ranked deduped routes with day paths highlighted on the map and the FILTER ACTIVE warning preserved, and adventure mode as designed in SPEC section 10: tap a trailhead, choose each night from the live frontier, options ranked by remaining finishes, with an honest walk-out check at the end. New SwitchbackMap.bat launcher; fastapi and uvicorn are optional extras, the engine remains standard library. Offline test suite via injected fetcher (which immediately caught the feature-flag mapper assuming a nested schema that does not exist); live boot proof served the map and solved a real Glacier window.

## v2.0.7 (2026-07-13)

Cloud watcher. New .github/workflows/watch.yml runs one watch cycle every 30 minutes on GitHub Actions and accepts ad-hoc watches from the GitHub mobile app via workflow_dispatch inputs. New watch_config.json defines the standing watch with an enabled flag; new --config mode on the watch CLI loads it and exits cleanly when disabled (proven: no-op in under a second, enabled cycle watched 27 live cells). Watch state and scan history persist across runs via the Actions cache with rolling keys; exactly-once alerting is soft in the cloud, duplicate-not-miss on rare cache eviction. Telegram credentials come from repo secrets, never the repo.

## v2.0.6 (2026-07-13)

Silent-filter bug, caught by the owner's first live test drive (run from a phone, in chat). profile.json ships trip_type "loop", and the trips report disclosed party and daily limits but never the shape filter, so a Rainier run showed 4 weak routes (top score 0.145) while silently discarding 635 others. The same window with the filter off returns 639 routes and a top score of 1.040. The report header now states the active trip type always, and prints an explicit FILTER ACTIVE warning naming what was discarded and how to see it. Threaded through the CLI and the GUI. No solver changes; the solver was right, the report was quiet.

## v2.0.5 (2026-07-13)

AllTrails integration matrix decided and recorded in BACKLOG: edge seeding and land-unit labels now, traffic-label crowd proxy and corridor deep links soon, weather and review content live-only via the artifact path, the rest skipped. Discovery: trail_traffic and popularity sorts on the search tools deliver the crowd signal without the still-blocked details call.

## v2.0.4 (2026-07-13)

AllTrails synthesis unlocked at the owner's push. The blanket link-only stance is replaced by a nuanced policy (facts with attribution sparingly via the official MCP, content never, bulk never, the app never calls AllTrails). Proven live: the Lena corridor was pulled through the connector in-chat, its cross-boundary Forest and Park labels confirming the regions case, and its mileage and gain figures now seed the pilot in BACKLOG. Three synthesis uses recorded: gain validation, crowd proxy, day-hike POI enrichment.

## v2.0.3 (2026-07-13)

Full-conversation sweep against the docs at the owner's request. Two gaps found and closed: the naming runners-up and Switchback Travel trademark caveat now live in FUTURE.md next to the monetization gates, and HANDOFF records that Rainier's blank size field means capacity always derives from availability totals. Everything else checked out captured.

## v2.0.2 (2026-07-12)

Regions recorded, coverage generated. BACKLOG gains the cross-boundary regions design (multi-permit plus permitless stitching, FCFS honesty rule, Lena corridor pilot) at the owner's direction. New coverage command and generated PARKS.md replace any hand-maintained park list; Tier 0 universality documented. No engine behavior changes. The generator's first run caught a real staleness bug (extract-time counts never refreshed by features), so coverage now counts coordinates from the camps array directly.

## v2.0.1 (2026-07-12)

Doc audit, prompted by the owner catching real drift between conversation and docs. SPEC now records the grade deferral next to the schema that still showed grade_pct. BACKLOG gains the park and forest expansion plan as a plan (archetypes, forest targets on the same platform, holdouts, first wave Olympic then Teton, cost trajectory). HANDOFF gains the owner's browser publish workflow with the ghost-file caution, the five-step test-drive gate before v2.1, and a new standing convention: conversational decisions get written into docs in the same turn. No code changes.

## v2.0.0 (2026-07-12)

M10: docs and invariants; the engine ladder is complete. README rewritten around a measured quickstart (fresh copy to first ranked result in about a minute; the command itself ran in one second on a one-month window). New tests/test_shapes.py pins the classifier on known shapes, day bounds across a 178-itinerary synthetic run, and endings monotonicity. Recorded insight: Sunrise's Northern Loop is correctly a lollipop (the trailhead connector is walked twice); White River around the full Wonderland is the pure loop.

## v1.10.0 (2026-07-12)

M9: watch mode and Telegram alerts. New switchback/watch.py: a pure alert state machine (Full-to-Reservable transitions only, one re-check flicker filter, exactly one alert per opening, restart-safe persisted state) inside a jittered polling loop that also feeds the history log. Telegram config via env vars or gitignored telegram.json (example committed); alerts carry camp, date, remaining, and a booking link. The watch CLI supports --codes, --party, --interval, --once, --no-send, and --inject; the manufactured-transition done-criterion produced exactly one message through the real fetch path. State machine pinned by tests/test_watch.py.

## v1.9.0 (2026-07-12)

M8: scan history logger. New switchback/history.py hooked into api.fetch_division_month, the choke point every caller passes through, so every availability fetch from any entry point appends raw cells to gitignored SQLite, fail-silent, with SWITCHBACK_NO_HISTORY as the off switch. New history stats and history demand commands; demand.json (fullness-rate proxy, 30-sample minimum) feeds the existing scorer solitude term. Proven live: one ordinary fetch appended 30 cells.

## v1.8.0 (2026-07-12)

M7: GPX and CalTopo export. New switchback/gpx.py: itinerary to GPX 1.1 with waypoints per stop (elevations in meters), one track per moving day following graph node paths, layovers noted, straight node-to-node lines by design. trips --gpx N exports any listed route; a standalone export command needs no availability fetch; TripFinder.bat prompts for GPX export. caltopo_export.py now attaches rating and percentile properties, plus optional --window open-night counts, when a park dataset exists (verified live on Rainier). Sample file glacier_2026-09-22_BRE_GAB-GLF.gpx ships for import smoke testing. Invariant tests in tests/test_gpx.py.

## v1.7.0 (2026-07-12)

M6, reshuffled and landed: trips in the GUI plus route steering. Adventure mode interaction moved to the v2.1 web UI (the engine functions shipped with M4/M5 and wait fully tested). New Find Trips button in switchback_gui runs the engine with the saved profile through the existing worker/queue pattern and opens the ranked report in a results window; switchback/report.py is the shared renderer so GUI and CLI cannot drift. New --via flag filters to routes that sleep at or pass through a named camp, with pass-throughs counting; Graph.find resolves codes, names, and unique substrings; verified live with a pass-through-only filter. TripFinder.bat gains a via prompt.

## v1.6.2 (2026-07-12)

Basecamp day hikes. The solver always allowed consecutive nights at one camp; layover days now come alive. New in switchback/scoring.py: day-hike options from any basecamp over the route graph (out-and-back miles and gain summed both directions), ranked 60/40 by destination quality and effort fit, with unwalkable distances filtered; availability is deliberately ignored for destinations, since day hikes need no permit, which makes basecamping an availability-arbitrage move (sleep where quota exists, visit where it does not). Scoring change: a layover day is now credited with its best achievable day-hike fit instead of being skipped, so layovers at camps with nothing nearby rank lower. The trips CLI prints day-hike suggestions under each route with a layover. Package version aligned to 1.6.2. New test assertions cover round-trip math, layover credit, and note formatting.

## v1.6.1 (2026-07-08)

Convenience addition, not a roadmap milestone. New TripFinder.bat: a prompt-driven double-click wrapper around python -m switchback trips, so the engine can be test-driven without a terminal. Added in response to a real point of confusion: Switchback.bat only ever launched the original GUI, and every engine feature since M0 has been command-line only with no visible entry point.

## v1.6.0 (2026-07-08)

M5: scoring. New switchback/scoring.py and scoring.json: config-driven feature priors (lake, creek, elevation band, trail depth from the graph), per-park percentile normalization, personal overrides via parks/ratings.json, day-fit against the saved profile, lake term, and a crowd stub that engages when demand history exists. Trips output is now ranked with route-level deduplication and availability date spans. Validated live on Rainier: 35,777 itineraries across 641 routes ranked in seconds; priors converge on hand ratings. Invariant tests added.

## v1.5.0 (2026-07-08)

M4: solver core. New switchback/solver.py: availability-gated DP over nights and camps with pass-through day legs, party and stay-limit handling, basecamp self-loops, endings counts, and the trip-type classifier (loop, out_and_back, lollipop, mixed) via mirrored-hop stem stripping. New trips CLI with profile defaults and a codes filter. Parity proven synthetically (tests/test_solver.py) and live against real inventory.

## v1.4.0 (2026-07-08)

M3: route graphs. New switchback/graph.py resolving parks/edges/<slug>_edges.json with fuzzy name resolution (compass abbreviations, fallback nodes instead of silent edge drops), direction-aware gains, and endpoint-delta est gains where unsourced. Rainier: 33 edges across the Wonderland corridor, Spray Park, and Northern Loop, cross-checked to the tenth against three sources. Glacier: Belly River corridor folded in with sourced climbs. Recorded limitation: est gains understate passes about 40 percent until the DEM pass.

## v1.3.0 (2026-07-08)

M2: coordinates and feature tags. New switchback/features.py and a features CLI command: OSM name-join coordinate fill with foot/head-aware normalization, subset matching, and a manual queue; USGS NHD hydrography joins (lake within 400 m with name and acreage, creek within 200 m) replacing the OSM water plan after Overpass congestion, which also lands the roadmap-specified USGS source; batched GLO-90 elevation per node; straight-line trailhead distance placeholder. Extraction filters extended (chalets, shelters, ranger stations, cabins, lookouts, winter lots, CDT duplicates, undesignated zones), bringing Glacier to its true 66 designated camps. Results: Rainier 186/186 located with 50 lake camps; Glacier 62/66 with 41 lake camps and a 4-camp manual queue. Engine gained an OSM disk cache with time-boxed prefetch for sandbox wall-clock limits.

## v1.2.0 (2026-07-08)

M1: park extractor. New switchback/extract.py and an extract CLI command writing parks/<slug>.json: every camp with normalized coordinates (0,0 becomes null), the Administrative / Hitch Rail / Spike filter applied as a recorded flag, lake and trail parsing, size and status fields; every entrance with coordinates and parking flags. rainier.json (190 camps, 186 with coords, 60 entrances) and glacier.json (213 camps, 158 included, 0 coords, 53 entrances) generated live. Data finding recorded: entrance division_ids is permission data, not proximity, so it cannot seed graph edges.

## v1.1.0 (2026-07-07)

M0: engine split. New switchback/ package: stdlib-only data layer moved verbatim from the GUI, shared availability row builder, profile loader, and a CLI (search, availability, profile). The GUI now imports the engine, dead imports removed, behavior unchanged. Added profile.json and requirements.txt. Verified live: CLI availability for Glacier ELF matches GUI classification. Round-two decisions recorded: engine first with web UI as v2.1, one saved effort profile, grade deferred until the DEM pass.

## v1.0.1 (2026-07-07)

Docs only. Recorded round-one product decisions (local web app as target UI with FastAPI plus Leaflet architecture, on-demand plus per-trip watch operating model, no anchor trip) and added the Permit Difficulty Index to the backlog as DIRECTED.

## v1.0.0 (2026-07-07)

Initial public release.

- GUI availability finder (switchback_gui.py): search any recreation.gov wilderness permit, pull every camp's availability across a date range on 6 threads, classify each camp-night (Reservable, Walk-up only, Full, Not released), and export a styled, filterable Excel workbook.
- CalTopo exporter (caltopo_export.py): dump any permit's camps and trailheads as a CalTopo-importable GeoJSON layer, colored by camp type, parking flags on trailheads.
- Adventure mode demo (belly_river_adventure.py): live 3-night itinerary search for Glacier's Belly River area over a sourced route graph, with the interactive frontier walkthrough, endings-remaining counts, batch ranking, and a planning mode for when advance inventory is gone.
- Design docs: SPEC, SCOPE, ROADMAP, BACKLOG, HANDOFF, FUTURE (historical).
