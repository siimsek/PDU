"""Run the switch-edge measurement and two Family-2 combined OVP corners.

These are targeted reruns of existing G1 families, not extra DOE families.
The vendor devices are represented by a datasheet-parameterized delay and an
ideal controlled switch; this is intentionally logged as a behavioral screen.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from ovp_component_analysis import OUT, build_results


ROOT = Path(__file__).resolve().parents[1]
DEST = OUT / "sim"
NGSPICE = Path(r"F:\Spice64\bin\ngspice_con.exe")
MEASURE_RE = re.compile(r"(?im)^\s*([a-z0-9_]+)\s*=\s*([+-]?[0-9.]+(?:e[+-]?\d+)?)")


def timing_deck() -> str:
    return """* Measure switch-edge timing in preserved Family-1 ideal latch model.
* Model's CTRL falling threshold is Vt-Vh=0.45 V; not a physical switch.
.param VTRIP=11.46 COUT=10u TDELAY=0.5u CLATCH=1n VSWITCH=0.5
Vfault SOURCE 0 PWL(0 11 4.999m 11 5m 16.9 5.2m 16.9 5.201m 11 6m 11)
Rsource SOURCE PRE 0.54
VSW_SENSE PRE PRE_SW 0
Sdisconnect PRE_SW O1 CTRL 0 IDEALSW
Clatch CTRL 0 {CLATCH} IC=1
Rlatch CTRL 0 1T
Btrip CTRL 0 I=if(V(O1)>VTRIP,CLATCH*VSWITCH/TDELAY,0)
.model IDEALSW SW(Ron=10m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT O1 0 {COUT}
Rload O1 0 1Meg
.ic V(O1)=11
.tran 10n 6m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran O1_PEAK MAX V(O1) FROM=4.9m TO=5.2m
.meas tran OVP_TRIP WHEN V(O1)=VTRIP RISE=1
.meas tran CTRL_OPEN WHEN V(CTRL)=0.45 FALL=1
.meas tran OVP_TOFF TRIG V(O1) VAL=VTRIP RISE=1 TARG V(CTRL) VAL=0.45 FALL=1
.meas tran OVP_TO_CURRENT_OFF TRIG V(O1) VAL=VTRIP RISE=1 TARG I(VSW_SENSE) VAL=1m FALL=1
.meas tran I_BEFORE_OFF FIND I(VSW_SENSE) AT=5.0005m
.meas tran I_AFTER_OFF FIND I(VSW_SENSE) AT=5.1m
.end
"""


def combined_deck(c_eff_uF: float, threshold_v: float, total_delay_s: float, load_ohm: float) -> str:
    tdelay_ns = total_delay_s * 1e9
    return f"""* Family-2 buck high-side short plus O1 branch OVP candidate timing screen.
* Shared VOUT still feeds S2E. eFuse circuit-breaker current dynamics are not modeled.
* Comparator/latch/driver delay is folded into TDELAY; FETs are Ron/Roff switches.
.param VTRIP={threshold_v:.12g} CBUK=92.6514u COUT={c_eff_uF:.12g}u
.param TDELAY={tdelay_ns:.12g}n CLATCH=1n VSWITCH=0.5
Vshort VIN 0 PWL(0 11 999u 11 1m 26 2m 26)
Rcoil VIN LNODE 0.03245
Lfault LNODE VOUT 5.44u IC=0
CBUS VOUT 0 {{CBUK}} IC=11
Rbleed VOUT 0 1k
Sefuse VOUT PRE CTRL_EF 0 EFUSESW
Clatch_EF CTRL_EF 0 10n IC=1
Rlatch_EF CTRL_EF 0 1T
Btrip_EF CTRL_EF 0 I=if(V(VOUT)>16.32,1m,0)
.model EFUSESW SW(Ron=10m Roff=1T Vt=0.5 Vh=0.05)
VSW_SENSE PRE PRE_OVP 0
Sdisconnect PRE_OVP O1 CTRL_OVP 0 OVPSW
Clatch_OVP CTRL_OVP 0 {{CLATCH}} IC=1
Rlatch_OVP CTRL_OVP 0 1T
Btrip_OVP CTRL_OVP 0 I=if(V(O1)>VTRIP,CLATCH*(1-0.45)/TDELAY,0)
.model OVPSW SW(Ron=5.6m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT O1 0 {{COUT}} IC=10.9
Rload1 O1 0 {load_ohm:.12g}
Sefuse_S2E VOUT S2E CTRL_S2E 0 EFUSESW
Clatch_S2E CTRL_S2E 0 10n IC=1
Rlatch_S2E CTRL_S2E 0 1T
Btrip_S2E CTRL_S2E 0 I=if(V(VOUT)>16.32,1m,0)
CEFOUT_S2E S2E 0 10u IC=10.9
Rload_S2E S2E 0 2.2
.ic V(VOUT)=11 V(O1)=10.9 V(S2E)=10.9
.tran 10n 2m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran BUS_PEAK MAX V(VOUT) FROM=1m TO=2m
.meas tran O1_PEAK MAX V(O1) FROM=1m TO=2m
.meas tran S2E_PEAK MAX V(S2E) FROM=1m TO=2m
.meas tran PHASE_CURRENT MAX I(Lfault) FROM=1m TO=2m
.meas tran OVP_I_PEAK MAX I(VSW_SENSE) FROM=1m TO=1.2m
.meas tran OVP_TRIP WHEN V(O1)=VTRIP RISE=1
.meas tran CTRL_OPEN WHEN V(CTRL_OVP)=0.45 FALL=1
.meas tran OVP_TOFF TRIG V(O1) VAL=VTRIP RISE=1 TARG V(CTRL_OVP) VAL=0.45 FALL=1
.meas tran OVP_TO_CURRENT_OFF TRIG V(O1) VAL=VTRIP RISE=1 TARG I(VSW_SENSE) VAL=1m FALL=1
.end
"""


def execute(deck_path: Path) -> dict:
    log_path = deck_path.with_suffix(".log")
    if not NGSPICE.is_file():
        return {"deck": deck_path.name, "log": log_path.name, "completed": False,
                "exit_code": None, "error": f"ngspice not found at {NGSPICE}", "measures": {}}
    proc = subprocess.run(
        [str(NGSPICE), "-D", "ngbehavior=ltpsa", "-b", "-o", str(log_path), str(deck_path)],
        cwd=ROOT / "simulation", capture_output=True, text=True, timeout=120, check=False,
    )
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else proc.stdout + proc.stderr
    values = {m.group(1).lower(): float(m.group(2)) for m in MEASURE_RE.finditer(log)}
    completed = proc.returncode == 0 and bool(values) and "run simulation(s) aborted" not in log.lower()
    return {"deck": deck_path.name, "log": str(log_path.relative_to(ROOT)),
            "completed": completed, "exit_code": proc.returncode,
            "error": None if completed else (proc.stderr or "ngspice failed or measurements missing"),
            "measures": values}


def write_deck_preserving(path: Path, deck: str) -> bool:
    """Write a deck; archive both sides first if replacing existing evidence."""
    if path.exists() and path.read_text(encoding="ascii") == deck:
        return False
    if path.exists() or path.with_suffix(".log").exists():
        index = 1
        while (path.with_name(f"{path.stem}-attempt{index}.cir").exists()
               or path.with_name(f"{path.stem}-attempt{index}.log").exists()):
            index += 1
        if path.exists():
            shutil.copy2(path, path.with_name(f"{path.stem}-attempt{index}.cir"))
        if path.with_suffix(".log").exists():
            shutil.copy2(path.with_suffix(".log"), path.with_name(f"{path.stem}-attempt{index}.log"))
    path.write_text(deck, encoding="ascii")
    return True


def read_existing(deck_path: Path) -> dict:
    log_path = deck_path.with_suffix(".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    values = {m.group(1).lower(): float(m.group(2)) for m in MEASURE_RE.finditer(log)}
    completed = bool(values) and "run simulation(s) aborted" not in log.lower()
    return {"deck": deck_path.name, "log": str(log_path.relative_to(ROOT)),
            "completed": completed, "exit_code": 0 if completed else None,
            "error": None if completed else "existing evidence log missing or incomplete",
            "measures": values, "reused_existing_log": True}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    calc = build_results()
    threshold = calc["threshold"]["enumerated_max_V"]
    total_delay = calc["timing"]["estimated_total_toff_ns"] * 1e-9
    timing_path = DEST / "family1-switch-off-measurement.cir"
    changed_timing = write_deck_preserving(timing_path, timing_deck())
    timing_case = execute(timing_path) if changed_timing or not timing_path.with_suffix(".log").exists() else read_existing(timing_path)
    case_paths = []
    scenarios = (("10uF-7A", 10.0, 1.57), ("4uF-no-load", 4.0, 1e12))
    for label, c_eff, load_ohm in scenarios:
        path = DEST / f"family2-buck-short-independent-ovp-final-{label}.cir"
        changed = write_deck_preserving(path, combined_deck(c_eff, threshold, total_delay, load_ohm))
        case_paths.append((path, changed, label, c_eff, load_ohm))

    cases = [timing_case]
    for path, changed, label, c_eff, load_ohm in case_paths:
        case = execute(path) if changed or not path.with_suffix(".log").exists() else read_existing(path)
        case["scenario"] = label
        case["ceff_uF"] = c_eff
        case["O1_load_ohm"] = load_ohm
        cases.append(case)
    data = {
        "classification": "SİM behavioral screen; not component-transistor model and not physical measurement",
        "budget": "targeted rerun of existing Family 1 and Family 2; no sixth G1 condition family",
        "prior_uncalibrated_run_preserved": [
            "reports/g1/sim/family2-buck-short-independent-ovp-10uF.cir/.log",
            "reports/g1/sim/family2-buck-short-independent-ovp-4uF.cir/.log",
        ],
        "prior_run_note": "The first two combined decks used the old 1.1x control-slope equation and are retained as superseded calibration runs, not counted as final model results.",
        "prior_calibrated_loaded_sensitivity_preserved": "reports/g1/sim/family2-buck-short-independent-ovp-calibrated-4uF.cir/.log; not treated as a worst-case no-load corner",
        "component_corner_inputs": {
            "threshold_high_V": threshold,
            "summed_delay_estimate_ns_not_guaranteed": calc["timing"]["estimated_total_toff_ns"],
            "mosfet_pair_ron_ohm": 0.0056,
            "mosfet_model": "ideal switch with datasheet-screened on-resistance and calculated delay; SOA/gate waveform are absent",
            "efuse_model": "ideal 16.32 V OVP switch; current-limit/fast-trip current dynamics excluded",
            "capacitor_corners_uF": [10.0, 4.0],
            "capacitor_esr_esl": "zero in deck as optimistic bound; actual values are open",
        },
        "cases": cases,
        "physical_measurement": "NOT PERFORMED: no assembled board or oscilloscope acquisition exists in workspace",
        "family2_original_18p8039V_fail_preserved": True,
        "family4_10p7109V_fail_preserved": True,
    }
    for case in cases[1:]:
        peak = case["measures"].get("o1_peak") if case["completed"] else None
        case["criterion_O1_le_12V"] = bool(peak is not None and peak <= 12.0)
        current_peak = case["measures"].get("ovp_i_peak") if case["completed"] else None
        if current_peak is not None:
            current_screen = calc["fault_current"]["fast_trip_current_screen_A"]
            case["current_margin_to_provisional_fast_trip_screen_A"] = current_screen - current_peak
            case["current_margin_is_guaranteed"] = False
            current_off = case["measures"].get("ovp_to_current_off")
            case["series_current_off_measurement_valid"] = current_off is not None and current_off >= 0
            case["switch_open_time_source"] = (
                "series current below 1 mA after trip"
                if case["series_current_off_measurement_valid"]
                else "control-threshold timing only; series current was already below 1 mA in the selected window"
            )
        case["ceff_vs_ideal_charge_balance_screen"] = (
            "below provisional Ceff minimum; model result is not worst-case evidence"
            if case["ceff_uF"] < calc["ceff"]["ceff_min_charge_balance_uF"]
            else "at/above provisional Ceff minimum; parasitic and current-envelope limits remain open"
        )
        case["status"] = "within 12.0 V in this behavioral screen only; design acceptance BLOCKED" if case["criterion_O1_le_12V"] else (
            "FAIL in behavioral screen" if peak is not None and peak > 12.0 else "INCOMPLETE — no acceptance")
    timing = cases[0]
    if timing["completed"]:
        mm = timing["measures"]
        timing["measured_trip_to_control_threshold_s"] = mm.get("ovp_toff")
        timing["measured_trip_to_series_current_below_1mA_s"] = mm.get("ovp_to_current_off")
        timing["separate_crossing_measurement_delta_s"] = mm.get("ctrl_open", 0) - mm.get("ovp_trip", 0)
        timing["analytical_expected_off_s"] = 0.55e-6
        if timing["measured_trip_to_series_current_below_1mA_s"] is not None:
            current_off = timing["measured_trip_to_series_current_below_1mA_s"]
            timing["measurement_minus_analytic_ns"] = (current_off - 0.55e-6) * 1e9
            timing["measurement_minus_analytic_percent"] = (current_off / 0.55e-6 - 1.0) * 100.0
        timing["physical_measurement"] = False

    out = OUT / "ovp-component-sim.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"result": out.relative_to(ROOT).as_posix(),
                      "cases": [{"deck": c["deck"], "completed": c["completed"],
                                 "measures": c["measures"], "status": c.get("status", "measured ideal-model edge")} for c in cases]},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
