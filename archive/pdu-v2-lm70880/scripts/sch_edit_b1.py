"""T-006 schematic block B1 (input path) — reproducible edit of PDU.kicad_sch with the lossless S-expression tool.

    python scripts/sch_edit_b1.py            # edits PDU.kicad_sch in place (run on a committed tree; revert with git checkout)

Edits (G5 decisions):
  * F1 removed from the board (T-004 / D-001: fuse is off-board in the battery lead): delete the F1 symbol and the VBAT
    label, bridge the two former fuse pin points with a wire -> J1 pin 1 joins /ANODE.
  * MPN property of every B1 part set from design/pdu_v2_spec.yaml (added hidden when missing).
Not changed here: D1 cathode net (spec /ANODE vs schematic /VIN) — pending THINKER decision D-007.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "PDU.kicad_sch"
F1_PIN_POINTS = ((59.69, 365.76), (67.31, 365.76))   # Device:Fuse at (63.5, 365.76) rot 90, pins at +-3.81 mm
B1_REFS = ["J1", "D1", "U5", "Q1", "CIN_U5", "CVCAP", "CBIN1", "CBIN2"] + [f"CIN{i}" for i in range(1, 9)]


def spec_mpn():
    sys.path.insert(0, str(ROOT))
    from analysis.check_consistency import parse_spec
    spec, _ = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    return {r: spec[r]["mpn"] for r in B1_REFS}


def apply(text: str, mpn: dict) -> tuple[str, list]:
    root = ks.parse(text)
    sch = ks.top(root)
    log = []
    f1 = ks.symbol_by_ref(root, "F1")
    if f1 is not None:
        ks.remove_node(sch, f1)
        log.append("F1 symbol removed")
        for lab in ks.labels(sch, "VBAT"):
            ks.remove_node(sch, lab)
            log.append(f"label VBAT at {ks.at_of(lab)} removed")
        anchor = next(sch.children("wire"))
        ks.insert_after(sch, anchor, ks.wire_text(*F1_PIN_POINTS, str(uuid.uuid5(uuid.NAMESPACE_URL, "PDU/T-006/F1-bridge"))))
        log.append(f"wire {F1_PIN_POINTS} added (former F1 pins)")
    for ref, m in mpn.items():
        log.append(f"{ref}.MPN {ks.set_or_add_property(root, ref, 'MPN', m)} = {m}")
    return ks.dumps(root), log


def main() -> int:
    text = SCH.read_bytes().decode("utf-8")
    new, log = apply(text, spec_mpn())
    SCH.write_bytes(new.encode("utf-8"))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
