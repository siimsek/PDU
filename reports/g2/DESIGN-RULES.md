# G2 zorunlu tasarım kuralları kataloğu

Kaynak: G1'deki 8 inceleme turu (`reports/g1/PR2-REVIEW-*.md`), G1 kapanış kararı ve üretici datasheet'leri. Her kural yeni tasarımda **baştan** sağlanır. Etiketler: HESAP / DATASHEET(sayfa) / SİM / VARSAYIM / AÇIK. "Sağlandı" sütunu tasarımın kuralı nasıl karşıladığını, "Durum" sütunu kanıt düzeyini verir. SİM fiziksel kanıt değildir.

Kısaltmalar: `VRAW` = buck COUT ortak barası; `VSAFE` = ayırıcı sonrası, U3/U4 IN düğümü; `Q_ISO` = ortak bara seri MOSFET; `U_DRV` = LM74502H; `U_CMP` = TLV3601; `U_LAT` = SN74LVC1G74; `U_REF` = REF5025A-Q1; `U_LDO5` = TPS7A1650-Q1.

## A. Koruma mimarisi ve eşik

| ID | Zorunlu kural | Kaynak | Nasıl sağlandı (G2) | Durum |
|---|---|---|---|---|
| R01 | Ayırıcı, U3/U4 IN pinlerinin **önünde** olmalı; ortak bara hatasında U3/U4 IN <30 V abs-max (hedef ≤24 V önerilen). | G1 kapanış; `shared-bus-ovp-results.json` 40.709 V; TPS25982 DATASHEET Rev D p.7 | `Q_ISO` VRAW→VSAFE arasında; U3/U4 IN yalnız VSAFE'e bağlı. | SİM (Aile 1), fiziksel AÇIK |
| R02 | O1 anlık tepe ≤12.0 V her durumda: `trip_max + overdrive + dV/dt·t_off,max + parazitik ≤ 12.0 V`. | Kullanıcı şartı; REQUIREMENTS.md | Aşama 2 bütçe hesabı (`analysis/g2/protection.py`), Aile 1 ve 5. | HESAP+SİM; fiziksel AÇIK |
| R03 | Trip alt köşesi normal çalışmadaki en yüksek baranın üstünde olmalı (yanlış mandallanma yok): `trip_min ≥ 11.22 V transient bandı + 30 mV gürültü payı`. | REQUIREMENTS çelişki notu 2 (11.22 V transient üst bandı); mandallı politika | Eşik bölücüsü bu alt sınıra göre seçildi; yük bırakma aşımı Aile 3'te bu değerin altında tutulur. | HESAP+SİM |
| R04 | Yalnız **maksimum** (garantili) gecikme kullanılır; test koşulu (overdrive, VCM, yük kapasitesi) yazılır. Tipik değer kanıt değildir. | 6694409747 (TLV1701 yalnız tipik), 6683120653 | TLV3601 4.5 ns max (50 mV OD, VCM=VEE+0.3 V) ve LM74502H tOVP_OFF 1 µs max (C_GS=4.7 nF) koşullarıyla bütçe; koşul dışı kısımlar "koşullu" işaretli. | DATASHEET (koşullu) |
| R05 | Karşılaştırıcı giriş ortak modu: eşik geçişi anında VCM önerilen aralıkta olmalı; aralık dışına çıkan fault'ta karşılaştırıcı çıkışına güvenilmez, koruma bağımsız bir yolla tutulmalı. | 6692033623 §1, 6694409747 | Trip anında VCM ≈2.5 V (aralık −0.2…5.2 V). VRAW > ~23.9 V'ta giriş aralık dışı; bu bölgeyi `U_DRV` OV pinindeki **bağımsız kaba OV bölücüsü** kapatır (VS-beslemeli, mantık rayından bağımsız). Mandal bir kez set olunca karşılaştırıcı çıkışı önemsizdir. | HESAP; fiziksel AÇIK |
| R06 | Karşılaştırıcı giriş clamp akımı VCC=0 ve VRAW=53.3 V (TVS clamp) köşesinde ≤10 mA. | TLV3601 DATASHEET Rev E p.5 dipnot; 6692033623 | Bölücü Thevenin direnci ≥1.9 kΩ; hesap tüm köşelerde. | HESAP |
| R07 | Clamp üzerinden 5 V rayına geri besleme rayı belirsiz bölgeye taşımamalı. | 6692033623 §3 | 5 V rayında bleeder; ray LDO'suz iken denge gerilimi hesabı. | HESAP |
| R08 | Mandal VCC <1.65 V'ta durum belirsiz → mandal durumuna güvenilmez; mantık rayı geçerli olana kadar kapı **bağımsız yolla** kapalı tutulur. | SN74LVC1G74 DATASHEET Rev G p.4; 6692825552 §2 | `U_DRV` EN/UVLO pini 5 V rayından bölücüyle beslenir: 5 V rayı ≥3.3 V olmadan kapı açılamaz; ray 2.57–3.09 V altına inerse kapı kapanır. | DATASHEET+HESAP |
| R09 | PRE ve CLR aynı anda aktifse çıkış güvenli (KAPALI) yönde olmalı. | SN74LVC1G74 fonksiyon tablosu (PRE=L,CLR=L → Q=H, Q̄=H) | Trip = PRE (Q=H → OV pini yüksek → kapı kapalı). Reset/POR = CLR. Çakışmada Q=H → KAPALI. | DATASHEET |
| R10 | Açılışta mandal belirli şekilde temizlenmeli; açılışta hata varsa ayırıcı kapalı kalmalı. | 6692825552 §2; 6693550928 | POR RC + LDO PG → CLR. Karşılaştırıcı 2.1 V POR altında çıkışı LOW tutar → PRE aktif → Q=H (KAPALI). | DATASHEET+HESAP |
| R11 | Reset yalnız güç döngüsü veya manuel buton; otomatik yeniden deneme yok; hata sürerken reset etkisiz. | Kullanıcı varsayılanı; 6692825552 §2 | Buton CLR'yi çeker; PRE aktifken Q=H kalır (R09). | DATASHEET |
| R12 | Sürücü/mantık beslemesi kaybında **aktif** hızlı kapı boşaltma yolu olmalı; yalnız pasif G-S direnci yetmez. | 6693550928 (10 kΩ pasif: 238.779 µs **FAIL**) | `U_DRV` EN düşüşünde iç deşarj anahtarı (RDSON 0.4–2 Ω, DATASHEET p.5); VS kaybında kapı yükü kaynak tarafına boşalır + G-S direnci. Gecikme (tUVLO_OFF) yalnız tipik 2 µs → koşullu. | DATASHEET (tipik) → tezgâh |
| R13 | Her FET'te bağımsız G-S boşaltma direnci. | 6692825552 | `R_GS` 100 kΩ (Q_ISO G-S). | Tasarımda |
| R14 | Kapı sürücüsü maks kapanma gecikmesi **gerçek kapı yükünde** geçerli olmalı. | 6694409747 (LTC7001 70 ns yalnız 1 nF) | LM74502H koşulu C_GS=4.7 nF; seçilen CSD19531Q5A Ciss max 3.87 nF, Qg(10 V) max 48 nC. Eşdeğerlik sınırda → **koşullu garanti, tezgâh ölçümüyle kabul**. | DATASHEET (koşullu) |
| R15 | Ayırıcı FET VDS ≥ VRAW maks (TVS clamp 53.3 V) + pay; VGS sınırı; kapanma enerjisi SOA/çığ sınırı içinde. | 6683120653; CSD19536 SOA 100 µs | CSD19531Q5A 100 V, ±20 V; kapanma enerjisi hesabı tek darbe çığ enerjisiyle (180 mJ, DATASHEET p.1) karşılaştırılır. | HESAP; SOA fiziksel AÇIK |

## B. eFuse ve güç yolu

| ID | Zorunlu kural | Kaynak | Nasıl sağlandı (G2) | Durum |
|---|---|---|---|---|
| R16 | eFuse OUT ≤ min(30 V, VIN+0.3 V) abs-max her durumda (ayırıcı açılınca, giriş kaybında). | TPS25982 DATASHEET Rev D p.6; 6693550928 (OUT−IN 10.997 V) | VSAFE'e bleeder; her eFuse'ta OUT→IN Schottky (`D_REV1/2`); ayırıcı yalnız OV'de açılır (giriş kaybında açılmaz). Schottky Vf ≤0.3 V yalnız düşük akımda tipik → **koşullu**. | HESAP+SİM (Aile 4); fiziksel AÇIK |
| R17 | ILIM yalnız datasheet'in garanti verdiği tablo noktalarından seçilir; ara değer interpolasyonu garanti sayılmaz. O1+S2E garantili-min toplam ≥7.5 A. | TPS25982 DATASHEET p.9 tablosu; 6681813880 (7.4877 A FAIL) | RILIM_O1=182 Ω (7.23–9.07 A), RILIM_S2E=300 Ω (4.36–5.66 A). | DATASHEET+HESAP |
| R18 | Konnektör sürekli akımı üretici derating'i içinde; kontak/kablo eşleşik set. | G1 KICAD-CHANGE-LIST (Micro-Fit W-W 7 A) | Molex PS bu turda okunamadı → **doğrulanamadı**; seçim AÇIK. | AÇIK |
| R19 | eFuse EN/UVLO ve PG bölücüleri VSAFE'ten beslenir (ayırıcı açıkken eFuse'lar da kapanır). | G1 kapanış | REN1/REN2 VSAFE'e. | Tasarımda |

## C. Algılama, ray ve termal

| ID | Zorunlu kural | Kaynak | Nasıl sağlandı (G2) | Durum |
|---|---|---|---|---|
| R20 | Hata bölücüsündeki direnç gücü sürekli hata gerilimine göre ≤%50 nominal. | 6692033623 §2 | Bölücü direnç gücü 26 V sürekli ve 53.3 V geçici için hesaplanır; paket buna göre. | HESAP |
| R21 | Mantık/koruma LDO'su sürekli hata gerilimi görmemeli (termal). | 6692825552 §4 (40.709 V'ta Tj 130.49 °C) | `U_LDO5` girişi VIN (Q1 sonrası, 20–26 V), VRAW değil. | HESAP |
| R22 | TPS7A16 PG yalnız VIN ≥3 V'ta geçerli; düşük VIN güvenliği PG'ye bırakılmaz. | TPS7A16-Q1 DATASHEET Rev E p.6 | Kapı kapatma yolu R08'deki EN bölücüsüdür; PG yalnız CLR açılış zamanlaması için. | DATASHEET |
| R23 | Bölücü/referans tek arızasında güvenli durum analiz edilir; tek açık direnç tüm OV korumasını kaldırmamalı. | 6692825552, kullanıcı G2 talimatı | Referans kaybı → karşılaştırıcı LOW → trip (güvenli). Alt direnç açık → trip (güvenli). Üst direnç açık → hassas yol kör; **kaba OV yolu** VSAFE'i ≤12.77 V'ta keser (U3/U4 korunur, O1 12 V garantisi yok) → artık risk, AÇIK. | HESAP |
| R24 | Algılama VRAW (ayırıcı öncesi) üzerinde; ayırıcı açıldıktan sonra hata sürdükçe mandal tutar. | 6683120653 deck | U_CMP bölücüsü VRAW'da. | Tasarımda |

## D. Güç katı, döngü ve doğrulama

| ID | Zorunlu kural | Kaynak | Nasıl sağlandı (G2) | Durum |
|---|---|---|---|---|
| R25 | Bootstrap: LM70880 CBOOT=47 nF (VCC=8 V seçilirse 1 Ω seri); ayrık sürücü kullanılırsa sürücünün CB eşitsizliği (LTC7001: CB > 306 nF + 10·CG). | LM70880 DATASHEET p.4 pin tablosu; 6694409747 LTC7001 bootstrap | LM70880 CBOOT 47 nF + RBOOT 1 Ω korunur. Seçilen koruma zincirinde ayrık bootstrap yok (LM74502H iç şarj pompası, VCAP 0.1 µF DATASHEET p.4). | DATASHEET |
| R26 | Yük adımı 0.75→7 A ve geri: bara min ≥10.78 V; aşım R03 eşiğinin altında. Kriter gevşetilmez. | G1 Family 4 10.7109 V **FAIL** | Ceff artırımı + COMP yeniden seçimi (Aşama 4), Aile 3. | SİM; fiziksel AÇIK |
| R27 | Döngü PM ≥45°, GM ≥6 dB tüm Ceff/L/gm/VIN/yük köşelerinde; model belirsizliği PM'den pay olarak düşülür. | G1 BENCH T3 | Analitik + SPICE AC (Aşama 4). | HESAP+SİM; FRA şart |
| R28 | Her hesap iki yolla; fark raporlu; birimli; pytest'li. | Kullanıcı G2 kuralı; 6681813880 P1 | `analysis/g2/*` her sonuçta `path_a`, `path_b`, `diff`. | HESAP |
| R29 | Tamamlanmayan simülasyon PASS sayılmaz; FAIL silinmez; ilk/son deneme ve hash saklanır. | G1-R2-04, 6693550928 | `analysis/g2/sim_runner.py` completed bayrağı + SHA256. | Tasarımda |
| R30 | Tezgâh enjeksiyonu için erişim: VRAW enjeksiyon padi, VSAFE/O1/S2E/GATE test noktaları; enjeksiyon akım sınırlı fixture ile. | G1 KICAD-CHANGE-LIST | KICAD-CHANGE-LIST-FINAL test noktaları. | Tasarımda |

## Kapanış durumu (Aşama 6)

| ID | Sağlandı? | Kanıt | AÇIK kalan |
|---|---|---|---|
| R01 | Evet | SİM F1/F5: VSAFE ≤11.915 V (korumasız referans 33.0 V FAIL) | fiziksel T5c |
| R02 | Evet (model/hesap) | HESAP 11.935 V, SİM F1 11.912 V, F5 maks 11.912 V | tezgâh T5b/T5c; ölçüm belirsizliği (USER-DECISIONS #2) |
| R03 | Kısmen | trip_min 11.2649 V (bant + 44.9 mV); SİM F3 nominal bırakma ≤11.19 V | yığılmış üst köşe bırakma 11.35 V > trip_min (F3 FAIL) → trim/kullanıcı kararı |
| R04 | Evet (koşullu) | DATASHEET maks değerler ve koşulları `params.py`'de | VCM/overdrive ve 4.7 nF eşdeğerliği tezgâhta |
| R05 | Evet | HESAP: VCM aralık dışı VRAW>23.24 V; kaba OV ≤13.70 V | — |
| R06 | Evet | HESAP 6.29 / 6.47 mA < 10 mA | — |
| R07 | Kısmen | HESAP: 1 kΩ bleeder ile 26 V'ta ray 1.92 V | ≥40 V hata + LDO yokken ray 3.1–4.1 V; kaba OV yoluna güvenilir |
| R08 | Evet | HESAP EN kapama 2.57–3.16 V > 2.1 V POR > 1.65 V | — |
| R09 | Evet | DATASHEET fonksiyon tablosu | — |
| R10 | Evet | POR RC 120 ms + PG; karşılaştırıcı POR LOW | tezgâh T1/T5e |
| R11 | Evet | DATASHEET | tezgâh T5f |
| R12 | Kısmen | LM74502H EN deşarjı (RDSON 0.4–2 Ω) | tUVLO_OFF yalnız tipik 2 µs → T5e |
| R13 | Evet | R_GS 100 kΩ (BOM) | — |
| R14 | Koşullu | Qg oranı 0.97 (gerçek ≤ test yükü) | tezgâh T5b |
| R15 | Kısmen | VDS payı 46.7 V; enerji oranı 0.0022 × EAS | SOA µs grafiği okunamadı |
| R16 | Evet (model) | SİM F4: D_REV ile OUT−IN 0.133 V; D_REV'siz 0.777 V FAIL | Schottky Vf tipik; T6b |
| R17 | Evet | DATASHEET p.9 tablo noktaları; toplam min 11.59 A | — |
| R18 | Hayır | — | Molex PS okunamadı → AÇIK |
| R19 | Evet | KICAD-CHANGE-LIST-FINAL (REN1 → VSAFE) | — |
| R20 | Evet | R_OVT 26 V'ta %20 (geçici 53.3 V'ta %84, kısa süreli) | — |
| R21 | Evet | U10 IN = VIN | termal VIN 26 V: 0.34 W |
| R22 | Evet | Kapı kapatma EN bölücüsüyle | — |
| R23 | Kısmen | Referans/alt direnç arızası güvenli | R_OVT açık: SİM O1 13.94 V (artık risk), Q2 D-S kısa (tek nokta) |
| R24 | Evet | Bölücü VRAW'da | — |
| R25 | Evet | CBOOT 47 nF + 1 Ω; LM74502H VCAP 100 nF | — |
| R26 | Kısmen | SİM F3 nominal 6/6 PASS (min 10.81 V) — G1 Family 4 FAIL nominal köşede kapandı | yığılmış alt köşe min 10.64 V FAIL → trim/kullanıcı kararı |
| R27 | Evet (model) | 432 köşe PM 66.9° (−10° → 56.9°), GM 11.7 dB; ngspice AC <0.001° | tezgâh FRA T3 |
| R28 | Evet | her modülde path A/B + fark; 91 pytest | bağımsız fiziksel ikinci yol yok |
| R29 | Evet | sim-results.json completed/SHA256, `-attemptN` | — |
| R30 | Evet | KICAD-CHANGE-LIST-FINAL §3 | — |
