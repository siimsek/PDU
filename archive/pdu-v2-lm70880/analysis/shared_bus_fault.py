"""Reproducible shared-bus overvoltage fault screens for G1 / PR #2.

These decks are behavioral screens.  They do not model TPS25982 silicon or
the selected comparator/FET chain.  Original Family-2 evidence is read only;
new decks and logs use distinct filenames.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "g1"
SIM_DIR = REPORT_DIR / "sim"
ORIGINAL_DECK = SIM_DIR / "family2-buck-short-independent-ovp-final-10uF-7A.cir"
OUT_JSON = REPORT_DIR / "shared-bus-ovp-results.json"

VTRIP = 11.623168833598632
T_OFF_S = 325.4e-9
# Exact formula outputs retained in reports/g1/calc-results.json; these are
# nominal current-limit estimates, not guaranteed channel minima.
O1_NOMINAL_ILIM_A = 4.9604983388704325
S2E_NOMINAL_ILIM_A = 2.5272185430463576
S2E_WORKING_MAX_A_12V = 0.22
S2E_START_MAX_A_12V = 1.5
S2E_SPEC_MIN_V = 9.0
S2E_SPEC_MAX_V = 28.0
TPS25982_RECOMMENDED_MAX_V = 24.0
TPS25982_ABS_MAX_V = 30.0
TPS1686_OVP_MIN_V = 1.11
TPS1686_OVP_TYP_V = 1.17
TPS1686_OVP_MAX_V = 1.20


def required_capacitance_uF(current_a: float, delay_s: float,
                            initial_v: float, limit_v: float) -> float:
    """Ideal constant-current charge bound C >= I*t/dV, returned in uF."""
    if current_a < 0 or delay_s < 0 or limit_v <= initial_v:
        raise ValueError("require I >= 0, t >= 0, and Vlimit > Vinitial")
    if current_a == 0 or delay_s == 0:
        return 0.0
    return current_a * delay_s / (limit_v - initial_v) * 1e6


def load_current_at(voltage_v: float, resistance_ohm: float) -> float:
    if voltage_v < 0 or resistance_ohm <= 0:
        raise ValueError("voltage must be nonnegative and resistance positive")
    return voltage_v / resistance_ohm


def tps1686_ovlo_threshold_bounds(nominal_trip_v: float,
                                  divider_tolerance: float = 0.01) -> tuple[float, float]:
    """Threshold corners relative to a divider set at 1.17 V nominal OVLO."""
    if nominal_trip_v <= 0 or not 0 <= divider_tolerance < 1:
        raise ValueError("nominal threshold must be positive and tolerance in [0, 1)")
    divider_min = (1 - divider_tolerance) / (1 + divider_tolerance)
    divider_max = (1 + divider_tolerance) / (1 - divider_tolerance)
    low = nominal_trip_v * TPS1686_OVP_MIN_V / TPS1686_OVP_TYP_V * divider_min
    high = nominal_trip_v * TPS1686_OVP_MAX_V / TPS1686_OVP_TYP_V * divider_max
    return low, high


def tps1686_min_high_corner_for_steady_bus(steady_max_v: float) -> float:
    """Infimum high trip corner if the low trip corner must clear steady max."""
    return steady_max_v * TPS1686_OVP_MAX_V / TPS1686_OVP_MIN_V


def parse_measures(log_text: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for match in re.finditer(r"^\s*([a-z][a-z0-9_]*)\s*=\s*([-+0-9.eE]+)",
                             log_text, re.MULTILINE | re.IGNORECASE):
        result[match.group(1).lower()] = float(match.group(2))
    return result


def _integrator(name: str, node_expr: str, threshold_v: float) -> str:
    tag = name.upper()
    return "\n".join((
        f"BINT_{tag} 0 T_{tag} I=if({node_expr}>{threshold_v},1u,0)",
        f"CT_{tag} T_{tag} 0 1u IC=0",
        f"RT_{tag} T_{tag} 0 1T",
        f".meas tran {tag}_DURATION_S FIND V(T_{tag}) AT=2m",
    ))


def build_existing_overload_duration_deck() -> str:
    """Add non-loading threshold-time integrators to an unchanged source deck."""
    text = ORIGINAL_DECK.read_text(encoding="utf-8")
    text = text.replace(
        "* Family-2 buck high-side short plus O1 branch OVP candidate timing screen.",
        "* Derived measurement copy: historical overload stress; source deck preserved.",
        1,
    )
    additions = "\n".join((
        _integrator("U3_GT24", "V(VOUT)", TPS25982_RECOMMENDED_MAX_V),
        _integrator("U4_GT24", "V(VOUT)", TPS25982_RECOMMENDED_MAX_V),
        _integrator("U3_GT30", "V(VOUT)", TPS25982_ABS_MAX_V),
        _integrator("U4_GT30", "V(VOUT)", TPS25982_ABS_MAX_V),
        ".meas tran U3_IN_PEAK MAX V(VOUT) FROM=1m TO=2m",
        ".meas tran U4_IN_PEAK MAX V(VOUT) FROM=1m TO=2m",
    ))
    return text.replace(".tran 10n 2m 0 20n uic", additions + "\n.tran 10n 2m 0 20n uic", 1)


def build_common_isolator_deck(s2e_current_a: float, case_name: str) -> str:
    """Common latched series disconnect before the U3/U4 IN split."""
    total_i = O1_NOMINAL_ILIM_A + s2e_current_a
    source_pre_fault_v = 11.0 + 0.03245 * total_i
    return f"""* G1 shared bus OVP: common disconnect ahead of both TPS25982 IN groups.
* Behavioral component/timing screen only; no physical result.
.param VTRIP={VTRIP:.12g} TDELAY={T_OFF_S:.12g} CLATCH=1n CBUK=92.6514u
Vshort VIN 0 PWL(0 {source_pre_fault_v:.12g} 999u {source_pre_fault_v:.12g} 1m 26 2m 26)
Rcoil VIN LNODE 0.03245
Lfault LNODE VRAW 5.44u IC={total_i:.12g}
CBUS VRAW 0 {{CBUK}} IC=11
Rbleed VRAW 0 1k
VSW_SENSE VRAW VRAW_SW 0
Sbus VRAW_SW VSAFE CTRL_BUS 0 OVPSW
Clatch_BUS CTRL_BUS 0 {{CLATCH}} IC=1
Rlatch_BUS CTRL_BUS 0 1T
Btrip_BUS CTRL_BUS 0 I=if(V(VRAW)>VTRIP,CLATCH*(1-0.45)/TDELAY,0)
.model OVPSW SW(Ron=5.6m Roff=1T Vt=0.5 Vh=0.05)
* Exported-netlist input caps: two 100 nF parts; BOM/derating not established.
CEFIN1 VSAFE 0 100n IC=11
CEFIN2 VSAFE 0 100n IC=11
* Existing branch eFuse behavioral switches; not TPS25982 silicon.
Sefuse_O1 VSAFE O1 CTRL_EF1 0 EFUSESW
Clatch_EF1 CTRL_EF1 0 10n IC=1
Rlatch_EF1 CTRL_EF1 0 1T
Btrip_EF1 CTRL_EF1 0 I=if(V(VSAFE)>16.32,1m,0)
Sefuse_S2E VSAFE S2E CTRL_EF2 0 EFUSESW
Clatch_EF2 CTRL_EF2 0 10n IC=1
Rlatch_EF2 CTRL_EF2 0 1T
Btrip_EF2 CTRL_EF2 0 I=if(V(VSAFE)>16.32,1m,0)
.model EFUSESW SW(Ron=10m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT1 O1 0 10u IC=11
CEFOUT2 S2E 0 10u IC=11
* VARSAYIM: O1 branch at configured nominal ILIM; actual port current unmeasured.
BLOAD_O1 O1 0 I={O1_NOMINAL_ILIM_A:.12g}*min(max(V(O1)/11,0),1)
* DATASHEET: S2E steady/start-up max at 12 V, held constant as sensitivity only.
BLOAD_S2E S2E 0 I={s2e_current_a:.12g}*min(max(V(S2E)/11,0),1)
.ic V(VRAW)=11 V(VSAFE)=11 V(O1)=10.9 V(S2E)=10.9
.tran 10n 2m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran RAW_PEAK MAX V(VRAW) FROM=1m TO=2m
.meas tran U3_IN_PEAK MAX V(VSAFE) FROM=1m TO=2m
.meas tran U4_IN_PEAK MAX V(VSAFE) FROM=1m TO=2m
.meas tran O1_PEAK MAX V(O1) FROM=1m TO=2m
.meas tran S2E_PEAK MAX V(S2E) FROM=1m TO=2m
.meas tran PHASE_CURRENT_PEAK MAX I(Lfault) FROM=1m TO=2m
.meas tran COMMON_SWITCH_BRANCH_I_PEAK MAX I(VSW_SENSE) FROM=1m TO=1.02m
.meas tran COMMON_SWITCH_I_AT_TRIP FIND I(VSW_SENSE) WHEN V(VRAW)=VTRIP RISE=1
.meas tran COMMON_SWITCH_I_AT_OPEN FIND I(VSW_SENSE) WHEN V(CTRL_BUS)=0.45 FALL=1
.meas tran O1_MIN MIN V(O1) FROM=1m TO=2m
.meas tran S2E_MIN MIN V(S2E) FROM=1m TO=2m
.meas tran BUS_TRIP WHEN V(VRAW)=VTRIP RISE=1
.meas tran BUS_OPEN WHEN V(CTRL_BUS)=0.45 FALL=1
.meas tran BUS_T_OFF TRIG V(VRAW) VAL=VTRIP RISE=1 TARG V(CTRL_BUS) VAL=0.45 FALL=1
{_integrator("CAND_U3_GT24", "V(VSAFE)", TPS25982_RECOMMENDED_MAX_V)}
{_integrator("CAND_U4_GT24", "V(VSAFE)", TPS25982_RECOMMENDED_MAX_V)}
{_integrator("CAND_U3_GT30", "V(VSAFE)", TPS25982_ABS_MAX_V)}
{_integrator("CAND_U4_GT30", "V(VSAFE)", TPS25982_ABS_MAX_V)}
.end
"""


def build_high_voltage_efuse_deck(s2e_current_a: float,
                                  s2e_trip_v: float = 24.0) -> str:
    """TPS1686 adjustable OVLO concept; 3 us is its datasheet minimum only."""
    total_i = O1_NOMINAL_ILIM_A + s2e_current_a
    delay = 3e-6
    source_pre_fault_v = 11.0 + 0.03245 * total_i
    return f"""* TPS1686 high-voltage eFuse concept: input withstand plus port OVLO.
* 3 us is a published minimum tOVP; no maximum is specified, so this is not WC.
.param TOvp={delay:.12g} CLATCH=1n CBUK=92.6514u
Vshort VIN 0 PWL(0 {source_pre_fault_v:.12g} 999u {source_pre_fault_v:.12g} 1m 26 2m 26)
Rcoil VIN LNODE 0.03245
Lfault LNODE VRAW 5.44u IC={total_i:.12g}
CBUS VRAW 0 {{CBUK}} IC=11
Rbleed VRAW 0 1k
* 80 V rated eFuse candidate sees the raw bus directly.
* OVLO thresholds are ideal nominal screens, not selected divider corners.
Sefuse_O1 VRAW O1 CTRL_O1 0 EFUSESW
Clatch_O1 CTRL_O1 0 {{CLATCH}} IC=1
Rlatch_O1 CTRL_O1 0 1T
Btrip_O1 CTRL_O1 0 I=if(V(VRAW)>11.3,CLATCH*(1-0.45)/TOvp,0)
Sefuse_S2E VRAW S2E CTRL_S2E 0 EFUSESW
Clatch_S2E CTRL_S2E 0 {{CLATCH}} IC=1
Rlatch_S2E CTRL_S2E 0 1T
Btrip_S2E CTRL_S2E 0 I=if(V(VRAW)>{s2e_trip_v:.12g},CLATCH*(1-0.45)/TOvp,0)
.model EFUSESW SW(Ron=16m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT1 O1 0 10u IC=11
CEFOUT2 S2E 0 10u IC=11
BLOAD_O1 O1 0 I={O1_NOMINAL_ILIM_A:.12g}*min(max(V(O1)/11,0),1)
BLOAD_S2E S2E 0 I={s2e_current_a:.12g}*min(max(V(S2E)/11,0),1)
.ic V(VRAW)=11 V(O1)=11 V(S2E)=11
.tran 10n 2m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran RAW_PEAK MAX V(VRAW) FROM=1m TO=2m
.meas tran O1_PEAK MAX V(O1) FROM=1m TO=2m
.meas tran S2E_PEAK MAX V(S2E) FROM=1m TO=2m
.meas tran PHASE_CURRENT_PEAK MAX I(Lfault) FROM=1m TO=2m
.meas tran O1_TRIP WHEN V(VRAW)=11.3 RISE=1
.meas tran S2E_TRIP WHEN V(VRAW)={s2e_trip_v:.12g} RISE=1
{_integrator("HV_U3_GT24", "V(VRAW)", TPS25982_RECOMMENDED_MAX_V)}
{_integrator("HV_U3_GT30", "V(VRAW)", TPS25982_ABS_MAX_V)}
.end
"""


def run_case(name: str, deck_text: str, ngspice: Path) -> dict:
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    deck = SIM_DIR / f"{name}.cir"
    log = SIM_DIR / f"{name}.log"
    deck.write_text(deck_text, encoding="utf-8", newline="\n")
    try:
        proc = subprocess.run([str(ngspice), "-D", "ngbehavior=ltpsa", "-b",
                               "-o", str(log), str(deck)],
                              cwd=SIM_DIR, capture_output=True, text=True, timeout=120)
        log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        return {
            "deck": str(deck.relative_to(ROOT)).replace("\\", "/"),
            "log": str(log.relative_to(ROOT)).replace("\\", "/"),
            "exit_code": proc.returncode,
            "completed": proc.returncode == 0 and "No. of Data Rows" in log_text,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "measures": parse_measures(log_text),
            "raw_log": log_text,
        }
    except Exception as exc:  # keep runner failure visible in the results JSON
        return {"deck": str(deck.relative_to(ROOT)).replace("\\", "/"),
                "log": str(log.relative_to(ROOT)).replace("\\", "/"),
                "exit_code": None, "completed": False,
                "error": repr(exc), "measures": {}}


def run_all(ngspice: Path | None = None) -> dict:
    if ngspice is None:
        env = os.environ.get("PDU_NGSPICE")
        ngspice = Path(env) if env else Path(r"F:\Spice64\bin\ngspice_con.exe")

    cases = [
        run_case("family2-shared-bus-duration-legacy-overload-final-measures",
                 build_existing_overload_duration_deck(), ngspice),
        run_case("family2-common-bus-isolator-s2e-steady-branch-current-meas",
                 build_common_isolator_deck(S2E_WORKING_MAX_A_12V, "steady"), ngspice),
        run_case("family2-common-bus-isolator-s2e-startup-branch-current-meas",
                 build_common_isolator_deck(S2E_START_MAX_A_12V, "startup"), ngspice),
        run_case("family2-tps1686-hv-efuse-screen-s2e-startup-ovlo24-final-measures",
                 build_high_voltage_efuse_deck(S2E_START_MAX_A_12V, 24.0), ngspice),
    ]

    cap_rows = []
    common_startup = next((c for c in cases if "startup-branch-current-meas" in c["deck"]), {})
    model_switch_peak_a = common_startup.get("measures", {}).get("common_switch_branch_i_peak")
    cap_currents = [("7.5A total capacity target", 7.5),
                    ("legacy combined overload stress", 12.0063694268),
                    ("legacy inductor/phase-current screen, not port current", 67.7984)]
    if model_switch_peak_a is not None:
        cap_currents.append(("corrected common-isolator startup deck branch peak", model_switch_peak_a))
    for label, current in cap_currents:
        cap_rows.append({
            "label": label,
            "fault_current_A": current,
            "existing_common_trip_high_V": VTRIP,
            "allowed_peak_for_O1_V": 12.0,
            "ceff_min_for_O1_uF": required_capacitance_uF(current, T_OFF_S, VTRIP, 12.0),
            "ceff_min_for_TPS25982_IN_absmax_uF": required_capacitance_uF(current, T_OFF_S, VTRIP, TPS25982_ABS_MAX_V),
            "ceff_min_for_TPS25982_IN_recommended_uF": required_capacitance_uF(current, T_OFF_S, VTRIP, TPS25982_RECOMMENDED_MAX_V),
        })
    tps1686_nominal_ovlo = 11.3
    ovlo_low, ovlo_high = tps1686_ovlo_threshold_bounds(tps1686_nominal_ovlo)
    allowed_window_low_v = 11.1605
    allowed_window_high_v = 12.0
    branch_peak_vs_efuse_limit = None
    if model_switch_peak_a is not None:
        nominal_limit_sum = O1_NOMINAL_ILIM_A + S2E_NOMINAL_ILIM_A
        branch_peak_vs_efuse_limit = {
            "model_branch_peak_A": model_switch_peak_a,
            "configured_nominal_ILIM_sum_A": nominal_limit_sum,
            "model_peak_excess_A": model_switch_peak_a - nominal_limit_sum,
            "model_peak_excess_percent": (model_switch_peak_a / nominal_limit_sum - 1) * 100,
            "interpretation": "diagnostic only: behavioral eFuse switches do not implement current limiting; not a hardware fault-current margin",
        }
    return {
        "classification": "behavioral SPICE and calculation screens only; no physical measurement",
        "sources": {
            "TPS25982": "TI TPS25982 Rev D (May 2026) p.7: 24 V recommended max, 30 V absolute max",
            "S2E": "SLAMTEC RPLIDAR S2E v1.5 p.12: 9-28 V, 0.22 A working max and 1.5 A start max at 12 V",
            "TPS1686": "TI TPS1686 Rev A (Nov 2025) p.7/p.9: 9-80 V operating, 92 V abs max; external OVP tOVP minimum 3 us, no maximum",
        },
        "load_classification": {
            "original_deck_O1_at_11V_A": load_current_at(11, 1.57),
            "original_deck_S2E_at_11V_A": load_current_at(11, 2.2),
            "original_deck_total_A": load_current_at(11, 1.57) + load_current_at(11, 2.2),
            "legacy_classification": "overload stress / outside configured operating envelope; original deck and log preserved",
            "configured_eFuse_nominal_total_A": O1_NOMINAL_ILIM_A + S2E_NOMINAL_ILIM_A,
            "nominal_gap_to_7p5A_A": 7.5 - (O1_NOMINAL_ILIM_A + S2E_NOMINAL_ILIM_A),
            "S2E_actual_load_current_not_measured": True,
            "O1_actual_load_current_not_measured": True,
            "startup_duration": "not specified by cited S2E datasheet; constant 1.5 A deck is sensitivity screen only",
            "load_model": "current sink scales from zero at 0 V to the requested current at 11 V; it is a behavioral load, not a measured S2E load waveform",
        },
        "calculated_ceff_bounds": cap_rows,
        "branch_peak_vs_efuse_limit_screen": branch_peak_vs_efuse_limit,
        "tps1686_high_voltage_efuse_screen": {
            "candidate_orderable_mpn": "TPS16861NLMR (candidate only; latch-off selection must be confirmed)",
            "operating_input_range_V": [9.0, 80.0],
            "absolute_max_input_V": 92.0,
            "ovlo_threshold_nominal_V": tps1686_nominal_ovlo,
            "assumed_divider_tolerance": 0.01,
            "ovlo_corner_low_V": ovlo_low,
            "ovlo_corner_high_V": ovlo_high,
            "min_high_corner_if_low_corner_exceeds_steady_bus_V": tps1686_min_high_corner_for_steady_bus(allowed_window_low_v),
            "required_trip_window_V": [allowed_window_low_v, allowed_window_high_v],
            "threshold_window_feasible_before_dynamic_overshoot": tps1686_min_high_corner_for_steady_bus(allowed_window_low_v) <= allowed_window_high_v,
            "published_external_ovp_response": "minimum 3 us; maximum not specified",
            "variant_mapping_note": "TI datasheet comparison table §4 p.3 maps TPS16861 to latch-off; §7.3.4.2 p.22 prose reverses TPS16860/61 for circuit-breaker behavior. Confirm exact variant with TI before selection.",
            "stock": "not verified",
        },
        "cases": cases,
        "physical_test": "NOT PERFORMED",
        "preserved_failures": {
            "family2_original_O1_18p8039V_FAIL": True,
            "family4_bus_10p7109V_FAIL": True,
            "WP1_WP2_open_failures_preserved": True,
        },
    }


def main() -> int:
    result = run_all()
    serializable = json.loads(json.dumps(result, default=str))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(serializable, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT_JSON),
        "cases": [{"deck": c["deck"], "completed": c["completed"],
                   "exit_code": c["exit_code"], "measures": c.get("measures", {})}
                  for c in result["cases"]],
    }, indent=2))
    return 0 if all(c.get("completed") for c in result["cases"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
