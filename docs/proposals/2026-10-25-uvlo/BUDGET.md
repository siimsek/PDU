# WP2 2026-10-25-uvlo – Hata ve marj bütçesi

Kaynak: `simulation/proposals/2026-10-25-uvlo/uvlo_budget.py`. Komut: `python3 uvlo_budget.py > results/uvlo-budget.out`, rc 0. Makine çıktısı `results/uvlo-budget.json`.
Yöntem: her hata terimi ±1 köşelerine **katı doğrusal** toplamla girer (C3 için 2^10 köşe, zamanlayıcı için 2^10). RSS yalnızca bilgi amaçlı raporlanır. Sınıflar: **G** garanti (datasheet min/max), **T** tipik, **V** varsayım, **Ç** çıkarım.

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
| TLV3202 VIO | ≤ 4 mV | G | SBOS561C s.5 |
| TLV3202 CMRR / PSRR | ≥ 60 / 65 dB | G | SBOS561C s.5. CMRR terimi gerçek REFD = 3,3698 V'ta hesaplanır |
| VIO_C3 toplam | 4,926 mV | Ç | |
| TLV3202 Hint | 0–5 mV (1,2 mV tipik) | T/V | SBOS561C s.5 |
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
| a başlatma | 20 − I_Q·R − V_r,max | **+0,0185 V** | +0,120 V |
| b aşırı deşarj | V_f,min − 18,0 | **+0,0234 V** | +0,115 V |
| c motorboating | min_köşe(H − (P_IN/V_f)·R) − 0,10 | **+0,0295 V** | +0,044 V |
| d 20 V'ta çalışma | VIN_op(20 V, 7,5 A) − V_f,max − 0,10 | **+0,1561 V** | +0,249 V |
| e 26 V'ta ortak mod | 4,90 − S_UV,max(26 V) | **+0,071 V** | – |

Eşik aralıkları: V_r 19,470–19,978 V; V_f 18,023–18,490 V; H 1,433–1,502 V. VIN_op(20 V) = 18,746 V. Köşeler arası V_r,min − V_f,max = 0,980 V.
c için açıklama: kapanma anında VIN = V_f iken EMF = V_f + I·R olur. Akım kesilince VIN bu EMF'ye çıkar. EMF < V_r olmalıdır, yoksa salınım oluşur. Bu karşılaştırma aynı köşede (aynı kart, aynı sıcaklık) yapılır.

## 4. Zamanlayıcı ve EN (RTT 11,0k, CTT 10 µF, RHB 1 M, RK1/RK2 10,0k/40,2k, RDEN/RUV2 10k/10k)
| Büyüklük | Sonuç | Marj |
|---|---|---|
| Soğuk açılış gecikmesi | 77,8–255,0 ms | ≥ 60 ms: +17,8 ms; ≤ 300 ms: +45,0 ms |
| Tam dip sonrası (T0 = 0,85 + 0,225 V) | 65,0–219,5 ms | +4,98 ms |
| Zamanlayıcı headroom (V∞ − V_th) | ≥ 0,738 V | +0,538 V (gerekli 0,2 V) |
| EN yüksek | ≥ 2,289 V | VEN-TH,max + 0,5 V üzerinde +0,739 V |
| EN düşük | ≤ 0,121 V | < 0,4 V: +0,279 V |
| EN düşük, U22 açık (OUTA düşük) | ≤ 2,6 mV = (V5,maks/(RDEN·0,97) + IEN)·RON,maks 4,9 Ω (G, SCDS410D s.5) | < 0,4 V: +0,397 V |
| EN yüksek, U22 kapalı kaçağı | 2 nA × 5 kΩ = 10 µV (G, SCDS410D s.5) | EN yüksek sonucunu değiştirmez (≥ 2,289 V) |
Not: EN bölücüsü (RDEN, RUV2) önceki sürümde yanlışlıkla ERA toleransıyla hesaplanmıştı. 2026-10-25'te katı %3'e düzeltildi (commit 6e6c063). Eski değerler 2,351 / 0,118 V idi.

## 5. Alternatifler ve regresyonlar
| Durum | En kötü | Beklenen | Gerçekleşen |
|---|---|---|---|
| A0 baseline 180k/10k | V_r,max 21,12 V | FAIL | FAIL ✔ |
| A1 yalnızca bölücü | V_f tipik ≈ 16,16 V | FAIL | FAIL ✔ |
| B TPS3700 | H tipik 0,27 V | FAIL | FAIL ✔ |
| D LM7480x | V_f,min 16,94 V | FAIL | FAIL ✔ |
| C2 itme-çekme Rh (en iyi E96: 28,0k/7,87k/95,3k) | −0,1019 V | FAIL | FAIL ✔ |
| Yanlış RBU 8,66k | −0,3479 V | FAIL | FAIL ✔ |
| Yanlış RXU 100k | −0,1009 V | FAIL | FAIL ✔ |

## 6. Düzeltme günlüğü
- 2026-10-25: VIO CMRR terimi RR2 = 40,2k'da hesaplanıyordu (0,09 mV iyimser). `vio_c3(RR1, RR2)` ile düzeltildi.
- 2026-10-25: RHB 1 M, ERA aralığı dışında kaldığı için %1 jenerik parça (katı %3) olarak hesaba katıldı.
- 2026-10-25: RDEN/RUV2 katı %3 olarak hesaba katıldı (§4).
- 2026-10-25: U22 EN kapısı eklendi (§4, `en_low_gated_margin_V`). Eşik bütçesi (V_r/V_f/H, marj a–e) değişmedi.
Hiçbir sınır gevşetilmedi.
