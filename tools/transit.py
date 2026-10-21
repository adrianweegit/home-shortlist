"""Estimate weekday-morning public-transport trips from a home to each saved place.

Modes: walk; direct bus; walk/bus -> MRT (NEL preferred, CCL/NSL/DTL allowed) -> walk/bus.
No LRT. At most one bus leg plus rail, or one bus leg alone. Kids' walking pace.
"""
import json, math, sys, os, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hs

# Bus stops and routes from the open sgbusdata project (LTA DataMall), cached locally.
CACHE = os.environ.get("HS_BUS_CACHE", "/tmp/hs-busdata")
def _data(name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/cheeaun/sgbusdata/main/data/v1/{name}", p)
    return json.load(open(p))
stops = _data("stops.min.json")
services = _data("services.min.json")

WALK_MPM, DETOUR = 70.0, 1.3          # child walking pace m/min, street detour
BUS_MIN_PER_KM, BUS_WAIT = 3.4, 6.0   # peak bus incl. stops; average wait
RAIL_STOP_MIN, RAIL_WAIT, XFER = 2.2, 3.0, 5.0
BOARD_R, ALIGHT_R = 450, 450          # m to/from bus stops
STN_WALK_MAX = 1300                   # m walking to a station

def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 6371000*2*math.asin(math.sqrt(h))
def walk_min(a, b): return hav(a, b)*DETOUR/WALK_MPM

# Rail network (lat, lng), ordered per line.
LINES = {
 "NEL": [("Little India","NE7",1.3066,103.8492),("Farrer Park","NE8",1.3124,103.8546),("Boon Keng","NE9",1.3195,103.8618),
         ("Potong Pasir","NE10",1.3313,103.8690),("Woodleigh","NE11",1.33919,103.87082),("Serangoon","NE12",1.3498,103.8735),
         ("Kovan","NE13",1.3601,103.8850),("Hougang","NE14",1.3713,103.8925),("Buangkok","NE15",1.3829,103.8930),
         ("Sengkang","NE16",1.3917,103.8953),("Punggol","NE17",1.4052,103.9024),("Punggol Coast","NE18",1.4155,103.9108)],
 "CCL": [("MacPherson","CC10",1.3266,103.8900),("Tai Seng","CC11",1.3359,103.8878),("Bartley","CC12",1.3427,103.8797),
         ("Serangoon","CC13",1.3498,103.8735),("Lorong Chuan","CC14",1.3516,103.8640),("Bishan","CC15",1.3510,103.8485),
         ("Marymount","CC16",1.3492,103.8394)],
 "NSL": [("Bishan","NS17",1.3510,103.8485),("Ang Mo Kio","NS16",1.3700,103.8495),("Yio Chu Kang","NS15",1.3818,103.8449)],
 "DTL": [("MacPherson","DT26",1.3266,103.8900),("Ubi","DT27",1.3300,103.8990),("Kaki Bukit","DT28",1.3349,103.9085),
         ("Bedok North","DT29",1.3352,103.9180),("Bedok Reservoir","DT30",1.3366,103.9322),("Tampines West","DT31",1.3456,103.9384)],
}
STN = {}
for line, sts in LINES.items():
    for i, (n, code, la, lo) in enumerate(sts):
        STN.setdefault(n, {"pos": (la, lo), "codes": []})["codes"].append(code)

def rail(a, b):
    """Best (minutes, transfers, description) between stations a and b using up to 2 line changes."""
    import heapq
    graph = {}
    for line, sts in LINES.items():
        for i in range(len(sts)-1):
            x, y = (sts[i][0], line), (sts[i+1][0], line)
            graph.setdefault(x, []).append((y, RAIL_STOP_MIN)); graph.setdefault(y, []).append((x, RAIL_STOP_MIN))
    for n in STN:  # interchange edges
        ls = [l for l in LINES if any(s[0] == n for s in LINES[l])]
        for l1 in ls:
            for l2 in ls:
                if l1 != l2: graph.setdefault((n, l1), []).append(((n, l2), XFER))
    starts = [(n, l) for (n, l) in graph if n == a]
    best = None
    pq = [(0.0, 0, s, [s]) for s in starts]
    seen = {}
    while pq:
        t, x, node, path = heapq.heappop(pq)
        if node[0] == b:
            if best is None or t < best[0]: best = (t, x, path)
            continue
        if seen.get(node, 1e9) <= t: continue
        seen[node] = t
        for nb, w in graph.get(node, []):
            nx = x + (1 if nb[0] == node[0] else 0)
            if nx <= 2: heapq.heappush(pq, (t+w, nx, nb, path+[nb]))
    if not best: return None
    t, x, path = best
    lines = []
    for n, l in path:
        if not lines or lines[-1] != l: lines.append(l)
    stops_n = sum(1 for i in range(1, len(path)) if path[i][0] != path[i-1][0])
    return t, x, lines, stops_n

STOP_POS = {k: (v[1], v[0]) for k, v in stops.items()}
def near_stops(p, r): return [(k, hav(p, q)) for k, q in STOP_POS.items() if hav(p, q) <= r]

def bus_legs(origin_stops, dest_stops):
    """Direct bus options: list of (svc, board, alight, ride_min)."""
    o = dict(origin_stops); d = dict(dest_stops); out = []
    for svc, info in services.items():
        for route in info.get("routes", []):
            idx = {s: i for i, s in enumerate(route)}
            for b in o:
                if b not in idx: continue
                for a in d:
                    if a in idx and idx[a] > idx[b]:
                        seg = route[idx[b]:idx[a]+1]
                        km = sum(hav(STOP_POS[seg[i]], STOP_POS[seg[i+1]]) for i in range(len(seg)-1) if seg[i] in STOP_POS and seg[i+1] in STOP_POS)/1000*1.2
                        out.append((svc, b, a, km*BUS_MIN_PER_KM, len(seg)-1))
    return out

def name(stop): return stops[stop][2] if stop in stops else stop

SHUTTLE_MIN = 10  # wait + ride on a condo shuttle to its MRT (runs to a timetable)

def trips(origin, dest, dest_label, dest_is_station=None, shuttle=None):
    """shuttle: {"to": <station name in STN>, "verified": bool} — a condo shuttle bus to the MRT.
    A verified shuttle replaces the first leg; an unverified one is only reported under withShuttle."""
    opts = []
    w = walk_min(origin, dest)
    if w <= 18: opts.append(dict(min=w, xfers=0, walk=w, desc=f"Walk {round(w)} min", mode="walk"))
    os_ = near_stops(origin, BOARD_R); ds = near_stops(dest, ALIGHT_R)
    # direct bus
    for svc, b, a, ride, n in bus_legs(os_, ds):
        wb = walk_min(origin, STOP_POS[b]); wa = walk_min(STOP_POS[a], dest)
        t = wb + BUS_WAIT + ride + wa
        opts.append(dict(min=t, xfers=0, walk=max(wb, wa), mode="bus",
                         desc=f"Walk {round(wb)} min → bus {svc} at {name(b)} ({n} stop{"s" if n != 1 else ""}) → walk {round(wa)} min"))
    # stations usable at each end
    o_stn = [(s, walk_min(origin, v["pos"])) for s, v in STN.items() if hav(origin, v["pos"])*DETOUR <= STN_WALK_MAX]
    if dest_is_station: d_stn = [(dest_is_station, 0.0, None)]
    else:
        d_stn = [(s, walk_min(v["pos"], dest), None) for s, v in STN.items() if hav(dest, v["pos"])*DETOUR <= 1700]
    # bus to a station (feeder) — stops within 250 m of a station
    feeder = []
    for s, v in STN.items():
        fs = near_stops(v["pos"], 250)
        for svc, b, a, ride, n in bus_legs(os_, fs):
            wb = walk_min(origin, STOP_POS[b]); wa = walk_min(STOP_POS[a], v["pos"])
            feeder.append((s, wb + BUS_WAIT + ride + wa, f"Walk {round(wb)} min → bus {svc} ({n} stop{"s" if n != 1 else ""}) to {s}", max(wb, wa)))
    # bus from a station to destination (for the school)
    egress = []
    if not dest_is_station:
        for s, v in STN.items():
            fs = near_stops(v["pos"], 250)
            for svc, b, a, ride, n in bus_legs(fs, ds):
                wa = walk_min(STOP_POS[a], dest)
                egress.append((s, BUS_WAIT + ride + wa + 2, f"bus {svc} from {s} ({n} stop{"s" if n != 1 else ""}) → walk {round(wa)} min", wa))
    def add_rail(s1, t_in, desc_in, walk_in, s2, t_out, desc_out, walk_out, extra_x):
        if s1 == s2:
            return
        r = rail(s1, s2)
        if not r: return
        rt, rx, lines, n = r
        line_txt = " → ".join(lines)
        t = t_in + RAIL_WAIT + rt + t_out
        x = rx + extra_x
        code = "/".join(STN[s1]["codes"])
        opts.append(dict(min=t, xfers=x, walk=max(walk_in, walk_out), mode="mrt",
                         nel=("NEL" in lines), lines=lines,
                         desc=f"{desc_in} → {line_txt} {s1} to {s2} ({n} stop{"s" if n != 1 else ""})" + (f" → {desc_out}" if desc_out else "")))
    ins = [(s, t, f"Walk {round(t)} min to {s} ({'/'.join(STN[s]['codes'])})", t, 0) for s, t in o_stn] + \
          [(s, t, d, wk, 1) for s, t, d, wk in feeder]
    sh = shuttle and shuttle.get("to") in STN and shuttle.get("to")
    if sh: ins.append((sh, SHUTTLE_MIN, f"Condo shuttle to {sh} ({'/'.join(STN[sh]['codes'])})", 2, 0))
    outs = [(s, t, (f"walk {round(t)} min" if t > 0.5 else ""), t, 0) for s, t, _ in d_stn] + \
           [(s, t, d, wk, 1) for s, t, d, wk in egress]
    for s1, t1, d1, w1, x1 in ins:
        for s2, t2, d2, w2, x2 in outs:
            add_rail(s1, t1, d1, w1, s2, t2, d2, w2, x1 + x2)
    if not opts: return None
    # Kids: penalise each change and long walks a little when choosing
    best = min(opts, key=lambda o: o["min"] + 5*o["xfers"] + max(0, o["walk"]-10))
    m, x, wk = best["min"], best["xfers"], best["walk"]
    if best["mode"] == "walk":
        rating = "easy" if m <= 12 else "ok" if m <= 20 else "hard"
    else:
      rating = "easy" if (m <= 25 and x == 0 and wk <= 10) or (m <= 22 and x <= 1 and wk <= 8) else \
               "hard" if (m > 40 or x >= 2 or wk > 15) else "ok"
    out = dict(min=round(m), xfers=x, walk=round(wk), rating=rating, route=best["desc"],
               mode=best["mode"], nel=bool(best.get("nel")), shuttle=bool(sh and best["desc"].startswith("Condo shuttle")))
    return out


def for_point(lat, lng, places, shuttle=None):
    o = (lat, lng)
    out = {}
    for p in places:
        d = (p["lat"], p["lng"]); st = p.get("station")
        if shuttle and shuttle.get("to") and not shuttle.get("verified"):
            # unverified: rate without it, but show what it would give
            t = trips(o, d, p["label"], dest_is_station=st)
            w = trips(o, d, p["label"], dest_is_station=st, shuttle=dict(shuttle, verified=True))
            if t and w and w.get("shuttle") and w["min"] < t["min"]: t["withShuttle"] = {"min": w["min"], "rating": w["rating"], "route": w["route"]}
            out[p["key"]] = t
        else:
            out[p["key"]] = trips(o, d, p["label"], dest_is_station=st, shuttle=shuttle if shuttle and shuttle.get("verified") else None)
    return out

USAGE = """Usage:
  transit.py point <lat> <lng> [shuttleStation] [verified]   print trips from a point to every saved place
  transit.py unit <unitId> <lat> <lng>  compute and save lat/lng + transit on a unit
  transit.py all                        recompute every unit that has lat/lng
Places come from Firestore hs_meta/places (items: key, label, lat, lng, optional station)."""

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(USAGE)
    places = hs.get("meta", "places")["items"]
    if a[0] == "point":
        sh = {"to": a[3], "verified": len(a) > 4 and a[4].lower().startswith("v")} if len(a) > 3 else None
        print(json.dumps(for_point(float(a[1]), float(a[2]), places, sh), ensure_ascii=False, indent=1))
    elif a[0] == "unit":
        lat, lng = float(a[2]), float(a[3])
        u = hs.get("units", a[1]); sh = u.get("shuttle") if isinstance(u.get("shuttle"), dict) else None
        t = for_point(lat, lng, places, sh)
        hs.update("units", a[1], {"lat": lat, "lng": lng, "transit": t})
        print(json.dumps(t, ensure_ascii=False, indent=1))
    elif a[0] == "all":
        for u in hs.list_docs("hs_units"):
            if isinstance(u.get("lat"), (int, float)):
                sh = u.get("shuttle") if isinstance(u.get("shuttle"), dict) else None
                hs.update("units", u["id"], {"transit": for_point(u["lat"], u["lng"], places, sh)})
                print("updated", u["id"])
    else:
        sys.exit(USAGE)
