# BACKLOG.md

Future features, categorized, with the owner's direction recorded. Status tags: DIRECTED (Noah gave explicit direction), DISCUSSED (analyzed together, no commitment), PARKED (explicitly deferred by Noah), GATED (blocked behind a decision gate). Last updated 2026-07-07. Engine work lives in ROADMAP.md; rationale lives in SPEC.md and SCOPE.md.

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

RMNP corridor buildout: Glacier Gorge, East Inlet, Sandbeach Lake, North Inlet, Lawn Lake (240+ sites remain un-graphed). IPW: verify the east-of-divide connector zones to close the Pawnee-Buchanan loop; merge the 3-days-in-advance permit 4675319 as a dual inventory. Maroon Bells: Conundrum to Copper Lake over Triangle Pass link; semantics of the Areas Outside of Permit Zones division. Sand Dunes: NPS mileage table QA; investigate the September Sand Ramp thinness (closure vs sellout). Coordinate QA queue now spans MB zones, all IPW, all Dunes, RMNP Thunder pair, plus the earlier Teton, Enchantments, and Lena flags. Black Canyon joins Zion, Smokies, and Denali as holdouts. Rerun dem rmnp when the Open-Meteo rate limit clears (one Wild Basin edge is on arithmetic). Seasonal division modeling: RMNP winter variants (26 divisions, currently excluded) as a season-gated inventory layer.

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
Goal: full trip generation in permit-free areas. Plan: derive candidate camp nodes from OSM named lakes and basins plus trail junctions inside the boundary, build edges by routing on the area TrailNet, availability is synthetic always-open through the existing region overlay machinery (policy none). Pilot on one Weminuche drainage (Needle Creek or Vallecito) and compare output against published route knowledge before trusting it anywhere. Auto may work, auto may need a curation pass; that is the test. STATUS: phase A PASSED 2026-07-13, see EXPERIMENTS.md; phase B (synthetic availability plus solver) is next. Next area waves per COLORADO.md: La Garita and Powderhorn complete the San Juans, then the central classics.


## Rubber band route builder (owner spec 2026-07-13)
Tap a node, drag toward another; the real trail polyline animates outward along the actual path, green while inside the area boundary, amber the moment it crosses out, release to commit the leg and advance the frontier. Phase 1, permit parks: no routing needed, animate the stored edge polylines with stroke dashoffset toward the neighbor nearest the drag bearing, merge with Adventure mode's frontier stepper. Phase 2, dispersed areas: ship trail adjacency in the area files, client side Dijkstra with a binary heap targeting under 100 ms at Weminuche scale, ray cast point in polygon against the boundary rings for the color split. Pairs with the dispersed itineraries experiment; adjacency shipped for one enables the other.


## Rubber band residuals (v2.11 SHIPPED 2026-07-13)
GPX export of a drawn route. South San Juan connectivity audit (main network only 15% of nodes; likely heavy bbox-pad capture plus CDT corridor fragmentation, verify against the boundary). Undo last leg. Park-side phase 1 is schema-adaptive against /api/park; if the button never appears on parks, the payload shape drifted, check the adapter first.


## Washington map wave (v2.13 capture complete, builds queued)
One command each, statuses flip to map on success: glacierpeak, pasayten, mountadams, indianheaven, lakechelansawtooth, mountbaker, noisydiobsud, williamodouglas, henrymjackson, wildsky, norsepeak, boulderriver, salmopriest, wenahatucannon, buckhorn, thebrothers, mountskokomish, colonelbob, wondermountain, tatoosh, glacierview, trappercreek, clearwater. North Cascades, St. Helens, Juniper Dunes, and the PCT corridor need non-USFS-wilderness boundary sources first.
