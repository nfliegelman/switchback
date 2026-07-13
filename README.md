# Switchback

Backcountry permit availability, trip planning, and effort math, automated. A switchback is the trail's answer to terrain too steep to climb in one go; this project does the same thing to backcountry itineraries.

## Quickstart

Measured 2026-07-12: a fresh copy reaches its first ranked result in about a minute, most of it human typing. The command itself ran in one second on a one-month window.

1. Install Python 3.8 or newer (the python.org Windows installer includes tkinter). The engine needs no pip installs; it is standard library only.
2. Download or clone this repository and open a terminal in its folder.
3. Run: `python -m switchback trips glacier --start 2026-09-18 --end 2026-09-24 --nights 3 --codes GAB,COS,GLF,ELF`
   You get every bookable itinerary in that window, ranked by fit against your saved effort profile, camp quality, and lake nights, deduplicated by route with availability date spans, trip shape classified (loop, out_and_back, lollipop), and day-hike suggestions on any layover day.
4. Append `--gpx 1` to export the top route to `permit_exports/` as a GPX for CalTopo, AllTrails, or a Garmin. Lines are straight segments between graph nodes; snap to trails after import.
5. Windows, no terminal: double-click `TripFinder.bat` for the same thing with prompts, or `Switchback.bat` for the availability GUI, which now has a Find Trips button running the same engine.

## What's inside (v2.0.0)

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

Unsourced elevation gains are endpoint-delta estimates that understate passes by roughly 40 percent (benchmarked against a GPS log), so treat gain limits as soft at Rainier until the DEM pass lands; Glacier's big climbs are sourced numbers. GPX tracks are straight lines between graph nodes by design. Demand percentages are a fullness-rate proxy until the history log has weeks of depth.

## Where it's going

v2.0.0 completes the engine ladder (M0 through M10, see ROADMAP.md). Next is v2.1: the local web UI with the map, ranked routes as layers, and the choose-your-own-adventure frontier explorer, whose engine functions already exist. BACKLOG.md holds everything else. SPEC.md and SCOPE.md hold design rationale. HANDOFF.md exists so any AI assistant can pick the project up cold.

## Versioning

v1.0.0 was the original GUI upload. Each engine milestone bumped the minor version; v2.0.0 marks the complete engine, reached 2026-07-12. The web UI ships as v2.1.
