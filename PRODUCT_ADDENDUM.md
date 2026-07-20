# PRODUCT_ADDENDUM.md

Historical Context Addendum to PRODUCT.md. Written v3.3.0 (2026-07-17)
by Claude at the owner's request, after verifying the brief's claims
against the repository. The instruction was candor over defense, and
that cuts both ways: the first correction below is to Claude, not to
the brief.

## 0. A correction to the reviewer, who is me

I verified the brief expecting to find invented file references.
Instead every file it cites exists: SPEC.md, SCOPE.md, FUTURE.md,
PARKS.md, web.py, web_index.html, board.py, history.py,
caltopo_export.py, scoring.json, parks/ratings.json. I have shipped
roughly thirty releases while never opening five of them. The brief
audited the whole repository; I had been operating on the slice of it
that recent sessions touched. Two consequences: the brief's repo
observations deserve default trust, and CLAUDE.md now instructs
sessions to survey the full tree before claiming anything is missing.
The one file the brief names that does not exist is parks/demand.json;
the loader hook for it exists in scoring.py and returns empty.

## 1. Goals, constraints, and decisions the brief missed

The owner cannot read code and operates from a phone most days. Every
consumer surface must survive that: double-click launchers, plain
language PRs, OWNER.md as the human task ledger. The brief's UX vision
is compatible but never states the constraint, and it is the binding
one.

The dash prohibition is an owner directive enforced by a release gate
since v2.6; the brief itself arrived full of em and en dashes and was
sanitized on ingest, the same treatment rec.gov permit names get.

Honesty conventions are already product features, not aspirations:
first-come nights print "no reservation system exists, availability
assumed, arrive early"; dispersed parks carry an experimental flag and
ship only after grading against a published oracle; sparse map fetches
carry an advisory floor note; every edge carries a src citation under a
tiered miles policy (official beats measured beats estimated). The
brief's confidence vocabulary in section 6.3 is a renaming and
formalization of an existing house value, which makes it cheap to
adopt.

Decisions the brief could not know because they postdate or sit outside
its snapshot: trip-shape multi-select shipped at the engine level in
v3.1.0 with the owner's default set (loop, out and back, basecamp);
corridor buffer is 1.0 km by owner decision; the calibration scaffold,
reaction ballots, trail-true gain grading (within one percent of a GPS
log), and toughest-stretch day profiles all exist and the owner
explicitly moved calibration reactions to future todo on 2026-07-17;
the AllTrails detail-approval gate finally cleared, so crowd-volume
data flows when wanted; CLAUDE.md and a session bootstrap landed
v3.2.2 for Claude Code.

One open data bug the brief must inherit: the Maroon Zone anchor node
sits at about 13,450 ft on the West Maroon ridge instead of the
camping valley. Any Elks-adjacent destination is disqualified from
"fully verified" status until it is fixed, and the v2.23 mileage
correction on that corridor is under re-audit for the same root cause.

## 2. Where the brief conflicts with prior decisions

Genuine conflicts are few. The brief parks "expanding map coverage
merely to increase an area count"; the last month did exactly that
wave, deliberately, and finished it (planned atlas rows are zero). No
conflict going forward, but the Archetype B expansion (Sierra
trailhead-quota parks) that I recommended to the owner two days ago
fails the brief's own decision filter and moves to Parked below. I
concur with the demotion; the filter is right and my earlier
recommendation predates it.

The brief's Gap 7 says the solver closes every trip at its starting
entrance. Verified true at solver.py line 155. This quietly corrects
some of our own recent vocabulary: the "mixed" routes in the
calibration ballots also return to their start, and the point_to_point
toggle shipped in v3.1.0 maps to a shape the enumerator never
produces. The shuttle option is now removed from the web UI (done in
v3.3.0) and point_to_point stays engine vocabulary only.

The brief treats profile.json's silent use as a defect; prior sessions
treated it as a feature for a single-owner tool. The brief is right for
the product Switchback is becoming: per-search visible constraints,
with the profile as defaults.

## 3. Looks like scope creep, was strategic

The 72-area atlas and three long-trail corridors look like breadth for
its own sake. They are the boundary rings that power the route
editor's inside/outside legality coloring the brief asks for in
section 12, and they are the permit-free fallback inventory that P1
route repair needs. The spend is sunk and frozen; the asset remains.

The dispersed pilots look experimental. They are the permit-free
fallback engine with the brief's honesty bar already built in: pilots
that fail their oracle get deleted whole (two of three did in v2.27).

The dual-permit merge looks niche. It is availability correctness for
Indian Peaks and the Enchantments, one of which the brief itself names
as a vertical-slice candidate; without it the product would call
bookable nights closed.

Trail-true gain grading and toughest-stretch look like polish. They
are the literal inputs to the brief's card requirements: hardest day,
tradeoff generation, and effort explanation.

The watch and demand-history plumbing looks like a competing alert
product. It is the substrate the brief's P1 complete-trip alerts and
saved-trip re-solving stand on, and the demand history is what will
price camp scarcity in explanations.

The .bat kit and OWNER.md look like non-product overhead. They are the
only test harness the owner can execute, which makes them the delivery
channel for the brief's manual UX test script.

## 4. Technical and data constraints Claude Code must understand

CLAUDE.md at the root is the operating manual and is updated as part of
this release; the load-bearing items: geometry polylines live in
canonical sorted-key orientation and must be re-oriented per edge
before any direction-dependent math; graph.find() returns None on
ambiguity, not just absence; solver.route_nodes() returns a set;
availability merges across dual inventories are MAX per date, never
sum; the engine package is stdlib-only by design; USGS EPQS is dead
from sandbox egress and the elevation order is OpenTopoData ned10m
then open-elevation; Overpass work uses short-leash timeouts with
maps.mail.ru as the reliable mirror and area builds batch three or
fewer; ArcGIS envelopes must be JSON objects and BLM's server cannot
be trusted with LIKE; state files (telegram.json, history.sqlite,
watch state, pdi, caches) never enter commits; tests run offline and
`python -m pytest -q` now runs all twelve suites; the SCOPE.md
principle that a route is an ordered camp list, never freehand
geometry, is why the brief's Edit-this-trip surface is cheap, and it
must not be violated by the editor work.

## 5. Preserve even while de-prioritized

The calibration scaffold, ballots, elevation profiles, and
toughest-stretch display (owner: future todo, infrastructure stays).
The three corridors and the atlas (frozen assets). The dispersed
machinery and its oracle gates. The AllTrails oracle channel, now that
its approval finally works. The watch, Telegram path, board cron, and
demand history. The GPX and CalTopo export path. The GUI, demoted per
the brief to admin utility but kept as the owner's permit-lookup and
spreadsheet tool. FUTURE.md's monetization gates, already archived in
place. HANDOFF.md's decision log in full; it is the project's memory
and the reason this addendum could be written.

## 6. Brief assumptions I believe are incorrect

Fewer than expected, and I say that having just been corrected myself.
parks/demand.json does not exist; the hook does. The preserved-assets
list slightly overstates present scoring inputs accordingly. The
capability audit line calling trip styles "one dropdown" was true of
the UI and understated the engine, where the multi-select shipped in
v3.1.0; the drift ran the direction opposite to implied. The estimate
of "roughly nine trip-ready graph datasets" is close; PARKS.md is
regenerated this release for the exact current count after the RMNP
buildout. The Rainier basecamp-domination example could not be cheaply
reproduced and is accepted as plausible rather than verified. Section
8's Campflare integration assumptions are strategy, not repo fact, and
are adopted as-is. Everything else the brief asserts about the
repository checked out.

## 7. Recommended priority adjustments

Adopt the brief's P0 list with these changes. Add to P0: the Maroon
anchor relocation and edge re-audit, because a data-integrity bug that
manufactures 13,000 ft phantom climbs disqualifies a marquee state
from every quality bar in section 16, and the fix is one focused
session. Add to P0, already done in this release: standard test
discovery, shuttle removal, and the documentation reset itself. Name
the vertical-slice destinations now rather than later; recommendation:
Mount Rainier (the brief's own worked example, mature graph), Rocky
Mountain NP (86 live camps after the v2.26 buildout, rich frontcountry
campgrounds on rec.gov, the owner's home state), and Lena (the
mixed-policy golden scenario in miniature). Indian Peaks is the strong
fourth when dual-permit correctness deserves a showcase. Keep
calibration reactions in P1 exactly where the brief puts scoring
calibration; the owner's future-todo decision and the brief agree, and
the 50-to-100 evaluation target already has its scaffold. Move
Archetype B (Sierra trailhead-quota architecture) from the old roadmap
horizon to Parked until P0 metrics are healthy; it is the definition
of coverage-before-product. Solitude modeling stays Parked per the
brief even though its data source is newly unlocked. Point-to-point
stays P2 and now tells the truth everywhere in the UI. Everything the
brief parks, stays parked, including the monetization gates that were
already parked twice.
