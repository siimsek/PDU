"""T-010 schematic block B5 (common-bus isolator + OVP latch + 5 V protection rail) — reproducible edit.

    python scripts/sch_edit_b5.py      # run on a tree with B1..B3 applied; revert with git checkout -- PDU.kicad_sch

All 30 parts come from design/pdu_v2_spec.yaml; every pin gets a local label with its spec net (no wires), NC pins
get no_connect flags. Placement: free band between the two phase converters (x 165..340 mm, y 180..215 mm, 1.27 grid).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
from sch_place import place_part  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "PDU.kicad_sch"
G = 1.27
ICS = [("U6", "PDU:LM74502HDDFR", 138), ("Q2", "Transistor_FET:CSD19531Q5A", 161), ("U7", "PDU:TLV3601DCKR", 185),
       ("U8", "Reference_Voltage:REF5025AD", 209), ("U9", "PDU:SN74LVC1G74DCUR", 236), ("U10", "PDU:TPS7A1650QDGNRQ1", 264)]
IC_Y = 142 * G
PASSIVES = ["RRAWBL", "R_GS", "C_ISO_VCAP", "C_ISO_VS", "R_OVT", "R_OVB", "C_CMP", "C_REF_IN", "C_REF_OUT", "C_REF_NR",
            "C_LAT", "R_CLR", "C_CLR", "SW1", "R_Q", "R_OV2T", "R_OV2B", "R_EN1", "R_EN2", "C_LDO_IN", "C_LDO_OUT",
            "C_LDO_DELAY", "R_BL5", "R_BLS"]
P_X0, P_DX, P_Y = 130 * G, 12 * G, (158 * G, 169 * G)
B5_REFS = [r for r, *_ in ICS] + PASSIVES


def lib_for(ref: str) -> str:
    if ref == "SW1":
        return "Switch:SW_Push"
    return "Device:R" if ref.startswith("R") else "Device:C"


def apply(text: str, spec: dict) -> tuple[str, list]:
    root = ks.parse(text)
    log = []
    for ref, lib_id, kx in ICS:
        placed = place_part(root, ref, lib_id, (kx * G, IC_Y), spec[ref])
        log.append(f"{ref} {lib_id} at ({kx * G:g}, {IC_Y:g}): {len(placed)} pins labelled")
    for k, ref in enumerate(PASSIVES):
        at = (round(P_X0 + P_DX * (k % 12), 2), P_Y[k // 12])
        placed = place_part(root, ref, lib_for(ref), at, spec[ref])
        log.append(f"{ref} at {at}: {placed}")
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
