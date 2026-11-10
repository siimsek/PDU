#!/usr/bin/env python3
"""Ayrik buck: kapi surucu, PWM, geri besleme, yumusak baslatma ve yardimci besleme degerleri.

Calistir: python buck/kontrol.py  ->  buck/kontrol-sonuc.json
Gerilim modlu kontrol; kararlilik dogrusal ortalama modelle hesaplanir. Fiziksel olcum degildir.
"""
from __future__ import annotations

import cmath
import json
import math
from pathlib import Path

import hesap as H

# KARAR: secilen standart degerler
VZ = 12.0               # zener
VBE = 0.7
VCC = VZ - VBE
R_VCC = 2.2e3
I_CC = 0.030            # kontrol devresi toplam akimi (VARSAYIM)
VREF = 2.5
R_REF = 5.6e3
R_M = 10e3              # orta nokta bolucu (her kol)
RH1, RH2 = 27e3, 100e3  # histerezis
R_I, C_I = 8.66e3, 1e-9 # integrator; karsilastirici gecikmesiyle LTspice'te ~100 kHz
R_PU_TRI = 1e3
R_PU_PWM, R_B_PWM = 2.2e3, 1.2e3
R_E, R_UP = 160.0, 620.0
R_G, R_GS = 4.7, 10e3
R_RAIL, C_RAIL = 330.0, 1e-6
R1, RB = 34e3, 10e3
R2, C2, C1, R3, C3 = 33e3, 10e-9, 47e-12, 2.2e3, 10e-9
R_SS, C_SS = 10e3, 1e-6
GECIKME = 1e-6          # PWM+karsilastirici gecikmesi (VARSAYIM)
R_SERI = 0.035          # DCR + Rds*D (kararlilik modeli)


def tip3(f: float):
    s = 2j * math.pi * f
    a = R2 + 1 / (s * C2)
    b = 1 / (s * C1)
    zf = a * b / (a + b)
    c = R3 + 1 / (s * C3)
    zi = R1 * c / (R1 + c)
    return zf / zi


def plant(f: float, vin: float, r: float, esr: float, l: float, c: float, vpp: float):
    s = 2j * math.pi * f
    zc = esr + 1 / (s * c)
    z = r * zc / (r + zc)
    return vin / vpp * z / (z + R_SERI + s * l) * cmath.exp(-s * GECIKME)


def marj(vin, r, esr, l, c, vpp):
    onceki = pp = fc = pm = gm = None
    sar = 0.0
    for i in range(700):
        f = 10 ** (1.5 + i * 0.006)
        t = plant(f, vin, r, esr, l, c, vpp) * tip3(f)
        g, ph = abs(t), math.degrees(cmath.phase(t))
        if pp is not None:
            while ph + sar - pp > 180:
                sar -= 360
            while ph + sar - pp < -180:
                sar += 360
        ph += sar
        pp = ph
        if onceki and onceki[0] >= 1 > g:
            fc, pm = f, 180 + ph
        if onceki and fc and onceki[1] > -180 >= ph and gm is None:
            gm = -20 * math.log10(g)
        onceki = (g, ph)
    return fc, pm, gm


def hesapla() -> dict:
    k = RH1 / RH2
    vpp = k * VCC
    vm = VCC / 2
    f_tri = 1 / (4 * k * R_I * C_I)
    vb = VCC * R_B_PWM / (R_PU_PWM + R_B_PWM)
    ils = (vb - VBE) / R_E
    drop = ils * R_UP
    dmax = H.duty_gercek(20.0)
    l0 = H.e12_ust(H.VO * (1 - H.VO / 26.0) / (H.RIPPLE * H.IO * H.F))
    c0 = H.COUT_ADET * H.COUT_UF
    kose = [(v, r, e, l0 * a, c0 * b) for v in (20.0, 26.0) for r in (H.VO / H.IO, H.VO / 0.75)
            for e in (0.0075, 0.010, 0.020, 0.040) for a in (0.8, 1.2) for b in (0.8, 1.2)]
    m = [marj(*x, vpp) for x in kose]
    nom = marj(22.2, H.VO / H.IO, 0.020, l0, c0, vpp)
    vo = VREF * (1 + R1 / RB)
    def vo_kose(ref, rt):
        return VREF * (1 + ref) * (1 + R1 / RB * (1 + rt) / (1 - rt))
    return {
        "not": "HESAP; VARSAYIM girdileri parca secilince degisir. Fiziksel olcum yok.",
        "yardimci_besleme": {"Vcc_V": VCC, "R_ohm": R_VCC, "I_zener_20V_mA": (20 - VZ) / R_VCC * 1e3, "I_zener_26V_mA": (26 - VZ) / R_VCC * 1e3,
                             "P_R_26V_W": (26 - VZ) ** 2 / R_VCC, "P_gecis_26V_W": (26 - VCC) * I_CC, "I_cc_varsayim_mA": I_CC * 1e3},
        "referans": {"Vref_V": VREF, "R_ohm": R_REF, "I_mA": (VCC - VREF) / R_REF * 1e3},
        "ucgen": {"k": k, "Vcc_V": VCC, "Vm_V": vm, "Vpp_V": vpp, "Vvadi_V": vm - vpp / 2, "Vtepe_V": vm + vpp / 2, "f_kHz": f_tri / 1e3,
                  "R_I_ohm": R_I, "C_I_nF": C_I * 1e9, "egim_V_us": 2 * vpp * f_tri / 1e6, "mod_kazanc_20V": 20 / vpp, "mod_kazanc_26V": 26 / vpp},
        "pwm": {"Vc_D_min_V": vm - vpp / 2 + H.VO / 26 * vpp, "Vc_D_max_V": vm - vpp / 2 + dmax * vpp, "D_max": dmax},
        "surucu": {"Vb_V": vb, "I_seviye_mA": ils * 1e3, "dusum_V": drop, "R_E_ohm": R_E, "R_UP_ohm": R_UP, "P_RUP_W": drop ** 2 / R_UP * dmax,
                   "P_RE_W": ils ** 2 * R_E * dmax, "P_Qls_26V_W": (26 - drop - (vb - VBE)) * ils * H.VO / 26,
                   "I_kapi_tepe_A_beta100": ils * 100, "Rg_ohm": R_G, "Rgs_ohm": R_GS},
        "kapi_rayi": {"R_ohm": R_RAIL, "C_uF": C_RAIL * 1e6, "I_20V_mA": (20 - VZ) / R_RAIL * 1e3, "I_26V_mA": (26 - VZ) / R_RAIL * 1e3,
                      "P_R_26V_W": (26 - VZ) ** 2 / R_RAIL, "P_zener_26V_W": VZ * (26 - VZ) / R_RAIL, "I_kapi_ort_mA": H.QG * H.F * 1e3,
                      "dV_ray_V": H.QG / C_RAIL},
        "geri_besleme": {"R1_ohm": R1, "Rb_ohm": RB, "Vo_V": vo, "Vo_min_ref1_R01": vo_kose(-0.01, -0.001), "Vo_max_ref1_R01": vo_kose(0.01, 0.001),
                         "R2_ohm": R2, "C2_nF": C2 * 1e9, "C1_pF": C1 * 1e12, "R3_ohm": R3, "C3_nF": C3 * 1e9,
                         "fz1_Hz": 1 / (2 * math.pi * R2 * C2), "fz2_Hz": 1 / (2 * math.pi * (R1 + R3) * C3),
                         "fp1_Hz": 1 / (2 * math.pi * R3 * C3), "fp2_Hz": 1 / (2 * math.pi * R2 * C1)},
        "kararlilik": {"nominal_fc_kHz": nom[0] / 1e3, "nominal_PM_derece": nom[1], "fc_min_kHz": min(x[0] for x in m) / 1e3, "fc_max_kHz": max(x[0] for x in m) / 1e3,
                       "PM_min_derece": min(x[1] for x in m), "GM_min_dB": min(x[2] for x in m if x[2] is not None), "kose_sayisi": len(m)},
        "yumusak_baslatma": {"R_ohm": R_SS, "C_uF": C_SS * 1e6, "tau_ms": R_SS * C_SS * 1e3,
                             "Icout_max_A": c0 * H.VO / (R_SS * C_SS), "tau_min_ms_Icout_7p5A": c0 * H.VO / H.IO * 1e3},
    }


def main() -> None:
    s = hesapla()
    p = Path(__file__).with_name("kontrol-sonuc.json")
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(s, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
