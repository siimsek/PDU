"""T-021 copper pours and thermal vias (no track routing) — run with KiCad's bundled Python 10.0.7 (D-009):

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_zones.py

Adds to the T-020 board: L2 (In1.Cu) GND plane, L3 (In2.Cu) /VIN, /VOUT, /VSAFE pours and local /GND islands under the
LM70880s, L4 (B.Cu) secondary GND, and via-in-pad arrays on the exposed/drain/source pads. Fills all zones and writes
reports/g5/T-021/zone-audit.json and thermal-area.json. Coordinates: D-006 (origin lower-left, y up).
Via size and counts are VARSAYIM (PCB-HANDOFF §7 DFM 0.3/0.6 via-in-pad filled; manufacturer confirmation AÇIK).
Run on a clean T-020 board (`git checkout -- PDU.kicad_pcb` first): the script only adds items.
"""
from __future__ import annotations

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
    ("L3_VOUT", "/VOUT", "In2", 0, [(24.5, 28.4), (98.0, 28.4), (98.0, 57.3), (24.5, 57.3)]),
    # Q2 source pads face west (bank side): pocket + north strip carries /VSAFE round the drain to the eFuse side
    ("L3_VSAFE", "/VSAFE", "In2", 1, [(90.2, 53.0), (92.0, 53.0), (92.0, 56.7), (98.4, 56.7), (98.4, 8.0), (W - E, 8.0), (W - E, 58.0), (90.2, 58.0)]),
    ("L3_GND_U1", "/GND", "In2", 2, [(45.5, 73.0), (52.5, 73.0), (52.5, 80.0), (45.5, 80.0)]),
    ("L3_GND_U2", "/GND", "In2", 2, [(31.0, 4.0), (38.0, 4.0), (38.0, 11.0), (31.0, 11.0)]),
]
# (ref, pad number, net, nx, ny, pitch x, pitch y) — grid centred on the (largest) copper pad of that number
ARRAYS = [("U1", "30", "/GND", 3, 2, 1.0, 0.8), ("U2", "30", "/GND", 3, 2, 1.0, 0.8),
          ("Q1", "5", "/VIN", 3, 3, 1.2, 1.2), ("Q2", "5", "/VOUT", 3, 3, 1.2, 1.2)]
PAD_VIAS = [("Q2", "1", "/VSAFE"), ("Q2", "2", "/VSAFE"), ("Q2", "3", "/VSAFE")]
THERMAL = {"Q1": ("/VIN", "In2"), "Q2": ("/VOUT", "In2")}


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
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, obj in (("zone-audit.json", {"kicad": P.GetBuildVersion(), "zones": audit, "vias": vias}),
                    ("thermal-area.json", thermal)):
        with (OUT / fn).open("w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(json.dumps({"zones": [(a["zone"], a["islands"], a["fill_area_mm2"]) for a in audit], "vias": len(vias), "thermal": {k: v["connected_fill_area_mm2"] for k, v in thermal.items()}}))
    return 0 if all(v["pass"] for v in thermal.values()) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
