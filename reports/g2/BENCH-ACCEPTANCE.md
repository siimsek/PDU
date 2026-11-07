# G2 — tezgâh kabul planı (T0–T6)

SİM sütunu davranışsal ortalama model tahminidir ([`SIM-RESULTS.md`](SIM-RESULTS.md)); HESAP sütunu `analysis/g2` hesaplarıdır. **Kabul yalnız ölçüm sütunuyla verilir.** Kriterler gevşetilmez: O1 anlık ≤12.0 V, kararlı bara ≤11.1605 V, yük adımında bara ≥10.78 V, U3/U4 IN <30 V (hedef ≤24 V).

## Ekipman

- 4 kanal osiloskop ≥200 MHz, 10:1 pasif prob (yay uçlu kısa GND), ≥1 diferansiyel prob (VDS, VGS ölçümü için)
- Akım probu ≥50 A tepe, ≥10 MHz (faz/hata akımı)
- Laboratuvar güç kaynağı 0–30 V / ≥10 A, akım sınırlı; ikinci kaynak 0–30 V / 3 A (enjeksiyon)
- Elektronik yük ≥10 A, adım eğimi ≥1 A/µs, dinamik mod
- Frekans tepkisi analizörü (FRA) 10 Hz–1 MHz, enjeksiyon trafosu
- 6.5 hane DMM (eşik ölçümü), termal kamera veya termokupl
- **OV enjeksiyon fixture'ı:** harici MOSFET + sürücü + seri 1–2 Ω güç direnci + 6.8 µH bobin üzerinden 26 V'u `J_OVP_INJ_BUS`'a bağlar (yüksek taraf kısasının emülasyonu); buck `JP_EN_BUCK` ile kapalı. Ayrı yavaş rampa modu: 0.1 V/s.

## Durdurma koşulları (her testte)

VSAFE >24 V, O1 >12.0 V, LM70880 kılıf >110 °C, Q1/Q2 kılıf >100 °C, beklenmeyen giriş akımı >6 A sürekli, duman/koku → kaynağı kes, kaydet, testi durdur.

## Testler

| Test | Yöntem | HESAP / SİM tahmini | Ölçüm kabul kriteri |
|---|---|---|---|
| **T0** görsel/süreklilik | Polarite (D1, D2/D3, D_REV, Q1, Q2), kısa devre ölçümü (VIN, VOUT, VSAFE, P5V–GND) | — | kısa yok; diyot yönleri doğru |
| **T1** yüksüz açılış | 20 / 22.2 / 26 V, akım sınırlı kaynak; VRAW, VSAFE, O1, S2E, VIN | SİM F2: VRAW son 11.0 V, aşım ≤11.02 V, mandal set olmaz; hot-plug VIN tepe 42.1 V (1 µH kablo VARSAYIMI) | VRAW 10.8333–11.1605 V; aşım <11.265 V (trip_min); mandal Q=L; VIN tepe <65 V |
| **T2** UVLO | Yavaş rampa 15→22 V ve geri; dip 22.2→15→22.2 V | HESAP açma 17.365–19.623 V; düşüş ~16.56 V **tipik**; SİM F2: 20 V'a rampada açılır, dipte kapanıp yeniden kalkar | Açma ≤20.0 V; kapanma kaydedilir (garanti aralığı AÇIK); yeniden kalkışta mandal set olmaz |
| **T3** döngü (FRA) | R_INJ=49.9 Ω, TP_FB_INJ_A/B; VIN 20/26 V × 0.75/7 A | Model PM min 66.9°, GM min 11.7 dB, fc 9.8–40.9 kHz | **PM ≥45°, GM ≥6 dB** her noktada; gerekirse RCOMP 10–33k / CCOMP 2.2–10 nF / CHF 22–100 pF |
| **T4** yük adımı + termal | 0.75→7→0.75 A (O1 portundan, S2E 0.22 A); 30 dk 7 A ısıl | SİM F3 nominal: min 10.81 V (en kötü Ceff/gm), bırakma maks 11.19 V; HESAP LM70880 Tj 137.7 °C @85 °C ortam (VARSAYIM) | Bara min ≥10.78 V; bırakma tepe <11.22 V ve mandal set olmaz; kılıf sıcaklıklarından Tj ≤125 °C tahmini |
| **T5a** OV eşiği | Buck kapalı; J_OVP_INJ_BUS'tan 0.1 V/s rampa; Q (TP_OVP_Q) yükseldiği VRAW | HESAP 11.265–11.531 V | Ölçülen trip bu aralıkta ve >11.22 V |
| **T5b** kapanma gecikmesi | Fixture adım modu (VRAW 11.0→13 V, <1 µs yükselme); TP_OVP_SENSE geçişi → TP_ISO_GATE (VGS<1 V) ve Q2 akımı <1 mA | HESAP ≤1.047 µs (karşılaştırıcı 50 mV OD + LM74502H 4.7 nF koşullu) | **Ölçülen ≤1.0 µs gate, toplam ≤1.05 µs**; aşılırsa yedek B / daha küçük Qg FET değerlendirilir |
| **T5c** yüksek taraf kısa emülasyonu | Fixture: 26 V → 6.8 µH → VRAW, buck kapalı, yük yok ve 5 A; COUT tam takılı | SİM F1: O1 tepe 11.91 V (en kötü), VSAFE 11.91 V, VDS ≤27.5 V; korumasız referans O1 19.57 V | **O1 ≤12.0 V, VSAFE <24 V**; Q2 VDS < 100 V; Q2 sağlam |
| **T5d** kaba OV yolu | R_OVT sökülü (hassas yol kör) + T5a/T5c | HESAP 11.55–13.70 V; SİM F5 artık-risk koşusu | VSAFE ≤13.7 V; O1 >12 V olabilir → **artık risk kaydı** |
| **T5e** ray kaybı | Normal çalışmada U10 çıkışı zorla düşürülür (P5V→0); VIN kaybı; VRAW kaybı | HESAP EN kapama P5V 2.57–3.16 V; tUVLO_OFF tipik 2 µs | Q2 kapanır, eFuse'lar kapanır, yeniden açılışta mandal temiz; kapanma süresi kaydedilir |
| **T5f** reset | Hata sürerken ve kalktıktan sonra SW1 | DATASHEET fonksiyon tablosu: hata sürerken Q=H | Hata sürerken açılmaz; hata kalkınca yalnız SW1 veya güç döngüsü açar |
| **T6a** O1 kısa devre | 10 mΩ kısa, O1 | SİM F4: O1 akımı ≤8.35 A (ILIM typ modelinde), S2E min 10.82 V, mandal set olmaz | O1 akımı 7.23–9.07 A aralığında sınırlanır/keser; S2E ≥9 V (S2E datasheet min) |
| **T6b** giriş kaybı / OUT>IN | VBAT ani kesme, O1 yüksüz, S2E 0.22 A; 3 s kayıt | SİM F4: OUT−IN ≤2.5 mV (D_REV ile) | OUT−IN ≤0.3 V her an (TPS25982 abs-max) |
| **T6c** ILIM toplam | O1 ve S2E aynı anda rampa | HESAP garantili-min 7.23 + 4.36 A | Her port kendi aralığında; toplam ≥7.5 A'da kesme olmaz |

## Kayıt

Her test için: tarih, kart seri no, ekipman/prob, ortam sıcaklığı, ham osiloskop dosyası, kabul sonucu. Fiziksel kabul tamamlanmadan G2 tasarımı "doğrulandı" sayılmaz.
