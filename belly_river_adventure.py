#!/usr/bin/env python3
"""
belly_river_adventure.py (Switchback)

Working demo of Switchback's adventure mode on Glacier's Belly River area.
Fetches LIVE availability from recreation.gov for the ten camps in
belly_river_graph.json, then:
  1. prints the choose-your-own-adventure walkthrough (night-1 frontier
     from all trailheads, pick Elizabeth Lake Foot, night-2 frontier, ...)
  2. prints every bookable 3-night itinerary in the date window, ranked.

Rules per SPEC.md section 10: virtual origin over all
trailheads, same-trailhead return, direction-aware gain, backward
feasibility so every option shown has at least one valid ending,
endings_remaining on every card.
"""
import json
import heapq
import itertools
import urllib.request
import urllib.parse
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor

PERMIT_ID = "4675321"  # Glacier National Park Wilderness Permits
BASE = "https://www.recreation.gov"
UA = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/124.0.0.0 Safari/537.36"),
      "Accept": "application/json"}

# ---- trip request (edit these) -------------------------------------------
PARTY = 2
NIGHTS = 3
WINDOW_START = date(2026, 7, 10)
WINDOW_END = date(2026, 9, 22)          # last allowed first-night
MAX_MI, MAX_GAIN = 13.0, 4000
PREF_MI, PREF_GAIN = 9.0, 2200
W_DAYFIT, W_CAMP = 0.4, 0.6

# ---- data ----------------------------------------------------------------
def _get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))

G = json.load(open(__file__.rsplit("/", 1)[0] + "/belly_river_graph.json"))
CAMPS, THS = G["camps"], set(G["trailheads"])
ADJ = {}
for e in G["edges"]:
    ADJ.setdefault(e["a"], []).append((e["b"], e["miles"], e["gain_ab"]))
    ADJ.setdefault(e["b"], []).append((e["a"], e["miles"], e["loss_ab"]))

def leg(a, b):
    """Shortest trail path a->b: (miles, gain_in_direction). Pass-throughs allowed."""
    pq, seen = [(0.0, 0, a)], {}
    while pq:
        mi, gain, node = heapq.heappop(pq)
        if node in seen:
            continue
        seen[node] = (mi, gain)
        if node == b:
            return mi, gain
        for nxt, m, g in ADJ.get(node, []):
            if nxt not in seen:
                heapq.heappush(pq, (round(mi + m, 1), gain + g, nxt))
    return None

LEG = {(a, b): leg(a, b) for a in list(CAMPS) + list(THS)
       for b in list(CAMPS) + list(THS) if a != b}

def ok(a, b):
    mi, gain = LEG[(a, b)]
    return mi <= MAX_MI and gain <= MAX_GAIN

def day_fit(a, b):
    mi, gain = LEG[(a, b)]
    f_mi = max(0.0, 1 - abs(mi - PREF_MI) / PREF_MI)
    f_g = max(0.0, 1 - abs(gain - PREF_GAIN) / PREF_GAIN)
    return (f_mi + f_g) / 2

# ---- live availability ----------------------------------------------------
def division_ids():
    payload = _get(f"{BASE}/api/permitcontent/{PERMIT_ID}").get("payload", {})
    out = {}
    for d in (payload.get("divisions") or {}).values():
        name = d.get("name") or ""
        code = name.split(" - ")[0].strip()
        if code in CAMPS and "Spike" not in name and "Hitch" not in name \
                and "Administrative" not in name:
            out[code] = str(d.get("id"))
    return out

def month_avail(div_id, year, month):
    url = (f"{BASE}/api/permititinerary/{PERMIT_ID}/division/{div_id}"
           f"/availability/month?month={month}&year={year}&commercial=false")
    payload = _get(url).get("payload", {}) or {}
    per = {}
    for _qt, dm in (payload.get("quota_type_maps") or {}).items():
        for dstr, cell in dm.items():
            cur = per.setdefault(dstr[:10], 0)
            per[dstr[:10]] = cur + (cell.get("remaining") or 0)
    if not per:
        for dstr, val in (payload.get("bools") or {}).items():
            per[dstr[:10]] = 1 if val else 0
    return per

def fetch_availability():
    ids = division_ids()
    avail = {c: {} for c in ids}
    jobs = [(c, ids[c], y, m) for c in ids for (y, m) in ((2026, 7), (2026, 8), (2026, 9))]
    def work(j):
        c, i, y, m = j
        return c, month_avail(i, y, m)
    with ThreadPoolExecutor(max_workers=6) as ex:
        for c, per in ex.map(work, jobs):
            avail[c].update(per)
    return avail

AV = fetch_availability()
RELAX = False

def open_night(camp, d):
    if RELAX:
        return True
    return AV.get(camp, {}).get(d.isoformat(), 0) >= PARTY

# ---- solver: DP with backward feasibility ---------------------------------
def itineraries(start_d, th):
    """All camp sequences of length NIGHTS from/to th within bounds+availability."""
    outs = []
    def rec(pos, night, seq):
        if night == NIGHTS:
            if ok(pos, th):
                outs.append(tuple(seq))
            return
        d = start_d + timedelta(days=night)
        for c in CAMPS:
            if (c == pos or ok(pos, c)) and open_night(c, d):
                rec(c, night + 1, seq + [c])
    rec(th, 0, [])
    return outs

def score(seq, th):
    stops = [th] + list(seq) + [th]
    fits = [day_fit(a, b) for a, b in zip(stops, stops[1:]) if a != b]
    camp_avg = sum(CAMPS[c]["draft_prior"] for c in seq) / len(seq) / 5
    return W_DAYFIT * (sum(fits) / max(len(fits), 1)) + W_CAMP * camp_avg

# ---- output ----------------------------------------------------------------
def card(pos, c, d, remaining_endings):
    mi, gain = (0.0, 0) if c == pos else LEG[(pos, c)]
    r = AV.get(c, {}).get(d.isoformat(), 0)
    lk = "lake" if CAMPS[c]["lake"] else "    "
    return (f"  {c} {CAMPS[c]['name']:<20} rating {CAMPS[c]['draft_prior']:.1f}  "
            f"{mi:>4.1f} mi  +{gain:<4} ft  {lk}  {r} sites open  "
            f"endings: {remaining_endings}")

def walkthrough():
    # find first date where an ELF-first itinerary exists from SWIFT_TH
    for offset in range((WINDOW_END - WINDOW_START).days + 1):
        d0 = WINDOW_START + timedelta(days=offset)
        its = itineraries(d0, "SWIFT_TH")
        elf_first = [s for s in its if s[0] == "ELF"]
        if elf_first:
            print(f"\n=== ADVENTURE MODE: start {d0}, party of {PARTY}, "
                  f"{NIGHTS} nights, return to Iceberg/Ptarmigan TH ===")
            n1 = sorted({s[0] for s in its})
            print(f"\nNight 1 frontier (from Iceberg/Ptarmigan TH), "
                  f"{len(its)} total endings:")
            for c in n1:
                print(card("SWIFT_TH", c, d0, len([s for s in its if s[0] == c])))
            print("\n> You choose ELF Elizabeth Lake Foot.")
            n2 = sorted({s[1] for s in elf_first})
            print(f"\nNight 2 frontier (from Elizabeth Lake Foot):")
            for c in n2:
                print(card("ELF", c, d0 + timedelta(days=1),
                           len([s for s in elf_first if s[1] == c])))
            return
    print("\nNo ELF-first itinerary from Many Glacier exists in the window.")

def batch():
    rows = []
    for offset in range((WINDOW_END - WINDOW_START).days + 1):
        d0 = WINDOW_START + timedelta(days=offset)
        for th in THS:
            for seq in itineraries(d0, th):
                rows.append((score(seq, th), d0, th, seq))
    rows.sort(reverse=True)
    print(f"\n=== BATCH MODE: {len(rows)} bookable {NIGHTS}-night itineraries "
          f"{WINDOW_START} to {WINDOW_END} (party {PARTY}) ===")
    seen_dates = set()
    shown = 0
    for sc, d0, th, seq in rows:
        key = (d0.isocalendar()[1], seq)   # one per week per route
        if key in seen_dates:
            continue
        seen_dates.add(key)
        print(f"  {sc:.2f}  start {d0}  {th:<8} " + " > ".join(seq))
        shown += 1
        if shown >= 15:
            break
    if not rows:
        print("  none bookable at current availability (walk-up share excluded)")
    return len(rows)

if __name__ == "__main__":
    open_days = {c: sum(1 for v in AV[c].values() if v >= PARTY) for c in AV}
    print(f"party-of-{PARTY} open dates per camp (Jul-Sep):", open_days)
    walkthrough()
    n = batch()
    if n < 3:
        RELAX = True
        print("\n" + "=" * 70)
        print(f"PLANNING MODE: only {n} advance-bookable chain(s) remain, so the")
        print("frontier below ignores availability. Design the route here, then")
        print("watch for cancellations or line up for the walk-up share.")
        print("=" * 70)
        walkthrough()
