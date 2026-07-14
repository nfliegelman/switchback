# OWNER.md

Your side of the house. Everything Switchback needs from Noah, split by device, updated every release. Claude keeps this current; check it whenever you lose track.

## Phone, anytime (each under 5 minutes)

1. DELETE TODAY'S GITHUB TOKEN. github.com > Settings > Developer settings > Fine-grained tokens > delete. Do this after every build day, no exceptions.
2. Telegram secrets. Repo Settings > Secrets and variables > Actions > New secret: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (your existing digest bot). Unlocks watch alerts and the cloud watcher.
3. Glance at the Actions tab once after a push day: Switchback watch and the board cron should both be listed and green.
4. Next Claude session that uses AllTrails details: a permission prompt appears MID-CALL; tap approve. Three sessions have missed it. Unlocks crowd-volume stats.
5. Answer two standing questions in any chat: (a) profile trip_type: keep loop or flip to any? The loop filter once hid 635 of 639 routes. (b) Corridor buffer width: 1.5 km default was used; veto if you want 1 or 2.

## Desktop, first session back (about 45 minutes total)

6. Calibration half hour, the single highest-value thing on this list. On desktop run: python -m switchback calibrate glacier --start <date> --end <date> (repeat for maroonbells and rmnp). Each run prints the top ten with score components and writes docs/CALIBRATION_NOTES.md with a REACTION line under every route. Fill those in with anything: too far, too flat, wrong camps, boring, love it. Then hand the file to Claude and scoring.json gets fit to you. Scoring stays generic until this happens.
7. Smoke test: click Find Trips in the old GUI once (switchback_gui.py). It compiles but no human has clicked it.
8. Smoke test: import the shipped sample GPX (glacier_2026-09-22_BRE_GAB-GLF.gpx) into CalTopo or AllTrails. Confirm it draws.
9. Smoke test: paste your bot token into telegram.json (copy telegram.json.example), run python -m switchback watch glacier --inject --once, confirm one Telegram message arrives.
10. Optional, whenever you hike it: record a GPX trace of the Conundrum spur. It is the one edge waiting on your feet.

## Done (kept for the record)

- 2026-07-14: all three long-trail corridors built at your 1.5 km default; veto window stays open, a rebuild is one command per corridor.

- 2026-07-14: pushed v2.20.0 and v2.21.0 to GitHub with tags (Claude, with your PAT).
