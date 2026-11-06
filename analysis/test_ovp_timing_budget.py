import json
from pathlib import Path

import pytest

from analysis.ovp_timing_budget import RESULT_PATH, build_results, pin_connection_table


def test_comparator_threshold_corner_ranges_are_reproducible():
    result = build_results()
    tlv = result["comparator_candidates"][0]["threshold_corners"]
    ltc = result["comparator_candidates"][1]["threshold_corners"]
    assert tlv["nominal_V"] == pytest.approx(11.475)
    assert 11.2 < tlv["minimum_V"] < tlv["maximum_V"] < 12.0
    assert 11.2 < ltc["minimum_V"] < ltc["maximum_V"] < 12.0
    assert tlv["unmodeled_resistor_TCR"] is True
    assert ltc["unmodeled_input_bias_and_leakage"] is True
    checks = result["calculation_cross_checks"]
    assert checks["TLV1701_corner_min_abs_difference_V"] < 1e-12
    assert checks["TLV1701_corner_max_abs_difference_V"] < 1e-12
    assert checks["LTC6752_corner_min_abs_difference_V"] < 1e-12
    assert checks["LTC6752_corner_max_abs_difference_V"] < 1e-12
    assert "not independent silicon" in checks["scope"]


def test_timing_screen_and_o1_voltage_budget_remain_separate():
    result = build_results()
    timing = result["timing"]
    assert timing["TLV1701_chain"]["illustrative_sum_s"] > 0.5e-6
    assert timing["TLV1701_chain"]["worst_case_status"].startswith("OPEN")
    assert timing["LTC6752_chain"]["conditional_sum_s"] < 0.5e-6
    assert timing["LTC6752_chain"]["worst_case_status"].startswith("OPEN")
    assert timing["O1_limit"]["criterion_V"] == 12.0
    assert timing["O1_limit"]["TLV_max_total_trip_to_current_interruption_s"] < 0.5e-6
    assert "0.5us screen is not substituted" in timing["O1_limit"]["status"]
    assert timing["TLV1701_chain"]["input_overdrive_build_to_100mV_s_under_assumptions"] > timing["O1_limit"]["TLV_max_total_trip_to_current_interruption_s"]
    assert timing["LTC6752_chain"]["conditional_sum_including_overdrive_s"] > timing["O1_limit"]["LTC_max_total_trip_to_current_interruption_s"]
    checks = result["calculation_cross_checks"]
    assert checks["TLV1701_overdrive_time_abs_difference_s"] < 1e-15
    assert checks["LTC6752_overdrive_time_abs_difference_s"] < 1e-15


def test_comparator_maximum_and_fault_input_ranges_are_not_overstated():
    result = build_results()
    tlv, ltc = result["comparator_candidates"]
    assert tlv["propagation"]["guaranteed_max_s"] is None
    assert ltc["propagation"]["published_max_s"] == pytest.approx(5.7e-9)
    assert "actual candidate threshold common mode is about 2.5V" in ltc["propagation"]["conditions"]
    assert ltc["fault_input_over_operating_common_mode_at_40p709V_V"] > 3.7
    assert "NO FEASIBLE GUARANTEED" in result["decision"]


def test_bjt_current_screen_keeps_datasheet_condition_limit_open():
    bjt = build_results()["bjt_screen"]
    assert 0.45e-3 < bjt["Q_INP_CLAMP_base_current_A"][0] < 0.55e-3
    assert bjt["Q_INP_CLAMP_forced_beta_max"] < 11
    assert bjt["Q_INP_RELEASE_forced_beta_max"] < 11
    assert bjt["CLR_N_high_margin_over_VIH_V"] > 0.8
    assert bjt["status"].startswith("SCREEN ONLY")
    assert bjt["CLR_node_sink_leakage_A"] == pytest.approx(2.07e-6)
    assert sum(bjt["CLR_node_sink_leakage_breakdown_A"].values()) == pytest.approx(2.07e-6)


def test_pin_map_uses_one_pg_clr_node_and_has_all_critical_control_pins():
    result = build_results()
    table = pin_connection_table()
    common = [row for row in table if row["net"] == "CLR_N = PG_OK"]
    assert len(common) >= 5
    assert "single common pull-up" in next(row["connect"] for row in table if row["ref_pin"] == "R_CLR 10k")
    all_text = "\n".join(f"{r['ref_pin']} {r['net']} {r['connect']}" for r in table)
    for needle in ("INP", "TGDN", "TGUP", "TS", "BST", "PRE", "ARM_CLK", "Q_INP_CLAMP", "Q_INP_RELEASE"):
        assert needle in all_text
    assert len(result["pin_connection_table"]) == len(table)
    bst = next(r for r in table if r["ref_pin"] == "U_DRIVER pin 9 BST")
    assert ">306nF effective" in bst["connect"]
    assert "0.1uF is insufficient" in bst["connect"]


def test_bootstrap_capacitor_uses_two_fet_worst_case_gate_charge():
    result = build_results()
    cb = result["timing"]["LTC7001_bootstrap"]
    assert cb["two_FET_Qg_max_C"] == pytest.approx(306e-9)
    assert cb["required_Ceff_F"] == pytest.approx(306e-9)
    assert cb["candidate_0p1uF_satisfies"] is False


def test_efuse_evidence_and_r6_event_order_are_not_promoted_to_pass():
    e = build_results()["efuse_manufacturer_evidence"]
    assert e["input_abs_max_V"] == 30.0
    assert "VIN + 0.3" in e["output_max_abs_V"]
    assert e["official_model"]["encrypted"] is True
    assert e["official_model"]["local_simulator_available"] is False
    assert "900us" in e["r6_fixture_sequence"] and "1ms" in e["r6_fixture_sequence"]
    assert e["status"].startswith("OPEN")


def test_preserves_prior_fails_and_never_claims_physical_acceptance():
    result = build_results()
    status = result["preserved_status"]
    assert status["Family2_O1_18p8039V"].startswith("FAIL")
    assert status["Family4_bus_10p7109V"].startswith("FAIL")
    assert status["common_bus_TPS25982_IN_40p709V"].startswith("FAIL")
    assert status["O1_peak_le_12V"].startswith("OPEN")
    assert result["physical_acceptance"] is False


def test_saved_json_matches_reproducible_analysis():
    assert RESULT_PATH.exists()
    saved = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    expected = build_results()
    assert saved["decision"] == expected["decision"]
    assert saved["timing"]["O1_limit"]["TLV_trip_max_V_under_declared_assumptions"] == pytest.approx(
        expected["timing"]["O1_limit"]["TLV_trip_max_V_under_declared_assumptions"]
    )
