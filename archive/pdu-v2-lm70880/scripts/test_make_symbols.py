"""T-017: generated symbols cover every spec pin and the library parses."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
import make_symbols as ms  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis.check_consistency import parse_spec  # noqa: E402

USES = {"INA296A2QDGKRQ1": ["U11", "U12"], "TLV3601DCKR": ["U7", "U13", "U14"], "SN74LVC1G74DCUR": ["U9"],
        "LM74502HDDFR": ["U6"], "TPS7A1650QDGNRQ1": ["U10"]}


def test_symbols_in_library_match_generator():
    lib = ks.top(ks.parse((ROOT / "hardware/lib/PDU.kicad_sym").read_text(encoding="utf-8")))
    for name, (_, fp, pins) in ms.SYMBOLS.items():
        sym = next(s for s in lib.children("symbol") if s.atoms()[1].value == name)
        got = {next(p.children("number")).atoms()[1].value for p in ks.walk(sym) if p.head == "pin"}
        assert got == {p[0] for p in pins}, name


def test_every_spec_pin_exists_and_footprint_matches():
    spec, _ = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    for name, refs in USES.items():
        nums = {p[0] for p in ms.SYMBOLS[name][2]}
        for ref in refs:
            assert spec[ref]["footprint"] == ms.SYMBOLS[name][1], ref
            assert set(spec[ref]["pins"]) <= nums, (ref, set(spec[ref]["pins"]) - nums)
