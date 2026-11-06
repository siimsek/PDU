import pytest

from analysis.g2 import power as pw


@pytest.fixture(scope="module")
def r():
    return pw.compute()


def test_inductor_two_paths_and_margins(r):
    i = r["inductor"]
    assert abs(i["peak_diff_A"]) < 1e-2 and abs(i["irms_diff_A"]) < 1e-3
    assert i["isat_margin_at_ilim_A"] > 2.0 and i["irms_margin_A"] > 2.0
    assert i["ocp_above_capacity"]


def test_slope_comp_at_least_half_downslope(r):
    assert r["inductor"]["slope_comp_check"]["se_over_sn"] > 0.5


def test_shunt_derating_below_50pct(r):
    assert r["sense"]["derating"] < 0.5


def test_cout_ripple_two_paths(r):
    c = r["cout"]
    assert abs(c["diff_A"]) < 0.01 and c["ripple_voltage_pp_V"] < 0.01 and c["voltage_derating"] < 0.5


def test_ilim_guaranteed_sum(r):
    e = r["efuse"]
    assert e["sum_min_ge_7p5"] and e["sum_min_A"] == pytest.approx(11.59)
    assert e["o1_margin_over_load_envelope_A"] > 0 and e["s2e_margin_over_start_A"] > 0


def test_uvlo_174k_restarts_at_20V_and_180k_fail_preserved(r):
    assert r["uvlo_174k"]["restart_at_20V"]
    assert not r["uvlo_180k_old"]["restart_at_20V"]
    assert all(abs(x) < 1e-2 for x in r["uvlo_174k"]["diff_V"])


def test_ic_thermal_flagged_not_hidden(r):
    # at the assumed 85 C ambient the derived IC Tj exceeds the 125 C screen: must stay visible
    assert r["losses"]["tj_ic_C"]["evm_18p6"] > 125
