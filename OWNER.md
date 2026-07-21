# OWNER.md

Your side of the house. Everything Switchback needs from Noah, split by device, updated every release. Claude keeps this current; check it whenever you lose track.

## Phone, anytime (each under 5 minutes)

1. DELETE TODAY'S GITHUB TOKEN (the one from the 2026-07-15 session). Same drill as always: Settings > Developer settings > Fine-grained tokens.
2. (CLOSED 2026-07-15) AllTrails detail approval worked; crowd-volume stats confirmed flowing (Vestal Basin returned 89 reviews, 189 completed hikes). The solitude signal now has a live data source when a future session wires it into scoring.
3. Map board check: open the board (your home screen icon, or nfliegelman.github.io/switchback/board/). Bottom-left should say v3.6.1; the app caches itself, so give it a close-and-reopen or two. Tap a trip and confirm trail lines draw.
4. Releases check: repo page > Releases. You should see every version back to v1.0.0, each with a downloadable zip. That page is your download spot from now on.
5. Two one-minute taps to finish the Releases backfill (GitHub refused to let the robot stamp these two specific versions, a permissions rule; everything else landed): repo page > Releases > Draft a new release > in the tag box type v3.4.1 and choose Create new tag > for Target open Recent Commits and pick the commit titled "v3.4.1: the owner test drive plan in OWNER.md, releases robot hardened (PR 2)" > tap Generate release notes > Publish. Then repeat with tag v3.4.2 on the commit titled "v3.4.2: releases robot repair, version bump and paper trail".

## Product brief: RECEIVED and processed (2026-07-17)

The alignment brief is now Part 2 of project/PRODUCT.md; Claude's candid Historical Context Addendum is its Part 1; the roadmap is rewritten around it. Nothing owed from you here; read project/PRODUCT.md Part 1 section 7 if you want the priority changes in one place.

## Checking you are on the right version

Everything now announces itself. The CLI prints "switchback v3.6.1" at the top of every command; the app window title bar shows "Switchback v3.6.1"; the map board shows it bottom-left; the .bat files print it first. If any surface does not say v3.6.1, you are running an old copy: grab the newest zip from the Releases page.

## Desktop, the big test drive (your call, 2026-07-20; about 90 minutes, fine to split across evenings)

Do these in order and keep one running note of anything broken, confusing, or great. Messy reactions are exactly the data Claude needs; there are no wrong answers here.

6. Fresh copy first: repo page > Releases > top entry > download "Source code (zip)" and extract it. Every surface should say v3.6.1; if one does not, you grabbed an old zip.
7. REOPENED, the calibration half hour: double-click CALIBRATE.bat, wait 2 or 3 minutes, then type a few words after every REACTION line in the Notepad file that opens (would you actually hike it? too hard, too easy, wrong camps, anything look wrong?), save, and send the file text to Claude. Scoring stays generic until this lands. One caution: if a Maroon Bells route's miles look off, note it and move on; that corridor has a known data bug already on the fix list.
8. Smoke test: double-click SMOKE_GUI.bat, click Find Trips once, note whether results appear.
9. The real app: double-click Switchback.bat. A second black window titled "Switchback server" will open and stay open: that is the app running, leave it alone (closing it, or clicking Quit in the app, shuts Switchback down). Your browser opens on its own once the server is ready. Run a live search on each of Rainier, RMNP, and Lena for a window you might actually go (say late September, 3 nights, party of 2). Gut-check the top three trips per park: miles, climbs, camps, shapes. Click any day's mileage (the underlined "Xmi/Yft" text) to open a small elevation chart for that day, showing where the climbing actually sits. Flip the trip-shape toggles. Draw a route with the rubber-band builder. Export one GPX.

9a. NEW IN v3.6.1, the big one: the "Plan trips" button (now the green primary button; the old list moved to "Classic list"). Pick Rainier, set your dates and party up top, then fill the short form: how far and how much climbing you are comfortable with per day, your absolute maximums, what kind of trip, and tick "Add a campground near the trailhead the night before". Read the one-sentence summary, hit Find trips, and judge what comes back: each card should read like a trip a human would describe, with where you sleep every single night, what is bookable, what is first-come, and what Switchback honestly does not know. Open one, check the night-by-night list and the map line, click a booking link, download the GPX. Then try limits that are impossible (say max 2 miles a day) and confirm it tells you the smallest change that would open trips up instead of just saying no. Also new: every hiking day shows an estimated time that counts steep miles for more (your 45 percent grade request), there is a pace picker in the form, and clicking a day's mileage now also shows the estimated time and the steepest section of that day from real elevation data. Gut-check those times against hikes you know. If you want your exact speeds used, send Claude your per-grade paces and they go in as your personal table. Note anything confusing or dishonest-feeling; this screen is the product now.
10. GPX proof: at caltopo.com click Import and load docs\samples\sample_rmnp_route.gpx from the extracted folder (a line should draw near Estes Park), then import the GPX you exported in step 9 the same way.
11. Alerts: double-click TELEGRAM_TEST.bat; first run opens a file to paste your two bot values into, second run sends one test message to your phone.
12. Optional, whenever you hike it: record a GPX trace of the Conundrum spur. Still the one edge waiting on your feet.

Report back with three things: the filled calibration sheet, your running note from steps 6 to 11, and screenshots of anything that looked wrong. Claude folds all of it into scoring and the fix list.

## Done (kept for the record)

- 2026-07-20: the markdown cleanup you asked for, in two passes: an automated v3.3.1 pass merged overlapping docs (the addendum now lives inside PRODUCT.md as its Part 1), then v3.4.0 finished the folder layout you approved. The repo front page now shows just README, OWNER, CLAUDE, and CHANGELOG; the working docs live in project/; the app-written coverage table is coverage/COVERAGE.md. Nothing was deleted, only merged or moved. Also per your ask, every version now shows up on the repo's Releases page on GitHub automatically, past ones included, and each release carries a downloadable zip of the code as of that version, which is the safest place to grab your re-download from now on.

- 2026-07-15: old PAT deleted, Telegram secrets landed, Actions verified green (your items 1 to 3). Standing questions answered: corridor buffer vetoed to 1 km (all three corridors rebuilt same day) and the loop-vs-any question superseded by your trip-shape toggles request, now specced in ROADMAP. The accidental "Add files via upload" commit was force-push deleted.

- 2026-07-14: v2.20.0 through v3.0.0 shipped and pushed in one day. Nine releases, all tagged. Your five phone tasks and four desktop tasks above are the entire critical path now.

- 2026-07-14: all three long-trail corridors built at your 1.5 km default; veto window stays open, a rebuild is one command per corridor.

- 2026-07-14: pushed v2.20.0 and v2.21.0 to GitHub with tags (Claude, with your PAT).
