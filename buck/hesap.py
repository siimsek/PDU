#!/usr/bin/env python3
"""Analitik hesap: tek faz, asenkron, acik cevrim buck guc kati.

Bu betik LTspice calistirmaz; denklemlerden ozet tablolari ekrana yazar (ANALITIK HESAP).
Simulasyon karsiligi `python buck/dogrula.py` ile alinir. Fiziksel olcum yoktur.
Degerler ana sematikle aynidir; bulunan parcaya gore asagidaki sabitler degistirilir.
"""
from __future__ import annotations

import math

VO_V = 11.0
IO_A = 7.5                                   # tasarim akimi (yuk zarfi 6,64 A + pay)
VIN_V = (20.0, 22.2, 24.6, 25.2, 26.0)       # zorunlu test noktalari
VIN_ANA_V = 24.6
FSW_HZ = 100_000.0

# Ana sematikteki degerler = secilen parcalarin veri sayfasi degerleri (PARCA-HEDEFLERI.md)
L_H = 33e-6             # Bourns 2300HT-330: 33 uH @0 A; 13,6 A'de 23 uH (demir tozu, yumusak doyum)
DCR_OHM = 15e-3         # maks
COUT_F = 680e-6         # Rubycon 25ZLH680M 10x16
ESR_OUT_OHM = 28e-3     # 100 kHz empedans, maks; hedef pencere 20-30 mohm
CIN_F = 1360e-6         # 2 x Panasonic EEUFR1V681B (680 uF / 35 V)
ESR_IN_OHM = 10e-3      # 2 x 20 mohm paralel
RON_OHM = 11e-3         # STP75NF75, 25 C maks
VF_V = 0.46             # IXYS DSB60C60HB esik gerilimi (150 C, kayip hesabi icin)
RD_OHM = 3.1e-3         # 6,2 mohm/bacak, iki bacak paralel

L_DUSUK = 0.30          # akim altinda dusum (~%17 @ 7,5-8,5 A, dogrusal varsayim) + %15 tolerans
L_YUKSEK = 0.15
C_TOL = 0.20
ESR_TOL = 0.20
SATURATION_MARGIN = 0.30

# Yukler. DATASHEET: uretici belgesi; TAHMIN: yayimlanmis deger yok.
O1_VMIN, O1_VMAX, O1_IMAX = 5.0, 12.0, 5.0        # DATASHEET  T3 Gemstone O1 DC girisi 5-12 V / 5 A
S2E_VMIN, S2E_VMAX = 9.0, 28.0                    # DATASHEET  RPLIDAR S2E 9-28 V (tipik 12 V)
S2E_RIPPLE = 0.03                                 # DATASHEET  besleme ripple'i en cok %3
P_S2E_CALISMA_W = 12 * 0.22                       # DATASHEET  12 V'ta en cok 0,22 A
P_S2E_KALKIS_W = 12 * 1.5                         # DATASHEET  12 V'ta en cok 1,5 A (sure verilmemis)
P_O1_ZARF_W = VO_V * O1_IMAX                      # DATASHEET  anma akimi; gercek tuketim degil
P_O1_TIPIK_W = 10.0                               # TAHMIN


def duty(vin: float, io: float, vo: float = VO_V) -> float:
    """CCM duty; anahtar, diyot ve bobin dusumleri dahil."""
    return (vo + VF_V + io * (DCR_OHM + RD_OHM)) / (vin + VF_V + io * (RD_OHM - RON_OHM))


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
        "icout_rms": di / math.sqrt(12), "sw_rms": sw_rms, "d_avg": d_avg,
        "dvout": di * (esr + 1 / (8 * FSW_HZ * c)),
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
        # sabit guc yukuyle acik cevrim LC'nin kararlilik siniri: R_yuk > L / (C (Rs + ESR))
        "p_cpl_sinir_w": VO_V**2 * c * (rs + esr) / l,
        # ideal kontrolcu (duty aninda 0) ile yuk atma tepe gerilimi, enerji dengesi
        "atma_tepe_v": lambda i0, i1: math.sqrt(VO_V**2 + l * (i0**2 - i1**2) / c),
        # sert kalkis kestirimi (LC'ye basamak): Itepe ~ Vo / Z0 (LTspice ile %3 icinde uyusuyor)
        "sert_kalkis_itepe_a": VO_V / z0,
    }


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
    print("  Verim yalnız iletim kayıplarıdır; anahtarlama, çekirdek ve sürücü kayıpları yoktur.")

    kose = nokta(max(VIN_V), l=L_H * (1 - L_DUSUK), c=COUT_F * (1 - C_TOL), esr=ESR_OUT_OHM * (1 + ESR_TOL))
    print(f"\n2) Tolerans köşesi (26 V, L −%30, Cout −%20, ESR +%20): dIL={kose['di']:.2f} A, ILtepe={kose['ipk']:.2f} A,"
          f" Isat ölçütü (+%30)={kose['ipk']*(1+SATURATION_MARGIN):.1f} A, dVout={kose['dvout']*1e3:.1f} mV")

    print("\n3) Yük uyumu (11 V çıkış)")
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

    q = dinamik()
    print(f"\n5) LC dinamiği: f0={q['f0_hz']:.0f} Hz, Z0={q['z0']:.3f} Ω, ESR sıfırı={q['f_esr_hz']/1e3:.1f} kHz")
    print(f"  Sabit güç yüküyle açık çevrim kararlılık sınırı: P < {q['p_cpl_sinir_w']:.0f} W"
          f" (zarf {P_O1_ZARF_W+P_S2E_CALISMA_W:.1f} W, S2E kalkışında {P_O1_ZARF_W+P_S2E_KALKIS_W:.1f} W)")
    qk = dinamik(L_H * (1 + L_YUKSEK), COUT_F * (1 - C_TOL), ESR_OUT_OHM * (1 - ESR_TOL))
    print(f"  Köşe (L +%15, Cout −%20, ESR −%20): P < {qk['p_cpl_sinir_w']:.0f} W")
    i0, i1 = O1_IMAX + i_s2e_k, (4.0 + P_S2E_CALISMA_W) / VO_V
    print(f"  Yük atma {i0:.2f}→{i1:.2f} A, ideal kontrolcü sınırı: {q['atma_tepe_v'](i0, i1):.2f} V"
          f" (köşe {qk['atma_tepe_v'](i0, i1):.2f} V)")
    print(f"  Sert kalkış kestirimi (yumuşak kalkış yok): ILtepe ≈ {q['sert_kalkis_itepe_a']:.0f} A")
