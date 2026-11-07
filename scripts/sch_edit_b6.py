"""T-011 schematic block B6 (eFuses and output ports) — reproducible edit of PDU.kicad_sch.

    python scripts/sch_edit_b6.py      # run with B1..B5 applied; revert with git checkout -- PDU.kicad_sch

* U3/U4 IN islands (IN pins + CEFIN) and REN1 top: label VOUT -> VSAFE (common-bus isolator output, G2/G3).
* D_REV1/D_REV2 (SS34, eFuse OUT -> VSAFE reverse path, R16) placed with labelled pins.
* Values / footprints / MPNs of every B6 part from the spec (RILIM 182/300 ohm, CEFOUT 1206, D2/D3 SMC,
  J2 Molex 46015-0206 footprint, U3/U4 TPS259824LNRGER).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
from sch_place import place_part  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "PDU.kicad_sch"
B6_REFS = ["U3", "RILIM1", "RIMON1", "CDVDT1", "CEFIN1", "CEFOUT1", "RPG1", "RPG1B", "D_REV1", "D2", "U4", "RILIM2",
           "RIMON2", "CDVDT2", "CEFIN2", "CEFOUT2", "RPG2", "RPG2B", "D_REV2", "D3", "REN1", "REN2", "J3", "J2"]
NUMERIC = re.compile(r"^[0-9.]+[pnumkMR]?$")
NEW_AT = {"D_REV1": (394 * 1.27, 32 * 1.27), "D_REV2": (410 * 1.27, 32 * 1.27)}


def _on(p, a, b, t=0.01):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs(x1 - x2) < t:
        return abs(x - x1) < t and min(y1, y2) - t <= y <= max(y1, y2) + t
    if abs(y1 - y2) < t:
        return abs(y - y1) < t and min(x1, x2) - t <= x <= max(x1, x2) + t
    return False


def island_labels(sch, start):
    wires = []
    for w in sch.children("wire"):
        xy = [(float(a.atoms()[1].value), float(a.atoms()[2].value)) for a in next(w.children("pts")).children("xy")]
        wires.append((xy[0], xy[-1]))
    seen, todo, segs = set(), [start], []
    while todo:
        p = todo.pop()
        for i, (a, b) in enumerate(wires):
            if i not in seen and (_on(p, a, b) or (abs(p[0] - a[0]) < 0.01 and abs(p[1] - a[1]) < 0.01)):
                seen.add(i)
                segs.append((a, b))
                todo += [a, b]
    return [n for n in sch.children("label") if any(_on(ks.at_of(n), a, b) for a, b in segs)]


def apply(text: str, spec: dict) -> tuple[str, list]:
    root = ks.parse(text)
    sch = ks.top(root)
    log = []
    for ref in ("U3", "U4"):
        start = ks.pin_points(sch, root, ref)["1"]
        for lab in island_labels(sch, start):
            if lab.atoms()[1].value == "VOUT":
                ks.set_label_text(lab, "VSAFE")
                log.append(f"{ref} IN island label VOUT -> VSAFE at {ks.at_of(lab)}")
    pt = ks.pin_points(sch, root, "REN1")["1"]
    for kind, name, node in ks.items_at(sch, pt):
        if kind == "label" and name == "VOUT":
            ks.set_label_text(node, "VSAFE")
            log.append(f"REN1.1 label VOUT -> VSAFE at {pt}")
    for ref, at in NEW_AT.items():
        placed = place_part(root, ref, "Device:D_Schottky", at, spec[ref])
        log.append(f"{ref} at {at}: {placed}")
    for ref in B6_REFS:
        s = spec[ref]
        sym = ks.symbol_by_ref(root, ref)
        old = {p.atoms()[1].value: p.atoms()[2].value for p in sym.children("property")}
        if old.get("MPN") and old["MPN"] != s["mpn"]:
            for extra in ("Specification", "TCR", "Tolerance", "Manufacturer"):
                ks.remove_property(root, ref, extra)
            ks.set_property(root, ref, "Datasheet", "")
        if NUMERIC.match(s["value"]):
            ks.set_property(root, ref, "Value", s["value"])
        ks.set_property(root, ref, "Footprint", s["footprint"])
        ks.set_or_add_property(root, ref, "MPN", s["mpn"])
    if ks.symbol_by_ref(root, "#FLG05") is None:      # /VSAFE drives U3/U4 IN power pins (Q2 source is passive)
        from sch_edit_b2 import clone_resistor as clone_symbol, label_text
        at = (430 * 1.27, 32 * 1.27)
        clone_symbol(root, sch, "#FLG03", "#FLG05", at, 0)
        pin = ks.pin_points(sch, root, "#FLG05")["1"]
        ks.insert_after(sch, next(sch.children("label")), label_text("VSAFE", pin, "FLG05-VSAFE"))
        log.append(f"PWR_FLAG #FLG05 on VSAFE at {pin}")
    log.append(f"Value/Footprint/MPN set for {len(B6_REFS)} refs")
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
