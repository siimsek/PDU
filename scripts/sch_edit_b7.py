"""T-012 schematic block B7 — D-008 test pads / fixture pads / solder jumper, sheet notes and title block.

    python scripts/sch_edit_b7.py      # run with B1..B6 applied; revert with git checkout -- PDU.kicad_sch

* 36 TestPoint symbols + J_OVP_INJ_BUS (Conn_01x02) + JP_EN_BUCK (SolderJumper_2_Open), in_bom = no
  (PCB-only, decisions/D-008-test-points.md), labelled pins (no wires).
* Sheet notes rewritten to the G5 design (old notes described the pre-G2 board: F1 on board, eFuse OVP 16.9 V).
* Title block: IDA PDU, date, revision G5.
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
TP_ROWS = [((285, 15), (44, 52)), ((20, 12), (60, 66))]   # (x0 grid, dx grid), (row y grid, row y grid); clear of notes/titles
NOTES = {
    "GUC AKISI:": "GUC AKISI: F1 (kart disi) -> J1 -> U5/Q1 -> VIN -> U1 + U2 -> VOUT 11 V\\n"
                  "VOUT -> Q2 ayirici -> VSAFE -> U3 -> J2/O1  |  U4 -> J3/S2E\\n"
                  "Ayni net adi tasiyan etiketler elektriksel olarak baglidir.",
    "O1 KORUMASI TAMAMLANMADI": "O1 KORUMASI: ORTAK BARA AYIRICI (G2-G5)",
    "O1 giris araligi": "O1 giris araligi 5-12 V (T3 resmi sayfa, D-002); hedef anlik tepe <= 12,0 V.\\n"
                        "Koruma: Q2/U6 ayirici + hassas OVP (U7/U8/U9) + faz asiri akim (U11-U15).\\n"
                        "Kabul: BENCH T5c/T5g tezgah olcumu (simulasyon fiziksel kanit degildir).\\n"
                        "F1 kart disi: Eaton PV-10A10F + CHPV1U (D-001).",
    "PROTOTIP:": "PROTOTIP: sema G5 betikleriyle uretildi (scripts/sch_edit_b*.py, spec: design/pdu_v2_spec.yaml); fiziksel test yok.\\n"
                 "Davranissal SPICE gecisleri donanim koruma, termal, SOA veya dongu kararliligi onayi degildir.",
}


def set_text(node, value: str) -> None:
    a = node.atoms()[1]
    node[node.index(a)] = ks.Atom('"' + value.replace('"', "'") + '"')   # value already uses KiCad \n escapes


def apply(text: str, spec: dict) -> tuple[str, list]:
    root = ks.parse(text)
    sch = ks.top(root)
    log = []
    tps = [r for r in spec if r.startswith("TP_")]
    for k, ref in enumerate(tps):
        (x0, dx), ys = TP_ROWS[k // 18]
        row, col = divmod(k % 18, 9)
        at = ((x0 + dx * col) * G, ys[row] * G)
        place_part(root, ref, "Connector:TestPoint", at, spec[ref], in_bom=False)
    log.append(f"{len(tps)} test points placed (in_bom no)")
    place_part(root, "J_OVP_INJ_BUS", "Connector_Generic:Conn_01x02", (292 * G, 62 * G), spec["J_OVP_INJ_BUS"], in_bom=False)
    place_part(root, "JP_EN_BUCK", "Jumper:SolderJumper_2_Open", (312 * G, 62 * G), spec["JP_EN_BUCK"], in_bom=False)
    log.append("J_OVP_INJ_BUS, JP_EN_BUCK placed (in_bom no)")
    for t in sch.children("text"):
        v = t.atoms()[1].value
        for key, new in NOTES.items():
            if v.startswith(key):
                set_text(t, new)
                log.append(f"note updated: {key}")
    if next(sch.children("title_block"), None) is None:
        paper = next(sch.children("paper"))
        ks.insert_after(sch, paper, '(title_block\n\t\t(title "IDA PDU - 6S LiPo -> 11 V, 2 faz buck + ortak bara ayirici")\n'
                                    '\t\t(date "2026-11-07")\n\t\t(rev "G5")\n\t\t(company "siimsek/PDU")\n'
                                    '\t\t(comment 1 "Uretici: scripts/sch_edit_b1..b7.py; spec design/pdu_v2_spec.yaml")\n\t)')
        log.append("title block added")
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
