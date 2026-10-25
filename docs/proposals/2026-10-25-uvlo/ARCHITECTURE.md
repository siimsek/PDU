# WP2 2026-10-25-uvlo – Mimari (seçilen: C3)

## 1. Sorun (baseline)
LM70880 EN/UVLO ucu doğrudan VIN'den RUV1 180 k / RUV2 10,0 k bölücüyle sürülüyor (`simulation/pdu-circuit.inc`).
- Yükselen eşik VEN 0,95–1,05 V (G, SNVSBX7A s.6), yani VIN_r = 17,05–21,12 V (1 %, 100 ppm/K, V). 21,12 V > 20 V olduğu için 20 V'ta açılış **garanti değil**.
- Histerezis yalnızca 0,1 V tipik (T). Düşen eşik garanti edilmez, tipik değeri yaklaşık 17,1 V'tur. 18,0 V aşırı deşarj sınırının altında kalır.
- 7,5 A'de I·R ≈ 1,3 V düşüm, 0,1 V'luk tipik histerezisi aşar. Sonuç: kapanma/açılma salınımı (motorboating) riski.
Regresyon: `reg-baseline-180k10k-*` deck'leri ve bütçedeki `A0` bu davranışı **FAIL** olarak yeniden üretir.

## 2. Seçilen çözüm C3 – TLV3202 (A: VIN UVLO, B: yeniden başlatma zamanlayıcısı) + TMUX1102 anahtarlı bölücü histerezisi
```
VIN ─RTU 39,2k─┬─ S_UV ──► U20A IN+ (3)          VREF_OVP(U12 4,096 V) ─RR1U 10,0k─┬─ REFD_UV ──► U20A IN− (2)
               ├─RBU 8,87k── GND                                                    └─RR2U 46,4k── GND   (CRU 10n)
               ├─CFU 100n── GND
               └─RXU 90,9k── SWD_UV ── U21 TMUX1102 D(1) / S(2)=GND, SEL(4)=OUTA_UV  (SEL düşük = anahtar AÇIK)
U20A OUT(1) = OUTA_UV ─RTT 11,0k─┬─ T_UV ──► U20B IN+ (5)        V5_OVP ─RK1 10,0k─┬─ KTH_UV ──► U20B IN− (6)
                                  ├─CTT 10µ── GND                                    └─RK2 40,2k── GND (CK 10n)
                                  ├─DTT 1N4148WS (A=T_UV, K=DTK_UV) ─RDIS 100── OUTA_UV   (hızlı boşaltma)
                                  └─RHB 1M── OUTB_UV                                   (zamanlayıcı histerezisi)
U20B OUT(7) = OUTB_UV ─RDEN 10k─┬─ EN_BUCK ──► U1/U2 LM70880 EN/UVLO
                                └─RUV2 10,0k── GND   (RUV1 180k: DNP)
U20 VCC(8) = U21 VDD(5) = V5_OVP (U11 TPS7A1650, WP1)
```
**Çalışma:**
- VIN düşükken OUTA düşüktür, U21 açıktır ve RXU, RBU'ya paraleldir. S_UV küçük kalır, bu da yükselen eşiği yüksek tutar:
  V_r = REFD·(1 + RTU/(RBU‖RXU)). Tipik değerler: REFD = 4,096·46,4/56,4 = 3,3698 V, V_r = 19,72 V.
- OUTA yükselince U21 açılır ve eşik V_f = REFD·(1 + RTU/RBU) = 18,26 V (tipik) değerine iner.
- Histerezis yalnızca direnç oranlarına, REF35'e, VIO'ya, Hint'e ve RON'a bağlıdır. **VOH/VOL'a ve V5'e bağlı değildir.** C2'yi bozan şey bu bağımlılıktı (bkz. §3).
- OUTA yüksekken CTT, RTT üzerinden dolar. T_UV > KTH = 0,8008·V5 olunca OUTB yükselir (RHB ile mandallanır) ve EN_BUCK = OUTB/2 ≥ 2,351 V olur.
- OUTA düştüğünde CTT, DTT + RDIS üzerinden hızla boşalır, OUTB düşer ve EN ≤ 0,118 V olur.
- Gecikme oranla belirlenir (V5'ten bağımsız): t ≈ RTT·CTT·ln(1/(1−0,8)). Soğuk açılışta 77,8–255,0 ms, tam boşalmış dip sonrasında 65,0–219,5 ms.
- **Besleme yokken** (V5 < 2,7 V) çıkışlar düşük kabul edildi (V; TLV3202 bu bölgede tanımsız). RUV2, EN'i GND'ye çeker. Tezgâh testi B-U4.

Sıralama: U10 TPS48000, EN/UVLO'yu VIN'den alır (REN10/REN11, WP1). FET, TDRV_EN (≤ 50,8 ms, WP1 bütçesi) sonra açılır. Buck EN ise ≥ 77,8 ms sonra gelir. Böylece P0-03'te açılış çınlaması FET açıkken buck soft-start'ıyla oluşur ve WP1'in test ettiği yol korunur.

## 3. Karşılaştırma (sayısal, `results/uvlo-budget.json` → `alternatives`)
| Seçenek | Açıklama | En kötü sonuç | Karar |
|---|---|---|---|
| A0 baseline | 180 k / 10 k, LM70880 EN | V_r,max 21,12 V > 20 V; V_f garanti yok (tipik ~17,1 V) | FAIL |
| A1 | Yalnızca bölücüyü ayarlamak (RUV1 169,6 k) | V_r,max 19,96 V ama V_f tipik 16,16 V < 18 V ve garanti yok | FAIL |
| B | TPS3700 (SBVS187G) + ERA bölücü | Histerezis tipik 0,27 V (min yok). Gereken I·R + 0,1 = 1,41 V → motorboating | FAIL |
| D | LM74800/LM74810 EN/UVLO (LM74700 yerine) | V_f,min 16,94 V < 18 V | FAIL |
| C2 | TLV3202 A + Rh geri besleme (itme-çekme) | En iyi E96 kombinasyonunda en kötü marj −0,102 V (VOH/VOL ve V5 yayılımı) | FAIL |
| **C3** | TLV3202 A + TMUX1102 anahtarlı bölücü | Marjlar: a +0,0185 / b +0,0234 / c +0,0295 / d +0,1561 / e +0,071 V | **SEÇİLDİ** |

Müdahale ölçüsü: buck, kompanzasyon, WP1 OVP ve RAW bankı değişmez. RUV1 sökülür (DNP), RUV2 kalır. Yeni parçalar 2 IC, 8 hassas direnç, 3 jenerik direnç, 1 diyot ve 6 kondansatördür. Mevcut V5_OVP ve VREF_OVP kullanılır, yeni bir regülatör ya da referans eklenmez.

## 4. Bilinen sınırlamalar
- Marj a (+18,5 mV) dar. Sebebi ERA-3ARB'nin katı doğrusal toplamı (%0,4/parça) ve REF35'in %0,296 hatası. RSS bilgi amaçlıdır: a +0,121 V. Gevşek bir dirence geçmek bütçeyi bozar (`SOURCING.md` not 1).
- 18,0 V eşiği V (hücre üretici verisi yok).
- R_total 0,25 Ω üstü (0,30–0,45 Ω) INFO olarak raporlanır, garanti dışıdır.
- Kısa dip (< ~1 ms) sonrasında zamanlayıcı kısmen boşalır, yeniden başlatma gecikmesi 60 ms'nin altına düşebilir (RESULTS.md).
