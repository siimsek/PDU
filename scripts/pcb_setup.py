"""T-013 PCB setup (no routing) — run with KiCad's bundled Python (pcbnew 10.0.7):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_setup.py [netlist.net]

Rebuilds PDU.kicad_pcb from the schematic netlist (kicad-cli sch export netlist) — reproducible, no GUI:
  * removes the pre-G2 prototype content (72 footprints, 101.6 x 76.2 outline, 2 layers),
  * D-006: 120 x 85 mm Edge.Cuts outline, aux/grid origin at the lower-left corner, 4 copper layers,
  * D-006 §7: 4x M3 NPTH (MountingHole_3.2mm_M3, board-only) at (6,6) (114,6) (6,79) (114,79) + copper keep-out,
  * every netlist component: footprint from the stock/PDU library, Reference/Value/MPN, symbol path (parity),
    exclude-from-BOM attribute, pad nets,
  * rough placement: PCB-HANDOFF §3 groups (scripts/floorplan.py GROUPS) shelf-packed into D-006 §3 regions.
Stackup (thickness/dielectric) is written afterwards by scripts/pcb_stackup.py (stdlib, kicad_sexpr) because the
BOARD_STACKUP class is not exposed to Python.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

import pcbnew as P

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
from floorplan import GROUPS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "PDU.kicad_pcb"
STOCK = Path(os.environ.get("KICAD_FP_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\footprints"))
CUSTOM = ROOT / "hardware" / "lib" / "PDU.pretty"
OUT = ROOT / "reports" / "g5" / "T-013" / "placement.json"

W, H = 120.0, 85.0          # D-006
OX, OY = 30.0, 30.0         # KiCad position of the board's top-left corner (page margin only)
HOLES = [(6, 6), (114, 6), (6, 79), (114, 79)]   # D-006 coordinates (origin lower-left, y up)
HOLE_KEEPOUT_R = 4.0        # VARSAYIM: M3 pan head / washer Ø ~7 mm + margin
GAP = 0.4                   # courtyard gap in rough placement
GAP_BY_GROUP = {"COUT bankası (32× C5750)": 0.15}   # 8 x 4 C5750 grid fits the ~63 x 25 mm strip (D-006 §3)

# D-006 §3 regions (x0, y0, x1, y1) in D-006 coordinates; group names from floorplan.GROUPS.
REGIONS = {   # list of rectangles per group, filled in order
    "Giriş (J1, TVS, ters kutup, CIN)": [(0.5, 47.5, 24, 72), (0.5, 13, 24, 37.5), (15, 38, 24, 47)],
    "Buck faz 1": [(25, 58, 57, 84.5)],
    "Buck faz 2": [(25, 0.5, 57, 27)],
    "COUT bankası (32× C5750)": [(24.5, 28.5, 90, 57)],
    "Buck ortak kontrol (FB/COMP/UV/CFG)": [(58, 58, 75, 84.5)],
    "OVP + OC mantık, REF, mandal, LDO": [(76, 58, 108, 84.5)],
    "Ortak bara ayırıcı": [(90.5, 28.5, 98.5, 57)],
    "eFuse + çıkış konnektörleri": [(99, 37.5, 112.5, 58), (99, 11, 119.5, 27.5), (99, 28.5, 105, 37)],
    "Test noktaları / fixture (D-008)": [(58, 9.5, 98, 27)],
}
# Edge-pinned parts (D-006 §3, PCB-HANDOFF §6-7): ref -> (edge, centre along the edge, rotation deg).
# Micro-Fit 43045 horizontal opens towards -y at 0 deg: 90 deg faces west, 270 deg faces east.
PINNED = {"J1": ("W", 42.5, 90), "J3": ("E", 32.6, 270), "J2": ("E", 46.0, 0), "J_OVP_INJ_BUS": ("S", 78.0, 0)}
EDGE_MARGIN = 0.5


def mm(v: float) -> int:
    return P.FromMM(v)


def kpos(x: float, y: float) -> P.VECTOR2I:
    """D-006 (lower-left origin, y up) -> KiCad board coordinates."""
    return P.VECTOR2I(mm(OX + x), mm(OY + H - y))


def _fields(comp) -> dict:
    """Symbol fields (name -> value) except Footprint; schematic parity compares them with the footprint fields."""
    out = {}
    fl = next(comp.children("fields"), None)
    for f in (fl.children("field") if fl is not None else []):
        name = next(f.children("name")).atoms()[1].value
        vals = [x for x in f.atoms()[1:] if isinstance(x, ks.Atom)]
        if name != "Footprint":
            out[name] = vals[0].value if vals else ""
    return out


def parse_netlist(path: Path):
    root = ks.top(ks.parse(path.read_text(encoding="utf-8")))
    comps, nets = [], {}
    for c in next(root.children("components")).children("comp"):
        val = lambda h: next((n.atoms()[1].value for n in c.children(h) if len(n.atoms()) > 1), "")  # noqa: E731
        props = {next(p.children("name")).atoms()[1].value: (next(p.children("value"), None).atoms()[1].value
                 if next(p.children("value"), None) is not None else "") for p in c.children("property")}
        comps.append({"ref": val("ref"), "value": val("value"), "footprint": val("footprint"),
                      "tstamp": val("tstamps"), "desc": val("description"), "mpn": props.get("MPN", ""), "no_bom": "exclude_from_bom" in props,
                      "dnp": "dnp" in props, "fields": _fields(c)})
    for n in next(root.children("nets")).children("net"):
        name = next(n.children("name")).atoms()[1].value
        for node in n.children("node"):
            nets[(next(node.children("ref")).atoms()[1].value, next(node.children("pin")).atoms()[1].value)] = name
    return comps, nets


_IO = P.PCB_IO_KICAD_SEXPR()


def load_fp(fpid: str) -> P.FOOTPRINT:
    lib, name = fpid.split(":", 1)
    d = CUSTOM if lib == "PDU" else STOCK / f"{lib}.pretty"
    fp = _IO.FootprintLoad(str(d), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    fp.SetFPID(P.LIB_ID(lib, name))
    return fp


def old_items(path: Path) -> int:
    """Top-level items of the board being replaced (reported only). Removing items through SWIG corrupts the type
    table in pcbnew 10.0.7 (later FootprintLoad returns an untyped SwigPyObject), so a new board is built instead."""
    root = ks.top(ks.parse(path.read_text(encoding="utf-8")))
    return sum(1 for c in root.children() if c.head in ("footprint", "gr_line", "gr_rect", "gr_arc", "gr_circle",
                                                          "gr_poly", "segment", "via", "arc", "zone"))


def outline(b: P.BOARD) -> None:
    pts = [(0, 0), (W, 0), (W, H), (0, H)]
    for i in range(4):
        s = P.PCB_SHAPE(b)
        s.SetShape(P.SHAPE_T_SEGMENT)
        s.SetStart(kpos(*pts[i]))
        s.SetEnd(kpos(*pts[(i + 1) % 4]))
        s.SetLayer(P.Edge_Cuts)
        s.SetWidth(mm(0.1))
        b.Add(s)
    ds = b.GetDesignSettings()
    ds.SetAuxOrigin(kpos(0, 0))
    ds.SetGridOrigin(kpos(0, 0))


def holes(b: P.BOARD) -> None:
    for i, (x, y) in enumerate(HOLES, 1):
        fp = load_fp("MountingHole:MountingHole_3.2mm_M3")
        fp.SetReference(f"H{i}")
        fp.SetPosition(kpos(x, y))
        fp.SetAttributes(fp.GetAttributes() | P.FP_BOARD_ONLY | P.FP_EXCLUDE_FROM_BOM | P.FP_EXCLUDE_FROM_POS_FILES)
        b.Add(fp)
        z = P.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetZoneName(f"KEEPOUT_H{i}")
        ls = P.LSET()
        for lay in (P.F_Cu, P.In1_Cu, P.In2_Cu, P.B_Cu):
            ls.AddLayer(lay)
        z.SetLayerSet(ls)
        ol = z.Outline()
        ol.NewOutline()
        for k in range(24):
            a = 2 * math.pi * k / 24
            p = kpos(x + HOLE_KEEPOUT_R * math.cos(a), y + HOLE_KEEPOUT_R * math.sin(a))
            ol.Append(p.x, p.y)
        b.Add(z)


def region_marks(b: P.BOARD) -> None:
    """Group regions as Dwgs.User rectangles + labels (documentation layer, not fabricated)."""
    for g, (x0, y0, x1, y1) in ((g, r) for g, rs in REGIONS.items() for r in rs):
        r = P.PCB_SHAPE(b)
        r.SetShape(P.SHAPE_T_RECT)
        r.SetStart(kpos(x0, y1))
        r.SetEnd(kpos(x1, y0))
        r.SetLayer(P.Dwgs_User)
        r.SetWidth(mm(0.15))
        b.Add(r)
        t = P.PCB_TEXT(b)
        t.SetText(g.split(" (")[0])
        t.SetLayer(P.Dwgs_User)
        t.SetTextSize(P.VECTOR2I(mm(1.2), mm(1.2)))
        t.SetTextThickness(mm(0.15))
        t.SetHorizJustify(P.GR_TEXT_H_ALIGN_LEFT)
        t.SetPosition(kpos(x0 + 0.5, y1 - 1.2))
        b.Add(t)


def courtyard_box(fp: P.FOOTPRINT):
    """(w, h, dx, dy): courtyard bbox size and offset of the anchor from the bbox top-left, mm, at rotation 0."""
    poly = fp.GetCourtyard(P.F_CrtYd)
    bb = poly.BBox() if poly.OutlineCount() else fp.GetBoundingBox(False)
    pos = fp.GetPosition()
    return (P.ToMM(bb.GetWidth()), P.ToMM(bb.GetHeight()), P.ToMM(pos.x - bb.GetX()), P.ToMM(pos.y - bb.GetY()))


def pin(box, edge: str, c: float):
    """Anchor (D-006 coords) putting the courtyard bbox against `edge`, centred at `c` along it."""
    w, h, dx, dy = box
    if edge in ("W", "E"):
        left = EDGE_MARGIN if edge == "W" else W - EDGE_MARGIN - w
        return left + dx, c + h / 2 - dy
    top = EDGE_MARGIN + h if edge == "S" else H - EDGE_MARGIN
    return c - w / 2 + dx, top - dy


def pack_multi(items, rects, gap):
    out, rest = {}, dict(items)
    for r in rects:
        pos, over = pack(rest, r, gap)
        out.update(pos)
        rest = {k: rest[k] for k in over}
    return out, sorted(rest)


def pack(items, region, gap=GAP):
    """Shelf packing, tallest first, rows from the region's top edge. Returns {ref: (x, y)} anchors, overflow refs."""
    x0, y0, x1, y1 = region
    out, over = {}, []
    cx, top, row_h = x0, y1, 0.0
    for ref, (w, h, dx, dy) in sorted(items.items(), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0])):
        if cx + w > x1 + 1e-6:
            cx, top, row_h = x0, top - row_h - gap, 0.0
        if top - h < y0 - 1e-6 or w > x1 - x0:
            over.append(ref)
            continue
        out[ref] = (cx + dx, top - dy)       # D-006 coords of the anchor (bbox top-left = (cx, top))
        cx += w + gap
        row_h = max(row_h, h)
    return out, over


def main(argv) -> int:
    netlist = Path(argv[1]) if len(argv) > 1 else ROOT / "reports" / "g5" / "T-013" / "netlist.net"
    comps, pinnet = parse_netlist(netlist)
    removed = old_items(PCB)
    b = P.CreateEmptyBoard()
    b.SetCopperLayerCount(4)
    outline(b)
    holes(b)
    region_marks(b)
    netinfo = {}
    for name in sorted(set(pinnet.values())):
        ni = P.NETINFO_ITEM(b, name)
        b.Add(ni)
        netinfo[name] = ni
    fps, unmatched_pads = {}, []
    for c in comps:
        fp = load_fp(c["footprint"])
        fp.SetReference(c["ref"])
        fp.SetValue(c["value"])
        for name, value in c["fields"].items():   # MPN, Manufacturer, Datasheet, Description ... (parity)
            fp.SetField(name, value)
            fld = fp.GetField(name)
            if fld is not None and name not in ("Reference", "Value"):
                fld.SetVisible(False)
        fp.SetPath(P.KIID_PATH("/" + c["tstamp"]))
        fp.SetSheetname("/")
        fp.SetSheetfile("PDU.kicad_sch")
        attr = fp.GetAttributes()
        if c["no_bom"]:
            attr |= P.FP_EXCLUDE_FROM_BOM
        if c["dnp"]:
            attr |= P.FP_DNP
        fp.SetAttributes(attr)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if not num:
                continue
            name = pinnet.get((c["ref"], num))
            if name is None:
                unmatched_pads.append(f"{c['ref']}.{num}")
                continue
            pad.SetNet(netinfo[name])
        fps[c["ref"]] = fp
    groups = {g: {} for g in REGIONS}
    ungrouped, placed = [], {}
    for ref, (edge, c, rot) in PINNED.items():
        fps[ref].SetOrientationDegrees(rot)
        fps[ref].BuildCourtyardCaches()
        placed[ref] = pin(courtyard_box(fps[ref]), edge, c)
    for ref, fp in fps.items():
        if ref in PINNED:
            continue
        g = next((g for g, rx in GROUPS if re.match(rx, ref)), None)
        if g is None:
            ungrouped.append(ref)
            g = "OVP + OC mantık, REF, mandal, LDO"
        groups[g][ref] = courtyard_box(fp)
    overflow = {}
    for g, items in groups.items():
        pos, over = pack_multi(items, REGIONS[g], GAP_BY_GROUP.get(g, GAP))
        placed.update(pos)
        if over:
            overflow[g] = over
    for ref, fp in fps.items():
        if ref in placed:
            fp.SetPosition(kpos(*placed[ref]))
        b.Add(fp)
    b.BuildConnectivity()
    P.SaveBoard(str(PCB), b, True)   # skip settings: PDU.kicad_pro is written by pcb_rules.py
    res = {"generator": "scripts/pcb_setup.py", "netlist": netlist.relative_to(ROOT).as_posix(),
           "removed_items": removed, "board_mm": [W, H], "copper_layers": b.GetCopperLayerCount(),
           "pinned": PINNED, "holes": HOLES, "hole_keepout_r_mm": HOLE_KEEPOUT_R, "footprints": len(fps), "nets": len(netinfo),
           "regions": REGIONS, "groups": {g: sorted(v) for g, v in groups.items()}, "ungrouped": ungrouped,
           "overflow": overflow, "pads_without_netlist_pin": unmatched_pads,
           "positions_d006": {r: [round(x, 3), round(y, 3)] for r, (x, y) in sorted(placed.items())}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: res[k] for k in ("removed_items", "copper_layers", "footprints", "nets", "ungrouped",
                                          "overflow", "pads_without_netlist_pin")}, ensure_ascii=False))
    return 1 if overflow else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
