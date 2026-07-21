# Authorship and Research Integrity Audit: Switchback

Audit date: 2026-07-21. Auditor: Claude Code session (diagnostic phase, no
repository changes made). Target: the Switchback repository at HEAD
`b87e204` (v3.6.1), branch `claude/repository-audit-protocol-udux73`.
Framework: the attached Authorship, Research Integrity, and AI-Residue
protocol. No em or en dashes are used anywhere in this report, per the
house rule.

## Executive result

- Residue score: 26 / 100 (band: 15 to 29, light residue and documentation gaps).
- Evidence confidence: 70 percent (medium-high).
- Application run: PARTIAL. The stdlib engine and the planner workflow were
  run offline and produced correct structured output; the full offline
  test suite was run directly (13 of 15 files green). The 2 that did not
  run (test_web.py, test_plan_api.py) import fastapi at module load and so
  error out here rather than skip; under the standard `python3 -m pytest -q`
  they would surface as 2 failures, meaning the documented "full suite
  green" presumes the web extras (fastapi, uvicorn) are installed, which
  cc_setup.sh and the .bat launchers do on the owner's real machine but
  which are absent in this bare sandbox. test_browser.py self-skips cleanly
  without chromium.
  The FastAPI web server and the live rec.gov availability path could NOT
  be exercised here (fastapi is not installed in this environment and
  outbound rec.gov egress is blocked); the real-browser UI could NOT be
  rendered (Leaflet CDN unreachable, no chromium).
- External research verified: YES, spot-checked. Two load-bearing data
  claims that the current phase depends on were independently confirmed
  against live sources (Ohanapecosh Campground closed for the 2026 season
  for construction; White River Campground is first-come, first-served).
- Critical workflows tested: the OFFLINE planning workflow was tested
  directly (16 golden scenarios pass; a live planner run produced correct
  cards, itineraries, and honesty labels). The LIVE availability workflow
  and the browser UI were NOT testable in this environment.
- Overall classification: STRONGLY AUTHORED with light, well-localized
  residue. This is not a template or a generated prototype. It is a
  single-owner, domain-specific product with an unusually complete
  decision record. Residue concentrates in four places: accessibility,
  a hard third-party CDN dependency, version-string drift across static
  surfaces, and a small set of decisions asserted without visible research
  (the stdlib-only rule and the hand-set scoring or pace weights).
- Highest-risk finding: the entire web UI hard-fails if the Leaflet unpkg
  CDN is unreachable (no fallback, no guard, the service worker does not
  cache it), and the flagship destination (Rainier) has never been
  verified end-to-end by a human or against live inventory (it is honestly
  held at VERIFICATION BLOCKED). The product's core promise is therefore
  unproven in production even though it is proven in tests.
- Strongest authored decision: the research provenance of the engine's
  externally-probed technical choices (elevation source order, rec.gov API
  reverse-engineering, dual-permit MAX-merge, Overpass strategy, solver
  design). These carry dated live probes, exclusion logs, oracle tests,
  ground-truth matches, and disclosed self-corrections. This is the
  opposite of research residue.

## Product truth

- Primary user: one named non-coder, Noah, who plans PNW and Rockies
  backpacking trips and operates mostly from a phone (PRODUCT.md:40,
  CLAUDE.md:23). The delivery model (two double-click .bat files, a phone
  PWA, an OWNER.md task list in plain language) is built entirely around
  this constraint.
- Primary workflow: describe a trip (destination or region, dates, party,
  physical limits, shape preferences), receive multiple complete
  recommendations, inspect a night-by-night itinerary and route,
  understand availability and booking, export or monitor
  (MASTER_COURSE_CORRECTION.md:34 to 39). This is the organizing spine of
  the codebase and the roadmap.
- Owner constraints: cannot read code; wants exactly two entry points
  (phone app, one Windows double-click); no em or en dashes anywhere;
  surgical edits; evidence-based, quantified communication; verify prices
  and market claims before repeating them (HANDOFF.md:9 to 18).
- Security and privacy boundary: a personal, single-user, localhost-only
  tool. The web app binds to 127.0.0.1:8756 with no `--host` override
  (Switchback.bat:31, 39). No accounts, no multi-tenant data, no PII
  beyond the owner's own trip parameters. Telegram alert secrets live in a
  gitignored file or GitHub Actions secrets, never in code.
- Key assumptions the product rests on: (1) rec.gov's undocumented
  permit-itinerary API stays shaped as reverse-engineered; (2) the owner
  will eventually complete the calibration sheet that tunes scoring; (3)
  the owner runs on Windows with Python on PATH; (4) network egress to
  rec.gov, Overpass, and OpenTopoData is available on the owner's machine
  even though it is blocked in the build sandbox.

## Architecture applicability map

| Layer | Status | Current implementation | Evidence | Finding |
|---|---|---|---|---|
| 1. Product form | Required now | Local web app (daily driver) + phone PWA (monitoring) + CLI + Tkinter GUI (admin/spreadsheet) | HANDOFF.md:80; PARKED_FEATURES.md:22 | Authored. Multiple forms, each with a written role. |
| 2. Runtime and hosting | Required now | Local Python process; GitHub Pages for the PWA; GitHub Actions for cron | board.yml, watch.yml; HANDOFF.md:136 | Authored; hosting is validated-inheritance from the owner's prior Actions/Pages projects. |
| 3. Primary framework | Required now | No frontend framework (single-file Leaflet + vanilla JS); FastAPI for the local API | web_index.html; web.py:29 to 31 | Authored, with the no-build choice explicitly flagged revisitable (PRODUCT.md:1699). |
| 4. API or server boundary | Required now | FastAPI, injected fetch_fn/elev_fn for offline testing | web.py:169, 299 | Authored; dependency injection for testability is deliberate. |
| 5. Data persistence | Required now | JSON park datasets + one SQLite history DB | parks/*.json; history.py | Authored; local-first, stdlib sqlite3. |
| 6. Object storage and media | Not required | Static icons in the repo | docs/board/*.png | Correct absence for a personal tool. |
| 7. Authentication | Not required | None | Switchback.bat:31 (localhost bind) | Correct absence; single-user localhost. |
| 8. Authorization | Not required | None | as above | Correct absence. |
| 9. Local state and sync | Required now | profile.json config; watch state JSON; sqlite history | config.py; watch.py | Authored; state owned in the engine layer, not the UI. |
| 10. Background jobs | Required now | Actions cron for board refresh and watch | board.yml, watch.yml | Authored; idempotent, least-privilege. |
| 11. Search | Possibly required | rec.gov permit search proxied | api.py | Authored for the domain. |
| 12. Notifications | Required now | Telegram bot via watch | watch.py; watch.yml | Authored; secrets handled correctly. |
| 13. Payments | Not required | None (monetization parked) | PARKED_FEATURES.md:34 | Correct absence; explicitly parked. |
| 14. Analytics | Not required | None | (no analytics deps) | Correct absence for a personal tool. |
| 15. Logging and observability | Possibly required | Print-to-stderr, Actions logs, run-log naming in release robot | release.yml | Adequate for scale; no structured monitoring (acceptable). |
| 16. UI foundation and styling | Required now | Hand-authored CSS token set (pine/sand/ink), no component library | web_index.html:9 | Authored; strong anti-residue signal (see Category D). |
| 17. Forms and validation | Required now | Plain-language server-side validation with echoed defaults | plans.py:199 to 277 | Authored; validation returns hiker-readable errors. |
| 18. Testing | Required now | 16 test files, offline-by-design, real-browser gate | tests/; test_planner.py | Authored; behavior-focused (see Category J). |
| 19. Deployment and environments | Required now | .bat launchers, cc_setup.sh, Actions | Switchback.bat; scripts/cc_setup.sh | Authored for a non-coder owner. |
| 20. Backups, migrations, recovery | Unknown | history.sqlite snapshot committed to data/; no documented restore/rollback | board.yml; .gitignore | Gap: no explicit backup/rollback doc; low stakes but Unknown. |
| 21. Security controls | Required now | localhost bind, parameterized SQL, secrets via env/Actions | history.py:63; watch.yml | Authored for the threat model. |
| 22. External APIs | Required now | rec.gov, Overpass, OpenTopoData, NHD, ArcGIS, Leaflet/OSM tiles | HANDOFF.md:51 to 66 | Authored, with dated probes and exclusion logs; Leaflet CDN has no fallback (risk). |
| 23. Native/mobile/desktop/extension | Required now | PWA (installable) + Tkinter desktop | manifest.webmanifest; switchback_gui.py | Authored; PWA is domain-appropriate. |
| 24. Accessibility and i18n | Possibly required | Minimal; English only | web_index.html (no ARIA) | Gap: weakest layer (see Category I). i18n correctly absent. |

## Scorecard

| Category | Weight | Score (0 to 3) | Confidence | Summary |
|---|---:|---:|---:|---|
| A. Product specificity and IA | 10% | 0.5 | 85% | One user, one workflow, anti-scope-creep filter, documented shell-to-task IA migration. Minor: an unreconciled owner-capability contradiction and three overlapping entry points. |
| B. Research integrity and provenance | 15% | 0.7 | 75% | Exceptional provenance for externally-probed technical decisions; a few honestly-labeled asserted defaults (stdlib-only rationale absent; scoring/pace hand-set pending calibration). |
| C. Stack, service, architecture fit | 15% | 1.0 | 75% | Proportionate local-first design, justified forms. Main ding: a hard Leaflet CDN dependency with no fallback. |
| D. Visual system and composition | 12% | 0.5 | 80% | Coherent bespoke palette, zero gradient/glass/bento/hero residue, domain-specific map marks. Minor: color-only map status; off-brand Tkinter theme. |
| E. Interaction and state completeness | 12% | 1.0 | 75% | Honest empty/error/offline states, quantified relaxations, freshness stamps. Gaps: destructive quit with no confirm, no focus management, one silent swallow, one raw alert. |
| F. Copy and content integrity | 6% | 0.75 | 85% | Domain-correct consistent terminology, plain-English summary, no promotional filler. Ding: README self-contradicts on version (v3.4.3 vs shipped 3.6.1). |
| G. Frontend, component, code architecture | 10% | 1.0 | 80% | Typed contract, DI, no framework bloat, behavior tests. Residue: broad except clauses, dead root demo files, duplicate imports (coverage.py) and helpers (web/board), version constants hardcoded in three places. |
| H. Backend, data, authorization, security | 10% | 1.0 | 80% | localhost bind, parameterized SQL, no secrets in code, least-privilege CI. A cluster of small unexamined edges (see finding 7): unauth os._exit quit, retry-less Telegram send, no schema migrations, GET-mutates-disk, sanitize-not-at-ingest, incomplete requirements.txt. |
| I. Accessibility and performance | 6% | 1.75 | 75% | Weakest area: no ARIA, no h1, broken heading order, one sub-AA color, color-only map status, hard CDN dependency. |
| J. Testing, deployment, recovery, docs | 4% | 0.75 | 80% | Offline suite green, real-browser gate, golden scenarios, idempotent release robot, extraordinary decision log. Ding: version drift; no restore/rollback doc. |

Weighted residue (each category score mapped to 0 to 100 by score/3, times
weight, summed): approximately 26. Band: 15 to 29, light residue and
documentation gaps.

## Decision-provenance map

| Decision | Classification | Evidence | Research quality | Validation | Risk |
|---|---|---|---|---|---|
| Elevation source order (OpenTopoData ned10m, then open-elevation; EPQS rejected) | Authored | HANDOFF.md:116; EXPERIMENTS.md:16, 21 | High: exclusion log + dated probe | 11 of 11 elevations delivered where EPQS failed | Low |
| rec.gov API reverse-engineering (endpoints, User-Agent, negative clamp) | Authored | HANDOFF.md:53 to 57 | High: live probes with a dated self-correction | CLI verified live vs Glacier ELF | Medium (undocumented upstream API) |
| Dual-permit availability MAX-merge (never sum) | Authored | HANDOFF.md:114; EXPERIMENTS.md:37 | High: domain reasoning + idempotency | Live proof (Cascade Creek 5 open on the 3-day channel) | Low |
| Solver as ordered camp list, virtual origin/sink, backward feasibility | Authored | SPEC.md:25, 200; HANDOFF.md:73 to 74 | High: rationale + cost argument | Synthetic parity oracle test | Low |
| Overpass mirror strategy + coverage gate | Authored | HANDOFF.md:59, 130; CLAUDE.md:79 | High: learned via live congestion | 70 percent node-coverage acceptance gate | Low |
| Local web app + FastAPI CORS backend + no-build Leaflet | Authored (form) / Generated-default (no-build frontend, flagged revisitable) | HANDOFF.md:80; PRODUCT.md:1699 | Medium: owner criterion + CORS reason; framework question left open | Booted live once (map + a real trips call) | Medium (CDN dependency) |
| PWA on GitHub Pages + service-worker cache policy | Authored + Validated-inheritance | HANDOFF.md:126, 136 | Medium-high: per-resource reasoning; hosting inherited from prior projects | Board cron runs daily | Low |
| Corridor buffer_km = 1.0 | Authored (owner decision on a documented tradeoff) | EXPERIMENTS.md:33; HANDOFF.md:104 | Medium-high: size-vs-capture tradeoff laid out, then decided | Rebuilt all three corridors same day | Low |
| stdlib-only engine | Generated-default / Unvalidated-inheritance | CLAUDE.md:18; PRODUCT.md:140; requirements.txt | Low: asserted "by design", no rationale, no comparison | Architecturally real (deps are GUI/web only) | Low (constraint is benign) |
| Scoring weights (day_fit asymmetric, camp 0.6, lakes 0.15) | Generated-default, honestly labeled | scoring.json:2, 11; SPEC.md:147; HANDOFF.md:85 | Low: hand-set "guesses"; calibration scaffold pending | Not calibrated; owner sheet not returned | Medium (product quality rests on untuned weights) |
| Pace bands | Generated-default from a named function (Tobler), honestly labeled | HANDOFF.md:87; BACKLOG.md:33 | Low-medium: Tobler-informed, pending owner GPX | Half-speed doubling verified in tests | Low-medium |
| Frontcountry data (Ohanapecosh closed 2026, White River first-come) | Authored + externally verified | HANDOFF.md:88; CURRENT_PHASE.md:24; and this audit's live check | High: corrected by a live audit, re-confirmed here | Both claims verified against live sources today | Low |

## Per-layer research sufficiency

| Layer | Candidates | Primary sources | Operational evidence | Adversarial review | Validation | Contradictions | Confidence | Result |
|---|---:|---:|---:|---|---|---|---|---|
| Elevation source | 3+ (EPQS, OpenTopoData, open-elevation, Open-Meteo) | Yes, dated | Yes | Yes (EPQS retried before rejecting) | Yes (11 of 11) | Disclosed (transient vs blocked) | High | Authored |
| rec.gov API | N/A (the only source) | Yes, dated probes | Yes | Yes (permission-vs-proximity self-correction) | Yes (live CLI) | Disclosed | High | Authored |
| Dual-permit merge | 2 (sum vs max) | Domain reasoning | Yes (live Cascade Creek) | Yes (Group false-match check) | Yes (idempotent) | None | High | Authored |
| Solver model | 2 (camp list vs freehand geometry) | Design rationale | Yes (live Glacier) | Yes (ambiguity case) | Yes (oracle) | None | High | Authored |
| Overpass/OSM | Multiple mirrors + NHD/gov fallback | Yes | Yes | Yes (partial-extract catch) | Yes (coverage gate) | Disclosed | High | Authored |
| Web architecture | 3 named (terminal, Tkinter, local web) | Owner criterion + CORS | Yes (booted once) | Partial | Partial (offline only) | None | Medium | Authored (form) |
| Frontend build | 2 (no-build vs framework) | Pragmatic | Yes | No (question left open) | No | None | Medium | Generated-default, flagged |
| stdlib-only | 1 (asserted) | None | N/A | No | N/A | None | Low | Generated-default |
| Scoring model | 1 (hand-set) | SPEC section 4 | No (uncalibrated) | No | No (owner sheet pending) | None | Low | Generated-default, labeled |
| PWA cache | Per-resource reasoned | iOS/manifest facts | Yes (daily cron) | Partial | Partial | None | Medium-high | Authored |
| Corridor buffer | 3 values weighed (1.0/1.5/2.0) | File-size vs capture | Yes | Partial | Yes (rebuilt) | Evolution disclosed (1.5 to 1.0) | Medium-high | Authored |

## Critical research failures

Using the rubric's red-flag list, the findings are mild and mostly
disclosed rather than concealed. There are no fabricated citations, no
obsolete-version claims presented as current, and no toy benchmark passed
off as production proof. The genuine flags:

1. Competitor pricing is dated but not inline-sourced. FUTURE.md:52 and
   BACKLOG.md:89 quote Campnab, Outdoor Status, PeakPeeker, and
   PermitAlert prices "as of July 2026" with no links, while the owner's
   own rule (HANDOFF.md:17) demands verifying prices against real sources.
   The verification may have happened off-doc; the provenance is not shown.
   Severity: mild.
2. Self-projected monetization economics. PRODUCT.md:1979 proposes a
   "$39 to 59/year" price and an ARR table. This is owner strategy, not
   researched market data, and is labeled not-P0, so it is acceptable as a
   projection but is a self-generated default, not evidence.
3. Single-chain accuracy benchmark. The dem_trail "+1 percent vs GPS"
   claim rests on one chain against one GPS log (EXPERIMENTS.md:44). It is
   honestly scoped and not overclaimed, but n = 1.
4. Two asserted-without-research defaults: the stdlib-only rule has no
   stated rationale anywhere, and the scoring/pace weights are hand-set
   "guesses" (scoring.json:11) awaiting a calibration that has not
   happened. Both are honestly labeled, so they are transparency-preserving
   defaults rather than concealed ones, but they govern real product
   behavior (ranking quality).

Counterweight (genuine research integrity, credited): failed pilots deleted
whole rather than shipped half-built (HANDOFF.md:108, two of three dropped
on oracle failure); the flagship destination demoted to VERIFICATION
BLOCKED when its complete-trip label proved premature (COVERAGE_STATUS.md:28);
sandbox availability results explicitly refused as unreliable
(HANDOFF.md:91); a reviewer self-correction admitting a thirty-release blind
spot and naming the one hallucinated file (PRODUCT.md:26 to 38); a
mileage-weighted containment metric adopted after node-fraction was found
to underread (HANDOFF.md:115). These are the behaviors the rubric is
designed to reward.

## Top findings

### 1. The web UI hard-fails without the Leaflet CDN, and the flagship trip is unverified in production
- Category: C (architecture fit) and E (state completeness), with I (reliability).
- Evidence: `web_index.html:7,100,103` load Leaflet from `unpkg.com` with no
  SRI and no local fallback; the first executable line, `const map =
  L.map('map', ...)`, throws if `L` is undefined, aborting the entire
  inline script (parks load, plan form, adventure mode never initialize).
  `docs/board/sw.js:14` early-returns on cross-origin requests, so the PWA
  service worker never caches Leaflet, meaning even an "installed" board
  has no map engine offline. The project's own docs confirm this is a live
  failure mode (HANDOFF.md v3.4.3 entry: "outbound proxy tunnels to
  unpkg.com fail, so the full page never runs in a real browser from
  here"). Separately, Rainier, the one destination the whole current phase
  is proving, is honestly classified VERIFICATION BLOCKED
  (COVERAGE_STATUS.md:28): no human has taken or fully dry-run a
  recommended trip, and no live rec.gov run has confirmed the booking
  links resolve.
- Decision provenance: Generated-default (no-build single file), explicitly
  flagged as revisitable (PRODUCT.md:1699).
- Severity: HIGH (this is the single point of failure for the product's
  primary surface, plus an unproven core promise).
- User impact: if unpkg is down, slow, or blocked, the owner sees a dead
  blank page with no explanation. The offline PWA, the product's phone
  story, has no map without a warm HTTP cache.
- Technical impact: total UI outage from one third-party dependency; no
  graceful degradation.
- Confidence: HIGH on the CDN fragility (verified in code and corroborated
  by the repo's own notes); HIGH on the verification-blocked status.
- Recommended correction: vendor Leaflet locally (self-host the ~140 KB
  JS/CSS next to the app), or add an `if (!window.L)` guard that renders a
  plain "map failed to load" message and still lets the text-based plan
  results render. Precache Leaflet in the service worker.
- Research required before correction: confirm Leaflet's license permits
  redistribution (BSD-2, it does) and pick the pinned version already in
  use (1.9.4).
- Validation required: load the page with the network throttled or unpkg
  blocked and confirm the plan flow still works.
- Estimated effort: 1 to 2 hours.
- Migration or regression risk: low (self-hosting a pinned asset).

### 2. Version strings drift across static surfaces (board, service worker, README) while the engine is v3.6.1
- Category: F (content integrity) and J (docs).
- Evidence: `switchback/__init__.py:2` is `3.6.1` and `CHANGELOG.md:5` tops
  at v3.6.1, but `docs/board/index.html:183` hardcodes "switchback v3.4.3",
  `docs/board/sw.js:1` keys the cache to `sb-shell-v3430`, and `README.md:3,35`
  says v3.4.3 and even asserts "if it does not say v3.4.3, you are not on
  this release." OWNER.md tells the owner the board should read v3.6.1,
  which the board code contradicts.
- Decision provenance: Accidental (static surfaces not updated with the
  dynamic ones).
- Severity: MEDIUM (erodes the honesty the product otherwise enforces; the
  stale service-worker cache key can serve returning PWA users an old
  shell).
- User impact: the owner is told to check for v3.6.1 and will see v3.4.3;
  the README makes a false self-verifying claim.
- Technical impact: `sb-shell-v3430` never invalidates on a board change,
  so clients can keep an old page (the exact failure the SHELL constant
  exists to prevent).
- Confidence: HIGH (verified first-hand).
- Recommended correction: source the board footer and README version from
  `__version__` (or a generated constant), and bump the SHELL string on any
  board change (the repo already documents this rule at HANDOFF.md:126).
- Research required: none.
- Validation required: load the board, confirm the footer and a bumped
  cache key.
- Estimated effort: under 1 hour.
- Migration or regression risk: none.

### 3. Accessibility is the weakest layer: no ARIA, no heading landmarks, one sub-AA color, color-only map status
- Category: I (accessibility) with E.
- Evidence: repo-wide there are no `aria-`, `role=`, `tabindex`, or custom
  `:focus` rules in `web_index.html` or `docs/board/index.html`; there is
  no `<h1>` and the web app jumps to `<h3>` (web_index.html:323,471,478);
  the board has no headings at all. The muted gray `#7a746a` used for the
  legend, timestamps, and hints computes to about 4.1:1 on the sand
  background (below the 4.5:1 AA threshold). Map camp status is encoded by
  fill color only (web_index.html:165; board:68); in grayscale, open and
  full collapse together. Async result panels mutate innerHTML with no
  `aria-live`.
- Decision provenance: Accidental (a11y was never in scope).
- Severity: MEDIUM overall, higher for the public PWA than for the
  localhost app used by one sighted owner.
- User impact: low for the current single known user; real for the
  Pages-hosted board, which is public.
- Technical impact: fails several WCAG AA checks.
- Confidence: HIGH (agent-verified with computed ratios).
- Recommended correction: add one `<h1>` per page, a visible focus style, a
  text or shape channel alongside map color (the tooltips already carry the
  words; add a shape or pattern), and darken the muted gray to about
  `#6b6459` for AA.
- Research required: none (standard WCAG).
- Validation required: an axe or Lighthouse pass and a keyboard walkthrough.
- Estimated effort: 2 to 4 hours.
- Migration or regression risk: none.

### 4. Two consequential decisions are asserted without visible research: the stdlib-only rule and the scoring/pace weights
- Category: B (research integrity).
- Evidence: the stdlib-only constraint is stated as "by design" with no
  rationale, comparison, or benefit anywhere (CLAUDE.md:18; PRODUCT.md:140).
  The scoring weights are labeled "hand-set guesses per SPEC section 4"
  (scoring.json:11) and the calibration that would replace them requires an
  owner reaction sheet that has not been returned (BACKLOG.md:18; OWNER.md).
  The day_fit asymmetry, a consequential ranking change, was owner opinion,
  not data (HANDOFF.md:85).
- Decision provenance: Generated-default, both honestly labeled.
- Severity: LOW for stdlib-only (a benign, even helpful constraint for
  distributability); MEDIUM for scoring (ranking quality, the product's
  differentiator, rests on untuned weights).
- User impact: recommendation ordering may not match the owner's real
  preferences until calibration happens.
- Technical impact: none structural; the weights are externalized in
  scoring.json and easy to retune.
- Confidence: HIGH.
- Recommended correction: write one paragraph of rationale for stdlib-only
  (distributability, zero-install, auditability) so it is a decision rather
  than a habit; and treat completing the calibration sheet as the gating
  task it already is in the backlog.
- Research required: the calibration itself (the owner's reactions to a set
  of ranked trips).
- Validation required: re-run the golden scenarios after any weight change.
- Estimated effort: rationale under 1 hour; calibration is owner-gated.
- Migration or regression risk: low.

### 5. Small interaction-state gaps: destructive quit with no confirmation, one silent swallow, one raw alert
- Category: E (interaction and state completeness).
- Evidence: the quit trigger is a 4-letter link inside the map copyright
  line (web_index.html:105) that immediately POSTs to `/api/quit`, which
  runs `threading.Timer(0.4, lambda: os._exit(0))` (web.py:169 to 173); no
  `confirm()` exists anywhere in the repo. Availability-refresh errors are
  swallowed to `console.log` only (web_index.html:168), leaving stale dots
  with no user notice. GPX export failure uses a raw `alert()`
  (web_index.html:496), the only JS dialog in an otherwise inline-message
  app.
- Decision provenance: Accidental (edge affordances not hardened).
- Severity: LOW (localhost, single user), but the quit is a genuine
  one-misclick-kills-the-app hazard.
- User impact: an accidental click on "quit" terminates the server with no
  warning; a silent availability failure can mislead.
- Technical impact: minor.
- Confidence: HIGH (verified in code).
- Recommended correction: add a confirm step (or move quit out of the map
  footer), surface availability-refresh failures as an inline warning, and
  replace the alert with the app's existing warn div.
- Research required: none.
- Validation required: manual click-through.
- Estimated effort: 1 to 2 hours.
- Migration or regression risk: none.

### 6. The owner's own capability is described two contradictory ways
- Category: A (product specificity).
- Evidence: HANDOFF.md:7 calls Noah a "strong Python builder (has shipped
  multiple quant models with GitHub Actions and Pages dashboards)"; CLAUDE.md:23
  and PRODUCT.md:40 say he "cannot read code." The entire delivery model
  (.bat launchers, OWNER.md, plain-language PRs) rests on the second
  premise. The two are never reconciled.
- Decision provenance: Unknown (documentation drift about the primary user).
- Severity: LOW, but it is the foundational product assumption.
- User impact: none directly, but it muddies decisions about how much to
  automate versus expose.
- Confidence: HIGH (both quotes verified).
- Recommended correction: one sentence reconciling the two (for example,
  "builds quant models but does not read this codebase and operates from a
  phone").
- Research required: ask the owner.
- Estimated effort: minutes.
- Migration or regression risk: none.

### 7. A cluster of small unexamined backend edges
- Category: H (backend, data, security) with G and C.
- Evidence: (a) `requirements.txt` omits the deps the code actually imports
  (fastapi, uvicorn, pydantic, shapely); the real install list lives only in
  scripts/cc_setup.sh:5 and the .bat launchers, so `pip install -r
  requirements.txt` cannot run the web server. (b) `send_telegram` (watch.py:84)
  has no retry or try/guard, unlike `api._get_json` which retries three
  times, and it is called unguarded at watch.py:165, so a single transient
  Telegram outage raises out of a watch cycle. (c) `coverage.py:51` is the
  one genuinely silent `except Exception: pass` in the engine, which will
  mask a real graph-build failure in the coverage survey. (d)
  `coverage.py:133 to 134` import `json as _json` twice on consecutive
  lines (plus a redundant re-import at :107); `_codes_filter` and `_coords`
  are duplicated between web.py and board.py. (e) history.py has no schema
  versioning or migration path (only CREATE TABLE IF NOT EXISTS), so a
  future column change has no upgrade route. (f) any availability-touching
  GET writes parks/history.sqlite as a side effect (api.py:131), a
  surprising REST semantic (deliberate, but a GET mutating disk). (g) the
  house dash rule is enforced by curation plus a manual grep gate, not by
  ingest-path code: extract_park (extract.py:62) does not sanitize
  camp/division/entrance names; only three display-name sites call the
  replace. The rule holds today (the tree is clean) but by discipline, not
  by systematic code.
- Decision provenance: mix of Generated-default (requirements.txt,
  duplicate imports) and Accidental (retry omission, silent swallow).
- Severity: LOW individually and for the localhost/single-user threat
  model, but the rubric asks that clusters of unexamined defaults be
  flagged, and this is one.
- User impact: a transient Telegram failure can drop a cloud watch cycle
  (the next 30-minute cron recovers it); a fresh contributor cannot install
  the web deps from the manifest.
- Technical impact: minor reliability and maintainability drag.
- Confidence: HIGH (all verified in code).
- Recommended correction: add a `requirements-web.txt` (or extras) listing
  fastapi/uvicorn/pydantic/shapely; wrap `send_telegram` in the same retry
  as `_get_json`; narrow or log the coverage.py swallow; delete the
  duplicate imports and de-duplicate the two helpers; add a one-line schema
  version to the history DB; and either move dash sanitize into extract_park
  or keep the manual gate but document that it is the real enforcement.
- Research required: none.
- Validation required: `pip install` from the new manifest boots the web
  app; a simulated Telegram 500 does not crash the watch loop.
- Estimated effort: 2 to 3 hours total.
- Migration or regression risk: low.

## Fast removals

- Delete or clearly quarantine the orphaned root demo files
  `belly_river_adventure.py` and `belly_river_graph.json`: the graph data
  was folded into `parks/edges/glacier_edges.json` (its own note says so),
  and nothing imports either file. Keeping them is documented historical
  retention, so this is optional, but they clutter the root the owner is
  told to keep to four markdown files.
- Remove the stale `v3.4.3` self-claim sentence in README.md (finding 2).
- Replace the raw `alert()` in web_index.html:496 with the existing warn div.
- Delete the duplicate `import json as _json` lines in coverage.py:133 to 134
  and the redundant re-import at coverage.py:107.

## Structural corrections

- Vendor Leaflet locally and add a `window.L` guard (finding 1). This is the
  highest-leverage structural change; it converts the primary surface from
  "fails closed on a third-party outage" to "degrades gracefully."
- Drive every user-visible version string from `__version__` (finding 2).
- Add the minimal accessibility layer: one h1 per page, focus styles, a
  non-color status channel on the map, and one darker muted color
  (finding 3).
- Close the owner-verification gates for Rainier (an owner browser
  walkthrough and one live-network run) so the flagship promise is proven,
  not just tested. This is already the top of CURRENT_PHASE.md; the audit
  simply confirms it is the correct next milestone.

## Decisions to retain

- FastAPI for the local API: a common, well-maintained choice used for a
  real reason (a local backend to escape browser CORS against rec.gov,
  HANDOFF.md:80), with dependency injection that keeps the test suite
  offline. Retain.
- No-build single-file Leaflet frontend: proportionate to a one-owner tool;
  avoids a build toolchain the owner cannot operate. Retain, but fix the
  CDN dependency (finding 1). The framework question is already open in the
  docs, which is the right posture.
- stdlib-only engine: benign and arguably a strength (zero-install,
  auditable, distributable). Retain; just write down why (finding 4).
- SQLite for history: correct local-first, transactional store; parameterized
  queries; fail-silent by design so a logging error never breaks a fetch.
  Retain.
- GitHub Pages plus Actions cron: validated-inheritance from the owner's
  prior working projects, least-privilege permissions, idempotent release
  automation. Retain.
- The typed TripPlan contract and the complete-night invariant (plans.py):
  this is the product's spine and is genuinely well-built. Retain and
  protect.
- The coverage classification ladder and the honesty labels: retain; they
  are the product's integrity backbone.

## Missing evidence and unknowns

- Live rec.gov behavior: not observable here (egress blocked). The API
  shape is taken on the repo's dated probes, which are credible but could
  drift upstream at any time.
- Real-browser rendering: not observable here (Leaflet CDN unreachable, no
  chromium). The repo mitigates with a playwright test that self-skips when
  chromium is absent (it skipped here); the owner's browser drive remains
  the first true render.
- The FastAPI web server was not booted here (fastapi is not installed in
  this environment; installing it was out of scope for a diagnostic phase).
  The offline TestClient tests that exercise `/api/plan` also could not run
  here for the same reason (they skipped, they did not fail).
- Backup and restore: no documented procedure for the SQLite history beyond
  the daily committed snapshot; restore is untested.
- Scoring quality: unquantifiable until the owner completes the calibration
  sheet; today's ranking rests on hand-set weights.
- Owner-side Windows workflow: the .bat launchers could not be exercised on
  Windows from here.

## Recommended remediation order

1. Fix the Leaflet CDN single point of failure (vendor locally plus a
   guard, and precache in the service worker). Highest user-facing risk,
   1 to 2 hours. (Finding 1)
2. Unify version strings from `__version__` and bump the service-worker
   SHELL. Restores the product's own honesty discipline, under 1 hour.
   (Finding 2)
3. Close the Rainier verification gates (owner browser walkthrough plus one
   live-network run). Proves the core promise; already the active phase.
   (Finding 1, second half)
4. Harden the interaction edges: confirm-on-quit, surface the swallowed
   availability error, replace the alert. 1 to 2 hours. (Finding 5)
5. Add the minimal accessibility layer. 2 to 4 hours, and more valuable for
   the public PWA than the local app. (Finding 3)
6. Write the stdlib-only rationale and treat the calibration sheet as the
   gating task it is. (Finding 4)
7. Clear the backend hygiene cluster: a web extras manifest, a retry on
   send_telegram, and the duplicate-import and helper de-duplication. 2 to 3
   hours. (Finding 7)
8. Reconcile the owner-capability contradiction and remove the orphaned
   root demo files. Minutes each. (Findings 6 and fast removals)

## What could change this audit

- A live rec.gov run that the booking links resolve and inventory matches
  would move Rainier from VERIFICATION BLOCKED toward verified and lift
  Category C and the executive risk finding.
- Booting the FastAPI app and rendering the real browser UI could surface
  interaction or state defects not visible in code (the repo's own history
  shows a real-browser test once caught a form-crash that a DOM stub
  passed, HANDOFF.md:88), which would raise Category E residue.
- Completing the scoring calibration would convert the largest
  asserted-default (Category B, finding 4) into an authored, validated
  decision and lower the B and overall score.
- Evidence that the competitor pricing in FUTURE.md and BACKLOG.md was
  actually source-verified (per the owner's own rule) would clear the one
  standing research flag.
- A dependency or platform change (adopting a frontend framework, or a
  rec.gov API change) would require re-running the Category C and B
  sufficiency tables.
