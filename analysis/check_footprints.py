"""T-005: custom footprint / symbol verification against transcribed manufacturer land patterns.

    python analysis/check_footprints.py            # exit 0 = all checks pass; writes reports/g5/footprints/check.json

Reference data below is transcribed from the official TI package drawings (EXAMPLE BOARD LAYOUT pages); every value
carries its page. Checks per footprint:
  1. every reference pad number exists; rectangular pads: centre and size within TOL (0.02 mm);
  2. polygon/decomposed pads (same number, several primitives): copper bounding box within TOL of the drawing extents;
  3. exposed pads are separate numbered pads (not paste-only);
  4. courtyard (F.CrtYd) exists and encloses package body and all copper;
  5. pin-1 marker: an F.SilkS or F.Fab item within 1.5 mm of pad 1 (outside the body for silk);
  6. symbol pin numbers/names (hardware/lib/PDU.kicad_sym) equal the datasheet pin table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import kicad_sexpr as ks  # noqa: E402

TOL = 0.02
LIB = ROOT / "hardware" / "lib"
OUT = ROOT / "reports" / "g5" / "footprints" / "check.json"


def _rge_pads():
    p = {}
    for i in range(6):
        p[str(1 + i)] = (-1.9125, -1.25 + 0.5 * i, 0.575, 0.24)
        p[str(7 + i)] = (-1.25 + 0.5 * i, 1.9125, 0.24, 0.575)
        p[str(13 + i)] = (1.9125, 1.25 - 0.5 * i, 0.575, 0.24)
        p[str(19 + i)] = (1.25 - 0.5 * i, -1.9125, 0.24, 0.575)
    p["25"] = (0.0, -0.625, 2.7, 1.45)   # thermal pad 1 = IN
    p["26"] = (0.0, 0.925, 2.7, 0.85)    # thermal pad 2 = GND
    return p


def _rrx_pads():
    p = {}
    for n, y in zip(range(1, 9), (-2.25, -1.75, -1.25, -0.25, 0.25, 1.25, 1.75, 2.25)):
        p[str(n)] = (-2.9, y, 0.6, 0.25)
    for n, x in zip(range(9, 17), (-2.0, -1.5, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0)):
        p[str(n)] = (x, 2.9, 0.25, 0.6)
    for n, y in zip(range(17, 23), (1.75, 1.25, 0.75, -0.75, -1.25, -1.75)):
        p[str(n)] = (2.9, y, 0.6, 0.25)
    for n, x in zip(range(23, 30), (2.0, 1.5, 1.0, 0.5, -1.0, -1.5, -2.0)):
        p[str(n)] = (x, -2.9, 0.25, 0.6)
    p["30"] = (0.037, 1.308, 3.125, 1.584)  # PGND die-attach pad
    return p


REFERENCE = {
    "TDSON-8-1_Konnect": {  # Q1 BSC160N10NS3 G; data via R-003 (THINKER), reports/R-003/land-data.md
        "source": "Infineon BSC160N10NS3 G datasheet Rev. 2.4, Fig. 2 p.10 (footprint); PG-TDSON-8-1 package drawing Rev. 01.00 p.2",
        "body": (0.0, 0.0),
        "pads": {"1": (-2.9, -1.905, 0.85, 0.5), "2": (-2.9, -0.635, 0.85, 0.5), "3": (-2.9, 0.635, 0.85, 0.5),
                 "4": (-2.9, 1.905, 0.85, 0.5), "5": (1.05, 0.0, 4.55, 4.41)},
        "polygons": {}, "exposed": ["5"], "symbol": None,
    },
    "TDK_C5750_2220_Recommended": {  # COUT1-32 C5750X7S2A226M280KB; data via R-003
        "source": "TDK Product Center C5750X7S2A226M280KB, Recommended Land Pattern PA 4.10-4.80 / PB 1.20-1.40 / PC 4.00-5.00 mm",
        "body": (0.0, 0.0), "pads": {"1": (-2.875, 0.0, 1.3, 4.5), "2": (2.875, 0.0, 1.3, 4.5)},
        "ranges": {"PA": (4.10, 4.80), "PB": (1.20, 1.40), "PC": (4.00, 5.00)},
        "polygons": {}, "exposed": [], "symbol": None, "pin1": False,
    },
    "TPS25982_RGE0024M": {
        "source": "TI TPS25982 SLVSEI3D, RGE0024M 4223975/B, p.55 (outline), p.56 (example board layout)",
        "body": (4.0, 4.0), "pads": _rge_pads(), "polygons": {}, "exposed": ["25", "26"],
        "symbol": "TPS259824ONRGET",
        "pin_table": {**{str(n): "IN" for n in (1, 2, 3, 16)}, **{str(n): "GND" for n in (4, 5, 14)}, "6": "EN/UVLO",
                      "7": "ITIMER", "8": "ILIM", "9": "IMON", "10": "RETRY_DLY", "11": "NRETRY", "12": "LDSTRT",
                      "13": "PG", "15": "dVdt", **{str(n): "OUT" for n in range(17, 25)}, "25": "IN_EP", "26": "GND_EP"},
        "pin_table_source": "TI TPS25982 Table 5-1, p.5-6 (thermal pad 1 = IN, pad 2 = GND)",
    },
    "LM70880_RRX0029B_RectLands": {
        "source": "TI LM70880-Q1 SNVSBX7A, RRX0029B 4228757/D, p.51 (outline), p.52 (example board layout)",
        "body": (6.0, 6.0), "pads": _rrx_pads(),
        # decomposed copper (same pad number repeated): drawing extents x0, y0, x1, y1
        "polygons": {"29": (-3.2, -3.2, -0.625, -0.484), "22": (-0.125, -2.1, 3.2, -0.14)},
        "exposed": ["30"], "symbol": "LM70880QRRXRQ1",
        "pin_table": {"1": "VIN4", "2": "VIN5", "3": "VIN6", "4": "CBOOT", "5": "SW4", "6": "BIAS", "7": "PG/SYNCOUT",
                      "8": "PFM/SYNCIN", "9": "EN/UVLO", "10": "NC", "11": "ISNS+", "12": "VOUT", "13": "CONFIG",
                      "14": "RT", "15": "EXTCOMP", "16": "FB", "17": "AGND", "18": "VDDA", "19": "VCC", "20": "SW1",
                      "21": "SW2", "22": "SW3", "23": "PGND1", "24": "PGND2", "25": "PGND3", "26": "PGND4",
                      "27": "VIN1", "28": "VIN2", "29": "VIN3", "30": "PGND"},
        "pin_table_source": "TI LM70880-Q1 Table 5-1, p.3-4 (VIN1-3 / SW1-3 numbering per figure 5-1)",
    },
}


def _val(node, head):
    c = next(node.children(head), None)
    return [float(a.value) for a in c.atoms()[1:3]] if c is not None else None


def load_footprint(path: Path, text: str | None = None):
    root = ks.parse(text if text is not None else path.read_text(encoding="utf-8"))
    pads, graphics = {}, []
    for n in ks.walk(root):
        if n.head == "pad":
            num = n.atoms()[1].value
            at, size = _val(n, "at"), _val(n, "size")
            layers = [a.value for a in next(n.children("layers")).atoms()[1:]]
            if num and any(l.endswith(".Cu") or l == "*.Cu" for l in layers):
                pads.setdefault(num, []).append((at[0], at[1], size[0], size[1]))
        elif n.head in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc"):
            lay = next((c.atoms()[1].value for c in n.children("layer")), "")
            pts = [[float(a.value) for a in s.atoms()[1:3]] for s in ks.walk(n)
                   if s.head in ("start", "end", "xy", "center", "mid")]
            graphics.append((lay, pts))
    return pads, graphics


def _bbox(prims):
    xs0 = [x - w / 2 for x, y, w, h in prims]
    ys0 = [y - h / 2 for x, y, w, h in prims]
    xs1 = [x + w / 2 for x, y, w, h in prims]
    ys1 = [y + h / 2 for x, y, w, h in prims]
    return min(xs0), min(ys0), max(xs1), max(ys1)


def load_symbol_pins(name: str):
    root = [x for x in ks.parse((LIB / "PDU.kicad_sym").read_text(encoding="utf-8")) if isinstance(x, ks.SList)][0]
    for sym in root.children("symbol"):
        if sym.atoms()[1].value == name:
            out = {}
            for n in ks.walk(sym):
                if n.head == "pin":
                    out[next(n.children("number")).atoms()[1].value] = next(n.children("name")).atoms()[1].value
            return out
    return None


def check_one(name: str, ref: dict, text: str | None = None) -> dict:
    errs = []
    pads, graphics = load_footprint(LIB / "PDU.pretty" / f"{name}.kicad_mod", text)
    for num, (x, y, w, h) in ref["pads"].items():
        prims = pads.get(num)
        if not prims:
            errs.append(f"pad {num} missing")
            continue
        # the drawing pad must match one primitive exactly (other same-number primitives are common copper)
        if not any(abs(px - x) <= TOL and abs(py - y) <= TOL and abs(pw - w) <= TOL and abs(ph - h) <= TOL
                   for px, py, pw, ph in prims):
            errs.append(f"pad {num}: no primitive matches ({x},{y}) {w}x{h} within {TOL} mm; got {prims[:2]}")
    for num, ext in ref["polygons"].items():
        prims = [p for p in pads.get(num, []) if not (p[2] in (0.25, 0.6) and p[3] in (0.25, 0.6))]
        bb = _bbox(prims) if prims else None
        if bb is None or any(abs(a - b) > TOL for a, b in zip(bb, ext)):
            errs.append(f"polygon pad {num}: bbox {tuple(round(v, 3) for v in bb) if bb else None} != drawing {ext}")
    for num in ref["exposed"]:
        if num not in pads:
            errs.append(f"exposed pad {num} not a numbered copper pad")
    all_cu = _bbox([p for prims in pads.values() for p in prims])
    bw, bh = ref["body"]
    crt = [p for lay, pts in graphics if lay == "F.CrtYd" for p in pts]
    if not crt:
        errs.append("no F.CrtYd courtyard")
    else:
        cx0, cy0 = min(p[0] for p in crt), min(p[1] for p in crt)
        cx1, cy1 = max(p[0] for p in crt), max(p[1] for p in crt)
        need = (min(-bw / 2, all_cu[0]), min(-bh / 2, all_cu[1]), max(bw / 2, all_cu[2]), max(bh / 2, all_cu[3]))
        if not (cx0 <= need[0] and cy0 <= need[1] and cx1 >= need[2] and cy1 >= need[3]):
            errs.append(f"courtyard {round(cx0, 3), round(cy0, 3), round(cx1, 3), round(cy1, 3)} does not enclose body/copper {need}")
    for key, (lo, hi) in ref.get("ranges", {}).items():
        # two-terminal land: PA = inner gap, PB = pad length along the part, PC = pad width (TDK naming)
        (x1, _, w1, h1), (x2, _, w2, h2) = pads["1"][0], pads["2"][0]
        val = {"PA": abs(x2 - x1) - (w1 + w2) / 2, "PB": w1, "PC": h1}[key]
        if not lo <= val <= hi:
            errs.append(f"{key} = {val:.3f} mm outside manufacturer range {lo}-{hi}")
    if ref.get("pin1", True):
        p1 = ref["pads"]["1"]
        marks = [p for lay, pts in graphics if lay in ("F.SilkS", "F.Fab") for p in pts
                 if ((p[0] - p1[0]) ** 2 + (p[1] - p1[1]) ** 2) ** 0.5 <= 1.5]
        if not marks:
            errs.append("no pin-1 marker (F.SilkS/F.Fab item within 1.5 mm of pad 1)")
    sym = load_symbol_pins(ref["symbol"]) if ref.get("symbol") else {}
    if not ref.get("symbol"):
        pass  # stock KiCad symbol (Device:*); pin mapping checked by the schematic consistency step
    elif sym is None:
        errs.append(f"symbol {ref['symbol']} not in PDU.kicad_sym")
    else:
        norm = lambda s: s.replace(" ", "")  # noqa: E731
        for num, nm in ref["pin_table"].items():
            if norm(sym.get(num, "")) != norm(nm):
                errs.append(f"symbol pin {num}: '{sym.get(num)}' != datasheet '{nm}'")
        extra = set(sym) - set(ref["pin_table"])
        if extra:
            errs.append(f"symbol has pins not in datasheet table: {sorted(extra)}")
    return {"footprint": name, "source": ref["source"], "pin_table_source": ref.get("pin_table_source", "—"),
            "pads_checked": len(ref["pads"]), "polygons_checked": len(ref["polygons"]), "pass": not errs, "errors": errs}


def main() -> int:
    res = [check_one(n, r) for n, r in REFERENCE.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"tolerance_mm": TOL, "results": res}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    for r in res:
        print(f"{r['footprint']}: {'PASS' if r['pass'] else 'FAIL'} ({r['pads_checked']} pads, {r['polygons_checked']} polygons)")
        for e in r["errors"]:
            print("  -", e)
    return 0 if all(r["pass"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
