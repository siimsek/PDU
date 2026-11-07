# G4 — kullanıcıdan gereken girdiler (en çok 6)

[`reports/g3/USER-DECISIONS.md`](../g3/USER-DECISIONS.md) listesinin yerini alır. G3 maddeleri 3 (trim), 6 (Molex/SMCJ33A) ve 8 (MLCC) G4'te tasarım/belge düzeyinde kapandı. Cevaplanmayan maddede aşağıdaki varsayılan geçerlidir (VARSAYIM).

| # | Girdi | Geçerli varsayılan | Değişirse etkilenen |
|---|---|---|---|
| 1 | **T-1: O1 ve S2E gerçek akım ölçümü** (ortalama, 10 ms RMS, tepe, kalkış; BENCH T-1) | O1 RMS ≤7.0 A, tepe < ILIM min 7.23 A; S2E < 4.36 A | RILIM_O1/S2E, J2 kontak sayısı, port iz genişliği, COUT |
| 2 | **T3 Gemstone O1 datasheet'i** (mutlak maks giriş, kısa süreli aşım toleransı) | 12.0 V sert sınır; HESAP O1 ≤11.41 V (marj 0.59 V) | O1 marjı; OC eşiği; ölçüm belirsizliği payı |
| 3 | **F1 sigorta + yuva datasheet'i** — aday Littelfuse 456 serisi 0456020.ER (20 A) veya eşdeğer ≥10 A, ≥53.3 VDC, ≥1040 A DC kesme; G4'te Littelfuse PDF tarayıcıda indirme olarak açıldı, okunmadı | F1 MPN AÇIK (BOM'da MPN'siz tek satır); footprint ÖZEL | F1 footprint, I²t koordinasyonu, PCB-READY madde 14 |
| 4 | **Vishay IHLP4040DZER6R8M01 (6.8 µH) L(I) eğrisi 16–40 A** (veya tezgâh ölçümü) | 16 A üstü son eğim uzatıldı, taban 0.15 (0.05'e kadar tarandı) | Yalnız OC tetiği devre dışıyken anlamlı; OC tetiğiyle O1 ≤11.41 V tüm tabanlarda |
| 5 | **Tasarım ortam sıcaklığı / muhafaza / hava akışı** | 50 °C (40 °C de raporlu): LM70880 Tj 105.9 / 95.9 °C (EVM bakırı); izinli ortam ≤69 °C | Bakır/via yoğunluğu, kart boyutu, BENCH T4 |
| 6 | **Trim kabulü ve batarya kesim politikası:** (a) kart başı R_TRIM üretim adımı kabul mü; (b) VFB toleransının sıcaklık payı yarı (VARSAYIM) — LM70880 için TI'dan sıcaklık/başlangıç ayrımı; (c) 18 V (3.0 V/hücre) kesim BMS'te mi | (a) evet, T1b; (b) yarı; (c) BMS — kart UVLO düşüşü 14.67–18.64 V aralığında garanti edilemez | (b) tamamı sıcaklık ise trimli adım min ≈10.75 V FAIL → COUT/RCOMP yeniden; (c) UVLO bölücüsü |

Batarya iç direnci 20–200 mΩ, 18 AWG 0.5–1.5 m kablo varsayımları (G4 varsayılan 5) değişmedi; F1 kesme akımı 1040 A bu aralığın alt ucundan gelir.
