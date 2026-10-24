# WP1 – Garanti pencere bütçesi (`window_budget.py`)

Komut: `python3 simulation/proposals/2026-10-25-o1-ovp/window_budget.py --json window-budget.json`
Sınıflandırma: **G** = veri sayfası MIN/MAX garanti · **T** = yalnız tipik (garantiye sayılmaz) · **A** = varsayım · **I** = çıkarım.
Tüm parametreler, kaynak sayfa/tabloyla birlikte `window-budget.json` → `params` içinde.

## 1. Trip penceresi (G + A1)
| Büyüklük | Değer |
|---|---|
| VREF sınırları | 4,086576 – 4,105424 V |
| Trip (RAW) min / nom / max | **11,2929 / 11,3976 / 11,5167 V** |
| Yanlış-tetik tabanı | 11,22 V (11,1605 V statik max + 59,5 mV pay) → marj **72,9 mV** |
| Ömür (R_life ±0,1 %) dahil | 11,2784 – 11,5315 V; taban marjı 58,4 mV |
| Yalnız tipik terimler (CMRR 80 dB, uzun dönem, termal hist.) eklenince | +2,39 mV (kapanıyor) |

## 2. Eğim rampaları (0,07 / 0,17 / 0,23 V/µs) — RAW tepe
Zincir: TLV3601 tPD 4,5 ns + RC gecikmesi + TPS48000 tPD(INP_L) **1,05 µs max** + kapı kuyruk payı 50 ns (A).

| Eğim | Tepe (garanti) | 12 V marjı | Tepe (ömür dahil) | Duyarlılık: + tipik Qg/IPD 139 ns |
|---|---|---|---|---|
| 0,07 V/µs | 11,7389 V | 0,261 V | 11,7537 V | 11,7486 V |
| 0,17 V/µs | 11,8571 V | 0,143 V | 11,8719 V | 11,8807 V |
| 0,23 V/µs | **11,9280 V** | **0,072 V** | 11,9429 V | 11,9599 V |

`closes_guaranteed = True`, `closes_with_life = True`.

## 3. Buck high-side short dalga formu (26 V, L 2,72 µH + 15,4 mΩ, I0 7,5 A, V0 11,1605 V)
Trip RAW = vtrip_max + 50 mV/k_min = 11,656 V; zincir 1,1045 µs.

| RAW bankı | ESR | t_trip | t_off | RAW @ t_off | 12 V marjı | Durum |
|---|---|---|---|---|---|---|
| 92,65 µF | 1 mΩ | 2,96 µs | 4,07 µs | 11,9911 V | **9 mV** | PASS (SINIRDA) |
| 165 µF | 1 mΩ | 4,23 µs | 5,33 µs | 11,8943 V | 106 mV | PASS |
| 92,65 µF | 12,5 mΩ | 2,05 µs | 3,16 µs | 11,9988 V | **1,2 mV** | PASS (SINIRDA) |
| 92,65 µF | 100 mΩ (−40 °C stres) | 0,08 µs | 1,18 µs | 12,635 V | −0,635 V | **FAIL – ayrı stres köşesi** (I·ESR adımı eğim varsayımının dışında) |

Duyarlılık (tipik Qg/IPD süresi eklenince): c92/1 mΩ 12,036 V, c92/12,5 mΩ 12,044 V → FAIL; c165 11,925 V PASS. **Argüman:** tPD(INP_L) 47 nF/11 V→1 V test yükü = 470 nC ile belirtilmiştir; bizim kapı yükümüz ≤ 277 nC olduğundan tipik kapı süresini ayrıca eklemek çift sayımdır. Bu bir **çıkarımdır (I), TI garantisi değildir.**

Diğer duyarlılıklar: Cf 47 pF/22 pF yalnız ~13–19 mV kazandırır; RAW C 92,65→130 µF yalnız ~60 mV kazandırır.

## 4. Sonuç
- Eğim rampalarında bütçe garanti (G+A1) ile kapanır (en kötü 72 mV).
- Kısa-devre dalga formunda analitik bütçe **1,2–9 mV** ile kapanır. ngspice son koşusu (`wp1-final-1`, 2026-10-25 01:24 TSİ) wchi köşesinde: c92/1 mΩ **11,996 V PASS (4 mV)**, c92/12,5 mΩ **12,0368 V FAIL** (wchi komparatör modeli +50 mV overdrive gecikme varsayımını da içerir → analitik bütçeden daha kötümser). typ köşesi her iki ESR'de PASS.
- **Sonuç: aday mimari bu haliyle O1 ≤ 12,0 V kriterini tüm kabul köşelerinde karşılamıyor → BLOKLAYICI.** Kriter gevşetilmedi.
- Azaltma seçenekleri (kullanıcı kararı, WP2): bus setpoint'ini düşürmek (en etkili), daha hızlı/ güçlü kapı sürücü, RAW kapasitesini 165 µF'a çıkarmak (+97 mV).
- A1/G1: TLV3601 VIO, VCM=4,1 V'ta garanti değil; ±4,1 mV ek pay varsayımı TI teyidi veya tezgâh karakterizasyonu ister.
