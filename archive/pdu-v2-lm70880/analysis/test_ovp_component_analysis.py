import json
from pathlib import Path

from ovp_component_analysis import (
    VTRIP_LIMIT,
    build_results,
    ceff_min_charge_coulombs,
    ceff_min_overshoot_bisect,
    divider_window_for_trip_target,
    threshold_bounds_enumerated,
    threshold_bounds_interval,
)


def test_threshold_corner_enumeration_is_inside_conservative_interval():
    enum_low, enum_high = threshold_bounds_enumerated()
    bound_low, bound_high = threshold_bounds_interval()
    assert bound_low <= enum_low
    assert enum_high <= bound_high
    data = build_results()
    assert data["threshold"]["worst_min_margin_above_steady_bus_mV"] > 0
    assert data["threshold"]["worst_max_headroom_to_12V_mV"] > 0
    window = divider_window_for_trip_target()
    assert window["candidate_rtop_in_window"] is False
    assert 3.0 < window["window_width_ohm"] < 5.0
    assert window["at_rtop_min_trip_min_V"] >= window["minimum_trip_bound_V"]
    assert window["at_rtop_max_trip_max_V"] <= window["prior_provisional_trip_max_V"]


def test_ceff_closed_form_and_bisection_crosscheck_match():
    i_fault = 11.9
    t_off = 324.7e-9
    headroom = VTRIP_LIMIT - 11.65
    first = ceff_min_charge_coulombs(i_fault, t_off, headroom)
    second = ceff_min_overshoot_bisect(i_fault, t_off, headroom)
    assert abs(first - second) < 1e-18
    results = build_results()["ceff"]
    assert results["review_10A_500ns_scenario_uF"] < results["review_10A_550ns_scenario_uF"]
    assert results["review_10A_500ns_scenario_uF"] > 10.0


def test_fault_current_screen_and_soA_remain_open_fail_closed():
    data = build_results()
    assert data["fault_current"]["fast_trip_current_screen_A"] > 11.0
    assert data["fault_current"]["is_guaranteed_fault_current_ceiling"] is False
    assert data["timing"]["guaranteed_total_toff_ns"] is None
    assert data["mosfet"]["soa_verified_at_turnoff_time"] is False
    assert data["ceff"]["minimum_ceff_for_physical_pass"] is None
    assert data["decision"].startswith("BLOCKED")
def test_combined_fault_logs_do_not_erase_historical_fails_or_claim_physical_pass():
    evidence = Path(__file__).resolve().parents[1] / "reports/g1/ovp-component-sim.json"
    result = json.loads(evidence.read_text(encoding="utf-8"))
    assert result["family2_original_18p8039V_fail_preserved"] is True
    assert result["family4_10p7109V_fail_preserved"] is True
    assert result["physical_measurement"].startswith("NOT PERFORMED")
    timing = result["cases"][0]
    assert timing["completed"] is True
    assert timing["measures"]["ovp_to_current_off"] > 0
    assert timing["measured_trip_to_series_current_below_1mA_s"] > 0
    assert len([case for case in result["cases"] if case.get("scenario")]) == 2
    for case in result["cases"]:
        if case.get("scenario"):
            assert case["completed"] is True
            assert case["status"].endswith("design acceptance BLOCKED")
            measured = case["measures"].get("ovp_to_current_off")
            assert case["series_current_off_measurement_valid"] is (measured is not None and measured >= 0)
