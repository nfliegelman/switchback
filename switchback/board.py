"""
switchback.board: the v2.3 phone-native trip board.

A scheduled GitHub Actions job (board.yml) runs this daily: it solves
ranked trips for the windows in board_config.json and writes
docs/board/board.json, which the static docs/board/index.html renders
on GitHub Pages. Read-only but fully phone-usable: the compute happens
on GitHub's machines, the map is just a file.

Windows support relative dates so a standing config never goes stale:
{"start_in_days": 14, "span_days": 14} means two weeks out, for two
weeks. Regions work here too, since availability goes through
fetch_for_graph; first-come camps carry their policy into the JSON and
the board labels them honestly.
"""
import json
import os
from datetime import date, datetime, timedelta, timezone

from .config import load_profile
from .geometry import day_path
from .graph import Graph
from .report import dedupe_routes
from .scoring import Scorer
from .solver import Solver, fetch_for_graph


def resolve_window(w, today):
    if w.get("start"):
        return date.fromisoformat(w["start"]), date.fromisoformat(w["end"])
    s = today + timedelta(days=int(w.get("start_in_days", 14)))
    return s, s + timedelta(days=int(w.get("span_days", 14)) - 1)


def _codes_filter(g, camps, codes):
    if not codes:
        return camps
    want = {c.strip().upper() for c in codes.split(",") if c.strip()}
    return [c for c in camps
            if g.name(c).split(" - ")[0].strip().upper() in want]


def _coords(g, nid):
    n = g.nodes[nid]
    return [n.get("lat"), n.get("lon")]


def build_window(w, prof, fetch_fn=None, today=None):
    today = today or date.today()
    start, end = resolve_window(w, today)
    g = Graph(w["slug"])
    camps = _codes_filter(g, g.camps(), w.get("codes"))
    nights = int(w.get("nights", 3))
    party = int(w.get("party", prof["party_size"]))
    av = fetch_for_graph(g, camps, start, end + timedelta(days=nights),
                         fetch_fn=fetch_fn)
    s = Solver(g, av, party=party, nights=nights,
               max_mi=prof["daily_max"]["miles"],
               max_gain=prof["daily_max"]["gain_ft"])
    rows = s.batch(g.entrances(), start, end,
                   trip_type=w.get("trip_type", "any"))
    scorer = Scorer(g)
    pref_mi = prof["daily_pref"]["miles"]
    pref_gain = prof["daily_pref"]["gain_ft"]
    ranked = scorer.rank(rows, pref_mi, pref_gain)
    all_routes = dedupe_routes(ranked)
    routes = []
    for v in all_routes[: int(w.get("limit", 10))]:
        r = v["best"]
        stops_full = [r["entrance"]] + list(r["seq"]) + [r["entrance"]]
        day_paths = [day_path(w["slug"], g, [a, b])
                     for a, b in zip(stops_full, stops_full[1:])]
        routes.append({
            "score": round(r["score"], 3), "type": r["type"],
            "entrance": g.name(r["entrance"]),
            "stops": [{"name": g.name(c),
                       "policy": g.nodes[c].get("policy", "reservation")}
                      for c in r["seq"]],
            "days": r["days"],
            "dates": sorted(d.isoformat() for d in v["dates"]),
            "notes": scorer.layover_notes(r, pref_mi, pref_gain),
            "day_paths": day_paths,
        })
    camps_out = []
    for c in camps:
        n = g.nodes[c]
        days = av.get(c) or {}
        opens = sorted(d for d, rem in days.items()
                       if start.isoformat() <= d <= end.isoformat()
                       and rem is not None and rem >= party)
        camps_out.append({"name": n["name"], "lat": n.get("lat"),
                          "lon": n.get("lon"),
                          "policy": n.get("policy", "reservation"),
                          "open_nights": len(opens)})
    return {"title": w.get("title") or f"{g.park['name']}",
            "slug": w["slug"], "park": g.park["name"],
            "start": start.isoformat(), "end": end.isoformat(),
            "nights": nights, "party": party,
            "trip_type": w.get("trip_type", "any"),
            "itineraries": len(ranked), "routes_total": len(all_routes),
            "routes": routes, "camps": camps_out}


def build_board(cfg, fetch_fn=None, today=None):
    prof = load_profile()
    windows = []
    for w in cfg.get("windows", []):
        try:
            windows.append(build_window(w, prof, fetch_fn=fetch_fn,
                                        today=today))
        except Exception as ex:
            windows.append({"title": w.get("title", w.get("slug", "?")),
                            "slug": w.get("slug"), "error": str(ex)})
    return {"generated_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "windows": windows}


def write_board(cfg_path, out_dir, fetch_fn=None, today=None):
    with open(cfg_path) as fh:
        cfg = json.load(fh)
    board = build_board(cfg, fetch_fn=fetch_fn, today=today)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "board.json")
    with open(out, "w") as fh:
        def _seam_count(obj):
            import math as _m
            n = 0
            stack = [obj]
            while stack:
                x = stack.pop()
                if isinstance(x, dict):
                    dps = x.get("day_paths")
                    if isinstance(dps, list):
                        for dp in dps:
                            for i in range(len(dp) - 1):
                                la1, lo1 = _m.radians(dp[i][0]), _m.radians(dp[i][1])
                                la2, lo2 = _m.radians(dp[i+1][0]), _m.radians(dp[i+1][1])
                                h = (_m.sin((la2-la1)/2)**2
                                     + _m.cos(la1)*_m.cos(la2)*_m.sin((lo2-lo1)/2)**2)
                                if 3958.8*2*_m.asin(_m.sqrt(h)) > 0.5:
                                    n += 1
                    stack.extend(x.values())
                elif isinstance(x, list):
                    stack.extend(x)
            return n
        print(f"seam guard: {_seam_count(board)} straight or seam hops over 0.5 mi across all windows")
        json.dump(board, fh)
    return out, board
