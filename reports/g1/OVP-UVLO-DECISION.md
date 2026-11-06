# O1 OVP ve UVLO mimari kararı

## G1 kapanış kararı (2026-11-07) — geçerli karar

**Bu bölüm, aşağıdaki "Karar (SUPERSEDED)" bölümünün yerini alır.** Eski metin geçmiş kaydı olarak silinmedi.

**Neden değişti:** Eski karar ayırıcıyı O1 dalına, **U3 çıkışından sonra** koyuyordu. [`shared-bus-ovp-results.json`](shared-bus-ovp-results.json) ve [`G1-SUMMARY.md`](G1-SUMMARY.md) ise buck high-side short (ortak bara hatası) sırasında ortak `VOUT`'un **U3/U4 IN pinlerinde 40.709 V** gördüğünü gösteriyor (SİM; >24 V süresi 731.759 µs, >30 V süresi 161.124 µs). TPS25982 IN için 30 V abs-max ve 24 V önerilen max var (DATASHEET, TI Rev D p.7). U3'ten sonra konan ayırıcı U3/U4'ün kendi IN pinini korumaz. Bu nedenle "U3 sonrası O1 ayırıcı" tek başına geçersizdir.

### Üç mimari, tek tablo

| Ölçüt | (a) Ortak bara seri ayırıcı (OVP kontrolcülü), COUT ile U3/U4 IN ayrımı arasında | (b) Giriş tarafında kenetleme / surge-stopper tipi tek IC | (c) O1'e özel ayırıcı + U3/U4 için ayrı koruma |
|---|---|---|---|
| U3/U4 IN ≤30 V (ortak bara hatası) | **SİM:** IN tepesi 11.6217–11.6273 V; >24 V ve >30 V süresi 0 ([family2-common-bus-isolator-*](sim/)). | **Doğrulanamadı.** Repo'da yalnız TPS1686x okunmuş, o da port başına HV eFuse olarak; ortak barada tek surge-stopper IC için üretici datasheet'i bu turda okunmadı, MPN önerilmez. TPS1686x ekranında ham IN 39.389 V'u 92 V abs-max içinde taşır (SİM/DATASHEET). | O1 dalındaki ayırıcı U3'ten sonra ise **FAIL**: aynı model 40.709 V. Koruma ancak ayrı bir ön-eFuse anahtarı eklenirse sağlanır; bu durumda U3/U4 önündeki kısım fiilen (a) ya da port başına (a) kopyası olur. |
| O1 ≤12.0 V | **SİM:** 11.5550–11.5606 V (ideal anahtar, ESR/ESL yok). Eşik köşesi 11.3281–11.6232 V (HESAP). | **Uyumsuz:** TPS1686 OVLO toleransı 11.1605–12.0 V penceresine sığmaz; alt köşe ≥11.1605 V iken üst köşe en az 12.0654 V (HESAP). tOVP min 3 µs, max yok (DATASHEET). Doğrusal kenetleme tipi için doğrulanamadı. | **SİM:** O1 dalı ayırıcısı ile O1 11.6900 / 11.6857 V. U3/U4 IN sorunu çözülmeden anlamı yok. |
| S2E | Ortak trip'te S2E de kapanır (fail-off). SİM S2E tepesi 11.5896–11.6080 V. | TPS1686 ekranında S2E 25.6365 V (S2E 9–28 V çalışma aralığında). | O1 trip'inde S2E çalışmaya devam edebilir; S2E için ayrı eşik/zincir gerekir. |
| Tezgâhta test edilebilirlik | **İyi.** Tek enjeksiyon noktası (`TP_VOUT_RAW` → `VOUT_PROT`) iki portu birlikte doğrular; tek eşik, tek latch/reset, tek gecikme ölçümü. | Basit (tek IC). Ancak 12 V penceresi datasheet toleransıyla kapanmadığı için tezgâhta geçen bir örnek parça tasarım kabulü sayılmaz. | **Zayıf.** İki ayrı zincir, iki eşik, iki reset; hem U3 öncesi hem O1 sonrası enjeksiyon ve birleşik hata testleri gerekir. |
| Parça sayısı (kontrol zinciri) | **1 takım:** TLV3601DCKR + REF5025AQDRQ1 + SN74LVC1G74DCUR + LTC7001EMSE#PBF + 2×CSD19536KTTT + TPS7A1601QDGNRQ1/TPS7A1650QDGNRQ1 + bölücü (aday MPN'ler [`OVP-ENGINEERING-RESULT.md`](OVP-ENGINEERING-RESULT.md); stok doğrulanmadı). | En az (1 IC + FET/pasif) — ama ortak bara için MPN doğrulanamadı. TPS1686x ×2 seçilirse 6×5 mm VQFN, mevcut TPS25982 footprint'ine uymaz. | **2 takım** (yaklaşık iki kat comparator/referans/latch/sürücü/FET). |
| Mevcut hesaplarla çelişki | Yok. Eşik 11.3281–11.6232 V aynı bölücü/referans hesabı; ideal Ceff ekranı 6.48 µF (7.5 A) / 8.56 µF (9.91 A model branch peak). 11.46 V eski hedefin 163.2 mV aşıldığı bilgisi aynen geçerli (12.0 V sert sınır değişmez). | **Çelişir:** OVLO pencere hesabı ve tOVP max'ın yokluğu. | U3 sonrası yerleşim, 40.709 V sonucu ile çelişir. |
| Açık kalanlar | Gerçek kapanma süresi, FET SOA (100 µs'den kısa eğri yok), ortak dal akımı (model 9.91 A, ILIM toplamından %32 yüksek), VOUT_PROT Ceff, harici O1 backfeed yolu, latch/LDO fail-safe — hepsi AÇIK. | Datasheet okunmadan değerlendirilemez. | (a)'nın tüm açıkları ×2. |

### Öneri

**(a) Ortak bara seri ayırıcı.** Buck çıkış kapasitörleri (`VOUT_RAW`) ile U3/U4 IN ayrımı (`VOUT_PROT`) arasına tek latch-off, back-to-back seri MOSFET ayırıcı; algılama `VOUT_RAW` üzerinde (model deck'teki gibi); aday kontrol zinciri yukarıdaki tek takım. Bu, ortak bara hatasında hem U3/U4 IN abs-max'ını hem O1 ≤12 V'u modelde aynı anda karşılayan tek adaydır. **Tasarım PASS'i değildir.** Fiziksel kapanma süresi, SOA ve Ceff tezgâhta ölçülmeden O1 ≤12.0 V kabul edilmez.

**Yedek: (c)'nin port başına varyantı.** Ayırıcılar her eFuse'un **önüne** konur: O1 için aynı zincir U3 IN öncesinde, S2E için ayrı eşikli ikinci zincir U4 IN öncesinde. Yedeğe yalnız şu durumlarda geçilir: (1) O1 hatasında S2E'nin kapanması kabul edilmezse (kullanıcı kararı), ya da (2) ortak anahtar tezgâhta ortak dal akımında SOA/ısıl sınırı geçemezse. U3 sonrası O1 ayırıcı hiçbir varyantta tek koruma olarak kullanılmaz.

**(b) elendi:** TPS1686x için OVLO penceresi ve tOVP max eksikliği sayısal olarak uyumsuz; ortak bara surge-stopper IC'si için datasheet doğrulanamadı.

UVLO kararı değişmedi: **RUV1 180 kΩ → 174 kΩ**, RUV2 10 kΩ (aşağıdaki UVLO bölümü).

## Karar (SUPERSEDED — G1 kapanış kararıyla geçersiz; U3/U4 IN 40.709 V bulgusundan önce yazıldı)

**SUPERSEDED öneri (aday mimari):** O1 çıkışında, TPS259824O'dan sonra çalışan bağımsız hızlı comparator + referans + set-dominant latch + seri back-to-back MOSFET disconnect. OVP eşiği nominal 11.35 V, tüm toleranslarda en çok 11.46 V hedefi; toplam algılama/gate kapanma gecikmesi ≤0.5 µs hedefi; O1 kapasitans en az mevcut 10 µF kabulü. Bu eşik ve gecikme henüz **tasarım girdisi/varsayım** düzeyindedir; tam MPN seçilmedi, kanıtlanmış OVP değildir.

**SUPERSEDED yedek:** PR #1 hibrit mimarisini ancak bağımsız çözüm comparator/latch/MOSFET sıcaklık, gecikme veya hata enjeksiyonu kabulünü geçemezse tekrar değerlendir. Çok bileşenli yedek doğrudan öneri değildir.

Kararı fiziksel hata enjeksiyonunun kolaylığı ve ana güç katından bağımsız izolasyon belirledi. Crowbar+F1 seçeneği, F1'in DC kesme/I²t/arıza akımı bilinmediği için yedek bile olamayacak kadar koordinasyonsuzdur. Mevcut 16.9 V eFuse OVP'si ana şartı sağlamaz.

## Adayların karşılaştırması

| Aday | En kötü O1 tepe ve sonuç | Ek parça / sadelik | Tezgâh testi | Model güven sınırı |
|---|---|---|---|---|
| PR #1 hibrit (TPS48000-Q1, 4×CSD18540Q5B, TLV3601, REF35409, TPS7A1650, pasifler) | PR#1 raporunda seçilmiş model köşesi 11.90318 V (12 V'a 96.8 mV marj). Dört ESL deck abort etti; latch bypass/bağımsız köşelerde 12.412–12.418 V FAIL. Fiziksel pass yok. | En az 5 IC + 4 güç MOSFET'i + bias ve çok sayıda pasif; yüksek karmaşıklık. | Hata enjeksiyonu mümkün; çoklu latch/enable dalları ayrı ayrı test edilmeli. | PR modeli tamamlanmamış; ESL abortları kanıt değildir, silikon/transient/SOA yok. |
| LTC4365 adayı (repo geçmişi) | Yerel native-LTspice yüksek eşik kaydı 11.8302 V; buck high-side short kaydı **12.3818 V FAIL**; `PROJECT-STATE.md` başka corner 12.4055 V raporlar. Başarısız köşe korunur. | Tek kontrolcü + harici MOSFET/pasifler; PR#1'den basit, ama ek analog kontrol. | Gate/OVP trip ve buck kısa devre testleri yapılabilir. | Yerel LTspice macro-model + yaklaşık MOSFET; ana devrede yok, kayıtlar farklı köşeler. |
| Bağımsız comparator + latch + seri disconnect (öneri) | Family 1 ideal source-pulse/latch modeli 11.9741 V gösterir; O1≤12.0 V'a yalnız 25.9 mV model marjı var. Bu sonuç Family 2 buck high-side-short topolojisine uygulanamaz; orada O1=18.8039 V **FAIL** ve bağımsız aday devre yok. Hesap ekranı 11.9635 V, parazitik/turnoff hariç; model/hypothesis agreement değil. | 1 comparator + 1 referans + latch (tek/iki kapı) + 2 FET + bölücü/pasif; makul ve test edilebilir. Exact MPN/stok yok. | O1 ucuna akım sınırlı 11.5–16.9 V pulse uygula; ayrıca buck high-side short ve bağımsız OVP birlikte hata enjeksiyonuyla denenmeli. | SPICE ideal eşik/gecikme/FET temsilidir; comparator offset/overdrive, gate charge, FET SOA, kablo/PCB L ve Ceff corner yoktur. İki senaryo tek aday güvenlik kanıtı değildir. |
| O1 crowbar + F1 | Tepe crowbar tepki anında ≤12 V olabilir, fakat hata akımı/fuse açma davranışı bilinmediği için sayısal maksimum hesaplanamadı: AÇIK. | Crowbar anahtarı + sürüş + koordineli DC fuse; mevcut F1 seçimsiz. | Test edilebilir, ancak tek kullanımlık fuse, ark/enerji ve tekrar kurulumu gerekir. | Fuse açma eğrisi, batarya/kablo empedansı ve crowbar SOA yok; geçme iddiası mümkün değil. |

### OVP eşik/gecikme hesabı

| Varsayım | Hesap | Sonuç |
|---|---|---:|
| Eşik üst corner | 11.35 V nominal × (1 + 1%) | 11.4635 V |
| Kapasitif yükselme, 5 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.25 V; O1≈11.7135 V |
| Kapasitif yükselme, 10 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.50 V; O1≈11.9635 V |
| Hedefe kalan pay | 12.0−11.9635 | 36.5 mV; ESL/turnoff ve ölçüm belirsizliği hariç |

Bu senaryoda mevcut CEFOUT=10 µF yalnız nominal değer; DC-bias/derating ve FET turnoff akımı doğrulanmadı. 10 A arıza akımının gerçek sınırı bilinmiyor. Dolayısıyla öneri hesapta çok az marjla koşullu olarak mümkün görünür, **tasarım kanıtı değildir**. Kart için en az 100 MHz osiloskopla gerçek pulse ve hata enjeksiyonu zorunludur.

### PR #2 bağımsız incelemesi — OVP kanıt kapsamı

İnceleme HEAD'indeki [`family1-ovp-independent-latch.cir`](https://github.com/siimsek/PDU/blob/adf727f244092b3628ba759b1dee5cd48909a19c/reports/g1/sim/family1-ovp-independent-latch.cir) içinde `.param TDELAY=0.5u` tanımlı, fakat devre ifadesinde kullanılmıyordu. Gözlenen ideal gecikme Clatch, Btrip sink akımı ve 0.5 V switch eşiğinden doğuyordu. Düzeltme koşusunda TDELAY artık Btrip akımını belirleyen ideal parametredir; eski deck ve log [`family1-ovp-independent-latch-attempt3.cir`](sim/family1-ovp-independent-latch-attempt3.cir) / [`.log`](sim/family1-ovp-independent-latch-attempt3.log) altında korunur. Yeni 11.9741 V ölçümü bu ideal model için tekrarlanabilir; gerçek comparator/gate gecikmesi ölçümü değildir.

Family 1 yüksek giriş pulse'ı ile ideal seri anahtarı yalıtır. Family 2'nin buck high-side short kaynağı ve O1 eFuse yükü ayrıdır; family 2 deck'inde bağımsız comparator/latch/series-disconnect yoktur. Bu nedenle **buck short + önerilen aday OVP birleşik testi yapılmadı ve kanıt yoktur**. Aday MPN ve datasheet garantili gecikme/offset mevcut olmadığından bir bileşen köşesi/pass değeri üretilemez.

| Sonraki birleşik hata testi için köşe ekseni | Gerekli veri | Durum |
|---|---|---|
| Trip threshold | Referans initial accuracy/TCR, comparator offset vs overdrive/temp, divider tolerance/TCR | MPN yok; sayısal worst-case AÇIK |
| Fault-to-off delay | Comparator propagation vs overdrive/temp, latch/gate delay, gate-source/sink current, FET Qg and driver impedance | MPN yok; 0.5 µs varsayımı kanıt değil |
| O1 overshoot | Minimum Ceff after DC-bias/tolerance/aging, ESL/ESR, harness/PCB inductance/resistance, fault/load current envelope | Ceff/ESL and physical fault current AÇIK |
| Disconnect survival | MOSFET VDS/SOA and turnoff waveform, reverse/backfeed path, repeated pulse/thermal limits | Exact FET and SOA waveform AÇIK |
| Buck short response | Shorted high-side switch, independent OVP connected at O1, actual eFuse state, fault current and source impedance | Family 2 has no candidate OVP; combined case AÇIK |

Measured or guaranteed inputs must be selected before this matrix can produce a valid component-corner simulation. Until then the 12.0 V O1 criterion remains unproven.

## UVLO politikası ve basit bölücü

20 V yeniden kalkış, dondurulmuş 20–26 V giriş zarfının alt ucuna ulaşabilmek için gereklidir. 6S için 20/6=3.333 V/hücre. Ancak batarya koruması tek başına bu UVLO'ya bırakılmamalıdır; yaklaşık 16.5 V tipik falling (0.9× rising varsayımı) 2.75 V/hücre olur ve batarya üretici kesim politikası bilinmiyor.

- Mevcut 180k/10k, eşik0.95–1.05 V ve iki direnç ±1% köşesinde yükselen eşik 17.711–20.332 V verir; 20 V restart FAIL.
- **En basit değişiklik:** RUV1 180 kΩ → 174 kΩ (RUV2=10 kΩ kalır). Aynı varsayımlarla açma yaklaşık17.14–19.69 V; nominal yaklaşık18.4 V; üst corner 3.28 V/hücre. EN leakage ve TCR dahil değil.
- EN leakage değişimi yaklaşık `I_EN × Rtop`; 174k için her 1 µA, açma eşiğinde 0.174 V değişim yapar. Garantili EN leakage sınırı doğrulanmadı.
- RUV1 için exact MPN/tolerans/TCR ve RUV2 matching seçimi açık; tasarım değişikliği öneridir, uygulanmış değildir.

G1 family 3'ün behavioral-model açılış/UVLO kriter PASS'i, WP2 dinamik kriterlerini doğrulamaz. 174 kΩ/10 kΩ yalnız statik yükselen eşik aday hesabıdır; VIN-OK→EN ≥60 ms, her EN yükselişinde M1, V_f≥18 V, dip ve çift darbe kapıları için G1'de devre modeli/koşusu/ölçüm yoktur. PR #1 WP2'deki 161 PASS / 69 FAIL / 6 eksik tarihsel yeniden değerlendirme olduğu gibi AÇIK kalır.

PR#1 WP2'deki comparator/mux/reference'lı çok-IC UVLO ancak batarya histerezisi/pack-state işlevi 174k/10k pasif bölücüyle sağlanamazsa gerekçelendirilebilir; bugünkü G1 statik eşik hesabı bu karmaşıklığı tek başına gerektirmiyor. Bununla birlikte WP2'nin M1 ≥60 ms gecikme, V_f ≥18 V ve dip sonrası yeniden başlama kapıları pasif bölücü/modelle kanıtlanmıyor; bunlar bu kararla kapanmış sayılmaz.

## Güncel PR #1 WP1/WP2 karşılaştırması

PR dalı `wp/baseline-2026-10-24` @ `9d8f5e1` salt-okunur incelendi. WP1 rev3'ün tamamlanan O1 tepe sonucu 11.90318 V olsa da dört ESL deck'i incomplete, doğrulayıcı exit 2 ve N-01 güvenli üst sınır varsayımı 13.03882 V olarak kalıyor. G1 ideal modelindeki 11.9741 V, farklı model/topoloji ve eksik parazitler sebebiyle bunu kapatmıyor. WP2'nin 161 PASS / 69 FAIL / 6 eksik sayımı eski Tur-5 loglarının Tur-6 doğrulayıcısıyla yeniden değerlendirmesidir; yeni elektriksel kabul koşusu değildir. Tam farklar ve kanıt referansları [`PREVIOUS-WP-COMPARISON.md`](PREVIOUS-WP-COMPARISON.md) içindedir.

## Kaynaklar

- Ana OVP/UVLO açık durumu: [`docs/design.md`](../../docs/design.md), [`docs/PROJECT-STATE.md`](../../docs/PROJECT-STATE.md), [`docs/REVIEW-CHECKLIST.md`](../../docs/REVIEW-CHECKLIST.md).
- PR#1 hibrit önerisi ve sonuçlar: [PR #1](https://github.com/siimsek/PDU/pull/1) (yalnız girdi; tamamlanmış/merge edilmiş tasarım kabulü değildir).
- Hesap ayrıntısı: [`calc-results.json`](calc-results.json), [`calc-results.md`](calc-results.md); ideal aday koşusu: [`sim-results.json`](sim-results.json).

## PR #2 second independent review (comment 6682187742) — component-level follow-up

The reviewer findings remain useful and the OVP design remains **BLOCKED**. This addendum records the additional measurement, MPN candidates and combined model cases; it does not revise any acceptance limit or historical FAIL.

| Review item | Follow-up evidence | Status |
|---|---|---|
| G1-R2-01 switch-off timing | Ideal Family 1 now measures series current below 1 mA at 557.183 ns after trip; analytic ideal-switch threshold crossing is 550 ns. The original `TDELAY=0.5 µs` is not a physical turn-off measurement. | SİM; physical measurement **not performed** |
| G1-R2-02 capacitor/current envelope | Updated selected-component threshold high corner is 11.6232 V. At the provisional 11.965 A fast-trip threshold screen and estimated 325.4 ns, ideal charge balance requires 10.332 µF. The 10 µF scenario is below this screen. Current is not bounded by the eFuse fast-trip threshold; ESR/ESL/tail and Ceff aging/bias are absent. | HESAP; physical minimum Ceff **AÇIK** |
| G1-R2-03 actual MPN chain | Candidate comparator/reference/latch/driver/back-to-back MOSFET/LDO MPNs and official manufacturer datasheets are listed in [OVP-ENGINEERING-RESULT.md](OVP-ENGINEERING-RESULT.md) and [OVP-COMPONENT-REVIEW.md](OVP-COMPONENT-REVIEW.md). Comparator delay at selected low overdrive, real loaded driver timing, reset/startup circuit and FET SOA remain unverified. | Candidate for lab engineering only; no OVP acceptance |
| G1-R2-04 fail-closed checks | Tests verify the exact measured-current edge exists, historical Family 2/4 FAILs remain, combined SPICE outputs are blocked, and the no-load current-threshold timing cannot be accepted when negative. | 14 Python tests pass; analysis/test result is not electrical acceptance |

### Combined Family 2 high-side short with O1 candidate switch

Two completed target corners share the Family 2 behavioral high-side-short deck and add the independent O1 branch disconnect. With 10 µF / 7 A, O1 peaks at 11.6900 V, S2E at 19.0809 V, and simulated series current falls below 1 mA 326.123 ns after the O1 threshold crossing. With 4 µF / no load, O1 peaks at 11.6857 V and S2E at 18.8274 V; series current is already below 1 mA before the trigger window, so current-based switch-off measurement is invalid and only the 325.262 ns control-threshold interval is available. Both satisfy only their behavioral model O1 criterion; no design or physical PASS is claimed.

The combined deck uses ideal switches and zero capacitor ESR/ESL and excludes the real eFuse current-limit / fast-trip waveform. Thus the 10 µF model outcome below 12 V does not close the ideal current/time Ceff screen, nor does it provide a guaranteed current margin. The O1-branch switch does not protect S2E from the shared bus fault. The full inputs and logs are linked from [OVP-ENGINEERING-RESULT.md](OVP-ENGINEERING-RESULT.md) and [SIMULATION-RESULTS.md](SIMULATION-RESULTS.md).

### Decision and retained open findings

The candidate MPN chain is concrete enough to prototype, but **not demonstrated safe enough to select as an accepted OVP architecture**: comparator delay at the actual overdrive is unbounded by the quoted datasheet test row; end-to-end switch time lacks a guaranteed bound; the provisional fast-trip threshold is not a hard current ceiling; minimum physical Ceff is unknown; and the selected MOSFET SOA does not cover the sub-microsecond estimate. No real board or scope capture exists.

The 3.59 kΩ / 1.00 kΩ divider candidate also yields a worst-case trip of 11.6232 V, which misses the prior provisional 11.46 V upper trip target by 163.2 mV (the hard O1 ceiling remains 12.0 V). Under the present corner assumptions, the mathematical Rtop interval satisfying only `trip_min >= 11.1605 V` and `trip_max <= 11.46 V` is 3.52195…3.52569 kΩ, a 3.74 Ω-wide window with **no** noise/ripple allowance. Its midpoint gives only about 4.6 mV margin to both limits. Do not adopt this interval as a validated resistor recommendation; O1 noise/ripple and an exact resistor MPN remain open.

The independent-OVP-free Family 2 **18.8039 V FAIL**, Family 4 **10.7109 V FAIL**, WP1 four incomplete ESL conditions and N-01, and WP2 **69 FAIL / 6 incomplete** remain open. PR #1 and main were not changed; no KiCad file was edited.
