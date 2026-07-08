"""Switchback CLI. M0 scope: search, availability, profile.

Examples:
    python -m switchback search "glacier wilderness"
    python -m switchback availability 4675321 --start 2026-09-01 --end 2026-09-07 --filter "ELF -"
    python -m switchback profile
"""
import argparse
import sys
from datetime import date

from .api import search_permits, get_divisions, fetch_availability_rows, HEADERS
from .config import load_profile, PROFILE_PATH
from .extract import extract_park, save_park, summary
from .features import annotate, feature_summary


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

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
