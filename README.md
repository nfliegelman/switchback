# Switchback

Backcountry permit availability, trip planning, and effort math, automated. A switchback is the trail's answer to terrain too steep to climb in one go; this project does the same thing to backcountry itineraries.

## What it does today (v1.1.0)

**Permit availability finder (GUI).** Search any recreation.gov wilderness or backcountry permit, load every camp and zone in it, and pull availability across your date range on six threads. Each camp-night is classified (Reservable, Walk-up only, Full, Not released) and exported to a styled Excel workbook with filters, conditional formatting, and percent-remaining color scales. Windows: double-click `Switchback.bat`. Anywhere: `python switchback_gui.py`.

**CalTopo layer exporter.** `python caltopo_export.py <permit_id>` dumps every camp and trailhead in a permit as a GeoJSON file you can import straight into CalTopo: trailside camps, cross-country zones, alpine and winter sites color-coded, trailheads with parking flags. Validated on Mount Rainier (245 features) and built for any permit on the platform.

**Engine CLI (new at v1.1.0).** The data layer lives in a stdlib-only `switchback/` package with a CLI: `python -m switchback search "glacier wilderness"`, `python -m switchback availability 4675321 --start 2026-09-01 --end 2026-09-07 --filter "ELF -"`, `python -m switchback profile` to view the saved effort profile in `profile.json`, `python -m switchback extract 4675321 --slug glacier` to build the park datasets in `parks/`, `python -m switchback features glacier` to fill coordinates and tag lakes and elevations, `python -m switchback graph rainier --leg Longmire "Golden Lakes Camp"` to query the route graph, and `python -m switchback trips glacier --start 2026-09-01 --end 2026-09-22 --codes GAB,COS,GLF,ELF` to enumerate bookable itineraries within your limits. The GUI and the coming trip solver share this engine.

**Adventure mode demo (Glacier, Belly River).** `python belly_river_adventure.py` runs a live 3-night itinerary search for the Belly River drainage: a route graph with cited mileages and per-direction elevation, live availability for ten camps, a choose-your-own-adventure frontier walkthrough where every option shown is guaranteed to have at least one valid ending, and a batch mode that enumerates every bookable chain in the window. When advance inventory is sold out, planning mode relaxes availability so you can design a route for the walk-up line or cancellation watching.

## Requirements

Python 3.8+ with tkinter (included in the python.org Windows installer). The GUI auto-installs `customtkinter` and `openpyxl` on first run; the engine package, exporter, and demo use only the standard library.

## Where it's going

ROADMAP.md tracks the build toward v2.0.0, the full Switchback engine: enter a park, dates, party size, and your daily distance, elevation, and grade limits, and get ranked itineraries that are actually bookable right now, with loop, out-and-back, and lollipop trip shapes, an interactive frontier explorer, camp ratings, and GPX export for AllTrails, Garmin, Gaia, or CalTopo. BACKLOG.md holds everything beyond that. SPEC.md and SCOPE.md hold the design rationale. HANDOFF.md exists so any AI assistant can pick the project up cold.

## Versioning

v1.0.0 is this initial release. Each completed roadmap milestone bumps the minor version; completing all ten is v2.0.0. Patches are fixes.

## Data and respect

Unofficial and unaffiliated with recreation.gov, the National Park Service, CalTopo, or AllTrails. The tools read recreation.gov's public endpoints with modest, threaded, backoff-respecting requests, and they never book, hold, or reserve anything. Availability output is a snapshot: always confirm on recreation.gov before committing plans. No AllTrails or WTA content is stored, ever; those stay links.

Mileage sources for the Belly River graph are cited edge-by-edge inside `belly_river_graph.json`. Values flagged `est` are topographic estimates pending a proper elevation pass; trust the sourced numbers, verify the flagged ones.
