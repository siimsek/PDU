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

## Grup 2 (20 kondansatör, 40 pin; R-026)

Kayıt: [group2-map.csv](group2-map.csv), [group2-coverage.json](group2-coverage.json). Üretici: [gen_group2.py](gen_group2.py). Toplu değerler `design/pdu_v2_params.inc` ile `sim_runner.py` formüllerinden yeniden hesaplandı ve eşit çıktı.

| Durum | Sayı | Referans |
|---|---:|---|
| EŞLEŞTİ | 13 | CEFIN1–2, CEFOUT1–2, CIN1–8, COUT1 |
| AÇIK | 7 | CBIN1–2, CBOOT1–2, CDVDT1–2, CIN_U5 |

Pin: 26 EŞLEŞTİ, 14 AÇIK. EŞLEŞTİ yalnız düğüm ve toplu eleman karşılığı demektir. CIN, CEFIN ve CPORT Ceff oranları VARSAYIM kalır; bu grup modeli doğrulamaz.

Eksikler: CBIN (2×10 nF) `CIN_EFF` içinde yok. CIN_U5 (22 nF) için `anode` düğümünde eleman yok. CBOOT ve CDVDT karşılıksızdır. Kalan 140 referans AÇIK, G3–G9.

## Önerilen takip

Üretim kararı THINKER'ındır. Aday işler: dVdt ve VCAP için veri sayfası hesabı veya alt devre, iki F5 tamamlanmayan köşenin yeniden koşusu, T-032 G2 eşlemesi. Bu kart yalnız kapsamı kaydeder.
