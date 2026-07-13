# Experiments

## Dispersed itineraries, phase A (2026-07-13): PASS

Question: can camp candidates for permit-free areas be generated automatically? Method: named waters from OSM plus 3-way junctions, snapped to the shipped Weminuche graph with a 400 m gate, Dijkstra from the Needleton bridge. Graded pairs against published route knowledge: Twin Lakes auto 7.7 mi vs published 7.2 to 8.0; Columbine Lake 9.1 vs about 9 to 9.5; the Chicago Basin junction lands at 6.6 vs published 6 to 6.5. Verdict: auto candidate generation works inside the published bands. The snap gate is mandatory; an ungated run matched a distant Ruby Lake 3.4 km off the network. Far-basin lakes at 23 to 26 mi are real multi-day objectives, not errors. Phase B: synthetic always-open availability through the region overlay machinery and solver integration, then a second grading pass, with the AllTrails QA channel as the verification layer before anything ships to the app.
