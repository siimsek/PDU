"""T-020 detailed placement (no routing) — run with KiCad's bundled Python (10.0.7):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_place.py

Moves footprints of the T-013 board and repositions Reference texts; nets, values, footprints, outline, holes, stackup
and rules are untouched. Coordinates are D-006 (origin lower-left, y up). Critical parts have explicit positions
(PCB-HANDOFF §3); the rest are shelf-packed per list in `SLOTS`, each box reserving room for its refdes.
Edge-pinned connectors (T-013) and H1-H4 do not move.
"""
from __future__ import annotations

import json
import os
import math
import re
import sys
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "PDU.kicad_pcb"
OUT = ROOT / "reports" / "g5" / "T-020"
sys.path.insert(0, str(Path(__file__).resolve().parent))

W, H, OX, OY = 120.0, 85.0, 30.0, 30.0
TEXT_H, TEXT_T = 0.8, 0.12      # rules: min_text_height 0.8, min_text_thickness 0.08
GAP = 0.45
EDGE_SILK = 0.7
HOLES = [(6, 6), (114, 6), (6, 79), (114, 79)]
HOLE_KEEP = 4.2

# ref -> (x, y, rot|None). Hot loops: CIN column on the LM70880 VIN-PGND edge (HANDOFF §3.2).
FIXED = {
    "U1": (49.0, 76.5, 180), "L1": (37.8, 76.5, 180), "RS1": (35.0, 67.6, None),
    "U2": (34.5, 7.5, 0), "L2": (45.5, 8.5, None), "RS2": (46.5, 16.6, None),
    "D1": (6.0, 51.0, None), "Q1": (17.0, 51.0, None), "U5": (19.5, 42.5, None),
}
HOT = {"U1": ["CIN1", "CIN2", "CIN3", "CIN4"], "U2": ["CIN5", "CIN6", "CIN7", "CIN8"]}
# R-015: CIN layouts, offsets (dx, dy, rotation) relative to U1 at 180 deg; U2 is the same layout turned 180 deg.
# Rotation 180 = /VIN pad east, /GND pad west; 270 = /VIN pad north, /GND pad south.
# West (SW pads 20-22, L1) and north (control pins 9-16) of U1 carry no VIN/PGND pads; board bottom is excluded by D-006.
CIN_VARIANTS = {
    "A_tek_sutun": [(0, -5.59, 180), (0, -9.13, 180), (0, -12.67, 180), (0, -16.21, 180)],
    "B_2x2_guney": [(-2.45, -5.59, 180), (2.45, -5.59, 180), (-2.45, -9.13, 180), (2.45, -9.13, 180)],
    "C_guney_dogu_yan": [(0, -5.59, 180), (0, -9.13, 180), (5.55, -3.2, 270), (9.1, -3.2, 270)],
    "D_guney_dogu_alt": [(0, -5.59, 180), (0, -9.13, 180), (4.25, -6.25, 270), (7.8, -6.25, 270)],
}
CIN_VARIANT = os.environ.get("PDU_CIN_VARIANT", "C_guney_dogu_yan")
PINNED = {"J1", "J2", "J3", "J_OVP_INJ_BUS", "H1", "H2", "H3", "H4"}

SLOTS = [
    # (rectangles, ref regex) — first match wins; rectangles filled in order
    ([(44.7, 80.7, 59.5, 84.2)], r"^(CVCC1|CVDDA1|RT1)$"),                 # U1 north side (control side, away from SW)
    ([(53.2, 75.9, 63.0, 80.3)], r"^(CBOOT1|RBOOT1)$"),                   # U1 pin 4 side
    ([(25.0, 58.0, 45.0, 65.2)], r"^(U11|C_INA1|U13|C_OCC1)$"),           # next to RS1, >= 10 mm from SW1 (HANDOFF 5b)
    ([(25.0, 0.5, 39.0, 3.7)], r"^(CVDDA2|RT2)$"),                  # U2 south side
    ([(37.1, 14.2, 42.0, 19.0)], r"^CVCC2$"),
    ([(25.0, 13.5, 30.6, 27.0)], r"^(CBOOT2|RBOOT2)$"),                    # U2 pin 4 side
    ([(37.2, 19.2, 57.0, 27.0)], r"^(U12|C_INA2|U14|C_OCC2)$"),           # next to RS2, >= 10 mm from SW2
    ([(0.5, 64.0, 24.0, 72.0)], r"^(CIN_U5|CVCAP|CBIN\d)$"),
    ([(0.5, 29.0, 24.0, 37.5)], r"^(TP_ANODE|TP_VIN|TP_GATE.*|TP_GND_POWER)$"),
    ([(63.5, 58.0, 75.0, 84.2)], r"^(RCFG\d|RSYNC|RFB\d|R_INJ|R_TRIM|RCOMP|CCOMP|CHF|RUV\d)$"),
    ([(24.5, 28.5, 90.0, 57.0)], r"^(COUT\d+|RRAWBL)$"),
    ([(90.5, 28.5, 98.5, 57.0)], r"^(U6|Q2|R_GS|C_ISO_.*)$"),
    ([(76.0, 58.0, 108.0, 84.2)], r"^(R_OV.*|U7|U8|U9|U10|U15|C_AND|R_OC[TB]|C_CMP|C_REF_.*|C_LAT|R_CLR|C_CLR|SW1|R_Q|R_EN\d|C_LDO_.*|R_BL5|R_BLS)$"),
    ([(99.0, 37.5, 112.5, 58.0), (99.0, 11.0, 119.5, 27.5), (99.0, 28.5, 105.0, 37.0), (99.0, 0.7, 109.0, 10.7)],
     r"^(U3|U4|RILIM\d|RIMON\d|CDVDT\d|CEFIN\d|CEFOUT\d|RPG\d.*|D_REV\d|D2|D3|REN\d)$"),
    ([(58.0, 10.8, 98.0, 27.0), (0.5, 13.0, 24.0, 28.5), (58.0, 0.7, 66.5, 10.5), (89.8, 0.7, 98.0, 10.5), (0.5, 55.0, 24.0, 63.5)], r"^(TP_.*|JP_EN_BUCK)$"),
]
TIGHT = {r"^(COUT\d+|RRAWBL)$": 0.15}


def kpos(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY + H - y))


def box_mm(bb):
    return P.ToMM(bb.GetLeft()), P.ToMM(bb.GetTop()), P.ToMM(bb.GetRight()), P.ToMM(bb.GetBottom())


def courtyard(fp):
    fp.BuildCourtyardCaches()
    poly = fp.GetCourtyard(P.F_CrtYd)
    bb = poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False)
    pos = fp.GetPosition()
    return P.ToMM(bb.GetWidth()), P.ToMM(bb.GetHeight()), P.ToMM(pos.x - bb.GetX()), P.ToMM(pos.y - bb.GetY())


def text_size(ref: str):
    """Approximate refdes extent (stroke font), mm; the placer re-measures with KiCad before committing."""
    return max(1.0, len(ref) * TEXT_H * 0.92), TEXT_H + 0.6


def pack(items, rects, gap):
    """Tallest-first shelves. items: {ref: (w, h, dx, dy, box_w, box_h)}. Anchors in D-006; part sits at the box bottom."""
    out, rest = {}, dict(items)
    for x0, y0, x1, y1 in rects:
        cx, top, row, left = x0, y1, 0.0, {}
        for ref, it in sorted(rest.items(), key=lambda kv: (-kv[1][5], -kv[1][4], kv[0])):
            w, h, dx, dy, bw, bh = it
            if cx + bw > x1 + 1e-6:
                cx, top, row = x0, top - row - gap, 0.0
            if top - bh < y0 - 1e-6 or bw > x1 - x0 + 1e-6:
                left[ref] = it
                continue
            px = cx + (bw - w) / 2                  # courtyard centred in the box; refdes row above it
            out[ref] = (px + dx, top - (bh - h) - dy)
            cx += bw + gap
            row = max(row, bh)
        rest = left
    return out, sorted(rest)


def main() -> int:
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    b = P.LoadBoard(str(PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    before = {r: fps[r].GetPosition() for r in fps}
    placed, overflow = {}, {}

    for ref, (x, y, rot) in FIXED.items():
        if rot is not None:
            fps[ref].SetOrientationDegrees(rot)
        placed[ref] = (x, y)
    for ic, caps in HOT.items():
        x, y, rot = FIXED[ic]
        sign = 1 if rot == 180 else -1                  # U2 = U1 layout turned 180 deg
        for c, (dx, dy, r) in zip(caps, CIN_VARIANTS[CIN_VARIANT]):
            fps[c].SetOrientationDegrees((r + (0 if rot == 180 else 180)) % 360)
            placed[c] = (x + sign * dx, y + sign * dy)

    for ref, (x, y) in placed.items():
        fps[ref].SetPosition(kpos(x, y))
    for rects, rx in SLOTS:
        refs = [r for r in fps if re.match(rx, r) and r not in placed and r not in PINNED]
        tight = TIGHT.get(rx)
        items = {}
        for r in refs:
            w, h, dx, dy = courtyard(fps[r])
            tw, th = text_size(r)
            big = min(w, h) >= 4.0                  # refdes fits on the body of large parts
            items[r] = (w, h, dx, dy, w if (big or tight) else max(w, tw), h if (big or tight) else h + th)
        pos, over = pack(items, rects, tight if tight is not None else GAP)
        for r, (x, y) in pos.items():
            fps[r].SetPosition(kpos(x, y))
            placed[r] = (x, y)
        if over:
            overflow[rx] = over
    missing = [r for r in fps if r not in placed and r not in PINNED]

    # refdes placement: obstacles are copper pads, footprint silk, already placed text, edge and hole keep-outs
    obst = []
    for f in fps.values():
        for pad in f.Pads():
            obst.append(box_mm(pad.GetBoundingBox()))
        for g in f.GraphicalItems():
            if g.GetLayer() != P.F_SilkS:
                continue
            if g.GetShape() in (P.SHAPE_T_RECT, P.SHAPE_T_POLY):   # outline only: the interior stays usable for the refdes
                l_, t_, r_, b_ = box_mm(g.GetBoundingBox())
                obst += [(l_, t_, r_, t_ + 0.2), (l_, b_ - 0.2, r_, b_), (l_, t_, l_ + 0.2, b_), (r_ - 0.2, t_, r_, b_)]
            else:
                obst.append(box_mm(g.GetBoundingBox()))
    holes_k = [(OX + x, OY + H - y) for x, y in HOLES]
    x_lo, x_hi, y_lo, y_hi = OX + EDGE_SILK, OX + W - EDGE_SILK, OY + EDGE_SILK, OY + H - EDGE_SILK

    def free(b_):
        l, t, r, bt = b_
        if l < x_lo or r > x_hi or t < y_lo or bt > y_hi:
            return False
        if any(l < hr + 0.12 and r > hl - 0.12 and t < hb + 0.12 and bt > ht - 0.12 for hl, ht, hr, hb in obst):
            return False
        for hx, hy in holes_k:
            if max(l - hx, hx - r, 0) ** 2 + max(t - hy, hy - bt, 0) ** 2 < HOLE_KEEP ** 2:
                return False
        return True

    labels, unplaced = {}, []
    order = sorted(fps, key=lambda r: (min(courtyard(fps[r])[:2]), r))
    for ref in order:
        f = fps[ref]
        t = f.Reference()
        t.SetVisible(True)
        t.SetLayer(P.F_SilkS)
        t.SetTextSize(P.VECTOR2I(P.FromMM(TEXT_H), P.FromMM(TEXT_H)))
        t.SetTextThickness(P.FromMM(TEXT_T))
        t.SetHorizJustify(P.GR_TEXT_H_ALIGN_CENTER)
        t.SetVertJustify(P.GR_TEXT_V_ALIGN_CENTER)
        poly = f.GetCourtyard(P.F_CrtYd)
        cl, ct, cr, cb = box_mm(poly.BBox() if poly.OutlineCount() else f.GetBoundingBox(False))
        cx, cy = (cl + cr) / 2, (ct + cb) / 2
        chosen = None
        tw, th = text_size(ref)
        cands = [(cx, cy, 0), (cx, cy, 90)] if min(cr - cl, cb - ct) >= 4.0 else []
        for ext in (0.0, 0.3, 0.7, 1.2, 1.8, 2.5, 3.3, 4.2, 5.2, 6.5, 8.0):
            for ang in (0, 90):
                ax, ay = (tw, th) if ang == 0 else (th, tw)
                cands += [(cx, ct - ay / 2 - 0.1 - ext, ang), (cx, cb + ay / 2 + 0.1 + ext, ang),
                          (cr + ax / 2 + 0.1 + ext, cy, ang), (cl - ax / 2 - 0.1 - ext, cy, ang)]
                for s_ in (-1, 1):
                    cands += [(cx + s_ * ax / 2, ct - ay / 2 - 0.1 - ext, ang), (cx + s_ * ax / 2, cb + ay / 2 + 0.1 + ext, ang)]
        for x, y, ang in cands:
            t.SetPosition(P.VECTOR2I(P.FromMM(x), P.FromMM(y)))
            t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))
            bx = box_mm(t.GetBoundingBox())
            if free(bx):
                chosen = (x, y, ang, bx)
                break
        if chosen is None:
            unplaced.append(ref)
            continue
        x, y, ang, bx = chosen
        t.SetPosition(P.VECTOR2I(P.FromMM(x), P.FromMM(y)))
        t.SetTextAngle(P.EDA_ANGLE(float(ang), P.DEGREES_T))
        obst.append(bx)
        labels[ref] = {"x": round(x - OX, 3), "y_d006": round(OY + H - y, 3), "angle": ang,
                       "dist_from_part_mm": round(math.dist((x, y), (cx, cy)), 2)}

    b.BuildConnectivity()
    P.SaveBoard(str(PCB), b, True)

    def d006(f):
        p = f.GetPosition()
        return [round(P.ToMM(p.x) - OX, 3), round(OY + H - P.ToMM(p.y), 3)]

    def pad(ref, num):
        p = next(x for x in fps[ref].Pads() if x.GetNumber() == num).GetPosition()
        return (P.ToMM(p.x), P.ToMM(p.y))

    pos = {r: d006(fps[r]) for r in sorted(fps)}

    def edges(pd):
        return box_mm(pd.GetBoundingBox())

    def gap(a_, b_):
        return math.hypot(max(a_[0] - b_[2], b_[0] - a_[2], 0.0), max(a_[1] - b_[3], b_[1] - a_[3], 0.0))

    def ctr(e):
        return ((e[0] + e[2]) / 2, (e[1] + e[3]) / 2)

    hot_loop = {"variant": CIN_VARIANT, "basis": "HESAP: edge gaps cap /VIN pad - nearest IC /VIN pad + cap /GND pad - nearest IC PGND pad 23-26; "
                "bbox of the four pad centres; not a routed loop"}
    for ic, caps in HOT.items():
        v_ic = [edges(x) for x in fps[ic].Pads() if x.GetNetname() == "/VIN"]
        g_ic = [edges(x) for x in fps[ic].Pads() if x.GetNumber() in ("23", "24", "25", "26")]
        rows = []
        for c in caps:
            cv = edges(next(x for x in fps[c].Pads() if x.GetNetname() == "/VIN"))
            cg = edges(next(x for x in fps[c].Pads() if x.GetNetname() == "/GND"))
            nv, ng = min(v_ic, key=lambda e: gap(cv, e)), min(g_ic, key=lambda e: gap(cg, e))
            pts = [ctr(cv), ctr(cg), ctr(nv), ctr(ng)]
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            rows.append({"cap": c, "vin_gap_mm": round(gap(cv, nv), 3), "gnd_gap_mm": round(gap(cg, ng), 3),
                         "path_mm": round(gap(cv, nv) + gap(cg, ng), 3),
                         "bbox_mm2": round((max(xs) - min(xs)) * (max(ys) - min(ys)), 2),
                         "center_mm": round(math.dist(pos[ic], pos[c]), 2)})
        hot_loop[ic] = {"caps": rows, "path_sum_mm": round(sum(r["path_mm"] for r in rows), 3),
                        "path_max_mm": max(r["path_mm"] for r in rows), "bbox_sum_mm2": round(sum(r["bbox_mm2"] for r in rows), 2)}
    metrics = {
        "U6.GATE-Q2.G_pad_mm": None, "CIN_center_to_IC_mm": {
            ic: [round(math.dist(pos[ic], pos[c]), 2) for c in caps] for ic, caps in HOT.items()},
        "RS_to_INA_center_mm": {"RS1-U11": round(math.dist(pos["RS1"], pos["U11"]), 2), "RS2-U12": round(math.dist(pos["RS2"], pos["U12"]), 2)},
        "INA_to_comparator_mm": {"U11-U13": round(math.dist(pos["U11"], pos["U13"]), 2), "U12-U14": round(math.dist(pos["U12"], pos["U14"]), 2)},
        "L_center_to_IC_mm": {"L1-U1": round(math.dist(pos["L1"], pos["U1"]), 2), "L2-U2": round(math.dist(pos["L2"], pos["U2"]), 2)},
        "D1_to_J1_mm": round(math.dist(pos["D1"], pos["J1"]), 2),
    }
    gate = {"U6": None, "Q2": None}
    for r in gate:
        for p_ in fps[r].Pads():
            if p_.GetNetname() == "/ISO_GATE":
                gate[r] = (P.ToMM(p_.GetPosition().x), P.ToMM(p_.GetPosition().y))
    metrics["U6.GATE-Q2.G_pad_mm"] = round(math.dist(gate["U6"], gate["Q2"]), 2)
    moved = sum(1 for r in fps if fps[r].GetPosition() != before[r])
    res = {"generator": "scripts/pcb_place.py", "kicad": P.GetBuildVersion(), "footprints": len(fps), "moved": moved,
           "overflow": overflow, "missing": missing, "unplaced_refdes": unplaced, "metrics": metrics, "hot_loop": hot_loop,
           "positions_d006": pos, "refdes": labels}
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "placement.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    far = sorted(((v["dist_from_part_mm"], k) for k, v in labels.items()), reverse=True)[:5]
    print(json.dumps({k: res[k] for k in ("kicad", "moved", "overflow", "missing", "unplaced_refdes", "metrics")} | {"far": far}, ensure_ascii=False))
    return 1 if overflow or missing or unplaced else 0


if __name__ == "__main__":
    sys.exit(main())
