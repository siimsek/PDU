"""Fail-safe OVP sense and shared-isolator charge evidence for PR #2.

The TLV3601 and TLV1851 are represented by datasheet limits in calculations;
neither has a transistor-level ngspice model in this repository. Behavioral
SPICE results are screens, never physical acceptance.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.shared_bus_fault import build_common_isolator_deck

REPORTS = ROOT / "reports" / "g1"
SIM = REPORTS / "sim"
RESULT_JSON = REPORTS / "sense-failsafe-results.json"

VREF = 2.5
RTOP = 17_950.0
RBOT = 5_000.0
R_BLEED = 470.0
R_TOL = 0.001
R_TCR = 25e-6
R_BLEED_TOL = 0.01
VREF_INITIAL = 0.001
VREF_TCR = 8e-6
VREF_LOAD_PPM_PER_MA = 30.0
VREF_LINE_PPM_PER_V = 1.0
TLV3601_VOS = 5e-3
TLV3601_HYST = 5e-3
TLV3601_IB = 5e-6
TLV1851_VOS = 4.4e-3
TLV1851_HYST = 5e-3
TLV1851_IB_MAX = 1.5e-9
TRIP_WINDOW = (11.1605, 12.0)
RAW_CORNERS = (11.0, 26.0, 38.7219, 40.709)
RAIL_CORNERS = (0.0, 2.4, 5.0, 5.5)
CLAMP_OFFSET_V = 0.3
TLV_INPUT_CURRENT_LIMIT_A = 10e-3
TLV3601_POR_V = 2.1
LVC1G74_MIN_V = 1.65
TPS7A16_RAIL_NOM_V = 5.0
TPS7A16_TOL = 0.02
TPS7A16_THETA_JA_C_PER_W = 66.2
TLV3601_IQ_MAX_A = 7e-3
REF5025_IQ_MAX_A = 1.2e-3
TEMP_CORNERS_C = (-40.0, 125.0)

OLD_RTOP = 3_590.0
OLD_RBOT = 1_000.0
OLD_DIVIDER_WITHOUT_SERIES = True


def divider_open_circuit_v(vraw_v: float, rtop_ohm: float, rbot_ohm: float) -> float:
    if vraw_v < 0 or rtop_ohm <= 0 or rbot_ohm <= 0:
        raise ValueError("voltage must be nonnegative and both resistors positive")
    return vraw_v * rbot_ohm / (rtop_ohm + rbot_ohm)


def divider_thevenin_ohm(rtop_ohm: float, rbot_ohm: float) -> float:
    if rtop_ohm <= 0 or rbot_ohm <= 0:
        raise ValueError("both resistors must be positive")
    return rtop_ohm * rbot_ohm / (rtop_ohm + rbot_ohm)


def clamp_current_a(vraw_v: float, vcc_v: float, rtop_ohm: float,
                    rbot_ohm: float, clamp_offset_v: float = CLAMP_OFFSET_V) -> float:
    """KCL solution for an ideal VCC+offset clamp on a divider node."""
    vpin = min(divider_open_circuit_v(vraw_v, rtop_ohm, rbot_ohm), vcc_v + clamp_offset_v)
    current = (vraw_v - vpin) / rtop_ohm - vpin / rbot_ohm
    return max(0.0, current)


def clamp_current_nodal_a(vraw_v: float, vcc_v: float, rtop_ohm: float,
                          rbot_ohm: float, clamp_offset_v: float = CLAMP_OFFSET_V) -> float:
    """Independent nodal solution using conductance balance at the clamp node."""
    clamp_v = vcc_v + clamp_offset_v
    unclamped_v = vraw_v * rbot_ohm / (rtop_ohm + rbot_ohm)
    if unclamped_v <= clamp_v:
        return 0.0
    # At the constrained node, incoming divider current minus the bottom-leg
    # current is the clamp branch current (KCL). This avoids the Thevenin form
    # used by clamp_current_a().
    return max(0.0, (vraw_v - clamp_v) / rtop_ohm - clamp_v / rbot_ohm)


def resistor_corner_values(nominal_ohm: float) -> tuple[float, ...]:
    return tuple(nominal_ohm * (1 + sign * (R_TOL + R_TCR * abs(temp - 25.0)))
                 for temp, sign in itertools.product(TEMP_CORNERS_C, (-1, 1)))


def max_clamp_current_corner_a(vraw_v: float, vcc_v: float,
                               clamp_offset_v: float = CLAMP_OFFSET_V) -> float:
    return max(clamp_current_a(vraw_v, vcc_v, rt, rb, clamp_offset_v)
               for rt in resistor_corner_values(RTOP)
               for rb in resistor_corner_values(RBOT))


def rail_equilibrium_v(vraw_v: float, rtop_ohm: float, rbot_ohm: float,
                       rbleed_ohm: float, clamp_offset_v: float = CLAMP_OFFSET_V) -> float:
    """Closed-form equilibrium when clamp current is sunk by Rbleed."""
    if min(rtop_ohm, rbot_ohm, rbleed_ohm) <= 0:
        raise ValueError("all resistances must be positive")
    gtop, gbot, gbleed = 1 / rtop_ohm, 1 / rbot_ohm, 1 / rbleed_ohm
    numerator = (vraw_v - clamp_offset_v) * gtop - clamp_offset_v * gbot
    return max(0.0, numerator / (gtop + gbot + gbleed))


def rail_equilibrium_bisect_v(vraw_v: float, rtop_ohm: float, rbot_ohm: float,
                              rbleed_ohm: float, clamp_offset_v: float = CLAMP_OFFSET_V) -> float:
    """Independent monotone KCL root solve for the unpowered comparator rail."""
    lo, hi = 0.0, max(vraw_v, 1.0)
    for _ in range(100):
        mid = (lo + hi) / 2
        pin = mid + clamp_offset_v
        injection = max(0.0, (vraw_v - pin) / rtop_ohm - pin / rbot_ohm)
        if injection > mid / rbleed_ohm:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def max_unpowered_rail_equilibrium_corner_v(vraw_v: float) -> float:
    return max(rail_equilibrium_v(vraw_v, rt, rb, rbleed, 0.0)
               for rt in resistor_corner_values(RTOP)
               for rb in resistor_corner_values(RBOT)
               for rbleed in (R_BLEED * (1 + R_BLEED_TOL),))


def max_unpowered_rail_equilibrium_bisect_corner_v(vraw_v: float) -> float:
    return max(rail_equilibrium_bisect_v(vraw_v, rt, rb, rbleed, 0.0)
               for rt in resistor_corner_values(RTOP)
               for rb in resistor_corner_values(RBOT)
               for rbleed in (R_BLEED * (1 + R_BLEED_TOL),))


def threshold_corners(comparator: str = "TLV3601") -> list[dict[str, float]]:
    if comparator == "TLV3601":
        vos, hyst, ib = TLV3601_VOS, TLV3601_HYST, TLV3601_IB
    elif comparator == "TLV1851":
        vos, hyst, ib = TLV1851_VOS, TLV1851_HYST, TLV1851_IB_MAX
    else:
        raise ValueError("unsupported comparator")
    rows: list[dict[str, float]] = []
    for temp_c, ref_sign, rt_sign, rb_sign, vos_sign, hyst_sign, ib_sign in itertools.product(
            TEMP_CORNERS_C, (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1)):
        dt = temp_c - 25.0
        rt = RTOP * (1 + rt_sign * (R_TOL + R_TCR * abs(dt)))
        rb = RBOT * (1 + rb_sign * (R_TOL + R_TCR * abs(dt)))
        # REF5025 load is bounded by the summed maximum comparator input currents.
        load_ma = (TLV3601_IB + TLV1851_IB_MAX) * 1000
        ref_err = VREF_INITIAL + VREF_TCR * abs(dt)
        ref_err += VREF_LOAD_PPM_PER_MA * 1e-6 * load_ma
        ref_err += VREF_LINE_PPM_PER_V * 1e-6 * (5.0 * TPS7A16_TOL)
        vref = VREF * (1 + ref_sign * ref_err)
        rth = divider_thevenin_ohm(rt, rb)
        input_error = vos_sign * vos + hyst_sign * hyst + ib_sign * ib * rth
        ratio = rt / rb
        rows.append({"temperature_C": temp_c, "rtop_ohm": rt, "rbot_ohm": rb,
                     "vref_V": vref, "vtrip_V": (vref + input_error) * (1 + ratio)})
    return rows


def threshold_bounds_interval(comparator: str = "TLV3601") -> tuple[float, float]:
    if comparator == "TLV3601":
        vos, hyst, ib = TLV3601_VOS, TLV3601_HYST, TLV3601_IB
    elif comparator == "TLV1851":
        vos, hyst, ib = TLV1851_VOS, TLV1851_HYST, TLV1851_IB_MAX
    else:
        raise ValueError("unsupported comparator")
    dt = 100.0
    tmax = R_TOL + R_TCR * dt
    ratio_min = RTOP * (1 - tmax) / (RBOT * (1 + tmax))
    ratio_max = RTOP * (1 + tmax) / (RBOT * (1 - tmax))
    load_ma = (TLV3601_IB + TLV1851_IB_MAX) * 1000
    ref_error = VREF_INITIAL + VREF_TCR * dt
    ref_error += VREF_LOAD_PPM_PER_MA * 1e-6 * load_ma
    ref_error += VREF_LINE_PPM_PER_V * 1e-6 * (5.0 * TPS7A16_TOL)
    ref_lo, ref_hi = VREF * (1 - ref_error), VREF * (1 + ref_error)
    rth_hi = divider_thevenin_ohm(RTOP * (1 + tmax), RBOT * (1 + tmax))
    input_error = vos + hyst + ib * rth_hi
    return ((ref_lo - input_error) * (1 + ratio_min),
            (ref_hi + input_error) * (1 + ratio_max))


def build_charge_balance_deck() -> str:
    deck = build_common_isolator_deck(1.5, "startup")
    replacements = {
        "CEFIN1 VSAFE 0 100n IC=11": "V_CEFIN1_SENSE VSAFE CEFIN1_NODE 0\nCEFIN1 CEFIN1_NODE 0 100n IC=11",
        "CEFIN2 VSAFE 0 100n IC=11": "V_CEFIN2_SENSE VSAFE CEFIN2_NODE 0\nCEFIN2 CEFIN2_NODE 0 100n IC=11",
        "Sefuse_O1 VSAFE O1 CTRL_EF1 0 EFUSESW": "V_EFUSE_O1_SENSE VSAFE VSAFE_O1 0\nSefuse_O1 VSAFE_O1 O1 CTRL_EF1 0 EFUSESW",
        "Sefuse_S2E VSAFE S2E CTRL_EF2 0 EFUSESW": "V_EFUSE_S2E_SENSE VSAFE VSAFE_S2E 0\nSefuse_S2E VSAFE_S2E S2E CTRL_EF2 0 EFUSESW",
        "CEFOUT1 O1 0 10u IC=11": "V_CEFOUT1_SENSE O1 CEFOUT1_NODE 0\nCEFOUT1 CEFOUT1_NODE 0 10u IC=11",
        "CEFOUT2 S2E 0 10u IC=11": "V_CEFOUT2_SENSE S2E CEFOUT2_NODE 0\nCEFOUT2 CEFOUT2_NODE 0 10u IC=11",
        "BLOAD_O1 O1 0 I=4.96049833887*min(max(V(O1)/11,0),1)": "V_LOAD_O1_SENSE O1 O1_LOAD 0\nBLOAD_O1 O1_LOAD 0 I=4.96049833887*min(max(V(O1)/11,0),1)",
        "BLOAD_S2E S2E 0 I=1.5*min(max(V(S2E)/11,0),1)": "V_LOAD_S2E_SENSE S2E S2E_LOAD 0\nBLOAD_S2E S2E_LOAD 0 I=1.5*min(max(V(S2E)/11,0),1)",
    }
    for old, new in replacements.items():
        if old not in deck:
            raise RuntimeError(f"charge-balance source line not found: {old}")
        deck = deck.replace(old, new, 1)
    names = ("SW", "IN1", "IN2", "EF1", "EF2", "OUT1", "OUT2", "LOAD1", "LOAD2")
    sources = ("VSW_SENSE", "V_CEFIN1_SENSE", "V_CEFIN2_SENSE", "V_EFUSE_O1_SENSE",
               "V_EFUSE_S2E_SENSE", "V_CEFOUT1_SENSE", "V_CEFOUT2_SENSE",
               "V_LOAD_O1_SENSE", "V_LOAD_S2E_SENSE")
    lines = []
    for name, source in zip(names, sources):
        lines.extend((f"BINT_Q_{name} 0 T_Q_{name} I=if(time>1m,I({source}),0)",
                      f"CQ_{name} T_Q_{name} 0 1 IC=0", f"RQ_{name} T_Q_{name} 0 1T",
                      f".meas tran Q_{name}_C FIND V(T_Q_{name}) AT=2m"))
    for name, source in zip(("IN1", "IN2", "OUT1", "OUT2"),
                            ("V_CEFIN1_SENSE", "V_CEFIN2_SENSE", "V_CEFOUT1_SENSE", "V_CEFOUT2_SENSE")):
        lines.extend((f".meas tran I_{name}_MAX MAX I({source}) FROM=1m TO=1.02m",
                      f".meas tran I_{name}_MIN MIN I({source}) FROM=1m TO=1.02m"))
    return deck.replace(".end", "\n".join(lines) + "\n.end", 1)


def build_sense_rail_loss_deck() -> str:
    return f"""* Behavioral screen: TLV3601 clamp-current path and 5-V rail loss.
* Comparator silicon is not modeled. Vpin clamp is a fixed 0.3-V diode approximation.
VRAW RAW 0 PWL(0 0 50u 0 100u 11 900u 11 1m 40.709 20m 40.709)
RTOP RAW SDIV {RTOP}
RBOT SDIV 0 {RBOT}
VSENSE SDIV PIN 0
* Datasheet-guided clamp screen: positive diode current into VCC when PIN>VCC+0.3.
BCLAMP PIN CLAMP_NODE I=if(V(PIN,VCC)>0.3,(V(PIN,VCC)-0.3)/1,0)
VCLAMP_SENSE CLAMP_NODE VCC 0
V5SRC V5SRC_NODE 0 5
VLDOCONTROL LDOCONTROL 0 PWL(0 0 49u 0 50u 1 2m 1 2.001m 0 20m 0)
SLDO V5SRC_NODE VCC LDOCONTROL 0 LDO_SWITCH
.model LDO_SWITCH SW(Ron=0.1 Roff=1T Vt=0.5 Vh=0.05)
C5 VCC 0 2.2u IC=0
RBLEED VCC 0 {R_BLEED}
* Maximum steady loads used only while the comparator rail is valid.
B_TLV_IQ VCC 0 I=if(V(VCC)>2.1,7m,0)
B_REF_IQ VCC 0 I=if(V(VCC)>2.7,1.2m,0)
.tran 1u 20m 0 2u uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran VDIV_AT_FAULT FIND V(SDIV) AT=1.5m
.meas tran VPIN_AT_FAULT FIND V(PIN) AT=1.5m
.meas tran VCC_AT_FAULT FIND V(VCC) AT=1.5m
.meas tran ICLAMP_FAULT FIND I(VCLAMP_SENSE) AT=1.5m
.meas tran VCC_AFTER_LOSS_MAX MAX V(VCC) FROM=5m TO=20m
.meas tran VCC_AFTER_LOSS_END FIND V(VCC) AT=20m
.meas tran ICLAMP_MAX MAX I(VCLAMP_SENSE) FROM=2m TO=20m
.end
"""


def parse_measures(log_text: str) -> dict[str, float]:
    return {m.group(1).lower(): float(m.group(2)) for m in re.finditer(
        r"^\s*([a-z][a-z0-9_]*)\s*=\s*([-+0-9.eE]+)", log_text,
        re.MULTILINE | re.IGNORECASE)}


def run_case(name: str, deck_text: str, ngspice: Path) -> dict:
    SIM.mkdir(parents=True, exist_ok=True)
    deck = SIM / f"{name}.cir"
    log = SIM / f"{name}.log"
    deck.write_text(deck_text, encoding="ascii", newline="\n")
    try:
        proc = subprocess.run([str(ngspice), "-D", "ngbehavior=ltpsa", "-b", "-o", str(log), str(deck)],
                              cwd=SIM, capture_output=True, text=True, timeout=120, check=False)
        log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else proc.stdout + proc.stderr
        measures = parse_measures(log_text)
        if "charge-balance" in name:
            required = (set(f"q_{key.lower()}_c" for key in
                            ("SW", "IN1", "IN2", "EF1", "EF2", "OUT1", "OUT2", "LOAD1", "LOAD2"))
                        | set(f"i_{key.lower()}_{edge}" for key in ("IN1", "IN2", "OUT1", "OUT2")
                              for edge in ("max", "min")))
        else:
            required = {"vdiv_at_fault", "vpin_at_fault", "vcc_at_fault", "iclamp_fault",
                        "vcc_after_loss_max", "vcc_after_loss_end", "iclamp_max"}
        missing = sorted(required - set(measures))
        completed = proc.returncode == 0 and "No. of Data Rows" in log_text and not missing
        return {"deck": deck.relative_to(ROOT).as_posix(), "log": log.relative_to(ROOT).as_posix(),
                "exit_code": proc.returncode, "completed": completed, "missing_measures": missing,
                "measures": measures,
                "stderr": proc.stderr, "raw_log": log_text}
    except Exception as exc:
        return {"deck": deck.relative_to(ROOT).as_posix(), "log": log.relative_to(ROOT).as_posix(),
                "exit_code": None, "completed": False, "error": repr(exc), "measures": {}}


def build_results() -> dict:
    grid = []
    for raw in RAW_CORNERS:
        for vcc in RAIL_CORNERS:
            pin_oc = divider_open_circuit_v(raw, RTOP, RBOT)
            pin = min(pin_oc, vcc + CLAMP_OFFSET_V)
            current = clamp_current_a(raw, vcc, RTOP, RBOT)
            grid.append({"VRAW_V": raw, "VCC_V": vcc, "divider_open_circuit_V": pin_oc,
                         "TLV3601_pin_clamp_model_V": pin,
                         "injection_current_mA": current * 1e3,
                         "TLV3601_abs_max_current_mA": 10.0,
                         "input_common_mode_valid": pin <= vcc + 0.2,
                         "TLV1851_fail_safe_input_valid": pin_oc <= 40.0,
                         "TLV1851_unpowered_input_fail_safe": vcc == 0 and pin_oc <= 40.0,
                         "comparator_state": ("unpowered" if vcc < 2.4 else
                                              "fault; TLV3601 beyond recommended common-mode" if raw > 12 and pin > vcc + 0.2 else
                                              "fault" if raw > 12 else "nominal-safe")})
    worst_i = max(max_clamp_current_corner_a(raw, vcc) for raw in RAW_CORNERS for vcc in RAIL_CORNERS) * 1e3
    worst_equilibrium = max_unpowered_rail_equilibrium_corner_v(max(RAW_CORNERS))
    tlv_bounds = [r["vtrip_V"] for r in threshold_corners("TLV3601")]
    hv_bounds = [r["vtrip_V"] for r in threshold_corners("TLV1851")]
    tlv_interval = threshold_bounds_interval("TLV3601")
    hv_interval = threshold_bounds_interval("TLV1851")
    vout_max = TPS7A16_RAIL_NOM_V * (1 + TPS7A16_TOL)
    rbleed_min = R_BLEED * (1 - R_BLEED_TOL)
    iq_total = TLV3601_IQ_MAX_A + REF5025_IQ_MAX_A + vout_max / rbleed_min + 10e-6
    p_ldo = (max(RAW_CORNERS) - TPS7A16_RAIL_NOM_V * (1 - TPS7A16_TOL)) * iq_total
    ldo_dT = p_ldo * TPS7A16_THETA_JA_C_PER_W
    original_worst = max(clamp_current_a(raw, 0.0, OLD_RTOP, OLD_RBOT) for raw in RAW_CORNERS)
    old_calc = clamp_current_a(40.709, 0, OLD_RTOP, OLD_RBOT)
    return {
        "classification": "HESAP plus behavioral SİM; datasheet-based limits are not physical acceptance",
        "candidate": {"fast_comparator": "TLV3601DCKR", "fail_safe_overrail_supervisor": "TLV1851DBVR",
                     "reference": "REF5025AQDRQ1", "latch": "SN74LVC1G74DCUR",
                     "driver": "LTC7001EMSE#PBF", "FET_pair": "2x CSD19536KTTT",
                     "sense_divider_Rtop_ohm": RTOP, "sense_divider_Rbottom_ohm": RBOT,
                     "rail_bleeder_ohm": R_BLEED, "5V_source": "TPS7A1650QDGNRQ1 from RAW",
                     "12V_driver_source": "TPS7A1601QDGNRQ1 from VIN/battery"},
        "source_evidence": {
            "TLV3601": "TI TLV360x Rev E pp.5-7: VCC 2.4..5.5V; input abs VCC±0.3V; input clamp current ±10mA; recommended VCM VCC±0.2V; 7mA max IQ; POR output LOW below 2.1V.",
            "TLV1851": "TI TLV185x Rev B pp.16,19: fail-safe input -0.1..40V independent of V+, not diode-clamped to V+; POR output LOW for up to 2ms; offset ±4.4mV and hysteresis max 5mV.",
            "TPS7A16": "TI TPS7A16-Q1 Rev E pp.1,5-6,10,21: 3..60V input, 5V version ±2%, 100mA, PG trip 85..95% rising and 83..93% falling, PG valid for VIN>=3V; DGN thetaJA 66.2C/W.",
            "LVC1G74": "TI SN74LVC1G74 Rev G pp.1,4,7: VCC 1.65..5.5V; active-low asynchronous CLR; Ioff only ensures powered-down output backflow protection, no power-up latch state.",
            "LTC7001": "ADI LTC7001 Rev G pp.2-4: INP internal 1Mohm pulldown; VCCUV=0 sets minimum rising gate UVLO 3.1..3.7V and falling 2.8..3.4V; UVLO pulls TGDN to TS; 4ohm max pull-down at VCC=VBST=12V.",
            "CSD19536": "TI CSD19536KTT Rev C pp.1-2,5-6: 100V VDS, ±20V VGS, 2.8mohm max at VGS=6V; shortest SOA plotted pulse is 100us; sub-us SOA not verified.",
            "TPS7A16 thermal screen": "125C is a conservative engineering screen, not a TI absolute or recommended limit. TI Rev E lists operating TJ -40..150C and rising thermal shutdown 170C; thetaJA 66.2C/W is a JEDEC test-board metric, not this PCB.",
        },
        "legacy_clamp_reproduction": {"raw_40p709_V_vcc0_injection_mA": old_calc * 1e3,
                                       "worst_grid_mA": original_worst * 1e3,
                                       "comment_value_10p96_mA_reproduced_with_0p3V_clamp": old_calc * 1e3,
                                       "abs_max_limit_mA": 10.0,
                                       "result": "FAIL preserved: original divider exceeds 10mA condition at 40.709V/VCC=0"},
        "sense_corners": grid,
        "current_limit": {"max_injection_mA_fixed_0p3V_clamp": worst_i,
                          "max_injection_mA_zero_v_clamp_conservative": max(
                              max_clamp_current_corner_a(raw, vcc, 0.0) for raw in RAW_CORNERS for vcc in RAIL_CORNERS) * 1e3,
                          "limit_mA": 10.0, "margin_mA_vs_10mA": 10.0 - worst_i,
                          "status": "calculation meets absolute input-current condition only under static divider/clamp model"},
        "unpowered_rail": {"Rbleed_ohm": R_BLEED, "Vrail_equilibrium_worst_V_zero_vf": worst_equilibrium,
                           "TLV3601_POR_V": TLV3601_POR_V,
                           "LVC1G74_min_V": LVC1G74_MIN_V,
                           "rail_below_POR_and_latch_min": worst_equilibrium < min(TLV3601_POR_V, LVC1G74_MIN_V),
                           "closed_form_minus_bisection_V": worst_equilibrium -
                               max_unpowered_rail_equilibrium_bisect_corner_v(max(RAW_CORNERS))},
        "threshold": {"TLV3601_enumerated_V": [min(tlv_bounds), max(tlv_bounds)],
                      "TLV3601_interval_V": tlv_interval,
                      "TLV3601_enum_interval_delta_mV": max(abs(min(tlv_bounds)-tlv_interval[0]),
                                                            abs(max(tlv_bounds)-tlv_interval[1]))*1e3,
                      "TLV1851_enumerated_V": [min(hv_bounds), max(hv_bounds)],
                      "TLV1851_interval_V": hv_interval,
                      "required_trip_window_V": list(TRIP_WINDOW),
                      "TLV3601_within_static_window": min(tlv_bounds) >= TRIP_WINDOW[0] and max(tlv_bounds) <= TRIP_WINDOW[1],
                      "noise_ripple_and_measurement_margin_included": False},
        "rail_and_thermal": {"LDO_output_V_min_max": [5*(1-TPS7A16_TOL), vout_max],
                              "bleeder_current_max_mA": vout_max/rbleed_min*1e3,
                              "divider_Rtop_fault_power_W_unpowered_clamp": (max(RAW_CORNERS) - CLAMP_OFFSET_V)**2 / min(resistor_corner_values(RTOP)),
                              "estimated_total_5V_load_max_mA": iq_total*1e3,
                              "LDO_power_at_40p709V_W": p_ldo,
                              "thetaJA_C_per_W": TPS7A16_THETA_JA_C_PER_W,
                              "estimated_deltaT_C": ldo_dT,
                              "estimated_Tj_at_25C_ambient_C": 25+ldo_dT,
                              "estimated_Tj_at_85C_ambient_C": 85+ldo_dT,
                              "conservative_Tj_screen_C": 125,
                              "datasheet_Tj_operating_max_C": 150,
                              "datasheet_TSD_rising_C": 170,
                              "125C_screen_is_TI_limit": False,
                              "at_85C_ambient_status": "FAIL against conservative 125C screen; below datasheet 150C maximum only under JEDEC theta estimate; actual PCB and pulse Tj open" if 85+ldo_dT > 125 else "within conservative screen under JEDEC theta estimate"},
        "timing_and_driver": {"fast_path_TLV3601_max_ns": 4.5,
                              "TLV3601_tpd_condition": "50mV overdrive, comparator input must remain within common-mode range; no max outside those conditions",
                              "slow_fail_safe_TLV1851": "datasheet plots are typical; no guaranteed maximum propagation delay found; interlock only, not fast OVP proof",
                              "driver_supply_normal_V": 12.0,
                              "driver_uvlo_VCCUV_ground_rising_min_max_V": [3.1, 3.7],
                              "driver_uvlo_falling_min_max_V": [2.8, 3.4],
                              "driver_OFF_when_VCC_0_or_2p4": True,
                              "driver_valid_when_5_or_5p5": True,
                              "INP_external_10k_pulldown_and_per_FET_GS_pulldown_required": True,
                              "FET_SOA_and_physical_gate_off_time": "OPEN"},
        "charge_balance": {"input_and_output_capacitor_currents_separated_in_spice": True,
                           "physical_Ceff": "OPEN: modeled 2x100nF input and 2x10uF output caps are behavioral placeholders"},
        "physical_test": "NOT PERFORMED",
        "preserved_failures": {"family2_original_O1_18p8039V_FAIL": True,
                               "family2_common_bus_40p709V_TPS25982_IN_FAIL": True,
                               "family4_bus_10p7109V_FAIL": True,
                               "baseline_O1_16p89V_FAIL": True,
                               "WP1_incomplete_4_and_N01_open": True,
                               "WP2_69_FAIL_6_incomplete": True},
    }


def main() -> int:
    ngspice = Path(os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe"))
    results = build_results()
    version = subprocess.run([str(ngspice), "--version"], capture_output=True, text=True, check=False)
    results["ngspice_version"] = next((line.strip() for line in (version.stdout+version.stderr).splitlines()
                                       if "ngspice-" in line), "unavailable")
    charge = run_case("family2-common-bus-charge-balance-split", build_charge_balance_deck(), ngspice)
    rail = run_case("ovp-tlv3601-divider-rail-loss-screen", build_sense_rail_loss_deck(), ngspice)
    results["spice_cases"] = [charge, rail]
    m = charge.get("measures", {})
    if charge.get("completed") and all(f"q_{key.lower()}_c" in m for key in ("SW", "IN1", "IN2", "EF1", "EF2", "OUT1", "OUT2", "LOAD1", "LOAD2")):
        q = {key: m[f"q_{key.lower()}_c"] for key in ("SW", "IN1", "IN2", "EF1", "EF2", "OUT1", "OUT2", "LOAD1", "LOAD2")}
        results["charge_balance"]["measured_charge_C"] = q
        results["charge_balance"]["common_node_residual_C"] = q["SW"] - sum(q[k] for k in ("IN1", "IN2", "EF1", "EF2"))
        results["charge_balance"]["O1_branch_residual_C"] = q["EF1"] - q["OUT1"] - q["LOAD1"]
        results["charge_balance"]["S2E_branch_residual_C"] = q["EF2"] - q["OUT2"] - q["LOAD2"]
    if rail.get("completed"):
        results["unpowered_rail"]["spice_VCC_at_fault_V"] = rail["measures"].get("vcc_at_fault")
        results["unpowered_rail"]["spice_VCC_max_after_loss_V"] = rail["measures"].get("vcc_after_loss_max")
        results["unpowered_rail"]["spice_VCC_end_after_loss_V"] = rail["measures"].get("vcc_after_loss_end")
        results["unpowered_rail"]["spice_input_clamp_peak_A"] = rail["measures"].get("iclamp_max")
    RESULT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": RESULT_JSON.relative_to(ROOT).as_posix(),
                      "ngspice_version": results["ngspice_version"],
                      "original_divider_40p709V_VCC0_injection_mA": results["legacy_clamp_reproduction"]["raw_40p709_V_vcc0_injection_mA"],
                      "candidate_TLV3601_trip_bounds_V": results["threshold"]["TLV3601_enumerated_V"],
                      "candidate_max_injection_mA": results["current_limit"]["max_injection_mA_fixed_0p3V_clamp"],
                      "candidate_rail_equilibrium_V": results["unpowered_rail"]["Vrail_equilibrium_worst_V_zero_vf"],
                      "spice_cases": [{"deck": c["deck"], "completed": c["completed"],
                                       "exit_code": c["exit_code"], "measures": c.get("measures", {})}
                                      for c in results["spice_cases"]]}, indent=2, ensure_ascii=False))
    return 0 if all(c.get("completed") for c in results["spice_cases"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
