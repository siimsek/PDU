"""Tests for analysis/check_footprints.py (T-005a)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis import check_footprints as cf  # noqa: E402


def test_custom_footprints_match_ti_land_patterns():
    for name, ref in cf.REFERENCE.items():
        r = cf.check_one(name, ref)
        assert r["pass"], (name, r["errors"])


def test_shifted_pad_is_detected():
    name = "TPS25982_RGE0024M"
    text = (cf.LIB / "PDU.pretty" / f"{name}.kicad_mod").read_text(encoding="utf-8")
    bad = text.replace('(pad "1" smd roundrect (at -1.9125 -1.25)', '(pad "1" smd roundrect (at -1.9425 -1.25)')
    assert bad != text
    r = cf.check_one(name, cf.REFERENCE[name], bad)
    assert not r["pass"] and any("pad 1" in e for e in r["errors"])


def test_missing_exposed_pad_is_detected():
    name = "TPS25982_RGE0024M"
    text = (cf.LIB / "PDU.pretty" / f"{name}.kicad_mod").read_text(encoding="utf-8")
    bad = text.replace('(pad "26" smd', '(pad "" smd')
    r = cf.check_one(name, cf.REFERENCE[name], bad)
    assert not r["pass"]
