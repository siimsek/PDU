"""Reproducible static audit of review comment 6681813880 evidence.

This checks the committed SPICE decks/logs and calculation metadata. It does
not run ngspice or claim electrical/physical acceptance.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g1"
REVIEWED_HEAD = "adf727f244092b3628ba759b1dee5cd48909a19c"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_git(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout


def _measure(log: str, name: str) -> tuple[float, float | None]:
    match = re.search(
        rf"(?im)^\s*{re.escape(name)}\s*=\s*([+-]?[\d.]+(?:e[+-]?\d+)?)\s*(?:at=\s*([\d.]+(?:e[+-]?\d+)?))?",
        log,
    )
    if not match:
        raise ValueError(f"measurement not found in log: {name}")
    return float(match.group(1)), float(match.group(2)) if match.group(2) else None


def build_verification() -> dict:
    sim = json.loads(_read(OUT / "sim-results.json"))
    calc = json.loads(_read(OUT / "calc-results.json"))
    family = {item["family"]: item for item in sim["families"]}
    required = {
        "family1_ovp": "family1-ovp-independent-latch",
        "family2_buck_highside_short": "family2-buck-highside-short",
        "family4_load_step_comp_corners": "family4-load-step-minc_lowcomp",
    }
    for name in required:
        if name not in family:
            raise ValueError(f"missing simulation family: {name}")

    f1_deck = _read(OUT / "sim" / f"{required['family1_ovp']}.cir")
    f1_old_deck = _read_git(REVIEWED_HEAD, "reports/g1/sim/family1-ovp-independent-latch.cir")
    f1_log = _read(OUT / "sim" / f"{required['family1_ovp']}.log")
    f2_deck = _read(OUT / "sim" / f"{required['family2_buck_highside_short']}.cir")
    f2_log = _read(OUT / "sim" / f"{required['family2_buck_highside_short']}.log")
    f4_deck = _read(OUT / "sim" / f"{required['family4_load_step_comp_corners']}.cir")
    f4_log = _read(OUT / "sim" / f"{required['family4_load_step_comp_corners']}.log")

    f1_value, _ = _measure(f1_log, "o1_peak")
    f2_o1, _ = _measure(f2_log, "o1_peak")
    f2_bus, _ = _measure(f2_log, "bus_peak")
    f2_phase, _ = _measure(f2_log, "phase_current")
    f4_min, f4_min_time_s = _measure(f4_log, "bus_min")
    f4_recover, _ = _measure(f4_log, "bus_recover")
    f4_floor = 10.78
    f4_high_step_time_s = 10e-3
    f4_initial_load_a = 0.45 + 0.30
    f4_step_load_a = 4.5 + 2.5

    active_lines = [line for line in f1_deck.splitlines() if not line.lstrip().startswith("*")]
    old_active_lines = [line for line in f1_old_deck.splitlines() if not line.lstrip().startswith("*")]
    f1_tdelay_uses = sum(line.upper().count("TDELAY") for line in active_lines if not line.lstrip().upper().startswith(".PARAM"))
    old_tdelay_uses = sum(line.upper().count("TDELAY") for line in old_active_lines if not line.lstrip().upper().startswith(".PARAM"))
    calc_validation = calc["dual_path_validation_summary"]
    previous = _read(OUT / "PREVIOUS-WP-COMPARISON.md").replace("**", "")
    decision = _read(OUT / "OVP-UVLO-DECISION.md")

    checks = {
        "family1_tdelay_is_used_after_correction": f1_tdelay_uses >= 1 and old_tdelay_uses == 0,
        "family1_peak_matches_spice_log": abs(f1_value - family["family1_ovp"]["cases"][0]["measures"]["o1_peak"]) < 1e-4,
        "family1_model_gate_pass_is_preserved": family["family1_ovp"]["completed"] and family["family1_ovp"]["criterion_pass"] and f1_value <= 12.0,
        "family2_ovp_candidate_absent_and_fail_preserved": "Sdisconnect" not in f2_deck and not family["family2_buck_highside_short"]["criterion_pass"] and f2_o1 > 12.0,
        "family4_transient_fail_preserved": not family["family4_load_step_comp_corners"]["criterion_pass"] and f4_min < f4_floor,
        "wp2_historical_fail_and_incomplete_counts_present": "161 PASS / 69 FAIL / 6" in previous,
        "uvlo_dynamic_gates_marked_open": all(token in decision for token in ("60 ms", "M1", "dip", "çift darbe", "AÇIK")),
        "independent_physical_validation_count_is_zero": calc_validation["independent_physical_model_validations"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("review evidence checks failed: " + ", ".join(failed))

    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty_state = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    return {
        "review_comment_id": 6681813880,
        "reviewed_head": REVIEWED_HEAD,
        "audit_worktree_head": current_head,
        "working_tree_dirty_at_audit": bool(dirty_state),
        "audit_scope": "Static checks of saved ngspice decks/logs and report/calculation metadata. No new SPICE run and no physical acceptance.",
        "checks": checks,
        "family1_ovp": {
            "original_deck": f"{REVIEWED_HEAD}:reports/g1/sim/family1-ovp-independent-latch.cir",
            "original_tdelay_uses_outside_param": old_tdelay_uses,
            "corrected_deck": "sim/family1-ovp-independent-latch.cir",
            "corrected_tdelay_uses_outside_param": f1_tdelay_uses,
            "o1_peak_V": f1_value,
            "limit_V": 12.0,
            "model_margin_mV": (12.0 - f1_value) * 1000.0,
            "candidate_high_side_short_proof": "OPEN: family 1 is not the family 2 buck-short topology; no selected component models/corners.",
        },
        "family2_buck_highside_short": {
            "o1_peak_V": f2_o1,
            "bus_peak_V": f2_bus,
            "phase_current_peak_A": f2_phase,
            "criterion": "FAIL: O1 peak exceeds 12.0 V; independent candidate OVP absent.",
        },
        "family4_load_step": {
            "deck": "sim/family4-load-step-minc_lowcomp.cir",
            "load_step_A": [f4_initial_load_a, f4_step_load_a],
            "measurement_window_ms": [10.0, 12.0],
            "bus_min_V": f4_min,
            "bus_min_time_ms": f4_min_time_s * 1000.0,
            "minimum_after_step_us": (f4_min_time_s - f4_high_step_time_s) * 1e6,
            "bus_recover_V": f4_recover,
            "minimum_below_10p78V_mV": (f4_floor - f4_min) * 1000.0,
            "criterion": "FAIL retained; time is inside the measurement window. Silicon loop cause remains OPEN.",
        },
        "wp2_uvlo": {
            "historical_re_evaluation": "161 PASS / 69 FAIL / 6 incomplete; unchanged",
            "g1_static_174k_10k_candidate": "Not evidence for dynamic WP2 timing/restart gates.",
            "dynamic_gates": "OPEN",
        },
        "calculation_two_path_review": calc_validation,
        "existing_efuse_capacity_screen": calc["port_capacity_screen"],
        "physical_acceptance": "NOT PERFORMED",
    }


def main() -> None:
    data = build_verification()
    path = OUT / "pr2-review-verification.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path.relative_to(ROOT)), "checks_passed": len(data["checks"]), "audit_scope": data["audit_scope"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
