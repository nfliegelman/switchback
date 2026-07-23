"""Switchback CLI. M0 scope: search, availability, profile.

Examples:
    python -m switchback search "glacier wilderness"
    python -m switchback availability 4675321 --start 2026-09-01 --end 2026-09-07 --filter "ELF -"
    python -m switchback profile
"""
import argparse
import sys
from datetime import date, timedelta

from .api import search_permits, get_divisions, fetch_availability_rows
from .config import load_profile, PROFILE_PATH
from .extract import extract_park, save_park, summary
from .features import annotate, feature_summary
from .graph import Graph
from .solver import Solver, fetch_for_graph
from .scoring import Scorer
from .report import format_trips


def cmd_search(args):
    results, err = search_permits(args.query)
    if err:
        sys.exit(f"search failed: {err}")
    for r in results:
        print(f"{r['permit_id']:>12}  {r['name']}  |  {r['park']}")


def cmd_availability(args):
    info, err = get_divisions(args.permit_id)
    if err:
        sys.exit(f"couldn't load permit {args.permit_id}: {err}")
    divisions = info["divisions"]
    if args.skip_group:
        divisions = [d for d in divisions if not d["is_group"]]
    if args.filter:
        divisions = [d for d in divisions
                     if args.filter.lower() in (d["name"] or "").lower()]
    if not divisions:
        sys.exit("no divisions match that filter")
    print(f"{info['permit_name']}: {len(divisions)} divisions", file=sys.stderr)

    def prog(f):
        pct = round(f * 100)
        if pct % 10 == 0:
            print(f"  fetching {pct}%", end="\r", file=sys.stderr)

    rows, errors, njobs = fetch_availability_rows(
        args.permit_id, divisions,
        date.fromisoformat(args.start), date.fromisoformat(args.end),
        only_available=args.only_available, progress=prog)
    print(" " * 30, end="\r", file=sys.stderr)

    print(f"{'camp_or_zone':<34} {'type':<20} {'date':<10} "
          f"{'rem':>5} {'status':<13} walkup lake")
    for r in rows:
        rem = "" if r[5] is None else r[5]
        print(f"{(r[0] or '')[:33]:<34} {(r[1] or '')[:19]:<20} {r[3]:<10} "
              f"{str(rem):>5} {r[4]:<13} {r[8]:^6} {r[9]:^4}")
    print(f"{len(rows)} rows"
          + (f", {errors}/{njobs} requests errored" if errors else ""),
          file=sys.stderr)


def cmd_extract(args):
    park = extract_park(args.permit_id, slug=args.slug)
    path = save_park(park, args.out_dir)
    print(summary(park))
    print(f"wrote {path}")


def cmd_features(args):
    from .features import BBOXES, prefetch
    bbox = tuple(float(x) for x in args.bbox.split(",")) if args.bbox else None
    if args.prefetch:
        done, total = prefetch(bbox or BBOXES[args.slug], args.budget)
        print(f"{'COMPLETE' if done == total else 'PARTIAL'} {done}/{total}")
        return
    park = annotate(args.slug, bbox=bbox)
    print(feature_summary(park))


def cmd_graph(args):
    g = Graph(args.slug)
    print(g.report())
    if args.leg:
        a, b = g.find(args.leg[0]), g.find(args.leg[1])
        if not a or not b:
            sys.exit("node not found")
        got = g.leg(a, b)
        if not got:
            sys.exit("no route")
        mi, gain, path = got
        print(f"{g.name(a)} to {g.name(b)}: {mi} mi, +{gain} ft")
        print("  via " + " > ".join(g.name(p) for p in path))


def cmd_trips(args):
    prof = load_profile()
    g = Graph(args.slug)
    camps = g.camps()
    if args.codes:
        want = {c.strip().upper() for c in args.codes.split(",")}
        camps = [c for c in camps
                 if g.name(c).split(" - ")[0].strip().upper() in want]
    if not camps:
        sys.exit("no camps selected")
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    print(f"fetching availability for {len(camps)} camps...", file=sys.stderr)
    nights = args.nights or 3
    av = fetch_for_graph(g, camps, start, end + timedelta(days=nights))
    s = Solver(g, av,
               party=args.party or prof["party_size"],
               nights=nights,
               max_mi=args.max_mi or prof["daily_max"]["miles"],
               max_gain=args.max_gain or prof["daily_max"]["gain_ft"],
               basecamp_ok=not args.no_basecamp)
    trip_sel = (args.trip_types if args.trip_types is not None
                else prof.get("trip_types")
                if prof.get("trip_types") is not None
                else args.trip_type or prof.get("trip_type", "any"))
    rows = s.batch(g.entrances(), start, end, trip_types=trip_sel)
    if args.via:
        via_id = g.find(args.via)
        if not via_id:
            sys.exit(f"--via camp not found: {args.via}")
        rows = [r for r in rows
                if via_id in s.route_nodes(r["entrance"], r["seq"])]
        print(f"via {g.name(via_id)}: {len(rows)} itineraries", file=sys.stderr)
    scorer = Scorer(g)
    ranked = scorer.rank(rows, prof["daily_pref"]["miles"],
                         prof["daily_pref"]["gain_ft"])
    if args.sort == "date":
        ranked.sort(key=lambda r: (r["start"], -r["score"]))
    text, shown = format_trips(
        g, scorer, ranked, prof["daily_pref"]["miles"],
        prof["daily_pref"]["gain_ft"], nights, s.party, s.max_mi, s.max_gain,
        sort=args.sort, trip_types=trip_sel)
    print(text)
    if args.gpx:
        if not 1 <= args.gpx <= min(len(shown), 15):
            sys.exit(f"--gpx must be 1..{min(len(shown), 15)}")
        from .gpx import write_itinerary_gpx
        path, skipped = write_itinerary_gpx(g, shown[args.gpx - 1]["best"])
        print(f"GPX written: {path}")
        if skipped:
            print(f"  skipped (no coordinates): {', '.join(skipped)}")
        print("  Note: straight lines between graph nodes, not trail "
              "geometry. Snap to trails in CalTopo or AllTrails.")


def cmd_export(args):
    from .gpx import write_itinerary_gpx, DISCLAIMER
    g = Graph(args.slug)
    ent = g.find(args.entrance)
    if not ent:
        sys.exit(f"entrance not found: {args.entrance}")
    if g.nodes[ent]["kind"] != "entrance":
        print(f"note: {g.name(ent)} is a {g.nodes[ent]['kind']}, not an entrance",
              file=sys.stderr)
    seq = []
    for ref in args.camps.split(","):
        nid = g.find(ref.strip())
        if not nid:
            sys.exit(f"camp not found: {ref.strip()}")
        seq.append(nid)
    row = {"entrance": ent, "seq": tuple(seq),
           "start": date.fromisoformat(args.start)}
    path, skipped = write_itinerary_gpx(g, row, title=args.name)
    print(f"GPX written: {path}")
    if skipped:
        print(f"  skipped (no coordinates): {', '.join(skipped)}")
    print(f"  Note: {DISCLAIMER}")


def cmd_watch(args):
    from .watch import run_watch, load_config
    prof = load_profile()
    if args.config:
        cfg = load_config(args.config)
        if cfg is None:
            print(f"{args.config}: missing or enabled is false; nothing to watch")
            return
        args.slug = args.slug or cfg.get("slug")
        args.start = args.start or cfg.get("start")
        args.end = args.end or cfg.get("end")
        args.codes = args.codes or cfg.get("codes")
        args.party = args.party or cfg.get("party")
    if not (args.slug and args.start and args.end):
        sys.exit("watch needs a slug, --start, and --end (or --config)")
    g = Graph(args.slug)
    camps = g.camps()
    if args.codes:
        want = {c.strip().upper() for c in args.codes.split(",")}
        camps = [c for c in camps
                 if g.name(c).split(" - ")[0].strip().upper() in want]
    if not camps:
        sys.exit("no camps selected")
    div_ids = [g.nodes[c]["division_id"] for c in camps]
    sent = run_watch(g, div_ids,
                     date.fromisoformat(args.start),
                     date.fromisoformat(args.end),
                     party=args.party or prof["party_size"],
                     interval=args.interval, once=args.once,
                     no_send=args.no_send, inject=args.inject)
    print(f"watch ended, {sent} alert(s) sent")


def cmd_atlas(args):
    from .coverage import render_atlas
    print(f"coverage/COVERAGE.md regenerated, {render_atlas()} entries")


def cmd_area(args):
    from .areas import build_area
    build_area(args.slug)


def cmd_calibrate(args):
    """The owner's half hour: run a real search, print the top ten with
    the score broken into its components, and write a reaction sheet to
    docs/CALIBRATION_NOTES.md. Reactions fold into scoring.json in the
    session after Noah fills the sheet. --pdi-check audits whether the
    committed demand history is deep enough to re-norm percentiles."""
    import os as _o
    import re as _re
    import sqlite3 as _s
    if args.pdi_check:
        path = _o.path.join("data", "history.sqlite")
        if not _o.path.exists(path):
            print("PDI: no committed snapshot at data/history.sqlite")
            return
        con = _s.connect(path)
        tabs = [r[0] for r in con.execute(
            "select name from sqlite_master where type='table'")]
        if not tabs:
            print("PDI: snapshot exists but is EMPTY (zero tables). The "
                  "cloud watcher's cache may hold history; verify on the "
                  "Actions page after the Telegram secrets land. "
                  "Percentile re-norm is NOT ready.")
            return
        for t in tabs:
            n = con.execute(f"select count(*) from {t}").fetchone()[0]
            print(f"PDI: table {t}: {n} rows")
        return
    from datetime import date, timedelta
    from .graph import Graph
    from .solver import Solver, fetch_for_graph
    from .scoring import Scorer
    g = Graph(args.slug)
    start = date.fromisoformat(args.start) if args.start         else date.today() + timedelta(days=2)
    end = date.fromisoformat(args.end) if args.end         else start + timedelta(days=2)
    av = fetch_for_graph(g, g.camps(), start, end)
    s = Solver(g, av, party=args.party, nights=args.nights,
               max_mi=13.0, max_gain=4000)
    rows = s.batch(g.entrances(), start, end)
    sc = Scorer(g)
    from .config import load_profile
    _pref = load_profile().get("daily_pref", {})
    pref_mi = float(_pref.get("miles", 6.0))
    pref_gain = int(_pref.get("gain_ft", 1500))
    ranked = sc.rank(rows, pref_mi, pref_gain)
    from .report import dedupe_routes
    rows = [v["best"] for v in dedupe_routes(ranked, "score")][:10]
    for r in rows:
        try:
            r["breakdown"] = sc.score(r, pref_mi, pref_gain)
        except Exception:
            r["breakdown"] = {}
    lines = ["# CALIBRATION_NOTES", "",
             f"Search: {args.slug}, {start} to {end}, "
             f"{args.nights} nights, party {args.party}. "
             f"Days easier than your comfortable {pref_mi:g} mi / "
             f"{pref_gain:,} ft now "
             "count as GOOD days; only harder-than-comfortable is "
             "penalized, and any such day is flagged below.",
             "For each row write one reaction: too far / too flat / "
             "wrong camps / boring / crowded / good / love it. "
             "Add anything else that felt off.",
             "If a trip with flagged days still ranks high, that is its "
             "camps scoring exceptionally well. If that tradeoff feels "
             "wrong to you, say so; that balance is exactly what this "
             "sheet tunes.", ""]
    if not rows:
        lines += ["(no bookable itineraries in this window: sold out or "
                  "not yet released; nothing to grade here, not a bug)", ""]
    prof_cache = {}
    def hops_for(r):
        """Ordered node hops for a route including the exit leg, per
        the trip-shape trap in CLAUDE.md."""
        hops = [r["entrance"]] + list(r["seq"])
        if len(r["days"]) > len(hops) - 1:
            if r.get("type") in ("loop", "out_and_back", "lollipop",
                                 "basecamp"):
                hops.append(r["entrance"])
            else:
                last = hops[-1]
                cand = sorted(
                    g.entrances(),
                    key=lambda e: abs(g.nodes[e].get("lat") or 99
                                      - (g.nodes[last].get("lat") or 0))
                    + abs(g.nodes[e].get("lon") or 199
                          - (g.nodes[last].get("lon") or 0)))[:6]
                legs = [(g.leg(last, e), e) for e in cand]
                legs = [(l[0], e) for l, e in legs if l]
                if legs:
                    hops.append(min(legs)[1])
        return hops

    def day_terrain(r):
        """{day number: terrain line} for the hiking days (layover days
        carry no trace). Keyed by day so the row prints its detail in
        day order, interleaved with the layover notes (owner catch
        2026-07-22: day 2's layover note printed before day 1's terrain,
        so a basecamp row read out of sequence)."""
        if args.no_profile:
            return {}
        from .dem import day_toughness
        out = {}
        for k, (x, y) in enumerate(zip(hops_for(r), hops_for(r)[1:]), 1):
            if x == y:
                continue
            key = (x, y)
            if key not in prof_cache:
                try:
                    prof_cache[key] = day_toughness(args.slug, g, x, y)
                except Exception:
                    prof_cache[key] = None
            t = prof_cache[key]
            if t:
                from .pace import describe_trace
                desc = describe_trace(t["mi"], t["elev_ft"],
                                      include_time=False,
                                      include_updown=False)
                if desc:
                    out[k] = f"day {k} terrain: {desc}"
        return out
    def _nm(c):
        return g.name(c).split(" (")[0].split(" - ")[0].strip()
    for i, r in enumerate(rows, 1):
        b = r.get("breakdown") or {}
        seq = list(r["seq"])
        uniq = list(dict.fromkeys(seq))
        if len(seq) >= 2 and len(uniq) == 1:
            stay = (f"BASECAMP: {len(seq)} nights at {_nm(seq[0])} "
                    f"campsite (hike in, stay put, hike out)")
        elif len(uniq) == 1:
            stay = f"1 night at {_nm(seq[0])} campsite"
        else:
            stay = ("camps: " + ", then ".join(_nm(c) for c in seq)
                    + f"  [{r['type'].replace('_', ' ')}]")
        from .pace import direction_word, leg_updown
        hops = hops_for(r)
        day_bits = []
        for k, (mi, gn) in enumerate(r["days"], 1):
            if not mi:
                day_bits.append(f"day {k} layover at camp")
                continue
            flag = (" ABOVE YOUR COMFORTABLE DAY"
                    if mi > pref_mi or gn > pref_gain else "")
            updown, word = f"+{gn:g} ft", ""
            if k < len(hops):
                leg = g.leg(hops[k - 1], hops[k])
                if leg:
                    up, down = leg_updown(g, leg[2])
                    word = direction_word(up, down)
                    updown = f"+{up:,} ft up / -{down:,} ft down"
            day_bits.append(f"day {k} {mi:g} mi, {updown}"
                            + (f", {word}" if word else "") + flag)
        line = (f"{i}. score {r['score']}  {stay}\n"
                f"   from {g.name(r['entrance'])}\n"
                f"   {'; '.join(day_bits)}\n"
                f"   (effort fit {b.get('day_fit')}, camp quality "
                f"{b.get('camp_pct')}, lake nights {b.get('lake_nights')})")
        # per-day detail (layover day hikes and terrain) interleaved in
        # day order so a row never reads out of sequence.
        detail = {}
        for note in sc.layover_notes(r, pref_mi, pref_gain):
            m = _re.match(r"day (\d+)", note)
            detail.setdefault(int(m.group(1)) if m else 0, []).append(note)
        for k, text in day_terrain(r).items():
            detail.setdefault(k, []).append(text)
        for k in sorted(detail):
            for d in detail[k]:
                line += f"\n   {d}"
        print(line)
        lines += [line, "   REACTION: ", ""]
    _o.makedirs("docs", exist_ok=True)
    sheet = _o.path.join("docs", "CALIBRATION_NOTES.md")
    fresh = not _o.path.exists(sheet)
    body = lines if fresh else [""] + lines[2:]
    if not fresh:
        body[1] = "## " + body[1][8:]
    with open(sheet, "a") as fh:
        fh.write("\n".join(body) + "\n")
    print(("created" if fresh else "appended to")
          + " docs/CALIBRATION_NOTES.md")


def cmd_corridor(args):
    from .corridor import build_corridor
    build_corridor(args.slug, max_tiles=args.max_tiles)


def cmd_dem_trail(args):
    from .dem import dem_trail
    updated, skipped, lines = dem_trail(args.slug, dry=args.dry, force=args.force)
    print("\n".join(lines))
    print(f"{updated} edges regraded on trail geometry, "
          f"{len(skipped)} skipped")
    for s in skipped[:8]:
        print("  skip:", s)


def cmd_merge_inventory(args):
    from .extract import merge_dual_inventory
    matched, unmatched = merge_dual_inventory(args.slug, args.permit_id)
    print(f"{matched} camps now carry permit {args.permit_id} as a second "
          f"inventory")
    if unmatched:
        print(f"  unmatched extra divisions: {', '.join(unmatched)}")


def cmd_geometry(args):
    from .geometry import harvest
    routed, fallbacks, lines = harvest(args.slug, dry=args.dry)
    print("\n".join(lines[-12:]))
    print(f"{routed} edge(s) routed along real trails, "
          f"{len(fallbacks)} fallback(s)")


def cmd_dem(args):
    from .dem import dem_edges
    updated, skipped, lines = dem_edges(args.slug, dry=args.dry)
    print("\n".join(lines) if lines else "  nothing to update")
    print(f"{updated} edge(s) {'previewed' if args.dry else 'updated'}, "
          f"{len(skipped)} skipped")
    for s in skipped:
        print(f"  skipped: {s}")


def cmd_board(args):
    from .board import write_board
    out, board = write_board(args.config, args.out)
    print(f"wrote {out}")
    for w in board["windows"]:
        if w.get("error"):
            print(f"  {w['title']}: ERROR {w['error']}")
        else:
            print(f"  {w['title']}: {w['itineraries']} itineraries, "
                  f"{w['routes_total']} routes, top "
                  f"{w['routes'][0]['score'] if w['routes'] else 'n/a'}")


def cmd_coverage(args):
    from .coverage import survey, render, write_coverage
    rows, queue = survey()
    if args.write:
        n = write_coverage()
        print(f"coverage/COVERAGE.md regenerated, {len(rows)} datasets, {n} atlas rows")
    else:
        print(render(rows, queue))

def cmd_history(args):
    from . import history
    if args.action == "stats":
        print(history.stats())
    elif args.action == "pdi":
        path, n = history.derive_pdi()
        print(f"wrote {path}: {n} camps qualified")
        if n == 0:
            print("  (needs 30+ future-dated observations per camp; the "
                  "watcher and board accrue these daily; the index matures "
                  "with the log)")
    else:
        path, n = history.derive_demand()
        print(f"wrote {path}: {n} camps with enough samples")
        if n == 0:
            print("  (needs 30+ future-dated observations per camp; keep scanning)")


def cmd_profile(args):
    prof = load_profile()
    print(f"profile file: {PROFILE_PATH}")
    for k, v in prof.items():
        print(f"  {k}: {v}")


def main():
    from . import __version__
    print(f"switchback v{__version__}", file=sys.stderr)
    p = argparse.ArgumentParser(prog="switchback")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search recreation.gov permits")
    s.add_argument("query")
    s.set_defaults(fn=cmd_search)

    a = sub.add_parser("availability", help="classified availability table")
    a.add_argument("permit_id")
    a.add_argument("--start", required=True)
    a.add_argument("--end", required=True)
    a.add_argument("--filter", default="", help="substring match on camp name")
    a.add_argument("--only-available", action="store_true")
    a.add_argument("--skip-group", action="store_true")
    a.set_defaults(fn=cmd_availability)

    xp = sub.add_parser("export", help="write an itinerary GPX, no availability fetch")
    xp.add_argument("slug")
    xp.add_argument("entrance", help="entrance code or name, e.g. BRE or Longmire")
    xp.add_argument("camps", help="camp sequence, comma separated, e.g. GAB,GLF,GAB")
    xp.add_argument("--start", required=True, help="trip start date YYYY-MM-DD")
    xp.add_argument("--name", default=None)
    xp.set_defaults(fn=cmd_export)

    wa = sub.add_parser("watch", help="poll for openings, alert on Telegram")
    wa.add_argument("slug", nargs="?", default=None)
    wa.add_argument("--start", default=None)
    wa.add_argument("--end", default=None)
    wa.add_argument("--config", default=None, metavar="PATH",
                    help="load slug/window/codes/party from a JSON file; "
                         "exits cleanly when it says enabled: false")
    wa.add_argument("--codes", default=None, help="camp codes, comma separated (default: all graph camps)")
    wa.add_argument("--party", type=int, default=None)
    wa.add_argument("--interval", type=int, default=300, help="seconds between polls, jittered")
    wa.add_argument("--once", action="store_true", help="run one cycle (two with --inject) and exit")
    wa.add_argument("--no-send", action="store_true", help="print alerts instead of sending")
    wa.add_argument("--inject", default=None, metavar="DIV:DATE",
                    help="manufacture an opening to test the pipeline end to end")
    wa.set_defaults(fn=cmd_watch)

    at = sub.add_parser("atlas", help="regenerate coverage/COVERAGE.md from the atlas json")
    at.set_defaults(fn=cmd_atlas)

    ar = sub.add_parser("area", help="build a dispersed trail area: boundary plus full trail layer")
    ar.add_argument("slug")
    ar.set_defaults(fn=cmd_area)

    ge = sub.add_parser("geometry", help="harvest real trail polylines from OSM")
    ge.add_argument("slug")
    ge.add_argument("--dry", action="store_true")
    ge.set_defaults(fn=cmd_geometry)

    de = sub.add_parser("dem", help="fill DEM route-sampled gains for estimated edges")
    de.add_argument("slug")
    de.add_argument("--dry", action="store_true")
    de.set_defaults(fn=cmd_dem)

    bo = sub.add_parser("board", help="compute the static trip board (Pages)")
    bo.add_argument("--config", default="board_config.json")
    bo.add_argument("--out", default="docs/board")
    bo.set_defaults(fn=cmd_board)

    co = sub.add_parser("coverage", help="which parks are at which tier")
    co.add_argument("--write", action="store_true", help="regenerate coverage/COVERAGE.md")
    co.set_defaults(fn=cmd_coverage)

    hi = sub.add_parser("history", help="scan-history stats or demand derivation")
    hi.add_argument("action", choices=["stats", "demand", "pdi"])
    hi.set_defaults(fn=cmd_history)

    pr = sub.add_parser("profile", help="show the saved effort profile")
    pr.set_defaults(fn=cmd_profile)

    ca = sub.add_parser("calibrate", help="run a search and write the "
                        "owner reaction sheet; --pdi-check audits history")
    ca.add_argument("slug", nargs="?", default="glacier")
    ca.add_argument("--start"); ca.add_argument("--end")
    ca.add_argument("--nights", type=int, default=2)
    ca.add_argument("--party", type=int, default=2)
    ca.add_argument("--pdi-check", action="store_true")
    ca.add_argument("--no-profile", action="store_true",
                    help="skip the toughest-stretch day profiles (faster)")
    ca.set_defaults(fn=cmd_calibrate)

    co = sub.add_parser("corridor", help="build a long-trail corridor "
                        "area: buffered centerline plus tiled trails")
    co.add_argument("slug")
    co.add_argument("--max-tiles", type=int, default=8)
    co.set_defaults(fn=cmd_corridor)

    dt = sub.add_parser("dem-trail", help="regrade est gains by sampling "
                        "elevation along real trail polylines")
    dt.add_argument("slug")
    dt.add_argument("--dry", action="store_true")
    dt.add_argument("--force", action="store_true", help="regrade dem_trail_v1 edges too")
    dt.set_defaults(fn=cmd_dem_trail)

    mi = sub.add_parser("merge-inventory", help="attach a second rec.gov "
                        "permit's divisions to a park's camps by name")
    mi.add_argument("slug")
    mi.add_argument("permit_id")
    mi.set_defaults(fn=cmd_merge_inventory)

    ex = sub.add_parser("extract", help="write parks/<slug>.json from a permit")
    ex.add_argument("permit_id")
    ex.add_argument("--slug", default=None, help="output name, e.g. rainier")
    ex.add_argument("--out-dir", default="parks")
    ex.set_defaults(fn=cmd_extract)

    fe = sub.add_parser("features", help="fill coords and feature tags for a park")
    fe.add_argument("slug")
    fe.add_argument("--bbox", default=None, help="S,W,N,E override")
    fe.add_argument("--prefetch", action="store_true",
                    help="only fill the OSM cache, time-boxed")
    fe.add_argument("--budget", type=int, default=300)
    fe.set_defaults(fn=cmd_features)

    gr = sub.add_parser("graph", help="build and validate a park route graph")
    gr.add_argument("slug")
    gr.add_argument("--leg", nargs=2, metavar=("A", "B"),
                    help="spot-check shortest route between two node names")
    gr.set_defaults(fn=cmd_graph)

    tr = sub.add_parser("trips", help="find bookable itineraries")
    tr.add_argument("slug")
    tr.add_argument("--start", required=True)
    tr.add_argument("--end", required=True)
    tr.add_argument("--nights", type=int, default=None)
    tr.add_argument("--party", type=int, default=None)
    tr.add_argument("--max-mi", type=float, default=None)
    tr.add_argument("--max-gain", type=int, default=None)
    tr.add_argument("--trip-type", default=None,
                    choices=["any", "loop", "out_and_back", "lollipop"],
                    help="legacy single shape; --trip-types is preferred")
    tr.add_argument("--trip-types", default=None,
                    help="comma list of shapes to allow: loop, out and "
                         "back, basecamp, point_to_point, or any")
    tr.add_argument("--codes", default=None,
                    help="restrict to camp codes, comma separated")
    tr.add_argument("--no-basecamp", action="store_true")
    tr.add_argument("--sort", default="score", choices=["score", "date"])
    tr.add_argument("--via", default=None,
                    help="only routes that sleep at or pass through this camp")
    tr.add_argument("--gpx", type=int, default=None, metavar="N",
                    help="export the Nth listed route to permit_exports/")
    tr.set_defaults(fn=cmd_trips)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
