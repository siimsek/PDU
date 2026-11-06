"""R7 OVP timing, threshold, BJT-drive and pin-map screens.

These calculations use published component limits where the test conditions
match, and explicit assumptions everywhere else. They do not model silicon or
constitute O1 physical acceptance.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "reports" / "g1" / "ovp-r7-calculations.json"

VREF_NOM_V = 2.5
VREF_INITIAL_TOL = 0.001
VREF_TCR_PER_C = 8e-6
VREF_T0_C = 25.0
TEMP_MIN_C = -40.0
TEMP_MAX_C = 125.0
RESISTOR_TOL = 0.01
R_SENSE_TOP_OHM = 17_950.0
R_SENSE_BOTTOM_OHM = 5_000.0
TLV1701_VOS_MAX_V = 6.3e-3
LTC6752_H_VOS_MAX_V = 9e-3

V5_NOM_V = 5.0
V12_NOM_V = 12.0
LDO_OUTPUT_ASSUMED_TOL = 0.02
R_CLR_PULLUP_OHM = 10_000.0
R_INP_SERIES_OHM = 1_000.0
R_CLAMP_BASE_OHM = 22_000.0
R_RELEASE_BASE_OHM = 62_000.0
R_TOL = 0.01
MMBT3904_VBE_SCREEN_MIN_V = 0.65
MMBT3904_VBE_SCREEN_MAX_V = 0.95
MMBT3904_VCESAT_SCREEN_MAX_V = 0.30
# Worst-case sink into CLR_N: two TPS7A16-Q1 PG pins (1 uA each) and
# TLV1701-Q1 open-collector leakage (70 nA). These are manufacturer limits.
CLR_NODE_SINK_LEAKAGE_A = 2.07e-6

FET_QG_MAX_C = 153e-9
FET_QG_TEST_V = 10.0
FET_COUNT = 2
LTC7001_R_TGDN_MAX_OHM = 4.0
GATE_OFF_SCREEN_V = 2.1
GATE_INITIAL_V = 10.0
LATCH_CLR_TO_Q_MAX_S = 6.1e-9
LTC7001_INP_TO_TGDN_MAX_S = 70e-9
TLV1701_TPHL_TYP_S = 460e-9
LTC6752_H_TPD_MAX_S = 5.7e-9
LTC7001_CG_EXTERNAL_F = 0.0

O1_LIMIT_V = 12.0
O1_FAULT_CURRENT_ASSUMED_A = 10.0
O1_CEFF_ASSUMED_F = 10e-6
TIMING_SCREEN_S = 0.5e-6


def reference_corners() -> tuple[float, float]:
    """REF5025A-Q1 initial accuracy plus max TCR to either temperature end."""
    max_delta_c = max(abs(TEMP_MIN_C - VREF_T0_C), abs(TEMP_MAX_C - VREF_T0_C))
    total_fraction = VREF_INITIAL_TOL + VREF_TCR_PER_C * max_delta_c
    return VREF_NOM_V * (1 - total_fraction), VREF_NOM_V * (1 + total_fraction)


def divider_threshold_corners(vos_abs_max_v: float) -> dict[str, float]:
    """Corner span with ±1% divider parts; resistor TCR is not selected."""
    vref_min, vref_max = reference_corners()
    rtop_min = R_SENSE_TOP_OHM * (1 - RESISTOR_TOL)
    rtop_max = R_SENSE_TOP_OHM * (1 + RESISTOR_TOL)
    rbot_min = R_SENSE_BOTTOM_OHM * (1 - RESISTOR_TOL)
    rbot_max = R_SENSE_BOTTOM_OHM * (1 + RESISTOR_TOL)
    return {
        "nominal_V": VREF_NOM_V * (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM) / R_SENSE_BOTTOM_OHM,
        "minimum_V": (vref_min - vos_abs_max_v) * (rtop_min + rbot_max) / rbot_max,
        "maximum_V": (vref_max + vos_abs_max_v) * (rtop_max + rbot_min) / rbot_min,
        "assumed_resistor_tolerance_fraction": RESISTOR_TOL,
        "unmodeled_resistor_TCR": True,
        "unmodeled_input_bias_and_leakage": True,
    }


def divider_threshold_corner_enumeration(vos_abs_max_v: float) -> tuple[float, float]:
    """Independent endpoint enumeration for the four scalar corner inputs."""
    vref_min, vref_max = reference_corners()
    rtop = (R_SENSE_TOP_OHM * (1 - RESISTOR_TOL), R_SENSE_TOP_OHM * (1 + RESISTOR_TOL))
    rbottom = (R_SENSE_BOTTOM_OHM * (1 - RESISTOR_TOL), R_SENSE_BOTTOM_OHM * (1 + RESISTOR_TOL))
    vrefs = (vref_min, vref_max)
    offsets = (-vos_abs_max_v, vos_abs_max_v)
    corners = [
        (vref + offset) * (rt + rb) / rb
        for vref in vrefs
        for offset in offsets
        for rt in rtop
        for rb in rbottom
    ]
    return min(corners), max(corners)


def gate_charge_screen_time_s() -> float:
    """Datasheet-Qg-to-capacitance RC screen, not a guaranteed FET turn-off."""
    ceq_total = FET_COUNT * FET_QG_MAX_C / FET_QG_TEST_V
    tau = LTC7001_R_TGDN_MAX_OHM * ceq_total
    return tau * math.log(GATE_INITIAL_V / GATE_OFF_SCREEN_V)


def required_bootstrap_capacitance_f() -> float:
    """LTC7001 CB inequality evaluated with two CSD19536KTT max Qg values."""
    total_qg = FET_COUNT * FET_QG_MAX_C
    return total_qg / 1.0 + 10.0 * LTC7001_CG_EXTERNAL_F


def time_to_comparator_overdrive_s(input_overdrive_v: float, fault_a: float, ceff_f: float) -> float:
    """Constant-current bus ramp translated through the OVP divider."""
    divider_gain = R_SENSE_BOTTOM_OHM / (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM)
    input_diff_slope_v_per_s = divider_gain * fault_a / ceff_f
    return input_overdrive_v / input_diff_slope_v_per_s


def time_to_comparator_overdrive_charge_balance_s(input_overdrive_v: float, fault_a: float, ceff_f: float) -> float:
    """Charge-balance route to the same overdrive under constant-current assumptions."""
    divider_gain = R_SENSE_BOTTOM_OHM / (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM)
    bus_delta_v = input_overdrive_v / divider_gain
    return ceff_f * bus_delta_v / fault_a


def max_delay_for_o1_v(vtrip_max_v: float, fault_a: float, ceff_f: float) -> float:
    """Constant-current charge balance; negative means threshold exceeds limit."""
    return (O1_LIMIT_V - vtrip_max_v) * ceff_f / fault_a


def bjt_drive_screen() -> dict[str, float | str]:
    """Resistive screening corners; VBE/VCE values are outside exact load points."""
    v5_min = V5_NOM_V * (1 - LDO_OUTPUT_ASSUMED_TOL)
    v5_max = V5_NOM_V * (1 + LDO_OUTPUT_ASSUMED_TOL)
    v12_min = V12_NOM_V * (1 - LDO_OUTPUT_ASSUMED_TOL)
    v12_max = V12_NOM_V * (1 + LDO_OUTPUT_ASSUMED_TOL)

    rclamp_min = R_CLAMP_BASE_OHM * (1 - R_TOL)
    rclamp_max = R_CLAMP_BASE_OHM * (1 + R_TOL)
    rrelease_min = R_RELEASE_BASE_OHM * (1 - R_TOL)
    rrelease_max = R_RELEASE_BASE_OHM * (1 + R_TOL)
    rpull_min = R_CLR_PULLUP_OHM * (1 - R_TOL)
    rpull_max = R_CLR_PULLUP_OHM * (1 + R_TOL)
    rinp_min = R_INP_SERIES_OHM * (1 - R_TOL)

    clamp_ib_min = (v12_min - MMBT3904_VBE_SCREEN_MAX_V) / rclamp_max
    clamp_ib_max = (v12_max - MMBT3904_VBE_SCREEN_MIN_V) / rclamp_min
    inp_ic_max = (v5_max - MMBT3904_VCESAT_SCREEN_MAX_V) / rinp_min
    clamp_forced_beta = inp_ic_max / clamp_ib_min

    clr_ib_min = (
        v5_min - MMBT3904_VBE_SCREEN_MAX_V - rpull_max * CLR_NODE_SINK_LEAKAGE_A
    ) / (rpull_max + rrelease_max)
    clr_high_min = v5_min - rpull_max * (clr_ib_min + CLR_NODE_SINK_LEAKAGE_A)
    latch_vih_min = 0.7 * v5_min
    release_ic_max = clamp_ib_max
    release_forced_beta = release_ic_max / clr_ib_min

    return {
        "assumption_5V_range_V": [v5_min, v5_max],
        "assumption_12V_range_V": [v12_min, v12_max],
        "assumed_resistor_tolerance_fraction": R_TOL,
        "MMBT3904_VBE_screen_V": [MMBT3904_VBE_SCREEN_MIN_V, MMBT3904_VBE_SCREEN_MAX_V],
        "MMBT3904_VCEsat_screen_max_V": MMBT3904_VCESAT_SCREEN_MAX_V,
        "CLR_node_sink_leakage_A": CLR_NODE_SINK_LEAKAGE_A,
        "CLR_node_sink_leakage_breakdown_A": {
            "TPS7A1650QDGNRQ1_PG": 1.0e-6,
            "TPS7A1601QDGNRQ1_PG": 1.0e-6,
            "TLV1701QDBVRQ1_open_collector": 70e-9,
        },
        "Q_INP_CLAMP_base_current_A": [clamp_ib_min, clamp_ib_max],
        "Q_INP_CLAMP_INP_collector_current_max_A": inp_ic_max,
        "Q_INP_CLAMP_forced_beta_max": clamp_forced_beta,
        "Q_INP_RELEASE_base_current_min_A": clr_ib_min,
        "Q_INP_RELEASE_collector_current_max_A": release_ic_max,
        "Q_INP_RELEASE_forced_beta_max": release_forced_beta,
        "CLR_N_high_min_V_with_release_base_load": clr_high_min,
        "SN74LVC1G74_VIH_min_at_VCC_min_V": latch_vih_min,
        "CLR_N_high_margin_over_VIH_V": clr_high_min - latch_vih_min,
        "status": "SCREEN ONLY: MMBT3904 saturation values are specified at 10mA/1mA and 50mA/5mA, not this sub-mA load; resistor MPN/TCR and rail sequencing are unresolved.",
    }


def pin_connection_table() -> list[dict[str, str]]:
    """One textual pin map; PG_OK and CLR_N are intentionally one physical node."""
    return [
        {"ref_pin": "U_OVP TLV1701QDBVRQ1 pin 1 IN+", "net": "VREF_2V5", "connect": "U_REF REF5025AQDRQ1 pin 6 VOUT"},
        {"ref_pin": "U_OVP pin 2 V−", "net": "GND", "connect": "ground plane"},
        {"ref_pin": "U_OVP pin 3 IN−", "net": "VRAW_SENSE", "connect": "R_SENSE_TOP 17.95k from VRAW; R_SENSE_BOTTOM 5.00k to GND"},
        {"ref_pin": "U_OVP pin 4 OUT open collector", "net": "CLR_N = PG_OK", "connect": "wired low-dominant with U5/U12 PG and U_LATCH pin 6; one 10k pull-up to +5V"},
        {"ref_pin": "U_OVP pin 5 V+", "net": "+12V_DRIVER", "connect": "U12 TPS7A1601QDGNRQ1 output pin 1"},
        {"ref_pin": "U_REF REF5025AQDRQ1 pin 2 VIN", "net": "+5V", "connect": "U5 TPS7A1650QDGNRQ1 output pin 1"},
        {"ref_pin": "U_REF pin 3 TEMP", "net": "NC", "connect": "leave open"},
        {"ref_pin": "U_REF pin 4 GND", "net": "GND", "connect": "ground"},
        {"ref_pin": "U_REF pin 5 TRIM/NR", "net": "REF_NR", "connect": "1uF to GND per candidate wiring; verify exact reference application circuit"},
        {"ref_pin": "U_REF pin 7 NC; pins 1,8 DNC", "net": "NC/DNC", "connect": "leave as datasheet specifies"},
        {"ref_pin": "U5 TPS7A1650QDGNRQ1 pin 3 PG", "net": "CLR_N = PG_OK", "connect": "open-drain; low when 5V rail is below PG threshold while VIN≥3V"},
        {"ref_pin": "U12 TPS7A1601QDGNRQ1 pin 3 PG", "net": "CLR_N = PG_OK", "connect": "open-drain; low when 12V rail is below PG threshold while VIN≥3V"},
        {"ref_pin": "R_CLR 10k", "net": "CLR_N to +5V", "connect": "single common pull-up only"},
        {"ref_pin": "U_LATCH SN74LVC1G74DCUR pin 1 CLK", "net": "ARM_CLK", "connect": "B3U-1000P momentary switch to +5V; 100k pull-down to GND"},
        {"ref_pin": "U_LATCH pin 2 D", "net": "+5V", "connect": "logic high for manual ARM rising edge"},
        {"ref_pin": "U_LATCH pin 3 Qbar", "net": "NC", "connect": "unused"},
        {"ref_pin": "U_LATCH pin 4 GND", "net": "GND", "connect": "ground"},
        {"ref_pin": "U_LATCH pin 5 Q", "net": "INP_CMD", "connect": "1k series resistor to U_DRIVER LTC7001EMSE#PBF pin 4 INP; Q_INP_CLAMP collector also joins INP"},
        {"ref_pin": "U_LATCH pin 6 CLR", "net": "CLR_N = PG_OK", "connect": "same node as comparator OUT and both open-drain PG pins"},
        {"ref_pin": "U_LATCH pin 7 PRE", "net": "PRE_N", "connect": "10k pull-up to +5V; never join CLR_N"},
        {"ref_pin": "U_LATCH pin 8 VCC", "net": "+5V", "connect": "U5 output"},
        {"ref_pin": "Q_INP_CLAMP MMBT3904LT1G pin 1 B", "net": "CLAMP_B", "connect": "22k from +12V_DRIVER"},
        {"ref_pin": "Q_INP_CLAMP pin 2 E", "net": "GND", "connect": "ground"},
        {"ref_pin": "Q_INP_CLAMP pin 3 C", "net": "INP_CMD", "connect": "U_DRIVER pin 4 INP"},
        {"ref_pin": "Q_INP_RELEASE MMBT3904LT1G pin 1 B", "net": "CLR_N = PG_OK", "connect": "62k base resistor from the common node"},
        {"ref_pin": "Q_INP_RELEASE pin 2 E", "net": "GND", "connect": "ground"},
        {"ref_pin": "Q_INP_RELEASE pin 3 C", "net": "CLAMP_B", "connect": "sinks Q_INP_CLAMP base when rails are healthy"},
        {"ref_pin": "U_DRIVER LTC7001EMSE#PBF pin 1 VCC", "net": "+12V_DRIVER", "connect": "U12 output; 100nF local bypass"},
        {"ref_pin": "U_DRIVER pin 2 VCCUV", "net": "GND", "connect": "select minimum rising UVLO; do not count UVLO as a timing guarantee"},
        {"ref_pin": "U_DRIVER pin 3 GND", "net": "GND", "connect": "ground"},
        {"ref_pin": "U_DRIVER pin 4 INP", "net": "INP_CMD", "connect": "latch Q through1k and Q_INP_CLAMP collector"},
        {"ref_pin": "U_DRIVER pin 5 OVLO", "net": "GND", "connect": "unused; tie low"},
        {"ref_pin": "U_DRIVER pin 6 TGDN", "net": "GATE1/GATE2", "connect": "common active pull-down to TS; each FET gate has 10k gate-to-source bleed"},
        {"ref_pin": "U_DRIVER pin 7 TGUP", "net": "GATE1/GATE2", "connect": "individual 10Ω turn-on resistor to each gate"},
        {"ref_pin": "U_DRIVER pin 8 TS", "net": "TS", "connect": "Q1/Q2 common-source node"},
        {"ref_pin": "U_DRIVER pin 9 BST", "net": "BST", "connect": ">306nF effective BST-to-TS for two FETs, before any CG contribution; 0.1uF is insufficient; select capacitor by bias/tolerance later"},
        {"ref_pin": "U_DRIVER pin 10 NC; EP pin 11", "net": "NC/GND", "connect": "pin 10 open; exposed pad to GND per package guidance"},
        {"ref_pin": "Q1/Q2 CSD19536KTTT pin 1 G", "net": "GATE1/GATE2", "connect": "individual TGUP resistor; common TGDN node; separate 10k to each source"},
        {"ref_pin": "Q1 CSD19536KTTT pin 2 D/tab", "net": "VRAW", "connect": "upstream side of common disconnect"},
        {"ref_pin": "Q2 CSD19536KTTT pin 2 D/tab", "net": "VSAFE", "connect": "downstream side / eFuse IN bus"},
        {"ref_pin": "Q1/Q2 CSD19536KTTT pin 3 S", "net": "TS", "connect": "tie both sources together"},
    ]


def build_results() -> dict[str, Any]:
    tlv = divider_threshold_corners(TLV1701_VOS_MAX_V)
    ltc = divider_threshold_corners(LTC6752_H_VOS_MAX_V)
    tlv_enum = divider_threshold_corner_enumeration(TLV1701_VOS_MAX_V)
    ltc_enum = divider_threshold_corner_enumeration(LTC6752_H_VOS_MAX_V)
    gate_t = gate_charge_screen_time_s()
    cb_min_f = required_bootstrap_capacitance_f()
    tlv_illustrative = TLV1701_TPHL_TYP_S + LATCH_CLR_TO_Q_MAX_S + LTC7001_INP_TO_TGDN_MAX_S + gate_t
    ltc_conditional = LTC6752_H_TPD_MAX_S + LATCH_CLR_TO_Q_MAX_S + LTC7001_INP_TO_TGDN_MAX_S + gate_t
    tlv_overdrive_build = time_to_comparator_overdrive_s(100e-3, O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F)
    ltc_overdrive_build = time_to_comparator_overdrive_s(50e-3, O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F)
    tlv_timing_including_overdrive = tlv_overdrive_build + tlv_illustrative
    ltc_timing_including_overdrive = ltc_overdrive_build + ltc_conditional
    tlv_overdrive_charge = time_to_comparator_overdrive_charge_balance_s(100e-3, O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F)
    ltc_overdrive_charge = time_to_comparator_overdrive_charge_balance_s(50e-3, O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F)
    return {
        "classification": "HESAP + DATASHEET extraction + VARSAYIM; no physical or silicon-level PASS",
        "starting_head": "17945c5cba258f33face4c7fee56f28370597d2f",
        "comparator_candidates": [
            {
                "mpn": "TLV1701QDBVRQ1",
                "manufacturer": "Texas Instruments",
                "package": "SOT-23-5",
                "lifecycle": "TI orderable MPN shown ACTIVE; inventory/stock not queried",
                "supply_range_V": [2.2, 36.0],
                "input_common_mode": "V− to V+ (rail-to-rail)",
                "input_offset_abs_max_V": TLV1701_VOS_MAX_V,
                "propagation": {"published_typical_pHL_s": TLV1701_TPHL_TYP_S, "published_typical_pLH_s": 560e-9, "guaranteed_max_s": None, "conditions": "100mV overdrive, CL=15pF, RPULLUP=5.1kΩ, 25°C; maximum column blank"},
                "fault_input_at_40p709V_V": 40.709 * R_SENSE_BOTTOM_OHM / (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM),
                "fault_input_valid_with_12V_rail": True,
                "rail_loss": "No guaranteed comparator output state with V+ absent found; U12 PG can clear only while its datasheet VIN conditions hold.",
                "threshold_corners": tlv,
                "decision": "Wide-input monitor candidate; not a timing-qualified sole OVP because tPD(max) is unspecified.",
            },
            {
                "mpn": "LTC6752HMS8-2#TRPBF",
                "manufacturer": "Analog Devices",
                "package": "8-lead MSOP",
                "lifecycle": "ADI product page lists PRODUCTION; inventory/stock not queried; no automotive qualification claim used",
                "supply_range_V": {"VCC_input": [2.45, 5.25], "VDD_output": [1.71, 3.5]},
                "input_common_mode_at_VCC_5V": [-0.2, 5.1],
                "input_offset_abs_max_V": LTC6752_H_VOS_MAX_V,
                "propagation": {"published_max_s": LTC6752_H_TPD_MAX_S, "conditions": "H grade, VCC=5V, VDD=1.8V, CL=5pF, 50mV overdrive, datasheet common-mode test setup VCM=300mV; actual candidate threshold common mode is about 2.5V; no max is stated for zero overdrive or guaranteed at this actual VCM"},
                "fault_input_at_40p709V_V": 40.709 * R_SENSE_BOTTOM_OHM / (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM),
                "fault_input_over_operating_common_mode_at_40p709V_V": 40.709 * R_SENSE_BOTTOM_OHM / (R_SENSE_TOP_OHM + R_SENSE_BOTTOM_OHM) - 5.1,
                "rail_loss": "Two supply pins permit either sequencing, but no valid fault-output state with both supplies absent is guaranteed; VDD=1.8V output needs level translation to the 5V CLR_N net.",
                "threshold_corners": ltc,
                "decision": "Fast comparator candidate only with a new fault-input clamp and 1.8V-to-5V low-dominant interface; not drop-in.",
            },
        ],
        "calculation_cross_checks": {
            "threshold_corner_method_1": "closed-form monotonic endpoints",
            "threshold_corner_method_2": "enumerate all 16 combinations of VREF, offset, Rtop and Rbottom endpoints",
            "TLV1701_corner_min_abs_difference_V": abs(tlv["minimum_V"] - tlv_enum[0]),
            "TLV1701_corner_max_abs_difference_V": abs(tlv["maximum_V"] - tlv_enum[1]),
            "LTC6752_corner_min_abs_difference_V": abs(ltc["minimum_V"] - ltc_enum[0]),
            "LTC6752_corner_max_abs_difference_V": abs(ltc["maximum_V"] - ltc_enum[1]),
            "overdrive_method_1": "comparator differential slew from I/C bus slope and divider gain",
            "overdrive_method_2": "capacitor charge needed for bus delta divided by fault current",
            "TLV1701_overdrive_time_abs_difference_s": abs(tlv_overdrive_build - tlv_overdrive_charge),
            "LTC6752_overdrive_time_abs_difference_s": abs(ltc_overdrive_build - ltc_overdrive_charge),
            "scope": "Independent calculation algorithms/formulations over the same assumptions; not independent silicon or physical validation.",
        },
        "timing": {
            "gate_charge_screen": {"Qg_max_C_per_FET": FET_QG_MAX_C, "test_VGS_V": FET_QG_TEST_V, "Ceq_proxy_total_F": FET_COUNT * FET_QG_MAX_C / FET_QG_TEST_V, "TGDN_R_max_ohm_at_VCC_BST_12V": LTC7001_R_TGDN_MAX_OHM, "time_10V_to_2p1V_proxy_s": gate_t, "status": "RC proxy only; not a guaranteed two-FET discharge time"},
            "LTC7001_bootstrap": {"formula": "CB > total_Qg/1V + 10*CG", "two_FET_Qg_max_C": FET_COUNT * FET_QG_MAX_C, "external_CG_assumed_F": LTC7001_CG_EXTERNAL_F, "required_Ceff_F": cb_min_f, "candidate_0p1uF_satisfies": 0.1e-6 > cb_min_f, "status": "DATASHEET inequality evaluated at Qg maximum; no selected capacitor or DC-bias derating yet"},
            "TLV1701_chain": {"illustrative_sum_s": tlv_illustrative, "input_overdrive_build_to_100mV_s_under_assumptions": tlv_overdrive_build, "conditional_sum_including_overdrive_s": tlv_timing_including_overdrive, "sum_terms": {"comparator_typical": TLV1701_TPHL_TYP_S, "SN74LVC1G74_CLR_to_Q_max": LATCH_CLR_TO_Q_MAX_S, "LTC7001_INP_to_TGDN_max_at_1nF": LTC7001_INP_TO_TGDN_MAX_S, "two_FET_gate_charge_RC_proxy": gate_t}, "below_0p5us_screen": tlv_timing_including_overdrive < TIMING_SCREEN_S, "worst_case_status": "OPEN: comparator has no guaranteed tPD(max), its 100mV test overdrive builds after threshold crossing, driver load differs, and gate proxy is not a bound"},
            "LTC6752_chain": {"conditional_sum_s": ltc_conditional, "input_overdrive_build_to_50mV_s_under_assumptions": ltc_overdrive_build, "conditional_sum_including_overdrive_s": ltc_timing_including_overdrive, "sum_terms": {"comparator_published_max_at_50mV_overdrive_and_VCM_0p3V": LTC6752_H_TPD_MAX_S, "SN74LVC1G74_CLR_to_Q_max": LATCH_CLR_TO_Q_MAX_S, "LTC7001_INP_to_TGDN_max_at_1nF": LTC7001_INP_TO_TGDN_MAX_S, "two_FET_gate_charge_RC_proxy": gate_t}, "below_0p5us_screen": ltc_timing_including_overdrive < TIMING_SCREEN_S, "O1_budget_remaining_after_conditional_sum_s": max_delay_for_o1_v(ltc["maximum_V"], O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F) - ltc_timing_including_overdrive, "worst_case_status": "OPEN: 50mV comparator max is published at VCM=300mV, not the candidate's about 2.5V; that overdrive builds after threshold; conditional sum exceeds O1 charge budget under assumptions and still omits input clamp, output translation, driver-load mismatch and FET turn-off guarantee"},
            "O1_limit": {"criterion_V": O1_LIMIT_V, "fault_current_assumption_A": O1_FAULT_CURRENT_ASSUMED_A, "Ceff_assumption_F": O1_CEFF_ASSUMED_F, "TLV_trip_max_V_under_declared_assumptions": tlv["maximum_V"], "TLV_max_total_trip_to_current_interruption_s": max_delay_for_o1_v(tlv["maximum_V"], O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F), "TLV_time_to_100mV_overdrive_s": tlv_overdrive_build, "LTC_trip_max_V_under_declared_assumptions": ltc["maximum_V"], "LTC_max_total_trip_to_current_interruption_s": max_delay_for_o1_v(ltc["maximum_V"], O1_FAULT_CURRENT_ASSUMED_A, O1_CEFF_ASSUMED_F), "LTC_time_to_50mV_overdrive_s": ltc_overdrive_build, "0p5us_screen_s": TIMING_SCREEN_S, "status": "Conditional constant-current charge balance only; actual I_fault(t), Ceff_min, ESR/ESL, clamp delay, measurement uncertainty and O1 transient remain OPEN. 0.5us screen is not substituted for O1≤12.0V."},
        },
        "bjt_screen": bjt_drive_screen(),
        "single_node_definition": "CLR_N and PG_OK are the same copper node; it has one 10k pull-up to +5V and joins both TPS7A16-Q1 PG open-drains, TLV1701-Q1 OUT, latch CLR, and Q_INP_RELEASE base through 62k. Sink leakage screen is 1uA + 1uA + 70nA; PG behavior is specified only while each LDO VIN is at least 3V.",
        "pin_connection_table": pin_connection_table(),
        "efuse_manufacturer_evidence": {
            "part": "TPS259824O",
            "datasheet": "TI TPS25982 Rev D, §6.1 p.6 and §6.3 p.7",
            "input_abs_max_V": 30.0,
            "output_max_abs_V": "min(30V, VIN + 0.3V)",
            "recommended_vin_V": [2.7, 24.0],
            "reverse_current_or_input_loss_behavior": "No explicit guaranteed reverse-current, reverse-blocking, or input-loss OUT discharge behavior identified in datasheet text. OUT≤VIN+0.3V is an absolute maximum boundary, not an internal protective action guarantee.",
            "official_model": {"name": "TPS259824O PSpice Transient Model SLVMD37", "model_version": "Final 1.30", "date": "24APR2019", "simulator": "PSpice 16.2", "encrypted": True, "modeled_features": ["startup into pre-biased output", "current limit", "IMON", "OV/UV", "dV/dt", "PG/Fault", "thermal shutdown time"], "omitted_features": ["temperature dependence", "input supply current vs input voltage in normal operation", "input supply current vs input voltage at shutdown"], "local_simulator_available": False, "status": "Official model was retrieved and its readable header inspected; encrypted model could not be run locally (PSpice/Cadence not installed). It is not a production guarantee."},
            "r6_fixture_sequence": "In the CO_OPEN negative fixture the ideal common switch and ideal eFuse paths are forced open at 900us; the RAW fault ramp begins at 1ms. This is precharged/input-loss stress only, not real detection/turn-off sequencing.",
            "status": "OPEN: behavioral fixture remains conditional; actual TPS259824O silicon reverse current, UVLO and differential transient response unverified.",
        },
        "preserved_status": {
            "Family2_O1_18p8039V": "FAIL retained",
            "Family4_bus_10p7109V": "FAIL retained",
            "common_bus_TPS25982_IN_40p709V": "FAIL retained",
            "O1_peak_le_12V": "OPEN; physical measurement not performed",
            "normal_bus_le_11p1605V": "OPEN",
            "R6_passive_gate_bleed_0p5us_fixture": "FAIL retained as behavioral screen only; not a device prediction",
            "WP1": "4 ESL incomplete; N-01 open",
            "WP2": "69 FAIL / 6 incomplete",
            "physical_gate_turnoff_and_FET_SOA": "OPEN",
        },
        "decision": "NO FEASIBLE GUARANTEED OVP CHAIN YET",
        "physical_acceptance": False,
    }


def main() -> int:
    result = build_results()
    RESULT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": RESULT_PATH.relative_to(ROOT).as_posix(),
        "decision": result["decision"],
        "TLV_threshold_max_V": result["comparator_candidates"][0]["threshold_corners"]["maximum_V"],
        "LTC_threshold_max_V": result["comparator_candidates"][1]["threshold_corners"]["maximum_V"],
        "TLV_timing_sum_ns_illustrative": result["timing"]["TLV1701_chain"]["illustrative_sum_s"] * 1e9,
        "LTC_timing_sum_ns_conditional": result["timing"]["LTC6752_chain"]["conditional_sum_s"] * 1e9,
        "Q_release_forced_beta": result["bjt_screen"]["Q_INP_RELEASE_forced_beta_max"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
