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
