# SPEC.md

Design spec for Switchback: the trip-finding engine layered on the permit finder. Companion to FUTURE.md (this is Tier 3, fully expanded). Status: design, not built.

## 1. Purpose

Turn "is camp X open" into "given my constraints and taste, what are the best trips I can actually book right now." Input is a trip request. Output is ranked, bookable itineraries with per-day stats, camp tags, and booking links.

## 2. Trip request schema

```json
{
  "park": "mount-rainier",
  "window": {"start": "2026-08-14", "end": "2026-08-23"},
  "nights": 3,
  "party_size": 2,
  "basecamp_ok": true,
  "daily": {
    "pref": {"miles": 9, "gain_ft": 2200},
    "max":  {"miles": 13, "gain_ft": 4000, "grade_pct": 18}
  },
  "prefs": {
    "lakes": 1.0,
    "solitude": 0.6,
    "rating_weight": 1.0
  }
}
```

Hard fields filter. Values under `prefs` are weights in the scorer; 0 disables a term.

## 3. Data model (extends the route graph)

Nodes (camps, trailheads) and edges (distance, gain, loss, max sustained grade) per the graph design already validated against the Rainier payload. Additions:

```
camp_features: camp_id, lake_within_400m, lake_name, waterbody_acres,
               creek_within_200m, elevation_ft, dist_to_trailhead_mi,
               quota_size, stay_limit_nights,
               links {alltrails, wta, caltopo, nps}
camp_ratings:  camp_id, personal_rating (0-5, nullable),
               computed_prior (0-5), notes, sources[]
camp_demand:   camp_id, date, remaining, total, scanned_at
```

camp_demand rows come free from the availability scans once the history logger (FUTURE.md item 11) is on.

## 4. Scoring model

Two stages, deliberately separated.

Stage 1, feasibility (hard filters): an availability chain exists across the window (remaining >= party_size on the right night at each camp, walk-up excluded by default), every day within max miles/gain/grade, per-camp stay limits respected, basecamp repeats only if basecamp_ok.

Stage 2, score per feasible itinerary:

```
day_fit    = 1 - |actual - pref| / pref        miles and gain, averaged, clamped 0..1
camp_score = rating percentile within park     personal_rating overrides computed_prior
lake_term  = lakes_w * share_of_nights_at_lake_camps
crowd_term = solitude_w * (1 - demand_pct)     sign flips if crowds are preferred
score      = w1*mean(day_fit) + w2*mean(camp_score) + lake_term + crowd_term
```

Ratings normalize to percentile within their park, so a 4.5 at Glacier competes only against Glacier. Cold start: with no personal ratings and no demand history, camp_score falls back to computed_prior and crowd_term drops out. The engine works on day one and sharpens as data accrues.

computed_prior = f(lake proximity, elevation band, distance from trailhead, quota size). Hand-set coefficients first; revisit only after 20+ personal ratings exist to calibrate against.

## 5. Data sources per feature

| Feature | Source | Method | License |
|---|---|---|---|
| Lake / creek proximity | USGS hydrography (NHD waterbodies, flowlines); OSM water polygons | Spatial join: camp coords within 400 m / 200 m | Public domain / ODbL |
| Elevation, gain, grade | USGS 3DEP DEM | Sample along edge geometry, smooth, window for sustained grade | Public domain |
| Distance to trailhead | Route graph | Shortest path from camp to nearest entrance node | Derived |
| Quota size, stay limits | permitcontent payload + park rules pages | Extract, manually verify | Public domain |
| Demand / crowding | Own availability scan history | Fill velocity: days-to-full per camp per date, expressed as demand percentile | Own data |
| Ratings | Personal + synthesized research | Lazy workflow, section 7 | Own original scores |
| Community conditions | WTA trip reports, AllTrails | Links stored per camp; content never stored | Link-only |

## 6. Park archetypes

Archetype A, camp-night parks: you book a specific camp or zone each night. Examples: Rainier, Glacier, Yellowstone, Grand Teton, Olympic, Grand Canyon use areas. Full graph plus chain solver applies.

Archetype B, entry-quota parks: you book a trailhead entry for day 1, then camp anywhere legal. Examples: Yosemite, Sequoia/Kings Canyon, most USFS wilderness quotas. Feasibility is a single division check (the trailhead) on one date; the graph still drives quality scoring but not chaining. Note: in these permits the "divisions" the existing engine fetches are the trailheads, so the same endpoint serves both archetypes.

Holdouts running their own booking systems (verify at onboarding; cover late or never): Zion, Great Smoky Mountains, Denali.

Onboarding checklist per park: confirm booking system and archetype (systems migrate between seasons), pull divisions and entrances, source official mileages or run the OSM/DEM compute, spatial-join features, spot-check 5 edges against a map, record stay limits and season dates.

## 7. Ratings workflow (lazy, assisted)

1. Never pre-rate a park. Rate only camps that surface in real results. At Rainier, maybe 25 of 190 divisions will ever appear in a top ranking.
2. For an unrated surfaced camp, run a research pass: a Claude session with web search across WTA reports, NPS pages, and trail blogs, plus AllTrails details via the official MCP at planning time. Output: a draft prior 0-5, a two-line justification, and source links stored in sources[].
3. A personal edit sets personal_rating, which overrides the prior permanently.
4. Ratings are original synthesized judgments. If this ever ships beyond personal use, no column may mirror another platform's stars.

## 8. Phasing

| Phase | Contents | Effort | Unlocks |
|---|---|---|---|
| P1 | Payload extractor (camps + entrances), Rainier edges from official NPS mileages, feature spatial joins, scorer on computed_prior only, CLI trip request | 20-28 h | Working recommender, one park |
| P2 | Demand logger wired into every scan, onboard Enchantments plus Olympic or Glacier, lazy rating loop | 10-15 h plus a season of scans | Crowd term, calibrated ratings |
| P3 | Archetype B support (Yosemite), OSM/DEM edge pipeline for parks without published mileages, non-permit campground availability endpoint | 20-30 h | Breadth |

## 9. Risks and non-goals

- The demand signal needs weeks to months of scan history before it means anything. Start logging in P1 even though scoring uses it in P2.
- No-permit dispersed backcountry has no structured camp inventory and no clean legality metadata. Out of scope until P3 at the earliest, possibly forever.
- Unsmoothed DEM sampling overstates gain by roughly 10-25 percent. Smooth, and validate against official numbers wherever they exist.
- Park booking systems migrate. Re-verify archetype and endpoints every season, per park.
- AllTrails and WTA content is link-only, always.

## 10. Adventure mode (interactive frontier search)

Batch mode and adventure mode are the same solver. The DP lattice over (night, camp) states is the book: batch mode enumerates every ending and ranks them, adventure mode turns one page at a time. Editing an existing route is re-opening the book at chapter k, so this section absorbs the structured route editing line item in SCOPE.md.

Start resolution. Trailheads are ordinary nodes. A virtual origin connects to every entry trailhead at zero cost, so the night-1 frontier is every camp reachable from any trailhead within daily bounds. A camp reachable from multiple trailheads appears once, with one via entry per approach carrying that approach's distance, gain, and grade. The trailhead choice is deferred until logistics force it. Validated against live Glacier data: Elizabeth Lake Foot is reachable from both the BRE Belly River Trail and IPE Iceberg/Ptarmigan Trail entrances, exactly the case this design defers rather than forces.

Exit resolution. A virtual sink mirrors the origin, shaped by trip_type, a hard filter:

- out_and_back: exit equals entry, retracing allowed
- loop: exit equals entry, retraced edges penalized in scoring
- shuttle: any exit trailhead, flagged as requiring a second car or pickup

Direction-aware edges. Edges store gain and loss separately; reverse traversal swaps them. A river-valley approach and a pass approach to the same camp differ mainly in profile, and limit alerts must reflect the direction actually walked.

Dead-end protection. Before rendering a frontier, run feasibility backward from the sink: an option is shown only if at least one complete, availability-valid, within-bounds trip still exists through it. Each card also shows endings_remaining, the count of feasible completions through that choice, computed from the same DP table. No page leads to a trip that cannot finish.

Frontier card contents: camp name, rating percentile, availability that night vs party size, per-via leg stats from the current position, lake and creek tags, demand percentile, endings_remaining. A layover appears as a self-loop card when basecamp_ok and availability allow.

Freshness. Availability is re-verified with one live check the moment a card is picked, so a page cannot go stale between the scan and the selection.

Data-quality findings from Glacier (permit 4675321, 213 divisions):

- Coordinates are 0,0 throughout Glacier's payload, unlike Rainier's 186 of 190 populated. Fallback order per field: payload, NPS park GIS, OSM name-join, manual entry. Already covered by the onboarding checklist.
- Divisions include administrative sites, stock hitch rails, and spike camps. Each park needs a division filter so the frontier shows only reservable hiker camps by default.
- Official camp and trailhead mileage tables exist in the park's backcountry guide, so Glacier edges are transcription, like Rainier.

Cost. Backward pruning plus endings counts: 2-3 h in the solver. Interactive UI: 6-10 h on map v0, or 2-3 h as a numbered-list CLI available immediately after P1. Net effect on SCOPE.md totals: +2-4 h, since this absorbs the 8-12 h structured editing line.


## Addendum, v1.6.2 (2026-07-12): basecamp day hikes

Layover days (consecutive nights at one camp) are enriched, not just
permitted. Scorer._dh_options computes out-and-back routes from the
basecamp to every other graph camp; day_hikes ranks them 60/40 by
destination percentile and effort fit and filters unwalkable distances;
layover_notes renders CLI lines. Destination availability is ignored by
design: day hikes need no permit, so basecamping converts a sold-out
destination into a reachable one. Scoring counts each layover as its
best achievable day-hike fit rather than skipping the day. v1 limits
destinations to graph camps; POI nodes are in BACKLOG.
