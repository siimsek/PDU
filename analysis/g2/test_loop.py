import json
from pathlib import Path

import pytest

from analysis.g2 import design as D
from analysis.g2 import loop

RES = Path(__file__).resolve().parents[2] / "reports" / "g2" / "loop-results.json"


def test_design_matches_selected_compensation():
    sel = json.loads(RES.read_text(encoding="utf-8"))["selected"]
    assert (sel["rcomp"], sel["ccomp"], sel["chf"]) == (D.RCOMP, D.CCOMP, D.CHF)


def test_all_corners_meet_pm_with_model_margin_and_gm():
    ev = loop.evaluate(D.RCOMP, D.CCOMP, D.CHF)
    assert ev["all_crossed"]
    assert ev["pm_min"] - loop.PM_MODEL_MARGIN >= loop.PM_TARGET
    assert ev["gm_min"] >= loop.GM_TARGET
    assert ev["fc_max"] <= 480e3 / 6 and len(ev["rows"]) == 3 * 3 * 3 * 2 * 2 * 2


def test_spice_ac_agrees_with_analytic():
    d = json.loads(RES.read_text(encoding="utf-8"))
    assert len(d["spice_checks"]) == 5
    for c in d["spice_checks"]:
        assert c["spice"]["completed"]
        assert abs(c["diff_pm_deg"]) < 0.5 and abs(c["diff_fc_rel"]) < 0.01
