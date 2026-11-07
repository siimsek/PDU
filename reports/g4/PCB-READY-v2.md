# G4 — PCB-HAZIR kapısı v2

Dal `wp/g4-closure`. Etiketler: HESAP / DATASHEET / SİM / VARSAYIM / AÇIK. Simülasyon fiziksel kanıt değildir. G3 kapısı: [`reports/g3/PCB-READY.md`](../g3/PCB-READY.md).

## Sonuç: **PCB-HAZIR (koşullu)**

KiCad aktarımına geçilebilir: G3'ün iki tasarım açığı (N1 bobin doyumu, yığılmış tolerans köşeleri) tasarım değişikliğiyle kapandı, BOM'da MPN'siz tek satır (F1) kaldı, belge zinciri ve tutarlılık denetimi temiz. Koşullar KiCad yerleşimini engellemez ama **tasarım kabulünü** engeller: fiziksel ölçüm yok (T-1, T1b, T5c, T5g başta), F1 datasheet'i yok, INA296 gecikmesi ve 16 A üstü L(I) yalnız tipik/VARSAYIM.

| # | Madde | Kriter | Sonuç | Kanıt |
|---|---|---|---|---|
| 1 | Test/baseline | pytest tam; run_all exit 0; ERC/DRC baseline | **GEÇTİ** — 98 passed (2.3 s); run_all 11/11 adım exit 0 (6 dk 0 s, 76 SPICE koşusu); ERC 0, DRC 228 uyarı / 197 bağlantısız / 73 parite (G3 ile aynı; 301 = 228 + 73, AUDIT2 §1) | [`VERIFY.md`](../g2/VERIFY.md), [`baseline/`](baseline/) |
| 2a | Koruma mimarisi | tek seçim + yedek, MPN datasheet'ten | **GEÇTİ** — G3 zinciri + faz OC tetiği (INA296A2QDGKRQ1 ×2, TLV3601DCKR ×2, SN74LVC1G11DBVR) | [`PROTECTION-DECISION.md`](../g2/PROTECTION-DECISION.md) §0 |
| 2b | O1 ≤12.0 V, U3/U4 IN <30 V | tamamlanmış köşe koşuları | **GEÇTİ (koşullu)** — HESAP ≤11.41 V (L tabanı 0.05'e kadar); SİM F1 ≤11.37 V, F5 48 köşe ≤11.07 V; VSAFE ≤11.37 V; ham bara ≤35.8 V < 60 V. Koşul: INA296 gecikmesi tipik (4× tipikte 11.56 V) | [`SIM-RESULTS.md`](../g2/SIM-RESULTS.md), [`N1-DECISION.md`](N1-DECISION.md) |
| 2c | G1 Family 2 ve 4 FAIL'leri | tasarımla kapanmış veya AÇIK + tezgâh yolu | Family 2: **kapandı** (gerilim + faz OC tetiği; korumasız referans F1 19.35 V FAIL korunur). Family 4: **nominal (10.89–10.93 V) ve trimli (10.79 / 11.20 V) köşelerde kapandı**; trimsiz yığılmış köşeler 10.73 / 11.26 V görünür FAIL → kabul T1b trimi | SİM F1/F3, [`B2-B6.md`](B2-B6.md) §B4 |
| 3 | DESIGN-RULES | her madde durumlu | **GEÇTİ** — R02/R03/R18/R26 G4'te "Evet" (R02 tezgâh koşullu); R14 koşullu; R15, R23 kısmen (Q2 D-S kısa) | [`DESIGN-RULES.md`](../g2/DESIGN-RULES.md) |
| 4 | BOM-v2 | MPN'siz sayı/gerekçe; kritik parçalar MPN'li, derating geçmiş | **GEÇTİ (1 AÇIK)** — 147 satır, 146 MPN'li; tek AÇIK F1 (aday 0456020.ER, DC kesme belgesi okunamadı); derating aşımı 0 | [`bom-v2.csv`](../../design/bom-v2.csv), [`BOM-OPEN.md`](../g2/BOM-OPEN.md) |
| 5 | KICAD-CHANGE-LIST-FINAL | eski→yeni ref/ağ/footprint, TP/DNP | **GEÇTİ** — G4 bölümü (U11–U15, R_OCT/R_OCB, RFB2+R_TRIM, COUT17–32, D1, J2, CEFOUT 1206, BIAS AGND, F1 ağı) | [`KICAD-CHANGE-LIST-FINAL.md`](../g2/KICAD-CHANGE-LIST-FINAL.md) |
| 6 | PCB-HANDOFF | katman, netclass, döngü, termal, konnektör, boyut | **GEÇTİ** — 32× COUT bankası, OC Kelvin yönlendirme, J2 4 devre, 50/40 °C termal, 120 × 85 mm tahmini; routing JSON yeniden üretildi | [`PCB-HANDOFF.md`](../g2/PCB-HANDOFF.md) |
| 7 | BENCH-ACCEPTANCE | güncel sayılar, yeni testler | **GEÇTİ** — T-1 (akım), T1b (trim), T5g (OC eşik/gecikme) eklendi; SİM sütunları G4 | [`BENCH-ACCEPTANCE.md`](../g2/BENCH-ACCEPTANCE.md) |
| 8 | KiCad dosyası değişmedi | `git diff --name-only a1dbeeb..HEAD \| grep -E '\.kicad_(sch\|pcb\|pro\|sym\|mod)$'` boş | **GEÇTİ** — çıktı boş | git |
| 9 | Repo temiz | START-HERE ≤1 sayfa, AGENTS/CLAUDE ≤80 satır, arşiv manifesti | **GEÇTİ** — START-HERE 36, AGENTS 40, CLAUDE 9 satır; manifest 1044 dosya `sha256sum -c` geçti | §Temizlik |
| 10 | USER-DECISIONS | ≤6 madde | **GEÇTİ** — 6 madde | [`USER-DECISIONS.md`](USER-DECISIONS.md) |
| 11 | N1 bobin doyumu (G3 AÇIK) | O1 ≤12.0 V doyumlu L ile | **GEÇTİ (koşullu)** — madde 2b | N1-DECISION |
| 12 | eFuse varyantı | datasheet ile doğrulanmış | **GEÇTİ** — TPS259824LNRGER aktif sınırlayıcı (p.4, p.50) | AUDIT2 §3 |
| 13 | LM70880 BIAS | abs-max ve p.13 koşulu | **GEÇTİ** — AGND | B2-B6 §B3 |
| 14 | Yığılmış tolerans | statik + yük adımı köşeleri kriter içinde | **GEÇTİ (koşullu)** — kart başı trim ile 10.79 / 11.20 V; koşul: VFB toleransının yarısı sıcaklık (VARSAYIM) | B2-B6 §B4 |
| 15 | Tutarlılık | spec ↔ BOM ↔ SPICE, 0 hata | **GEÇTİ** — `check_consistency.py` 0 hata; eski değer grep'i aktif zincirde temiz | [`consistency.json`](consistency.json) |
| 16 | Footprint haritası | her BOM satırı için stok/özel + doğrulama | **GEÇTİ** — 105 stok (KiCad 10 dosyası doğrulandı), 38 özel / 5 paket (F1, Q1, LM70880 RRX, C5750, TPS25982 RGE) | [`footprint-map.csv`](../../design/footprint-map.csv) |
| 17 | Termal (ortam 50/40 °C) | Tj ≤125 °C | **GEÇTİ (koşullu)** — LM70880 105.9 / 95.9 °C EVM bakırıyla; JEDEC bakırında 150.6 °C FAIL → EVM benzeri via/bakır zorunlu; %92 verim VARSAYIM | `power-results.json` `g4_tj_by_ambient_C` |
| 18 | Datasheet kapsamı | kritik parçalar resmi kaynaktan | **KISMEN** — SMCJ33A, Molex, TDK MLCC, INA296, LVC1G11, Omron okundu; **F1 okunamadı**; MLCC DC-bias grafiği okunamadı (Ceff VARSAYIM korunur) | [`datasheet-inputs.md`](datasheet-inputs.md), USER-DECISIONS #3 |

## Fiziksel kabul olmadan kapanmayanlar

1. T-1: O1/S2E gerçek akımı (RILIM ve J2 kararını doğrular).
2. T1b: kart başı trim sonrası VOUT 10.980–11.008 V; T3 FRA (PM ≥45°, GM ≥6 dB; gm maks bilinmiyor).
3. T5c: gerçek bobinle üst anahtar kısa devre emülasyonu, O1 ≤12.0 V; T5g: OC eşiği 12.97–13.60 A ve INA296 gecikmesi ≤4 µs.
4. T5b: karşılaştırıcı + LM74502H gerçek CSD19531Q5A yükünde kapanma süresi.
5. T4: yük adımı (≥10.78 V, bırakma <11.22 V) ve 50 °C eşdeğeri termal.
6. T2: UVLO düşüş eşiği (14.67–18.64 V aralığında, yalnız tipik histerezis).
7. T6: eFuse aktif sınırlayıcı, S2E izolasyonu, OUT−IN ≤0.3 V.
8. F1 DC kesme/I²t koordinasyonu; hot-plug VIN tepe (SİM 42.1 V) ve SMCJ33A kelepçesi.
9. Q2 D-S kısa (tek nokta arızası) ve Q2 µs SOA.
10. Özel footprint land/paste kabulü (5 paket) ve stok land'lerin TI önerisiyle karşılaştırılması.

## Temizlik ve token

| Ölçüm | G3 sonu | G4 sonu | Not |
|---|---:|---:|---|
| İzlenen dosya / aktif (arşiv dışı) | 1209 / 328 | 1408 / 363 | +164 G4 deneme kanıtı arşivde; aktif artış G4 rapor/hesap dosyaları |
| İzlenen / aktif boyut | 37.7 / 3.81 MB | 39.24 / 4.78 MB | aktif artış 32× COUT ve OC koşularının deck/log'ları |
| Ajan giriş paketi (START-HERE + AGENTS + CLAUDE + PCB-HANDOFF) | ≈3.9k token | 14.7k karakter ≈ **4.6k token** | karakter/3.2; hedef ≤15k ✓ |
| pytest | 95 passed, 2.7 s | **98 passed, 2.3 s** | +3 G4 testi |
| run_all | 7 adım, 4 dk 18 s | **11 adım, 6 dk 0 s** | +N1/B4/B5/tutarlılık; SPICE 76 koşu |
| Arşiv manifesti | 880 dosya | **1044 dosya**, `sha256sum -c` geçti | INDEX'e G3/G4 deneme satırı |
| Klon boyutu (`git count-objects -vH`) | — | paket 29.46 MiB | Geçmişte G2 hata ayıklama dökümleri duruyor: `reports/g2/sim/f4/e.txt` 29.0 MB, `f2/d.txt` 10.7 MB (G3'te `git rm`); geçmiş yeniden yazılmadığı için klon küçülmez (yasak: rebase/force push). Gerekirse `git clone --filter=blob:limit=5m` |

## KiCad fazına girdi sırası

`KICAD-CHANGE-LIST-FINAL.md` (G4 bölümü önce) → şema (`pdu_v2_spec.yaml` ağ eşliği, `footprint-map.csv`) → `PCB-HANDOFF.md` netclass/yerleşim → ERC/DRC (`reports/g4/baseline/` ile karşılaştır) → F1 MPN kararı.
