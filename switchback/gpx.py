"""
switchback.gpx: M7 itinerary export.

Writes GPX 1.1 the way CalTopo, AllTrails custom maps, and Garmin
Explore all accept: <wpt> per stop (entrance and each camp, with
elevation in meters where known) and one <trk> per moving day whose
points follow the route graph's node path, so pass-through camps and
junctions shape the line. Segments are straight lines between graph
nodes by design; real trail geometry is a backlog item. Layover days
produce no track, just a note in the metadata description.
"""
import os
import re
from datetime import timedelta
from xml.sax.saxutils import escape

DISCLAIMER = ("Straight lines between route-graph nodes, not trail "
              "geometry. Snap to trails in CalTopo or AllTrails.")


def _ele(n):
    ft = n.get("elevation_ft")
    return f"\n    <ele>{ft * 0.3048:.1f}</ele>" if ft is not None else ""


def _wpt(n, label):
    return (f'  <wpt lat="{n["lat"]:.6f}" lon="{n["lon"]:.6f}">{_ele(n)}\n'
            f"    <name>{escape(label)}</name>\n"
            f"    <desc>{escape(n['kind'])}"
            + (f", {n['elevation_ft']} ft" if n.get("elevation_ft") else "")
            + "</desc>\n  </wpt>")


def build_gpx(g, entrance, seq, start_date, title=None):
    """Returns (xml_text, skipped_names)."""
    stops = [entrance] + list(seq) + [entrance]
    title = title or f"Switchback {g.slug} {start_date.isoformat()}"
    skipped, wpts = [], []
    for nid in [entrance] + list(dict.fromkeys(seq)):
        n = g.nodes[nid]
        if n["lat"] is None:
            skipped.append(n["name"])
            continue
        wpts.append(_wpt(n, n["name"].split(" - ")[0]
                         if " - " in n["name"] else n["name"]))

    trks, layovers = [], []
    for day, (a, b) in enumerate(zip(stops, stops[1:]), 1):
        d = (start_date + timedelta(days=day - 1)).isoformat()
        if a == b:
            layovers.append(f"day {day} ({d}): layover at "
                            f"{g.name(a).split(' - ')[0]}")
            continue
        leg = g.leg(a, b)
        path = leg[2] if leg else [a, b]
        pts = [g.nodes[p] for p in path if g.nodes[p]["lat"] is not None]
        if len(pts) < 2:
            skipped.append(f"day {day} leg ({g.name(a)} to {g.name(b)})")
            continue
        body = "\n".join(
            f'      <trkpt lat="{p["lat"]:.6f}" lon="{p["lon"]:.6f}">'
            f'{_ele(p)}</trkpt>' for p in pts)
        name = (f"Day {day} ({d}): {g.name(a).split(' - ')[0]} to "
                f"{g.name(b).split(' - ')[0]}, {leg[0]} mi" if leg else
                f"Day {day} ({d})")
        trks.append(f"  <trk>\n    <name>{escape(name)}</name>\n"
                    f"    <trkseg>\n{body}\n    </trkseg>\n  </trk>")

    desc = DISCLAIMER + (" Layovers: " + "; ".join(layovers) + "."
                         if layovers else "")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<gpx version="1.1" creator="Switchback" '
           'xmlns="http://www.topografix.com/GPX/1/1">\n'
           f"  <metadata>\n    <name>{escape(title)}</name>\n"
           f"    <desc>{escape(desc)}</desc>\n  </metadata>\n"
           + "\n".join(wpts) + "\n" + "\n".join(trks) + "\n</gpx>\n")
    return xml, skipped


def write_itinerary_gpx(g, row, out_dir="permit_exports", title=None):
    os.makedirs(out_dir, exist_ok=True)
    ent = g.name(row["entrance"]).split(" - ")[0]
    codes = "-".join(g.name(c).split(" - ")[0]
                     for c in dict.fromkeys(row["seq"]))
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_",
                  f"{g.slug}_{row['start'].isoformat()}_{ent}_{codes}")[:80]
    xml, skipped = build_gpx(g, row["entrance"], row["seq"],
                             row["start"], title)
    path = os.path.join(out_dir, stem + ".gpx")
    with open(path, "w") as fh:
        fh.write(xml)
    return path, skipped
