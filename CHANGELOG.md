# CHANGELOG

Versioning per ROADMAP.md: milestones bump the minor version; v2.0.0 is the full Switchback engine.

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
