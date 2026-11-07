# G2 — tezgâh kabul planı (T0–T6)

SİM sütunu davranışsal ortalama model tahminidir ([`SIM-RESULTS.md`](SIM-RESULTS.md)); HESAP sütunu `analysis/g2` hesaplarıdır. **Kabul yalnız ölçüm sütunuyla verilir.** Kriterler gevşetilmez: O1 anlık ≤12.0 V, kararlı bara ≤11.1605 V, yük adımında bara ≥10.78 V, U3/U4 IN <30 V (hedef ≤24 V).

## Ekipman

- 4 kanal osiloskop ≥200 MHz, 10:1 pasif prob (yay uçlu kısa GND), ≥1 diferansiyel prob (VDS, VGS ölçümü için)
- Akım probu ≥50 A tepe, ≥10 MHz (faz/hata akımı)
- Laboratuvar güç kaynağı 0–30 V / ≥10 A, akım sınırlı; ikinci kaynak 0–30 V / 3 A (enjeksiyon)
- Elektronik yük ≥10 A, adım eğimi ≥1 A/µs, dinamik mod
- Frekans tepkisi analizörü (FRA) 10 Hz–1 MHz, enjeksiyon trafosu
- 6.5 hane DMM (eşik ölçümü, trim), termal kamera veya termokupl
- R_TRIM seti: TNPW0603 0.1 % 280–604 Ω (b4-results.json `trim_table`)
- **OC enjeksiyonu (G4):** RS1/RS2 Kelvin padlerine 0–20 A darbe akım kaynağı (≤10 µs, buck kapalı) veya şönt üzerinde eşdeğer gerilim (75–110 mV) uygulayan düşük empedanslı darbe üreteci
- **OV enjeksiyon fixture'ı:** harici MOSFET + sürücü + seri 1–2 Ω güç direnci + 6.8 µH bobin üzerinden 26 V'u `J_OVP_INJ_BUS`'a bağlar (yüksek taraf kısasının emülasyonu); buck `JP_EN_BUCK` ile kapalı. Ayrı yavaş rampa modu: 0.1 V/s.

## Durdurma koşulları (her testte)

VSAFE >24 V, O1 >12.0 V, LM70880 kılıf >110 °C, Q1/Q2 kılıf >100 °C, beklenmeyen giriş akımı >6 A sürekli, duman/koku → kaynağı kes, kaydet, testi durdur.

## Testler

| Test | Yöntem | HESAP / SİM tahmini | Ölçüm kabul kriteri |
|---|---|---|---|
| **T0** görsel/süreklilik (+ kart dışı F1: Eaton PV-10A10F / CHPV1U batarya + kablosunda, bataryaya en yakın) | Polarite (D1, D2/D3, D_REV, Q1, Q2), kısa devre ölçümü (VIN, VOUT, VSAFE, P5V–GND) | — | kısa yok; diyot yönleri doğru |
| **T-1** O1 ve S2E gerçek akım ölçümü (G4) | Hedef yük (T3 Gemstone O1, S2E) ile çalışma profilinde akım probu + 10 kHz kayıt: ortalama, 10 ms RMS, tepe, başlangıç akımı | Tasarım zarfı: BUS 7.5 A, O1 ILIM 7.23–9.07 A, S2E 4.36–5.66 A (DATASHEET p.9) | O1 tepe < 7.23 A (ILIM min) ve RMS ≤7.0 A; S2E tepe < 4.36 A; aşılırsa RILIM/konnektör/COUT kararı yeniden açılır |
| **T1** yüksüz açılış | 20 / 22.2 / 26 V, akım sınırlı kaynak; VRAW, VSAFE, O1, S2E, VIN | SİM F2: VRAW son 11.0 V, aşım ≤11.02 V, mandal set olmaz; hot-plug VIN tepe 42.1 V (1 µH kablo VARSAYIMI) | VRAW 10.8333–11.1605 V; aşım <11.259 V (trip_min); mandal Q=L; VIN tepe <65 V |
| **T1b** kart başı trim (G4) | 25 °C, yüksüz, VIN 22.2 V, 15 dk ısınma; VOUT'u 6.5 hane DMM ile ölç; `b4-results.json` `trim_table`'dan R_TRIM seç (varsayılan 442 Ω → 10.994 V); tak, tekrar ölç | HESAP trimli pencere 10.888–11.105 V | Trim sonrası VOUT 10.980–11.008 V (10.994 V ± ½ adım 0.125 %); kayıt: seri no, R_TRIM, önce/sonra |
| **T2** UVLO | Yavaş rampa 15→22 V ve geri; dip 22.2→15→22.2 V | HESAP açma 17.365–19.623 V; düşüş ~16.56 V **tipik**; SİM F2: 20 V'a rampada açılır, dipte kapanıp yeniden kalkar | Açma ≤20.0 V; kapanma kaydedilir (garanti aralığı AÇIK); yeniden kalkışta mandal set olmaz |
| **T3** döngü (FRA) | R_INJ=49.9 Ω, TP_FB_INJ_A/B; VIN 20/26 V × 0.75/7 A | Model (G4, 32× COUT, RCOMP 33.2k) PM min 63.1°, GM min 11.5 dB, fc 9.6–39.6 kHz; gm maks bilinmiyor (0.5–1.8 mS'de geçer) | **PM ≥45°, GM ≥6 dB** her noktada; gerekirse RCOMP 22–47k / CCOMP 4.7–22 nF / CHF 22–100 pF |
| **T4** yük adımı + termal | 0.75→7→0.75 A (O1 portundan, S2E 0.22 A); 30 dk 7 A ısıl | SİM F3 (G4) nominal min 10.89–10.93 V, bırakma ≤11.09 V; trimli köşeler 10.79 / 11.20 V; trimsiz yığılmış köşeler 10.73 / 11.26 V (FAIL, T1b ile kapanır); HESAP LM70880 Tj 105.9 °C @50 °C, 95.9 °C @40 °C (EVM bakırı, VARSAYIM) | T1b sonrası: bara min ≥10.78 V; bırakma tepe <11.22 V ve mandal set olmaz; kılıf sıcaklıklarından Tj ≤125 °C tahmini (ortam 50 °C ve 40 °C'ye ölçekle) |
| **T5a** OV eşiği | Buck kapalı; J_OVP_INJ_BUS'tan 0.1 V/s rampa; Q (TP_OVP_Q) yükseldiği VRAW | HESAP 11.259–11.537 V | Ölçülen trip bu aralıkta ve >11.22 V |
| **T5b** kapanma gecikmesi | Fixture adım modu (VRAW 11.0→13 V, <1 µs yükselme); TP_OVP_SENSE geçişi → TP_ISO_GATE (VGS<1 V) ve Q2 akımı <1 mA | HESAP ≤1.048 µs (karşılaştırıcı 50 mV OD + LM74502H 4.7 nF koşullu) | **Ölçülen ≤1.0 µs gate, toplam ≤1.05 µs**; aşılırsa yedek B / daha küçük Qg FET değerlendirilir |
| **T5c** yüksek taraf kısa emülasyonu | Fixture: 26 V → 6.8 µH → VRAW, buck kapalı, yük yok ve 5 A; COUT tam takılı | SİM F1 (G4, doğrusal olmayan L(i) + OC tetiği): O1 ≤11.37 V, VSAFE ≤11.37 V, VDS ≤24.9 V, açılışta faz akımı ≤22.1 A, sonrasında ≤138 A; ham bara ≤35.8 V; korumasız referans O1 19.35 V (FAIL). HESAP ≤11.41 V | **O1 ≤12.0 V, VSAFE <24 V**; tetik yolu (OC/OV) TP_OC_SENSE ve TP_OVP_BUS_N'den kaydedilir; Q2 VDS < 100 V; VRAW < 60 V; Q2 sağlam |
| **T5d** kaba OV yolu | R_OVT sökülü (hassas yol kör) + T5a/T5c | HESAP 11.58–13.74 V; G4 SİM F5 residual (OC yolu aktif) O1 11.20 V | T5c ile: O1 ≤12.0 V (OC yolu tetikler); yalnız T5a rampasında VSAFE ≤13.74 V (kaba eşik) |
| **T5g** faz OC eşiği ve gecikmesi (G4) | Buck kapalı; RS1 ve RS2'ye ayrı ayrı akım darbesi (0→20 A, 1 µs yükselme) ve yavaş rampa; TP_OC_SENSE1/2, TP_OVP_BUS_N, Q, TP_ISO_GATE | HESAP eşik 12.97–13.60 A; OC zinciri ≤2.556 µs (INA296 1.5 µs VARSAYIM); izinli gerçek gecikme 3,29 µs @ L tabanı 0,05 (D-004 bağımsız HESAP) | Eşik 12.97–13.60 A içinde; **tam zincir gecikmesi (akım 13,6 A'yı geçiş → TP_ISO_GATE VGS <1 V) ≤3,0 µs**, ölçüm genişletilmiş belirsizliği U ≤0,1 µs (prob gecikmesi düzeltilmiş, akım probu ≥10 MHz); 26 V, min Ceff, her faz ayrı; T5c ile birlikte doğrudan O1 tepe ≤12,0 V (D-004). Aşılırsa D-004 seçenek (a)/(b) yeniden açılır; her iki faz mandalı set eder |
| **T5e** ray kaybı | Normal çalışmada U10 çıkışı zorla düşürülür (P5V→0); VIN kaybı; VRAW kaybı | HESAP EN kapama P5V 2.57–3.16 V; tUVLO_OFF tipik 2 µs | Q2 kapanır, eFuse'lar kapanır, yeniden açılışta mandal temiz; kapanma süresi kaydedilir |
| **T5f** reset | Hata sürerken ve kalktıktan sonra SW1 | DATASHEET fonksiyon tablosu: hata sürerken Q=H | Hata sürerken açılmaz; hata kalkınca yalnız SW1 veya güç döngüsü açar |
| **T6a** O1 kısa devre | 10 mΩ kısa, O1 | SİM F4 (ILIM max 9.07 A, aktif sınırlayıcı TPS259824L): ayırıcı akımı ≤9.29 A, S2E min 10.84 V, mandal set olmaz | O1 akımı 7.23–9.07 A aralığında sınırlanır/keser; S2E ≥9 V (S2E datasheet min) |
| **T6b** giriş kaybı / OUT>IN | VBAT ani kesme, O1 yüksüz, S2E 0.22 A; 3 s kayıt | SİM F4: OUT−IN ≤0.115 V (D_REV ile; D_REV'siz 0.758 V FAIL) | OUT−IN ≤0.3 V her an (TPS25982 abs-max) |
| **T6c** ILIM toplam | O1 ve S2E aynı anda rampa | HESAP garantili-min 7.23 + 4.36 A | Her port kendi aralığında; toplam ≥7.5 A'da kesme olmaz |

## Kayıt

Her test için: tarih, kart seri no, ekipman/prob, ortam sıcaklığı, ham osiloskop dosyası, kabul sonucu. Fiziksel kabul tamamlanmadan G2 tasarımı "doğrulandı" sayılmaz.
