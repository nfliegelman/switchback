# SCOPE.md

Feature triage for the full loop: recommend camp sequences within effort limits, display on a map, edit or build routes, export GPX to AllTrails / Garmin / CalTopo. Companion to SPEC.md and FUTURE.md. Part of Switchback.

## The principle that keeps this buildable

A route is an ordered list of camps (with pass-through flags), never a geometric line. Geometry, distance, gain, and the GPX track are always derived from the camp sequence via graph edges. Editing becomes list surgery: swap a camp, insert or remove a night, reverse direction. The solver, the map editor, and the GPX exporter share one representation, so building the editor is cheap. The moment routes become freehand geometry, cost jumps an order of magnitude, and freehand only matters in camp-anywhere terrain where designated camps do not constrain you anyway.

## Bucket 1: build ourselves, well

| Feature | Effort | Notes |
|---|---|---|
| Availability engine | Done | Search, divisions, month availability, classification |
| Payload extractor: camps, trailheads, parking, connectivity | 2 h | Validated live against Rainier, 245 features |
| Route graph for camp-night parks from official mileages | 3-5 h per park | Rainier, Glacier, Teton, Olympic, Yellowstone |
| Feature tags via spatial joins: lakes, creeks, elevation, trailhead distance | 8-12 h once | USGS hydrography + 3DEP, then cheap per park |
| Itinerary solver: chained availability, daily max miles/gain/grade, basecamp, pass-through | 6-10 h | DP over (day, camp) states |
| Scoring and ranking: weights, per-park percentiles, cold-start priors | 4-6 h | Third time building this pattern this year |
| Demand signal from own scan history | 2-3 h | Plus a season of logged scans before it means anything |
| Ratings store + lazy research workflow | 2 h | Ongoing curation, only for camps that surface |
| Map v0: Leaflet on GitHub Pages, ranked routes as selectable layers, availability/rating markers, per-day stat cards, amber/red limit alerts | 12-18 h | Same repo pattern as Nimbus/Drizzle dashboards |
| Structured route editing: swap camp for valid alternates, insert/remove night, reverse, build from scratch by clicking camps | 8-12 h | List surgery per the principle above |
| GPX export: track + camp waypoints | 1-2 h | Imports to AllTrails custom maps, Garmin, Gaia, CalTopo |
| CalTopo GeoJSON feed | Shipped | +2 h later for rating and availability properties |
| Weather per camp (NWS point forecasts) | 2-3 h | Free, official |
| Telegram watch alerts | 3-5 h | Reuses existing bot |
| Multi-park portfolio scan | 2-3 h | "Where can I go these dates" |

Complete loop for camp-night parks: roughly 41-60 h total.

## Bucket 2: feasible, but real work

| Feature | Effort | Why it is here |
|---|---|---|
| Freehand routing along trails (click anywhere, snap via OSM trail graph) | 15-25 h + QA per region | Graph build, point snapping, gap fixing, on-the-fly elevation. Only needed for camp-anywhere terrain |
| OSM + DEM edge pipeline for parks without published mileages | 12-20 h + QA per park | Compute replaces transcription |
| Archetype B parks (Yosemite, SEKI trailhead quotas) | 10-15 h | Different feasibility model, camp-anywhere rules encoding, pulls freehand routing forward |
| Curated non-permit areas (2-3 favorite forests) | Manual per area | Fine for places you actually use, does not scale |
| Seasonal snow depth overlay (public gridded snow data) | 6-10 h | Optional, nice for shoulder-season planning |
| Holdout booking systems: Zion, Smokies, state parks | Per system | Each a separate fragile integration; only on demonstrated need |

## Bucket 3: not feasible or not smart

| Feature | Why |
|---|---|
| AllTrails route builder integration, automation, or scraping | No public API, actively enforced; the GPX handoff is the whole legitimate surface |
| Storing or mirroring AllTrails/WTA content | Link-only, always |
| Auto-booking permits | TOS, account-ban risk |
| CalTopo-clone drag interaction | Interop beats imitation; export to CalTopo instead |
| Programmatic Garmin push | Approval-gated developer API; manual GPX import costs two taps |
| Per-camp crowding from external sources | No public data at that granularity; the scan-derived demand signal is the substitute |
| National no-permit legality database | No structured source exists anywhere |
| Structured water-source status | Community knowledge; lives in linked WTA and NPS reports |

## Build order

1. P1 engine: extractor, Rainier graph, feature joins, solver, scorer, CLI request. 20-28 h.
2. GPX export immediately after. 1-2 h. This closes the full loop early, with CalTopo as the interim map and editor.
3. Map v0 display. 12-18 h.
4. Structured editing on the map. 8-12 h.
5. Bucket 2 items only when a specific planned trip demands them.
