import math

import pytest

from analysis.shared_bus_fault import (
    ORIGINAL_DECK,
    O1_NOMINAL_ILIM_A,
    S2E_NOMINAL_ILIM_A,
    VTRIP,
    T_OFF_S,
    build_common_isolator_deck,
    build_existing_overload_duration_deck,
    build_high_voltage_efuse_deck,
    load_current_at,
    required_capacitance_uF,
    tps1686_min_high_corner_for_steady_bus,
    tps1686_ovlo_threshold_bounds,
)


def test_ceff_charge_bound_matches_dimensional_calculation():
    expected = 7.5 * 325.4e-9 / (12.0 - 11.623168833598632) * 1e6
    assert required_capacitance_uF(7.5, T_OFF_S, VTRIP, 12.0) == pytest.approx(expected)


def test_ceff_rejects_nonpositive_voltage_headroom():
    with pytest.raises(ValueError):
        required_capacitance_uF(1.0, 1e-6, 12.0, 12.0)


def test_legacy_12a_case_loads_are_explicitly_resistive_and_overload():
    assert load_current_at(11.0, 1.57) == pytest.approx(7.00636942675)
    assert load_current_at(11.0, 2.2) == pytest.approx(5.0)
    assert load_current_at(11.0, 1.57) + load_current_at(11.0, 2.2) > 12.0


def test_duration_deck_is_derived_and_does_not_rewrite_original():
    original = ORIGINAL_DECK.read_text(encoding="utf-8")
    derived = build_existing_overload_duration_deck()
    assert "U3_GT24_DURATION_S" in derived
    assert "U4_GT30_DURATION_S" in derived
    assert "V(VOUT)>24.0" in derived
    assert ORIGINAL_DECK.read_text(encoding="utf-8") == original


def test_common_isolator_is_ahead_of_both_branch_input_models():
    deck = build_common_isolator_deck(1.5, "startup")
    assert "Sbus VRAW_SW VSAFE CTRL_BUS" in deck
    assert "Sefuse_O1 VSAFE O1" in deck
    assert "Sefuse_S2E VSAFE S2E" in deck
    assert "VSAFE" in deck and "VRAW" in deck
    assert f"BLOAD_O1 O1 0 I={O1_NOMINAL_ILIM_A:.12g}" in deck
    assert "BLOAD_S2E S2E 0 I=1.5" in deck
    assert math.isclose(O1_NOMINAL_ILIM_A + 1.5, 6.4604983388704325)


def test_configured_nominal_efuse_limits_match_g1_calculation_output():
    assert O1_NOMINAL_ILIM_A == pytest.approx(4.9604983388704325)
    assert S2E_NOMINAL_ILIM_A == pytest.approx(2.5272185430463576)
    assert O1_NOMINAL_ILIM_A + S2E_NOMINAL_ILIM_A == pytest.approx(7.48771688191679)
    assert 7.5 - O1_NOMINAL_ILIM_A - S2E_NOMINAL_ILIM_A == pytest.approx(0.01228311808320992)


def test_high_voltage_candidate_keeps_unknown_maximum_response_visible():
    deck = build_high_voltage_efuse_deck(0.22)
    assert "3 us is a published minimum tOVP; no maximum is specified" in deck
    assert "Btrip_O1" in deck and "Btrip_S2E" in deck


def test_tps1686_ovlo_accuracy_cannot_fit_static_bus_to_o1_window():
    low, high = tps1686_ovlo_threshold_bounds(11.3, 0.01)
    assert low < 11.1605
    assert high < 12.0
    assert tps1686_min_high_corner_for_steady_bus(11.1605) > 12.0
