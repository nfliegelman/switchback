"""
switchback.report: shared trip-report rendering.

One renderer serves the CLI today and the GUI's Find Trips window as of
M6, so the two can never drift apart; the v2.1 web UI consumes the same
dedupe structure. Routes are deduplicated by (entrance, camp sequence)
with the best-scoring date shown and the rest collapsed into a span.
"""


def dedupe_routes(ranked, sort="score"):
    routes = {}
    for r in ranked:
        key = (r["entrance"], r["seq"])
        if key not in routes:
            routes[key] = {"best": r, "dates": []}
        routes[key]["dates"].append(r["start"])
    shown = list(routes.values())
    if sort == "score":
        shown.sort(key=lambda v: v["best"]["score"], reverse=True)
    return shown


def format_trips(g, scorer, ranked, pref_mi, pref_gain, nights, party,
                 max_mi, max_gain, sort="score", limit=15, trip_type="any"):
    """Returns (text, shown) where shown is the deduped route list, so a
    caller can act on the Nth displayed route (e.g. GPX export)."""
    shown = dedupe_routes(ranked, sort)
    lines = [f"{len(ranked)} bookable {nights}-night itineraries across "
             f"{len(shown)} distinct routes, party {party}, "
             f"max {max_mi} mi / {max_gain} ft, "
             f"trip type {trip_type}, ranked:"]
    if trip_type and trip_type != "any":
        lines.append(f"  FILTER ACTIVE: only {trip_type} trips are shown. "
                     "Routes of every other shape were discarded before "
                     "ranking. Use --trip-type any to see them all, or edit "
                     "trip_type in profile.json.")
    for i, v in enumerate(shown[:limit], 1):
        r = v["best"]
        days = " ".join(f"{m:.1f}mi" for m, _ in r["days"])
        names = " > ".join(g.name(c).split(" - ")[0] for c in r["seq"])
        lk = f" lakes:{r['lake_nights']}/{len(r['seq'])}" if r["lake_nights"] else ""
        ds = sorted(v["dates"])
        when = ds[0].isoformat() if len(ds) == 1 else \
            f"{ds[0].isoformat()} (+{len(ds) - 1} more dates thru {ds[-1].isoformat()})"
        lines.append(f"  {i:>2}. {r['score']:.3f}  "
                     f"{g.name(r['entrance'])[:24]:<24} {names}  [{r['type']}]"
                     f"  days: {days}{lk}")
        lines.append(f"          available: {when}")
        for note in scorer.layover_notes(r, pref_mi, pref_gain):
            lines.append(f"          {note}")
    if len(shown) > limit:
        lines.append(f"  ... and {len(shown) - limit} more routes")
    return "\n".join(lines), shown
