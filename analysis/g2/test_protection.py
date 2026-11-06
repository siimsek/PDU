import pytest

from analysis.g2 import protection as p
from analysis.g2.params import v


@pytest.fixture(scope="module")
def res16():
    return p.compute(16)


def test_divider_pair_is_pinned(res16):
    assert res16["precision_divider"]["rt_ohm"] == 8250.0
    assert res16["precision_divider"]["rb_ohm"] == 2320.0


def test_trip_two_paths_agree_and_respect_R03(res16):
    a = res16["trip_threshold"]["path_a_enumerated"]
    b = res16["trip_threshold"]["path_b_interval"]
    assert abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) < 1e-3
    assert a[0] >= v("BUS_TRANSIENT_MAX") + 0.030


def test_comparator_common_mode_valid_at_trip(res16):
    assert res16["trip_threshold"]["comparator_vcm_at_trip_V"] < 5.0 * 0.98 + v("CMP_VCM_HI")


def test_clamp_current_below_10mA_both_paths(res16):
    c = res16["clamp_current"]
    assert c["vcc0_vraw_clamp_A_pathA"] < c["limit_A"]
    assert c["vcc0_vraw_clamp_A_pathB_worst"] < c["limit_A"]


def test_coarse_ov_window(res16):
    co = res16["coarse_ov"]
    assert co["above_transient_band"] and co["below_efuse_in_recommended"]
    assert co["path_a"][0] > res16["trip_threshold"]["path_a_enumerated"][1]  # precision path trips first
    assert abs(co["diff_V"][0]) < 0.05 and abs(co["diff_V"][1]) < 0.05
    assert co["latched_margin_over_ovr_max_V"] > 0.3


def test_en_gating_turns_gate_off_before_logic_undefined(res16):
    e = res16["en_gating"]
    assert e["gate_off_before_latch_undefined"] and e["gate_off_before_comparator_por"] and e["rail_on_below_5V_min"]


def test_timing_uses_max_values_only(res16):
    t = res16["timing"]
    assert t["parts_s"]["lm74502h_tovp_off_max"] == v("DRV_TOVP_OFF_MAX")
    assert t["total_max_s"] < 1.1e-6


def test_o1_peak_margin_needs_more_than_original_8_cout():
    assert p.compute(16)["o1_peak_worst"]["margin_V"] > 0.050
    r8 = p.compute(8)["o1_peak_worst"]
    assert r8["margin_V"] < 0.005, "original 8x COUT leaves essentially no O1 margin"


def test_peak_closed_form_is_conservative_upper_bound(res16):
    # path A ignores series resistance (lossless) so it must not be below path B; difference reported
    for c in res16["o1_peak_cases"]:
        assert c["diff_V"] > -1e-3 and c["diff_V"] < 0.05


def test_fet_limits(res16):
    f = res16["fet"]
    assert f["vds_margin_V"] > 40 and f["vgs_rating_ok"] and f["energy_ratio"] < 0.01
