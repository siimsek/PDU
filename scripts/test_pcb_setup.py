"""T-013 PCB setup checks (stdlib; pcbnew not needed — they read the committed board/project/rule files)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
import pcb_drc  # noqa: E402
import pcb_rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
T013 = ROOT / "reports" / "g5" / "T-013"


def test_rules_match_routing_and_board():
    assert pcb_rules.check() == []


def test_dru_widths_are_routing_g2():
    rows = pcb_rules.routing_rows()
    text = pcb_rules.dru_text(rows)
    for row in pcb_rules.CLASS_OF:
        assert f"(opt {rows[row]['selected_width_mm']:g}mm)" in text
    assert pcb_rules.DRU.read_text(encoding="utf-8") == text   # committed file is the generator output


def test_stackup_is_4_layer_1p6():
    tot = sum(t for _, _, t in pcb_rules.STACKUP if t)
    assert abs(tot - 1.6) < 1e-9
    assert [n for n, typ, _ in pcb_rules.STACKUP if typ == "copper"] == ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]


def test_strip_keeps_holes_only():
    root = ks.top(ks.parse(pcb_drc.strip_footprints((ROOT / "PDU.kicad_pcb").read_text(encoding="utf-8"))))
    refs = []
    for fp in root.children("footprint"):
        for p in fp.children("property"):
            if p.atoms()[1].value == "Reference":
                refs.append(p.atoms()[2].value)
    assert sorted(refs) == ["H1", "H2", "H3", "H4"]


def test_placement_inside_board_and_complete():
    pl = json.loads((T013 / "placement.json").read_text(encoding="utf-8"))
    assert pl["footprints"] == 180 and not pl["overflow"] and not pl["ungrouped"]
    assert len(pl["positions_d006"]) == 180
    for x, y in pl["positions_d006"].values():
        assert 0 < x < 120 and 0 < y < 85


def test_drc_gate_recorded_pass():
    s = json.loads((T013 / "drc-summary.json").read_text(encoding="utf-8"))
    assert s["pass"] and s["schematic_parity_issues"] == 0 and not s["empty_errors"]
