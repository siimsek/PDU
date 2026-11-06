import json
import math
from pathlib import Path

import pytest

from analysis.ovp_control_chain_followup import (
    CONTROL_CHAIN_CANDIDATE,
    FET_CEQ_PROXY_F,
    GATE_BLEED_OHM,
    GATE_INITIAL_V,
    GATE_SCREEN_V,
    build_efuse_out_in_deck,
    build_gate_loss_deck,
    simulate_control_sequence,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "reports/g1/ovp-control-chain-followup.json"


def saved_results():
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def test_two_targeted_fixtures_completed_and_are_behavioral_only():
    result = saved_results()
    assert result["gate_loss"]["completed"] is True
    assert result["efuse_out_in"]["completed"] is True
    assert result["gate_loss"]["solver_exit_code"] == 0
    assert result["efuse_out_in"]["solver_exit_code"] == 0
    assert "no physical PASS" in result["classification"]
    assert "not a TPS259824O transient prediction" in result["efuse_out_in"]["interpretation"]


def test_gate_charge_proxy_and_independent_rc_crosscheck():
    result = saved_results()["gate_loss"]
    expected_c = 153e-9 / 10
    assert FET_CEQ_PROXY_F == pytest.approx(expected_c)
    assert result["gate_proxy"]["Ceq_proxy_F_per_FET"] == pytest.approx(expected_c)
    calc = result["analytical_crosscheck"]
    assert calc["passive_tau_s"] == pytest.approx(10_000 * expected_c)
    assert calc["passive_to_2p1V_s"] == pytest.approx(10_000 * expected_c * math.log(10 / 2.1))
    assert abs(result["ngspice_vs_calculation"]["passive_to_2p1V_percent_delta"]) < 0.01


def test_all_gate_voltages_are_ts_referenced_and_active_is_not_silicon_pass():
    deck = build_gate_loss_deck()
    assert "VTS_A TSA 0 26" in deck and "VTS_P TSP 0 26" in deck
    assert "BVGS_A VGS_A 0 V=V(GA)-V(TSA)" in deck
    assert "BVGS_P VGS_P 0 V=V(GP)-V(TSP)" in deck
    result = saved_results()["gate_loss"]
    m = result["measures"]
    assert m["vgs1_active_0p5us"] == pytest.approx(m["vgs2_active_0p5us"])
    assert m["vgs1_passive_0p5us"] == pytest.approx(m["vgs2_passive_0p5us"])
    assert m["vgs1_active_0p5us"] < 0.2
    assert m["vgs1_passive_0p5us"] > 9.9
    assert result["status"].startswith("OPEN")


def test_passive_gate_bleed_misses_previous_fast_turnoff_screen():
    result = saved_results()["gate_loss"]
    m = result["measures"]
    active_delay = m["tactive_to_2p1"] - 10e-6
    passive_delay = m["tpassive_to_2p1"] - 10e-6
    analytical_passive = GATE_BLEED_OHM * FET_CEQ_PROXY_F * math.log(GATE_INITIAL_V / GATE_SCREEN_V)
    assert active_delay < 0.5e-6
    assert passive_delay == pytest.approx(analytical_passive, rel=0.005)
    assert passive_delay > 200e-6


def test_efuse_common_open_and_precharged_input_loss_are_distinct():
    result = saved_results()["efuse_out_in"]
    status = result["duration_and_boundary_register"]
    assert status["co_open_o1"]["max_OUT_minus_IN_V"] > 10.9
    assert status["co_open_o1"]["duration_is_right_censored"] is True
    assert status["co_open_s2e"]["max_OUT_minus_IN_V"] > 9.0
    assert 3.8e-3 < status["co_open_s2e"]["duration_above_0p3V_measured_s"] < 4.1e-3
    assert status["input_loss_o1"]["max_OUT_minus_IN_V"] == pytest.approx(11.0, abs=0.01)
    assert status["input_loss_o1"]["duration_is_right_censored"] is True
    assert status["input_loss_s2e"]["max_OUT_minus_IN_V"] > 10.9


def test_bilateral_switch_mask_is_explicitly_rejected_as_physical_evidence():
    result = saved_results()["efuse_out_in"]
    status = result["duration_and_boundary_register"]
    assert status["co_mask_o1"]["max_OUT_minus_IN_V"] < 0.3
    assert status["co_mask_s2e"]["max_OUT_minus_IN_V"] < 0.3
    assert "not admissible as device evidence" in result["interpretation"]
    assert "reverse-current behavior is not modeled" in result["interpretation"]


def test_efuse_s2e_rc_formula_agrees_with_simulated_duration():
    result = saved_results()["efuse_out_in"]["analytical_crosscheck"]
    assert abs(result["ngspice_direct_input_loss_S2E_delta_percent"]) < 1.0
    assert result["O1_RC_time_to_0p3V_s"] > 7.0
    assert result["S2E_RC_time_to_0p3V_s"] == pytest.approx(3.93e-3, rel=0.01)


def test_temporal_state_machine_starts_unknown_and_requires_new_press_after_fault():
    rows = simulate_control_sequence()
    assert [row["Q_after"] for row in rows] == [None, False, False, True, False, False, False, True]
    assert rows[0]["Q_before"] is None
    assert rows[2]["Q_after"] is False
    assert rows[4]["CLR_n"] == 0 and rows[4]["Q_after"] is False
    assert rows[5]["ARM_rising_edge"] is False and rows[5]["Q_after"] is False
    assert rows[7]["ARM_rising_edge"] is True and rows[7]["Q_after"] is True
    assert all(row["PRE_n"] == 1 for row in rows)


def test_both_rails_absent_does_not_credit_latch_or_driver_state():
    rows = simulate_control_sequence()
    cold = rows[0]
    assert cold["logic_VCC_V"] == 0
    assert cold["driver_VCC_V"] == 0
    assert cold["Q_after"] is None
    assert "NOT_CREDITED" in cold["INP_policy"]
    assert "G-S_BLEEDS_ONLY" in cold["INP_policy"]


def test_candidate_contains_real_mpn_pin_maps_and_correct_ltc_pin_order():
    c = CONTROL_CHAIN_CANDIDATE
    assert c["sense"]["U_OVP"]["mpn"] == "TLV1701QDBVRQ1"
    assert c["sense"]["U_OVP"] == {
        "mpn": "TLV1701QDBVRQ1", "package": "SOT-23-5",
        "IN+": 1, "V-": 2, "IN-": 3, "OUT_open_collector": 4, "V+": 5,
    }
    assert c["sense"]["U_REF"]["mpn"] == "REF5025AQDRQ1"
    assert c["sense"]["nominal_trip_V"] == pytest.approx(11.475)
    screen = c["sense"]["nominal_sense_fault_screen"]
    assert screen["VRAW_11p1605V_sense_V"] < 2.5
    assert screen["VRAW_trip_11p475V_sense_V"] == pytest.approx(2.5)
    assert 2.5 < screen["VRAW_40p709V_sense_V"] < 12.0
    assert c["sense"]["fault_path"].find("OUT pin 4 sinks CLR_n") >= 0
    assert c["logic_and_pg"]["U_LATCH"]["mpn"] == "SN74LVC1G74DCUR"
    assert c["driver_and_disconnect"]["U_DRIVER"]["TS"] == 8
    assert c["driver_and_disconnect"]["U_DRIVER"]["BST"] == 9
    assert c["driver_and_disconnect"]["U_DRIVER"]["TGDN"] == 6
    assert c["driver_and_disconnect"]["Q1_Q2"]["G"] == 1
    assert c["driver_and_disconnect"]["Q1_Q2"]["S"] == 3


def test_candidate_keeps_open_items_and_prior_fails():
    result = saved_results()
    assert result["candidate_chain"]["classification"].startswith("REAL-MPN")
    assert result["candidate_chain"]["unfrozen_passives"]
    assert result["preserved_status"]["Family2_O1_18p8039V"] == "FAIL retained"
    assert result["preserved_status"]["Family4_bus_10p7109V"] == "FAIL retained"
    assert result["preserved_status"]["O1_peak_le_12V_physical"] == "OPEN"


def test_fixture_decks_keep_device_models_explicitly_ideal():
    gate = build_gate_loss_deck()
    efuse = build_efuse_out_in_deck()
    assert "idealized 4ohm TGDN resistance" in gate
    assert "NOT a silicon model" in efuse
    assert "CO_MASK" in efuse and "INPUT_LOSS" in efuse
    assert "EFUSESW SW(Ron=1m Roff=1T" in efuse
