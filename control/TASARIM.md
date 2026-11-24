# Dijital kontrol ve doğrulama

## Model ve veri kaynakları

Güç katının kaynağı `6879e87` commit’indeki [LTspice ASC](../buck/ltspice/buck_guc_kati.asc), [analitik hesap](../buck/hesap.py) ve [LTspice koşu üreticisi](../buck/dogrula.py). Özgün S1 ve D1 tanımları korunur. ngspice devresi için `Vfwd` ve `Ron` davranışı açık bir denklemle çevrilir. Nominal 24,6 V, 1,4667 Ω koşusu 11,0005 V, 55,68 mV t-t ve 6,560–8,441 A verir. Tarihî LTspice kaydı 11,000 V, 55,7 mV t-t ve 6,56–8,44 A’dır. Bunlar simülasyon sonuçlarıdır.

Hesapta `[iL, vCout, vCd]` kullanılır. Çıkış düğümü `iL = iLoad + (vo-vCo)/ESR + (vo-vCd)/Rd` ile çözülür. Sabit güç yükünün artımlı iletkenliği `-P/Vo²`, sabit akımın sıfır, dirençli yükün pozitiftir. İndüktör düşümüne DCR ve anahtar/diyotun duty ağırlıklı iletim direnci eklenir. Bu CCM modeli güç katının 3. derecesini korur. Matris üssüyle bir periyotluk sıfırıncı derece tutucu ve periyot içi örnekleme oluşturulur. Bir sonraki PWM güncellemesi için açık `z^-1` eklenir. Hesap yük ve giriş köşelerini kapsar. DCM ve arıza davranışı anahtarlamalı modele aittir.

## Kontrol mimarileri

| Aday | Karar |
|---|---|
| PI, giriş feedforward’lu PI | Kararlı CCM ayarı LC kutup çiftinin altına kalıyor. Giriş feedforward giriş adımını telafi ediyor, tek başına yeterli yük adımı sönümü sağlamıyor. |
| Filtreli PI / Type II / 2P2Z | Hızlı bir CCM ayarı, köşe marjlarından ödün veriyor. Sınanan ayarda PI ailesine yakın kalıyor. Akım modunun indirgenmiş dış gerilim döngüsünde daha uygun. |
| Giriş feedforward’lu Type III / 3P3Z | İlk hedef. İki sıfır LC çiftine faz desteği, yüksek frekans kutupları kazanç düşümü sağlar. Ön filtre ve Tustin PI kullanılarak doyum takibi doğrudan integratöre verilir. Büyük gerilim düşmesinde akım desteği ve hafif yükte darbe atlama eklenir. |
| Ölçülen akım + gerilim kaskadı | Test edilen çift PI’nin dış döngü kazanç marjı bazı köşelerde geri besleme kazancı ters yönde değiştiğinde dar. CCM sonuçları ve ortak yük senaryosunda alınan kilitlenmeler ilk mimariye göre avantaj göstermedi. Hafif yükte sabit zamanlı akım örneğinin DCM darbesini kaçırması için darbe alanı kestirimi denendi. |
| Donanım tepe akım modu | G474 DAC rampası + COMP + HRTIM EEV ile aday. 20 V’ta anma duty yaklaşık %56,4. Nominal eşikler için ayrık akım eşlemesinde `ma > (m2 − m1) / 2`. 20 V, 11 V, L minimum köşesinde yaklaşık 0,06 A/µs, 11,7 V civarında yaklaşık 0,09 A/µs. Başlangıç tasarım denemesi 0,25 A/µs, periyotta 2,5 A eşdeğer rampadır. Akım algısı ve rampanın eşiğe etkisi yeniden tasarım gerektirir. Bu adayın PDU’ya özgü çevrimi henüz çalıştırılmadı. |
| Bir çevrimde öngörülü kontrol ve histeretik/COT | Çalışma zarfı boyunca L, ESR, filtre sapması ve örnekleme zamanına duyarlılık ile değişken frekans/EMI yükü getirir. Kullanılan sabit frekanslı aday ihtiyaçları karşıladığında önceliği düşüktür. Akıma bağlı büyük sinyal desteği araştırma değerlendirmesine dahil edilmiştir. |

`python -m control.design --optimize` sabit tohumlu diferansiyel evrimle CCM marjlarını ve kesim frekansını birlikte iyileştirir. `python -m control.design` kayıtlı katsayıları yeniden değerlendirir. Tustin katsayıları CMake derlemesinde üretilir. Açık çevrim marjları dengedeki doğrusal kısım içindir. Doyum, akım desteği ve darbe atlama ayrı senaryolarda sınanır. Büyük-sinyal desteği Type III adayının bir parçasıdır. A/B koşusu aynı giriş ve yük uyarısını beş adaya uygular.

PDU G474 adayını Cortex-M4F, ADC tetikleme, HRTIM zaman çözünürlüğü ve bağımsız fault yollarıyla prototip hedefi olarak kullanır. Uygun pinler ve bağımsız koruma gereksinimi sağlanırsa G431/G473 gibi gelişmiş timer’lı alternatifler ve F334 HRTIM değerlendirilebilir. G47x’in hızlı DAC rampası ve HRTIM EEV hattı peak-current denemesi için alan bırakır. X-CUBE-DPOWER örnekleri, FMAC ve NuttX örneği zamanlama ve çevrebirim referansıdır. Katsayı üretimi, test ve derleme Python, CMake ve GNU Arm ile tekrarlanabilir. X-CUBE-DPOWER’ın CubeMX ve WDS odaklı, CCM ağırlıklı yapılandırması bu iş akışının parçası değildir.

- [ST AN5496, buck gerilim modu](https://www.st.com/resource/en/application_note/dm00706301.pdf)
- [ST AN5497, buck tepe akım modu](https://www.st.com/resource/en/application_note/dm00706304-buck-current-mode-with-the-bg474edpow1-discovery-kit-stmicroelectronics.pdf)
- [ST AN5788, STM32 PID ve IIR](https://www.st.com/resource/en/application_note/an5788-stm32-digital-power-pid-and-iir-filters-for-smps-control-design-and-comparison-on-bg414edpow1-discovery-kit-stmicroelectronics.pdf)
- [Microchip, 2P2Z ve 3P3Z](https://developerhelp.microchip.com/xwiki/bin/view/applications/power/switching-regulators-/digital-compensator-design-tool/type-selection/)
- [TI SPRABE7A, sayısal tepe akım ve slope compensation](https://www.ti.com/lit/an/sprabe7a/sprabe7a.pdf)
- [Peterchev ve Sanders, DPWM çözünürlüğü ve limit cycle](https://power.eecs.berkeley.edu/publications/peterch_03.pdf)
- [ST X-CUBE-DPOWER](https://www.st.com/en/embedded-software/x-cube-dpower.html)
- [Apache NuttX, B-G474E-DPOW1 açık kaynak SMPS sürücüsü](https://apache.googlesource.com/nuttx/%2B/0efe8c4f42e5b5f982d7644fe9dc90afb8f67a31/boards/arm/stm32/b-g474e-dpow1/src/stm32_smps.c)

## Sayısal zamanlama ve model sınırları

170 MHz HRTIM ×32 ile 54 400 tick/periyot, nominal tick yaklaşık 184 ps. 0 darbe, 150 ns minimum etkin darbe ve %75 maksimum duty. Giriş 12 bit 0–32 V, çıkış 0–16 V, akım 0–16 A eşdeğerinde kuantalanır. ADC tetik nominal 7,1 µs; üç dönüşüm için hedef 1,4 µs. Komut yazımı en geç 9,6 µs, sonraki periyotta preload güncellemesi. CPU hesap bütçesi ve öncelik yükü DWT ile ölçülecek. Üç kayıp ADC çevriminde yazılım kilidi, ilerleme yoksa ayrı IWDG reseti var. Firmware ve simülasyon aynı C kontrol fonksiyonunu çalıştırır.

Anahtarlamalı model açık/kapalı durumları, diyot akımının sıfırda kesilmesini, PWM/ADC çözünürlüğünü, gürültüyü, ADC ve kontrol süresini, gate kenar gecikmelerini, kısa devre ve aşırı gerilim yollarını içerir. ngspice darbeleri tekrar sürerek ayrı devre integrasyonu yapar. C modelinin ikinci dereceden integrasyonu 100 ns ve 50 ns adım karşılaştırmasıyla sınanır. Röle, ADC aperture, doyum, layout parazitikleri, gerçek driver/referans toleransları, kaynak empedansı ve EMI için parça ve tezgâh kanıtı gerekiyor. Anahtarlama kaybı `Vin × Ipeak × (tr+tf) × fs / 2` yaklaşımıdır. Çekirdek, ters diyot kapasitansı, MCU beslemesi, sürücü ve yardımcı devre kayıpları bu verimden hariçtir. `results.json` içinde tahmini verim ve kayıp ayrı kalemlerdir.

- [STM32G474 veri sayfası](https://www.st.com/resource/en/datasheet/stm32g474pb.pdf)
- [RM0440, STM32G4 çevrebirimleri](https://www.st.com/resource/en/reference_manual/dm00355726.pdf)
- [AN4539, HRTIM cookbook](https://www.st.com/resource/en/application_note/DM00121475.pdf)
- [AN5346, STM32G4 ADC tasarımı](https://www.st.com/content/st_com/en/technical-documents/an5346-stm32g4-adc-use-tips-and-recommendations-stmicroelectronics.html)
- [STM32G4x4 hata listesi ES0430](https://www.st.com/en/microcontrollers-microprocessors/stm32g4x4/documentation.html)

## Donanım arayüzü ve arıza bütçeleri

G474 hedefi PA0/PA1/PA2 üzerinden bobin akımı, Vout ve Vin okur. PA8 TA1 çıkışı için adaydır. Sayısal ölçeğe karşı nominal bölücüler Vin için 26,1 kΩ/3,00 kΩ ve Vout için 10,0 kΩ/2,60 kΩ. Tolerans ve ADC giriş yerleşmesi için düşük empedanslı tampon, ratiometrik referans takibi ve iki noktalı kalibrasyon gerekir. Ölçüm doyumu ve ADC duruşu yazılımda ele alınır. İç aralıkta takılı gerilim örneği için bağımsız OVP devrede kalır.

Hesaplanan `4,12 mΩ × 50 V/V` akım arayüzü 206 mV/A ve 7,5 A’da yaklaşık 0,232 W şönt kaybı getirir. Şöntten Kelvin algılama, bobin ve çıkış kapasitörleri arasında. INA293A2 bant genişliği ve ortak mod aralığı açısından aday. Ayrı hızlı karşılaştırıcı eşiği ve HRTIM EEV1, CPU devre dışıyken darbenin sonlandırılması içindir. Duyarlı güç düğümlerinin tezgâh ölçümü ile 0,65 µs bütçe kapanır. OVP, ADC bölücüsünden ayrı 37,4 kΩ/10,0 kΩ bölücü, 2,5 V referans ve ayrı beslenen latch ile FLT1, gate driver inhibit ve enerji kesme komutuna gider. EEV1/FLT1 pin ataması ve analog güç kaybı durumundaki fail-off doğrulanacak. `python -m control.interface` kabul edilen parça tolerans hedeflerinden OCP 9,61–9,99 A, OVP 11,775–11,926 V ve kısa devre tavanı 10,72 A hesaplar. Bunlar devre toleransı bütçeleridir.

Sürücü adayları UCC27282 ve LTC7001. Bootstrap şarjı hesapta 45 nC ve 330 nF etkin kapasitansla çevrim başına yaklaşık 0,14 V düşer. %75 duty sınırı 2,5 µs minimum off süresi bırakır. Asenkron çıkışta uzun darbe atlama, ön gerilim ve boş yükte anahtar düğümü bootstrap’ı yenilemeyebilir. LTC7001’in charge pump’ı başlangıcı destekler. 100 kHz’de 4,5 mA ortalama gate yükü, bootstrap diyodu/harici şarj yolu ve driver ısısı ayrıca ölçülmelidir. Hızlı sürücü beslemesi için 10–12 V sınıfı yerel yardımcı kaynak, MCU/ADC için filtrelenmiş 3,3 V ve gate pull-down. UVLO ve harici arming, MCU reset ve kendi besleme arızasında gate’i kapalı tutmalı.

PWM duruşu, S1 drain-source kısa devresinde kaynak enerjisini kesmez. Aktif giriş ayırıcı Cin ile S1 arasına yerleştirilmeli veya Cin’in kalan enerjisi ayrıca hesaba katılmalı. Model köşesinde PWM üzerinden OVP, S1 kısa devresinde 12 V’u tutamıyor. 2 µs ideal giriş ayırmada dahi indüktör enerjisi yük düğümünde sınırı aşabiliyor. Bağımsız çıkış kesme veya klemp, ters akım bloklama, sigorta ve MOSFET SOA, kablo sıcak takma ve çıkış kısa devresinde kondansatör boşalma yolu tasarlanıp ölçülmeden hassas yük bağlantısına geçilmez. 11 V’ta Cout+Cd’de yaklaşık 89 mJ depolanır. Sürekli CPL yükü 82,5 W olup 8 V’ta 10,3 A isteyebilir. Bununla başlatma modelde koruma ile kesilir. Gecikmeli yük etkinleştirme / power-good veya yükün kendi UVLO ve akım rampası gerekir.

Firmwarenin tezgâh imajında TA1 donanımsal olarak susturulur, PA8 GPIO-low kalır ve SWD üzerinden istenen duty/timing okunur. Enerjili firmware arming için fiziksel kat doğrulaması, OCP/OVP, güç iyi, bağımsız watchdog ve arıza kilidi bağlanmalıdır.

- [TI INA293](https://www.ti.com/lit/ds/symlink/ina293.pdf)
- [TI TLV3501 ve TLV3201 karşılaştırıcı](https://www.ti.com/lit/ds/symlink/tlv3501.pdf)
- [TI UCC27282](https://www.ti.com/lit/ds/symlink/ucc27282.pdf)
- [ADI LTC7001](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc7001.pdf)
- [TI TPS2663, giriş eFuse aday sınıfı](https://www.ti.com/lit/ds/symlink/tps2663.pdf)

Teknik uygunluk ve Türkiye’den temin için üretici sipariş kodu üzerinden yeniden fiyat, stok, teslim ve kılıf sorgusu yapılır. Yukarıdaki parçalar ilk laboratuvar adaylarıdır.
