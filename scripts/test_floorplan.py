"""Tests for the T-003 floorplan budget."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import floorplan as fp  # noqa: E402


@pytest.mark.skipif(not fp.STOCK.exists(), reason="KiCad stock footprint library not installed")
def test_every_bom_row_has_area_and_groups_sum():
    res = fp.compute()
    assert res["missing"] == []
    assert res["parts"] == 142
    assert abs(sum(g["area_mm2"] for g in res["groups"].values()) - res["total_courtyard_mm2"]) < 0.5
    assert "diğer" not in res["groups"], "every ref must map to a PCB-HANDOFF group"
    cout = [r for r in res["rows"] if r["ref"].startswith("COUT")]
    assert len(cout) == 32 and all(r["area_mm2"] > 40 for r in cout)


def test_custom_footprint_courtyard_bbox():
    w, h = fp.bbox(fp.CUSTOM / "TDK_C5750_2220_Recommended.kicad_mod")
    assert 5.0 < w < 10.0 and 4.0 < h < 8.0
