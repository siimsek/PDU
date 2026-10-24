# WP1 rev2 – Mimari karşılaştırma ve seçilen aday

## 1. Sorun
Baseline'da (`simulation/pdu-efuse-ovp.ng.cir`) bus 11→18 V'a çıktığında O1 portu **~16,89 V** görür (U3 TPS259824'ün sabit OVP'si O1'in 12 V sınırının çok üstünde). Kriter `o1_peak ≤ 12 V` bilerek FAIL eden regresyon olarak tutulur.

## 2. Seçenekler (≥3)

| Seçenek | Açıklama | 12 V marjı | Latch / retry | Toparlanma | O1 / S2E etkisi | Cload / inrush | Sonuç |
|---|---|---|---|---|---|---|---|
| **A. Hibrit global OVP (seçilen)** | Buck çıkışı RAW ile bus VOUT arasına sırt sırta 2×2 CSD18540Q5B + TPS48000-Q1 sürücü; RAW'ı hassas komparatör (TLV3601 + REF35409 + 0,1 % bölücü) izler, TPS48000 OV pini yedek (backstop) | Eğim rampalarında garanti bütçe 72–261 mV; kısa devrede **rev2 (16 × 22 µF RAW, ≥ 185,3 µF) 108,6–213,5 mV** (rev1 92,65 µF: 1,2–9 mV); sim wchi en kötü c165/12,5 mΩ **11,9026 V (97 mV) PASS**; 2 ESL-typ deck yakınsamadı (açık) | Otomatik retry (TLV3601 VHYST 1,5–5 mV pinde ≈ 4–14 mV RAW tarafında); TPS48000 latch kullanılmıyor | RAW normale dönünce FET'ler tekrar açılır (sim: reset 10,98–11,02 V) | Her iki port (O1 ve S2E) korunur; U3/U4 IN ≤ 30 V abs max kalır (bus rev2'de yalnız 100 mΩ stres köşesinde 13,04 V'a (wchi) ve MC rampada 12,18 V'a çıkar; 100 mΩ stres ve MC rampada O1 portu U3 OVP sayesinde ≤ 12 V) | COUT'lar RAW tarafına taşınır; VOUT tarafında yalnızca eFuse girişleri; FET'ler INP ile yavaş açılır (CBST 0,47 µF, TDRV_EN ≤ 50,8 ms) | **Seçildi (rev2: RAW bankı 16 × C5750X7S2A226M280KB; tüm kabul köşeleri ≥ 50 mV garanti marjı)** |
| B. Yalnız O1-yerel OVP | U3 sonrası O1 hattına ayrı OVP (ör. TPS2663/TPS1663 sınıfı, ayarlanabilir OVP) | O1 için benzer pencere; S2E korunmaz (S2E zaten ayrı) | Cihaza göre latch/retry | Yerel | S2E değişmez; bus 18 V'a çıkabilir → U4 ve S2E stres altında kalır | O1 hattına ek RDS(on) ve inrush | Bus'ı korumadığı için ikincil |
| C. Crowbar + sigorta | Bus'ta SCR/MOSFET crowbar, öncesinde sigorta | Hızlı (µs altı) ama sigorta atar | **Latch (kalıcı)**; sigorta değişimi | Manuel servis | Tüm yükler düşer | Crowbar akımı buck'ı ve RAW C'yi zorlar | Uçuşta kabul edilemez kesinti; yedek olarak düşünülebilir |
| D. Bus setpoint'ini düşürme (kullanıcı kararı; rev2 kapsamı dışı) | 11,0 V → ör. 10,8 V; trip penceresi aşağı kaydırılabilir | Her 0,1 V düşüş ≈ 0,1 V ek marj | — | — | O1 alt sınırı 5 V, sorun değil; S2E ve diğer yükler için alt sınırlar doğrulanmalı | Etkisiz | Kapsam dışı (gereksinim değişikliği); rev2 ile gerekmiyor |
| E. A + daha hızlı kapatma (güçlü PD / ayrık deşarj katı) | rev1 bankıyla 50 mV için 132–155 ns daha kısa garanti zinciri gerekir; I(PD) yalnız tipik, ayrık kat için MIN/MAX zamanlama verisi yok | — | — | — | Yeni aktif yol (seviye kaydırma, VGS/abs-max riskleri) | — | Reddedildi (BUDGET.md §5); RAW C artışı tek başına yeterli |
| (Reddedildi) VOUT'u algılama | Komparatör bus'ı izlesin | — | — | — | — | FET'ler açıkken buck geri beslemesi VOUT'tan alınırsa kapalıyken buck VIN'e kadar çıkar (wind-up) | Reddedildi; geri besleme RAW'a taşındı (RFB1, RS1/RS2, XU1/XU2) |

## 3. Seçilen parçalar (gerçek MPN, veri sayfası referansı)

| Ref | MPN | Üretici | Rol | Kullanılan garanti (MIN/MAX) değerler | Yalnız tipik (bütçeye garanti diye girmez) | Veri sayfası |
|---|---|---|---|---|---|---|
| U10 | TPS48000QDGXRQ1 | TI | Sırt sırta N-FET sürücü, INP girişi | tPD(INP_L) **1,05 µs max** (V(PD−SRC)=1 V, CL=47 nF); tPU(INP_H) 1,68 µs max; tPD(OV_OFF) 5,55 µs max; INP_H ≤ 2 V, INP_L ≥ 0,8 V; BST UVLO r 7,19/9/10,81 V, f 6,54/8,2/9,64 V; CP off 9,34/11,6/13,86 V; I(BST) 100/345/555 µA; OV r 1,17/1,23/1,28 V, f 1,08/1,14/1,19 V; PU/PD/BST–SRC abs max 19 V | IPU 1,69 A, IPD 2 A, tPD 0,36 µs | SLUSEZ1B, Ara 2023, rev. Mart 2026, s.7 (elektriksel tablo), s.11 Şekil 6-1; Denklem (4) CBST; https://www.ti.com/lit/ds/symlink/tps4800-q1.pdf |
| Q10–Q13 | CSD18540Q5B (×4, 2 paralel sırt sırta çift) | TI | Güç anahtarları | 60 V; RDS(on) 3,3 mΩ max @4,5 V, 2,2 mΩ max @10 V; Qg 53 nC max @10 V | CDS/CGS (model) | SLPS488B, Haz 2014, rev. Nis 2017, s.3; https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf |
| U13 | TLV3601DCKR | TI | RAW komparatörü | VIO ±5 mV (**yalnız VCM=VEE+0,3 V**); VHYST 1,5–5 mV; IB ±5 µA (bütçede); tPD 4,5 ns max @50 mV OD; VCC 2,4–5,5 V; giriş abs max VCC+0,3 V / 10 mA | CMRR 80 dB | SNOSDB1E, Haz 2021, rev. Nis 2023, s.7; https://www.ti.com/lit/ds/symlink/tlv3601.pdf |
| U12 | REF35409QDBVR | TI | 4,096 V referans | ±0,05 % başlangıç; 12 ppm/K; hat 120 ppm/V; yük 60 ppm/mA | Uzun dönem kayma, termal histerezis | SNAS809C, Ara 2021, rev. Eyl 2024, s.5; https://www.ti.com/lit/ds/symlink/ref35.pdf |
| U11 | TPS7A1650DGNR | TI | 5 V yardımcı LDO (VIN'den) | 60 V giriş; 100 mA çıkış (DigiKey ürün özniteliği; veri sayfası sayfası bu pakette ayrıca işaretlenmedi) | — | SBVS171F, Ara 2011, rev. Eki 2015; https://www.ti.com/lit/ds/symlink/tps7a16.pdf |
| RSNS10 / RSNS11 | ERA-3ARB2051V (2,05 kΩ) / ERA-3ARB1151V (1,15 kΩ) | Panasonic | RAW bölücü | ±0,1 %, ±10 ppm/K | — | Panasonic ERA-xA veri sayfası AOA0000C307 s.2 (bütçe kaynağı; bu kutuda PDF kopyası yok → rev./tarih **doğrulanamadı**); DigiKey ERA-3ARB1151V özniteliği 0,1 % / ±10 ppm/K ile tutarlı |
| COUT1–8 (mevcut) + **COUT21–28 (rev2 yeni)** | C5750X7S2A226M280KB (×16) | TDK | RAW bankı | ±20 % (M), 100 V, X7S ±22 % (0 V bias) | 11 V/25 °C efektif 20,622 µF (TDK modeli, tipik); yaşlanma −10 % varsayım | TDK ürün sayfası https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB ; nitelendirme `hardware/COUT-qualification.md` |
| U3/U4 (mevcut) | TPS259824ONRGET | TI | eFuse (değişmedi) | IN abs max 30 V, EN/UVLO abs max 7 V | — | SLVSEI3D, Eki 2018, rev. Mayıs 2026, §6.1 s.7 |

Alternatif komparatörler (listelendi, simüle edilmedi): TLV3201 (tlv3201.pdf), TLV7011 (tlv7011.pdf).
Veri sayfası PDF sha256 (yerel kopya, pakete eklenmedi): tps4800-q1 `f4566ecc…a839`, csd18540q5b `2e43c4a2…54e0`, tlv3601 `4cc42486…2ca2d`, ref35 `a3ba3224…31dd4`, tps7a16 `4e05cfde…f80`, tps25982 `655c21db…bc1f`.

## 4. Seçilen değerler
- Bölücü Rt/Rb = 2050/1150 Ω (k = 0,359375), CSNS 100 pF, RIN 1 kΩ → trip penceresi **11,2929–11,5167 V** (nom 11,3976 V), alt sınır marjı 72,9 mV (ömür dahil 58,4 mV) **11,22 V yanlış-tetik test seviyesine** karşı. 11,22 V bir normal-bus sınırı değildir; normal bus sınırı **≤ 11,1605 V** (R2b; sim en kötü 11,0314 V).
- EN 100k/10k (VIN'den); OV yedek 90,9k/10k (RAW, 1 %) → 11,58–13,17 V, yalnız yedek (tPD 5,55 µs).
- CBST 0,47 µF: dip 0,59 V; TDRV_EN tipik 12,3 ms, en kötü 50,8 ms (IBST 100 µA).
- rev2 P1-1/P1-4: U11 COUT11 **10 µF X7R 1206** (GRM31CR71E106KA12L; SBVS171F ≥ 2,2 µF **efektif** şartı DC-bias altında 2,2 µF 0805 ile sağlanamazdı), U12 CREF12 **1 µF** (GRM188R71C105KA12D), U13 VCC bypass **CBYP13 100 nF** (GRM188R71H104KA93D; SPICE'ta yok). SPICE ile BOM değerleri eşit (COUT11 10u, CREF12 1u).
- U11 çıkışında 499 Ω bleed: giriş-clamp enjeksiyon akımını (RAW 45 V'ta 6,2 mA) emer; min bleed akımı 9,8 mA.
- NPAR = 2: her yönde 2 paralel FET (toplam 4), Qg toplamı 277 nC (13,86 V VGS'te FET başına 69,3 nC).
- **rev2 RAW bankı:** 16 × 22 µF (COUT1–8 + COUT21–28), efektif min 185,30 µF / maks 483,05 µF (BUDGET.md §3). Kısa-devre garanti marjı: 185,3 µF'ta ≥ 108,6 mV; **rev2 P0-1 dürüst minimum 165 µF / 12,5 mΩ'da 94,2 mV** (ömür dahil 76,7 mV); tüm kabul köşelerinde min 72,0 mV (ömür dahil 57,2 mV; belirleyici 0,23 V/µs rampa). Garanti marjları V/Ç sınıfı terimlere (BUDGET.md §8) koşulludur. **WP3:** buck kompanzasyonu ~88 µF için seçilmişti, 185–483 µF ile kararlılık yeniden kanıtlanmalı.
