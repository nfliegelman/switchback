# Switchback

v3.4.2. A constraint-based backcountry trip planner: tell it when you
can go and what you can handle, it finds complete trips you can
actually take, checked against live rec.gov availability.

Start here by role. Product direction: project/PRODUCT.md (addendum
first, brief second), then project/ROADMAP.md. Working in the code
(human or Claude Code): CLAUDE.md first, then project/HANDOFF.md's
decision log. The owner's own task list: OWNER.md. Coverage truth:
coverage/COVERAGE.md, one file, tiers first then both state atlases
(mapped does not mean plannable; the tier column is the truth).

What works today: availability-aware itinerary search across the
trip-ready parks in coverage/COVERAGE.md (`python3 -m switchback trips <slug> ...`),
trail-true elevation grading, GPX export, a PWA map board with a
rubber-band route builder, cancellation watching with Telegram alerts,
dual-permit availability merging, experimental dispersed-camp pilots,
and long-trail corridor maps. What it is becoming is defined by
project/PRODUCT.md: complete night-by-night trip plans with frontcountry
arrival nights, explainable recommendations, and an integrated trip
editor.

The layout, in one breath: the root holds this README, OWNER.md (the
owner's task list), CLAUDE.md (the session operating manual), and
CHANGELOG.md (what shipped). project/ holds the working docs that
steer development, plus project/archive/ for retired plans. coverage/
holds the one file the app writes; edit parks/atlas.json and rerun the
command, never the file itself. Code is switchback/, park data parks/,
the published map site docs/, tests tests/.

Tests: `python -m pytest -q` runs the full twelve-suite invariant
battery, offline. Non-coder path: START_HERE.txt and the .bat
launchers. Every surface prints its version; if it does not say
v3.4.2, you are not on this release.
