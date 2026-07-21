# CLAUDE.md

Operating manual for Claude Code sessions in this repository. Read project/HANDOFF.md before doing anything else; its decision log is the
project's memory and it wins every argument with this file. For product
direction (what to build and why), read project/MASTER_COURSE_CORRECTION.md
(the newest directive, supersedes conflicting older priorities), then
project/CURRENT_PHASE.md for where the work stands, then
project/ROADMAP.md; project/PRODUCT.md is background and yields to the
directive. SURVEY THE FULL FILE TREE before
claiming anything is missing; a prior reviewer shipped thirty releases
without opening five root docs that existed the whole time.

## What this is

Switchback is a constraint-based backcountry itinerary engine owned by a
non-coder. It plans multi-night trips against live rec.gov availability
across 72 mapped landscapes in Colorado and Washington, watches for
cancellations, and renders a PWA map. The engine package is stdlib-only
by design; keep it that way.

## The owner

Noah cannot read code. Every PR description must explain what changed
and why in plain language a hiker understands. OWNER.md is his task
list; if your change creates or closes an owner task, update OWNER.md
in the same PR. Never ask him to run commands beyond double-clicking a
.bat file or filling in a text file.

## Hard rules, no exceptions

1. NO EM DASHES OR EN DASHES anywhere in any file, ever, including
   docs, code comments, JSON data, and commit messages. Rec.gov permit
   names sometimes carry en dashes into fetched data; sanitize on
   ingest. Gate before every commit:
   `grep -rlP '\x{2013}|\x{2014}' --include='*.py' --include='*.md' --include='*.json' . && echo FAIL || echo CLEAN`
2. Surgical edits. Change the fewest lines that do the job. Never
   reformat, resort, or "clean up" untouched code.
3. Decisions get written down the same session they are made: durable
   conventions and hard-won facts go in project/HANDOFF.md's decision log
   (newest first), deferred work goes in project/BACKLOG.md, experiment
   results in project/EXPERIMENTS.md.
4. Version bumps are for meaningful, user-testable milestones ONLY
   (owner directive 2026-07-20, supersedes the old version-per-PR
   habit). Routine and documentation-only work ships without a bump.
   When a milestone does bump: switchback/__init__.py, a CHANGELOG.md
   entry (prose, no bullets), and the vX.Y.Z: commit-subject
   convention so the release robot can tag it.
5. Full quality gate green before any push. The canonical gate is
   `bash scripts/check.sh` (dash sweep, ruff pyflakes, pytest); CI runs
   that same script read-only on every pull request and push to main
   (.github/workflows/ci.yml). Install the tooling once with
   `pip install -r requirements-web.txt -r requirements-dev.txt`. The
   bare test command is still `python3 -m pytest -q` (discovers
   everything);
   `for t in tests/test_*.py; do python3 $t >/dev/null || echo FAIL $t; done`
   is the no-pytest fallback. Tests run offline by design; keep them
   that way. Ruff lints pyflakes only (real defects, not house style);
   config in ruff.toml.
6. Never commit state: telegram.json, parks/history.sqlite*,
   parks/.watch_state.json, parks/pdi.json, parks/.osm_cache/,
   permit_exports/, docs/CALIBRATION_NOTES.md. The .gitignore covers
   these; do not weaken it.
7. Defer whole, never half-built. If a feature cannot finish in the
   session, record the design and land nothing, rather than landing a
   stub.

## Domain traps that have each cost a session

- Geometry polylines are stored in canonical sorted-key orientation.
  Any consumer computing direction-dependent quantities (gains, GPX,
  profiles) MUST orient to its own a-to-b first. Unoriented use graded
  every descent as a climb once.
- graph.find() returns None on AMBIGUOUS names, not just missing ones.
  "Maroon Zone" matches multiple camps; use the full division name.
- solver.route_nodes() returns a SET. Never index it.
- Trip day lists include the exit leg but camp sequences do not; derive
  the exit hop from trip shape (loop, out_and_back, lollipop, basecamp
  end at the entrance) or nearest-by-trail entrance for mixed.
- ArcGIS envelope parameters must be JSON objects, not comma strings.
  BLM's server rejects UPPER() and is unreliable with LIKE; use exact
  NLCS_NAME or a spatial envelope.
- USGS EPQS is dead from sandbox egress. Elevation source order:
  OpenTopoData ned10m (100 points per call, 1 second between calls),
  then open-elevation. Meters times 3.28084.
- Overpass: maps.mail.ru answers when others hang. Tiny bboxes can hang
  a full mirror timeout; use short-leash timeouts (25s query, 35s
  socket) and retry. Batch area builds three or fewer per command.
- Availability merge across dual permits is MAX per date, never sum;
  a party books within one inventory.
- Miles policy tiers: official published figures beat geometry
  measurements beat estimates; geometry may replace curated miles only
  for recall-grade networks. Cite src on every edge.
- KNOWN OPEN BUG: the Maroon Zone anchor node 4675333025 sits at about
  13,450 ft on the West Maroon ridge instead of the camping valley.
  Elks distances and profiles near that node are suspect; the fix plan
  is in BACKLOG.md. The v2.23 mileage correction on that corridor is
  under re-audit for the same reason.
- Corridor buffer_km is 1.0 BY OWNER DECISION. Do not change it.

## Commands you will actually use

- `python3 -m switchback trips <slug> --start Y-M-D --end Y-M-D
  --nights N --trip-types "loop,out and back,basecamp"` live search
- `python3 -m switchback calibrate <slug> ...` owner reaction sheet
- `python3 -m switchback dem-trail <slug>` trail-true gains (resumable)
- `python3 -m switchback corridor <slug> --max-tiles N` (resumable)
- `python3 -m switchback area <slug>` landscape build from atlas row
- `python3 -m switchback atlas` regenerate coverage/COVERAGE.md
- `python3 -m switchback merge-inventory <slug> <permit_id>` dual permit
- `python3 -m switchback watch <slug> --inject --once` alert test

Live commands need network egress to recreation.gov, overpass mirrors,
api.opentopodata.org, and the ArcGIS services named in areas.py. If the
session environment has no network, do code-and-tests work only and say
so in the PR.

## Where things live

parks/*.json park data; parks/edges/ edge specs with provenance;
parks/geometry/ display polylines; parks/frontcountry/ curated
arrival and recovery campgrounds; parks/atlas.json the landscape
registry; docs/areas/ built landscape maps plus index.json manifest;
docs/board/ the PWA (bump the sw.js SHELL string when changing it);
switchback/ the engine (plans.py the request and TripPlan contract,
planner.py the orchestration above the solver, frontcountry.py the
curated-stay loader); tests/ offline suite; root markdown is README,
OWNER, CLAUDE, CHANGELOG only; project/ the working docs
(MASTER_COURSE_CORRECTION, CURRENT_PHASE, PARKED_FEATURES,
COVERAGE_STATUS, PRODUCT, ROADMAP, SPEC, HANDOFF, BACKLOG,
EXPERIMENTS, archive/FUTURE.md);
coverage/COVERAGE.md the generated coverage truth, written by the app.
