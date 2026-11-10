"""Worst-case screen for a real-component O1 OVP candidate; never a safety proof."""
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g1"

VREF = 2.5
RTOP = 3_590.0
RBOT = 1_000.0
RES_TOL = 0.001
RES_TCR = 25e-6
VREF_INITIAL = 0.001
VREF_TCR = 8e-6
VREF_LOAD_PPM_PER_MA = 30.0
VREF_LINE_PPM_PER_V = 1.0
COMP_OFFSET = 5e-3
COMP_HYST_MAX = 5e-3
COMP_IB_MAX = 5e-6
VTRIP_LIMIT = 12.0
STEADY_BUS_MAX = 11.1605
PRIOR_PROVISIONAL_TRIP_MAX = 11.46

# Datasheet-corner entries form an engineering timing estimate only. Several
# published values are conditional/typical; see the generated report.
COMP_TPD_S = 4.5e-9
LATCH_TPD_S = 6.1e-9
DRIVER_TPD_S = 70e-9
FET_QG_MAX_C = 153e-9
FET_COUNT = 2
DRIVER_RPD_MAX_OHM = 4.0
ASSUMED_MILLER_V = 5.0
REVIEW_FAULT_CURRENT_A = 10.0
REVIEW_TDELAY_S = 0.5e-6
REVIEW_IDEAL_EDGE_S = 0.55e-6


def threshold_corner_values(rtop_ohm: float = RTOP) -> list[dict[str, float]]:
    """Enumerate independent ref/resistor/temp/input-error sign corners."""
    rows: list[dict[str, float]] = []
    divider_load_ma = VREF / (rtop_ohm + RBOT) * 1000.0
    vref_load_error = VREF_LOAD_PPM_PER_MA * 1e-6 * divider_load_ma
    # The 5-V LDO is ±2%; from nominal to a rail endpoint is 0.1 V.
    vref_line_error = VREF_LINE_PPM_PER_V * 1e-6 * 0.1
    for temp_c, ref_s, rt_s, rb_s, vos_s, hyst_s, ib_s in itertools.product(
        (-40.0, 125.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, 1.0),
    ):
        dt = temp_c - 25.0
        rt = rtop_ohm * (1.0 + rt_s * (RES_TOL + RES_TCR * abs(dt)))
        rb = RBOT * (1.0 + rb_s * (RES_TOL + RES_TCR * abs(dt)))
        vref = VREF * (1.0 + ref_s * (VREF_INITIAL + VREF_TCR * abs(dt) + vref_load_error + vref_line_error))
        ratio = rt / rb
        rth = rt * rb / (rt + rb)
        v_input_error = vos_s * COMP_OFFSET + hyst_s * COMP_HYST_MAX + ib_s * COMP_IB_MAX * rth
        rows.append({
            "temp_C": temp_c,
            "rtop_ohm": rt,
            "rbot_ohm": rb,
            "vref_V": vref,
            "ratio": ratio,
            "vtrip_V": (vref + v_input_error) * (1.0 + ratio),
        })
    return rows


def threshold_bounds_enumerated(rtop_ohm: float = RTOP) -> tuple[float, float]:
    values = [x["vtrip_V"] for x in threshold_corner_values(rtop_ohm)]
    return min(values), max(values)


def threshold_bounds_interval(rtop_ohm: float = RTOP) -> tuple[float, float]:
    """Independent interval propagation, deliberately conservative."""
    max_dt = 100.0
    divider_load_ma = VREF / (rtop_ohm + RBOT) * 1000.0
    ref_extra = VREF_LOAD_PPM_PER_MA * 1e-6 * divider_load_ma + VREF_LINE_PPM_PER_V * 1e-6 * 0.1
    ref_low = VREF * (1.0 - VREF_INITIAL - VREF_TCR * max_dt - ref_extra)
    ref_high = VREF * (1.0 + VREF_INITIAL + VREF_TCR * max_dt + ref_extra)
    rtol_tcr = RES_TOL + RES_TCR * max_dt
    ratio_low = rtop_ohm * (1.0 - rtol_tcr) / (RBOT * (1.0 + rtol_tcr))
    ratio_high = rtop_ohm * (1.0 + rtol_tcr) / (RBOT * (1.0 - rtol_tcr))
    rth_hi = (rtop_ohm * (1 + rtol_tcr)) * (RBOT * (1 + rtol_tcr)) / (
        rtop_ohm * (1 + rtol_tcr) + RBOT * (1 + rtol_tcr)
    )
    error = COMP_OFFSET + COMP_HYST_MAX + COMP_IB_MAX * rth_hi
    return (
        (ref_low - error) * (1.0 + ratio_low),
        (ref_high + error) * (1.0 + ratio_high),
    )


def divider_window_for_trip_target() -> dict[str, float]:
    """Find Rtop bounds with trip_min >= bus_max and trip_max <= prior target."""
    lo, hi = 1_000.0, 10_000.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if threshold_bounds_enumerated(mid)[0] < STEADY_BUS_MAX:
            lo = mid
        else:
            hi = mid
    rtop_min = hi

    lo, hi = 1_000.0, 10_000.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if threshold_bounds_enumerated(mid)[1] <= PRIOR_PROVISIONAL_TRIP_MAX:
            lo = mid
        else:
            hi = mid
    rtop_max = lo
    return {
        "prior_provisional_trip_max_V": PRIOR_PROVISIONAL_TRIP_MAX,
        "minimum_trip_bound_V": STEADY_BUS_MAX,
        "rtop_min_ohm": rtop_min,
        "rtop_max_ohm": rtop_max,
        "window_width_ohm": rtop_max - rtop_min,
        "at_rtop_min_trip_min_V": threshold_bounds_enumerated(rtop_min)[0],
        "at_rtop_min_trip_max_V": threshold_bounds_enumerated(rtop_min)[1],
        "at_rtop_max_trip_min_V": threshold_bounds_enumerated(rtop_max)[0],
        "at_rtop_max_trip_max_V": threshold_bounds_enumerated(rtop_max)[1],
        "candidate_rtop_ohm": RTOP,
        "candidate_rtop_in_window": rtop_min <= RTOP <= rtop_max,
        "status": "window excludes noise/ripple margin; candidate outside window" if not (rtop_min <= RTOP <= rtop_max) else "window excludes noise/ripple margin",
    }


def off_time_estimate_s() -> float:
    gate_charge = FET_COUNT * FET_QG_MAX_C
    sink_current = ASSUMED_MILLER_V / DRIVER_RPD_MAX_OHM
    gate_discharge = gate_charge / sink_current
    return COMP_TPD_S + LATCH_TPD_S + DRIVER_TPD_S + gate_discharge


def ceff_min_charge_coulombs(current_a: float, off_time_s: float, headroom_v: float) -> float:
    return current_a * off_time_s / headroom_v


def ceff_min_overshoot_bisect(current_a: float, off_time_s: float, headroom_v: float) -> float:
    """Numerically solve the overshoot inequality as an independent check."""
    if current_a <= 0 or off_time_s <= 0 or headroom_v <= 0:
        raise ValueError("current, off_time, and headroom must be positive")
    low, high = 0.0, 1.0
    while current_a * off_time_s / high > headroom_v:
        high *= 2.0
    for _ in range(100):
        mid = (low + high) / 2.0
        if current_a * off_time_s / mid <= headroom_v:
            high = mid
        else:
            low = mid
    return high


def build_results() -> dict:
    lo, hi = threshold_bounds_enumerated()
    lo_interval, hi_interval = threshold_bounds_interval()
    divider_window = divider_window_for_trip_target()
    toff = off_time_estimate_s()
    # Use the datasheet's 300-ohm high-temperature ILIM maximum conservatively
    # for the 301-ohm BOM value, then add an explicit 1% low-R sensitivity.
    ilim_hi_at_301 = (5.66 - 0.11) * 300.0 / (301.0 * (1.0 - 0.01)) + 0.11
    fast_trip_screen = 2.1 * ilim_hi_at_301
    headroom = VTRIP_LIMIT - hi
    ceff = ceff_min_charge_coulombs(fast_trip_screen, toff, headroom)
    ceff2 = ceff_min_overshoot_bisect(fast_trip_screen, toff, headroom)
    gate_charge = FET_COUNT * FET_QG_MAX_C
    gate_i = ASSUMED_MILLER_V / DRIVER_RPD_MAX_OHM
    return {
        "candidate_chain": {
            "comparator": {"mpn": "TLV3601DCKR", "package": "SC70-5 / DCK0005A", "supply_V": "2.4..5.5", "temp_C": "-40..125"},
            "reference": {"mpn": "REF5025AQDRQ1", "package": "SOIC-8 / D", "output_V": 2.5, "temp_C": "-40..125"},
            "latch": {"mpn": "SN74LVC1G74DCUR", "package": "VSSOP-8 / DCU", "implementation": "asynchronous CLR/PRE D flip-flop used as set/reset latch; power-up clear and manual arm required"},
            "driver": {"mpn": "LTC7001EMSE#PBF", "package": "10-lead MSOP with exposed pad", "driver_supply_V": 12.0},
            "mosfets": {"mpn": "CSD19536KTTT", "quantity": 2, "package": "TO-263 / D2PAK", "topology": "common-source back-to-back"},
            "bias_regulators": [
                {"mpn": "TPS7A1601QDGNRQ1", "setpoint_V": 12.0, "package": "HVSSOP-8 / DGN"},
                {"mpn": "TPS7A1650QDGNRQ1", "setpoint_V": 5.0, "package": "HVSSOP-8 / DGN"},
            ],
            "divider": {"Rtop_ohm": RTOP, "Rbottom_ohm": RBOT, "nominal_threshold_V": VREF * (1 + RTOP / RBOT), "tol_assumption_percent": 0.1, "tcr_assumption_ppm_per_K": 25},
        },
        "threshold": {
            "enumerated_min_V": lo,
            "enumerated_max_V": hi,
            "interval_min_V": lo_interval,
            "interval_max_V": hi_interval,
            "enumeration_interval_difference_mV": max(abs(lo - lo_interval), abs(hi - hi_interval)) * 1000,
            "worst_min_margin_above_steady_bus_mV": (lo - STEADY_BUS_MAX) * 1000,
            "worst_max_headroom_to_12V_mV": (VTRIP_LIMIT - hi) * 1000,
            "corners_included": ["reference initial accuracy, 8 ppm/K max drift, 30 ppm/mA max load regulation at 0.545 mA load and 1 ppm/V max line regulation across 0.1 V LDO span", "0.1% resistor tolerance", "25 ppm/K resistor TCR", "comparator ±5 mV offset", "up to 5 mV hysteresis", "5 µA max comparator input bias"],
        },
        "prior_provisional_trip_target_window": divider_window,
        "timing": {
            "comparator_tpd_ns": COMP_TPD_S * 1e9,
            "latch_tpd_ns": LATCH_TPD_S * 1e9,
            "driver_tpd_ns": DRIVER_TPD_S * 1e9,
            "two_fet_total_gate_charge_nC": gate_charge * 1e9,
            "assumed_miller_voltage_V": ASSUMED_MILLER_V,
            "driver_rpd_max_ohm": DRIVER_RPD_MAX_OHM,
            "estimated_sink_current_A": gate_i,
            "estimated_gate_discharge_ns": gate_charge / gate_i * 1e9,
            "estimated_total_toff_ns": toff * 1e9,
            "guaranteed_total_toff_ns": None,
            "physical_switch_off_measured": False,
            "limitations": [
                "TLV3601 4.5 ns maximum is specified at 50 mV overdrive; delay at smaller overdrive/slew is not bounded by that row.",
                "LTC7001 70 ns maximum propagation is specified with 1 nF load; the two-FET Qg load is not that test condition.",
                "FET turn-off estimate uses total maximum Qg and an assumed 5 V Miller plateau; the exact gate-charge waveform and Qgd maximum are not supplied as a guaranteed bound.",
            ],
        },
        "fault_current": {
            "RILIM_nominal_ohm": 301,
            "RILIM_tolerance_for_screen_percent": 1.0,
            "datasheet_ILIM_max_at_300ohm_A": 5.66,
            "screen_ILIM_max_at_301ohm_A": ilim_hi_at_301,
            "datasheet_fast_trip_ratio": 2.1,
            "fast_trip_current_screen_A": fast_trip_screen,
            "is_guaranteed_fault_current_ceiling": False,
            "why_open": "TPS259824O is the circuit-breaker variant; 2.1×ILIM is a fast-trip threshold, not a hard clamp. Its 400 ns tSC is not used as a guaranteed maximum current bound here. The no-OVP Family-2 model also reaches 63.6654 A phase current; that is a separate stress sensitivity, not measured O1 current.",
        },
        "ceff": {
            "screen_current_A": fast_trip_screen,
            "screen_to_off_ns": toff * 1e9,
            "trip_high_V": hi,
            "headroom_V": headroom,
            "ceff_min_charge_balance_uF": ceff * 1e6,
            "ceff_min_bisection_uF": ceff2 * 1e6,
            "independent_method_difference_pF": abs(ceff - ceff2) * 1e12,
            "independent_method": "closed-form charge balance vs numerical bisection of Vtrip + I*t/C <= 12 V",
            "at_10uF_peak_screen_V": hi + fast_trip_screen * toff / 10e-6,
            "at_4uF_sensitivity_peak_V": hi + fast_trip_screen * toff / 4e-6,
            "ceff_min_at_63p6654A_model_stress_uF": ceff_min_charge_coulombs(63.6654, toff, headroom) * 1e6,
            "review_10A_500ns_scenario_uF": ceff_min_charge_coulombs(REVIEW_FAULT_CURRENT_A, REVIEW_TDELAY_S, headroom) * 1e6,
            "review_10A_550ns_scenario_uF": ceff_min_charge_coulombs(REVIEW_FAULT_CURRENT_A, REVIEW_IDEAL_EDGE_S, headroom) * 1e6,
            "esr_esl_turnoff_tail_and_probe_uncertainty_included": False,
            "minimum_ceff_for_physical_pass": None,
        },
        "mosfet": {
            "vds_abs_rating_each_V": 100.0,
            "rds_on_max_each_at_vgs6V_mohm": 2.8,
            "pair_rds_on_screen_mohm_at_datasheet_test_corner": 5.6,
            "pair_conduction_loss_at_7p5A_W_at_datasheet_test_corner": 7.5**2 * 5.6e-3,
            "Qg_max_each_at_10V_nC": 153.0,
            "SOA_shortest_published_curve_time_us": 100.0,
            "candidate_turnoff_estimate_us": toff * 1e6,
            "soa_verified_at_turnoff_time": False,
            "reason": "The CSD19536KTT SOA plot begins at 100 µs; estimated turn-off is about 0.325 µs, and fault VDS/current sharing and waveform are not guaranteed. Do not extrapolate the SOA curve or mark this pair PASS.",
        },
        "gate": {
            "driver_supply_candidate_V": 12.0,
            "driver_minimum_vcc_V": 3.5,
            "driver_maximum_vcc_V": 15.0,
            "fet_vgs_abs_max_V": 20.0,
            "gate_drive_headroom_status": "nominally within published ratings; exact output/gate charge corner remains model-only",
        },
        "decision": "BLOCKED: real orderable-component chain selected for analysis, but no guaranteed end-to-end switch-off/current envelope, Ceff margin including parasitics, or sub-100-us MOSFET SOA proof. The combined SPICE cases are engineering screens only.",
    }


def render_markdown(data: dict) -> str:
    t = data["threshold"]
    d = data["timing"]
    c = data["ceff"]
    f = data["fault_current"]
    m = data["mosfet"]
    w = data["prior_provisional_trip_target_window"]
    return f"""# O1 OVP: component and timing feasibility screen

Etiketler: **DATASHEET** = manufacturer specification; **HESAP** = reproducible calculation; **SİM** = ngspice model; **AÇIK** = unbounded or unmeasured; **VARSAYIM** = explicit scenario input.

## Conclusion

**AÇIK / BLOCKED.** A concrete component chain is identified below, but this analysis does not produce a guaranteed end-to-end switch-off time or a bounded fault current. The 12.0 V O1 maximum therefore cannot be accepted. The Family 2 and Family 4 FAILs remain unchanged.

## Candidate chain (datasheets and exact orderables)

| Function | Candidate MPN | Package | Evidence / limit |
|---|---|---|---|
| Comparator | `TLV3601DCKR` | SC70-5 | DATASHEET: ±5 mV offset, 5 µA max input bias, 4.5 ns max only at 50 mV overdrive, −40…125 °C. |
| Precision reference | `REF5025AQDRQ1` | SOIC-8 | DATASHEET: 2.5 V, 0.1% initial accuracy, 8 ppm/K max drift, −40…125 °C. |
| Set/reset memory | `SN74LVC1G74DCUR` | VSSOP-8 | Active-low asynchronous CLR/PRE; CLR-to-Q max 6.1 ns at 5 V and −40…125 °C. Requires a fail-safe power-up clear, one-way fault injection to CLR and deliberate manual ARM through PRE. |
| High-side driver | `LTC7001EMSE#PBF` | 10-lead MSOP with exposed pad | DATASHEET: VCC 3.5…15 V, 70 ns max input-to-output at 1 nF, pull-down 4 Ω max at VCC=VBST=12 V. |
| Back-to-back FETs | `CSD19536KTTT` ×2 | TO-263 / D2PAK | DATASHEET: 100 V, 2.8 mΩ max at VGS=6 V, Qg 153 nC max at VGS=10 V; SOA plot's shortest curve is 100 µs. |
| 12 V driver rail | `TPS7A1601QDGNRQ1` | HVSSOP-8 / DGN | Adjustable high-voltage LDO candidate; exact divider, startup and power-good reset must be designed. |
| 5 V analog/logic rail | `TPS7A1650QDGNRQ1` | HVSSOP-8 / DGN | Fixed 5 V high-voltage LDO candidate. |
| Threshold divider | 3.59 kΩ / 1.00 kΩ, each 0.1%, ≤25 ppm/K | TBD | **VARSAYIM** component class; exact resistor MPN and layout not selected. Nominal trip 11.475 V. |

No distributor stock claim is made. TI's live pages showed `TLV3601DCKR`, `REF5025AQDRQ1`, and `CSD19536KTTT` as out of stock when checked; exact purchaseable stock for the other candidates was not verified. TI marks `SN74LVC1G74DCUR` active; the candidate's availability is not confirmed. Manufacturer status is not a BOM purchase reservation. The previous dual-NOR proposal `SN74LVC2G02` was dropped because TI's product page says it is in production to support existing customers and is not recommended for new designs.

## Trip threshold corner

| Quantity | Result | Label |
|---|---:|---|
| Nominal threshold | {data['candidate_chain']['divider']['nominal_threshold_V']:.4f} V | HESAP |
| Enumerated threshold minimum | {t['enumerated_min_V']:.4f} V | HESAP |
| Enumerated threshold maximum | {t['enumerated_max_V']:.4f} V | HESAP |
| Conservative interval maximum | {t['interval_max_V']:.4f} V | HESAP cross-check |
| Minimum trip margin above 11.1605 V bus limit | {t['worst_min_margin_above_steady_bus_mV']:.1f} mV | HESAP; O1 ripple/noise not included |
| Maximum headroom to 12.0 V | {t['worst_max_headroom_to_12V_mV']:.1f} mV | HESAP; ESR/ESL excluded |
| Previous provisional upper trip target | Candidate exceeds 11.46 V by {t['enumerated_max_V'] - PRIOR_PROVISIONAL_TRIP_MAX:.3f} V | HESAP; 3.59 kΩ divider does not meet that earlier target |
| Theoretical Rtop interval for trip-min >= bus max and trip-max <= 11.46 V | {w['rtop_min_ohm']:.2f}…{w['rtop_max_ohm']:.2f} Ω | HESAP only; {w['window_width_ohm']:.2f} Ω total width and no ripple/noise margin |
| Difference: corner enumeration vs interval propagation | {t['enumeration_interval_difference_mV']:.3f} mV | independent bound check |

Corner includes reference initial accuracy and temperature drift, resistor tolerance/TCR, comparator offset, maximum hysteresis and maximum input bias current. Resistors were assumed 0.1%/25 ppm/K because the proposed design class is not yet selected; O1's actual ripple and noise are not supplied.

## Switch-off time and Ceff/fault-current margins

The older ideal Family 1 deck has an ideal timer nominally set to 0.500 µs. The model's switch opens when CTRL falls below `Vt−Vh = 0.45 V`; CTRL begins at 1 V and discharges at 1 V/µs. Therefore the **calculated ideal-model trip-to-open is 0.550 µs**, and the new measurement deck measures the same edge pair. This is not a physical measurement.

| Timing contribution | Value | Source / limit |
|---|---:|---|
| Comparator | {d['comparator_tpd_ns']:.1f} ns | DATASHEET max only at 50 mV overdrive; low-overdrive delay not bounded |
| FF asynchronous clear | {d['latch_tpd_ns']:.1f} ns | DATASHEET CLR→Q max at 5 V, −40…125 °C |
| Gate driver | {d['driver_tpd_ns']:.1f} ns | DATASHEET max with 1 nF load, not the selected FET pair |
| Pair gate discharge screen | {d['estimated_gate_discharge_ns']:.1f} ns | HESAP: 306 nC ÷ (5 V / 4 Ω); 5 V Miller plateau is an assumption |
| Summed engineering estimate | {d['estimated_total_toff_ns']:.1f} ns | HESAP only; **not a guaranteed upper bound** |
| Physical switch-off measurement | Not performed | AÇIK: no assembled board / probe capture in this workspace |

**Ceff screen.** Using the threshold upper corner {t['enumerated_max_V']:.4f} V and a provisional {f['fast_trip_current_screen_A']:.2f} A current screen from the existing O1 eFuse's high-temperature ILIM maximum and nominal 2.1× fast-trip threshold, the calculated Ceff minimum is **{c['ceff_min_charge_balance_uF']:.2f} µF** for the {c['screen_to_off_ns']:.1f} ns timing estimate. Closed-form charge balance and numerical bisection of the same overshoot inequality differ by {c['independent_method_difference_pF']:.3f} pF; this is an algorithmic cross-check, not independent physical evidence. At 10 µF the idealized peak screen is {c['at_10uF_peak_screen_V']:.3f} V; at 4 µF it is {c['at_4uF_sensitivity_peak_V']:.3f} V. These omit ESR, ESL, turn-off tail and measurement error.

This is **not** a bounded worst-case result: the eFuse is a circuit-breaker part, and 2.1×ILIM is a fast-trip trigger, not a current clamp. The 400 ns short-circuit response is not accepted as a maximum fault-current bound for this OVP chain. With the old Family 2 model's 63.6654 A phase-current stress, the same idealized formula requires {c['ceff_min_at_63p6654A_model_stress_uF']:.1f} µF; that phase current is not an O1 output-current measurement. Thus no finite physical Ceff minimum can be signed off until the fault current/time envelope and actual port capacitor part are established.

## MOSFET and SOA screen

Two `CSD19536KTTT` devices give a 5.6 mΩ pair at the datasheet's 6 V gate-drive test point and about {m['pair_conduction_loss_at_7p5A_W_at_datasheet_test_corner']:.3f} W at 7.5 A at that test corner. Hot RDS(on) needs the datasheet's curve and the selected board thermal path; it is not folded into a guaranteed thermal result. Qg max is 153 nC each at 10 V. The estimated {m['candidate_turnoff_estimate_us']:.3f} µs turn-off lies far below the datasheet SOA plot's 100 µs shortest pulse curve. The fault VDS/current division across the two FETs is not known. **SOA: AÇIK; no PASS.**

## S2E and fault-source separation

This OVP switch is on the O1 branch only. A buck high-side short raises the shared VOUT feeding both eFuses; an O1 series disconnect does not isolate S2E. TPS259824O's internal 16.9 V nominal OVLO (16.32…17.31 V rising datasheet range) is above 12 V and its 5 µs OVP response cannot establish S2E protection without a numeric S2E input/absolute-maximum limit. Direct external O1 backfeed also bypasses an upstream-only disconnect unless the candidate switch is physically placed at the port connector. These are separate unresolved fault paths.

## Official manufacturer references

- [TI TLV360x datasheet](https://www.ti.com/lit/ds/symlink/tlv3601.pdf), pp. 1, 3, 7 (package, limits, propagation/offset/bias).
- [TI REF50xxA-Q1 datasheet](https://www.ti.com/lit/ds/symlink/ref5025a-q1.pdf), pp. 1, 5–6 (accuracy, drift, load/line and temperature range).
- [TI SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), pp. 1, 4, 7 (asynchronous preset/clear, package, CLR-to-Q delay).
- [ADI LTC7001 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc7001.pdf), pp. 1–3, 8–9 (supply, gate drive, propagation and output resistance).
- [TI CSD19536KTT datasheet](https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf), pp. 1–2, 5–6 (ratings, gate charge, RDS(on), SOA).
- [TI TPS7A16-Q1 datasheet](https://www.ti.com/lit/ds/symlink/tps7a16-q1.pdf), pp. 1, 6 (input/output range and accuracy).
- [TI TPS25982 datasheet](https://www.ti.com/lit/ds/symlink/tps25982.pdf), pp. 1, 8–10, 23–26 (current threshold, trip response and circuit-breaker behavior).

Reproduce with `python analysis/ovp_component_analysis.py`; tests are in `analysis/test_ovp_component_analysis.py`.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = build_results()
    (OUT / "ovp-component-calculation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "OVP-COMPONENT-REVIEW.md").write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({
        "threshold_min_V": result["threshold"]["enumerated_min_V"],
        "threshold_max_V": result["threshold"]["enumerated_max_V"],
        "estimated_off_ns_not_guaranteed": result["timing"]["estimated_total_toff_ns"],
        "screen_fault_A_not_ceiling": result["fault_current"]["fast_trip_current_screen_A"],
        "ceff_min_uF_excludes_parasitics": result["ceff"]["ceff_min_charge_balance_uF"],
        "decision": result["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
