# WP2 2026-10-25-uvlo – Modeller ve sınıfları

Simülatör: **ngspice-44.2** (`-D ngbehavior=ltpsa`). **LTspice: bulut ortamında çalıştırılmadı.** Sözdizimi LTspice ile uyumlu olacak şekilde yazıldı ama LTspice'ta doğrulanmadı.
Model sınıfları:
- **D**: üretici SPICE modeli (bu pakette **yok**)
- **B**: datasheet tabanlı davranışsal model (G/T değerleri parametre olarak verilir)
- **K**: türetilmiş/ortalama model (mühendislik yaklaşıklığı)
- **İ**: ideal/varsayım
Hiçbir model TI, Panasonic veya Diodes tarafından sağlanmış değildir.

## 1. Dosyalar
| Dosya | İçerik |
|---|---|
| `simulation/proposals/2026-10-25-uvlo/pdu-uvlo-behavioral.lib` | UVLO_BUCK, UVLO_CMP, UVLO_TMUX1102, UVLO_LIPO |
| `pdu-uvlo-block.inc` | C3 bloğu (U20A/B, U21 ve pasifler) |
| `pdu-circuit-uvlo.inc` | WP1 rev3 devresinden türetildi. Değişen tek şey: XU1/XU2 → UVLO_BUCK, RUV1 DNP |
| `pdu-circuit-uvlo-baseline.inc` | Regresyon: RUV1 180k / RUV2 10k korunur |
| `pdu-o1ovp-block-uvlo.inc` | WP1 OVP bloğunun kopyası. Tek değişiklik: VLDO = {V5_P} (TPS7A16 ±%2 köşesi). OVP hibriti **değişmedi** |
| `gen_uvlo.py` / `run_uvlo.py` / `verify_uvlo.py` | Deck üretimi (52 deck), paralel koşu, bağımsız doğrulayıcı |
| `uvlo_budget.py` | Analitik bütçe. SPICE köşeleri bütçenin uç köşeleridir, uydurulmuş değer yoktur |

## 2. Eleman bazında sınıf
| Eleman | Model | Sınıf | Kaynak ve sınırlamalar |
|---|---|---|---|
| U1/U2 LM70880 | UVLO_BUCK (PDU_BUCK türevi, ortalama döngü) | K | EN yükselen VENR 0,95/1,0/1,05 V (G, SNVSBX7A s.6). Düşen eşik VENR − 0,1 V (T). VCC UVLO 4,5/4,0 V (V). tSS 1,9/2,8/4,4 ms (G, s.8). Devre dışıyken SW tri-state + gövde diyotları. COMP kenetleme 0–5 V (V, §3). Kayıp, deck'te ayrı bir kaynaktır (η = 0,88, V) |
| U20 TLV3202 (A, B) | UVLO_CMP | B | VIO/Hint köşeleri, VOH düşümü ≤ 170 mV, VOL ≤ 225 mV, IIB (G, SBOS561C s.5). Rout 10 Ω (V). VCC < 2,7 V iken çıkış DÜŞÜK (V → B-U4). Yayılım gecikmesi yok (40 ns ≪ zaman sabitleri) |
| U22 TMUX1102 (EN kapısı) | UVLO_TMUX1102 | B | U21 ile aynı model. **Anahtarlama gecikmesi (tON/tOFF) modellenmedi** (anlık, V); ns mertebesinde olduğu, CFU gecikmesinin (~0,26 ms) yanında ihmal edilebilir olduğu varsayıldı. Tezgâh B-U15 |
| U21 TMUX1102 | UVLO_TMUX1102 | B | RON 1,8 tipik / 4,9 Ω maks (G, SCDS410D s.5). Mantık eşiği 1,18 V ± 0,1 V (VIL 0,87 / VIH 1,49 V, G). VDD < 1,08 V iken KAPALI (V). Kaçak, düğüm akımı köşesinde |
| DTT 1N4148WS | jenerik diyot .model + Bilkd kaçak kaynağı | İ/B | Is/N/Rs jenerik (V). Kaçak ≤ 30 µA köşesi (G üst sınır, DS30097 Rev.27) |
| CTT 10 µF X7R | ideal C, köşe değeri | İ + G/V | +%26,5 / −%49 (BUDGET §2) |
| Pil 6S + kablo | UVLO_LIPO: R0 + R1‖C1 + Lcab + Rcab | İ/V | R0 0,100, R1 0,050 Ω, τ 20 ms (gerçek ~10 s; pencereye sığması için **hızlandırıldı**, bu muhafazakâr tarafta kalır). Lcab 1 µH. Rcab 0,074 Ω (R_total 0,25 = R0 0,100 + R1 0,050 + Rcab 0,074 + kart 0,026 [R_F1 + Q1 modeli]) |
| U10 TPS48000, U11 TPS7A1650, U12 REF35409, U13 TLV3601, Q FET'ler | WP1 modelleri (`../2026-10-25-o1-ovp/`) | B/K | WP1 MODELS.md. **TDRV_EN yeniden kurma gecikmesi modelde yok** (§4) |
| Yükler, eFuse'lar (U3/U4) | baseline `pdu-behavioral.lib` | K | baseline ile aynı |

## 3. Model düzeltmesi: COMP windup (2026-10-25)
**Bulgu.** Davranışsal PDU_BUCK'ta COMP düğümünde yalnızca Roa 64 MΩ vardı, kenetleme yoktu. dip0v-300us deck'inde buck, RAW ayar noktasının üstündeyken yeniden etkinleşti. COMP, CCOMP 4,7 nF üzerinde yaklaşık −1 kV'a sarıldı. Toparlanma sırasında buck ~12 ms ölü kaldı, ardından RAW 16,7 V'a aştı ve OVP döngüleri oluştu.
**Değerlendirme.** Bir gm hata yükselticisinin çıkışı kendi besleme raylarını aşamaz. Bu bir **model artefaktıdır**, silikon davranışı değildir.
**Düzeltme.** `Bclamp P15 P17 I={MAIN}*(max(V(P15,P17)-5,0)+min(V(P15,P17),0))*10` ile COMP 0–5 V aralığına kenetlendi (V: LM70880 COMP kenet seviyeleri datasheet'ten alınmadı).
Sonuç (typ köşesi, ön koşu): POST penceresinde regülasyon var, RAW 10,996 V, VGS 11,6 V.
**Hiçbir sınır veya kontrol değiştirilmedi.** Gerçek kenetleme davranışı B-U9 tezgâh testiyle doğrulanmalıdır.

## 4. Modelin kapsamadığı ve bilinen riskler
- **TPS48000 TDRV_EN yeniden kurma:** Davranışsal U10, EN/UVLO tekrar yükseldiğinde FET'i yalnızca TDON ile açar. Gerçek parça her yeniden etkinleşmede ~50 ms (TDRV_EN) beklerse, kısa bir dip sonrasında buck (kısmen boşalmış zamanlayıcı, ~30 ms) FET'ten **önce** başlayabilir. Bu P0-03 riskidir; bkz. RESULTS ve BENCH-TEST B-U10.
- **U10 UVLO'su VIN'den gelir.** VIN çöktüğünde FET kapanır ve yük kopar, bu da RAW aşımına yol açar (simülasyonda 12,87 V; OVP bunu doğru şekilde keser).
- Anahtarlama dalgalanması yoktur (ortalama model). MARGIN_DYN 0,10 V bu payı varsayım olarak taşır.
- TLV3202'nin 0–2,7 V besleme bölgesindeki davranışı tanımsızdır (V → B-U4).
- REF35 lehim kayması 0 kabul edildi (V → B-U7).
