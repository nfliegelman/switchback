"""
switchback.web: the v2.1 map server.

A small FastAPI app that serves the Leaflet single-file frontend and a
JSON API over the existing engine. The engine itself stays standard
library; fastapi and uvicorn are optional extras needed only for the
map. Run from the repo root:

    python -m uvicorn switchback.web:app --port 8756

or double-click SwitchbackMap.bat on Windows. Endpoints:

    GET  /                      the map
    GET  /api/parks             coverage survey (park picker)
    GET  /api/park/{slug}       nodes with coords plus edges (map layer)
    GET  /api/availability/...  open-night counts per camp (marker color)
    POST /api/trips             ranked, deduped routes with day paths
    POST /api/frontier          adventure mode: one night at a time

Availability fetches are cached in-process for two minutes per window,
so frontier clicks feel instant after the first. create_app(fetch_fn=)
accepts an injectable fetcher, mirroring watch.py, so tests run offline.
"""
import json
import os
import time
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from . import planner
from .config import load_profile
from .extract import load_park
from .coverage import survey
from .geometry import ATTRIBUTION as GEOM_ATTRIBUTION, day_path, path_for
from .gpx import build_gpx
from .graph import Graph
from .plans import validate_request
from .report import dedupe_routes
from .scoring import Scorer
from .solver import Solver, fetch_availability, fetch_for_graph

_HERE = os.path.dirname(os.path.abspath(__file__))
_AV_CACHE = {}
_AV_TTL = 120


class TripsReq(BaseModel):
    slug: str
    start: date
    end: date
    nights: int = 3
    party: int | None = None
    codes: str | None = None
    via: str | None = None
    trip_type: str = "any"
    limit: int = 12


class ProfileReq(BaseModel):
    slug: str
    a: str
    b: str
    pace: float | dict | None = None


class PlanReq(BaseModel):
    """The consumer trip request (plans.TripRequest wire shape).
    Effort fields left null fall back to profile.json as visible
    defaults; the response echoes what was actually used."""
    slug: str
    start: date
    latest_start: date | None = None
    nights: int = 2
    party: int | None = None
    pref_mi: float | None = None
    max_mi: float | None = None
    pref_gain: int | None = None
    max_gain: int | None = None
    shapes: list[str] = []
    first_come_ok: bool = True
    arrival_night: bool = False
    recovery_night: bool = False
    limit: int = 8
    pace: float | dict | None = None


class PlanGpxReq(BaseModel):
    slug: str
    entrance: str
    seq: list[str]
    start: date
    title: str | None = None


class FrontierReq(BaseModel):
    slug: str
    entrance: str
    start: date
    seq: list[str] = []
    nights: int = 3
    party: int | None = None


def _graph(slug):
    try:
        return Graph(slug)
    except Exception as ex:
        raise HTTPException(404, f"no route graph for {slug}: {ex}")


def _feats(slug):
    """camp id -> {lake: bool}; goes through load_park so regions get
    their merged member camps, not just the overlay file."""
    try:
        d = load_park(slug)
    except Exception:
        return {}
    return {str(c.get("id")): {"lake": c.get("water_lake_flag") in ("Y", True)}
            for c in d.get("camps", [])}


def _codes_filter(g, camps, codes):
    if not codes:
        return camps
    want = {c.strip().upper() for c in codes.split(",") if c.strip()}
    return [c for c in camps
            if g.name(c).split(" - ")[0].strip().upper() in want]


def _availability_by_node(g, camps, start, end, fetch_fn):
    key = (g.park["slug"], start.isoformat(), end.isoformat(),
           tuple(sorted(camps)))
    hit = _AV_CACHE.get(key)
    if hit and time.time() - hit[0] < _AV_TTL:
        return hit[1]
    by_node = fetch_for_graph(g, camps, start, end, fetch_fn=fetch_fn)
    _AV_CACHE[key] = (time.time(), by_node)
    return by_node


def _solver(g, av, prof, party, nights):
    return Solver(g, av, party=party or prof["party_size"], nights=nights,
                  max_mi=prof["daily_max"]["miles"],
                  max_gain=prof["daily_max"]["gain_ft"])


def _coords(g, nid):
    n = g.nodes[nid]
    return [n.get("lat"), n.get("lon")]


def create_app(fetch_fn=None, elev_fn=None):
    app = FastAPI(title="Switchback", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index():
        with open(os.path.join(_HERE, "web_index.html"),
                  encoding="utf-8") as fh:
            return fh.read()

    @app.get("/api/parks")
    def parks():
        rows, _q = survey()
        return [r for r in rows if r.get("edges")]

    @app.post("/api/quit")
    def quit_server():
        import threading
        threading.Timer(0.4, lambda: os._exit(0)).start()
        return {"bye": True}

    @app.get("/api/areas")
    def areas():
        p = os.path.join("docs", "areas", "index.json")
        if not os.path.exists(p):
            return {"areas": []}
        with open(p) as fh:
            return json.load(fh)

    @app.get("/api/area/{slug}")
    def area(slug: str):
        p = os.path.join("docs", "areas", f"{slug}.json")
        if not os.path.exists(p):
            raise HTTPException(404, f"no trail area named {slug!r}")
        with open(p) as fh:
            return json.load(fh)

    @app.get("/api/park/{slug}")
    def park(slug: str):
        g = _graph(slug)
        feats = _feats(slug)
        nodes = []
        for nid, n in g.nodes.items():
            f = feats.get(str(n.get("division_id"))) or {}
            nodes.append({"id": nid, "kind": n.get("kind"),
                          "name": n.get("name"),
                          "lat": n.get("lat"), "lon": n.get("lon"),
                          "elevation_ft": n.get("elevation_ft"),
                          "policy": n.get("policy", "reservation"),
                          "lake": bool(f.get("lake"))})
        seen, edges = set(), []
        for a, lst in g.adj.items():
            for b, mi, gain, est, _k in lst:
                key = frozenset((a, b))
                if key in seen:
                    continue
                seen.add(key)
                rec = {"a": a, "b": b, "mi": mi, "est": bool(est)}
                p = path_for(slug, a, b)
                if p:
                    rec["path"] = p
                edges.append(rec)
        return {"slug": slug, "name": g.park["name"],
                "permit_id": g.park["permit_id"],
                "nodes": nodes, "edges": edges}

    @app.get("/api/availability/{slug}")
    def availability(slug: str, start: date, end: date,
                     party: int | None = None):
        g = _graph(slug)
        prof = load_profile()
        p = party or prof["party_size"]
        av = _availability_by_node(g, g.camps(), start, end, fetch_fn)
        out = []
        for c in g.camps():
            days = av.get(c) or {}
            open_dates = sorted(d for d, r in days.items()
                                if r is not None and r >= p)
            out.append({"id": c, "open_nights": len(open_dates),
                        "open_dates": open_dates})
        return {"party": p, "camps": out}

    @app.post("/api/trips")
    def trips(req: TripsReq):
        g = _graph(req.slug)
        prof = load_profile()
        camps = _codes_filter(g, g.camps(), req.codes)
        if not camps:
            raise HTTPException(400, "no camps match those codes")
        av = _availability_by_node(
            g, camps, req.start, req.end + timedelta(days=req.nights),
            fetch_fn)
        s = _solver(g, av, prof, req.party, req.nights)
        rows = s.batch(g.entrances(), req.start, req.end,
                       trip_type=req.trip_type)
        if req.via:
            vid = g.find(req.via)
            if not vid:
                raise HTTPException(400, f"cannot resolve via: {req.via}")
            rows = [r for r in rows
                    if vid in s.route_nodes(r["entrance"], r["seq"])]
        scorer = Scorer(g)
        pref_mi = prof["daily_pref"]["miles"]
        pref_gain = prof["daily_pref"]["gain_ft"]
        ranked = scorer.rank(rows, pref_mi, pref_gain)
        shown = dedupe_routes(ranked)[:req.limit]
        routes = []
        for v in shown:
            r = v["best"]
            stops = [r["entrance"]] + list(r["seq"]) + [r["entrance"]]
            day_paths = [day_path(req.slug, g, [a, b])
                         for a, b in zip(stops, stops[1:])]
            routes.append({
                "score": round(r["score"], 3),
                "type": r["type"],
                "entrance": {"id": r["entrance"],
                             "name": g.name(r["entrance"])},
                "stops": [{"id": c, "name": g.name(c),
                           "policy": g.nodes[c].get("policy", "reservation")}
                          for c in r["seq"]],
                "days": r["days"],
                "dates": sorted(d.isoformat() for d in v["dates"]),
                "notes": scorer.layover_notes(r, pref_mi, pref_gain),
                "day_paths": day_paths,
            })
        return {"itineraries": len(ranked), "routes_total":
                len(dedupe_routes(ranked)), "trip_type": req.trip_type,
                "party": s.party, "routes": routes}

    @app.get("/api/plan/defaults")
    def plan_defaults():
        prof = load_profile()
        return {"party": prof["party_size"],
                "pref_mi": prof["daily_pref"]["miles"],
                "pref_gain": prof["daily_pref"]["gain_ft"],
                "max_mi": prof["daily_max"]["miles"],
                "max_gain": prof["daily_max"]["gain_ft"],
                "shapes": prof.get("trip_types") or []}

    @app.post("/api/plan")
    def plan(req: PlanReq):
        raw = (req.model_dump() if hasattr(req, "model_dump")
               else req.dict())
        parsed, errors = validate_request(raw, load_profile())
        if errors:
            raise HTTPException(400, {"errors": errors})
        g = _graph(parsed.slug)
        fs, fe = planner.availability_window(parsed)
        av = _availability_by_node(g, g.camps(), fs, fe, fetch_fn)
        try:
            return planner.plan_trips(parsed, availability=av, graph=g,
                                      include_geometry=True)
        except planner.PlannerError as ex:
            raise HTTPException(404, str(ex))

    @app.post("/api/plan/gpx")
    def plan_gpx(req: PlanGpxReq):
        g = _graph(req.slug)
        if req.entrance not in g.nodes or any(c not in g.nodes
                                              for c in req.seq):
            raise HTTPException(400, "unknown route nodes for GPX export")
        xml, _skipped = build_gpx(g, req.entrance, req.seq, req.start,
                                  req.title)
        return Response(content=xml, media_type="application/gpx+xml")

    @app.post("/api/profile")
    def profile(req: ProfileReq):
        from .dem import day_toughness
        from .pace import (grade_sections, hours_for_sections,
                           normalize_pace, steep_summary)
        g = _graph(req.slug)
        prof = day_toughness(req.slug, g, req.a, req.b, elev_fn=elev_fn)
        if not prof:
            raise HTTPException(404, "no usable trail line between those two stops")
        pace, _errs = normalize_pace(req.pace)
        sections = grade_sections(prof["mi"], prof["elev_ft"])
        if sections:
            steepest, steep_mi = steep_summary(sections)
            prof["sections"] = sections
            prof["est_hours"] = hours_for_sections(sections, pace)
            prof["steepest_pct"] = steepest
            prof["steep_miles_30plus"] = steep_mi
        return prof

    @app.post("/api/frontier")
    def frontier(req: FrontierReq):
        g = _graph(req.slug)
        prof = load_profile()
        ent = g.find(req.entrance) or req.entrance
        if ent not in g.nodes:
            raise HTTPException(400, f"unknown entrance: {req.entrance}")
        av = _availability_by_node(
            g, g.camps(), req.start,
            req.start + timedelta(days=req.nights + 1), fetch_fn)
        s = _solver(g, av, prof, req.party, req.nights)
        seq = [g.find(x) or x for x in req.seq]
        pos = seq[-1] if seq else ent
        night = len(seq)
        streak = 1
        for prev in reversed(seq[:-1]):
            if prev == pos:
                streak += 1
            else:
                break
        resp = {"night": night, "nights": req.nights,
                "pos": {"id": pos, "name": g.name(pos)}, "options": []}
        if night >= req.nights:
            leg = g.leg(pos, ent)
            resp["finish"] = {"ok": bool(s.day_ok(pos, ent)),
                              "mi": leg[0] if leg else None,
                              "gain": leg[1] if leg else None,
                              "entrance": g.name(ent)}
            return resp
        d = req.start + timedelta(days=night)
        for c in s.camps:
            if c == pos:
                if not s.basecamp_ok or (s.max_stay
                                         and streak + 1 > s.max_stay):
                    continue
            elif not s.day_ok(pos, c):
                continue
            if not s.open_night(c, d):
                continue
            leg = g.leg(pos, c)
            remaining = (av.get(c) or {}).get(d.isoformat())
            resp["options"].append({
                "id": c, "name": g.name(c),
                "policy": g.nodes[c].get("policy", "reservation"),
                "mi": leg[0] if leg else 0.0,
                "gain": leg[1] if leg else 0,
                "remaining": remaining,
                "endings": s.endings(ent, req.start, night + 1, c,
                                     streak + 1 if c == pos else 1),
                "lake": bool((_feats(req.slug).get(
                    str(g.nodes[c].get("division_id"))) or {}).get("lake")),
            })
        resp["options"].sort(key=lambda o: -o["endings"])
        resp["date"] = d.isoformat()
        return resp

    return app


app = create_app()
