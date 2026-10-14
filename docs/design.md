# IDA PDU — Tek Ana Kaynak

**Sürüm:** 1.0 • **Tarih:** 2026-10-14 • **Durum:** Mühendislik referansı; prototip ve üretim öncesi doğrulama açık

**Birim sistemi:** SI • **Ondalık ayırıcı:** nokta

> Bu çalışma, 6S bataryadan tek bir 11 V senkron Buck dönüştürücüyle iki korumalı çıkış üretmek için uygulanabilir bir referans tasarımdır. Güç bütçesi gerçek kart ölçümleriyle doğrulanmadığı için tasarım henüz üretime hazır değildir.

## 1. Tasarım kararı

IDA PDU; 20–26 V tasarım giriş aralığında tek LM70880-Q1 tabanlı senkron Buck ile 11.0 V ortak bara üretir. T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E ayrı eFuse korumalı kollara bağlanır. Başlangıç gereksinimi 7 A / 77 W idi. Ön çalışma, 78 W katalog değerlerine dayalı üst planlama zarfını karşılamak için geçici hedefi 7.5 A / 82.5 W olarak ele alır; ölçülmüş yük değildir. Bu hedef, üretici değerlerinden türetilen korumacı fakat doğrulanmamış 78 W eşzamanlı yük varsayımına yaklaşık %5.8 güç marjı verir. 7.5 A değeri doğrulanmış gerçek yük akımı değildir.


## 2. Gereksinimler ve sınırlar

| Öğe | Referans hedef / kaynak değeri | Durum |
|---|---|---|
| Batarya | 6S; nominal 22.2 V; tasarım hesabı 20–26 V | 20–26 V proje varsayımı; gerçek hücre/ESC transient kaydı alınmalı |
| PDU ana çıkışı | 11.0 V, hedef tolerans ±2% | Tasarım hedefi; ölçüm yok |
| Toplam yük bütçesi | 7.5 A sürekli; 82.5 W | Tasarım hedefi; termal/yük profiliyle doğrulanmalı |
| Gemstone O1 giriş | T3 donanım deposunda DC 5–12 V / 5 A | Kapasite/rating; gerçek tüketim veya kalkış akımı değil |
| RPLIDAR S2E giriş | 9–28 V, tipik 12 V; 12 V'ta kalkış tipik 1.2 A, tabloda maks. 1.5 A; çalışma tipik 0.2 A, maks. 0.22 A | Resmî S2E veri sayfası; daha düşük başlatma geriliminde daha fazla akım uyarısı var |
| Topraklama | Ortak GND, izolesiz | Sistem arayüzü varsayımı; Ethernet ekran/toprak bağlantısı incelenmeli |
| Arayüzler | O1 besleme jakı; S2E güç kablosu; Ethernet RJ45/UDP | O1 jak geometrisi/polaritesi ve S2E kablo konnektörünün sipariş kodu doğrulanmalı |
| Çevre | Titreşimli batarya/ESC ortamı | EMC, titreşim, nem ve termal sınıf gereksinimleri tanımlı değil |

**Kaynaklar arasındaki uyumsuzluk:** T3'ün kendi t3gemstone/hardware deposu 5–12 V / 5 A yazarken ArduPilot genel bakış sayfası 5–12 V / 3 A yazıyor. Üretici donanım deposundaki 5 A değeri bu referans bütçesinde üst sınır kabul edilmiştir; kart sürümüne ait üretici etiketi/kılavuzu ve gerçek güç ölçümü olmadan 5 A gerçek tüketim gibi yorumlanmamalıdır.

## 3. Mimari

    6S BAT (20–26 V)
      → giriş sigortası
      → TVS ve ters kutup koruması (parça/koordinasyon testi açık)
      → giriş filtre ve bulk kapasite
      → LM70880-Q1, 400 kHz senkron Buck, 11.0 V
      → 11 V ortak bara (hedef toplam sürekli akım 7.5 A)
           ├─ TPS25982 circuit-breaker eFuse, ayar yaklaşık 6 A → T3 Gemstone O1
           └─ TPS25982 circuit-breaker eFuse, ayar yaklaşık 2.5 A → RPLIDAR S2E
      → ortak GND; S2E Ethernet RJ45/UDP

Çıkış koruma ayarları doğrulanacak başlangıç noktalarıdır. O1 portu için 6.0 A limit, O1'in listelenen 5 A giriş kapasitesinden yüksek olduğu için gerçek çalışma akımı, kablo/konnektör sınırı ve eFuse akım toleransıyla değerlendirilmelidir. S2E için 2.5 A limit, 11 V kalkış ölçümüyle doğrulanmalıdır. İki eFuse ayarı toplam yükü 7.5 A'da sert biçimde sınırlamaz; ana Buck termal/akım sınırı ve yazılı test limiti ayrıca uygulanmalıdır.

## 4. Yük bütçesi

S2E veri sayfasında 12 V'ta ilk kalkış tipik 1.2 A, tabloda azami 1.5 A verilmiştir. S2E'nin düşük başlatma geriliminde daha fazla akım çekebileceği belirtilir. 11 V'a sabit güç dönüşümü yalnızca planlama varsayımıdır.

Korumacı planlama zarfı:

- O1: 12 V × 5 A = 60 W (üretici giriş kapasitesinden türetilen üst zarf; kartın gerçek yükü değil).
- S2E: 12 V × 1.5 A = 18 W (datasheet start-current üst değeri; çalışma akımı tipik 2.4 W).
- Birlikte: 78 W.
- 11 V ortak barada: 78 W / 11 V = 7.091 A.
- 7.5 A / 82.5 W hedefi bu zarfın üzerinde 4.5 W veya %5.8 marj bırakır.

Bu hesapta O1 5 A ve S2E 1.5 A'nın eşzamanlı gerçek ölçüm olduğu iddia edilmez. S2E 1.5 A değeri 12 V için verilmiştir; 11 V kalkışı ölçülmelidir. Prototip öncesi iki cihazın ayrı ayrı ve eşzamanlı giriş akımı, kalkış dalga şekli, minimum bataryada ve en ağır yazılım/çevre birimlerinde ölçülmelidir.

## 5. Topoloji seçimi

| Topoloji | Karar | Gerekçe |
|---|---|---|
| Senkron Buck | Seçildi | 20–26 V'tan 11 V'a düşürme, yaklaşık 80 W, yüksek verim ve düşük doğrusal eleman kaybı; ortak GND kabul ediliyor |
| Asenkron Buck | Elendi | Diyot kaybı yaklaşık (1−D) × 0.5 V × 7.5 A ≈ 1.7–2.2 W; ısı ve verim cezası |
| Boost | Elendi | Giriş hedef çıkıştan yüksek; gerekli dönüşüm yönünün tersi |
| Buck-Boost | Elendi | Giriş aralığında 11 V'un altına düşme yok; fazladan anahtar/kontrol kaybı ve maliyet |
| Flyback/forward | Elendi | İzolasyon gereksinimi yok; 80 W civarında manyetik tasarım ve EMI karmaşıklığı gereksiz |

## 6. Ana Buck seçimi ve alternatifler

| Aday | Üretici sınırı | Karar |
|---|---|---|
| TI LM70880-Q1 | 4.5–80 V, 8 A, 200 kHz–2.2 MHz; ayarlanabilir çıkış; 29-pin 6×6 mm VQFN | Ön referans. 6S transientleri için 36 V sınıfı çözümlerden fazla giriş payı; 8 A sınıfı |
| TI LM61495 | 3–36 V, 10 A; 42 V abs max yalnızca sınırlı transient koşulunda | ESC/batarya transienti ölçülmeden 36 V çalışma sınırı dar; 80 V aday tercih edildi |
| ADI LT8645S | 3.4–65 V, 8 A | Düşük EMI adayı; 8 A sınırı ve maliyet/tedarik karşılaştırması gerekir |
| TI LM5146-Q1 | 5.5–100 V kontrolcü; harici MOSFET | Daha yüksek transient ihtiyacında seçenek; güç elemanı ve sürücü tasarım yükü daha yüksek |

LM70880-Q1 içindeki anahtarlar entegredir. TI'nin yayımladığı 48 V giriş, 12 V/8 A, 400 kHz örneği yalnızca başlangıç devresi ve yerleşim için referanstır. Oradaki %95.6 verim IDA PDU verimi değildir. IDA PDU çalışma aralığı, 11 V çıkış, batarya empedansı ve PCB ısıl koşulları farklıdır.

## 7. İlk boyutlandırma

### 7.1 Duty ve giriş akımı

İdeal duty: D = Vout / Vin. Pout = 11 V × 7.5 A = 82.5 W. Iin = Pout/(Vin×η); verim %90–95 hesap senaryosudur, ölçüm veya IDA PDU simülasyon sonucu değildir.

| Vin | D (ideal) | Iin @ η=95% | Iin @ η=90% |
|---:|---:|---:|---:|
| 20.0 V | 0.550 | 4.342 A | 4.583 A |
| 22.2 V | 0.495 | 3.912 A | 4.129 A |
| 25.2 V | 0.437 | 3.446 A | 3.638 A |
| 26.0 V | 0.423 | 3.340 A | 3.526 A |

Batarya, kablo, sigorta ve konnektör hesabında yalnızca nominal 22.2 V kullanılmamalı; 20 V ve transient testi dahil edilmelidir.

### 7.2 Endüktör

Ön seçim L = 6.8 µH, fs = 400 kHz. ΔIL = Vout × (1−D)/(L×fs).

| Vin | ΔIL p-p | 7.5 A yükte hesaplanan tepe akım |
|---:|---:|---:|
| 20.0 V | 1.82 A | 8.41 A |
| 22.2 V | 2.04 A | 8.52 A |
| 25.2 V | 2.28 A | 8.64 A |
| 26.0 V | 2.33 A | 8.67 A |

TI'nin örnek tasarım BOM'unda Coilcraft XGL1010-682MEC, 6.8 µH, tipik 6.2 mΩ DCR ve 16 A katalog akım sınıfı listelenmiştir. Doyum/ısınma akım eğrisi, parça datasheet'i ve bakır sıcaklığı üzerinden ayrıca kontrol edilmeli. 7.5 A DC'de yalnızca DCR tahmini I²R ≈ 0.35 W; AC bakır ve çekirdek kayıpları dahil değildir.

### 7.3 Çıkış ayarı ve filtre

LM70880-Q1 FB referansı 0.8 V. Vout = 0.8 × (1 + Rtop/Rbottom). 130 kΩ / 10.2 kΩ için hesaplanan hedef 10.996 V. Bu ideal direnç hesabıdır; gerçek tolerans, bias akımı, yük regülasyonu ve transient ölçümü kapsam dışı.

Başlangıç değerleri:

- CIN: TI örneğinden 4 × 4.7 µF, 100 V X7S seramik; yerel yüksek frekans bypass ve kaynağa bağlı bulk kapasite ayrıca seçilecek.
- COUT: TI örneğinden 4 × 22 µF, 25 V X7R seramik; 11 V DC-bias altında etkin kapasite üretici eğrisinden kontrol edilecek. 6 adet 22 µF ile başlamak olasıdır fakat kararlılık/yerleşim kontrolü olmadan net değer değildir.
- L1: 6.8 µH, XGL1010-682MEC aday.
- CBOOT: 47 nF; CVCC: 4.7 µF; CVDDA: 0.1 µF; RT: 54.9 kΩ yaklaşık 400 kHz — TI tasarım referansı.
- Geri besleme kompanzasyonu: TI'nin ilgili 8 A örnek değerleri yalnızca başlangıç noktası; 11 V, gerçek Ceff, yük profili ve parazitiklerle yeniden hesaplanmalı.
- Akım algılama: 5 mΩ düşük endüktanslı şönt, Kelvin hatları; TI örnek topolojisi. 56 mV eşiğe göre ideal nominal tepe eşik hesabı 11.2 A. Nihai limit, indüktör tepe akımı ve anahtar termaliyle incelenmeli.

Seramik kondansatörün üzerindeki nominal toplam kapasite DC bias altında geçerli olmayabilir. Üretici DC-bias eğrisi olmadan ripple hesabı tam nominal kapasite kabulüyle sonuçlandırılamaz.

## 8. Koruma ve arayüz

| Bölüm | Referans çözüm | Açık doğrulama |
|---|---|---|
| Batarya giriş sigortası | 10 A sınıfı, DC ve kesme kapasitesi uygun, bataryaya yakın | MPN, gecikme eğrisi, batarya kısa devre akımı ve kablo koordinasyonu |
| Giriş TVS | Littelfuse SMCJ33A: 33 V standoff, katalogdaki 28.2 A testinde 53.3 V max clamp | ESC transient enerjisi/akımı, gerçek clamp, sigorta ve koruma IC koordinasyonu |
| Ters kutup | 100 V sınıfı yüksek taraf ters-polarite/ideal-diode devresi | Tam topoloji/MPN açık; 65 V kontrolcü ancak clamp üst sınırı doğrulanınca kullanılabilir |
| Port eFuse | TI TPS259824ONRGET: 2.7–24 V, 15 A class, 2.7 mΩ typical; circuit-breaker option, 16.9 V input OVP variant | Full-temperature limit accuracy, breaker timer, thermal layout, reset/fault, stock |
| O1 port | Yaklaşık 6 A eFuse nominal ayarı ilk deneme | Gerçek akım, kart sürümü, jak polaritesi/ölçüsü, kablo ve konnektör |
| S2E port | Yaklaşık 2.5 A eFuse nominal ayarı ilk deneme | 11 V start current, güç kablosu pinleri ve akım kapasitesi |
| Ethernet | RJ45, 10/100 Ethernet ve UDP cihaz arayüzü | Besleme dönüşü ve Ethernet ekranı topraklaması sistem seviyesinde |

TPS25982 veri sayfası akım limit bağıntısı RILIM[Ω] = 1460/(ILIM[A]−0.11): 6.0 A için yaklaşık 248 Ω (249 Ω E96 başlangıç), 2.5 A için yaklaşık 611 Ω (604 Ω E96 başlangıç). Bu eşdeğer nominal ayardır; full-temperature eFuse threshold range ve circuit-breaker timer ayrıca kontrol edilmeli. TPS259824ONRGET varyantının 16.9 V OVP girişi, 11 V rail için uygundur. Port akımı, kapasitif inrush ve kalkış zamanlaması cihaz başına ölçülmeden son değer seçilmemeli.

Konnektör üretici/modeli uydurulmamıştır. O1 DC jakının dış/iç çapı, kutup polaritesi, mekanik kilitleme ve kablo türü; S2E dört pin güç konnektörünün üretici numarası doğrulanmalı. Datasheet pin tablosu S2E pin 1 VCC, pin 2 GND, pin 3/4 bağlantısız der.

## 9. PCB yerleşim ve üretim

Ön öneri 4 katmanlı karttır: üst katmanda güç elemanları ve kısa anahtarlama döngüsü; bitişik kesintisiz GND referans katmanı; iç katmanlarda güç/geri dönüş dağıtımı; altta sinyal ve yardımcı bakır. Giriş seramikleri VIN/PGND güç pinlerine çok yakın, SW alanı küçük, FB/COMP/ISNS Kelvin yönlendirmeleri gürültülü düğümlerden uzakta olmalı. eFuse ve konnektör hatları için iz genişliği ve bakır sıcaklık artışı hesaplanmalı; via sayısı termal akım yoluna göre seçilmeli.

Bu bir katman yığını siparişi veya bitmiş PCB değildir. 2 oz dış bakır önerisi üretici fiyat/kurallarına göre doğrulanacak. Paket yalnızca işlevsel blok diyagramı içeren bir KiCad .kicad_sch dosyası taşır; devre sembolleri ve netlist yoktur. Elektriksel şema ve PCB çizilmedi; ERC/DRC çalıştırılmadı.

## 10. Ön BOM ve maliyet durumu

| Ref | Aday / MPN | Adet | Fiyat bilgisi (2026-10-14 erişimi) | Durum |
|---|---|---:|---|---|
| U1 | TI LM70880QRRXRQ1 | 1 | DigiKey ABD: 1 adet $8.17; 10 adet $6.326/adet; vergi/taşıma/ithalat hariç | Yerel teslim maliyeti değil |
| L1 | Coilcraft XGL1010-682MEC | 1 | Teklif gerekli | TI tasarım BOM'unda listelenen aday |
| U2,U3 | TI TPS259824ONRGET | 2 | Mouser ABD: $4.67/adet tekli fiyat görünümü; vergi/taşıma hariç; stok sipariş öncesi doğrulanmalı | 15 A sınıfı circuit-breaker eFuse; 16.9 V OVP variant; iki port akım limiti ayrı ayarlanır |
| D1 | Littelfuse SMCJ33A | 1 | Mouser TR: €0.662 tekli sayfa fiyatı; vergi/taşıma hariç | Surge testi öncesi aday |
| Pasifler | TI uygulama sınıfı, nihai değerler hesapla | Set | Teklif gerekli | DC bias/tolerans/gerilim sınıfı açık |
| F1 | 10 A DC sigorta ve tutucu | 1 | Seçilen eğri ve yerel fiyat gerekli | MPN açık |
| Q1 | Ters kutup koruma FET/denetleyici | 1 set | MPN ve fiyat açık | Surge koordinasyonu kapanınca seçilecek |
| J1,J2 | Güç konnektörleri/kablolar | 2 set | Eşleşme doğrulanınca teklif | MPN açık |
| PCB+montaj | 4 kat, dış bakır hedefi 2 oz | 1 | Gerber ve BOM ile üretici teklifi gerekli | Tasarım dosyası yok |

Bu snapshot tam maliyet hesabı değildir. Fiyatı görülen üç ana kalemin kısmi subtotalı U1 + iki eFuse için $17.51 USD ve TVS için €0.662'dir; iki para birimi tek toplam değildir. Türkiye teslim fiyatları, PCB, montaj, kablo ve gümrük kalemleri teklif gerektirir. Brief'teki 5000–7000 TL hedef bütçesi doğrulanmış değildir; bu yabancı satıcı fiyatlarını kur/vergi eklemeden TL toplamına katmayın.

## 11. Riskler ve doğrulama kapıları

| ID | Risk | Etki | Kapatma ölçütü |
|---|---|---|---|
| R1 | O1 kaynaklarında 3 A ve 5 A rating çelişkisi; tüketim bilinmiyor | PDU yetersiz veya aşırı boyutlu olabilir | Board etiketi/üretici yanıtı ve ağır yazılımda akım ölçümü |
| R2 | S2E 11 V başlatma akımı 12 V tablosundan farklı | eFuse trip veya bus droop | 9/10/11/12 V start ve eşzamanlı yük testi |
| R3 | ESC transient belirsiz | U1, TVS veya reverse guard hasarı | Giriş waveform/enerji ölçümü ve coordinated clamp hesabı |
| R4 | 8 A sınıfı dönüştürücü termali | Isıl kapanma/ömür kısalması | En düşük Vin/tam yükte termal denge ve derating |
| R5 | Ceff/kompanzasyon varsayımı | Regülasyon/ringing/kararsızlık | DC-bias eğrisi, üretici model, load transient ve bench loop kontrolü |
| R6 | Konnektör/polarite/kablo tanımsız | Yanlış kablolama veya düşük uç gerilimi | Kart sürümü, kablo eşlemesi ve akımda uç voltajı |
| R7 | eFuse toleransı/ısı | Erken açma veya sıcak çalışma | Eşik ve RDS(on) sıcaklığını port başına ölç |
| R8 | KiCad/PCB henüz üretilmemiş | Üretim mümkün değil | IDA PDU şema, footprint, ERC/DRC ve Gerber kontrolü |

1. **Gereksinim:** O1 kart sürümü, giriş ratingi, jak polaritesi, kablo uzunluğu, ESC transienti ve ortam sıcaklığını dondur.
2. **Yük:** Her cihazın ayrı ve eşzamanlı kalkış/steady akımını en az 100 kS/s kayıtla ölç.
3. **Elektrik:** 20/22.2/26 V giriş; boş/yarım/tam yük ve load step; PDU/cihaz uçlarında 11 V ±2%, ripple, overshoot.
4. **Koruma:** Ters kutup, giriş/port kısa devre, eFuse limit/latch, surge ve brownout.
5. **Termal/EMC:** En kötü giriş/yük ve sıcak ortamda termal denge; kablo, Ethernet, radyo ve sensör etkisi.
6. **Üretim:** Şema/PCB, ERC/DRC, footprint/MPN, Gerber ve ilk kart bring-up.

Ölçüm raporu olmadan verim, termal güvenlik, EMC geçişi veya saha güvenliği iddia edilmemelidir. Hedefler ve sonuçlar ayrı tutulur.

## 12. Kaynaklar

- T3 Gemstone resmi donanım deposu, O1 güç tablosu: https://github.com/t3gemstone/hardware
- T3 Gemstone O1 dokümanı: https://docs.t3gemstone.org/en/boards/o1/introduction
- ArduPilot Gemstone O1 overview (3 A çelişkisi): https://ardupilot.org/dev/docs/common-t3-gem-o1-overview.html
- SLAMTEC RPLIDAR S2E datasheet v1.8: https://wiki.slamtec.com/download/attachments/83066883/SLAMTEC_rplidar_datasheet_S2E_v1.8_en.pdf?api=v2
- TI LM70880-Q1 product/datasheet: https://www.ti.com/product/LM70880-Q1 • https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf
- TI LM708x0-Q1 application examples: https://www.ti.com/lit/ds/symlink/lm70840-q1.pdf
- DigiKey LM70880QRRXRQ1 pricing/supply: https://www.digikey.com/en/products/detail/texas-instruments/LM70880QRRXRQ1/24420927
- TI LM61495: https://www.ti.com/product/LM61495
- ADI LT8645S datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/8645sf.pdf
- TI LM5146-Q1: https://www.ti.com/product/LM5146-Q1
- TI TPS25982 datasheet (D sürümü, May 2026): https://www.ti.com/lit/ds/symlink/tps25982.pdf
- Mouser TPS259824ONRGET price page: https://www.mouser.com/en/ProductDetail/Texas-Instruments/TPS259824ONRGET
- Littelfuse SMCJ33A: https://www.littelfuse.com/assetdocs/littelfuse-tvs-diode-smcj-datasheet?assetguid=8a337998-7c2c-4b8a-8c6d-8f2b6c5d3d8e
- Mouser TR SMCJ33A price page: https://www.mouser.com.tr/ProductDetail/Littelfuse/SMCJ33A

## 13. Olgunluk

Mimari ve hesap referansı. Elektriksel KiCad şeması/PCB, üretici SPICE makromodeliyle doğrulama, laboratuvar testi, tam maliyet teklifi ve fiziksel konnektör eşleşmesi yok. Bu belge prototip veya üretim sonucu iddia etmez.
