"""T-017: generate custom schematic symbols (hardware/lib/PDU.kicad_sym) from datasheet pin tables.

    python scripts/make_symbols.py          # adds/replaces the symbols below in hardware/lib/PDU.kicad_sym

Pin tables were read from the rendered datasheet pages (BUILDER, 2026-11-07); THINKER R-008 verifies them independently.
Each symbol: rectangle body, pins on the left (inputs) and right (outputs/supplies), 2.54 mm pitch, 2.54 mm pin length.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "hardware" / "lib" / "PDU.kicad_sym"

# name: (datasheet + page, footprint, [(number, name, type, side)]) ; side L/R
SYMBOLS = {
    "INA296A2QDGKRQ1": ("TI INA296A-Q1 SBOSA32D Table 5-1 p.2 (DGK)", "Package_SO:VSSOP-8_3x3mm_P0.65mm", [
        ("8", "IN+", "input", "L"), ("1", "IN-", "input", "L"), ("7", "REF1", "input", "L"), ("3", "REF2", "input", "L"),
        ("6", "VS", "power_in", "R"), ("5", "OUT", "output", "R"), ("4", "NC", "passive", "R"), ("2", "GND", "power_in", "R")]),
    "TLV3601DCKR": ("TI TLV3601 SNOSDB1E Table 5-1 p.3 (DCK 5-pin)", "Package_TO_SOT_SMD:SOT-353_SC-70-5", [
        ("3", "IN+", "input", "L"), ("4", "IN-", "input", "L"),
        ("5", "VCC", "power_in", "R"), ("1", "OUT", "output", "R"), ("2", "VEE", "power_in", "R")]),
    "SN74LVC1G74DCUR": ("TI SN74LVC1G74 SCES794G Pin Functions p.4 (DCU)", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", [
        ("2", "D", "input", "L"), ("1", "CLK", "input", "L"), ("7", "~{PRE}", "input", "L"), ("6", "~{CLR}", "input", "L"),
        ("8", "VCC", "power_in", "R"), ("5", "Q", "output", "R"), ("3", "~{Q}", "output", "R"), ("4", "GND", "power_in", "R")]),
    "LM74502HDDFR": ("TI LM74502H-Q1 Pin Functions (DDF SOT-23-8)", "Package_TO_SOT_SMD:TSOT-23-8", [
        ("5", "VS", "power_in", "L"), ("1", "EN/UVLO", "input", "L"), ("7", "OV", "input", "L"), ("3", "NC", "no_connect", "L"),
        ("4", "VCAP", "passive", "R"), ("6", "GATE", "output", "R"), ("8", "SRC", "input", "R"), ("2", "GND", "power_in", "R")]),
    "TPS7A1650QDGNRQ1": ("TI TPS7A16-Q1 SBVS188E Table 5-1 p.3 (DGN; thermal pad -> GND recommended)",
                         "Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm", [
        ("8", "IN", "power_in", "L"), ("5", "EN", "input", "L"), ("7", "DELAY", "passive", "L"), ("6", "NC", "no_connect", "L"),
        ("1", "OUT", "power_out", "R"), ("3", "PG", "open_collector", "R"), ("2", "FB/NC", "passive", "R"), ("4", "GND", "power_in", "R"),
        ("9", "EP", "passive", "R")]),
}


def symbol_text(name: str, src: str, fp: str, pins) -> str:
    left = [p for p in pins if p[3] == "L"]
    right = [p for p in pins if p[3] == "R"]
    n = max(len(left), len(right))
    h = 2.54 * (n + 1)
    w = 10.16 if name.startswith(("TLV", "SN74")) else 12.7
    top = h / 2
    out = [f'  (symbol "{name}"', '    (pin_names (offset 1.016))', '    (exclude_from_sim no)', '    (in_bom yes)',
           '    (on_board yes)',
           f'    (property "Reference" "U" (at 0 {top + 2.54:g} 0) (effects (font (size 1.27 1.27))))',
           f'    (property "Value" "{name}" (at 0 {-top - 2.54:g} 0) (effects (font (size 1.27 1.27))))',
           f'    (property "Footprint" "{fp}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           '    (property "Datasheet" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           f'    (property "Description" "{src}" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))',
           f'    (symbol "{name}_0_1"',
           f'      (rectangle (start {-w / 2:g} {top:g}) (end {w / 2:g} {-top:g}) (stroke (width 0.254) (type default)) (fill (type background)))',
           '    )', f'    (symbol "{name}_1_1"']
    for side, lst in (("L", left), ("R", right)):
        for k, (num, pname, typ, _) in enumerate(lst):
            y = top - 2.54 * (k + 1)
            x, ang = (-w / 2 - 2.54, 0) if side == "L" else (w / 2 + 2.54, 180)
            out.append(f'      (pin {typ} line (at {x:g} {y:g} {ang}) (length 2.54)'
                       f' (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    out += ['    )', '  )']
    return "\n".join(out)


def main() -> int:
    text = LIB.read_bytes().decode("utf-8")
    root = ks.parse(text)
    lib = ks.top(root)
    for name, (src, fp, pins) in SYMBOLS.items():
        old = next((s for s in lib.children("symbol") if s.atoms()[1].value == name), None)
        if old is not None:
            ks.remove_node(lib, old)
        last = list(lib.children("symbol"))[-1]
        ks.insert_after(lib, last, symbol_text(name, src, fp, pins).strip(), indent="\n  ")
        print("symbol", name, len(pins), "pins")
    LIB.write_bytes(ks.dumps(root).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
