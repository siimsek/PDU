"""T-008 schematic block B3 (output capacitor bank) — COUT 8 -> 32 (G4 B4: 32x C5750X7S2A226M280KB).

    python scripts/sch_edit_b3.py      # run on a tree where B1+B2 are applied; revert with git checkout -- PDU.kicad_sch

COUT9..COUT32 are clones of COUT8 placed on a free 3 x 8 grid (top-left of the A2 sheet, 1.27 mm grid), each
connected by local labels VOUT (pin 1) and GND (pin 2) — same nets as COUT1..8. Value/Footprint/MPN from the spec.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
from sch_edit_b2 import clone_resistor as clone_symbol, label_text  # noqa: E402  (generic Device:* clone)

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "PDU.kicad_sch"
X0, DX = 171.45, 12.7          # columns (free area top-centre, clear of title and notes)
ROWS = (27.94, 43.18, 58.42)    # symbol centres; pins at +-3.81 mm
NEW = [f"COUT{i}" for i in range(9, 33)]


def apply(text: str, spec: dict) -> tuple[str, list]:
    root = ks.parse(text)
    sch = ks.top(root)
    log = []
    for k, ref in enumerate(NEW):
        if ks.symbol_by_ref(root, ref) is not None:
            continue
        at = (round(X0 + DX * (k % 8), 2), ROWS[k // 8])
        clone_symbol(root, sch, "COUT8", ref, at, 0)
        pins = ks.pin_points(sch, root, ref)
        anchor = next(sch.children("label"))
        ks.insert_after(sch, anchor, label_text("VOUT", pins["1"], f"{ref}-VOUT"))
        ks.insert_after(sch, anchor, label_text("GND", pins["2"], f"{ref}-GND"))
        s = spec[ref]
        ks.set_property(root, ref, "Value", s["value"])
        ks.set_property(root, ref, "Footprint", s["footprint"])
        ks.set_or_add_property(root, ref, "MPN", s["mpn"])
    log.append(f"{len(NEW)} capacitors COUT9..COUT32 at x {X0}..{X0 + 7 * DX}, rows {ROWS}")
    for i in range(1, 9):                       # existing bank: spec MPN/footprint
        ref = f"COUT{i}"
        ks.set_property(root, ref, "Footprint", spec[ref]["footprint"])
        ks.set_or_add_property(root, ref, "MPN", spec[ref]["mpn"])
    return ks.dumps(root), log


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from analysis.check_consistency import parse_spec
    spec, _ = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    new, log = apply(SCH.read_bytes().decode("utf-8"), spec)
    SCH.write_bytes(new.encode("utf-8"))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
