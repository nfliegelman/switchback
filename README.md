# Switchback

Switchback v3.0.0. A constraint-based backcountry itinerary engine: 72 landscape maps across Colorado and Washington (wilderness, parks, monuments, state lands, and the CT, CDT-CO, and PCT-WA corridors), live rec.gov availability with dual-permit merging, trail-true elevation grading within one percent of GPS logs, an experimental dispersed layer, a PWA map with a rubber-band route builder and GPX export, cloud watching with Telegram alerts, and a scoring layer waiting on its owner's calibration half hour. HANDOFF.md carries the decision log; OWNER.md carries the human's side; ROADMAP.md carries what v3.x means.


Backcountry permit availability, trip planning, and effort math, automated. A switchback is the trail's answer to terrain too steep to climb in one go; this project does the same thing to backcountry itineraries.

## Quickstart

Two ways in. No terminal, no black boxes; if a console window ever appears, that is a bug, not a step.

**Phone (the everyday app).** Open https://nfliegelman.github.io/switchback/board/ in Safari or Chrome, tap Share, then Add to Home Screen. That is the app: today's ranked trips on a map, refreshed every morning, plus every built Colorado wilderness under explore areas. Anything you have opened once keeps working with no signal (the base map tiles still want a connection).

**Computer (the full engine).** One-time setup: install Python from https://www.python.org/downloads/ and CHECK the box "Add python.exe to PATH". After that, double-click `Switchback.bat`. The same app opens in your browser with the full engine behind it: any dates, any window, Find Trips, Adventure mode, and GPX export that follows the real trail line wherever one is mapped. The very first run installs two small pieces for the local map, about thirty seconds, then never again. Use the quit link at the bottom of the page when you are done. `Switchback Classic.bat` opens the availability grid and styled Excel export in its own window.

### Advanced: the terminal (optional, for the curious)

Measured 2026-07-12: a fresh copy reaches its first ranked result in about a minute, most of it human typing. The command itself ran in one second on a one-month window.

Open a terminal in this folder and run: `python -m switchback trips glacier --start 2026-09-18 --end 2026-09-24 --nights 3 --codes GAB,COS,GLF,ELF`
You get every bookable itinerary in that window, ranked by fit against your saved effort profile, camp quality, and lake nights, deduplicated by route with availability date spans, trip shape classified (loop, out_and_back, lollipop), and day-hike suggestions on any layover day. Append `--gpx 1` to export the top route to `permit_exports/` as a GPX for CalTopo, AllTrails, or a Garmin; since v2.8 the lines follow real trail geometry (OSM plus USGS and USFS centerlines) and go straight only where no dataset has a mapped trail. The engine itself needs no pip installs; fastapi and uvicorn are used only by the local map and install themselves on first double-click.

## What's inside (v2.0.0)

**The trip board (v2.3, phone-native).** A daily GitHub Action computes ranked trips for the windows in `board_config.json` (relative dates, so the config never goes stale) and commits `docs/board/board.json`; the static page at `docs/board/` renders them on a map. Enable it once: repo Settings, Pages, deploy from branch, main, /docs. Then the board lives at your Pages URL under /board/, readable from any phone, refreshed every morning, with first-come sites labeled honestly. The same job snapshots the scan history into `data/` daily so the demand dataset survives anything.

**Regions (v2.2).** A region stitches permits and permitless sites that share trails into one plannable graph. `parks/lena.json` is the pilot: Lower Lena Lake (Olympic NF, first-come, no permit system) chains to Upper Lena Lake (Olympic NP, permit 4098362) in one itinerary, with first-come nights labeled everywhere they appear. `python -m switchback trips lena` works today.

**The map (v2.1).** `SwitchbackMap.bat` (or `python -m uvicorn switchback.web:app --port 8756` after `pip install fastapi uvicorn`) opens the local web UI: pick a park, camps color by open nights in your window, Find Trips draws ranked routes on the trail graph, and Adventure mode builds a trip one night at a time from the live frontier, each option showing distance, climb, sites left, and how many ways the trip can still finish. The engine stays standard library; fastapi and uvicorn are needed only for the map.

**Availability finder (GUI).** Search any recreation.gov wilderness permit, pull classified availability (Reservable, Walk-up only, Full, Not released) across a date range on six threads, export a styled Excel workbook. The Find Trips button runs the trip engine with your saved profile and opens the ranked report in a window.

**Trip engine (CLI).** `trips` enumerates bookable itineraries within your daily limits (`profile.json`: party, preferred and max miles and gain), scores them with editable weights (`scoring.json`), and understands basecamps: a layover day gets ranked day-hike options, because the night needs a permit but the day hike does not, which turns basecamping into availability arbitrage. `--via COS` keeps only routes that sleep at or pass through a camp. `--trip-type loop` filters by shape.

**Watch mode and Telegram alerts.** `python -m switchback watch glacier --start 2026-09-18 --end 2026-09-25 --codes ELF,COS` polls on a jittered interval and messages you when a full camp-night opens. Alerts fire exactly once per opening, only after the opening survives one re-check (flicker filter), and carry camp, date, spots left, and a booking link. Setup: copy `telegram.json.example` to `telegram.json` and paste your bot token and chat id, or set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID. Test the pipeline without sending: add `--once --no-send --inject DIV:2026-09-23`.

**Cloud watcher (GitHub Actions).** The repo ships `.github/workflows/watch.yml`: a cron job every 30 minutes runs one watch cycle on GitHub's machines, so alerts reach your phone with no computer running anywhere. Activate it in three steps: add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID under repo Settings, Secrets and variables, Actions; edit `watch_config.json` (set enabled to true, pick park, window, camps); push. Ad-hoc watches fire from the GitHub mobile app via Actions, Switchback watch, Run workflow, which accepts park, window, codes, and party as form inputs. Watch state and scan history persist between runs through the Actions cache, so exactly-once alerting is soft-guaranteed: a rare cache eviction can cost one duplicate alert, never a missed one. GitHub pauses cron on repos with no activity for 60 days; any commit revives it.

**Scan history.** Every availability fetch, from any entry point, silently appends to `parks/history.sqlite`. `python -m switchback history stats` shows growth; `history demand` derives a fullness-rate demand file that the scorer's solitude term reads automatically once camps have 30 or more observations. The longer Switchback runs, the smarter it gets.

**Exports.** `export glacier BRE GAB,GLF,GAB --start 2026-09-22` writes an itinerary GPX with no availability fetch. `python caltopo_export.py <permit_id>` writes a CalTopo GeoJSON layer of every camp and trailhead, with rating and percentile properties attached when a park dataset exists, plus optional `--window START END` open-night counts.

**Coverage.** `python -m switchback coverage --write` regenerates PARKS.md, the living list of which parks sit at which tier. The availability finder itself needs no setup for any recreation.gov permit, park or forest alike.

**Park data pipeline.** `search` finds permits, `extract <permit_id> --slug <name>` builds `parks/<slug>.json`, `features <slug>` fills coordinates (OSM name-join with a manual queue) and tags lakes, creeks, and elevations from USGS sources, `graph <slug>` validates the route network, `availability` is the classic classified table. Adding a camp-night park is extract, features, then transcribing its mileage table into `parks/edges/`.

## Requirements

Python 3.8+ with tkinter for the GUI (included in the python.org Windows installer). The GUI auto-installs `customtkinter` and `openpyxl` on first run; everything else is standard library.

## Honest cautions

Elevation gains carry a method tier: sourced numbers, then AllTrails-derived and pass-arithmetic figures, then DEM line-sampled estimates (benchmarked within 7 percent, erring high, on a Rainier GPS log; the dem command self-flags results where the line crosses ridges the trail contours around, which is why the Tetons and Enchantments use pass arithmetic instead), then raw endpoint deltas. Run python -m switchback dem <slug> after adding edges. GPX tracks are straight lines between graph nodes by design. Demand percentages are a fullness-rate proxy until the history log has weeks of depth.

## Where it's going

v2.0.0 completes the engine ladder (M0 through M10, see ROADMAP.md). Next is v2.1: the local web UI with the map, ranked routes as layers, and the choose-your-own-adventure frontier explorer, whose engine functions already exist. BACKLOG.md holds everything else. SPEC.md and SCOPE.md hold design rationale. HANDOFF.md exists so any AI assistant can pick the project up cold.

## Versioning

v1.0.0 was the original GUI upload. Each engine milestone bumped the minor version; v2.0.0 marks the complete engine, reached 2026-07-12. The web UI ships as v2.1.


## Trail geometry

Route lines on the map, the board, and in GPX exports follow real trail polylines harvested from OpenStreetMap, with straight-line fallback wherever routing honestly failed (each case is recorded in BACKLOG). Trail geometry is derived from OpenStreetMap via the Overpass API, copyright OpenStreetMap contributors, ODbL 1.0.
