"""
switchback.graph: M3 route graphs.

Loads parks/edges/<slug>_edges.json, resolves human-readable node names
against the park dataset (camps by fuzzy name or code, entrances by
ENT:<name>, junctions and standalone trailheads by declared key), and
builds a bidirectional graph with direction-aware gain and loss.

Gain policy: edges may carry sourced gain_ab/loss_ab. When absent, gain
is estimated from node elevation deltas and flagged est. Endpoint deltas
understate true gain over passes; the DEM pass replaces them.

leg(a, b) returns (miles, gain, node_path) for the shortest trail route,
so day legs may pass through camps without sleeping there.
"""
import heapq
import json
import os

from .extract import load_park
from .features import norm

EDGE_DIR = os.path.join("parks", "edges")


class Graph:
    def __init__(self, slug):
        self.slug = slug
        self.park = load_park(slug)
        with open(os.path.join(EDGE_DIR, f"{slug}_edges.json")) as fh:
            spec = json.load(fh)

        self.nodes = {}          # node_id -> dict(kind, name, lat, lon, elevation_ft, division_id)
        self.adj = {}            # node_id -> [(other, miles, gain, est, edge_key)]
        self.unresolved = []
        self.est_edges = 0
        self.sourced_edges = 0

        self._camp_by_norm = {}
        self._camp_by_code = {}
        for c in self.park["camps"]:
            if not c["included"]:
                continue
            self._camp_by_norm.setdefault(norm(c["name"]), c)
            if c.get("code"):
                self._camp_by_code[c["code"]] = c
        self._ent_by_norm = {norm(e["name"]): e for e in self.park["entrances"]
                             if e.get("included", True)}

        for n in spec.get("nodes", []):
            self.nodes[n["key"]] = {"kind": n.get("kind", "junction"),
                                    "name": n.get("name", n["key"]),
                                    "lat": n.get("lat"), "lon": n.get("lon"),
                                    "elevation_ft": n.get("elevation_ft"),
                                    "division_id": None}

        for e in spec["edges"]:
            a = self._resolve(e["a"])
            b = self._resolve(e["b"])
            if a is None or b is None:
                continue
            self._add(a, b, e)

    # ------------------------------------------------------------------
    @staticmethod
    def _fuzzy(target_norm, pool):
        """Unique subset/superset token match against a {norm: obj} pool."""
        t = set(target_norm.split())
        need = min(2, len(t))
        hits = [k for k in pool
                if (t <= set(k.split()) or set(k.split()) <= t)
                and len(t & set(k.split())) >= need]
        return pool[hits[0]] if len(hits) == 1 else None

    def _resolve(self, ref):
        if ref in self.nodes:
            return ref
        if ref.startswith("ENT:"):
            key = norm(ref[4:])
            ent = self._ent_by_norm.get(key) or self._fuzzy(key, self._ent_by_norm)
            if ent is None:
                nid = f"ENT:{key}"
                if nid not in self.nodes:
                    self.unresolved.append(ref)
                    self.nodes[nid] = {"kind": "entrance", "name": ref[4:],
                                       "lat": None, "lon": None,
                                       "elevation_ft": None, "division_id": None}
                return nid
            nid = f"ENT:{ent['id']}"
            if nid not in self.nodes:
                self.nodes[nid] = {"kind": "entrance", "name": ent["name"],
                                   "lat": ent["lat"], "lon": ent["lon"],
                                   "elevation_ft": ent.get("elevation_ft"),
                                   "division_id": None}
            return nid
        camp = (self._camp_by_code.get(ref)
                or self._camp_by_norm.get(norm(ref))
                or self._fuzzy(norm(ref), self._camp_by_norm))
        if camp is None:
            nid = f"J:{norm(ref)}"
            if nid not in self.nodes:
                self.unresolved.append(ref)
                self.nodes[nid] = {"kind": "junction", "name": ref,
                                   "lat": None, "lon": None,
                                   "elevation_ft": None, "division_id": None}
            return nid
        nid = camp["id"]
        if nid not in self.nodes:
            self.nodes[nid] = {"kind": "camp", "name": camp["name"],
                               "lat": camp["lat"], "lon": camp["lon"],
                               "elevation_ft": camp.get("elevation_ft"),
                               "division_id": camp["id"] if camp.get(
                                   "policy", "reservation") == "reservation"
                                   else None,
                               "permit_id": camp.get(
                                   "permit_id", self.park.get("permit_id")),
                               "policy": camp.get("policy", "reservation")}
        return nid

    def _add(self, a, b, e):
        miles = float(e["miles"])
        gain_ab, loss_ab = e.get("gain_ab"), e.get("loss_ab")
        est = bool(e.get("est_gain")) or gain_ab is None
        if gain_ab is None:
            ea = self.nodes[a].get("elevation_ft")
            eb = self.nodes[b].get("elevation_ft")
            delta = (eb - ea) if (ea is not None and eb is not None) else 0
            gain_ab, loss_ab = max(delta, 0), max(-delta, 0)
        if e.get("est_gain") or e.get("gain_ab") is None:
            self.est_edges += 1
        else:
            self.sourced_edges += 1
        key = frozenset((a, b))
        self.adj.setdefault(a, []).append((b, miles, gain_ab, est, key))
        self.adj.setdefault(b, []).append((a, miles, loss_ab if loss_ab is not None else 0, est, key))

    # ------------------------------------------------------------------
    def leg(self, a, b):
        """Shortest trail route a to b: (miles, gain_in_direction, node_path)."""
        if a == b:
            return (0.0, 0, [a])
        pq, seen, prev = [(0.0, 0, a, None)], {}, {}
        while pq:
            mi, gain, node, par = heapq.heappop(pq)
            if node in seen:
                continue
            seen[node] = (mi, gain)
            prev[node] = par
            if node == b:
                path, cur = [], b
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                return (round(mi, 1), gain, path[::-1])
            for nxt, m, g, _est, _k in self.adj.get(node, []):
                if nxt not in seen:
                    heapq.heappush(pq, (round(mi + m, 2), gain + g, nxt, node))
        return None

    def leg_edges(self, path):
        """Undirected edge keys along a node path."""
        return [frozenset((path[i], path[i + 1])) for i in range(len(path) - 1)]

    def camps(self):
        return [nid for nid, n in self.nodes.items() if n["kind"] == "camp"]

    def entrances(self):
        return [nid for nid, n in self.nodes.items() if n["kind"] == "entrance"]

    def name(self, nid):
        return self.nodes[nid]["name"]

    def find(self, ref):
        """Resolve a user reference: node id, camp code, normalized name,
        or unique case-insensitive substring. None if unresolvable."""
        if ref in self.nodes:
            return ref
        up = ref.strip().upper()
        for nid, n in self.nodes.items():
            if n["name"].split(" - ")[0].strip().upper() == up:
                return nid
        target = norm(ref)
        for nid, n in self.nodes.items():
            if norm(n["name"]) == target:
                return nid
        subs = [nid for nid, n in self.nodes.items()
                if ref.lower() in n["name"].lower()]
        return subs[0] if len(subs) == 1 else None

    def report(self):
        kinds = {}
        for n in self.nodes.values():
            kinds[n["kind"]] = kinds.get(n["kind"], 0) + 1
        lines = [f"{self.slug} graph: {len(self.nodes)} nodes {kinds}, "
                 f"{self.sourced_edges + self.est_edges} edges "
                 f"({self.sourced_edges} sourced gains, {self.est_edges} est)"]
        if self.unresolved:
            lines.append(f"  UNRESOLVED refs: {self.unresolved}")
        return "\n".join(lines)
