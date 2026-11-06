"""Build evidence-linked G1 decision, requirements, BOM and handoff reports."""
import csv
import json
from pathlib import Path
from pdu_calc import ROOT, OUT

def write(name, body):
    (OUT/name).write_text(body.strip()+"\n",encoding="utf-8")

def requirements():
    write("REQUIREMENTS.md", """
# G1 gereksinim dondurma

Kaynak önceliği `docs/REPOSITORY.md` sırasındadır: dışa aktarılmış netlist/BOM, güncel teknik ve durum belgeleri; PR #1 önerileri yalnız girdi. G1 dalı `main` tabanı `a1dbeeb` üzerinde korunmuştur; PR #1 WP1/WP2 güncel HEAD `9d8f5e1` ayrı salt-okunur kanıt olarak karşılaştırıldı (`PREVIOUS-WP-COMPARISON.md`), hiçbir öneri ana tasarıma uygulanmış sayılmadı. Bu dondurma AI analiz sınırıdır; KiCad kaynakları değiştirilmemiştir.

| Başlık | G1 dondurulan değer | Etiket / kaynak |
|---|---|---|
| Giriş | 6S LiPo, 20–26 V; nominal 22.2 V. Batarya iç direnci, kablo empedansı, ani darbeler ve düşük hücre cutoff'u verilmedi. | DATASHEET değil, REPO [`docs/design.md`](../../docs/design.md), `PROJECT-STATE.md` |
| Ortak bara | 11.0 V nominal, 7 A/77 W yük hedefi; güç katı kapasitesi 7.5 A/82.5 W. 7.5 A kapasite hedefi gerçek yük ölçümü değildir. | REPO |
| Yük akımları | O1/S2E sürekli, kalkış, adım ve tepe akımı ölçülmedi. PR #1'de O1 “5 A” hedefi bulunur; ana repo bunu atamaz, dolayısıyla G1 ölçüm girdisi sayılmaz. | AÇIK; PR#1 girdi |
| O1 mutlak giriş zarfı | Anlık tepe ≤12.0 V; bu sınır aşılmaz. Stabil bara ≤11.1605 V. | Kullanıcı şartı + `simulation/static-corner-results.json` |
| S2E giriş aralığı | Ana doküman, eFuse değerleri ve mevcut netlist S2E için garanti edilmiş min/max giriş gerilimi tanımlamıyor. Nominal bara yaklaşık 11 V'tur; üst/alt port sınırı açık. | AÇIK |
| DC doğruluk | Ana setpoint nominal 10.9961 V; kayıtlı FB statik köşesi 10.8333–11.1605 V. Mevcut gereksinim notunda 10.78–11.22 V ±2% çalışma bandı; kullanıcıya verilen kararlı üst sınırı 11.1605 V daha sıkıdır. | HESAP / REPO |
| Transient | PR#1 REQUIREMENTS 10.78–11.22 V transient çalışma bandını verir; ancak kullanıcı O1 ≤12.0 V anlık tepe şartı her durumda üstündür. Gerçek yük profili yok. | PR#1 girdi / AÇIK |
| Ortam sıcaklığı | Kullanıcı tanımlamadı. Hesap raporunda 25°C referans senaryosu; -40..125°C elektriksel cihaz aralığı ve 125°C COUT/eFuse sınırları ayrıca taranır; tasarım ortamı/mahfaza sıcaklığı açık. | VARSAYIM / AÇIK |
| Giriş açma | 20 V'ta yeniden kalkış istenen giriş zarfının alt ucuna karşılık gelir. 6S hücre başına 3.333 V. | HESAP |
| Mimari | J1 → F1 → LM74700+Q1 ters polarite/ideal diyot → VIN → 2×LM70880-Q1, ortak COMP/EN/VOUT, SYNCOUT→SYNCIN ve 180° → 2×TPS259824O → O1/S2E. | REPO |
| F1 | “10 A” yalnız not/değer; MPN, yuva/footprint, DC kesme, I²t ve kaynakla koordinasyon onaylanmadı. | AÇIK |

## Çelişki ve uygulanacak yorum

1. 7 A ana bara hedefi ile PR#1'deki O1=5 A varsayımı aynı şey değildir. O1/S2E akım bölüşümü ölçülmedi; G1 akım bütçesi toplam 7/7.5 A ile sınırlandırılır.
2. PR#1 çalışma bandı transient için 11.22 V üst sınırı verir; kayıtlı statik FB köşesi 11.1605 V'tur. Kararlı durumda 11.1605 V uygulanır; transientte 11.22 V bara üst sınırı ve O1'de her zaman 12.0 V mutlak tepe uygulanır.
3. `RUV1/RUV2=180k/10k` kayıtlı köşe hesabı 20.3318 V'a çıkar; 20 V yeniden kalkışla uyumlu değildir. EN sızıntısı/TCR eklenmemiştir.
4. Mevcut TPS259824O 16.9 V nominal OVP'si O1 ≤12.0 V şartını karşılamaz; bu tasarım kabul edilmemiş FAIL'dir.

## Kullanılan resmi kaynaklar

- TI LM70880-Q1, Rev C datasheet, §§6–8, 11–12: [PDF](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf).
- TI TPS25982, Rev C, §§5–8, 10: [PDF](https://www.ti.com/lit/ds/symlink/tps25982.pdf).
- TI LM74700-Q1, Rev G, §§5–6: [PDF](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf).
- LM70880 page mapping (PDF pages): p5 absolute max; p6 EN/thermal; p7 VFB/gm/RT table; p8 current sense; p14 oscillator equation; p16 compensation/current-sense; p34 propagation-delay overshoot/Kelvin guidance.
- TPS25982 page mapping (PDF pages): p7–10 operating/electrical/current-limit/OVP-response tables; p21 OVP operation; p23 ILIM formula; p28 IMON use; p35 RILIM example.
- LM74700-Q1 page mapping (PDF pages): p5 max/recommended ratings; p6 thermal/electrical data.
- Vishay IHLP-4040DZ-L1: p1 electrical table and ratings; p2–3 performance curves: [PDF](https://www.vishay.com/docs/34207/ihlp-4040dz-l1.pdf). Vishay cross-reference document #34509 p1 lists candidate code `IHLP4040DZER6R8M01` for 6.8 µH/23.3 mΩ/13.5 A saturation/8 A heat-rating current: [official cross-reference](https://www.vishay.com/doc/?34509=).
- TDK C5750 characterization p1: [PDF](https://product.tdk.com/en/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c5750x7s2a226m280kb.pdf). Vendor SPICE-derived Ceff/ESR is separately recorded in `hardware/validation/c5750/vendor-ac-summary.json`.
- Molex PS-43045-001 Rev P5 current derating p8: [PDF](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf).
- Infineon BSC160N10NS3-G Product Summary p1: [PDF](https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc160n10ns3-ds-en.pdf).
- TDK C5750X7S2A226M280KB official product data and local qualification: [product](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB), [`hardware/COUT-qualification.md`](../../hardware/COUT-qualification.md).
- Molex 43045 connector series, PS-43045-001 Rev P5: [PDF](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/430/43045/PS-43045-001.pdf).
""")

def decision():
    write("OVP-UVLO-DECISION.md", """
# O1 OVP ve UVLO mimari kararı

## Karar

**Öneri (aday mimari):** O1 çıkışında, TPS259824O'dan sonra çalışan bağımsız hızlı comparator + referans + set-dominant latch + seri back-to-back MOSFET disconnect. OVP eşiği nominal 11.35 V, tüm toleranslarda en çok 11.46 V hedefi; toplam algılama/gate kapanma gecikmesi ≤0.5 µs hedefi; O1 kapasitans en az mevcut 10 µF kabulü. Bu eşik ve gecikme henüz **tasarım girdisi/varsayım** düzeyindedir; tam MPN seçilmedi, kanıtlanmış OVP değildir.

**Yedek:** PR #1 hibrit mimarisini ancak bağımsız çözüm comparator/latch/MOSFET sıcaklık, gecikme veya hata enjeksiyonu kabulünü geçemezse tekrar değerlendir. Çok bileşenli yedek doğrudan öneri değildir.

Kararı fiziksel hata enjeksiyonunun kolaylığı ve ana güç katından bağımsız izolasyon belirledi. Crowbar+F1 seçeneği, F1'in DC kesme/I²t/arıza akımı bilinmediği için yedek bile olamayacak kadar koordinasyonsuzdur. Mevcut 16.9 V eFuse OVP'si ana şartı sağlamaz.

## Adayların karşılaştırması

| Aday | En kötü O1 tepe ve sonuç | Ek parça / sadelik | Tezgâh testi | Model güven sınırı |
|---|---|---|---|---|
| PR #1 hibrit (TPS48000-Q1, 4×CSD18540Q5B, TLV3601, REF35409, TPS7A1650, pasifler) | PR#1 raporunda seçilmiş model köşesi 11.90318 V (12 V'a 96.8 mV marj). Dört ESL deck abort etti; latch bypass/bağımsız köşelerde 12.412–12.418 V FAIL. Fiziksel pass yok. | En az 5 IC + 4 güç MOSFET'i + bias ve çok sayıda pasif; yüksek karmaşıklık. | Hata enjeksiyonu mümkün; çoklu latch/enable dalları ayrı ayrı test edilmeli. | PR modeli tamamlanmamış; ESL abortları kanıt değildir, silikon/transient/SOA yok. |
| LTC4365 adayı (repo geçmişi) | Yerel native-LTspice yüksek eşik kaydı 11.8302 V; buck high-side short kaydı **12.3818 V FAIL**; `PROJECT-STATE.md` başka corner 12.4055 V raporlar. Başarısız köşe korunur. | Tek kontrolcü + harici MOSFET/pasifler; PR#1'den basit, ama ek analog kontrol. | Gate/OVP trip ve buck kısa devre testleri yapılabilir. | Yerel LTspice macro-model + yaklaşık MOSFET; ana devrede yok, kayıtlar farklı köşeler. |
| Bağımsız comparator + latch + seri disconnect (öneri) | İdeal gecikme/akım modeli bu raporun hedefli family-1 SİM'inde; bu bir komponent sonucu değildir. Hedef üst köşe 11.46 V, 10 A/10 µF/0.5 µs basit üst sınır ≈11.96 V (HESAP, parazitik/turnoff akımı hariç). | 1 comparator + 1 referans + latch (tek/iki kapı) + 2 FET + bölücü/pasif; makul ve test edilebilir. Exact MPN/stok yok. | O1 ucuna akım sınırlı 11.5–16.9 V pulse uygula; trip, latch, reset ve kalan tepeyi aynı anda ölç. | SPICE yalnız ideal eşik/gecikme/FET temsil eder; comparator offset/overdrive, gate charge, FET SOA ve kablo endüktansı dahil değil. |
| O1 crowbar + F1 | Tepe crowbar tepki anında ≤12 V olabilir, fakat hata akımı/fuse açma davranışı bilinmediği için sayısal maksimum hesaplanamadı: AÇIK. | Crowbar anahtarı + sürüş + koordineli DC fuse; mevcut F1 seçimsiz. | Test edilebilir, ancak tek kullanımlık fuse, ark/enerji ve tekrar kurulumu gerekir. | Fuse açma eğrisi, batarya/kablo empedansı ve crowbar SOA yok; geçme iddiası mümkün değil. |

### OVP eşik/gecikme hesabı

| Varsayım | Hesap | Sonuç |
|---|---|---:|
| Eşik üst corner | 11.35 V nominal × (1 + 1%) | 11.4635 V |
| Kapasitif yükselme, 5 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.25 V; O1≈11.7135 V |
| Kapasitif yükselme, 10 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.50 V; O1≈11.9635 V |
| Hedefe kalan pay | 12.0−11.9635 | 36.5 mV; ESL/turnoff ve ölçüm belirsizliği hariç |

Bu senaryoda mevcut CEFOUT=10 µF yalnız nominal değer; DC-bias/derating ve FET turnoff akımı doğrulanmadı. 10 A arıza akımının gerçek sınırı bilinmiyor. Dolayısıyla öneri hesapta çok az marjla koşullu olarak mümkün görünür, **tasarım kanıtı değildir**. Kart için en az 100 MHz osiloskopla gerçek pulse ve hata enjeksiyonu zorunludur.

## UVLO politikası ve basit bölücü

20 V yeniden kalkış, dondurulmuş 20–26 V giriş zarfının alt ucuna ulaşabilmek için gereklidir. 6S için 20/6=3.333 V/hücre. Ancak batarya koruması tek başına bu UVLO'ya bırakılmamalıdır; yaklaşık 16.5 V tipik falling (0.9× rising varsayımı) 2.75 V/hücre olur ve batarya üretici kesim politikası bilinmiyor.

- Mevcut 180k/10k, eşik0.95–1.05 V ve iki direnç ±1% köşesinde yükselen eşik 17.711–20.332 V verir; 20 V restart FAIL.
- **En basit değişiklik:** RUV1 180 kΩ → 174 kΩ (RUV2=10 kΩ kalır). Aynı varsayımlarla açma yaklaşık17.14–19.69 V; nominal yaklaşık18.4 V; üst corner 3.28 V/hücre. EN leakage ve TCR dahil değil.
- EN leakage değişimi yaklaşık `I_EN × Rtop`; 174k için her 1 µA, açma eşiğinde 0.174 V değişim yapar. Garantili EN leakage sınırı doğrulanmadı.
- RUV1 için exact MPN/tolerans/TCR ve RUV2 matching seçimi açık; tasarım değişikliği öneridir, uygulanmış değildir.

PR#1 WP2'deki comparator/mux/reference'lı çok-IC UVLO ancak batarya histerezisi/pack-state işlevi 174k/10k pasif bölücüyle sağlanamazsa gerekçelendirilebilir; bugünkü G1 statik eşik hesabı bu karmaşıklığı tek başına gerektirmiyor. Bununla birlikte WP2'nin M1 ≥60 ms gecikme, V_f ≥18 V ve dip sonrası yeniden başlama kapıları pasif bölücü/modelle kanıtlanmıyor; bunlar bu kararla kapanmış sayılmaz.

## Güncel PR #1 WP1/WP2 karşılaştırması

PR dalı `wp/baseline-2026-10-24` @ `9d8f5e1` salt-okunur incelendi. WP1 rev3'ün tamamlanan O1 tepe sonucu 11.90318 V olsa da dört ESL deck'i incomplete, doğrulayıcı exit 2 ve N-01 güvenli üst sınır varsayımı 13.03882 V olarak kalıyor. G1 ideal modelindeki 11.9741 V, farklı model/topoloji ve eksik parazitler sebebiyle bunu kapatmıyor. WP2'nin 161 PASS / 69 FAIL / 6 eksik sayımı eski Tur-5 loglarının Tur-6 doğrulayıcısıyla yeniden değerlendirmesidir; yeni elektriksel kabul koşusu değildir. Tam farklar ve kanıt referansları [`PREVIOUS-WP-COMPARISON.md`](PREVIOUS-WP-COMPARISON.md) içindedir.

## Kaynaklar

- Ana OVP/UVLO açık durumu: [`docs/design.md`](../../docs/design.md), [`docs/PROJECT-STATE.md`](../../docs/PROJECT-STATE.md), [`docs/REVIEW-CHECKLIST.md`](../../docs/REVIEW-CHECKLIST.md).
- PR#1 hibrit önerisi ve sonuçlar: [PR #1](https://github.com/siimsek/PDU/pull/1) (yalnız girdi; tamamlanmış/merge edilmiş tasarım kabulü değildir).
- Hesap ayrıntısı: [`calc-results.json`](calc-results.json), [`calc-results.md`](calc-results.md); ideal aday koşusu: [`sim-results.json`](sim-results.json).
""")

def handoff_docs():
    write("BENCH-ACCEPTANCE.md", """
# Fiziksel test kabul kriterleri (T0–T6)

Bu kriterler ölçümle kapanır; SİM sonucu kabul yerine geçmez. O1 anlık tepe her aşamada ≤12.0 V; kararlı bara ≤11.1605 V şartları gevşetilmez.

| Test | Düzeneği ve ölçüm | Geçme kriteri | Model/hesap beklentisi (ayrı; fiziksel kanıt değildir) |
|---|---|---|---|
| T0 Görsel/soğuk | Mikroskop, DMM, 4-wire düşük-ohm ölçer; J1 girişinde akım sınırlı kaynak kapalı. | Yanlış polarite/short yok; F1, TVS, Q1, L1/L2, COUT, RS ve connector MPN/footprint/polarite kayıtları eşleşir. GND-VIN direnç kısa devre değildir; değer kart şemasıyla tutarlı kaydedilir. | SİM yok. BOM 57 boş MPN ile kart kabul edilemez. |
| T1 Açılış ve statik regülasyon | 0–30 V/≥10 A kaynak; T0 sonrası 20/22.2/26 V; önce 0.75 A sonra gerçek port split ile 7 A. 100 MHz scope, 10× kısa ground spring/diff probe. | 20 V'ta yeniden kalkış; settle sonrası bus 10.78–11.1605 V; O1 peak ≤12.0 V. 7.5 A kapasite testi ayrı, 7.5 A yük iki eFuse nominal limitlerini aşmadan dağıtılabilirse yapılır. | Mevcut behavioral baseline 20 V startup bus≈10.996 V; fiziksel davranış tahmini değildir. |
| T2 7 A sürekli/termal | 7 A toplam yük, 20/26 V giriş, en az 30 dakika veya sıcaklık dengesi; termokupl/IR kamera ve akım probları. | Bus 10.78–11.1605 V; bobin, IC, FET, eFuse, konektör sıcaklığı kendi datasheet limitinin ≥20°C altında; güç kaybı ve sıcaklık kaydı. 7.5 A ayrı kapasite testi yalnızca RILIM guaranteed-min range actual port split'i karşılayıp marj verirse; mevcut nominal ILIM sum 7.4877 A **FAIL**. | HESAP 80/90/95% verim için 20.63/9.17/4.34 W toplam kayıp hassasiyeti; kart termali bilinmiyor. |
| T3 Yük adımı | Elektronik yük iki portta; toplam 0.75→7.00→0.75 A, rise/fall ≤1 A/µs. O1 connector ve baraya eşzamanlı prob. FRA: 10 Hz–200 kHz, injection transformer/resistor. | O1 her an ≤12.0 V; bara transient 10.78–11.22 V içinde, ≤1 ms içinde settle edip 10.78–11.1605 V'a döner; ölçülen faz marjı ≥45°, gain marjı ≥6 dB. | Mevcut 0.45→4.5 A behavioral adım 10.804–10.996 V; 7 A / kompanzasyon köşesi için ölçüm beklentisi yok. |
| T4 O1 OVP fault injection | Kart O1 yükünden ayrık; ayarlı pulse kaynağı/seri güç direnci ve akım probu, dışarıdan 11.4→16.9 V pulse. Önce 1 A sınırlı, sonra 5 A ve en son 10 A fixture limiti; fiziksel kaynak/fixture sınırı doğrulanmadan yükseltme yok. | Uygulanan her pulse'da O1 konektör tepe ≤12.0 V; latch reset davranışı belirlenmiş; güç katı/port zarar görmez; 5 tekrar x3 köşe. Aşılırsa derhal durdur ve FAIL kaydet. | Aday ideal model 11.96 V @10 A/0.5µs varsayımı; gerçek comparator/gate/parazit yok. Mevcut eFuse yalnız 16.9 V nominal olduğundan başarısız beklenti. |
| T5 UVLO/batarya ramp | 0–26 V programlanabilir kaynak, 0.1 V/s ve 1 V/s ramp, 0.75 A yük; batarya simülatörü veya 6S hücre emülatörü. | 20.00 V'a yükselirken her seferde kalkış; kararlı bara aralıkta. Falling cutoff/histerezis yalnız pack üretici cutoff politikası belirlendikten sonra pass/fail olur; test öncesi batarya güvenlik cutoff'u bağımsızdır. Hıçkırık/tekrarlı aç-kapa yok. | 174k/10k hesap üst rising corner19.69 V (EN leakage/TCR hariç). |
| T6 eFuse kısa devre/hot-plug | O1 ve S2E ayrı test; kısa devre MOSFET/röle fixture, akım probu, 100 MHz scope; 10 µF+port kablosu, port hot-plug fixture. | O-variant data-sheet short test koşulunda (>3×ILIM) akım kesme ≤400 ns; normal operating current/short re-try ve latch davranışı ayrıca kaydedilir. Hot-plug bus/O1 ≤11.22 transient, O1 ≤12.0 mutlak; port akımı/tepe/termal hasar yok. | behavioral short model nominal 0.5 µs latch varsayımı ile TI≤400ns değerini kanıtlamaz. dV/dt data-sheet pin akımı 2–6.33 V/ms sensitivity; gerçek çıktı yükü ölçülmeli. |

## Ekipman ve güvenlik kapıları

- Osiloskop ≥100 MHz, ≥1 GS/s, iki eşzamanlı kanal; düşük endüktanslı ground spring veya ≥100 MHz diferansiyel prob; port tepe için prob ucu doğrudan konektörde. Akım probu ≥20 MHz. Ripple için bandwidth limit ayrıca raporlanır.
- Elektronik yük ≥10 A / ≥120 W, edge kontrolü 1 A/µs; iki bağımsız kanal ya da dağıtım fixture'ı. DC kaynağı 0–30 V, ≥10 A, programlanabilir current limit. FRA 10 Hz–200 kHz ve loop injection aksesuarı.
- T4/T6 ilk enerjilemede kaynak limiti ≤1 A, sigortalı fixture ve koruyucu gözlük; test yükü/gerçek bağlı cihaz OVP geçmeden bağlanmaz. Güçlü akım adımı ve short için uzaktan tetik/kapalı kutu kullan.
- Anında durdur: O1 >12.0 V, bara >11.22 V transient zarfı, giriş pininde 80 V'a yaklaşma, Q1 VDS 80 V, herhangi IC/inductor datasheet sıcaklık sınırı, akım >fixture/fuse rating, duman/koku, kontrolsüz osilasyon. Hasarlı/FAIL numuneyi tekrar enerjileme.
- T4 hata akımı artışı ancak batarya/kablo/fuse ve TVS/SOA koordinasyonu ayrıca kabul edilince; 10 A test fixture sınırıdır, donanımın akım garantisi değildir.
""")

    write("KICAD-CHANGE-LIST.md", """
# Sonraki KiCad fazına aktarılacak değişiklik listesi

Bu liste taslak değişiklik emridir; bu G1 dalında hiçbir `*.kicad_*` dosyası değiştirilmedi.

| Ref/net | Eski → öneri | Footprint/işlem | Gerekçe ve kanıt |
|---|---|---|---|
| RUV1, VIN/EN_BUCK | 180 kΩ → 174 kΩ; RUV2 10 kΩ korunur | 0603; TCR/toleransı exact seçilecek | 20 V worst-case rising 19.69 V HESAP; EN leakage/TCR AÇIK. `calc-results.json`, OVP-UVLO decision. |
| RILIM1/RILIM2, ILIM_O1/S2E | 301/604 Ω → yalnız gerçek yük split'ini karşılayan ve datasheet guaranteed-min sum ≥7.5 A + ölçüm marjı veren değerler; exact values AÇIK | 0603; tolerance/TCR per vendor and TI supported value range | Nominal formulas sum7.4877 A <7.5 A by12.3 mA; exact-value current-limit guarantee unavailable. `calc-results.json/port_capacity_screen`. |
| O1_11V / U3 çıkışı | U3 sonrası bağımsız comparator+latch+back-to-back series disconnect ekle; eşik üst corner ≤11.46 V, toplam gecikme hedef ≤0.5 µs | Yeni comparator, reference, latch, 2×FET; exact refs/MPN/footprint/stok bu fazda AÇIK | O1 12 V limiti; mevcut U3 eFuse 16.9 V; OVP decision ve sim family-1. MPN uydurulmadı. |
| F1 / VBAT | “10A” placeholder → source fault/I²t/DC interrupt ile seçilen fuse + holder/footprint | F1 footprint ve servis/clearance alanı ekle; MPN açık | Batarya/kablo dirençleri yok; akım, I²t ve interrupt capacity hesaplanamaz. HESAP/AÇIK. |
| L1/L2, SW_PH1/2 | 6.8 µH korunabilir; candidate MPN IHLP4040DZER6R8M01; BOM/onay/stok open | IHLP-4040 generic land yerine exact vendor land karşılaştır | Ripple2.916 A p-p, phase peak5.583 A (+10% share); Vishay p1 Isat13.5 A (~20% L drop), heat-current8 A (40°C rise). |
| RS1/RS2, ISNS1/2 | 7.5 mΩ korunabilir; ≤1%/≤100 ppm/K varsayımını sağlayan exact low-ohm part | 2512, ≥0.5 W tavsiye; Kelvin ayrı pad/escape | HESAP worst share'de ~0.13 W/faz ve sense limit6.6–8.5 A; current error ve TCR açık. |
| COUT1–8, VOUT/GND | 8× C5750X7S2A226M280KB korunur; etkin Ceff/aging/ESR BOM notuna ekle | Mevcut özel 2220 land; üretici land/termal/flex kabulü korunur | DC-bias typical164.98 µF; sensitivity min92.65/max241.53 µF, yaşlanma %10 varsayım. |
| D1, VIN/GND | SMCJ33A family → üretici exact MPN; TVS/F1 ile koordinasyon | SMC footprint; gerçek standoff/clamp current/pulse energy ve placement kontrol | 53.3 V datasheet-family clamp varsayımı; transient/energy open. |
| D2/D3, O1/S2E/GND | SS34 generic → exact vendor MPN/rating; kullanılacağı fault akımı doğrula | SMA pad family check; path 7.5A ise 3A family yeterli değildir | BOM MPN/rating boş; topology/fault path açığı. |
| J1/J2/J3 | 43045-0200 family → header + matching housing/crimp/contact/cable exact MPN | Horizontal Micro-Fit 3.0 2-circuit; footprint pin pitch, keying, polarization and clearance verify | Molex W-B 18AWG 8.5A, W-W 7A; J2 7.5A hedefe W-W sınırı yetmez. |
| U5/Q1 | LM74700 generic MPN + BSC160N10NS3G value → exact orderable BOM fields, SOA/thermal-reviewed assembly | U5 SOT23-6, Q1 PG-TDSON-8 adapted land; final land/paste/thermal acceptance | 53.3V conditional margin; Q1 hot SOA/fault waveform open; `calc-results.json`. |
| U1/U2 + RCOMP/CCOMP/CHF | Mevcut değerleri doğrudan onaylama; RCOMP/CCOMP/CHF için bench-adjustable pad seçenekleri | 0603; RCOMP 6.8–27k, CCOMP 2.2–10nF, CHF 22–100pF test seçenekleri; default values DNP/jumper plan | Gerçek loop crossover/phase margin hesaplanamadı. FRA T3 pass ≥45°/6 dB ile seç. |

## Test noktaları / enjeksiyon padleri

- `TP_VBAT` (F1 öncesi), `TP_ANODE`, `TP_VIN`, `TP_VOUT`, `TP_O1_PRE` (U3 öncesi), `TP_O1` (son OVP sonrası), `TP_S2E`, `TP_GND` (probe return), `TP_EN_BUCK`, `TP_COMP`, `TP_SW1`, `TP_SW2`, `TP_ISNS1+/-`, `TP_ISNS2+/-` Kelvin, `TP_PG_O1`, `TP_PG_S2E`, `TP_IMON_O1`, `TP_IMON_S2E`.
- O1 OVP için `J_OVP_INJ` iki pad, korumalı external pulse fixture'a bağlanır; test sırasında normal power path'ten izolasyon ve limitli seri direnç fixture dışında yapılır. PCB'de O1 sonrası `R_OVP_BYPASS` footprinti DNP kalır ve normal durumda jumper takılmaz; bypass sökülü olarak fault-test yapılır. Aşırı gerilimde yük bağlama yok.
- `RINJ_FB` footprinti (default 0 Ω, 0603, FRA için 10–49.9 Ω opsiyon) FB üst koluna seri yerleştir; `TP_FB_UP/DOWN` ile FRA injection. Seri direnç DC oran etkisi ve noise ile şematik incelemede teyit edilir.
- EN/OVP comparator fault injection için `RFAULT_EN` DNP ≥100 kΩ seri pull-up/pull-down padleri; doğrudan batarya/rail injection yok.
- Akım şöntü için RS padlerinde ayrı Kelvin force/sense bağlantıları; hiçbir sense via/load-current via ortak boyun kullanmaz.

## PCB zorunlu yönlendirme girdileri

- **4 katman önerilir:** L1 komponent/switch kısa döngü; L2 kesintisiz GND dönüş; L3 güç dağıtım (VIN/VOUT, net alanları); L4 sinyal/yardımcı. 2 katmanda tam GND referansı ve termal yayılım bozulur. 2L/4L IR-drop karşılaştırması yalnız varsayımlıdır; stackup/fab copper bilgisi alınmadan plane sharing credit yok.
- 31.5 µm hesap bakırında, ΔT=20°C IPC-2221 dış iz taraması: BUS_POWER 7.5 A ve O1/S2E ayrı 7.5 A zarfı için 2L/4L minimumlarını `routing-comparison.json` satırlarından al. Akım bölüşümü ölçülmediği için port dalı zarfı ayrı ayrı tam kapasitedir. Her 50 mm güç segmentinde 50 mV IR-drop bütçesi; eski 6 mm bus class üretim garantisi değildir. `routing-input.json` varsayımları/akım değerlerini taşır.
- Güç via geçişlerinde G1 minimum sayı 0.5 A/via varsayımıyla routing JSON'da; sonraki fazda üreticinin plating/drill ve termal relief verisiyle yeniden hesaplanmadan DRC minimumuna çevrilmez. En az iki plane stitching sırası, gerekirse daha çok sayıda, via-in-pad açıkça üreticiye onaylatılır.
- U1/U2 high-frequency CIN–VIN–PGND döngüsü en küçük alan; SW bakırı kısa ve IC/FB/COMP'tan uzakta; SW node test padini min alan yap. Her iki şönt Kelvin, ortak GND dönüşüne güç padinden ayrı; COMP ve FB gürültülü bakır altından geçmez.
- EFuse/FET/O1 akım döngüsü konektöre kısa-geniş; test noktaları yüksek akım taşımaz. O1 disconnect MOSFET'leri / eFuse / F1 ısı dağılımı ile TVS/F1 loop geometrisi birlikte incelenir.

Önceki fazda KiCad'e aktarım öncesi onay: exact MPN, pad/pin map, net parity, clearance, power-loop ve DRC/short kontrolleri.
""")

def bom_report():
    bom=list(csv.DictReader((ROOT/"hardware/pdu-current-bom.csv").open(encoding="utf-8-sig",newline="")))
    rows=[]
    for x in bom:
        ref=x["Reference"]; value=x["Value"]; fp=x["Footprint"]; mpn=x["MPN"].strip()
        evidence="`hardware/pdu-current-bom.csv`; datasheet links/notes in `reports/g1/REQUIREMENTS.md` and `calc-results.md`."
        exact=mpn or "UNRESOLVED — no exact MPN in canonical BOM; no MPN invented."
        pkg="Standard footprint/value-family only; exact maker package/land match cannot be verified without MPN."
        stress="Operating stress/rating unavailable or topology dependent; verify exact datasheet before release."
        rating="Open: rating, tolerance/TCR and 50% derating cannot be established from BOM fields."
        absmax="AÇIK: exact part/maximum pin stress unknown."
        stock="Current stock/lifecycle not verified."
        verdict="AÇIK"
        if ref.startswith("COUT"):
            evidence="TDK C5750 product characterization PDF p1; vendor bias/AC model output `hardware/validation/c5750/vendor-ac-summary.json`; see [`COUT-qualification.md`](../../hardware/COUT-qualification.md)."
            pkg="TDK 2220 / special land was qualified in local COUT physical record; stencil, flex-crack and assembled thermal acceptance remain open."
            stress="100 V part vs assumed 53.3 V input TVS clamp: 1.88× stress, voltage rating passes 1.5× screen; DC-bias typical at 11 V is 20.622 µF each."
            rating="Ceff bank 92.651–241.527 µF includes assumed 10% aging on low side; ESR and aging are not guaranteed corners."
            absmax="Conditional rating margin +46.7 V to 53.3 V assumed clamp; actual transient overshoot/energy open."
            stock="Current distributor stock/lifecycle not verified (cached inventory is stale)."
            verdict="KISMİ"
        elif ref in ("RFB1","RFB2","RIMON1","RIMON2"):
            pkg="Panasonic ERA3AEB MPN confirms 0603 nominal package; land is generic 0603."
            stress="Divider/monitor voltage or power below stated 0.1 W component rating; exact resistor stress corner in calc report."
            rating="0.1%, ≤25 ppm/K; ≤0.1 W from manufacturer data; power use under 50% screen."
            absmax="No voltage or power absolute-max violation found for calculated operation; ESD/assembly not covered."
            stock="Current stock/lifecycle not verified."
            verdict="KISMİ"
        elif ref in ("U1","U2"):
            evidence="TI LM70880-Q1 PDF pp.5–8, 14, 16, 34; official PDF linked in REQUIREMENTS.md."
            pkg="Exact LM70880QRRXRQ1 RRX0029B identity and custom lands; footprint is documented approximate rectangular pad construction, not vendor CAD."
            stress="VIN operating 4.5–80 V; this project 20–26 V. VOUT/ISNS max60 V; TVS 53.3 V assumed gives only6.7 V operating margin."
            rating="8 A controller per datasheet; two phase capacity depends on current sharing, thermal and loop validation."
            absmax="VIN pin87.5 V; VOUT/ISNS60 V; conditional +34.2 V to 53.3 V only for VIN absolute; VOUT/ISNS needs separate mapping."
            stock="Current stock/lifecycle not verified."
            verdict="KISMİ"
        elif ref in ("U3","U4"):
            evidence="TI TPS25982 PDF pp.7–10, 21, 23, 28, 35; official PDF linked in REQUIREMENTS.md."
            pkg="Exact TPS259824ONRGET RGE0024M custom footprint; IN/GND exposed pads separated; assembly stencil/thermal via acceptance remains open."
            stress="VIN 24 V operating max; 30 V absolute; normal 11 V port; 26 V on common bus during a buck fault remains below 30 V but at/beyond recommended operating conditions."
            rating="RON max4.5 mΩ, TJ max125°C; ILIM exact resistor min/max not published for 301/604 Ω."
            absmax="OVP min16.32/typ16.9/max17.31 V does not meet O1≤12 V; hard FAIL for O1 protection."
            stock="Current stock/lifecycle not verified."
            verdict="FAIL/AÇIK"
        elif ref=="Q1":
            evidence="Infineon BSC160N10NS3-G Product Summary PDF p1; official part page and PDF linked in BOM record. SOA detail remains open."
            exact="Candidate from Value field: BSC160N10NS3G; MPN column blank (identity appears exact in Value)."
            pkg="PG-TDSON-8; adapted footprint is not exact vendor land and needs production land/paste review."
            stress="100 V VDS vs assumed 53.3 V clamp; conditional 46.7 V margin. RDS(on) 16 mΩ max at specified gate/25°C; hot SOA/loss open."
            rating="25°C conduction screen is in calc-results; hot RDS and fault SOA not signed."
            absmax="VDS conditional margin +46.7 V; transient, gate and SOA margins open."
            verdict="KISMİ"
        elif ref in ("L1","L2"):
            exact="Candidate MPN: IHLP4040DZER6R8M01; official cross-reference document #34509 p1; not yet approved or entered in canonical BOM."
            evidence="Vishay IHLP-4040DZ-L1 datasheet p1 and cross-reference document #34509 p1; links in REQUIREMENTS.md."
            pkg="Generic 4040 family land; exact part suffix and pad/height match open."
            stress="6.8 µH ±20%, DCR max23.3 mΩ, Isat13.5 A at ≈20% inductance drop, heat-rating current8 A at 40°C rise per Vishay p1 table. Calculated peak5.583 A under +10% share assumption."
            rating="Saturation headroom screen +7.917 A; 8 A heat-rating vs calculated per-phase RMS and ambient/board thermal remains to verify. Candidate exact MPN is not selected."
            absmax="Conditional Isat headroom +7.917 A; coil temperature remains unverified."
            verdict="KISMİ"
        elif ref=="F1":
            exact="UNRESOLVED — `10A` is placeholder only; no manufacturer or MPN selected."
            pkg="No footprint/holder in BOM."
            stress="Prospective battery/cable short current unknown; 10 A value is not approved."
            rating="DC interrupt, time-current, I²t, temperature derating and coordination with TVS/Q1 unknown."
            absmax="Cannot verify."
            verdict="FAIL/AÇIK"
        elif ref in ("J1","J2","J3"):
            exact="Candidate header MPN: Molex 43045-0200 from existing footprint/value and Molex part page; matching housing, terminal and cable MPN absent."
            evidence="Molex 43045-0200 official product page (2 circuits, right-angle, 8.5 A/contact) and PS-43045-001 Rev P5 p8; links in REQUIREMENTS.md."
            pkg="Footprint nominal two-circuit horizontal Micro-Fit 3.0; pin pitch/key/polarity mating-part and pad geometry need exact drawing check."
            stress="Molex spec: 18 AWG W-B up to8.5 A; W-W7 A; 20 AWG W-B7 A. J2 7.5 A target fails W-W/20AWG W-B."
            rating="Harness, contact, ambient and connector derating unspecified."
            absmax="Conditional 18 AWG W-B margin+1.0 A; actual wiring configuration absent."
            stock="Current connector/contact/cable stock/lifecycle not verified."
            verdict="KISMİ"
        elif ref in ("D1","D2","D3"):
            exact="Generic family only; exact manufacturer MPN not supplied."
            pkg="SMCJ family or SMA family nominal footprint; vendor mechanical tolerance and pad match open."
            stress="D1 SMCJ33A assumed 33 V standoff/53.3 V clamp at specified pulse; D2/D3 SS34 family is nominal 3 A/40 V only if exact datasheet matches."
            rating="TVS pulse energy/clamp and Schottky continuous/transient current not qualified; D2/D3 path current role must be confirmed."
            absmax="D1 conditional +6.7 V LM74700 operating margin to60 V; clamp transients/energy open. D2/D3 voltage/current exact MPN open."
            verdict="AÇIK"
        elif ref=="U5":
            exact="`LM74700` generic value; exact orderable Q1 suffix/MPN not entered."
            pkg="SOT-23-6 nominal footprint; exact manufacturer suffix/package drawing needs check."
            stress="60 V operating/65 V absolute ANODE; conditional +6.7/+11.7 V to 53.3 V clamp."
            rating="Gate drive, reverse event and thermal under fault not measured."
            absmax="Conditional to clamp only; surge margin open."
            verdict="AÇIK"
        elif ref.startswith("R"):
            stress="Current/power derived from value and network; resistor max voltage/power not populated."
            rating="Need tolerance/TCR and rating data; standard 0603 is not a derating proof."
        elif ref.startswith("C"):
            stress="For CIN/CBIN on VIN use 53.3 V assumed clamp and require ≥80 V rating; for bootstrap/COMP/eFuse capacitors use their pin differential datasheet stress. Exact voltage rating is not populated."
            rating="Ceramic DC-bias Ceff/tolerance/temperature/aging and ≤50% voltage-rating rule cannot be checked without exact MPN."
        if not mpn and ref.startswith("R") and ref not in ("RFB1","RFB2","RIMON1","RIMON2"):
            exact="UNRESOLVED — no exact MPN; select by value, tolerance/TCR, package and power screen."
        if not mpn and ref.startswith("C") and not ref.startswith("COUT"):
            exact="UNRESOLVED — no exact MPN; select dielectric/voltage/derated-Ceff/package by node stress."
        rows.append([ref,value,mpn or "",exact,fp,pkg,stress,rating,absmax,stock,verdict,evidence])
    path=OUT/"bom-verification.csv"
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f); w.writerow(["Reference","Value","MPN_in_BOM","MPN_candidate_or_status","Footprint_assessment","Package_footprint_match","Voltage_current_power_derating","Tolerance_TCR_DC_bias_requirement","Absolute_max_margin","Stock_lifecycle","Status","Evidence"]); w.writerows(rows)
    blanks=sum(1 for x in rows if not x[2])
    write("BOM-OPEN-ITEMS.md",f"""
# BOM doğrulama açıkları

- Satır işlendi: **{len(rows)}/73**.
- BOM MPN sütunu boş: **{blanks}** satır. Hiçbir MPN uydurulmadı; Value alanından kesin kimlik yalnız Q1 ve konektör family candidate olarak not edildi, sipariş kodu diye onaylanmadı.
- F1 ve yuva/footprint seçilmedi; short current, DC interrupt ve I²t koordinasyonu açık.
- L1/L2 candidate IHLP4040DZER6R8M01 found from Vishay official cross-reference; BOM approval, stock, hot DCR and land match remain open.
- J1/J2/J3 mating housing/contact/cable absent. 7.5 A target requires exact 18 AWG wire-to-board setup; wire-to-wire 18 AWG 7 A published maximum is below target.
- SMCJ33A/SS34 generic manufacturerless family; exact TVS pulse/thermal and diode-current roles open.
- RS1/RS2 exact shunt, power/TCR/tolerance missing; recommended selection screen ≥0.5 W, ≤1% and ≤100 ppm/K, subject to vendor qualification.
- CIN/CBIN/CEFOUT and other generic MLCCs have no voltage rating or manufacturer; CIN/CBIN on the protected VIN node need a ≥80 V candidate to satisfy 1.5×53.3 V assumed clamp screen. 10 µF port Ceff under 11 V DC bias is unknown.
- Current live inventory/lifecycle was not verifiable for any line; no stale cached quantity is presented as current.
- Exact datasheet verification for generic R/C and SS34 cannot be completed without exact manufacturer/MPN input. Ask for PDFs/approved vendor list rather than inferring family data.

Row detail: [`bom-verification.csv`](bom-verification.csv).
""")

def summary():
    sim_path=OUT/"sim-results.json"
    sim=json.loads(sim_path.read_text(encoding="utf-8")) if sim_path.exists() else {"families":[]}
    done=sum(1 for f in sim.get("families",[]) if f["completed"])
    model_pass=sum(1 for f in sim.get("families",[]) if f["criterion_pass"])
    model_fail=", ".join(f["family"] for f in sim.get("families",[]) if f["completed"] and not f["criterion_pass"])
    rows=[
      ("Gereksinimler", "20–26 V; 11 V/7 A; capacity7.5 A; O1≤12.0 V; ports not measured", "REPO/AÇIK", "REQUIREMENTS.md", "frozen"),
      ("Buck/FB", "ΔIL2.916 A; phase peak5.583 A assumption; FB10.8333–11.1605 V; Vishay Isat13.5 A", "HESAP/DATASHEET/VARSAYIM", "calc-results.json/.md", "phase share and exact L BOM approval open"),
      ("Loop/UVLO", "RCOMP sensitivity10.0–26.1k; 174k/10k UVLO upper19.69 V before leakage/TCR", "VARSAYIM/AÇIK", "calc-results.json; OVP-UVLO-DECISION.md", "FRA and battery cutoff policy open"),
      ("O1 OVP", "Existing 16.89 V FAIL; ideal candidate sim11.974 V PASS model only", "SİM/FAIL", "sim-results.json; OVP-UVLO-DECISION.md", "physical injection required"),
      ("eFuse/protection", "ILIM nominal4.96/2.53 A; sum7.4877 A <7.5 A FAIL; F1/I²t and Q1 SOA open", "HESAP/FAIL/AÇIK", "calc-results.json", "source/cable/MPN evidence needed"),
      ("Targeted sim", f"{done}/5 families complete; {model_pass} model gates pass; model FAIL: {model_fail}; no physical proof", "SİM", "SIMULATION-RESULTS.md", "family2/4 FAIL retained"),
      ("Prior WP1/WP2", "WP1 4 ESL incomplete + N-01; WP2 historical 161/69/6, no new electrical run", "SİM/FAIL/AÇIK", "PREVIOUS-WP-COMPARISON.md", "all open findings retained"),
      ("BOM", "73/73 rows reviewed; exact MPN/stock/package gaps listed", "DATASHEET/AÇIK", "bom-verification.csv; BOM-OPEN-ITEMS.md", "procurement open"),
      ("Next phase", "T0–T6 and schematic/PCB change list ready", "HESAP/VARSAYIM", "BENCH-ACCEPTANCE.md; KICAD-CHANGE-LIST.md", "transfer input"),
    ]
    table="| Madde | Sonuç | Etiket | Kanıt dosyası | Durum |\n|---|---|---|---|---|\n"+"\n".join("| %s | %s | %s | `%s` | %s |"%r for r in rows)
    write("G1-SUMMARY.md",f"""
# G1 AI analiz özeti

Dal `wp/g1-ai-analysis`; 6S LiPo PDU için hesap/simülasyon/karar ve sonraki faz girdileri. `*.kicad_*` değiştirilmedi.

{table}

## Fiziksel kabul olmadan kapanmayanlar

- O1 anlık tepe ≤12.0 V OVP hata enjeksiyonu; mevcut 16.9 V eFuse FAIL.
- WP1 dört ESL tamamlanmaması ve N-01 üst sınırı; WP2 katı tarihsel 69 FAIL / 6 eksik.
- Gerçek 7 A/7.5 A yük profili, iki faz current sharing ve 20 V yeniden kalkış.
- Döngü Bode: PM≥45°, GM≥6 dB ve transient testi.
- F1/kablo/batarya kısa devre akımı, DC kesme/I²t, TVS/Q1 SOA koordinasyonu.
- Kart termal dengesi, konektör/kablo, footprint ve üretim land/stencil.
- MPN/stok ve tasarım ortam sıcaklığı.

## Benden gereken girdiler/PDF'ler

1. O1 ve S2E ölçülmüş startup/continuous/peak akım dalga şekilleri ve yük bölüşümü.
2. Batarya iç direnci/kısa devre akımı, hücre üretici cutoff'u, kablo uzunluğu/kesiti/konnektör mating seti.
3. Ortam ve enclosure sıcaklığı, airflow ve kart copper stackup/fabricator minimum plating.
4. F1/holder, shunt RS, IHLP inductor, TVS ve generic C/R için onaylı MPN/vendor PDFs veya AVL.
5. OVP için izin verilen recovery/latch/reset davranışı ve 10 µF port capacitance minimum tolerans/DC-bias datasheet.
6. O1 ≤12 V sınırında ölçüm bandwidth/probe uncertainty payının kullanıcı tarafından onayı.
""")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    requirements(); decision(); handoff_docs(); bom_report(); summary()

if __name__=="__main__": main()
