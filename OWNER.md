# OWNER.md

Your side of the house. Everything Switchback needs from Noah, split by device, updated every release. Claude keeps this current; check it whenever you lose track.

## Phone, anytime (each under 5 minutes)

1. DELETE TODAY'S GITHUB TOKEN (the one from the 2026-07-15 session). Same drill as always: Settings > Developer settings > Fine-grained tokens.
2. (CLOSED 2026-07-15) AllTrails detail approval worked; crowd-volume stats confirmed flowing (Vestal Basin returned 89 reviews, 189 completed hikes). The solitude signal now has a live data source when a future session wires it into scoring.

## Desktop, first session back (about 45 minutes total)

6. Calibration half hour, the single highest-value thing on this list. On desktop run: python -m switchback calibrate glacier --start <date> --end <date> (repeat for maroonbells and rmnp). Each run prints the top ten with score components and writes docs/CALIBRATION_NOTES.md with a REACTION line under every route. Fill those in with anything: too far, too flat, wrong camps, boring, love it. Then hand the file to Claude and scoring.json gets fit to you. Scoring stays generic until this happens.
7. Smoke test: click Find Trips in the old GUI once (switchback_gui.py). It compiles but no human has clicked it.
8. Smoke test: import the shipped sample GPX (glacier_2026-09-22_BRE_GAB-GLF.gpx) into CalTopo or AllTrails. Confirm it draws.
9. Smoke test: paste your bot token into telegram.json (copy telegram.json.example), run python -m switchback watch glacier --inject --once, confirm one Telegram message arrives.
10. Optional, whenever you hike it: record a GPX trace of the Conundrum spur. It is the one edge waiting on your feet.

## Done (kept for the record)

- 2026-07-15: old PAT deleted, Telegram secrets landed, Actions verified green (your items 1 to 3). Standing questions answered: corridor buffer vetoed to 1 km (all three corridors rebuilt same day) and the loop-vs-any question superseded by your trip-shape toggles request, now specced in ROADMAP. The accidental "Add files via upload" commit was force-push deleted.

- 2026-07-14: v2.20.0 through v3.0.0 shipped and pushed in one day. Nine releases, all tagged. Your five phone tasks and four desktop tasks above are the entire critical path now.

- 2026-07-14: all three long-trail corridors built at your 1.5 km default; veto window stays open, a rebuild is one command per corridor.

- 2026-07-14: pushed v2.20.0 and v2.21.0 to GitHub with tags (Claude, with your PAT).
