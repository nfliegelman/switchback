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
