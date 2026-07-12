"""M7 invariants: GPX parses, waypoint and per-day track counts are
right, layovers produce no track, no point ever lacks coordinates,
elevations ride along in meters."""
import sys, os, xml.etree.ElementTree as ET
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.graph import Graph
from switchback.gpx import build_gpx

NS = "{http://www.topografix.com/GPX/1/1}"


def main():
    g = Graph("glacier")
    ent = g.find("BRE")
    gab, glf = g.find("GAB"), g.find("GLF")
    xml, skipped = build_gpx(g, ent, (gab, glf, gab), date(2026, 9, 22))
    root = ET.fromstring(xml)
    assert root.tag == NS + "gpx"
    wpts = root.findall(NS + "wpt")
    assert len(wpts) == 3, f"expected BRE, GAB, GLF waypoints, got {len(wpts)}"
    trks = root.findall(NS + "trk")
    assert len(trks) == 4, f"expected 4 moving days, got {len(trks)}"
    for trk in trks:
        pts = trk.findall(f"{NS}trkseg/{NS}trkpt")
        assert len(pts) >= 2
        for p in pts:
            assert p.get("lat") and p.get("lon")
    assert any(w.find(NS + "ele") is not None for w in wpts), "elevations missing"
    assert not skipped, f"unexpected skips: {skipped}"

    xml2, _ = build_gpx(g, ent, (gab, gab, gab), date(2026, 9, 22))
    root2 = ET.fromstring(xml2)
    assert len(root2.findall(NS + "trk")) == 2, "layover days must not produce tracks"
    assert "layover" in root2.find(f"{NS}metadata/{NS}desc").text
    print("GPX OK: 3 waypoints, 4 day-tracks, layovers noted, all points located")


if __name__ == "__main__":
    main()
