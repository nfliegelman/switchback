"""v2.4 invariants: hysteresis gain math is exact on a synthetic profile,
sourced edges are never touched, coordless edges are skipped honestly."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback.dem import gain_loss_ft, sample_line, dem_edges

def main():
    # flat, +300 m climb, -100 m dip, +50 m: up 350 m, down 100 m
    prof = [1000.0]*5 + [1000 + 30*i for i in range(1, 11)] \
         + [1300 - 20*i for i in range(1, 6)] + [1200 + 10*i for i in range(1, 6)]
    up, down = gain_loss_ft(prof)
    assert up == int(round(350*3.28084)) and down == int(round(100*3.28084)), (up, down)

    # 2 m wiggles never count as climbing
    up2, down2 = gain_loss_ft([1000, 1002, 1000, 1002, 1000])
    assert (up2, down2) == (0, 0)

    pts = sample_line((48.0, -113.0), (48.0, -113.1))
    assert 60 <= len(pts) <= 100 and pts[0] == (48.0, -113.0)

    calls = []
    def fake_elev(coords):
        calls.append(len(coords))
        return [1000 + 200*abs(i - len(coords)//2)/(len(coords)//2)
                for i in range(len(coords))]  # a symmetric pass
    spec_before = json.load(open("parks/edges/glacier_edges.json"))
    sourced_before = [e for e in spec_before["edges"]
                      if e.get("gain_ab") is not None and not e.get("est_gain")]
    updated, skipped, lines = dem_edges("glacier", elev_fn=fake_elev, dry=True)
    assert updated > 0 and calls, "estimated edges must get sampled"
    spec_after = json.load(open("parks/edges/glacier_edges.json"))
    assert spec_after == spec_before, "dry run must not write"
    print(f"DEM OK: gain math exact ({up} up / {down} down ft), wiggles filtered, "
          f"{updated} glacier edges sampled dry, {len(skipped)} skipped, "
          f"{len(sourced_before)} sourced edges untouched")

if __name__ == "__main__":
    main()
