# HANDOFF.md

You are an AI picking up this project in a fresh conversation. Read this file first, then ROADMAP.md, then skim SPEC.md and SCOPE.md. Last updated 2026-07-07.

## What this project is

Switchback: a permit-aware backpacking trip finder built on recreation.gov data. The name is the trail's answer to terrain that is too steep for one day, which is what the solver does to itineraries. It started as a Tkinter GUI that dumps wilderness permit availability to Excel and is growing into: a constraint-based itinerary recommender (daily miles, gain, grade bounds), an interactive "adventure mode" frontier explorer, camp ratings, and GPX or CalTopo handoff. Owner: Noah, construction estimator, strong Python builder (has shipped multiple quant models with GitHub Actions and Pages dashboards), plans PNW and Rockies trips.

## Owner conventions. Non-negotiable. Violations are noticed.

1. NO em dashes or en dashes anywhere: chat, docs, code comments, filenames. Use commas, colons, periods, hyphens. Run a dash grep before every handback.
2. Surgical edits only. Never rewrite files wholesale when a targeted change works.
3. Every handback is the COMPLETE repo as a zip, with full files, nothing truncated.
4. Never return state JSON files (runtime or model state). Data snapshots and config are fine; the availability fetch stays live in scripts.
5. Style: quantified, evidence-based, concise. Tables for comparisons. Distinguish critical, moderate, and negligible differences. Give a recommendation, the strongest argument against it, and challenge the premise when warranted.
6. Reddit protocol for any community-sentiment claims: only with actual threads found, links provided, quotes cited, counts given. If none found, say so explicitly and label synthesis as synthesis.
7. Verify prices and market claims against real sources before repeating them.
8. At most one clarifying question per turn; answer what can be answered first.

## Repo inventory

- switchback_gui.py (was permit_finder_gui.py): original working GUI. Search permits, load divisions, fetch monthly availability (6 threads), classify (Reservable, Walk-up only, Full, Not released, Hidden), styled xlsx export. Renamed, window title updated, em dashes purged 2026-07-07; logic untouched.
- Switchback.bat (was Permit_Finder.bat): Windows launcher, updated for the rename.
- FUTURE.md: first roadmap. SUPERSEDED by ROADMAP.md and BACKLOG.md; kept for history and the monetization gates G1-G3.
- SPEC.md (was TRIPFINDER_SPEC.md): full engine design. Section 10 is adventure mode (virtual origin and sink, backward feasibility, endings_remaining, trip types, freshness re-check).
- SCOPE.md: three-bucket feature triage and the core principle: a route is an ordered camp list, geometry always derived.
- ROADMAP.md: the V1 build tracker, milestones M0-M10 with checkboxes. THE active plan.
- BACKLOG.md: categorized future features with the owner's direction per item.
- README.md: public-facing overview for GitHub, current capabilities and quickstart.
- CHANGELOG.md: version history; owner bumps versions per ROADMAP.md scheme.
- .gitignore: excludes permit_exports/, caches.
- caltopo_export.py: works today. Dumps any permit's camps and trailheads as CalTopo-importable GeoJSON, colored by type. Run: python caltopo_export.py <permit_id>.
- caltopo_Mount_Rainier_...geojson: generated sample, 245 features.
- belly_river_graph.json: hand-built Glacier Belly River graph. Every edge has miles, gain_ab, loss_ab, and a src citation; est flags mark topo estimates.
- belly_river_adventure.py: WORKING adventure-mode demo. Fetches live availability for 10 Belly River camps, runs the frontier walkthrough and batch enumeration, falls back to planning mode when advance inventory is nearly gone.

## Validated technical facts (probed live, dates noted)

- Rainier wilderness permit id 4675317: 190 divisions, 186 with real lat/long; entrances array has 60 trailheads with lat/long, has_parking, and division_ids linking trailheads to camps. (2026-07-07)
- Glacier wilderness permit id 4675321: 213 divisions, coordinates all 0,0 (fill from NPS GIS or OSM name-join); divisions include Administrative, Hitch Rail, and Spike variants that must be filtered; owner's example camps exist as ELF, ELH, POI, MOJ, MOL; trailheads BRE Belly River Trail and IPE Iceberg/Ptarmigan Trail exist. (2026-07-07)
- Availability endpoint: GET /api/permititinerary/{permit}/division/{division}/availability/month?month=M&year=Y&commercial=false. Sum remaining across payload.quota_type_maps; payload.bools is the fallback shape. remaining can be NEGATIVE (admin holds); clamp to 0. Browser User-Agent header required on all rec.gov calls.
- Search endpoint: /api/search?q=...&entity_type=permit. permitcontent: /api/permitcontent/{permit}.
- child_distances is empty for Rainier and Glacier; camp-to-camp mileage comes from official park tables or OSM plus DEM compute.
- Mileage sources used for Belly River: PNTA Glacier permit planner PDF (corridor mileages; ELF is 3.4 off the corridor at mile 6.1), enjoyyourparks Red Gap page (Many Glacier to ELF 9.8 mi, Redgap to ELF 4.6 mi and about 2,500 ft), roamingbearmedia (pass to Poia 5.7 mi, 1,754 ft), repicjourney (Poia TH to Poia 6.4 mi), Glacier Guides (TH to tunnel 10.6 mi round trip, 2,300 ft).
- OSM has the Wonderland Trail as a route relation and 75 camp_site features in the Rainier bbox. AllTrails has NO public API and enforces against scrapers (community scraper shut down Jan 2026); official AllTrails MCP exists in the owner's Claude for read-only lookups; content is link-only, never stored.
- Live scarcity snapshot 2026-07-07, party of 2, Jul 10 to Sep 22: exactly one advance-bookable 3-night Belly River chain (start Sept 22, Chief Mountain, GAB > GLF > GAB). STALE IMMEDIATELY; re-fetch, never quote this as current.

## Decisions log (dated 2026-07-07 unless noted)

- Trip types V1: loop, out_and_back, lollipop. Classifier on the closed walk: no repeated edges = loop; full retrace = out_and_back; repeats forming one contiguous stem = lollipop.
- Shuttle: PARKED by owner, future toggle.
- Same-trailhead return only in V1. Virtual origin over all entry trailheads defers the trailhead choice; virtual sink mirrors it.
- Backward feasibility always on: never show a frontier option without at least one valid completion; show endings_remaining per card.
- Batch top-N is the default entry point; adventure mode is the explore and modify layer.
- Ratings: lazy (rate only camps that surface), personal rating overrides computed prior, per-park percentile normalization. Priors currently hand-set in belly_river_graph.json, labeled DRAFT.
- Demand and crowding comes only from our own scan history (M8 logger); no external source exists.
- Walk-up inventory excluded from bookable results by default; planning mode relaxes availability for walk-up strategy.
- GPX handoff to AllTrails, Garmin, Gaia, CalTopo is the integration surface. CalTopo interop over imitation.
- 2026-07-07 (round-one product answers): day-to-day interface target is a LOCAL WEB APP, chosen by the owner's criterion of the most interactive, intuitive, visually appealing UI; terminal and the tkinter GUI are not the daily driver. Architecture note: browsers cannot call recreation.gov (CORS), so the web UI is a local FastAPI backend proxying the API plus a no-build-step Leaflet frontend in a single HTML file. Whether the web UI ships inside v2.0.0 or immediately after as v2.x is pending an explicit scope decision. Operating model: on-demand planning plus per-trip watch mode, no always-on scanner. No anchor trip; build in ROADMAP order. New DIRECTED backlog item: Permit Difficulty Index (BACKLOG.md category 4).
- 2026-07-07: App named SWITCHBACK. Version scheme: v1.0.0 = state at first GitHub upload; each completed roadmap milestone bumps the minor version; all ten = v2.0.0. The repo is now fully dash-clean including code, and every handback must keep it that way.

## Known issues

- Negative remaining renders as "-1 sites open" in belly_river_adventure.py card output; clamp in M6.
- GPX export not built yet; CalTopo GeoJSON lacks rating and availability properties until M5 and M8 data exists.
- est-flagged gains in belly_river_graph.json pending a DEM pass; ELF to ELH and ELH to HEL distances are estimates pending the park table.

## Next actions

1. Ask the owner for a real date window, party size, and trip type; rerun belly_river_adventure.py live if a trip is imminent.
2. Otherwise start ROADMAP.md at M0. Exception rule: pull M9 (watch mode plus Telegram) forward if the owner wants Glacier cancellation alerts now; ELF, COS, ELH are the camps to watch.
3. On every handback: dash grep, full repo zip, keep this file updated (decisions log and validated facts grow; snapshots get re-dated).
