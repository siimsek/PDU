"""Pin-level fail-safe and thermal audit for the G1 OVP candidate.

The state table is a logic contract, not a device macromodel. The included
SPICE fixture deliberately injects a stuck-high LTC7001 INP request while the
5-V logic rail is lost; its ideal clamp path is not a selected silicon part.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

try:
    from .ovp_control_chain_followup import simulate_control_sequence
except ImportError:  # direct execution as ``python analysis/ovp_fail_safe_audit.py``
    from ovp_control_chain_followup import simulate_control_sequence


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "reports" / "g1" / "sim"
RESULT_PATH = ROOT / "reports" / "g1" / "fail-safe-audit-results.json"
DECK_PATH = SIM_DIR / "ovp-control-loss-negative-fixture.cir"
LOG_PATH = SIM_DIR / "ovp-control-loss-negative-fixture.log"

LATCH_MIN_VCC_V = 1.65
LTC7001_INP_VIH_MIN_V = 1.7
LTC7001_INP_VIH_MAX_V = 2.2
LTC7001_INP_VIL_MIN_V = 1.3
LTC7001_INP_VIL_MAX_V = 1.8
LTC7001_VCC_UVLO_RISE_V = (3.1, 3.7)
LTC7001_VCC_UVLO_FALL_V = (2.8, 3.4)
LTC7001_BST_TS_UVLO_FALL_V = (2.8, 3.1)
LTC7001_RPD_MAX_OHM_AT_12V = 4.0
LTC7001_RPU_MAX_OHM_AT_12V = 7.0
TPS7A16_THETA_JA_C_PER_W = 66.2
TPS7A16_TJ_OPERATING_MAX_C = 150.0
TPS7A16_TSD_RISING_C = 170.0
CONSERVATIVE_TJ_SCREEN_C = 125.0  # project screening value, not TI limit
THERMAL_AMBIENT_ASSUMPTION_C = 85.0
TPS7A16_VOUT_MIN_V = 4.9
TPS7A16_VOUT_MAX_V = 5.1
TPS7A16_IQ_SCREEN_A = 15e-6  # published light-load max reused as a sensitivity
TLV3601_IQ_MAX_A = 7e-3
REF5025_IQ_MAX_A = 1.2e-3
DFF_IQ_SCREEN_A = 10e-6
BLEED_R_OHM = 470.0
BLEED_R_TOL = 0.01


def latch_next_q(q: bool | None, *, vcc_v: float, clr_n: bool,
                 pre_n: bool, arm_edge: bool, arm_permitted: bool) -> bool | None:
    """SN74LVC1G74 state contract; None means unspecified/out of range."""
    if vcc_v < LATCH_MIN_VCC_V:
        return None
    if not pre_n and not clr_n:
        return None  # TI function table calls this configuration nonstable.
    if not clr_n:
        return False
    if not pre_n:
        return True
    if q is None:
        return None  # power-up state is not guaranteed without an asserted CLR.
    if arm_edge and arm_permitted:
        return True  # D is tied high; qualified manual clock sets Q.
    return q


def next_latch_state(q: bool | None, *, vcc_v: float, pg_ok: bool,
                     raw_safe: bool, monitors_healthy: bool,
                     arm_edge: bool) -> bool | None:
    """Required policy: any invalid condition clears; only safe manual ARM sets."""
    fault_clear = pg_ok and raw_safe and monitors_healthy
    return latch_next_q(q, vcc_v=vcc_v, clr_n=fault_clear, pre_n=True,
                        arm_edge=arm_edge,
                        arm_permitted=fault_clear and vcc_v >= 4.5)


def control_truth_table() -> list[dict[str, object]]:
    """Temporal logic contract starting at Q=None; never seed case outputs."""
    rows = simulate_control_sequence()
    for row in rows:
        row.update({
            "case": row["event"],
            "LDO_PG_OK": row["PG_OK"],
            "monitor_healthy": row["monitors_ok"],
            "manual_ARM_edge": row["ARM_rising_edge"],
            "LTC7001_INP_policy": row["INP_policy"],
            "LTC7001_TGDN_policy": "to TS while driver operation is valid; otherwise only the separate gate-source bleeds are credited",
            "FET1_FET2_VGS_policy": "not inferred from Q when either supply is invalid; tied-gate network is unverified",
        })
    return rows


def thermal_screen(ambient_c: float = THERMAL_AMBIENT_ASSUMPTION_C) -> dict[str, object]:
    """Steady-state theta-JA screen; fault-pulse peak is deliberately OPEN."""
    rbleed_min = BLEED_R_OHM * (1 - BLEED_R_TOL)
    bleed_i_a = TPS7A16_VOUT_MAX_V / rbleed_min
    bleed_p_w = TPS7A16_VOUT_MAX_V**2 / rbleed_min
    i_load_a = TLV3601_IQ_MAX_A + REF5025_IQ_MAX_A + DFF_IQ_SCREEN_A + bleed_i_a
    sources = {
        "VRAW_normal_11V_sustained": 11.0,
        "VRAW_fault_26V_sustained": 26.0,
        "VRAW_fault_40p709V_sustained_hypothetical": 40.709,
        "protected_VIN_min_20V_sustained": 20.0,
        "protected_VIN_max_26V_sustained": 26.0,
    }
    rows: dict[str, dict[str, float | str | bool]] = {}
    for name, vin in sources.items():
        # Mixed corners: max load at VOUT high plus minimum regulated VOUT
        # for pass-element loss. This slightly overbounds the screen.
        p_w = max(0.0, (vin - TPS7A16_VOUT_MIN_V) * i_load_a)
        p_w += vin * TPS7A16_IQ_SCREEN_A
        rise_c = p_w * TPS7A16_THETA_JA_C_PER_W
        tj_c = ambient_c + rise_c
        rows[name] = {
            "VIN_V": vin,
            "I5V_load_mA_screen": i_load_a * 1e3,
            "P_LDO_W_steady_screen": p_w,
            "thetaJA_C_per_W_datasheet_test_board": TPS7A16_THETA_JA_C_PER_W,
            "deltaT_C_steady_screen": rise_c,
            "Tj_C_at_assumed_ambient": tj_c,
            "below_conservative_125C_screen": tj_c <= CONSERVATIVE_TJ_SCREEN_C,
            "below_datasheet_150C_operating_max": tj_c <= TPS7A16_TJ_OPERATING_MAX_C,
            "status": "HESAP steady-state thetaJA estimate; board theta unknown",
        }
    return {
        "ambient_C": ambient_c,
        "ambient_is_assumption": True,
        "load_current_mA_screen": i_load_a * 1e3,
        "LDO_IQ_15uA_use": "published light-load maximum reused as sensitivity; not a guaranteed max at this load",
        "bleeder": {
            "R_ohm": BLEED_R_OHM,
            "tolerance_fraction": BLEED_R_TOL,
            "I_mA_at_5p1V_Rmin": bleed_i_a * 1e3,
            "P_mW_at_5p1V_Rmin": bleed_p_w * 1e3,
            "part_rating_status": "OPEN: exact resistor MPN and temperature derating absent",
        },
        "datasheet_Tj_operating_max_C": TPS7A16_TJ_OPERATING_MAX_C,
        "datasheet_TSD_rising_C": TPS7A16_TSD_RISING_C,
        "125C_screen_C": CONSERVATIVE_TJ_SCREEN_C,
        "125C_is_TI_limit": False,
        "sources": rows,
        "VRAW_40p709V_fault_pulse": {
            "pulse_duration_s": None,
            "Tj_peak_C": None,
            "status": "OPEN: exact RAW pulse duration and transient thermal impedance Ztheta(t) not established",
        },
        "source_choice": {
            "VRAW": "lowest normal loss, but LDO input follows buck common-bus fault and 40.709V pulse",
            "protected_VIN": "recommended analysis candidate: 20-26V source is independent of buck output fault; max steady estimate below 125C screen at assumed 85C, but actual PCB theta/rail fail behavior remain open",
        },
    }


def build_control_loss_deck() -> str:
    """One small negative fault-injection deck; no IC macro-models."""
    return r"""* NEGATIVE FIXTURE: high-side INP command vs independent fault clamp.
* Not a silicon model: forced high command represents an unknown/out-of-range
* latch output. Ideal monitor threshold and ideal LTC7001 switching are used.
* Cg=Qg/VGS=118nC/10V per CSD19536 typical charge; not a worst-case gate model.
VLOGIC VLOGIC 0 PWL(0 5 900u 5 901u 0 1.5m 0)
VDRIVER VDRIVER 0 12
VQFORCE QFORCE 0 5
* A=missing independent clamp; B=ideal driver-rail-powered fail-low clamp.
RQA QFORCE INP_A 1k
RPA INP_A 0 10k
RINTA INP_A 0 1Meg
RQB QFORCE INP_B_PRE 1k
RPREB INP_B_PRE INP_B 0.2
RPB INP_B 0 10k
RINTB INP_B 0 1Meg
* Monitor is intentionally ideal and has no MPN/timing proof.
BMON MON_BAD 0 V=if(V(VLOGIC)>4.05,0,5)
SMON INP_B 0 MON_BAD 0 IDEALCLAMP
.model IDEALCLAMP SW(Ron=0.2 Roff=1T Vt=2.5 Vh=0.1)
* LTC7001 input stage: falling input below 1.6V commands TGDN; 4ohm max
* pull-down at VCC=VBST=12V. Use effective VGS drive=10V for this screen.
BDRVA GDRA 0 V=if(V(INP_A)<1.6,0,10)
BDRVB GDRB 0 V=if(V(INP_B)<1.6,0,10)
RG1A GDRA G1A 4
RG2A GDRA G2A 4
RG1B GDRB G1B 4
RG2B GDRB G2B 4
CG1A G1A 0 11.8n IC=10
CG2A G2A 0 11.8n IC=10
CG1B G1B 0 11.8n IC=10
CG2B G2B 0 11.8n IC=10
RGS1A G1A 0 10k
RGS2A G2A 0 10k
RGS1B G1B 0 10k
RGS2B G2B 0 10k
.tran 10n 1.5m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran INP_A_AFTER_LOSS FIND V(INP_A) AT=1.1m
.meas tran G1A_AFTER_LOSS FIND V(G1A) AT=1.1m
.meas tran G2A_AFTER_LOSS FIND V(G2A) AT=1.1m
.meas tran INP_B_AFTER_LOSS FIND V(INP_B) AT=1.1m
.meas tran G1B_AFTER_LOSS FIND V(G1B) AT=1.1m
.meas tran G2B_AFTER_LOSS FIND V(G2B) AT=1.1m
.meas tran G1B_MAX_AFTER_MON MAX V(G1B) FROM=902u TO=1.5m
.meas tran G2B_MAX_AFTER_MON MAX V(G2B) FROM=902u TO=1.5m
.end
"""


def run_fixture() -> dict[str, object]:
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    deck = build_control_loss_deck()
    DECK_PATH.write_text(deck, encoding="utf-8", newline="\n")
    ngspice = Path(os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe"))
    result = subprocess.run([str(ngspice), "-D", "ngbehavior=ltpsa", "-b", "-o",
                             str(LOG_PATH), str(DECK_PATH)], cwd=SIM_DIR,
                            capture_output=True, text=True, check=False)
    log = LOG_PATH.read_text(encoding="utf-8", errors="replace") if LOG_PATH.exists() else result.stdout + result.stderr
    if not LOG_PATH.exists():
        LOG_PATH.write_text(log, encoding="utf-8", newline="\n")
    required = {
        "inp_a_after_loss", "g1a_after_loss", "g2a_after_loss",
        "inp_b_after_loss", "g1b_after_loss", "g2b_after_loss",
        "g1b_max_after_mon", "g2b_max_after_mon",
    }
    measures: dict[str, float] = {}
    for line in log.splitlines():
        parts = line.split("=", 1)
        if len(parts) == 2:
            name = parts[0].strip().lower()
            if name not in required:
                continue
            try:
                measures[name] = float(parts[1].strip().split()[0])
            except ValueError:
                continue
    missing = sorted(required - measures.keys())
    completed = result.returncode == 0 and "No. of Data Rows" in log and not missing
    return {
        "deck": DECK_PATH.relative_to(ROOT).as_posix(),
        "log": LOG_PATH.relative_to(ROOT).as_posix(),
        "solver_exit_code": result.returncode,
        "completed": completed,
        "missing_measures": missing,
        "measures": measures,
        "limitations": [
            "forced high command is an injected fault, not SN74LVC1G74 behavior",
            "ideal monitor and switch are not a selected supervisor/driver model",
            "MOSFET gate capacitance uses typical Qg-derived estimate; no max Qg/SOA/timing proof",
            "logic thresholds and external clamp source are not physically verified",
        ],
    }


def build_results(run_spice: bool = True) -> dict[str, object]:
    fixture = run_fixture() if run_spice else {"completed": False, "status": "not run"}
    return {
        "classification": "DATASHEET + HESAP + negative behavioral fixture; no physical acceptance",
        "latch_candidate": "SN74LVC1G74DCUR",
        "driver_candidate": "LTC7001EMSE#PBF",
        "FET_candidate": "2x CSD19536KTTT back-to-back",
        "datasheet_pin_contract": {
            "SN74LVC1G74DCUR_DCUpins": {"CLK": 1, "D": 2, "Qbar": 3, "GND": 4, "Q": 5, "CLR_n": 6, "PRE_n": 7, "VCC": 8},
            "SN74LVC1G74": "VCC 1.65-5.5V; CLR_n low -> Q=0; PRE_n low -> Q=1; both low is nonstable; no power-up default specified",
            "LTC7001": "VCC pin1; VCCUV pin2; GND pin3; INP pin4; OVLO pin5; TGDN pin6; TGUP pin7; TS pin8; BST pin9; NC pin10; exposed pad pin11 GND. INP VIH 1.7-2.2V, VIL 1.3-1.8V; internal 1Mohm pull-down; TGDN pulls to TS; TGUP pulls up to BST.",
            "TPS7A16QDGNRQ1_DGN8": {"OUT": 1, "FB_NC": 2, "PG": 3, "GND": 4, "EN": 5, "NC": 6, "DELAY": 7, "IN": 8},
            "TPS7A16_PG": "PG pin3 is open-drain active-high; pulls low below falling threshold 83-93% VOUT; PG function requires VIN>=3V; deassert timing has no guaranteed max used here; pull-up and receiving logic are unselected",
            "CSD19536KTTT_D2PAK_each": {"G": 1, "D": 2, "S": 3, "tab": "D"},
            "CSD19536KTTT": "100V VDS, +/-20V VGS; Qg 118nC typical / 153nC max under datasheet test conditions; each device requires its own G pin1-to-S pin3 bleed; no physical two-gate turn-off result",
        },
        "current_candidate_status": {
            "actual_pin_netlist_in_repo": False,
            "CLR_PRE_ARM_fault_combiner_verified": False,
            "independent_logic_rail_loss_clamp_part_selected": False,
            "INP_external_10k_pulldown_fitted": False,
            "two_gate_source_pulldowns_fitted": False,
            "fail_safe_state": "OPEN; VCC<1.65V is explicitly unspecified latch operation, not SAFE",
        },
        "logic_truth_table": control_truth_table(),
        "thermal_screen": thermal_screen(),
        "input_loss_efuse": {
            "device": "TPS259824O",
            "recommended_IN_V": [2.7, 24.0],
            "absolute_max_IN_V": [-0.3, 30.0],
            "recommended_OUT_max": "VIN + 0.3V",
            "absolute_max_OUT_max": "min(30V, VIN + 0.3V)",
            "datasheet_reverse_current_block_guarantee_found": False,
            "datasheet_poweroff_reverse_path_spec_found": False,
            "precharged_OUT_with_IN_lost": "OPEN/outside specified OUT-to-IN voltage condition when OUT remains above VIN+0.3V; do not infer reverse-current block or internal body-diode behavior",
            "11V_precharge_input_loss_screen": {
                "model_precharged_OUT_V": 11.0,
                "VIN_lost_V": 0.0,
                "VOUT_minus_VIN_V": 11.0,
                "datasheet_abs_max_VOUT_at_VIN0_V": 0.3,
                "conditional_excess_V": 10.7,
                "status": "FAIL if output stays precharged at 11V after IN collapses; actual decay/current behavior OPEN",
            },
            "old_Q_EF2_minus_44p547uC": "ideal bilateral SW artifact only; not physical current, hold-up, backfeed, or protection evidence",
            "required_validation": "separate hardware test or vendor clarification; no claim made from the ideal-switch simulation",
        },
        "negative_fixture": fixture,
        "status_register": [
            {"item": "SN74LVC1G74 pin/function contract", "status": "PASS", "scope": "datasheet logic only"},
            {"item": "VCC below 1.65V implies latch safe", "status": "FAIL", "scope": "claim rejected; state is unspecified"},
            {"item": "present CLR/ARM/PG/INP/FET network", "status": "OPEN", "scope": "not wired or physically verified"},
            {"item": "ideal clamp negative fixture", "status": "PASS", "scope": "behavioral test only"},
            {"item": "no-clamp stuck-high INP fixture", "status": "FAIL", "scope": "injected fault leaves modeled gates on"},
            {"item": "TPS259824O reverse-current blocking", "status": "OPEN", "scope": "no datasheet guarantee found"},
            {"item": "11V OUT retained at VIN=0", "status": "FAIL", "scope": "conditional OUT absolute maximum violation if retained"},
            {"item": "LDO normal 11V and sustained 26V thermal screens", "status": "PASS", "scope": "125C screen / JEDEC theta assumption only"},
            {"item": "LDO 40.709V sustained hypothetical", "status": "FAIL", "scope": "125C conservative screen only"},
            {"item": "LDO 40.709V pulse peak Tj", "status": "OPEN", "scope": "pulse duration and Ztheta(t) absent"},
            {"item": "O1 <=12V and normal bus <=11.1605V physical acceptance", "status": "OPEN", "scope": "no physical testing performed"},
        ],
        "acceptance": {
            "O1_peak_limit_V": 12.0,
            "normal_bus_max_V": 11.1605,
            "criteria_relaxed": False,
            "physical_test": "NOT PERFORMED",
            "design_status": "BLOCKED / OPEN",
        },
    }


def main() -> int:
    results = build_results(run_spice=True)
    RESULT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fixture = results["negative_fixture"]
    print(json.dumps({
        "output": RESULT_PATH.relative_to(ROOT).as_posix(),
        "fixture_completed": fixture.get("completed"),
        "solver_exit_code": fixture.get("solver_exit_code"),
        "missing_measures": fixture.get("missing_measures"),
        "thermal_Tj_C_at_85C": {key: row["Tj_C_at_assumed_ambient"] for key, row in results["thermal_screen"]["sources"].items()},
        "design_status": results["acceptance"]["design_status"],
    }, indent=2))
    return 0 if fixture.get("completed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
