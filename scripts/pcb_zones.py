"""T-021 copper pours and thermal vias (no track routing) — run with KiCad's bundled Python 10.0.7 (D-009):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_zones.py

Adds to the T-020 board: L2 (In1.Cu) GND plane, L3 (In2.Cu) /VIN, /VOUT, /VSAFE pours and local /GND islands under the
LM70880s, L4 (B.Cu) secondary GND, and via-in-pad arrays on the exposed/drain/source pads. Fills all zones and writes
reports/g5/T-021/zone-audit.json and thermal-area.json. Coordinates: D-006 (origin lower-left, y up).
Via size and counts are VARSAYIM (PCB-HANDOFF §7 DFM 0.3/0.6 via-in-pad filled; manufacturer confirmation AÇIK).
Run on a clean T-020 board (`git checkout -- PDU.kicad_pcb` first): the script only adds items.
"""
from __future__ import annotations

import heapq
import json
import math
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "PDU.kicad_pcb"
OUT = ROOT / "reports" / "g5" / "T-021"
W, H, OX, OY = 120.0, 85.0, 30.0, 30.0
VIA_D, VIA_DRILL = 0.6, 0.3
MIN_AREA_MM2 = 645.16          # 1 in² (PCB-HANDOFF §3.4/§4)
E = 0.7                        # copper-to-edge margin of the pour outlines (rule: 0.5 mm)

FULL = [(E, E), (W - E, E), (W - E, H - E), (E, H - E)]
# (name, net, layer, priority, outline)
ZONES = [
    ("L2_GND", "/GND", "In1", 0, FULL),
    ("L4_GND", "/GND", "B", 0, FULL),
    ("L3_VIN", "/VIN", "In2", 0, [(E, E), (59.8, E), (59.8, 28.0), (24.2, 28.0), (24.2, 57.6), (59.8, 57.6), (59.8, H - E), (E, H - E)]),
    ("L3_VOUT", "/VOUT", "In2", 0, [(24.5, 28.4), (97.2, 28.4), (97.2, 57.3), (24.5, 57.3)]),
    # Q2 source pads face west (bank side): pocket + wide north band (L3 is empty above y 58) carries /VSAFE to the eFuse side.
    # Band height 18.3+ mm follows routing-g2 BUS_POWER inner_width_min (R-016 path check found a 1.3 mm strip in round 1).
    ("L3_VSAFE", "/VSAFE", "In2", 1, [(86.2, 53.0), (92.0, 53.0), (92.0, 56.7), (97.6, 56.7), (97.6, 8.0), (W - E, 8.0), (W - E, 77.0), (86.2, 77.0)]),
    ("L3_GND_U1", "/GND", "In2", 2, [(45.5, 73.0), (52.5, 73.0), (52.5, 80.0), (45.5, 80.0)]),
    ("L3_GND_U2", "/GND", "In2", 2, [(31.0, 4.0), (38.0, 4.0), (38.0, 11.0), (31.0, 11.0)]),
]
# (ref, pad number, net, nx, ny, pitch x, pitch y) — grid centred on the (largest) copper pad of that number
ARRAYS = [("U1", "30", "/GND", 3, 2, 1.0, 0.8), ("U2", "30", "/GND", 3, 2, 1.0, 0.8),
          ("Q1", "5", "/VIN", 3, 3, 1.2, 1.2), ("Q2", "5", "/VOUT", 3, 3, 1.2, 1.2)]
PAD_VIAS = [("Q2", "1", "/VSAFE"), ("Q2", "2", "/VSAFE"), ("Q2", "3", "/VSAFE")]
THERMAL = {"Q1": ("/VIN", "In2"), "Q2": ("/VOUT", "In2")}
# R-016: 100 nF input caps at their eFuse IN-GND pin pairs (TPS25982 §11.1). (ref, x, y, rot, refdes x, y, angle); pad 1 (/VSAFE) north.
# U3 uses west IN 1-3 / GND 4-5 (U4 sits east of it); U4 uses east IN 16 / GND 14 because its west pins face U3.
MOVES = [("CEFIN1", 98.2, 41.2, 270, 96.75, 41.2, 90), ("CEFIN2", 110.6, 40.67, 270, 112.05, 40.67, 90)]
REFDES_ONLY = [("U3", 101.6, 37.6, 0)]
GRID = 0.2                      # mm, q2-path raster
END_R = 2.5                     # mm: local pad/via surroundings excluded from the bottleneck (a via's own edge is not a corridor)
BUS_INNER_MIN = 18.36           # routing-g2 BUS_POWER inner_width_min_mm (7.5 A, IPC-2221 fit, screening)
BUS_VIAS_MIN = 15               # routing-g2 BUS_POWER vias_min


def raster(polys):
    """Even-odd scan conversion of a fractured SHAPE_POLY_SET -> list of bytearray rows, row 0 at D-006 y = GRID/2."""
    nx, ny = int(W / GRID), int(H / GRID)
    rows = [bytearray(nx) for _ in range(ny)]
    for o in range(polys.OutlineCount()):
        ol = polys.COutline(o)
        pts = [(P.ToMM(ol.CPoint(i).x) - OX, OY + H - P.ToMM(ol.CPoint(i).y)) for i in range(ol.PointCount())]
        for r in range(ny):
            y = (r + 0.5) * GRID
            xs = sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) for a, b in zip(pts, pts[1:] + pts[:1]) if (a[1] <= y) != (b[1] <= y))
            for x0, x1 in zip(xs[::2], xs[1::2]):
                for c in range(max(0, int(x0 / GRID + 0.5)), min(nx, int(x1 / GRID + 0.5))):
                    rows[r][c] ^= 1
    return rows


def clearance(m):
    """3-4 chamfer distance to non-copper, in mm."""
    ny, nx = len(m), len(m[0])
    d = [[(10 ** 9 if m[r][c] else 0) for c in range(nx)] for r in range(ny)]
    for r in range(ny):
        for c in range(nx):
            if d[r][c]:
                v = d[r][c]
                if c:
                    v = min(v, d[r][c - 1] + 3)
                if r:
                    v = min(v, d[r - 1][c] + 3)
                    if c:
                        v = min(v, d[r - 1][c - 1] + 4)
                    if c + 1 < nx:
                        v = min(v, d[r - 1][c + 1] + 4)
                d[r][c] = v if (c and r and c + 1 < nx and r + 1 < ny) else min(v, 3)
    for r in range(ny - 1, -1, -1):
        for c in range(nx - 1, -1, -1):
            if d[r][c]:
                v = d[r][c]
                if c + 1 < nx:
                    v = min(v, d[r][c + 1] + 3)
                if r + 1 < ny:
                    v = min(v, d[r + 1][c] + 3)
                    if c + 1 < nx:
                        v = min(v, d[r + 1][c + 1] + 4)
                    if c:
                        v = min(v, d[r + 1][c - 1] + 4)
                d[r][c] = v
    return [[x * GRID / 3.0 for x in row] for row in d]


N8 = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]


def cell(m, x, y):
    """Nearest copper cell to a D-006 point (via/pad centres can sit in the anti-pad of a not yet existing via)."""
    r0, c0 = int(y / GRID), int(x / GRID)
    for rad in range(0, 15):
        for r in range(r0 - rad, r0 + rad + 1):
            for c in range(c0 - rad, c0 + rad + 1):
                if 0 <= r < len(m) and 0 <= c < len(m[0]) and m[r][c]:
                    return r, c
    return None


def spread(m, cl, src):
    """From the source cells: shortest in-copper length and widest-path bottleneck (full width mm) to every cell."""
    ny, nx = len(m), len(m[0])
    dist, q = {}, []
    for r, c in src:
        dist[(r, c)] = 0.0
        heapq.heappush(q, (0.0, r, c))
    while q:
        d0, r, c = heapq.heappop(q)
        if d0 > dist[(r, c)]:
            continue
        for dr, dc, w in N8:
            a, b = r + dr, c + dc
            if 0 <= a < ny and 0 <= b < nx and m[a][b]:
                nd = d0 + w * GRID
                if nd < dist.get((a, b), 1e18):
                    dist[(a, b)] = nd
                    heapq.heappush(q, (nd, a, b))
    rad = int(END_R / GRID)
    near_src = {(r + a, c + b) for r, c in src for a in range(-rad, rad + 1) for b in range(-rad, rad + 1) if a * a + b * b <= rad * rad}
    wid, q = {}, []
    for r, c in src:
        wid[(r, c)] = 1e9
        heapq.heappush(q, (-1e9, r, c))
    while q:
        w0, r, c = heapq.heappop(q)
        if -w0 < wid[(r, c)]:
            continue
        for dr, dc, _ in N8:
            a, b = r + dr, c + dc
            if 0 <= a < ny and 0 <= b < nx and m[a][b]:
                nw = -w0 if (a, b) in near_src else min(-w0, cl[a][b])
                if nw > wid.get((a, b), 0.0):
                    wid[(a, b)] = nw
                    heapq.heappush(q, (-nw, a, b))
    return dist, wid


def kpos(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY + H - y))


def layer(n):
    return {"In1": P.In1_Cu, "In2": P.In2_Cu, "B": P.B_Cu, "F": P.F_Cu}[n]


def main() -> int:
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    b = P.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    nets = b.GetNetInfo()
    for ref, x, y, rot, tx, ty, ang in MOVES:
        fps[ref].SetOrientationDegrees(rot)
        fps[ref].SetPosition(kpos(x, y))
        t = fps[ref].Reference()
        t.SetPosition(kpos(tx, ty))
        t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))
    for ref, tx, ty, ang in REFDES_ONLY:
        t = fps[ref].Reference()
        t.SetPosition(kpos(tx, ty))
        t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))
    made = {}
    for name, net, lay, prio, pts in ZONES:
        z = P.ZONE(b)
        z.SetZoneName(name)
        z.SetNet(nets.GetNetItem(net))
        z.SetLayer(layer(lay))
        z.SetAssignedPriority(prio)
        z.SetMinThickness(P.FromMM(0.25))
        z.SetLocalClearance(P.FromMM(0.3))
        z.SetThermalReliefGap(P.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(P.FromMM(0.5))
        z.SetPadConnection(P.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            p = kpos(x, y)
            ol.Append(p.x, p.y)
        b.Add(z)
        made[name] = z

    vias = []

    def add_via(x_mm, y_mm, net, tag):
        v = P.PCB_VIA(b)
        v.SetPosition(P.VECTOR2I(P.FromMM(x_mm), P.FromMM(y_mm)))
        v.SetViaType(P.VIATYPE_THROUGH)
        v.SetLayerPair(P.F_Cu, P.B_Cu)
        v.SetDrill(P.FromMM(VIA_DRILL))
        v.SetWidth(P.F_Cu, P.FromMM(VIA_D))
        v.SetNet(nets.GetNetItem(net))
        b.Add(v)
        vias.append({"tag": tag, "net": net, "x_d006": round(x_mm - OX, 3), "y_d006": round(OY + H - y_mm, 3),
                     "pad_mm": VIA_D, "drill_mm": VIA_DRILL})

    for ref, num, net, nx, ny, px, py in ARRAYS:
        pad = max((p for p in fps[ref].Pads() if p.GetNumber() == num), key=lambda p: p.GetSize(P.F_Cu).x * p.GetSize(P.F_Cu).y)
        c = pad.GetPosition()
        cx, cy = P.ToMM(c.x), P.ToMM(c.y)
        for i in range(nx):
            for j in range(ny):
                add_via(cx + (i - (nx - 1) / 2) * px, cy + (j - (ny - 1) / 2) * py, net, f"{ref}.{num}")
    for ref, num, net in PAD_VIAS:
        c = next(p for p in fps[ref].Pads() if p.GetNumber() == num).GetPosition()
        add_via(P.ToMM(c.x), P.ToMM(c.y), net, f"{ref}.{num}")

    filler = P.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildConnectivity()
    P.SaveBoard(str(PCB), b, True)

    def poly_area(polys, i):
        a = polys.COutline(i).Area()
        for h in range(polys.HoleCount(i)):
            a -= polys.CHole(i, h).Area()
        return abs(a) * 1e-12 if False else abs(a) / (P.FromMM(1.0) ** 2)

    audit = []
    pieces = {}
    for name, z in made.items():
        lay = z.GetFirstLayer()
        polys = z.GetFilledPolysList(lay)
        areas = [round(poly_area(polys, i), 2) for i in range(polys.OutlineCount())]
        pieces[name] = polys
        audit.append({"zone": name, "net": z.GetNetname(), "layer": b.GetLayerName(lay), "priority": z.GetAssignedPriority(),
                      "islands": polys.OutlineCount(), "fill_area_mm2": round(sum(areas), 2), "island_areas_mm2": areas})
    thermal = {}
    for ref, (net, lay) in THERMAL.items():
        zone_name = {"Q1": "L3_VIN", "Q2": "L3_VOUT"}[ref]
        v = next(x for x in vias if x["tag"] == f"{ref}.5")
        pt = kpos(v["x_d006"], v["y_d006"])
        polys = pieces[zone_name]
        idx = next((i for i in range(polys.OutlineCount()) if polys.COutline(i).PointInside(pt)), None)
        area = poly_area(polys, idx) if idx is not None else 0.0
        thermal[ref] = {"net": net, "layer": lay + ".Cu", "zone": zone_name, "connected_by": f"{sum(1 for x in vias if x['tag'] == f'{ref}.5')} vias on pad 5",
                        "connected_fill_area_mm2": round(area, 2), "required_mm2": MIN_AREA_MM2, "pass": area >= MIN_AREA_MM2}
    def pad_pt(ref, num):
        c = next(x for x in fps[ref].Pads() if x.GetNumber() == num).GetPosition()
        return P.ToMM(c.x) - OX, OY + H - P.ToMM(c.y)

    def via_pts(tag):
        return [(v["x_d006"], v["y_d006"]) for v in vias if v["tag"] in tag]

    fault = {"basis": "HESAP on filled copper (GRID mm raster, 3-4 chamfer). Not a routed path: COUT, U3/U4 and CEFIN have no vias to L3 yet, "
                      "so each pad is treated as if a via to L3 stood at its centre (T-022 must add them). Width = 2 x bottleneck clearance, excluding END_R around sources and targets.",
             "grid_mm": GRID, "end_exclusion_radius_mm": END_R, "bus_inner_min_width_mm": BUS_INNER_MIN, "bus_vias_min": BUS_VIAS_MIN}
    for key, zone, srcs, targets in (
            ("VOUT_Q2_drain_to_COUT", "L3_VOUT", via_pts(("Q2.5",)), {f"COUT{i}": pad_pt(f"COUT{i}", "1") for i in range(1, 33)}),
            ("VSAFE_Q2_source_to_eFuse", "L3_VSAFE", via_pts(("Q2.1", "Q2.2", "Q2.3")), {"U3_IN_1": pad_pt("U3", "1"), "U4_IN_16": pad_pt("U4", "16"), "CEFIN1_1": pad_pt("CEFIN1", "1"), "CEFIN2_1": pad_pt("CEFIN2", "1")})):
        m = raster(pieces[zone])
        cl = clearance(m)
        src = [cell(m, x, y) for x, y in srcs]
        dist, wid = spread(m, cl, [c for c in src if c])
        res = {}
        for name, (x, y) in targets.items():
            c = cell(m, x, y)
            rad = int(END_R / GRID)
            best = max((wid.get((c[0] + a, c[1] + b), 0.0) for a in range(-rad, rad + 1) for b in range(-rad, rad + 1) if a * a + b * b <= rad * rad), default=0.0)
            res[name] = {"len_mm": round(dist[c], 2), "bottleneck_width_mm": round(2 * best, 2)} if c in dist else {"unreachable": True}
        ok = [v for v in res.values() if "len_mm" in v]
        fault[key] = {"zone": zone, "sources": len(srcs), "targets": res, "len_min_mm": min(v["len_mm"] for v in ok), "len_max_mm": max(v["len_mm"] for v in ok),
                      "bottleneck_min_mm": min(v["bottleneck_width_mm"] for v in ok), "unreachable": [k for k, v in res.items() if "len_mm" not in v]}
    gnd = {}
    for ref, num in (("CEFIN1", "2"), ("CEFIN2", "2")):
        p0 = pad_pt(ref, num)
        cg = [pad_pt(f"COUT{i}", "2") for i in range(1, 33)]
        gnd[ref] = {"to_nearest_COUT_GND_mm": round(min(math.dist(p0, q) for q in cg), 2)}
    fault["L2_GND_return_straight_line"] = gnd
    fault["via_counts"] = {"Q2_drain_L3": len(via_pts(("Q2.5",))), "Q2_source_L3": len(via_pts(("Q2.1", "Q2.2", "Q2.3"))), "required_each": BUS_VIAS_MIN}
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, obj in (("zone-audit.json", {"kicad": P.GetBuildVersion(), "zones": audit, "vias": vias}),
                    ("thermal-area.json", thermal), ("q2-path.json", fault)):
        with (OUT / fn).open("w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(json.dumps({"zones": [(a["zone"], a["islands"], a["fill_area_mm2"]) for a in audit], "vias": len(vias), "thermal": {k: v["connected_fill_area_mm2"] for k, v in thermal.items()},
                      "VOUT": {k: fault["VOUT_Q2_drain_to_COUT"][k] for k in ("len_min_mm", "len_max_mm", "bottleneck_min_mm", "unreachable")},
                      "VSAFE": fault["VSAFE_Q2_source_to_eFuse"]["targets"], "gnd": gnd}))
    return 0 if all(v["pass"] for v in thermal.values()) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
