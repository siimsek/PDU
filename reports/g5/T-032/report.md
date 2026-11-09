# T-032 Grup 1 — şema ile SPICE kapsam eşlemesi

**Durum: Review. Şema, PCB, deck ve tasarım değiştirilmedi.** Bu rapor kapsam eşlemesidir; ad veya değer eşitliği model doğrulaması değildir ve simülasyon fiziksel kanıt değildir.

Girdi: `reports/g5/T-027/ledger-*.csv`, `design/pdu_v2.cir`, `design/pdu_v2_params.inc`, `reports/g2/sim-results.json`. Çıktı: [group1-map.csv](group1-map.csv) (pin satırları, deck satır numaraları, durum, gerekçe) ve [coverage.json](coverage.json). [gen_map.py](gen_map.py) üretir.

Karar: `pdu_v2.cir` kendi başlığına göre silikon modeli değil, davranışsal ortalama model. Bu yüzden eşleme durumu ve model uygunluğu ayrı sütundur.

## Grup 1 (20 referans, 136 pin)

| Durum | Sayı | Referans |
|---|---:|---|
| EŞLEŞTİ | 13 | D1, RS1, RS2, L1, L2, RFB1, RFB2, R_TRIM, RCOMP, CCOMP, CHF, RUV1, RUV2 |
| AÇIK | 7 | Q1, U5, U1, U2, Q2, U6, U3 |

Toplu temsil: SPICE `RFB2` 10,2 kΩ, şemada RFB2 9,76 kΩ + R_TRIM 442 Ω (10,202 kΩ). R_INJ deck'te yok; `RFB1` üst ucu `vraw` varsayılıyor.

Kalan 160 referans AÇIK, ≤20'lik 8 grup ([coverage.json](coverage.json)). Çoklu temsil: COUT 32 referans → `COUT`, CIN 9 → `CIN`, CEF 4 → `CEFIN` (eşleme grubu sırasında doğrulanacak). 38 referans test/mekanik adayı olarak ayrıldı; UYGULANMAZ kararı kendi grubunda gerekçeyle verilecek.

## Simülasyon durumu (`reports/g2/sim-results.json`, 76 koşu)

| Koşu | Tamam | Kriter | Not |
|---|---|---|---|
| f1_noprot_baseline | evet | hayır | Korumasız karşılaştırma koşusu; rapor adı referansı işaret ediyor (kasıtlılık bu kartta bağımsız doğrulanmadı) |
| f3_stacked_low_setpoint_cmin_gmmin | evet | hayır | AÇIK |
| f3_stacked_high_setpoint_cmin_gmmin | evet | hayır | AÇIK |
| f4_input_loss_without_drev | evet | hayır | D_REV olmadan karşılaştırma |
| f5_vt11.487_td300ns_ctyp_r200m_l0.8 | hayır | hayır | Tamamlanmadı, PASS sayılmaz |
| f5_vt11.765_td300ns_ctyp_r200m_l0.8 | hayır | hayır | Tamamlanmadı, PASS sayılmaz |

## Modellenmeyen davranış (eksik listesi)

Deck'te karşılığı olmayan veya soyut kalanlar. Sonuçları **doğrulanamadı**.

- **U3/U4 dVdt:** `BEF1/BEF2` çıkış rampası içermez; CDVDT ve 70 mm hat etkisi (R-022 Tur 9) kapsam dışı. Veri sayfası hesabı veya model gerekir.
- **U5/U6 VCAP ve gate:** Şarj pompası yok; `/VCAP` şarj süresi ve Q1/Q2 gate zamanlaması soyut (`TDLY`).
- **U1/U2 yardımcı beslemeler:** VCC, VDDA, BIAS, CBOOT/SW4 yok; BIAS'ın AGND'ye bağlı olmasından doğan ek kayıp `power.py`'de VARSAYIM.
- **Anahtarlama ve ripple:** Ortalama model; SW kuplajı, COMP/FB yakınlığı, parazitik L ve via etkisi yok.
- **R_INJ / FRA, IMON, ILIM ağı, PG/SYNC ve U9/U15 mantık kapıları:** Yok veya soyut.
- **Isı:** Yok.

## Önerilen takip

Üretim kararı THINKER'ındır. Aday işler: dVdt ve VCAP için veri sayfası hesabı veya alt devre, iki F5 tamamlanmayan köşenin yeniden koşusu, T-032 G2 eşlemesi. Bu kart yalnız kapsamı kaydeder.
