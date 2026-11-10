#!/usr/bin/env python3
"""Sabit 11 V / 7.5 A icin analitik L/f/C on elemesi; LTspice calistirmaz.

Verim yuzdesi uretmez: gercek parcalarin kayip verileri olmadan siralama yapilamaz.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import hesap

FREQUENCIES_KHZ = (50, 75, 100, 150, 200, 250, 300)
INDUCTORS_UH = (10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82, 100, 150)
CAPACITORS_UF = (47, 100, 150, 220, 330, 470, 680, 1000)
VIN_GRID = tuple(20 + n / 10 for n in range(61))
L_TOL = 0.20
C_TOL = 0.20
MAX_CURRENT_RIPPLE_FRACTION = 0.30


def evaluate(f_khz: float, l_uh: float, cin_uf: float, cout_uf: float) -> dict:
    """CCM ripple/stress bounds with simultaneous negative L/C tolerances."""
    f_hz = f_khz * 1e3
    l_h = l_uh * 1e-6 * (1 - L_TOL)
    cin_f = cin_uf * 1e-6 * (1 - C_TOL)
    cout_f = cout_uf * 1e-6 * (1 - C_TOL)
    cases = []
    for vin_v in VIN_GRID:
        duty = hesap.VO_V / vin_v
        di = hesap.VO_V * (1 - duty) / (f_hz * l_h)
        il_rms_sq = hesap.IO_A**2 + di**2 / 12
        icin_sq = duty * (1 - duty) * hesap.IO_A**2 + duty * di**2 / 12
        icout_sq = di**2 / 12
        vin_ripple_v = (
            hesap.IO_A * duty * (1 - duty) / (f_hz * cin_f)
            + (hesap.IO_A + di / 2) * hesap.ESR_IN_OHM
        )
        vout_ripple_v = di / (8 * f_hz * cout_f) + di * hesap.ESR_OUT_OHM
        cases.append({
            "Vin_V": vin_v,
            "delta_IL_pp_A": di,
            "IL_peak_A": hesap.IO_A + di / 2,
            "IL_rms_squared_A2": il_rms_sq,
            "ICIN_rms_A": math.sqrt(icin_sq),
            "ICOUT_rms_A": math.sqrt(icout_sq),
            "VIN_ripple_Vpp": vin_ripple_v,
            "VOUT_ripple_Vpp": vout_ripple_v,
            "capacitor_ESR_loss_W": (
                icin_sq * hesap.ESR_IN_OHM + icout_sq * hesap.ESR_OUT_OHM
            ),
        })
    worst_di = max(c["delta_IL_pp_A"] for c in cases)
    worst_vin = max(c["VIN_ripple_Vpp"] for c in cases)
    worst_vout = max(c["VOUT_ripple_Vpp"] for c in cases)
    current_ok = worst_di <= MAX_CURRENT_RIPPLE_FRACTION * hesap.IO_A
    input_ok = worst_vin <= hesap.INPUT_RIPPLE_LIMIT_V
    output_ok = worst_vout <= hesap.OUTPUT_RIPPLE_LIMIT_V
    return {
        "f_kHz": f_khz,
        "L_uH": l_uh,
        "CIN_uF": cin_uf,
        "COUT_uF": cout_uf,
        "max_delta_IL_pp_A": worst_di,
        "max_IL_peak_A": max(c["IL_peak_A"] for c in cases),
        "max_VIN_ripple_mVpp_bound": worst_vin * 1e3,
        "max_VOUT_ripple_mVpp_bound": worst_vout * 1e3,
        "max_ICIN_rms_A_bound": max(c["ICIN_rms_A"] for c in cases),
        "max_ICOUT_rms_A": max(c["ICOUT_rms_A"] for c in cases),
        "max_capacitor_ESR_loss_W_assumed": max(c["capacitor_ESR_loss_W"] for c in cases),
        "max_copper_loss_W_per_mOhm_DCR": max(c["IL_rms_squared_A2"] for c in cases) * 1e-3,
        "switching_loss_W_per_uJ_cycle": f_hz * 1e-6,
        "checks": {"current_ripple": current_ok, "input_ripple_bound": input_ok, "output_ripple": output_ok},
        "passes_analytic_screen": current_ok and input_ok and output_ok,
        "efficiency_pct": None,
    }


def sweep() -> dict:
    feasible_count = 0
    lf_options = []
    for f_khz, l_uh in itertools.product(FREQUENCIES_KHZ, INDUCTORS_UH):
        # Ripple limits for CIN/COUT are independent in this first-order model.
        base = evaluate(f_khz, l_uh, max(CAPACITORS_UF), max(CAPACITORS_UF))
        if not base["passes_analytic_screen"]:
            continue
        cin_options = [c for c in CAPACITORS_UF if evaluate(
            f_khz, l_uh, c, max(CAPACITORS_UF)
        )["checks"]["input_ripple_bound"]]
        cout_options = [c for c in CAPACITORS_UF if evaluate(
            f_khz, l_uh, max(CAPACITORS_UF), c
        )["checks"]["output_ripple"]]
        feasible_count += len(cin_options) * len(cout_options)
        if cin_options and cout_options:
            lf_options.append(evaluate(f_khz, l_uh, min(cin_options), min(cout_options)))

    starting_points = []
    for f_khz in FREQUENCIES_KHZ:
        candidates = [row for row in lf_options if row["f_kHz"] == f_khz]
        if candidates:
            starting_points.append(min(candidates, key=lambda row: row["L_uH"]))

    return {
        "classification": "ANALİTİK ÖN ELEME; simülasyon veya verim optimizasyon sonucu değil",
        "fixed_output": {"Vout_V": hesap.VO_V, "Iout_A": hesap.IO_A, "Pout_W": hesap.VO_V * hesap.IO_A, "RLOAD_ohm": hesap.VO_V / hesap.IO_A},
        "grid": {"f_kHz": FREQUENCIES_KHZ, "L_uH": INDUCTORS_UH, "CIN_uF": CAPACITORS_UF, "COUT_uF": CAPACITORS_UF, "Vin_V_min": 20, "Vin_V_max": 26, "Vin_step_V": 0.1},
        "limits_and_assumptions": {
            "L_tolerance_minus_fraction": L_TOL,
            "C_tolerance_minus_fraction": C_TOL,
            "current_ripple_max_fraction_Iout": MAX_CURRENT_RIPPLE_FRACTION,
            "VIN_ripple_limit_mVpp": hesap.INPUT_RIPPLE_LIMIT_V * 1e3,
            "VOUT_ripple_limit_mVpp": hesap.OUTPUT_RIPPLE_LIMIT_V * 1e3,
            "ESRIN_assumed_mOhm": hesap.ESR_IN_OHM * 1e3,
            "ESROUT_assumed_mOhm": hesap.ESR_OUT_OHM * 1e3,
            "input_bound": "Giriş kondansatörünün anahtarlama AC akımını taşıdığı kabulü. Gerçek akım paylaşımı kaynak empedansına bağlıdır.",
        },
        "total_L_f_CIN_COUT_combinations": len(FREQUENCIES_KHZ) * len(INDUCTORS_UH) * len(CAPACITORS_UF)**2,
        "combinations_passing_analytic_screen": feasible_count,
        "per_frequency_lowest_L_starting_points": starting_points,
        "other_feasible_L_f_pairs_with_minimum_listed_capacitances": lf_options,
        "previous_reference_with_added_C_tolerance": evaluate(100, 39, 470, 220),
        "efficiency_status": "Hesaplanmadı; tüm efficiency_pct alanları null. Sabit ESR ve bilinmeyen DCR ile fiziksel verim kazananı seçilemez.",
        "next_loss_inputs": ["MOSFET RDS(on,T), Qg, Coss ve geçiş enerjisi", "Diyot Vf(I,T), kapasitans ve varsa ters toparlanma", "Her bobin adayının DCR(T), çekirdek/AC kaybı, Isat ve Irms verisi", "Kondansatörlerin ESR(f,T), etkin kapasitans ve ripple akımı sınırı", "Sürme enerjisi ve tanımlı giriş gücü ölçüm sınırı"],
    }


def write_report(data: dict) -> str:
    lines = [
        "# Sabit çıkış hedefinde L / f / C taraması",
        "",
        "Analitik ön eleme: **11 V / 7,5 A / 82,5 W**. LTspice çalıştırılmadı; verim yüzdesi hesaplanmadı.",
        "",
        f"{data['total_L_f_CIN_COUT_combinations']} kombinasyon incelendi; {data['combinations_passing_analytic_screen']} kombinasyon belirtilen analitik sınırları sağlıyor.",
        "Giriş 20–26 V arasında 0,1 V adımla tarandı. Her noktada ideal duty Vo/Vin; gerçek kayıplı karşılaştırmada her kombinasyonun duty'si aynı 11 V çıkışı verecek şekilde ayrıca ayarlanmalı.",
        "",
        "## Varsayımlar",
        "",
        "- L ve her iki C aynı anda nominalden %20 düşük kabul edildi.",
        "- Bobin akım ripple sınırı: 2,25 A p-p (%30 Iout).",
        "- Çıkış ripple sınırı: 55 mV p-p; giriş ripple üst sınır hesabı: 200 mV p-p.",
        "- ESRIN=15 mΩ ve ESROUT=20 mΩ bütün adaylarda sabit varsayıldı. Bunlar parça verisi değil.",
        "- Giriş ripple hesabı, kondansatörün anahtarlama AC akımını taşıdığı üst sınır yaklaşımıdır. İdeal gerilim kaynağına doğrudan paralel bir CIN'in gerilim ripple'ı bu hesapla aynı olmaz; kaynak empedansı tanımlanmalı.",
        "- Kalkış, yük adımı, sıcaklık, doyum ve kayıpların çıkış gerilimine etkisi bu taramada yok.",
        "",
        "## Her frekansta en küçük L ile bulunan örnekler",
        "",
        "Bu liste verim sıralaması değildir. Kapasitörler, aday listesinden sınırları sağlayan en küçük nominal değerlerdir; sınırdaki değerler nihai seçim değildir.",
        "",
    ]
    for row in data["per_frequency_lowest_L_starting_points"]:
        lines.append(
            f"- **{row['f_kHz']:g} kHz / {row['L_uH']:g} µH / CIN {row['CIN_uF']:g} µF / COUT {row['COUT_uF']:g} µF**: "
            f"ΔIL ≤ {row['max_delta_IL_pp_A']:.3f} A p-p, çıkış ripple ≤ {row['max_VOUT_ripple_mVpp_bound']:.1f} mV p-p, "
            f"giriş ripple hesabı ≤ {row['max_VIN_ripple_mVpp_bound']:.1f} mV p-p."
        )
    old = data["previous_reference_with_added_C_tolerance"]
    lines += [
        "",
        "## Önceki referansın ek tolerans kontrolü",
        "",
        f"100 kHz / 39 µH / CIN 470 µF / COUT 220 µF için L ve C birlikte −%20 olduğunda çıkış ripple hesabı {old['max_VOUT_ripple_mVpp_bound']:.2f} mV p-p. Önceki 52,24 mV hesabı COUT nominal kalırken yapılmıştı. 55 mV sınırı bu ek köşede az farkla aşılır; COUT 220 µF henüz kesin seçim değildir.",
        "",
        "## Verimi sıralamak için gereken model",
        "",
        "η = Pout / Pin; her adayda Pout = 82,5 W korunmalı. İdeal kayıpsız elemanlar %100 verir ve fiziksel verim kazananı göstermez.",
        "",
        "Bobin bakır kaybı IL_rms²·DCR, kondansatör kaybı IC_rms²·ESR ve anahtarlama kaybı E_cycle·f ile değişir. Büyük L'nin DCR ve çekirdek kaybı, düşük frekansın gerektirdiği daha büyük parçalar, gerçek parça verileriyle birlikte değerlendirilmelidir. JSON'da DCR başına bakır kaybı ve çevrim enerjisi başına anahtarlama kaybı katsayıları tutulur; toplam verim olarak sunulmaz.",
        "",
        "Örneğin çevrim başına 1 µJ kayıp 50 kHz'te 0,05 W; 100 kHz'te 0,10 W; 200 kHz'te 0,20 W eder. Bu bir MOSFET'e atanmış kayıp değeri değil, duyarlılık hesabıdır.",
        "",
        "Verim için gereken parça verileri:",
        "",
    ]
    lines += [f"- {item}" for item in data["next_loss_inputs"]]
    lines += [
        "",
        "İlk eleme sonrası gerçek kayıp verileriyle kısa liste oluşturulacak; ardından birlikte kurulacak LTspice güç katında aynı çıkış gücü ve kararlı durum koşullarıyla karşılaştırılacak.",
        "",
        "Kaynaklar: [ADI — An Efficiency Primer](https://www.analog.com/en/resources/technical-articles/an-efficiency-primer-for-switchmode-dcdc-converter-power-supplies.html), [TI — How the Switching Frequency Affects the Performance of Buck Converter](https://www.ti.com/lit/an/slvaed3a/slvaed3a.pdf).",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = sweep()
    root = Path(__file__).resolve().parent
    (root / "tarama-sonuc.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (root / "PARAMETRE-KARSILASTIRMA.md").write_text(write_report(result), encoding="utf-8", newline="\n")
    print(f"{result['total_L_f_CIN_COUT_combinations']} kombinasyon; {result['combinations_passing_analytic_screen']} analitik elemeden geçti.")
    for candidate in result["per_frequency_lowest_L_starting_points"]:
        print(json.dumps(candidate, ensure_ascii=False))
