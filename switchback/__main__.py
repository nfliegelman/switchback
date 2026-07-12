"""Switchback CLI. M0 scope: search, availability, profile.

Examples:
    python -m switchback search "glacier wilderness"
    python -m switchback availability 4675321 --start 2026-09-01 --end 2026-09-07 --filter "ELF -"
    python -m switchback profile
"""
import argparse
import sys
from datetime import date, timedelta

from .api import search_permits, get_divisions, fetch_availability_rows, HEADERS
from .config import load_profile, PROFILE_PATH
from .extract import extract_park, save_park, summary
from .features import annotate, feature_summary
from .graph import Graph
from .solver import Solver, fetch_availability
from .scoring import Scorer


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

    widths = [34, 20, 10, 5, 13]
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
        from .features import norm
        def find(ref):
            for nid, n in g.nodes.items():
                if norm(n["name"]) == norm(ref) or nid == ref:
                    return nid
            sys.exit(f"node not found: {ref}")
        a, b = find(args.leg[0]), find(args.leg[1])
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
    div_ids = [g.nodes[c]["division_id"] for c in camps]
    permit_id = g.park["permit_id"]
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    print(f"fetching availability for {len(camps)} camps...", file=sys.stderr)
    nights = args.nights or 3
    av_raw = fetch_availability(permit_id, div_ids, start,
                                end + timedelta(days=nights),
                                progress=lambda f: None)
    av = {c: av_raw[g.nodes[c]["division_id"]] for c in camps}
    s = Solver(g, av,
               party=args.party or prof["party_size"],
               nights=nights,
               max_mi=args.max_mi or prof["daily_max"]["miles"],
               max_gain=args.max_gain or prof["daily_max"]["gain_ft"],
               basecamp_ok=not args.no_basecamp)
    rows = s.batch(g.entrances(), start, end,
                   trip_type=args.trip_type or prof.get("trip_type", "any"))
    scorer = Scorer(g)
    ranked = scorer.rank(rows, prof["daily_pref"]["miles"],
                         prof["daily_pref"]["gain_ft"])
    if args.sort == "date":
        ranked.sort(key=lambda r: (r["start"], -r["score"]))
    routes = {}
    for r in ranked:
        key = (r["entrance"], r["seq"])
        if key not in routes:
            routes[key] = {"best": r, "dates": []}
        routes[key]["dates"].append(r["start"])
    shown = sorted(routes.values(), key=lambda v: v["best"]["score"],
                   reverse=True) if args.sort == "score" else list(routes.values())
    print(f"{len(ranked)} bookable {s.nights}-night itineraries across "
          f"{len(routes)} distinct routes, party {s.party}, "
          f"max {s.max_mi} mi / {s.max_gain} ft, ranked:")
    for v in shown[:15]:
        r = v["best"]
        days = " ".join(f"{m:.1f}mi" for m, _ in r["days"])
        names = " > ".join(g.name(c).split(" - ")[0] for c in r["seq"])
        lk = f" lakes:{r['lake_nights']}/{len(r['seq'])}" if r["lake_nights"] else ""
        ds = sorted(v["dates"])
        when = ds[0].isoformat() if len(ds) == 1 else             f"{ds[0].isoformat()} (+{len(ds) - 1} more dates thru {ds[-1].isoformat()})"
        print(f"  {r['score']:.3f}  {g.name(r['entrance'])[:24]:<24} {names}"
              f"  [{r['type']}]  days: {days}{lk}\n"
              f"          available: {when}")
        for note in scorer.layover_notes(r, prof["daily_pref"]["miles"],
                                         prof["daily_pref"]["gain_ft"]):
            print(f"          {note}")
    if len(routes) > 15:
        print(f"  ... and {len(routes) - 15} more routes")


def cmd_profile(args):
    prof = load_profile()
    print(f"profile file: {PROFILE_PATH}")
    for k, v in prof.items():
        print(f"  {k}: {v}")


def main():
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

    pr = sub.add_parser("profile", help="show the saved effort profile")
    pr.set_defaults(fn=cmd_profile)

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
                    choices=["any", "loop", "out_and_back", "lollipop"])
    tr.add_argument("--codes", default=None,
                    help="restrict to camp codes, comma separated")
    tr.add_argument("--no-basecamp", action="store_true")
    tr.add_argument("--sort", default="score", choices=["score", "date"])
    tr.set_defaults(fn=cmd_trips)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
