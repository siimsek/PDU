"""Tests for the lossless KiCad S-expression tool (T-002)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

MINI = '''(kicad_sch (version 20250114)
\t(symbol (lib_id "Device:R") (at 10 20 0)
\t\t(property "Reference" "R1" (at 0 0 0))
\t\t(property "Value" "10k" (at 0 0 0) (effects (font (size 1.27 1.27))))
\t)
)
'''


def test_roundtrip_project_files_byte_identical():
    for f in [ROOT / "PDU.kicad_sch", ROOT / "PDU.kicad_pcb", *sorted((ROOT / "hardware/lib/PDU.pretty").glob("*.kicad_mod"))]:
        src = f.read_bytes().decode("utf-8")
        assert ks.dumps(ks.parse(src)) == src, f.name


def test_set_property_changes_only_that_atom():
    root = ks.parse(MINI)
    assert ks.set_property(root, "R1", "Value", 'a"b')
    out = ks.dumps(root)
    assert '(property "Value" "a\\"b" (at 0 0 0)' in out
    assert out.replace('"a\\"b"', '"10k"') == MINI


def test_missing_ref_returns_false():
    assert not ks.set_property(ks.parse(MINI), "R9", "Value", "1k")


def test_unbalanced_raises():
    import pytest
    with pytest.raises(ValueError):
        ks.parse("(a (b)")
