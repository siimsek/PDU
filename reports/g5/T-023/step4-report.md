# T-023 Adım 4 — R-022 Tur 8 sonrası (T-023 Done değil)

**Durum: T-023 InProgress.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **0** (önceki ara kart 14), L2 **1** ada, `/GND` padlerinin L2 eksiği yok. Uyarı: `{'warning:via_dangling': 6}`. Bu kanıt DRC/geometri kanıtıdır; SI, kararlılık, kuplaj, ısı ve fiziksel prob erişimini **kanıtlamaz**.

Bu adımın ham çıktıları: [step4-signal-audit.json](step4-signal-audit.json), [step4-routes.json](step4-routes.json), [step4-gnd-applied.json](step4-gnd-applied.json), [step4-ref-audit.json](step4-ref-audit.json), [drc-step4.json](drc-step4.json), [step4-audit.json](step4-audit.json), [critical-lengths.json](critical-lengths.json), [signal-route-audit.json](signal-route-audit.json). Adım 3 kanıtları `a1c6076`'daki içerikleriyle `step3-*.json`, `drc-step3.json` ve `step3-probe-map.*`, `step3-assembly-map.*` adlarında geri konuldu. `2e6f702` ara raporu [step4-interim-report.md](step4-interim-report.md) olarak saklandı.

Netclass ve DRC kuralları değişmedi. Router artık montaj deliği yasak bölgelerini de işaretliyor.

## Beş karar için ne yapıldı

### 1. U5 `/GATE`
T-022 via'ları **kaydırılmadı** (`/ANODE` bakırı `a1c6076` ile aynı). Çıkış pad kenarından başlıyor: `(21,29; 42,5)` ile via merkezleri arası HESAP 1,027 mm, DRC geçti. U5.5 → Q1.4 yolu 12,169 mm.

### 2. U3/U4 DVDT
U3.16/U4.16 `/VSAFE` saplaması `T023_ESC_U3_16`/`U4_16` bölgesi oldu; U3.17/U4.17 `/O1_11V`/`/S2E_11V` bağı pad köşesine alındı. DVDT 15. pinden 0,6 mm ile çıkıyor (DRC).

### 3. U1.13/U1.14 ve U2.13/U2.14
Önce mevcut izinlerde kısa çıkış arandı; 0,25 mm iz `U1.12` ile 0,6 mm'yi sağlayamadı. Bu yüzden `/VOUT` ve `/ISNS` pin çıkışları iz yerine 0,2 mm genişlikte bölge oldu (`T023_ESC_U1_11/12`, `U2_11/12`) ve sense via'ları taşındı: `/VOUT` U1 (49,0; 80,4) → (49,34; 81,0), U2 (34,5; 2,9) → (34,105; 3,0); `/ISNS1` (50,1; 80,95) → (50,4; 80,25), `/ISNS2` (33,4; 3,6) → (33,1; 3,75). `T022_TAP_ISNS1` ucu kısaltıldı, `T022_TAP_TP_VOUT_3` doğu ve kuzey kenarı genişletildi.

**Dikkat:** kesiti azalan güç/sense bakırı yok denemez: 0,2 mm boyun, sense akımıyla çalıştığı VARSAYIMINA dayanır (AÇIK). Üretici minimum bölge genişliği onayı **doğrulanamadı**.

### 4. CVDDA ve CBOOT/RBOOT
Yerleşim U1/U2 pinlerine alındı (`STEP4_PLACE`). L1/U1 courtyard aralığı (1,11 mm) bir 0603 için yetmediğinden CVDDA1 U1 kuzeyinde, CVCC1 güneyde kaldı.

| Yol | Ağ | Yol mm | Düz mm |
|---|---|---:|---:|
| U1.18 → CVDDA1.1 | `/VDDA1` | 4,516 | 3,843 |
| U2.18 → CVDDA2.1 | `/VDDA2` | 4,56 | 4,442 |
| U1.19 → CVCC1.1 | `/VCC1` | 8,398 | 8,143 |
| U2.19 → CVCC2.1 | `/VCC2` | 11,867 | 9,843 |
| U1.4 → RBOOT1.2 | `/CBOOT1` | 1,564 | 2,225 |
| RBOOT1.1 → CBOOT1.1 | `/CBOOT_R1` | 0,707 | 1,615 |
| CBOOT1.2 → U1.5 | `/SW4_PH1` | 2,087 | 2,386 |
| U2.4 → RBOOT2.2 | `/CBOOT2` | 0,901 | 1,588 |
| RBOOT2.1 → CBOOT2.1 | `/CBOOT_R2` | 0,65 | 1,551 |
| CBOOT2.2 → U2.5 | `/SW4_PH2` | 1,44 | 2,05 |
| U1.14 → RT1.1 | `/RT_PH1` | 8,991 | 6,914 |
| U1.13 → RCFG1.1 | `/CFG_PRI` | 3,958 | 2,921 |
| U2.14 → RT2.1 | `/RT_PH2` | 2,361 | 3,14 |
| U2.13 → RCFG2.1 | `/CFG_SEC` | 3,994 | 3,572 |
| U5.5 → Q1.4 | `/GATE` | 12,169 | 9,286 |
| U5.1 → CVCAP.1 | `/VCAP` | 28,759 | 26,629 |
| U3.15 → CDVDT1.1 | `/DVDT_O1` | 38,05 | 24,008 |
| U4.15 → CDVDT2.1 | `/DVDT_S2E` | 69,651 | 23,427 |
| U4.8 → RILIM2.1 | `/ILIM_S2E` | 6,366 | 6,608 |
| U3.8 → RILIM1.1 | `/ILIM_O1` | 32,104 | 26,82 |

Yol: iz merkez çizgisi ve via üzerinden en kısa grafik; bölgeler dahil değil, akım dağılımı değil.

Ara karta göre ağ toplamı (mm / via):

| Ağ | `2e6f702` | Şimdi |
|---|---:|---:|
| `/VDDA1` | 71,562 / 6 | 69,355 / 8 |
| `/VDDA2` | 62,077 / 0 | 4,56 / 0 |
| `/VCC2` | 12,882 / 2 | 13,006 / 2 |
| `/CBOOT2` | 26,697 / 2 | 0,901 / 0 |
| `/SW4_PH1` | 6,056 / 2 | 2,087 / 0 |
| `/SW4_PH2` | 34,01 / 2 | 1,44 / 0 |
| `/VCAP` | 31,511 / 0 | 29,896 / 2 |
| `/OVP_Q` | 138,166 / 13 | 25,591 / 2 |

`/VDDA1` toplamı RSYNC dalını da içerir (U1.18 → CVDDA1.1 yukarıdaki satırdır). `/VCAP` için yerleşim değişmedi: termal ve gate konumu **doğrulanamadı**, zorunlu taşıma çıkarılmadı. `/DVDT_S2E` ve `/DVDT_O1` uzun kaldı; zayıf sinyal olduğu VARSAYIM, kabulü THINKER'ındır.

### 5. `/OVP_REF` ve prob
`TP_OVP_Q` `R_Q.1` yanına alındı (101,5; 62,6). Mevcut prob GND'lerine uzaklık: TP_GND_FB 41,515 mm, atanmış TP_GND_OVP 54,653 mm; en yakın GND pasif pad C_CMP.2 5,537 mm. TP_OC_SENSE1 değişmedi: TP_GND_POWER 37,565 mm, TP_GND_OC 41,382 mm; en yakın GND pasif pad COUT1.2 5,883 mm. Atama değiştirilmedi, yeni pad kartı **açılmadı**; kısa dönüş için pasif pad kullanılıp kullanılmayacağı THINKER/T-024 kararıdır.

## Güç, Kelvin, HV (`a1c6076` ile)

`--audit2`: Kelvin 8,205 / 8,798 / 7,917 / 10,468 mm (≤15), L2 tek ada. `/ANODE` ve `/ISO_GATE` iz/via kümesi `a1c6076` ile aynı. Değişenler: `/VOUT` 4 eleman çıktı 3 girdi (U1/U2 boyun izi ve via'lar + R_INJ via'sı önceki turdan), `/ISNS1`, `/ISNS2` boyun ve via, `/VIN` U10.5 boyun ucu ve via (TAP_U10_5 bölgesi eklendi), `/VSAFE` U3/U4.16 saplamaları, `/O1_11V` ve `/S2E_11V` birer bağ. Zone değişimi: `T022_TAP_ISNS1`, `T022_TAP_TP_VOUT_3`; eklenen `T023_ESC_*`, `T023_TAP_U10_5`. Boyun denetimi (`pcb_drc.neck_audit`) 0 ihlal. Bu karşılaştırma doldurulmuş bakırı veya akım kapasitesini kanıtlamaz.

HV 0,6 mm: DRC kuralı değişmedi ve 0 ihlal; tek tek pay ölçümü yapılmadı.

## FB/COMP ve referanslar (`a1c6076` → şimdi)

| Ağ | Önce mm / via | Sonra mm / via | Önce SW kenar | Sonra SW kenar |
|---|---:|---:|---:|---:|
| `/FB` | 8,9 / 0 | 9,256 / 0 | 1,197 | 1,148 |
| `/COMP` | 130,581 / 0 | 130,101 / 2 | 1,798 | 1,634 |
| `/FB_INJ` | 108,919 / 2 | 55,405 / 4 | 3,848 | 2,057 |
| `/OVP_REF` | 40,437 / 0 | 52,98 / 0 | 25,558 | 14,835 |
| `/OC_REF` | 117,42 / 2 | 114,967 / 2 | 9,775 | 9,775 |

`/COMP` iki via kazandı (U2 tarafı), SW kenarı azaldı. FB ve COMP halkası batıya 0,5 mm kaydı. SI ve kararlılık **doğrulanamadı**.

## Silk ve haritalar

19 pasif ve 12 TP'nin silk'i gizlendi. Harita SHA'sı `a1c0a4f7afed418c…` [probe-map.md](probe-map.md) ve [assembly-map.md](assembly-map.md) içinde. Fiziksel doğrulama T-024'tedir.

## Doğrulanamayanlar

SI/kararlılık, kuplaj/gürültü, startup, dönüş akımı, ısı, üretici minimum via ve bölge onayı, fiziksel prob/fixture/montaj erişimi. DRC 0 üretime hazır demek değildir.
