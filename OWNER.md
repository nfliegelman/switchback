# OWNER.md

Your side of the house. Everything Switchback needs from Noah, split by device, updated every release. Claude keeps this current; check it whenever you lose track.

## Phone, anytime (each under 5 minutes)

1. DELETE TODAY'S GITHUB TOKEN (the one from the 2026-07-15 session). Same drill as always: Settings > Developer settings > Fine-grained tokens.
2. (CLOSED 2026-07-15) AllTrails detail approval worked; crowd-volume stats confirmed flowing (Vestal Basin returned 89 reviews, 189 completed hikes). The solitude signal now has a live data source when a future session wires it into scoring.

## Product brief: RECEIVED and processed (2026-07-17)

The alignment brief is now Part 2 of project/PRODUCT.md; Claude's candid Historical Context Addendum is its Part 1; the roadmap is rewritten around it. Nothing owed from you here; read project/PRODUCT.md Part 1 section 7 if you want the priority changes in one place.

## Checking you are on the right version

Everything now announces itself. The CLI prints "switchback v3.4.0" at the top of every command; the app window title bar shows "Switchback v3.4.0"; the map board shows it bottom-left; the .bat files print it first. If any surface does not say v3.4.0, you are running an old copy: re-download the ZIP from GitHub.

## Desktop, first session back (about 45 minutes total)

6. (MOVED TO FUTURE TODO by your call, 2026-07-17; everything stays ready) Calibration: double-click CALIBRATE.bat, wait 2 or 3 minutes, then type a few words after every REACTION line in the Notepad file that opens, save, and send that file (or its text) to Claude. Scoring stays generic until this happens.
7. Smoke test: double-click SMOKE_GUI.bat, click Find Trips once, note whether results appear or anything looks broken.
8. Smoke test: go to caltopo.com, click Import (top left), choose docs\samples\sample_rmnp_route.gpx from the extracted folder, confirm a line draws on the map near Estes Park.
9. Smoke test: double-click TELEGRAM_TEST.bat; first run opens a file to paste your two bot values into, second run sends one test message to your phone.
10. Optional, whenever you hike it: record a GPX trace of the Conundrum spur. It is the one edge waiting on your feet.

## Done (kept for the record)

- 2026-07-20: the markdown cleanup you asked for, in two passes: an automated v3.3.1 pass merged overlapping docs (the addendum now lives inside PRODUCT.md as its Part 1), then v3.4.0 finished the folder layout you approved. The repo front page now shows just README, OWNER, CLAUDE, and CHANGELOG; the working docs live in project/; the app-written coverage table is coverage/COVERAGE.md. Nothing was deleted, only merged or moved. Also per your ask, every version now shows up on the repo's Releases page on GitHub automatically, past ones included, and each release carries a downloadable zip of the code as of that version, which is the safest place to grab your re-download from now on.

- 2026-07-15: old PAT deleted, Telegram secrets landed, Actions verified green (your items 1 to 3). Standing questions answered: corridor buffer vetoed to 1 km (all three corridors rebuilt same day) and the loop-vs-any question superseded by your trip-shape toggles request, now specced in ROADMAP. The accidental "Add files via upload" commit was force-push deleted.

- 2026-07-14: v2.20.0 through v3.0.0 shipped and pushed in one day. Nine releases, all tagged. Your five phone tasks and four desktop tasks above are the entire critical path now.

- 2026-07-14: all three long-trail corridors built at your 1.5 km default; veto window stays open, a rebuild is one command per corridor.

- 2026-07-14: pushed v2.20.0 and v2.21.0 to GitHub with tags (Claude, with your PAT).
