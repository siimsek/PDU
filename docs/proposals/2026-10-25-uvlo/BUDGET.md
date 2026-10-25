# WP2 2026-10-25-uvlo – Hata ve marj bütçesi

Kaynak: `simulation/proposals/2026-10-25-uvlo/uvlo_budget.py`. Komut: `python3 uvlo_budget.py > results/uvlo-budget.out`, rc 0. Makine çıktısı `results/uvlo-budget.json`.
Yöntem: her hata terimi ±1 köşelerine **katı doğrusal** toplamla girer (Tur 3 T3-07: bağımsız işaret eksenleri, C3 için 2^12 = 4096 köşe, O3 için 2^14 = 16384, zamanlayıcı ve reset için 2^10 = 1024; VIO/CMRR ve REF yük akımı her köşede o köşenin RR1/RR2 değeriyle hesaplanır; `uvlo-budget.json` → `n_vertices`). RSS yalnızca bilgi amaçlı raporlanır. Sınıflar: **G** garanti (datasheet min/max), **T** tipik, **V** varsayım, **Ç** çıkarım.

## 1. Gereksinim girdileri
| Sembol | Değer | Sınıf | Not |
|---|---|---|---|
| E_START | 20,0 V (EMF) | V | "20 V girişte" ifadesinin en katı okuması: açık devre EMF |
| V_FALL_MIN | 18,0 V | V | 3,00 V/hücre (6S), hücre üretici verisi yok |
| P_OUT | 82,5 W | G (brief) | 7,5 A × 11 V |
| ETA | 0,88 | V | LM70880'de garanti verim yok (yalnızca tipik eğri) |
| P_HK | 0,30 W | V | LDO bleed, denetleyiciler |
| P_IN | 94,05 W | Ç | P_OUT/ETA + P_HK |
| R_TOTAL_MAX | 0,25 Ω | V | Döküm toplamı 0,237 Ω: pil omik 0,100, polarizasyon 0,050, kablo 0,020, konnektör 0,002, J1 0,020, F1 0,010, Q1 sıcak 0,030, PCB 0,005 |
| I_Q_PRESTART | 15 mA | V | buck çalışmadan önceki giriş akımı |
| MARGIN_DYN | 0,10 V | V | dalgalanma, yük adımı ve inrush için dinamik pay |
| T_SEQ_MIN | 60 ms | Ç | TPS48000 TDRV_EN en kötü 50,8 ms (WP1 bütçesi) + ~%18 |
| T_SEQ_MAX | 300 ms | V | kullanıcı açısından kabul edilebilir gecikme (güvenlik sınırı değil) |

## 2. Bileşen hata terimleri
| Terim | Değer | Sınıf | Kaynak |
|---|---|---|---|
| REF35409 ilk doğruluk | ±%0,05 | G | SNAS809C s.5 |
| REF35 TC 12 ppm/K × 145 K | ±%0,174 | G | SNAS809C s.5 (kutu yöntemi) |
| REF35 105→125 °C ekstrapolasyon | ±%0,024 | Ç | spesifikasyon aralığı dışında |
| REF35 uzun dönem (10 kh) | ±%0,04 | V | 40 ppm/1000 h × 10 |
| REF35 termal histerezis | ±70 ppm | T (sınır olarak kullanıldı) | SNAS809C s.5 |
| REF35 hat regülasyonu | ±12 ppm | G | 120 ppm/V × 0,1 V |
| REF35 yük regülasyonu | 20 ppm/mA | T (sınır) | SNAS809C s.1 |
| REF35 lehim kayması | 0 | V | belirtilmemiş → B-U7 |
| **E_REF toplam** | **±%0,296** | | |
| ERA-3ARB tolerans | ±%0,1 | G | Panasonic AOA0000C307 |
| ERA-3ARB TCR 10 ppm/K × 100 K | ±%0,1 | G | aynı |
| ERA-3ARB dayanıklılık 85 °C 1000 h | ±%0,1 | G (test sınırı) | aynı |
| ERA-3ARB lehim ısısı | ±%0,1 | G (test sınırı) | aynı |
| **E_RES toplam** | **±%0,4** | | |
| Jenerik %1 kalın film (RHB, RDEN, RUV2) | ±%3 (1 % + 100 ppm/K × 100 K + %1 ömür) | V | Yageo RC_L V.14 s.5/s.8 ile uyumlu |
| TLV3202 VIO | **≤ 6 mV** (−40…125 °C; 25 °C'de ≤ 5 mV) | G | SBOS561C Rev C (Mayıs 2024) s.5 tablo 6.5, TLV3202 satırı. **Düzeltme (Tur 1 P0):** önceki 4 mV TLV3201 satırıydı |
| TLV3202 CMRR / PSRR | ≥ 60 / 65 dB | G | SBOS561C s.5. CMRR terimi gerçek REFD = 3,3698 V'ta hesaplanır |
| VIO_C3 toplam | 6,926 mV | Ç | VIO 6 mV + CMRR terimi (REFD 3,3698 V) + PSRR terimi |
| TLV3202 Hint | 0–5 mV (1,2 mV tipik) | T/V | SBOS561C s.5: yalnız tipik; **maksimum belirtilmemiş → üst sınır varsayım (sınırsız terim)** |
| TLV3202 IIB | ±5 nA | G | SBOS561C s.5 |
| TLV3202 VCC−VOH / VOL | ≤ 170 / ≤ 225 mV @4 mA | G | SBOS561C s.5 |
| TMUX1102 RON | ≤ 4,9 Ω | G | SCDS410D s.5 |
| TMUX1102 kaçak | ±2 nA | G | SCDS410D s.5 |
| TMUX1102 VIH / VIL | 1,49 / 0,87 V | G | SCDS410D s.5 |
| TPS7A1650 V5 | 4,90–5,10 V | G | SBVS171F s.6 |
| LM70880 VEN-TH | 0,95–1,05 V | G | SNVSBX7A s.6 |
| LM70880 EN düşük mantık | < 0,4 V | T/açıklama | SNVSBX7A s.13 §7.3.3 |
| LM70880 IEN | ±1 µA | V | belirtilmemiş |
| 1N4148WS IRM | ≤ 30 µA (25 V, 150 °C) | G/Ç | Diodes DS30097 Rev.27, ≤ 5,1 V / 125 °C için üst sınır |
| 1N4148WS artık VF | ≤ 0,85 V | Ç/V | VFM 0,715 V @1 mA + −40 °C payı |
| CTT 10 µF X7R | +%26,5 / −%49 | G + V | ±%10 (G), X7R ±%15 (G), DC bias 5 V −%30 (V), yaşlanma −%5 (V) |

## 3. Marj tanımları ve sonuçlar (C3: RTU 39,2k, RBU 8,87k, RXU 90,9k, RR1U 10,0k, RR2U 46,4k)
| Marj | Tanım | Katı | RSS (bilgi) |
|---|---|---|---|
| a başlatma | 20 − I_Q·R − V_r,max | **+0,00664 V** | +0,109 V |
| b aşırı deşarj | V_f,min − 18,0 | **+0,01272 V** | +0,104 V |
| c motorboating | min_köşe(H − (P_IN/V_f)·R) − 0,10 | **+0,02789 V** | +0,043 V |
| d 20 V'ta çalışma | VIN_op(20 V, 7,5 A) − V_f,max − 0,10 | **+0,14514 V** | +0,238 V |
| e 26 V'ta ortak mod | 4,90 − S_UV,max(26 V) | **+0,07104 V** | – |

Tur 3 (T3-07, köşe başına VIO/CMRR + REF yükü) öncesi değerler: a +6,73, b +12,64, c +27,87, d +145,22, e +71,04 mV; fark ≤ 0,09 mV. Eşik aralıkları (VIO 6 mV): V_r 19,458–19,990 V; V_f 18,013–18,500 V; H 1,432–1,503 V. VIN_op(20 V) = 18,746 V. Köşeler arası V_r,min − V_f,max = 0,958 V.
(Önceki 4 mV'lik hatalı VIO ile: a +0,0185, b +0,0234, c +0,0295, d +0,1561 V; V_r 19,470–19,978 V; V_f 18,023–18,490 V.)
c için açıklama: kapanma anında VIN = V_f iken EMF = V_f + I·R olur. Akım kesilince VIN bu EMF'ye çıkar. EMF < V_r olmalıdır, yoksa salınım oluşur. Bu karşılaştırma aynı köşede (aynı kart, aynı sıcaklık) yapılır.

## 3a. 20 V başlatma garantisi durumu (ChatGPT WP2 Tur 1 P0) – **AÇIK BLOKLAYICI**
`start_guarantee_status()` (`uvlo_budget.py`, `results/uvlo-budget.json` → `start_guarantee`). Durum: **`NOT_GUARANTEED_POSITIVE_UNDER_ASSUMPTIONS`**. Katı marjlar pozitif (a +6,64 mV, b +12,72 mV; Tur 3 köşe başına hesap) ama yalnızca aşağıdaki G-dışı terimlerin varsayılan sınırları doğruysa. Bu yüzden "20 V'ta garantili yeniden başlatma" **iddia edilmiyor**. Gereksinimler (E_START 20,0 V EMF, V_FALL_MIN 18,0 V, MARGIN_DYN 0,10 V) gevşetilmedi.

| G-dışı terim | Sınıf | Bütçedeki değer | a marjından yediği | b marjından yediği | Sınırı var mı? |
|---|---|---|---|---|---|
| TLV3202 iç histerezis Hint üst sınırı | V | 5 mV (datasheet: 1,2 mV tipik, max yok) | 11,19 mV (tipik 1,2 mV'a göre) | 10,23 mV | **Hayır** |
| REF35 uzun dönem kayma (40 ppm/1000 h × 10) | V | 400 ppm | 7,95 mV | 7,25 mV | **Hayır** (10 kh doğrusal ekstrapolasyon) |
| REF35 TC 105→125 °C ekstrapolasyonu | Ç | 240 ppm | 4,77 mV | 4,35 mV | spesifikasyon dışı |
| I_Q_PRESTART × R_TOTAL_MAX | V | 15 mA × 0,25 Ω | 3,75 mV | – | varsayım |
| REF35 termal histerezis | T | 70 ppm | 1,39 mV | 1,27 mV | tipik, sınır olarak kullanıldı |
| REF35 yük regülasyonu | T | 20 ppm/mA | 0,03 mV | 0,03 mV | tipik |
| REF35 lehim kayması | V | 0 | 0 | 0 | **Hayır** (belirtilmemiş; B-U07) |
| PSRR terimi için 0,1 V besleme kayması | V | 0,1 V × 65 dB | < 0,06 mV (karşılaştırıcıda) | – | varsayım |

**Kırılma noktaları (Tur 2 hesabı, Tur 3 düzeltmesi ≤ 0,09 mV):** Hint_max = **7,28 mV** olursa a = 0. REF35'te bütçe dışı **+338 ppm** ek hata (ör. lehim kayması) a'yı, **+698 ppm** b'yi sıfırlar. Tek bir sınırsız terimin (Hint, lehim kayması, uzun dönem) bu düzeyleri aşmayacağına dair datasheet garantisi yok. Bu yüzden mevcut marj, garanti için **yetersiz** kabul edildi.

**Tasarım değişikliği önerileri (uygulanmadı; KiCad/BOM değişmedi; parametrik Ç, parça seçilmedi/doğrulanmadı).** `search_c3()` en iyi E96 yeniden merkezlemesi:
| Seçenek | En kötü marj | a / b / c (mV) | Not |
|---|---|---|---|
| O0 yalnız bölücüyü yeniden merkezlemek (mevcut parçalar) | +6,73 mV (Tur 2; Tur 3 köşe başına +6,64) | 6,73 / 12,64 / 27,87 | Seçili tasarım zaten optimum → **yalnız bölücü/histerezis ayarı yetmez** |
| O1 referans toplam hatası ×0,5 (daha düşük TC/kayma sınıfı referans) | +33,47 mV | 34,03 / 40,15 / 33,47 | Aday referansın garantili TC/uzun dönem verisi doğrulanmalı |
| O2 bölücü direnç hatası ×0,5 (oran-eşlemeli ince film ağı sınıfı) | +63,48 mV | 63,48 / 64,62 / 63,51 | En etkili seçenek. Oran toleransı ve TCR izleme garantili olmalı |
| O3 O1 + O2 | +84,86 mV | 84,86 / 85,99 / 89,12 | |
Ek seçenekler: (i) Hint bağımlılığını kaldırmak için garantili histerezis/ofset verisi olan karşılaştırıcı. Bunun için aday datasheet incelemesi gerekir (bu turda yapılmadı). (ii) B-U tezgâh ölçümüyle Hint, REF35 lehim kayması ve uzun dönem kaymanın sınırlanması. Bu ölçüm garantiyi ancak lot kapsamı için destekler, datasheet garantisinin yerini tutmaz. Seçim kullanıcı/donanım kararıdır.

## 3b. O3 aday varyantı (WP2 Tur 2) – **aday, KiCad/ana BOM değişmedi; başlatma garantisi AÇIK**
`uvlo_budget.py` → `results/uvlo-budget.json` → `o3_variant` (commit 873a94a). Parçalar: **U23 REF5040IDGKT** (TI SBOS410O; 4,096 V, %0,05 başlangıç, 3 ppm/°C maks, −40…125 °C), V5_OVP'den beslenir, yalnız VREF_UV → RR1U'yu sürer; WP1 REF35 (U12) yalnız OVP'yi besler (OVP köşesi VREF_P typ 4,096 / wchi 4,105424 / wclo 4,086576, değişmedi). Bölücüler: **N1** = Vishay ACAS 0606 AT, DF düzeni, grade U (Rt/Rb), **N2** = ACAS (RR1/RR2), Rx ayrık ERA-3ARB (0,1 %). Direnç modeli: eleman = nom·(1 + s_c·(e_abs − e_rel) + s_i·e_rel), e_rel %0,25 (oran), e_abs %0,4 (Vishay ACAS doc 28770, 15-Jun-2026). E_REF_O3 = 1321 ppm + 50 ppm/mA yük regülasyonu; I_Q_PRESTART_O3 = 16,2 mA (REF5040 dahil).

| Değer | O3 seçimi |
|---|---|
| Rt / Rb / Rx / RR1 / RR2 | 24,3k / 5,36k / 53,6k / 10,0k / 41,2k |
| V_r / V_f / H (köşe aralığı) | 19,560–19,922 V / 18,070–18,394 V / 1,476–1,542 V |
| Marjlar a / b / c / d / e | **+73,87 / +70,32 / +75,54 / +251,33 / +182,14 mV** (Tur 3 köşe başına hesap, 16384 köşe; Tur 2: +73,91 / +70,28 / +75,54 / +251,37 / +182,14). C3: +6,64 / +12,72 / +27,89 / +145,14 / +71,04 |
| 125 °C göreli kayma duyarlılığı | a +45,37, b +42,88 mV |
| Durum | **`NOT_GUARANTEED_POSITIVE_UNDER_ASSUMPTIONS`** – 3 sınırsız terim: REF5040 uzun dönem, REF5040 lehim kayması, TLV3202 Hint |
| Terim etkileri a / b | uzun dönem +5,46 / +4,99; termal histerezis +0,99 / +0,91; Hint +11,43 / +10,47; ACAS DF varsayımı (Tur 2 değeri) +37,88 / +36,73; I_Q +4,05 (yalnız a) mV |
| Regresyon | Yanlış Rb 5,23k: en kötü −0,3013 V → beklenen FAIL (bütçe ve deck `o3-reg-misset-rbu-5k23-vrmax`) |

**Tur 3 (T3-04, T3-08):** Vishay 28770 dayanıklılık (70 °C 1000 h) ve lehim ısısı rakamları not (2) gereği yalnız **AE** (eşit değer) dizileri içindir; O3 DF düzenidir. Bu yüzden mutlak ve göreli dayanıklılık + lehim terimleri artık **V (varsayım, AE-only, DF için varsayıldı)** sınıfındadır (`net_rel_terms`, `net_abs_terms`). Duyarlılık (`sensitivity_ae_only_terms`): 85 °C/85 % RH nem-ısı yalnız-AE senaryosunda a 66,6 mV; 125 °C dayanıklılık senaryosunda a 44,3 / b 42,79 mV – hepsi pozitif ama **garanti değil**. Başabaş: göreli kaymada bütçe dışı **%0,187** ek kayma a/b'yi sıfırlar. Vishay'den DF sınırı teyidi ya da çevre/yaşlanma yeterlilik planı gerekir (BENCH-TEST B-U). Aday sipariş kodları (datasheet kod biçimine göre, **stok ve pin-1/eşleme doğrulanmadı**): N1 **ACASN5361U2432P1AT** (R1 5,36k / R2 24,3k), N2 **ACASN1002U4122P1AT** (R1 10,0k / R2 41,2k). Satın alma yapılmadı.

Notlar: O3, C3 parametrik O3 tahminine (+84,86 mV) yakın ama altında; sebebi gerçek parça verisi (ACAS oran toleransı, REF5040 yük regülasyonu, I_Q artışı). ACAS DF grade U sipariş kodu **doğrulanmadı**; varsayım yanlışsa (ör. yalnız AE düzeni) a/b'den ~37 mV kaybolur. LT5400 (O3b) reddedildi: önerilen REF5050 ≥ 5,2 V besleme ister. TLV3602 önerilmedi: histerezis tablosu VCM = VEE + 0,3 V koşulunda; bu devrede ~3,37 V; ayrıca 7 mA/kanal. Stok: 2026-10-25 12:31 TSİ Mouser araması erişim engeli (captcha) → **doğrulanamadı**; önceki arama özeti (saat belirsiz) ACASN1001S2001P1AT 947, ACASN1002U1002P1AT 15 991 adet gösterdi, bunlar seçilen değerler değildir. Simülasyon fiziksel ölçüm değildir.

## 4. Zamanlayıcı ve EN (RTT 11,0k, CTT 10 µF, RHB 1 M, RK1/RK2 10,0k/40,2k, RDEN/RUV2 10k/10k)
| Büyüklük | Sonuç | Marj |
|---|---|---|
| Soğuk açılış gecikmesi | 77,7–255,3 ms | ≥ 60 ms: +17,7 ms; ≤ 300 ms: +44,7 ms |
| Tam dip sonrası (T0 = 0,85 + 0,225 V) | 64,9–219,8 ms | +4,89 ms |
| Zamanlayıcı headroom (V∞ − V_th) | ≥ 0,736 V | +0,536 V (gerekli 0,2 V) |
| EN yüksek | ≥ 2,289 V | VEN-TH,max + 0,5 V üzerinde +0,739 V |
| EN düşük | ≤ 0,121 V | < 0,4 V: +0,279 V |
| EN düşük, U22 açık (OUTA düşük) | ≤ 2,6 mV = (V5,maks/(RDEN·0,97) + IEN)·RON,maks 4,9 Ω (G, SCDS410D s.5) | < 0,4 V: +0,397 V |
| EN yüksek, U22 kapalı kaçağı | 2 nA × 5 kΩ = 10 µV (G, SCDS410D s.5) | EN yüksek sonucunu değiştirmez (≥ 2,289 V) |
Not: EN bölücüsü (RDEN, RUV2) önceki sürümde yanlışlıkla ERA toleransıyla hesaplanmıştı. 2026-10-25'te katı %3'e düzeltildi (commit 6e6c063). Eski değerler 2,351 / 0,118 V idi.

## 4b. CTT hızlı reset + Schmitt zamanlayıcı (WP2 Tur 3 UVLO-T3-02) – **aday, KiCad/ana BOM değişmedi**
`uvlo_budget.py` → `results/uvlo-budget.json` → `timer.reset` (5a81584; 2^10 = 1024 köşe). Devre: OUTA_UV, RST/CST gerdirici ve DST (BAT54A, jenerik model, V) ile OUTA_D'ye taşınır; OUTA_D düşünce SEL24 = OUTA_D·RSB/(RSA+RSB) U24 TMUX1102'yi (G: VIL ≤ 0,87 V / VIH ≥ 1,49 V, iki köşe) açar ve CTT, RDSC 100 Ω üzerinden boşalır. U25 TMUX1102 + RK1A 10,5k / RK4 210k zamanlayıcı karşılaştırıcısına Schmitt alt eşiği V_L ekler (yükselen eşik bacağı (RK1A+RON)‖RK4 = 10,0k, önceki ile aynı).

| Büyüklük | Sonuç | Marj / not |
|---|---|---|
| V_L (Schmitt alt eşik) | 0,754–0,852 V | |
| Bırakmada CTT (V_rel) | ≤ 53,5 mV | V_L'nin altında, +0,600 V |
| Gerdirici tutma süresi (OUTA ↑ sonrası reset devam) | 7,93–26,26 ms | deşarjdan +5,02 ms uzun |
| CTT deşarj süresi | ≤ 2,91 ms | |
| Deşarj tepe akımı | ≤ 52,6 mA | TMUX1102 IDC 60 mA (G, Tj 125 °C) altında, +7,4 mA; darbe değeri varsayımı gerekmez |
| Tam reset sonrası VIN-OK → EN | ≥ 85,04 ms | |
| Kısa dip sonrası VIN-OK → EN (en kötü) | ≥ 67,75 ms | 65 ms geçici hedefe +2,75 ms; 60 ms sınırına +7,75 ms |
| VIN-OK → EN maks (tutma dahil) | ≤ 281,8 ms | ≤ 300 ms: +18,2 ms |

Not: incelemenin geçici hedefi "her dip sonrası OUTA ↑ anında V_CTT ≤ 1,0 V" bu mimaride **harfiyen sağlanmaz**: reset OUTA döndükten sonraki tutma penceresinde tamamlanır (OUTA ↑ anında CTT simülasyonda 4,37 V'a kadar görülebilir), bırakma anında CTT ≤ 53,5 mV'tur ve gecikme son OUTA ↑'tan ölçülür. Asıl sınır (≥ 60 ms, son OUTA ↑'tan) ve 65 ms geçici hedef bütçede ve simülasyonda sağlanır (RESULTS.md §11). µs mertebesindeki darbeler (OUTA ~1,6 ms'den kısa düşük) Schmitt yeniden başlatmasını tetiklemeyebilir; reset-baskın mandal önerisi açık. Simülasyon fiziksel ölçüm değildir.

## 5. Alternatifler ve regresyonlar
| Durum | En kötü | Beklenen | Gerçekleşen |
|---|---|---|---|
| A0 baseline 180k/10k | V_r,max 21,12 V | FAIL | FAIL ✔ |
| A1 yalnızca bölücü | V_f tipik ≈ 16,16 V | FAIL | FAIL ✔ |
| B TPS3700 | H tipik 0,27 V | FAIL | FAIL ✔ |
| D LM7480x | V_f,min 16,94 V | FAIL | FAIL ✔ |
| C2 itme-çekme Rh (en iyi E96: 28,0k/7,87k/95,3k) | −0,1117 V | FAIL | FAIL ✔ |
| Yanlış RBU 8,66k | −0,3599 V | FAIL | FAIL ✔ |
| Yanlış RXU 100k | −0,1025 V | FAIL | FAIL ✔ |

## 6. Düzeltme günlüğü
- 2026-10-25: VIO CMRR terimi RR2 = 40,2k'da hesaplanıyordu (0,09 mV iyimser). `vio_c3(RR1, RR2)` ile düzeltildi.
- 2026-10-25: RHB 1 M, ERA aralığı dışında kaldığı için %1 jenerik parça (katı %3) olarak hesaba katıldı.
- 2026-10-25: RDEN/RUV2 katı %3 olarak hesaba katıldı (§4).
- 2026-10-25 (Tur 1 P0): TLV3202 VIO 4 → 6 mV (SBOS561C Rev C s.5 tablo 6.5; 4 mV TLV3201 satırıydı). a +18,50 → +6,73 mV, b +23,41 → +12,64 mV. `start_guarantee_status()` eklendi (§3a); decks yeniden üretildi.
- 2026-10-25: U22 EN kapısı eklendi (§4, `en_low_gated_margin_V`). Eşik bütçesi (V_r/V_f/H, marj a–e) değişmedi.
- 2026-10-25 (Tur 3 T3-07): VIO/CMRR ve REF yük akımı köşe başına; C3 a/b/c/d/e +6,64 / +12,72 / +27,89 / +145,14 / +71,04 mV; O3 +73,87 / +70,32 / +75,54 / +251,33 / +182,14 mV (f6482f0).
- 2026-10-25 (Tur 3 T3-04): ACAS DF dayanıklılık/lehim terimleri G → V (AE-only) (f6482f0).
- 2026-10-25 (Tur 3 T3-02): §4b CTT hızlı reset + Schmitt aday bütçesi (5a81584).
Hiçbir sınır gevşetilmedi.
