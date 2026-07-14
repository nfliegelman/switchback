# Experiments

## Dispersed itineraries, phase A (2026-07-13): PASS

Question: can camp candidates for permit-free areas be generated automatically? Method: named waters from OSM plus 3-way junctions, snapped to the shipped Weminuche graph with a 400 m gate, Dijkstra from the Needleton bridge. Graded pairs against published route knowledge: Twin Lakes auto 7.7 mi vs published 7.2 to 8.0; Columbine Lake 9.1 vs about 9 to 9.5; the Chicago Basin junction lands at 6.6 vs published 6 to 6.5. Verdict: auto candidate generation works inside the published bands. The snap gate is mandatory; an ungated run matched a distant Ruby Lake 3.4 km off the network. Far-basin lakes at 23 to 26 mi are real multi-day objectives, not errors. Phase B: synthetic always-open availability through the region overlay machinery and solver integration, then a second grading pass, with the AllTrails QA channel as the verification layer before anything ships to the app.

## Dispersed itineraries, phase B (2026-07-13): PASS

The solver ran end to end on a fully auto-generated dispersed park (parks/weminuchepilot.json, camps policy none): 14 bookable 2-night itineraries, ranked, with day-hike suggestions and the first-come honesty line intact. The number 2 itinerary reproduces the classic Chicago Basin trip exactly (Needleton 7.7 to Twin Lakes, 1.1 to the basin junction, 6.6 out). AllTrails oracle check: Windom Peak via Needle Creek measures 18.1 mi round trip, 9.05 one way including the summit spur; the auto graph's 7.7 plus the roughly 1.3 mile summit leg matches inside a tenth of a mile. Recorded limitations before app exposure: the candidate dedupe was over-aggressive (2 camps survived; widen the keep filter), gains are absent pending dem_trail, and junction camps need human-readable names. Next: scale the builder across areas and surface pilot parks in the app behind an experimental flag.

## Roadmap sweep (2026-07-13): items 1, 3, 5 outcomes

Item 1 shipped: build_pilot productized (widened dedupe, named junctions), Needle Creek regenerated at 10 camps and 30 edges yielding 168 itineraries across 24 routes; USGS EPQS returned nothing from the container so gains remain absent with the endpoint recorded for retry. Item 3: both WA hangers built on clean retries (transient mirror pathology confirmed), Glacier ELH to HEL corrected to 2.6 on oracle-consistent evidence, ELF to IPE still queued, South San Juan audit still queued. Item 5: the IPW dual merge is designed, not built: the schema is single permit_id, so the merge needs availability-layer list support with name-keyed division mapping across inventories. Item 4 (boundary source expansion) did not fit this session. Item 2 (calibration) and Telegram secrets remain the owner's.

## Session-floor sprint (2026-07-13): items 1 and 4 sealed, 2 and 3 deferred

Item 1: EPQS dead on a second independent attempt hours apart, upgraded from transient to blocked egress; alternates for next session: OpenTopoData, open-elevation, or Open-Meteo elevation. The pilot park is already listed by the local app with dispersed in its name; formal experimental flagging rides the gains fix. Item 4 closed three ways. South San Juan audit: 79 percent of nodes sit outside the boundary, so the small main network is pad-capture halo plus genuinely sparse interior mapping, not a pipeline bug; a clip-to-boundary display toggle is the recorded improvement, and the containment-fraction audit is now a standing QA tool. Conundrum: AllTrails anchors the springs at 17.1 mi round trip, 8.55 one way, plus 2762 ft; the trailhead coordinate is relocated to the road terminus and oracle-anchored, and with both datasets lacking the lower valley trail the straight is a confirmed absence, graduated to the GPX patch channel. ELF to IPE stays queued. Items 2 and 3 deferred whole rather than started and abandoned: each is a session of invasive work, and a clean pushed state beats a half-open surgery.

## Item 1 completion (2026-07-13): gains live, pilot flagged experimental

OpenTopoData NED 10m delivered 11 of 11 elevations where EPQS was blocked; edges carry gain_ab with est_gain flagged; the pilot park carries experimental true. The itinerary count fell from 168 to 14 under the real 4000 ft daily ceiling, which is the constraint engine telling the truth instead of counting gain-blind fantasies. Items 2 and 3 hand to the next session with the NPS boundary endpoint probe result recorded in HANDOFF.

## Long-trail corridor treatment (designed 2026-07-14, build pending)

The three corridor rows (Colorado Trail, CDT Colorado, PCT Washington) do not fit the polygon pipeline; this is their design, written before any build per the standing convention.

Boundary: the corridor polygon is a buffered centerline. Fetch the trail's OSM route relation, stitch member ways into one centerline (run _bridge_components on the stitched line first; relation gaps are the known failure), buffer 1.5 km per side, simplify at 150 m, store as ordinary boundary rings so rubber band green and amber logic works unchanged.

Trails: tile the corridor bbox chain into segments of about 0.3 degrees and run the existing mirror-walked fetch per tile against the disk cache, then dedupe elements by way id before the junction graph. Estimated tile counts: CT about 20, CDT-CO about 30, PCT-WA about 22. Each corridor is a session-scale build at current mirror behavior.

File size: cap area files near 1 MB by splitting a corridor into segment files if needed; the board loader is already lazy per area.

Owner question before building: buffer width. 1 km keeps files small and misses some side trails; 2 km roughly doubles capture and size. Default proposal is 1.5 km.

## Item 3 completion (2026-07-14): IPW dual-permit merge live

The schema blocker is gone: camps carry an optional inventories list of extra (permit_id, division_id) pairs, fetch_for_graph fetches every inventory and MAX-merges per date (a party books within one inventory, so sum would overstate). merge-inventory <slug> <permit_id> attaches a second permit by normalized division name; on Indian Peaks it matched all 17 zones of the 3-days-in-advance permit 4675319 exactly, zero Group false-matches, idempotent on re-run. Live proof July 15 to 17: Cascade Creek on July 16 had 5 spots open only on the 3-day channel, a night the full-season permit alone called closed. The shared report carries a NOTE naming the short-release channel. Enchantments (233273 plus daily 445863) reuses this machinery when its turn comes.

## v2.22 QA sweep results (2026-07-14)

ELF-IPE CONFIRMED at 9.8: AllTrails oracle triangulation (Ptarmigan Tunnel out and back 10.7 RT, trail 10235884, so 5.35 one way) plus the tunnel-to-Elizabeth-foot descent lands on 9.75 to 9.8. Closed. Neighbor discrepancy RECORDED, no change: graph ELF to COS is 6.0 (PNTA spur 3.4 plus junction-to-Cosley 2.6, both official planner figures), while the AllTrails community route to Cosley (10031955, 27.8 RT) implies 4.1; official planner figures win per the miles policy, community route likely drawn short or using the ford cutoff. Elk Range display QA: Maroon Zone to North Fork stored 7.19 vs 11.8 displayed geometry; edge flagged geometry_suspect, resolution rides the v2.23 dem_trail polyline pass which samples that line anyway. MB Areas Outside of Permit Zones semantics DECIDED: it is rec.gov's dispersed catch-all outside designated zones, stays included as real inventory, stays un-graphed (no single location exists to graph); future dispersed-zone modeling can adopt it. Enchantments is the second dual-inventory park: daily lottery 445863 matched all 5 zones of 233273 in one merge-inventory command.
