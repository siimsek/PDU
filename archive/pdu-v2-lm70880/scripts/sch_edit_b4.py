"""T-009 schematic block B4 (phase over-current trip: INA296A2 + TLV3601 per phase, 3-input AND into the OVP latch).

    python scripts/sch_edit_b4.py      # run after sch_edit_b5.py (B4 nets /P5V_PROT, /OVP_REF, /OVP_BUS_N, /OVP_TRIP_N)

Parts and nets from design/pdu_v2_spec.yaml; label-per-pin placement (no wires). Placement: free band at the bottom
centre of the sheet (x 150..300 mm, y 368..390 mm, 1.27 grid).
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
ICS = [("U11", "PDU:INA296A2QDGKRQ1", 120), ("U13", "PDU:TLV3601DCKR", 142), ("U12", "PDU:INA296A2QDGKRQ1", 164),
       ("U14", "PDU:TLV3601DCKR", 186), ("U15", "74xGxx:74LVC1G11", 208)]
IC_Y = 290 * G
PASSIVES = ["R_OCT", "R_OCB", "C_INA1", "C_INA2", "C_OCC1", "C_OCC2", "C_AND"]
P_X0, P_DX, P_Y = 120 * G, 12 * G, 307 * G
B4_REFS = [r for r, *_ in ICS] + PASSIVES


def apply(text: str, spec: dict) -> tuple[str, list]:
    root = ks.parse(text)
    log = []
    for ref, lib_id, kx in ICS:
        placed = place_part(root, ref, lib_id, (kx * G, IC_Y), spec[ref])
        log.append(f"{ref} {lib_id} at ({kx * G:g}, {IC_Y:g}): {placed}")
    for k, ref in enumerate(PASSIVES):
        at = (round(P_X0 + P_DX * k, 2), P_Y)
        placed = place_part(root, ref, "Device:R" if ref.startswith("R") else "Device:C", at, spec[ref])
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
