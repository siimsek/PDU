"""T-023 signal routing (D-012) — KiCad's bundled Python 10.0.7 (D-009).

Step 1 (D-012, read-only for PDU.kicad_pcb):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_route_signals.py --step1
    ...python.exe scripts/pcb_route_signals.py --step2      # writes PDU.kicad_pcb: run on the T-022 board only (it refuses a board that already has T023_ zones)
    ...python.exe scripts/pcb_route_signals.py --audit2     # step 2 evidence: DRC, Kelvin lengths, SW distance, L2
    ...python.exe scripts/pcb_route_signals.py --assembly-map                 # R-022 Tur 5: board-bound map of the passives with hidden silk references
    ...python.exe scripts/pcb_route_signals.py --audit-ref [--before <board>] / --probe-map   # R-022 Tur 3: reference-net geometry, board-bound probe map
    ...python.exe scripts/pcb_route_signals.py --step3 / --gnd / --audit3    # order after --step2: signals, then GND returns in the room left, then evidence

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
TP_MOVES = [("RFB1", 42.55, 83.8), ("RFB2", 45.95, 83.8), ("R_TRIM", 49.15, 83.8), ("CHF", 53.6, 83.8), ("RCOMP", 57.0, 83.8), ("CCOMP", 60.4, 83.8), ("TP_COMP", 54.3, 22.7), ("TP_GND_FB", 65.6, 83.45), ("TP_FB_INJ_A", 62.4, 71.8), ("TP_FB_INJ_B", 68.4, 71.8),
            ("TP_GND_OVP", 76.5, 14.0), ("TP_OVP_REF", 68.4, 83.6), ("TP_OC_REF", 47.6, 22.0), ("TP_OVP_Q", 101.5, 62.6), ("TP_OC_SENSE1", 33.0, 59.5), ("TP_OC_SENSE2", 38.5, 27.0), ("TP_GND_OC", 50.5, 22.0), ("TP_ISNS1P", 40.2, 67.6), ("TP_ISNS1N", 29.6, 67.4), ("TP_ISNS2P", 38.8, 20.0), ("TP_ISNS2N", 45.6, 19.6)]
# R-022 Tur 8: local placement of the LM70880 bypass, bootstrap and pin resistors (SNVSBX7A p.4, p.44): (ref, x, y, orientation)
STEP4_PLACE = [("CVDDA1", 46.3, 81.55, 0), ("CVCC1", 44.55, 69.5, 0), ("RCFG1", 51.125, 81.7, 0), ("RSYNC", 59.0, 81.9, 0), ("CBOOT1", 54.625, 78.125, 180), ("RBOOT1", 54.93, 76.55, 180),
               ("CVDDA2", 40.0, 2.2, 0), ("RBOOT2", 29.2, 7.55, 0), ("CBOOT2", 29.2, 6.0, 0), ("RCFG2", 32.4, 1.5, 180), ("RT2", 36.825, 1.5, 0), ("RILIM2", 104.95, 32.15, 270)]
# R-022 Tur 8: 0.6 mm HV escape beside the fine-pitch /VOUT and /ISNS pins, as zones (no track centre fits inside the pads). (name, net, polygon on F.Cu)
ESCAPES = [("T023_ESC_U1_12", "/VOUT", [(49.0, 79.12), (49.375, 79.12), (49.375, 80.85), (49.65, 80.85), (49.65, 81.35), (49.175, 81.35), (49.175, 79.4)]),
           ("T023_ESC_U1_11", "/ISNS1", [(49.975, 79.12), (50.175, 79.12), (50.175, 80.0), (50.6, 80.05), (50.6, 80.45), (50.2, 80.45), (49.975, 80.1)]),
           ("T023_ESC_U2_12", "/VOUT", [(34.5, 4.88), (34.125, 4.88), (34.125, 3.15), (33.85, 3.15), (33.85, 2.65), (34.325, 2.65), (34.325, 4.6)]),
           ("T023_ESC_U2_11", "/ISNS2", [(33.525, 4.88), (33.325, 4.88), (33.325, 4.0), (32.9, 3.95), (32.9, 3.55), (33.3, 3.55), (33.525, 3.9)]),
           ("T023_ESC_U3_16", "/VSAFE", [(102.8, 41.1), (103.24, 41.1), (103.24, 41.325), (102.8, 41.325)]), ("T023_ESC_U4_16", "/VSAFE", [(109.59, 41.1), (110.03, 41.1), (110.03, 41.325), (109.59, 41.325)])]
ESC_TRACKS = (("/VOUT", (49.0, 79.65), (49.0, 80.4)), ("/ISNS1", (50.0, 79.65), (50.1, 80.95)), ("/VOUT", (34.5, 4.35), (34.5, 2.9)), ("/ISNS2", (33.5, 4.35), (33.4, 3.6)), ("/VSAFE", (103.225, 41.12), (102.8, 41.12)), ("/VSAFE", (110.015, 41.12), (109.6, 41.12)))
ESC_VIAS = (("/VOUT", (49.0, 80.4), (49.34, 81.0)), ("/ISNS1", (50.1, 80.95), (50.4, 80.25)), ("/VOUT", (34.5, 2.9), (34.105, 3.0)), ("/ISNS2", (33.4, 3.6), (33.1, 3.75)), ("/VIN", (90.35, 79.75), (89.6, 79.4)))
GATE_W = 0.4
TP_GATE = (97.4, 44.6)
TP_BRANCH = [(94.8, 47.49), (96.2, 46.5), (96.2, 44.6), (97.4, 44.6)]
R_GS_POS = (97.5, 49.3)
R_GS_LINK = [(95.9, 49.3), (96.675, 49.3)]
R_GS_VIA = (98.325, 49.3)
OLD_R_GS_VIA = (92.85, 36.645)
REFDES = [("C_ISO_VCAP", 92.6, 44.6, 0), ("R_GS", 97.5, 47.6, 0), ("TP_ISNS1P", 41.5, 69.2, 0), ("RS1", 35.9, 70.2, 0), ("U11", 28.2, 59.4, 0), ("TP_ISNS1N", 26.0, 68.0, 90),
          ("TP_ISNS2P", 36.6, 21.6, 90), ("R_INJ", 65.34, 70.3, 0), ("TP_OC_SENSE1", 33.0, 57.9, 0), ("RS2", 53.4, 21.0, 0)]
HIDE_REF = ("CIN3", "TP_SW1", "TP_ISNS1P", "TP_OVP_Q", "RBOOT1", "RBOOT2", "CBOOT1", "CBOOT2", "CVDDA2", "RCFG1", "RCFG2", "RIMON2", "RILIM2", "TP_ISO_GATE", "TP_GND_OC", "TP_ISNS2N", "TP_OVP_REF", "RFB1", "RFB2", "R_TRIM", "CHF", "RCOMP", "CCOMP", "TP_COMP", "TP_GND_OVP", "CVCC1", "CVDDA1", "RT1", "TP_OC_REF", "TP_FB_INJ_A", "TP_FB_INJ_B")       # no silk-free spot beside these pads; they stay identified in D-008 and the assembly drawing
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


def t_zone(b, name, net, lay, polys, min_t=0.25, clr=0.3):
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
        z.SetMinThickness(P.FromMM(min_t))
        z.SetLocalClearance(P.FromMM(clr))
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
    for ref, x, y, ang in STEP4_PLACE:
        fp[ref].SetOrientationDegrees(ang)
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
    t_zone(b, "T023_TAP_R_INJ_F", "/VOUT", P.F_Cu, [[(62.0, 71.35), (64.9, 71.35), (64.9, 74.4), (64.1, 74.4), (64.1, 72.25), (62.0, 72.25)]])
    t_zone(b, "T023_TAP_R_INJ_B", "/VOUT", P.B_Cu, [[(48.6, 80.0), (49.7, 80.0), (49.7, 82.2), (64.1, 82.2), (64.1, 73.6), (64.9, 73.6), (64.9, 83.0), (48.6, 83.0)]])
    t_via(b, "/VOUT", (64.5, 74.0))
    t_track(b, "/GND", P.F_Cu, 0.25, [(43.3, 24.7), (44.35, 24.455)])       # R-022 Tur 2: U14.2 joins U12.4's local GND before the signals take the room
    # R-022 Tur 2: the U6.5 tap moves 0.35 mm east so /ISO_OV can pass under U6 with 0.6 mm to /VOUT (positions only)
    tap = next(t for t in b.GetTracks() if t.Type() == P.PCB_VIA_T and t.GetNetname() == "/VOUT" and math.dist(d6(t.GetPosition()), (93.4, 45.75)) < 0.01)
    tap.SetPosition(kp(93.75, 45.75))
    neck = next(t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and t.GetNetname() == "/VOUT" and math.dist(d6(t.GetStart()), (93.4, 46.7)) < 0.01)
    neck.SetEnd(kp(93.75, 45.75))
    stub = next(t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and t.GetNetname() == "/VSAFE" and math.dist(d6(t.GetStart()) if math.dist(d6(t.GetStart()), (93.733, 49.3)) < 0.01 else d6(t.GetEnd()), (93.733, 49.3)) < 0.01 and min(math.dist(d6(t.GetStart()), (93.733, 48.79)), math.dist(d6(t.GetEnd()), (93.733, 48.79))) < 0.01)
    if math.dist(d6(stub.GetEnd()), (93.733, 48.79)) < 0.01:
        stub.SetEnd(kp(93.733, 49.0))
    else:
        stub.SetStart(kp(93.733, 49.0))
    t_track(b, "/GND", P.F_Cu, 0.25, [(31.0, 62.33), (32.1, 62.62)])       # U11.7 has no room for its own via beside the RS1 Kelvin arm; it shares U13.2's via
    gone = [t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and any(t.GetNetname() == n_ and math.dist(d6(t.GetStart()), a_) < 0.01 and math.dist(d6(t.GetEnd()), c_) < 0.01 for n_, a_, c_ in ESC_TRACKS)]
    assert len(gone) == len(ESC_TRACKS), len(gone)
    for n_, a_, c_ in ESC_VIAS:
        next(t for t in b.GetTracks() if t.Type() == P.PCB_VIA_T and t.GetNetname() == n_ and math.dist(d6(t.GetPosition()), a_) < 0.01).SetPosition(kp(*c_))
    stub = next(t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and t.GetNetname() == "/VIN" and math.dist(d6(t.GetEnd()), (90.35, 79.75)) < 0.01)
    stub.SetEnd(kp(89.6, 79.4))
    for dx_ in (0.0, 6.79):                  # U3/U4.17: the link starts at the pad corner so the /VSAFE tie of pin 16 keeps 0.6 mm
        t = next(t for t in b.GetTracks() if t.Type() != P.PCB_VIA_T and t.GetLayer() == P.F_Cu and t.GetNetname() in ("/O1_11V", "/S2E_11V") and min(math.dist(d6(t.GetStart()), (103.77 + dx_, 41.78)), math.dist(d6(t.GetEnd()), (103.77 + dx_, 41.78))) < 0.03)
        (t.SetStart if math.dist(d6(t.GetStart()), (103.77 + dx_, 41.78)) < 0.03 else t.SetEnd)(kp(103.795 + dx_, 41.795))
    tail = next(z for z in b.Zones() if z.GetZoneName().startswith("T022_TAP_ISNS1"))     # the unused end above the moved via would push the /VOUT ribbon off the U1.12 via (0.6 mm)
    ol = tail.Outline()
    for i_ in range(ol.VertexCount()):
        v_ = ol.CVertex(i_)
        if d6(v_)[1] > 80.7:
            ol.SetVertex(i_, kp(50.05 if d6(v_)[0] < 50.0 else d6(v_)[0], 80.65))
    ol = next(z for z in b.Zones() if z.GetZoneName().startswith("T022_TAP_TP_VOUT") and z.GetBoundingBox().Contains(kp(49.0, 81.0))).Outline()     # the moved U1.12 via stays inside both /VOUT ribbons, which is what joins them
    for i_ in range(ol.VertexCount()):
        v_ = ol.CVertex(i_)
        x_, y_ = d6(v_)
        if abs(x_ - 49.4) < 0.01 or abs(y_ - 83.0) < 0.01:      # east side: the moved via; north side: room for the CVDDA1.2 GND via without splitting the ribbon
            ol.SetVertex(i_, kp(49.7 if abs(x_ - 49.4) < 0.01 else x_, 83.5 if abs(y_ - 83.0) < 0.01 else y_))
    t_zone(b, "T023_TAP_U10_5", "/VIN", P.B_Cu, [[(89.3, 79.1), (90.75, 79.1), (90.75, 80.0), (89.3, 80.0)]])
    for name_, net_, pts_ in ESCAPES:
        t_zone(b, name_, net_, P.F_Cu, [pts_], min_t=0.19, clr=0.2)
    for t in gone:
        b.Remove(t)
    P.ZONE_FILLER(b).Fill(b.Zones())
    P.SaveBoard(str(PCB), b, True)
    print(json.dumps({"kelvin_mm": {k: round(conductor_mm(v), 3) for k, v in KELVIN.items()}}, ensure_ascii=False))
    return 0


def gnd_returns():
    """Run after the signal router: every /GND pad not yet on L2 gets a local stub and via in the room the signals left."""
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    geo = Geo(b)
    state = l2_state(b)
    by = {f"{p['ref']}.{p['pin']}": p for p in geo.pads if p["net"] == "/GND"}
    cands = candidates(geo, state, frozenset())
    apply_candidates(b, cands, by)
    # A pad with no straight stub to a free via position gets a searched F.Cu path to the nearest one.
    open_groups = [c for c in cands if not c["via"]]
    if open_groups:
        P.ZONE_FILLER(b).Fill(b.Zones())
        g2 = Geo(b)
        netcode = {n: i + 1 for i, n in enumerate(sorted({p["net"] for p in g2.pads} | {s_[3] for s_ in g2.segs} | {v[1] for v in g2.vias} | {z.GetNetname() for z in b.Zones()}))}
        G = build_grid(b, g2, netcode)
        code = netcode["/GND"]
        shared = set()
        for c in open_groups:
            pad_rec = next(p for p in g2.pads if f"{p['ref']}.{p['pin']}" == c["pads"][0])
            pin = (c["pads"][0], centre(pad_rec), pad_rec["front"], pad_rec["th"], pad_rec["rect"])
            cell, ex = pad_exit(G, code, pin, 0)
            if not cell:
                c["reason"] = "no free exit at the pad"
                continue
            found = nearest_via(G, code, cell)
            if not found:
                c["reason"] = "no via position reachable on F.Cu"
                continue
            path = simplify(found)
            xy = [(i * GRID, j * GRID) for j, i, _ in path]
            t_track(b, "/GND", P.F_Cu, ROUTE_W, [pin[1], ex, xy[0]])
            if len(xy) > 1:
                t_track(b, "/GND", P.F_Cu, ROUTE_W, xy)
            near_via = min((q for q, n_ in g2.vias if n_ == "/GND"), key=lambda q: math.dist(q, xy[-1]), default=None)
            if near_via is not None and math.dist(near_via, xy[-1]) < 0.7:     # join a via already there instead of drilling beside it
                t_track(b, "/GND", P.F_Cu, ROUTE_W, [xy[-1], near_via])
                xy = xy + [near_via]
            elif xy[-1] not in shared:          # several searched pads can end on one via; drill it once
                t_via(b, "/GND", xy[-1])
                shared.add(xy[-1])
            c.update({"via": list(xy[-1]), "from": pin[0], "stub_mm": round(polylen([pin[1], ex] + xy), 2), "path": "searched"})
            for a_, c_ in zip([pin[1], ex] + xy, ([pin[1], ex] + xy)[1:]):
                G.seg([0], code, a_, c_, ROUTE_W + ROUTE_CLR + DIAG_MARGIN, ROUTE_W / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)
            G.seg([0, 1, 2], code, xy[-1], xy[-1], VIA_R + ROUTE_CLR + ROUTE_W / 2 + DIAG_MARGIN, VIA_R + ROUTE_CLR + VIA_R + DIAG_MARGIN)
    P.ZONE_FILLER(b).Fill(b.Zones())
    P.SaveBoard(str(PCB), b, True)
    placed = [c for c in cands if c["via"]]
    with (OUT / "step4-gnd-applied.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"groups": len(cands), "new_vias": len(placed), "no_position_found": [c["pads"] for c in cands if not c["via"]], "max_centre_to_via_mm": max((c["stub_mm"] for c in placed), default=None), "candidates": cands}, f, indent=0, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"new_gnd_vias": len(placed), "no_position": [c["pads"] for c in cands if not c["via"]]}, ensure_ascii=False))
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


# --------------------------------------------------------------------------- step 3 (D-012): bounded deterministic router for FB/COMP/OVP/OC
STEP3_NETS = ("/FB", "/FB_TRIM", "/FB_INJ", "/COMP", "/COMP_MID", "/OVP_SENSE", "/OVP_REF", "/OVP_TRIP_N", "/OVP_Q", "/OVP_BUS_N", "/OC_SENSE1", "/OC_SENSE2", "/OC_REF", "/OC_TRIP1_N", "/OC_TRIP2_N", "/CLR_N", "/ISO_EN", "/ISO_OV")
HV_NETS = ("/ANODE", "/VIN", "/VOUT", "/VSAFE")
STEP4_NETS = ("/CBOOT1", "/CBOOT2", "/CBOOT_R1", "/CBOOT_R2", "/CFG_PRI", "/CFG_SEC", "/DVDT_O1", "/DVDT_S2E", "/EN_BUCK", "/EN_EFUSE", "/GATE", "/ILIM_O1", "/ILIM_S2E", "/IMON_O1", "/IMON_S2E", "/ISO_VCAP", "/LDO_DELAY", "/P5V_PROT", "/PG_O1", "/PG_S2E", "/REF_NR", "/RT_PH1", "/RT_PH2", "/SW4_PH1", "/SW4_PH2", "/SYNC", "/VCAP", "/VCC1", "/VCC2", "/VDDA1", "/VDDA2")
AUX_NETS = ("/CBOOT1", "/CBOOT2", "/CBOOT_R1", "/CBOOT_R2", "/SW4_PH1", "/SW4_PH2", "/VCAP", "/GATE", "/VCC1", "/VCC2", "/VDDA1", "/VDDA2", "/ISO_VCAP")   # AUX_LOCAL netclass: 0.5 mm where it fits, 0.25 mm at the pad ends
AUX_W = 0.5
STEP4_HOLD = ()
STEP3_FIRST = ("/COMP", "/FB", "/OVP_REF", "/OC_REF", "/ISO_EN", "/OVP_BUS_N", "/ISO_OV", "/CLR_N", "/OC_TRIP2_N", "/EN_BUCK", "/SYNC", "/EN_EFUSE", "/ILIM_O1", "/IMON_O1", "/DVDT_O1", "/PG_O1", "/DVDT_S2E", "/PG_S2E", "/ILIM_S2E", "/IMON_S2E")   # routed in this order, before the span-sorted rest
SENSITIVE = ("/COMP", "/FB", "/OVP_REF", "/OC_REF")   # R-022 Tur 3: F.Cu over L2 first, few layer changes, away from SW
SENS_FAR = ("/OVP_REF", "/OC_REF")   # PCB-HANDOFF §3 item 5 group: the 10 mm cost applies to these only; /FB and /COMP must stay at U1
STEP3_ROOT = {"/EN_EFUSE": "U3.6", "/OVP_REF": "U8.6", "/OC_REF": "R_OCB.1", "/VDDA1": "CVDDA1.1", "/VDDA2": "CVDDA2.1"}   # tree grows out from the source/divider so probes and branches stay local
SENS_KEEP = 10.0       # mm: PCB-HANDOFF §3 item 5; a routing cost, not a pass/fail limit
SENS_B_COST = 2.0
SENS_VIA_COST = 24.0
STEP3_PREFIX = {"/GND": {"U6.2": [(91.457, 48.14), (88.8, 48.14)], "U15.2": [(91.698, 81.055), (92.72, 81.29)], "U11.2": [(26.112, 61.03), (26.112, 62.33), (24.2, 62.33)],
                         "R_TRIM.2": [(49.975, 83.8), (50.95, 83.6)], "CHF.2": [(54.375, 83.8), (55.25, 83.8)], "CCOMP.2": [(61.175, 83.8), (62.0, 83.8)], "R_BLS.2": [(91.225, 75.685), (90.95, 74.48)], "C_LDO_DELAY.2": [(87.897, 71.845), (87.32, 72.44)], "U10.9": [(87.115, 81.005), (86.02, 79.83)], "U2.16": [(36.5, 4.6), (36.82, 5.6)], "CVDDA1.2": [(47.075, 82.0), (47.075, 82.32)], "RT1.2": [(56.046, 82.025), (55.49, 81.43)], "RCFG1.2": [(52.35, 81.7), (52.75, 81.7)], "CVCC1.2": [(45.5, 68.775), (45.5, 68.3)], "C_LAT.2": [(78.6, 64.07), (78.6, 63.5)], "RILIM2.2": [(104.95, 30.9), (104.95, 30.4)], "U9.1": [(101.02, 82.255), (100.35, 82.5)], "SW1.2": [(99.5, 81.95), (99.5, 82.4)], "RIMON1.2": [(102.43, 34.4), (102.75, 33.75)], "RIMON2.2": [(102.43, 31.42), (102.95, 31.9)], "CVDDA2.2": [(41.225, 2.2), (41.75, 2.2)], "RCFG2.2": [(31.175, 1.5), (30.7, 1.5)], "U7.2": [(103.395, 75.715), (103.908, 75.715), (104.25, 75.75)], "C_OCC1.2": [(43.189, 63.025), (44.04, 63.29)], "RT2.2": [(37.65, 1.975), (37.65, 2.6)], "U1.6": [(51.9, 77.75), (52.7, 77.75)], "U1.8": [(51.9, 78.75), (52.7, 78.75)], "U2.6": [(31.6, 6.25), (32.4, 6.25)]}, "/GATE": {"U5.5": [(21.29, 42.5), (21.95, 42.5)]}, "/DVDT_O1": {"U3.15": [(103.78, 40.63), (104.15, 40.63), (104.15, 34.5), (104.4, 33.9)]}, "/ILIM_O1": {"U3.8": [(100.84, 38.75), (100.84, 37.65)]}, "/IMON_O1": {"U3.9": [(101.34, 38.75), (101.34, 37.65), (102.95, 36.05), (102.95, 34.8)]}, "/EN_EFUSE": {"U3.6": [(99.4, 39.67), (99.0, 39.67), (99.0, 35.55)]}, "/DVDT_S2E": {"U4.15": [(110.57, 40.63), (110.92, 40.63), (110.92, 38.52), (108.0, 35.6), (107.85, 35.1)]}, "/PG_O1": {"U3.13": [(103.68, 39.6), (103.65, 39.2), (103.65, 34.5), (103.5, 34.05)]}, "/PG_S2E": {"U4.13": [(110.47, 39.6), (110.4, 39.2), (110.4, 38.64), (106.8, 35.04), (106.95, 34.35)]}, "/LDO_DELAY": {"U10.7": [(89.97, 81.26), (90.65, 81.26), (90.65, 78.9)]}, "/P5V_PROT": {"U10.1": [(84.26, 81.98), (84.0, 82.3), (84.0, 82.8)], "U9.2": [(102.25, 81.755), (102.75, 81.75)]}, "/VCC1": {"U1.19": [(45.8, 77.25), (45.5, 77.05), (45.2, 76.95)]}, "/OVP_BUS_N": {"U7.1": [(103.395, 76.365), (102.6, 76.365), (102.6, 77.4)]}, "/COMP": {"U1.15": [(47.46, 79.5), (47.46, 79.75), (47.395, 80.4), (47.395, 80.7), (44.25, 80.7), (44.25, 82.95), (63.4, 82.95)], "U2.15": [(36.04, 4.31), (36.04, 3.9)]}, "/EN_BUCK": {"U1.9": [(51.05, 79.69), (51.05, 80.1), (51.3, 80.55)]}, "/IMON_S2E": {"U4.9": [(108.13, 38.75), (108.13, 37.01), (105.9, 34.78), (105.9, 32.4)]},
                "/ISO_OV": {"U6.7": [(93.733, 48.14), (92.5, 48.14), (92.5, 45.4)]}, "/OVP_Q": {"U9.5": [(104.445, 80.755), (105.4, 80.755), (105.4, 80.0)]},
                "/OVP_REF": {"U7.3": [(103.395, 75.065), (102.5, 75.065), (102.5, 74.2)]}, "/OC_TRIP2_N": {"U14.1": [(44.757, 25.105), (44.0, 25.105), (44.0, 26.2)]}}
# R-022 Tur 4 / SNVSCD3 p.44, p.20: FB divider at the FB pin and compensation at the primary. Hand-placed copper, routed nowhere else.
STEP3_FIXED = {"/VDDA1": [[(45.85, 77.75), (45.4, 77.8), (45.4, 79.6)], [(44.9, 81.55), (45.15, 81.55)]],
               "/RT_PH1": [[(47.95, 79.69), (47.855, 80.4), (47.855, 82.5), (54.03, 82.5)]], "/CFG_PRI": [[(48.45, 79.69), (48.315, 80.4), (48.315, 82.03), (49.92, 82.03)]],
               "/RT_PH2": [[(35.55, 4.31), (35.585, 3.6), (35.62, 1.95)]], "/CFG_SEC": [[(35.05, 4.31), (35.13, 3.6), (35.13, 1.85), (33.6, 1.85)]],
               "/CBOOT1": [[(52.2, 76.25), (52.95, 76.25), (53.75, 76.4)]], "/SW4_PH1": [[(52.2, 76.75), (52.75, 76.75), (53.5, 77.6), (53.85, 77.8)]], "/CBOOT_R1": [[(55.6, 77.7), (55.7, 77.0)]],
               "/EN_EFUSE": [[(106.2, 39.67), (105.9, 39.67), (105.9, 36.15), (105.1, 35.55)]], "/ILIM_S2E": [[(107.63, 38.75), (107.63, 37.15), (106.08, 35.6), (105.45, 34.97), (105.28, 34.5), (105.0, 33.35)]], "/CBOOT2": [[(31.3, 7.75), (30.4, 7.7)]], "/SW4_PH2": [[(31.3, 7.25), (30.7, 6.3), (30.4, 6.2)]], "/CBOOT_R2": [[(28.4, 7.1), (28.4, 6.45)]], "/FB": [[(47.0, 79.4), (46.9, 80.25), (43.8, 80.25), (43.8, 83.8)], [(43.375, 83.8), (45.125, 83.8)]], "/FB_TRIM": [[(46.775, 83.8), (48.325, 83.8)]],
               "/GND": [[(101.02, 80.755), (99.9, 80.755)], [(46.38, 78.25), (47.5, 78.25)], [(84.965, 80.03), (86.02, 79.83)], [(65.6, 83.45), (62.0, 83.8)], [(36.82, 5.6), (37.4, 5.75)]], "/COMP_MID": [[(57.825, 83.8), (59.625, 83.8)]], "/COMP": [[(52.825, 82.95), (52.825, 83.8)], [(56.175, 82.95), (56.175, 83.8)]]}
STEP3_SKIP = ("/ILIM_S2E", "/FB", "/FB_TRIM", "/COMP_MID", "/RT_PH1", "/RT_PH2", "/CFG_PRI", "/CFG_SEC", "/CBOOT1", "/CBOOT_R1", "/SW4_PH1", "/CBOOT2", "/CBOOT_R2", "/SW4_PH2")
STEP4_VIAS = {"/VDDA1": [(45.4, 79.6), (44.9, 81.55)], "/EN_EFUSE": [(99.0, 35.55), (105.1, 35.55)], "/IMON_O1": [(102.95, 34.8)], "/PG_O1": [(103.5, 34.05)], "/PG_S2E": [(106.95, 34.35)], "/DVDT_O1": [(104.4, 33.9)]}
STEP4_B = {"/VDDA1": [[(45.4, 79.6), (44.9, 81.55)]], "/EN_EFUSE": [[(99.0, 35.55), (105.1, 35.55)]]}
STEP4_SEED = {"/VDDA1": [(45.4, 77.8, 0)], "/EN_EFUSE": [(99.0, 35.55, 1), (105.1, 35.55, 1)]}
STEP4_B_NET = ("/IMON_O1", "/DVDT_O1", "/PG_S2E")   # off F.Cu in the U3/U4 fan-out corridor
STEP4_B_KEEP = ((105.95, 31.35, 108.15, 33.85),)   # J3.2: room for the L4_GND thermal spokes
STEP4_FORCE_B = ("U3.9", "U3.13", "U3.15", "U4.13")   # these pad exits end on a placed via: the rest of the net stays off F.Cu, which the U3/U4 fan-out needs
STEP4_KEEP = {"/P5V_PROT": [(84.0, 82.8), (102.75, 81.75)], "/EN_BUCK": [(51.3, 80.55)], "/IMON_O1": [(102.95, 34.8)],  "/DVDT_S2E": [(107.85, 35.1)]}   # room for the via the router will drop at the end of a walled-in pad exit
STEP3_DONE = ("RCOMP.1", "CHF.1", "U1.18", "U4.6")
YIELDING_ZONES = ("T022_F_VSAFE_Q2",)
GRID = 0.15
ROUTE_W = 0.25
ROUTE_CLR = 0.2
HV_CLR = 0.6
EDGE_CLR = 0.5
HOLE_CLR = 0.25
SW_KEEP = 4.0          # mm: cost grows inside this distance of switch copper (PCB-HANDOFF §3, standard L14)
LAYER_COST = {0: 1.0, 1: 1.3}   # F.Cu first: L2 GND is its reference
VIA_COST = 8.0
MAX_EXPAND = 900000
DIAG_MARGIN = 0.04     # mm: a diagonal step between two free cell centres passes this much closer to a corner


class Grid:
    def __init__(self):
        import numpy as np
        self.np = np
        self.nx, self.ny = int(W / GRID) + 1, int(H / GRID) + 1
        self.cnt = [np.zeros((self.ny, self.nx), np.uint8) for _ in range(3)]      # F, B, In2 (via only)
        self.own = [np.full((self.ny, self.nx), -1, np.int32) for _ in range(3)]
        self.vcnt = [np.zeros((self.ny, self.nx), np.uint8) for _ in range(3)]
        self.vown = [np.full((self.ny, self.nx), -1, np.int32) for _ in range(3)]
        ys, xs = np.mgrid[0:self.ny, 0:self.nx]
        self.xs, self.ys = xs * GRID, ys * GRID
        self.sw = np.zeros((self.ny, self.nx), float)
        self.sw10 = np.zeros((self.ny, self.nx), float)
        edge = (self.xs < EDGE_CLR + ROUTE_W / 2) | (self.xs > W - EDGE_CLR - ROUTE_W / 2) | (self.ys < EDGE_CLR + ROUTE_W / 2) | (self.ys > H - EDGE_CLR - ROUTE_W / 2)
        vedge = (self.xs < EDGE_CLR + VIA_R) | (self.xs > W - EDGE_CLR - VIA_R) | (self.ys < EDGE_CLR + VIA_R) | (self.ys > H - EDGE_CLR - VIA_R)
        for L in range(3):
            self.cnt[L][edge] = 2
            self.vcnt[L][vedge] = 2

    def _apply(self, cnt, own, sel, net):
        np = self.np
        free = sel & (own == -1)
        own[free] = net
        cnt[free] = np.maximum(cnt[free], 1)
        other = sel & (own != -1) & (own != net)
        cnt[other] = 2

    def window(self, x0, y0, x1, y1, m):
        i0, i1 = max(0, int((x0 - m) / GRID)), min(self.nx - 1, int((x1 + m) / GRID) + 1)
        j0, j1 = max(0, int((y0 - m) / GRID)), min(self.ny - 1, int((y1 + m) / GRID) + 1)
        return j0, j1 + 1, i0, i1 + 1

    def mark_dist(self, layers, net, bbox, dist_fn, track_m, via_m):
        m = max(track_m, via_m)
        j0, j1, i0, i1 = self.window(*bbox, m)
        X, Y = self.xs[j0:j1, i0:i1], self.ys[j0:j1, i0:i1]
        d = dist_fn(X, Y)
        for L in layers:
            self._apply(self.cnt[L][j0:j1, i0:i1], self.own[L][j0:j1, i0:i1], d <= track_m, net)
            self._apply(self.vcnt[L][j0:j1, i0:i1], self.vown[L][j0:j1, i0:i1], d <= via_m, net)

    def rect(self, layers, net, r, track_m, via_m):
        np = self.np
        def f(X, Y):
            dx = np.maximum(np.maximum(r[0] - X, 0), X - r[2])
            dy = np.maximum(np.maximum(r[1] - Y, 0), Y - r[3])
            return np.hypot(dx, dy)
        self.mark_dist(layers, net, r, f, track_m, via_m)

    def seg(self, layers, net, a, c, track_m, via_m):
        np = self.np
        vx, vy = c[0] - a[0], c[1] - a[1]
        ln2 = vx * vx + vy * vy
        def f(X, Y):
            t = np.clip(((X - a[0]) * vx + (Y - a[1]) * vy) / ln2, 0, 1) if ln2 else 0
            return np.hypot(X - a[0] - t * vx, Y - a[1] - t * vy)
        self.mark_dist(layers, net, (min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1])), f, track_m, via_m)

    def poly(self, layers, net, pts, track_m, via_m):
        np = self.np
        xs_, ys_ = [p[0] for p in pts], [p[1] for p in pts]
        def f(X, Y):
            d = np.full(X.shape, 1e9)
            inside = np.zeros(X.shape, bool)
            n = len(pts)
            for i in range(n):
                a, c = pts[i], pts[(i + 1) % n]
                vx, vy = c[0] - a[0], c[1] - a[1]
                ln2 = vx * vx + vy * vy or 1e-12
                t = np.clip(((X - a[0]) * vx + (Y - a[1]) * vy) / ln2, 0, 1)
                d = np.minimum(d, np.hypot(X - a[0] - t * vx, Y - a[1] - t * vy))
                cond = (a[1] > Y) != (c[1] > Y)
                with np.errstate(divide="ignore", invalid="ignore"):
                    xc = a[0] + (Y - a[1]) * vx / (vy if vy else 1e-12)
                inside ^= cond & (X < xc)
            d[inside] = 0
            return d
        self.mark_dist(layers, net, (min(xs_), min(ys_), max(xs_), max(ys_)), f, track_m, via_m)

    def free(self, L, net):
        return (self.cnt[L] == 0) | ((self.cnt[L] == 1) & (self.own[L] == net))

    def via_free(self, net):
        np = self.np
        out = np.ones((self.ny, self.nx), bool)
        for L in range(3):
            out &= (self.vcnt[L] == 0) | ((self.vcnt[L] == 1) & (self.vown[L] == net))
        return out


def clearances(net, other, item, fine=False):
    """(track margin, via margin) from an item's edge to a new 0.25 mm track centre / 0.6 mm via centre.

    INPUT_POWER nets carry a 0.3 mm class clearance. Fine-pitch pads take no diagonal margin: a 0.5 mm pitch leaves no room for it, and the board DRC is the judge.
    """
    hv = other in HV_NETS and item != "pad"
    clr = HV_CLR if hv else (0.3 if other in ("/ANODE", "/VIN") else ROUTE_CLR)
    if item == "zone":
        clr = max(clr, 0.3)
    extra = 0.0 if fine else DIAG_MARGIN
    return clr + ROUTE_W / 2 + extra, clr + VIA_R + extra


def build_grid(b, geo, netcode):
    G = Grid()
    for p in geo.pads:
        code = netcode.get(p["net"], -2 - len(p["ref"]))
        layers = [0, 1, 2] if p["th"] else ([0] if p["front"] else [1])
        t, v = clearances(None, p["net"], "pad", fine=min(p["rect"][2] - p["rect"][0], p["rect"][3] - p["rect"][1]) <= 0.65)
        G.rect(layers, code, p["rect"], t, v)
        if p["th"]:                                      # hole clearance applies to every net, including the routed net's own via
            G.rect([0, 1, 2], -9, ((p["rect"][0] + p["rect"][2]) / 2, (p["rect"][1] + p["rect"][3]) / 2, (p["rect"][0] + p["rect"][2]) / 2, (p["rect"][1] + p["rect"][3]) / 2), 0.0, 0.0)
    for a, c, half, net, lay in geo.segs:
        t, v = clearances(None, net, "track")
        L = {P.F_Cu: 0, P.B_Cu: 1}.get(lay)
        if L is not None:
            G.seg([L], netcode.get(net, -3), a, c, half + t, half + v)
    for q, net in geo.vias:
        t, v = clearances(None, net, "via")
        code = netcode.get(net, -3)
        G.seg([0, 1, 2], code, q, q, VIA_R + t, max(VIA_R + v, 2 * DRILL_R + HOLE_CLR))
    for z in b.Zones():
        name, net = z.GetZoneName(), z.GetNetname()
        if not name.startswith(("T022_", "T023_")) or name.startswith(YIELDING_ZONES):
            continue
        L = 0 if z.IsOnLayer(P.F_Cu) else (1 if z.IsOnLayer(P.B_Cu) else 2)
        t, v = clearances(None, net, "zone")
        G.poly([L], netcode.get(net, -3), outline_pts(z), t, v)
    for z in b.Zones():                                  # mounting-hole keepouts: no copper of any net
        if z.GetIsRuleArea():
            G.poly([0, 1, 2], -9, outline_pts(z), ROUTE_W / 2 + DIAG_MARGIN, VIA_R + DIAG_MARGIN)
    sw_cells = [r for r in geo.pads if r["net"].startswith(("/SW_PH", "/SW4_PH"))]
    np = G.np
    for r in sw_cells:
        dx = np.maximum(np.maximum(r["rect"][0] - G.xs, 0), G.xs - r["rect"][2])
        dy = np.maximum(np.maximum(r["rect"][1] - G.ys, 0), G.ys - r["rect"][3])
        G.sw = np.maximum(G.sw, np.clip(1 - np.hypot(dx, dy) / SW_KEEP, 0, 1))
        G.sw10 = np.maximum(G.sw10, np.clip(1 - np.hypot(dx, dy) / SENS_KEEP, 0, 1))
    return G


def eroded(m, k):
    """Cells whose k-cell neighbourhood is free: room for a wider track."""
    import numpy as np
    out = m.copy()
    for _ in range(k):
        out[1:, :] &= m[:-1, :]
        out[:-1, :] &= m[1:, :]
        out[:, 1:] &= m[:, :-1]
        out[:, :-1] &= m[:, 1:]
        m = out.copy()
    return out


def dilated(m, k):
    out = m.copy()
    for _ in range(k):
        n_ = out.copy()
        n_[1:, :] |= out[:-1, :]
        n_[:-1, :] |= out[1:, :]
        n_[:, 1:] |= out[:, :-1]
        n_[:, :-1] |= out[:, 1:]
        out = n_
    return out


def astar(G, net, sources, goal, goal_layer=0, sensitive=False, masks=None):
    import heapq
    np = G.np
    free = masks if masks is not None else [G.free(0, net), G.free(1, net)]
    via = G.via_free(net)
    N8 = [(0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    gj, gi = goal
    def h(j, i):
        dx, dy = abs(i - gi), abs(j - gj)
        return (max(dx, dy) + 0.414 * min(dx, dy))
    dist, prev, heap = {}, {}, []
    for (j, i, L) in sources:
        dist[(j, i, L)] = 0.0
        heapq.heappush(heap, (h(j, i), 0.0, j, i, L))
    n = 0
    while heap and n < MAX_EXPAND:
        f0, d0, j, i, L = heapq.heappop(heap)
        if d0 > dist.get((j, i, L), 1e18):
            continue
        n += 1
        if (j, i) == (gj, gi) and L == goal_layer:
            path = [(j, i, L)]
            while path[-1] in prev:
                path.append(prev[path[-1]])
            return path[::-1], n
        for dj, di, w in N8:
            a, c = j + dj, i + di
            if 0 <= a < G.ny and 0 <= c < G.nx and free[L][a, c]:
                lc = SENS_B_COST if (sensitive and L == 1) else LAYER_COST[L]
                nd = d0 + w * lc * (1.0 + 3.0 * float(G.sw[a, c]) + (3.0 * float(G.sw10[a, c]) if sensitive == "far" else 0.0))
                if nd < dist.get((a, c, L), 1e18):
                    dist[(a, c, L)] = nd
                    prev[(a, c, L)] = (j, i, L)
                    heapq.heappush(heap, (nd + h(a, c), nd, a, c, L))
        if via[j, i]:
            k = (j, i, 1 - L)
            vc = SENS_VIA_COST if sensitive else VIA_COST
            if free[1 - L][j, i] and d0 + vc < dist.get(k, 1e18):
                dist[k] = d0 + vc
                prev[k] = (j, i, L)
                heapq.heappush(heap, (dist[k] + h(j, i), dist[k], j, i, 1 - L))
    return None, n


def snap(G, net, xy, L):
    free = G.free(L, net)
    j0, i0 = int(round(xy[1] / GRID)), int(round(xy[0] / GRID))
    for rad in range(0, 6):
        best = None
        for j in range(j0 - rad, j0 + rad + 1):
            for i in range(i0 - rad, i0 + rad + 1):
                if 0 <= j < G.ny and 0 <= i < G.nx and free[j, i]:
                    d = (j * GRID - xy[1]) ** 2 + (i * GRID - xy[0]) ** 2
                    if best is None or d < best[0]:
                        best = (d, j, i)
        if best:
            return best[1], best[2]
    return None


def stub_clear(free, a, c):
    """The short exit stub from the pad axis to its grid cell must stay in free cells too."""
    n = max(1, int(math.dist(a, c) / (GRID / 2)))
    for k in range(n + 1):
        x, y = a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n
        j, i = int(round(y / GRID)), int(round(x / GRID))
        if not (0 <= j < free.shape[0] and 0 <= i < free.shape[1]) or not free[j, i]:
            return False
    return True


def pad_exit(G, net, pin, L):
    """Leave a pad along its long axis (a fine-pitch pad has no sideways room): returns (grid cell, exact axis point) or (None, None)."""
    r = pin[4]
    cx, cy = pin[1]
    w, h = r[2] - r[0], r[3] - r[1]
    free = G.free(L, net)
    dirs = [(1, 0), (-1, 0)] if w >= h else [(0, 1), (0, -1)]
    dirs += [(0, 1), (0, -1)] if w >= h else [(1, 0), (-1, 0)]
    best = None
    for rank, (dx, dy) in enumerate(dirs):
        for k in range(0, 8):
            ex, ey = cx + dx * (w / 2 + 0.05 * k), cy + dy * (h / 2 + 0.05 * k)
            ex, ey = (ex, cy) if dx else (cx, ey)
            for j in range(int(ey / GRID) - 1, int(ey / GRID) + 3):
                for i in range(int(ex / GRID) - 1, int(ex / GRID) + 3):
                    if 0 <= j < G.ny and 0 <= i < G.nx and free[j, i] and stub_clear(free, (ex, ey), (i * GRID, j * GRID)):
                        d = math.hypot(j * GRID - ey, i * GRID - ex) + 0.05 * k + rank * 0.2
                        if best is None or d < best[0]:
                            best = (d, (j, i), (ex, ey))
        if best and rank in (0, 1) and best[0] < 0.5 + rank * 0.2:
            break
    if best is None and min(w, h) <= 0.65:       # fine pitch: the pad axis is the only clear corridor, so walk along it to the first free cell; DRC is the judge
        for rank, (dx, dy) in enumerate(dirs[:2]):
            for k in range(0, 24):
                ex, ey = cx + dx * (w / 2 + 0.05 * k), cy + dy * (h / 2 + 0.05 * k)
                ex, ey = (ex, cy) if dx else (cx, ey)
                j, i = int(round(ey / GRID)), int(round(ex / GRID))
                if 0 <= j < G.ny and 0 <= i < G.nx and free[j, i]:
                    d = 0.05 * k + math.hypot(j * GRID - ey, i * GRID - ex)
                    if best is None or d < best[0]:
                        best = (d, (j, i), (ex, ey))
                    break
    return (best[1], best[2]) if best else (None, None)


def nearest_via(G, net, start):
    """Breadth-first F.Cu search from a pad exit to the nearest cell where a via fits."""
    import collections as c_
    free, via = G.free(0, net), G.via_free(net)
    q, prev = c_.deque([start]), {start: None}
    while q:
        cur = q.popleft()
        if via[cur] and cur != start:
            path = [(cur[0], cur[1], 0)]
            while prev[(path[-1][0], path[-1][1])] is not None:
                u = prev[(path[-1][0], path[-1][1])]
                path.append((u[0], u[1], 0))
            return path[::-1]
        for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx_ = (cur[0] + dj, cur[1] + di)
            if nx_ not in prev and 0 <= nx_[0] < G.ny and 0 <= nx_[1] < G.nx and free[nx_]:
                prev[nx_] = cur
                q.append(nx_)
                if len(prev) > 60000:
                    return None
    return None


def simplify(cells):
    out = [cells[0]]
    for k in range(1, len(cells) - 1):
        a, b, c = out[-1], cells[k], cells[k + 1]
        if a[2] != b[2] or b[2] != c[2] or (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
            out.append(b)
    out.append(cells[-1])
    return out


def step3():
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    geo = Geo(b)
    netcode = {n: i + 1 for i, n in enumerate(sorted({p["net"] for p in geo.pads} | {s_[3] for s_ in geo.segs} | {v[1] for v in geo.vias} | {z.GetNetname() for z in b.Zones()}))}
    G = build_grid(b, geo, netcode)
    pins = {n: [(f"{p['ref']}.{p['pin']}", centre(p), p["front"], p["th"], p["rect"]) for p in geo.pads if p["net"] == n] for n in STEP3_NETS + STEP4_NETS}
    def span(n):
        c = [q[1] for q in pins[n]]
        return (max(x[0] for x in c) - min(x[0] for x in c)) + (max(x[1] for x in c) - min(x[1] for x in c))
    log = {"routed": [], "failed": []}
    prefix_end = {}
    stubs_drawn = set()
    for net, group in STEP3_PREFIX.items():
        for pin, pts in group.items():
            t_track(b, net, P.F_Cu, ROUTE_W, pts)
            for a_, c_ in zip(pts, pts[1:]):
                G.seg([0], netcode[net], a_, c_, ROUTE_W + ROUTE_CLR + DIAG_MARGIN, ROUTE_W / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)
            prefix_end[pin] = pts[-1]
            if net == "/GND":                 # U6.2 is walled in by /ISO_OV if its via waits for --gnd
                t_via(b, net, pts[-1])
                G.seg([0, 1, 2], netcode[net], pts[-1], pts[-1], VIA_R + ROUTE_CLR + ROUTE_W / 2 + DIAG_MARGIN, VIA_R + ROUTE_CLR + VIA_R + DIAG_MARGIN)

    for net, group in STEP3_FIXED.items():
        for pts in group:
            t_track(b, net, P.F_Cu, ROUTE_W, pts)
            for a_, c_ in zip(pts, pts[1:]):
                G.seg([0], netcode[net], a_, c_, ROUTE_W + ROUTE_CLR + DIAG_MARGIN, ROUTE_W / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)

    for net, group in STEP4_B.items():
        for pts in group:
            t_track(b, net, P.B_Cu, ROUTE_W, pts)
            for a_, c_ in zip(pts, pts[1:]):
                G.seg([1], netcode[net], a_, c_, ROUTE_W + ROUTE_CLR + DIAG_MARGIN, ROUTE_W / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)
    for rect_ in STEP4_B_KEEP:
        G.rect([1], -9, rect_, ROUTE_W / 2 + DIAG_MARGIN, VIA_R + DIAG_MARGIN)
    placed_ = {(int(round(x_ / GRID)) * GRID, int(round(y_ / GRID)) * GRID) for g_ in STEP4_VIAS.values() for x_, y_ in g_}
    for net, group in STEP4_VIAS.items():
        for xy in group:
            t_via(b, net, xy)
            G.seg([0, 1, 2], netcode[net], xy, xy, VIA_R + ROUTE_CLR + ROUTE_W / 2 + DIAG_MARGIN, VIA_R + ROUTE_CLR + VIA_R + DIAG_MARGIN)

    for net, group in STEP4_KEEP.items():
        for xy in group:
            G.seg([0, 1, 2], netcode[net], xy, xy, VIA_R + ROUTE_CLR + ROUTE_W / 2 + DIAG_MARGIN, VIA_R + ROUTE_CLR + VIA_R + DIAG_MARGIN)

    def exit_of(q, code, L):
        if q[0] in prefix_end:
            return snap(G, code, prefix_end[q[0]], L), prefix_end[q[0]]
        return pad_exit(G, code, q, L)

    for net in sorted(STEP3_NETS + STEP4_NETS, key=lambda n: (STEP3_FIRST.index(n) if n in STEP3_FIRST else len(STEP3_FIRST), 0 if (n in STEP4_NETS and span(n) < 12.0) else 1, span(n))):   # short local nets take their pad exits before the long nets close them
        if net in STEP3_SKIP or net in STEP4_HOLD:
            continue
        code = netcode[net]
        root = next((q for q in pins[net] if q[0] == STEP3_ROOT.get(net)), pins[net][0])
        done = [root]
        todo = [q for q in pins[net] if q is not root and q[0] not in STEP3_DONE]
        seen = set()
        exits = {}

        def add_src(q):
            L = 1 if (q[3] is False and q[2] is False) or q[0] in STEP4_FORCE_B else 0
            cell, ex = exit_of(q, code, L)
            if cell:
                exits[q[0]] = ex
                seen.add((cell[0], cell[1], L))
            return cell, L
        add_src(done[0])
        for x_, y_, l_ in STEP4_SEED.get(net, ()):
            seen.add((int(round(y_ / GRID)), int(round(x_ / GRID)), l_))
        while todo:
            todo.sort(key=lambda q: min(math.dist(q[1], d[1]) for d in done))
            q = todo.pop(0)
            L = 1 if (q[3] is False and q[2] is False) or q[0] in STEP4_FORCE_B else 0
            cell, ex = exit_of(q, code, L)
            if cell:
                exits[q[0]] = ex
            if not cell or not seen:
                log["failed"].append({"net": net, "pin": q[0], "why": "no free grid cell at the pad"})
                continue
            wide = {}
            if net in AUX_NETS:
                for L_ in (0, 1):
                    wide[L_] = eroded(G.free(L_, code), 1)
                src_ = G.np.zeros((G.ny, G.nx), bool)
                for j_, i_, l_ in seen:
                    src_[j_, i_] = True
                src_[cell[0], cell[1]] = True
                near_ = dilated(src_, 8)
                masks_ = [wide[0] | (G.free(0, code) & near_), wide[1] | (G.free(1, code) & near_)]
            elif net in STEP4_B_NET:
                src_ = G.np.zeros((G.ny, G.nx), bool)
                for j_, i_, l_ in seen:
                    if l_ == 0:
                        src_[j_, i_] = True
                if L == 0:
                    src_[cell[0], cell[1]] = True
                win_ = (G.xs > 98.0) & (G.xs < 111.5) & (G.ys > 30.0) & (G.ys < 38.5)      # the U3/U4 fan-out corridor stays free on F.Cu for the nets that have no B.Cu there
                masks_ = [G.free(0, code) & (dilated(src_, 20) | ~win_), G.free(1, code)]
            else:
                masks_ = None
            path, n = astar(G, code, sorted(seen), cell, L, sensitive=("far" if net in SENS_FAR else net in SENSITIVE), masks=masks_)
            if not path:
                log["failed"].append({"net": net, "pin": q[0], "why": f"no route ({n} expansions)"})
                continue
            pts = simplify(path)
            xy = [(i * GRID, j * GRID, L2) for j, i, L2 in pts]
            net_len = 0.0
            for (x0, y0, L0), (x1, y1, L1) in zip(xy, xy[1:]):
                if L0 != L1:
                    if (x0, y0) not in placed_:
                        t_via(b, net, (x0, y0))
                    G.seg([0, 1, 2], code, (x0, y0), (x0, y0), VIA_R + ROUTE_CLR + ROUTE_W / 2 + DIAG_MARGIN, VIA_R + ROUTE_CLR + VIA_R + DIAG_MARGIN)
                    continue
                if (x0, y0) != (x1, y1):
                    w_ = ROUTE_W
                    if wide and all(wide[L0][int(round(y_ / GRID)), int(round(x_ / GRID))] for x_, y_ in sample([(x0, y0), (x1, y1)], GRID)):
                        w_ = AUX_W
                    t_track(b, net, LAYERS["F"] if L0 == 0 else LAYERS["B"], w_, [(x0, y0), (x1, y1)])
                    net_len += math.dist((x0, y0), (x1, y1))
                    G.seg([L0], code, (x0, y0), (x1, y1), w_ / 2 + ROUTE_W / 2 + ROUTE_CLR + DIAG_MARGIN, w_ / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)
            def pad_stub(pin, end):
                layer = LAYERS["F"] if end[2] == 0 else LAYERS["B"]
                pts_ = [exits[pin[0]], end[:2]] if pin[0] in prefix_end else [pin[1], exits.get(pin[0], pin[1]), end[:2]]
                for a_, c_ in zip(pts_, pts_[1:]):
                    key_ = (net, layer, *sorted(((round(a_[0], 4), round(a_[1], 4)), (round(c_[0], 4), round(c_[1], 4)))))
                    if math.dist(a_, c_) > 1e-6 and key_ not in stubs_drawn:
                        stubs_drawn.add(key_)
                        t_track(b, net, layer, ROUTE_W, [a_, c_])
                        G.seg([end[2]], code, a_, c_, ROUTE_W + ROUTE_CLR + DIAG_MARGIN, ROUTE_W / 2 + ROUTE_CLR + VIA_R + DIAG_MARGIN)
            pad_stub(q, xy[-1])
            src_cell = (xy[0][1], xy[0][0])
            near = min(done, key=lambda d: math.dist(d[1], xy[0][:2]))
            if math.dist(prefix_end.get(near[0], exits.get(near[0], near[1])), xy[0][:2]) < max(0.9, max(near[4][2] - near[4][0], near[4][3] - near[4][1]) / 2 + 0.3) and xy[0][2] == (1 if (near[3] is False and near[2] is False) else 0):
                pad_stub(near, xy[0])          # only on the pad's own layer
            seen.update(path)
            done.append(q)
            log["routed"].append({"net": net, "pin": q[0], "length_mm": round(net_len, 2), "vias": sum(1 for a0, c0 in zip(xy, xy[1:]) if a0[2] != c0[2]), "layers": sorted({"F" if x[2] == 0 else "B" for x in xy})})
    P.ZONE_FILLER(b).Fill(b.Zones())
    P.SaveBoard(str(PCB), b, True)
    with (OUT / "step4-routes.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"grid_mm": GRID, "route_width_mm": ROUTE_W, **log}, f, indent=0, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"routed": len(log["routed"]), "failed": log["failed"], "vias": sum(r["vias"] for r in log["routed"]), "total_mm": round(sum(r["length_mm"] for r in log["routed"]), 1)}, ensure_ascii=False))
    return 0


def step3_audit():
    b = P.LoadBoard(str(PCB))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    D = drc(PCB, OUT / "drc-step4.json")
    now = summary(D)
    base = json.loads((OUT / "step1-baseline.json").read_text(encoding="utf-8"))
    routes = json.loads((OUT / "step4-routes.json").read_text(encoding="utf-8"))
    gnd = json.loads((OUT / "step4-gnd-applied.json").read_text(encoding="utf-8"))
    step2 = json.loads((OUT / "step2-audit.json").read_text(encoding="utf-8"))["after"]
    geo = Geo(b)
    sw_pads = [r for r in geo.pads if r["net"].startswith(("/SW_PH", "/SW4_PH"))]
    sw_zones = [outline_pts(z) for z in b.Zones() if z.GetNetname().startswith("/SW_PH")]
    per = {}
    for n in STEP3_NETS:
        segs = [(a0, c0, L) for a0, c0, _, net, L in geo.segs if net == n]
        pts = [q for a0, c0, _ in segs for q in sample([a0, c0], 0.2)]
        d_pad = min((geo.rect_dist(r["rect"], *q) for r in sw_pads for q in pts), default=None)
        d_zone = min((min(geo.seg_dist(u, v, q) for u, v in zip(o, o[1:] + o[:1])) for o in sw_zones for q in pts), default=None)
        per[n] = {"open_pairs": now["pairs_by_net"].get(n, 0), "track_mm": round(sum(math.dist(a0, c0) for a0, c0, _ in segs), 2), "layers": sorted({"F" if L == P.F_Cu else "B" for _, _, L in segs}),
                  "vias": sum(1 for _, net in geo.vias if net == n), "min_distance_to_sw_pad_mm": round(d_pad, 2) if d_pad is not None else None, "min_distance_to_sw_copper_outline_mm": round(d_zone, 2) if d_zone is not None else None}
    l2 = next(z for z in b.Zones() if z.GetZoneName() == "L2_GND").GetFilledPolysList(P.In1_Cu)
    state = l2_state(b)
    out = {"kicad": P.GetBuildVersion(), "step1_baseline": {k: base[k] for k in ("errors", "unconnected_pairs", "schematic_parity_issues")}, "after": {k: now[k] for k in ("errors", "by_type", "schematic_parity_issues", "unconnected_pairs", "pairs_by_net")},
           "new_opens_vs_step1": {n: now["pairs_by_net"].get(n, 0) - v for n, v in base["pairs_by_net"].items() if now["pairs_by_net"].get(n, 0) > v},
           "new_opens_vs_step2": {n: v - step2["pairs_by_net"].get(n, 0) for n, v in now["pairs_by_net"].items() if v > step2["pairs_by_net"].get(n, 0)},
           "router": {"grid_mm": routes["grid_mm"], "route_width_mm": routes["route_width_mm"], "connections_routed": len(routes["routed"]), "connections_failed": routes["failed"]}, "nets": per,
           "gnd": {"new_vias": gnd["new_vias"], "no_position": gnd["no_position_found"], "searched_paths": sum(1 for c in gnd["candidates"] if c.get("path") == "searched"), "pads_not_on_L2": [k for k, v in state.items() if not v["on_L2"]]}, "l2_islands": l2.OutlineCount()}
    with (OUT / "step4-signal-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: out[k] for k in ("after", "new_opens_vs_step1", "new_opens_vs_step2", "gnd", "l2_islands")} | {"router": {k: out["router"][k] for k in ("connections_routed",)}, "failed": out["router"]["connections_failed"], "nets": {k: (v["open_pairs"], v["track_mm"], v["vias"], v["min_distance_to_sw_pad_mm"]) for k, v in per.items()}}, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------- R-022 Tur 3: reference-net evidence and the board-bound probe map
REF_PAIRS = {"/OVP_REF": ("U8.6", ("U7.3", "R_OCT.1", "C_REF_OUT.1", "TP_OVP_REF.1")), "/OC_REF": ("R_OCB.1", ("U13.3", "U14.3", "R_OCT.2", "TP_OC_REF.1")),
             "/FB": ("U1.16", ("RFB2.1", "RFB1.2")), "/FB_INJ": ("RFB1.1", ("R_INJ.2", "TP_FB_INJ_B.1")), "/COMP": ("U1.15", ("RCOMP.1", "CHF.1", "U2.15", "TP_COMP.1"))}
RETURN_PAIRS = (("U1.17", "R_TRIM.2"), ("U1.17", "CHF.2"), ("U1.17", "CCOMP.2"), ("R_OCB.2", "U13.2"), ("R_OCB.2", "U14.2"), ("C_REF_OUT.2", "U7.2"), ("C_REF_OUT.2", "R_OCB.2"))
SW_BANDS = (2.0, 3.0, 5.0, 10.0)


def inside_poly(o, q):
    hit = False
    for u, v in zip(o, o[1:] + o[:1]):
        if (u[1] > q[1]) != (v[1] > q[1]) and q[0] < u[0] + (q[1] - u[1]) * (v[0] - u[0]) / (v[1] - u[1]):
            hit = not hit
    return hit


def net_paths(geo, net, root, targets):
    """Shortest centre-line path over the net's own copper; T-junctions are split, a via or a pad joins layers at zero length."""
    import heapq
    segs = [s_ for s_ in geo.segs if s_[3] == net]
    vias = [q for q, n_ in geo.vias if n_ == net]
    pads = {f"{p_['ref']}.{p_['pin']}": p_ for p_ in geo.pads if p_["net"] == net}
    key = lambda q: (round(q[0], 3), round(q[1], 3))
    by_layer = collections.defaultdict(set)
    for a0, c0, _, _, lay in segs:
        by_layer[lay].update((key(a0), key(c0)))
    for lay in (P.F_Cu, P.B_Cu):
        by_layer[lay].update(key(q) for q in vias)
    for p_ in pads.values():
        for lay in ((P.F_Cu, P.B_Cu) if p_["th"] else ((P.F_Cu,) if p_["front"] else (P.B_Cu,))):
            by_layer[lay].add(key(centre(p_)))
    adj = collections.defaultdict(list)
    for a0, c0, half, _, lay in segs:
        ln = math.dist(a0, c0)
        if ln == 0:
            continue
        on = sorted((((q[0] - a0[0]) * (c0[0] - a0[0]) + (q[1] - a0[1]) * (c0[1] - a0[1])) / ln, q) for q in by_layer[lay] if Geo.seg_dist(a0, c0, q) <= half + 0.02)
        for (t0, q0), (t1, q1) in zip(on, on[1:]):
            adj[q0].append((q1, t1 - t0, lay))
            adj[q1].append((q0, t1 - t0, lay))
    for p_ in pads.values():
        c_ = key(centre(p_))
        for lay in ((P.F_Cu, P.B_Cu) if p_["th"] else ((P.F_Cu,) if p_["front"] else (P.B_Cu,))):
            for q in by_layer[lay]:
                if q != c_ and Geo.rect_dist(p_["rect"], *q) <= 0.01:
                    adj[c_].append((q, 0.0, None))
                    adj[q].append((c_, 0.0, None))
    src = key(centre(pads[root]))
    dist, prev, heap = {src: 0.0}, {}, [(0.0, src)]
    while heap:
        d0, u = heapq.heappop(heap)
        if d0 > dist[u]:
            continue
        for v, w, lay in adj[u]:
            if d0 + w < dist.get(v, 1e18):
                dist[v] = d0 + w
                prev[v] = (u, lay, w)
                heapq.heappush(heap, (d0 + w, v))
    out = {}
    for t in targets:
        v = key(centre(pads[t]))
        if v not in dist:
            out[t] = {"connected": False}
            continue
        mm = {P.F_Cu: 0.0, P.B_Cu: 0.0}
        seq = []
        while v in prev:
            v, lay, w = prev[v]
            if lay is not None:
                mm[lay] += w
                seq.append(lay)
        out[t] = {"connected": True, "path_mm": round(mm[P.F_Cu] + mm[P.B_Cu], 3), "f_mm": round(mm[P.F_Cu], 3), "b_mm": round(mm[P.B_Cu], 3), "layer_changes": sum(1 for x, y in zip(seq, seq[1:]) if x != y), "straight_mm": round(math.dist(centre(pads[root]), centre(pads[t])), 3)}
    return out


def ref_audit_board(path):
    b = P.LoadBoard(str(path))
    P.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    geo = Geo(b)
    sw_pads = [r for r in geo.pads if r["net"].startswith(("/SW_PH", "/SW4_PH"))]
    sw_zones = [outline_pts(z) for z in b.Zones() if z.GetNetname().startswith(("/SW_PH", "/SW4_PH"))]
    def sw_dist(q):
        d = min(Geo.rect_dist(r["rect"], *q) for r in sw_pads)
        for o in sw_zones:
            d = min(d, 0.0 if inside_poly(o, q) else min(Geo.seg_dist(u, v, q) for u, v in zip(o, o[1:] + o[:1])))
        return d
    l2 = next(z for z in b.Zones() if z.GetZoneName() == "L2_GND")
    l3 = [z for z in b.Zones() if z.IsOnLayer(P.In2_Cu)]
    gnd_vias = [q for q, n_ in geo.vias if n_ == "/GND"]
    out = {"nets": {}, "returns": {}}
    for net, (root, targets) in REF_PAIRS.items():
        segs = [s_ for s_ in geo.segs if s_[3] == net]
        bands = {str(d): 0.0 for d in SW_BANDS}
        mn = (1e9, None)
        f_mm = b_mm = uncovered = 0.0
        gaps = 0
        l3_mm = collections.Counter()
        for a0, c0, half, _, lay in segs:
            ln = math.dist(a0, c0)
            if ln == 0:
                continue
            qs = sample([a0, c0], 0.2)
            dl = ln / len(qs)
            in_gap = False
            for q in qs:
                d = max(0.0, sw_dist(q) - half)
                if d < mn[0]:
                    mn = (d, [round(q[0], 2), round(q[1], 2)])
                for t in SW_BANDS:
                    if d <= t:
                        bands[str(t)] += dl
                if lay == P.F_Cu:
                    if not l2.HitTestFilledArea(P.In1_Cu, kp(*q), 0):
                        uncovered += dl
                        gaps += 0 if in_gap else 1
                        in_gap = True
                    else:
                        in_gap = False
                else:
                    z_ = next((z for z in l3 if z.HitTestFilledArea(P.In2_Cu, kp(*q), 0)), None)
                    l3_mm[z_.GetNetname() if z_ else "(boş)"] += dl
            f_mm += ln if lay == P.F_Cu else 0.0
            b_mm += ln if lay != P.F_Cu else 0.0
        vias = [q for q, n_ in geo.vias if n_ == net]
        out["nets"][net] = {"track_mm": round(f_mm + b_mm, 3), "f_mm": round(f_mm, 3), "b_mm": round(b_mm, 3), "vias": len(vias), "paths_from": root, "paths": net_paths(geo, net, root, targets),
                            "sw_min_edge_mm": round(mn[0], 3), "sw_min_at_d6": mn[1], "track_mm_within_edge_distance_of_sw": {k: round(v, 2) for k, v in bands.items()},
                            "f_samples_without_l2_mm": round(uncovered, 2), "f_l2_gap_runs": gaps, "b_mm_by_adjacent_l3_net": {k: round(v, 2) for k, v in l3_mm.items()},
                            "signal_via_to_nearest_gnd_via_mm": [round(min(math.dist(q, g) for g in gnd_vias), 2) for q in vias]}
    t_ = net_paths(geo, "/COMP", "TP_COMP.1", ("U1.15", "U2.15"))
    u_ = out["nets"]["/COMP"]["paths"]["U2.15"]["path_mm"]
    out["tp_comp_branch_stub_mm"] = round((t_["U1.15"]["path_mm"] + t_["U2.15"]["path_mm"] - u_) / 2, 3)
    pads = {f"{p_['ref']}.{p_['pin']}": p_ for p_ in geo.pads}
    for x, y in RETURN_PAIRS:
        if x not in pads or y not in pads or pads[x]["net"] != "/GND" or pads[y]["net"] != "/GND":
            out["returns"][f"{x}-{y}"] = None
            continue
        u, v = centre(pads[x]), centre(pads[y])
        qs = sample([u, v], 0.25)
        hit = sum(1 for q in qs if l2.HitTestFilledArea(P.In1_Cu, kp(*q), 0))
        out["returns"][f"{x}-{y}"] = {"straight_mm": round(math.dist(u, v), 3), "l2_filled_share_of_straight_line": round(hit / len(qs), 3)}
    return out


def ref_audit():
    res = {"kicad": P.GetBuildVersion(), "method": "Centre-line geometry on the saved board after refill: samples every 0.2 mm, paths over the net's own copper. Geometry only; no coupling, return-current or noise solution.", "after": ref_audit_board(PCB)}
    if "--before" in sys.argv:
        res["before"] = ref_audit_board(sys.argv[sys.argv.index("--before") + 1])
    with (OUT / "step4-ref-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: {n: {x: v[x] for x in ("track_mm", "vias", "sw_min_edge_mm")} for n, v in res[k]["nets"].items()} for k in res if k in ("before", "after")}, ensure_ascii=False))
    return 0


FB_LOOP_ANCHORS = ("U1.16", "U1.15", "RFB2.1", "RFB1.2", "R_TRIM.2", "CHF.2", "RCOMP.1", "CCOMP.2")
ASSIGNED_PROBE_GND = {"TP_COMP": "TP_GND_OC", "TP_OC_REF": "TP_GND_OC", "TP_OVP_REF": "TP_GND_FB", "TP_FB_INJ_A": "TP_GND_FB", "TP_FB_INJ_B": "TP_GND_FB", "TP_OVP_SENSE": "TP_GND_OVP", "TP_OVP_BUS_N": "TP_GND_OVP", "TP_OVP_TRIP_N": "TP_GND_OVP"}    # R-022 Tur 4-7
HIDDEN_PASSIVES = ("RFB1", "RFB2", "R_TRIM", "CHF", "RCOMP", "CCOMP", "CVCC1", "CVDDA1", "RT1", "RBOOT1", "RBOOT2", "CBOOT1", "CBOOT2", "CVDDA2", "RCFG1", "RCFG2", "RIMON2", "RILIM2", "CIN3")


def assembly_map():
    """Readable, board-bound placement list for the passives whose silk reference is hidden (R-022 Tur 5, checked at the T-024 gate)."""
    import csv
    import hashlib
    sha = hashlib.sha256(PCB.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    with (ROOT / "design" / "bom-v2.csv").open(encoding="utf-8", newline="") as f:
        bom = {r["ref"]: r for r in csv.DictReader(f)}
    b = P.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    rows = []
    for ref in HIDDEN_PASSIVES:
        fp, line = fps[ref], bom[ref]
        q = fp.GetPosition()
        pads = {p_.GetNumber(): p_.GetNetname() for p_ in fp.Pads()}
        if fp.GetValue() != line["value"]:
            raise SystemExit(f"{ref}: board value {fp.GetValue()} differs from BOM {line['value']}")
        if fp.Reference().IsVisible():
            raise SystemExit(f"{ref}: silk reference is visible; the map no longer matches the board")
        rows.append({"ref": ref, "value": line["value"], "mpn": line["mpn"], "manufacturer": line["manufacturer"], "footprint": fp.GetFPIDAsString(), "d6_mm": [round(P.ToMM(q.x) - 30, 3), round(115 - P.ToMM(q.y), 3)], "pcb_mm": [round(P.ToMM(q.x), 3), round(P.ToMM(q.y), 3)], "rotation_deg": round(fp.GetOrientationDegrees(), 1), "side": "F" if fp.GetLayer() == P.F_Cu else "B", "pad_nets": pads})
    with (OUT / "assembly-map.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"board": "PDU.kicad_pcb", "board_sha256_lf": sha, "kicad": P.GetBuildVersion(), "bom": "design/bom-v2.csv", "rows": rows}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    fmt = lambda v: f"{v:.3f}".replace(".", ",")
    body = "\n".join(f"| {r['ref']} | {r['value']} | {r['mpn']} | {r['manufacturer']} | `{r['footprint'].split(':')[-1]}` | {fmt(r['d6_mm'][0])} ; {fmt(r['d6_mm'][1])} | {fmt(r['pcb_mm'][0])} ; {fmt(r['pcb_mm'][1])} | {r['rotation_deg']:.0f}° | {r['side']} | " + ", ".join(f"{k}: `{v}`" for k, v in sorted(r["pad_nets"].items())) + " |" for r in rows)
    txt = f"""# T-023 montaj haritası: silk referansı gizli pasifler

**Bu harita yalnız şu kart içeriği için geçerlidir.** `PDU.kicad_pcb` SHA-256 (satır sonu LF): `{sha}`. KiCad {P.GetBuildVersion()}. BOM: `design/bom-v2.csv`. Kart değişirse `--assembly-map` ile yeniden üretin; SHA uyuşmuyorsa bu tabloyu kullanmayın. T-024 imalat kapısı bu eşleşmeyi ister.

Konum, yön, değer ve ağlar karttan betikle alındı; değerler BOM ile karşılaştırıldı. D-006: orijin sol alt, y yukarı. PCB: KiCad pafta koordinatı. Dönme KiCad açısıdır.

| Ref | Değer | MPN | Üretici | Footprint | D-006 x ; y (mm) | PCB x ; y (mm) | Dönme | Yüz | Pad ağları |
|---|---|---|---|---|---|---|---:|---|---|
{body}

## Doğrulanamayanlar

Montaj hattı, yeniden işleme erişimi ve kart üzerinde yerinde tanıma doğrulanmadı. Bu dosya üretici montaj çizimi yerine geçmez.
"""
    (OUT / "assembly-map.md").write_text(txt, encoding="utf-8", newline="\n")
    print(json.dumps({"sha": sha, "rows": len(rows)}, ensure_ascii=False))
    return 0


def probe_map():
    import hashlib
    sha = hashlib.sha256(PCB.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    b = P.LoadBoard(str(PCB))
    rows = []
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        if not ref.startswith("TP_"):
            continue
        p_ = next(iter(fp.Pads()))
        q = p_.GetPosition()
        rows.append({"ref": ref, "net": p_.GetNetname(), "d6_mm": [round(P.ToMM(q.x) - 30, 3), round(115 - P.ToMM(q.y), 3)], "pcb_mm": [round(P.ToMM(q.x), 3), round(P.ToMM(q.y), 3)], "side": "F" if fp.GetLayer() == P.F_Cu else "B", "pad_mm": round(P.ToMM(p_.GetSizeX()), 2), "silk_ref_visible": bool(fp.Reference().IsVisible())})
    rows.sort(key=lambda r: r["ref"])
    gnds = [r for r in rows if r["net"] == "/GND"]
    for r in rows:
        g = min((x for x in gnds if x is not r), key=lambda x: math.dist(x["d6_mm"], r["d6_mm"]), default=None)
        r["nearest_probe_gnd"] = g["ref"] if g else None
        r["nearest_probe_gnd_mm"] = round(math.dist(g["d6_mm"], r["d6_mm"]), 2) if g else None
        if r["ref"] in ASSIGNED_PROBE_GND:
            a_ = next(x for x in gnds if x["ref"] == ASSIGNED_PROBE_GND[r["ref"]])
            r["assigned_probe_gnd"] = a_["ref"]
            r["assigned_probe_gnd_mm"] = round(math.dist(a_["d6_mm"], r["d6_mm"]), 2)
    pads_ = {f"{f.GetReference()}.{q_.GetNumber()}": q_ for f in b.GetFootprints() for q_ in f.Pads()}
    anchor = {k: (round(P.ToMM(pads_[k].GetPosition().x) - 30, 3), round(115 - P.ToMM(pads_[k].GetPosition().y), 3)) for k in FB_LOOP_ANCHORS}
    fb_gnd = next(r for r in rows if r["ref"] == "TP_GND_FB")["d6_mm"]
    fb_loop = {k: round(math.dist(fb_gnd, v), 3) for k, v in anchor.items()}
    out = {"board": "PDU.kicad_pcb", "board_sha256_lf": sha, "kicad": P.GetBuildVersion(), "tp_gnd_fb_to_fb_loop_mm": fb_loop, "rows": rows}
    with (OUT / "probe-map.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    fmt = lambda v: f"{v:.3f}".replace(".", ",")
    line = lambda r: f"| {r['ref']} | `{r['net']}` | {fmt(r['d6_mm'][0])} ; {fmt(r['d6_mm'][1])} | {fmt(r['pcb_mm'][0])} ; {fmt(r['pcb_mm'][1])} | {r['side']} | {str(r['pad_mm']).replace('.', ',')} | {r['nearest_probe_gnd'] or '—'} ({str(r['nearest_probe_gnd_mm']).replace('.', ',')} mm) |"
    head = "| Ref | Ağ | D-006 x ; y (mm) | PCB x ; y (mm) | Yüz | Pad Ø (mm) | En yakın prob GND |\n|---|---|---|---|---|---:|---|\n"
    hidden = [r for r in rows if not r["silk_ref_visible"]]
    txt = f"""# T-023 prob haritası

**Bu harita yalnız şu kart içeriği için geçerlidir.** `PDU.kicad_pcb` SHA-256 (satır sonu LF): `{sha}`. KiCad {P.GetBuildVersion()}. Kart değişirse `--probe-map` ile yeniden üretin; SHA uyuşmuyorsa bu tabloyu kullanmayın.

Koordinatlar pcbnew pad merkezinden betikle alındı. D-006: orijin sol alt, y yukarı. PCB: KiCad pafta koordinatı, D-006 x+30, 115−y. Mesafeler düz çizgidir.

## Silk etiketi gizli test noktaları ({len(hidden)})

{head}{chr(10).join(line(r) for r in hidden)}

## Tüm test noktaları ({len(rows)})

{head}{chr(10).join(line(r) for r in rows)}

## TP_GND_FB ile FB/loop grubu (pad merkezleri, mm)

{chr(10).join(f"- {k}: {str(v).replace('.', ',')}" for k, v in fb_loop.items())}

## Atanmış prob GND

{chr(10).join(f"- {r['ref']} → {r['assigned_probe_gnd']}: {str(r['assigned_probe_gnd_mm']).replace('.', ',')} mm" for r in rows if r.get("assigned_probe_gnd"))}

## Doğrulanamayanlar

Fiziksel prob erişimi ve yerinde tanıma doğrulanmadı. Bu dosya montaj çizimi değildir. Fiziksel test veya üretimden önce basılı kopya kart üzerinde yerinde doğrulanmalıdır.
"""
    (OUT / "probe-map.md").write_text(txt, encoding="utf-8", newline="\n")
    print(json.dumps({"sha": sha, "rows": len(rows), "hidden": [r["ref"] for r in hidden]}, ensure_ascii=False))
    return 0


STEP4_ROLES = {"FB": ("TP_GND_FB.1", ("U1.16", "RCOMP.1", "R_TRIM.2", "TP_FB_INJ_A.1", "TP_FB_INJ_B.1", "TP_OVP_REF.1")), "OC": ("TP_GND_OC.1", ("TP_OC_SENSE1.1", "TP_OC_SENSE2.1", "TP_OC_REF.1", "TP_COMP.1", "U14.2", "U13.2")),
               "OVP/J_OVP": ("TP_GND_OVP.1", ("J_OVP_INJ_BUS.2", "TP_OVP_SENSE.1", "TP_OVP_BUS_N.1", "TP_OVP_TRIP_N.1", "TP_OVP_Q.1", "TP_VSAFE.1", "TP_VOUT.1")), "POWER": ("TP_GND_POWER.1", ("J1.2", "TP_ANODE.1", "TP_VIN.1"))}


LOCAL_PATHS = (("U1.18", "CVDDA1.1"), ("U2.18", "CVDDA2.1"), ("U1.19", "CVCC1.1"), ("U2.19", "CVCC2.1"), ("U1.4", "RBOOT1.2"), ("RBOOT1.1", "CBOOT1.1"), ("CBOOT1.2", "U1.5"), ("U2.4", "RBOOT2.2"), ("RBOOT2.1", "CBOOT2.1"), ("CBOOT2.2", "U2.5"),
               ("U1.14", "RT1.1"), ("U1.13", "RCFG1.1"), ("U2.14", "RT2.1"), ("U2.13", "RCFG2.1"), ("U5.5", "Q1.4"), ("U5.1", "CVCAP.1"), ("U3.15", "CDVDT1.1"), ("U4.15", "CDVDT2.1"), ("U4.8", "RILIM2.1"), ("U3.8", "RILIM1.1"))


def local_path(geo, a_, c_):
    """Shortest copper path between two pads over track centre lines; a via joins its layers. Zones are not traversed."""
    import heapq
    pa, pc = next(q for q in geo.pads if f"{q['ref']}.{q['pin']}" == a_), next(q for q in geo.pads if f"{q['ref']}.{q['pin']}" == c_)
    net = pa["net"]
    edges = collections.defaultdict(list)
    nodes = set()
    key = lambda xy, lay: (round(xy[0], 3), round(xy[1], 3), lay)
    for u_, v_, _, n_, lay in geo.segs:
        if n_ == net:
            k0, k1 = key(u_, lay), key(v_, lay)
            nodes |= {k0, k1}
            edges[k0].append((math.dist(u_, v_), k1))
            edges[k1].append((math.dist(u_, v_), k0))
    vias = [q for q, n_ in geo.vias if n_ == net]
    for q in vias:
        at = [k for k in nodes if math.dist(k[:2], q) < 0.08]
        for k in at:
            for m in at:
                if k != m:
                    edges[k].append((math.dist(k[:2], m[:2]), m))
    lays = {pa["front"]: P.F_Cu, False: P.B_Cu}
    def touching(p_):
        lay_ = P.F_Cu if p_["front"] else P.B_Cu
        return [k for k in nodes if k[2] == lay_ and geo.rect_dist(p_["rect"], k[0], k[1]) < 0.02]
    src, dst = touching(pa), set(touching(pc))
    dist, heap = {}, []
    for k in src:
        dist[k] = 0.0
        heapq.heappush(heap, (0.0, k))
    best = None
    while heap:
        d0, k = heapq.heappop(heap)
        if d0 > dist.get(k, 1e18):
            continue
        if k in dst:
            best = d0
            break
        for w_, m in edges[k]:
            if d0 + w_ < dist.get(m, 1e18):
                dist[m] = d0 + w_
                heapq.heappush(heap, (d0 + w_, m))
    return {"net": net, "path_mm": None if best is None else round(best, 3), "net_vias": len(vias)}


def step4_audit():
    """R-022 Tur 7 evidence: probe GND roles, FRA pads at R_INJ, per-net copper of every routed signal, remaining opens by net."""
    import collections as c_
    b = P.LoadBoard(str(PCB))
    pos = {f"{f.GetReference()}.{q.GetNumber()}": d6(q.GetPosition()) for f in b.GetFootprints() for q in f.Pads()}
    roles = {r: {"gnd": g, "mm": {m: round(math.dist(pos[m], pos[g]), 3) for m in ms}} for r, (g, ms) in STEP4_ROLES.items()}
    fra = {"TP_FB_INJ_A-TP_FB_INJ_B": round(math.dist(pos["TP_FB_INJ_A.1"], pos["TP_FB_INJ_B.1"]), 3), "TP_FB_INJ_A-R_INJ.1": round(math.dist(pos["TP_FB_INJ_A.1"], pos["R_INJ.1"]), 3), "TP_FB_INJ_B-R_INJ.2": round(math.dist(pos["TP_FB_INJ_B.1"], pos["R_INJ.2"]), 3)}
    per = c_.defaultdict(lambda: {"mm": 0.0, "wide_mm": 0.0, "vias": 0})
    for t in b.GetTracks():
        n = t.GetNetname()
        if n not in STEP4_NETS and n not in STEP3_NETS:
            continue
        if t.Type() == P.PCB_VIA_T:
            per[n]["vias"] += 1
        else:
            per[n]["mm"] += P.ToMM(t.GetLength())
            per[n]["wide_mm"] += P.ToMM(t.GetLength()) if t.GetWidth() >= P.FromMM(AUX_W) else 0.0
    per = {k: {x: round(v, 3) for x, v in d.items()} for k, d in sorted(per.items())}
    drc_ = json.loads((OUT / "drc-step4.json").read_text(encoding="utf-8"))
    routes = json.loads((OUT / "step4-routes.json").read_text(encoding="utf-8"))
    pairs = []
    for u in drc_["unconnected_items"]:
        pairs.append([i["description"] for i in u["items"]])
    geo = Geo(b)
    local = {f"{u_}->{v_}": local_path(geo, u_, v_) for u_, v_ in LOCAL_PATHS}
    for row in local.values():
        row["straight_mm"] = None
    for u_, v_ in LOCAL_PATHS:
        local[f"{u_}->{v_}"]["straight_mm"] = round(math.dist(pos[u_], pos[v_]), 3)
    gnd_tp = {r_: pos[r_] for r_ in pos if r_.startswith("TP_GND")}
    gnd_pads = {f"{q_['ref']}.{q_['pin']}": centre(q_) for q_ in geo.pads if q_["net"] == "/GND" and not q_["ref"].startswith(("TP_", "U", "J", "Q"))}
    probe = {}
    for t_ in ("TP_OVP_Q.1", "TP_OC_SENSE1.1"):
        near_ = sorted(gnd_tp, key=lambda k_: math.dist(gnd_tp[k_], pos[t_]))[:2]
        pad_ = min(gnd_pads, key=lambda k_: math.dist(gnd_pads[k_], pos[t_]))
        probe[t_] = {"xy_mm": [round(v_, 3) for v_ in pos[t_]], "nearest_probe_gnd": [[k_, round(math.dist(gnd_tp[k_], pos[t_]), 3)] for k_ in near_], "nearest_gnd_passive_pad": [pad_, round(math.dist(gnd_pads[pad_], pos[t_]), 3)]}
    out = {"kicad": P.GetBuildVersion(), "method": "Pad-centre straight distances and summed track lengths from the saved board; geometry only.", "probe_gnd_roles": roles, "fra_pads": fra, "held_for_hv_rule": list(STEP4_HOLD), "router_failed": routes["failed"], "connections_routed": len(routes["routed"]), "net_copper": per, "open_pairs": pairs, "local_paths_mm": local, "probe_gnd_options": probe}
    critical = {"kicad": out["kicad"], "method": "Layered shortest path over track centre lines and vias (zones are not traversed); not a current-density or SI result.", "local_paths_mm": local}
    with (OUT / "critical-lengths.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(critical, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with (OUT / "signal-route-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump({"kicad": out["kicad"], "open_pairs": pairs, "router_failed": routes["failed"], "connections_routed": len(routes["routed"]), "net_copper": per}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with (OUT / "step4-audit.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"open": len(pairs), "routed": out["connections_routed"], "failed": len(routes["failed"])}, ensure_ascii=False))
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
    if "--step3" in sys.argv:
        sys.exit(step3())
    if "--gnd" in sys.argv:
        sys.exit(gnd_returns())
    if "--audit4" in sys.argv:
        sys.exit(step4_audit())
    if "--audit-ref" in sys.argv:
        sys.exit(ref_audit())
    if "--assembly-map" in sys.argv:
        sys.exit(assembly_map())
    if "--probe-map" in sys.argv:
        sys.exit(probe_map())
    if "--audit3" in sys.argv:
        sys.exit(step3_audit())
    raise SystemExit(__doc__)
