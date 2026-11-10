#!/usr/bin/env python3
"""Ayrik buck: topoloji karsilastirma ve guc kati degerleri.

Calistir: python buck/hesap.py  ->  buck/hesap-sonuc.json
Harici paket gerektirmez. Etiketler: GEREKSINIM, SECIM, VARSAYIM, HESAP.
Bu dosya fiziksel olcum degildir; VARSAYIM degerleri parca secilince guncellenir.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# GEREKSINIM
VO = 11.0
IO = 7.5                # tasarim akimi; hedef yuk 7 A
VIN = (20.0, 22.2, 26.0)
VIN_MIN, VIN_NOM, VIN_MAX = VIN
I_STEP = 7.0 - 0.75     # yuk adimi, A

# SECIM
F = 100e3
RIPPLE = 0.30           # bobin dalgalanmasi / faz akimi
L_TOL = 0.20
ISAT_PAY = 1.30
IRMS_PAY = 1.20
FC = 10e3               # hedef kapali cevrim kesim frekansi (F/10)
RS_KAYNAK = 0.050       # batarya+kablo, 20-200 mOhm araligindan orta deger (VARSAYIM)

# Secilen kapasitor banklari
COUT_ADET, COUT_UF, COUT_ESR_ADET = 2, 680e-6, 0.040
CIN_ADET, CIN_UF, CIN_ESR_ADET = 2, 220e-6, 0.050

# VARSAYIM: parca secilince gercek degerle degisir
VF = 0.6                # Schottky, 7.5 A civari
RDS = 0.030             # MOSFET, sicak
DCR_TEK = 0.020         # tek faz bobin direnci
TSW = 60e-9             # kenar basina anahtarlama suresi
TD = 100e-9             # senkron olu zaman
VF_GOVDE = 0.8          # olu zamanda govde diyodu
QG = 100e-9             # S1 kapi yuku ust siniri
VG = 12.0               # kapi surme gerilimi
TA = 50.0               # ortam, C
TJ_HEDEF = 125.0        # tasarim ust siniri, C

E12 = (10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82)

# VARSAYIM: goreli birim, teklif degildir; parca secilince gercek fiyatla degisir
MALIYET = {"mosfet": 1.5, "schottky": 1.0, "bobin_tek": 3.0, "bobin_faz": 2.0, "cout": 0.7, "cin": 0.5,
           "seramik": 0.2, "sogutucu": 1.0, "surucu": 0.8, "olu_zaman": 0.5, "pwm": 1.5, "faz_180": 1.0,
           "akim_paylasim": 3.0}


def e12_ust(deger_h: float) -> float:
    """Gereken endüktansa esit veya buyuk ilk E12 degeri."""
    for dekad in (1e-6, 1e-5, 1e-4):
        for n in E12:
            if n * dekad >= deger_h * (1 - 1e-12):
                return n * dekad
    raise ValueError(deger_h)


def duty_gercek(vin: float, n: int = 1, rs: float = 0.0) -> float:
    dcr = DCR_TEK * n
    iph = IO / n
    vin_eff = vin - rs * VO * IO / (0.94 * vin)
    return (VO + VF + iph * dcr) / (vin_eff - iph * RDS + VF)


def ripple_akim(vin: float, l: float, f: float = F) -> float:
    return VO * (1 - VO / vin) / (l * f)


def cin_rms(d: float, n: int) -> float:
    if n == 1:
        return IO * math.sqrt(d * (1 - d))
    if d <= 0.5:
        return IO / 2 * math.sqrt(2 * d * (1 - 2 * d))
    return IO / 2 * math.sqrt((2 * d - 1) * (2 - 2 * d))


def cout_kanseli(d: float, di: float, n: int) -> float:
    if n == 1:
        return di
    k = (1 - 2 * d) / (1 - d) if d < 0.5 else (2 * d - 1) / d
    return di * abs(k)


def kayip(vin: float, n: int, senkron: bool, irms_ph: float, f: float = F) -> dict:
    d = duty_gercek(vin, n)
    iph = IO / n
    dcr = DCR_TEK * n
    s_ilet = n * irms_ph**2 * RDS * d
    s_sw = n * 0.5 * vin * iph * 2 * TSW * f
    if senkron:
        alt = n * (irms_ph**2 * RDS * (1 - d) + 2 * TD * f * VF_GOVDE * iph)
    else:
        alt = n * VF * iph * (1 - d)
    l_cu = n * irms_ph**2 * dcr
    top = s_ilet + s_sw + alt + l_cu
    return {"vin": vin, "d": d, "s_iletim": s_ilet, "s_anahtarlama": s_sw, "alt_eleman": alt, "bobin_dcr": l_cu,
            "toplam": top, "verim_yuzde": 100 * VO * IO / (VO * IO + top)}


def topoloji(ad: str, n: int, senkron: bool, cin_adet: int, parca_ek: dict) -> dict:
    iph = IO / n
    dmin = VO / VIN_MAX
    l_gerek = VO * (1 - dmin) / (RIPPLE * iph * F)
    l = e12_ust(l_gerek)
    di = ripple_akim(VIN_MAX, l)
    di_lmin = di / (1 - L_TOL)
    ipk = iph + di_lmin / 2
    irms = math.sqrt(iph**2 + di**2 / 12)
    enerji = n * 0.5 * l * ipk**2
    cin_irms = max(cin_rms(VO / v, n) for v in VIN + (VO * 2,))
    # cikis akim dalgalanmasi: VIN taramasi, L -%20
    iout_pp = max(cout_kanseli(VO / v, ripple_akim(v, l) / (1 - L_TOL), n) for v in VIN)
    c = COUT_ADET * COUT_UF
    esr = COUT_ESR_ADET / COUT_ADET
    dvo = iout_pp / (8 * n * F * c) + iout_pp * esr
    kayiplar = [kayip(v, n, senkron, irms) for v in VIN]
    p = {"mosfet": n * (2 if senkron else 1), "schottky": 0 if senkron else n,
         "bobin_tek": 1 if n == 1 else 0, "bobin_faz": n if n > 1 else 0, "cout": COUT_ADET, "cin": cin_adet,
         "seramik": 4, "sogutucu": n if not senkron else 1, "surucu": n * (2 if senkron else 1),
         "olu_zaman": n if senkron else 0, "pwm": 1, "faz_180": 1 if n > 1 else 0, "akim_paylasim": 1 if n > 1 else 0}
    p.update(parca_ek)
    maliyet = sum(MALIYET[k] * v for k, v in p.items())
    guc_parca = p["mosfet"] + p["schottky"] + p["bobin_tek"] + p["bobin_faz"] + p["cout"] + p["cin"] + p["seramik"]
    return {"ad": ad, "faz": n, "senkron": senkron, "faz_akimi_A": iph, "L_gerekli_uH": l_gerek * 1e6, "L_secilen_uH": l * 1e6,
            "dI_pp_A": di, "dI_pp_Lmin_A": di_lmin, "Ipk_Lmin_A": ipk, "Irms_faz_A": irms, "Isat_gerek_A": ipk * ISAT_PAY,
            "L_toplam_enerji_mJ": enerji * 1e3, "Cin_rms_A": cin_irms, "Cikis_akim_pp_A": iout_pp, "dVo_mV": dvo * 1e3,
            "kayiplar": kayiplar, "en_kotu_kayip_W": max(k["toplam"] for k in kayiplar),
            "en_kotu_verim": min(k["verim_yuzde"] for k in kayiplar), "parca": p, "guc_kati_parca": guc_parca,
            "maliyet_gorece": maliyet}


def ek_secenekler() -> dict:
    sepic_d = VO / (VIN_MIN + VO)
    sepic_iin = IO * sepic_d / (1 - sepic_d)
    return {"lineer_kayip_W_26V": (VIN_MAX - VO) * IO, "lineer_verim_26V_yuzde": 100 * VO / VIN_MAX,
            "sepic_anahtar_V": VIN_MAX + VO, "sepic_anahtar_ort_tepe_A_20V": sepic_iin + IO, "sepic_giris_akim_A_20V": sepic_iin}


def frekans_tarama() -> list:
    r = []
    for f in (50e3, 75e3, 100e3, 150e3, 200e3):
        lg = VO * (1 - VO / VIN_MAX) / (RIPPLE * IO * f)
        l = e12_ust(lg)
        di = ripple_akim(VIN_MAX, l, f)
        ipk = IO + di / (1 - L_TOL) / 2
        k = kayip(VIN_MAX, 1, False, math.sqrt(IO**2 + di**2 / 12), f)
        r.append({"f_kHz": f / 1e3, "L_gerek_uH": lg * 1e6, "L_uH": l * 1e6, "enerji_mJ": 0.5 * l * ipk**2 * 1e3,
                  "s_anahtarlama_W": k["s_anahtarlama"], "toplam_W": k["toplam"], "verim_yuzde": k["verim_yuzde"],
                  "ton_min_us": (VO / VIN_MAX) / f * 1e6})
    return r


def ripple_tarama() -> list:
    r = []
    for rr in (0.2, 0.3, 0.4):
        lg = VO * (1 - VO / VIN_MAX) / (rr * IO * F)
        l = e12_ust(lg)
        di = ripple_akim(VIN_MAX, l)
        ipk = IO + di / (1 - L_TOL) / 2
        r.append({"r": rr, "L_gerek_uH": lg * 1e6, "L_uH": l * 1e6, "dI_A": di, "Ipk_A": ipk, "Isat_A": ipk * ISAT_PAY,
                  "enerji_mJ": 0.5 * l * ipk**2 * 1e3})
    return r


def guc_kati() -> dict:
    t = topoloji("A", 1, False, CIN_ADET, {})
    l = t["L_secilen_uH"] * 1e-6
    di_l = t["dI_pp_Lmin_A"]
    cout, esr = COUT_ADET * COUT_UF, COUT_ESR_ADET / COUT_ADET
    cin, cin_esr = CIN_ADET * CIN_UF, CIN_ESR_ADET / CIN_ADET
    ipk = t["Ipk_Lmin_A"]
    dmax = VO / VIN_MIN
    dmin = VO / VIN_MAX
    k26 = kayip(VIN_MAX, 1, False, t["Irms_faz_A"])
    k20 = kayip(VIN_MIN, 1, False, t["Irms_faz_A"])
    s_w = max(k["s_iletim"] + k["s_anahtarlama"] for k in (k20, k26))
    d_w = max(k["alt_eleman"] for k in (k20, k26))
    return {
        "bobin": {"L_uH": l * 1e6, "tolerans": L_TOL, "L_gerek_uH": t["L_gerekli_uH"], "dI_nom_A": t["dI_pp_A"], "dI_Lmin_A": di_l,
                  "Ipk_Lmin_A": ipk, "Irms_A": t["Irms_faz_A"], "Isat_min_A": ipk * ISAT_PAY, "Irms_min_A": t["Irms_faz_A"] * IRMS_PAY,
                  "DCR_max_mOhm": DCR_TEK * 1e3, "CCM_sinir_A": t["dI_pp_A"] / 2},
        "cout": {"toplam_uF": cout * 1e6, "esr_toplam_mOhm": esr * 1e3, "C_min_ripple_uF": di_l / (8 * F * 0.011) * 1e6,
                 "ESR_max_ripple_mOhm": 0.099 / di_l * 1e3, "dVo_ripple_mV": (di_l / (8 * F * cout) + di_l * esr) * 1e3,
                 "Irms_A": di_l / math.sqrt(12), "yuk_adim_C_mV": I_STEP / (2 * math.pi * FC * cout) * 1e3,
                 "yuk_adim_ESR_mV": I_STEP * esr * 1e3, "yuk_adim_toplam_mV": (I_STEP / (2 * math.pi * FC * cout) + I_STEP * esr) * 1e3,
                 "f0_Hz": 1 / (2 * math.pi * math.sqrt(l * cout)), "Z0_ohm": math.sqrt(l / cout), "esr_sifir_Hz": 1 / (2 * math.pi * esr * cout)},
        "cin": {"toplam_uF": cin * 1e6, "esr_toplam_mOhm": cin_esr * 1e3, "Irms_A": t["Cin_rms_A"], "Irms_adet_A": t["Cin_rms_A"] / CIN_ADET,
                "C_min_100mV_uF": IO * 0.25 / (F * 0.1) * 1e6, "dV_C_mV": IO * 0.25 / (F * cin) * 1e3, "dV_ESR_mV": cin_esr * ipk * 1e3,
                "giris_ort_A_20V_eta94": VO * IO / (VIN_MIN * 0.94)},
        "s1": {"Vds_calisma_V": VIN_MAX, "Ipk_A": ipk, "Irms_A": IO * math.sqrt(dmax), "kayip_W": s_w, "Rds_max_mOhm": RDS * 1e3,
               "Ig_tepe_A_Qg100n": QG / TSW, "kapi_kayip_W": QG * VG * F, "theta_max_K_W": (TJ_HEDEF - TA) / s_w},
        "fd": {"Vr_calisma_V": VIN_MAX, "Ipk_A": ipk, "If_ort_A": IO * (1 - dmin), "kayip_W": d_w, "theta_max_K_W": (TJ_HEDEF - TA) / d_w},
        "duty": {str(v): {"ideal": VO / v, "kayipli": duty_gercek(v)} for v in VIN},
        "yuk": {"R_7p5A_ohm": VO / IO, "P_7p5A_W": VO * IO, "R_7A_ohm": VO / 7, "P_7A_W": VO * 7},
    }


def hesapla() -> dict:
    return {
        "not": "HESAP; VARSAYIM girdileri parca secilince degisir. Fiziksel olcum yok.",
        "varsayim": {"VF": VF, "RDS": RDS, "DCR_tek": DCR_TEK, "DCR_cift_faz": DCR_TEK * 2, "TSW": TSW, "TD": TD, "QG": QG, "VG": VG, "TA": TA,
                     "RS_kaynak": RS_KAYNAK},
        "maliyet_birim": MALIYET,
        "topolojiler": [
            topoloji("A: Tek faz asenkron", 1, False, CIN_ADET, {}),
            topoloji("B: Tek faz senkron", 1, True, CIN_ADET, {}),
            topoloji("C: Cift faz 180 asenkron", 2, False, 1, {}),
            topoloji("D: Cift faz 180 senkron", 2, True, 1, {}),
        ],
        "ek_secenekler": ek_secenekler(),
        "frekans_tarama": frekans_tarama(),
        "ripple_tarama": ripple_tarama(),
        "guc_kati": guc_kati(),
    }


def main() -> None:
    sonuc = hesapla()
    cikti = Path(__file__).with_name("hesap-sonuc.json")
    cikti.write_text(json.dumps(sonuc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(sonuc, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
