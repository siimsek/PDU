#!/usr/bin/env python3
"""Analitik baslangic hesabi: tek faz, asenkron, acik cevrim buck.

Bu betik LTspice calistirmaz; yalnizca varsayim ve denklemlerden hesap JSON'u uretir.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


VO_V = 11.0
IO_A = 7.5
VIN_V = (20.0, 22.2, 26.0)
FSW_HZ = 100_000.0

# Tek nokta referansi; tarama kazani veya veri sayfasi ile secilmis parcalar degildir.
L_H = 39e-6
CIN_F = 470e-6
COUT_F = 220e-6
ESR_IN_OHM = 15e-3
ESR_OUT_OHM = 20e-3

L_TOLERANCE = 0.20
RIPPLE_TARGET_FRACTION = 0.25
OUTPUT_RIPPLE_LIMIT_V = 0.005 * VO_V
INPUT_RIPPLE_LIMIT_V = 0.01 * min(VIN_V)
SATURATION_MARGIN = 0.30


def ripple_voltage(delta_i_pp: float, capacitance: float, esr: float) -> dict[str, float]:
    capacitive = delta_i_pp / (8 * FSW_HZ * capacitance)
    resistive = delta_i_pp * esr
    return {
        "capacitive_Vpp": capacitive,
        "esr_Vpp": resistive,
        "total_approx_Vpp": capacitive + resistive,
    }


def calculate() -> dict[str, object]:
    output_power_w = VO_V * IO_A
    l_min_h = (
        VO_V * (1 - VO_V / max(VIN_V))
        / (RIPPLE_TARGET_FRACTION * IO_A * FSW_HZ)
    )
    duty_nominal = VO_V / VIN_V[1]
    steady_cases: list[dict[str, float]] = []

    for vin_v in VIN_V:
        duty = VO_V / vin_v
        delta_i_pp = VO_V * (1 - duty) / (L_H * FSW_HZ)
        inductor_peak_a = IO_A + delta_i_pp / 2
        inductor_rms_a = math.sqrt(IO_A**2 + delta_i_pp**2 / 12)

        # RMS for the pulsed source current, including triangular inductor ripple.
        cin_rms_a = math.sqrt(
            duty * (1 - duty) * IO_A**2 + duty * delta_i_pp**2 / 12
        )
        cin_cap_v = IO_A * duty * (1 - duty) / (FSW_HZ * CIN_F)
        cin_esr_v = (IO_A + delta_i_pp / 2) * ESR_IN_OHM
        cout_ripple = ripple_voltage(delta_i_pp, COUT_F, ESR_OUT_OHM)

        steady_cases.append({
            "Vin_V": vin_v,
            "duty_ideal": duty,
            "Ton_us": duty / FSW_HZ * 1e6,
            "Iin_average_ideal_A": output_power_w / vin_v,
            "delta_IL_pp_A": delta_i_pp,
            "IL_peak_A": inductor_peak_a,
            "IL_rms_A": inductor_rms_a,
            "ICIN_rms_A_approx": cin_rms_a,
            "ICOUT_rms_A_approx": delta_i_pp / math.sqrt(12),
            "VIN_ripple_cap_Vpp": cin_cap_v,
            "VIN_ripple_esr_Vpp": cin_esr_v,
            "VIN_ripple_total_approx_Vpp": cin_cap_v + cin_esr_v,
            "VOUT_ripple": cout_ripple,
            "switch_rms_A_ideal": math.sqrt(
                duty * (IO_A**2 + delta_i_pp**2 / 12)
            ),
            "diode_average_A_ideal": IO_A * (1 - duty),
            "diode_rms_A_ideal": math.sqrt(
                (1 - duty) * (IO_A**2 + delta_i_pp**2 / 12)
            ),
        })

    delta_i_worst_tol = (
        VO_V * (1 - VO_V / max(VIN_V))
        / (L_H * (1 - L_TOLERANCE) * FSW_HZ)
    )
    peak_worst_tol = IO_A + delta_i_worst_tol / 2
    output_ripple_worst_tol = ripple_voltage(
        delta_i_worst_tol, COUT_F, ESR_OUT_OHM
    )

    cin_ripple_worst_tol = []
    cin_rms_worst_tol = []
    for vin_v in VIN_V:
        duty = VO_V / vin_v
        delta_i_tol = (
            VO_V * (1 - duty)
            / (L_H * (1 - L_TOLERANCE) * FSW_HZ)
        )
        cin_cap_v = IO_A * duty * (1 - duty) / (FSW_HZ * CIN_F)
        cin_esr_v = (IO_A + delta_i_tol / 2) * ESR_IN_OHM
        cin_ripple_worst_tol.append(cin_cap_v + cin_esr_v)
        cin_rms_worst_tol.append(math.sqrt(
            duty * (1 - duty) * IO_A**2 + duty * delta_i_tol**2 / 12
        ))

    fixed_duty_cases = []
    for vin_v in VIN_V:
        vout_v = duty_nominal * vin_v
        fixed_duty_cases.append({
            "Vin_V": vin_v,
            "Vout_ideal_V": vout_v,
            "Iload_at_RLOAD_A": vout_v / (VO_V / IO_A),
        })

    return {
        "classification": "ANALİTİK HESAP / VARSAYIM; LTspice veya fiziksel ölçüm değil",
        "topology": "tek faz asenkron açık çevrim buck",
        "units": "Hesapta SI; alan adlarında birimler belirtilmiştir",
        "parameters": {
            "Vin_V": list(VIN_V),
            "Vout_target_V": VO_V,
            "Iout_design_A": IO_A,
            "Pout_target_W": output_power_w,
            "Fsw_Hz": FSW_HZ,
            "L_uH": L_H * 1e6,
            "L_tolerance_fraction": L_TOLERANCE,
            "CIN_uF": CIN_F * 1e6,
            "ESRIN_mOhm_assumed": ESR_IN_OHM * 1e3,
            "COUT_uF": COUT_F * 1e6,
            "ESROUT_mOhm_assumed": ESR_OUT_OHM * 1e3,
            "RLOAD_ohm": VO_V / IO_A,
        },
        "selection_checks": {
            "inductor_ripple_target_fraction": RIPPLE_TARGET_FRACTION,
            "L_min_uH_for_ripple_target_at_Vin_max": l_min_h * 1e6,
            "selected_standard_L_uH": L_H * 1e6,
            "L_at_minus20pct_uH": L_H * (1 - L_TOLERANCE) * 1e6,
            "delta_IL_pp_at_Vin_max_A_nominal_L": steady_cases[-1]["delta_IL_pp_A"],
            "delta_IL_pp_at_Vin_max_A_minus20pct_L": delta_i_worst_tol,
            "current_ripple_fraction_at_Vin_max_minus20pct_L": delta_i_worst_tol / IO_A,
            "IL_peak_A_at_Vin_max_minus20pct_L": peak_worst_tol,
            "Isat_steady_state_screen_A_with_30pct_margin": peak_worst_tol * (1 + SATURATION_MARGIN),
            "VOUT_ripple_limit_mVpp": OUTPUT_RIPPLE_LIMIT_V * 1e3,
            "VOUT_ripple_mVpp_at_Vin_max_minus20pct_L": output_ripple_worst_tol["total_approx_Vpp"] * 1e3,
            "VIN_ripple_limit_mVpp": INPUT_RIPPLE_LIMIT_V * 1e3,
            "VIN_ripple_max_approx_mVpp_at_minus20pct_L": max(cin_ripple_worst_tol) * 1e3,
            "ICIN_rms_max_approx_A_at_minus20pct_L": max(cin_rms_worst_tol),
            "fixed_nominal_duty": duty_nominal,
            "fixed_nominal_duty_cases": fixed_duty_cases,
        },
        "steady_state_cases": steady_cases,
        "model_notes": [
            "Açık çevrim duty, Vin değiştiğinde Vout değerini regüle etmez.",
            "CIN/COUT ESR değerleri model varsayımıdır; gerçek parça verisi değildir.",
            "Bobin doyum akımı kontrolü kalkış ve arıza akımlarını kapsamaz.",
            "Anahtarlama kaybı, termal davranış, parazitik yerleşim ve fiziksel davranış modellenmemiştir.",
        ],
    }


if __name__ == "__main__":
    result_path = Path(__file__).with_name("hesap-sonuc.json")
    result_path.write_text(
        json.dumps(calculate(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result_path)
