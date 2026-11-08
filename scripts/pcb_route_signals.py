"""T-023 signal routing (D-012) — KiCad's bundled Python 10.0.7 (D-009).

Step 1 (D-012, read-only for PDU.kicad_pcb):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_route_signals.py --step1

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
        self.keep = [z for z in b.Zones() if z.GetZoneName().startswith("T022_") and z.GetNetname() != "/GND"]

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
        for a in g[1:]:
            near = min(g[:g.index(a)], key=lambda c: math.dist(centre(by[a]), centre(by[c])))
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


if __name__ == "__main__":
    if "--step1" in sys.argv:
        sys.exit(step1())
    raise SystemExit(__doc__)
