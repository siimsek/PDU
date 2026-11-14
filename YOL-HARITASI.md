# Yol Haritası ve Durum

Bu dosya projenin **nerede olduğunu** ve **sırada ne olduğunu** gösterir. Bir yapay zekâ aracı veya yeni biri depoyu açtığında önce burayı, sonra [AGENTS.md](AGENTS.md) dosyasını okur.

**Son güncelleme:** 14 Kasım 2026 (kapalı çevrim ek testleri, dış kaynak karşılaştırması ve ön puanın sınırları belgelendi; geçici güç katı varyantlarının test kapsamı bekleniyor)

**14 Kasım 2026 kapalı çevrim son ek testi:** LT3844 F üretici makromodeli 20 µs yük rampasında 10,794–11,165 V, 20–26–20 V / 200 ms CPL testinde 10,904–11,043 V verdi; ham dalga şeklinden sabit-frekansın ≈99,95 kHz olduğu sayıldı. Bu model dondurulmuş güç yolunda olmayan 9,76 mΩ seri akım algı direnci ve yaklaşık 0,549 W HESAP kaybı ekler. Type-III Ki=200 / 9 A **ideal** akım kesimi, 20 µs rampada 9,809–11,478 V ve 200 ms CPL'de 10,857–11,047 V verdi. Yüksüz 20 V başlangıcında 48 ms referans rampasıyla simülasyon 120 ms'ye uzatıldığında 11,413 V tepe / 11,410 V geç değer ölçüldü; önceki 40 ms koşusu rampayı tamamlamadan bittiği için 11,584 V ara penceresi son değer sayılmadı. 60/80 ms rampaları 11,353/11,290 V geç değer verdi. Histeretik 25 mV modeli daha dar çıktı aralığı verdi fakat frekansı girişe göre yaklaşık 93,7–121,2 kHz değiştirdi. Bu nedenle 100 kHz şartı için LT3844 benzeri tepe-akım kontrolü en güçlü dinamik referans; güç yolu katı biçimde aynı kalacaksa 48 ms'lik Type-III test yönü mevcut alternatiftir. İki modeldeki akım algısı idealdir/ek dirençlidir; gerçek akım koruması, OVP, maliyet/verim ve fiziksel test kanıtlanmadı. Son puanlama, dış üretici ve satılabilir modül karşılaştırması, tekrar testleri ve açık riskler [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16 içindedir.

**14 Kasım 2026 puan ve güç katı değişikliği değerlendirmesi:** Mevcut LT3844 sabit-frekans puanı 74/100'dür; 77/100 histeretik sonuç ise 100 kHz sabit kalmadığı için koşulludur. Aynı ağırlıklarla yalnız güç katına uyum ve ek kayıp puanlarını 100 yapmak, diğer başlıklar değişmezse toplamı yaklaşık 86/100'e çıkarır; 90 üzeri için kanıt, maliyet/kolaylık ve koruma puanlarında da gerekçeli iyileşme gerekir. Bobin DCR'sini RC ağıyla algılamak, seri şönt kaybını önlemek için araştırılabilir; üretici örneklerinde %10–15 oda sıcaklığı akım sınırı doğruluğu ve senkron buck topolojisi görüldüğünden asenkron PDU'da doğrudan uyum kanıtlanmış değildir. Bu yeni varyantlar test edilmedi veya seçilmedi; puan hesabı ve kaynaklar [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16.7'dedir.

**14 Kasım 2026 tam tekrar ve kontrol ağı incelemesi:** Dondurulmuş açık çevrim kat üzerinde on depo kipi (`hesap`, `sayisal`, `secilen`, `pencere`, `tarama`, `mevcut`, `kararlilik`, `zarf`, `stres`, `grafik`) seri koşuldu ve süreç çıkış kodları 0'dı; bu elektriksel PASS değildir, açık çevrim başarısız/uyarı satırları §13–14'te korunmuştur. Depo dışında toplam 69 kompanzasyon ağı kaba FRA ile tarandı; D/F finalistleri için üç köşede hassas FRA, 200 ms CPL, çizgi adımı, hafif/yüksüz, tam yük kalkışı ve +5/+50 °C makromodel koşuları yapıldı. D ve F ağları seçilmiş makromodel senaryolarında 9–12 V ve 165 mV sınırlarında kaldı; simüle bobin akım tepeleri koşula göre yaklaşık 8,30–9,67 A idi. Bu, genel modül kabulü, gerçek bobinin 12 A dayanımı, tüm toleranslar veya arıza korumasını kanıtlamaz. FRA çok küçük uyarım tekrarı gürültü tabanında kaldı, D ağı uyarım genliğine duyarlı çıktı ve kazanç payı ölçüm aralığında belirlenemedi. Bu nedenle kapalı çevrim değerleri seçilmedi. D, F'ye yakın geçici yanıtı daha düşük bant genişliğiyle verdiği için **sonraki geçici model turu için önerilen başlangıçtır**, global optimum değildir. LT3844 testinde gerekli seri akım algılama direnci dondurulmuş güç yolunda bulunmadığından yaklaşık 0,55 W ek kayıp/seri direnç arayüz riski ayrıca kaydedildi. OVP 12 V sınırını hâlâ geçemedi. Ayrıntı [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §14'tedir.

**14 Kasım 2026 gerilim-kipi geçici karşılaştırması:** Aynı güç katında açık RC durum elemanlı Type-III model Ki=500/1000 s⁻¹ ile denendi. Ki=500 örneği 20–26 V tam-yük giriş geçişinde 10,642–11,424 V; 24,6 V'ta 200 ms 41,25→82,5 W CPL testinde 10,830–11,057 V ve son 1 ms'de 58,0 mV t-t verdi. 0,24 A'da 11,00 V/29,7 mV; yüksüzde 11,397 V ölçüldü. Ayrı 11 A çevrim-başı sınırı yalnız ideal `I(L1)` izleyicisidir; gerçek algı devresi değildir. Küçük-sinyal ortalama model hesabı Ki=500 için tam yükte 2,95 kHz/66,3°; 82,5 W CPL'de 3,08 kHz/63,6° verdi. Bu seçilmiş ideal model koşullarıdır; gerçek kontrolcü, tüm sıcaklık/toleranslar, OVP, maliyet/verim veya fiziksel test doğrulanmadı. Voltaj kipi artık PI örneğine bakılarak elenemez; akım kipiyle birlikte adaydır, mimari seçilmedi. Ayrıntı [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §15'tedir.

**13 Kasım 2026 kanıt notu:** Dondurma geçmiş kullanıcı kararıdır; denenmiş model ve senaryoların dışına genellenmez. 200 ms testleri birden fazla model setinde, 500 ms testi ise ayrı bir pencere köşesi senaryosunda koşuldu. 200 ms'den kısa darbede gözlenen sönüm tek başına geçme kanıtı değildir; ihlal veya büyüme ise başarısızlıktır. Sıfır süreç çıkış kodu elektriksel geçme anlamına gelmez. Ayrıntı: [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §13.

**13 Kasım 2026 tekrar koşuları:** Analitik hesap, ana şematik ve tüm depo kipleri `sayisal`, `secilen`, `pencere`, `tarama`, `mevcut`, `kararlilik`, `zarf`, `stres`, `grafik` seri biçimde yeniden koşuldu. Belirli pencere ve 200 ms kararlılık senaryoları geçti; açık çevrim hafif yük, sert kalkış, bazı parazitik stresler ve eski dalsız modellerde sınır dışı sonuçlar da tekrar görüldü. 200 ms'den kısa darbelerin yanlış GEÇTİ etiketi düzeltildi ve `kararlilik` güncel kodla tam olarak yeniden koşuldu: kısa, sınır içi örnekler BELİRSİZ; 27 adet 200 ms model-yük satırı ve ayrı 500 ms örneği GEÇTİ; dört eski dalsız karşılaştırma KALDI. Ayrıca LT3844 ve PI geçici kapalı çevrim modelleri, LTC4365/ideal ayırıcı arıza testleri 100/50 ns adımlarında tekrarlandı. LT3844 örneği line/CPL ve hafif-yük testlerini geçti; PI örneği hızlı giriş testinde 9,66–12,90 V ve 19,16 A tepe verdi; LTC4365'in sentetik 11→25 V testleri 12 V'u aştı. LM5088 makromodeli yakınsamadı. Bu sonuçlar yöntem yönü önerir fakat parça, OVP veya gerçek yük güvenliği onaylamaz; [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §13'tedir.

**Güncel çalışma sırası:** Önce kalan teknik denetim ve sistem gereksinimleri; ardından PWM, geri besleme, sürücü ve korumaların **mimari ve arayüz gereksinimleri**; sonra kontrolcü ve güç katı adaylarının birlikte değerlendirilmesi, kesin seçim, doğrulama ve prototip. Bobin için 33 µH, 7,5–10 mΩ @20 °C başlangıç hedefidir ([parça hedefleri](buck/PARCA-HEDEFLERI.md)); gerçek çekirdek ve sarım ölçülmeden ve kontrolcü uyumu görülmeden nihai değildir. Örnek 48,0 V sıcak takma hesabına karşı 50 V Cin payı açık risktir.

## Şu anki durum

| | |
|---|---|
| **Proje** | Tekne için güç dağıtım kartı (PDU): 6S bataryadan (20–26 V) 11 V / 7,5 A üreten tek faz asenkron buck dönüştürücü |
| **Modül zarfı** | 0–7,5 A / 82,5 W; dirençli, sabit akımlı ve sabit güçlü yükler. Kapalı çevrim için 11 V ±%5 kararlı durum ve ≤ 165 mV t-t ripple hedeflendi; cihazların ortak çalışma aralığı 9–12 V. Arızada çıkışın kesilmesi kabul edildi; O1'in 12 V üst sınırının korunması henüz doğrulanmadı. Açık çevrim dondurması önceki O1/S2E ölçütlerine dayanır. |
| **Referans yükler** | T3 Gemstone O1 (5–12 V) ve SLAMTEC RPLIDAR S2E (9–28 V); cihaza özgü uyumluluk testi olarak, modülün tek tasarım sınırı olarak değil |
| **Aktif iş** | Kontrol yöntemlerinin model düzeyindeki genişletilmiş karşılaştırması tamamlandı. 100 kHz için tepe-akım kanıtı güçlü; ancak modeli 9,76 mΩ seri direnç içeriyor. Dondurulmuş güç yolunu koruyan Type-III modeli 48 ms soft-start ile seçilen testleri geçti; ideal akım algısı donanımda çözülmedi. Mimari ve değer seçilmedi. |
| **Dondurma durumu** | **FROZEN** (açık çevrim simülasyon dondurması, 12.11.2026): örneklenen koşullar sınandı, `Cd = 470 µF + seri Rd = 0,22 Ω` ve gerilim sınıfı hedefleri onaylandı. Kapalı çevrim ve gerçek parçalar doğrulanmadı ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §12.1). |
| **Bekleyen iş** | Tepe-akım modelindeki seri algı direnci güç yolu değişikliği ve 0,549 W HESAP kaybı getirir. Type-III ve histeretik modellerde `I(L1)` ideal izleyicisi gerçek akım sensörü değildir; Type-III'nin tüm sıcaklık/tolerans ve yüksüz koşulları taranmadı. Gerçek bobin tepe akımı, bağımsız OVP'nin O1 portunda 12 V altında kesmesi, maliyet/verim ve fiziksel ölçüm açık. |
| **Sıradaki karar** | Güç katı dondurması başlangıç referansı olarak kalacak; geçici test kapsamına DCR akım algılı asenkron varyantı alalım mı? Bu en az güç yolu değişikliği adayıdır ama uyumu ve sıcaklık/tolerans doğruluğu kanıtlanmamıştır. Senkron doğrultma daha büyük bir değişikliktir. Bu karar parça, devre değeri veya açık çevrim dondurmasını değiştirmez. PCB kapsam dışı. |
| **Devrenin hâli** | Açık çevrim, soft-start yok. LTspice'ta örnek senaryolar sınandı; **fiziksel devre ve ölçüm yok** |
| **Güvenlik** | Gerçek O1 / S2E **bağlanmaz**: açık çevrim 12 V üst sınırını garanti etmez |
| **Ana aşama** | **A — Ana güç devresi** sürüyor; B kontrol aşamasının arayüz ve mimari hazırlığı paralel ele alınacak |
| **Dal** | Bütün iş `main` dalında. Güncel hâl her zaman `main`'dedir |
| **Aşama kaydı** | Aşama A: `ANA-GUC-DEVRESI` dalı (ara kayıt: hedef değerlerin doğrulandığı hâl, etiket `ana-guc-devresi-v2`) ve [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) milestone'u (açık). İkisi de Aşama A kapanınca (Adım 3 sonu) güncellenir/kapatılır |

### Şematikteki değerler (tek bakışta)

| Eleman | Şematik | 1. sıra aday (kesin değil) | Kabul aralığı |
|---|---|---|---|
| Giriş | 24,6 V (ana nokta) | 6S batarya | 20–26 V |
| Çıkış | 11 V / 7,5 A | — | — |
| Anahtarlama | 100 kHz, Ton 4,59 µs | — | — |
| L1 | 33 µH el sarım, DCR 7,81 mΩ (HESAP) | Magnetics Kool Mµ 40µ `0077536A7` 22 sarım (2. sıra: satın alma, Würth 74435583300) | **33 µH** (el sarım 30,7–36,1 µH; satın alma ±%20 de geçti); DCR 6,5–15 mΩ (el sarım hedefi 7,5–10 mΩ) |
| Cout | 1000 µF, ESR 35 mΩ | Nichicon UHE1E102MHD6TO *(R/C referansı; kesin parça ≥35 V seçilecek)* | 1000 µF ±%20, ESR ≤ 35 mΩ, **≥ 35 V** (S1 kısa devresinde 27,3–31,1 V) |
| Cd + Rd | **470 µF + seri 0,22 Ω** | — (dondurma sonrası seçilecek) | Cd: 470 µF ±%20, **≥ 35 V**; Rd: 0,22 Ω (Rd + Cd_ESR toplamı **0,15–0,60 Ω**), ≥ 0,25 W |
| Cin | 2 × 1000 µF, ESR 15 mΩ | 2 × TDK B41859D7108M000 *(R/C referansı; kesin parça ≥50 V seçilecek)* | toplam ripple akımı ≥ 4,5 A, **≥ 50 V**; örnek sıcak takma hesabı 48,0 V, gerçek kaynak ve pay doğrulanmadı |
| S1 | Ron 5,6 mΩ | STP100N6F7 | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V |
| D1 | 0,38 V + 8 mΩ | STPS40M60CT (iki bacak paralel) | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V |

LTspice sonucu (24,6 V, 7,5 A): çıkış 11,000 V, ripple 55,7 mV t-t, bobin akımı 6,56–8,44 A, iletim kaybı 2,38 W (Rd kaybı ≈ 1,3 mW); anahtarlama, çekirdek ve kondansatör kayıplarıyla kestirim ≈ 3,24 W (HESAP).
Adayların sırası ve gerekçesi, doğrulama durumu ve kriterlerin nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Kanıt: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

## İş akışı

Sıra (13.11.2026 güncellemesi): **gereksinimleri ve kalan denetimi tamamla → kontrol / sürücü / koruma mimarisini belirle → kontrolcü ve güç katı adaylarını birlikte değerlendir → kullanıcıyla parçaları kesinleştir ve bobini ölç → gerçek değerlerle güç katı ve kapalı çevrimi doğrula → tezgâh → PCB**. Adım numaraları bağımlılıkları anlatır, katı yürütme sırası değildir. 12.11.2026 açık çevrim simülasyon dondurması tarihî bir referans olarak korunur; kapalı çevrim uyumu veya fiziksel doğrulama değildir. Uyum sorunu çıkarsa değişiklik kullanıcı kararıyla ve yeniden doğrulanarak ele alınır.

### Sıradaki iş

Güç katının **simülasyon dondurması (`FROZEN`, §12.1 #1–12)** tamamlandı:
- Çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω`** sönüm dalı eklendi; tarihli koşular ve senaryo bazındaki sonuçları [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) içindedir. 200 ms model setleri ile tek 500 ms köşesi ayrı değerlendirilir; açık çevrim kalkış ve giriş değişimi güvenli regülasyon sağlamaz.
- Gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak belirlendi; dondurma kullanıcı tarafından onaylandı.

1. Kalan kod/hesap denetimini bitir; belirlenen geçici ortam ve genel çıkış hedeflerini gerçek koşullarla doğrula, batarya/kablo ve geçici durum şartlarının açık ayrıntılarını kullanıcıyla belirle.
2. Kontrol yöntemini, üst taraf sürme, frekans ve duty sınırlarını, hafif yük, soft-start, akım sınırı ve bağımsız aşırı gerilim koruması arayüzlerini belirle. Çıktı devre seçimi değil, karşılaştırılabilir gereksinimlerdir.
3. Kontrolcü adaylarının 33 µH, Cout ve Cd–Rd filtresi, CPL yük, S1 kapı yükü ve çalışma köşeleriyle uyumunu değerlendir; uyumsuzluk varsa kullanıcıya sun. 33 µH için deneme sarımı yapılabilir; 22 sarım yalnız belirtilen çekirdeğe ait örnektir.
4. Kullanıcıyla kontrolcü ve güç katı parçalarını tek tek seç; bobin ve parçaları ölç. Gerçek değerlerle güç katı testlerini ve kapalı çevrim kararlılık, kalkış, yük/giriş değişimi ile koruma senaryolarını doğrula. Fiziksel devre ve ölçüm yapılmadan sonuçları ölçüm olarak sunma.

### Mimari ve denetim ara sonucu (13.11.2026)

- **HESAP:** `python buck/hesap.py` yeniden çalıştırıldı. 20–26 V / 7,5 A için hesaplanan iletim süresi yaklaşık 4,36–5,64 µs; 24,6 V noktasında bobin tepe akımı 8,44 A ve çıkış ripple'ı 55,7 mV t-t. Bunlar analitik, belirli varsayımlara dayalı açık çevrim hesaplarıdır; yeni kapalı çevrim kabulünü kanıtlamaz.
- **Arayüzler:** Analog kontrolcü 100 kHz referansı, üst taraf N-MOSFET sürmesi, hafif/yüksüz çalışma, 33 µH ve Cd–Rd dahil çıkış filtresi, sabit güç yükü, yumuşak kalkış ve akım sınırıyla birlikte değerlendirilmelidir. Açık çevrim sönüm sonucu, kapalı çevrim kararlılığı anlamına gelmez. Bootstrap kullanan bir sürücünün hafif yükte beslenmesi de aday düzeyinde kontrol edilmelidir.
- **Koruma:** O1'e enerji verilen noktada 12 V üst sınırı korunmalı; S1 kısa devresinde yalnız PWM'i durdurmak yeterli değildir. Bağımsız koruma için algılama eşiği ve toleransı, tepki süresi, ayırma yolu ve arıza sırasındaki gerilim ayrıca doğrulanmalıdır. Ortak koruma tercihi bu gereksinimi kaldırmaz.
- **Açık sınır:** Cihazların ortak çalışma aralığı 9–12 V'tur; arızada enerji kesilmesi kabul edilir. O1 girişinde 12 V'un aşılmaması gereklidir; aşırı gerilim korumasının tepki süresi ve kapsamı henüz doğrulanmadı. Kullanıcı, her olası yük geçişinde aralığı koruma şartını değil cihazları arızadan korumayı amaçladığını açıkladı; yük basamağı hızı ve arıza kapsamı sayısallaştırılmadı. Motor kaynaklı değişimlerin ayrıntılı incelenmesi kullanıcı isteğiyle şimdilik kapsam dışıdır; bu koşullarda garanti çıkarılmaz.
- **Kod incelemesi:** `kos`, `ton_ayarla`, `darbe_karari`, `kararlilik` ve `zarf` ilgili bölümleri incelendi. Ölçüm eksikliği kontrolü ve kısa darbe sınıflandırması mevcut; `zarf` çıktısının genel sınırlar onaylanmadı ifadesi 13.11.2026 tarihli yeni kararlardan önceki durumu yansıtır. Bu kip açık çevrim olduğu için yeni kapalı çevrim hedeflerine genel GEÇTİ kararı vermez. Kod değiştirilmedi; bu inceleme tüm kodun kapsamlı denetimi değildir, kalan denetim açıktır.
- **13.11 tarihli mimari ara değerlendirme:** Akım/gerilim kipli ve diğer analog kontrol seçenekleri; bağımsız çıkış ayırıcı, giriş ayırıcı, crowbar, TVS ve röle yaklaşımları [OPTIMIZASYON.md mimari notunda](buck/OPTIMIZASYON.md) karşılaştırıldı. İlk incelenecek yön harici S1/D1 ile akım kipli analog kontrol ve bağımsız ortak çıkış ayırıcıydı; bu seçim değildi. 14.11 Type-III testi sonrası gerilim kipi de geçici adaydır (§15). Maliyet ve 12 V koruması gerçek devrelerle doğrulanmadı.
- **Aday araştırması:** Kullanıcı isteğiyle LM5088-2, LT3844 ve alternatif kontrolcüler ile LTC4365 / MAX6495 ailesi ve çeşitli eFuse çözümleri [parça hedeflerinde](buck/PARCA-HEDEFLERI.md) sırasız karşılaştırıldı. Her iki uygun görünen kontrolcü de mevcut modelde bulunmayan akım algılama direnci gerektirebilir; güç katı sönümü ve kayıplar yeniden doğrulanmalıdır. O1 için 12 V altı koruma hızı ve eşik penceresi hiçbir adayda henüz gösterilmedi.
- **13.11 geçici model testleri:** Güç katı değiştirilmeden LT3844 üretici modeli ve örnek PI kontrolü tekrarlandı. LT3844'in 106 kHz/10 mΩ kurulumunda 20–26 V giriş geçişi, 200 ms CPL ve hafif/yüksüz testler geçti; akım eşiğinin alt toleransında akım sınırı marjı kanıtlanmadı. Genel PI örneğinin dokuz ayarı giriş geçişinde 11 V ±%5 bandını aştı; bu tüm gerilim-kipi çözümlerini elemez. 14.11 Type-III RC denemesi [OPTIMIZASYON.md §15](buck/OPTIMIZASYON.md) içindedir. LTC4365 modelinin sert giriş testleri 12 V'u aştı. LM5088 modeli yakınsamadı.
- **13.11 tarihli yöntem önerisi:** Yaklaşık 100 kHz analog tepe akım kipi, harici üst N-MOSFET + asenkron D1, soft-start ve bağımsız ortak-port latch-off OVP idi. 14.11 Type-III gerilim-kipi modeli eklendiğinden bu artık tek yöntem önerisi değildir; iki analog yöntem de geçici adaydır. Gerçek akım algısı, eşikler, OVP, maliyet/verim ve sıcaklık/tolerans kapsamı açık kalır. Ayrıntılar [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §14–15'tedir.
- **Sonraki iş (14.11.2026):** Model düzeyindeki karşılaştırma [OPTIMIZASYON.md §16](buck/OPTIMIZASYON.md) tamamlandı. Kullanıcı, tepe-akım kipini Adım 4–7 arayüz gereksinimlerini hazırlamak için öncelikli yöntem yönü olarak kabul edip etmeyeceğine karar verir; Type-III veya ortalama-akım yöntemini öne almayı da seçebilir. Bu karar parça, kompanzasyon değeri veya şematik onayı değildir. Kalan kod/hesap denetimi açıktır; PCB ve fiziksel prototip kapsam dışıdır.

## Ana aşamalar

Adımlar dört ana aşamada toplanır. **Dal ve milestone yalnız ana aşama düzeyinde açılır**; tek tek adımlar, parça güncellemeleri ve belge düzeltmeleri için açılmaz (yalnız `main`'e commit). Kurallar: [AGENTS.md](AGENTS.md) §4.7.

| Ana aşama | Adımlar | Dal | Milestone | Durum |
|---|---|---|---|---|
| **A — Ana güç devresi** | 0–3 | `ANA-GUC-DEVRESI` (var) | [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) (açık) | 🔄 Sürüyor; parça seçimi kontrol mimarisiyle birlikte değerlendirilecek |
| **B — Kontrol** | 4–7 (sürücü, PWM ve yumuşak kalkış, geri besleme, korumalar) | açılmadı | açılmadı | ⏳ Mimari / arayüz hazırlığı sırada; tasarım yapılmadı |
| **C — Prototip ve ölçüm** | 8 | açılmadı | açılmadı | ⛔ Kullanıcı başlatır |
| **D — PCB ve gerçek yük** | 9–10 | açılmadı | açılmadı | ⛔ Kullanıcı başlatır |

- Bir ana aşamaya başlanırken kullanıcı isterse milestone açılır; aşama kapanırken dal `main`'in o anki hâline getirilir ve milestone kapatılır.
- Dal ve milestone adlarını kullanıcı verir.

## Adımlar

Sıra takvim değildir. Her adımın bir tamamlanma ölçütü vardır; ölçüt sağlanmadan adım "tamam" sayılmaz. Bir sonraki adıma yalnız kullanıcı istediğinde geçilir.

| # | Adım | Durum |
|---|---|---|
| 0 | Gereksinimler ve yükler | ✅ Tamam |
| 1 | Ana güç devresi: değerler ve doğrulama | ✅ Tamam |
| 2 | Gerçek parçaların bulunması | 🔄 Adaylar var; kesin seçim kontrol mimarisiyle birlikte |
| 3 | Kayıp ve ısı; güç katının dondurulması | ⏳ Bekliyor |
| 4 | Kapı sürücüsü | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 5 | PWM üretimi ve yumuşak kalkış | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 6 | Geri besleme ve kompanzasyon | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 7 | Korumalar | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 8 | Tezgâh prototipi ve ölçüm | ⛔ Kapsam dışı |
| 9 | PCB | ⛔ Kapsam dışı |
| 10 | Gerçek yüklerin bağlanması | ⛔ Kapsam dışı |

### 0. Gereksinimler ve yükler — ✅ tamam

- Yükler belirlendi ve üretici belgelerinden doğrulandı: O1 DC girişi 5–12 V / 5 A; S2E 9–28 V, 12 V'ta en çok 0,22 A çalışma ve 1,5 A kalkış, ripple sınırı %3.
- 11 V iki yükün aralığında. Yük zarfı 6,64 A; 7,5 A hedefi yeterli.
- **Açık kalan:** O1'in gerçek tüketimi, kalkış akımı ve mutlak maksimum gerilimi yayımlanmamış (4 / 10 W değerleri tahmindir).
- Çıktı: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §2.

### 1. Ana güç devresi: değerler ve doğrulama — ✅ tamam

- Güç katı değerleri referans yük senaryolarına (sabit güç yükü) göre seçildi ve LTspice'ta sınandı: 5 giriş noktası, yük adımları, yük atma, kalkış, giriş değişimi, örneklenen tolerans köşeleri. Bazı senaryolar sınır dışıdır; aşağıya bakınız.
- Kabul aralıkları: L 33 µH el sarım (DCR 6,5–15 mΩ, hedef 7,5–10 mΩ); Cout 1000 µF ±%20, ESR ≤ 35 mΩ, ≥ 35 V; çıkışa paralel sönüm dalı **Cd 470 µF ±%20 (≥ 35 V) + seri Rd 0,22 Ω** (Rd + Cd_ESR toplamı 0,15–0,60 Ω); Cin ≥ 50 V, ≥ 4,5 A ripple. Örneklenen model setlerinin 200 ms sonuçları ve bir 500 ms köşe senaryosu 9–12 V içinde sönümlü raporlandı ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §4.4, §5, §6, §10).
- Bulunan temel sorunlar: sabit güç yüküyle eski değerler ve dalsız tolerans köşesi salınıyordu (`Cd + Rd` dalıyla kapandı); açık çevrim hafif yükte ve giriş değişiminde 11 V'u tutamıyor; sert kalkışta 61,4 A / 16,6 V.
- Çıktılar: [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc), [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md), [buck/hesap.py](buck/hesap.py), [buck/dogrula.py](buck/dogrula.py).
- **Ölçüt:** belirtilen referans yük ve tolerans senaryolarında 9–12 V, ripple ≤ 165 mV ve 200 ms darbede sönüm aranır. `pencere` 3/3 ve `kararlilik` 27/27 sonuçları yalnız o tabloların sınanan senaryolarına aittir; tüm tolerans kombinasyonları sınanmadı. `secilen` içinde sabit duty ile 57,6 → 6,6 W hafif yüke geçişte 16,07 V görülür; bu senaryo 9–12 V koşulunu sağlamaz ve geri beslemeye devredilir ([OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §5.4).

### 2. Gerçek parçaların bulunması — 🔄 sürüyor (aday listesi hazır, kesin seçim bekliyor)

- **Yapıldı:**
  - Her parça için ölçülebilir kriterler ve nedenleri yazıldı.
  - Kriterlerle dış araştırma yapıldı; adaylar kriterlerle karşılaştırıldı.
  - Dört bobin/kondansatör kombinasyonu LTspice köşe testinden geçirildi. Araştırmanın önerdiği 47 µH + 18 mΩ kombinasyonu **kaldı** (12,83 V, 3 V salınım); 33 µH + 35 mΩ **geçti**.
  - Adaylar öncelik sırasına dizildi; kullanıcı kararıyla liste "olabilir" listesidir, kesin seçim değildir.
  - 1. sıra adayların değerleri ve `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalı şematiğe, `hesap.py` ve `dogrula.py` içine yazıldı; `dogrula.py secilen` yeniden koşuldu: sınanan anma ve tolerans senaryolarında sonuçlar sınırların içinde ve sönümlü (12.11.2026).
  - ST veri sayfaları okundu (STPS40M60C Doc ID 018813 Rev 1; STB100N6F7 DocID027210 Rev 2, STP100N6F7'nin D²PAK kardeşi) ve Magnetics `0077536A7` çekirdek veri sayfası (rev. 6/1/2022) doğrulandı.
  - Çıkış sönümü (`Cd = 470 µF + Rd = 0,22 Ω`) ve gerilim sınıfları (**Cout/Cd ≥ 35 V**, **Cin ≥ 50 V**) kararlaştırıldı.
  - Yeni gerilim sınıflarına (`Cout ≥ 35 V`, `Cd ≥ 35 V`, `Rd 0,22 Ω`, `Cin ≥ 50 V`) ve yardımcı elemanlara (giriş MLCC, ortak soğutucu + TO-220 yalıtım, D1 RC sönümleyici) uygun Türkiye ve yurt dışı stoklu adaylar üretici veri sayfalarından doğrulandı, 5 kondansatör seti geçici LTspice köşe testinden geçirildi (5/5 geçti) ve [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) aday listesine eklendi (şematik 1. sıra değerleri kullanıcı seçim yapana kadar değiştirilmedi, 12.11.2026).
- **Kalan (kullanıcı — dondurma sonrası §12.2):**
  - Dondurulan hedef aralıklara göre kesin parçaların belirlenmesi (`Cout` ve `Cd` ≥ 35 V, `Cin` ≥ 50 V, `Rd` 0,22 Ω dahil; bulunurluk, fiyat, delikli/yüzey montaj tercihi).
  - Kesinleşen parçaların değerlerinin üretici veri sayfasından teyidi; [STP100N6F7 TO-220 veri sayfası](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf) erişilebilir, Nichicon / TDK ESR yayımlamıyor.
  - L1 bobininin sarılması; L1, Cout ve Cd fiziksel ölçümü; soğutucu ve seramik kondansatör parça seçimi ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9.5, §11, §12.2).
  - Gerçek parça ve sarım değerlerinin şematiğe yazılıp testlerin yeniden koşulması.
- **Ölçüt:** tüm güç katı parçaları (`L1`, `Cout`, `Cd`, `Rd`, `Cin`, `S1`, `D1`) **kesinleşmiş**, parça numarası, veri sayfası kaynağı ve kullanılan değerler tabloda; değerler üretici veri sayfasından/ölçümden teyitli; bu değerlerle `dogrula.py secilen` sınırların içinde.

### 3. Kayıp ve ısı; güç katının dondurulması — ⏳ bekliyor (hesap kısmı yapıldı, adım kapanmadı)

- **Yapıldı (12.11.2026, HESAP ve ideal olmayan SİM; ölçüm yok):** kayıp bütçesi (toplam ≈ 2,8–3,4 W, verim ≈ %96,1–96,8), çekirdek kaybı (≈ 0,09–0,14 W, B² varsayımıyla kestirim; üst sınır değil), D1 / S1 / L1 ısıl denge ve soğutucu hedefi (ortak, Rth(s-a) ≤ 12 K/W; D1 soğutucusuz ısıl kaçağa gider), anahtarlama zili duyarlılığı (seramik dekuplaj olmadan D1 ters gerilimi 60 V'u aşabiliyor), sıcak takma ve S1 kısa devre gerilimleri ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9).
- **Kalan:** parçalar kesinleşince yeniden hesap; soğutucu, seramik kondansatör ve sönümleyici parça seçimi; fiziksel ölçümler; dondurma kapısının kapanması (§12).

- Bobin çekirdek kaybı (modelde yok) üretici verisiyle hesaplanır.
- S1 ve D1 eklem sıcaklıkları kayıp ve ısıl dirençten hesaplanır; soğutucu ihtiyacı belirlenir.
- Anahtarlama kaybı için ilk kestirim (gerçek parçanın kapı yükü ve geçiş süreleriyle).
- Sönümleyici (snubber) ve giriş/çıkış seramik kondansatörlerinin gerekip gerekmediğine karar verilir.
- **Ölçüt:** sıcaklık dahil kayıp bütçesi yazılı; güç katı eleman listesi değişmeyecek şekilde kayıtlı.

### 4. Kapı sürücüsü — ⏳ mimari hazırlığı sırada

Şematikteki `PULSE` kaynağının yerini gerçek sürücü alır. Üst taraftaki N-MOSFET için sürme yöntemi (bootstrap), sürücü entegresi, kapı direnci, sürücü beslemesi.
**Ölçüt:** sürücülü simülasyonda verim ve gerilim zorlanmaları Adım 1 sonuçlarıyla karşılaştırılmış.

### 5. PWM üretimi ve yumuşak kalkış — ⏳ mimari hazırlığı sırada

PWM kontrolcü seçimi, frekans ayarı, duty rampası. Sert kalkıştaki 61,4 A / 16,6 V sorununu bu adım kapatır.
**Ölçüt:** kalkışta çıkış 12 V'u aşmıyor; bobin tepe akımı doyma payının içinde.

### 6. Geri besleme ve kompanzasyon — ⏳ mimari hazırlığı sırada

Çıkış gerilimi algılama, hata yükselteci, kompanzasyon. Tasarım verileri: Ton aralığı 2,1–5,6 µs, DCM/CCM geçişi ≈ 0,94 A, ana LC f0 ≈ 0,88 kHz, Cd–Rd köşesi ≈ 1,54 kHz, ESR sıfırı ≥ 4,5 kHz (3. derece çıkış filtresi), yük sabit güç karakterli, yük atma bütçesi ≈ 0,75 V (soğuk ESR'de 3 periyot gecikmeyle 11,76 V). Devredilen şartların tam listesi: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §11; açık çevrim köşe sönümü `Cd + Rd` dalıyla sağlanmıştır, kapalı çevrim faz/kazanç payları bu adımda gösterilmelidir.
**Ölçüt:** 20–26 V ve 0,24–7,5 A referans yük aralığında çıkış belirlenecek 11 V toleransında; genel modül zarfının 0 A dahil gereksinimleri kullanıcıyla ayrıca belirlenip doğrulanmış; O1 girişinde 12 V üst sınırı her koşulda korunuyor; faz ve kazanç payları belgelenmiş.

### 7. Korumalar — ⏳ mimari hazırlığı sırada

Aşırı akım, çıkış aşırı gerilim (anahtar kısa devre kalırsa çıkış giriş gerilimine çıkar; O1 için bağımsız koruma), giriş düşük gerilim, sigorta ve ters polarite, batarya takma anındaki ani akım.
**Ölçüt:** her arıza senaryosu için O1 girişi 12 V altında kaldığı gösterilmiş.

### 8. Tezgâh prototipi ve ölçüm — ⛔ kapsam dışı

Direnç yükle kurulum; kararlı durum, ripple, verim, sıcaklık, kalkış ve yük adımı ölçümleri. Simülasyonla karşılaştırma.
**Ölçüt:** ölçümler belgelenmiş; simülasyondan sapmalar açıklanmış.

### 9. PCB — ⛔ kapsam dışı

Şematik çizimi, yerleşim, tasarım kuralı denetimi. Kurallar: [AGENTS.md](AGENTS.md) "PCB aşaması" bölümü.
**Ölçüt:** elektriksel ve tasarım kuralı denetimleri hatasız; akım yolları ve ısı hesapları belgelenmiş.

### 10. Gerçek yüklerin bağlanması — ⛔ kapsam dışı

Yalnız Adım 6, 7 ve 8 tamamlandıktan ve O1 girişinde 12 V üst sınırı ölçümle gösterildikten sonra.

## Karar günlüğü

Yeni kararlar en üste eklenir. Bir değeri değiştirmeden önce burada ve [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) içinde nedenine bakılır.

| Tarih | Karar | Neden |
|---|---|---|
| 14.11.2026 | Model düzeyindeki yöntem karşılaştırması tamamlandı; sonraki arayüz gereksinimleri adımı için sabit-frekans analog tepe-akım kipi **önerilir**, mimari kararı kullanıcıda kalır | D/F LT3844 makromodeli seçilmiş çizgi/CPL, kalkış, yüksüz ve hızlı yük rampası testlerinde Type-III Ki=200 modelinden daha dar geçiş aralığı verdi; ortalama-akım anahtarlamalı taslağı hafif-yükte başarısız kaldı. Bu sonuçlar global optimumu, fiziksel verimi veya OVP'yi kanıtlamaz. D/F, kontrolcü parçası ve akım-sense ağı seçilmedi; puanlama ve sınırlar [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16 içindedir. |
| 14.11.2026 | Analog tepe akım kontrol ağı için **D** (68 kΩ / 3,3 nF / 22 pF) ve **F** (100 kΩ / 3,3 nF / 22 pF) yalnız model karşılaştırma adayları olarak tutulur; kesin değer/parça seçilmez | 69 kaba FRA birleşimi ve finalist zaman alanı testleri D/F'yi öne çıkardı. Ancak küçük işaret FRA'sı uyarım genliğine duyarlı ve kazanç payı bulunamadı; 9,76 mΩ akım algılama direnci yaklaşık 0,55 W/73 mV ekleyip dondurulmuş güç yolunu değiştiriyor; OVP de 12 V sınırını geçmedi. Kullanıcı tercihi bekleniyor; ayrıntı [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §14 |
| 13.11.2026 | PWM, üst taraf sürme ve yumuşak kalkışı mümkün olduğunca aynı hazır analog kontrolcüyle sağlayan mimari öncelikli değerlendirilecek | Kullanıcı onayı; 100 kHz açık çevrim referansı korunur. Uygunluk, maliyet ve sürme/kalkış koşulları henüz doğrulanmadı; kontrolcü seçilmedi. |
| 13.11.2026 | Çıkışlarda **ortak koruma** tercih edilir; bir cihazdaki arızanın iki cihazın enerjisini kesmesi kabul edilir | Kullanıcı kararı. O1 için bağımsız aşırı gerilim koruması gereksinimi devam eder; ortak korumanın kapsamı ve uygulanması henüz tasarlanmadı. |
| 13.11.2026 | Batarya normal kullanımda kullanıcıya göre yaklaşık **23–25 V**, yoğun kullanımda yaklaşık **21 V** seviyesine iner; **20 V altı ve 26 V üstünde giriş kapatması**, kolay ve düşük maliyetle sağlanabiliyorsa değerlendirilecek | Kullanıcı bilgisi ve tercihi; gerilimler ölçüm kaydı olarak sunulmaz. Eşik toleransları, geçici durum ve yeniden açılma davranışı belirlenmedi; giriş koruması henüz tasarlanmadı. |
| 13.11.2026 | Referans cihazların ortak çalışma aralığı **9–12 V**; arızada cihazların enerjisinin kesilmesi kabul edilir | Kullanıcı açıklaması: amaç her olası yük basamağında gerilimi sürdürmek değil, arızada cihazları korumaktır. O1 girişinde 12 V aşılmamalı; koruma ve arıza kapsamı henüz tasarlanmadı veya doğrulanmadı. İlk kalkışta sıfırdan yükselme ve korumayla kapanma istisnadır. |
| 13.11.2026 | Kapalı çevrim için öncelikle **hazır analog kontrolcü mimarisi** değerlendirilecek | Kullanıcı tercihi: maliyet ve uygulama kolaylığı. Kontrol yöntemi ve parça seçilmedi; mevcut güç katı, yükler ve korumalarla uyum henüz doğrulanmadı. |
| 13.11.2026 | O1 için bağımsız aşırı gerilim koruması mimari gereksinimdir; aşırı akımda kontrolcüde hazırsa otomatik yeniden deneme tercih edilir | Kullanıcı onayı. Aşırı gerilimde elle sıfırlama veya otomatik deneme kararı, güvenlik ve maliyetle birlikte uygun çözümler karşılaştırılınca verilecek; koruma henüz tasarlanmadı veya doğrulanmadı. |
| 13.11.2026 | Genel modülün 0–7,5 A çıkış aralığında dalgalanma hedefi **≤ 165 mV tepeden tepeye** | Kullanıcı onayı; mevcut O1/S2E test ölçütü genel modül için de hedef olarak kabul edildi. Kapalı çevrim ve tüm çalışma koşullarında henüz doğrulanmadı. |
| 13.11.2026 | Kapalı çevrim için geçici kararlı durum çıkış hedefi **11 V ±%5 (10,45–11,55 V)**; maliyet ve uygulama kolaylığı öncelikli, verim de değerlendirilecek | Kullanıcı kararı. Ani geçiş sınırları ve O1 için bağımsız 12 V üst sınırının korunması ayrıca belirlenip doğrulanacak; hedef henüz simülasyon veya ölçümle gösterilmedi. Açık çevrim dondurması değişmedi. |
| 13.11.2026 | Motor kaynaklı giriş değişimlerinin ayrıntılı incelenmesi şimdilik kapsam dışında | Kullanıcı isteği. Motorlar ortak bataryayı paylaşır; oluşturabilecekleri geçici gerilimler ölçülmedi veya doğrulanmadı. 20–26 V test aralığı dışındaki çalışma ve güvenlik bu kararla garanti edilmez. |
| 13.11.2026 | Batarya: **6S16P LiPo, 22,2 V nominal, 25,2 V tam dolu, 39,2 Ah, 870,24 Wh; Daly 6S BMS**. Motorlar ve PDU aynı bataryayı paylaşır. Batarya ile PDU arası en fazla yaklaşık **30 cm** hedefleniyor; şarj sırasında PDU çalışmayacak | Kullanıcı bilgisi; mesafe tek yönlü yerleşim mesafesi olarak ele alınır. BMS model numarası ve eşikleri, kablo kesiti, batarya/kablo empedansı ve ortak yüklerin oluşturduğu geçici gerilimler henüz doğrulanmadı. Mevcut 20–26 V giriş test aralığı değişmedi. |
| 13.11.2026 | PDU kapalı ve kuru bir elektronik bölmesine kurulacak; geçici bölme içi çalışma sıcaklığı hedefi **+5…+50 °C** | Kullanıcı kararı: alt sınır Antalya için yaklaşık tahmin, üst sınır tasarım hedefidir; ikisi de ölçülmedi. Bölme doğrudan güneş görmüyor ve motorlardan ayrı; güneş ve diğer elektronikler bölmeyi ısıtabilir. Gerçek koşullar öğrenilince hedef gözden geçirilecek. |
| 13.11.2026 | Kesin parça seçiminden önce kontrol ve koruma mimarisinin gereksinimleri belirlenir; kontrolcü ile güç katı adayları birlikte değerlendirilir | Kullanıcı isteği: PWM/geri besleme ile L, çıkış filtresi ve MOSFET sürme gereksinimleri birbirine bağlıdır. 12.11 tarihli açık çevrim dondurması ve aday sırası korunur; yeni kapalı çevrim tasarımı veya seçim yapılmadı. |
| 12.11.2026 | Güç katı simülasyon dondurması **FROZEN** olarak onaylandı (§12.1 #1–12 tamamlandı) | Kullanıcı onayı. Sırada §12.2 (dondurulan hedef aralıklara göre kesin parça seçimi, bobin sarımı ve gerçek değerlerle yeniden doğrulama) var |
| 12.11.2026 | Gerilim sınıfları: **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V**. Genel modül için ayrı sınır tanımlanmadı (dondurma O1/S2E uyumluluk ölçütleriyle yapılır) | Kullanıcı kararı. S1 kısa devresinde çıkış 27,3–31,1 V'a çıkıyor (25 V aşılıyor); düşük dirençli kaynakla sıcak takmada Cin 45–46,5 V'a çıkabiliyor (35 V aşılıyor). Kesin parçalar §12.2'de bu sınıflara göre seçilecek |
| 12.11.2026 | Çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω` sönüm dalı** eklendi (`sematik_uret.py`, `hesap.py`, `dogrula.py`, `AGENTS.md` §4.1) | Kullanıcı kararı. Dalsız devrede `L +%20 / Cout −%20 / ESR 15 mΩ` köşesi 200 ms darbede salınıyordu (9,91–12,05 V). Sınanan model setlerinde `Pkritik ≥ 126 W > 82,5 W`, `pencere` 3/3 ve `kararlilik` 27/27 GEÇTİ; `Rd` kaybı 1,3 mW. Diğer ESR ve tolerans kombinasyonları için belirsizlik sürüyor. |
| 12.11.2026 | Sıra: önce simülasyonda dondurma, sonra parça seçimi / bobin sarımı, sonra gerçek değerlerle test, sonra PCB. Dondurma kapısı iki basamağa ayrıldı | Kullanıcı kararı: elde bobin ve parça yok; bobin dondurulan değerlere göre sarılacak. Fiziksel ölçüm dondurmanın ön koşulu sayılmaz |
| 12.11.2026 | Doğrulama düzeltmesi (değer değişmedi): test netlistlerinde anahtar yumuşak geçişli (`Vh=-0.5`); Ton ayarı yeniden yazıldı; yük adımı darbesi 200 ms ve sönüm ölçümü kabul kararına eklendi | Kullanıcı isteği (dondurma hazırlığı). `Vh=0` LTspice'ta ±1 ns titreme ve sahte ripple (70 mV yerine 64 mV) üretiyordu; 20 ms'lik darbe, zaman sabiti ≈ 0,2 s olan büyüyen salınımı kaçırıyordu. Sonuç: tolerans köşesinde 33 µH dahil hepsi **kaldı**; dondurma BLOCKED |
| 12.11.2026 | Şematik: L1 DCR 14,52 → 7,81 mΩ (el sarım, HESAP @20 °C), Ton 4,61 → 4,59 µs. Cout 35 mΩ ve Cin 15 mΩ "maks. empedans, ESR varsayımı" olarak işaretlendi; polimer Cin (VINATech) ve Panasonic FR seçilmedi; STPS40M60CT korundu | Kullanıcı kararı. `secilen` ve `pencere` yeniden koşuldu: 33 µH geçti; 39 ve 47 µH kaldı |
| 12.11.2026 | L1 için 1. sıra el sarım (Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım, ≈ 33,4 µH), 2. sıra satın alma | Kullanıcı kararı (hocanın önerisi: hazır bobinlerin Isat değeri garanti edilmiyor). SİM: DCR 6,5–9,5 mΩ ile köşe testi geçti; 47 µH el sarım kaldı (12,61 V). Şematik DCR değeri ölçüm sonrası kesinleşir |
| 12.11.2026 | L1: 33 µH ve 47 µH iki seçenek olarak kalır; 39 µH kabul edilmez | Kullanıcı kararı. Güncel `pencere`: 39 µH köşede 12,06 V ile kaldı; 47 µH 0,04 V payla geçti ve S2E kalkış süresine (yayımlanmamış, eşik ≈ 32 ms) bağlı |
| 11.11.2026 | Dal ve milestone yalnız ana aşamalarda (A–D) açılır; adımlar ve küçük değişiklikler yalnız `main`'e commit | Kullanıcı kararı: her değişiklikte yeni dal/milestone istenmiyor |
| 11.11.2026 | Parçalar kesin seçim değil, öncelik sıralı aday listesidir; şematik 1. sıra adayların değerlerini taşır (Würth 74435583300, Nichicon UHE1E102MHD6TO, 2 × TDK B41859D7108M000, STP100N6F7, STPS40M60CT) | Kullanıcı kararı. 1. sıra: dış araştırma adayları arasından LTspice köşe testini en geniş payla geçen set |
| 11.11.2026 | Cout için 18 mΩ değil 35 mΩ'luk kondansatör | Veri sayfasındaki 18 ve 35 mΩ değerleri 100 kHz maksimum empedanstır, ESR değildir; gerçek ESR eski dalsız modelin sönüm alt sınırının altına inebilir (47 µH ile 12,83 V) |
| 11.11.2026 | S1 için en düşük dirençli değil en düşük kapı yüklü aday (30 nC) | İletim kaybı zaten 0,15 W; düşük kapı yükü sürücü aşamasını kolaylaştırır |
| 11.11.2026 | Parçayı araç seçmez; kriterler yazılır, kullanıcı bulur ve kesinleştirir | Kullanıcı kararı: önce Türkiye'de kolay bulunan değerler |
| 11.11.2026 | Cout 680 → 1000 µF | 680 µF en kötü tolerans köşesinde 12,06 V; 1000 µF aynı köşede 11,81 V ve daha yaygın değer |
| 11.11.2026 | L1 kabul aralığı 33–47 µH; 22 µH elendi | 22 µH'de tipik yük kesintili iletimde, çıkış 8,78 V'a düşüyor |
| 11.11.2026 | Cout ESR'sine alt sınır kondu (15–35 mΩ) | ESR, LC'nin sönüm direncidir; çok düşük ESR sabit güç yüküyle salınım yaratır |
| 11.11.2026 | Daha büyük L / Cout'a gidilmedi | Giriş değişiminin çıkışa etkisi L/C'den bağımsız; büyük LC geçişi kötüleştiriyor |
| 11.11.2026 | Cout 330 → 680 µF, Cin ve diğerleri aynı | Eski değerler 57,6 W sabit güç yükünde 2,9 V t-t salınıyordu |
| 11.11.2026 | Ana çalışma noktası 22,2 → 24,6 V | Normal çalışma gerilimi; test noktaları 20 / 22,2 / 24,6 / 25,2 / 26 V |
| 11.11.2026 | fsw 100 kHz'de kaldı | Hedefler sağlanıyor; frekans artışının bedeli ideal modelle ölçülemiyor |

## Bu dosya nasıl güncellenir

- Bir adım ilerlediğinde veya bittiğinde: "Şu anki durum" tablosu, adım tablosundaki durum ve ilgili adımın "yapıldı / yapılacak" satırları aynı değişiklikte güncellenir.
- Şematik değeri değiştiğinde: "Şematikteki değerler" tablosu ve karar günlüğü güncellenir.
- "Son güncelleme" tarihi değiştirilir.
- Yeni dal, etiket veya milestone yalnız bir ana aşama açılır/kapanırken ve kullanıcı isteyince oluşturulur; "Ana aşamalar" tablosu o zaman güncellenir.
- Yapılmamış iş "tamam" yazılmaz; koşulmamış test sonucu yazılmaz.
