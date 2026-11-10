"""Fail-closed checks for PR #2 independent review evidence boundaries."""
from verify_pr2_review import build_verification


def test_ovp_delay_fix_does_not_join_unrelated_short_model():
    proof = build_verification()
    assert proof["checks"]["family1_tdelay_is_used_after_correction"]
    assert proof["family1_ovp"]["model_margin_mV"] < 30.0
    assert "OPEN" in proof["family1_ovp"]["candidate_high_side_short_proof"]
    assert proof["family2_buck_highside_short"]["o1_peak_V"] > 12.0


def test_load_step_minimum_is_in_window_and_fail_remains():
    proof = build_verification()
    result = proof["family4_load_step"]
    assert result["measurement_window_ms"] == [10.0, 12.0]
    assert 0 < result["minimum_after_step_us"] < 2000
    assert result["minimum_below_10p78V_mV"] > 0
    assert "FAIL retained" in result["criterion"]


def test_static_uvlo_and_arithmetic_crosschecks_are_not_physical_acceptance():
    proof = build_verification()
    assert proof["checks"]["wp2_historical_fail_and_incomplete_counts_present"]
    assert proof["wp2_uvlo"]["dynamic_gates"] == "OPEN"
    assert proof["calculation_two_path_review"]["independent_physical_model_validations"] == 0
    assert proof["physical_acceptance"] == "NOT PERFORMED"
