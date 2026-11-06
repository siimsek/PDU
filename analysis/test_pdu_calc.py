import math

from pdu_calc import build_results, feedback_corner, uvlo_corner


def test_buck_ripple_two_equations_agree():
    r = build_results()["buck"]["ripple"]
    assert math.isclose(r["value"], 2.918, rel_tol=1e-3)
    assert r["absolute_difference"] < 1e-12


def test_phase_peak_and_coil_saturation_screen():
    d = build_results()["buck"]
    assert d["phase_peak"]["value"] < d["IHLP_family_screen"]["published_Isat_A_at_approx_20pct_L_drop"]
    assert d["phase_peak"]["absolute_difference"] < 1e-12


def test_fb_corner_extrema_two_methods_agree():
    c = feedback_corner()
    assert math.isclose(c["min_V"], c["second_min_V"], rel_tol=1e-12)
    assert math.isclose(c["max_V"], c["second_max_V"], rel_tol=1e-12)


def test_uvlo_174k_candidate_restarts_within_20v_before_leakage():
    c = uvlo_corner(174e3, 10e3)
    assert c["max_V"] <= 20.0
    assert math.isclose(c["max_V"], c["second_max_V"], rel_tol=1e-12)


def test_all_reported_dual_paths_have_difference_fields():
    data = build_results()
    assert data["dual_path_validation_summary"]["independent_physical_model_validations"] == 0
    for entry in data["dual_path_checks"]:
        assert "absolute_difference" in entry
        assert "relative_difference_percent" in entry
        assert entry["validation_scope"] in {
            "same_equation_arithmetic_crosscheck",
            "independent_algorithm_same_equation",
        }
        assert entry["absolute_difference"] < 1e-8


def test_ovp_is_reported_open_and_not_as_a_pass():
    data = build_results()
    assert data["input_protection"]["F1_fault_current_A"].startswith("AÇIK")
    assert data["loop"]["phase_margin_estimate_deg"] is None


def test_routing_2l_4l_envelopes_use_updated_load_and_meet_drop_screen():
    data = build_results()
    rows = data["routing"]["calculation"]["rows"]
    by_name = {row["name"]: row for row in rows}
    assert by_name["BUS_POWER"]["current_A_screen"] == 7.5
    assert by_name["O1_POWER"]["current_A_screen"] == 7.5
    assert by_name["S2E_POWER"]["current_A_screen"] == 7.5
    for row in rows:
        assert row["2_layer"]["drop_mV"] <= 50.0 + 1e-9
        assert row["4_layer_two_equal_paths"]["drop_mV"] <= 50.0 + 1e-9
    assert all(x["absolute_difference"] < 1e-8 for x in data["routing"]["dual_path_checks"])

