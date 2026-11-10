import pytest

from analysis.ovp_sense_fail_safe import (
    OLD_RBOT,
    OLD_RTOP,
    R_BLEED,
    R_BLEED_TOL,
    RAIL_CORNERS,
    RAW_CORNERS,
    RBOT,
    RTOP,
    TLV3601_POR_V,
    TLV_INPUT_CURRENT_LIMIT_A,
    build_charge_balance_deck,
    build_sense_rail_loss_deck,
    clamp_current_a,
    clamp_current_nodal_a,
    divider_open_circuit_v,
    max_clamp_current_corner_a,
    max_unpowered_rail_equilibrium_corner_v,
    rail_equilibrium_bisect_v,
    rail_equilibrium_v,
    threshold_bounds_interval,
    threshold_corners,
)


def test_reproduce_comment_6692033623_unpowered_current_fail():
    injection = clamp_current_a(40.709, 0.0, OLD_RTOP, OLD_RBOT)
    assert injection * 1e3 == pytest.approx(10.956, abs=0.002)
    assert injection > TLV_INPUT_CURRENT_LIMIT_A


def test_candidate_clamp_current_all_review_corners_is_under_absmax():
    values = [clamp_current_a(raw, vcc, RTOP, RBOT)
              for raw in RAW_CORNERS for vcc in RAIL_CORNERS]
    conservative_zero_vf = [clamp_current_a(raw, vcc, RTOP, RBOT, 0.0)
                            for raw in RAW_CORNERS for vcc in RAIL_CORNERS]
    assert max(values) < TLV_INPUT_CURRENT_LIMIT_A
    assert max(conservative_zero_vf) < TLV_INPUT_CURRENT_LIMIT_A
    assert max(max_clamp_current_corner_a(raw, vcc) for raw in RAW_CORNERS for vcc in RAIL_CORNERS) < TLV_INPUT_CURRENT_LIMIT_A


def test_divider_clamp_kcl_matches_independent_nodal_solution():
    for raw in RAW_CORNERS:
        for vcc in RAIL_CORNERS:
            assert clamp_current_a(raw, vcc, RTOP, RBOT) == pytest.approx(
                clamp_current_nodal_a(raw, vcc, RTOP, RBOT), rel=1e-8, abs=1e-10)


def test_unpowered_rail_result_bounds_rail_only_not_latch_safety():
    calc = rail_equilibrium_v(40.709, RTOP, RBOT, R_BLEED * (1 + R_BLEED_TOL), 0.0)
    bisect = rail_equilibrium_bisect_v(40.709, RTOP, RBOT,
                                       R_BLEED * (1 + R_BLEED_TOL), 0.0)
    assert calc == pytest.approx(bisect, abs=1e-10)
    assert calc < 1.2
    assert calc < TLV3601_POR_V
    # Below 1.65 V, SN74LVC1G74 behavior is unspecified; this bound proves
    # only that modeled back-power keeps the rail low, not that Q/CLR/gates are safe.
    assert calc < 1.65
    assert max_unpowered_rail_equilibrium_corner_v(40.709) < 1.2


def test_threshold_corner_enumeration_and_interval_agree_and_keep_limits():
    enumerated = [row["vtrip_V"] for row in threshold_corners("TLV3601")]
    interval = threshold_bounds_interval("TLV3601")
    assert min(enumerated) == pytest.approx(interval[0], abs=0.001)
    assert max(enumerated) == pytest.approx(interval[1], abs=0.001)
    assert min(enumerated) >= 11.1605
    assert max(enumerated) <= 12.0


def test_tlv1851_input_is_fail_safe_at_fault_and_unpowered():
    at_fault = divider_open_circuit_v(40.709, RTOP, RBOT)
    assert 8.8 < at_fault < 9.0
    assert at_fault < 40.0
    # TLV1851 fail-safe input is not diode-clamped to V+; high input cannot feed 5-V rail.
    assert max(divider_open_circuit_v(raw, RTOP, RBOT) for raw in RAW_CORNERS) < 40.0


def test_charge_balance_deck_has_separate_input_output_capacitor_and_branch_sensors():
    deck = build_charge_balance_deck()
    for token in ("V_CEFIN1_SENSE", "V_CEFIN2_SENSE", "V_CEFOUT1_SENSE",
                  "V_CEFOUT2_SENSE", "V_EFUSE_O1_SENSE", "V_EFUSE_S2E_SENSE",
                  "V_LOAD_O1_SENSE", "V_LOAD_S2E_SENSE", "Q_SW_C", "Q_OUT1_C"):
        assert token in deck
    assert "I(V_CEFIN1_SENSE)" in deck
    assert "I(V_CEFOUT1_SENSE)" in deck


def test_unpowered_rail_loss_deck_starts_raw_fault_and_measures_recovery():
    deck = build_sense_rail_loss_deck()
    assert "40.709" in deck
    assert "VCC_AFTER_LOSS_MAX" in deck
    assert "VCC_AFTER_LOSS_END" in deck
    assert "ICLAMP_MAX" in deck


def test_original_g1_and_wp_failures_remain_explicit_in_result_contract():
    from analysis.ovp_sense_fail_safe import build_results

    failures = build_results()["preserved_failures"]
    assert failures["family2_original_O1_18p8039V_FAIL"] is True
    assert failures["family2_common_bus_40p709V_TPS25982_IN_FAIL"] is True
    assert failures["family4_bus_10p7109V_FAIL"] is True
    assert failures["baseline_O1_16p89V_FAIL"] is True
    assert failures["WP1_incomplete_4_and_N01_open"] is True
    assert failures["WP2_69_FAIL_6_incomplete"] is True


def test_ldo_thermal_screen_is_not_silently_called_pass_at_85c():
    from analysis.ovp_sense_fail_safe import build_results

    rail = build_results()["rail_and_thermal"]
    assert rail["estimated_Tj_at_85C_ambient_C"] > rail["conservative_Tj_screen_C"]
    assert rail["estimated_Tj_at_85C_ambient_C"] < rail["datasheet_Tj_operating_max_C"]
    assert rail["125C_screen_is_TI_limit"] is False
    assert "FAIL" in rail["at_85C_ambient_status"]
