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
