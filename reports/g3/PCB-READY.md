# G3 — PCB-HAZIR kapısı

Dal `wp/g3-pcb-ready`. Kanıt etiketleri: HESAP / DATASHEET / SİM / VARSAYIM / AÇIK. Simülasyon fiziksel kanıt değildir.

## Sonuç: **PCB-HAZIR (koşullu)**

KiCad aktarımına geçilebilir: mimari tek seçimli, değerler/ağlar/footprint kaynakları ve yönlendirme kuralları tam. Koşullar (aşağıdaki AÇIK maddeler) KiCad yerleşimini engellemez ama **tasarım kabulünü** engeller: bobin doyumu (N1), yığılmış tolerans köşeleri, LM70880 termali, MPN'siz 43 BOM satırı ve hiçbir fiziksel ölçüm yapılmamış olması.

| # | Madde | Kriter | Sonuç | Kanıt |
|---|---|---|---|---|
| 1 | Test/baseline | pytest tam; `run_all.py` tek komut exit 0; baseline ERC/DRC/ngspice kayıtlı | **GEÇTİ** — 95 passed; run_all 7/7 exit 0 (4 dk 15 s); ERC 0, DRC 197 bağlantısız/228 uyarı/73 parite; ngspice O1 16.890 V = Linux 16.89 V | [`reports/g2/VERIFY.md`](../g2/VERIFY.md), [`baseline/`](baseline/), [`AUDIT.md`](AUDIT.md) §1 |
| 2a | Koruma mimarisi | tek seçim + yedek, MPN'ler datasheet'ten | **GEÇTİ** — TLV3601DCKR + REF5025AQDRQ1 + SN74LVC1G74DCUR → LM74502HDDFR → CSD19531Q5A; yedek LTC7001 zinciri | [`PROTECTION-DECISION.md`](../g2/PROTECTION-DECISION.md) |
| 2b | O1 ≤12.0 V, U3/U4 IN <30 V | tamamlanmış köşe koşuları | **GEÇTİ (koşullu)** — SİM F1/F5 52 korumalı koşu: O1 ≤11.920 V, VSAFE ≤11.922 V; HESAP 11.941 V. Koşul: gecikmeler datasheet test koşulu dışında; **bobin doyumu modelde yok (L_eff ≤0.4 → 12.019 V)** | [`SIM-RESULTS.md`](../g2/SIM-RESULTS.md), AUDIT N1 |
| 2c | G1 Family 2 ve 4 FAIL'leri | tasarımla kapanmış veya AÇIK + tezgâh yolu | Family 2 (O1 18.80 V): **kapandı (SİM)**, korumasız referans FAIL korunur (19.57 V). Family 4 (10.71 V): **nominal köşelerde kapandı** (8/8, min 10.802 V); **yığılmış statik+transient köşeler AÇIK** (alt 10.64 V; üstte bırakma mandalı set eder) → trim kararı (USER-DECISIONS #3) + BENCH T4 | SİM F1/F3 |
| 3 | DESIGN-RULES | her madde sağlandı/kanıtlı veya AÇIK | **GEÇTİ** — 30 kuralın hepsi durumlu; R02/R08/R14 koşullu, R18 AÇIK; kanıtsız "Evet" yok | [`DESIGN-RULES.md`](../g2/DESIGN-RULES.md) kapanış tablosu |
| 4 | BOM-v2 | tüm satırlar işli; MPN'siz sayı/gerekçe; kritik parçalar MPN'li ve derating geçmiş | **KISMEN** — 114 satır, 71 MPN'li, 43 AÇIK (37 MLCC, F1, D1 TVS, J1–J3, SW1) gerekçeli. Kritik parçalardan L1/L2, RS1/2, Q1, Q2, U1–U10 MPN'li ve derating geçti; **F1, TVS, konnektörler MPN'siz** (üretici datasheet'ine erişim yok). U5/U6/U10 abs-max'ın %82–89'u (53.3 V TVS VARSAYIMI) | [`bom-v2.csv`](../../design/bom-v2.csv), [`BOM-OPEN.md`](../g2/BOM-OPEN.md) |
| 5 | KICAD-CHANGE-LIST-FINAL | eski→yeni ref/ağ/footprint; footprint kaynağı veya "özel footprint"; TP/enjeksiyon/DNP | **GEÇTİ** — değişen 16, eklenen ~40 ref; U3/U4 L varyantı, BIAS→VSAFE, R_INJ düşük Z tarafında; footprint kaynağı her satırda (KiCad lib + doğrulanacak TI land / repo özel land); TP, J_OVP_INJ_BUS, JP_EN_BUCK, DNP listesi | [`KICAD-CHANGE-LIST-FINAL.md`](../g2/KICAD-CHANGE-LIST-FINAL.md), [`pdu_v2_spec.yaml`](../../design/pdu_v2_spec.yaml) |
| 6 | PCB-HANDOFF | 4 katman gerekçeli, stackup, netclass/via (calculate_routing_rules güncel), döngüler, gruplar, termal, konnektör, boyut, DFM | **GEÇTİ** — 4L/1 oz; seçilen genişlikler 2.6–5.5 mm, via 9–19; `calculate_routing_rules.py` G2 planını okuyor ve kontrolleri geçiyor | [`PCB-HANDOFF.md`](../g2/PCB-HANDOFF.md), [`routing-width-calculations.json`](../../hardware/routing-width-calculations.json) |
| 7 | BENCH-ACCEPTANCE | T0–T6 güncel sayılar, ekipman, durdurma, enjeksiyon | **GEÇTİ** — G3 sayılarıyla güncellendi (eşik 11.259–11.537 V, gecikme ≤1.048 µs, F4 0.133 V, bobin doyumu notu) | [`BENCH-ACCEPTANCE.md`](../g2/BENCH-ACCEPTANCE.md) |
| 8 | KiCad dosyası değişmedi | `git diff --name-only a1dbeeb..HEAD \| grep -i kicad` boş | **GEÇTİ (not ile)** — `.kicad_*` dosyası yok; `-i` ile eşleşen yalnız iki belge adı: `reports/g1/KICAD-CHANGE-LIST.md`, `reports/g2/KICAD-CHANGE-LIST-FINAL.md`. Kesin kontrol: `git diff --name-only a1dbeeb..HEAD \| grep '\.kicad_'` boş | git |
| 9 | Repo temiz | START-HERE ≤1 sayfa, giriş ≤15k token, arşiv INDEX+manifest, satır sonları | **GEÇTİ** — START-HERE 37 satır; paket ≈3.9k token; aktif dosya −%69; manifest 880 dosya doğrulandı; CRLF yalnız bilinçli `-text` kanıt dosyalarında | [`CLEANUP.md`](CLEANUP.md), [`archive/INDEX.md`](../../archive/INDEX.md) |
| 10 | Fiziksel kabul listesi ve USER-DECISIONS | güncel; ≤8 madde | **GEÇTİ** — aşağıda; USER-DECISIONS 8 madde | [`USER-DECISIONS.md`](USER-DECISIONS.md) |

## Fiziksel kabul olmadan kapanmayanlar

1. O1 ≤12.0 V gerçek hata enjeksiyonu (T5c) — gerçek bobin L(I) doyumu dahil (N1).
2. Kapanma süresi: karşılaştırıcı (VCM 2.53 V, düşük overdrive) ve LM74502H'nin gerçek CSD19531Q5A yükündeki gecikmesi (T5b).
3. Q2 µs ölçeğinde SOA / kapanma enerjisi (modelde ideal anahtar).
4. Döngü FRA: PM ≥45°, GM ≥6 dB (model belirsizliği: COMP iç ölçeği, gm maks VARSAYIM) (T3).
5. Yük adımı bara ≥10.78 V — nominal marj 22 mV; yığılmış köşeler (T4) ve bırakmada mandallanmama.
6. LM70880 termal (85 °C'de tahmini Tj 137.7 °C, %92 verim VARSAYIMI) ve kart ısınması (T4).
7. eFuse aktif sınırlayıcı davranışı, S2E izolasyonu, OUT−IN ≤0.3 V (D_REV tipik Vf/kaçak) (T6).
8. UVLO düşüş eşiği (yalnız tipik histerezis), ray kaybı kapanma süreleri (tipik) (T2/T5e).
9. Hot-plug VIN tepe / TVS clamp (TVS datasheet doğrulanamadı), F1 kesme koordinasyonu.
10. Artık tek-nokta arızaları: R_OVT açık devre (SİM O1 13.98 V), Q2 D-S kısa.
11. Footprint/land kabulü: LM70880 RRX, TPS25982 RGE, BSC160 TDSON, C5750 2220 özel land'leri; U6/U7/U9/U10/Q2 KiCad kütüphane land'inin TI önerisiyle karşılaştırılması.

## KiCad fazına girdi sırası

`KICAD-CHANGE-LIST-FINAL.md` → şema (`pdu_v2_spec.yaml` ağ eşliği) → `PCB-HANDOFF.md` netclass/yerleşim → ERC/DRC (`reports/g3/baseline` ile karşılaştır) → BOM-OPEN satırları için MPN kararı.
