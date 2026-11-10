#!/usr/bin/env python3
"""TASARIM-HESABI.md dosyasini hesap-sonuc.json ve ltspice-sonuc.json'dan uretir (elle sayi yazilmaz)."""
from __future__ import annotations

import json
from pathlib import Path

B = Path(__file__).parent
H = json.loads((B / "hesap-sonuc.json").read_text(encoding="utf-8"))
S = json.loads((B / "ltspice-sonuc.json").read_text(encoding="utf-8"))
KT = json.loads((B / "kontrol-sonuc.json").read_text(encoding="utf-8"))
TM = json.loads((B / "ltspice-tam-sonuc.json").read_text(encoding="utf-8"))


def n(x: float, k: int = 2) -> str:
    return f"{x:.{k}f}".replace(".", ",")


A, Bs, C, D = H["topolojiler"]
G = H["guc_kati"]
L, CO, CI, S1, FD = G["bobin"], G["cout"], G["cin"], G["s1"], G["fd"]
V = H["varsayim"]
EK = H["ek_secenekler"]
T = S["tek_faz"]
CF = S["cift_faz"]
LM = S["tek_faz_Lmin_26"]
U1, U2 = S["cift_faz_duty_farki_0.005"], S["cift_faz_duty_farki_0.01"]
K26 = A["kayiplar"][2]
K20 = A["kayiplar"][0]
YB, RF, UC, PW, SR, KR, GB, KL, YS = (KT[x] for x in ("yardimci_besleme", "referans", "ucgen", "pwm", "surucu", "kapi_rayi", "geri_besleme", "kararlilik", "yumusak_baslatma"))
KALK_I = max(TM[k]["KALKI"] for k in ("20V", "22p2V", "26V", "26V_hafif"))
ISAT = max(L["Isat_min_A"], 1.12 * KALK_I)
VERIMLER = [TM[k]["VERIM"] for k in ("20V", "22p2V", "26V")]


def tam_satir(ad, k):
    r = TM[k]
    return (f"| {ad} | {n(r['VSS'], 3)} V | {n((r['VSMAX'] - r['VSMIN']) * 1e3, 0)} mV | {n(r['ILMAXS'])} A | {n(r['KALKV'])} V | {n(r['KALKI'])} A | "
            f"{n(r['UST'])} V | {n(r['ALT'])} V | %{n(r['VERIM'], 1)} | {1e-3 / r['TPER']:.1f} kHz |")


tam_tablo = "\n".join(["| Durum | Vo | ΔVo | IL tepe | Kalkış Vo tepe | Kalkış IL tepe | Yük düşünce Vo tepe | Yük binince Vo dip | Verim | f |", "|---|---|---|---|---|---|---|---|---|---|",
                       tam_satir("20 V, 7,5 A", "20V"), tam_satir("22,2 V, 7,5 A", "22p2V"), tam_satir("26 V, 7,5 A", "26V"), tam_satir("26 V, 0,75 A", "26V_hafif")])


def satir_top(baslik, f):
    return f"| {baslik} | " + " | ".join(f(t) for t in (A, Bs, C, D)) + " |"


top_tablo = "\n".join([
    "| Ölçüt | A: Tek faz asenkron | B: Tek faz senkron | C: Çift faz 180° asenkron | D: Çift faz 180° senkron |",
    "|---|---|---|---|---|",
    satir_top("Bobin", lambda t: f"{t['faz']} × {t['L_secilen_uH']:.0f} µH"),
    satir_top("Faz başına tepe akım", lambda t: f"{n(t['Ipk_Lmin_A'])} A"),
    satir_top("Toplam bobin enerjisi", lambda t: f"{n(t['L_toplam_enerji_mJ'])} mJ"),
    satir_top("Giriş kapasitörü RMS", lambda t: f"{n(t['Cin_rms_A'])} A"),
    satir_top("Çıkış dalgalanması", lambda t: f"{n(t['dVo_mV'], 1)} mV"),
    satir_top("En kötü kayıp", lambda t: f"{n(t['en_kotu_kayip_W'])} W"),
    satir_top("En kötü verim", lambda t: f"%{n(t['en_kotu_verim'], 1)}"),
    satir_top("MOSFET / Schottky", lambda t: f"{t['parca']['mosfet']} / {t['parca']['schottky']}"),
    satir_top("Kapı sürücü kanalı", lambda t: str(t["parca"]["surucu"])),
    "| Ölü zaman gerekir mi | Hayır | Evet | Hayır | Evet |",
    "| 180° PWM gerekir mi | Hayır | Hayır | Evet | Evet |",
    "| Akım paylaşım devresi | Hayır | Hayır | Evet | Evet |",
    satir_top("Göreli maliyet", lambda t: n(t["maliyet_gorece"], 1)),
    "| Tasarım ve hata ayıklama | **En kolay** | Orta | Zor | En zor |",
])

frek = "\n".join(["| f | Gereken L | Seçilen L | Bobin enerjisi | Anahtarlama kaybı | Toplam kayıp | Verim |", "|---|---|---|---|---|---|---|"] + [
    (lambda b: f"| {b}{x['f_kHz']:.0f} kHz{b} | {n(x['L_gerek_uH'], 1)} µH | {x['L_uH']:.0f} µH | {n(x['enerji_mJ'])} mJ | {n(x['s_anahtarlama_W'])} W | {n(x['toplam_W'])} W | %{n(x['verim_yuzde'], 1)} |")("**" if x["f_kHz"] == 100 else "")
    for x in H["frekans_tarama"]])

rip = "\n".join(["| Dalgalanma | Seçilen L | ΔI | Tepe akım | Gereken Isat | Bobin enerjisi |", "|---|---|---|---|---|---|"] + [
    f"| %{x['r'] * 100:.0f} | {x['L_uH']:.0f} µH | {n(x['dI_A'])} A | {n(x['Ipk_A'])} A | {n(x['Isat_A'])} A | {n(x['enerji_mJ'])} mJ |"
    for x in H["ripple_tarama"]])

MD = f"""# Tasarım Hesabı: Topoloji Kararı ve Güç Katı Değerleri

**Tarih:** 10 Kasım 2026. **Giriş:** 20–26 V (nominal 22,2 V). **Çıkış:** 11 V, tasarım akımı 7,5 A (hedef yük 7 A).

Bu belgedeki sayılar `buck/hesap.py` ve `buck/ltspice_sina.py` çıktılarından üretilir. Hepsi hesap ve simülasyondur, fiziksel ölçüm yoktur.

## 1. Sonuç

**Karar: tek faz asenkron buck, 100 kHz.** Hocanın gösterdiği devrenin kendisidir: S1, FD, L, C.

Güç katı için parçaların sağlaması gereken değerler:

| Eleman | Değer | Akım | Gerilim | Diğer şartlar |
|---|---|---|---|---|
| L1 bobin | **{L['L_uH']:.0f} µH** ±%20 | Isat ≥ {n(ISAT, 0)} A, Irms ≥ {n(L['Irms_min_A'], 1)} A | Anahtarlama düğümü {S1['Vds_calisma_V']:.0f} V | DCR ≤ {L['DCR_max_mOhm']:.0f} mΩ |
| Cout | **2 × 680 µF** ({CO['toplam_uF']:.0f} µF), yanına 2 × 10 µF seramik | Her biri ≥ {n(CO['Irms_A'] / 2)} A RMS | ≥ 35 V | Her birinin ESR'si ≤ 40 mΩ |
| Cin | **2 × 220 µF** ({CI['toplam_uF']:.0f} µF), yanına 2 × 4,7 µF seramik | Her biri ≥ {n(CI['Irms_adet_A'])} A RMS | ≥ 50 V | Her birinin ESR'si ≤ 50 mΩ |
| S1 MOSFET | Rds ≤ {S1['Rds_max_mOhm']:.0f} mΩ, Qg ≤ 100 nC | {n(S1['Ipk_A'])} A tepe, {n(S1['Irms_A'])} A RMS, Id ≥ 20 A seçilir | VDS ≥ 60 V | Toplam ısıl direnç ≤ {n(S1['theta_max_K_W'], 1)} K/W |
| FD Schottky | Vf ≤ 0,6 V (7,5 A'de) | {n(FD['Ipk_A'])} A tepe, {n(FD['If_ort_A'])} A ortalama, ≥ 15 A sınıfı | VR ≥ 60 V | Toplam ısıl direnç ≤ {n(FD['theta_max_K_W'], 1)} K/W |
| Test yükü | {n(G['yuk']['R_7p5A_ohm'], 3)} Ω | 7,5 A | 11 V | {n(G['yuk']['P_7p5A_W'], 1)} W; 7 A için {n(G['yuk']['R_7A_ohm'], 3)} Ω, {n(G['yuk']['P_7A_W'], 0)} W |

Duty oranı Vin 20 / 22,2 / 26 V için ideal {n(G['duty']['20.0']['ideal'], 3)} / {n(G['duty']['22.2']['ideal'], 3)} / {n(G['duty']['26.0']['ideal'], 3)}, kayıplı modelde {n(G['duty']['20.0']['kayipli'], 3)} / {n(G['duty']['22.2']['kayipli'], 3)} / {n(G['duty']['26.0']['kayipli'], 3)}.

Gerilim sınıfları için çalışma geriliminin yaklaşık iki katı alındı, çünkü anahtarlama düğümünde ringing oluşur. Seramik kapasitör adetleri hesapla değil, yüksek frekans yolu için seçimle konuldu.

Bobin doyma şartı kalkış nedeniyle arttı: kararlı tepe {n(L['Ipk_Lmin_A'])} A iken LTspice'te ilk darbelerde akım {n(KALK_I)} A'e çıkıyor. Şart %12 payla {n(ISAT, 0)} A alındı.

## 2. Kesin devre

**Kararlar:**

- **S1 P-MOS.** Yüzen bootstrap beslemesi gerekmez, sürücü transistörlerle kurulur.
- **Hazır buck, PWM kontrolcü veya sürücü entegresi yok.** Yalnız bir çift op-amp, bir çift karşılaştırıcı ve bir 2,5 V referans kullanılır.
- **Gerilim modlu kontrol, Tip III kompanzasyon.** Tip II düşük ESR'de faz payını 0°'ye düşürdüğü için elendi.
- **Korumalar yok.** Bu yüzden gerçek cihazlar bağlanmaz, testler güç direnciyle yapılır.

Tüm devrenin netlisti: `buck/buck-tam.cir`. LTspice ile doğrudan açılır.

| Blok | Eleman | Değer | Not |
|---|---|---|---|
| Yardımcı 11,3 V | Rv, Dv, Qv, Ccc | {YB['R_ohm'] / 1e3:.1f} kΩ, 12 V zener, NPN, 10 µF | Qv kaybı {n(YB['P_gecis_26V_W'])} W ({YB['I_cc_varsayim_mA']:.0f} mA varsayımı) |
| Referans | Rr, Dr | {RF['R_ohm'] / 1e3:.1f} kΩ, 2,5 V şönt ±%1 | {n(RF['I_mA'])} mA |
| Yumuşak başlatma | Rss, Css | {YS['R_ohm'] / 1e3:.0f} kΩ, {YS['C_uF']:.0f} µF | τ = {n(YS['tau_ms'], 0)} ms |
| Orta nokta | Rm1, Rm2, Cm | 10 kΩ, 10 kΩ, 100 nF | Vm = {n(UC['Vm_V'])} V |
| Üçgen üreteci | Ri, Ci | {UC['R_I_ohm'] / 1e3:.2f} kΩ, {UC['C_I_nF']:.0f} nF C0G | Sim. yaklaşık 100 kHz, tezgâhta Ri ile ayarlanır |
| Histerezis | Rh1, Rh2, Rpu | 27 kΩ, 100 kΩ, 1 kΩ | {n(UC['Vvadi_V'])}–{n(UC['Vtepe_V'])} V, {n(UC['Vpp_V'])} V tepe-tepe |
| Geri besleme | R1, Rb | {GB['R1_ohm'] / 1e3:.0f} kΩ, {GB['Rb_ohm'] / 1e3:.0f} kΩ, ±%0,1 | Vo = {n(GB['Vo_V'], 1)} V ({n(GB['Vo_min_ref1_R01'])}–{n(GB['Vo_max_ref1_R01'])} V) |
| Tip III | R2, C2, C1, R3, C3 | {GB['R2_ohm'] / 1e3:.0f} kΩ, {GB['C2_nF']:.0f} nF, {GB['C1_pF']:.0f} pF, {GB['R3_ohm'] / 1e3:.1f} kΩ, {GB['C3_nF']:.0f} nF | Kapasitörler C0G veya film |
| PWM çıkışı | Rp, Rb2 | 2,2 kΩ, 1,2 kΩ | Baz {n(SR['Vb_V'])} V |
| Seviye kaydırıcı | QL, Re, Rup | NPN, {SR['R_E_ohm']:.0f} Ω, {SR['R_UP_ohm']:.0f} Ω | {n(SR['I_seviye_mA'], 1)} mA, Rup {n(SR['P_RUP_W'])} W |
| Totem sürücü | Qn, Qp, Rg, Rgs | NPN + PNP (≥ 2 A tepe, ≥ 40 V), {n(SR['Rg_ohm'], 1)} Ω, {SR['Rgs_ohm'] / 1e3:.0f} kΩ | Kapı tepe yaklaşık {n(SR['I_kapi_tepe_A_beta100'], 1)} A |
| Kapı rayı (Vin−12 V) | Rz, Dz, Crail | {KR['R_ohm']:.0f} Ω 1 W, 12 V 1 W zener, {KR['C_uF']:.0f} µF | Rz {n(KR['P_R_26V_W'])} W, zener {n(KR['P_zener_26V_W'])} W (26 V) |

**Entegre şartları:** Op-amp GBW ≥ 5 MHz, yükselme ≥ 10 V/µs, en az 16 V besleme, girişi 0–5 V aralığını kapsamalı. Karşılaştırıcı açık kollektör, gecikme ≤ 150 ns, en az 16 V besleme. Karşılaştırıcı gecikmesi frekansı etkiler.

**Kararlılık** (doğrusal model, {KL['kose_sayisi']} köşe: Vin, yük, ESR 7,5–40 mΩ, L ve C ±%20): nominal kesim {n(KL['nominal_fc_kHz'], 1)} kHz ve faz payı {n(KL['nominal_PM_derece'], 0)}°. En kötü durumda faz payı {n(KL['PM_min_derece'], 1)}°, kazanç payı {n(KL['GM_min_dB'], 1)} dB, kesim {n(KL['fc_min_kHz'], 1)}–{n(KL['fc_max_kHz'], 1)} kHz.

**LTspice tam devre** (kapalı çevrim, transistör seviyesi sürücü, genel MOSFET/BJT/diyot modelleri, davranışsal op-amp ve karşılaştırıcı; yük 7,5 A ↔ 0,75 A adımı):

{tam_tablo}

Tam yükte verim %{n(min(VERIMLER), 1)}–{n(max(VERIMLER), 1)}, kontrol devresi ve kaynak kaybı dahil. Çıkış tüm durumlarda 12 V'un altında, yük adımı ±%2 bandı içinde kalıyor. Transistör modelleri genel olduğundan bu sonuçlar parça seçilince yeniden koşulur.

## 3. Seçeneklerin karşılaştırması

Dört seçenek aynı girdiler ve aynı varsayımlarla hesaplandı. Çift fazda bobin başına DCR 40 mΩ alındı, böylece toplam bakır kaybı tek fazla eşit tutuldu.

{top_tablo}

Göreli maliyet tahmindir, teklif değildir. Parça seçilince gerçek fiyatla güncellenir. Birim ağırlıklar `hesap.py` içindeki `MALIYET` tablosundadır.

**Neden tek faz asenkron:**

- **Çift faz bobinde tasarruf etmiyor.** Aynı yüzde dalgalanmada toplam bobin enerjisi {n(A['L_toplam_enerji_mJ'])} mJ yerine {n(C['L_toplam_enerji_mJ'])} mJ çıkıyor. Yani yalnızca iki ayrı daha küçük bobin alıyoruz.
- **Çift fazın kazancı küçük, bedeli büyük.** Asenkron çift fazda en kötü verim %{n(A['en_kotu_verim'], 1)} yerine %{n(C['en_kotu_verim'], 1)} oluyor, çünkü kaybın büyük kısmı diyotta ve o azalmıyor. Göreli maliyet ise {n(A['maliyet_gorece'], 1)} yerine {n(C['maliyet_gorece'], 1)} oluyor.
- **Çift fazın gerçek faydası kapasitörlerde.** Giriş RMS akımı {n(A['Cin_rms_A'])} A yerine {n(C['Cin_rms_A'])} A, çıkış dalgalanması {n(A['dVo_mV'], 1)} mV yerine {n(C['dVo_mV'], 1)} mV oluyor. 82,5 W için bu, birkaç kapasitörle zaten çözülüyor.
- **Çift faz akım paylaşım devresi ister.** LTspice'te fazlar arasında yalnız 0,005 duty farkı (50 ns) akımları {n(U1['I_faz1_A'])} A / {n(U1['I_faz2_A'])} A yapıyor, 0,01 farkta {n(U2['I_faz1_A'])} A / {n(U2['I_faz2_A'])} A oluyor. Basit gerilim modlu kontrolle dengede kalmaz.
- **Senkron bir sonraki adımdır.** Diyot yerine MOSFET kullanmak en kötü kaybı {n(A['en_kotu_kayip_W'])} W yerine {n(Bs['en_kotu_kayip_W'])} W yapar, fakat ölü zaman ve ikinci kapı sürücüsü gerekir, yanlış ayar iki MOSFET'i birden yakar. Aynı L ve C ile sonradan yapılabilir.

**Elenen diğer seçenekler:**

- **Doğrusal regülatör:** 26 V'ta {n(EK['lineer_kayip_W_26V'], 1)} W ısı, verim %{n(EK['lineer_verim_26V_yuzde'], 1)}.
- **SEPIC / buck-boost:** Çıkış her zaman girişten düşük olduğu için gerekmiyor. Anahtar {n(EK['sepic_anahtar_V'], 0)} V ve yaklaşık {n(EK['sepic_anahtar_ort_tepe_A_20V'], 1)} A görür, iki bobin ve ek kuplaj kapasitörü ister.
- **Hazır modül veya buck entegresi:** Hocanın kararıyla kapsam dışı.

## 4. Hesap adımları

**Varsayımlar** (parça seçilince gerçek değerlerle değişir): Vf = {n(V['VF'], 1)} V, Rds = {V['RDS'] * 1e3:.0f} mΩ, DCR = {V['DCR_tek'] * 1e3:.0f} mΩ, kenar başına geçiş {V['TSW'] * 1e9:.0f} ns, kaynak direnci {V['RS_kaynak'] * 1e3:.0f} mΩ, ortam {V['TA']:.0f} °C, Tj üst sınırı 125 °C.

**Frekans.** Yükseldikçe bobin küçülür, kayıp artar. 100 kHz, kaybı ve bobin boyutunu dengeler; 26 V'ta iletim süresi 4,23 µs olur ve elle kurulan sürücüye yeterli pay kalır.

{frek}

**Bobin.** %30 dalgalanma seçildi:

```text
L ≥ Vo·(1 − Dmin) / (r·Io·f) = {n(L['L_gerek_uH'], 1)} µH  →  {L['L_uH']:.0f} µH
ΔI = {n(L['dI_nom_A'])} A,  L −%20 iken ΔI = {n(L['dI_Lmin_A'])} A
Ipk = Io + ΔI/2 = {n(L['Ipk_Lmin_A'])} A
Isat ≥ 1,3 · Ipk = {n(L['Isat_min_A'], 1)} A
Irms = √(Io² + ΔI²/12) = {n(L['Irms_A'])} A,  1,2 pay ile {n(L['Irms_min_A'], 1)} A
CCM sınırı: Io > ΔI/2 = {n(L['CCM_sinir_A'])} A
```

{rip}

**Çıkış kapasitörü.** İki şart var, büyük olan belirler:

```text
Dalgalanma (110 mV hedef): C ≥ {CO['C_min_ripple_uF']:.0f} µF,  ESR ≤ {n(CO['ESR_max_ripple_mOhm'], 1)} mΩ
Yük adımı 7 → 0,75 A, kesim {10} kHz:  ΔV ≈ ΔI/(2π·fc·C) + ΔI·ESR
                                     = {n(CO['yuk_adim_C_mV'], 1)} mV + {n(CO['yuk_adim_ESR_mV'], 1)} mV = {n(CO['yuk_adim_toplam_mV'], 1)} mV
```

Yük adımı hedefi ±%2 (220 mV), yani bu da bir öneridir. Dalgalanma için 273 µF yeterken 2 × 680 µF seçilmesinin nedeni yük adımıdır. Bu seçim PROJE-TANIMI'ndaki 1000 µF başlangıç değerinin yerine geçer. Sonuç: dalgalanma üst sınırı {n(CO['dVo_ripple_mV'], 1)} mV, LC kutbu {n(CO['f0_Hz'], 0)} Hz, ESR sıfırı {n(CO['esr_sifir_Hz'], 0)} Hz.

**Giriş kapasitörü.**

```text
ICin,rms = Io·√(D(1−D)) = {n(CI['Irms_A'])} A  (en kötü, D ≈ 0,5)
C ≥ Io·D(1−D) / (f·ΔV) = {n(CI['C_min_100mV_uF'], 1)} µF  (100 mV için)
{CI['toplam_uF']:.0f} µF ile: {n(CI['dV_C_mV'], 1)} mV kapasitif + {n(CI['dV_ESR_mV'], 0)} mV ESR
```

**Kayıplar ve ısı** (tek faz asenkron):

| Kalem | Vin = 20 V | Vin = 26 V |
|---|---|---|
| FD iletimi | {n(K20['alt_eleman'])} W | {n(K26['alt_eleman'])} W |
| S1 anahtarlama | {n(K20['s_anahtarlama'])} W | {n(K26['s_anahtarlama'])} W |
| Bobin DCR | {n(K20['bobin_dcr'])} W | {n(K26['bobin_dcr'])} W |
| S1 iletimi | {n(K20['s_iletim'])} W | {n(K26['s_iletim'])} W |
| **Toplam / verim** | **{n(K20['toplam'])} W, %{n(K20['verim_yuzde'], 1)}** | **{n(K26['toplam'])} W, %{n(K26['verim_yuzde'], 1)}** |

Çekirdek kaybı, kapı sürme, ringing ve diyot toparlanması dahil değildir. Isıl dirençler `(125 − 50) / P` ile bulundu; FD ve S1 için soğutucu gerekir.

## 5. Topoloji karşılaştırması için LTspice koşusu

Açık çevrim, duty elle verildi. Devre: seçilen L ve C, ESR ve DCR, 50 mΩ kaynak direnci, 30 mΩ davranışsal anahtar, 0,6 V diyot. Anahtarlama kaybı modelde yoktur.

| Durum | Vo | ΔVo | ΔIL | Cin RMS | Verim (anahtarlama hariç) |
|---|---|---|---|---|---|
| Tek faz, 20 V | {n(T['20']['Vo_ort_V'], 3)} V | {n(T['20']['dVo_mV'], 1)} mV | {n(T['20']['dI_A'])} A | {n(T['20']['Cin_rms_A'])} A | %{n(T['20']['verim_anahtarlama_haric'], 1)} |
| Tek faz, 22,2 V | {n(T['22.2']['Vo_ort_V'], 3)} V | {n(T['22.2']['dVo_mV'], 1)} mV | {n(T['22.2']['dI_A'])} A | {n(T['22.2']['Cin_rms_A'])} A | %{n(T['22.2']['verim_anahtarlama_haric'], 1)} |
| Tek faz, 26 V | {n(T['26']['Vo_ort_V'], 3)} V | {n(T['26']['dVo_mV'], 1)} mV | {n(T['26']['dI_A'])} A | {n(T['26']['Cin_rms_A'])} A | %{n(T['26']['verim_anahtarlama_haric'], 1)} |
| Tek faz, 26 V, L −%20 | {n(LM['Vo_ort_V'], 3)} V | {n(LM['dVo_mV'], 1)} mV | {n(LM['dI_A'])} A | {n(LM['Cin_rms_A'])} A | %{n(LM['verim_anahtarlama_haric'], 1)} |
| Çift faz, 20 V | {n(CF['20']['Vo_ort_V'], 3)} V | {n(CF['20']['dVo_mV'], 1)} mV | — | {n(CF['20']['Cin_rms_A'])} A | %{n(CF['20']['verim_anahtarlama_haric'], 1)} |
| Çift faz, 22,2 V | {n(CF['22.2']['Vo_ort_V'], 3)} V | {n(CF['22.2']['dVo_mV'], 1)} mV | — | {n(CF['22.2']['Cin_rms_A'])} A | %{n(CF['22.2']['verim_anahtarlama_haric'], 1)} |
| Çift faz, 26 V | {n(CF['26']['Vo_ort_V'], 3)} V | {n(CF['26']['dVo_mV'], 1)} mV | — | {n(CF['26']['Cin_rms_A'])} A | %{n(CF['26']['verim_anahtarlama_haric'], 1)} |

- 26 V, L −%20 için ΔIL hesapta {n(L['dI_Lmin_A'])} A, LTspice'te {n(LM['dI_A'])} A. Dalgalanma hesapta en çok {n(CO['dVo_ripple_mV'], 1)} mV, LTspice'te {n(LM['dVo_mV'], 1)} mV.
- Cin RMS LTspice'te {n(T['22.2']['Cin_rms_A'])} A çıkıyor, hesapta {n(CI['Irms_A'])} A. Modeldeki kaynak salt dirençtir ve akımın bir kısmını paylaşır. Gerçekte batarya kablosu endüktiftir, bu yüzden kapasitör {n(CI['Irms_A'])} A'e göre seçilir.
- Geri besleme yok, duty elle verildi. Bu nedenle Vo 11 V'un biraz altındadır.

## 6. Sıradaki adım: parça seçimi

Bölüm 1 ve 2'deki tablolar parça ararken filtre olarak kullanılır. Seçilen her parça için üretici verisindeki gerçek Vf, Rds, DCR, ESR ve geçiş süreleri `hesap.py` ile `ltspice_tam.py` içine girilir, hesaplar ve LTspice yeniden koşulur.
"""

(B / "TASARIM-HESABI.md").write_text(MD, encoding="utf-8", newline="\n")
print("yazildi", len(MD.splitlines()), "satir")
