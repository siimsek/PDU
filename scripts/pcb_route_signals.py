"""T-023 signal routing (D-012) — KiCad's bundled Python 10.0.7 (D-009).

Step 1 (D-012, read-only for PDU.kicad_pcb):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_route_signals.py --step1
    ...python.exe scripts/pcb_route_signals.py --step2      # writes PDU.kicad_pcb: run on the T-022 board only (it refuses a board that already has T023_ zones)
    ...python.exe scripts/pcb_route_signals.py --audit2     # step 2 evidence: DRC, Kelvin lengths, SW distance, L2

Writes reports/g5/T-023/: step1-baseline.json (refill + DRC + parity), step1-inventory.json (every open pair by net/ref/pin, D-012 classes,
every /GND pad with its L2 state), gnd-via-candidates.json (local F.Cu stub + through via candidates), and proves them on a temporary copy.
Coordinates: D-006 (origin lower-left, y up). Vias 0.6/0.3 mm are VARSAYIM (PCB-HANDOFF §7).
"""
from __future__ import annotations

import collections
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "PDU.kicad_pcb"
OUT = ROOT / "reports" / "g5" / "T-023"
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
OX, OY, H, W = 30.0, 30.0, 85.0, 120.0
VIA_R, DRILL_R = 0.3, 0.15
STUB = 0.25
CLR = 0.2                 # class clearance of /GND against other copper
HOLE_GAP = 0.25           # min_hole_to_hole, min_hole_clearance
EDGE = 0.5
SHARE_MM = 1.7            # GND pads of one footprint closer than this may share one via through a straight F.Cu link
CLASSES = {"Gate": {"/GATE", "/ISO_GATE"}, "FB/COMP": {"/FB", "/FB_INJ", "/FB_TRIM", "/COMP", "/COMP_MID"},
           "OVP/OC mantık": {"/CLR_N", "/ISO_EN", "/ISO_OV", "/OC_REF", "/OC_SENSE1", "/OC_SENSE2", "/OC_TRIP1_N", "/OC_TRIP2_N", "/OVP_BUS_N", "/OVP_Q", "/OVP_REF", "/OVP_SENSE", "/OVP_TRIP_N"},
           "Kelvin": {"/ISNS1", "/ISNS2"}, "GND dönüş": {"/GND"}}
VOUT_KELVIN = ("U11", "U12", "TP_ISNS")
VOUT_FB = ("R_INJ", "TP_FB_INJ")


def d6(v):
    return P.ToMM(v.x) - OX, OY + H - P.ToMM(v.y)


def kp(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY + H - y))


def drc(pcb, out):
    subprocess.run([CLI, "pcb", "drc", "--schematic-parity", "--format", "json", "--severity-all", "--refill-zones", "-o", str(out), str(pcb)], check=True, capture_output=True)
    return json.loads(Path(out).read_text(encoding="utf-8"))


def net_of(text):
    m = re.search(r"\[([^\]]+)\]", text)
    return m.group(1) if m else ""


def classify(net, items):
    if net == "/VOUT":
        refs = " ".join(items)
        if any(k in refs for k in VOUT_KELVIN):
            return "Kelvin"
        if any(k in refs for k in VOUT_FB):
            return "FB/COMP"
    for name, nets in CLASSES.items():
        if net in nets:
            return name
    return "Diğer"


def summary(d):
    pairs = collections.Counter(net_of(u["items"][0]["description"]) for u in d.get("unconnected_items", []))
    return {"errors": sum(1 for v in d["violations"] if v["severity"] == "error"), "by_type": dict(collections.Counter(f"{v['severity']}:{v['type']}" for v in d["violations"])),
            "schematic_parity_issues": len(d.get("schematic_parity", [])), "unconnected_pairs": len(d.get("unconnected_items", [])), "pairs_by_net": dict(sorted(pairs.items()))}


class Geo:
    def __init__(self, b):
        self.b = b
        self.pads, self.segs, self.vias = [], [], []
        for f in b.GetFootprints():
            ref = f.GetReference()
            for p in f.Pads():
                bb = p.GetBoundingBox()
                a, c = d6(P.VECTOR2I(bb.GetLeft(), bb.GetBottom())), d6(P.VECTOR2I(bb.GetRight(), bb.GetTop()))
                th = p.GetAttribute() in (P.PAD_ATTRIB_PTH, P.PAD_ATTRIB_NPTH)
                self.pads.append({"ref": ref, "pin": p.GetNumber(), "net": p.GetNetname(), "rect": (a[0], a[1], c[0], c[1]), "th": th, "front": p.IsOnLayer(P.F_Cu), "pad": p})
        for t in b.GetTracks():
            if t.Type() == P.PCB_VIA_T:
                self.vias.append((d6(t.GetPosition()), t.GetNetname()))
            else:
                self.segs.append((d6(t.GetStart()), d6(t.GetEnd()), P.ToMM(t.GetWidth()) / 2, t.GetNetname(), t.GetLayer()))
        self.keep = [z for z in b.Zones() if z.GetZoneName().startswith(("T022_", "T023_")) and z.GetNetname() != "/GND"]

    @staticmethod
    def rect_dist(r, x, y):
        dx = max(r[0] - x, 0, x - r[2])
        dy = max(r[1] - y, 0, y - r[3])
        return math.hypot(dx, dy)

    @staticmethod
    def seg_dist(a, c, q):
        vx, vy = c[0] - a[0], c[1] - a[1]
        ln2 = vx * vx + vy * vy
        t = 0.0 if ln2 == 0 else max(0.0, min(1.0, ((q[0] - a[0]) * vx + (q[1] - a[1]) * vy) / ln2))
        return math.dist((a[0] + t * vx, a[1] + t * vy), q)

    def zone_hit(self, x, y, r, layers):
        pts = [(x, y)] + [(x + r * math.cos(i * math.pi / 4), y + r * math.sin(i * math.pi / 4)) for i in range(8)]
        for z in self.keep:
            for lay in layers:
                if z.IsOnLayer(lay) and any(z.HitTestFilledArea(lay, kp(*q), 0) for q in pts):
                    return True
        return False

    def via_ok(self, x, y, extra=()):
        if not (VIA_R + EDGE <= x <= W - VIA_R - EDGE and VIA_R + EDGE <= y <= H - VIA_R - EDGE):
            return False
        for p in self.pads:
            d = self.rect_dist(p["rect"], x, y)
            if p["th"] and d < DRILL_R + HOLE_GAP:
                return False
            if p["net"] != "/GND" and d < VIA_R + CLR:
                return False
        for (q, net) in list(self.vias) + [(e, "/GND") for e in extra]:
            d = math.dist(q, (x, y))
            if d < 2 * DRILL_R + HOLE_GAP or (net != "/GND" and d < 2 * VIA_R + CLR):
                return False
        for a, c, half, net, _ in self.segs:
            if net != "/GND" and self.seg_dist(a, c, (x, y)) < half + VIA_R + CLR:
                return False
        return not self.zone_hit(x, y, VIA_R + 0.3, (P.F_Cu, P.In2_Cu, P.B_Cu))

    def stub_ok(self, a, c, own=None):
        n = max(2, int(math.dist(a, c) / 0.05))
        for i in range(n + 1):
            q = (a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n)
            for p in self.pads:
                if p["front"] and p["net"] != "/GND" and self.rect_dist(p["rect"], *q) < STUB / 2 + CLR:
                    return False
            for u, v, half, net, lay in self.segs:
                if lay == P.F_Cu and net != "/GND" and self.seg_dist(u, v, q) < half + STUB / 2 + CLR:
                    return False
            if i % 3 == 0 and self.zone_hit(q[0], q[1], STUB / 2 + 0.3, (P.F_Cu,)):
                return False
        return True


def centre(p):
    r = p["rect"]
    return (r[0] + r[2]) / 2, (r[1] + r[3]) / 2


def l2_state(b):
    conn = b.GetConnectivity()
    out = {}
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != "/GND":
                continue
            items = conn.GetConnectedItems(p)
            zones = sorted({x.GetZoneName() for x in items if x.GetClass() == "ZONE"})
            pads = sorted({f"{x.GetParentFootprint().GetReference()}.{x.GetNumber()}" for x in items if x.GetClass() == "PAD"} | {f"{f.GetReference()}.{p.GetNumber()}"})
            out[f"{f.GetReference()}.{p.GetNumber()}"] = {"uuid": p.m_Uuid.AsString(), "on_L2": "L2_GND" in zones, "connected_zones": zones, "cluster": pads}
    return out


def candidates(geo, state, banned=frozenset()):
    """One entry per copper cluster not yet on L2. Cluster pads of one footprint in a straight line share one via."""
    by = {f"{p['ref']}.{p['pin']}": p for p in geo.pads if p["net"] == "/GND"}
    open_keys = sorted({tuple(v["cluster"]) for k, v in state.items() if not v["on_L2"]})
    # merge neighbouring clusters of one footprint when a straight F.Cu link clears every other pad
    groups = []
    for cl in open_keys:
        groups.append(list(cl))
    merged = True
    while merged:
        merged = False
        for i, g1 in enumerate(groups):
            for j in range(i + 1, len(groups)):
                g2 = groups[j]
                if g1[0].split(".")[0] != g2[0].split(".")[0]:
                    continue
                pairs = [(a, c) for a in g1 for c in g2 if math.dist(centre(by[a]), centre(by[c])) <= SHARE_MM]
                if pairs and geo.stub_ok(centre(by[pairs[0][0]]), centre(by[pairs[0][1]])):
                    groups[i] = g1 + g2
                    del groups[j]
                    merged = True
                    break
            if merged:
                break
    res, placed = [], []
    for g in groups:
        links = []
        origin = {x: tuple(state[x]["cluster"]) for x in g}
        for a in g[1:]:
            before = g[:g.index(a)]
            if any(origin[c] == origin[a] for c in before):
                continue              # already joined by copper (one KiCad cluster): no extra link
            near = min(before, key=lambda c: math.dist(centre(by[a]), centre(by[c])))
            links.append([near, a])
        pad = by[g[0]]
        best = None
        for name in g:
            p = by[name]
            r = p["rect"]
            cx, cy = centre(p)
            for dist in [0.5 + 0.1 * i for i in range(26)]:
                for k in range(16):
                    ang = k * math.pi / 8
                    x, y = cx + (dist + (r[2] - r[0]) / 2 * abs(math.cos(ang))) * math.cos(ang), cy + (dist + (r[3] - r[1]) / 2 * abs(math.sin(ang))) * math.sin(ang)
                    q = (round(x, 2), round(y, 2))
                    ln = math.dist((cx, cy), q)
                    start = (round(cx + (q[0] - cx) / ln * 0.08, 3), round(cy + (q[1] - cy) / ln * 0.08, 3))   # anchor stays inside the pad, 0.08 mm towards the via
                    if q in banned or not geo.via_ok(q[0], q[1], placed) or not geo.stub_ok(start, q):
                        continue
                    best = {"via": q, "from": name, "start": start, "stub_mm": round(ln, 2)}
                    break
                if best:
                    break
            if best:
                break
        if best:
            placed.append(best["via"])
            res.append({"pads": g, "links": links, **best})
        else:
            res.append({"pads": g, "links": links, "via": None, "from": None, "stub_mm": None, "reason": "no clear position within 3.1 mm of the pad edge"})
    return res


def apply_candidates(b, cands, by):
    net = b.GetNetInfo().GetNetItem("/GND")

    def trk(a, c):
        t = P.PCB_TRACK(b)
        t.SetStart(kp(*a))
        t.SetEnd(kp(*c))
        t.SetWidth(P.FromMM(STUB))
        t.SetLayer(P.F_Cu)
        t.SetNet(net)
        b.Add(t)
    for c in cands:
        if not c["via"]:
            continue
        v = P.PCB_VIA(b)
        v.SetPosition(kp(*c["via"]))
        v.SetViaType(P.VIATYPE_THROUGH)
        v.SetLayerPair(P.F_Cu, P.B_Cu)
        v.SetDrill(P.FromMM(DRILL_R * 2))
        v.SetWidth(P.F_Cu, P.FromMM(VIA_R * 2))
        v.SetNet(net)
        b.Add(v)
        trk(c["start"], c["via"])
        for a, e in c["links"]:
            trk(centre(by[a]), centre(by[e]))


def l2_fill(pcb):
    b = P.LoadBoard(str(pcb))
    P.ZONE_FILLER(b).Fill(b.Zones())
    z = next(x for x in b.Zones() if x.GetZoneName() == "L2_GND")
    f = z.GetFilledPolysList(P.In1_Cu)
    a = 0.0
    for i in range(f.OutlineCount()):
        a += abs(f.COutline(i).Area())
        for h in range(f.HoleCount(i)):
            a -= abs(f.CHole(i, h).Area())
    return {"islands": f.OutlineCount(), "fill_area_mm2": round(a / P.FromMM(1.0) ** 2, 2)}


def step1():
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    OUT.mkdir(parents=True, exist_ok=True)
    D = drc(PCB, OUT / "drc-step1-baseline.json")
    base = {"kicad": P.GetBuildVersion(), **summary(D), "warnings": [{"type": v["type"], "items": [i["description"] for i in v["items"]]} for v in D["violations"] if v["severity"] == "warning"]}
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    geo = Geo(b)
    uid = {p["pad"].m_Uuid.AsString(): f"{p['ref']}.{p['pin']}" for p in geo.pads}
    state = l2_state(b)
    pairs, cls = [], collections.Counter()
    for u in D.get("unconnected_items", []):
        names = [uid.get(i.get("uuid", ""), i["description"]) for i in u["items"]]
        net = net_of(u["items"][0]["description"])
        c = classify(net, names)
        cls[c] += 1
        pairs.append({"net": net, "class": c, "a": names[0], "b": names[1] if len(names) > 1 else "", "uuids": [i.get("uuid", "") for i in u["items"]]})
    desc = {i["description"] for u in D.get("unconnected_items", []) if net_of(u["items"][0]["description"]) == "/GND" for i in u["items"]}
    gnd_endpoints = sorted({n for p in pairs if p["net"] == "/GND" for n in (p["a"], p["b"])})
    gnd_rows = [{"pad": k, **v} for k, v in sorted(state.items())]
    inv = {"pairs": len(pairs), "pairs_by_class": dict(cls), "gnd_pairs": cls["GND dönüş"], "gnd_distinct_descriptions": len(desc), "gnd_distinct_endpoints": len(gnd_endpoints), "gnd_endpoints": gnd_endpoints,
           "gnd_pads_total": len(gnd_rows), "gnd_pads_on_L2": sum(1 for r in gnd_rows if r["on_L2"]), "gnd_pads_not_on_L2": [r["pad"] for r in gnd_rows if not r["on_L2"]],
           "gnd_vias_existing": sum(1 for _, n in geo.vias if n == "/GND"), "open_pairs": pairs, "gnd_pads": gnd_rows}
    by = {f"{p['ref']}.{p['pin']}": p for p in geo.pads if p["net"] == "/GND"}
    banned, tries, cands, trial, l2 = set(), [], [], None, None
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for fn in ("PDU.kicad_pro", "PDU.kicad_dru"):
            shutil.copy(ROOT / fn, t / fn)
        for rnd in range(1, 6):
            cands = candidates(geo, state, banned)
            bt = P.LoadBoard(str(PCB))
            g2 = Geo(bt)
            apply_candidates(bt, cands, {f"{p['ref']}.{p['pin']}": p for p in g2.pads if p["net"] == "/GND"})
            P.ZONE_FILLER(bt).Fill(bt.Zones())
            P.SaveBoard(str(t / "PDU.kicad_pcb"), bt, True)
            d = drc(t / "PDU.kicad_pcb", t / "drc.json")
            trial = summary(d)
            bad = []
            for v in d["violations"]:
                if v["severity"] != "error":
                    continue
                for c in cands:
                    if c["via"] and any("/GND" in i["description"] and abs(i["pos"]["x"] - OX - c["via"][0]) < 0.6 and abs(OY + H - i["pos"]["y"] - c["via"][1]) < 0.6 for i in v["items"]):
                        bad.append(tuple(c["via"]))
            tries.append({"round": rnd, "errors": trial["errors"], "by_type": trial["by_type"], "gnd_pairs_left": trial["pairs_by_net"].get("/GND", 0), "banned": len(set(bad))})
            if trial["errors"] == 0 or not bad:
                break
            banned |= set(bad)
        l2 = l2_fill(t / "PDU.kicad_pcb")
    placed = [c for c in cands if c["via"]]
    res = {"basis": "Trial on a temporary copy of PDU.kicad_pcb; the repository board is unchanged. Via 0.6/0.3 mm, stub 0.25 mm F.Cu (VARSAYIM PCB-HANDOFF §7).",
           "open_gnd_copper_groups_before_sharing": len({tuple(v["cluster"]) for v in state.values() if not v["on_L2"]}), "groups_after_sharing": len(cands),
           "new_vias": len(placed), "no_position_found": [c["pads"] for c in cands if not c["via"]], "max_stub_mm": max((c["stub_mm"] for c in placed), default=None),
           "trial_rounds": tries, "trial_result": trial, "l2_before": l2_fill(PCB), "l2_after_trial": l2, "candidates": cands}
    for fn, obj in (("step1-baseline.json", base), ("step1-inventory.json", inv), ("gnd-via-candidates.json", res)):
        with (OUT / fn).open("w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=0, ensure_ascii=False)
            f.write("\n")
    print(json.dumps({"baseline": {k: base[k] for k in ("errors", "by_type", "schematic_parity_issues", "unconnected_pairs")}, "classes": dict(cls), "gnd": {k: inv[k] for k in ("gnd_pairs", "gnd_distinct_descriptions", "gnd_distinct_endpoints", "gnd_pads_total", "gnd_pads_on_L2", "gnd_vias_existing")},
                      "trial": {k: res[k] for k in ("open_gnd_copper_groups_before_sharing", "groups_after_sharing", "new_vias", "no_position_found", "max_stub_mm", "trial_rounds", "l2_before", "l2_after_trial")}, "after": {k: trial[k] for k in ("errors", "by_type", "schematic_parity_issues", "unconnected_pairs")}}, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------- step 2 (D-012, R-019, R-020)
# Kelvin arms are power-class nets (/ISNSx PHASE, /VOUT BUS): zone taps carrying no load current, 0.25 mm necks only inside the INA296 courtyard.
# Each conductor: [(layer, width, polyline)]; vias join consecutive parts; "tp" = short branch to its moved test pad.
# Phase 2: U12 at 180 deg puts IN+ west and IN- east at its south end, the same order as RS2.1/RS2.2, so both arms run parallel on F.Cu.
# Phase 1: RS1 at 180 deg (scripts/pcb_route_power.py) gives the same order, so both arms are parallel on F.Cu; the alternatives with RS1/U11 unchanged are in --probe1.
U12_POS, U12_ROT = (40.425, 23.805), 180
PAD_U12_1, PAD_U12_8 = (42.538, 22.83), (38.313, 22.83)
KELVIN = {
    "RS1-U11 IN+ (/ISNS1)": {"net": "/ISNS1", "from": "U11.8", "to": "RS1.1", "parts": [("F", 0.4, [(37.7, 66.4), (37.4, 66.0), (31.85, 63.9), (30.337, 62.98)])], "vias": [], "neck": [],
                             "tp": ("F", 0.4, [(37.7, 66.4), (40.2, 67.6)])},
    "RS1-U11 IN- (/VOUT)": {"net": "/VOUT", "from": "U11.1", "to": "RS1.2", "parts": [("F", 0.4, [(32.037, 67.6), (32.45, 66.0), (26.9, 63.9), (26.112, 62.98)])], "vias": [], "neck": [],
                            "tp": ("F", 0.4, [(32.037, 67.6), (30.4, 67.4)])},
    "RS2-U12 IN+ (/ISNS2)": {"net": "/ISNS2", "from": "U12.8", "to": "RS2.1", "parts": [("F", 0.4, [(43.9, 17.7), (44.0, 18.4), (38.8, 22.4), PAD_U12_8])], "vias": [], "neck": [],
                             "tp": ("F", 0.4, [(40.0, 21.48), (38.8, 20.0)])},
    "RS2-U12 IN- (/VOUT)": {"net": "/VOUT", "from": "U12.1", "to": "RS2.2", "parts": [("F", 0.4, [(49.1, 15.6), (48.3, 16.2), (48.3, 18.4), (43.1, 22.4), PAD_U12_1])], "vias": [], "neck": [],
                            "tp": ("F", 0.4, [(45.6, 20.477), (45.6, 19.6)])},
}
# R-020: test pads beside their Kelvin arm (search starts from R-020's coordinates, then checked against the new route).
TP_MOVES = [("TP_ISNS1P", 40.2, 67.6), ("TP_ISNS1N", 29.6, 67.4), ("TP_ISNS2P", 38.8, 20.0), ("TP_ISNS2N", 45.6, 19.6)]
GATE_W = 0.4
TP_GATE = (97.4, 44.6)
TP_BRANCH = [(94.8, 47.49), (96.2, 46.5), (96.2, 44.6), (97.4, 44.6)]
R_GS_POS = (97.5, 49.3)
R_GS_LINK = [(95.9, 49.3), (96.675, 49.3)]
R_GS_VIA = (98.325, 49.3)
OLD_R_GS_VIA = (92.85, 36.645)
REFDES = [("C_ISO_VCAP", 92.6, 44.6, 0), ("R_GS", 97.5, 47.6, 0), ("TP_ISNS1P", 41.5, 69.2, 0), ("RS1", 35.9, 70.2, 0), ("U11", 28.2, 59.4, 0), ("TP_ISNS1N", 26.0, 68.0, 90),
          ("TP_ISNS2P", 36.6, 21.6, 90), ("TP_ISNS2N", 48.4, 21.6, 0), ("RS2", 52.5, 21.0, 0)]
HIDE_REF = ("TP_ISO_GATE",)       # no silk-free spot beside the gate pad; the pad stays identified in D-008 and the assembly drawing
KELVIN_LIMIT = 15.0
# R-021: the real sense vias on the shunt pads (not the pad centres)
SENSE_VIAS = {"RS1.1": (37.7, 66.4), "RS1.2": (32.3, 66.4), "RS2.1": (43.9, 17.7), "RS2.2": (49.1, 15.6)}
POWER_ZONES = ("T022_F_VOUT_RS",)
LAYERS = {"F": P.F_Cu, "B": P.B_Cu}


def polylen(pts):
    return sum(math.dist(a, c) for a, c in zip(pts, pts[1:]))


def t_track(b, net, lay, w, pts):
    for a, c in zip(pts, pts[1:]):
        t = P.PCB_TRACK(b)
        t.SetStart(kp(*a))
        t.SetEnd(kp(*c))
        t.SetWidth(P.FromMM(w))
        t.SetLayer(lay)
        t.SetNet(b.GetNetInfo().GetNetItem(net))
        b.Add(t)


def t_via(b, net, xy):
    v = P.PCB_VIA(b)
    v.SetPosition(kp(*xy))
    v.SetViaType(P.VIATYPE_THROUGH)
    v.SetLayerPair(P.F_Cu, P.B_Cu)
    v.SetDrill(P.FromMM(DRILL_R * 2))
    v.SetWidth(P.F_Cu, P.FromMM(VIA_R * 2))
    v.SetNet(b.GetNetInfo().GetNetItem(net))
    b.Add(v)


def t_zone(b, name, net, lay, polys):
    """One zone from one or more overlapping polygons of the same conductor (a branch must be in the same fill as its arm to be connected)."""
    s0 = P.SHAPE_POLY_SET()
    for poly in polys:
        o = P.SHAPE_POLY_SET()
        o.NewOutline()
        for x, y in poly:
            q = kp(x, y)
            o.Append(q.x, q.y)
        s0.BooleanAdd(o)
    for i in range(s0.OutlineCount()):
        z = P.ZONE(b)
        z.SetZoneName(f"{name}_{i}")
        z.SetNet(b.GetNetInfo().GetNetItem(net))
        z.SetLayer(lay)
        z.SetAssignedPriority(7)
        z.SetMinThickness(P.FromMM(0.25))
        z.SetLocalClearance(P.FromMM(0.3))
        z.SetThermalReliefGap(P.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(P.FromMM(0.5))
        z.SetPadConnection(P.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_NEVER)
        ol = z.Outline()
        idx = ol.NewOutline()
        c = s0.COutline(i)
        for j in range(c.PointCount()):
            ol.Append(c.CPoint(j).x, c.CPoint(j).y, idx)
        b.Add(z)


def extend(pts, d=0.4):
    q = list(pts)
    ln = math.dist(q[0], q[1])
    q[0] = (q[0][0] + (q[0][0] - q[1][0]) / ln * d, q[0][1] + (q[0][1] - q[1][1]) / ln * d)
    ln = math.dist(q[-1], q[-2])
    q[-1] = (q[-1][0] + (q[-1][0] - q[-2][0]) / ln * d, q[-1][1] + (q[-1][1] - q[-2][1]) / ln * d)
    return q


def conductor_mm(k):
    return sum(polylen(p[2]) for p in k["parts"]) + polylen(k["neck"])


def step2():
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    sys.path.insert(0, str(ROOT / "scripts"))
    from pcb_route_power import ribbon
    b = P.LoadBoard(str(PCB))
    if any(z.GetZoneName().startswith("T023_") for z in b.Zones()):
        raise SystemExit("Board already has T023_ zones: start from the T-022 board.")
    fp = {f.GetReference(): f for f in b.GetFootprints()}
    fp["TP_ISO_GATE"].SetPosition(kp(*TP_GATE))
    fp["U12"].SetOrientationDegrees(U12_ROT)
    fp["R_GS"].SetPosition(kp(*R_GS_POS))
    for ref, x, y in TP_MOVES:
        fp[ref].SetPosition(kp(x, y))
    for ref, x, y, ang in REFDES:
        t = fp[ref].Reference()
        t.SetPosition(kp(x, y))
        t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))
    for ref in HIDE_REF:
        fp[ref].Reference().SetVisible(False)
    # the T-022 R_GS.2 via and its B.Cu tap follow the part (positions only; pcbnew Remove corrupts SWIG tables)
    old = next(t for t in b.GetTracks() if t.Type() == P.PCB_VIA_T and t.GetNetname() == "/VSAFE" and math.dist(d6(t.GetPosition()), OLD_R_GS_VIA) < 0.01)
    old.SetPosition(kp(*R_GS_VIA))
    tap = next(z for z in b.Zones() if z.GetZoneName().startswith("T022_TAP_R_GS"))
    ol = tap.Outline()
    ol.RemoveAllContours()
    ol.NewOutline()
    for x, y in ((97.95, 48.9), (98.7, 48.9), (98.7, 49.7), (97.95, 49.7)):
        q = kp(x, y)
        ol.Append(q.x, q.y)
    for i, (name, k) in enumerate(KELVIN.items()):
        for j, (lay, w, pts) in enumerate(k["parts"]):
            polys = [ribbon(extend(pts), w)]
            if k["tp"] and k["tp"][0] == lay and j == 0:
                polys.append(ribbon(extend(k["tp"][2]), k["tp"][1]))
            t_zone(b, f"T023_KELVIN_{i}_{j}", k["net"], LAYERS[lay], polys)
        for xy in k["vias"]:
            t_via(b, k["net"], xy)
        if k["neck"]:
            t_track(b, k["net"], P.F_Cu, 0.25, k["neck"])
    t_track(b, "/ISO_GATE", P.F_Cu, GATE_W, TP_BRANCH)
    t_track(b, "/ISO_GATE", P.F_Cu, GATE_W, R_GS_LINK)
    t_track(b, "/GND", P.F_Cu, 0.25, [(31.0, 62.33), (32.1, 62.62)])       # U11.7 has no room for its own via beside the RS1 Kelvin arm; it shares U13.2's via
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    geo = Geo(b)
    state = l2_state(b)
    by = {f"{p['ref']}.{p['pin']}": p for p in geo.pads if p["net"] == "/GND"}
    cands = candidates(geo, state, frozenset())
    apply_candidates(b, cands, by)
    P.ZONE_FILLER(b).Fill(b.Zones())
    P.SaveBoard(str(PCB), b, True)
    placed = [c for c in cands if c["via"]]
    with (OUT / "step2-gnd-applied.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"groups": len(cands), "new_vias": len(placed), "no_position_found": [c["pads"] for c in cands if not c["via"]], "max_centre_to_via_mm": max((c["stub_mm"] for c in placed), default=None), "candidates": cands}, f, indent=0, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"kelvin_mm": {k: round(conductor_mm(v), 3) for k, v in KELVIN.items()}, "new_gnd_vias": len(placed), "no_position": [c["pads"] for c in cands if not c["via"]]}, ensure_ascii=False))
    return 0


def sample(pts, step=0.05):
    out = []
    for a, c in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, c) / step))
        out += [(a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n) for i in range(n + 1)]
    return out


def outline_pts(z):
    ol = z.Outline().COutline(0)
    return [d6(ol.CPoint(i)) for i in range(ol.PointCount())]


def nearest_on(path, q):
    return min(math.dist(q, x) for x in path)


def step2_audit():
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    D = drc(PCB, OUT / "drc-step2.json")
    base = json.loads((OUT / "step1-baseline.json").read_text(encoding="utf-8"))
    now = summary(D)
    geo = Geo(b)
    conn = b.GetConnectivity()
    pads = {f"{f.GetReference()}.{p.GetNumber()}": p for f in b.GetFootprints() for p in f.Pads()}
    sw = [r for r in geo.pads if r["net"].startswith("/SW_PH")]
    swz = [outline_pts(z) for z in b.Zones() if z.GetNetname().startswith("/SW_PH")]
    l2 = next(z for z in b.Zones() if z.GetZoneName() == "L2_GND")
    res = {}

    def pad_of(r):
        return next(x for x in geo.pads if f"{x['ref']}.{x['pin']}" == r)

    for name, k in KELVIN.items():
        items = conn.GetConnectedItems(pads[k["from"]])
        linked = any(x.GetClass() == "PAD" and f"{x.GetParentFootprint().GetReference()}.{x.GetNumber()}" == k["to"] for x in items)
        pts = [q for p in k["parts"] for q in sample(p[2])] + (sample(k["neck"]) if k["neck"] else [])
        sw_pad = min(geo.rect_dist(r["rect"], *q) for r in sw for q in pts)
        sw_zone = min(min(geo.seg_dist(u, v, q) for u, v in zip(o, o[1:] + o[:1])) for o in swz for q in pts)
        res[name] = {"route_mm": round(conductor_mm(k), 3), "limit_mm": KELVIN_LIMIT, "meets_limit": conductor_mm(k) <= KELVIN_LIMIT, "parts": [{"layer": lay + ".Cu", "width_mm": w, "length_mm": round(polylen(p), 3)} for lay, w, p in k["parts"]],
                     "vias": len(k["vias"]), "neck_mm": round(polylen(k["neck"]), 3), "kicad_connected": linked, "from": k["from"], "to": k["to"], "pad_centre": [round(v, 3) for v in centre(pad_of(k["to"]))], "ribbon_start": k["parts"][0][2][0], "sense_via": SENSE_VIAS.get(k["to"]),
                     "min_distance_to_sw_pad_mm": round(sw_pad, 2), "min_distance_to_sw_copper_outline_mm": round(sw_zone, 2), "l2_under_route_fraction": round(sum(1 for q in pts if l2.HitTestFilledArea(P.In1_Cu, kp(*q), 0)) / len(pts), 3)}
    # R-021: measured on the board, not from names: is each sense via / Kelvin arm inside load-carrying copper of its own net?
    tracks = [t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and P.ToMM(t.GetWidth()) >= 2.0]
    zones = [z for z in b.Zones() if z.GetZoneName().startswith(POWER_ZONES)]
    vias = {tuple(round(v, 2) for v in d6(t.GetPosition())): t for t in b.GetTracks() if t.Type() == P.PCB_VIA_T}
    sense = {}
    for pad, xy in SENSE_VIAS.items():
        net = pads[pad].GetNetname()
        q = kp(*xy)
        ptr = [t for t in tracks if t.GetNetname() == net]
        gaps = [geo.seg_dist(d6(t.GetStart()), d6(t.GetEnd()), xy) - P.ToMM(t.GetWidth()) / 2 - VIA_R for t in ptr]
        zo = [z for z in zones if z.GetNetname() == net]
        zgaps = [min(geo.seg_dist(u, v, xy) for u, v in zip(o, o[1:] + o[:1])) - VIA_R for o in (outline_pts(z) for z in zo)]
        sense[pad] = {"pad_centre": [round(v, 3) for v in centre(pad_of(pad))], "sense_via": xy, "via_exists_on_net": tuple(round(v, 2) for v in xy) in vias and vias[tuple(round(v, 2) for v in xy)].GetNetname() == net,
                      "via_centre_in_power_track": any(t.HitTest(q, 0) for t in ptr), "via_centre_in_power_zone": any(z.HitTestFilledArea(z.GetFirstLayer(), q, 0) for z in zo),
                      "min_gap_to_power_track_mm": round(min(gaps), 3) if gaps else None, "min_gap_to_power_zone_outline_mm": round(min(zgaps), 3) if zgaps else None}
    arms = {}
    for name, k in KELVIN.items():
        hit = 0
        pts = []
        for lay, w, poly in k["parts"]:
            pts = sample(extend(poly))
            hit += sum(1 for q in pts for t in tracks if t.GetNetname() == k["net"] and t.GetLayer() == LAYERS[lay] and t.HitTest(kp(*q), 0))
            hit += sum(1 for q in pts for z in zones if z.GetNetname() == k["net"] and z.IsOnLayer(LAYERS[lay]) and z.HitTestFilledArea(LAYERS[lay], kp(*q), 0))
        arms[name] = {"centre_line_samples_in_own_power_copper": hit}
    pair = {}
    for phase, plus, minus in (("phase 1", "RS1-U11 IN+ (/ISNS1)", "RS1-U11 IN- (/VOUT)"), ("phase 2", "RS2-U12 IN+ (/ISNS2)", "RS2-U12 IN- (/VOUT)")):
        pp, mm = [q for x in KELVIN[plus]["parts"] for q in sample(x[2])], [q for x in KELVIN[minus]["parts"] for q in sample(x[2])]
        d = sorted(nearest_on(mm, q) for q in pp[::4])
        pair[phase] = {"IN+_to_IN-_max_mm": round(d[-1], 3), "IN+_to_IN-_median_mm": round(d[len(d) // 2], 3), "IN-_to_IN+_max_mm": round(max(nearest_on(pp, q) for q in mm[::4]), 3),
                       "length_difference_mm": round(abs(conductor_mm(KELVIN[plus]) - conductor_mm(KELVIN[minus])), 3)}
    a1 = KELVIN["RS2-U12 IN+ (/ISNS2)"]["parts"][0][2][1:3]
    a2 = KELVIN["RS2-U12 IN- (/VOUT)"]["parts"][0][2][2:4]
    def ang(s):
        return math.degrees(math.atan2(s[1][1] - s[0][1], s[1][0] - s[0][0]))
    pair["phase 2"]["main_section_angle_difference_deg"] = round(abs(ang(a1) - ang(a2)), 2)
    b1 = KELVIN["RS1-U11 IN+ (/ISNS1)"]["parts"][0][2][1:3]
    b2 = KELVIN["RS1-U11 IN- (/VOUT)"]["parts"][0][2][1:3]
    pair["phase 1"]["main_section_angle_difference_deg"] = round(abs(ang(b1) - ang(b2)), 2)
    g1, gr = centre(pad_of("Q2.4")), centre(pad_of("R_GS.1"))
    s1, gr2 = min((centre(pad_of(f"Q2.{n}")) for n in (1, 2, 3)), key=lambda c: math.dist(c, centre(pad_of("R_GS.2")))), centre(pad_of("R_GS.2"))
    gp = {"main_U6_Q2_mm": round(polylen([(93.733, 47.49), (94.2, 47.49), (94.8, 47.49), (95.9, 48.65), (95.9, 51.453)]), 3), "limit_mm": 10.0, "width_mm": GATE_W, "layer": "F.Cu",
          "Q2_gate_to_R_GS1_centre_mm": round(math.dist(g1, gr), 3), "Q2_source_to_R_GS2_centre_mm": round(math.dist(s1, gr2), 3), "R_GS_link_track_mm": round(polylen(R_GS_LINK), 3),
          "R_GS_gate_path_from_Q2_gate_pad_mm": round(math.dist(g1, R_GS_LINK[0]) + polylen(R_GS_LINK), 3), "tp_iso_gate_branch_mm": round(polylen(TP_BRANCH), 3)}
    tps = {}
    for ref, (x, y) in {"TP_ISNS1P": (40.2, 67.6), "TP_ISNS1N": (29.6, 67.4), "TP_ISNS2P": (38.8, 20.0), "TP_ISNS2N": (45.6, 19.6)}.items():
        k = next(v for v in KELVIN.values() if ("ISNS1" in ref and "RS1" in v["from"] + v["to"] or "ISNS2" in ref and "RS2" in v["from"] + v["to"]) and ("P" in ref[-1:]) == (v["net"].startswith("/ISNS")))
        items = conn.GetConnectedItems(pads[f"{ref}.1"])
        linked = any(x_.GetClass() == "PAD" and f"{x_.GetParentFootprint().GetReference()}.{x_.GetNumber()}" == k["to"] for x_ in items)
        tps[ref] = {"position": [x, y], "branch_mm": round(polylen(k["tp"][2]), 3), "net_arm": k["net"], "kicad_connected_to_shunt_pad": linked}
    l2f = l2.GetFilledPolysList(P.In1_Cu)
    area = 0.0
    for i in range(l2f.OutlineCount()):
        area += abs(l2f.COutline(i).Area())
        for h in range(l2f.HoleCount(i)):
            area -= abs(l2f.CHole(i, h).Area())
    gapp = json.loads((OUT / "step2-gnd-applied.json").read_text(encoding="utf-8"))
    opened = {n: now["pairs_by_net"].get(n, 0) - v for n, v in base["pairs_by_net"].items() if now["pairs_by_net"].get(n, 0) > v}
    gnd_left = [k for k, v in l2_state(b).items() if not v["on_L2"]]
    out = {"kicad": P.GetBuildVersion(), "baseline": {k: base[k] for k in ("errors", "unconnected_pairs", "schematic_parity_issues")}, "after": {k: now[k] for k in ("errors", "by_type", "schematic_parity_issues", "unconnected_pairs", "pairs_by_net")},
           "new_opens_vs_step1": opened, "kelvin": res, "kelvin_pairing": pair, "sense_takeoff": sense, "kelvin_arm_power_overlap": arms, "gate": gp, "test_pads": tps, "l2": {"islands": l2f.OutlineCount(), "fill_area_mm2": round(area / P.FromMM(1.0) ** 2, 2)},
           "gnd_vias": {"new": gapp["new_vias"], "groups": gapp["groups"], "max_centre_to_via_mm": gapp["max_centre_to_via_mm"], "gnd_pads_not_on_L2": gnd_left}}
    with (OUT / "step2-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: out[k] for k in ("new_opens_vs_step1", "kelvin_pairing", "sense_takeoff", "kelvin_arm_power_overlap", "l2", "gnd_vias")} | {"after": {k: out["after"][k] for k in ("errors", "by_type", "schematic_parity_issues", "unconnected_pairs")}, "kelvin": {k: (v["route_mm"], v["kicad_connected"], v["min_distance_to_sw_copper_outline_mm"], v["l2_under_route_fraction"]) for k, v in res.items()}}, ensure_ascii=False, indent=0))
    return 0


# --------------------------------------------------------------------------- R-020 Tur 2: phase-1 alternatives with RS1/U11 unchanged, on temporary copies
PROBE_ALTERNATIVES = {
    "B_mevcut_F_ve_B": {"plus": [("F", 0.4, [(32.3, 66.4), (31.0, 64.9), (30.337, 62.98)])], "minus": [("F", 0.4, [(37.6, 68.3), (33.9, 65.6), (32.5, 64.0)]), ("B", 0.8, [(32.5, 64.0), (26.1, 64.0)])], "vias": [(32.5, 64.0), (26.1, 64.0)], "neck": [(26.1, 64.0), (26.1, 63.1)]},
    "A_ikisi_F_kuzeyden": {"plus": [("F", 0.4, [(32.3, 66.4), (31.0, 64.9), (30.337, 62.98)])], "minus": [("F", 0.4, [(37.6, 68.3), (36.8, 70.6), (31.0, 70.6), (27.0, 66.0), (26.112, 62.98)])], "vias": [], "neck": []},
    "C_F_uzerinde_gidis_donus": {"plus": [("F", 0.4, [(32.3, 66.4), (31.4, 65.2), (27.4, 65.2), (27.4, 64.4), (30.337, 62.98)])], "minus": [("F", 0.4, [(37.6, 68.3), (33.9, 65.6), (32.5, 64.0)]), ("B", 0.8, [(32.5, 64.0), (26.1, 64.0)])], "vias": [(32.5, 64.0), (26.1, 64.0)], "neck": [(26.1, 64.0), (26.1, 63.1)]},
}


def probe_phase1():
    sys.path.insert(0, str(ROOT / "scripts"))
    from pcb_route_power import ribbon
    results = {}
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for fn in ("PDU.kicad_pro", "PDU.kicad_dru"):
            shutil.copy(ROOT / fn, t / fn)
        for name, alt in PROBE_ALTERNATIVES.items():
            b = P.LoadBoard(str(PCB))
            for j, (lay, w, pts) in enumerate(alt["plus"]):
                t_zone(b, f"T023_PROBE_P{j}", "/ISNS1", LAYERS[lay], [ribbon(extend(pts), w)])
            for j, (lay, w, pts) in enumerate(alt["minus"]):
                t_zone(b, f"T023_PROBE_M{j}", "/VOUT", LAYERS[lay], [ribbon(extend(pts), w)])
            for xy in alt["vias"]:
                t_via(b, "/VOUT", xy)
            if alt["neck"]:
                t_track(b, "/VOUT", P.F_Cu, 0.25, alt["neck"])
            P.ZONE_FILLER(b).Fill(b.Zones())
            P.SaveBoard(str(t / "PDU.kicad_pcb"), b, True)
            d = drc(t / "PDU.kicad_pcb", t / "drc.json")
            s0 = summary(d)
            pl, mi = sum(polylen(x[2]) for x in alt["plus"]), sum(polylen(x[2]) for x in alt["minus"]) + polylen(alt["neck"])
            pp = [q for x in alt["plus"] for q in sample(x[2])]
            mm = [q for x in alt["minus"] for q in sample(x[2])]
            near = sum(1 for q in mm if nearest_on(pp, q) <= 2.0) / len(mm)
            results[name] = {"errors": s0["errors"], "error_types": {k: v for k, v in s0["by_type"].items() if k.startswith("error")}, "parity": s0["schematic_parity_issues"], "IN+_mm": round(pl, 3), "IN-_mm": round(mi, 3), "IN-_share_within_2mm_of_IN+": round(near, 3), "pass_15mm": pl <= KELVIN_LIMIT and mi <= KELVIN_LIMIT}
    with (OUT / "phase1-alternatives.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"basis": "R-020 Tur 2: RS1 and U11 unchanged, temporary copies of the T-022 board, only the phase-1 arms added.", "results": results}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(results, ensure_ascii=False, indent=0))
    return 0


if __name__ == "__main__":
    if "--step1" in sys.argv:
        sys.exit(step1())
    if "--step2" in sys.argv:
        sys.exit(step2())
    if "--audit2" in sys.argv:
        sys.exit(step2_audit())
    if "--probe1" in sys.argv:
        sys.exit(probe_phase1())
    raise SystemExit(__doc__)
