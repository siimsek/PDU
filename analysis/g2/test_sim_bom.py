import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM = json.loads((ROOT / "reports" / "g2" / "sim-results.json").read_text(encoding="utf-8"))
PROT = json.loads((ROOT / "reports" / "g2" / "protection-results.json").read_text(encoding="utf-8"))

EXPECTED_FAIL = {"f1_noprot_baseline", "f4_input_loss_without_drev", "f5_precision_path_open_residual",
                 "f3_stacked_low_setpoint_cmin_gmmin", "f3_stacked_high_setpoint_cmin_gmmin"}


def test_all_five_families_completed():
    s = SIM["summary"]
    assert set(s) == {"F1", "F2", "F3", "F4", "F5"}
    for fam, v in s.items():
        assert v["runs"] > 0 and v["completed"] == v["runs"], fam


def test_failures_are_exactly_the_recorded_ones():
    fails = {n for n, r in SIM["runs"].items() if not r["pass"]}
    assert fails == EXPECTED_FAIL


def test_unprotected_baseline_fail_is_preserved():
    r = SIM["runs"]["f1_noprot_baseline"]["measures"]
    assert r["o1_max_fault"] > 12.0 and r["vsafe_max_fault"] > 30.0


def test_o1_hesap_and_sim_agree_for_worst_case():
    sim = SIM["runs"]["f1_worst"]["measures"]["o1_max_fault"]
    hesap = PROT["o1_peak_worst"]["peak_V"]
    assert sim <= 12.0 and hesap <= 12.0
    assert abs(sim - hesap) < 0.05, (sim, hesap)


def test_f5_sweep_worst_below_limit():
    o1 = [r["measures"]["o1_max_fault"] for n, r in SIM["runs"].items()
          if r["family"] == "F5" and n != "f5_precision_path_open_residual"]
    assert len(o1) == 48 and max(o1) <= 12.0


def test_every_run_has_hashes_and_logs():
    for n, r in SIM["runs"].items():
        assert len(r["deck_sha256"]) == 64 and r["log_sha256"] and (ROOT / r["log"]).exists(), n


def test_bom_no_mpn_without_datasheet_and_derating():
    rows = list(csv.DictReader((ROOT / "design" / "bom-v2.csv").open(encoding="utf-8")))
    assert len(rows) >= 80
    for row in rows:
        if row["mpn"]:
            assert row["datasheet"], row["ref"]
        assert not row["derating_ok"].startswith("NO"), row["ref"]
    opened = (ROOT / "reports" / "g2" / "BOM-OPEN.md").read_text(encoding="utf-8")
    for row in rows:
        if not row["mpn"]:
            assert f"| {row['ref']} |" in opened, row["ref"]


def test_no_kicad_files_in_g2_outputs():
    for p in (ROOT / "design").iterdir():
        assert ".kicad_" not in p.name


# ---- G3 audit regression guards
def test_efuse_is_active_current_limiter_variant():
    rows = {r["ref"]: r for r in csv.DictReader((ROOT / "design" / "bom-v2.csv").open(encoding="utf-8"))}
    assert rows["U3"]["mpn"] == rows["U4"]["mpn"] == "TPS259824LNRGER"


def test_lm70880_bias_on_protected_rail_and_fra_injection_at_low_z_side():
    spec = (ROOT / "design" / "pdu_v2_spec.yaml").read_text(encoding="utf-8")
    assert spec.count('"BIAS(6)": "/VSAFE"') == 2
    blk = spec.split("- ref: R_INJ")[1].split("- ref:")[0]
    assert '"/VOUT"' in blk and '"/FB_INJ"' in blk


def test_sim_runs_match_current_case_set_and_transient_band_criterion():
    from analysis.g2 import sim_runner
    assert set(SIM["runs"]) == set(sim_runner.family_cases())
    for n, r in SIM["runs"].items():
        if r["family"] == "F3":
            assert r["criteria"]["bus_max_release"]["limit"] == 11.22, n


def test_raw_bus_fault_peak_below_lm70880_vout_pin_limit():
    for n, r in SIM["runs"].items():
        if "vraw_max_fault" in r["criteria"]:
            assert r["measures"]["vraw_max_fault"] < 60.0, n
