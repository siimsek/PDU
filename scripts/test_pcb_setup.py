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


def _with_segment(text: str, a, b, w: float, net: str) -> str:
    seg = (f'\t(segment\n\t\t(start {a[0]:g} {a[1]:g})\n\t\t(end {b[0]:g} {b[1]:g})\n\t\t(width {w:g})\n'
           f'\t\t(layer "F.Cu")\n\t\t(net "{net}")\n\t\t(uuid "00000000-0000-0000-0000-000000000001")\n\t)\n')
    i = text.rstrip().rfind(")")
    return text[:i] + seg + text[i:]


def test_neck_audit_limits_scope_and_length():
    text = (ROOT / "PDU.kicad_pcb").read_text(encoding="utf-8")
    rows = pcb_rules.routing_rows()
    pad = next(p for p in pcb_drc.fine_pads(text, rows) if p[1] == "U1" and p[2] == "/VIN")
    x, y = pad[3], pad[4]
    assert pcb_drc.neck_audit(_with_segment(text, (x, y), (x + 1.0, y), 0.3, "/VIN"), rows) == []
    long_ = pcb_drc.neck_audit(_with_segment(text, (x, y), (x + 3.0, y), 0.3, "/VIN"), rows)
    assert long_ and "length" in long_[0]["why"][0]
    free = pcb_drc.neck_audit(_with_segment(text, (90, 87.2), (91, 87.2), 0.3, "/VIN"), rows)
    assert free and "not ended" in free[0]["why"][-1]
    assert pcb_drc.neck_audit(_with_segment(text, (90, 87.2), (95, 87.2), 3.3, "/VIN"), rows) == []
    assert pcb_drc.neck_audit(_with_segment(text, (x, y), (x + 1.0, y), 0.2, "/VIN"), rows)[0]["why"][0] == "width < neck min"


def test_cin_at_buck_hot_loop():
    """R-012 #1: CIN1-4 at U1, CIN5-8 at U2 (PCB-HANDOFF §3.2), not in the input group."""
    import math
    pl = json.loads((T013 / "placement.json").read_text(encoding="utf-8"))
    pos = pl["positions_d006"]
    for ic, caps in (("U1", range(1, 5)), ("U2", range(5, 9))):
        d = sorted(math.dist(pos[ic], pos[f"CIN{i}"]) for i in caps)
        assert d[0] < 6.0 and d[-1] < 17.0
    assert all(f"CIN{i}" in pl["groups"]["Buck faz 1"] for i in range(1, 5))
    assert all(f"CIN{i}" in pl["groups"]["Buck faz 2"] for i in range(5, 9))


def test_neck_probe_recorded_pass():
    assert json.loads((T013 / "neck-probe.json").read_text(encoding="utf-8"))["pass"]


def _with_arc(text: str, a, m, b, w: float, net: str) -> str:
    arc = (f'\t(arc\n\t\t(start {a[0]:g} {a[1]:g})\n\t\t(mid {m[0]:g} {m[1]:g})\n\t\t(end {b[0]:g} {b[1]:g})\n'
           f'\t\t(width {w:g})\n\t\t(layer "F.Cu")\n\t\t(net "{net}")\n\t\t(uuid "00000000-0000-0000-0000-000000000002")\n\t)\n')
    i = text.rstrip().rfind(")")
    return text[:i] + arc + text[i:]


def test_arc_length_is_true_length_not_chord():
    import math
    assert abs(pcb_drc.arc_length((0, 0), (0.6, -0.6), (1.2, 0)) - math.pi * 0.6) < 1e-9      # semicircle
    assert abs(pcb_drc.arc_length((1, 0), (-1, 1e-4), (0, -1)) - 1.5 * math.pi) < 1e-6      # 3/4 circle, far side
    assert abs(pcb_drc.arc_length((0, 0), (0.5, 0), (1, 0)) - 1.0) < 1e-12                   # collinear


def test_neck_audit_arcs():
    """R-012 tur 2: a pad-ended neck arc with chord <= 1.5 mm but true length > 1.5 mm must fail; a short one passes."""
    text = (ROOT / "PDU.kicad_pcb").read_text(encoding="utf-8")
    rows = pcb_rules.routing_rows()
    pad = next(p for p in pcb_drc.fine_pads(text, rows) if p[1] == "U1" and p[2] == "/VIN")
    x, y = pad[3], pad[4]
    long_arc = pcb_drc.neck_audit(_with_arc(text, (x, y), (x + 0.6, y - 0.6), (x + 1.2, y), 0.3, "/VIN"), rows)
    assert len(long_arc) == 1 and long_arc[0]["kind"] == "arc" and long_arc[0]["why"] == ["length 1.88 > 1.5 mm"]
    assert pcb_drc.neck_audit(_with_arc(text, (x, y), (x + 0.45, y - 0.08), (x + 0.9, y), 0.3, "/VIN"), rows) == []
