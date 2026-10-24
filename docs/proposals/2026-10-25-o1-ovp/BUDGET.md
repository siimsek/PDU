# WP1 rev3 – Koşullu pencere bütçesi (`window_budget.py`)

Komut: `python3 simulation/proposals/2026-10-25-o1-ovp/window_budget.py --json window-budget.json`
Sınıflandırma (rev2, inceleme P0/P1 sonrası): **G** = veri sayfası MIN/MAX garanti · **T** = yalnız tipik (garantiye sayılmaz) · **V** = varsayım · **Ç** = çıkarım (analitik türetme, üretici garantisi değil). Terim tablosu: §8.
Tüm parametreler, kaynak sayfa/tabloyla birlikte `window-budget.json` → `params` içinde.

### 0. Terminoloji (rev3, ChatGPT tur-2 P0-04)
Bu belgedeki marjlar **"garanti marjı" değildir**: **varsayımlar ve çıkarımlar altında hesaplanan koşullu marj**dır. Yalnız **G** terimleri üretici MIN/MAX garantisidir; zincirde aşağıdaki 5 V/Ç halkası vardır ve her biri ilgili tezgâh testi geçilene kadar açıktır (WP1 bu testler olmadan tamamlanmış sayılmaz):

| # | Varsayım / çıkarım zinciri | Sınıf | Bütçedeki değer | Bozulursa | Kapatan tezgâh testi |
|---|---|---|---|---|---|
| 1 | A1: TLV3601 VIO'nun VCM = 4,096 V'ta ek ofseti ≤ 4,10 mV (TI yalnız VCM = VEE+0,3 V'ta garanti verir) | V | 4,096 mV | > 11,97 mV → hedef 50 mV kaybolur; > 29,89 mV → 12 V koşulu kaybolur (§4b) | **B2** |
| 2 | tPD(INP_L) 1,05 µs max'ın 47 nF test yükünden 4-FET kapımıza aktarımı (en kötü oran 0,9685 ≤ 1, `gate_discharge_wc.py`) + 50 ns kapı kuyruk payı | Ç + V | 1,05 µs + 50 ns | oran > 1 veya kuyruk > 50 ns → rampa/kısa-devre tepeleri yükselir | **B5** |
| 3 | RAW bankı dürüst minimum 165 µF (DC-bias × sıcaklık × yaşlanma birleşik garanti yok) | V | 165 µF | < 165 µF → kısa-devre tepesi yükselir | **B11** |
| 4 | Bank+montaj ESL ≤ 2 nH (TDK ESL okunmadı, yerleşim modellenmedi) | V | 0 / 2 nH | çınlama/ek tepe | **B11 / B13** |
| 5 | O1 ≤ RAW (O1 portu RAW'dan yüksek olamaz; e-fuse/yol düşümü pozitif) – O1 tepesinin RAW tepesiyle sınırlandığı çıkarımı | Ç | O1 tepe ≤ RAW tepe | port tepesi RAW'ı aşarsa 12 V koşulu doğrudan ölçülmeli | **B13** |

JSON anahtarları (`min_guaranteed_V`, `closes_guaranteed` vb.) CI uyumluluğu için tarihsel adlarıyla bırakıldı; anlamları **koşullu marj**dır.

## 1. Trip penceresi (G + V: A1)
| Büyüklük | Değer |
|---|---|
| VREF sınırları | 4,086576 – 4,105424 V |
| Trip (RAW) min / nom / max | **11,2929 / 11,3976 / 11,5167 V** |
| Yanlış-tetik **test seviyesi** | 11,22 V (+2 % bant kenarı; uyarım seviyesi, normal bus sınırı DEĞİL) → marj **72,9 mV** |
| Normal bus tavanı (rev2 P1-2) | **11,1605 V** – tüm normal işletme decklerinde ayrı `NORMAL_BUS_MAX` iddiası |
| Ömür (R_life ±0,1 %) dahil | 11,2784 – 11,5315 V; taban marjı 58,4 mV |
| Yalnız tipik terimler (CMRR 80 dB, uzun dönem, termal hist.) eklenince | +2,39 mV (kapanıyor) |

## 2. Eğim rampaları (0,07 / 0,17 / 0,23 V/µs) — RAW tepe
Zincir: TLV3601 tPD 4,5 ns + RC gecikmesi + TPS48000 tPD(INP_L) **1,05 µs max** + kapı kuyruk payı 50 ns (V). tPD(INP_L) 47 nF test yükü → 277/288 nC aktarımı: Ç (`gate_discharge_wc.py`, en kötü oran 0,9685 ≤ 1).

| Eğim | Tepe (koşullu) | 12 V koşullu marjı | Tepe (ömür dahil) | Duyarlılık: + tipik Qg/IPD 139 ns |
|---|---|---|---|---|
| 0,07 V/µs | 11,7389 V | 0,261 V | 11,7537 V | 11,7486 V |
| 0,17 V/µs | 11,8571 V | 0,143 V | 11,8719 V | 11,8807 V |
| 0,23 V/µs | **11,9280 V** | **0,072 V** | 11,9429 V | 11,9599 V |

`closes_guaranteed = True`, `closes_with_life = True`.

## 3. RAW bankı (rev2 değişikliği)
COUT1–8 + **COUT21–COUT28** = **16 × TDK C5750X7S2A226M280KB** (22 µF / 100 V / X7S / 2220, ±20 %), mevcut nitelikli parça ve ayak izi (`hardware/COUT-qualification.md`).

| Terim | Değer | Sınıf |
|---|---|---|
| 11 V'ta parça başı C (TDK DC-bias modeli, 25 °C) | 20,622 µF | T (tipik model, MIN değil) |
| Tolerans | ±20 % | G (parça kodu "M") |
| Sıcaklık (X7S, −55…125 °C) | ±22 % | G (EIA sınıf tanımı, 0 V bias) |
| Yaşlanma | −10 % | V (TDK garantisi yok) |
| **Min. efektif bank (ürün)** | 16 × 11,581 = **185,30 µF** | T×G×V |
| CBIAS 0,5 kart deckleri | 176 µF (16 × 22 µF × 0,5) – rev2'de açık kabul köşesi | Ç |
| **Dürüst min. (inceleme P0-1)** | **165 µF** (185,3'ün ~11 % altı: DC-bias × sıcaklık birleşik garanti yok) | V |
| ESL (bank + montaj) | 0 ve **2 nH** köşesi | V (TDK ESL okunmadı) |
| Maks. efektif bank | 16 × 30,191 = **483,05 µF** | T×G |
| ESR köşesi | 1 mΩ ve **12,5 mΩ değiştirilmedi** (16 parça gerçekte düşürür → kötümser) | V |

Not: min/maks, tipik DC-bias model değeri üzerine çarpımsal duyarlılık sınırlarıdır; TDK birleşik garanti vermez. **Buck kompanzasyonu (RCOMP 9,53k / CCOMP 4,7n / CHF 47p) ~88 µF civarında seçilmiştir; 185–483 µF aralığında döngü kararlılığı WP3'te kanıtlanmalıdır** (bu pakette yalnız davranışsal buck modeliyle başlangıç/yük basamağı koşuldu).

## 4. Buck high-side short dalga formu (26 V, L 2,72 µH + 15,4 mΩ, I0 7,5 A, V0 11,1605 V)
Trip RAW = vtrip_max + 50 mV/k_min = 11,6562 V; zincir 4,5 ns + 1,05 µs + 50 ns = 1,1045 µs (kapı deşarjı ayrıca eklenmez – Ç, `gate_discharge_wc.py`). ESL köşesinde dI/dt = (VS − R·I − Vc − I·ESR)/(L + ESL), RAW = Vc + I·ESR + ESL·dI/dt (bu modelde ESL seri yola eklendiği için tepe hafif DÜŞER; ESL çınlaması/yerleşim modellenmedi → B13).

| Vaka | C | ESR | ESL | t_trip | t_off | RAW @ t_off (koşullu) | 12 V koşullu marjı | Ömür dahil | + tipik Qg/IPD (duyarlılık, garanti değil) |
|---|---|---|---|---|---|---|---|---|---|
| **c185** | 185.30 µF | 1 mΩ | 0 nH | 4.53 µs | 5.63 µs | 11.8788 V | **121,2 mV** | 103,6 mV | 92,6 mV |
| **c185-esr12m5** | 185.30 µF | 12.5 mΩ | 0 nH | 2.83 µs | 3.94 µs | 11.8914 V | **108,6 mV** | 91,4 mV | 78,6 mV |
| **c483** | 483.05 µF | 1 mΩ | 0 nH | 7.81 µs | 8.92 µs | 11.7865 V | **213,5 mV** | 197,0 mV | 197,2 mV |
| **c483-esr12m5** | 483.05 µF | 12.5 mΩ | 0 nH | 3.99 µs | 5.10 µs | 11.8072 V | **192,8 mV** | 176,6 mV | 174,1 mV |
| **c176** | 176.00 µF | 1 mΩ | 0 nH | 4.39 µs | 5.50 µs | 11.8856 V | **114,4 mV** | 96,8 mV | 84,9 mV |
| **c176-esr12m5** | 176.00 µF | 12.5 mΩ | 0 nH | 2.77 µs | 3.88 µs | 11.8975 V | **102,5 mV** | 85,0 mV | 71,6 mV |
| **c165** | 165.00 µF | 1 mΩ | 0 nH | 4.23 µs | 5.33 µs | 11.8943 V | **105,7 mV** | 88,1 mV | 74,9 mV |
| **c165-esr12m5** | 165.00 µF | 12.5 mΩ | 0 nH | 2.70 µs | 3.80 µs | 11.9058 V | **94,2 mV** | 76,7 mV | 62,1 mV |
| **c185-esr12m5-esl2n** | 185.30 µF | 12.5 mΩ | 2 nH | 2.78 µs | 3.88 µs | 11.8891 V | **110,9 mV** | 93,6 mV | 81,1 mV |
| **c165-esr12m5-esl2n** | 165.00 µF | 12.5 mΩ | 2 nH | 2.64 µs | 3.75 µs | 11.9037 V | **96,3 mV** | 79,0 mV | 64,5 mV |
| rev1-c92 (superseded) | 92.65 µF | 1 mΩ | 0 nH | 2.96 µs | 4.07 µs | 11.9911 V | 8,9 mV | -9,5 mV | -35,5 mV |
| rev1-c92-esr12m5 (superseded) | 92.65 µF | 12.5 mΩ | 0 nH | 2.05 µs | 3.16 µs | 11.9988 V | 1,2 mV | -17,2 mV | -44,0 mV |
| c120-esr12m5 (info, below every bound) | 120.00 µF | 12.5 mΩ | 0 nH | 2.33 µs | 3.44 µs | 11.9525 V | 47,5 mV | 29,6 mV | 9,0 mV |
| c130-esr12m5 (info, below every bound) | 130.00 µF | 12.5 mΩ | 0 nH | 2.42 µs | 3.53 µs | 11.9398 V | 60,2 mV | 42,6 mV | 23,4 mV |
| Stres: c185 / 100 mΩ (−40 °C) | 185,30 µF | 100 mΩ | 0 nH | 0,08 µs | 1,18 µs | 12,5695 V (RAW) | −569,5 mV (RAW) | – | – |

Kabul satırları: ilk on satır (rev2: 176 µF, **165 µF dürüst min.** ve 2 nH ESL köşeleri eklendi). rev1/c120/c130 satırları bilgi amaçlıdır. 100 mΩ satırı ayrı stres köşesidir (I·ESR adımı eğim varsayımının dışında; O1 değeri ngspice'ta U3 eFuse üzerinden ölçülür, bkz. RESULTS.md). Hedef 50 mV için gereken min. efektif C (12,5 mΩ): **≈ 122 µF** (c120: 47,5 mV, c130: 60,2 mV).

### 4b. TLV3601 VCM toleransı (inceleme P0-2) – V sınıfı
TLV3601 VIO yalnız VCM = VEE + 0,3 V'ta garantilidir; CMRR yalnız tipik (80 dB). Çalışma VCM = 4,096 V (kayma 3,796 V). Bütçedeki A1 varsayımı: ek ofset ≤ 4,10 mV (pin). `window_budget.py → vcm_tolerance` bisection sonucu:

| Ölçüt | Pin'de izin verilen toplam VCM terimi | CMRR eşdeğeri |
|---|---|---|
| Tüm marjlar ≥ 0 (12 V ve 11,22 V tarafı) | **29,89 mV** (A1'in +25,79 mV üstü) | **42,1 dB** |
| Tüm marjlar ≥ 50 mV hedefi | **11,97 mV** (A1'in +7,87 mV üstü) | **50,0 dB** |
| Tipik (bilgi) | – | 80 dB |

Sonuç: garanti değil, **V**; tolerans sayısal olarak verildi; tezgâh B2 zorunlu. Alternatif (WP2): TLV3201 (VIO tüm VCM aralığında) + REF35250 ile VCM düşürme – mimari değişikliği olduğu için bu pakette uygulanmadı.

## 5. Seçenek karşılaştırması (aynı koşullu zincir, yalnız ilgili kaldıraç değişir)
| Seçenek | Koşullu marj etkisi | Risk | Karar |
|---|---|---|---|
| **A. RAW C artırımı: +8 × C5750X7S2A226M280KB (16 parça)** | Kısa devre en kötü marj 1,2 → **108,6 mV** (12,5 mΩ). Hedef 50 mV için gereken min. efektif C (12,5 mΩ): **≈122 µF** | Aynı nitelikli MPN/ayak izi; yeni aktif devre yok. Riskler: alan (+8 × 7,85×6,20 mm courtyard), maliyet, tedarik (DigiKey stok 0, 24 hf), **buck döngü kararlılığı (WP3)**, başlangıç şarj akımı | **SEÇİLDİ** |
| B. Daha hızlı kapatma (güçlü PD / ayrık hızlı deşarj katı / farklı sürücü) | rev1 bankıyla 50 mV için koşullu zincirin **132 ns (1 mΩ) / 155 ns (12,5 mΩ)** kısalması gerekir. TPS48000 I(PD) 2 A yalnız TİPİK (MIN yok); tPD(INP_L) iç gecikmedir, dış sink bunu kısaltmaz. Ayrık katın (komparatör → seviye kaydırıcı → G-SRC deşarj) MIN/MAX zamanlaması için doğrulanmış MPN/veri sayfası bu çalışmada yok | Yeni aktif yol: seviye kaydırma, VGS negatif/±20 V sınırı, PD–SRC abs-max, PU ile çatışma, yanlış tetik/ESD; garanti verisi yok | Reddedildi (WP2 yedek seçenek) |
| C. Düşük-Qg FET | Koşullu marj kazancı **0 mV**: tPD(INP_L) max zaten 470 nC test yükünde (> 277 nC) belirtilmiş; yalnız tipik duyarlılık satırı iyileşir | RDS(on)/SOA yeniden doğrulama | Reddedildi |
| D. Kombinasyon (A+B) | A tek başına hedefi sağlıyor | B'nin riskleri eklenir | Gerek yok |
| (Kapsam dışı) Bus setpoint düşürme | – | Gereksinim değişikliği | Kullanıcı kararı |

## 6. Marj özeti – tüm kabul köşeleri (hedef ≥ 50 mV koşullu marj)
| Köşe | Koşullu marj (varsayımlar ve çıkarımlar altında) | Ömür (R_life) dahil |
|---|---|---|
| slope 0,07 V/us | 261,1 mV | 246,3 mV |
| slope 0,17 V/us | 142,9 mV | 128,1 mV |
| slope 0,23 V/us | 72,0 mV | 57,2 mV |
| short c185 | 121,2 mV | 103,6 mV |
| short c185-esr12m5 | 108,6 mV | 91,4 mV |
| short c483 | 213,5 mV | 197,0 mV |
| short c483-esr12m5 | 192,8 mV | 176,6 mV |
| short c176 | 114,4 mV | 96,8 mV |
| short c176-esr12m5 | 102,5 mV | 85,0 mV |
| short c165 | 105,7 mV | 88,1 mV |
| short c165-esr12m5 | 94,2 mV | 76,7 mV |
| short c185-esr12m5-esl2n | 110,9 mV | 93,6 mV |
| short c165-esr12m5-esl2n | 96,3 mV | 79,0 mV |
| floor 11,22 V | 72,9 mV | 58,4 mV |
| **Min.** | **72.0 mV → hedef karşılandı** | **57.2 mV → hedef karşılandı** |

`margin_summary.meets_target = true`, `meets_target_with_life = true`. Rampa köşeleri RAW kapasitesinden bağımsızdır. **Duyarlılık uyarısı:** 0,23 V/µs rampasına tipik Qg/IPD süresi eklenirse marj 40,1 mV'a iner (< 50 mV); bu satır koşullu marjın da dışındadır (Ç argümanı), tezgâhta (B5) doğrulanmalıdır. VCM terimi 11,97 mV'u aşarsa hedef, 29,89 mV'u aşarsa 12 V koşulu kaybolur (§4b).

## 7. Sonuç
- rev2 (16 × 22 µF RAW bankı) ile **koşullu bütçe (varsayımlar ve çıkarımlar altında hesaplanan) tüm kabul köşelerinde ≥ 72.0 mV (ömür dahil ≥ 57.2 mV)** marjla kapanır; dürüst min. 165 µF / 12,5 mΩ köşesinde 94,2 mV (ömür 76,7 mV). Kriter gevşetilmedi, setpoint değişmedi.
- Bu koşullu marj, **V** ve **Ç** sınıfı terimlerin (A1 VCM, tPD aktarımı, C yaşlanma, dürüst min. C, ESL, kapı kuyruk payı) doğru olması koşuluna bağlıdır. Bu terimler tezgâhta (B2, B5, B11, B13) doğrulanmadan WP1 tamamlanmış sayılmaz.
- ngspice wchi sonuçları ve marjları: RESULTS.md.

## 8. Terim sınıflandırması (window_budget.py `params`, otomatik)
| Terim | Değer | Sınıf | Kaynak (veri sayfası/sayfa veya gerekçe) |
|---|---|---|---|
| `VREF_nom` | 4.096 V | **G** | REF35409 nominal, SNAS809C p1/p5 |
| `VREF_init` | 0.0005 1 | **G** | REF35 initial accuracy +/-0.05 % max @25C, SNAS809C p5 |
| `VREF_TC` | 1.2e-05 1/K | **G** | REF35 TC 12 ppm/K max (box) -40..105C SOT-23, SNAS809C p5 |
| `VREF_dT` | 145.0 K | **V** | full -40..105C box span applied as deviation from 25C value (conservative) |
| `VREF_line` | 0.00012 1/V | **G** | REF35 line regulation 120 ppm/V max (VREF>=2.5V), SNAS809C p5 |
| `VREF_dVin` | 0.504 V | **Ç** | TPS7A1650 5V +/-2 % (SBVS171F p6) -> 4.9..5.1V vs test VIN=VREF+0.5=4.596V |
| `VREF_load` | 6e-05 1/mA | **G** | REF35 load reg 60 ppm/mA max (sourcing), SNAS809C p5 |
| `VREF_longterm_typ` | 4e-05 1 | **T** | REF35 long-term 40 ppm 1000h TYPICAL, SNAS809C p5 |
| `VREF_thyst_typ` | 7e-05 1 | **T** | REF35 thermal hysteresis 70 ppm TYPICAL, SNAS809C p5 |
| `VIO` | 0.005 V | **G** | TLV3601 VIO +/-5 mV max -40..125C @VCM=VEE+0.3V, SNOSDB1E p7 |
| `VHYST_min` | 0.0015 V | **G** | TLV3601 VHYST min 1.5 mV, SNOSDB1E p7 |
| `VHYST_max` | 0.005 V | **G** | TLV3601 VHYST max 5 mV (ensured by characterization), SNOSDB1E p7 |
| `IB` | 5e-06 V | **G** | TLV3601 IB 5 uA max -40..125C, SNOSDB1E p7 |
| `CMRR_typ_dB` | 80 dB | **T** | TLV3601 CMRR 80 dB TYPICAL only; VIO not guaranteed at VCM=4.096V, SNOSDB1E p7 |
| `VCM_allow` | 0.004096 V | **V** | ASSUMPTION A1 (V, NOT guaranteed): extra offset at VCM=4.096V <= 4.1 mV (= 60 dB CMRR over 4.1 V, 20 dB worse than the 80 dB typical). TLV3601 VIO is guaranteed only at VCM=VEE+0.3V (SNOSDB1E 6.5 conditions). Open guarantee gap G1. |
| `tPD_cmp` | 4.5e-09 s | **G** | TLV3601 tPD 4.5 ns max -40..125C @50 mV overdrive (char.), SNOSDB1E p7 |
| `VOD_spec` | 0.05 V | **G** | overdrive at which tPD is specified, SNOSDB1E p7 |
| `tPD_INP_L` | 1.05e-06 s | **G** | TPS4800 tPD(INP_L) 1.05 us max, INP low -> PD low (1V, Fig. p11), CL=47nF, TJ=-40..150C, test VS=48V, V(BST-SRC)=11V, SLUSEZ1B p7 |
| `VBST_TEST` | 11.0 V | **G** | switching-table test condition V(BST-SRC)=11 V, SLUSEZ1B p7 |
| `IPD_typ` | 2.0 V | **T** | TPS4800 I(PD) 2 A peak TYPICAL only, SLUSEZ1B p7 |
| `VBST_OFF_max` | 13.86 V | **G** | charge pump turn-off 13.86 V max = max VGS, SLUSEZ1B p6 |
| `VBST_ON_min` | 8.24 V | **G** | charge pump turn-on 8.24 V min = min VGS (steady), SLUSEZ1B p6 |
| `t_gate_tail` | 5e-08 s | **V** | allowance from V(PD-SRC)=1V to channel cut-off at hot Vth (<1V possible) |
| `Q_47nF_test` | 4.7e-07 C | **Ç** | tPD(INP_L) test load 47 nF from V(BST-SRC)=11 V to 1 V = 470 nC; INFERENCE (not a TI guarantee) that tPD(INP_L) max covers our 4-FET gate: gate_discharge_wc.py bounds a resistive-sink model at <=0.97x the test-load time incl. Qg max scaling, Qgd x2, plateau at an assumed hot Vth 1.1 V, VBST 13.86 V, RG max (gate-discharge-wc.json) |
| `Qg10_max` | 5.3e-08 C | **G** | CSD18540Q5B Qg(10V) 53 nC max, SLPS488B p3 |
| `Ciss_max` | 4.23e-09 F | **G** | CSD18540Q5B Ciss 4230 pF max, SLPS488B p3 |
| `NFET` | 4 1 | **V** | two parallel back-to-back pairs QA1/QA2 + QB1/QB2, one gate drive (PD tied to all gates) |
| `R_tol` | 0.001 1 | **G** | ERA-8ARB +/-0.1 % (RSNS10A+B series sum: same bound), AOA0000C307 p2 |
| `R_TCR` | 1e-05 1/K | **G** | ERA-8ARB +/-10 ppm/K, AOA0000C307 p2 |
| `R_dT` | 100.0 K | **V** | resistor at -40..125C, worst /T-25C/=100 K (no TCR tracking credited) |
| `R_life` | 0.001 1 | **G** | ERA-xA (ERA-8A used, rev3) endurance/soldering/damp-heat test limit +/-0.1 % each (separate column), AOA0000C307 performance table common to all sizes |
| `RIN` | 1000.0 ohm | **V** | series input resistor tap->IN- (abs-max current limit); IB flows through Rpar+RIN |
| `Cf` | 1e-10 F | **V** | C0G 100 pF filter at comparator IN- (Rpar*Cf lag added) |
| `Cf_tol` | 0.05 1 | **G** | C0G +/-5 % (GRM1885C1H101JA01, to be confirmed) |
| `V_O1_MAX` | 12.0 V | **G** | O1 instantaneous absolute limit, requirement (not loosened) |
| `V_FLOOR` | 11.22 V | **V** | no-false-trip floor: OVP must NOT trip at the 11.22 V false-trip TEST level (+2 % band edge; = 11.1605 V normal-bus max + 59.5 mV). Normal-bus limit itself is 11.1605 V (rev2 P1-2) |
| `V_STATIC_MAX` | 11.1605 V | **G** | check_static_corners baseline static bus max |
| `N_RAW` | 16 1 | **V** | rev2 design choice: 8 existing + 8 added RAW capacitors, same MPN/footprint (hardware/COUT-qualification.md) |
| `C_11V_typ` | 2.062219e-05 F | **T** | TDK vendor DC-bias model @11 V 25C, 20.62219 uF per part (hardware/COUT-qualification.md; typical model, not a MIN) |
| `C_tol` | 0.2 1 | **G** | C5750X7S2A226M280KB capacitance tolerance +/-20 % (M), TDK part number / DigiKey 2026-10-25 |
| `C_temp` | 0.22 1 | **G** | X7S class: +/-22 % over -55..125C (EIA X7S definition, at 0 V bias) |
| `C_aging` | 0.1 1 | **V** | ASSUMED 10 % aging sensitivity (no TDK guarantee; same as hardware/COUT-qualification.md) |
| `ESR_corner` | 0.0125 ohm | **V** | 12.5 mOhm bank ESR corner kept UNCHANGED from rev1 although 16 parts lower it (pessimistic) |
| `MARGIN_TARGET` | 0.05 V | **V** | rev2 design target: >= ~50 mV guaranteed margin to the 12.0 V O1 limit at every acceptance corner (target, not a new criterion) |
| `ESL_bank` | 2e-09 H | **V** | ASSUMED total RAW-bank ESL incl. mounting (16 parallel 2220 parts; TDK ESL not read -> deliberately pessimistic 2 nH); adds L*di/dt to RAW in the esl2n short rows |
| `C_honest_min` | 0.000165 F | **V** | independent-review honest minimum effective C (extra ~11 % below the 185.3 uF product bound for DC-bias x temperature interaction); acceptance row, not a datasheet value |
| `C_cbias05` | 0.000176 F | **Ç** | 16 x 22 uF x CBIAS 0.5 = 176 uF: the C used by the startup/load board decks (baseline CBIAS convention); acceptance row |
