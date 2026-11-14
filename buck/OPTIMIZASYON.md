# Güç katı optimizasyonu ve doğrulama

**Tarih:** 12 Kasım 2026 · **Araç:** LTspice 26.1.1 (toplu kip), Python 3.14.5 · ideal anahtar/diyot, L/C + ESR/DCR + çıkış sönüm dalı Cd–Rd (§9.3 ve §9.4'teki ideal olmayan senaryolar ayrıca belirtilmiştir) · **Fiziksel ölçüm yok.**

**Dondurma durumu: FROZEN (simülasyon dondurması, 12 Kasım 2026):** çıkış sönüm dalı (`Cd = 470 µF + seri Rd = 0,22 Ω`) eklendi ve §13'te belirtilen test kipleri koşuldu; `Cout` ve `Cd` için ≥ 35 V, `Cin` için ≥ 50 V gerilim sınıfı kabul edildi; §12.1 kapısındaki 1–12 numaralı maddelerin tamamı kullanıcı onayı dahil kapandı. Güncel iş sırası: gereksinimler ve kontrol mimarisi, ardından birlikte parça değerlendirmesi ve ölçümler (§12.2).

**Güncel gereksinim notu (13.11.2026):** Kullanıcı, sonraki kapalı çevrim tasarımı için genel 0–7,5 A modülde 11 V ±%5 kararlı durum ve ≤ 165 mV t-t ripple hedeflerini onayladı. Referans cihazların ortak çalışma aralığı 9–12 V'tur; arızada enerjinin kesilmesi kabul edilir, O1 girişinde 12 V üst sınırı korunmalıdır. Kullanıcı amacı her olası yük basamağında gerilimi sürdürmek değil arızada cihazları korumak olarak açıkladı; geçiş ve arıza kapsamları ayrıntılandırılacak, hedefler henüz doğrulanmadı. §12.1 ve §13'te genel sınırların tanımsızlığına ilişkin ifadeler 12.11.2026 dondurma ve tarihli koşuların koşuludur, güncel karar değildir. Mimari ara değerlendirme [yol haritasındadır](../YOL-HARITASI.md).

Etiketler: **DATASHEET** üretici belgesi · **ÇIKARIM** üretici şemasından veya eğrisinden okunan, doğrulanmamış · **TAHMİN** yayımlanmış değer yok · **HESAP** `python buck/hesap.py` · **SİM** `python buck/dogrula.py` · **ÖLÇÜM** fiziksel (bu belgede hiç yok).

Bu belge güncel kararı anlatır. Değerler parça numarasından bağımsızdır; parça kriterleri [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md) dosyasındadır.

### Kontrol ve bağımsız koruma mimarisi karşılaştırması (13.11.2026)

Bu bölüm mimari değerlendirmedir; aşağıdaki ayrı bölümde geçici kapalı çevrim SİM sonuçları yer alır. Parça sırası değiştirilmedi, kalıcı kontrol veya koruma devresi tasarlanmadı ve fiziksel ÖLÇÜM yapılmadı. Maliyet sırası nicel fiyat karşılaştırması değildir: üretici, stok, tedarik, ek elemanlar, soğutma ve işçilik bilinmeden en ucuz seçenek belirlenemez. Sınırlar: girişte 20–26 V referans aralığı, +5…+50 °C geçici ortam, 11 V ±%5 kararlı çıkış, 0–7,5 A, ≤ 165 mV t-t ripple, O1 girişinde 12 V üst sınırı; arızada ortak çıkış kesilebilir.

**Kontrol yöntemleri:**

1. **Akım kipli sabit frekanslı analog kontrolcü + harici S1/D1:** 100 kHz'lik asenkron referansla birlikte ilk incelenecek mimaridir. Akım algılama ve döngü başına sınırlama bazı kontrolcülerde bulunur; dış kompanzasyon, akım algılama elemanları ve sürme beslemesi kontrolcüye göre değişir. D≈%50 üzeri çalışmada eğim kompanzasyonu, gürültü, kısa devre davranışı ve akım sınırının toleransı kontrol edilmelidir. Sınır tepe bobin akımıdır, 7,5 A ortalama yük akımıyla aynı değildir. Üretici karşılaştırması: [Analog Devices, Choose the Right Regulator, Part 1](https://www.analog.com/en/resources/technical-articles/2022/07/16/11/59/choose-the-right-regulator-for-the-job-part-1-regulator-control-schemes.html).
2. **Gerilim kipli sabit frekanslı kontrol:** mevcut güç katıyla prensipte kullanılabilir; akım sınırı ve kompanzasyon uygulaması farklı olabilir. LC çift kutbu, Cd–Rd kolu, CPL ve CCM/DCM geçişinde yeterli kararlılık gösterilmelidir. Önceki genel PI örneği yöntemi elemez; 14.11'de açık RC durumlarıyla kurulan Type-III model seçilmiş geçici testleri geçti (§15). Daha ucuz olduğu veya daha çok parça gerektireceği seçim yapılmadan söylenemez. [TI, Buck Converter Architectures](https://www.ti.com/content/dam/videos/external-videos/en-us/1/3816841626001/3873670638001.mp4/subassets/4.1-overview-presentation.pdf).
3. **Sabit iletim süreli / histeretik veya iç kompanzasyonlu kontrol:** az harici ayar elemanı sunabilir; frekans ve ripple yükle değişebilir, belirli çıkış filtresi ve ESR aralığı gerekebilir. 33 µH, 1000 µF, 470 µF + 0,22 Ω, 0 A ve ≤ 165 mV ripple uyumu aday veri sayfası ve kapalı çevrim testleriyle gösterilmeden basit sayılmaz. Sabit 100 kHz açık çevrim test sonuçları doğrudan aktarılmaz.
4. **Tümleşik anahtarlı dönüştürücü / senkron güç katı:** ayrı anahtar veya diyodu azaltabilir ve verimi değiştirebilir; mevcut asenkron güç katını değiştirir, dolayısıyla korunmuş başlangıç referansı olarak seçilemez. Kullanıcı isterse sonradan ayrı karşılaştırma ve yeniden doğrulama gerekir.
5. **Ortalama akım kipli analog kontrol:** akımın ortalamasını ayrıca düzenleyebilir ve akım paylaşımı / sabit akım gerekirse yarar sağlayabilir; bu PDU'nun ana ihtiyacı sabit 11 V olduğundan ek akım döngüsü ve kompanzasyonu ilk seçim için gerekçelendirilmedi. 33 µH, DCM/CCM geçişi ve 0,9–4,5 kHz çıkış kutup/sıfırlarıyla test edilmedi.
6. **Dijital PWM (MCU):** Vin/yük kestirimi, kaydedilebilir hata ve daha esnek başlatma mantığı sağlar; ADC örnekleme gecikmesi, PWM/ölçüm çözünürlüğü, firmware hatası, watchdog ve güvenli varsayılan çıkış gibi yeni işler getirir. Bu basit bir 11 V buck için en ucuz/kolay seçenek gösterilmedi; hızlı bağımsız OVP yine analog donanım olmalıdır. Dijital kontrol simüle edilmedi.

**Geri besleme yapısı:** Gerilim döngüsü, çıkış bölücüsünden 11 V hedefini tutar; akım kipli PWM'in çevrim içi akım algısı ayrı iç kontrol/koruma sinyalidir. Akım limiti, PDU'yu sabit akım kaynağına çevirme hedefi değildir. İlk düzenlemede gerilim geri beslemesi Cout uçlarından (koruma kesicisinden önce) Kelvin alınır; OVP ise anahtarın yük tarafındaki gerçek ortak porta bakar. Böylece OVP açıldığında kontrolör yanlışlıkla sıfır geri besleme görüp duty'yi sona sürmez. Bu seçim koruma MOSFET'inin seri direncindeki düşümü telafi etmez; 7,5 A'de örnek 10 mΩ 75 mV/0,56 W'tır. Portun 10,45–11,55 V regülasyonu ayrıca doğrulanır. OVP eşiğinin **en düşük** değeri normal/165 mV ripple tepesinin üstünde, en yüksek eşik + tolerans + algılama/kapama gecikmesi kaynaklı aşım ise O1 portunda 12 V'un altında olmalıdır. Yaklaşık 285 mV'luk (11,715→12 V) en ihtiyatlı örnek pay; kontrol, koruma ve yük portu toleranslarına ayrılmadan eşik değeri seçilemez.

**Kontrol yöntemi karar matrisi (parça değil):**

| Yöntem | Bu güç katıyla uyum | Güçlü yön | Ana risk/ek iş | Bu projedeki kanıt | Şu anki karar |
|---|---|---|---|---|---|
| Sabit frekans tepe akım kipli analog | Yüksek; harici üst N-MOSFET/asenkron D1'le doğrudan denetleyici bulunabilir | Hat/yük geçişi başına hızlı PWM tepkisi; akım sınırı ve soft-start bazı tek çiplerde | Akım algı gürültüsü, slope compensation, threshold toleransı, algılama elemanı kaybı | LT3844 modeli iyi davranış gösterdi; akım sınırı marjı yok, gerçek OVP ayrı | **Önerilen başlangıç yöntemi** |
| Sabit frekans gerilim kipli analog | Topolojiye bağlı | Normal gerilim döngüsü akım kipinden ayrıdır; akım algı elemanı tasarrufu olasılığı | LC/CPL kompanzasyonu; çevrim-başı sınır için ayrıca gerçek akım algılama gerekir | Genel PI örneği zayıftı; Type-III RC modeli §15'te seçilmiş testleri geçti, gerçek entegre/sense yok | Akım kipiyle eş aday; maliyet/verim kanıtı yok |
| Histeretik/COT | Adaya bağlı | Bazı IC'lerde az dış kompanzasyon | Frekans değişkenliği, ESR/filtre ve ripple bağımlılığı | Bu güç katında test yok | Puanlanmadı |
| Ortalama akım analog | Harici güç katıyla mümkün | Akım düzenleme daha hassas | İkinci döngü, ölçüm ve kompanzasyon maliyeti | Test yok; sabit 11 V için gerekli değil | Şimdilik fazla karmaşık |
| Dijital PWM/MCU | Harici güç katıyla mümkün | Ayarlanabilir ve tanılama esnekliği | Firmware, ADC gecikmesi/çözünürlüğü, doğrulama ve yine de bağımsız analog OVP | Test yok | Hedef için gereksiz karmaşıklık |
| Senkron/tümleşik buck | Güç katısını değiştirir | Potansiyel verim/BOM avantajı | D1 yerine alt anahtar ve yeni doğrulama; açık çevrim dondurmasını değiştirir | Bu istekte test edilmedi | Kullanıcı onayı olmadan kapsam dışı |

**Sürücü ve kalkış:** Üst taraf N-MOSFET sürmek için gate gerilimi source'a göre sağlanmalı; bootstrap bir olasılıktır ama hafif yükte ve sıfır akımda yeterli şarj süresi kanıtlanmalıdır. [Analog Devices AN-2582](https://www.analog.com/en/resources/app-notes/an-2582.html) bu sorunu açıklar; belgede verilen koşullar bu devrede oluşmuş ölçüm değildir. `hesap.py` 20–26 V / 7,5 A için 4,36–5,64 µs iletim süresi verir; hafif yükte farklıdır ve kontrolcünün minimum iletim/kapanma süreleri ayrıca incelenir. 5 ms ideal duty rampası en düşük Z0 köşesinde 12,8 A verdi (§5.8); kontrolcüye ait soft-start süresi bu testteki duty rampasıyla eşit sayılamaz. Kalkış akımı, gerçek soft-start yöntemi, yük ve toleranslarla yeniden sınanmalıdır.

**Aşırı gerilim mimarileri:**

- **Yalnız kontrolcü OVP / PWM kapama:** ek işlev içeriyorsa devre basitleşebilir, fakat S1 fiziksel kısa devresinde giriş hâlâ çıkışa ulaşabilir; bağımsız yük koruması yerine kabul edilmez. [Analog Devices, LTM4641 koruma açıklaması](https://www.analog.com/en/resources/technical-articles/10a-module-step-down-regulator-with-advanced-input-and-load-protection.html).
- **Dönüştürücü çıkışından sonra bağımsız elektronik ayırıcı:** ayrı referans/eşik ve seri geçiş anahtarı veya uygun entegre koruma ile her iki cihaz aynı anda ayrılabilir. İlk araştırma için mantıklı yön; fakat 7,5 A sürekli akım, tolerans, başlatma, ısınma ve arızada kapalı kalma, en yüksek hatalı giriş gerilimi, algılama noktası, tepki süresi, kapasite ve çıkış parazitleri gösterilmelidir. Koruma anahtarının body-diyot yönü/ters akım yolları incelenmeli; tek MOSFET her yönde engeller varsayılmaz. [TI, karşılaştırıcılı OVP](https://www.ti.com/tool/CIRCUIT060079); [Analog Devices, sistem koruması](https://www.analog.com/en/resources/technical-articles/complete-system-power-protection-design-guide.html).
- **Giriş ayırıcı:** güç katı arızasında kaynağı kesebilir, ancak bobin ve Cout/Cd'deki enerji ve hatalı S1 üzerinden akım yolu çıkışa aktarılabileceğinden tek başına O1 gerilim tepesini koruduğu varsayılamaz. Ayrı yük ayırıcısıyla karşılaştırılmalıdır.
- **Crowbar + sigorta:** aşırı gerilimde çıkışı kısa devre ederek sigortanın açmasını amaçlar. Büyük akım ve enerji, LiPo kaynağı, sigorta açma süresi ve kesme kapasitesi, anahtar dayanımı ve 12 V aşımı ayrıca gösterilmelidir. Yalnız bir sigorta gerilimi algılamaz. Örnek prensip: [TI, TPS5210 uygulama notu](https://www.ti.com/lit/an/slva044/slva044.pdf).
- **TVS / zener:** kısa darbelerde yardımcı olabilir; kelepçeleme gerilimi akımla yükselir ve sürekli güçlü arızada enerji kapasitesi aşılabilir. 11 V normal çalışma ile 12 V mutlak üst sınırı arasındaki dar pencerede tek başına yeterlilik kanıtlanmadı; ek koruma olarak bile gerçek eğri ve enerji incelenmeli.
- **Röle:** yalıtım sağlayabilir fakat açılma süresi, kontak ömrü, sıçrama ve bobin beslemesi nedeniyle hızlı aşımın tek koruması olduğu varsayılmaz. Gerçek süre ve O1 gerilim eğrisiyle doğrulanmalıdır.

**HESAP örnekleri — seçilmiş parça veya garanti değildir:** 7,5 A'de seri anahtar direnci 5 / 10 / 20 mΩ ise gerilim düşümü 37,5 / 75 / 150 mV, iletim kaybı 0,281 / 0,563 / 1,125 W olur (`I·R`, `I²·R`); gerçek sıcak direnç, akım dağılımı ve ısıl yol bilinmiyor. 11,55 V kararlı ortalama üst sınırı ve 165 mV t-t ripple için, dalga şekli simetrisi varsaymadan tüm ripple'ın yukarıda olduğu ihtiyatlı örnekte 11,715 V tepe ve 12 V'a 285 mV kalır; toleranslar, transient ve ölçüm noktası ayrıca değerlendirilir. Örnek olarak 8 A yalnız 100 µF'ye akarsa dV/dt = 0,08 V/µs; 1 µs'de 80 mV artış olur. Bu kapasite ve akım cihazların gerçek değerleri değildir; gerçek ağ ve arıza akımıyla kapanma öncesi aşım hesaplanmalıdır.

**Algılama ve doğrulama:** Koruma öncesi ve cihaz tarafı gerilimler farklıdır; koruma sonrası algılama, hat düşümü ve yük kapasitansı kompanzasyon kararlılığını etkileyebilir. Dönüştürücü tarafında algılama daha basit olabilir ama seri kayıp yükteki gerilimi düşürür; hangisi seçilirse açık anahtar, kablo kopması, prebias, yük kapasitansı ve geri besleme kararlılığı sınanır. Koruma bağımsız referans ve besleme dahil arıza etki alanı için incelenir; UVLO, başlangıçta varsayılan kapalı durum, arızadan sonra yeniden açılma ve kısa aralıklı denemelerde tekrarlanan aşım değerlendirilir. O1 portunda ve koruma öncesinde aynı anda en yüksek gerilim, eşik min/maks ve gecikme dahil gösterilmeden koruma PASS değildir.

**Açık kararlar:** Uygun kontrolcü/koruma adayları araştırıldı; gerçek fiyat/BOM ve üretilebilirlik karşılaştırması eksiktir, mevcut parça sırası değişmez. Motor kaynaklı geçiciler çalışma kapsamı dışı bırakıldı; bu koşullar veya yayımlanmamış O1 mutlak maksimumu hakkında garanti verilmez. Giriş 20 V altı / 26 V üstü kesme ve OVP sonrası latch/otomatik yeniden başlatma seçilmedi. Kod denetimi kısmi; `zarf` çıktısında genel sınırlar onaylanmadı ifadesi eskidir, test açık çevrimdir ve kapalı çevrim sonucu vermez.

### Geçici kapalı çevrim ve koruma denemeleri (13.11.2026)

**Kapsam ve sınır:** Kullanıcı isteğiyle dosyalar depo dışındaki `%TEMP%\pdu-control-study-20261113` altında üretildi; ana `.asc`, değerler ve aday sırası değiştirilmedi. LTspice 26.1.1, üretici LT3844/LTC4365 modelleri; güç anahtarı/diyot ideal veya aşağıda belirtilen yaklaşık VDMOS'tur. Güç katı referans değerleri L=33 µH, DCR=7,81 mΩ, Cout=1000 µF/35 mΩ, Cd=470 µF/Rd=0,22 Ω, Cin=2×1000 µF/15 mΩ, S1=5,6 mΩ, D1=0,38 V+8 mΩ. LT3844 için **yalnız geçici testte** indüktör çıkışına 10 mΩ algılama direnci eklendi; orijinal dondurma güncellenmedi. FSET=191 kΩ ile ham dalgadaki tam yük anahtarlaması yaklaşık **106 kHz**, tam 100 kHz değil; 150 kΩ ile yapılan önceki yaklaşık 130 kHz denemeleri bu karşılaştırmaya katılmadı. Çalışma 27 °C simülatör ayarında; gerçek +5…+50 °C tolerans köşeleri değildir. Gerilim kipli PI örneği genel davranışsal modeldir, gerçek entegre değildir; akım sınırı, gerçek sürücü ve koruma içermez.

**Kontrol denemeleri — SİM:**

| Durum | LT3844 üretici modeli + ideal güç katı | Genel PI + ideal güç katı | Sınır |
|---|---|---|---|
| 20 V, 7,5 A direnç | 10,9937 V ortalama; 42,48 mV t-t | 11,0000 V; 44,98 mV t-t | 25–30 ms ortalama, 29–30 ms ripple |
| 24,6 V, 7,5 A direnç | 10,99516 V; 52,70 mV t-t | 11,0000 V; 55,67 mV t-t | LT 100 ns; PI 100 ns |
| 26 V, 7,5 A direnç | 10,99552 V; 55,03 mV t-t | 11,0000 V; 58,19 mV t-t | 25–30 ms ortalama |
| 200 ms CPL 41,25→82,5 W→41,25 W | 10,8385–11,1519 V; bobin tepe 9,889 A | 10,6354–11,3528 V; bobin tepe 11,315 A | 24,6 V; 20 µs yük rampası; 20–230 ms ölçüm; öncesinde direnç yükünden CPL'ye geçiş |
| Giriş 24,6→20→26 V | 10,9551–11,0436 V; bobin tepe 8,701 A | 9,6610–12,8937 V; bobin tepe 19,139 A | 7,5 A direnç; her giriş rampası 100 µs; 20–40 ms ölçüm |
| 0,24 A ve 0 A | yaklaşık VDMOS ile sırasıyla 11,00145 V/30,59 mV, 11,00269 V/7,97 mV | sırasıyla 11,1796 V/52,97 mV, 12,00184 V/0,013 mV | 24,6 V; 25–30 ms ortalama, 29–30 ms ripple; 0 A, 1 GΩ model yükü |

LT hafif yük ilk ideal-SW denemesi aşırı yavaş ilerledi ve kesildi; daha sonra depodaki §9.3'ten **veri sayfasından türetilmiş yaklaşık VDMOS** kullanıldı, ST üretici MOSFET modeli değildir. 0 A'da PI yaklaşık 12 V'ta kaldı ve 11 V ±%5 kararlı durum hedefini sağlamadı; ideal 1 GΩ yükte aşırı gerilim boşalmasının gerçek yüklerle aynı olacağı varsayılmaz. LT giriş ve CPL sonuçları koruma devresi olmadan; her yöntem farklı kontrol ayarı ve eklerle test edildiğinden yalnız bu somut modeller karşılaştırılabilir. PI giriş testi başlangıçta iç integratörün gerçekçi olmayan DC başlangıcı nedeniyle geçersizdi; `.ic V(integ)=0` ile düzeltildi ve yukarıdaki sonuçlar tekrar koşuldu. PI için Kp=0,01/0,03/0,05 ve integratör katsayısı 0,00003/0,0001/0,0003 A/V dokuz kombinasyonda giriş testinde tepe 12,468–14,622 V oldu; tüm PI yöntemlerinin sınırı değildir. En düşük tepe 50 ns tekrarında 12,474 V'tur.

**Bağımsız kontrol ve sayısal yakınsama:** `.meas` çıktılarındaki Vmin/Vmax ve ortalamalar, ham `.raw` dalgasının bağımsız NumPy zaman ağırlıklı analiziyle karşılaştırıldı. LT tam yük 24,6 V: 100/50 ns'te 10,995163/10,995164 V ve 52,697/52,506 mV. 200 ms CPL: 200/100 ns LT 10,83850–11,15188 / 10,83890–11,15148 V; PI 10,63545–11,35282 / 10,63790–11,35132 V. Son iki 1,2 ms pencerede filtrelenmiş salınım LT yaklaşık 2,0 mV t-t; sonuç yalnız bu yük/model içindir. Giriş testi LT 100/50 ns 10,95510–11,04360 / 10,95501–11,04348 V; PI 9,66098–12,89368 / 9,66264–12,89577 V. İki zaman adımı ve ayrı okuma **aynı modelin sayısal kontrolüdür**; bağımsız fiziksel doğrulama veya bağımsız model değildir.

**Koruma denemeleri — SİM, koşul bağımlı:** LTC4365 üretici modeli ve 10 mΩ ideal seri ayırıcı, 2,2 nF ideal gate yükü, cihaz tarafında 100 µF/20 mΩ ve 1,4667 Ω yük ile LT3844 güç katına bağlandı. 24,6 V ideal kaynak, 48 ms'de anahtara paralel 1 mΩ kısa devre: koruma öncesi tepe 32,6368 V, cihaz tarafı 11,79703 V, bobin tepe 72,18 A; 50 ns tekrarında 32,6368 V / 11,79708 V / 72,18 A. Kısa devre bobini doğrusal kabul eder; gate ideal ve FET gövde diyodu, kapı–dren kapasitansı ve gerçek yük bilinmez. 72 A'de bobin doyumu/gerçek kaynak empedansı kapsanmaz. Yalnız **bu benzetim köşesinde** cihaz tarafı 12 V altındadır; koruma veya güç elemanlarının güvenliği doğrulanmadı.

Aynı birleşik kısa devre denemesinde, yalnız yük tarafındaki varsayılan kapasite 10 µF ve 1000 µF yapıldığında cihaz tarafı tepeleri sırasıyla **11,81995 V ve 11,66786 V**; koruma öncesi tepeler 32,59353 V ve 32,86535 V, bobin tepeleri 71,79 A ve 74,22 A oldu (100 ns). 50 ns tekrarında cihaz tarafı tepeleri sırasıyla 11,82014 V ve 11,66806 V'tur; her iki kapasitede tepe ayrıca ham dalgadan okundu. Bu üç kapasite cihazların ölçülmüş giriş kapasiteleri değildir; 1000 µF koşusunda ayırmadan sonra depolanan enerji nedeniyle 51–52 ms arası cihaz tarafı ortalaması hâlâ yaklaşık 1,15 V'tur. Bu sonuçlar doğrusal bobin ve ideal ayırıcı sınırlarını ortadan kaldırmaz.

Ayrı bir **sentetik sert giriş** testinde aynı LTC4365 modeli, 10 mΩ ideal ayırıcı, 11→25 V ideal kaynak rampası, 1,4667 Ω yük, cihaz tarafı 10/100/1000 µF (20 mΩ ESR) ile denendi. 1 µs rampada tepeler sırasıyla 23,401 / 20,834 / 20,227 V; 10 µs rampada 13,293 / 12,806 / 12,624 V'tur. 10 µF/1 µs örneği 20 ns tekrarında 23,277 V; 100 µF/10 µs 50 ns tekrarında 12,807 V. Bütün tepeler ayrı ham dalga okumalarıyla da kontrol edildi. 1 µs veya 10 µs rampalar gerçek PDU arıza dalgası olarak doğrulanmadı; bunlar modele zorla uygulanan sınama girdileridir. LTC4365-1'de 100 µF/10 µs koşusu 100/50 ns'te 13,060/13,061 V. Bu sonuçlar, seçilen ayırıcı modelinin ve eşiğin söz konusu zorlanmalarda yetersiz olduğunu gösterir; entegrelerin bütün gerçek devrelerde başarısızlığını göstermez.

Ek **davranışsal ideal koruma** testinde 11,7 V nominal eşik, 100 µF/20 mΩ yük tarafı kapasitesi, 10 mΩ ideal seri anahtar ve sabit 0,2/1/4 µs gecikme varsayıldı; gerçek koruma entegresi veya gerçek MOSFET modeli değildir. 11→25 V / 1 µs giriş rampası için sırasıyla 13,294 / 20,973 / 23,415 V; 10 µs rampası için 11,611 / 12,467 / 16,109 V tepe bulundu. 0,2 µs gecikme / 1 µs rampası 10 ns tekrarında 13,293 V'tur. Eşik/kapı toleransı, parazitikler ve gerçek cihaz kapasitesi bilinmemektedir.

**LM5088 ve diğerleri:** TI'nin şifresiz PSpice transient modeli LTspice'ta nominal ilk koşuda ve Gear/UIC denemesinde yakınsamadı; bir üçüncü kısa denemede tolerans uyarılarıyla ilerleme durdu ve kesildi. Bu, LM5088'in elektriksel başarısızlığı değildir. Model metninde RST pini yalnız 1 GΩ ile toprağa bağlanmış göründüğünden hiccup işlevi bu modelle doğrulanmış sayılamaz. MAX6495 üretici modeli, gerçek direnç/kapasitör toleransları, gerçek MOSFET kapama/parazitleri, ısıl davranış, diğer adaylar ve gerçek ölçüm test edilmedi. Kesin sıralama veya tüm olasılıkların tarandığı iddia edilmez.

**Puanlama — yeniden koşulan belirli modeller, 100 puanlık tarama:** Güç katına uyum 15; 20–26 V tam-yük regülasyonu 10; giriş geçişi 15; 200 ms CPL adımı 15; hafif/yüksüz çalışma 10; yumuşak kalkış ve akım sınırı 15; bağımsız OVP 10; maliyet/uygulama kolaylığı 5; verim kanıtı 5. Bu, aynı anda gerçekten kurulmuş iki eşdeğer devrenin karşılaştırması değildir: PI genel davranışsal örnektir, LT3844'te güç anahtarı/diyot çoğu koşuda idealdir. **LT3844 test düzeni:** 15+10+15+15+10+6+0+[0–5]+[0–5] = **71–81/100**. **PI test örneği:** 15+10+0+15+0+0+0+[0–5]+[0–5] = **40–50/100**. Maliyet ve verim için veri olmadığı için aralık bırakılmıştır; LT'nin OVP testi 12 V'u aştığından koruma puanı sıfırdır. Bu puanlar yalnız test edilmiş örneklere aittir, analog akım kipinin veya gerilim kipinin genel puanı değildir. LM5088 yakınsamadığından puanlanamaz. OVP **zorunlu güvenlik kapısıdır**: puan aralığı ne olursa olsun, portta 12 V sınırı kanıtlanmadığı için gerçek yüke geçişe izin vermez.

### Önceki yöntem önerisi (13.11.2026; 14.11 Type-III testinden önce)

Bu tarihli öneri, yalnız 13.11'e kadar mevcut kanıta dayanır. Güncel genişletilmiş yöntem karşılaştırması ve bir sonraki karar §16'dadır.

Bu, incelenen kanıtlara dayalı **şimdilik en uygun yöntem önerisidir; kullanıcının mimariyi veya bir parçayı onayladığı anlamına gelmez**. Mevcut asenkron S1/D1 güç katısını koruyarak sabit frekanslı (yaklaşık 100 kHz) analog **tepe akım kipli** kontrolcü kullanılsın. 11 V regülasyon geri beslemesi Cout uçlarından, bağımsız ortak çıkış kesicisinden **önce** Kelvin bağlantıyla alınsın. Bobin akım algılaması ayrı işlev olsun; başlangıçta yumuşak kalkış, her anahtarlama çevriminde akım sınırı ve uzun süreli aşırı yükte otomatik hiccup yeniden denemesi bulunsun. O1/S2E portunu izleyen bağımsız aşırı gerilim koruması ise tetiklenince kilitlenip kullanıcı müdahalesine kadar kapalı kalsın. Bu ayrım, sıradan aşırı akımın otomatik toparlanmasına izin verirken O1'i tehlikeye sokabilecek çıkış arızasının tekrar tekrar bağlanmasını önler. Bunlar yöntem düzeyinde öneridir; eşiği, zamanlamayı, parçayı veya devre değerini seçmez.

**13.11 tarihli yöntem değerlendirmesi:** Test edilmiş LT3844 örneği, giriş geçişi ve hafif/yüksüz durumda PI örneğinden belirgin biçimde iyi; 200 ms CPL adımında ikisi de seçilen 9–12 V bandında kaldı. O tarihte analog akım kipi, davranışsal PI'dan daha iyi başlangıç yönüydü. 14.11'deki Type-III RC gerilim-kipi modeli bu sonucu değiştirdi: artık gerilim kipi yöntem düzeyinde elenmiş değildir (§15). Sabit-açık-zaman/histeretik, ortalama akım kipi ve dijital PWM için bu güç katısıyla aynı test paketi koşulmadı; bunlara sayısal sıralama verilmesi dayanaksız olur.

**Algılama noktası gerekçesi — HESAP:** Koruma ayırıcısı açıldığında normal geri besleme bağlantısının kopmaması ve açık ayırıcıyı ana düzenleme döngüsüne katmamak için Cout tarafı ilk incelenecek yöndür. Dezavantajı, ayırıcı ve bağlantıların gerilim düşümünü düzeltmemesidir: yalnız 10 mΩ seri eleman varsayımıyla 7,5 A'de 75 mV düşüm ve 0,5625 W kayıp olur; Cout 11,00 V ise yük 10,925 V'tur. Gerçek sıcak direnç, olası iki MOSFET, konnektör/kablo ve koruma ekleri bilinmediğinden portun tüm koşullarda 10,45–11,55 V içinde kaldığı gösterilmedi. Koruma sonrası algılama yükte düşümü telafi edebilir fakat ayırıcı açılması, bağlantı kopması ve ilave dinamikler için özel davranış ve kararlılık kanıtı gerekir. Tercih, port regülasyon ve koruma gereksinimleriyle birlikte doğrulanacaktır.

**Kontrolcü adayları — DATASHEET / SİM / HESAP:** LT3844, bu yöntem için test edilebilen somut örnektir, kesin veya en ucuz seçim değildir. Üretici belgesi akım kipini, harici N-MOS sürmeyi, programlanabilir frekansı ve soft-start'ı doğrular; 100–500 kHz aralığı 100 kHz hedefini kapsar. Fakat geçici düzen 191 kΩ FSET ile yaklaşık 106 kHz'te koştu ve 10 mΩ algılama direnci ekledi; 200 ms CPL tepesinde simüle bobin akımı 9,89 A olurken 90–115 mV eşik yalnızca 9–11,5 A aralığı verir. Düşük eşik ucunda normal/geçici tepeye pay kalmıyor. S1 kısa devre akımının doyumlu bobinle ne olacağı da test modelinden bilinemez. Bu nedenle **LT3844 parça olarak önerilmiyor**; yöntemi sınamak için kullanılmıştır. Direnç/eşik ve bobin güvenli akımı beraber çözümlenmeden akım sınırı seçilmez. [LT3844 veri sayfası](https://www.analog.com/media/en/technical-documentation/data-sheets/3844fc.pdf).

TI LM5088-2 veri sayfası harici üst N-MOS, asenkron akım kipli buck, 50 kHz–1 MHz ve soft-start/hiccup işlevlerini desteklediğinden mimariyle kâğıt üstünde uyumludur. Üretici PSpice modeli üç denemede yakınsamadı; modelin çıkış kodu 1 ve tolerans gevşetme döngüsü verdi. Bu **elektriksel elenme değildir**, ancak tekrar üretilebilir geçici SİM elde edilmeden bu proje için puanlanamaz. Veri sayfası akım algılama ve emüle rampasının gerçek bobin/Cd–Rd ile tasarlanmasını gerektirir. [LM5088 veri sayfası Rev. J](https://www.ti.com/lit/ds/symlink/lm5088.pdf).

**Koruma:** Çıkıştan sonra ortak, seri MOSFET'li, bağımsız ve tercihen aşırı gerilimde latch-off bir kesici yöntem olarak önerilir; bu gerçek bir 7,5 A devreyle doğrulanmadı. LTC4365 üretici modeli ve bu modele bağlanan 2,2 nF/ideal FET ayırıcı, 11→25 V sentetik sert girişte cihaz portunda 10–1000 µF varsayımına göre 12,624–23,401 V gördü; 100 µF/10 µs LTC4365 koşusu 12,806 V, LTC4365-1 varyantı 13,061 V oldu. 50 ns tekrarı aynı sonucu verdi. Bunlar modelin zorlanmış testidir; gerçek O1 arıza eğrisi değil, fakat bu ayar 12 V kapısını geçmez. Birleşik S1-kısa devre testindeki 11,797 V (100 µF) ve 11,668 V (1000 µF) sonuçları yalnız o benzetim köşesine özgüdür; tek başına yeterlilik göstermez. LTC4365 veri sayfası 0,5 V OV karşılaştırıcısı, 1–2 µs hata yayılımı ve 2,2 nF gate için 2–4 µs hızlı kapama belirtir; bu ayrı tanımlı zamanların basitçe toplanması veya gerçek port tepesini garanti etmesi doğru değildir. [LTC4365 veri sayfası](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4365.pdf).

MAX6497/MAX6499 ailesindeki latch-off ve harici MOSFET sürme, çıkış kesicisi için sonraki araştırma adayıdır; 0,494–0,518 V OVSET toleransı, bölücü dahil eşik penceresi, gate gecikmesi/kapasitansı, 7,5 A ısı ve S1 kısa devresi testi gösterilmeden uygun sayılmaz. MAX6498 otomatik tekrar dener; O1'in katı 12 V sınırı nedeniyle aşırı gerilim arızasında latch-off tercih edilir. [MAX6495–MAX6499 veri sayfası](https://www.analog.com/media/en/technical-documentation/data-sheets/max6495-max6499.pdf).

## 1. Karar

| Parametre | Hedef (aday parçalardan önce) | Kabul aralığı | Neden | Kanıt |
|---|---|---|---|---|
| Ana çalışma noktası | 24,6 V | 20–26 V; test 20 / 22,2 / 24,6 / 25,2 / 26 V | 6S bataryanın normal çalışma gerilimi | §5.1 |
| Çıkış | 11 V / 7,5 A | — | 11 V iki yükün aralığında (O1 5–12 V, S2E 9–28 V); yük zarfı 6,64 A, pay %13 | §2 |
| fsw | 100 kHz | sabit | Ripple ve dinamik hedefler sağlanıyor; frekansı artırmanın bedeli (anahtarlama kaybı) ideal modelle ölçülemez | §5.1 |
| Ton | 4,59 µs | — | 24,6 V / 7,5 A'de 11 V (SİM 11,000 V). İletim süresi PULSE kenarları yüzünden Ton + 10 ns'dir | §5.1 |
| L1 | 33 µH el sarım, 7,81 mΩ (@20 °C, HESAP) | **33 µH** (el sarım AL ±%8 → 30,7–36,1 µH; satın alınan ±%20 için örnek köşeler sınandı); Isat ≥ 12 A; DCR 6,5–15 mΩ (el sarım hedefi 7,5–10) | Akım ripple'ı %25; CCM sınırı 0,94 A tipik yükün (≈ 1,2 A) altında. 22 µH elendi (tipik yük DCM'de, çıkış 8,8 V'a düşer). 39 ve 47 µH sönüm dalıyla `pencere`'yi geçse de kullanıcı kararıyla 33 µH seçilmiştir | §4.1, §4.4 |
| Cout | 1000 µF | 1000 µF ±%20; **≥ 35 V** (kullanıcı kararı, §9.4) | Sabit güç yüküyle LC dinamiği ve ripple. S1 kısa devresinde çıkış 27,3–31,1 V'a çıktığından 35 V sınıfı kabul edildi | §4.1, §4.4, §9.4 |
| Cout ESR | 25 mΩ | **≤ 35 mΩ** @100 kHz, 20 °C (10 mΩ dahil belirli senaryolar sınandı; aralığın tamamı kanıtlanmadı) | Üst sınır ripple için (35 mΩ köşede 83 mV t-t). Cd + Rd sınanan düşük ESR senaryolarında sönüm sağlar; diğer kombinasyonlar ayrıca değerlendirilir (§6, §10) | §4.2, §4.4, §6, §10 |
| Çıkış sönüm dalı (Cd + seri Rd) | **470 µF + 0,22 Ω** | Cd: 470 µF ±%20, **≥ 35 V**; ayrık Rd: **0,22 Ω** (Cd ESR'si dahil toplam dal direnci **0,15–0,60 Ω**), ≥ 0,25 W | Sınanan köşe ve sıcak ESR (10 mΩ) senaryolarında Pkritik ≥ 126 W > 82,5 W; sürekli kayıp ≈ 1,3 mW. Tüm ESR kombinasyonları sınanmadı | §6, §10 |
| Cin | 2 × 1000 µF, 15 mΩ/adet | toplam ripple akımı ≥ 4,5 A; **≥ 50 V** (kullanıcı kararı, §9.4); ≥ 440 µF | 3,8 A RMS giriş ripple akımı boyutu belirler; örnek sıcak takma hesabında tepe 48,0 V, gerçek kaynak ve gerilim payı doğrulanmadı | §5.9, §9.4 |
| S1 | Ron 12 mΩ | RDS(on) ≤ 12 mΩ; VDS ≥ 55 V | İletim kaybı 0,32 W (şematik adayıyla 0,15 W) | §5.1 |
| D1 | 0,5 V + 10 mΩ | VF ≤ 0,58 V @ 7,5 A; VRRM ≥ 45 V (tercihen 60 V) | İletim kaybının üçte ikisi (şematik adayıyla 1,78 W @ 24,6 V) | §5.1 |

Geçmiş: başlangıç değerleri 22,2 V / Ton 5,14 µs / Cout 330 µF (15 mΩ) / Cin 2 × 220 µF idi. Cout önce 680 µF'a, sonra 1000 µF'a alındı; 200 ms darbe testiyle ortaya çıkan tolerans köşesi CPL salınımı için çıkışa paralel `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalı eklendi (12.11.2026). L1, fsw ve çıkış hedefi baştan beri aynıdır.

**Aday parçalar ve gerilim sınıfı durumu (kesin seçim değil):** tablodaki "Hedef" sütunu aday parçalar belirlenmeden önceki başlangıç hedefleridir. Şematik değerleri: L1 33 µH el sarım / 7,81 mΩ (Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım; 2. sıra satın alma: Würth 74435583300, DCR 14,52 mΩ), Cout 1000 µF / 35 mΩ, Cd 470 µF + seri Rd 0,22 Ω, Cin 2 × 1000 µF / 15 mΩ, S1 5,6 mΩ (STP100N6F7), D1 0,38 V + 8 mΩ (STPS40M60CT), Ton 4,59 µs. **Not:** mevcut listedeki 25 V Cout (Nichicon UHE1E102MHD6TO) ve 35 V Cin (TDK B41859D7108M000) adayları elektriksel R/C değerlerinin kaynağıdır; kullanıcı kararıyla minimum gerilim sınıfları **Cout/Cd ≥ 35 V** ve **Cin ≥ 50 V** olarak yükseltildiğinden, simülasyon dondurmasından sonraki parça seçimi basamağında (§12.2) bu gerilim sınıflarını sağlayan kesin parça numaraları seçilecektir ([PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md)).

Bu değerler güç katının **elektriksel temelidir**; devre açık çevrim kaldığı sürece gerçek O1/S2E bağlanamaz (§11).

**12 Kasım 2026 doğrulama ve sönüm dalı turunun özeti:**
- Ölçüm altyapısındaki iki hata giderildi: sahte ripple üreten `Vh=0` anahtar zamanlama titremesi ve yakınsamayan Ton ayarı (§5.0).
- 200 ms darbe testinde dalsız devrenin tolerans köşesinde (`L +%20`, `Cout −%20`, `ESR 15 mΩ`) 73–82,5 W sabit güç yüküyle salındığı görüldü; kullanıcı onayıyla çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω` sönüm dalı** şematiğe, `hesap.py`'ye ve `dogrula.py`'ye eklendi (§6, §10).
- Test kipleri (`hesap.py`, `sayisal`, `secilen`, `pencere`, `kararlilik`, `zarf`, `stres`, `grafik`) yeni devreyle koşuldu: §6.2'deki 200 ms model setleri ve §6.1'deki ayrı 500 ms pencere köşesi 9–12 V içinde sönmüş olarak raporlandı; çıkış ripple'ı 24,6 V'ta 64,3 → 55,7 mV'a, 26 V örneklenen köşede 96,1 → 83,1 mV'a, soğuk ESR yük atma tepesi 12,13 → 11,76 V'a indi. Açık çevrim kalkış ve giriş değişimi sonuçları ayrıca sınır dışıdır.
- Kullanıcı kararıyla gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak belirlendi; genel modül için ayrı sınır tanımlanmayıp O1/S2E uyumluluk ölçütleriyle simülasyon dondurmasına gidilmesi kararlaştırıldı (§12.1).

## 2. Gereksinimler: genel modül zarfı ve referans yükler

### 2.1 Genel modül (bu buck modülünün kendi zarfı)

Modül, tanımlı sınırlar içinde **farklı uyumlu yüklerle** çalışacak bir güç katıdır; O1 ve S2E bu zarfın içindeki iki referans yüktür (§2.2), zarfın kendisi değildir.

| Büyüklük | Zarf | Durum |
|---|---|---|
| Giriş | 20–26 V (6S); test 20 / 22,2 / 24,6 / 25,2 / 26 V; takma anı ve 28 V ayrıca stres senaryosu | tanımlı |
| Çıkış | 11 V anma; 0–7,5 A sürekli; en çok 82,5 W | tanımlı (bu modülün hedefi; başka gerilim/akım modüllerini yasaklamaz) |
| Yük tipleri | dirençli (CR), sabit akımlı (CC), sabit güçlü (CP / CPL), yük adımı (%25 ↔ %75, %50 → %100), tam yük atma, 0 A | test edildi (§6, §7) |
| 7,5 A üstü talep | Verilmek zorunda değil; **güvenle sınırlanmalıdır** | Adım 7 şartı (§11) |
| Ortam | 25 / 50 / 60 °C (HESAP, §9.2); kondansatör −10 °C Zmax (üst sınır varsayımı) | fiziksel doğrulama yok |
| Sürekli gerilim toleransı, ripple ve geçici durum sınırları | **Kullanıcı kararı (12.11.2026): şimdilik ayrı sınır tanımlanmadı**; simülasyon dondurması O1/S2E uyumluluk ölçütleriyle (9–12 V, ripple ≤ 165 mV, 200 ms darbede sönüm) yapılır | Kapandı (isteğe bağlı, tanımlanmadı) |

Genel modül için ayrı sınır tanımlanmadığından bu belgede "genel modül GEÇTİ" kararı **yoktur**; §7 tabloları karakterizasyon ve O1/S2E uyumluluk kaydı olarak tutulur. `dogrula.py` içindeki 9–12 V ve 165 mV ölçütleri O1/S2E uyumluluk ölçütüdür.

### 2.2 Referans yükler (cihaza özgü uyumluluk)

| | T3 Gemstone O1 | SLAMTEC RPLIDAR S2E |
|---|---|---|
| Besleme aralığı | 5–12 V DC konnektör, 5 A — DATASHEET | 9–28 V, tipik 12 V — DATASHEET |
| 11 V uygun mu | Evet; üst çalışma sınırına 1 V pay | Evet; alt sınıra 2 V pay |
| Çalışma akımı | Yayımlanmamış. Zarf 5 A (giriş anma akımı); tipik 10 W, boşta 4 W — TAHMİN | 12 V'ta tipik 0,20 A, en çok 0,22 A — DATASHEET |
| Kalkış | Yayımlanmamış | 12 V'ta tipik 1,2 A, en çok 1,5 A; süre verilmemiş; "düşük gerilimde kalkış daha çok akım ister" — DATASHEET |
| Ripple sınırı | Yayımlanmamış | Besleme geriliminin %3'ü (11 V'ta ±330 mV) — DATASHEET |
| Mutlak maksimum | Yayımlanmamış | Yayımlanmamış (28 V çalışma üst sınırı) |
| Giriş koruması | DC girişte TPS259470 eFuse, aşırı gerilim bölücüsü 1 MΩ / 88,7 kΩ (1,2 V eşikle ≈ 14,7 V), SMAJ16CA TVS; arkasında TPS62180 (4–15 V çalışma, 17 V mutlak) — ÇIKARIM, v0.2 şeması | Bilinmiyor |

- **O1'in 12 V üst sınırı yalnız O1'e giden port için bağlayıcıdır**; o port için bağımsız aşırı gerilim koruması Adım 7'dedir.
- Her iki cihazın girişinde DC-DC dönüştürücü var; bu yüzden testlerde **sabit güç yükü** olarak modellendi (S2E 2,64 W çalışma / 18 W kalkış, O1 4 / 10 / 55 W). Gerçek giriş dönüştürücüleri sonlu bantlıdır; ideal sabit güç modelinin her koşulda kötümser olduğu kanıtlanmamıştır.
- 11 V'ta akım: S2E 0,24 A, S2E kalkış 1,64 A, O1 zarf 5 A → sürekli zarf 5,24 A, anlık zarf 6,64 A; 7,5 A hedefinde pay %13.
- ArduPilot sayfası O1 DC girişini 5–12 V / **3 A** verir; üretici sayfaları 5 A. Zarf için 5 A kullanıldı.
- Tipik toplam yük (TAHMİN ≈ 1,2 A) bobinin CCM sınırına (0,95 A) çok yakındır; yalnız S2E veya boştaki O1 ile devre DCM'de çalışır.

Kaynaklar: [T3 Gemstone O1 ürün sayfası](https://t3gemstone.org/en/products/o1) · [O1 kart belgesi](https://docs.t3gemstone.org/en/boards/o1/introduction) · [O1 v0.2 şeması, s. 6–7](https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf) · [ArduPilot O1 sayfası](https://ardupilot.org/sub/docs/common-t3-gem-o1-overview.html) · [Waveshare RPLIDAR S2/S2E güç tablosu](https://www.waveshare.com/wiki/RPLIDAR_S2) (SLAMTEC datasheet tablosunun kopyası; SLAMTEC'in kendi PDF sunucusu erişim vermedi, önceki depo kaydı "datasheet S2E v1.5 s. 12" aynı değerleri veriyor) · [TPS25947](https://www.ti.com/lit/gpn/tps25947) · [TPS62180](https://www.ti.com/product/TPS62180).

## 3. Başlangıç tasarımında bulunan sorunlar (11 Kasım 2026 incelemesi)

1. **Yük modeli.** Tek doğrulama 7,5 A dirençti. Direnç LC'yi sönümler; sabit güç yükü sönümü azaltır. Eski değerlerle (33 µH / 330 µF / 15 mΩ) 57,6 W sabit güçte çıkış **2,9 V t-t sürekli salınıyor**, S2E kalkış darbesinde 8,97–13,29 V (SİM). HESAP sınırı (basitleştirilmiş): P < Vo²·C·(Rs+ESR)/L = 48 W; tam ifade §6'dadır.
2. **Hafif yük hiç incelenmemişti.** Sabit Ton'da 24,6 V girişte çıkış 0,6 A yükte 13,0 V, 0,24 A yükte 16,9 V'a çıkar (DCM; HESAP ve SİM aynı).
3. **Kalkış.** 34,7 A / 17,44 V yeniden doğrulandı (SİM). Neden: LC'ye basamak uygulanması; I tepe ≈ Vo/Z0, aşım yük sönümüne bağlı. Hafif yükte (12,6 W) aşım 21,0 V'a çıkar. L veya C seçimiyle giderilemez: taranan 9 adayın tamamında 17,2–17,6 V.
4. **Ana nokta ve test noktaları.** Hesap yalnız 20 / 22,2 / 26 V'u kapsıyordu; şematik 22,2 V'taydı.
5. **Duty.** `hesap.py` ideal D = Vo/Vin kullanıyordu; düşümlerle 24,6 V'ta Ton 4,47 değil 4,65 µs, ripple ≈ %4 daha büyük.
6. **Çıkış ripple sınırı** (%0,5 = 55 mV) cihazlardan türetilmemişti. S2E %3 ister; O1 için veri yok.
7. **Cout ESR hedefi tek taraflıydı** ("≤ 15 mΩ"). ESR düştükçe sönüm azalır.
8. **Cin simülasyonda etkisizdi:** V1 ideal kaynak olduğundan Cin akımı sıfırdır. Giriş tarafı ancak kaynak empedansıyla doğrulanabilir (§5.9).
9. Kayıp/verim hesabı yoktu.

## 4. Değerler nasıl seçildi

Ölçüt (O1/S2E uyumluluğu): referans yük senaryolarında (sabit güç) ve tolerans köşelerinde çıkışın **9–12 V** içinde kalması (S2E alt sınırı, O1 üst sınırı) ve ripple ≤ 165 mV t-t (çıkışın %1,5'i; S2E sınırı ±%3). Testlerde Ton sabittir: kontrolcünün tepki vermediği bir durumdur, tüm kapalı çevrim davranışları için en kötü sınır olduğu kanıtlanmamıştır. §4.1–§4.3 ve §4.4'ün ilk tablosu 11 Kasım 2026 koşularıdır (20 ms'lik darbe, eski ölçüm altyapısı); seçim gerekçesi olarak korunmuştur, güncel karar §4.4'ün son tablosu ve §6'dır.

### 4.1 İlk tarama: L × Cout (ESR 15 mΩ, 24,6 V)

`dogrula.py tarama`. Sütunlar: S2E kalkış darbesi (57,6 → 73 → 57,6 W) sırasında çıkış ve darbe öncesi/sırası salınım.

**13.11.2026 tekrar koşusu:** Güncel ölçüm altyapısıyla eski dalsız model yeniden tarandı; aşağıdaki 11.11.2026 tarihli tablonun bazı 20 ms ölçümleriyle aynı değildir. Örneğin 33 µH / 470 µF için zarf adımı 9,86–12,30 V, 33 µH / 330 µF için 8,97–13,18 V bulundu. Önceki tabloda sırasıyla 10,03–12,01 V ve 8,97–13,29 V kayıtlıdır. Koşular aynı altyapı sürümü değildir; bu farkların tek nedeni ayrı olarak kanıtlanmadı. Her iki kayıt da geçmiş dalsız modele aittir; kısa darbe tek başına kararlılık geçişi kanıtlamaz.

| L µH | Cout µF | ΔIL A | ΔVo mV | Vmin/Vmax V | 57,6 W salınım mV | 73 W salınım mV | sert kalkış A / V |
|---|---|---|---|---|---|---|---|
| 22 | 330 | 2,85 | 45,9 | 10,15/11,84 | 103 | 1623 | 41,8 / 17,6 |
| 22 | 470 | 2,85 | 45,6 | 10,63/11,31 | 43 | 47 | 48,2 / 17,6 |
| 22 | 680 | 2,85 | 45,5 | 10,72/11,25 | 43 | 44 | 56,0 / 17,4 |
| 33 | 330 (eski) | 1,90 | 29,3 | 8,97/13,29 | 2913 | 4205 | 34,9 / 17,4 |
| 33 | 470 | 1,90 | 29,2 | 10,03/12,01 | 376 | 1364 | 40,4 / 17,6 |
| 33 | 680 | 1,90 | 29,0 | 10,64/11,30 | 34 | 64 | 47,0 / 17,6 |
| 47 | 330 | 1,33 | 20,8 | 8,28/14,23 | 4047 | 5945 | 29,8 / 17,2 |
| 47 | 470 | 1,33 | 20,6 | 8,87/13,29 | 3092 | 4411 | 34,5 / 17,4 |
| 47 | 680 | 1,33 | 20,4 | 10,16/11,84 | 455 | 1628 | 40,4 / 17,5 |

- İletim verimi dokuz adayda da %96,0'dır: **L ve Cout verimi ayırt etmez**, ayırt eden sönümdür.
- Sabit güç yükü LC'yi sönümsüzleştirir. Kararlılık sınırı (HESAP, tam ifade §6): P < Vo²·(Rs+ESR)/(L/C + Rs·ESR). Cout/L oranı ve ESR büyüdükçe sınır yükselir.
- Sert kalkış aşımı tüm adaylarda 17,2–17,6 V: L/C ile giderilemez, yumuşak kalkış gerekir.

### 4.2 Cout ESR'sinin alt sınırı

33 µH / 680 µF, köşe L +%20 / Cout −%20, 57,6 W sabit güçte sürekli salınım (SİM):

| Cout ESR | 7,5 mΩ | 10 mΩ | 15 mΩ | 25 mΩ |
|---|---|---|---|---|
| Salınım t-t | 2480 mV | 2448 mV | 792 mV | 65 mV |

ESR, LC'nin sönüm direncidir. Bu eski dalsız modelde düşük ESR sönümü azaltır; o dönem için alt sınır konmuştur. Güncel Cd + Rd dalının sınanan senaryoları ve bunların kapsamı §10'dadır.

### 4.3 Giriş değişimi ve daha büyük L / Cout

Ton sabit, ESR 25 mΩ (SİM):

| | A: 33 µH / 680 µF | 47 µH / 1000 µF | 68 µH / 1500 µF | 33 µH / 1000 µF |
|---|---|---|---|---|
| Kararlı çıkış, 20 / 22,2 / 24,6 / 25,2 / 26 V giriş (7,5 A) | 8,89 / 9,90 / 11,00 / 11,27 / 11,64 V | aynı | aynı | aynı |
| Giriş 24,6 → 20 V rampası (57,6 W): Vmin / Vmax | 8,68 / 11,15 V | 8,14 / 11,59 V | 7,58 / 11,98 V | 8,53 / 11,27 V |
| Giriş 22,2 → 25,2 V rampası (57,6 W): Vmax | 12,66 V | 12,94 V | 13,32 V | 12,76 V |
| Çıkış ripple'ı anma / köşe | 47 / 74 mV | 33 / 52 mV | 23 / 36 mV | 47 / 74 mV |
| Sabit Ton'da 0,6 A yükte çıkış (24,6 V) | 12,98 V | 11,52 V | 11,17 V | 12,98 V |
| O1 tipik → zarf adımı: Vmin / Vmax | 10,04 / 11,80 V | 10,08 / 11,78 V | 10,11 / 11,75 V | 10,22 / 11,64 V |
| Köşe, S2E kalkışı @zarf: salınım 57,6 / 73 W | 171 / 881 mV | 83 / 434 mV | 152 / 411 mV | 36 / 54 mV |
| Sert kalkış | 45,8 A / 17,1 V | 46,1 A / 17,1 V | 46,5 A / 17,1 V | 53,3 A / 16,9 V |

- **Giriş değişiminin kararlı etkisi L ve Cout'tan bağımsızdır:** Vo ≈ D·Vin − düşümler. Parça değeriyle düzelmez; yalnız Ton girişe göre ayarlanırsa (ileri besleme veya geri besleme) sabit kalır.
- Çok büyük L / Cout giriş geçişini kötüleştirir (LC yavaşlar): 68 µH / 1500 µF'ta 7,58–13,32 V.
- 33 µH / 1000 µF, 33 µH / 680 µF'a göre yük adımında ve köşe sönümünde daha iyidir; bedeli daha yüksek sert kalkış akımıdır (yumuşak kalkışla zaten giderilir).

### 4.4 Kabul penceresi

`dogrula.py pencere`. Her L/Cout çifti için ESR penceresinin iki kenarı ve tolerans köşeleri (L −%30/+%20, Cout −%20) koşulur.

İlk deneme (Cout = 20 × L kuralı, ESR 20–35 mΩ):

| L µH | Cout µF | ΔIL A | IL tepe köşe A | ΔVo ESR 35 mΩ: anma / köşe mV | S2E kalkışı @zarf V | O1 tipik→zarf V | köşe: S2E kalkışı @zarf V | köşe: O1 tipik→zarf V | köşe salınım 57,6 / 73 W mV | köşe yük atma sınırı V | 9–12 V ve ≤165 mV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22 | 470 | 2.86 | 9.62 | 104 / 146 | 10.64–11.31 | 8.78–11.02 | 10.46–11.46 | 9.62–11.85 | 56 / 398 | 11.25 | KALDI |
| 33 | 680 | 1.89 | 8.91 | 66 / 98 | 10.64–11.31 | 10.03–11.80 | 10.38–11.67 | 9.78–12.06 | 130 / 717 | 11.24 | KALDI |
| 47 | 1000 | 1.33 | 8.51 | 46 / 75 | 10.70–11.31 | 10.07–11.79 | 10.67–11.24 | 9.84–11.88 | 83 / 367 | 11.23 | GEÇTİ |

- 22 µH / 470 µF: tipik yük (1,15 A) CCM sınırının (1,43 A) altında; Ton DCM'de ayarlıyken yük artınca çıkış 8,78 V'a düşer. **22 µH elendi.**
- 33 µH / 680 µF: en kötü köşede O1 tipik → zarf adımında 12,06 V. **680 µF elendi.**

Son pencere (Cout 1000 µF, ESR 15–35 mΩ, paralel sönüm dalı **Cd = 470 µF + seri Rd = 0,22 Ω**), şematikteki 1. sıra değerleriyle (el sarım L1 DCR 7,81 mΩ, Ron 5,6 mΩ, Vf 0,38 V + 8 mΩ). **12 Kasım 2026 koşusu (`dogrula.py pencere`), köşelerde Cout ve Cd −%20 (800 µF ve 376 µF), 200 ms darbe ile:**

| L µH | Cout µF | ΔIL A | IL tepe köşe A | ΔVo ESR 35 mΩ: anma / köşe mV | S2E kalkışı @zarf, 20 ms V | O1 tipik→zarf V | köşe: S2E kalkışı @zarf, 20 ms V | köşe: O1 tipik→zarf V | anma: 73 W 200 ms V, sönüm | köşe: 73 W 200 ms V, sönüm (LC periyodu başına oran) | köşe: 200 ms sonunda yavaş salınım mV t-t | köşe yük atma sınırı V | eski karar (yalnız 20 ms) | KARAR: 9–12 V, ≤165 mV, 200 ms'de sönümlü |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 33 | 1000 | 1.88 | 8.91 | 56 / 83 | 10.77–11.20 | 10.37–11.54 | 10.72–11.25 | 10.22–11.67 | 10.77–11.20 sönmüş | 10.72–11.25 sönmüş (×1.000) | 1 | 11.20 | geçti | GEÇTİ |
| 39 | 1000 | 1.59 | 8.69 | 47 / 70 | 10.75–11.22 | 10.31–11.59 | 10.70–11.27 | 10.15–11.74 | 10.75–11.22 sönmüş | 10.70–11.27 sönmüş (×1.000) | 1 | 11.20 | geçti | GEÇTİ |
| 47 | 1000 | 1.32 | 8.49 | 39 / 58 | 10.73–11.24 | 10.24–11.65 | 10.67–11.33 | 10.06–11.84 | 10.73–11.24 sönmüş | 10.67–11.30 sönmüş (×1.000) | 1 | 11.20 | geçti | GEÇTİ |

- Karar üç şeye bakar: (1) bütün yük adımlarında ve yük atmada 9–12 V, (2) 26 V köşe ripple'ı ≤ 165 mV, (3) S2E kalkış darbesi (57,6 → 73 W) **200 ms** sürdüğünde de 9–12 V ve yavaş (LC) salınımın sönmesi.
- Sönüm dalı eklenmeden önce aynı koşuda 33 / 39 / 47 µH satırlarının üçü de köşede **kalıyordu** (33 µH: 9,91–12,05 V, 2082 mV t-t sürekli salınım; 39 / 47 µH: 12,59 / 12,86 V). **`Cd = 470 µF + Rd = 0,22 Ω` sönüm dalıyla üç satır da GEÇTİ**: 33 µH köşede 73 W 200 ms darbesi **10,72–11,25 V** içinde kalır ve darbe sonundaki yavaş salınım 1 mV t-t'dir (tamamen sönmüş).
- **Seçilen hedef L1 = 33 µH'dir** (kullanıcı kararı korunmuştur; sınanan köşede O1 adımı 10,22–11,67 V ve LC dinamiği diğer adaylara göre daha hızlıdır). `pencere` testindeki 33 µH +%20 ve 47 µH +%20 senaryoları sönüm dalıyla geçmiştir; bu sonuç tüm üretim toleransı kombinasyonlarını kanıtlamaz. El sarım için AL ±%8 kaynaklı 30,7–36,1 µH bir öngörüdür.
- Sınanan model setlerinde sönüm dalı, daha önce sorun yaratan düşük Cout ESR ve DCR senaryolarında sönüm sağlar (§6, §10). Tüm kombinasyonlar sınanmadı. Ölçülebilir parça ve sarım hedef aralıkları: [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md).

## 5. Şematik değerleriyle test sonuçları (SİM)

Şematik değerleri ([PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md)): L 33 µH / 7,81 mΩ (el sarım, HESAP) · Cout 1000 µF / 35 mΩ (maks. empedans, ESR varsayımı) · **Cd 470 µF + seri Rd 0,22 Ω** · Cin 2 × 1000 µF / 15 mΩ · Ron 5,6 mΩ · Vf 0,38 V + 8 mΩ · 100 kHz. Tablolar `python buck/dogrula.py secilen` çıktısıdır (12.11.2026, çıkış kodu 0).

### 5.0 Ölçüm altyapısı: bulunan hatalar ve düzeltme (`dogrula.py sayisal`)

Düzeltme öncesi tablolarda anahtar zamanlama titremesi yüzünden ripple HESAP'tan %5–9 yüksek görünüyordu. Neden deneyle ayrıldı (sönüm dalı dahil güncel devreyle):

| Anahtar modeli | iletim süresi ort. ns (Ton 4589 ns) | titreme t-t ns | titreme std ps | ΔVo mV t-t | dVo/dTon mV/ns (beklenen Vin/T = 2,46) | doğrudan sapma maks mV (Ton 4580–4600 ns) | ΔVo aralığı mV (aynı tarama) |
|---|---|---|---|---|---|---|---|
| idealler.lib (Vh=0, sert geçiş) | 4597.518 | 2.145 | 1013 | 60.6 | 2.535 | 4.08 | 56.2–60.8 |
| test modeli (Vh=−0,5, yumuşak geçiş) | 4598.981 | 0.000 | 0 | 55.7 | 2.475 | 0.00 | 55.7–55.7 |

- **Kök neden:** `idealler.lib` anahtarı `Vh=0` (sert geçiş) ile tanımlıdır. LTspice, 10 ns'lik PULSE kenarının ortasındaki geçiş anını zaman adımına göre çözer; iletim süresi periyottan periyoda ≈ 2 ns oynar (std ≈ 1 ns). Bu titreme LC'yi uyarır, 1 ms'lik pencerede tepe-tepe değeri büyütür ve Vo(Ton) eğrisini basamaklı yapar (doğrudan sapma 4,1 mV). `Vh=−0,5` (yumuşak geçiş) ile titreme **sıfırdır**.
- Denenip **neden olmadığı** görülenler: `plotwinsize=0` (sıkıştırma) etkisiz; `maxstep` 100 / 50 / 20 ns aynı sonucu verir (5 ns'de titreme sürer); bobinin varsayılan paralel direnci etkisiz; diyot `Epsilon` etkisiz. Ölçüm penceresini 15–16 ms'den 19–20 ms'ye almak sonucu değiştirir ama bunun nedeni pencere değil, `tstop` değişince zaman adımı diziliminin değişmesidir.
- **Düzeltme:** test netlistleri, `idealler.lib` ile aynı değerleri taşıyan ama anahtarı `Vh=-0.5` olan bir modeli netliste gömer. `idealler.lib`, `anahtar.asy`, `diyot.asy` ve ana şematik **değişmedi**. Ana şematiğin LTspice'taki kendi koşusu (`.tran 20m`, 19–20 ms) Vo = 11,000 V ve ΔVo = 55,7 mV t-t verir.
- **Ton ayarı:** kökü iki yandan sarar, ölçüt çıkış gerilimi cinsindendir (1 mV eşdeğeri veya akımın %0,5'i), Ton 9 basamakla yazılır, bobin başlangıç akımı vadi değeridir, **yakınsamazsa koşu hata ile durur**.

Beş girişte ripple, hesap (`ESR || Rd || Rload`) ve iki modelle:

| Vin V | Ton µs | HESAP ΔVo mV | yumuşak: ΔVo mV | yumuşak: Vo V | sert: ΔVo mV | sert: Vo V |
|---|---|---|---|---|---|---|
| 20 | 5.6271 | 45.0 | 45.0 | 11.0000 | 45.5 | 10.9999 |
| 22.2 | 5.0783 | 50.6 | 50.6 | 11.0000 | 55.2 | 10.9959 |
| 24.6 | 4.5898 | 55.7 | 55.7 | 11.0000 | 60.8 | 11.0009 |
| 25.2 | 4.4820 | 56.8 | 56.8 | 11.0000 | 57.4 | 10.9999 |
| 26 | 4.3459 | 58.2 | 58.2 | 11.0000 | 63.5 | 11.0009 |

Yakınsayan Ton değerleri [µs] (25 nokta, DCM dahil; hepsi yakınsadı):

| Vin V \ yük A | 0,24 | 0,6 | 1,15 | 2,5 | 7,5 |
|---|---|---|---|---|---|
| 20 | 3.1249 | 4.9467 | 5.5821 | 5.5917 | 5.6271 |
| 22.2 | 2.6598 | 4.2113 | 5.0373 | 5.0460 | 5.0783 |
| 24.6 | 2.2935 | 3.6321 | 4.5524 | 4.5604 | 4.5898 |
| 25.2 | 2.2177 | 3.5123 | 4.4454 | 4.4532 | 4.4820 |
| 26 | 2.1244 | 3.3647 | 4.3103 | 4.3179 | 4.3459 |

### 5.1 Kararlı durum, 7,5 A direnç yük, Ton her girişte 11 V'a ayarlı (ideal regülasyon varsayımı)

| Vin V | Ton µs | Vo V | ΔVo mV | IL A | S1 rms A | D1 ort A | Cout rms A | P S1 W | P D1 W | P L1 W | P toplam W | η iletim % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 5.627 | 11.000 | 45.0 | 6.74–8.26 | 5.64 | 3.27 | 0.37 | 0.18 | 1.44 | 0.44 | 2.06 | 97.56 |
| 22.2 | 5.078 | 11.000 | 50.6 | 6.64–8.36 | 5.36 | 3.68 | 0.42 | 0.16 | 1.62 | 0.44 | 2.23 | 97.37 |
| 24.6 | 4.590 | 11.000 | 55.7 | 6.56–8.44 | 5.10 | 4.05 | 0.46 | 0.15 | 1.78 | 0.44 | 2.38 | 97.20 |
| 25.2 | 4.482 | 11.000 | 56.8 | 6.54–8.46 | 5.04 | 4.13 | 0.47 | 0.14 | 1.82 | 0.44 | 2.41 | 97.16 |
| 26 | 4.346 | 11.000 | 58.2 | 6.52–8.48 | 4.96 | 4.23 | 0.48 | 0.14 | 1.86 | 0.44 | 2.45 | 97.11 |

Verim yalnız iletim kaybıdır (`Rd` üzerindeki ≈ 1,3 mW dahil); anahtarlama, çekirdek ve kondansatör kayıplarıyla kestirim §9.1'dedir. Ripple akımının %14'ü `0,22 Ω` sönüm dalından geçtiğinden `Cout` RMS akımı (0,46 A) ve çıkış ripple'ı (55,7 mV) dalsız devreye (0,53 A / 64,3 mV) göre düşmüştür; HESAP ile 0,0 mV içinde uyuşur.

![Kararlı durum](grafik/kararli.svg)

### 5.2 Kararlı durum, referans yük senaryoları, 24,6 V, Ton 11 V'a ayarlı (sabit güç yükü)

| Senaryo | P W | I@11V A | Ton µs | Kip | Vo V | ΔVo mV | IL tepe A | η iletim % |
|---|---|---|---|---|---|---|---|---|
| yalnız S2E çalışma | 2.64 | 0.24 | 2.293 | DCM | 10.995 | 29.4 | 0.95 | 98.0 |
| yalnız O1 boşta (tahmin) | 4.00 | 0.36 | 2.825 | DCM | 10.992 | 36.3 | 1.17 | 97.9 |
| yalnız O1 tipik (tahmin) | 10.00 | 0.91 | 4.473 | DCM | 10.984 | 56.7 | 1.85 | 97.9 |
| O1 boşta + S2E | 6.64 | 0.60 | 3.643 | DCM | 10.987 | 46.6 | 1.51 | 97.9 |
| O1 tipik + S2E | 12.64 | 1.15 | 4.552 | CCM | 11.000 | 56.9 | 2.09 | 97.9 |
| O1 tipik + S2E kalkış | 28.00 | 2.55 | 4.561 | CCM | 11.000 | 57.1 | 3.49 | 97.8 |
| yalnız O1 zarf 5 A | 55.00 | 5.00 | 4.575 | CCM | 11.000 | 57.6 | 5.94 | 97.5 |
| O1 zarf + S2E | 57.64 | 5.24 | 4.576 | CCM | 11.000 | 57.6 | 6.18 | 97.5 |
| O1 zarf + S2E kalkış | 73.00 | 6.64 | 4.585 | CCM | 11.000 | 57.9 | 7.58 | 97.3 |

Ripple her senaryoda S2E sınırının (±330 mV) çok altında. DCM satırlarında Vo'nun 11,000 V'tan 5–16 mV sapması, 16 ms'lik koşuda çıkışın tam oturmamasındandır (hafif yükte zaman sabiti onlarca ms); Ton kelepçeli ayardan gelir ve doğrudur. DCM'de gereken Ton yükle 2,3–4,5 µs arasında değişir: geri besleme bu aralığı kapsamalıdır.

### 5.3 Açık çevrim: Ton sabit (24,6 V / 7,5 A'ya ayarlı), giriş ve yük değişince kararlı çıkış [V]

| Vin V \ yük A@11V | 0.24 | 0.6 | 1.15 | 2.5 | 5.24 | 7.5 |
|---|---|---|---|---|---|---|
| 20 | 13.62 | 10.48 | 8.98 | 8.96 | 8.93 | 8.91 |
| 22.2 | 15.12 | 11.64 | 9.99 | 9.97 | 9.94 | 9.91 |
| 24.6 | 16.76 | 12.90 | 11.09 | 11.07 | 11.03 | 11.00 |
| 25.2 | 17.17 | 13.22 | 11.37 | 11.35 | 11.31 | 11.27 |
| 26 | 17.72 | 13.64 | 11.74 | 11.72 | 11.67 | 11.64 |

O1'in 5–12 V aralığı yalnız 24,6 V civarında ve yük CCM'deyken sağlanır. **Açık çevrim hiçbir L/C değeriyle regülasyon sağlamaz**; bu bir güç katı hatası değil, bilinen açık çevrim sınırıdır ve geri beslemeyle (Adım 6) kapanır. Yüksüz çalışmada çıkış giriş gerilimine tırmanır.

### 5.4 Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor), darbe 200 ms

| Adım (200 ms) | P W | Vmin V | Vmax V | ara kararlı V | ara salınım mV | son kararlı V | son salınım mV | IL tepe A | yavaş salınım |
|---|---|---|---|---|---|---|---|---|---|
| S2E kalkışı, O1 tipik | 12.6→28.0 | 10.78 | 11.20 | 10.98 | 57 | 11.00 | 57 | 4.4 | sönmüş |
| O1 tipik→zarf→tipik, S2E çalışıyor | 12.6→57.6 | 10.38 | 11.53 | 10.94 | 58 | 11.00 | 57 | 9.0 | sönmüş |
| S2E kalkışı, O1 zarf | 57.6→73.0 | 10.77 | 11.21 | 10.98 | 58 | 11.00 | 58 | 8.6 | sönmüş |
| O1 zarf→boşta→zarf, S2E çalışıyor | 57.6→6.6 | 10.45 | 16.07 | 16.04 | 37 | 11.00 | 58 | 8.9 | sönmüş |

İlk üç adımda çıkış kontrolcü olmadan bile 9–12 V içinde kalır (dalsız devreye göre sapma ≈ 50–140 mV daha dardır) ve salınım söner. Son satır DCM yükselmesidir (§5.3): 200 ms'de 16,07 V'a çıkar ve yalnız geri beslemeyle giderilir.

![Yük adımı](grafik/yuk_adimi.svg)

### 5.5 Yük atma, ideal kontrolcü sınırı (yük düştüğü anda duty = 0; en iyi durum)

| Vin V | 73→6,6 W Vtepe V | 82,5→2,6 W Vtepe V |
|---|---|---|
| 20 | 11.197 | 11.234 |
| 22.2 | 11.200 | 11.237 |
| 24.6 | 11.202 | 11.240 |
| 25.2 | 11.203 | 11.240 |
| 26 | 11.204 | 11.241 |

Bobindeki enerji `Cout` ve `Cd + Rd` dalına boşaldığında oluşan tepe budur (dalsız devredeki 11,28 V'tan 11,24 V'a düşer). Kontrol gecikmesinin ve soğuk ESR'nin etkisi §7.3'tedir.

### 5.6 Soğuk kalkış

| Vin V | Yük | sert: IL tepe A | sert: Vo tepe V | 5 ms duty rampası: IL tepe A | 5 ms duty rampası: Vo tepe V |
|---|---|---|---|---|---|
| 20 | 7,5 A direnç | 61.3 | 16.64 | 11.5 | 11.34 |
| 22.2 | 7,5 A direnç | 61.4 | 16.63 | 11.6 | 11.34 |
| 24.6 | 7,5 A direnç | 61.4 | 16.63 | 11.7 | 11.34 |
| 25.2 | 7,5 A direnç | 61.4 | 16.63 | 11.7 | 11.34 |
| 26 | 7,5 A direnç | 61.5 | 16.62 | 11.8 | 11.34 |
| 24.6 | O1 tipik + S2E (12,6 W) | 63.1 | 18.07 | 8.0 | 11.39 |

`Cd` sönüm dalı toplam çıkış kapasitesini artırdığı için sert kalkış tepe akımı 53,4 → 61,5 A'e çıkar, tepe gerilim sönüm sayesinde 17,01 → 16,62 V'a (12,6 W'ta 18,81 → 18,07 V'a) iner; sert kalkış hâlâ O1 girişini zorlar ve doğrusal olmayan bobini doyuma iter (`L/L0 ≈ %53` @61 A). 5 ms'lik duty rampasıyla (yumuşak kalkış varsayımı, Adım 5) bobin akımı 11,8 A ≤ 12 A ve çıkış 11,39 V ≤ 12 V içinde kalır.

![Kalkış](grafik/kalkis.svg)

### 5.7 Giriş değişimi, Ton sabit, O1 zarf + S2E (57,6 W)

| Vin V (1 ms rampa) | Vmin V | Vmax V | ara kararlı V |
|---|---|---|---|
| 24.6→20→24.6 | 8.33 | 11.50 | 8.87 |
| 24.6→26→24.6 | 10.82 | 11.82 | 11.65 |
| 22.2→25.2→22.2 | 10.62 | 12.90 | 12.53 |

Çıkış girişi oransal izler (ΔVo ≈ D·ΔVin). 20 V'ta S2E'nin 9 V alt sınırının altına, batarya dolarken O1'in 12 V sınırının üstüne çıkar. L/Cout ile düzelmez (§4.3); bilinen açık çevrim sınırıdır.

### 5.8 Tolerans köşeleri (L −%30/+%20, Cout ve Cd ±%20, ESR 15/35 mΩ), 7,5 A; zarf adımı 200 ms

| Köşe | Vin V | ΔVo mV | IL tepe A | zarf adım (200 ms) Vmin/Vmax | 73 W darbe sonu t-t mV | yavaş salınım | yük atma sınırı V | sert kalkış A/V | rampalı kalkış A/V |
|---|---|---|---|---|---|---|---|---|---|
| anma | 24.6 | 55.7 | 8.44 | 10.77/11.21 | 58 | sönmüş | 11.20 | 61.4/16.6 | 11.7/11.34 |
| ripple en kötü: L−, C−, ESR 35 mΩ | 26 | 83.1 | 8.91 | 10.77/11.21 | 86 | sönmüş | 11.21 | 65.0/16.5 | 11.5/11.26 |
| sönüm en zayıf: L+, C−, ESR 15 mΩ | 24.6 | 21.8 | 8.28 | 10.72/11.25 | 22 | sönmüş | 11.11 | 54.1/17.4 | 10.9/11.35 |
| Z0 en düşük: L−, C+, ESR 15 mΩ | 26 | 39.1 | 8.91 | 10.82/11.16 | 40 | sönmüş | 11.10 | 79.6/16.8 | 12.8/11.30 |

L −%30, −%20 toleransı ve tepe akımdaki endüktans düşümünü birlikte kapsar. **Dört köşenin tamamı GEÇER:** daha önce 9,91–12,05 V ve 2140 mV t-t sürekli salınımla kalan "sönüm en zayıf" köşe, `Cd = 376 µF (−%20) + Rd = 0,22 Ω` ile **10,72/11,25 V** aralığında ve **sönmüş** olarak kapanır (darbe sonu 22 mV t-t yalnız 100 kHz anahtarlama ripple'ıdır). `Z0 en düşük` köşede 5 ms rampa kalkış akımı 12,8 A'dir; Adım 5'te ≥ 6 ms rampa veya akım sınırlamalı kalkışla ≤ 12 A tutulur.

### 5.9 Giriş tarafı, batarya+kablo modeli (VARSAYIM 40 mΩ + 1 µH/10 mΩ), 7,5 A

| Batarya V | Vo V | ΔVin mV t-t | Cin toplam rms A | Cin ESR kaybı W |
|---|---|---|---|---|
| 20 | 10.870 | 69 | 3.69 | 0.10 |
| 24.6 | 10.908 | 71 | 3.73 | 0.10 |
| 26 | 10.917 | 71 | 3.71 | 0.10 |

Batarya 26 V sıcak takma (anahtar kapalı): V(vin) tepe 26.0 V, batarya akımı tepe 359 A

Ton ideal kaynağa göre ayarlıdır; kaynak direnci girişi ≈ 0,3 V düşürdüğü için açık çevrim çıkış 10,87–10,92 V'ta kalır (koşu bunu uyarı olarak yazar). Değerler tahmini kaynak empedansına bağlıdır; farklı kaynak R/L değerleri için sıcak takma süpürmesi §9.4'tedir. İki TDK kondansatörün toplam ripple akımı anma değeri 6,5 A'dir.

## 6. Sabit güç yükü ile kararlılık (HESAP + SİM)

`python buck/dogrula.py kararlilik` ve `python buck/hesap.py` §6. Ton sabit (açık çevrim), 24,6 V; şematikte `Cd = 470 µF + seri Rd = 0,22 Ω` sönüm dalı vardır (`C −%20` köşelerinde `Cd` de −%20 = 376 µF).

### 6.1 Darbe süresinin etkisi (1 ms – 500 ms)

Pencere köşesi: L 39,6 µH, Cout 800 µF, ESR 15 mΩ, Cd 376 µF + Rd 0,22 Ω, DCR 7,81 mΩ; 57,64 → 73 → 57,64 W.

| Darbe ms | Vmin V | Vmax V | darbe sonu t-t mV | yavaş salınım, son iki LC periyodu mV | oran | sönüm | 9–12 V | karar |
|---|---|---|---|---|---|---|---|---|
| 1 | 10.72 | 11.33 | 389 | — | — | kısa | içinde | BELİRSİZ |
| 5 | 10.72 | 11.27 | 231 | 207 → 140 | 0.679 | sönüyor | içinde | BELİRSİZ |
| 20 | 10.72 | 11.25 | 25 | 4 → 3 | 0.754 | sönmüş | içinde | BELİRSİZ |
| 50 | 10.72 | 11.25 | 22 | 1 → 1 | 1.000 | sönmüş | içinde | BELİRSİZ |
| 200 | 10.72 | 11.25 | 22 | 1 → 1 | 1.000 | sönmüş | içinde | GEÇTİ |
| 500 | 10.72 | 11.25 | 22 | 1 → 1 | 1.000 | sönmüş | içinde | GEÇTİ |

HESAP (aynı köşe, 73 W): denge 10.979 V, Pkritik 146.0 W, sönüm +287.2 1/s → LC periyodu başına oran 0.725, zaman sabiti 3 ms

- "oran": yavaş (≈ 0,9 kHz) salınımın art arda iki LC periyodundaki tepe-tepe değerlerinin oranı. Çıkış 4,8 kHz RC'den geçirilerek ölçülür (anahtarlama ripple'ı ayrılır). Sönüm sınıfları: sönmüş (< 20 mV) · sönüyor (oran < 0,98) · sürekli salınım (0,98–1,02) · büyüyor (> 1,02). Son ikisi kabul edilmez. **200 ms'den kısa, sınır içindeki sönümlü darbe tek başına geçiş kanıtı değildir:** güncel kodla yeniden koşuda bu satırların kararı BELİRSİZ'dir.
- Dalsız devrede aynı köşe 200 ms'de 9,91–12,05 V'a, 500 ms'de 9,64–12,32 V sınır çevrimine çıkıyordu (`Pkritik = 72 W`, sönüm −5,1 1/s). **Sönüm dalıyla sönüm +287 1/s'ye (τ ≈ 3 ms) döner**: 5 ms'de salınım periyot başına `×0,679` ile hızla söner (HESAP: `×0,725`), 20 ms'de 3 mV'a düşer ve 50–500 ms boyunca çıkış **10,72–11,25 V** aralığında tamamen sönmüş kalır.

### 6.2 Model setleri × yük (200 ms darbe)

| Model seti | P W | HESAP Pkritik W | HESAP sönüm 1/s | HESAP oran/periyot | SİM oran/periyot | SİM sönüm | Vmin V | Vmax V | 200 ms sonunda yavaş salınım mV | HESAP–SİM aynı yönde | 9–12 V | karar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anma (şematik) | 57.6→73.0 | 257 | +602 | 0.503 | 1.000 | sönmüş | 10.77 | 11.21 | 2 | evet | içinde | GEÇTİ |
| anma (şematik) | 41.2→82.5 | 256 | +573 | 0.520 | 1.000 | sönmüş | 10.42 | 11.50 | 2 | evet | içinde | GEÇTİ |
| anma (şematik) | 20.6→61.9 | 254 | +633 | 0.486 | 1.000 | sönmüş | 10.43 | 11.49 | 2 | evet | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 57.6→73.0 | 146 | +287 | 0.725 | 1.000 | sönmüş | 10.72 | 11.25 | 1 | evet | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 41.2→82.5 | 145 | +250 | 0.756 | 1.000 | sönmüş | 10.26 | 11.64 | 1 | evet | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 20.6→61.9 | 145 | +327 | 0.693 | 1.000 | sönmüş | 10.28 | 11.63 | 1 | evet | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 57.6→73.0 | 161 | +348 | 0.692 | 1.000 | sönmüş | 10.74 | 11.24 | 1 | evet | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 41.2→82.5 | 160 | +310 | 0.720 | 1.000 | sönmüş | 10.30 | 11.61 | 1 | evet | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 20.6→61.9 | 159 | +388 | 0.663 | 1.000 | sönmüş | 10.32 | 11.59 | 1 | evet | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 57.6→73.0 | 134 | +237 | 0.767 | 1.000 | sönmüş | 10.72 | 11.26 | 1 | evet | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 41.2→82.5 | 134 | +200 | 0.799 | 1.000 | sönmüş | 10.26 | 11.65 | 1 | evet | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 20.6→61.9 | 133 | +278 | 0.733 | 1.000 | sönmüş | 10.28 | 11.64 | 1 | evet | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 57.6→73.0 | 136 | +247 | 0.758 | 1.000 | sönmüş | 10.72 | 11.25 | 1 | evet | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 41.2→82.5 | 135 | +210 | 0.791 | 1.000 | sönmüş | 10.26 | 11.65 | 1 | evet | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 20.6→61.9 | 135 | +287 | 0.725 | 1.000 | sönmüş | 10.28 | 11.63 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 15 mΩ, Rd 4 mΩ | 57.6→73.0 | 199 | +407 | 0.629 | 1.000 | sönmüş | 10.77 | 11.21 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 15 mΩ, Rd 4 mΩ | 41.2→82.5 | 198 | +377 | 0.650 | 1.000 | sönmüş | 10.41 | 11.52 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 15 mΩ, Rd 4 mΩ | 20.6→61.9 | 198 | +440 | 0.606 | 1.000 | sönmüş | 10.42 | 11.51 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ | 57.6→73.0 | 187 | +368 | 0.657 | 1.000 | sönmüş | 10.78 | 11.20 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ | 41.2→82.5 | 186 | '+338'.replace("'","") | 0.680 | 1.000 | sönmüş | 10.40 | 11.52 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ | 41.2→82.5 | 186 | +338 | 0.680 | 1.000 | sönmüş | 10.40 | 11.52 | 1 | evet | içinde | GEÇTİ |
| anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ | 20.6→61.9 | 185 | +401 | 0.633 | 1.000 | sönmüş | 10.42 | 11.51 | 1 | evet | içinde | GEÇTİ |
| en çok kayıp (sıcak bakır/RDS, VF azami) | 57.6→73.0 | 262 | +627 | 0.489 | 1.000 | sönmüş | 10.77 | 11.21 | 2 | evet | içinde | GEÇTİ |
| en çok kayıp (sıcak bakır/RDS, VF azami) | 41.2→82.5 | 261 | +598 | 0.506 | 1.000 | sönmüş | 10.42 | 11.50 | 2 | evet | içinde | GEÇTİ |
| en çok kayıp (sıcak bakır/RDS, VF azami) | 20.6→61.9 | 259 | +658 | 0.472 | 1.000 | sönmüş | 10.43 | 11.49 | 2 | evet | içinde | GEÇTİ |
| soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır) | 57.6→73.0 | 430 | +1247 | 0.241 | 1.000 | sönmüş | 10.74 | 11.24 | 6 | evet | içinde | GEÇTİ |
| soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır) | 41.2→82.5 | 428 | +1224 | 0.248 | 1.000 | sönmüş | 10.41 | 11.50 | 6 | evet | içinde | GEÇTİ |
| soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır) | 20.6→61.9 | 426 | +1272 | 0.235 | 1.000 | sönmüş | 10.43 | 11.49 | 6 | evet | içinde | GEÇTİ |

Tam 3. derece durum uzayı ifadesi ve geçerlilik sınırı (`hesap.py` `cpl()`): durumlar `[iL, vCout, vCd]`, seri L + Rs (Rs = DCR + D·Ron + (1−D)·Rd), paralel kol Cout + ESR, paralel sönüm dalı Cd + Rd, yük i = P/v; denge noktası vo = vth − Rs·P/vo (`Cd` DC'yi keser).

```
6) Sabit güç yükü (CPL) ile açık çevrim kararlılığı — 3. derece tam ifade (şematik Cd=470 µF + Rd=0,22 Ω dahil)
   Durum uzayı [iL, vCout, vCd], gerçek denge noktası; C−%20 setlerinde Cd de −%20 (376 µF); duty 57,64 W'ta 11 V'a ayarlı, 24,6 V
   sönüm = −max Re(s) > 0: salınım söner (zaman sabiti 1/sönüm); sönüm < 0: BÜYÜR. Geçerlilik: cpl() açıklaması.
   model seti                                               Rs mΩ  Pkritik W | 57,64 W: sönüm 1/s | 73 W: Vo V  sönüm 1/s  τ ms   | 82,5 W: sönüm 1/s  τ ms
   anma (şematik)                                            14.7    256.6   |    +646.9          | 10.979    +602.2       2   |    +574.1       2
   pencere köşesi: L+%20, C−%20, ESR 15 mΩ                   14.7    146.0   |    +345.1          | 10.979    +287.2       3   |    +251.0       4
   el sarım: L+%8, C−%20, ESR 15 mΩ                          14.7    160.6   |    +405.9          | 10.979    +347.9       3   |    +311.6       3
   en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ             10.8    134.3   |    +294.9          | 10.985    +237.3       4   |    +201.3       5
   en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ     14.1    136.0   |    +305.4          | 10.980    +247.2       4   |    +210.8       5
   anma L/C, ESR 15 mΩ, Rd 4 mΩ                              12.1    199.1   |    +454.0          | 10.983    +407.4       2   |    +378.2       3
   anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ                     12.1    186.8   |    +415.3          | 10.983    +368.1       3   |    +338.7       3
   en çok kayıp (sıcak bakır/RDS, VF azami)                  16.3    262.0   |    +672.0          | 10.977    +627.2       2   |    +599.1       2
   soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır)                14.7    430.1   |   +1282.3          | 10.979   +1247.3       1   |   +1225.1       1
   ↑ = büyüyen salınımın zaman sabiti. Dalsız basitleştirilmiş sınır (Rs·ESR ve Cd-Rd yok, Vo = 11 V): anma 182 W, köşe 73 W.
   Sönüm dalıyla (470 µF + 0,22 Ω) yukarıdaki model setlerinde Pkritik > 82,5 W; diğer kombinasyonlar kanıtlanmaz.
```

- **9 model seti × 3 sabit güç adımı = 27 satırın tamamında HESAP ve SİM uyuşur ve tamamı GEÇER** (`10,26–11,65 V`, darbe sonunda yavaş salınım ≤ 6 mV t-t).
- En sert kombinasyonda bile (`L +%20`, `Cout −%20`, `Cd −%20`, `DCR 6,5 mΩ`, `Ron 4,7 mΩ`, `Rd_diyot 4 mΩ`, sıcak `Cout ESR 10 mΩ`) kritik güç `Pkritik = 126 W`'tır (82,5 W modül zarfının **1,53 katı**); sönüm zaman sabiti ≤ 5 ms'dir.
- Böylece `Cout`'un ölçülmemiş alt ESR sınırı artık bir kararlılık riski oluşturmaz; `Cout` seçimi yalnızca üst empedans/ESR (≤ 35 mΩ @100 kHz) ve ripple akımı ile sınırlanır.

## 7. Genel modül zarfı (SİM)

`python buck/dogrula.py zarf`. Genel modül için ayrı sınır tanımlanmadığından genel GEÇTİ/KALDI kararı yoktur; son sütun O1/S2E uyumluluğudur.

### 7.1 Kararlı durum, 0,24 A – 7,5 A, beş giriş (Ton her noktada 11 V'a ayarlı)

| Vin V | Yük | Ton µs | Kip | Vo V | kayma mV/ms | ΔVo mV | IL tepe A | iletim kaybı W |
|---|---|---|---|---|---|---|---|---|
| 20 | düşük 0,24 A | 3.125 | DCM | 10.997 | -0.2 | 26.4 | 0.85 | 0.04 |
| 20 | %25 | 5.587 | CCM | 11.000 | -0.0 | 45.7 | 2.64 | 0.37 |
| 20 | %50 | 5.601 | CCM | 11.000 | +0.0 | 45.5 | 4.51 | 0.84 |
| 20 | %75 | 5.614 | CCM | 11.000 | +0.0 | 45.2 | 6.39 | 1.40 |
| 20 | %100 | 5.627 | CCM | 11.000 | +0.0 | 45.0 | 8.26 | 2.06 |
| 22.2 | düşük 0,24 A | 2.660 | DCM | 10.996 | -0.2 | 27.9 | 0.91 | 0.05 |
| 22.2 | %25 | 5.042 | CCM | 11.000 | +0.0 | 51.4 | 2.73 | 0.41 |
| 22.2 | %50 | 5.054 | CCM | 11.000 | +0.0 | 51.1 | 4.61 | 0.92 |
| 22.2 | %75 | 5.066 | CCM | 11.000 | +0.0 | 50.9 | 6.48 | 1.52 |
| 22.2 | %100 | 5.078 | CCM | 11.000 | +0.0 | 50.6 | 8.36 | 2.23 |
| 24.6 | düşük 0,24 A | 2.293 | DCM | 10.996 | -0.2 | 29.2 | 0.95 | 0.05 |
| 24.6 | %25 | 4.557 | CCM | 11.000 | +0.0 | 56.4 | 2.81 | 0.45 |
| 24.6 | %50 | 4.568 | CCM | 11.000 | +0.0 | 56.2 | 4.69 | 0.99 |
| 24.6 | %75 | 4.579 | CCM | 11.000 | +0.0 | 55.9 | 6.57 | 1.63 |
| 24.6 | %100 | 4.590 | CCM | 11.000 | +0.0 | 55.7 | 8.44 | 2.38 |
| 25.2 | düşük 0,24 A | 2.218 | DCM | 10.996 | -0.2 | 29.5 | 0.96 | 0.06 |
| 25.2 | %25 | 4.450 | CCM | 11.000 | +0.0 | 57.5 | 2.83 | 0.46 |
| 25.2 | %50 | 4.460 | CCM | 11.000 | -0.0 | 57.3 | 4.71 | 1.01 |
| 25.2 | %75 | 4.471 | CCM | 11.000 | -0.0 | 57.0 | 6.58 | 1.66 |
| 25.2 | %100 | 4.482 | CCM | 11.000 | -0.0 | 56.8 | 8.46 | 2.41 |
| 26 | düşük 0,24 A | 2.124 | DCM | 10.996 | -0.2 | 29.9 | 0.97 | 0.06 |
| 26 | %25 | 4.314 | CCM | 11.000 | -0.0 | 59.0 | 2.86 | 0.47 |
| 26 | %50 | 4.325 | CCM | 11.000 | -0.0 | 58.7 | 4.73 | 1.03 |
| 26 | %75 | 4.335 | CCM | 11.000 | +0.0 | 58.4 | 6.61 | 1.69 |
| 26 | %100 | 4.346 | CCM | 11.000 | -0.0 | 58.2 | 8.48 | 2.45 |

Kararlı çalışma noktası yük tipinden (CR/CC/CP) bağımsızdır; tip yalnız dinamiği değiştirir. 0 A'de sabit Ton ile çıkış giriş gerilimine tırmanır: açık çevrimde tanımlı değildir, geri besleme gerektirir. DCM satırındaki kayma (−0,2 mV/ms) 16 ms'de oturmamış koşuyu gösterir.

### 7.2 Yük adımları: %25 ↔ %75 ve %50 → %100, CP / CC / CR (CP 200 ms, CC ve CR 50 ms)

| Vin V | Tip | P W (@11 V) | Vmin V | Vmax V | ara kararlı V | son kararlı V | sönüm | IL tepe A | O1/S2E 9–12 V |
|---|---|---|---|---|---|---|---|---|---|
| 20 | CP | 20.6→61.9→20.6 | 10.44 | 11.49 | 10.95 | 11.00 | sönmüş | 9.0 | içinde |
| 20 | CC | 20.6→61.9→20.6 | 10.47 | 11.47 | 10.95 | 11.00 | sönmüş | 8.6 | içinde |
| 20 | CR | 20.6→61.9→20.6 | 10.50 | 11.46 | 10.95 | 11.00 | sönmüş | 8.3 | içinde |
| 20 | CP | 41.2→82.5→41.2 | 10.42 | 11.50 | 10.95 | 11.00 | sönmüş | 11.0 | içinde |
| 20 | CC | 41.2→82.5→41.2 | 10.47 | 11.47 | 10.95 | 11.00 | sönmüş | 10.5 | içinde |
| 20 | CR | 41.2→82.5→41.2 | 10.51 | 11.45 | 10.95 | 11.00 | sönmüş | 10.1 | içinde |
| 24.6 | CP | 20.6→61.9→20.6 | 10.43 | 11.49 | 10.94 | 11.00 | sönmüş | 9.2 | içinde |
| 24.6 | CC | 20.6→61.9→20.6 | 10.47 | 11.48 | 10.94 | 11.00 | sönmüş | 8.8 | içinde |
| 24.6 | CR | 20.6→61.9→20.6 | 10.50 | 11.47 | 10.95 | 11.00 | sönmüş | 8.5 | içinde |
| 24.6 | CP | 41.2→82.5→41.2 | 10.42 | 11.50 | 10.94 | 11.00 | sönmüş | 11.2 | içinde |
| 24.6 | CC | 41.2→82.5→41.2 | 10.47 | 11.48 | 10.94 | 11.00 | sönmüş | 10.7 | içinde |
| 24.6 | CR | 41.2→82.5→41.2 | 10.50 | 11.46 | 10.95 | 11.00 | sönmüş | 10.3 | içinde |
| 26 | CP | 20.6→61.9→20.6 | 10.43 | 11.49 | 10.94 | 11.00 | sönmüş | 9.2 | içinde |
| 26 | CC | 20.6→61.9→20.6 | 10.46 | 11.48 | 10.94 | 11.00 | sönmüş | 8.9 | içinde |
| 26 | CR | 20.6→61.9→20.6 | 10.49 | 11.47 | 10.95 | 11.00 | sönmüş | 8.6 | içinde |
| 26 | CP | 41.2→82.5→41.2 | 10.42 | 11.50 | 10.94 | 11.00 | sönmüş | 11.2 | içinde |
| 26 | CC | 41.2→82.5→41.2 | 10.46 | 11.48 | 10.94 | 11.00 | sönmüş | 10.7 | içinde |
| 26 | CR | 41.2→82.5→41.2 | 10.50 | 11.46 | 10.95 | 11.00 | sönmüş | 10.3 | içinde |

Şematik anma değerleriyle üç yük tipinde ve üç girişte adımlar **10,42–11,50 V** içinde (±%5,3) ve sönümlüdür; dalsız devreye (`10,28–11,63 V`) göre geçici sapma ≈ 270 mV daralmıştır. Tolerans köşelerindeki CP sonuçları §6.2'dedir (`10,26–11,65 V`).

### 7.3 Tam yük atma 82,5 → 0 W, kontrolcü gecikmesiyle

| Model | Vin V | 0 periyot V | 1 periyot V | 2 periyot V | 3 periyot V |
|---|---|---|---|---|---|
| anma | 24.6 | 11.247 | 11.307 | 11.361 | 11.413 |
| anma | 26 | 11.248 | 11.309 | 11.362 | 11.414 |
| köşe L+%20, C−%20, ESR 35 mΩ | 24.6 | 11.245 | 11.316 | 11.384 | 11.450 |
| köşe L+%20, C−%20, ESR 35 mΩ | 26 | 11.246 | 11.317 | 11.385 | 11.451 |
| soğuk ESR 120 mΩ (üst sınır) | 24.6 | 11.630 | 11.690 | 11.725 | 11.757 |
| soğuk ESR 120 mΩ (üst sınır) | 26 | 11.634 | 11.693 | 11.728 | 11.760 |

Her PWM periyodu gecikme ≈ 60–70 mV ekler. **`Cd + Rd` dalının ek kazanımı:** yük anında kesildiğinde ilk sıçrama `120 mΩ || 0,22 Ω ≈ 78 mΩ` üzerinden oluştuğundan, sınanan senaryoda soğuk ESR üst sınırıyla (120 mΩ) tepe **11,97–12,13 V'tan 11,63–11,76 V'a düşer ve 3 periyot gecikmede 12 V altında kalır**. Bu senaryoda `Rd_toplam = 0,22 Ω` alınmıştır; soğukta `Rd_toplam ≈ 0,35 Ω` olursa yalnız ilk sıçrama `7,5 A × (0,12 || 0,35 Ω) ≈ 0,67 V` olarak hesaplanır. Gecikme ve sonraki tepe bu hesapla doğrulanmış değildir.

## 8. Köşe model setleri ve veri sayfası kanıtı

Tek bir "en kötü" set yoktur: sönüm için en kötü olan (düşük direnç) kayıp için en iyidir. Bu yüzden ayrı setler kullanılır (`dogrula.py` `SECILEN`, `EN_AZ_SONUM`, `EN_AZ_SONUM_SICAK`, `EN_COK_KAYIP`, `SOGUK`).

| Set | L / Cout / Cd | Cout ESR ve Rd | DCR | S1 Ron | D1 (çift) | Kullanım |
|---|---|---|---|---|---|---|
| Anma (şematik) | 33 µH / 1000 µF / 470 µF | ESR 35 mΩ (Zmax), Rd 0,22 Ω | 7,81 mΩ (HESAP) | 5,6 mΩ (25 °C azami) | 0,38 V + 8 mΩ | §5 |
| En az sönüm | × 1,2 / × 0,8 / × 0,8 | ESR 15 mΩ (senaryo), Rd 0,22 Ω | 6,5 mΩ (denenen alt sınır) | 4,7 mΩ (25 °C tipik; en düşük değer yayımlanmamış) | 0,39 V + 4 mΩ (25 °C tipik, 10–20 A) | §6 |
| En az sönüm, sıcak | × 1,2 / × 0,8 / × 0,8 | ESR 10 mΩ (**TAHMİN**), Rd 0,22 Ω | 7,81 mΩ | 6,6 mΩ (4,7 × 1,4) | 0,265 V + 6 mΩ (125 °C tipik) | §6 |
| En çok kayıp | anma | ESR 35 mΩ, Rd 0,22 Ω | 10,3 mΩ (100 °C bakır) | 7,84 mΩ (5,6 × 1,4, 100 °C) | 0,415 V + 4,5 mΩ (25 °C azami) | §6, §9 |
| Soğuk | anma | ESR 120 mΩ (−10 °C Zmax, **üst sınır**), Rd 0,22 Ω | 7,81 mΩ | 5,6 mΩ | 0,38 V + 8 mΩ | §6, §7.3 |

- **D1 çifti (DATASHEET, STPS40M60C Doc ID 018813 Rev 1, Tablo 4, diyot başına):** 5 / 10 / 20 A'de VF tipik 0,430 / 0,470 / 0,540 V (25 °C), 0,325 / 0,385 / 0,475 V (125 °C); azami 0,460 / 0,505 / 0,595 V (25 °C). İki bacak paralelken aynı gerilimde akım iki katıdır; çiftin eğimi 10–20 A toplam aralığında 4 mΩ (25 °C tipik), 6 mΩ (125 °C tipik) olur. Şematikteki 8 mΩ tek diyodun eğimidir: **kayıp için kötümser, sönüm için iyimserdir.** 7,5 A toplamda (3,75 A/bacak) eğri bu doğrulardan daha diktir; o noktanın sayısı yayımlanmamıştır, bu yüzden 4–6 mΩ bir **senaryo aralığıdır**, üretici garantisi değildir.
- **S1 (DATASHEET, [STP100N6F7 DocID027212 Rev 2](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf), Tablo 4):** VGS=10 V, ID=50 A koşulunda RDS(on) 4,7 mΩ tipik / 5,6 mΩ azami; en düşük değer yok. Sıcaklık çarpanı eğriden okunmuştur.
- **Cout / Cin:** üretici **ESR yayımlamaz**; 35 / 15 mΩ (20 °C) ve 120 / 38 mΩ (−10 °C) 100 kHz'teki en büyük **empedanstır** (|Z|), ESR değildir. Cin'de ESL reaktansı (≈ 26 nH → 16 mΩ @100 kHz) aynı büyüklüktedir. tanδ 120 Hz'te verilir ve 0,9 kHz ESR'sini doğrudan vermez. 15 ve 10 mΩ senaryodur. **ÖLÇÜM YOK.**
- **L1:** AL 69 nH ±%8 (DATASHEET) → 30,7–36,1 µH; DCR ve L(I) HESAP. **ÖLÇÜM YOK.** Köşe testlerindeki +%20, satın alınan bobinin toleransıdır; el sarım için +%8 ayrı satırda verilmiştir.

## 9. Kayıp, ısı ve gerilim stresi (Adım 3 girdisi; HESAP ve ideal olmayan SİM)

Bu bölüm Adım 3'ün hesap kısmıdır. Sürücü, soğutucu ve yerleşim seçilmediği için sayılar **kestirimdir**; hiçbiri ölçülmedi.

### 9.1 Kayıp bütçesi

```
7) Kayıp bütçesi, 7,5 A (HESAP; sürücü seçilmedi: Rg toplam ve 10 V sürme VARSAYIM)
   L1 çekirdek: ΔB = volt·saniye/(N·Ae); 900 mW/cm³ @100 kHz/100 mT noktasından B² ile ölçekleme (TAHMİN, üst sınır değil)
     Vin 20.0 V: volt·saniye  50.2 µV·s, ΔB  13.1 mT t-t, çekirdek ≈ 0.085 W
     Vin 22.2 V: volt·saniye  56.5 µV·s, ΔB  14.8 mT t-t, çekirdek ≈ 0.108 W
     Vin 24.6 V: volt·saniye  62.1 µV·s, ΔB  16.2 mT t-t, çekirdek ≈ 0.130 W
     Vin 25.2 V: volt·saniye  63.3 µV·s, ΔB  16.5 mT t-t, çekirdek ≈ 0.136 W
     Vin 26.0 V: volt·saniye  64.9 µV·s, ΔB  17.0 mT t-t, çekirdek ≈ 0.142 W
     Çekirdek kaybı akım ripple'ına değil volt·saniyeye bağlıdır: L −%30 köşesinde (ΔIL 2,8 A) ΔB DEĞİŞMEZ.
   Vin     S1 iletim  S1 anaht. (Rg 5/10/25 Ω)   D1 iletim  L1 bakır  L1 çekirdek  Cin    Cout   toplam (Rg 10)  verim %   kapı sürme
   20.0     0.18      0.32 / 0.50 / 1.05           1.44       0.44       0.09      0.10  0.005      2.75        96.77     30 mW
   22.2     0.16      0.36 / 0.56 / 1.17           1.62       0.44       0.11      0.11  0.006      3.01        96.48     30 mW
   24.6     0.15      0.40 / 0.63 / 1.30           1.78       0.44       0.13      0.11  0.007      3.24        96.22     30 mW
   25.2     0.14      0.42 / 0.65 / 1.34           1.82       0.44       0.14      0.11  0.008      3.30        96.16     30 mW
   26.0     0.14      0.43 / 0.67 / 1.39           1.86       0.44       0.14      0.10  0.008      3.37        96.07     30 mW
   Sönüm dalı (Cd=470 µF + Rd=0.22 Ω, 26 V): ripple akımı 76 mA RMS, Rd kaybı 1.3 mW (toplama dahildir).
   Geçiş süreleri (Rg 10 Ω, 26 V): açma 24 ns, kapama 24 ns; bileşenler: geçiş 0.48 W, Coss 0.05 W, D1 kapasitesi 0.15 W
   Snubber kaybı (kullanılırsa) C·V²·f: 1 nF → 68 mW, 2,2 nF → 149 mW (26 V). Sayılar kestirimdir; ölçülmedi.
```

- İdeal model verimi (%97,1–97,6) **gerçek verim değildir**; anahtarlama, çekirdek ve giriş kondansatörü kayıplarıyla kestirim %96,1–96,8'dir (Rg 10 Ω varsayımıyla).
- **Çekirdek kaybı ≈ 0,09–0,14 W (TAHMİN).** ΔB volt·saniyeden hesaplanır (13–17 mT t-t); veri sayfasının tek noktası (900 mW/cm³ azami @ 100 kHz / 100 mT) B² ile ölçeklendi. Bu varsayım ilgili düşük akı ve DC bias koşullarında üreticinin garanti ettiği bir üst sınır değildir. 0,22 W bu hesapla doğrulanamadı. Aynı volt·saniye ve sarım varsayımında L −%30 köşesinde ΔB değişmez.
- S1 anahtarlama kaybı toplam kapı direncine doğrusal bağlıdır (0,4–1,4 W). Parazitikli SİM (§9.3) aynı büyüklükte sonuç verir (S1 toplam 0,3–0,6 W).

### 9.2 Isıl denge ve soğutucu

```
8) Isıl denge (HESAP; Rth(ped) = 1 K/W ve soğutucu değerleri VARSAYIM, parça seçilmedi)
   D1 çifti: iletim kaybı sıcaklıkla düşer, ters kaçak ≈ her 12 K'de ikiye katlanır; denge Tj = Ta + Rth·P(Tj)
   'KAÇAK' = sabit nokta yok veya dP/dTj ≥ 1/Rth (veri sayfası Tablo 2 dipnot 3 koşulu sağlanmıyor)
   senaryo  Rth(s-a) K/W   Ta 25 °C: Tj / P   Ta 50 °C: Tj / P   Ta 60 °C: Tj / P
   tipik    soğutucusuz    KAÇAK             KAÇAK             KAÇAK
   tipik    20                61 °C / 1.63 W      84 °C / 1.56 W      94 °C / 1.55 W
   tipik    12                48 °C / 1.68 W      72 °C / 1.59 W      82 °C / 1.56 W
   tipik    8                 42 °C / 1.70 W      66 °C / 1.61 W      76 °C / 1.58 W
   tipik    5                 37 °C / 1.73 W      61 °C / 1.62 W      71 °C / 1.59 W
   azami    soğutucusuz    KAÇAK             KAÇAK             KAÇAK
   azami    20                63 °C / 1.74 W      88 °C / 1.71 W      99 °C / 1.76 W
   azami    12                50 °C / 1.79 W      74 °C / 1.72 W      84 °C / 1.71 W
   azami    8                 43 °C / 1.82 W      67 °C / 1.73 W      77 °C / 1.71 W
   azami    5                 38 °C / 1.85 W      62 °C / 1.75 W      72 °C / 1.72 W
     D1 azami @Tj  25 °C, 26 V: iletim 1.90 W + ters 0.00 W (IR 0 mA toplam) = 1.90 W
     D1 azami @Tj  75 °C, 26 V: iletim 1.66 W + ters 0.05 W (IR 5 mA toplam) = 1.71 W
     D1 azami @Tj 100 °C, 26 V: iletim 1.54 W + ters 0.23 W (IR 20 mA toplam) = 1.77 W
     D1 azami @Tj 125 °C, 26 V: iletim 1.42 W + ters 0.96 W (IR 85 mA toplam) = 2.38 W
     D1 azami @Tj 150 °C, 26 V: iletim 1.30 W + ters 4.08 W (IR 360 mA toplam) = 5.38 W
   S1 (RDS(on) azami, Rg 10 Ω, 20 V giriş = en yüksek iletim):
     soğutucusuz (62,5 K/W, DATASHEET)   69 °C / 0.71 W      96 °C / 0.74 W     107 °C / 0.75 W
     ped + 12 K/W                        35 °C / 0.68 W      60 °C / 0.70 W      70 °C / 0.71 W
     ped + 8 K/W                         32 °C / 0.68 W      57 °C / 0.70 W      67 °C / 0.71 W
   Ortak soğutucu (S1 + D1 aynı soğutucuda, ayrı pedlerle), D1 azami, S1 azami, 26 V:
     Rth(s-a) 12.0 K/W:  Ta 25: Ts   56 / TjD1   59 °C   Ta 50: Ts   81 / TjD1   84 °C   Ta 60: Ts   91 / TjD1   94 °C
     Rth(s-a)  8.0 K/W:  Ta 25: Ts   46 / TjD1   49 °C   Ta 50: Ts   70 / TjD1   74 °C   Ta 60: Ts   80 / TjD1   84 °C
     Rth(s-a)  5.0 K/W:  Ta 25: Ts   38 / TjD1   42 °C   Ta 50: Ts   63 / TjD1   66 °C   Ta 60: Ts   73 / TjD1   76 °C
   L1 @ 20 °C sargı: DCR 7.81 mΩ, bakır 0.44 W (bunun AC payı 3 mW) + çekirdek → 0.58 W; ΔT ≈ (mW/cm²)^0,833 = 4 K (Magnetics yaklaşık formülü)
   L1 @ 75 °C sargı: DCR 9.50 mΩ, bakır 0.54 W (bunun AC payı 3 mW) + çekirdek → 0.68 W; ΔT ≈ (mW/cm²)^0,833 = 5 K (Magnetics yaklaşık formülü)
   L1 @100 °C sargı: DCR 10.27 mΩ, bakır 0.58 W (bunun AC payı 3 mW) + çekirdek → 0.72 W; ΔT ≈ (mW/cm²)^0,833 = 5 K (Magnetics yaklaşık formülü)
   L1 doyma: L/L0 @8,9 A 97 %, @12 A 95 %, @20 A 88 %, @53 A 59 % (eğriden yaklaşık; ölçüm yok)
   Cin ripple: 3.77 A toplam → adet başına 1.88 A (anma 3.25 A @105 °C); Cout: 0.48 A (anma 1.9 A)
```

- **D1 soğutucusuz kullanılamaz:** TO-220'nin soğutucusuz ısıl direnciyle (62,5 K/W, TAHMİN) sabit nokta yoktur; ters kaçak akımı sıcaklıkla üstel büyür ve ısıl kaçak oluşur. Bu bir model çıktısıdır (IR'nin sıcaklık ve gerilimle değişimi eğriden okunmuştur); "kaçar" hükmü ölçümle doğrulanmalıdır, ama soğutucu gereği modelden bağımsız olarak açıktır (1,7–1,9 W).
- **Soğutucu boyutu (HESAP):** D1 ve S1 ortak soğutucuda, yalıtım pediyle (1 K/W varsayımı), 60 °C ortamda Tj(D1) ≤ 100 °C için **Rth(s-a) ≤ 12 K/W**; ≤ 85 °C için ≤ 8 K/W. Veri sayfasının kaçak koşulu (dP/dTj < 1/Rth(j-a)) 12 K/W'ta sağlanır. **Soğutucu parça numarası seçilmedi**; kılıf, montaj ve hava akışı belli olmadan bu yalnız bir hedeftir.
- S1 soğutucusuz da 107 °C'ta dengeye gelir (175 °C sınırına göre); ortak soğutucuda 70 °C civarındadır.
- L1 sıcaklık artışı ≈ 5 K (Magnetics'in yüzey alanı formülü, yaklaşık). Doyma: 8,9 A'de %97, 12 A'de %95.
- Prototipte ölçülecekler: D1 ve S1 kasa sıcaklığı (termokupl), soğutucu sıcaklığı, L1 sargı ve çekirdek sıcaklığı (termal kamera veya termokupl), 25 °C ve en az 50 °C ortamda, 7,5 A'de ısıl denge sağlanana kadar.

### 9.3 Anahtarlama zili ve gerilim stresi (`dogrula.py stres` §1)

Veri sayfası değerlerinden **türetilmiş** VDMOS ve Schottky modeli (ST'nin SPICE modeli değildir), varsayılan parazitikler: elektrolitik ESL 26 nH/adet, hücreye bara endüktansı 10–40 nH, TO-220 bacakları, ortak kaynak endüktansı 7,5 nH; kapı, anahtar düğümüne göre yüzen ideal 10 V kaynak + Rg (sürücü seçilmedi).

| Senaryo | Vin V | S1 VDS tepe V (anma 60) | D1 ters tepe V (anma 60) | V(sw) dip V | hücre barası tepe V | S1 toplam kayıp W | D1 kayıp W | snubber kaybı mW | ΔVo mV (Cout ESL 15 nH) |
|---|---|---|---|---|---|---|---|---|---|
| temel: bara 20 nH, Rg 10 Ω, MLCC yok, snubber yok | 26 | 46.1 | 63.1 | -4.1 | 45.5 | 0.42 | 1.79 | 0 | 77 |
| bara 10 nH | 26 | 41.6 | 56.3 | -4.2 | 36.8 | 0.46 | 1.79 | 0 | 77 |
| bara 40 nH | 26 | 54.8 | 69.7 | -3.9 | 56.1 | 0.40 | 1.79 | 0 | 74 |
| Rg 4,7 Ω | 26 | 47.3 | 65.7 | -4.3 | 46.8 | 0.31 | 1.78 | 0 | 74 |
| Rg 22 Ω | 26 | 43.4 | 58.5 | -3.6 | 43.2 | 0.63 | 1.82 | 0 | 87 |
| MLCC 4,7 µF etkin | 26 | 37.0 | 47.6 | -4.4 | 26.8 | 0.50 | 1.77 | 0 | 71 |
| MLCC + snubber 4,7 Ω / 1 nF | 26 | 36.6 | 41.2 | -5.2 | 26.6 | 0.49 | 1.77 | 52 | 71 |
| MLCC + snubber 2,2 Ω / 2,2 nF | 26 | 32.4 | 36.2 | -4.5 | 26.6 | 0.50 | 1.77 | 87 | 72 |
| MLCC + snubber 10 Ω / 470 pF | 26 | 37.3 | 44.3 | -4.9 | 26.6 | 0.49 | 1.77 | 32 | 71 |
| snubber 4,7 Ω / 1 nF, MLCC yok | 26 | 43.9 | 51.1 | -4.9 | 40.4 | 0.39 | 1.79 | 103 | 79 |
| bara 40 nH, Rg 4,7 Ω (en sert) | 26 | 56.2 | 69.9 | -4.0 | 56.1 | 0.29 | 1.78 | 0 | 70 |
| temel, 28 V | 28 | 48.1 | 66.7 | -4.1 | 48.3 | 0.44 | 1.89 | 0 | 79 |
| bara 40 nH, Rg 4,7 Ω, 28 V | 28 | 57.8 | 75.3 | -4.0 | 60.4 | 0.29 | 1.87 | 0 | 73 |
| MLCC + snubber 4,7 Ω / 1 nF, 28 V | 28 | 38.7 | 43.6 | -5.2 | 28.8 | 0.53 | 1.87 | 57 | 76 |

- Bu sayılar **aynı fiziksel devrenin doğrulanmış tepe değerleri değildir**; modele ve yerleşime bağlı bir duyarlılık çalışmasıdır. Denetim raporlarındaki 60–88 V aralığı da aynı sınıftadır.
- Seramik kondansatör olmadan elektrolitiklerin ESL'i hücre barasını 45–60 V'a sallar; **D1 ters gerilimi 60 V anmayı aşar** (63–75 V), S1 VDS 46–58 V ile anmaya dayanır (60 V mutlak sınıra pay yok).
- Hücreye yakın 4,7 µF etkin seramik kondansatörle D1 48 V, S1 37 V'a iner; 2,2 Ω + 2,2 nF RC ile 36 / 32 V (kayıp ≈ 86 mW).
- 60 V'luk parçalar için sonuç: **seramik giriş dekuplajı zorunlu**, RC sönümleyici için yer ayrılmalı. Tepe değerler **PROTOTİPTE ÖLÇÜLECEK**.

### 9.4 Giriş sıcak takma ve S1 kısa devre arızası

Sıcak takma (`dogrula.py stres` §2; aynı süpürmenin HESAP karşılığı `hesap.py` §9): 26 V basamak, anahtar kapalı, yüksüz.

| R kaynak mΩ \ L kaynak µH (V tepe / A tepe) | 0.2 | 0.5 | 1 | 2 | 5 | 10 |
|---|---|---|---|---|---|---|
| 5 | 28.4 / 1200 | 32.7 / 958 | 36.1* / 776 | 39.4* / 610 | 43.1* / 427 | 45.3* / 319 |
| 10 | 26.1 / 995 | 29.1 / 826 | 32.6 / 689 | 36.2* / 556 | 40.5* / 400 | 43.3* / 304 |
| 20 | 26.0 / 738 | 26.1 / 644 | 28.1 / 560 | 31.5 / 470 | 36.3* / 355 | 39.7* / 277 |
| 40 | 26.0 / 481 | 26.0 / 443 | 26.0 / 404 | 26.6 / 357 | 30.6 / 288 | 34.3 / 235 |
| 80 | 26.0 / 281 | 26.0 / 269 | 26.0 / 256 | 26.0 / 238 | 26.1 / 207 | 28.1 / 179 |

`*` = 35 V aşıldı. SİM tablosunda kaynak direnci ≥ 40 mΩ ise tepe 26–34 V'tur; daha düşük direnç ve yüksek endüktansla 35 V aşılabilir. C −%20 ve sıcak ESR senaryosunda ideal basamak HESAP 5 µH için 46,5 V, 10 µH için 48,0 V verir. Kullanıcının belirlediği **Cin ≥ 50 V** hedefine bu son örnekte yalnız %4 nominal pay kalır; gerçek kaynak ve geçici durum bilinmediğinden sınıfın yeterliliği açık risktir. Ani akım 180–1200 A'dir (kontak ve kondansatör için ayrı risk; Adım 7).

S1 kısa devre (`dogrula.py stres` §3; ideal elemanlar, Cd=470 µF + Rd=0,22 Ω dahil, batarya + kablo varsayımı):

| Batarya V | Yük | Vo tepe V | Vo son V | IL tepe A | Cout 25 V anması | Cout/Cd 35 V kriteri |
|---|---|---|---|---|---|---|
| 24.6 | 7,5 A direnç | 27.3 | 23.6 | 70 | AŞILIR | içinde |
| 24.6 | 0,24 A direnç | 29.2 | 24.6 | 62 | AŞILIR | içinde |
| 24.6 | 57,6 W sabit güç | 29.2 | 24.5 | 65 | AŞILIR | içinde |
| 26 | 7,5 A direnç | 29.0 | 24.9 | 76 | AŞILIR | içinde |
| 26 | 0,24 A direnç | 31.1 | 26.0 | 69 | AŞILIR | içinde |
| 26 | 57,6 W sabit güç | 31.1 | 25.9 | 72 | AŞILIR | içinde |

- Sınanan senaryolarda çıkış giriş gerilimine oturur (24–26 V) ve geçişte **27,3–31,1 V**'a çıkar (yüksüz açık çevrimde de girişe tırmanır). Kullanıcı kararıyla (12.11.2026) **Cout ve Cd gerilim sınıfı ≥ 35 V** hedeflendi; bu örnek tepeler hedefin altındadır ancak gerçek arızalarda yeterli pay kanıtlanmamıştır (mevcut 25 V aday kesin seçimde ≥35 V hedefini sağlamalıdır).
- O1 için: çıkış 12 V'un çok üstüne çıkar; bağımsız aşırı gerilim koruması şarttır (Adım 7).

```
9) Gerilim sınıfları ve arıza arayüzü (HESAP; kaynak R/L VARSAYIM süpürmesi)
   Sıcak takma: boş Cin'e 26 V basamak, tepe V(Cin) [V]; 35 V aşılırsa * (50 V kriteri altında kalır; ESR 7,5 mΩ, C 2000 µF)
     R kaynak mΩ \ L µH    0.2    0.5      1      2      5     10
          5              29.2   33.7   37.1*  40.2*  43.7*  45.8*
         10              26.2   29.7   33.3   36.8*  41.0*  43.7*
         20              26.0   26.1   28.4   31.9   36.7*  40.0*
         40              26.0   26.0   26.0   26.8   30.8   34.5
         80              26.0   26.0   26.0   26.0   26.1   28.2
   C −%20 ve sıcak ESR (TAHMİN 2 × 7 mΩ), R 5 mΩ: L 5 µH → 46.5 V; L 10 µH → 48.0 V (HESAP, ideal basamak)
   S1 kısa devre: çıkış kararlı hâlde girişe çıkar (20–26 V), geçişte 27,3–31,1 V (SİM) → Cout ve Cd 35 V kriteri içinde (mevcut 25 V aday AŞILIR).
   S1 VDS: 60 V anma; 26 V girişte pay 34 V, 28 V'ta 32 V (zil hariç). D1 VRRM 60 V aynı.
```

13.11.2026: HESAP tablosu düzeltildi. Eski ifade ideal kondansatör gerilimi tepesini uç gerilimi olarak kullanıyordu; güncel hesap seri ESR gerilimini de içerir. Üç örnek nokta, aynı seri RLC ve yaklaşık basamakla yapılan hedefli LTspice koşularıyla karşılaştırıldı (fark < 0,03 V). Yukarıdaki bağımsız `stres` SİM tablosu kendi ESL ve kaynak rampası varsayımlarını korur. Bu örnekler gerçek kablo ve batarya değerlerini doğrulamaz.

Ayrıca 10 µH / 5 mΩ, C 1600 µF / ESR 3,5 mΩ örneğinde düzeltilmiş HESAP **47,976 V**, eşdeğer seri RLC için 1 ns basamaklı hedefli SİM **47,976 V** verdi. Kaynak ve kondansatör modeli basitleştirilmiştir; fiziksel ölçüm değildir. `cpl()` dalsız aşırı sönümlü durumun en yavaş gerçek kutbunu da artık doğru hesaplar; örnek ikinci derece polinom kökleriyle karşılaştırıldı. `Pkritik` araması 600 W sınırında hâlâ kararlıysa artık bu sınırı gerçek sonuç gibi yazmak yerine hata verir. Uzun simülasyonların sonraki tekrar koşuları §13'te belgelenmiştir.

### 9.5 Bu aşamada varılan sonuçlar

| Konu | Sonuç | Durum |
|---|---|---|
| Giriş seramik dekuplajı | Hücreye (S1 drain – D1 anot) yakın, 26 V'ta **etkin** ≥ 4,7 µF. X7R 50 V'luk parçada DC bias düşümü ≈ %50 varsayılırsa anma ≈ 2 × 4,7 µF; gerçek düşüm seçilen parçanın eğrisinden alınmalı | Hedef değer (§12.2'de MPN seçilir) |
| RC sönümleyici (D1 üstü) | Başlangıç adayı 2,2 Ω + 2,2 nF (≈ 87 mW) veya 4,7 Ω + 1 nF (≈ 52 mW); kartta ölçülen zil frekansına göre ayarlanır | Yer ayrılacak (DNP olabilir); **PROTOTİPTE ÖLÇÜLECEK** |
| Soğutucu | S1 + D1 ortak, Rth(s-a) ≤ 12 K/W (hedef ≤ 8), iki kılıf yalıtım pediyle | Hedef değer (§12.2'de MPN seçilir) |
| Cout ve Cd gerilim sınıfı | **≥ 35 V** (kullanıcı kararı, 12.11.2026; S1 kısa devresi tepe 31,1 V'u kapsar; O1 portu için bağımsız OVP yine Adım 7'de) | **Kararlaştırıldı** |
| Cin gerilim sınıfı | **≥ 50 V** (kullanıcı kararı, 12.11.2026); örnek sıcak takma hesabı 48,0 V, gerçek gerilim ve pay doğrulanmadı; ani akım sınırlaması Adım 7'de | **Hedef, yeterlilik açık** |
| Çıkış sönümü | **Çıkışa paralel Cd = 470 µF + seri Rd = 0,22 Ω** şematiğe eklendi ve doğrulandı (§6, §10) | **Uygulandı ve doğrulandı** |

## 10. Sönüm seçenekleri ve seçilen sönüm dalı (`Cd = 470 µF + Rd = 0,22 Ω`)

Dalsız devredeki köşe başarısızlığı için seçenekler ve `Rd` kabul aralığı aynı model setleriyle karşılaştırıldı (`hesap.py` §6b):

```
6b) Sönüm seçenekleri ve Rd tolerans penceresi: Pkritik [W] (HESAP, 24,6 V; 470 µF + 0,22 Ω şematiğe uygulandı)
   Köşe = L +%20, ana Cout −%20, sönüm dalı kondansatörü −%20. ESR senaryoları: 15 mΩ (pencere alt kenarı) ve
   10 mΩ (TAHMİN, sıcak); paralel/büyük kondansatörde ESR parantezdeki oranla ölçeklenir (VARSAYIM, ölçüm yok).
   Rs: şematik (14,7 mΩ) ve en az sönüm (DCR 6,5, Ron 4,7, Rd 4 mΩ → 10,8 mΩ) setleri.
   seçenek                                              anma/35mΩ  köşe/15mΩ  köşe/10mΩ  en az sönüm köşe/15mΩ  köşe/10mΩ   ek kayıp
   dalsız (eski): 33 µH + 1000 µF                           174         72         60                63            51      —
   dalsız + DCR +5 mΩ (≈ 12,8 mΩ)                           188         84         72                75            63      +0,28 W
   dalsız + DCR +10 mΩ (≈ 17,8 mΩ)                          201         95         84                86            75      +0,57 W
   dalsız, Cout 1500 µF (ESR × 0,67 varsayımı)              199         90         78                76            64      —
   dalsız, Cout 2 × 680 µF (eşdeğer ESR × 0,5·1,3)          179         81         70                68            57      —
   dalsız, Cout 2 × 1000 µF (eşdeğer ESR × 0,5)             223        107         95                89            77      —
   sönüm dalı 470 µF + 0,15 Ω (Rd alt kenar)                231        127        119               115           106      ≈ 2 mW
   sönüm dalı 470 µF + 0,22 Ω (SEÇİLEN — şematik)           257        146        138               134           126      ≈ 1,2 mW
   sönüm dalı 470 µF + 0,35 Ω (Rd + Cd ESR)                 285        171        162               160           151      ≈ 0,9 mW
   sönüm dalı 470 µF + 0,60 Ω (soğuk Cd ESR üst sınır)      290        183        173               174           164      ≈ 0,5 mW
   sönüm dalı 1000 µF + 0,15 Ω                              364        236        230               223           217      ≈ 2 mW
   sönüm dalı 1000 µF + 0,33 Ω                              395        284        276               276           268      ≈ 1 mW
   82,5 W zarfının üstünde kalan hücreler doğal (açık çevrim) kararlıdır; altında kalanlar kararsızdır.
```

Sönüm dalı ve toplam dal direnci (`Rd_toplam = ayrık Rd + Cd ESR`) aralığının LTspice doğrulaması (`dogrula.py kararlilik` §3; 41,25 → 82,5 W, 200 ms, dal kondansatörü −%20 = 376 µF):

| Model seti | Sönüm dalı | HESAP Pkritik W | SİM sönüm | Vmin V | Vmax V | 200 ms sonunda yavaş salınım mV | 9–12 V | karar |
|---|---|---|---|---|---|---|---|---|
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | dalsız (eski) | 72 | sürekli salınım | 9.37 | 12.57 | 3125 | DIŞINDA | KALDI |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,15 Ω (alt kenar) | 127 | sönmüş | 10.26 | 11.64 | 1 | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,22 Ω (SEÇİLEN) | 145 | sönmüş | 10.26 | 11.64 | 1 | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,35 Ω (Rd + Cd ESR) | 170 | sönmüş | 10.25 | 11.65 | 1 | içinde | GEÇTİ |
| pencere köşesi: L+%20, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,60 Ω (soğuk Cd ESR) | 182 | sönmüş | 10.22 | 11.68 | 1 | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | dalsız (eski) | 80 | sürekli salınım | 9.49 | 12.95 | 2842 | DIŞINDA | KALDI |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,15 Ω (alt kenar) | 140 | sönmüş | 10.30 | 11.61 | 1 | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,22 Ω (SEÇİLEN) | 160 | sönmüş | 10.30 | 11.61 | 1 | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,35 Ω (Rd + Cd ESR) | 185 | sönmüş | 10.29 | 11.62 | 1 | içinde | GEÇTİ |
| el sarım: L+%8, C−%20, ESR 15 mΩ | 470 µF (−%20) + 0,60 Ω (soğuk Cd ESR) | 195 | sönmüş | 10.26 | 11.64 | 1 | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | dalsız (eski) | 63 | sürekli salınım | 9.36 | 13.40 | 3208 | DIŞINDA | KALDI |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 470 µF (−%20) + 0,15 Ω (alt kenar) | 114 | sönmüş | 10.26 | 11.65 | 1 | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 470 µF (−%20) + 0,22 Ω (SEÇİLEN) | 134 | sönmüş | 10.26 | 11.65 | 1 | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 470 µF (−%20) + 0,35 Ω (Rd + Cd ESR) | 160 | sönmüş | 10.25 | 11.66 | 1 | içinde | GEÇTİ |
| en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ | 470 µF (−%20) + 0,60 Ω (soğuk Cd ESR) | 173 | sönmüş | 10.22 | 11.69 | 1 | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | dalsız (eski) | 58 | sürekli salınım | 9.34 | 13.43 | 3254 | DIŞINDA | KALDI |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 470 µF (−%20) + 0,15 Ω (alt kenar) | 117 | sönmüş | 10.25 | 11.65 | 1 | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 470 µF (−%20) + 0,22 Ω (SEÇİLEN) | 135 | sönmüş | 10.26 | 11.65 | 1 | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 470 µF (−%20) + 0,35 Ω (Rd + Cd ESR) | 160 | sönmüş | 10.24 | 11.66 | 1 | içinde | GEÇTİ |
| en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ | 470 µF (−%20) + 0,60 Ω (soğuk Cd ESR) | 171 | sönmüş | 10.21 | 11.69 | 1 | içinde | GEÇTİ |

**Karar (kullanıcı onayı, 12.11.2026):** çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω`** sönüm dalı eklendi. Yukarıdaki dört model seti ve dört ayrık toplam dal direnci (0,15 / 0,22 / 0,35 / 0,60 Ω) için tabloda yuvarlanmış `Pkritik` 114–195 W ve SİM çıkışı 10,21–11,69 V'tur (sönmüş). Önceki HESAP seçenekleri tablosundaki farklı direnç ve ESR kombinasyonları için sonuçlar ayrıca verilmiştir. Bu örnekler aralıktaki tüm kombinasyonları kanıtlamaz; Cd ESR'si sıcaklık ve frekansta ayrıca doğrulanmalıdır. Sürekli `Rd` kaybı yaklaşık **1,3 mW**'tır (76 mA RMS, anma senaryosu).

## 11. Doğrulanamayanlar ve sonraki aşamalara devredilen şartlar

**Fiziksel ölçüm gerektirenler (hiçbiri yapılmadı — ÖLÇÜM YOK):**

| Parça | Ölçülecek | Neden |
|---|---|---|
| L1 | 22 sarımdan sonra L0 (100 kHz); L(I) 0 / 5 / 8,9 / 10,6 / 12 A (8,9 A'de ≥ %90); 4 telli DCR 20 °C ve sıcak; 7,5 A DC + ripple ile sargı ve çekirdek sıcaklığı (≥ 50 °C ortam); 10–12 A darbe | Sönüm (L, DCR), doyma, ısı |
| Cout | Birkaç numunede kapasite, ESR ve \|Z\| 0,9 kHz ve 100 kHz'te; 20 °C, sıcak (≈ 60–85 °C), mümkünse −10 °C | CPL sönümü (alt ESR), ripple ve yük atma sıçraması (üst ESR) |
| Cin | Kapasite, ESR, ESL; gerçek ripple akımı ve kasa sıcaklığı | Ripple akımı payı, hücre barası |
| Kaynak | 6S paket iç direnci, kablo R ve L; takma anında V(Cin) tepe | Cin gerilim sınıfı |
| S1, D1 | Kasa sıcaklıkları; VDS ve D1 ters gerilim tepe (kısa toprak yayıyla), zil frekansı | Isı, 60 V sınıfı, sönümleyici değeri |

**Adım 4–7'ye ölçülebilir arayüz şartı olarak devredilenler (şimdi devre eklenmedi):**

- **Sürücü (Adım 4):** 100 kHz'te üst taraf N-MOSFET; kapı yükü 30 nC; toplam kapı direnci 5–25 Ω aralığında anahtarlama kaybı 0,4–1,4 W; yüksüz / DCM'de bootstrap yenilemesi sağlanmalı (anahtar düğümü kendiliğinden toprağa inmez).
- **PWM ve yumuşak kalkış (Adım 5):** kalkışta bobin tepe akımı ≤ 12 A (L/L0 ≥ %95), çıkış ≤ 12 V; sert kalkış 61,5 A / 16,6 V'tur (12,6 W'ta 63,1 A / 18,1 V) ve bobin bu akımda ≈ %53'e düşer. 5 ms'lik duty rampası anmada 11,8 A / 11,34 V, en düşük Z0 köşesinde 12,8 A verir (Adım 5'te ≥ 6 ms rampa veya akım sınırlamalı kalkış kullanılmalı).
- **Geri besleme (Adım 6):** 20–26 V ve 0–7,5 A'de 11 V; Ton 2,1–5,6 µs; DCM/CCM geçişi ≈ 0,94 A; ana LC f0 ≈ 0,88 kHz, Cd–Rd köşesi ≈ 1,54 kHz, ESR sıfırı ≥ 4,5 kHz (3. derece çıkış filtresi kompanzasyonda dikkate alınmalı); yük sabit güç karakterli (82,5 W'ta artımsal direnç −1,47 Ω); açık çevrim köşe sönümü `Cd + Rd` dalıyla sağlanmıştır, kapalı çevrim faz/kazanç payı Adım 6'da gösterilmeli; 0 A'de çıkışın girişe tırmanması önlenmeli.
- **Yük atma bütçesi (Adım 6–7):** ideal sınır 11,25 V (82,5 → 0 W); her PWM periyodu gecikme ≈ +0,06–0,07 V; soğuk ESR üst sınırıyla (120 mΩ || 0,22 Ω) 3 periyot gecikmede 11,76 V (§7.3).
- **Korumalar (Adım 7):** 7,5 A üstü talepte akım sınırlama; S1 kısa devresinde sınanan senaryolarda çıkış 24–31,1 V (Cout/Cd ≥ 35 V hedefinin gerçek arızalarda yeterliliği doğrulanmadı; **O1 portu için bağımsız aşırı gerilim koruması zorunludur**); giriş düşük gerilim; sıcak takmada örneklenen ani akım (180–1200 A; Cin ≥ 50 V hedefinin gerçek kaynak ve payla yeterliliği doğrulanmadı, kontak/akım sınırlaması Adım 7'de); ters polarite.
- **Açık çevrimin bilinen sınırları (güç katı hatası değildir, ama PASS de sayılmaz):** giriş değişiminde çıkış oransal kayar (§5.7), hafif yükte ve yüksüz çıkış yükselir (§5.3, §5.4), sert kalkış aşımı (§5.6).

**Doğrulanmamış veriler:**
- O1'in gerçek tüketimi, kalkış akımı, mutlak maksimum gerilimi ve ripple toleransı yayımlanmamış; 4 / 10 W değerleri tahmindir.
- O1 giriş koruması (eFuse OVLO ≈ 14,7 V, TVS, TPS62180) v0.2 şemasının metin katmanından çıkarıldı; devre bağlantıları görülerek doğrulanmadı. 12 V üstü için dayanım varsayılmamalıdır.
- S2E kalkış darbesinin süresi ve 11 V'taki değeri (datasheet 12 V verir).
- [STP100N6F7 TO-220 veri sayfası](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf), DocID027212 Rev 2, Tablo 3 Rth(j-amb) = 62,5 °C/W verir; kılıf boyutları belgede bulunur ancak bir kütüphane ayak iziyle karşılaştırılmadı. ST'nin SPICE modeli kullanılmadı; §9.3 modeli veri sayfasından türetilmiştir.
- Seramik kondansatörün DC bias eğrisi, soğutucu ve yalıtım pedi ısıl dirençleri: parça seçilmedi.
- Soğuk köşe: −10 °C'ta Zmax'ın tamamı ESR sayılırsa (Cout 120 mΩ, Cin 38 mΩ) 26 V / L −%30 / Cout −%20 köşesinde ripple 165 mV ölçütünü **aşar** (11.11.2026 koşusu: 318 mV); kabul ölçütü değiştirilmedi, gerçek ESR ölçülmelidir.

**İdeal modelin kapsamadıkları:** anahtarlama geçişleri, diyot kapasitesi, bobin doyumu ve çekirdek kaybı, kondansatör ESL'i ve kapasitenin gerilim/sıcaklıkla değişimi, parazitik zil, ısıl davranış, EMI. Bunlar §9'da hesap veya ayrı senaryo olarak ele alınmıştır; hiçbiri ölçülmemiştir.

## 12. Dondurma kapısı (12 Kasım 2026)

12.11.2026'da açık çevrim değerleri simülasyon düzeyinde donduruldu. **13.11.2026 güncel iş sırası:** önce kontrol/sürücü/koruma mimarisinin gereksinimleri, sonra kontrolcü ile güç katı adaylarının birlikte değerlendirilmesi ve kullanıcıyla kesin seçim; ardından gerçek değerlerle güç katı ve kapalı çevrim doğrulaması, tezgâh ve PCB. Açık çevrim dondurması kapalı çevrim performansını veya fiziksel güvenliği kanıtlamaz. [YOL-HARITASI.md](../YOL-HARITASI.md) güncel iş sırasıdır.

Bu yüzden kapı iki basamaklıdır. **Simülasyon dondurması** değerleri ve parçaların tutması gereken ölçülebilir hedef aralıkları sabitler; bobin ve parçalar buna göre yapılır / seçilir. **Parça sonrası doğrulama** ayrı bir basamaktır ve simülasyon dondurmasını engellemez.

### 12.1 Simülasyon dondurması

| # | Kapı | Durum | Kanıt / eksik |
|---|---|---|---|
| 1 | Başlangıç sürümü, test ortamı, yerel değişikliklerin korunması | ✅ | LTspice 26.1.1; `main` |
| 2 | Ölçüm altyapısı güvenilir; 20 ms sahte geçiş kapandı | ✅ | §5.0, §6.1 |
| 3 | Tam 3. derece CPL sınırı ile uzun SİM birbirini açıklıyor | ✅ | §6.1, §6.2 |
| 4 | Anma değerlerinde 0–82,5 W zarfından seçilen CR / CC / CP senaryoları sönümlü | ✅ örnek senaryolar | §6.2, §7; tüm yük profilleri ve ara noktalar sınanmadı |
| 5 | Örneklenen tolerans model setlerinde sabit güç yükü sönümü | ✅ örneklenen senaryolar | `pencere` 3/3; `kararlilik` 200 ms için 27/27 satır ve ayrı bir 500 ms senaryosu (§6.1–6.2). Tüm sürekli parametre kombinasyonları sınanmadı. |
| 6 | Parçalar için hedef aralıklar yazılı; örnek model setleri simülasyonda sınanmış | ✅ örnek senaryolar | §1, §10 ve [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md): L1 33 µH (±%8 el sarım / ±%20 satın alma), DCR 6,5–15 mΩ, Cout 1000 µF ±%20 / ESR ≤ 35 mΩ, Cd 470 µF ±%20, Rd_toplam 0,15–0,60 Ω. Sürekli aralıkların tüm kombinasyonları sınanmadı. |
| 7 | Kayıp ve ısıl bütçe; soğutucu, seramik dekuplaj ve sönümleyici için hedef değerler | ✅ hedef değer (HESAP) | §9.1, §9.2, §9.5; parça numarası §12.2'de seçilir |
| 8 | Gerilim sınıfları: Cout/Cd (S1 kısa devresi) ve Cin (sıcak takma) | ✅ | Kullanıcı kararı (12.11.2026): **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** (§1, §9.4) |
| 9 | Genel modül sınırları (gerilim toleransı, ripple, geçici durum) | ✅ | Kullanıcı kararı (12.11.2026): ayrı sınır tanımlanmadı; O1/S2E uyumluluk ölçütleriyle (9–12 V, ≤ 165 mV, 200 ms sönüm) dondurulur (§2.1) |
| 10 | Sürücü / yumuşak kalkış / geri besleme / korumaya devredilen şartlar yazılı | ✅ | §11 |
| 11 | Kod / şematik / belgeler aynı değerleri taşıyor; belirlenen test kipleri koşuldu | ✅ tarihli kayıt | `sematik_uret.py`, `hesap.py`, `dogrula.py` senkron; §13'te listelenen 8 koşu çıkış kodu 0 ile tamamlandı. Elektriksel kararlar ilgili tablolardadır; diğer senaryolar bu kayda dahil değildir. |
| 12 | Kullanıcının dondurma onayı | ✅ | Kullanıcı onayı alındı (12.11.2026) |

**Karar: FROZEN (açık çevrim simülasyon dondurması, 12 Kasım 2026).** §12.1 tarihli karar kaydıdır. Kontrolcüyle uyum, kapalı çevrim ve gerçek parça değerleri bu kararın kapsamı dışındadır; güncel iş sırası yol haritasındadır.

### 12.2 Parça ve kontrol sonrası doğrulama

| İş | Ne zaman |
|---|---|
| Güç katı elemanları ve kontrolcü; soğutucu, seramik kondansatör, RC sönümleyici parçaları | Kontrol mimarisi ve güç katı uyumu değerlendirildikten sonra kullanıcıyla seçilir; gerilim ve ısıl paylar ayrıca doğrulanır |
| L1: L0, L(I), DCR, sıcaklık — hedef aralığın içinde mi | Bobin sarılınca |
| Cout / Cd / Cin: kapasite, ESR / empedans (0,9 kHz ve 100 kHz, sıcak / soğuk) ve Rd + Cd_ESR toplamı (0,15–0,60 Ω) — hedef aralığın içinde mi | Parçalar gelince |
| Kaynak iç direnci, kablo R ve L | Batarya ve kablo belli olunca |
| Gerçek parça değerleri üç dosyaya yazılır, `secilen`, `pencere`, `kararlilik`, `zarf` yeniden koşulur | Ölçümlerden sonra |
| Kapalı çevrim kararlılığı, yük/giriş değişimi, hafif yük, kalkış ve koruma senaryoları | Kontrol tasarımı ve kullanılan parça modelleriyle; daha sonra tezgâhta da doğrulanır |
| STP100N6F7 TO-220 ayak izinin veri sayfasıyla karşılaştırılması, üretici SPICE modellerinin değerlendirilmesi | Parça kesinleşince |
| Zil, sıcaklık ve verim ölçümleri | Tezgâh prototipi (Adım 8) |

Bu basamaktaki hiçbir iş yapılmadı ve hiçbiri "doğrulandı" sayılmaz; yalnız sıraları dondurmadan sonradır.

## 13. Tekrar üretme

```
python buck/hesap.py                # analitik özet; §6, §9, §10 (anlık)
python buck/dogrula.py sayisal      # §5.0 (≈ 3 dk)
python buck/dogrula.py secilen      # §5.1–§5.9 (≈ 20 dk)
python buck/dogrula.py pencere      # §4.4 son pencere (≈ 10 dk)
python buck/dogrula.py kararlilik   # §6, §10 (≈ 25 dk)
python buck/dogrula.py zarf         # §7 (≈ 10 dk)
python buck/dogrula.py stres        # §9.3, §9.4 (≈ 2 dk)
python buck/dogrula.py tarama       # §4.1 eski dalsız model; güncel altyapıyla tekrar koşuldu
python buck/dogrula.py mevcut       # en baştaki eski değerlerle aynı testler
python buck/dogrula.py grafik       # buck/grafik/*.svg
```

12 Kasım 2026'da `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalı eklendikten sonra `sematik_uret.py`, `hesap.py`, `sayisal`, `secilen`, `pencere`, `kararlilik`, `zarf`, `stres` ve `grafik` sırayla yeniden koşuldu; hepsi çıkış kodu 0 ile bitti. §4.1–§4.3 ve §4.4'ün ilk tablosu 11 Kasım 2026 dalsız seçim gerekçesi kayıtlarıdır; `tarama` 13 Kasım'da güncel altyapıyla da koşulmuş, farklı sonuçlar §4.1'de belirtilmiştir.

**Kanıtın sınırı (13.11.2026 kod incelemesi):** Çıkış kodu 0 tek başına elektriksel geçme kararı değildir; tabloların karar ve ölçüm sütunları ayrıca incelenmelidir. Önceki kod, LC sönümünü değerlendirmek için kısa kalan darbeye de GEÇTİ yazabiliyordu; bu satırlar sönüm açısından **belirsizdir**. 200 ms ve 500 ms sonuçları bu kısa-darbe sınıflandırmasına dayanmaz. Yeni kod eksik veya sonlu olmayan `.meas` sonuçlarını reddeder ve aynı adlı eski çıktıları koşudan önce siler. Yukarıdaki tablolar tarihli önceki koşuların kaydıdır; yeniden koşulan kipler aşağıda ayrıca belirtilir.

**13.11.2026 tekrar doğrulaması:** `sayisal`, `secilen` ve `pencere` güncel kodla yeniden koşuldu. `secilen` 53/53 ve `pencere` 4/4 tablo satırı (başlıklar dahil) bu belgedeki satırlarla birebir eşleşti. `pencere` üç satırda GEÇTİ; `secilen` hafif yüke sabit-duty geçişte 16,07 V ve sert kalkışta 16 V üstü sonuçları da yeniden üretti. Batarya/kablo modelinde 11 V'tan sapma için üç uyarı verildi; §5.9 sonuçlarıdır. Ayrı testlerde eski/eksik/geçersiz ölçümler ve kısa darbe sınıflandırması kontrol edildi; seri RLC sıcak takma hesabı üç örnekte sayısal entegrasyonla, CPL özdeğerleri 54 örnekte bağımsız matris çözümüyle karşılaştırıldı. Bu kontroller fiziksel ölçüm değildir.

`kararlilik` güncel karar koduyla tam olarak yeniden koşuldu: 1 / 5 / 20 / 50 ms sınır içi örnekler BELİRSİZ, 200 ms için 27/27 model-yük satırı ve ayrı 500 ms örneği GEÇTİ; dört eski dalsız karşılaştırma KALDI. Yeni karar fonksiyonu ayrıca sınır, büyüme ve ihlal örnekleriyle sınandı. Bu sonuçlar yalnız listelenen model ve yük senaryolarını kapsar.

`zarf` ve `stres` yeniden koşuldu: tablo satırları sırasıyla 52/52 ve 28/28 bu belgedeki satırlarla eşleşti (başlıklar dahil). Genel modül sınırları onaylanmadığından genel geçme kararı yoktur. Stres testinde varsayılan temel parazitik modelde D1 ters gerilimi 63,1 V ve bazı diğer senaryolarda daha yüksektir; bunlar gerçek ölçüm değildir ve parça/yerleşim doğrulamasına devredilir. Yük atma çıktısının metni, sınanan Cd–Rd kolunun da ilk sıçramaya katıldığını belirtmek üzere koşudan sonra düzeltildi; ölçüm hesabı değişmedi.

`tarama` ve `mevcut` da güncel altyapıyla yeniden koşuldu; bunlar eski, sönüm dalsız devrelerdir. `tarama`daki tarihî kayıtlarla farklılıklar §4.1'de belirtilmiştir. `mevcut` 33 µH / 330 µF modelinde 57,6 → 73 W, 200 ms adımda 8,97–13,46 V ve sürekli salınım verdi; 73 W kararlı durum ölçümünde ayrıca 2,8 mV/ms kayma uyarısı oluştu. Batarya/kablo modeli üç gerilim sapması uyarısı verdi. Bu sonuçlar güncel devreye ait değildir.

`grafik` yeniden koşuldu ve üç SVG dosyasında değişiklik oluşmadı. Şematik üreticisi geçici kopyada çalıştırıldığında `.asc` ve şematik `.svg` depodaki dosyalarla bayt düzeyinde eşleşti. Ana `.asc` ayrı bir geçici kopyada LTspice ile çalıştırıldı: 19–20 ms aralığında zamana göre ortalama **10,99987 V**, ripple **55,722 mV t-t** (SİM). Bu ana şematik koşusu sert anahtar modelini kullanır; fiziksel ölçüm değildir.

LTspice yolu farklıysa `LTSPICE` ortam değişkeniyle verilir. Test netlistleri geçici klasörde üretilir; ana şematiğe `.meas`, `.param`, yük modeli veya parça modeli eklenmez. §4.2, §4.3 ve §4.4'ün ilk tablosu tek seferlik koşulardır.

### 13.11.2026 tam tekrar koşusu ve kontrol çalışması

Kullanıcı isteğiyle bütün depo test kipleri `main` dalındaki dondurulmuş güç katı üzerinde yeniden ve **seri** çalıştırıldı: `hesap`, `sayisal`, `secilen`, `pencere`, `tarama`, `mevcut`, `kararlilik`, `zarf`, `stres`, `grafik`. Her komut LTspice/Python süreç çıkışı 0 ile bitti; bu yalnız koşunun tamamlandığı anlamına gelir. Geçen/kalan/uyarı sonuçları ilgili bölümlerde tutulur. Başlangıç/bitiş aralığı 13.11.2026 21:50–23:08 (Türkiye saati); tam konsol kaydı `%TEMP%\pdu-full-rerun-20261113.txt` altındadır. `grafik` SVG'leri depodaki dosyalarla aynı olduğundan çalışma ağacında değişmedi. Ana `.asc`, şematik değerleri ve açık çevrim FROZEN kararı değiştirilmedi.

**Kapalı çevrim ve OVP geçici tekrarları:** Dosyaların tamamı `%TEMP%\pdu-control-study-20261113` içindedir; depoya alınmadı. LT3844 üretici modeli 24,6→20→26 V giriş değişiminde 100/50 ns adımlarla 10,9550–11,0436 V aralığında ve yaklaşık 8,70 A bobin tepesinde sonuç verdi. 200 ms 41,25→82,5→41,25 W CPL testinde 10,8385–11,1519 V ve 9,889 A tepe; 100 ns tekrarı neredeyse aynıydı. 20 / 24,6 / 26 V tam yükte ortalama yaklaşık 10,994–10,996 V, ripple 42,5 / 52,5 / 55,0 mV'tur. Bu düzen 10 mΩ algılama direnci kullanır, yaklaşık 106 kHz'te çalışır ve çoğu güç elemanı idealdir; ana devrenin aynısı veya gerçek cihaz sonucu değildir.

LT3844'ün yüksüz ve 0,24 A testleri, veri sayfasından türetilmiş **yaklaşık** VDMOS modeliyle 100/50 ns'te tekrarlandı. 0,24 A'de ortalama yaklaşık 11,0015 V ve ripple 30,5 mV; 1 GΩ yüksüz örnekte yaklaşık 11,0027 V ve 7,9 mV'tur. 27 °C ideal kaynak/çevre ve model varsayımları, gerçek ST MOSFET'i, +5…+50 °C ve tam toleransları temsil etmez. Tam yük açılış modelinde LT3844'ün CSS çalışırken bobin akım tepesi yaklaşık 10,05 A ve çıkışın ilk tepe değeri 11,23 V civarı görüldü; bu, gerçek soft-start devresinin tolerans ve akım limiti doğrulaması değildir.

PI modeli için giriş değişiminde Kp=0,01/0,03/0,05 ve Ki=0,00003/0,0001/0,0003 ile dokuz ayrı ayar koşuldu. **Dokuzunun hepsi 11 V ±%5 anlık bandını ihlal etti**; en iyi taranan ayarda 9,8489–12,4676 V ve 17,31 A bobin tepesi görüldü. 100/50 ns giriş dalgası değerleri ve bağımsız `.raw` okuması tutarlıydı. Bu yalnız seçilen davranışsal PI örneğini eler; bütün gerilim-kipli analog kontrolcüleri veya iyi tasarlanmış kompanzasyonu elemez.

OVP tekrarında üretici LTC4365 modeliyle sert kaynak geçişi 11→25 V, cihaz portu 10/100/1000 µF ve iki geçiş süresinde sınandı. 100 µF/10 µs'te port tepe gerilimi 12,806 V; aynı testin `LTC4365-1` örneğinde 13,060 V'tur. Her iki sonuç 50 ns adımında 0,002 V içinde tekrarlandı ve **12 V üst sınırını geçemedi**. Bununla birlikte LTC4365 + ideal seri kesici ve LT3844'ün birleşik S1-kısa devre senaryosunda 100 µF varsayımında 11,797 V, 1000 µF varsayımında 11,668 V elde edildi. Kaynak arızası/rampa, port kapasitesi, MOSFET dinamiği ve model değişince sonuç değiştiğinden yalnız birleşik kısa devre köşesi koruma yeterliliği değildir.

TI LM5088 makromodeli nominal ve Gear/UIC koşularında çıkış kodu 1 ile başarısız oldu. Üçüncü probe koşusu logda aynı simülasyon zamanında sonsuza doğru büyüyen “tolerance relaxed” adımları üretip ham dalga yazmadı; sonuç oluşmadığı için süreç durduruldu. Bu **elektriksel başarısızlık sonucu değildir**. Özet tekrar kaydı `%TEMP%\pdu-closed-loop-rerun-20261113.txt` içindedir; bu çevrimdeki tamamlanmamış/kesilmiş denemeler raporda açık bırakılmıştır.

**Karar özeti:** Şimdilik en iyi kontrol yönü, donmuş asenkron S1/D1 güç katısını koruyan sabit frekanslı analog tepe akım kipidir; 11 V çıkış gerilimi döngüsü Cout'tan ölçer, bobin akım sınırı ayrı işlevdir. Üretici LT3844 testi bu yöntem için destekleyici ama parçayı seçtirmeyen kanıttır: 10 mΩ örneğinin 9 A düşük eşik ucu, 9,89 A geçici tepeye pay bırakmaz. LM5088-2 kâğıt üstünde uyumlu alternatif, SİM'de sonuçsuzdur. OVP için ortak porttan algılayan ayrı latch-off MOSFET ayırıcı yöntemi araştırılmalı; LTC4365 örneği 12 V sınırını geçemedi, MAX6497 ailesi ise test edilmedi. Maliyet, gerçek verim, akım eşiği ve OVP port tepe gerilimi çözülmeden parça veya devre değeri kesinleşmez. Kullanıcının sonraki kararı beklenmeden devreye aktarım yapılmaz.

### 14. 14.11.2026 tam tekrar ve geçici analog kontrol ağı taraması

Bu bölüm, 14.11.2026 tarihinde `main` dalındaki güç katı dondurması korunarak yapılan tekrarları ve yeni **geçici** kapalı çevrim çalışmalarını kaydeder. Geçici netlist, log ve tablolar `%TEMP%\pdu-control-opt-20261114` içindedir; depodaki `.asc`, `hesap.py`, `dogrula.py`, parça sırası ve açık çevrim değerleri değiştirilmedi. LTspice sürümü 26.1.1'dir. Bu kayıt **fiziksel ölçüm veya parça seçimi değildir**.

#### 14.1 Depo testlerinin 14 Kasım tekrarı

`hesap`, `sayisal`, `secilen`, `pencere`, `tarama`, `mevcut`, `kararlilik`, `zarf`, `stres` ve `grafik` kipleri seri olarak yeniden koşuldu; on komutun tamamı süreç çıkış kodu 0 ile bitti. Özet `%TEMP%\pdu-full-rerun-20261114-summary.csv`, kip çıktıları `%TEMP%\pdu-rerun-20261114-<kip>.txt` dosyalarındadır. Bu, bütün elektriksel senaryoların GEÇTİ anlamına gelmez: `secilen` içindeki sabit duty hafif-yük geçişi yaklaşık 16,07 V'a yükseldi; sert kalkış, bazı stresler ve eski dalsız modellerde sınır dışı sonuçlar vardır. `kararlilik`te yalnız tabloda ayrı ayrı listelenen 200 ms / 500 ms senaryoları geçer; kısa darbeler sönüm için belirsizdir. `zarf` genel modül kabul sınırı olarak onaylanmadığı için genel modül PASS kararı değildir. Güncel kodun ölçüm tabloları bu bölümün önceki tarihli satırlarında yer alır. **Çıkış kodu 0, elektriksel geçme kararı değildir.**

#### 14.2 Kompanzasyon araması — geçici test aralığı

Kontrolcü parçası seçilmeden önce, ADI LT3844 üretici makromodeli yalnız analog tepe akım mimarisini ve hata yükselteci ağını incelemek için kullanıldı. Frekans ayarı modelde yaklaşık 100 kHz'e kalibre edildi; açık çevrim güç katına akım algılama direnci eklendi. Diğer elemanlar ideal/parametrik kaldı; indüktör doyumu, anahtarlama kaybı, fiziksel MOSFET, parça sıcaklık eğrileri ve PCB parazitleri yoktur.

İlk kaba tarama zayıf-sönüm 20 V köşesinde 45 Rcomp/Ccomp/Cpole birleşimini, ardından sınırın devam edip etmediğini görmek için 24 genişletilmiş birleşimi koştu. Kaba FRA örneklemesi 500 Hz–50 kHz, oktav başına bir nokta, 0,5 mV enjeksiyon ve ortak kaydedilmiş çalışma noktası kullandı; bu nedenle yalnız eleme taramasıdır, her hücre için son doğrulama değildir. En iyi satırlar:

| Geçici ağ (Rcomp / Ccomp / Cpole) | 500 Hz–50 kHz kaba SİM, zayıf 20 V: crossover | Faz payı | Yorum |
|---|---:|---:|---|
| 49,9 kΩ / 1,5 nF / 47 pF | 4,167 kHz | 61,2° | İlk 45'li taramanın en iyisi; sonraki genişletmede aşıldı |
| 68 kΩ / 2,2 nF / 22 pF | 5,254 kHz | 75,0° | Genişletilmiş tarama |
| 100 kΩ / 3,3 nF / 22 pF | 7,746 kHz | 76,0° | Daha yüksek bant genişliği; ilk hassas köşe taramasına finalist seçildi |
| 49,9 kΩ / 3,3 nF / 22 pF | 3,856 kHz | 78,7° | Daha düşük crossover; 68 kΩ ağı tarafından hem marj hem bant bakımından kaba gridde geçildi |
| 68 kΩ / 3,3 nF / 22 pF | 5,328 kHz | 78,9° | Genişletilmiş taramanın en yüksek faz paylı/orta bantlı ağı; ikinci hassas finalist |

Genişletilmiş gridin sınırlarında Rcomp/Ccomp artırıldığında hem crossover hem faz payı değişmeye devam etti; bu nedenle tarama matematiksel/global optimum kanıtı değildir. ADI tasarım rehberi 45° üstünü genel alt hedef, 60°'yi iyi sonuç; döngü bant genişliği için anahtarlama frekansının yaklaşık 1/10–1/5 aralığını pratik üst sınır olarak verir. Bu tavsiye, burada ölçülen makro-model faz payını üretici garantisine dönüştürmez.

#### 14.3 Hassas FRA finalistleri ve ölçüm kararlılığı

İki genişletilmiş finalist her köşede kendi LT3844 çalışma noktası oluşturularak 500 Hz–20 kHz, oktav başına dört nokta, 100 ns azami adım, 10 ms bekleme ve 0,5 mV enjeksiyon ile ölçüldü. Aday D için zayıf köşede 0,25 mV tekrar da koşuldu.

| Geçici ağ | Köşe / uyarım | Crossover | LTspice FRA faz payı | Kazanç payı |
|---|---|---:|---:|---|
| D: 68 kΩ / 3,3 nF / 22 pF | Zayıf 20 V / 0,5 mV | 5,116 kHz | 80,9° | 500 Hz–20 kHz içinde −180° kesişimi yok |
| D | Zayıf 20 V / 0,25 mV | 4,761 kHz | 90,5° | Aynı |
| D | Sıcak-kayıplı 20 V | 5,781 kHz | 113,1° | Aynı |
| D | Nominal 26 V | 5,796 kHz | 109,3° | Aynı |
| F: 100 kΩ / 3,3 nF / 22 pF | Zayıf 20 V | 7,609 kHz | 76,0° | 500 Hz–20 kHz içinde −180° kesişimi yok |
| F | Sıcak-kayıplı 20 V | 8,717 kHz | 103,5° | Aynı |
| F | Nominal 26 V | 12,647 kHz | 98,3° | Aynı |

`FRA` ham verisi bağımsız olarak okundu: örneklenen kesişim frekansları LTspice özet satırlarıyla eşleşti. Bununla birlikte D ağında 0,5 mV ve 0,25 mV uyarım crossover'ı yaklaşık %7, faz payını 9,6° değiştirdi. Daha küçük 0,1 mV / 20 ms bekleme denemesinde hem D hem F için ham büyüklük/faz noktaları gürültülüydü ve LTspice 0 dB kesişimi bulmadı; bu devre kararsızlığı değil, bu uyarımda geçerli FRA ölçümü alınamamasıdır. Bu yüzden FRA sayıları bir ölçüm genliği bağımsızlığı göstermiyor; kazanç payı pozitif/sonlu bir değer olarak saptanmadı. **Adım 6 tamamlanmış/kararlılık kesin kanıtlanmış sayılamaz.** ADI, birden fazla gain/phase kesişimine veya anahtarlama frekansının yarısında yükselen ikinci kazanç tepesine dikkat edilmesini önerir; buradaki 23 frekanslı tarama bunların tümünü dışlamaz. Referanslar: [LT3844 veri sayfası](https://www.analog.com/media/en/technical-documentation/data-sheets/3844fc.pdf), [ADI loop-stability tasarım hedefleri](https://www.analog.com/en/resources/technical-articles/power-supply-loop-stability-compensation-part-3.html).

#### 14.4 D ve F ağlarının zaman alanı kıyası

Her iki finalist aynı LT3844 makromodeli ve aynı dondurulmuş filtre değerleriyle (zayıf 20 V köşesi: L=39,6 µH, Cout=800 µF/15 mΩ; nominal 26 V köşesi: L=33 µH, Cout=1000 µF/35 mΩ) koşuldu. 200 ms CPL basamağı 41,25→82,5→41,25 W idi; 20↔26 V çizgi basamağı zayıf parazitik modelde uygulandı. Hafif yük 0,24 A eşdeğer direnç, yüksüz model 1 GΩ'dur.

| Ağ | Senaryo | Vout min–max | Son 1 ms ripple | Bobin tepe | Model ölçütü |
|---|---|---:|---:|---:|---|
| D | 20 V, 200 ms CPL | 10,8895–11,0032 V | 18,1 mV t-t | 8,43 A | 9–12 V / 165 mV içinde |
| D | 26 V, 200 ms CPL | 10,8766–11,0254 V | 60,6 mV t-t | 8,78 A | İçinde |
| D | 20↔26 V, CPL | 10,8895–11,0325 V | 18,1 mV t-t | 8,85 A | İçinde |
| F | 20 V, 200 ms CPL | 10,9120–11,0032 V | 18,1 mV t-t | 8,30 A | İçinde |
| F | 26 V, 200 ms CPL | 10,8921–11,0254 V | 60,6 mV t-t | 8,66 A | İçinde |
| F | 20↔26 V, CPL | 10,9118–11,0265 V | 18,1 mV t-t | 8,79 A | İçinde |

İki ağın da bu **listelenmiş model** 200 ms dalgalarında zarf gerilimi aralık içinde kaldı; adım sonrası zarf ölçümündeki son pencere girişin tekrar 20 V'a dönmesini içerdiği için tekdüze sönüm ölçüsü değildir. İki ağ arasındaki min/max farkı yaklaşık 15–23 mV; aday F zayıf ve çizgi basamağı köşesinde biraz daha yüksek minimum verdi. Bu küçük fark, gerçek yük veya tüm toleranslar için performans sıralaması değildir.

| Ağ | 20 V hafif yük (0,24 A) | 26 V hafif yük (0,24 A) | 26 V yüksüz (1 GΩ) |
|---|---:|---:|---:|
| D | 10,9965–11,0083 V; 11,8 mV ripple | 10,9936–11,0238 V; 30,2 mV | 10,9897–11,0431 V; 5,9 mV |
| F | 10,9965–11,0083 V; 11,8 mV ripple | 10,9937–11,0239 V; 30,2 mV | 10,9898–11,0323 V; 5,9 mV |

Tam rezistif 7,5 A yükle kalkışta 20 V köşesinde her iki ağ da yaklaşık 9,08 A bobin tepesini, 11,02 V çıkış tepesini verdi; 26 V köşesinde tepe yaklaşık 9,67 A ve 11,04 V'tur. F ağında 90 mV akım algılama eşiğini temsilen LT3844'ün tipik 100 mV eşiği altında Rsense=10,9529 mΩ kullanıldığında 26 V kalkış tepe akımı 9,20 A, çıkış tepesi 11,125 V oldu. Bu eşdeğer direnç fiziksel sense toleransını, yol direncini de artırarak taklit eder; üretim toleransı modelinin tam karşılığı değildir. Makro-model yumuşak kalkışının bu koşuları çıkışın 12 V üstüne çıkmadığını gösterir, gerçek pin toleransları/akım sınırı doğrulaması değildir.

F ağı 20 V / tam yük CPL testinde `.temp 5` ve `.temp 50` ile de koşuldu: ikisinde yaklaşık 10,9119–11,0032 V ve 8,298 A elde edildi. 27 °C model sonucundan fark <0,1 mV civarındadır; bu makromodelde sıcaklık tepkisinin çok az olduğuna işaret eder, pasiflerin DCR/ESR, L(I), kondansatör kapasitesi, MOSFET ve fiziksel termal koşulların +5…+50 °C doğrulaması değildir.

#### 14.5 Sense direnci ve dondurulmuş güç katıyla arayüz

LT3844 veri sayfası SENSE uçlarını buck uygulamasında bobin yolundaki seri direncin iki yanına bağlar; tipik eşik 100 mV, sınır aralığı bu incelemede 90–115 mV ve önerilen ilk hesap `Rsense = 70 mV / Iout(max)`'tır. 7,5 A için bu denklem **9,33 mΩ HESAP** verir. 9,76 mΩ ±1% örneğinde datasheet eşikleri kullanılarak ilk eşik hesabı **9,13–11,90 A HESAP**tır; bu parça seçimi değildir ve dinamik akım davranışını içermez. Bu eşik genişliği, yaklaşık 12 A bobin doyma hedefiyle az pay bırakır.

9,76 mΩ seri direnç 7,5 A'de yaklaşık **73,2 mV ve 0,549 W HESAP** ekler (±1%: yaklaşık 0,544–0,555 W). Dondurulmuş L1 DCR'si 7,81 mΩ ise bobin ve sense dirençlerinin toplamı yaklaşık 17,57 mΩ olur; bu, yalnız bobin için yazılı 6,5–15 mΩ DCR kriterinin yerine geçmez fakat dondurulmuş açık çevrim çıkış yolunda bulunmayan ilave seri direnç ve yaklaşık 0,55 W kayıptır. Kapalı çevrim testleri bu direnci içerdi; `.asc` / açık çevrim dondurma içermez. Akım algılama yönteminin verim, filtre sönümü, CPL ve akım marjına etkisi için kontrol mimarisi–güç katı arayüzü kararı gerekir; burada dondurulmuş değer değiştirilmedi.

#### 14.6 Önceki sonuç ve açık işler (Type-III gerilim-kipi testinden önce)

**Arama kapsamı ve “optimum” sınırı:** Bu araştırma, ilk 45 ağ ve ardından 24 genişletilmiş ağdan oluşan **69 noktalı kaba taramadır**; sürekli değer uzayının tamamı, tüm toleranslar, tüm çalışma noktaları ve tüm fiziksel parazitler taranmadı. Hassas FRA yalnız iki finalist ve üç makromodel köşesinde yapıldı; ölçüm uyarım genliğine duyarlı kaldı. Bu yüzden matematiksel/global optimum, üretim toleranslarına dayanıklı kompanzasyon veya gerçek devre kararlılığı kanıtı yoktur. Bu 13.11 akım-kipi taramasının sınırları içinde **D, sıradaki geçici akım-kipi model turu için başlangıç ağı olarak önerilmişti**; 14.11 Type-III gerilim-kipi karşılaştırması yeni bölüm §15'tedir.

- **13.11 yöntem yönü:** sabit frekanslı analog tepe akım kipi, Cout'tan gerilim geri beslemesi, ayrı soft-start/akım sınırı ve O1 portunu gözeten bağımsız latch-off OVP ilk mimari adayı olarak önerilmişti. LT3844 yalnız test makromodelidir. 14.11 Type-III gerilim-kipi modeli de geçici aday oldu (§15); mimari/onay hâlâ açık.
- Geçici kompanzasyon ağı D, daha düşük crossover nedeniyle o tarihli çalışma için muhafazakâr başlangıç adayıydı; F daha hızlı yanıt veren karşılaştırma ağıydı. FRA'nın uyarım genliği duyarlılığı ve sonlu gain margin bulunamaması nedeniyle **D veya F kesin seçilmedi**. Bu kayıt, Type-III yöntem testinin yerini almaz.
- LT3844 sense direnci güç yoluna ek seri R/kayıp getirir ve açık çevrim dondurmasında yoktur. Emüle akım algılama gibi alternatiflerin makromodeli/uyumu bu çalışmada doğrulanmadı; bu yöntem veya direnç yerleşimi için parça araştırması yapılmadı.
- Bağımsız OVP hâlâ geçmedi: §13'teki LT4365 sert arıza geçişi portta 12 V üstünü gösterdi. D/F zaman alanı kontrolleri çıkış regülasyonunu test eder; O1'i kısa devre, kontrolcü hatası veya hızlı kaynak arızasında korumaz. Gerçek O1/S2E bağlanmaz, fiziksel prototip/PCB adımı açılmaz.
- Bu 13.11 kaydının sonraki karar önerisi, önce §15'teki Type-III testiyle genişletilmiş, ardından D/F ve ortalama-akım denemeleri de eklenerek §16'da karşılaştırılmıştır. Güncel yöntem özeti §16'dadır.

### 15. Gerilim kipli analog Type-III kontrol modeli (14.11.2026)

Bu test, kullanıcı isteğiyle **aynı dondurulmuş açık çevrim güç katısına** geçici gerilim geri beslemesi ekleyerek yöntem düzeyinde yapıldı. Netlist, log ve ham dalgalar `%TEMP%\pdu-vmode-20261114` altındadır; depodaki `.asc`, `sematik_uret.py`, `hesap.py`, `dogrula.py`, parça değerleri ve aday sırası değişmedi. LTspice 26.1.1 kullanıldı. Gerçek kontrol entegresi, MOSFET sürücüsü, OVP veya fiziksel ölçüm yoktur.

#### 15.1 Geçici model ve sınırları

Güç katı değerleri dondurulmuş örnekle aynıdır: Vin=20–26 V; 100 kHz; Cin=2×1000 µF/15 mΩ; S1 Ron=5,6 mΩ; D1 Vf=0,38 V + 8 mΩ; L1=33 µH/7,81 mΩ; Cout=1000 µF/35 mΩ; Cd=470 µF ve Rd=0,22 Ω. Gerçek parça veya tolerans seçimi anlamına gelmez.

Kontrol, 0–1 V test rampasını 100 kHz'de karşılaştıran sabit frekans PWM, 11 V referansını 6 ms'de yükselten soft-start ve doyumda integratör birikimini durduran davranışsal Type-III kompanzasyonla modellendi. Kompanzasyon iki açık RC durum ağıyla kuruldu:

- `H1(s)=(1+s/(2π·500 Hz))/(1+s/(2π·4,5 kHz))`: 35,3678 kΩ + 1 nF alçak geçiren durum ve ideal aktif ağırlıklı toplam.
- `H2(s)=(1+s/(2π·900 Hz))/(1+s/(2π·20 kHz))`: 7,95775 kΩ + 1 nF alçak geçiren durum ve ideal aktif ağırlıklı toplam.
- Denenen integratör katsayıları `Ki=500` ve `1000 s⁻¹`; bunlar **model değişkenidir, seçilmiş devre değeri değildir**. PWM duty aralığı 0–0,95 olarak sınırlandı.
- Ayrı çevrim-başı akım kesimi için model `I(L1)` değerini doğrudan izleyen **11 A ideal eşik** kullandı. Bu gerçek akım algı devresi, eşik toleransı veya kullanıcı kararı değildir; donanımda akım algısının kayıp ve maliyeti henüz modellenmedi.

#### 15.2 Zaman alanı sonuçları — SİM

| Deneme | Sonuç | Durum ve ölçüm aralığı |
|---|---|---|
| 24,6 V, 7,5 A direnç; Ki=500 | 10,9994 V ortalama; 55,9 mV t-t; başlangıçta 11,028 V maksimum; bobin 11,000 A maksimum, son kararlı pencerede 8,449 A | 8–10 ms ortalama, 9–10 ms ripple; 0–12 ms başlangıç. Başlangıç tepesinde modeldeki 11 A sınırı devreye girdi. |
| 24,6→20→26 V giriş rampası, 7,5 A direnç; Ki=200 | 10,213–11,786 V; 11 V±%5 bandı dışı, 9–12 V bandı içi | Her giriş değişimi 100 µs; 14,9–35,1 ms penceresi. |
| Aynı giriş geçişi; Ki=500 | 10,642–11,424 V; 20 V ve 26 V kararlı pencerelerinde sırasıyla 11,0000 ve 11,0000 V ortalama; ripple 45,0 ve 58,2 mV t-t; bobin tepe 11,000 A | 14,9–35,1 ms geçiş penceresi; son kontrol 100 ns azami adımla tekrarlandı. Ki=500 satırında ideal 11 A kesimi geçiş tepesini sınırladı. |
| Aynı giriş geçişi; Ki=1000 | 10,811–11,233 V; bobin tepe 10,488 A | 200 ns azami adım. Listelenen bu giriş/yük koşulunda 11 A ideal kesimi devreye girmedi. |
| 200 ms sabit-güç basamağı; Ki=500 | 10,830–11,057 V; 200 ms darbenin son 1 ms'sinde 58,0 mV t-t; bobin tepe 9,397 A | 24,6 V; 41,25 W'tan 82,5 W'a 20 µs rampalı geçiş, 200 ms tutma ve 20 µs dönüş rampası; geçiş dâhil 39,9–240,02 ms ölçümü. İlk 1 ms'deki toplam tepe-tepe hareketi 227 mV'dur; bu yük geçişini de içerir, kararlı ripple değildir. |
| Aynı CPL basamağı; Ki=1000 | 10,849–11,039 V; son 1 ms ripple 58,0 mV t-t; bobin tepe 9,064 A | Aynı giriş, yük rampası ve 100 ns adım. İlk 1 ms toplam tepe-tepe hareketi 191 mV'dur. |
| 0,24 A; Ki=500 | 10,9994 V ortalama; 29,7 mV t-t; kararlı min–maks 10,991–11,022 V | 35–39 ms ortalaması, 38–39 ms ripple. |
| Yüksüz, 1 GΩ; Ki=500 | 11,3967 V ortalama; 0 mV simüle ripple; başlangıç maksimumu 11,404 V | 35–39 ms penceresi. 11,55 V geçici üst hedefe yalnızca yaklaşık 0,15 V pay kalır; modelde yük yokken dönüştürücü çıkıştan enerji çekemez. |

#### 15.3 Soft-start ve model ayarlarının etkisi — SİM

Tam yükte soft-start süresi artırıldığında başlangıç tepe akımı azaldı, fakat çıkışın 9 V'a ulaşması gecikti. Aynı anda ölçülen 11 A model sınırı yalnız 6 ms satırında devreye girdi:

| Referans rampası | Bobin başlangıç tepe akımı | Çıkışın 9 V'a erişme zamanı | 30–35 ms ortalama çıkış |
|---:|---:|---:|---:|
| 6 ms | 11,000 A (11 A model sınırı) | 4,983 ms | 11,000 V |
| 12 ms | 9,737 A | 9,874 ms | 11,000 V |
| 20 ms | 9,219 A | 16,404 ms | 11,000 V |

Yüksüz kalkışta 6/12/20 ms rampalar için 30–35 ms ortalama çıkış sırasıyla 11,397/11,414/11,383 V; tepe değerleri 11,404/11,422/11,391 V oldu. Daha yavaş soft-start yüksüz gerilim payını anlamlı biçimde artırmadı. Başlatma süresi ve akım sınırı, sistem ihtiyacıyla birlikte seçilmelidir.

#### 15.4 Küçük-sinyal çapraz kontrolü — HESAP + AC SİM

Tam yükte CCM ortalama buck bitkisi, `Zp = 1/(1/Ryük + 1/ZCout + 1/ZCd)` ve `Gvd = Vin·Zp/(RL+sL+Zp)` ile hesaplandı. Aynı güç katının bağımsız LTspice AC ortalama devresinde 100 Hz, 878 Hz, 1 kHz, 3 kHz ve 5,5 kHz noktaları karşılaştırıldı; en büyük fark yaklaşık 0,005 dB ve 0,11° idi. RC kompanzasyon bloğunun ayrıca ölçülen AC cevabı analitik `Ki/s·H1·H2` ile eşleşti. Bu, yalnızca seçilen küçük-sinyal ortalama modelinin çapraz kontrolüdür.

| Ki | Tam yük direnç modeli: crossover / faz payı | 82,5 W CPL küçük-sinyal modeli: crossover / faz payı |
|---:|---:|---:|
| 500 s⁻¹ | 2,95 kHz / 66,3° | 3,08 kHz / 63,6° |
| 1000 s⁻¹ | 5,48 kHz / 66,6° | 5,71 kHz / 64,7° |

Faz payları açık RC transferi ile ortalama CCM bitkisinin çarpımından hesaplandı; LT3844 benzeri üretici FRA sonucu değildir. 0,1 Hz–1 MHz hesabında −180° faz kesişimi bulunmadı; bu nedenle sonlu bir kazanç payı değeri raporlanmıyor. DCM, anahtarlama/sürücü gecikmesi, gerçek op-amp/kontrolcü dinamiği, tolerans ve parazitikler dâhil değildir.

#### 15.5 İlk deneme hatası, yorum ve açık riskler

İlk geçici denemede aynı lead transferleri LTspice `LAPLACE` kaynaklarıyla temsil edildi. Uzun 250 ms koşuda bu temsil yaklaşık 1,2 V sürekli salınım verdi; akım sınırı 50 A'a yükseltilen tanı koşusunda 13,17 V ve 28,1 A görüldü. Sonra aynı transferler açık RC durum elemanlarıyla yeniden kuruldu: ortalama CPL modeli ve anahtarlamalı güç katı 200 ms testlerinde kararlı çıktı. LTspice `LAPLACE` kaynaklarının 500 ms pencereli bu uzun geçici koşudaki sonucu bağımsız RC modeliyle uyuşmadığından **geçerli devre sonucu sayılmadı ve yöntem elemesi için kullanılmadı**; şüphe edilen neden modelin geçici/FFT temsilidir. Bu test-kurulum sorunu kayıtlı kalır.

Önceki genel PI testinde dokuz kazanç ayarının başarısız olması, tüm gerilim-kipi analog çözümlerini elememiştir. Açık RC Type-III modeli seçilmiş nominal testleri geçti; bu nedenle gerilim kipi artık akım kipiyle birlikte model düzeyinde adaydır. Şu anki kanıt, nihai yöntemi veya kontrol değerlerini seçmek için yeterli değildir:

- Bu modelde anahtarlama MOSFET'i/diyotun dondurulmuş kayıpları dışında gerçek kontrolcü, kapı sürücüsü, analog doyum/bant genişliği, gürültü ve besleme davranışı yoktur. İdeal `I(L1)` izleyicisi gerçek çevrim-başı akım algılama devresini kanıtlamaz.
- +5…+50 °C, L/C/ESR/R/DCR toleransları, batarya+kablo empedansı, daha geniş CPL köşeleri ve 11 A sınırının eşiği/tepki toleransı bu testte taranmadı. Ki=500 ve Ki=1000 de nihai değer değildir.
- Gerçek OVP, S1 kısa devresi, hızlı kaynak arızası ve yük portu koruması bu denemeye dâhil değildir. Normal çalışma testinde çıkışın 12 V altında olması bağımsız O1 korumasını kanıtlamaz. **Gerçek O1/S2E bağlanmaz.**
- Her iki yöntem de analog olabilir; mevcut simülasyonlardan gerçek maliyet, üretilebilirlik veya verim sıralaması çıkarılamaz. Gerilim kipinde düzenleme için akım algı direncinden kaçınma olasılığı, ayrı güvenli akım sınırı gereksinimini ortadan kaldırmaz.
- Güç katı dondurması, parça sırası ve açık çevrim testleri değiştirilmedi; bu bölüm yeni parça araştırması veya mimari onay değildir.

**§15 ara sonucu (14.11.2026, genişletilmiş §16 karşılaştırmasından önce):** tepe-akım kipli analog (LT3844 test makromodelinde D/F) ve sabit-frekans gerilim kipli analog (Type-III RC davranışsal model) iki aday olarak görülüyordu. O bölümde akım kipi seçilmiş testlerde daha küçük çizgi-geçiş aralığı verdi; gerilim kipi Ki=500/1000 örneklerinde 200 ms CPL ve kararlı ripple ölçütlerini tuttu. D/F ve Type-III'nin daha sonraki ortak koşulları, ortalama-akım karşılaştırması, puanlama ve güncel geçici yön önerisi §16'dadır. Akım algılama kaybı, ideal akım sınırı farkı, FRA belirsizliği, OVP ve gerçek maliyet/verim çözülmeden mimari onayı veya parça seçimi yapılmaz.

### 16. Genişletilmiş kontrol yöntemi karşılaştırması (14.11.2026)

Bu turda yalnız `%TEMP%\pdu-control-compare-20261114` altındaki geçici netlistler, hesaplar ve loglar kullanıldı. Açık çevrim dondurması, şematik, güç katı değerleri, parça sırası ve aday listesi değiştirilmedi. LTspice 26.1.1 kullanıldı. Bütün sonuçlar **SİM** veya **HESAP** olarak etiketlenmiştir; fiziksel devre ve ölçüm yoktur. 11 V ±%5 kararlı durum, ≤165 mV t-t ripple ve geçişte 9–12 V sınırları bu karşılaştırmanın tasarım hedefleridir. Gerçek O1/S2E bağlanmaz.

#### 16.1 Karşılaştırılan modeller

- **Sabit-frekans analog tepe-akım kipi, D/F:** ADI LT3844 üretici makromodeli; D ağında Rcomp=68 kΩ, F ağında 100 kΩ; her ikisinde Ccomp=3,3 nF ve Cpole=22 pF. D/F, seçilmiş güç katı parçası değildir. Geçici model 9,76 mΩ akım algılama direnci içerir; 7,5 A'de bu direnç **73,2 mV ve 0,549 W HESAP** ekler (82,5 W çıkışın yaklaşık %0,67'si). Açık çevrim dondurulmuş güç yolunda bu direnç yoktur.
- **Sabit-frekans Type-III gerilim kipi, Ki=200 s⁻¹:** H1 sıfır/kutup 350 Hz/8 kHz; H2 600 Hz/30 kHz; 12 ms referans rampası ve 100 kHz davranışsal PWM. Gerçek op-amp, PWM entegresi, MOSFET sürücüsü veya analog akım algısı yoktur. Modeldeki I(L1) kesimi ideal karşılaştırıcıdır; donanım eşik toleransı ve gecikmesi içermez.
- **Ortalama-akım kipi, geçici iki-çevrim modeli:** dış Type-II gerilim çevrimi (Ki=1000, fz=50 Hz, fp=20 kHz), iç P akım çevrimi (Kpi=0,04, 1 kΩ/8,2 nF ölçüm filtresi) ve 9,5 A ideal tepe kesimi. Sadece yöntem uygulanabilirliğini görmek için kuruldu; akım algılama, iç çevrim ve kontrolcü tümü davranışsal/ideal modeldir.
- **Gerilim-kipi PI ve Type-II:** 24,6 V ortalama bitkisi üzerinde 7 pasif köşe × 4 yük türü HESAP taraması. Bu, bütün analog gerilim-kipi tasarımlarının testi değildir.
- **Diğer olasılıklar:** COT/histeretik ve dijital kontrol için bu turda PDU zaman-alanı netlisti kurulmadı. COT/histeretik, seçili 100 kHz sabit frekans hedefiyle doğrudan örtüşmeyen değişken frekans ve geri besleme ripple koşulları taşır; TI [AN-1481](https://www.ti.com/lit/an/snva166a/snva166a.pdf) bu frekans değişimini ve geri besleme ripple ihtiyacını açıklar. Dijital kontrol için ADC/PWM gecikmesi, firmware hata yönetimi ve ayrı donanım OVP arayüzü henüz tanımlı değildir. Bu yöntemler puanlamada düşük kanıt güveniyle tutulur.

#### 16.2 Ortak zaman-alanı testleri — SİM

| Koşul | Tepe-akım D | Tepe-akım F | Type-III Ki=200, Ilim=9 A |
|---|---:|---:|---:|
| 20 V, tam-yük kalkışı | Vort=10,993 V; ilk tepe 11,033 V; bobin tepe 9,438 A | Vort=10,993 V; ilk tepe 11,027 V; bobin tepe 9,438 A | Vort=11,000 V; ripple=45,0 mV; bobin tepe=9,000 A (ideal limit) |
| 0,24→7,5→0,24 A, 10 ms doğrusal rampalar | 10,950–11,049 V; ripple=56,81 mV; Ipk=8,468 A | 10,951–11,046 V; ripple=56,79 mV; Ipk=8,464 A | 10,085–11,221 V; ripple=56,83 mV; Ipk=8,471 A |
| 0,24→7,5→0,24 A, 20 µs doğrusal rampalar | 10,764–11,193 V; Ipk=9,096 A | 10,794–11,164 V; Ipk=8,817 A | 9,763–11,544 V; ripple=56,83 mV; Ipk=9,000 A (ideal limit) |
| 20→26→20 V, 200 ms CPL | 10,887–11,047 V; son 1 ms ripple=46,77 mV; Ipk=8,932 A | 10,904–11,043 V; son 1 ms ripple=46,76 mV; Ipk=8,878 A | Ilim=9 A: 10,338–11,505 V; son 1 ms ripple=46,88 mV; Ipk=9,000 A (ideal limit) |
| 26 V yüksüz, 1 GΩ | Vlate=11,0028 V; son ripple=5,89 mV; başlangıç tepesi=11,082 V | Vlate=11,0028 V; son ripple=5,89 mV; başlangıç tepesi=11,071 V | Vlate=11,6303 V; başlangıç tepesi=11,6367 V; kararlı hedefin 11,55 V üst sınırını aşar, ancak seçilmiş modelde 12 V altında |

D/F 10 ms rampalı yük koşuları 100 ms, 20 µs rampalı yük koşuları 80 ms, Type-III hızlı yük koşusu 100 ms sürdü. Bunlar tam basamak değil doğrusal rampa profilleridir. LT3844 D/F hızlı yük testleri ayrı ayrı koşturuldu; Type-III hızlı yük testinin ikinci koşusu ilk ölçümlerle aynı log değerlerini verdi.

Type-III Ki=100, 11 A ideal kesimle 20–26–20 V ve 200 ms CPL birleşiminde **9,812–12,066 V** verdi ve 12 V üst sınırını aştı. Ki=200 için aynı testte kesim 11/10/9,5/9 A'ya indirildiğinde tepe akımları yaklaşık 11/10/9,5/9 A oldu; en düşük çıkış 10,338 V'ta değişmedi, üst tepe 11,650/11,607/11,570/11,505 V'a indi. 20 µs yük testindeki 9 A sonucu tekrarlandı. Bu, yalnız ideal çevrim-başı sınır davranışıdır; gerçek bobin marjı veya akım limit devresi kanıtı değildir.

Yüksüz Type-III Ki=200 modeline test amacıyla 4,7 kΩ direnç eklenip 500 ms çalıştırıldığında son 4 ms ortalaması 11,0034 V, son 1 ms ripple 3,60 mV ve başlangıçtan itibaren en yüksek değer 11,6341 V oldu. **HESAP:** 11 V'ta 4,7 kΩ yaklaşık 2,34 mA ve 25,7 mW tüketir. Bu direnç depoya veya ana şematiğe eklenmedi; 250 ms ölçümü kararlı olmadığı için yalnız 500 ms sonucu kullanıldı.

#### 16.3 Ortalama-akım ve kompanzasyon ekranı — HESAP + sınırlı SİM

Dış Type-II Ki=1000/fz=50 Hz/fp=20 kHz ve geçici iç çevrimle tam-yük kalkışı 24,6 V'ta 11,000 V ortalama, 55,8 mV ripple ve 9,351 A tepe verdi. Aynı model 0,24 A hafif yükte başlayıp 20 µs doğrusal yük rampasına geçtiğinde Kiv=1000/200/2000 denemeleri 20–70 ms test penceresinde sırasıyla **16,87/19,66/16,83 V** tepe verdi; Ki=200 örneğinde en düşük değer 6,55 V oldu. Toplam kalkış tepeleri sırasıyla 19,16/21,29/18,70 V'tu. Bunlar seçilen davranışsal kurulum/kazanç denemelerinin başarısız sonuçlarıdır, ortalama-akım yönteminin bütün ayarlarının elendiği anlamına gelmez. Kiv=100 koşusu beş dakika içinde transient ölçüm üretmedi; ilgili LTspice işlemi durduruldu ve bu satır **tamamlanmadı**, PASS/FAIL sayılmadı. Bu nedenle yöntem anahtarlamalı performans açısından açık aday/risktir.

Ayrı HESAP ekranında ortalama-akım iç çevrimi 5/10/20 kHz tek kutup ve yarım periyot gecikmesiyle **ideal** kabul edildi. 648 Type-II/PI ayarı PM≥45° ve crossover≤10 kHz ölçütünü sağladı; bu ayarların PDU anahtarlamalı modeliyle doğrulaması yoktur. Aynı 7 pasif köşe × 4 yük ekranında:

- 1.170 gerilim-kipi Type-II ağı tarandı; 127 ayar kaba ölçütü sağladı, ancak bunların en yüksek crossover'ı 19,8 Hz idi. Crossover'ı 100 Hz üstünde ve PM≥45° olan üç ağın her birinde birden fazla 0 dB kesişimi bulundu; bunlar robust aday sayılmadı.
- 14 PI kazanç ayarının hepsinde en kötü köşe faz payı negatif çıktı.
- Type-III Ki=200, 350/600 Hz sıfırlar ve 8/30 kHz kutuplarla bağımsız yoğun frekans hesabında 84 VIN/köşe/yük birleşiminde tek crossover verdi. En kötü PM **59,084°**, crossover **4,581 kHz** (26 V, düşük-L/düşük-ESR köşesi, 82,5 W CPL); 24,6 V'ta en kötü 59,852°/4,384 kHz oldu. Bu sonuç ikinci bir skaler karmaşık-sayı hesaplamasıyla tekrarlandı; fark <0,001°. Küçük-sinyal ortalama CCM modeli, fiziksel kararlılık ölçümü değildir.

ADI [AN-149](https://www.analog.com/en/resources/app-notes/an-149.html), küçük-sinyal modelinin çalışma noktası çevresinde lineerleştirildiğini ve zaman-alanı/PCB etkilerinin ayrıca değerlendirilmesi gerektiğini belirtir. Buradaki HESAP sonuçları aynı sınırı taşır.

#### 16.4 Mimari karşılaştırma ve ön puan

Puanlar bir **mühendislik ön taramasıdır**, ölçülmüş maliyet/verim veya sertifikasyon puanı değildir. Ağırlıklar: çıkış hedefleri + 100 kHz + dondurulmuş güç yoluna uyum %35, kanıt gücü %25, uygulama sadeliği %15, beklenen devre maliyeti %10, güç yoluna ek kayıp %10, koruma bütünlüğü %5. Her başlık 0–100; yüksek maliyet/kayıp puanı görece daha az maliyet/ek kayıp beklentisi demektir. Maliyet puanı BOM teklifi değil, beklenen parça ve devre karmaşıklığına dayalı TAHMİN'dir; ADI/DigiKey sayıları yalnız kaynakta görülen ürün fiyatlarıdır. Ağırlıklı toplam yuvarlanmıştır. Kesin fiyat/BOM ve fiziksel test yoktur; yaklaşık 10 puandan küçük farklar karar gücü taşımaz.

| Yöntem / temsil | Uyum (35%) | Kanıt (25%) | Uygulama kolaylığı (15%) | Maliyet tahmini (10%) | Ek kayıp (10%) | Koruma (5%) | Ağırlıklı ön puan | Kanıt güveni |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sabit-frekans tepe-akım, LT3844 F makromodeli; 9,76 mΩ seri algı direnciyle | 75 | 85 | 70 | 60 | 65 | 60 | **74/100** | Orta: üretici makromodeli, fakat geçici güç yolunda dondurulmuş katta olmayan algı direnci var |
| Gerilim-kipi Type-III Ki=200; 48 ms referans rampası ve 9 A ideal akım kesimi | 80 | 65 | 50 | 60 | 90 | 35 | **69/100** | Düşük-orta: RC davranış modeli ve ideal akım izleyici; gerçek akım koruması yok |
| Histeretik 25 mV, sabit-100-kHz şartıyla | 55 | 60 | 75 | 80 | 80 | 30 | **63/100** | Düşük: ideal karşılaştırıcı/kilit ve ideal akım eşiği; ölçülen frekans 100 kHz sabit değil |
| Histeretik 25 mV, frekansın değişmesine izin verilirse (koşullu) | 95 | 60 | 75 | 80 | 80 | 30 | **77/100** | Düşük: model davranışı iyi, donanım denetleyicisi ve gürültü/blanking doğrulanmadı |
| Ortalama-akım çift çevrim, ilk geçici model | 40 | 45 | 35 | 40 | 50 | 30 | **41/100** | Düşük: yalnız ideal HESAP olumlu; anahtarlamalı hafif-yük koşusu sınır dışı/tamamlanmamış |
| Gerilim-kipi Type-II | 25 | 20 | 60 | 60 | 50 | 25 | **35/100** | Düşük: bir hızlı-geçiş örneği başarısız; tüm ayarlar taranmadı |
| Analog PI gerilim kipi | 15 | 10 | 85 | 80 | 50 | 25 | **35/100** | Düşük: yalnız sınırlı HESAP taraması |
| Dijital PWM + yazılım PI | 25 | 20 | 25 | 35 | 55 | 40 | **29/100** | Çok düşük: bu turda PDU zaman-alanı modeli veya firmware yok |

Uyum puanı hem 9–12 V / ±%5 / 165 mV hedeflerini hem 100 kHz ve dondurulmuş güç yoluyla uyumu tartar. Maliyet ve ek kayıp puanları tam BOM/verim hesabı değildir. Bu puanlar mühendislik yargısıdır; özellikle 5 puanlık koruma ağırlığı güvenlik kabulü anlamına gelmez. 10 puandan küçük toplam farklar anlamlı sıralama sayılmaz. LT3844 makromodeli geçişleri iyi tuttu, ancak 9,76 mΩ seri algı direnci dondurulmuş güç yolunda bulunmuyor. Type-III modelinde seri direnç yoktu; fakat 9 A akım sınırı gerçek algılayıcı değil, simülasyonda doğrudan `I(L1)` izleyen ideal bir karşılaştırıcıydı. Bu nedenle hiçbir satır gerçek donanım veya O1 aşırı-gerilim güvenliği onayı değildir.

#### 16.5 Geçici sonuç ve açık kapılar

**Sonuç:** sabit 100 kHz ve LT3844 modelinin eklediği 9,76 mΩ algı direncine izin verilirse, tepe-akım kipi bu test setinde en güçlü ve en çok doğrulanmış analog adaydır; bu dirençte 7,5 A için **0,549 W HESAP** kayıp vardır. Güç yolu kesinlikle aynı kalacaksa bu, doğrudan uygulanabilir kazanan değildir. Seri algı direnci eklenmeyen Type-III, 48 ms soft-start ile seçilen testleri tuttu; ancak gerçek akım algılama/koruma hâlâ çözülmedi. Değişken-frekans histeretik model en dar çıkış penceresini verdi ama 20–26–20 V sırasında 93,7–121,2 kHz'e kaydı ve ideal donanım modelidir. Dolayısıyla mevcut dondurma koşulunda henüz fiziksel olarak uygulanabilir nihai kontrol mimarisi kanıtlanmış değildir. Parça veya güç yolu değeri seçilmedi.

#### 16.6 Bağımsız yeniden test, ek yöntemler ve pazar karşılaştırması — SİM + DATASHEET

Bu ek turda LTspice 26.1.1 ile yalnız geçici dosyalar kullanıldı; güç katının repo içindeki değerleri, şematiği ve aday sırası değiştirilmedi. Yeni netlistler `%TEMP%\pdu-control-reassessment-20261114-final`, HESAP ekranları `%TEMP%\pdu-control-compare-20261114` altında tutuldu. Depodaki açık-çevrim on test kipi bu turda yeniden koşturulmadı: güç katı değişmedi ve 14 Kasım tarihli tam tekrar kaydı §13–14'tedir. Aşağıdaki değerler SİM veya HESAP'tır; fiziksel ölçüm değildir.

**LT3844 F, 100 kHz sabit-frekanslı tepe-akım makromodeli:** üretici modeli tam-yük 20 V kalkışında 11,027 V tepe / 10,993 V ortalama ve 9,440 A bobin tepesi verdi. Ham bobin akımı tepe aralıkları 40–50 ms tam-yük penceresinde yaklaşık **99,95 kHz** sayıldı. 20–26–20 V ve 200 ms sabit-güç yük testinde 10,904–11,043 V, son 1 ms'de 46,76 mV ripple, 8,878 A tepe; giriş 20 V'a döndükten sonra 10,970–11,099 V aralığı ölçüldü. Taze 20 µs yük rampası tekrarı 10,794–11,165 V ve 8,817 A verdi; tam yükte kararlı ripple yaklaşık 56,81 mV idi. 26 V yüksüz başlangıç ölçümünde ilk tepe 11,071 V, geç değer yaklaşık 11,003 V'tu. Simüle edilen sense direnci 9,76 mΩ olup dondurulmuş katın parçası değildir; çıkış akım yoluna eklenmiş bu direnç 7,5 A'ta **73,2 mV / 0,549 W HESAP** eder. Makromodelün ilk çalışma noktası Gear ile bulunamadı ama Gmin adımlamasıyla bulundu ve transient tamamlandı; sonuç bu nedenle sayıldı.

**Type-III Ki=200, feed-forward, 9 A ideal çevrim-başı akım sınırı:** 20 V tam-yük kalkışı 11,031 V tepe / 11,000 V ortalama ve 8,596 A verdi. 20 µs yük rampası 9,809–11,478 V, 56,85 mV ripple ve 9,000 A ideal eşik verdi. 200 ms CPL ve 20–26–20 V testinde 10,857–11,047 V, 46,88 mV ripple ve 8,774 A; kaynak döndüğünde son aralık 10,977–11,024 V oldu. Yüksüzde 20 V için 48 ms referans rampasıyla tam 120 ms simülasyon yapıldı: çıkışın ilk tepe değeri 11,413 V, 115–119 ms geç aralığı 11,410 V oldu; böylece 11 V ±%5 üst sınırı 11,55 V içinde kaldı. Önceki 40 ms koşusu referans rampası tamamlanmadan bittiği için 35–39 ms'deki 11,584 V son durum ölçütü olarak kullanılmadı. Aynı modelde 60 ms rampasıyla geç değer 11,353 V, 80 ms rampasıyla 11,290 V; 26 V'ta 48 ms örneği 11,328 V verdi. 48 ms bu seçilen yüksüz senaryoları geçirdi; bu değer donanım kararı değildir. 1 GΩ kaçak yolu sadece yüksüz test modelinde, düğümün sayısal olarak yüzmemesi için kullanıldı; gerçek devreye direnç eklenmedi.

Bu FF ağı için küçük-sinyal ortalama CCM **HESAP**'ı ayrıca 3 VIN × 7 pasif köşe × 4 yük = 84 senaryoda tekrarlandı: tek crossover bulunan her senaryoda en kötü faz payı **54,554°**, crossover **6,230 kHz** (26 V, düşük-L/düşük-ESR, 82,5 W CPL); en yüksek crossover 7,526 kHz oldu. Vektör ve skaler hesap farkı 0,001°'den küçüktür. Ayrı geniş ağ taramasında 3.116 PI/Type-II/Type-III ayarından 198'i ilk faz payı/bant genişliği ölçütünü geçti; en iyi Type-III hesabı K=100, 350/400 Hz sıfırlar ve 8/30 kHz kutuplarla 65,753° / 3,457 kHz verdi. Ancak bu K=100 ağı zaman-alanı testinde 26 V yüksüzde 12,007 V'a ve hızlı yükte 9,712–11,730 V'a ulaştı. Bu nedenle daha iyi HESAP faz payı tek başına iyi kontrol sonucu değildir; K=100 seçilmedi. K=200 ağının küçük-sinyal hesabı lineer CCM yaklaşımıdır ve doyum, DCM, gecikme, gerçek PWM/akım algısı veya OVP'yi kanıtlamaz.

**Histeretik karşılaştırıcı ve pulse-skip, 25/50 mV histerezis:** 25 mV modelinde tam-yükte 10,975–11,025 V, yaklaşık 50,02 mV ripple ve 9,000 A ideal tepe eşiği görüldü; ortalama darbe frekansı yaklaşık 111,33 kHz'ti. 20 µs yük rampasında 10,975–11,043 V / 50,02 mV / 8,715 A / 113,62 kHz ölçüldü. 200 ms CPL ve 20–26–20 V koşusunda 10,975–11,025 V / 50,02 mV / 8,326 A çıktı; darbe frekansı 20 V'ta 93,73 kHz, 26 V'ta 121,24 kHz, geri dönüşte 93,73 kHz olarak ham anahtarlama izlerinden sayıldı. 50 mV histerezisli örnekte tam-yükte 10,950–11,039 V / 89,00 mV / 62,58 kHz; hızlı geçişte 10,950–11,082 V / 90,62 mV / 62,73 kHz oldu; 25 mV örneğine göre daha geniş çıkış salınımı ve daha düşük ortalama frekans verdi. Yüksüzde 25 mV karşılaştırıcı darbe atlayıp 26 V başlangıç tepesini 11,025 V'ta tuttu; bu yalnız ideal mandal/karşılaştırıcıdır. Gerçek histerezis denetleyicisi, ölçüm filtresi, blanking, gürültü bağışıklığı ve akım algısı kurulmadı.

**İki bağımsız kontrol:** üç uzun koşunun kaydedilmiş `.raw` dalga şekillerinden NumPy ile yeniden hesaplanan Vmin/Vmax/ripple, LTspice `.meas` günlükleriyle sayısal çözünürlük içinde eşleşti. Histeretik 20–26–20 V frekansı ayrıca `V(q)` yükselen kenarlarını ham dosyadan sayarak tekrarlandı. Eksik veya geçersiz denemeler PASS sayılmadı: ilk CPL netlistindeki ölçüm penceresi/transient süresi uyuşmazlığı düzeltilip yeniden koşuldu; davranışsal yüksüz yük kaynağının çıkışı yüzdürmesi 1 GΩ test kaçağıyla giderildi; ilk 10 mV pulse-skip denemesi LTspice yakınsama toleransını gevşetip durduğu ve ölçümleri üretmediği için kullanılmadı. Bu düzeltmeler yalnız geçici test dosyalarındadır.

**Üretici ve satılabilir ürün karşılaştırması:**

- ADI [LT3844 veri sayfası](https://www.analog.com/media/en/technical-documentation/data-sheets/3844fc.pdf) ve [ürün sayfası](https://www.analog.com/en/products/lt3844.html) 100–500 kHz sabit-frekans, N-kanal MOSFET kapı sürücüsü, burst/light-load çalışma, soft-start, UVLO, akım sınırı ve termal kapatma işlevlerini belgeler. ADI sayfası 1 ku liste fiyatını 4,71 USD'den başlatıyor; bu yalnız denetleyici fiyatıdır, PDU BOM'u veya Türkiye'ye teslim maliyeti değildir. Veri sayfası buck'ta endüktör akımı algısı için seri `RSENSE` tarif eder; modeldeki güç yolu farkı gerçektir.
- ADI [AN-149](https://www.analog.com/en/resources/app-notes/an-149.html) gerilim-kipi için Type-III kompanzasyonun daha çok RC elemanı gerektirebildiğini ve akım algısının şönt, bobin DCR'si veya MOSFET RDS(on) üzerinden yapılabildiğini açıklar. DCR/RDS algısı bu turda LT3844 ile doğrulanmadı; ayrı devre ve kontrolcü uyum testi gerekir.
- TI [PMP10799](https://www.ti.com/tool/PMP10799) 19–32 V'tan 12 V/8 A'a senkron buck referansıdır; üretici 24 V'ta 4,5–8 A aralığı için >%97 verim, 50 mVpp ripple ve 8 A adımında <%2 çıkış değişimi bildirir. Raporunda 24 V / 8 A'da 36,4 kHz bant genişliği ve 64° faz payı gösterilir. Bu kart test için üretilmiş, satılmıyor; senkron güç katı kullandığından PDU'nun asenkron dondurmasına doğrudan taşınamaz.
- TI [TPS40170 veri sayfası](https://www.ti.com/lit/ds/symlink/tps40170.pdf) başka bir uygulanmış kontrol örneğidir: gerilim-kipi, giriş feed-forward, 100–600 kHz, soft-start ve akım/kısa-devre korumaları vardır. Ancak senkron alt MOSFET üzerinden OCP algısı kullanır; mevcut diyotlu kat için doğrudan uyumlu değildir. Bu örnek sabit-frekans gerilim kipinin endüstride geçerli olduğunu gösterir, fakat PDU için test sonucu sağlamaz.
- TI [LM5085 veri sayfasındaki](https://www.ti.com/lit/ds/symlink/lm5085.pdf) COT örneği harici P-kanal MOSFET kullanır ve FB'de en az 25 mV ripple gerektirir. Bu PDU'nun harici N-kanal anahtarına doğrudan uymaz; bizim histeretik modelimiz de LM5085 modeli değildir. Anahtarlama frekansı/geri-besleme ripple davranışı yük ve çalışma kipine göre ayrıca kontrol gerektirir.
- Satışta bulunan [RECOM RPMGE12-10](https://recom-power.com/en/products/switching-regulators/rec-p-RPMGE12-10.html) 18–75 V girişli, 8–15 V ayarlanabilir çıkışlı, 10 A / 120 W, üretici beyanıyla %95'e kadar verimli ve OCP/OTP/SCP korumalı tam DC/DC modülüdür. [DigiKey ABD sayfasında](https://sc-b.digikeyassets.com/en/products/detail/recom-power/RPMGE12-10/23346895) bu inceleme sırasında 1 adet fiyatı 34,50 USD, stok 253 ve üretici termin süresi 30 hafta gösterildi; fiyat/tedarik ülkeye ve zamana göre değişir. Bu ürün kontrol katı değil, güç katının tamamının yerine geçer; 11 V'a trimlenmesi ve cihazın 12 V tavanını güvenle koruması ayrıca doğrulanmadan aday sayılamaz.

PMP10799 gibi sabit-frekans gerilim-kipi örneği, COT/histeretik ürünler ve hazır modül piyasada mevcut yöntemleri gösterir. Hiçbir dış örneğin performansı PDU'da ölçülmüş gibi kullanılmadı; satılabilir modülün verimi de ideal/simüle PDU yöntem puanlarıyla doğrudan kıyaslanamaz.

**Bu turun nihai ara kararı:** 100 kHz hedefi korunursa, zaman-alanı kanıtı en güçlü kontrol yöntemi LT3844 tipi sabit-frekans tepe-akım kontrolüdür; ancak bu modeldeki 9,76 mΩ seri algı direnci güç yolunu ve ısı kaybını değiştirir. Güç yolu hiç değişmeyecekse 48 ms soft-start'lı Type-III, daha düşük toplam puanla test edilebilir bir sonraki kontrol adayıdır; gerçek akım algısı/koruması ve bütün çalışma köşeleri hâlâ gösterilmedi. Histeretik model yalnız değişken frekans kabul edilirse karşılaştırılabilir alternatif olur. Dondurulmuş kat, parça sırası ve değerleri değişmedi; gerçek O1/S2E, fiziksel prototip ve PCB aşamalarına geçilmedi.

Her üç yöntem için bağımsız OVP, 12 V altında kesme, bobinin gerçek sıcaklık/doyum marjı ve arıza testleri çözülmedi. Normal çalışma SİM'inde 12 V altında kalmak hata durumunda güvenlik kanıtı değildir. Gerçek yük, fiziksel prototip ve PCB aşamalarına geçilmez.

#### 16.7 Ön puanın 90 üzerine çıkma koşulları ve sınırlı güç katı değişikliği — HESAP + DATASHEET

Mevcut tablo puanları sabit ağırlıklarla değerlendirilmelidir; yeni bir güç katı fikri için önceden puan artışı varsayılmaz. Sabit 100 kHz adayları içinde en yüksek puan LT3844 F'nin **74/100** değeridir. **77/100** histeretik sonuç, frekansın girişle yaklaşık 93,7–121,2 kHz değişmesine izin veren koşullu senaryodur ve 100 kHz sabit gereksinimini karşılamaz.

LT3844 satırının mevcut alt puanları uyum=75, kanıt=85, kolaylık=70, maliyet=60, ek kayıp=65, koruma=60'tır. Ağırlıklı ham toplam:

`0,35×75 + 0,25×85 + 0,15×70 + 0,10×60 + 0,10×65 + 0,05×60 = 73,5` → yuvarlanmış **74/100**.

Yalnız güç katına uyumu ve ek kaybı kusursuz 100'e yükseltip diğer alt puanları aynı bıraksak bile:

`0,35×100 + 0,25×85 + 0,15×70 + 0,10×60 + 0,10×100 + 0,05×60 = 85,75` → yaklaşık **86/100**.

Bu nedenle küçük güç yolu iyileştirmesi tek başına 90 puanı sağlamaz. Aynı rubrikte örnek olarak uyum=95, kanıt=90, kolaylık=85, maliyet=85, ek kayıp=95, koruma=90 toplamı **91/100** eder. Bu yalnızca matematiksel örnektir; hiçbir mimari için bu puanlar verilmiş değildir. Gerçek test kanıtı, maliyet ve koruma tasarımı ayrıca elde edilmelidir. Ayrıca puan tablosundaki koruma ağırlığı yalnız %5'tir; 90+ sonuç O1 için bağımsız 12 V aşırı gerilim koruması koşulunu gevşetmez. OVP ve arıza anındaki port gerilimi doğrulanmadan güvenlik kapısı kapanmış sayılmaz.

**Şöntsüz akım algısı için araştırma yönü:** Dondurulmuş çıkış akım yoluna seri direnç eklememek için bobin sargısının DCR düşümü, bobine paralel bir RC algı ağı ile izlenebilir. TI'nin [LM5137-Q1 veri sayfası](https://www.ti.com/lit/ds/symlink/lm5137-q1.pdf) bu yöntemi, eşleşmiş `R_CS C_CS = L/DCR` zaman sabitiyle bobin DCR gerilimini taklit eden kayıpsız ve sürekli akım ölçümü olarak anlatır. Aynı belge, oda sıcaklığında tipik akım sınırı doğruluğunu %10–15 verir ve bu yöntemi hassas akım sınırı gerektirmeyen uygulamalar için ayırır. Belgedeki kontrolcü **senkron buck** içindir; bu örnek mevcut asenkron S1+D1 katıyla doğrudan uyum kanıtı değildir. ADI'nin [akım algılama konumları notu](https://www.analog.com/en/resources/technical-articles/switch-mode-power-supply-current-sensing-part-2-where-to-place-the-sense-resistor.html) da bobin DCR algısının harici seri şöntün kayıp ve maliyetini azaltabileceğini belirtir.

PDU'daki bobin DCR değeri henüz fiziksel ölçülmedi; sıcaklık katsayısı, endüktans ve DCR toleransı, RC eşleşmesi, anahtarlama düğümü gürültüsü, algı yükselteci/kontrolcü ortak-mod aralığı ve hata anındaki akım tepkisi çözülmedi. Bu nedenle DCR algısı **en az güç yolu değişikliğiyle araştırılabilecek bir adaydır**, seçilmiş yöntem veya güvenlik koruması değildir. DCR ağı, daha düşük değerli seri şönt ve senkron doğrultma ancak kullanıcı kapsamı netleştirdikten sonra geçici modellerde karşılaştırılabilir; açık çevrim dondurması, parça sırası ve değerleri değişmez. Bu bölümde yeni LTspice koşusu veya fiziksel test yapılmadı.
