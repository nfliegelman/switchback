# Switchback

v3.6.3. A constraint-based backcountry trip planner: tell it when you
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

Quality checks: `bash scripts/check.sh` runs the whole gate offline: no
em or en dashes, ruff for dead code, then the full pytest suite. Set the
tooling up once with `pip install -r requirements-web.txt -r requirements-dev.txt`.
GitHub runs that same script automatically on every pull request and every
push to main (.github/workflows/ci.yml, read-only, no secrets); a red mark
on a pull request means a check failed, open it to see which. CI is kept
separate from the board, watch, and release jobs, which are the only
workflows that write to the repo or use secrets. Protecting main so a
failing check blocks a merge is a one-time GitHub setting; see OWNER.md.

Non-coder path: START_HERE.txt and the .bat launchers. Every surface
prints its version from switchback/__init__.py; CHANGELOG.md names the
current release.
