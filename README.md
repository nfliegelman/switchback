# Switchback

v3.3.0. A constraint-based backcountry trip planner: tell it when you
can go and what you can handle, it finds complete trips you can
actually take, checked against live rec.gov availability.

Start here by role. Product direction: PRODUCT.md, then
PRODUCT_ADDENDUM.md, then ROADMAP.md. Working in the code (human or
Claude Code): CLAUDE.md first, then HANDOFF.md's decision log. The
owner's own task list: OWNER.md. Coverage truth: PARKS.md for
trip-ready datasets, COLORADO.md and WASHINGTON.md for the map atlas
(mapped does not mean plannable; the tier labels are the truth).

What works today: availability-aware itinerary search across the
trip-ready parks in PARKS.md (`python3 -m switchback trips <slug> ...`),
trail-true elevation grading, GPX export, a PWA map board with a
rubber-band route builder, cancellation watching with Telegram alerts,
dual-permit availability merging, experimental dispersed-camp pilots,
and long-trail corridor maps. What it is becoming is defined by
PRODUCT.md: complete night-by-night trip plans with frontcountry
arrival nights, explainable recommendations, and an integrated trip
editor.

Tests: `python -m pytest -q` runs the full twelve-suite invariant
battery, offline. Non-coder path: START_HERE.txt and the .bat
launchers. Every surface prints its version; if it does not say
v3.3.0, you are not on this release.
