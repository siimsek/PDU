#!/usr/bin/env python3
"""Analitik hesap: tek faz, asenkron, acik cevrim buck guc kati.

Bu betik LTspice calistirmaz; denklemlerden ozet tablolari ekrana yazar (ANALITIK HESAP).
Simulasyon karsiligi `python buck/dogrula.py` ile alinir. Fiziksel olcum yoktur.
Degerler ana sematikle aynidir; bulunan parcaya gore asagidaki sabitler degistirilir.

Bolum 1-5: kararli durum, tolerans, yuk uyumu, acik cevrim, LC dinamigi.
Bolum 6: sabit guc yuku (CPL) kararliligi, tam ifade ve kose model setleri.
Bolum 7-9: kayip butcesi, D1/S1/L1 isil hesap, gerilim sinifi ve arayuz sinirlari (Adim 3 girdisi).
Veri sayfasi sabitlerinin kaynagi ve sinifi (DATASHEET / CIKARIM / TAHMIN) yanlarinda yazilidir.
"""
from __future__ import annotations

import math

VO_V = 11.0
IO_A = 7.5                                   # tasarim akimi (modul zarfi 82,5 W)
VIN_V = (20.0, 22.2, 24.6, 25.2, 26.0)       # zorunlu test noktalari
VIN_ANA_V = 24.6
FSW_HZ = 100_000.0

# Ana sematikteki degerler: 1. sira aday parcalarin veri sayfasi degerleri; kesin secim degil (PARCA-HEDEFLERI.md).
L_H = 33e-6             # el sarim Kool Mu 40u 0077536A7, 22 sarim (33,4 uH); satin alinan: 33 veya 47 uH
DCR_OHM = 7.81e-3       # el sarim HESAP @20 C (sicak 9,5 mohm; denenen alt sinir 6,5 mohm)
COUT_F = 1000e-6        # Nichicon UHE1E102MHD6TO
ESR_OUT_OHM = 35e-3     # maks EMPEDANS (ESR degil); simulasyon varsayimi
ESR_OUT_MIN_OHM, ESR_OUT_MAX_OHM = 15e-3, 35e-3   # kabul penceresi (alt sinir LC sonumu, ust sinir ripple)
CIN_F = 2000e-6         # 2 x TDK B41859D7108M000
ESR_IN_OHM = 7.5e-3     # 2 x 15 mohm paralel
RON_OHM = 5.6e-3        # STP100N6F7, 25 C maks
VF_V = 0.38             # STPS40M60CT, iki bacak paralel; iki noktadan YAKLASIK
RD_OHM = 8e-3           # 7,5 A'de toplam 0,44 V

L_DUSUK = 0.30          # -%20 tolerans ve tepe akimda -%10 dusum birlikte
L_YUKSEK = 0.20
C_TOL = 0.20
SATURATION_MARGIN = 0.30

# Yukler. DATASHEET: uretici belgesi; TAHMIN: yayimlanmis deger yok.
O1_VMIN, O1_VMAX, O1_IMAX = 5.0, 12.0, 5.0        # DATASHEET  T3 Gemstone O1 DC girisi 5-12 V / 5 A
S2E_VMIN, S2E_VMAX = 9.0, 28.0                    # DATASHEET  RPLIDAR S2E 9-28 V (tipik 12 V)
S2E_RIPPLE = 0.03                                 # DATASHEET  besleme ripple'i en cok %3
P_S2E_CALISMA_W = 12 * 0.22                       # DATASHEET  12 V'ta en cok 0,22 A
P_S2E_KALKIS_W = 12 * 1.5                         # DATASHEET  12 V'ta en cok 1,5 A (sure verilmemis)
P_O1_ZARF_W = VO_V * O1_IMAX                      # DATASHEET  anma akimi; gercek tuketim degil
P_O1_TIPIK_W = 10.0                               # TAHMIN

# ---- Adim 3 girdileri: 1. sira aday parcalarin veri sayfasi degerleri ----------------------------
# L1 cekirdegi: Magnetics 0077536A7 veri sayfasi, Revision 6/1/2022 (DATASHEET)
L1_N = 22
L1_AL_NH, L1_AL_TOL = 69.0, 0.08          # nH/T^2, +-%8
L1_AE_M2 = 174e-6
L1_LE_M = 126e-3
L1_VE_CM3 = 22.0
L1_KAYIP_100K_100MT = 900.0               # mW/cm3 AZAMI @100 kHz, 100 mT (tepe)
L1_B_USSU = 2.0                           # CIKARIM: veri sayfasi tek nokta verir; Kool Mu icin B ussu ~2 alindi
L1_YUZEY_CM2 = 110.0                      # %40 sargi faktorunde sarili yuzey (DATASHEET 11 000 mm2)
L1_SARIM_BOYU_M = 66.5e-3                 # sarim basina tel boyu, %25 sargi faktoru (DATASHEET)
L1_BAKIR_MM2 = 100 * math.pi * 0.1 ** 2   # 100 x 0,20 mm litz
BAKIR_ALFA = 0.00393                      # 1/K
# DC bias egrisi (DATASHEET grafigi, EGRIDEN OKUMA, yaklasik): A·T -> AL nH/T^2
L1_BIAS = ((0, 69.0), (200, 67.0), (400, 61.5), (600, 56.0), (800, 50.0), (1000, 45.0), (1200, 39.5),
           (1400, 35.0), (1600, 31.0), (2000, 25.0))

# S1: STB100N6F7 DocID027210 Rev 2 (D2PAK; ayni kirmik, TO-220'li STP100N6F7 DocID027212 PDF'i acilamadi)
S1_RON_TIP, S1_RON_MAX = 4.7e-3, 5.6e-3   # DATASHEET, VGS 10 V, 50 A, 25 C; en dusuk deger yayimlanmamis
S1_RON_CARPAN = ((25, 1.0), (75, 1.2), (100, 1.4), (125, 1.5), (150, 1.65), (175, 1.8))   # EGRIDEN, yaklasik
S1_QG, S1_QGS, S1_QGD = 30e-9, 12.6e-9, 5.9e-9     # DATASHEET tipik, VDD 30 V, ID 100 A, VGS 10 V
S1_COSS_25V = 970e-12                     # DATASHEET tipik, VDS 25 V
S1_VPLATO = 5.0                           # CIKARIM: aktarim egrisinden 7,5 A icin ~4,8-5 V
S1_RTH_JC = 1.2                           # K/W DATASHEET
S1_TJ_MAX = 175.0
S1_VDS_MAX = 60.0
TO220_RTH_JA = 62.5                       # K/W TAHMIN: sogutucusuz TO-220 icin yaygin deger (bu parcanin belgesinde yok)

# D1: STPS40M60C Doc ID 018813 Rev 1 (May 2011), Tablo 2-4 (DATASHEET, diyot basina)
# Cift (iki bacak paralel) icin dogrusal model V = V0 + R I (I toplam akim), 10-20 A toplam noktalarindan:
D1_VF = {  # (V0, R) @25 C, (V0, R) @125 C
    "tipik": ((0.390, 0.0040), (0.265, 0.0060)),
    "azami": ((0.415, 0.0045), (0.275, 0.0080)),
}
D1_IR_125_60V = {"tipik": 0.050, "azami": 0.085}   # A/diyot; azami DATASHEET, tipik Sekil 8'den EGRIDEN
D1_IR_VR_CARPAN = 0.5                     # CIKARIM: Sekil 8 tipik egrisinde 26 V'taki akim ~ 60 V'takinin yarisi
D1_IR_IKIYE_K = 12.0                      # K; CIKARIM: Sekil 8'de 25 K'de ~x4
D1_RTH_JC_TOPLAM = 0.95                   # K/W DATASHEET (iki diyot birlikte)
D1_TJ_MAX = 150.0
D1_VRRM = 60.0
D1_CJ = ((1, 2700e-12), (8, 1000e-12), (25, 600e-12))   # F/diyot, Sekil 9'dan EGRIDEN
RTH_PED = 1.0                             # K/W TAHMIN: yalitim pedi + montaj (silikon ped tipik 0,5-1,5)

# Kondansator anma degerleri (DATASHEET)
COUT_VDC, COUT_IRIPPLE = 25.0, 1.90       # Nichicon UHE1E102MHD6TO: 25 V, 1,90 A (105 C, 100 kHz)
CIN_VDC, CIN_IRIPPLE = 35.0, 3.25         # TDK B41859D7108M000: 35 V, 3,25 A/adet (105 C, 100 kHz)
CIN_ESL_H = 26e-9                         # adet basina, PARCA-HEDEFLERI.md


def duty(vin: float, io: float, vo: float = VO_V) -> float:
    """CCM duty; anahtar, diyot ve bobin dusumleri dahil."""
    return (vo + VF_V + io * (DCR_OHM + RD_OHM)) / (vin + VF_V + io * (RD_OHM - RON_OHM))


def ripple_tt(di: float, esr: float, c: float, d: float, r_yuk: float | None = None) -> float:
    """Ucgen akimli seri R-C'nin tepe-tepe gerilimi (tam ifade).

    ESR·C her iki parcanin (iletim / serbest gecis) yarisindan buyukse dalga ESR'de olusur ve
    t-t = dIL·ESR'dir; kapasitif terim EKLENMEZ (eski `dIL·(ESR + 1/8fC)` toplami %4-5 fazla veriyordu).
    Direnc yukte ripple akiminin R/(R+ESR) kadari kondansatore gider.
    """
    if r_yuk:
        di = di * r_yuk / (r_yuk + esr)
    T = 1 / FSW_HZ
    ek = sum(di / (2 * c * ts) * (ts / 2 - esr * c) ** 2 for ts in (d * T, (1 - d) * T) if esr * c < ts / 2)
    return di * esr + ek


def nokta(vin: float, io: float = IO_A, l: float = L_H, c: float = COUT_F, esr: float = ESR_OUT_OHM) -> dict:
    d = duty(vin, io)
    di = (VO_V + VF_V + io * (DCR_OHM + RD_OHM)) * (1 - d) / (l * FSW_HZ)
    il_rms = math.sqrt(io**2 + di**2 / 12)
    sw_rms = math.sqrt(d) * il_rms
    d_rms = math.sqrt(1 - d) * il_rms
    d_avg = io * (1 - d)
    p_s1 = sw_rms**2 * RON_OHM
    p_d1 = VF_V * d_avg + RD_OHM * d_rms**2
    p_l1 = il_rms**2 * DCR_OHM
    kayip = p_s1 + p_d1 + p_l1
    return {
        "vin": vin, "d": d, "ton_us": d / FSW_HZ * 1e6, "di": di, "ipk": io + di / 2,
        "ikritik": di / 2,                                   # bunun altinda DCM
        "icin_rms": math.sqrt(d * (1 - d) * io**2 + d * di**2 / 12),
        "icout_rms": di / math.sqrt(12), "sw_rms": sw_rms, "d_rms": d_rms, "d_avg": d_avg, "il_rms": il_rms,
        "dvout": ripple_tt(di, esr, c, d, VO_V / io),
        "dvin": io * d * (1 - d) / (FSW_HZ * CIN_F) + (io + di / 2) * ESR_IN_OHM,
        "p_s1": p_s1, "p_d1": p_d1, "p_l1": p_l1, "kayip": kayip,
        "verim": VO_V * io / (VO_V * io + kayip),
    }


def acik_cevrim_vo(vin: float, d: float, r: float) -> float:
    """Sabit duty ve direnc yukte kararli cikis; CCM ve DCM'den gecerli olani."""
    # CCM: vo = d(vin - io Ron) - (1-d)(Vf + io Rd) - io DCR,  io = vo / r
    ccm = (d * vin - (1 - d) * VF_V) / (1 + (d * RON_OHM + (1 - d) * RD_OHM + DCR_OHM) / r)
    # DCM (dirençler ihmal): vo/r = d^2 T (vin-vo)(vin+Vf) / (2 L (vo+Vf))
    f = lambda v: d * d * (vin - v) * (vin + VF_V) / (2 * L_H * FSW_HZ * (v + VF_V)) - v / r
    lo, hi = 0.0, vin
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return max(ccm, lo)


def dinamik(l: float = L_H, c: float = COUT_F, esr: float = ESR_OUT_OHM, vin: float = VIN_ANA_V) -> dict:
    d = duty(vin, IO_A)
    rs = DCR_OHM + d * RON_OHM + (1 - d) * RD_OHM
    z0 = math.sqrt(l / c)
    return {
        "f0_hz": 1 / (2 * math.pi * math.sqrt(l * c)), "z0": z0,
        "f_esr_hz": 1 / (2 * math.pi * esr * c),
        # BASITLESTIRILMIS sinir (Rs·ESR terimi yok, Vo = 11 V sabit); tam ifade: cpl()
        "p_cpl_sinir_w": VO_V**2 * c * (rs + esr) / l,
        # ideal kontrolcu (duty aninda 0) ile yuk atma tepe gerilimi, enerji dengesi
        "atma_tepe_v": lambda i0, i1: math.sqrt(VO_V**2 + l * (i0**2 - i1**2) / c),
        # sert kalkis kestirimi (LC'ye basamak): Itepe ~ Vo / Z0 (LTspice ile %3 icinde uyusuyor)
        "sert_kalkis_itepe_a": VO_V / z0,
    }


# ---------------------------------------------------------------- 6) CPL kararliligi (tam ifade)
def cpl(l: float, c: float, esr: float, rs: float, vth: float, p: float) -> dict:
    """Sabit duty'li (acik cevrim) buck + sabit guc yuku: denge noktasi ve kucuk isaret kararliligi.

    Model: Thevenin kaynagi vth = D·Vin - (1-D)·Vf, seri L + rs (rs = DCR + D·Ron + (1-D)·Rd_dyn),
    paralel kol C + ESR, yuk i = P/v. Denge: vo = vth - rs·P/vo. Dengede yuk -R = -vo^2/P artimsal direnctir.
    Karakteristik denklem:  L C (R - ESR) s^2 + [R C (ESR + rs) - L - rs ESR C] s + (R - rs) = 0
    Kararlilik:  P < Pkritik = vo^2 (rs + ESR) / (L/C + rs ESR)      [birim: V^2·ohm / ohm^2 = W]
    sonum > 0 kararli (1/s); sonum < 0 ise salinim exp(-sonum·t) ile BUYUR.

    Gecerlilik siniri: CCM, ortalama model (f0 << fsw), ideal ve sonsuz bant genislikli CPL, dogrusal
    diyot/anahtar, ESL ve L(I) yok, kucuk isaret (buyuk salinimda sinir cevrimi olusur; genligi bu
    hesap vermez). Gercek yuklerin giris DC-DC'si sonlu bantlidir; bu hesap kotumser yondedir.
    """
    disc = vth * vth - 4 * rs * p
    if disc < 0:
        return {"vo": float("nan"), "r": float("nan"), "pkritik": float("nan"), "sonum": float("nan"),
                "f_hz": float("nan"), "kararli": False}
    vo = (vth + math.sqrt(disc)) / 2
    r = vo * vo / p if p > 0 else float("inf")
    if p > 0:
        a = l * c * (r - esr)
        b = r * c * (esr + rs) - l - rs * esr * c
        k = r - rs
    else:                                   # yuksuz: seri RLC
        a, b, k = l * c, c * (esr + rs), 1.0
    sonum = b / (2 * a)
    w2 = k / a - sonum * sonum
    # Pkritik kendi denge gerilimiyle: P = vo(P)^2 (rs+ESR)/(L/C + rs ESR), sabit nokta
    pk = VO_V ** 2 * (rs + esr) / (l / c + rs * esr)
    for _ in range(30):
        d2 = vth * vth - 4 * rs * pk
        vk = (vth + math.sqrt(max(d2, 0))) / 2
        pk = vk * vk * (rs + esr) / (l / c + rs * esr)
    return {"vo": vo, "r": r, "pkritik": pk, "sonum": sonum,
            "f_hz": math.sqrt(w2) / (2 * math.pi) if w2 > 0 else 0.0, "kararli": sonum > 0 and r > max(esr, rs)}


def cpl_seti(ad: str, l: float, c: float, esr: float, dcr: float, ron: float, vf: float, rd: float,
             vin: float = VIN_ANA_V, p_ayar: float = 57.64) -> dict:
    """Bir model seti icin: duty p_ayar gucunde 11 V'a ayarli (dogrula.py'deki yuk adimi gibi)."""
    io = p_ayar / VO_V
    d = (VO_V + vf + io * (dcr + rd)) / (vin + vf + io * (rd - ron))
    rs = dcr + d * ron + (1 - d) * rd
    vth = d * vin - (1 - d) * vf
    return {"ad": ad, "l": l, "c": c, "esr": esr, "rs": rs, "vth": vth, "d": d}


CPL_SETLERI = (
    # ad, L, C, ESR, DCR, Ron, Vf, Rd
    ("anma (şematik)", L_H, COUT_F, ESR_OUT_OHM, DCR_OHM, RON_OHM, VF_V, RD_OHM),
    ("pencere köşesi: L+%20, C−%20, ESR 15 mΩ", L_H * 1.2, COUT_F * 0.8, 15e-3, DCR_OHM, RON_OHM, VF_V, RD_OHM),
    ("el sarım: L+%8, C−%20, ESR 15 mΩ", L_H * 1.08, COUT_F * 0.8, 15e-3, DCR_OHM, RON_OHM, VF_V, RD_OHM),
    ("en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ", L_H * 1.2, COUT_F * 0.8, 15e-3, 6.5e-3, 4.7e-3, 0.39, 4e-3),
    ("en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ", L_H * 1.2, COUT_F * 0.8, 10e-3, 7.81e-3, 6.6e-3, 0.265, 6e-3),
    ("anma L/C, ESR 15 mΩ, Rd 4 mΩ", L_H, COUT_F, 15e-3, DCR_OHM, 4.7e-3, 0.39, 4e-3),
    ("anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ", L_H, COUT_F, 10e-3, DCR_OHM, 4.7e-3, 0.39, 4e-3),
    ("en çok kayıp (sıcak bakır/RDS, VF azami)", L_H, COUT_F, ESR_OUT_OHM, 10.3e-3, 7.84e-3, 0.415, 4.5e-3),
    ("soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır)", L_H, COUT_F, 120e-3, DCR_OHM, RON_OHM, VF_V, RD_OHM),
)


def cpl_dalli_kararli(l: float, c: float, esr: float, rs: float, vth: float, p: float,
                      cd: float = 0.0, rd: float = 1.0) -> bool:
    """cpl() ile ayni model + cikisa paralel Cd-Rd sonum dali. 3. derece; Routh-Hurwitz ile kararlilik."""
    disc = vth * vth - 4 * rs * p
    if disc < 0:
        return False
    vo = (vth + math.sqrt(disc)) / 2
    g = 1 / esr + (1 / rd if cd else 0.0) - p / (vo * vo)        # dugum iletkenligi (CPL negatif)
    if g <= 0:
        return False
    # durumlar x = [iL, vC, vCd];  v = (iL + vC/esr + vCd/rd) / g
    a = [[-rs / l - 1 / (g * l), -1 / (g * esr * l), (-1 / (g * rd * l)) if cd else 0.0],
         [1 / (g * esr * c), (1 / (g * esr) - 1) / (esr * c), (1 / (g * rd * esr * c)) if cd else 0.0],
         [0.0, 0.0, 0.0]]
    if not cd:
        tr = a[0][0] + a[1][1]
        det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
        return tr < 0 and det > 0
    a[2] = [1 / (g * rd * cd), 1 / (g * esr * rd * cd), (1 / (g * rd) - 1) / (rd * cd)]
    tr = a[0][0] + a[1][1] + a[2][2]
    m2 = sum(a[i][i] * a[j][j] - a[i][j] * a[j][i] for i, j in ((0, 1), (0, 2), (1, 2)))
    det = (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
           + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    a2, a1, a0 = -tr, m2, -det                                   # s^3 + a2 s^2 + a1 s + a0
    return a2 > 0 and a1 > 0 and a0 > 0 and a2 * a1 > a0


def cpl_dalli_pkritik(l, c, esr, rs, vth, cd=0.0, rd=1.0) -> float:
    lo, hi = 1.0, 600.0
    if not cpl_dalli_kararli(l, c, esr, rs, vth, lo, cd, rd):
        return 0.0
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cpl_dalli_kararli(l, c, esr, rs, vth, mid, cd, rd) else (lo, mid)
    return lo


# Sonum secenekleri (FZ-F). Hicbiri sematige UYGULANMADI; karar kullanicinindir.
# (ad, L carpani, C [F] anma, ESR senaryosu [ohm], ek DCR [ohm], Cd [F], Rd [ohm], ek kayip aciklamasi)
SONUM_SECENEKLERI = (
    ("mevcut: 33 µH + 1000 µF", 1.0, 1000e-6, None, 0.0, 0.0, 1.0, "—"),
    ("DCR +5 mΩ (≈ 12,8 mΩ)", 1.0, 1000e-6, None, 5e-3, 0.0, 1.0, "+0,28 W"),
    ("DCR +10 mΩ (≈ 17,8 mΩ)", 1.0, 1000e-6, None, 10e-3, 0.0, 1.0, "+0,57 W"),
    ("Cout 1500 µF (ESR × 0,67 varsayımı)", 1.0, 1500e-6, 0.67, 0.0, 0.0, 1.0, "—"),
    ("Cout 2 × 680 µF (eşdeğer ESR × 0,5·1,3 varsayımı)", 1.0, 1360e-6, 0.65, 0.0, 0.0, 1.0, "—"),
    ("Cout 2 × 1000 µF (eşdeğer ESR × 0,5)", 1.0, 2000e-6, 0.5, 0.0, 0.0, 1.0, "—"),
    ("sönüm dalı 470 µF + 0,22 Ω", 1.0, 1000e-6, None, 0.0, 470e-6, 0.22, "≈ 2 mW"),
    ("sönüm dalı 1000 µF + 0,15 Ω", 1.0, 1000e-6, None, 0.0, 1000e-6, 0.15, "≈ 3 mW"),
    ("sönüm dalı 2200 µF + 0,10 Ω", 1.0, 1000e-6, None, 0.0, 2200e-6, 0.10, "≈ 5 mW"),
    ("sönüm dalı 1000 µF + 0,33 Ω", 1.0, 1000e-6, None, 0.0, 1000e-6, 0.33, "≈ 1 mW"),
)


# ---------------------------------------------------------------- 7) kayip
def ara(tablo, x: float) -> float:
    """Parcali dogrusal ara deger (uclarda sabit)."""
    if x <= tablo[0][0]:
        return tablo[0][1]
    for (x0, y0), (x1, y1) in zip(tablo, tablo[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tablo[-1][1]


def l1_cekirdek(vin: float, io: float = IO_A) -> dict:
    """Cekirdek kaybi: dB volt-saniyeden (akim ripple'indan DEGIL) hesaplanir."""
    k = nokta(vin, io)
    v_l = vin - VO_V - io * (RON_OHM + DCR_OHM)          # iletimde bobin gerilimi
    volt_s = v_l * k["d"] / FSW_HZ
    db = volt_s / (L1_N * L1_AE_M2)                      # T, tepe-tepe
    p_cm3 = L1_KAYIP_100K_100MT * (db / 2 / 0.1) ** L1_B_USSU   # mW/cm3 (azami egri olcegi)
    return {"volt_s": volt_s, "db": db, "p_w": p_cm3 * L1_VE_CM3 / 1e3}


def l1_bakir(il_rms: float, di: float, t_c: float = 20.0) -> dict:
    dcr = DCR_OHM * (1 + BAKIR_ALFA * (t_c - 20))
    # litz 0,20 mm tel, 100 kHz'te deri kalinligi ~0,21 mm: AC/DC orani ~1 alindi (yakinlik etkisi HESAPLANMADI)
    return {"dcr": dcr, "p_w": il_rms ** 2 * dcr, "p_ac_w": di ** 2 / 12 * dcr}


def l1_bias(i: float) -> float:
    """Verilen akimda L / L0 (uretici DC bias egrisinden, yaklasik okuma)."""
    return ara(L1_BIAS, L1_N * i) / L1_AL_NH


def s1_anahtarlama(vin: float, i_vadi: float, i_tepe: float, rg: float, vdrv: float = 10.0) -> dict:
    """Anahtarlama kaybi KESTIRIMI (surucu secilmedi; rg = toplam kapi direnci, vdrv = surme gerilimi VARSAYIM).

    Gecis suresi: Qsw = Qgd + Qgs/2 (100 A kosullu veri sayfasi degeri; 7,5 A'de daha kucuktur -> ust kestirim).
    Ek: Coss enerjisi ve D1 eklem kapasitesinin sarji her acilista S1'de harcanir.
    """
    qsw = S1_QGD + S1_QGS / 2
    t_ac = qsw * rg / (vdrv - S1_VPLATO)
    t_kapa = qsw * rg / S1_VPLATO
    p_gecis = 0.5 * vin * (i_vadi * t_ac + i_tepe * t_kapa) * FSW_HZ
    # Coss gerilimle azalir; 25 V'taki degerin ~1,5 kati enerji-esdegeri alindi (TAHMIN)
    p_coss = 0.5 * 1.5 * S1_COSS_25V * vin ** 2 * FSW_HZ
    # D1 cifti: Cj(V) egrisinden yuk, Q ~ 2·Cj(V)·V/(1-m), m ~ 0,45
    q_d = 2 * ara(D1_CJ, vin) * vin / 0.55
    p_dkap = q_d * vin * FSW_HZ
    p_kapi = S1_QG * vdrv * FSW_HZ                       # surucude harcanir, S1'de degil
    return {"t_ac": t_ac, "t_kapa": t_kapa, "p_gecis": p_gecis, "p_coss": p_coss, "p_dkap": p_dkap,
            "p_s1": p_gecis + p_coss + p_dkap, "p_kapi": p_kapi}


def d1_kayip(tj: float, vin: float, senaryo: str = "azami", io: float = IO_A) -> dict:
    """D1 cifti: iletim (VF sicaklikla DUSER) + ters kacak (sicaklikla USTEL ARTAR)."""
    k = nokta(vin, io)
    (v25, r25), (v125, r125) = D1_VF[senaryo]
    t = min(max((tj - 25) / 100, 0.0), 1.25)
    v0, r = v25 + (v125 - v25) * t, r25 + (r125 - r25) * t
    p_il = v0 * k["d_avg"] + r * k["d_rms"] ** 2
    ir = D1_IR_125_60V[senaryo] * D1_IR_VR_CARPAN * 2 ** ((tj - 125) / D1_IR_IKIYE_K)   # A/diyot, VR = vin
    p_ters = 2 * ir * vin * k["d"]
    return {"p_il": p_il, "p_ters": p_ters, "p": p_il + p_ters, "ir_ma": 2 * ir * 1e3}


def isil_denge(kayip, rth: float, ta: float, tj_max: float) -> tuple[float, float, bool]:
    """Tj = Ta + Rth·P(Tj) sabit noktasi. (Tj, P, kararli). Kacakta (inf, inf, False)."""
    tj = ta
    for _ in range(400):
        p = kayip(tj)
        yeni = ta + rth * p
        if yeni > tj_max + 150:
            return float("inf"), float("inf"), False
        if abs(yeni - tj) < 1e-3:
            # kararlilik: dP/dT < 1/Rth
            egim = (kayip(yeni + 0.5) - kayip(yeni - 0.5))
            return yeni, p, egim < 1 / rth
        tj = tj + 0.5 * (yeni - tj)
    return float("inf"), float("inf"), False


def s1_kayip(tj: float, vin: float, rg: float, ron: float = S1_RON_MAX) -> float:
    k = nokta(vin)
    il = k["sw_rms"] ** 2 * ron * ara(S1_RON_CARPAN, tj)
    return il + s1_anahtarlama(vin, IO_A - k["di"] / 2, k["ipk"], rg)["p_s1"]


def sicak_takma(vbat: float, r_kaynak: float, l_kaynak: float, c: float = CIN_F, esr: float = ESR_IN_OHM) -> float:
    """Bos Cin'e basamak: seri RLC'nin kondansator UCLARINDAKI tepe gerilimi (ESR dahil, yuksuz, anahtar kapali)."""
    r = r_kaynak + esr
    w0 = 1 / math.sqrt(l_kaynak * c)
    z = r / 2 * math.sqrt(c / l_kaynak)
    if z >= 1:
        return vbat
    wd = w0 * math.sqrt(1 - z * z)
    # kapasitor gerilimi tepe: vbat (1 + exp(-z pi / sqrt(1-z^2))); ESR uzerindeki dusum tepede sifirdir (i = 0)
    return vbat * (1 + math.exp(-z * math.pi / math.sqrt(1 - z * z)))


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("ANALİTİK HESAP (LTspice veya ölçüm değil)")
    print(f"L={L_H*1e6:g} µH/{DCR_OHM*1e3:g} mΩ  COUT={COUT_F*1e6:g} µF/{ESR_OUT_OHM*1e3:g} mΩ  "
          f"CIN={CIN_F*1e6:g} µF/{ESR_IN_OHM*1e3:g} mΩ  Ron={RON_OHM*1e3:g} mΩ  Vf={VF_V:g} V+{RD_OHM*1e3:g} mΩ  "
          f"fsw={FSW_HZ/1e3:g} kHz  Io={IO_A:g} A")

    print("\n1) Kararlı durum, 11 V / 7,5 A (duty her girişte 11 V'a göre; düşümler dahil)")
    print("  Vin     D    Ton_us  dIL  ILtepe Ikritik ICINrms ICOUTrms S1rms D1ort dVout_mV dVin_mV  P_S1  P_D1  P_L1 toplam  verim%")
    for v in VIN_V:
        k = nokta(v)
        print(f"{k['vin']:5.1f} {k['d']:.4f} {k['ton_us']:6.3f} {k['di']:5.2f} {k['ipk']:6.2f} {k['ikritik']:6.2f}"
              f" {k['icin_rms']:7.2f} {k['icout_rms']:8.2f} {k['sw_rms']:5.2f} {k['d_avg']:5.2f} {k['dvout']*1e3:8.1f}"
              f" {k['dvin']*1e3:7.1f} {k['p_s1']:5.2f} {k['p_d1']:5.2f} {k['p_l1']:5.2f} {k['kayip']:6.2f} {k['verim']*100:7.2f}")
    print("  Verim yalnız iletim kayıplarıdır; anahtarlama, çekirdek ve sürücü kayıpları bölüm 7'dedir.")
    print("  Ton, PULSE kaynağının süresinden 10 ns uzundur (10 ns kenarların ortasında anahtarlanır).")

    kose = nokta(max(VIN_V), l=L_H * (1 - L_DUSUK), c=COUT_F * (1 - C_TOL), esr=ESR_OUT_MAX_OHM)
    print(f"\n2) Tolerans köşesi (26 V, L −%30, Cout −%20, ESR 35 mΩ): dIL={kose['di']:.2f} A, ILtepe={kose['ipk']:.2f} A,"
          f" Isat ölçütü (+%30)={kose['ipk']*(1+SATURATION_MARGIN):.1f} A, dVout={kose['dvout']*1e3:.1f} mV")

    print("\n3) Yük uyumu (11 V çıkış) — referans yükler; genel modül zarfı 0–7,5 A / 82,5 W")
    print(f"  O1  DC girişi {O1_VMIN:g}–{O1_VMAX:g} V: 11 V uygun, üst sınıra pay {O1_VMAX-VO_V:g} V (mutlak maksimum yayımlanmamış)")
    print(f"  S2E {S2E_VMIN:g}–{S2E_VMAX:g} V: 11 V uygun; izinli ripple ±{S2E_RIPPLE*VO_V*1e3:.0f} mV")
    i_s2e, i_s2e_k = P_S2E_CALISMA_W / VO_V, P_S2E_KALKIS_W / VO_V
    print(f"  Akım @11 V: S2E çalışma {i_s2e:.2f} A, S2E kalkış {i_s2e_k:.2f} A, O1 zarf {O1_IMAX:g} A")
    print(f"  Sürekli zarf {O1_IMAX+i_s2e:.2f} A, anlık zarf {O1_IMAX+i_s2e_k:.2f} A  →  7,5 A hedefinde pay"
          f" {(IO_A/(O1_IMAX+i_s2e_k)-1)*100:.0f} %")

    d0 = duty(VIN_ANA_V, IO_A)
    print(f"\n4) Açık çevrim: duty {d0:.4f} sabit (24,6 V / 7,5 A ayarı), direnç yükte kararlı çıkış [V]")
    amper = (0.24, 0.6, 1.15, 2.5, 5.24, 7.5)
    print("  Vin \\ yük A@11V " + " ".join(f"{a:6g}" for a in amper))
    for v in VIN_V:
        print(f"  {v:5.1f}           " + " ".join(f"{acik_cevrim_vo(v, d0, VO_V / a):6.2f}" for a in amper))
    print("  0 A'de (yüksüz) açık çevrim çıkışı giriş gerilimine tırmanır (tepe doğrultma): 20–26 V > Cout 25 V anma.")

    q = dinamik()
    print(f"\n5) LC dinamiği: f0={q['f0_hz']:.0f} Hz, Z0={q['z0']:.3f} Ω, ESR sıfırı={q['f_esr_hz']/1e3:.1f} kHz")
    qk = dinamik(L_H * (1 + L_YUKSEK), COUT_F * (1 - C_TOL), ESR_OUT_MIN_OHM)
    i0, i1 = O1_IMAX + i_s2e_k, (4.0 + P_S2E_CALISMA_W) / VO_V
    print(f"  Yük atma {i0:.2f}→{i1:.2f} A, ideal kontrolcü sınırı: {q['atma_tepe_v'](i0, i1):.2f} V"
          f" (köşe {qk['atma_tepe_v'](i0, i1):.2f} V); ESR sıçraması ΔI·ESR ayrıca eklenir"
          f" (7,5 A × 35 mΩ = {7.5*0.035*1e3:.0f} mV; −10 °C Zmax 120 mΩ ile {7.5*0.12:.2f} V)")
    print(f"  Sert kalkış kestirimi (yumuşak kalkış yok): ILtepe ≈ {q['sert_kalkis_itepe_a']:.0f} A;"
          f" bu akımda L/L0 ≈ {l1_bias(q['sert_kalkis_itepe_a'])*100:.0f} % (üretici bias eğrisi) → gerçek tepe daha yüksek")

    print("\n6) Sabit güç yükü (CPL) ile açık çevrim kararlılığı — tam ifade, gerçek denge noktası")
    print("   Pkritik = Vo²(Rs+ESR)/(L/C+Rs·ESR);  Rs = DCR + D·Ron + (1−D)·Rd;  duty 57,64 W'ta 11 V'a ayarlı, 24,6 V")
    print("   sönüm > 0: salınım söner (zaman sabiti 1/sönüm); sönüm < 0: BÜYÜR. Geçerlilik: cpl() açıklaması.")
    print(f"   {'model seti':56s} Rs mΩ  Pkritik W | 57,64 W: sönüm 1/s | 73 W: Vo V  sönüm 1/s  τ ms   | 82,5 W: sönüm 1/s  τ ms")
    for ad, l, c, esr, dcr, ron, vf, rd in CPL_SETLERI:
        s = cpl_seti(ad, l, c, esr, dcr, ron, vf, rd)
        a57, a73, a82 = (cpl(l, c, esr, s["rs"], s["vth"], pw) for pw in (57.64, 73.0, 82.5))
        tau = lambda x: f"{1e3/abs(x['sonum']):6.0f}{'' if x['sonum'] > 0 else '↑'}"
        print(f"   {ad:56s} {s['rs']*1e3:5.1f}  {a73['pkritik']:7.1f}   | {a57['sonum']:+9.1f}          |"
              f" {a73['vo']:6.3f} {a73['sonum']:+9.1f} {tau(a73):>7s}   | {a82['sonum']:+9.1f} {tau(a82):>7s}")
    print("   ↑ = büyüyen salınımın zaman sabiti. Basitleştirilmiş eski sınır (Rs·ESR yok, Vo = 11 V):"
          f" anma {q['p_cpl_sinir_w']:.0f} W, köşe {qk['p_cpl_sinir_w']:.0f} W.")
    print("   Gerekli pay tanımlı değildir (kullanıcı kararı); 82,5 W zarfı köşede Pkritik'in ÜSTÜNDEDİR.")

    print("\n6b) Sönüm seçenekleri: Pkritik [W] (HESAP, 24,6 V; hiçbiri şematiğe uygulanmadı)")
    print("   Köşe = L +%20, ana Cout −%20, sönüm dalı kondansatörü −%20. ESR senaryoları: 15 mΩ (pencere alt kenarı) ve")
    print("   10 mΩ (TAHMİN, sıcak); paralel/büyük kondansatörde ESR parantezdeki oranla ölçeklenir (VARSAYIM, ölçüm yok).")
    print("   Rs: şematik (14,7 mΩ) ve en az sönüm (DCR 6,5, Ron 4,7, Rd 4 mΩ → 10,8 mΩ) setleri.")
    print(f"   {'seçenek':52s} anma/35mΩ  köşe/15mΩ  köşe/10mΩ  en az sönüm köşe/15mΩ  köşe/10mΩ   ek kayıp")
    for ad, kl, c, esr_k, ek_dcr, cd, rdd, kayip_ack in SONUM_SECENEKLERI:
        h = []
        for dcr, ron, vf, rd_, lk, ck, esr in (
                (DCR_OHM, RON_OHM, VF_V, RD_OHM, 1.0, 1.0, 35e-3),
                (DCR_OHM, RON_OHM, VF_V, RD_OHM, 1.2, 0.8, 15e-3),
                (DCR_OHM, RON_OHM, VF_V, RD_OHM, 1.2, 0.8, 10e-3),
                (6.5e-3, 4.7e-3, 0.39, 4e-3, 1.2, 0.8, 15e-3),
                (6.5e-3, 4.7e-3, 0.39, 4e-3, 1.2, 0.8, 10e-3)):
            e = esr * (esr_k or 1.0)
            s = cpl_seti(ad, L_H * kl * lk, c * ck, e, dcr + ek_dcr, ron, vf, rd_)
            h.append(cpl_dalli_pkritik(s["l"], s["c"], e, s["rs"], s["vth"], cd * ck, rdd))
        print(f"   {ad:52s} {h[0]:7.0f}    {h[1]:7.0f}    {h[2]:7.0f}    {h[3]:14.0f}    {h[4]:10.0f}      {kayip_ack}")
    print("   82,5 W zarfının üstünde kalan hücreler doğal (açık çevrim) kararlıdır; altında kalanlar kararsızdır.")

    print("\n7) Kayıp bütçesi, 7,5 A (HESAP; sürücü seçilmedi: Rg toplam ve 10 V sürme VARSAYIM)")
    print("   L1 çekirdek: ΔB = volt·saniye/(N·Ae); kayıp 900 mW/cm³ @100 kHz/100 mT AZAMİ noktasından B² ile ölçeklendi (ÇIKARIM)")
    for v in VIN_V:
        c = l1_cekirdek(v)
        print(f"     Vin {v:4.1f} V: volt·saniye {c['volt_s']*1e6:5.1f} µV·s, ΔB {c['db']*1e3:5.1f} mT t-t, çekirdek ≤ {c['p_w']:.3f} W")
    print("     Çekirdek kaybı akım ripple'ına değil volt·saniyeye bağlıdır: L −%30 köşesinde (ΔIL 2,8 A) ΔB DEĞİŞMEZ.")
    print("   Vin     S1 iletim  S1 anaht. (Rg 5/10/25 Ω)   D1 iletim  L1 bakır  L1 çekirdek  Cin    Cout   toplam (Rg 10)  verim %   kapı sürme")
    for v in VIN_V:
        k = nokta(v)
        sw = [s1_anahtarlama(v, IO_A - k["di"] / 2, k["ipk"], rg) for rg in (5, 10, 25)]
        cin = k["icin_rms"] ** 2 * ESR_IN_OHM
        co = k["icout_rms"] ** 2 * ESR_OUT_OHM
        cek = l1_cekirdek(v)["p_w"]
        top = k["kayip"] + sw[1]["p_s1"] + cek + cin + co
        print(f"   {v:4.1f}    {k['p_s1']:5.2f}      {sw[0]['p_s1']:4.2f} / {sw[1]['p_s1']:4.2f} / {sw[2]['p_s1']:4.2f}          {k['p_d1']:5.2f}      {k['p_l1']:5.2f}      {cek:5.2f}     {cin:5.2f}  {co:5.3f}     {top:5.2f}        {VO_V*IO_A/(VO_V*IO_A+top)*100:5.2f}     {sw[1]['p_kapi']*1e3:.0f} mW")
    sw = s1_anahtarlama(26.0, 6.5, 8.5, 10)
    print(f"   Geçiş süreleri (Rg 10 Ω, 26 V): açma {sw['t_ac']*1e9:.0f} ns, kapama {sw['t_kapa']*1e9:.0f} ns;"
          f" bileşenler: geçiş {sw['p_gecis']:.2f} W, Coss {sw['p_coss']:.2f} W, D1 kapasitesi {sw['p_dkap']:.2f} W")
    print("   Snubber kaybı (kullanılırsa) C·V²·f: 1 nF → 68 mW, 2,2 nF → 149 mW (26 V). Sayılar kestirimdir; ölçülmedi.")

    print("\n8) Isıl denge (HESAP; Rth(ped) = 1 K/W ve soğutucu değerleri VARSAYIM, parça seçilmedi)")
    print("   D1 çifti: iletim kaybı sıcaklıkla düşer, ters kaçak ≈ her 12 K'de ikiye katlanır; denge Tj = Ta + Rth·P(Tj)")
    print("   'KAÇAK' = sabit nokta yok veya dP/dTj ≥ 1/Rth (veri sayfası Tablo 2 dipnot 3 koşulu sağlanmıyor)")
    print("   senaryo  Rth(s-a) K/W   " + "   ".join(f"Ta {ta} °C: Tj / P" for ta in (25, 50, 60)))
    for sen in ("tipik", "azami"):
        for ad, rsa in (("soğutucusuz", None), ("20", 20.0), ("12", 12.0), ("8", 8.0), ("5", 5.0)):
            rth = TO220_RTH_JA if rsa is None else D1_RTH_JC_TOPLAM + RTH_PED + rsa
            h = []
            for ta in (25, 50, 60):
                tj, pw, ok = isil_denge(lambda t: d1_kayip(t, 26.0, sen)["p"], rth, ta, D1_TJ_MAX)
                h.append("KAÇAK          " if not ok or tj > D1_TJ_MAX else f"{tj:5.0f} °C / {pw:4.2f} W")
            print(f"   {sen:7s}  {ad:12s}   " + "   ".join(h))
    for tj in (25, 75, 100, 125, 150):
        d = d1_kayip(tj, 26.0, "azami")
        print(f"     D1 azami @Tj {tj:3d} °C, 26 V: iletim {d['p_il']:.2f} W + ters {d['p_ters']:.2f} W (IR {d['ir_ma']:.0f} mA toplam) = {d['p']:.2f} W")
    print("   S1 (RDS(on) azami, Rg 10 Ω, 20 V giriş = en yüksek iletim):")
    for ad, rth in (("soğutucusuz (62,5 K/W, TAHMİN)", TO220_RTH_JA), ("ped + 12 K/W", S1_RTH_JC + RTH_PED + 12), ("ped + 8 K/W", S1_RTH_JC + RTH_PED + 8)):
        h = []
        for ta in (25, 50, 60):
            tj, pw, ok = isil_denge(lambda t: s1_kayip(t, 20.0, 10), rth, ta, S1_TJ_MAX)
            h.append(f"{tj:5.0f} °C / {pw:4.2f} W")
        print(f"     {ad:32s} " + "   ".join(h))
    # ortak sogutucu: S1 + D1 ayni sogutucuda
    print("   Ortak soğutucu (S1 + D1 aynı soğutucuda, ayrı pedlerle), D1 azami, S1 azami, 26 V:")
    for rsa in (12.0, 8.0, 5.0):
        h = []
        for ta in (25, 50, 60):
            ts = ta
            for _ in range(300):
                tjd = ts + (D1_RTH_JC_TOPLAM + RTH_PED) * d1_kayip(ts + 5, 26.0, "azami")["p"]
                for _ in range(50):
                    tjd = ts + (D1_RTH_JC_TOPLAM + RTH_PED) * d1_kayip(tjd, 26.0, "azami")["p"]
                    if tjd > 400:
                        break
                tjs = ts + (S1_RTH_JC + RTH_PED) * s1_kayip(ts + 3, 26.0, 10)
                pt = d1_kayip(min(tjd, 400), 26.0, "azami")["p"] + s1_kayip(tjs, 26.0, 10)
                yeni = ta + rsa * pt
                if yeni > 300:
                    ts = float("inf")
                    break
                ts += 0.3 * (yeni - ts)
            h.append("KAÇAK                 " if ts == float("inf") or tjd > D1_TJ_MAX else f"Ts {ts:4.0f} / TjD1 {tjd:4.0f} °C")
        print(f"     Rth(s-a) {rsa:4.1f} K/W:  " + "   ".join(f"Ta {ta}: {x}" for ta, x in zip((25, 50, 60), h)))
    kk = nokta(26.0)
    for t in (20, 75, 100):
        b = l1_bakir(kk["il_rms"], kk["di"], t)
        pt = b["p_w"] + l1_cekirdek(26.0)["p_w"]
        print(f"   L1 @{t:3d} °C sargı: DCR {b['dcr']*1e3:.2f} mΩ, bakır {b['p_w']:.2f} W (bunun AC payı {b['p_ac_w']*1e3:.0f} mW) + çekirdek"
              f" → {pt:.2f} W; ΔT ≈ (mW/cm²)^0,833 = {(pt*1e3/L1_YUZEY_CM2)**0.833:.0f} K (Magnetics yaklaşık formülü)")
    print(f"   L1 doyma: L/L0 @8,9 A {l1_bias(8.9)*100:.0f} %, @12 A {l1_bias(12)*100:.0f} %, @20 A {l1_bias(20)*100:.0f} %,"
          f" @53 A {l1_bias(53)*100:.0f} % (eğriden yaklaşık; ölçüm yok)")
    print(f"   Cin ripple: {max(nokta(v)['icin_rms'] for v in VIN_V):.2f} A toplam → adet başına {max(nokta(v)['icin_rms'] for v in VIN_V)/2:.2f} A"
          f" (anma {CIN_IRIPPLE} A @105 °C); Cout: {max(nokta(v)['icout_rms'] for v in VIN_V):.2f} A (anma {COUT_IRIPPLE} A)")

    print("\n9) Gerilim sınıfları ve arıza arayüzü (HESAP; kaynak R/L VARSAYIM süpürmesi)")
    print("   Sıcak takma: boş Cin'e 26 V basamak, tepe V(Cin) [V]; 35 V anma aşılırsa * (ESR 7,5 mΩ, C 2000 µF)")
    ls = (0.2e-6, 0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6)
    print("     R kaynak mΩ \\ L µH " + " ".join(f"{l*1e6:6g}" for l in ls))
    for r in (5e-3, 10e-3, 20e-3, 40e-3, 80e-3):
        print(f"     {r*1e3:6.0f}             " + " ".join(f"{(v:=sicak_takma(26.0, r, l)):5.1f}{'*' if v > CIN_VDC else ' '}" for l in ls))
    print("   C −%20 ve sıcak ESR (TAHMİN 2 × 7 mΩ) ile en kötü satır:"
          f" R 5 mΩ, L 5 µH → {sicak_takma(26.0, 5e-3, 5e-6, CIN_F*0.8, 3.5e-3):.1f} V")
    print(f"   S1 kısa devre: çıkış kararlı hâlde giriş gerilimine çıkar (20–26 V) → Cout {COUT_VDC:g} V anması 26 V'ta AŞILIR;")
    print(f"     LC basamağı aşımı ayrıca eklenir (SİM: dogrula.py stres). Yüksüz açık çevrimde de çıkış girişe tırmanır.")
    print(f"   S1 VDS: {S1_VDS_MAX:g} V anma; 26 V girişte pay {S1_VDS_MAX-26:g} V, 28 V'ta {S1_VDS_MAX-28:g} V (zil hariç)."
          f" D1 VRRM {D1_VRRM:g} V aynı.")
