"""T-022 power routing (D-010 still valid parts + D-011: Q2 at 90 deg) — KiCad's bundled Python 10.0.7 (D-009):

    git checkout <T-021 board> -- PDU.kicad_pcb      # the script only adds/moves items; it refuses a board already routed
    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_route_power.py
    ...python.exe scripts/pcb_route_power.py --audit [--empty-board <file>]     # writes reports/g5/T-022 evidence; optional empty-board copy for independent DRC

Coordinates: D-006 (origin lower-left, y up). Widths and via targets: reports/g2/routing-g2.json. Vias 0.6/0.3 (VARSAYIM, PCB-HANDOFF §7).
Long runs are tracks (checked by the class width rules). Tight pad groups and milliamp taps are filled zones (PCB-HANDOFF §1 L1 power
pours; T-022 "zone tap"): the track_width rules do not see zones, so power-zone widths are measured in the audit, never assumed.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "PDU.kicad_pcb"
OUT = ROOT / "reports" / "g5" / "T-022"
W, H, OX, OY = 120.0, 85.0, 30.0, 30.0
VIA_D, VIA_DRILL = 0.6, 0.3
E = 0.7
LAY = {"F": P.F_Cu, "In1": P.In1_Cu, "In2": P.In2_Cu, "B": P.B_Cu}
TAP = 0.8           # mm, milliamp zone taps; must exceed the 0.6 mm via land or KiCad does not connect the via to the fill
BRANCH = 1.5        # mm: D_REV and CEFOUT branches (R-018), sized in the audit for the 3 A diode rating
Q2_ROT = 90.0
GATE_W = 0.4


def kp(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY + H - y))


def d6(v):
    return P.ToMM(v.x) - OX, OY + H - P.ToMM(v.y)


def mirror_u2(x, y):
    """U1 group -> U2 group: the T-020 placement is a 180 deg copy about (41.75, 42)."""
    return 83.5 - x, 84.0 - y


def ribbon(pts, w):
    """Mitred outline of a polyline, width w."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        if i == 0:
            a = (x, y)
        if i == n - 1:
            b = (x, y)
        ux, uy = (x - a[0], y - a[1]) if i else (b[0] - x, b[1] - y)
        lu = math.hypot(ux, uy)
        ux, uy = ux / lu, uy / lu
        vx, vy = (b[0] - x, b[1] - y) if i < n - 1 else (ux, uy)
        lv = math.hypot(vx, vy)
        vx, vy = vx / lv, vy / lv
        nx, ny = -(uy + vy), (ux + vx)
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        s = max(0.5, (nx * -uy + ny * ux))
        h = w / 2 / s
        left.append((x + nx * h, y + ny * h))
        right.append((x - nx * h, y - ny * h))
    return left + right[::-1]


class Board:
    def __init__(self, path):
        self.b = P.LoadBoard(str(path))
        self.nets = self.b.GetNetInfo()
        self.fp = {f.GetReference(): f for f in self.b.GetFootprints()}
        self.log = {"tracks": [], "vias": [], "zones": []}
        self.pending = {}

    def pad(self, ref, num):
        ps = [p for p in self.fp[ref].Pads() if p.GetNumber() == str(num)]
        p = max(ps, key=lambda q: q.GetBoundingBox().GetWidth() * q.GetBoundingBox().GetHeight())
        bb = p.GetBoundingBox()
        cx, cy = d6(bb.GetCenter())
        return cx, cy, P.ToMM(bb.GetWidth()), P.ToMM(bb.GetHeight())

    def net(self, n):
        return self.nets.GetNetItem(n)

    def track(self, net, lay, w, pts, tag=""):
        for a, c in zip(pts, pts[1:]):
            t = P.PCB_TRACK(self.b)
            t.SetStart(kp(*a))
            t.SetEnd(kp(*c))
            t.SetWidth(P.FromMM(w))
            t.SetLayer(LAY[lay])
            t.SetNet(self.net(net))
            self.b.Add(t)
        length = sum(math.dist(a, c) for a, c in zip(pts, pts[1:]))
        self.log["tracks"].append({"net": net, "layer": lay, "width_mm": w, "length_mm": round(length, 3), "points": pts, "tag": tag})
        return length

    def via(self, net, x, y, tag=""):
        v = P.PCB_VIA(self.b)
        v.SetPosition(kp(x, y))
        v.SetViaType(P.VIATYPE_THROUGH)
        v.SetLayerPair(P.F_Cu, P.B_Cu)
        v.SetDrill(P.FromMM(VIA_DRILL))
        v.SetWidth(P.F_Cu, P.FromMM(VIA_D))
        v.SetNet(self.net(net))
        self.b.Add(v)
        self.log["vias"].append({"net": net, "x": round(x, 3), "y": round(y, 3), "tag": tag})

    def zone(self, name, net, lay, pts, prio=5, tag=""):
        """Polygons of one net, layer and priority are unioned into one ZONE (KiCad reports overlapping equal-priority zones)."""
        self.pending.setdefault((net, lay, prio), []).append((name, pts))
        self.log["zones"].append({"name": name, "net": net, "layer": lay, "tag": tag, "points": [[round(a, 3), round(c, 3)] for a, c in pts]})

    def build_zones(self):
        for (net, lay, prio), polys in self.pending.items():
            s = P.SHAPE_POLY_SET()
            for _, pts in polys:
                o = P.SHAPE_POLY_SET()
                o.NewOutline()
                for x, y in pts:
                    q = kp(x, y)
                    o.Append(q.x, q.y)
                s.BooleanAdd(o)
            for i in range(s.OutlineCount()):       # one ZONE per disjoint group: a multi-outline ZONE did not connect its narrow groups
                z = P.ZONE(self.b)
                z.SetZoneName(f"T022_{polys[0][0]}_{i}")
                z.SetNet(self.net(net))
                z.SetLayer(LAY[lay])
                z.SetAssignedPriority(prio)
                z.SetMinThickness(P.FromMM(0.25))
                z.SetLocalClearance(P.FromMM(0.3))
                z.SetThermalReliefGap(P.FromMM(0.3))
                z.SetThermalReliefSpokeWidth(P.FromMM(0.5))
                z.SetPadConnection(P.ZONE_CONNECTION_FULL)
                z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_NEVER)   # narrow taps: real orphans show as isolated_copper in DRC
                ol = z.Outline()
                idx = ol.NewOutline()
                c = s.COutline(i)
                for j in range(c.PointCount()):
                    ol.Append(c.CPoint(j).x, c.CPoint(j).y, idx)
                for h in range(s.HoleCount(i)):
                    hole = ol.NewHole(idx)
                    c = s.CHole(i, h)
                    for j in range(c.PointCount()):
                        ol.Append(c.CPoint(j).x, c.CPoint(j).y, idx, hole)
                self.b.Add(z)

    def tap(self, name, net, lay, pts, w=TAP):
        """Zone tap. Both ends run 0.4 mm past their anchor so the via/pad centre sits inside the fill, not on its edge."""
        def ext(a, b):
            ln = math.dist(a, b)
            return (a[0] + (a[0] - b[0]) / ln * 0.4, a[1] + (a[1] - b[1]) / ln * 0.4)
        q = [ext(pts[0], pts[1])] + list(pts[1:-1]) + [ext(pts[-1], pts[-2])]
        self.zone(name, net, lay, ribbon(q, w), prio=6, tag="tap")

    def via_on(self, ref, num, net, offs=((0, 0),), tag=""):
        cx, cy, _, _ = self.pad(ref, num)
        for dx, dy in offs:
            self.via(net, cx + dx, cy + dy, tag or f"{ref}.{num}")

    def reoutline(self, name, pts):
        z = next(x for x in self.b.Zones() if x.GetZoneName() == name)
        ol = z.Outline()
        ol.RemoveAllContours()
        ol.NewOutline()
        for x, y in pts:
            q = kp(x, y)
            ol.Append(q.x, q.y)


# R-018: TP_SW next to its SW node; U4 +1.15 mm east so CEFIN2 sits at the U4 IN/GND pins exactly like CEFIN1 at U3.
# R-020 Tur 2: RS1 at 180 deg gives RS1.2 (VOUT) west and RS1.1 (ISNS1) east, the same order as U11 IN-/IN+ seen from RS1, so both Kelvin arms run parallel on F.Cu.
MOVES = [("TP_SW1", 45.4, 71.6, None), ("TP_SW2", 38.1, 12.4, None), ("U4", 108.385, 40.925, None), ("CEFIN2", 104.99, 41.2, 270), ("RS1", 35.0, 67.6, 180)]


# reference text only, so the moved parts leave no silkscreen warning: (ref, x, y, angle)
REFDES = [("TP_SW1", 45.4, 68.4, 90), ("CIN1", 52.2, 68.9, 90), ("TP_SW2", 40.2, 14.6, 0), ("CIN5", 31.3, 15.1, 90), ("CEFIN2", 104.99, 37.7, 90)]


def placement(B):
    for ref, x, y, rot in MOVES:
        if rot is not None:
            B.fp[ref].SetOrientationDegrees(rot)
        B.fp[ref].SetPosition(kp(x, y))
    for ref, x, y, ang in REFDES:
        t = B.fp[ref].Reference()
        t.SetPosition(kp(x, y))
        t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))


def rotate_q2(B):
    f = B.fp["Q2"]
    if abs(f.GetOrientationDegrees()) > 1e-6:
        raise SystemExit("Q2 is not at 0 deg: start from the T-021 board (see the module docstring).")
    cx, cy = d6(f.GetPosition())
    boxes = [p.GetBoundingBox() for p in f.Pads() if p.GetNumber() in ("1", "2", "3", "5")]
    a = math.radians(Q2_ROT)
    n = 0
    for t in B.b.GetTracks():
        if t.Type() == P.PCB_VIA_T and any(x.Contains(t.GetPosition()) for x in boxes):
            x, y = d6(t.GetPosition())
            dx, dy = x - cx, y - cy
            t.SetPosition(kp(cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
            n += 1
    f.SetOrientationDegrees(Q2_ROT)
    return n


COL3 = ((0, -0.9), (0, 0), (0, 0.9))
ROW3 = ((-0.9, 0), (0, 0), (0.9, 0))
QUAD = ((-0.7, -0.8), (0.7, -0.8), (-0.7, 0.8), (0.7, 0.8))
COUT_COLS_P1 = (25.595, 33.685, 41.775, 49.865, 57.955, 66.045, 74.135, 82.225)
MAIN_BUS_P1 = (57.955, 66.045, 74.135, 82.225)


def isolator(B):
    """Q2 at 90 deg, local L3 outlines, gate, and the source/drain via fields (D-011)."""
    moved = rotate_q2(B)
    B.reoutline("L3_VSAFE", [(90.6, 49.3), (97.6, 49.3), (97.6, 3.5), (W - E, 3.5), (W - E, 77.0), (86.2, 77.0), (86.2, 57.8), (97.6, 57.8), (97.6, 52.1), (90.6, 52.1)])
    B.track("/ISO_GATE", "F", GATE_W, [(94.2, 47.49), (94.8, 47.49), (95.9, 48.65), (95.9, 51.453)], "Q2 gate (HANDOFF <=10 mm)")
    cx, cy = 93.995, 54.53
    for i, j in ((-.6, -.6), (.6, -.6), (-.6, .6), (.6, .6), (-1.8, -.6), (1.8, -.6), (-1.8, .6), (1.8, .6)):
        B.via("/VOUT", cx + i, cy + j, "Q2.5 drain field")
    for x in (91.8, 92.55, 93.3, 94.05, 94.8):
        for y in (49.95, 50.7):
            B.via("/VSAFE", x, y, "Q2 source field")
    for y in (49.95, 50.7):
        B.via("/VSAFE", 91.05, y, "Q2 source field")
    B.zone("F_VSAFE_Q2", "/VSAFE", "F", [(90.75, 49.6), (93.4, 49.6), (93.4, 48.6), (94.2, 48.6), (94.2, 49.6), (95.1, 49.6), (95.1, 52.0), (90.75, 52.0)], tag="Q2 source pads -> via field")
    B.track("/VSAFE", "F", 0.25, [(93.733, 49.3), (93.733, 48.79)], "U6.8 sense")
    return moved


def vout(B):
    B.track("/VOUT", "B", 7.0, [(93.995, 55.5), (84.5, 55.5), (84.5, 44.2), (57.955, 44.2)], "Q2 drain -> bank centre (D-011)")
    # 32 COUT pin 1 -> L3; pads under the main bus get two vias so the bus has >= 15 vias into L3
    for ref in range(1, 33):
        cx, cy, _, _ = B.pad(f"COUT{ref}", 1)
        if round(cx, 3) in MAIN_BUS_P1 and abs(cy - 44.195) < 4:
            for y in ((46.2, 47.4) if cy > 44.2 else (41.0, 42.2)):
                B.via("/VOUT", cx, y, f"COUT{ref}.1 bus")
        else:
            B.via("/VOUT", cx, cy, f"COUT{ref}.1")
    # 32 COUT pin 2 -> L2; the via stays outside the VOUT bus copper
    for ref in range(1, 33):
        cx, cy, _, _ = B.pad(f"COUT{ref}", 2)
        rx, ry = round(cx, 3), cy
        if abs(rx - 87.975) < .01 and abs(ry - 53.855) < .01:
            B.via("/GND", 88.5, 51.1, f"COUT{ref}.2")
            B.track("/GND", "F", 0.3, [(88.5, 51.1), (88.2, 51.9)], "COUT16 GND stub")
        elif abs(rx - 87.975) < .01 and abs(ry - 44.195) < 4:
            B.via("/GND", 88.5, ry, f"COUT{ref}.2")
        elif rx in (55.615, 63.705, 71.795, 79.885) and abs(ry - 44.195) < 4:
            B.via("/GND", rx, 48.6 if ry > 44.2 else 39.9, f"COUT{ref}.2")
        else:
            B.via("/GND", rx, ry, f"COUT{ref}.2")
    # Phase outputs: RS.2 -> F.Cu bus -> via field -> B.Cu bus -> COUT pin 1 + L3
    B.zone("F_VOUT_RS1", "/VOUT", "F", [(29.3, 68.9), (34.8, 68.9), (34.8, 72.9), (29.3, 72.9)], tag="RS1.2 output, leaves the pad north; its south edge stays free for the Kelvin arm")
    for x in (29.8, 30.6, 31.4, 32.2):
        for y in (70.0, 70.8, 71.6, 72.4):
            B.via("/VOUT", x, y, "RS1 output field")
    B.track("/VOUT", "B", 5.5, [(32.2, 71.0), (27.5, 71.0), (27.5, 60.0), (34.9, 57.0), (34.9, 47.4)], "RS1 output -> bank, clear of the RS1.2 sense via")
    B.zone("F_VOUT_RS2", "/VOUT", "F", [(48.9, 17.4), (50.1, 17.4), (50.1, 14.4), (55.9, 14.4), (55.9, 19.9), (48.9, 19.9)], tag="RS2.2 output, 5.5 mm tall; the pad south part stays free for the sense via (R-021)")
    for x in (51.8, 52.6, 53.4, 54.2):
        for y in (15.4, 16.2, 17.0, 17.8):
            B.via("/VOUT", x, y, "RS2 output field")
    B.track("/VOUT", "B", 5.5, [(53.0, 16.6), (53.0, 28.0), (51.0, 31.0), (51.0, 41.0)], "RS2 output -> bank")
    for y in (47.2, 48.8, 50.4, 52.0, 53.6, 55.2, 56.2):
        B.via("/VOUT", 36.5, y, "RS1 bank transfer")
    for y in (31.5, 33.1, 34.7, 36.3, 37.9, 39.5, 40.9):
        B.via("/VOUT", 52.6, y, "RS2 bank transfer")
    for ref, x, ys in (("COUT10", 33.685, (52.05, 53.25, 54.45, 55.65)), ("COUT18", 33.685, (45.6, 46.8, 48.0, 49.2)),
                       ("COUT5", 49.865, (32.7, 33.9, 35.1, 36.3)), ("COUT27", 49.865, (39.15, 40.35, 41.55, 42.75))):
        for y in ys:
            B.via("/VOUT", x, y, f"{ref}.1 phase")
    B.track("/VOUT", "B", 5.5, [(75.2, 34.535), (75.2, 20.0), (70.975, 8.0), (70.975, 4.545)], "J_OVP_INJ_BUS")
    # tiny decoupling / sense loads directly on L3 /VOUT (no track on the BUS class)
    for ref, num in (("C_ISO_VCAP", 2), ("C_ISO_VS", 1), ("RRAWBL", 1)):
        B.via_on(ref, num, "/VOUT", tag=f"{ref}.{num} tap")
    B.track("/VOUT", "F", 0.25, [(93.4, 46.7), (93.4, 45.75)], "U6.5 neck to via")
    B.via("/VOUT", 93.4, 45.75, "U6.5 tap")
    B.via("/VOUT", 77.0, 20.0, "TP_VOUT tap anchor")
    B.tap("TAP_TP_VOUT", "/VOUT", "B", [(77.0, 20.0), (88.871, 21.0), (88.871, 24.052)])
    B.via_on("TP_VOUT", 1, "/VOUT", tag="TP_VOUT")
    B.via("/VOUT", 89.0, 58.3, "R_OV tap anchor")
    B.tap("TAP_R_OV", "/VOUT", "B", [(89.0, 58.3), (88.587, 67.945), (98.5, 75.685)])
    B.via_on("R_OV2T", 1, "/VOUT", tag="R_OV2T.1 Kelvin")
    B.via_on("R_OVT", 1, "/VOUT", tag="R_OVT.1 Kelvin")


def vsafe(B):
    B.track("/VSAFE", "B", 5.5, [(92.0, 49.0), (98.5, 49.0), (98.5, 43.75)], "Q2 source -> eFuse")
    B.zone("B_VSAFE_EFUSE", "/VSAFE", "B", [(95.75, 36.5), (110.6, 36.5), (110.6, 43.25), (95.75, 43.25)], tag="under U3/U4; GND vias punch through")
    B.zone("F_VSAFE_U3", "/VSAFE", "F", [(97.7, 41.06), (100.6, 41.06), (100.6, 42.42), (97.7, 42.42)], tag="CEFIN1 + IN 1-3 + EP")
    B.track("/VSAFE", "F", 0.25, [(106.472, 41.175), (106.472, 42.175)], "U4 IN 1-3")
    B.track("/VSAFE", "F", 0.25, [(106.472, 41.675), (107.15, 41.675)], "U4 IN -> EP")
    B.zone("F_VSAFE_U4", "/VSAFE", "F", [(104.6, 41.06), (106.8, 41.06), (106.8, 42.42), (104.6, 42.42)], tag="CEFIN2 + IN 1-3")
    B.track("/VSAFE", "F", 0.25, [(103.225, 41.12), (102.8, 41.12)], "U3.16 -> EP (anchor kept >= 0.6 mm from U3.17 O1 copper)")
    B.track("/VSAFE", "F", 0.25, [(110.015, 41.12), (109.6, 41.12)], "U4.16 -> EP (anchor kept >= 0.6 mm from U4.17 S2E copper)")
    EP = tuple((x, y) for x in (-1.0, 0.0, 1.0) for y in (-0.35, 0.35))
    B.via_on("U3", 25, "/VSAFE", EP)
    B.via_on("U4", 25, "/VSAFE", EP)
    B.via_on("CEFIN1", 1, "/VSAFE")
    B.via_on("CEFIN2", 1, "/VSAFE")
    B.via("/VSAFE", 98.95, 41.75, "U3 IN field")
    B.via_on("D_REV1", 1, "/VSAFE", QUAD)
    B.via_on("D_REV2", 1, "/VSAFE", QUAD)
    B.via_on("REN1", 1, "/VSAFE", tag="REN1 tap")
    B.via_on("R_BLS", 1, "/VSAFE", tag="R_BLS tap")
    B.via_on("R_GS", 2, "/VSAFE", tag="R_GS.2 tap")
    B.via("/VSAFE", 96.0, 38.3, "R_GS tap anchor")
    B.tap("TAP_R_GS", "/VSAFE", "B", [(96.0, 38.3), (92.85, 37.3), (92.85, 36.645)])
    B.via_on("TP_VSAFE", 1, "/VSAFE", tag="TP_VSAFE")
    B.tap("TAP_TP_VSAFE", "/VSAFE", "In2", [(98.5, 25.5), (82.901, 25.5), (82.901, 24.052)])


def o1(B):
    B.zone("F_O1_U3", "/O1_11V", "F", [(100.1, 42.62), (103.1, 42.62), (103.1, 41.6), (104.2, 41.6), (104.2, 43.45), (105.55, 43.45), (105.55, 48.8), (102.1, 48.8), (102.1, 45.4), (100.1, 45.4)], tag="U3 OUT pins -> via field")
    for x in (102.6, 103.4, 104.2, 105.0):
        for y in (44.3, 45.1, 45.9, 46.7, 47.5, 48.3):
            B.via("/O1_11V", x, y, "U3 OUT field")
    B.track("/O1_11V", "B", 5.3, [(104.5, 51.85), (116.255, 51.85), (116.255, 49.25)], "U3 OUT -> J2.1 (north of D3 GND vias)")
    B.track("/O1_11V", "B", 5.3, [(104.5, 46.1), (104.5, 55.0), (101.0, 55.0)], "U3 OUT -> D2 TVS")
    B.track("/O1_11V", "F", 0.25, [(103.77, 41.775), (103.77, 42.175)], "U3.17-18")
    B.via_on("D2", 1, "/O1_11V", QUAD)
    B.via("/O1_11V", 112.0, 49.6, "O1 south tap anchor")
    B.tap("TAP_O1_DREV", "/O1_11V", "B", [(112.0, 49.6), (112.0, 27.5), (108.5, 26.6), (108.045, 24.905)], w=BRANCH)
    B.via_on("D_REV1", 2, "/O1_11V", QUAD)
    B.tap("TAP_O1_CEFOUT", "/O1_11V", "B", [(106.645, 23.305), (107.0, 20.0), (100.1, 19.5), (100.101, 17.665)], w=BRANCH)
    B.via_on("CEFOUT1", 1, "/O1_11V", tag="CEFOUT1")
    B.tap("TAP_O1_RPG", "/O1_11V", "B", [(100.101, 17.665), (101.35, 3.0), (101.35, 1.725)])
    B.via_on("RPG1", 2, "/O1_11V", tag="RPG1")
    B.via("/O1_11V", 96.5, 19.3, "TP_O1 layer change")
    B.tap("TAP_O1_TP_A", "/O1_11V", "B", [(100.1, 19.3), (96.5, 19.3)])
    B.tap("TAP_O1_TP_B", "/O1_11V", "In2", [(96.5, 19.3), (59.839, 19.107)])
    B.via_on("TP_O1", 1, "/O1_11V", tag="TP_O1")


def s2e(B):
    B.zone("F_S2E_U4", "/S2E_11V", "F", [(107.0, 42.6), (109.9, 42.6), (109.9, 41.6), (111.15, 41.6), (111.15, 45.4), (107.0, 45.4)], tag="U4 OUT pins")
    B.track("/S2E_11V", "F", 3.3, [(110.8, 44.3), (113.05, 44.3), (113.05, 37.5), (110.035, 34.5), (110.035, 32.6)], "U4 OUT -> J3.1")
    B.zone("F_S2E_D3", "/S2E_11V", "F", [(100.2, 48.6), (101.4, 48.6), (101.4, 49.3), (108.95, 49.3), (108.95, 43.0), (113.0, 43.0), (113.0, 52.65), (99.5, 52.65), (99.5, 49.3), (100.2, 49.3)], tag="U4 OUT -> D3 TVS, D3-D2 channel")
    B.track("/S2E_11V", "F", 0.25, [(110.56, 41.775), (110.56, 42.175)], "U4.17-18")
    B.tap("TAP_S2E_DREV", "/S2E_11V", "F", [(110.035, 31.5), (110.035, 27.2), (117.685, 27.2), (117.685, 25.0)], w=BRANCH)
    B.tap("TAP_S2E_CEFOUT", "/S2E_11V", "F", [(110.035, 27.2), (104.4, 27.2), (104.4, 19.2), (105.703, 18.6), (105.703, 17.665)], w=BRANCH)
    B.tap("TAP_S2E_RPG", "/S2E_11V", "F", [(105.703, 17.665), (105.703, 16.0), (106.9, 15.0), (106.9, 3.0), (105.6, 2.2), (104.85, 1.725)], w=0.5)
    B.via("/S2E_11V", 104.0, 26.2, "TP_S2E layer change")
    B.tap("TAP_S2E_TP", "/S2E_11V", "B", [(104.0, 26.2), (94.105, 26.2), (94.105, 24.052)])
    B.via_on("TP_S2E", 1, "/S2E_11V", tag="TP_S2E")


def efuse_gnd(B):
    for u, ox in (("U3", 0.0), ("U4", 6.79)):
        B.via_on(u, 26, "/GND", ((-1.0, 0.0), (0.0, 0.0), (1.0, 0.0)))
        B.track("/GND", "F", 0.25, [(99.683 + ox, 40.675), (99.683 + ox, 40.175), (100.4 + ox, 40.175)], f"{u} GND 4/5 -> EP")
        B.track("/GND", "F", 0.25, [(103.507 + ox, 40.175), (102.8 + ox, 40.175)], f"{u} GND 14 -> EP")
        for pin in (10, 11, 12):
            x, _, _, _ = B.pad(u, pin)
            B.track("/GND", "F", 0.25, [(x, 39.013), (x, 39.7)], f"{u} GND {pin} -> EP")
    B.track("/GND", "F", 0.3, [(98.2, 40.3), (99.683, 40.3)], "CEFIN1 GND")
    B.track("/GND", "F", 0.3, [(104.99, 40.3), (106.473, 40.3)], "CEFIN2 GND")
    B.via_on("CEFIN1", 2, "/GND")
    B.via_on("CEFIN2", 2, "/GND")
    B.via_on("D1", 2, "/GND", ((-1.0, -0.8), (0.0, -0.8), (-1.0, 0.8), (0.0, 0.8)), tag="D1 TVS return")
    B.via_on("D2", 2, "/GND", ((0.355, 0.4), (1.005, 0.4), (0.355, 1.3), (1.005, 1.3)), tag="D2 TVS return (clear of O1 B.Cu)")
    B.via_on("D3", 2, "/GND", ((0.355, -0.8), (1.005, -0.8), (0.355, 0.8), (1.005, 0.8)), tag="D3 TVS return (clear of O1 B.Cu)")
    B.via_on("CEFOUT1", 2, "/GND")
    B.via_on("CEFOUT2", 2, "/GND")


def buck(B, u, mirror):
    t = mirror_u2 if mirror else (lambda x, y: (x, y))
    names = ("U1", "CIN1", "CIN2", "CIN3", "CIN4", "SW_PH1") if not mirror else ("U2", "CIN5", "CIN6", "CIN7", "CIN8", "SW_PH2")
    _, c1, c2, c3, c4, sw = names
    tag = u
    B.zone(f"F_VIN_{tag}", "/VIN", "F", [t(*p) for p in ((49.75, 65.9), (51.2, 65.9), (51.2, 72.7), (60.0, 72.7), (60.0, 76.5), (52.9, 76.5), (52.9, 75.6), (52.35, 75.6), (52.35, 75.42), (49.75, 75.42))], tag="hot loop VIN")
    B.zone(f"F_PGND_{tag}", "/GND", "F", [t(*p) for p in ((46.75, 65.9), (48.75, 65.9), (48.75, 73.75), (46.75, 73.75))], prio=5, tag="hot loop PGND")
    B.zone(f"F_{sw}", f"/{sw}", "F", [t(*p) for p in ((43.0, 73.7), (46.6, 73.7), (46.6, 75.0), (47.0, 75.0), (47.0, 76.45), (43.0, 76.45))], tag="SW node")
    B.zone(f"F_{sw}_TP", f"/{sw}", "F", [t(*p) for p in ((44.9, 71.1), (45.9, 71.1), (45.9, 73.75), (44.9, 73.75))], tag="short lobe to the moved TP_SW pad")
    B.track("/VIN", "F", 0.25, [t(51.9, 74.25), t(51.9, 75.25)], f"{tag} VIN pins 1-3")
    B.track("/VIN", "F", 0.25, [t(50.5, 73.3), t(50.5, 74.79)], f"{tag} VIN pad 29")
    for ref, off in ((c1, COL3), (c2, COL3), (c3, ROW3), (c4, ROW3)):
        B.via_on(ref, 1, "/VIN", off, tag=f"{ref} VIN -> L3")
        B.via_on(ref, 2, "/GND", off, tag=f"{ref} PGND -> L2")


def input_side(B):
    # /ANODE: J1.1 (TH) on B.Cu to a via field beside Q1 sources, then 3.3 mm F.Cu onto pins 1-3
    B.track("/ANODE", "B", 3.3, [(9.965, 42.5), (9.965, 47.0), (12.05, 49.5), (12.05, 51.6)], "J1.1 -> Q1 field")
    for x in (11.3, 12.05, 12.8):
        for y in (50.4, 51.2, 52.0, 52.8):
            B.via("/ANODE", x, y, "Q1 source field")
    B.track("/ANODE", "F", 3.3, [(12.6, 51.6), (13.7, 51.6)], "Q1 pins 1-3")
    B.track("/ANODE", "F", 0.5, [(13.7, 51.6), (14.1, 52.905)], "Q1.1")
    B.track("/ANODE", "F", 0.5, [(13.7, 51.6), (14.1, 50.365)], "Q1.3")
    B.via_on("D1", 1, "/VIN", QUAD, tag="D1 TVS")
    B.via_on("TP_VIN", 1, "/VIN", tag="TP_VIN")
    B.via("/VIN", 20.9, 41.55, "U5.4 tap")
    for ref in ("CBIN1", "CBIN2"):
        B.via_on(ref, 1, "/VIN", tag=f"{ref} tap")
    B.via_on("TP_ANODE", 1, "/ANODE", tag="TP_ANODE")
    B.tap("TAP_TP_ANODE", "/ANODE", "B", [(9.965, 41.3), (12.725, 35.5), (12.725, 34.552)])
    B.via("/ANODE", 18.1, 41.55, "U5.3 tap")
    B.via("/ANODE", 20.9, 43.45, "U5.6 tap")
    B.tap("TAP_U5", "/ANODE", "B", [(11.3, 40.0), (18.1, 40.0), (18.1, 41.55)])
    B.tap("TAP_U5B", "/ANODE", "B", [(18.1, 40.0), (22.0, 40.0), (22.0, 43.45), (20.9, 43.45)])
    B.tap("TAP_U5A", "/ANODE", "B", [(9.965, 41.3), (11.3, 40.0)])
    B.via_on("CVCAP", 2, "/ANODE", tag="CVCAP.2")
    B.via_on("CIN_U5", 1, "/ANODE", tag="CIN_U5.1")
    B.tap("TAP_ANODE_N", "/ANODE", "B", [(12.05, 52.8), (12.05, 68.0), (16.241, 69.825)])
    B.tap("TAP_ANODE_NW", "/ANODE", "B", [(12.05, 68.0), (1.933, 68.0), (1.933, 69.825)])
    # /VIN milliamp loads east of the L3 /VIN pour
    B.tap("TAP_VIN_E", "/VIN", "B", [(59.0, 74.775), (67.7, 70.0), (67.7, 68.425)])
    B.via_on("RUV1", 1, "/VIN", tag="RUV1")
    B.tap("TAP_VIN_E2", "/VIN", "B", [(67.7, 70.0), (77.469, 72.0), (77.469, 75.665)])
    B.via_on("C_LDO_IN", 1, "/VIN", tag="C_LDO_IN")
    B.tap("TAP_VIN_E3", "/VIN", "B", [(77.469, 72.0), (90.35, 77.0), (90.35, 82.3)])
    for pin, y, vy in ((5, 79.9, 79.75), (8, 82.1, 82.3)):
        B.track("/VIN", "F", 0.25, [(89.7, y), (90.35, vy)], f"U10.{pin} neck")
        B.via("/VIN", 90.35, vy, f"U10.{pin}")


def controller_sense(B):
    """LM70880 ISNS/VOUT pins to the inner edge of RS1/RS2: separate pair, zero power current, HV 0.6 mm kept between the two taps."""
    B.track("/ISNS1", "F", 0.25, [(50.0, 79.65), (50.1, 80.95)], "U1.11 neck")
    B.via("/ISNS1", 50.1, 80.95, "U1.11")
    B.tap("TAP_ISNS1", "/ISNS1", "B", [(50.1, 80.95), (50.1, 79.1), (37.7, 79.1), (37.7, 66.4)])
    B.via("/ISNS1", 37.7, 66.4, "RS1.1 inner edge, south of the L1 power entry (R-021)")
    B.track("/VOUT", "F", 0.25, [(49.0, 79.65), (49.0, 80.4)], "U1.12 neck")
    B.via("/VOUT", 49.0, 80.4, "U1.12")
    B.tap("TAP_U1_VOUT", "/VOUT", "B", [(49.0, 80.4), (49.0, 82.6), (35.7, 82.6), (35.7, 67.0), (32.3, 66.4)])
    B.via("/VOUT", 32.3, 66.4, "RS1.2 inner edge")
    B.track("/ISNS2", "F", 0.25, [(33.5, 4.35), (33.4, 3.6)], "U2.11 neck")
    B.via("/ISNS2", 33.4, 3.6, "U2.11")
    B.tap("TAP_ISNS2", "/ISNS2", "B", [(33.4, 3.6), (33.4, 4.6), (43.9, 4.6), (43.9, 17.7)])
    B.via("/ISNS2", 43.9, 17.7, "RS2.1 inner edge, north of the L2 power entry (R-021)")
    B.track("/VOUT", "F", 0.25, [(34.5, 4.35), (34.5, 2.9)], "U2.12 neck")
    B.via("/VOUT", 34.5, 2.9, "U2.12")
    B.tap("TAP_U2_VOUT", "/VOUT", "B", [(34.5, 2.9), (34.5, 1.4), (49.1, 1.4), (49.1, 15.6)])
    B.via("/VOUT", 49.1, 15.6, "RS2.2 inner edge")


def phase(B):
    B.track("/ISNS1", "F", 2.6, [(34.4, 75.6), (37.96, 71.2), (37.96, 69.0)], "L1.2 -> RS1.1")
    B.track("/ISNS2", "F", 2.6, [(50.0, 10.8), (47.0, 13.0), (44.2, 14.6), (43.7, 15.4)], "L2.2 -> RS2.1")


def main():
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    B = Board(PCB)
    placement(B)
    moved = isolator(B)
    vout(B)
    vsafe(B)
    o1(B)
    s2e(B)
    efuse_gnd(B)
    buck(B, "U1", False)
    buck(B, "U2", True)
    input_side(B)
    phase(B)
    controller_sense(B)
    B.build_zones()
    P.ZONE_FILLER(B.b).Fill(B.b.Zones())
    B.b.BuildConnectivity()
    P.SaveBoard(str(PCB), B.b, True)
    OUT.mkdir(parents=True, exist_ok=True)
    B.log["q2"] = {"rotation_deg": Q2_ROT, "t021_vias_moved": moved}
    with (OUT / "route-items.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(B.log, f, indent=0, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"tracks": len(B.log["tracks"]), "vias": len(B.log["vias"]), "zones": len(B.log["zones"]), "moved": moved}))
    return 0


# --------------------------------------------------------------------------- audit (--audit, on the routed board)
AUDIT_NETS = ["/ANODE", "/VIN", "/VOUT", "/VSAFE", "/O1_11V", "/S2E_11V", "/SW_PH1", "/SW_PH2", "/ISNS1", "/ISNS2", "/ISO_GATE"]
LATER = {"/ISNS1": "T-023: U11.8 INA296 Kelvin and TP_ISNS1P", "/ISNS2": "T-023: U12.8 INA296 Kelvin and TP_ISNS2P", "/ISO_GATE": "T-023 R_GS and TP_ISO_GATE (Q2-U6 gate itself is routed)",
         "/VOUT": "T-023: U11.1/U12.1 INA296 Kelvin, TP_ISNS1N/2N, R_INJ, TP_FB_INJ_A"}
VIA_TARGETS = {"Q2 drain (/VOUT)": (("Q2.5 drain field",), 15, 9), "Q2 source (/VSAFE)": (("Q2 source field",), 15, 3),
               "U3 OUT -> B.Cu (/O1_11V)": (("U3 OUT field",), 19, 0), "J1/Q1 (/ANODE)": (("Q1 source field",), 9, 0),
               "RS1 output (/VOUT)": (("RS1 output field",), 15, 0), "RS2 output (/VOUT)": (("RS2 output field",), 15, 0)}
# Copper cross-sections through pours: (what, net, layer, centre point, axis of the cut, class minimum from routing-g2)
SECTIONS = [("/S2E_11V U4 -> D3 channel", "/S2E_11V", "F", (104.0, 51.0), "y", 2.97), ("/S2E_11V east drop", "/S2E_11V", "F", (110.5, 46.5), "x", 2.97),
            ("/O1_11V pins -> field", "/O1_11V", "F", (103.0, 44.0), "x", 4.76), ("/VIN CIN3/4 -> U1", "/VIN", "F", (56.0, 74.5), "y", 2.94),
            ("/VIN CIN7/8 -> U2", "/VIN", "F", (27.5, 9.5), "y", 2.94), ("/SW_PH1 U1 -> L1", "/SW_PH1", "F", (44.5, 75.0), "y", 2.35),
            ("/SW_PH2 U2 -> L2", "/SW_PH2", "F", (39.0, 8.9), "y", 2.35), ("/VOUT RS2.2 -> field", "/VOUT", "F", (50.5, 17.1), "y", 4.92), ("/VOUT RS1.2 -> field", "/VOUT", "F", (32.0, 69.4), "x", 4.92),
            ("/VSAFE under U3 -> U4", "/VSAFE", "B", (103.4, 41.5), "y", 4.92),
            ("/VSAFE around CEFIN2 GND via (sum of both sides)", "/VSAFE", "B", [(104.99, 38.0), (104.99, 42.2)], "y", 4.92),
            ("/O1_11V D_REV1 branch", "/O1_11V", "B", (112.0, 40.0), "x", 1.0), ("/S2E_11V D_REV2 branch", "/S2E_11V", "F", (114.0, 27.2), "y", 1.0)]


def run_drc(pcb, out, parity):
    import subprocess
    cli = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
    cmd = [cli, "pcb", "drc", "--format", "json", "--severity-all", "--refill-zones", "-o", str(out), str(pcb)]
    if parity:
        cmd.insert(3, "--schematic-parity")
    subprocess.run(cmd, check=True, capture_output=True)
    return json.loads(Path(out).read_text(encoding="utf-8"))


def shoelace(pts):
    return abs(sum(a[0] * c[1] - c[0] * a[1] for a, c in zip(pts, pts[1:] + pts[:1]))) / 2


def loops(b):
    """Geometric approximation (R-018 allows it in T-022): F.Cu conductor corners of each input-capacitor loop, plan view. Not a current solution."""
    fp = {f.GetReference(): f for f in b.GetFootprints()}

    def pad(ref, num):
        ps = [p for p in fp[ref].Pads() if p.GetNumber() == str(num)]
        q = max(ps, key=lambda x: x.GetBoundingBox().GetWidth() * x.GetBoundingBox().GetHeight())
        return d6(q.GetBoundingBox().GetCenter())

    def mid(*ps):
        return (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    out = {}
    for u, caps, vin_near, vin_far, gnd in (("U1", ("CIN1", "CIN2", "CIN3", "CIN4"), (27, 28), (1, 2, 3), (23, 24, 25, 26)), ("U2", ("CIN5", "CIN6", "CIN7", "CIN8"), (27, 28), (1, 2, 3), (23, 24, 25, 26))):
        pv_n, pv_f, pg = mid(*[pad(u, n) for n in vin_near]), mid(*[pad(u, n) for n in vin_far]), mid(*[pad(u, n) for n in gnd])
        for i, c in enumerate(caps):
            v = pv_n if i < 2 else pv_f
            cv, cg = pad(c, 1), pad(c, 2)
            out[f"{u}/{c}"] = {"area_mm2": round(shoelace([v, cv, cg, pg]), 2), "vin_pin_to_cap_mm": round(math.dist(v, cv), 2), "cap_gnd_to_pgnd_pin_mm": round(math.dist(cg, pg), 2),
                               "return_layer": "F.Cu PGND pour" if i < 2 else "L2 GND via (F.Cu cap pad to L2)"}
    for u, c, inn, gn in (("U3", "CEFIN1", (1, 2, 3), (4, 5)), ("U4", "CEFIN2", (1, 2, 3), (4, 5))):
        v, g = mid(*[pad(u, n) for n in inn]), mid(*[pad(u, n) for n in gn])
        cv, cg = pad(c, 1), pad(c, 2)
        out[f"{u}/{c}"] = {"area_mm2": round(shoelace([v, cv, cg, g]), 2), "vin_pin_to_cap_mm": round(math.dist(v, cv), 2), "cap_gnd_to_pgnd_pin_mm": round(math.dist(cg, g), 2),
                           "return_layer": "F.Cu track to GND pins 4/5", "in_path": "F.Cu pour, no via"}
    return {"basis": "geometrik yaklaşık: pad merkezleri arası düzlem poligonu, shoelace; akım çözümü değil", "loops": out}


def branch_check():
    """IPC-2221 fit used by routing-g2 (k 0.048, b 0.44, c 0.725, 31.5 um outer), for the 3 A D_REV rating. Screening, not IPC-2152."""
    rows = {}
    k, b, c, t_mil = 0.048, 0.44, 0.725, 31.5 / 25.4
    for name, amps, length in (("D_REV/CEFOUT branch, D_REV 3 A rating", 3.0, 40.0),):
        area = (amps / (k * 20.0 ** b)) ** (1 / c)
        need_mm = area / t_mil * 0.0254
        ohm = 1.72e-5 * length / (BRANCH * 0.0315)
        rows[name] = {"current_A": amps, "ipc_width_for_20C_mm": round(need_mm, 2), "branch_width_mm": BRANCH, "pass": BRANCH >= need_mm, "length_used_mm": length, "resistance_mohm": round(ohm * 1000, 1), "drop_mV": round(ohm * amps * 1000, 1),
                     "basis": "HESAP; CEFOUT transient current not simulated (doğrulanamadı)"}
    return rows


def neck_clearances(b):
    """Real minimum edge gaps for the tight neck tracks at the eFuse IN/OUT pins (track centre-line distance minus half widths; pad edges from pad bounding boxes)."""
    def seg_dist(a, c, q):
        vx, vy = c[0] - a[0], c[1] - a[1]
        ln2 = vx * vx + vy * vy
        t = 0.0 if ln2 == 0 else max(0.0, min(1.0, ((q[0] - a[0]) * vx + (q[1] - a[1]) * vy) / ln2))
        return math.dist((a[0] + t * vx, a[1] + t * vy), q)

    def seg_seg(s1, s2):
        return min(seg_dist(s1[0], s1[1], s2[0]), seg_dist(s1[0], s1[1], s2[1]), seg_dist(s2[0], s2[1], s1[0]), seg_dist(s2[0], s2[1], s1[1]))

    tr = [t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and P.ToMM(t.GetWidth()) < 0.6]

    def seg(t):
        return d6(t.GetStart()), d6(t.GetEnd())
    pairs = {"U3.16 VSAFE neck <-> U3.17 O1 stub": ("/VSAFE", "/O1_11V", 103.5), "U4.16 VSAFE neck <-> U4.17 S2E stub": ("/VSAFE", "/S2E_11V", 110.3)}
    out = {}
    for name, (n1, n2, xc) in pairs.items():
        t1 = [t for t in tr if t.GetNetname() == n1 and abs(seg(t)[0][0] - xc) < 1.2 and abs(seg(t)[0][1] - 41.12) < 0.02]
        t2 = [t for t in tr if t.GetNetname() == n2 and abs(seg(t)[0][0] - xc) < 1.2 and abs(seg(t)[0][1] - 41.775) < 0.02]
        if t1 and t2:
            g = seg_seg(seg(t1[0]), seg(t2[0])) - P.ToMM(t1[0].GetWidth()) / 2 - P.ToMM(t2[0].GetWidth()) / 2
            out[name] = {"edge_gap_mm": round(g, 3), "hv_rule_mm": 0.6, "manufacturer_tolerance": "doğrulanamadı (üretici DFM yok; PCB-HANDOFF §7 min 0.15/0.15 VARSAYIM)"}
    return out


def audit():
    import collections
    import re
    import shutil
    import tempfile
    sys.path.insert(0, str(ROOT / "scripts"))
    import pcb_drc as drc
    import pcb_rules as pr
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    D = run_drc(PCB, OUT / "drc.json", True)
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for fn in ("PDU.kicad_pro", "PDU.kicad_dru"):
            shutil.copy(ROOT / fn, t / fn)
        # Empty board = outline, stackup, holes and rules only (T-013 meaning): footprints and all routed copper removed.
        import kicad_sexpr as ks
        root = ks.parse(drc.strip_footprints(PCB.read_bytes().decode("utf-8")))
        top = ks.top(root)
        for head in ("segment", "arc", "via", "zone"):
            for node in list(top.children(head)):
                ks.remove_node(top, node)
        (t / "PDU.kicad_pcb").write_bytes(ks.dumps(root).encode("utf-8"))
        if "--empty-board" in sys.argv:           # hand a reviewer the exact file that this audit's DRC checks
            shutil.copy(t / "PDU.kicad_pcb", sys.argv[sys.argv.index("--empty-board") + 1])
        E = run_drc(t / "PDU.kicad_pcb", OUT / "drc-empty.json", False)

    def count(d):
        return dict(collections.Counter(f"{v['severity']}:{v['type']}" for v in d["violations"]))

    def errs(d):
        return sum(1 for v in d["violations"] if v["severity"] == "error")

    opens = collections.defaultdict(list)
    for u in D.get("unconnected_items", []):
        m = re.search(r"\[([^\]]+)\]", u["items"][0]["description"])
        if m:
            opens[m.group(1)].append([i["description"] for i in u["items"]])
    tracks = list(b.GetTracks())
    log = json.loads((OUT / "route-items.json").read_text(encoding="utf-8"))
    nets = {}
    for n in AUDIT_NETS:
        tr = [t for t in tracks if t.GetNetname() == n and t.Type() != P.PCB_VIA_T]
        nets[n] = {"tracks": len(tr), "track_layers": sorted({b.GetLayerName(t.GetLayer()) for t in tr}), "track_length_mm": round(sum(P.ToMM(t.GetLength()) for t in tr), 2),
                   "track_widths_mm": sorted({round(P.ToMM(t.GetWidth()), 3) for t in tr}), "vias": sum(1 for t in tracks if t.GetNetname() == n and t.Type() == P.PCB_VIA_T),
                   "zones": sorted(z.GetZoneName() for z in b.Zones() if z.GetNetname() == n),
                   "open_pairs": len(opens.get(n, [])), "open_pairs_detail": opens.get(n, []), "deferred_to": LATER.get(n, "") if opens.get(n) else ""}
    via_tgt = {}
    for k, (tags, need, base) in VIA_TARGETS.items():
        got = sum(1 for v in log["vias"] if v["tag"] in tags) + base
        via_tgt[k] = {"count": got, "routing_g2_target": need, "meets_target": got >= need, "includes_t021_vias": base}
    bus_l3 = sum(1 for v in log["vias"] if v["tag"].endswith(".1 bus"))
    via_tgt["/VOUT bus -> L3 (COUT pin 1 under the bus)"] = {"count": bus_l3, "routing_g2_target": 15, "meets_target": bus_l3 >= 15, "includes_t021_vias": 0}
    gate = next(e for e in log["tracks"] if e["net"] == "/ISO_GATE")
    pts = [(93.733, 47.49)] + [tuple(p) for p in gate["points"]]
    gate_mm = sum(math.dist(a, c) for a, c in zip(pts, pts[1:]))
    widths = {}
    for what, net, lay, c, axis, mn in SECTIONS:
        zs = [z for z in b.Zones() if z.GetNetname() == net and z.IsOnLayer(LAY[lay])]
        trs = [t for t in tracks if t.GetNetname() == net and t.Type() != P.PCB_VIA_T and t.GetLayer() == LAY[lay]]

        def cu(x, y):
            q = kp(x, y)
            return any(z.HitTestFilledArea(LAY[lay], q, 0) for z in zs) or any(t.HitTest(q, 0) for t in trs)

        span = []
        for c0 in (c if isinstance(c, list) else [c]):
            for sign in (-1, 1):
                k, step = 0, 0.02
                while k < 2000:
                    x, y = (c0[0] + sign * k * step, c0[1]) if axis == "x" else (c0[0], c0[1] + sign * k * step)
                    if not cu(x, y):
                        break
                    k += 1
                span.append(k * step)
        w = round(sum(span), 2)
        widths[what] = {"centre": c, "cut_axis": axis, "copper_width_mm": w, "class_min_mm": mn, "meets_min": w >= mn, "basis": "HESAP: copper span through this point, 0.02 mm steps"}
    area = {}
    for name in ("L2_GND", "L4_GND", "L3_VIN", "L3_VOUT", "L3_VSAFE"):
        z = next(x for x in b.Zones() if x.GetZoneName() == name)
        f = z.GetFilledPolysList(z.GetFirstLayer())
        vals = []
        for i in range(f.OutlineCount()):
            a = abs(f.COutline(i).Area())
            for h in range(f.HoleCount(i)):
                a -= abs(f.CHole(i, h).Area())
            vals.append(round(a / (P.FromMM(1.0) ** 2), 2))
        area[name] = {"islands": f.OutlineCount(), "fill_area_mm2": vals}
    neck = drc.neck_audit(PCB.read_text(encoding="utf-8"), pr.routing_rows())
    res = {"kicad": P.GetBuildVersion(),
           "board_drc": {"errors": errs(D), "by_type": count(D), "schematic_parity_issues": len(D.get("schematic_parity", [])), "unconnected_total": len(D.get("unconnected_items", []))},
           "empty_board_drc": {"errors": errs(E), "by_type": count(E)}, "neck_audit_violations": neck, "rules_check": pr.check(), "q2": log["q2"],
           "gate_q2_u6": {"centre_line_mm": round(gate_mm, 3), "limit_mm": 10.0, "width_mm": gate["width_mm"], "layer": gate["layer"], "basis": "from U6.6 pad centre to Q2.4 pad centre"},
           "nets": nets, "via_targets": via_tgt, "zone_widths": widths, "plane_areas": area,
           "loop_geometry": loops(b), "branch_current": branch_check(), "neck_clearance": neck_clearances(b),
           "not_measured": {"VIN_CIN_PGND_current_solved_loop": "doğrulanamadı: D-010 yöntemi akım çözümü ister; loop_geometry yalnız geometrik yaklaşıktır"},
           "assumptions": ["1 oz all layers, via 0.6/0.3 and via-in-pad filled/capped: manufacturer confirmation AÇIK (PCB-HANDOFF §7)"]}
    with (OUT / "power-route-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: res[k] for k in ("board_drc", "empty_board_drc", "gate_q2_u6", "via_targets", "zone_widths")}
                     | {"neck": len(neck), "rules": res["rules_check"], "planes": {k: v["islands"] for k, v in area.items()}, "opens": {k: v["open_pairs"] for k, v in nets.items()}}, ensure_ascii=False, indent=0))
    return 0


if __name__ == "__main__":
    sys.exit(audit() if "--audit" in sys.argv else main())
