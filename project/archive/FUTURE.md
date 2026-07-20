# FUTURE.md

Note (2026-07-07, reaffirmed v3.3.0): ARCHIVED. Superseded by PRODUCT.md, ROADMAP.md, and BACKLOG.md. Retained for history and the monetization gates, which stay parked per PRODUCT.md section 5.

Roadmap for the Recreation.gov Permit Availability Finder.

Current build (v1.0): permit search, division loading with trail/lake parsing from descriptions, month availability fetch (6 threads), status classification (Reservable / Walk-up only / Full / Not released), dark CustomTkinter GUI, styled Excel export with conditional formatting and a real Excel table.

Effort estimates assume the existing engine gets reused. Value is scored for the primary user planning day hikes and backpacking trips, PNW first.

## Tier 1: Core usability (do these first)

| # | Feature | What it does | Effort | Value |
|---|---------|--------------|--------|-------|
| 1 | Consecutive-night itinerary solver | Given an ordered camp sequence (e.g. Wonderland CW) and a flexible start window, find every start date where camp i has space on night i. Answers "when can I actually do this route" instead of making you eyeball a grid. | 4-6 h | Very high |
| 2 | N-night window mode | "Any 2 consecutive nights at camp X between Jul 15 and Aug 31." Collapses the raw grid into bookable windows. | 2-3 h | High |
| 3 | Party size filter | Only count a night as available if remaining >= party size. Rec.gov's own UI hides mismatches, which creates false hope in exports. | 1 h | High |
| 4 | Saved presets | JSON file of recent permits, divisions, date windows, party size. One click to rerun the usual scans. | 2 h | High |
| 5 | Coordinates + deep links | Pull lat/long per division (permitcontent payload where present, RIDB facility API as fallback) and emit hyperlinks in the Excel export: AllTrails explore view centered on the camp, Google Maps, CalTopo. | 3-4 h | High |
| 6 | Scan caching + request budget | Cache month payloads per session, jittered backoff, cap total requests. Cheaper reruns, kinder to the endpoints. | 2 h | Medium |

## Tier 2: Automation and alerts

| # | Feature | What it does | Effort | Value |
|---|---------|--------------|--------|-------|
| 7 | Engine/GUI split | Extract fetch + classify into permit_engine.py with a CLI. GUI imports it. Prerequisite for 8-11. | 3 h | Enabler |
| 8 | Watch mode with diffing | Rescan every N minutes, alert only on transitions (Full to Reservable). Keeps a last-scan state file, compares, notifies. | 3-4 h | High |
| 9 | Telegram alerts | Reuse the existing Telegram bot from the morning digest. Message contains camp, date, remaining, direct booking URL. | 1-2 h | High |
| 10 | GitHub Actions poller + Pages dashboard | Same pattern as the Nimbus/Drizzle repos: scheduled workflow writes availability JSON, static page renders it. Caveat: Actions cron is 5 min nominal but commonly delayed 10-15 min in practice. Fine for planning, wrong tool for sniping hot cancellations; use local Task Scheduler or a small VPS for the fast path. | 4-6 h | High |
| 11 | History logger | Append every scan to SQLite with timestamps. After one season this answers: which weekday/hour cancellations cluster, how far ahead each camp fills, how fast walk-up releases go. Build the dataset now, analyze later. | 2-3 h | Medium now, high later |

## Tier 3: Trip planning intelligence

| # | Feature | What it does | Effort | Value |
|---|---------|--------------|--------|-------|
| 12 | Route templates + alternate-camp graph | Encode routes as legs with acceptable camps per night (Wonderland CW/CCW, Northern Loop, alternates when a camp is full). Solver searches chains across alternates, not just one fixed sequence. | 6-10 h | Very high for backpacking |
| 13 | Trail context layer | Curated JSON mapping division to trails, leg mileage, elevation gain, water sources. Start with Rainier, Enchantments, North Cascades and grow per trip. This mapping does not exist cleanly anywhere public and is the durable value in the project. | Ongoing | High |
| 14 | AllTrails via official MCP | Zero-code path: the official AllTrails MCP is already connected in Claude (trail search by location/bounds/name, trail details, trailhead weather). Workflow: export the availability workbook, hand it to Claude, ask for trail matches. Medium path: a Claude artifact that calls the API with the AllTrails MCP for an interactive planner. Experimental path: standalone Python MCP client against alltrails.com/mcp (OAuth unknowns). Never scrape AllTrails; community scrapers were shut down at their request in Jan 2026. Zero-code path proven live 2026-07-13: the Lena corridor was pulled through the MCP in-chat and its figures seeded the regions pilot. | 0 h to a weekend | Medium-high |
| 15 | Weather per camp | NWS point forecast (free, official) via division coordinates, added as columns for scanned dates. | 2-3 h | Medium |
| 16 | Multi-permit portfolio scan | Run 2-3 permits for the same window into one workbook, one tab per park. Answers "where can I go that weekend" instead of "is this one place open." | 2-3 h | High |

## Tier 4: Platform and distribution

| # | Feature | Notes | Effort |
|---|---------|-------|--------|
| 17 | PyInstaller onefile exe | Removes the Python prerequisite for sharing. Expect antivirus false-positive friction with unsigned builds. | 2-4 h |
| 18 | Repo hygiene | README with screenshots, requirements.txt, license, CHANGELOG, semantic versioning. Needed before sharing anywhere. | 2 h |
| 19 | Web app | FastAPI plus a simple frontend, only if this ever serves people other than you. Turns a script into an ops commitment. | 20-40 h |

## Monetization candidates (parked behind gates)

Landscape as of July 2026: Campnab runs $10/mo entry tiers up to $90/mo, Outdoor Status sells an annual subscription with unlimited trackers, PeakPeeker charges $5 one-time per tracker with the first free and ships a route-aware planner, PermitAlert is free and donation-funded with 60-second checks. Generic cancellation alerting is a commoditized race toward free.

If this ever monetizes, the differentiator is itinerary chaining plus curated trail context, not alerts. Gates before writing any billing code:

- G1: Personally plan 5+ trips with it across two seasons.
- G2: At least 3 people you do not know ask to pay for it.
- G3: Accept the platform risk that the availability endpoints are undocumented and can change or be blocked without notice.

## Non-goals

- Auto-booking or holding reservations. TOS violation, account-ban risk, and ethically off-route.
- Scraping AllTrails. Actively enforced against.
- Sub-minute polling. Does not materially improve planning outcomes and stresses endpoints everyone depends on.


## Naming record (decided 2026-07-07, written down 2026-07-13 sweep)

Switchback won over Contour, Frontier, Legwork, Madhuvan, and Cairn (taken by an existing hiking safety app). One adjacency to remember: Switchback Travel is an established outdoor gear review publication. Irrelevant for a personal tool; becomes a real trademark and SEO consideration at gate G1. Re-evaluate the name before any paid launch.
