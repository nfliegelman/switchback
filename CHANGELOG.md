# CHANGELOG

Versioning per ROADMAP.md: milestones bump the minor version; v2.0.0 is the full Switchback engine.

## v2.22.0 (2026-07-14)

The QA sweep plus the second dual park. Enchantments daily lottery 445863 merged onto all 5 zones in one command, proving merge-inventory generic. ELF to IPE confirmed at 9.8 by AllTrails oracle triangulation and closed; the neighboring ELF to Cosley discrepancy (PNTA 6.0 vs a community-implied 4.1) is recorded with official figures retained. The Elk Range Maroon to North Fork display mismatch is flagged geometry_suspect for the dem_trail pass to resolve. Maroon Bells Areas Outside of Permit Zones semantics decided: real dispersed inventory, stays un-graphed. OWNER.md is born: every task on the owner, phone vs desktop, updated each release.

## v2.21.0 (2026-07-14)

Item 3, the dual-permit merge. Camps can now carry extra reservation inventories; the availability choke point fetches all of them and MAX-merges per date, since a party books within one inventory. A new merge-inventory command attaches a second permit by normalized division name. Indian Peaks is the first dual park: all 17 zones matched the 3-days-in-advance permit 4675319 exactly (zero Group false-matches), and the live proof found Cascade Creek on July 16 bookable only through the 3-day channel. The shared report labels the short-release channel honestly; watch mode is unchanged. Semantics are pinned in tests: max not sum, both permits fetched, second inventory can rescue a night.

## v2.20.0 (2026-07-14)

Item 2, the boundary source expansion. A six-source boundary registry (USFS wilderness, NPS units, wilderness.net all-agency, BLM WSA, USFS designated areas, PAD-US) replaces the single USFS service, and eleven planned rows became built maps in one pass: Black Canyon of the Gunnison, Gunnison Gorge, Dominguez Canyon, Black Ridge Canyons, Handies Peak WSA, Hermosa Creek SMA, Browns Canyon NM, Colorado State Forest SP, North Cascades NP, Juniper Dunes, and Mount St. Helens NVM. About 6,090 new trail miles; 83 built landscapes systemwide. A mileage-weighted containment audit cleared all eleven against Weminuche and Goat Rocks controls and retired the node-fraction variant, which underreads systematically. The three long-trail corridor rows now carry a written design in EXPERIMENTS.md and wait as their own build.

## v2.19.0 (2026-07-13)

Item 1 closed for real. Elevation gains flow into auto-generated dispersed parks via OpenTopoData NED 10m (EPQS confirmed blocked from this egress), est_gain flagged on every edge, and the Needle Creek pilot carries an experimental flag. The gains immediately proved their worth: itineraries fell from 168 to 14 under the owner's real 4000 ft daily ceiling, honest trips replacing gain-blind ones. An NPS boundary service probe is recorded for the item 2 build next session.

## v2.18.0 (2026-07-13)

The session-floor sprint: items 1 and 4 of the menu, sealed honestly, with 2 and 3 deferred whole rather than started and abandoned. EPQS confirmed blocked on a second attempt, alternates recorded. The South San Juan mystery closed by audit: 79 percent of its nodes sit outside the boundary, so the thin main network is pad capture plus sparse interior mapping, and the containment audit joins the QA toolkit. The Conundrum trailhead, the oldest open question in the repo, resolved against the oracle: 8.55 miles one way to the springs, coordinate relocated to the road terminus, and the remaining straight confirmed absent on both datasets, graduated to the GPX patch channel.

## v2.17.0 (2026-07-13)

The roadmap sweep, everything that fit. Phase B productized: build_pilot with widened dedupe and named junctions took Needle Creek from 2 camps to 10 and from 14 itineraries to 168 across 24 routes; gains blocked by an unreachable USGS EPQS endpoint, recorded for retry. Both Washington hangers built on clean retries, taking the state to 24 areas on the map and confirming the earlier failures as transient mirror pathology. Glacier's ELH to HEL leg corrected from 1.5 to 2.6 miles on oracle-consistent corridor evidence, the curated figure having been the outlier. The IPW dual-permit merge is now fully designed in EXPERIMENTS.md but unbuilt, since the schema is single permit_id and the merge belongs in the availability layer. Boundary source expansion, calibration, and Telegram remain open by honest constraint, not neglect.

## v2.16.0 (2026-07-13)

Dispersed itineraries phase B passes. dispersed.py now builds a real park from an area graph: auto camps with policy none, Dijkstra edges in the standard schema, and the existing solver produced 14 ranked bookable itineraries on the Needle Creek pilot, including the classic Chicago Basin trip reproduced exactly. The AllTrails oracle verified the flagship leg inside a tenth of a mile (Windom via Needle Creek, 18.1 mi RT). Limitations recorded in EXPERIMENTS.md before any app exposure: widen the candidate dedupe, gains await dem_trail, junction naming needs a pass.

## v2.15.0 (2026-07-13)

The Colorado map wave: all 27 remaining USFS wildernesses built in one session, roughly 12,000 new trail miles. Headliners: Sangre de Cristo at 1687 trail miles with 221 government additions (the new system champion), Collegiate Peaks 1049, Eagles Nest 1045 with the densest network in the state at 2229 OSM ways, Flat Tops 939 with the second biggest government rescue yet at 256 additions, West Elk 762, Lost Creek 593. One boundary-name fix recorded: the USFS service registers Cache La Poudre with a capital La. Colorado now stands at 4 live, 34 on the map, 11 planned (the non-wilderness boundary set: BLM units, Black Canyon, Hermosa, Browns Canyon, State Forest, and the two long-trail corridors). Systemwide: 70 built landscapes across two states, every one drag-routable.

## v2.14.0 (2026-07-13)

The Washington map wave. Twenty-one wilderness areas built through the unchanged pipeline in one session, about 9,000 new trail miles, headlined by Glacier Peak (1,475 mi), Pasayten (1,080), Wenaha-Tucannon (900), William O. Douglas (861), and Mount Baker (737). The way-count floor became advisory after two nearly trailless pockets starved the mirror walk; sparse areas now keep the best response with a printed note. Wonder Mountain and Glacier View stay planned honestly: their fetches hang a full mirror timeout on tiny bboxes, recorded in BACKLOG for a retry rather than fought today. Washington stands at 3 live, 22 on the map, 6 planned; the system totals 43 built landscapes across two states.

## v2.13.0 (2026-07-13)

The catch-up capture: every area on the owner's two-state census is now tracked in the system. The atlas went national: parks/atlas.json is the single source with a state field, and the generator renders COLORADO.md and WASHINGTON.md per state. Washington enters with 31 rows (3 live, 28 planned) spanning the NPS units, 26 wilderness areas with official USFS names wired for the area pipeline, Juniper Dunes, the St. Helens monument, and the PCT corridor, joining Colorado's 49 for 80 tracked landscapes. Goat Rocks proof-built through the unchanged pipeline on the first pull, 596 trail miles and 430 OSM ways plus 16 government additions, flipping to trails-on-map and confirming the boundary service, the junction graphs, and the rubber band all work identically outside Colorado. The remaining Washington map wave is a recorded checklist in BACKLOG, one command per area.

## v2.12.0 (2026-07-13)

The dispersed itineraries experiment ran its phase A pilot on the Needle Creek drainage and passed. switchback/dispersed.py generates camp candidates for permit-free areas from named waters and 3-way junctions over the shipped area graph, gated at 400 m snap distance, and the graded pairs landed inside published bands: Twin Lakes 7.7 mi auto vs 7.2 to 8.0 published, Columbine Lake 9.1 vs about 9 to 9.5, the Chicago Basin junction at 6.6 vs 6 to 6.5. Findings and the phase B plan live in EXPERIMENTS.md; synthetic availability and solver integration proceed next, with AllTrails as the QA layer before anything reaches the app.

## v2.11.0 (2026-07-13)

Steps one through three of the arc, in one release. La Garita and Powderhorn complete the San Juan wave: seven Colorado wildernesses on the map, about 3670 trail miles. Area files graduated from flat polylines to routable junction graphs, and the road there taught three recorded lessons: simplify AFTER splitting because Douglas-Peucker deletes the shared junction vertices trails cross at; police length at the component level because OSM chops long trails into sub-quarter-mile segments that a per-way filter shatters; and bridge micro-gaps at 200 m while leaving kilometre-scale islands alone, because a gap census showed the minor networks sit 1 to 16 km from the main one, which is geography, not error. The rubber band shipped both phases. On the phone board, open any area, tap draw route, tap a node, and drag: live Dijkstra over the shipped graph paints the real trail green where both endpoints sit inside the wilderness boundary and amber where the path escapes, with a running mileage total, taps committing legs. On the local app the same button appears for permit parks, animating the stored edge polylines toward the neighbor nearest the drag bearing, schema-adaptive and self-hiding if the payload shape ever changes. The board loader keeps a fallback for the old cached area format so phones holding stale files degrade to display-only instead of breaking, and the service worker shell constant is bumped per the standing rule.

## v2.10.1 (2026-07-13)

The owner clicked TripFinder.bat, got a wall of console prompts, and said the words every stopgap eventually hears. Launchers consolidated to exactly two: Switchback.bat now opens the real app in the browser (same UI as the phone, full engine behind it), auto-installs fastapi and uvicorn quietly on first run, launches the server windowless, and just reopens the browser if the server is already running. Switchback Classic.bat is the renamed window for the availability grid and Excel export. TripFinder.bat and SwitchbackMap.bat are retired; the map's Find Trips button replaced the former long ago and the latter folded into the main launcher. The local app gained a quit link (POST /api/quit) so a windowless server is never something to hunt down in Task Manager. README Quickstart rewritten phone first, double-click second, terminal demoted to an optional advanced section, and the stale claim that GPX exports are straight segments is corrected: lines have followed real trail geometry since v2.8.

## v2.10.0 (2026-07-13)

Switchback becomes a phone app. The board is now an installable PWA: web manifest, standalone display, theme color, generated icons including the apple-touch-icon iOS actually uses, and a service worker with three cache policies chosen deliberately. The app shell is precached, board.json is network first with cache fallback so availability never goes silently stale, and area files are stale while revalidate so a wilderness you have opened once keeps working in the parking lot with no signal (base map tiles still need network; recorded honestly). Install on iOS via Share then Add to Home Screen. The owner also specified the rubber band route builder, now written into ROADMAP and BACKLOG: tap a node, drag toward another, the real trail polyline animates along the actual path, green inside the boundary and amber past it, release to commit the leg. Phase 1 needs no routing on permit parks because the edge polylines already exist; phase 2 ships trail adjacency in area files and runs client side Dijkstra with point in polygon color splitting.

## v2.9.0 (2026-07-13)

Colorado goes statewide. A new atlas (parks/colorado_atlas.json, rendered to COLORADO.md by python -m switchback atlas) catalogs all 49 backpacking landscapes in the state: 4 national parks, 36 wilderness areas, BLM lands, other public lands, and the long trails, each with manager, permit reality, and status. The build also ships a second first-class entity alongside permit parks: trail areas, dispersed and permit-free, built by python -m switchback area <slug>. Each area fetches its official USFS wilderness boundary (EDW service, simplified from thousands of points to display weight), pulls every mapped foot way from OSM, adds government lines only where OSM has nothing within 120 m, and writes a lazy-loaded display file to docs/areas plus a manifest. The San Juan wave is live: Weminuche (1413 trail mi, Chicago Basin included), South San Juan (601), Uncompahgre (456), Lizard Head (217), Mount Sneffels (123), about 2810 mapped miles in 687 KB. Both map frontends grew an explore-areas picker drawing boundary and trails; the local app serves them at /api/areas and /api/area/{slug}. Mileage counts every mapped foot way in the padded bbox, not just official system trails, so figures run above agency numbers by design. Full itineraries for dispersed areas are the owner-approved next experiment: auto-generated campsite candidates from named lakes and basins with synthetic always-open availability, queued in ROADMAP and BACKLOG.

## v2.8.0 (2026-07-13)

Source synthesis, the CalTopo move done for a router instead of a renderer. geometry.py now carries a government trail layer: USGS The National Map trails (which aggregates the NPS park centerlines) plus the USFS EDW National Forest System trails, queried through the ArcGIS REST API with JSON envelopes (comma envelopes fail silently with zero features, recorded as a trap), quadtree tiling for transfer limits, and lazy disk caching so the layer is fetched only when OSM leaves an edge straight, rejected, or coarse. The rescue policy is a provenance-tagged waterfall: OSM remains the base, failures retry on the official centerlines under the same sanity gates, and every stored polyline now carries a src field. First blood: the White River to Summerland edge, a 39 mile OSM detour reject, now rides 6.6 miles of official NPS centerline, taking Rainier to 32 of 33. Equally valuable, the straights that failed on both independent datasets (Aasgard's boulderfield, the open dunefield, upper Sand Ramp, lower Conundrum) are upgraded from holes to confirmed absences. The Maroon Zone coordinate moved onto the valley-side trail, fixing the long-rejected Crater to Maroon leg (3.2 routed vs 3.4 curated) at the cost of the East Fork shuttle edge, which joins the honest straights; Elk Range zone QA remains queued, including the Maroon to North Fork line now measuring 11.8 mi against 7.19 stored miles. Scoreboard: 86 of 96 substantial edges trail-true (1 on government lines, 2 coarse), 10 straight with reasons named. Map attributions read OSM (ODbL) plus USGS and USFS.

## v2.7.1 (2026-07-13)

Seam fix, caught by the owner's second phone screenshot. path_for assumed stored polylines ran in sorted-key order while harvest stored them in first-encounter order, so 44 of 85 hops came back reversed at draw time; the trail line itself still rendered correctly, but every affected hop boundary produced a straight seam chord, which is exactly the Granite Creek to Mystic line in the screenshot and the matching Lena chords beneath it. Harvest now writes canonical sorted-key orientation, all nine geometry files were migrated in place with a coordinate-verified flip, and board generation gained a seam guard that prints the count of over 0.5 mi jumps across every window so a bad board can never pass silently. Post-fix: an independent scan shows 14 routes, zero jumps, all 11 test files green. Two lessons recorded: verify generated artifacts after the FINAL generation step, not an earlier one, and any unchecked orientation assumption will be wrong about half the time.

## v2.7.0 (2026-07-13)

Trail-true geometry, at the owner's order after the first live board test: the lines now track the paths of trails. New switchback/geometry.py pulls every foot-travel way in a park's bounding box from OpenStreetMap via Overpass (mirror rotation, a disk cache, and a coverage validator that accepts a response only if trail vertices sit within 800 m of at least 70 percent of graph nodes, which is what finally caught partial mirror extracts that had defeated size floors), stitches the ways into a routable network with union-find components and sub-30 m gap bridging, snaps endpoints to the nearest candidate per connected component so parking-lot fragments cannot shadow the real trail, routes with Dijkstra across up to five candidate pairs, simplifies with Douglas-Peucker at 12 m, and writes per-park polylines to parks/geometry/. A sanity gate rejects routed paths above 1.8x curated mileage as wrong-way detours (a wrong line is worse than a straight one) and keeps paths under 0.6x with a coarse flag. Spokes at or under 0.3 mi stay straight by design. The map server, the board, and GPX exports all draw through the shared day_path helper, with per-hop straight fallback and layover days emitting the stationary point. Across nine parks, 85 of 96 substantial edges now ride real OSM tread (2 of them coarse: shape trusted, mileage not), with 11 honest straight fallbacks. Four fallbacks are permanent by design: the Sand Dunes dunefield (no trail exists in open sand), Aasgard Pass (an OSM gap at the boulderfield), lower Conundrum (disconnected mid-valley), and Crater Lake to the upper West Maroon valley. The harvest doubled as a coordinate reckoning: the validator convicted memory-grade curation repeatedly (Marion Lake 4 km off, Geneva Lake 7 km, Devils Thumb Park 8.7 km, the Lena trailhead 1.1 km, the Maroon Scenic entrance at the welcome station), and the standing repair recipe is to anchor coords to OSM named features or snap to the big trail component's nearest vertex. Mileages were adopted from OSM-measured geometry for the recall-grade networks (Teton Crest, Indian Peaks, and the Maroon Bells trunk pass legs) and kept from published sources elsewhere, with routed lengths retained as a QA signal. Everything ships under ODbL with attribution in every geometry file and on every map surface. Trail-true DEM (dem_trail_v1) is unblocked by this work and queued behind the Open-Meteo rate limit.

## v2.6.0 (2026-07-13)

The Colorado wave, built to be right rather than fast. Four parks ship: Maroon Bells-Snowmass (permit 4675333) trips-ready with the Four Pass Loop trunk, the Crested Butte connection over West Maroon Pass, and the Conundrum, Capitol, Geneva, and Snowmass Creek approaches, modeled with cluster junctions so the solver finds ANY open site among Crater's 11, Conundrum's 20, or Capitol's 9 (the 40 site spokes are generated from the dataset, not typed); Indian Peaks (full-season permit 4675318; the 3-days-in-advance permit 4675319 is a separate inventory noted for a dual-permit merge) trips-ready across the Monarch, Brainard, Fourth of July, Hessie, and Devils Thumb Park approaches with group-division twins; Great Sand Dunes (4675316) trips-ready as the Sand Ramp linear chain plus the dunefield zone; Rocky Mountain (4675320) Tier 1 across 247 sites plus a trips-ready Wild Basin corridor anchored on NPS mileages. Black Canyon has no recreation.gov permit and joins the holdouts honestly. Live proofs: 24 September itineraries in Four Pass country including the loop itself as a 3-nighter, 16 at Indian Peaks, 301 across 64 routes in Wild Basin, and Sand Dunes honestly thin. Data-honesty catches recorded: RMNP still lists retired bivy sites as active (now excluded), Sand Dunes cloned the park HQ coordinate onto every site, and rec.gov zone coordinates are now junk three-for-three on forest permits. Day-hike suggestions now ignore sub-mile spokes. Gains: pass arithmetic in the Elks and Indian Peaks (DEM lines cross the ranges), DEM line in Wild Basin and the dunes where the terrain permits it.

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
