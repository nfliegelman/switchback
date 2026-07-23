# BACKLOG.md

Triaged v3.3.0 against PRODUCT.md priorities. Labels: P0 required for
the coherent product, P1 immediately after, P2 strategic, PARKED do
not build without new evidence, SHIPPED kept for the record. Items
below the triage table retain their original detail.

| Item | Label | Note |
|---|---|---|
| Maroon Zone anchor relocation and edge re-audit | SHIPPED v3.6.4 2026-07-22 | anchor was ON the Maroon Peak massif (13,421 ft); relocated into the West Maroon valley, both polylines truncated to drop the 1.23 mi ridge spur, Crater and North Fork mileages re-measured (3.4 to 1.9, 11.53 to 10.3), fake 31% grades gone. See HANDOFF 2026-07-22 |
| TripRequest, TripPlan, Stay, planner.py contract | P0 | Phase 1 core, spec in PRODUCT.md 6 and SPEC.md |
| Per-search effort in request API and form | P0 | ends silent profile.json dependence |
| Frontcountry curation for Rainier, RMNP, Lena | P0 | narrow, honest policy labels first |
| Trip-shape toggle UI (engine shipped v3.1.0) | P0 | form chips, vocabulary already aligned |
| Zero-result repair ladder with quantified relaxations | P0 | solver relaxation analysis |
| Golden scenario suite (PRODUCT.md 18.2) | P0 | 10 scenarios, offline fixtures |
| Complete-trip alerts on watch substrate | P1 | after TripPlan exists |
| Calibration reactions fold-in | P1 | PARTIAL 2026-07-22 (v3.6.3): Rainier and RMNP effort reactions folded into scoring weights (0.4/0.6/0.15 to 0.5/0.45/0.1); comfortable day 9 mi / 2200 ft validated by the reactions and kept. REMAINING: re-fold Maroon Bells after the Maroon Zone anchor fix (its day totals are corrupted today); the steep-descent term has its own row; optional further dials if Noah wants brutal-but-great-camp trips pushed below comfortable ones, a steeper above-comfortable day_fit penalty or a hardest-day weighting instead of the day mean |
| Route repair and permit-free fallbacks | P1 | corridors and dispersed are the inventory |
| Campflare handoff | P1 | outbound links first |
| Pilot inline-geometry carry-through | P1 | dispersed regrade quality |
| Dispersed candidate criteria pass (upper basins, orphan check) | P2 | revives Blue Lakes, Highland Mary |
| IPW as fourth slice destination | P2 | dual-permit showcase |
| Point-to-point with exit entrances and shuttle logistics | P2 | UI already truthful |
| Long-trail section planning on corridor assets | P2 | |
| Archetype B Sierra trailhead-quota parks | PARKED | fails the decision filter until P0 metrics healthy |
| Solitude modeling | PARKED | data unlocked, build parked per brief |
| More alert channels | PARKED | |
| Winter seasonal divisions | PARKED | |
| Monetization gates G1 to G3 | PARKED | see project/archive/FUTURE.md |
| Calibrate and trips must announce total network failure instead of reading as sold out | P1 | trust; the v2.0.6 silent-filter lesson applies; evidence 2026-07-20, a blocked container printed the honest-empty section for two live windows |
| Trace-backed durations at plan time | P1 | cache per-edge elevation traces to disk so the planner can run the 20-section grade math offline instead of the edge-level characteristic-grade fallback; profile panel already does the accurate version live |
| Calibrate default pace bands from owner GPX tracks | P2 | pace.py DEFAULT_PACE_MPH is Tobler-informed hand-set; real recorded hikes beat it; owner can already override via profile.json pace table |
| Trail surface quality as a secondary difficulty input | P1 | OWNER-DIRECTED 2026-07-20: tread matters independent of grade (Lena's smooth tread praised; the same grade on roots or scree is a different hike). Two sources, layered: OSM way tags as the objective base, since our fetch pipeline already pulls the ways (surface, sac_scale, trail_visibility; sac_scale T1 to T6 is a ready-made roughness ladder), stored per edge with src like every other edge fact; then AllTrails review text distilled per trail during the ratings harvest as color (same policy: sparing, attributed, never bulk, never fetched by the app). Surfaces in day terrain lines and as a scoring nudge only after reactions justify a weight. CONFIRMED 2026-07-22: the tags are NOT actually stored yet; geometry.py keeps trail SHAPE only (out geom) and drops the way tags, and parks/edges plus parks/geometry carry zero tread fields, so this needs a dedicated Overpass fetch pass, which the no-egress container blocks (proxy 403). Owner RAISED this to a calibration blocker ("calibration is useless without this"), so it moves ahead of finishing the effort presets; plan is a network-capable session for the fetch, with an optional Lena-only curated pilot first to validate the tag-to-difficulty model offline. SUPERSEDED 2026-07-22 by a live probe: OSM condition tags are EMPTY or uniform for US wilderness trails (Upper Lena, known brutal, has no tags at all), so the automated-fetch plan is dead. New plan: tread is a CURATED per-edge class seeded from the AllTrails MCP (difficulty plus review color, distilled and attributed per the standing policy) plus owner ground truth, grown destination by destination. See the 2026-07-22 HANDOFF entry |
| Per-day descent totals and richer objective descriptors in solver day stats | P2 | describe_trace now shows climbs, up/down, and grade buckets from the trace; carrying descent and climb counts into the offline solver day stats needs directional loss sums along each leg path, cheap via the adjacency reverse entries |
| AllTrails beauty ratings as a camp-quality prior | P1 | OWNER-DIRECTED 2026-07-20: AllTrails stars capture perceived beauty and overall experience, which is orthogonal to our difficulty math and is the rating channel the owner trusts most. Plan: harvest per destination, in sessions, via the official AllTrails MCP under the standing policy (factual points with src attribution, sparingly, never bulk, content never stored, the app never calls AllTrails directly); map each rated trail to the camps it serves and record star plus review count as a src-cited external prior in parks/ratings.json alongside personal ratings; personal ratings still override everything; Rainier first as the vertical slice, then RMNP and Lena. Slow destination-by-destination buildout is expected and fine |
| Leaflet CDN local fallback | PARKED | OWNER TABLED 2026-07-21: the map app loads Leaflet from unpkg at startup, so if unpkg is unreachable the whole UI blanks. Fix would vendor Leaflet locally plus an if-window.L guard plus service-worker precache. Owner accepts the outage risk for a personal tool; revisit only if it actually bites |
| Web UI interaction and accessibility hardening | P1 | AUDIT 2026-07-21 (project/audits/): confirm-on-quit, surface the swallowed availability-refresh error, replace the raw GPX alert, add an h1 plus visible focus plus a non-color map-status channel, darken the sub-AA muted gray. Primary-flow UI, so land behind the standing real-browser gate; needs a chromium-capable session |
| Backend hygiene cluster | P2 | AUDIT 2026-07-21: send_telegram has no retry while everything else does (a transient Telegram failure raises out of a watch cycle); history.py has no schema version; web and board duplicate _codes_filter and _coords; dash sanitize lives in three display sites, not the extract_park ingest path (the manual grep gate is the real enforcement). All low severity for a localhost single-user tool |
| Browser test in CI | P2 | QUALITY 2026-07-21: install playwright plus chromium in a CI job so tests/test_browser.py actually runs on GitHub, making CI the standing real-browser gate for primary-flow UI changes (today it self-skips without chromium). Would let the tabled web UI work be verified remotely without a local browser |
| Widen ruff, add type checking | P2 | QUALITY 2026-07-21: ruff.toml lints pyflakes (F) only, to avoid reformatting the compact house style; a later pass could add import-order or select E rules, and mypy could check the typed plans.py contract. Each needs its own green-up cleanup before landing in scripts/check.sh |
| Graphical grade mix in the app day detail | P1 | OWNER-DIRECTED 2026-07-22 (calibration note 2): replace the wall of per-grade mileages with a picture, a direction-aware stacked bar showing the percentage of a day at each grade band, steep downhill its own segment (pairs with the same-day pace.bucket_miles uphill/downhill split). Primary-flow UI so it lands behind the standing real-browser gate; the calibration sheet stays plain text since a markdown file cannot render the bar and per-grade miles there are still the calibration signal |
| Steep-descent difficulty term in scoring | P2 | OWNER SIGNAL 2026-07-22 (calibration): he repeatedly says steep downhill is worse than flat or gentle downhill, but the score has NO grade or descent term at all (only day_fit on miles plus gain, camp_pct, lakes, solitude). A steep-descent penalty is a real candidate, gated on clean per-edge profiles AND his re-read of the corrected v3.6.2 sheet; never tune it on the Maroon Zone anchor-bug grades |
| Trip-shape toggles engine, dual merge, corridors, RMNP buildout, dem_trail, toughest-stretch, coverage waves | SHIPPED | CHANGELOG.md |

## Original detail (pre-triage, kept)


Future features, categorized, with the owner's direction recorded. Status tags: DIRECTED (Noah gave explicit direction), DISCUSSED (analyzed together, no commitment), PARKED (explicitly deferred by Noah), GATED (blocked behind a decision gate). Last updated 2026-07-07. Engine work lives in ROADMAP.md; rationale lives in SPEC.md, whose Part 2 carries the old SCOPE.

## 1. Trip shapes and logistics

- Shuttle trip type (any exit trailhead, second-car flag). PARKED 2026-07-07: "not something I'd like to add just yet... a toggle in the future." Effort 2-4 h on the solver once wanted.
- Drive-time weighting of entry trailheads (prefer starts closer to where you slept). DISCUSSED. Needs origin input. 2-3 h.
- Per-camp stay limits and seasonal open dates encoded per park. DIRECTED (implied by basecamp mode). Partially in M4.

## 2. Map and UI

- Web UI (v2.1 per the 2026-07-07 engine-first decision): local FastAPI backend plus a Leaflet frontend in one HTML file (browsers cannot call recreation.gov directly, CORS), ranked routes as selectable layers, availability and rating colored markers, per-day stat cards, amber and red limit alerts. DIRECTED. 12-18 h.
- Adventure mode on the map (absorbs the route editor: swap, insert, remove, reverse, build by clicking camps). DIRECTED. 6-10 h on top of map v0.
- Stay versus pass-through toggle per clicked camp; alerts evaluate per day, not per leg. DIRECTED.
- GPX with real trail geometry instead of node-to-node lines. DISCUSSED. Needs edge geometries from OSM. 3-5 h after the OSM pipeline.
- CalTopo feed enrichment: rating and availability properties on the GeoJSON. DIRECTED. 2 h, lands with M5/M8 data.
- Rejected UI path: tkintermapview desktop maps. Dead end for sharing.

## 3. Data and coverage

- OSM plus DEM edge pipeline for parks without published mileage tables, with gain smoothing (raw DEM overstates 10-25 percent). DISCUSSED. 12-20 h plus QA per park.
- Additional camp-night parks: Yellowstone, Grand Teton, Olympic, Grand Canyon use areas. DISCUSSED. 3-6 h each with official tables.
- Archetype B parks (Yosemite, SEKI trailhead quotas, camp anywhere). DISCUSSED. 10-15 h; pulls the OSM pipeline forward.
- Enchantments zones. DISCUSSED. About 1 h; five zones.
- Curated non-permit areas, two or three favorite forests only. DISCUSSED. Manual, does not scale, fine for personal use.
- Holdout booking systems (Zion, Great Smoky, Denali, state parks). DISCUSSED. Only on demonstrated need; each is a separate fragile integration.
- Frontcountry campground availability (sibling rec.gov endpoint) to support basecamp day-hiking trips. DIRECTED (wanted "including non-permit ones"). About an evening.
- Seasonal snow depth overlay from public gridded snow data. DISCUSSED. 6-10 h, shoulder-season value.

## 4. Ratings and intelligence

- Lazy rating workflow: rate only camps that surface; Claude research pass drafts a prior with source links; personal rating overrides forever. DIRECTED. Reddit protocol applies: no Reddit claims without actual threads, links, and quotes; say so explicitly when none were found.
- Per-park percentile normalization ("a 4.5 at Glacier competes only against Glacier"). DIRECTED.
- Demand and crowding signal from own scan history (fill velocity percentile; sign flips with the solitude preference). DIRECTED. Needs a season of M8 logs before scoring uses it.
- Prior coefficient calibration after 20 or more personal ratings exist. DISCUSSED.
- Day-hike POI nodes: passes, lookouts, and non-camp lakes as graph destinations so basecamp suggestions go beyond camps (e.g. Ptarmigan Tunnel itself as a target). DIRECTED. 2-4 h once a park's POIs are listed.
- Olympic as next park: the owner's real Lena pattern (Lower Lena base, Upper Lena day hike) lives there and the Lena permit is on rec.gov. Extractor should work day one; edges need the Hamma Hamma corridor. DIRECTED.
- Weather per camp via NWS point forecasts. DISCUSSED. 2-3 h.
- Permit Difficulty Index (PDI): a 0 to 100 gettability score per camp and per park. DIRECTED 2026-07-07: rank how hard every permit is to get, because some routes have an easy permit you can wait for an opening on. Components: percent of season currently open (works from any single scan; Belly River 2026-07-07: Poia 9 open party-of-2 dates, Helen 0), sellout velocity from release day, observed cancellation rate, walk-up share. The last three need M8 history. Feeds an optional gettability term in scoring when dates are flexible.

## 5. Alerts and automation

- GitHub Actions poller plus Pages dashboard (Nimbus and Drizzle pattern). DISCUSSED. 4-6 h. Note Actions cron delays of 10-15 minutes; use local scheduling for fast cancellation windows.
- Multi-park portfolio scan ("where can I go these dates"). DIRECTED. 2-3 h.
- Watch-mode hardening: persistence check before alerting (rec.gov permits flicker), negative-remaining clamp, group-size hiding awareness. DISCUSSED.

## 6. Distribution and monetization

GATED behind FUTURE.md gates G1-G3 (5+ personal trips across two seasons; 3 strangers ask to pay; accept undocumented-endpoint platform risk). Landscape as of July 2026: Campnab from $10 to $90 per month, Outdoor Status annual, PeakPeeker $5 one-time, PermitAlert free. Generic alerting is commoditized; the only defensible angles are itinerary chaining plus curated trail context.

- PyInstaller onefile exe for sharing. DISCUSSED. 2-4 h, antivirus friction expected.
- Open source with README and screenshots. DISCUSSED. Near-free once M10 lands.
- Web app. DISCUSSED. 20-40 h; only if serving people beyond the owner.

## 7. Non-goals (settled, do not reopen without cause)

AllTrails route-builder integration, automation, or scraping. Storing or mirroring AllTrails or WTA content (link-only, always). Auto-booking permits. CalTopo-clone drag interaction. Programmatic Garmin push (manual GPX import is two taps). External per-camp crowding data. National no-permit legality database. Structured water-source status. Sub-minute polling.


## Web UI polish (v2.1.x, after the owner's desktop test drive)

Foundation shipped as v2.1.0. Remaining: GPX download button per route; day-hike cards on layovers (structured, not just note strings); scoring.json editor drawer so calibration is a slider not a file edit; region overlay once v2.2 lands; mobile-width layout pass; availability heat legend by date.

## Durable cloud history (small, follows the cloud watcher)

The Actions watcher accrues history.sqlite in the runner cache, which is best-effort storage. A nightly job should snapshot it back into the repo (or Pages artifact) so the demand dataset survives cache eviction and becomes plottable. One commit a day, not one per cycle.

## AllTrails synthesis via the official MCP (DIRECTED 2026-07-13, owner request)

The owner challenged the blanket link-only stance and was right: the official AllTrails MCP connected in his Claude returns structured facts (length, elevation gain, rating, difficulty, route type, land-unit label, URL) that can legitimately feed Switchback. Proven live 2026-07-13 by pulling the Lena corridor in-chat.

Refined policy, replacing the old blanket rule: factual data points (distances, gains) may be recorded sparingly in edge files with src attribution "AllTrails official MCP <date>", exactly as WTRF and PNTA numbers are recorded today. Descriptions, reviews, and photos are never stored, only linked. Bulk harvesting is never done; that is scraping with extra steps. The Switchback app itself never calls AllTrails: the MCP lives on the Claude side, so the channels are (a) in-chat research sessions whose outputs land in repo files with attribution, and (b) the FUTURE.md item 14 medium path, a Claude-API artifact passing the AllTrails MCP server for live lookups.

Three uses, in value order: (1) edge validation and seeding, especially GAINS, the engine's weakest number: an interim patch for the est-gain understatement until the DEM pass; (2) crowd proxy: trail popularity signals (ratings volume, traffic labels) approximate demand today instead of waiting weeks for M8 history, with the caveat that trail traffic is not camp fullness; (3) day-hike POI enrichment for basecamp layovers, live via the Claude-artifact path or link-only in the local app.

Integration matrix (decided 2026-07-13 after a full tool inventory; the connector exposes five tools, three proven live in-chat, two known by schema):

INTEGRATE NOW, critical tier: (1) length and elevation gain per named trail as edge seeds and validators with src attribution, the interim patch for the est-gain understatement until the DEM pass; (2) location_label, the land-unit tag on every trail card, as the regions QA signal confirming which permit system a trail belongs to, free in every result and exactly the Forest-vs-Park split the Lena pull demonstrated.

INTEGRATE SOON, moderate tier: (3) trail_traffic (light, moderate, heavy, from AllTrails activity data) plus most_popular and per-month popularity sorts on the near and bounds searches: a crowd and seasonality proxy available today without any details call, feeding the scoring solitude term as a prior until M8 history matures, with the standing caveat that trail traffic is not camp fullness; (4) alltrails_web_url stored per corridor for deep links on trips output and CalTopo properties, URLs being plainly storable; (5) features and attractions tags (waterfall, views, wildflowers, wildlife) as scoring terms beyond lake and as day-hike POI card content, deferred to the v2.1 scoring pass; (6) difficulty and route_type as QA cross-checks against day-fit and the classifier, never as scoring inputs.

LIVE-ONLY, never stored: (7) get_trail_weather_overview, the 7-day trailhead forecast, pairing naturally with watch alerts and trip cards via the Claude-artifact path, and folding into the existing Weather backlog item; (8) descriptions, review_summary, and photos, display-only through the artifact path.

SKIP: duration_minutes (our pace model derives this), suitability and dog rules (not permit-relevant), profile photos (content), trail_head_distance (null in practice).

Open blocker: get_trail_details (exact review counts, the sharpest crowd input) requires a permission tap that has not registered across three attempts; the dialog must be accepted while the call is pending. Until then the traffic labels carry the crowd proxy alone.

Harvested Lena seed data (src: AllTrails official MCP, 2026-07-13): Lower Lena Lake Trail, Olympic NATIONAL FOREST label, 6.4 mi RT, +1,548 ft, 4.7 stars, moderate, out and back. Lena Lake Trail to Upper Lena Lake Trail, Olympic NATIONAL PARK label, 13.4 mi RT, +4,655 ft, 4.5 stars, hard. Derived pilot edges (est flags apply, RT gains cannot be split exactly one-way): trailhead to Lower Lena 3.2 mi, roughly +1,400 ft; Lower Lena to Upper Lena 3.5 mi, roughly +2,500 ft, the famously steep section. Day-hike POI example from a Lower Lena basecamp: The Brothers via Lower Lena, 15.8 mi, +6,870 ft, 4.3 stars. AllTrails itself labels the two lakes to different land units, confirming the exact cross-boundary case the regions item below exists for.

## Trail geometry QA (v2.7 SHIPPED 2026-07-13)

v2.8 status: Summerland RESCUED on NPS centerlines. Confirmed absences on both datasets: Aasgard, the dunefield, upper Sand Ramp, lower Conundrum, the Ouzel spurs, Nickel Creek to Box Canyon (verify the 0.8 curated figure), and now Maroon to East Fork. The Conundrum Trailhead coordinate truth check is the single blocker for that spur. Remaining path to fewer straights: the GPX patch channel (owner traces win over everything).

Rainier: White River to Summerland and Nickel Creek to Box Canyon reject as detours, verify against NPS. Glacier: routed lengths say ELF to IPE is 11.3 vs curated 9.8 and ELH to HEL is 2.6 vs curated 1.5; both look like curated-mileage corrections, confirm before adopting (the AllTrails MCP is now connected as a sanctioned QA channel per the v2.0.4 policy). RMNP: the Siskin to Ouzel Lake and Ouzel to Upper Ouzel spurs reject as detours, likely unmapped campsite spurs. Enchantments: Aasgard stays straight until OSM maps the boulderfield line; the Snow Lakes descent measures 4.1 vs published 6.5, coarse digitization suspected. Sand Dunes: Little Medano to Aspen rejects as a detour and Cold Creek to Sand Creek does not snap; the dunefield fallback is permanent by design. Maroon Bells: an OSM gap sits above Crater Lake toward the upper West Maroon valley, lower Conundrum is disconnected mid-valley, the Conundrum Trailhead position deserves a truth check, and Elk Range dispersed-zone centers remain the fuzziest coords in the repo (QA against the USFS zone map). Board window tuning: the Four Pass window shows honest peak-season zeros; consider 45 to 66 days out for shoulder-season space. dem_trail_v1: sample elevation along the harvested polylines to retire pass arithmetic where geometry exists; unblocked, queued behind the Open-Meteo rate limit alongside the rmnp rerun.

## Colorado residuals (v2.6 SHIPPED 2026-07-13)

RMNP corridor buildout: Glacier Gorge, East Inlet, Sandbeach Lake, North Inlet, Lawn Lake (240+ sites remain un-graphed). IPW: verify the east-of-divide connector zones to close the Pawnee-Buchanan loop (the 4675319 dual-inventory merge SHIPPED v2.21.0; Enchantments reuses merge-inventory). Maroon Bells: Conundrum to Copper Lake over Triangle Pass link; semantics of the Areas Outside of Permit Zones division. Sand Dunes: NPS mileage table QA; investigate the September Sand Ramp thinness (closure vs sellout). Coordinate QA queue now spans MB zones, all IPW, all Dunes, RMNP Thunder pair, plus the earlier Teton, Enchantments, and Lena flags. Black Canyon joins Zion, Smokies, and Denali as holdouts. Rerun dem rmnp when the Open-Meteo rate limit clears (one Wild Basin edge is on arithmetic). Seasonal division modeling: RMNP winter variants (26 divisions, currently excluded) as a season-gated inventory layer.

## DEM and data QA residuals (v2.4/v2.5 SHIPPED 2026-07-13)

Trail-geometry DEM v2 (OSM way polylines instead of straight lines) would extend DEM coverage into canyon terrain; until then pass arithmetic covers it. Per-edge QA: Rainier Maple Creek to Paradise River and White River to Summerland (DEM overshoot flags). Coordinate QA: Teton Crest zones, Alaska Basin, Enchantments zones, Lena (all curated approximations). Enchantments daily-lottery permit 445863 as a dual-permit region with 233273. PDI components: sellout velocity and weekend premium activate as the daily scans deepen.

## Regions residuals (v2.2 SHIPPED 2026-07-13; design below kept for history)

Remaining from the pilot: Olympic features pass (~300 camps, OSM join session with the usual manual queue); Lena overlay coords QA against a GPS track; Olympic proper corridors (Grand Valley / Moose Lake first, it was the owner's top pick); The Brothers as a day-hike POI node; unify the web and board trip-building duplication into one tripsvc module.

## Cross-boundary regions (DIRECTED 2026-07-12, owner request; SHIPPED as v2.2.0)

The Lena problem: Lower Lena Lake is a no-permit FCFS site in Olympic National Forest; Upper Lena is inside Olympic National Park on a wilderness permit; they sit 2 to 3 trail miles apart on the same trail and should chain in one itinerary. Today's engine cannot do this: one park dataset carries one permit_id, the graph loads one park, and the solver fetches one permit's availability.

The design: a REGION stitches multiple permits plus permitless overlays into one graph. Camps gain optional permit_id and a policy field (reservation, fcfs, none); availability fetches group by permit; permitless camps get an always-open entry but their nights are labeled honestly (first-come, no reservation exists to check, capacity not guaranteed) and never shown as Reservable. Scoring, GPX, watch, and day hikes already operate on nodes and need no changes. The v2.1 adventure frontier on a region delivers the owner's exact UX: click Lower Lena for night 1 and Upper Lena appears for night 2 whenever ONP inventory has it.

Pilot region: the Lena corridor itself (two camps, one trailhead, two edges), which also makes the owner's real trip solvable. Seed mileage and gain figures already harvested via the AllTrails MCP, see the item above. Estimate: 4-8 h engine work plus trivial pilot data. Sequencing: after the v2.0.0 test drive, alongside or just before Olympic proper, since Lena IS the Olympic gateway.

## Park and forest expansion plan (recorded 2026-07-12, doc audit)

This plan existed only in conversation until the owner caught the drift. Recording it properly:

The trigger rule: a park or forest gets added when a real trip demands it, not on a schedule. Park additions are data sessions (extract, features, transcribe edges), fully independent of the v2.1 web UI code track; the two can interleave freely.

Archetype A (camp-night divisions, works with today's engine unchanged): most NPS wilderness permits (Yellowstone, Grand Teton, Olympic, Grand Canyon use areas) AND national forests on recreation.gov, because the platform is operator-agnostic; the extractor already runs on any permit id. High-value forest targets: Enchantments / Alpine Lakes zones (about 1 h, five zones), Desolation Wilderness, Mt. Whitney, and the Olympic NF Lena Lakes permit that motivated the basecamp feature.

Archetype B (trailhead-quota model: Yosemite JMT and wilderness, SEKI): needs the trailhead-quota solver variant where divisions are entry trailheads rather than camps. Scoped, not started.

Holdouts running their own booking systems (Zion, Great Smokies, Denali): out until a trip demands one badly enough to justify a custom integration.

First wave after the owner's v2.0.0 test drive: Olympic (NP plus the NF Lena permit), then Grand Teton. Cost per Archetype A park: 3-6 h today, dominated by mileage-table transcription; drops toward 1-2 h once the OSM plus DEM edge pipeline (above) replaces hand transcription.


## Dispersed itineraries experiment (owner approved 2026-07-13)
Goal: full trip generation in permit-free areas. Plan: derive candidate camp nodes from OSM named lakes and basins plus trail junctions inside the boundary, build edges by routing on the area TrailNet, availability is synthetic always-open through the existing region overlay machinery (policy none). Pilot on one Weminuche drainage (Needle Creek or Vallecito) and compare output against published route knowledge before trusting it anywhere. Auto may work, auto may need a curation pass; that is the test. STATUS: phase A PASSED 2026-07-13, see EXPERIMENTS.md; phase B (synthetic availability plus solver) is next. Next area waves per the Colorado atlas in coverage/COVERAGE.md: La Garita and Powderhorn complete the San Juans, then the central classics.


## Rubber band route builder (owner spec 2026-07-13)
Tap a node, drag toward another; the real trail polyline animates outward along the actual path, green while inside the area boundary, amber the moment it crosses out, release to commit the leg and advance the frontier. Phase 1, permit parks: no routing needed, animate the stored edge polylines with stroke dashoffset toward the neighbor nearest the drag bearing, merge with Adventure mode's frontier stepper. Phase 2, dispersed areas: ship trail adjacency in the area files, client side Dijkstra with a binary heap targeting under 100 ms at Weminuche scale, ray cast point in polygon against the boundary rings for the color split. Pairs with the dispersed itineraries experiment; adjacency shipped for one enables the other.


## Rubber band residuals (v2.11 SHIPPED 2026-07-13)
GPX export of a drawn route. South San Juan connectivity audit (main network only 15% of nodes; likely heavy bbox-pad capture plus CDT corridor fragmentation, verify against the boundary). Undo last leg. Park-side phase 1 is schema-adaptive against /api/park; if the button never appears on parks, the payload shape drifted, check the adapter first.


## Washington map wave (v2.13 capture complete, builds queued)
One command each, statuses flip to map on success: glacierpeak, pasayten, mountadams, indianheaven, lakechelansawtooth, mountbaker, noisydiobsud, williamodouglas, henrymjackson, wildsky, norsepeak, boulderriver, salmopriest, wenahatucannon, buckhorn, thebrothers, mountskokomish, colonelbob, wondermountain, tatoosh, glacierview, trappercreek, clearwater. North Cascades, St. Helens, Juniper Dunes, and the PCT corridor need non-USFS-wilderness boundary sources first.


## WA wave status (2026-07-13): 21 of 23 built. wondermountain and glacierview hang a full Overpass mirror timeout on tiny bboxes; retry another day or shrink the boundary pad before fetching.


## CO wave status (2026-07-13): 27 of 27 built, wave complete. Remaining planned CO rows are the non-wilderness boundary set; sources needed: BLM NCA polygons, NPS unit boundaries, monument and state park boundaries, and long-trail centerline corridors for the CT and CDT.

## Owner task tracking (2026-07-14)

OWNER.md is now the single list of everything on Noah, phone vs desktop; keeping it current on every release is a standing convention alongside the dash gate.

- Trip-shape toggles (owner, 2026-07-15): trip_types list replaces trip_type string; toggles in every settings surface; default all-on. Spec in ROADMAP v3.x. NOT STARTED.

- ELK RANGE ROOT CAUSE (found 2026-07-16, FIXED v3.6.4 2026-07-22, see HANDOFF; historical detail kept): the Maroon Zone anchor node 4675333025 sat at about 13,450 ft ON the West Maroon ridge; the curated zone centroid landed on the ridge, not in the camping valley. This is the true root of the v2.8 display mystery, and it taints the v2.23 mileage correction (7.19 to 11.53 was measured along geometry TO the misplaced node, so it inherits the error). NEXT SESSION: relocate the anchor to a representative valley point (Crater Lake basin, about 10,100 ft), re-derive the affected edges and geometry, re-audit the corrected mileage, and rerun the Elks calibration ballot. Until then, Elks distances and profiles above about 12,000 ft near Maroon Zone are suspect.
