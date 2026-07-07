# CHANGELOG

Versioning per ROADMAP.md: milestones bump the minor version; v2.0.0 is the full Switchback engine.

## v1.0.1 (2026-07-07)

Docs only. Recorded round-one product decisions (local web app as target UI with FastAPI plus Leaflet architecture, on-demand plus per-trip watch operating model, no anchor trip) and added the Permit Difficulty Index to the backlog as DIRECTED.

## v1.0.0 (2026-07-07)

Initial public release.

- GUI availability finder (switchback_gui.py): search any recreation.gov wilderness permit, pull every camp's availability across a date range on 6 threads, classify each camp-night (Reservable, Walk-up only, Full, Not released), and export a styled, filterable Excel workbook.
- CalTopo exporter (caltopo_export.py): dump any permit's camps and trailheads as a CalTopo-importable GeoJSON layer, colored by camp type, parking flags on trailheads.
- Adventure mode demo (belly_river_adventure.py): live 3-night itinerary search for Glacier's Belly River area over a sourced route graph, with the interactive frontier walkthrough, endings-remaining counts, batch ranking, and a planning mode for when advance inventory is gone.
- Design docs: SPEC, SCOPE, ROADMAP, BACKLOG, HANDOFF, FUTURE (historical).
