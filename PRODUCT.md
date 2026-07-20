# PRODUCT.md

The product source of truth, v3.3.1 (2026-07-17). Two parts: Part 1 is
the Historical Context Addendum, which reconciles the brief against
thirty releases of decisions and carries the operative priority
adjustments; Part 2 is the owner's product-alignment brief itself,
dash-sanitized on ingest, otherwise verbatim. Where the parts disagree,
Part 1 wins; both yield to HANDOFF.md on technical facts.

# Part 1: Historical Context Addendum

Written v3.3.0 (2026-07-17)
by Claude at the owner's request, after verifying the brief's claims
against the repository. The instruction was candor over defense, and
that cuts both ways: the first correction below is to Claude, not to
the brief.

## 0. A correction to the reviewer, who is me

I verified the brief expecting to find invented file references.
Instead every file it cites exists: SPEC.md, SCOPE.md, FUTURE.md,
PARKS.md, web.py, web_index.html, board.py, history.py,
caltopo_export.py, scoring.json, parks/ratings.json. I have shipped
roughly thirty releases while never opening five of them. The brief
audited the whole repository; I had been operating on the slice of it
that recent sessions touched. Two consequences: the brief's repo
observations deserve default trust, and CLAUDE.md now instructs
sessions to survey the full tree before claiming anything is missing.
The one file the brief names that does not exist is parks/demand.json;
the loader hook for it exists in scoring.py and returns empty.

## 1. Goals, constraints, and decisions the brief missed

The owner cannot read code and operates from a phone most days. Every
consumer surface must survive that: double-click launchers, plain
language PRs, OWNER.md as the human task ledger. The brief's UX vision
is compatible but never states the constraint, and it is the binding
one.

The dash prohibition is an owner directive enforced by a release gate
since v2.6; the brief itself arrived full of em and en dashes and was
sanitized on ingest, the same treatment rec.gov permit names get.

Honesty conventions are already product features, not aspirations:
first-come nights print "no reservation system exists, availability
assumed, arrive early"; dispersed parks carry an experimental flag and
ship only after grading against a published oracle; sparse map fetches
carry an advisory floor note; every edge carries a src citation under a
tiered miles policy (official beats measured beats estimated). The
brief's confidence vocabulary in section 6.3 is a renaming and
formalization of an existing house value, which makes it cheap to
adopt.

Decisions the brief could not know because they postdate or sit outside
its snapshot: trip-shape multi-select shipped at the engine level in
v3.1.0 with the owner's default set (loop, out and back, basecamp);
corridor buffer is 1.0 km by owner decision; the calibration scaffold,
reaction ballots, trail-true gain grading (within one percent of a GPS
log), and toughest-stretch day profiles all exist and the owner
explicitly moved calibration reactions to future todo on 2026-07-17;
the AllTrails detail-approval gate finally cleared, so crowd-volume
data flows when wanted; CLAUDE.md and a session bootstrap landed
v3.2.2 for Claude Code.

One open data bug the brief must inherit: the Maroon Zone anchor node
sits at about 13,450 ft on the West Maroon ridge instead of the
camping valley. Any Elks-adjacent destination is disqualified from
"fully verified" status until it is fixed, and the v2.23 mileage
correction on that corridor is under re-audit for the same root cause.

## 2. Where the brief conflicts with prior decisions

Genuine conflicts are few. The brief parks "expanding map coverage
merely to increase an area count"; the last month did exactly that
wave, deliberately, and finished it (planned atlas rows are zero). No
conflict going forward, but the Archetype B expansion (Sierra
trailhead-quota parks) that I recommended to the owner two days ago
fails the brief's own decision filter and moves to Parked below. I
concur with the demotion; the filter is right and my earlier
recommendation predates it.

The brief's Gap 7 says the solver closes every trip at its starting
entrance. Verified true at solver.py line 155. This quietly corrects
some of our own recent vocabulary: the "mixed" routes in the
calibration ballots also return to their start, and the point_to_point
toggle shipped in v3.1.0 maps to a shape the enumerator never
produces. The shuttle option is now removed from the web UI (done in
v3.3.0) and point_to_point stays engine vocabulary only.

The brief treats profile.json's silent use as a defect; prior sessions
treated it as a feature for a single-owner tool. The brief is right for
the product Switchback is becoming: per-search visible constraints,
with the profile as defaults.

## 3. Looks like scope creep, was strategic

The 72-area atlas and three long-trail corridors look like breadth for
its own sake. They are the boundary rings that power the route
editor's inside/outside legality coloring the brief asks for in
section 12, and they are the permit-free fallback inventory that P1
route repair needs. The spend is sunk and frozen; the asset remains.

The dispersed pilots look experimental. They are the permit-free
fallback engine with the brief's honesty bar already built in: pilots
that fail their oracle get deleted whole (two of three did in v2.27).

The dual-permit merge looks niche. It is availability correctness for
Indian Peaks and the Enchantments, one of which the brief itself names
as a vertical-slice candidate; without it the product would call
bookable nights closed.

Trail-true gain grading and toughest-stretch look like polish. They
are the literal inputs to the brief's card requirements: hardest day,
tradeoff generation, and effort explanation.

The watch and demand-history plumbing looks like a competing alert
product. It is the substrate the brief's P1 complete-trip alerts and
saved-trip re-solving stand on, and the demand history is what will
price camp scarcity in explanations.

The .bat kit and OWNER.md look like non-product overhead. They are the
only test harness the owner can execute, which makes them the delivery
channel for the brief's manual UX test script.

## 4. Technical and data constraints Claude Code must understand

CLAUDE.md at the root is the operating manual and is updated as part of
this release; the load-bearing items: geometry polylines live in
canonical sorted-key orientation and must be re-oriented per edge
before any direction-dependent math; graph.find() returns None on
ambiguity, not just absence; solver.route_nodes() returns a set;
availability merges across dual inventories are MAX per date, never
sum; the engine package is stdlib-only by design; USGS EPQS is dead
from sandbox egress and the elevation order is OpenTopoData ned10m
then open-elevation; Overpass work uses short-leash timeouts with
maps.mail.ru as the reliable mirror and area builds batch three or
fewer; ArcGIS envelopes must be JSON objects and BLM's server cannot
be trusted with LIKE; state files (telegram.json, history.sqlite,
watch state, pdi, caches) never enter commits; tests run offline and
`python -m pytest -q` now runs all twelve suites; the SCOPE.md
principle that a route is an ordered camp list, never freehand
geometry, is why the brief's Edit-this-trip surface is cheap, and it
must not be violated by the editor work.

## 5. Preserve even while de-prioritized

The calibration scaffold, ballots, elevation profiles, and
toughest-stretch display (owner: future todo, infrastructure stays).
The three corridors and the atlas (frozen assets). The dispersed
machinery and its oracle gates. The AllTrails oracle channel, now that
its approval finally works. The watch, Telegram path, board cron, and
demand history. The GPX and CalTopo export path. The GUI, demoted per
the brief to admin utility but kept as the owner's permit-lookup and
spreadsheet tool. FUTURE.md's monetization gates, already archived in
place. HANDOFF.md's decision log in full; it is the project's memory
and the reason this addendum could be written.

## 6. Brief assumptions I believe are incorrect

Fewer than expected, and I say that having just been corrected myself.
parks/demand.json does not exist; the hook does. The preserved-assets
list slightly overstates present scoring inputs accordingly. The
capability audit line calling trip styles "one dropdown" was true of
the UI and understated the engine, where the multi-select shipped in
v3.1.0; the drift ran the direction opposite to implied. The estimate
of "roughly nine trip-ready graph datasets" is close; PARKS.md is
regenerated this release for the exact current count after the RMNP
buildout. The Rainier basecamp-domination example could not be cheaply
reproduced and is accepted as plausible rather than verified. Section
8's Campflare integration assumptions are strategy, not repo fact, and
are adopted as-is. Everything else the brief asserts about the
repository checked out.

## 7. Recommended priority adjustments

Adopt the brief's P0 list with these changes. Add to P0: the Maroon
anchor relocation and edge re-audit, because a data-integrity bug that
manufactures 13,000 ft phantom climbs disqualifies a marquee state
from every quality bar in section 16, and the fix is one focused
session. Add to P0, already done in this release: standard test
discovery, shuttle removal, and the documentation reset itself. Name
the vertical-slice destinations now rather than later; recommendation:
Mount Rainier (the brief's own worked example, mature graph), Rocky
Mountain NP (86 live camps after the v2.26 buildout, rich frontcountry
campgrounds on rec.gov, the owner's home state), and Lena (the
mixed-policy golden scenario in miniature). Indian Peaks is the strong
fourth when dual-permit correctness deserves a showcase. Keep
calibration reactions in P1 exactly where the brief puts scoring
calibration; the owner's future-todo decision and the brief agree, and
the 50-to-100 evaluation target already has its scaffold. Move
Archetype B (Sierra trailhead-quota architecture) from the old roadmap
horizon to Parked until P0 metrics are healthy; it is the definition
of coverage-before-product. Solitude modeling stays Parked per the
brief even though its data source is newly unlocked. Point-to-point
stays P2 and now tells the truth everywhere in the UI. Everything the
brief parks, stays parked, including the monetization gates that were
already parked twice.


# Part 2: The product-alignment brief


## Read this first

This document is the current product-direction source of truth for Switchback. It is written for Claude Fable / Claude Code to review alongside the repository before making additional product or architecture decisions.

**Do not rebuild Switchback from scratch.** The repository contains a real and useful backcountry itinerary engine. The task is to preserve the strongest technical work, stop scope creep, clarify the product contract, redesign the consumer workflow, and build one complete vertical slice that genuinely helps someone plan a trip.

Before changing code:

1. Read this entire file.
2. Read `HANDOFF.md`, `SPEC.md`, `SCOPE.md`, `ROADMAP.md`, `BACKLOG.md`, `README.md`, and the latest entries in `CHANGELOG.md`.
3. Inspect the current request flow in `switchback/web.py` and `switchback/web_index.html`.
4. Inspect the recommendation engine in `switchback/solver.py`, `switchback/scoring.py`, `switchback/graph.py`, and `switchback/report.py`.
5. Inspect the static board and route creator in `docs/board/index.html` and `switchback/board.py`.
6. Inspect current coverage in `PARKS.md`, `COLORADO.md`, `WASHINGTON.md`, `parks/atlas.json`, and `docs/areas/index.json`.
7. Produce a concise audit of what should be kept, changed, integrated, hidden, deferred, or removed from the primary experience **before implementing another broad feature wave**.

Every proposed task should be labeled one of:

- **P0 -  required for a genuinely useful trip-planning product**
- **P1 -  valuable immediately after the useful vertical slice works**
- **P2 -  strategically useful but not part of the first coherent product**
- **Parked -  do not build without new evidence**

---

# 1. Executive product decision

Switchback should not try to become a better Campflare, another AllTrails, another CalTopo, or a generic road-trip planner.

Its clearest market position is:

> **Switchback finds complete backpacking trips that a specific person can realistically take, based on dates, physical limits, logistics, preferences, permits, and current availability.**

A tighter user-facing version is:

> **Tell Switchback when you can go and what you can handle. It shows complete trips you can actually take.**

Campflare can be used in tandem. Campflare is strong at campsite and permit cancellation alerts. Switchback should own the planning and decision layer:

- Campflare: **“This campsite or permit became available.”**
- Switchback: **“This complete trip now works for you.”**

The product should ultimately sit between inventory sources and navigation tools:

```text
Recreation.gov / Campflare / park inventory
        ↓
  SWITCHBACK: search, solve, rank, repair,
  explain, complete the trip night by night
        ↓
 CalTopo / AllTrails / Gaia / Garmin / booking pages
```

Switchback does not need to outperform Campflare at alert infrastructure or outperform CalTopo at professional mapping. It needs to answer a planning question that those products do not answer well:

> “Given my actual trip constraints, what should I book?”

---

# 2. The primary goal

The intended core workflow is:

> **Pick a national park or outdoor area, dates, party size, and limits → Switchback provides complete trip options with an appropriate place to stay for every night, including relevant frontcountry and backcountry campsites.**

This needs one important clarification. “Frontcountry and backcountry for each night” can describe two related use cases, and the product should support both without conflating them.

## Use case A: a complete vacation shell

Example:

- Friday night: frontcountry campground near the trailhead.
- Saturday night: backcountry Camp A.
- Sunday night: backcountry Camp B.
- Monday night: optional frontcountry recovery campground.

This solves arrival timing, long drives, permit-night sequencing, and post-trip logistics.

## Use case B: a frontcountry basecamp trip

Example:

- Friday through Sunday: one frontcountry campground.
- Saturday: major day hike.
- Sunday: second day hike.

The current code has backcountry basecamp logic, but frontcountry campground basecamping is only a backlog idea. Both use cases should share a common `TripPlan` model, but they should be presented as distinct trip styles.

## Definition of the product contract

For every recommended trip, Switchback should account for:

1. Where the user starts and ends.
2. The trip’s exact dates or feasible start-date options.
3. Every overnight stay.
4. Whether each stay is frontcountry, backcountry, first-come, dispersed, walk-up, lodging, or not yet arranged.
5. Availability status and freshness for every reservable night.
6. The hiking route and daily effort.
7. Driving and trailhead logistics when known.
8. The booking action or next action for every night.
9. What is verified, inferred, experimental, or unknown.
10. Why the recommendation fits the user better than the alternatives.

A “trip” is not just a route polyline or ordered list of backcountry camp codes. It is a complete, understandable, actionable plan.

---

# 3. Candid assessment: is Switchback accomplishing that goal today?

## Overall answer

**Partially. The core backcountry engine proves the concept, but the consumer product does not yet fulfill the full goal.**

A reasonable estimate is:

- **Core backcountry engine required for the goal: 65-75% present.**
- **Consumer workflow required for a genuinely useful planning product: 25-35% present.**
- **Complete selected-area → constraints → every-night trip plan: approximately 35-45% complete.**

These are directional estimates, not code-coverage statistics.

## Capability audit

| Goal component | Current state | Assessment |
|---|---|---|
| Select a supported park/region | `/api/parks`, map park selector, CLI slugs | **Works** for trip-ready graph datasets |
| Select a broad mapped wilderness | Static board `explore areas` selector | **Map-only** for most areas; does not imply itinerary support |
| Enter dates | Web and desktop UI accept dates | **Works**, although the meaning of exact dates vs start-date window is not explained clearly |
| Enter number of nights | Web supports nights; desktop prompts separately | **Works** |
| Enter party size | Web supports party size | **Works** |
| Enter preferred daily mileage/gain | Stored in `profile.json` | **Not exposed in the primary web UI** |
| Enter hard maximum mileage/gain | Stored in `profile.json` | **Not exposed in the primary web UI** |
| Select trip styles | Engine supports toggles; web shows one dropdown | **Partial**; current UI and engine vocabulary drift |
| Generate backcountry camp sequences | `Solver` enumerates availability-valid sequences | **Works** on supported graphs |
| Validate availability by night | Recreation.gov permit inventory is fetched by camp/date | **Works** for modeled backcountry inventory |
| Include first-come/no-reservation nodes | Region overlays synthesize availability and label policy | **Works experimentally**, with honest capacity limitations |
| Add frontcountry arrival/recovery camps | Listed in `BACKLOG.md` only | **Not implemented** |
| Search frontcountry campground inventory | No campground endpoint or frontcountry data model | **Not implemented** |
| Return an explicit night-by-night trip timeline | Results list stops, dates, and day mileage | **Partial**; not a complete overnight itinerary object or clear timeline |
| Provide booking links per night | Watch alerts can carry links; trip results generally do not | **Not implemented in the recommendation UI** |
| Search across multiple destinations | User selects one park/region | **Not implemented** |
| Flexible-date discovery | Engine searches a start-date window within one area | **Partially works**, but is not presented as a first-class flexible-date experience |
| Repair an unavailable route | Solver can enumerate alternatives, but no repair workflow exists | **Engine ingredients exist; product feature not implemented** |
| Edit a recommended route on the map | Rubber-band builder exists separately in the board | **Not integrated with recommendations** |
| Explain why a route ranks highly | Scoring components exist internally | **Not surfaced meaningfully** |
| Show confidence/data quality | Some data carries flags and docs contain cautions | **Not surfaced consistently in UI** |
| Export GPX | Implemented | **Works** |
| Alert on a complete viable trip | Current watch is camp-night based | **Not implemented** |
| Plan a road-trip corridor around opportunities | Concept only | **Not implemented** |

## The most important product gaps

### Gap 1: the main form does not actually collect the core constraints

The local web UI’s header collects:

- park,
- area,
- start and end,
- nights,
- party,
- one trip-shape dropdown,
- internal camp codes,
- a `via` camp,
- Find Trips / Adventure.

The user’s preferred and maximum daily mileage and elevation gain are hidden in `profile.json`. The API request object in `switchback/web.py` also does not accept per-search effort preferences or maximums. The server silently uses the saved profile.

That directly conflicts with the desired promise: “dates and limits in → suitable trips out.”

### Gap 2: there is no complete-trip orchestration layer

The current solver returns a backcountry entrance, camp sequence, route type, day statistics, possible start dates, and route geometry. It does not construct a complete vacation shell containing arrival night, backcountry nights, departure/recovery night, driving segments, or booking tasks.

Frontcountry support remains a backlog line:

> “Frontcountry campground availability (sibling rec.gov endpoint) to support basecamp day-hiking trips.”

This must become an explicit model and orchestration layer rather than another isolated availability table.

### Gap 3: the recommendation results are technically legible but not decision-friendly

Current route cards emphasize:

- a decimal score such as `1.110`,
- an entrance name,
- a compressed camp sequence,
- miles per day,
- count of possible start dates,
- unstructured notes.

They do not prominently answer:

- Is the full trip bookable now?
- What happens each day and where do I sleep each night?
- How hard is the hardest day?
- What makes this recommendation fit me?
- What is the tradeoff?
- Which nights are reservable, first-come, or uncertain?
- What do I click to book it?
- How long is the drive?
- What is the data-confidence level?

### Gap 4: the route creator is disconnected from the recommendation workflow

The static board’s rubber-band route builder is a useful technical prototype, but it lives in an “explore areas” mode separate from the itinerary recommendations. It does not begin with a recommended route and let the user modify it. It lacks the product context needed to make editing satisfying:

- visible day boundaries,
- camp-night handles,
- per-day mileage and gain,
- availability consequences,
- undo,
- reset to recommendation,
- clear start/end states,
- route warnings,
- comparison to the original recommendation.

The route creator should become **“Edit this trip”**, not a disconnected drawing utility.

### Gap 5: coverage language can imply more trip-planning depth than exists

The repo has approximately:

- 80 atlas rows,
- 72 generated map-area files,
- roughly nine trip-ready graph datasets/regions in `PARKS.md`.

The wide map coverage is useful, but most mapped areas cannot yet generate complete bookable itineraries. The product must separate these levels visibly:

1. **Explore map only**
2. **Route drawing available**
3. **Planning data available**
4. **Availability-aware recommendations available**
5. **Fully verified trip-planning destination**

### Gap 6: ranking can surface a technically valid but contextually wrong trip style

The current board’s top Rainier results can rank three consecutive nights at the same camp because basecamping is allowed and the camp scores highly. This may be excellent when the user asks for a basecamp. It may feel absurd when the user expects a moving backpacking itinerary.

Trip style must be an explicit user choice or strong preference. Basecamp, moving route, loop, out-and-back, and point-to-point should not compete indiscriminately without the UI explaining the distinction.

### Gap 7: point-to-point/shuttle language exceeds current solver behavior

The current web UI includes a `shuttle` option. The solver always starts and returns to the same entrance, and its classifier does not currently construct a different exit trailhead. The engine mapping includes `point_to_point`, but the core enumeration closes every trip at the starting entrance.

Until point-to-point is truly implemented, the UI should not imply that it works. Either:

- hide the option, or
- implement an explicit exit-entrance dimension and shuttle/logistics model.

### Gap 8: the test suite is stronger than pytest currently reveals

Running `python -m pytest -q` discovers only one test. The repository’s test files mostly use executable `main()` functions rather than pytest test functions. Running every `tests/test_*.py` file manually succeeds and covers meaningful invariants, including solver parity, geometry, GPX, regions, web API, watch behavior, and scoring.

The logic has valuable tests, but continuous integration can create false confidence unless the suite is converted or wrapped so normal test discovery executes all invariants.

### Gap 9: documentation has drifted

Examples:

- `CHANGELOG.md` reaches v3.2.1.
- `README.md` opens with v3.0.0.
- `README.md` still contains “What’s inside (v2.0.0)” and “Where it’s going” language describing v2.1 as future.
- `ROADMAP.md` mixes completed v1/v2 history with a short v3 horizon.
- `FUTURE.md`, `BACKLOG.md`, and `ROADMAP.md` overlap.

This makes scope creep easier because there is no single current product roadmap organized by outcomes.

---

# 4. What must be preserved

Do not discard the current engine. The following are real assets.

## 4.1 Availability data layer

Relevant files:

- `switchback/api.py`
- `switchback/extract.py`
- `switchback/solver.py` availability helpers
- `switchback/history.py`
- `switchback/watch.py`

Valuable capabilities:

- Recreation.gov permit search and division extraction.
- Date-level remaining inventory.
- Walk-up, hidden, full, reservable, and not-released classification.
- Multi-inventory merging.
- Scan history.
- Flicker-filtered alert state.

## 4.2 Route graph and itinerary solver

Relevant files:

- `switchback/graph.py`
- `switchback/solver.py`
- `parks/edges/*`
- region datasets such as Lena and Teton Crest.

Valuable capabilities:

- Daily mileage/gain feasibility.
- Pass-through routing between camps.
- Availability-valid multi-night camp sequences.
- Basecamp self-loops.
- Start-date window enumeration.
- Route-shape classification.
- `endings()` completion counts for interactive planning.

## 4.3 Geometry and export

Relevant files:

- `switchback/geometry.py`
- `switchback/gpx.py`
- `caltopo_export.py`
- `docs/areas/*.json`

Valuable capabilities:

- Trail-following geometry where mapped.
- Honest straight-line fallback.
- GPX export by day.
- OSM / USGS / USFS trail data.
- Boundary-aware trail networks.

## 4.4 Scoring ingredients

Relevant files:

- `switchback/scoring.py`
- `scoring.json`
- `parks/ratings.json`
- `parks/demand.json`

Valuable capabilities:

- Preferred-effort fit.
- Camp-quality priors.
- Lake-night signal.
- Personal ratings.
- Demand-history hook.
- Basecamp day-hike suggestions.

The scoring model needs calibration and better explanation, not replacement.

## 4.5 Region and permit-policy modeling

Relevant files:

- `switchback/areas.py`
- `switchback/dispersed.py`
- `switchback/corridor.py`
- `parks/lena.json`
- `parks/tetoncrest.json`

Valuable capabilities:

- Cross-boundary route graphs.
- Mixed permit and no-reservation nights.
- Synthetic availability with honest policy labels.
- Experimental dispersed-camp candidates.
- Long-trail corridors.

## 4.6 Existing UI prototypes

Relevant files:

- `switchback/web_index.html`
- `docs/board/index.html`
- `switchback_gui.py`

These should be treated as working prototypes and behavior references, not final design. Preserve their working interactions while replacing the information architecture.

---

# 5. Scope reset

## P0: the coherent product

P0 is the smallest version that would genuinely help plan a trip.

1. A clear trip-request form with actual constraints.
2. A request API that accepts those constraints per search.
3. A complete `TripPlan` response with every night accounted for.
4. Ranked, explainable recommendation cards.
5. A night-by-night trip detail view.
6. Frontcountry arrival/recovery and frontcountry-basecamp modeling for a small number of fully supported destinations.
7. Availability status, freshness, confidence, and booking action for each stay.
8. An integrated map that displays a selected recommendation.
9. “Edit this trip” using the existing route-network work.
10. Honest coverage levels and zero-results guidance.
11. Normal test discovery and a small golden-scenario suite.
12. One source-of-truth product document and current roadmap.

## P1: high-value follow-on

1. Flexible-date search across multiple supported destinations.
2. Route repair when the ideal itinerary is unavailable.
3. Permit-free and cross-boundary fallbacks.
4. Saved trip profiles.
5. Saved searches and complete-trip alerts.
6. Campflare handoff / watch links.
7. Drive-time filtering.
8. Conditions and season filters.
9. Recommendation feedback and scoring calibration.

## P2: strategic expansion

1. Road-corridor search.
2. Multi-stop outdoor vacations.
3. Group voting and shared planning.
4. More complete dispersed-trip generation.
5. Point-to-point and shuttle logistics.
6. Long-trail section planning.
7. Broader frontcountry inventory coverage.
8. Commercial subscription/one-time-trip features.

## Parked

Do not prioritize these until the P0 workflow is demonstrably useful:

- Replacing Garmin, Gaia, CalTopo, onX, or AllTrails navigation.
- Generic road-trip POIs, restaurants, hotels, attractions, or scenic-stop planning.
- Expanding map coverage merely to increase an area count.
- A generic AI chatbot as the primary interface.
- More alert channels before trip-level alert logic exists.
- Advanced solitude modeling before recommendation quality is calibrated.
- More experimental data layers that do not improve the complete trip workflow.
- Deep desktop/Tkinter product work; keep it as a utility or admin surface.

---

# 6. The product’s core data model

A new orchestration model should sit above the existing `Solver`. The solver remains responsible for feasible backcountry camp sequences. The orchestration layer turns a feasible route into a complete trip.

## 6.1 TripRequest

Suggested conceptual schema:

```json
{
  "destination": {
  "mode": "selected_area",
  "area_slugs": ["rainier"],
  "origin": "Seattle, WA",
  "max_drive_hours": 4.0,
  "road_corridor": null
  },
  "dates": {
  "mode": "flexible_start",
  "earliest_start": "2026-08-14",
  "latest_start": "2026-08-21",
  "backcountry_nights": 2,
  "arrival_frontcountry_nights": 1,
  "recovery_frontcountry_nights": 0
  },
  "party": {
  "size": 2,
  "dogs": 0
  },
  "effort": {
  "preferred_daily_miles": 8.0,
  "maximum_daily_miles": 11.0,
  "preferred_daily_gain_ft": 1800,
  "maximum_daily_gain_ft": 3000,
  "maximum_hard_days": 1
  },
  "style": {
  "moving_trip": true,
  "basecamp": true,
  "loop": true,
  "out_and_back": true,
  "point_to_point": false,
  "frontcountry_basecamp": false
  },
  "preferences": {
  "lakes": "high",
  "alpine_scenery": "high",
  "solitude": "medium",
  "swimming": "nice_to_have",
  "avoid_repeated_camp_nights": true
  },
  "permit_strategy": {
  "reservable": true,
  "walk_up": false,
  "first_come": true,
  "dispersed": false,
  "campflare_handoff": true
  },
  "logistics": {
  "one_car": true,
  "shuttle_available": false,
  "late_arrival": true
  }
}
```

P0 does not need every field, but the schema should leave room for the complete product. The first implementation should include:

- selected area,
- exact or flexible start dates,
- backcountry nights,
- optional arrival/recovery night,
- party size,
- preferred and maximum mileage,
- preferred and maximum gain,
- trip-style toggles,
- first-come tolerance,
- basic scenic priorities.

## 6.2 TripPlan

Suggested conceptual schema:

```json
{
  "id": "rainier-2026-08-15-mystic-dick",
  "title": "Mystic Lake Northern Loop Sampler",
  "status": "bookable_now",
  "confidence": "verified",
  "fit": {
  "overall": 0.87,
  "effort": 0.92,
  "scenery": 0.84,
  "availability": 1.0,
  "logistics": 0.74
  },
  "why_it_matches": [
  "No hiking day exceeds 10.2 miles",
  "Two lake-adjacent nights",
  "Available for both requested start dates"
  ],
  "tradeoffs": [
  "The final day has 2,850 feet of gain",
  "Trailhead parking may fill early"
  ],
  "trip_dates": {
  "start": "2026-08-15",
  "end": "2026-08-18",
  "alternate_starts": ["2026-08-16"]
  },
  "nights": [
  {
  "night_number": 0,
  "date": "2026-08-15",
  "stay_type": "frontcountry_campground",
  "name": "White River Campground",
  "availability": "unknown_or_first_come",
  "booking_url": null,
  "confidence": "official_policy_verified"
  },
  {
  "night_number": 1,
  "date": "2026-08-16",
  "stay_type": "backcountry_camp",
  "name": "Mystic Camp",
  "availability": "reservable",
  "remaining": 2,
  "booking_url": "...",
  "confidence": "live_inventory"
  },
  {
  "night_number": 2,
  "date": "2026-08-17",
  "stay_type": "backcountry_camp",
  "name": "Dick Creek Camp",
  "availability": "reservable",
  "remaining": 2,
  "booking_url": "...",
  "confidence": "live_inventory"
  }
  ],
  "days": [
  {
  "day_number": 1,
  "from": "White River Trailhead",
  "to": "Mystic Camp",
  "miles": 9.8,
  "gain_ft": 1983,
  "route_geometry": []
  }
  ],
  "totals": {
  "trail_miles": 27.4,
  "total_gain_ft": 6200,
  "hardest_day_miles": 10.2,
  "hardest_day_gain_ft": 2850,
  "drive_hours_each_way": 2.1
  },
  "actions": [
  {"type": "book_permit", "label": "Book backcountry permit", "url": "..."},
  {"type": "watch_campflare", "label": "Watch missing night on Campflare", "url": "..."},
  {"type": "export_gpx", "label": "Export GPX"}
  ]
}
```

The exact implementation can differ. The critical requirement is that the response contains a complete, explicit trip, not just solver internals.

## 6.3 Confidence vocabulary

Every result should distinguish:

- **Live inventory:** directly fetched and recent.
- **Official policy verified:** official source says first-come/no reservation, but capacity is not known.
- **Curated:** manually assembled from credible sources.
- **Derived:** calculated from route graph/geometry.
- **Experimental:** dispersed candidate or uncertain geometry.
- **Unknown:** user must verify.

A result should never imply that a first-come or dispersed night is guaranteed.

---

# 7. Search and recommendation pipeline

The intended orchestration flow is:

```text
1. Normalize user request
2. Resolve eligible destination(s)
3. Load only destinations with the required support level
4. Fetch availability for the necessary date range
5. Run existing backcountry solver with request-specific constraints
6. Build frontcountry arrival/recovery or basecamp options
7. Construct complete TripPlan objects
8. Apply hard filters
9. Score by user fit
10. Deduplicate meaningfully similar trips
11. Generate plain-language explanations and tradeoffs
12. Return exact-fit, stretch, and fallback groups
```

## Result groups

Recommendations should be grouped instead of presented as one undifferentiated score list.

### Exact matches

Meet every hard constraint and preferred trip style.

### Good alternatives

Meet every hard constraint but have a meaningful tradeoff, such as less lake access, longer drive, or first-come night.

### Stretch options

Exceed one clearly identified preference but never exceed a hard maximum unless the user explicitly chooses to view them.

### Permit-free or Campflare fallback

Not fully bookable now, but has one of:

- a similar permit-free route,
- a modified itinerary,
- a frontcountry basecamp version,
- a Campflare watch action for the missing night.

---

# 8. Campflare partnership model

Assume Campflare can be used alongside Switchback.

## What Switchback should not duplicate unnecessarily

- Generic campground cancellation alerts.
- Broad free campsite availability scanning as the headline product.
- Campflare’s notification delivery and existing user familiarity.

## What Switchback should add

### A. Campflare handoff

When a trip is almost viable, present:

> “This trip works except for Upper Lena on August 17. Watch that night on Campflare.”

Where possible, deep-link to the relevant permit/camp/date. Where a precise deep link is unavailable, show exact instructions and identifiers.

### B. Trip-level saved state

Switchback should remember the entire desired trip profile:

- dates,
- acceptable alternate dates,
- party size,
- limits,
- preferred area,
- acceptable substitute camps,
- route styles.

Campflare can alert that inventory changed. Switchback can re-solve and tell the user whether the **complete trip** now works.

### C. Honest integration boundaries

Do not depend on unofficial scraping or private APIs without permission. Treat Campflare as:

- an outbound complementary tool initially,
- a possible licensed API or referral partner later,
- not a hard runtime dependency for the first useful Switchback release.

---

# 9. UI strategy

UI quality is not cosmetic for this product. The user is making a complicated, high-friction outdoor decision. The interface must reduce uncertainty, make tradeoffs pleasurable to explore, and give the user confidence that the recommendation is real.

The current interface should be reorganized into three primary surfaces:

1. **Describe the trip**
2. **Browse recommendations**
3. **Inspect and edit one trip**

Do not place all functionality in a single toolbar above a map.

---

# 10. Surface 1: constraint entry

## Current problem

The current local web interface compresses many controls into one header row. Important user constraints are missing, while expert/internal fields such as camp codes and `via` are prominent.

This creates three problems:

- The form does not match the product promise.
- New users do not know which fields matter.
- The map appears before the product has helped make a decision.

## Recommended structure

Use a focused form, panel, or short stepper. It should feel closer to booking a trip than configuring a graph algorithm.

### Section 1: Where do you want to go?

Controls:

- `A specific park or area`
- `Anywhere within X hours of me` -  P1
- searchable destination selector,
- support badge such as `Full trip planning`, `Route planning`, or `Map only`.

P0 can default to a specific supported park/region.

### Section 2: When can you go?

Controls:

- exact dates,
- flexible start-date range,
- number of backcountry nights,
- optional arrival-night toggle,
- optional recovery-night toggle.

Use plain language:

- “I can start any day from August 14-21.”
- “I want 2 nights in the backcountry.”
- “Add a campground near the trailhead the night before.”

### Section 3: What can your group handle?

Show preferred and hard maximum separately.

Example controls:

```text
Comfortable day   8 miles  1,800 ft gain
Absolute maximum   11 miles  3,000 ft gain
```

Provide presets:

- Easy
- Moderate
- Challenging
- Custom

The saved `profile.json` values can become defaults, but the user must be able to see and change them per search.

### Section 4: What kind of trip sounds good?

Use multi-select cards or chips, not a single technical dropdown.

- Moving camp each night
- Basecamp with day hikes
- Loop
- Out and back
- Point to point -  hide until implemented
- Frontcountry basecamp

Explain the choices briefly.

### Section 5: Priorities

Keep this lightweight in P0:

- Lakes
- Alpine scenery
- Solitude
- Swimming
- Easier logistics
- Permit-free preferred

Use three-state preference chips such as `Important`, `Nice`, `No preference`, rather than forcing exact numerical weights.

### Advanced options

Collapse these by default:

- specific camp codes,
- must pass through a camp,
- walk-up policy,
- maximum stay,
- include experimental routes,
- route-data confidence threshold.

## Interaction and satisfaction requirements

- A sticky summary should update as the user changes constraints.
- Defaults should allow a useful search with fewer than five decisions.
- The primary CTA should say **Find trips**, not expose implementation language.
- Invalid combinations should be explained before the search runs.
- The form should show which destinations support the selected features.
- Searches should display a staged progress state: checking destinations → checking nights → building routes → ranking options.
- Returning users should be able to start from a saved profile.

## Suggested desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ SWITCHBACK              Saved trips Profile   │
├───────────────────────────────┬──────────────────────────────────────────┤
│ Plan a trip       │              │
│           │   Quiet destination preview    │
│ WHERE         │   or helpful illustration/map    │
│ [ Mount Rainier NP    ▾ ] │              │
│ Full trip planning supported │              │
│           │              │
│ WHEN          │              │
│ [ Aug 14 ] to [ Aug 21 ]  │              │
│ [2] backcountry nights    │              │
│ ☑ Add arrival campground   │              │
│           │              │
│ DAILY EFFORT      │              │
│ Comfortable  [8 mi] [1800 ft]│              │
│ Maximum   [11 mi] [3000 ft]│              │
│           │              │
│ TRIP STYLE        │              │
│ [Moving] [Basecamp] [Loop]  │              │
│           │              │
│ PRIORITIES        │              │
│ [Lakes ★] [Solitude] [Easy logistics]             │
│           │              │
│ [ Find trips ]      │              │
└───────────────────────────────┴──────────────────────────────────────────┘
```

On mobile, this becomes a single-column form with a sticky bottom CTA.

---

# 11. Surface 2: recommendation browsing

## Current problem

The current result list is a technical report translated into cards. The user must interpret codes, raw score decimals, route types, and mileage strings.

## Recommended layout

Use a synchronized card list and map, but make the recommendations primary. The map supports comparison; it should not consume the entire decision experience.

### Each recommendation card should show

1. Human-readable trip name.
2. Clear status:
  - Bookable now
  - Mostly bookable
  - First-come component
  - Permit-free
  - Watch one missing night
3. Exact dates and number of nights.
4. Trip style.
5. Total trail mileage.
6. Hardest day mileage and gain.
7. Drive time when available.
8. Small night-by-night timeline.
9. Two or three reasons it matches.
10. One or two explicit tradeoffs.
11. Confidence/freshness.
12. Actions:
 - View trip
 - Book / see booking steps
 - Edit route
 - Save
 - Watch on Campflare

### Do not show the raw decimal score as the main information

The score can remain internal. User-facing fit can be presented as:

- Great fit
- Good fit
- Stretch

Or as explained dimensions:

```text
Effort fit  Excellent
Availability  Fully bookable
Scenery   Strong lake emphasis
Logistics   Moderate drive
```

### Suggested card

```text
┌────────────────────────────────────────────────────────────┐
│ GREAT FIT            BOOKABLE NOW   │
│ Upper Lena Basecamp              │
│ Aug 16-18 • 2 backcountry nights • Out and back    │
│                    │
│ Fri  Lower Lena / FCFS arrival option         │
│ Sat  Upper Lena • reservable           │
│ Sun  Upper Lena • reservable           │
│                    │
│ 13.4 trail mi • hardest day 6.7 mi / 3,900 ft      │
│                    │
│ Why it fits: lake destination • no day over 7 miles    │
│ Tradeoff: first day is steep • Lower Lena is not guaranteed│
│                    │
│ [View trip] [Edit] [Booking steps]         │
└────────────────────────────────────────────────────────────┘
```

### Result grouping

Tabs or sections:

- Best matches
- Easier
- Permit-free
- Watchlist opportunities

### Zero-results state

“No routes” is not enough. Offer a repair ladder:

1. Shift dates by 1-3 days.
2. Add one first-come night.
3. Allow a basecamp.
4. Raise max mileage slightly.
5. Show a nearby permit-free alternative.
6. Create a Campflare watch for the missing night.

The system should quantify each relaxation:

> “Adding 0.8 miles to your maximum produces four fully bookable trips.”

That is a high-value use of the solver.

---

# 12. Surface 3: trip detail and route editor

## Product principle

The map editor should begin with a valid recommended trip. The user modifies something concrete rather than drawing from nothing.

## Trip-detail layout

Desktop:

```text
┌──────────────────────────────┬───────────────────────────────────────────┐
│ Mystic Lake Sampler    │               │
│ Bookable now       │       MAP         │
│          │               │
│ Day 0 • Arrival      │   route colored by day      │
│ White River Campground   │   camps labeled         │
│ First-come / verify    │   selected day highlighted      │
│          │               │
│ Day 1 • 9.8 mi • +1,983 ft │               │
│ Trailhead → Mystic Camp  │               │
│ [Change camp]      │               │
│          │               │
│ Day 2 • 7.2 mi day hike  │               │
│ Mystic basecamp      │               │
│ [Change day hike]    │               │
│          │               │
│ Booking checklist    │               │
│ ✓ Backcountry nights open  │               │
│ ! Arrival campground FCFS  │               │
│          │               │
│ [Export GPX] [Save] [Book] │               │
└──────────────────────────────┴───────────────────────────────────────────┘
```

## Route editor requirements

The existing rubber-band route builder is a starting point. The integrated editor should add:

### Essential P0 behavior

- Start with the selected recommendation drawn.
- Color each hiking day separately.
- Show camp-night markers and labels.
- Selecting a day highlights its route and metrics.
- Change a camp for a specific night.
- Add or remove a layover.
- Reverse a route where valid.
- Recalculate mileage, gain, availability, and fit immediately.
- Show whether the modified plan remains fully feasible.
- Undo last change.
- Reset to original recommendation.
- Export the edited route.

### Rubber-band interaction improvements

- Make snap targets visible when editing starts.
- Increase clarity around the current anchor and next legal targets.
- Preview the route and resulting day mileage before committing.
- Show a clear finish/cancel state.
- Do not disable map dragging without a very visible mode indicator.
- Distinguish inside-boundary and outside-boundary trail segments, but explain why it matters.
- Show unavailable camp targets as disabled rather than silently excluding them.
- Provide mobile-friendly tap selection; hover-only behavior is insufficient.
- Add a route-edit history.

### Important architectural choice

The general area route creator and recommendation editor should share routing code, but the recommendation editor should be the primary consumer product. “Explore and draw any route” can remain an advanced mode.

---

# 13. Frontcountry implementation plan

Frontcountry support is central to the stated product goal, but it should be added narrowly and credibly.

## 13.1 Model first

Create a common stay model:

```text
Stay
- id
- name
- date
- stay_type
- coordinates
- reservation_policy
- availability_status
- remaining_capacity
- booking_url
- source
- fetched_at
- confidence
- notes
```

`stay_type` should include:

- `backcountry_camp`
- `frontcountry_campground`
- `walkup_camp`
- `first_come_camp`
- `dispersed_candidate`
- `lodging` -  later
- `unplanned` -  explicit gap, never hidden

## 13.2 P0 source strategy

Do not start with universal campground support. Fully support frontcountry planning for the initial vertical-slice destinations.

For each selected destination, curate:

- appropriate arrival campgrounds,
- approximate drive time to trailheads,
- reservation policy,
- booking page,
- seasonal limitations,
- whether live availability can be fetched reliably.

Recommended initial destinations should come from existing high-confidence graph data and actual user relevance. Candidates:

- Mount Rainier
- Lena / Olympic gateway
- Indian Peaks or Rocky Mountain NP

Use two or three destinations for the first end-to-end slice, not all mapped areas.

## 13.3 Availability phases

### Phase A

Show curated official frontcountry options and policy. Live availability is optional but status must be honest:

- “Reservation required -  check availability”
- “First-come -  capacity not guaranteed”
- “Seasonal closure -  unavailable”

### Phase B

Add live Recreation.gov campground inventory where supported.

### Phase C

Rank multiple frontcountry options by:

- distance to trailhead,
- availability,
- arrival-time suitability,
- amenities,
- price,
- match with the selected backcountry route.

## 13.4 Complete-night invariant

A recommended `TripPlan` must pass this invariant:

> Every calendar night between trip start and trip end has exactly one stay record, or an explicit `unplanned` gap with a warning.

No hidden overnight gaps.

---

# 14. Recommendation scoring changes

The current scorer is a useful cold-start model. It needs to become request-aware and explainable.

## P0 changes

### A. Separate hard constraints from preferences

Hard constraints:

- maximum mileage,
- maximum gain,
- party capacity,
- required availability,
- allowed policies,
- route style if required.

Preferences:

- comfortable mileage/gain,
- lakes,
- scenery,
- solitude,
- fewer logistics,
- moving vs basecamp.

Never let a high camp score overcome a hard-limit violation.

### B. Make trip style part of scoring

A three-night stay at one camp should rank highly only when basecamp is selected or welcomed. If the user asks for a moving trip, repeated camp nights should be penalized or filtered.

### C. Return score components

The API should include enough data to create explanations:

```json
{
  "fit_components": {
  "effort": 0.91,
  "camp_quality": 0.78,
  "scenery": 0.85,
  "availability": 1.0,
  "logistics": 0.63,
  "trip_style": 0.95
  }
}
```

### D. Add tradeoff generation

Tradeoffs can initially be rule-based:

- hardest day near the maximum,
- first-come night,
- long drive,
- uncertain geometry,
- repeated camp night,
- no lake nights,
- one missing live availability source.

### E. Calibrate with human evaluations

Create a small evaluation interface or JSON fixture. For each recommended trip, record:

- would take,
- too hard,
- too easy,
- bad route shape,
- unattractive camps,
- too much driving,
- permit process too uncertain,
- great recommendation.

The first target should be **50-100 evaluated recommendations**, not a perfect machine-learning model.

---

# 15. Recommended roadmap

The roadmap should be organized around outcomes, not feature accumulation or version-number archaeology.

Time estimates below are rough single-developer effort ranges and should be adjusted after Claude audits dependencies.

## Phase 0 -  product and documentation reset

**Estimated effort: 1-3 focused days**

### Goals

- Establish one current product source of truth.
- Remove ambiguity about the P0 product.
- Prevent new scope from entering without classification.

### Tasks

1. Add or adopt `PRODUCT.md` using this brief as the basis.
2. Rewrite `ROADMAP.md` around P0/P1/P2 outcomes.
3. Convert shipped historical roadmap material into changelog/history references.
4. Update `README.md` to current version and current workflow.
5. Triage every open `BACKLOG.md` item.
6. Mark every coverage surface as map-only, routable, recommendations, or verified.
7. Fix test discovery so one standard command runs all invariant tests.
8. Document known product gaps explicitly.

### Done criteria

- A new contributor can identify the current product goal and top five tasks in under five minutes.
- No active roadmap document describes already-shipped v2 work as the current future.
- `pytest` or one documented standard test command runs the full suite.

## Phase 1 -  request and result contract

**Estimated effort: 3-7 focused days**

### Goals

- Make the backend API match the product promise.
- Preserve solver internals while introducing `TripRequest` and `TripPlan`.

### Tasks

1. Expand request schema to include preferred and maximum effort.
2. Add explicit trip-style toggles.
3. Hide point-to-point until supported.
4. Create the complete trip response model.
5. Add per-night availability details and booking actions.
6. Add score components and explanations.
7. Add coverage/confidence metadata.
8. Create an orchestration module, likely separate from `solver.py`.

Suggested new module names:

- `switchback/planner.py`
- `switchback/tripplan.py`
- `switchback/frontcountry.py`

Do not overload `solver.py` with frontcountry and UI presentation concerns.

### Done criteria

An API test can submit:

> Rainier, August 14-21, two backcountry nights, party two, comfortable eight miles/1,800 feet, maximum eleven miles/3,000 feet, loop or basecamp allowed

and receive complete, structured trip plans with explicit nights, days, fit explanations, and no hidden use of `profile.json` values.

## Phase 2 -  coherent UI vertical slice

**Estimated effort: 1-3 weeks depending on frontend approach**

### Goals

- Replace the toolbar-first interface with the three-surface workflow.
- Make two or three destinations genuinely useful.

### Tasks

1. Build the constraint-entry experience.
2. Build recommendation cards and result grouping.
3. Build trip detail with night-by-night timeline.
4. Synchronize route selection with the map.
5. Add exact booking steps.
6. Add zero-result repair suggestions.
7. Make the experience responsive and mobile-friendly.
8. Keep advanced fields behind progressive disclosure.

### Done criteria

A new user can:

1. Select a supported destination.
2. Enter dates and real effort constraints.
3. Understand the top three options without knowing camp codes.
4. See where they sleep every night.
5. Understand availability and uncertainty.
6. open booking steps or export a GPX.

Target usability metrics:

- Form completion: **under 90 seconds** for a first-time user.
- Time to understand top result: **under 30 seconds**.
- Time from opening app to actionable plan: **under 3 minutes**, excluding network delays.
- No more than **five required decisions** before the first search.

## Phase 3 -  frontcountry and integrated editing

**Estimated effort: 1-3 weeks for narrow destination coverage**

### Goals

- Fulfill the complete-night promise.
- Convert the route creator into an itinerary editor.

### Tasks

1. Add curated frontcountry data for initial destinations.
2. Add optional arrival/recovery nights.
3. Add frontcountry-basecamp trip type.
4. Enforce the complete-night invariant.
5. Start the route editor from a selected recommendation.
6. Add camp replacement, layover, reverse, undo, and reset.
7. Recalculate fit and availability after edits.
8. Export edited route GPX.

### Done criteria

A recommended trip can contain frontcountry and backcountry stays, every night is accounted for, and the user can change one backcountry night without leaving the trip-detail experience.

## Phase 4 -  cross-destination discovery and route repair

**Estimated effort: 2-5 weeks after the vertical slice is stable**

### Goals

- Deliver the strongest market differentiation.

### Tasks

1. Search across supported destinations.
2. Add origin and maximum drive time.
3. Add flexible-date portfolio search.
4. Build route-repair explanations.
5. Add permit-free and cross-boundary fallback ranking.
6. Save trip profiles.
7. Add complete-trip alerts.
8. Add Campflare handoff.

### Done criteria

The user can ask:

> “Find me any two-night backpacking trip within four hours of Denver next weekend, under ten miles and 2,500 feet per day.”

and receive complete, ranked, actionable plans.

## Phase 5 -  road-corridor planning and expansion

Only after P0/P1 metrics are healthy.

Potential tasks:

- Search near a driving corridor.
- Add multi-stop outdoor vacations.
- Add fully implemented point-to-point/shuttle trips.
- Expand live frontcountry inventory.
- Expand high-confidence dispersed trips.
- Add group collaboration.
- Monetization experiments.

---

# 16. Definition of a genuinely useful v1

Switchback is ready for real trip-planning use when all of the following are true.

## Product

- At least **three destinations** have fully verified end-to-end planning.
- The user can enter per-search preferred and maximum effort.
- The user can select exact or flexible dates.
- The user can choose moving, basecamp, loop, and out-and-back styles.
- The user receives at least three useful recommendations when inventory permits.
- Every recommendation has a human-readable explanation.
- Every night is accounted for.
- Frontcountry arrival/recovery options work for supported destinations.
- Every reservable night has a booking action.
- First-come and experimental nights are labeled honestly.
- A zero-result search gives quantified alternatives.
- GPX export works from the selected trip.
- The user can edit at least one camp night and see updated feasibility.

## Reliability

- At least **20 golden user scenarios** are stored and tested.
- Full invariant suite runs through one standard command.
- Availability errors do not create false “bookable” states.
- Geometry fallbacks are visible.
- Coverage levels are accurate.
- No unsupported point-to-point option appears.
- Recommendation data includes freshness timestamps.

## User validation

Initial targets:

| Metric | Target |
|---|---:|
| Supported searches returning at least one viable option | ≥70% |
| Searches that open a recommendation | ≥50% |
| Searches that save, export, or click booking steps | ≥20-30% |
| Top recommendation rated “would take” | ≥50% initially |
| Incorrect availability or feasibility reports | <2-3% |
| Test users who understand first-come uncertainty | ≥90% |
| Test users willing to use it for a real trip | 10+ before broad expansion |

---

# 17. Technical file-by-file priorities

These are hypotheses for Claude to verify, not mandatory architecture.

## `switchback/web.py`

P0:

- Expand request model with per-query preferences and hard limits.
- Accept trip-style arrays rather than one drifting string.
- Return complete trip objects.
- Include per-night availability and booking metadata.
- Include score explanations and confidence.
- Add a search endpoint that can later support multiple destinations.
- Stop relying invisibly on `profile.json` for core request constraints.

## `switchback/solver.py`

Preserve the current solver.

P0/P1:

- Continue accepting injected constraints.
- Ensure repeated camps reflect selected trip style.
- Separate true point-to-point work from same-entrance routes.
- Add structured “why no route” diagnostics if practical.
- Consider a controlled relaxation analysis for zero-result suggestions.

Do not add frontcountry campgrounds directly to the backcountry route graph unless they are genuinely trail-connected nodes. Use a planner/orchestrator above the solver.

## `switchback/scoring.py`

P0:

- Make scoring request-aware.
- Add trip-style fit.
- Return component scores.
- Generate explanation inputs.
- Prevent a generic basecamp from dominating moving-trip requests.

P1:

- Add drive/logistics fit.
- Calibrate using human evaluations.
- Add toughest-day preferences only after user feedback.

## `switchback/report.py`

Current text output can remain for CLI/debugging. Create a shared serialization/service layer so web, board, and CLI use the same trip-plan construction rather than duplicating presentation logic.

## `switchback/board.py`

The board can become a saved-search feed:

- “Trips matching your saved profiles today.”
- “One of your trip profiles became fully bookable.”

It should not be the primary place where general area exploration and recommendation browsing are merged.

## `switchback/web_index.html`

The single-file frontend was appropriate for proving the map. For the next consumer UI, assess whether to:

- keep a lightweight no-build architecture but split HTML/CSS/JS into maintainable files, or
- adopt a small component framework.

The decision should prioritize maintainability and satisfying interaction without creating a frontend rewrite project.

At minimum, separate:

- request form,
- result cards,
- trip detail,
- map layer,
- route editor,
- shared styles.

## `docs/board/index.html`

Extract the rubber-band routing behavior into reusable code. Integrate it into trip detail. Preserve advanced “explore area” mode after the core workflow is coherent.

## `switchback_gui.py`

Keep as an admin/utility surface for permit lookup and spreadsheet export. Do not invest in a second deep consumer trip-planning UI.

## New planning modules

Consider:

- `planner.py`: orchestrates destination selection, solver, frontcountry, scoring, and fallbacks.
- `models.py` or `tripplan.py`: request/response dataclasses or Pydantic models.
- `frontcountry.py`: campground records, policy, availability, and matching to trailheads.
- `explain.py`: match reasons, tradeoffs, and zero-result relaxation messages.

---

# 18. Testing and quality plan

## 18.1 Fix discovery first

All existing invariant scripts currently pass when executed individually, but normal pytest discovers only one test. Convert each `main()` invariant into one or more `test_*` functions or create a wrapper that invokes them.

One standard command should run:

- board,
- DEM,
- geometry,
- GPX,
- history,
- regions,
- scoring,
- shapes,
- solver,
- watch,
- web.

## 18.2 Add golden product scenarios

Suggested scenarios:

### Scenario 1: exact backcountry route

- Glacier Belly River.
- Three nights.
- Known synthetic availability.
- Verify exact camp sequence and dates.

### Scenario 2: mixed-policy region

- Lena.
- First-come Lower Lena plus reservable Upper Lena.
- Verify policy labels and no guarantee language.

### Scenario 3: basecamp requested

- Rainier.
- Basecamp allowed and preferred.
- Repeated camp nights can rank highly.

### Scenario 4: moving trip requested

- Rainier.
- Basecamp disabled.
- Repeated camp route must not appear.

### Scenario 5: complete vacation shell

- Arrival frontcountry night.
- Two backcountry nights.
- Every date has one stay.

### Scenario 6: no availability

- No exact route.
- Response proposes a quantified date shift, basecamp, or Campflare action.

### Scenario 7: route edit

- Change night-two camp.
- Verify route, miles, gain, availability, and fit update.

### Scenario 8: unsupported area

- Map-only area selected.
- UI clearly states what is and is not available.

### Scenario 9: stale or failed inventory

- Availability source errors.
- Result cannot be labeled bookable.

### Scenario 10: point-to-point hidden

- UI/API does not imply support until the solver handles different start/end entrances.

## 18.3 Manual UX test script

Ask five to ten backpackers to complete:

> Plan a two-night trip in a supported park for a flexible weekend, with one arrival campground and a maximum of ten miles per day.

Observe:

- where they hesitate,
- whether they understand preferred vs maximum,
- whether they understand the date window,
- whether they can compare routes,
- whether first-come status is clear,
- whether they can find booking steps,
- whether they trust the result.

---

# 19. Documentation alignment plan

## Recommended source-of-truth hierarchy

1. **`PRODUCT.md`** -  product promise, user, P0/P1/P2, definition of useful.
2. **`ROADMAP.md`** -  active outcome milestones only.
3. **`SPEC.md`** -  current technical product contract and models.
4. **`SCOPE.md`** -  build/borrow/avoid boundaries.
5. **`HANDOFF.md`** -  durable technical decisions and traps.
6. **`BACKLOG.md`** -  triaged tasks with priority and rationale.
7. **`CHANGELOG.md`** -  historical releases.
8. Generated coverage docs -  data facts, not roadmap.

## File-specific recommendations

| File | Keep? | Recommended role/change |
|---|---|---|
| `README.md` | Yes | Rewrite as concise current user/developer entry point. Correct version drift. Link to product and technical docs. |
| `HANDOFF.md` | Yes | Keep technical invariants, decisions, and known traps. Remove current product-priority duplication. |
| `SPEC.md` | Yes | Update around `TripRequest`, `TripPlan`, complete-night invariant, planner/solver separation, confidence, and frontcountry. |
| `SCOPE.md` | Yes | Reframe around the product wedge: build planning intelligence; integrate inventory/navigation; avoid generic road-trip and navigation scope. |
| `ROADMAP.md` | Yes | Replace active v1/v2 milestone history with current P0-P2 outcomes. Link to changelog for shipped history. |
| `BACKLOG.md` | Yes | Triage every item. Move shipped detail out. Add priority, user value, dependencies, and acceptance criterion. |
| `FUTURE.md` | Merge/archive | It overlaps roadmap/backlog. Keep only if it becomes a short strategic horizon; otherwise archive. |
| `OWNER.md` | Yes | Owner-only smoke tests and decisions. Keep short. |
| `EXPERIMENTS.md` | Yes | Experimental hypotheses and results only; do not use as product roadmap. |
| `PARKS.md` | Yes/generated | Keep generated. Improve support-tier vocabulary. |
| `COLORADO.md` | Yes/generated | Keep as coverage atlas. Do not equate mapped with trip-planning support. |
| `WASHINGTON.md` | Yes/generated | Same. |
| `CHANGELOG.md` | Yes | Preserve release history. |

## Do not delete useful history immediately

Archive or clearly mark historical sections rather than erasing technical context. The main goal is to make the current direction obvious.

---

# 20. Product decision filter

Before adding any feature, answer these questions.

1. Does it help a user find, understand, book, or modify a complete trip?
2. Does it improve the selected-area → dates/limits → night-by-night-plan workflow?
3. Does it strengthen the market wedge rather than duplicate a mature tool?
4. Can it be tested on a real trip scenario?
5. Does it work for at least one fully supported destination?
6. Is it more valuable than improving recommendation trust or UI clarity?
7. Does it require broad coverage before a narrow version can be useful?

Scoring rubric:

| Answer | Action |
|---|---|
| Strong yes to 1-4 | P0/P1 candidate |
| Helps only map breadth or technical novelty | P2 or parked |
| Duplicates Campflare/CalTopo/AllTrails | Integrate or export instead |
| Cannot be explained through a user scenario | Do not build yet |

---

# 21. Market and competitor context

The prior market review reached these conclusions.

## Campflare

Campflare covers broad campground cancellation alerts and now supports numerous wilderness-permit systems. Its strength makes generic permit alerts a weak primary wedge for Switchback.

Public product flow still expects the user to know relevant dates, destinations, camps, or zones. Switchback’s opportunity is to construct and rank the trip that should be watched or booked.

Reference:

- https://campflare.com/
- https://campflare.com/permits
- https://campflare.com/api

## Outdoor Status

Outdoor Status is a closer conceptual competitor because it combines permit alerts, destination content, and planners for prominent routes. Its public planning appears focused on curated marquee trips. Switchback can differentiate through generalized constraint-based enumeration across many camp combinations and route shapes.

Reference:

- https://outdoorstatus.com/best-backpacking-trips/
- https://outdoorstatus.com/unlimited/

## Mapping and navigation

AllTrails, CalTopo, Gaia, onX, and FarOut are mature. Switchback should export to them and use them as handoff tools rather than rebuilding their primary value.

References:

- https://www.alltrails.com/
- https://caltopo.com/
- https://www.gaiagps.com/
- https://www.onxmaps.com/backcountry/app
- https://faroutguides.com/

## General road trips and frontcountry camping

Roadtrippers, The Dyrt, and Hipcamp already cover general driving itineraries, POIs, and frontcountry discovery. Road-trip functionality in Switchback should be a constraint around backpacking opportunities, not a generic travel planner.

References:

- https://roadtrippers.com/
- https://thedyrt.com/
- https://www.hipcamp.com/

## Reddit demand signals

Recurring user problems found in Reddit research:

- People know when they can go but not what is actually available.
- Planning information is fragmented across park sites, Recreation.gov, maps, blogs, and forums.
- Users need alternatives when one night or camp breaks a route.
- Users struggle to identify credible permit-free alternatives.
- Real constraints include mileage, gain, group size, shuttle availability, dogs, lakes, driving time, snow, and first-come tolerance.

Representative threads:

- https://www.reddit.com/r/coloradohikers/comments/1kqnh1t/is_there_an_app_for_openavailable_backpacking/
- https://www.reddit.com/r/PNWhiking/comments/1lpewc3/looking_for_backpacking_recommendations_3_nights4/
- https://www.reddit.com/r/PNWhiking/comments/1twyss6/wondering_what_people_are_currently_using_to_plan/
- https://www.reddit.com/r/GrandTetonNatlPark/comments/1908hgo/tips_for_success_on_advanced_backcountry_permit/
- https://www.reddit.com/r/coloradohikers/comments/123z85l/seeking_info_on_shortish_couple_night_backpack_to/

The strongest validated job to be done is:

> **“I have these dates and limitations. Find me a complete trip that works, or tell me the smallest change that makes one work.”**

---

# 22. Monetization context

Monetization is not P0, but the product direction supports a credible paid tier.

Potential structure:

## Free

- Limited searches.
- Several supported destinations.
- Basic availability-aware recommendations.
- One saved profile.
- GPX export.
- Campflare handoff.

## Pro: approximately $39-59/year

- Unlimited cross-destination search.
- Flexible-date searches.
- Complete-trip alerts.
- Route repair.
- Multiple saved profiles.
- Drive-radius and road-corridor search.
- Advanced permit-free fallbacks.
- Group sharing.

## One-time trip plan: approximately $9-15

Useful for people who plan one major trip per year and resist another subscription.

At $49/year:

| Subscribers | Approximate annual recurring revenue |
|---:|---:|
| 100 | $4,900 |
| 500 | $24,500 |
| 2,000 | $98,000 |
| 5,000 | $245,000 |

The first commercial validation goal is not thousands of subscribers. It is proving that **20-50 serious backpackers** will pay because Switchback saves hours and finds a viable trip they would otherwise miss.

---

# 23. Claude’s requested deliverables

Claude should use this repository and brief to produce the following in order.

## Deliverable 1: product and architecture audit

Before making broad changes, report:

- What existing modules should remain unchanged.
- What modules need interfaces changed.
- Where a new planner/orchestrator belongs.
- Which current UI should be retired, reused, or integrated.
- Which current features are misleading or inaccessible.
- Which docs conflict.
- The exact smallest vertical slice.

## Deliverable 2: documentation alignment

Create/update:

- `PRODUCT.md`
- `ROADMAP.md`
- `SPEC.md`
- `SCOPE.md`
- `README.md`
- triaged `BACKLOG.md`

Do not erase useful history. Use `CHANGELOG.md` and archive sections appropriately.

## Deliverable 3: implementation plan

Provide a file-level plan with:

- dependencies,
- migrations,
- test additions,
- acceptance criteria,
- estimated effort,
- risks,
- explicit deferred items.

## Deliverable 4: first P0 vertical slice

Implement the smallest coherent path:

> selected supported destination + dates + visible effort limits + trip style → complete structured recommendations → night-by-night detail → booking/export actions.

Use existing solver and geometry. Do not begin with multi-destination search or generic road trips.

## Deliverable 5: UI proposal

Provide either:

- a working UI iteration, or
- detailed component hierarchy and wireframes before implementation.

The proposal must address:

1. constraint entry,
2. recommendation browsing,
3. route detail/editor.

## Deliverable 6: validation report

Run the full test suite and report:

- discovered tests,
- manually executed legacy invariants,
- new golden scenarios,
- remaining unsupported claims,
- areas where data confidence is insufficient.

---

# 24. Immediate highest-priority task list

If work begins immediately, use this order.

1. **Create the active product source of truth and triage the roadmap.**
2. **Fix normal test discovery.**
3. **Define `TripRequest`, `TripPlan`, `Stay`, and confidence models.**
4. **Expose preferred/max mileage and gain in the request API.**
5. **Hide unsupported point-to-point/shuttle options.**
6. **Build a complete structured response for existing backcountry results.**
7. **Redesign the request form.**
8. **Redesign the result cards and night-by-night detail.**
9. **Add one curated frontcountry arrival option for one destination.**
10. **Expand to two or three fully supported destinations.**
11. **Integrate route editing into selected trip detail.**
12. **Add quantified zero-result repair suggestions.**
13. **Add cross-destination/flexible-date search.**
14. **Add Campflare handoff and complete-trip saved alerts.**
15. **Only then consider road-corridor planning and broad expansion.**

---

# 25. Final directive

Switchback’s technical ambition is not the problem. The repository already contains multiple strong systems. The problem is that the user-facing product does not yet connect them into one clear promise.

The next milestone is not “more maps,” “more alerts,” or “more route tools.” It is:

> **A person selects a supported destination, dates, and real limits; Switchback returns several understandable, complete, actionable trips; every night is accounted for; the user can inspect, edit, book/watch, and export one without needing to understand the engine.**

Preserve the engine. Narrow the promise. Integrate the pieces. Make the interface feel calm, confident, and satisfying. Expand only after that vertical slice works on real trips.
