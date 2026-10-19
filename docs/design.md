# IDA PDU — Teknik tasarım notları

>19 Ekim2026 son durumu: [PROJECT-STATE](PROJECT-STATE.md) ve [kontrol listesi](REVIEW-CHECKLIST.md). Kesin RFB MPN'leri işlendi; RIMON1/2=806 Ω; COUT1–8=TDK22 µF100 V2220. Son DRC197 unrouted/301 uyarı,48 koşu512 geçen/2 O1 başarısız. Aşağıdaki eski hesap bölümleri kendi tarih/varsayımıyla korunur;25 V COUT,2,61k/4,99k IMON,299 uyarı ve “footprint yok” kayıtları güncel seçim sayılmaz. Gerçek döngü kararlılığı hâlâ açık.

## 2026-10-19 PCB güncellemesi

Son şema/netclass teslimi: `docs/SON-TESLIM.md`. Şema okunurluğu düzenlendi, nominal bağlantılar korundu;46 ağın tümüne sınıf atandı. Hesap için35µm nominal/31.5µm asgari varsayım tabanı seçildi;70µm artık opsiyonel üretim yükseltmesi, uygulanmış ayar değildir. RFB1/2 gizli seçim şartı0.1%,≤25ppm/K. Aşağıdaki önceki PCB kaydındaki bakır uyuşmazlığı bu hesap kararıyla yönlendirme açısından ele alındı; gerçek üretim kalınlığı ve termal test onayı hâlâ gerekir.

Bu bölüm önceki footprint/IPC/aktarım durumlarını günceller. MCP/API çalışıyor; yeni kullanıcı izniyle U1–U4 prototip footprintleri atandı ve72 parça PCB'de giriş, iki faz ve çıkış bloklarına taşındı. F1 seçimi açık. Prototip101,6×76,2mm sınır eklendi; son DRC197 unrouted/299 uyarı, bakır kısa devresi/clearance/courtyard çakışması yok. Şema bağlantıları/değerleri korundu; short_count0, ERC0/0. O1 OVP başarısızlığı sürüyor. Canlı stackup35µm, eski BOM70µm; güç izi boyutlandırması kapanmadı. Ayrıntı: `hardware/PCB-layout-status.md`. Üretim onayı yok.

**Sürüm:** 1.4 • **Tarih:** 2026-10-18 • **Durum:** Bootstrap/giriş bypass/PG düzeltildi; O1 aşırı gerilim koruması testi başarısız, PCB onayı yok

## Güncel düzeltme ve test kapsamı

Bu bölüm önceki değerlendirmelerin yerine geçer. RBOOT1/RBOOT2 = 1 Ω, CBOOT1/CBOOT2 = 47 nF ile seri bağlandı. CIN_U5 = 22 nF, ANODE–GND arasına eklendi. RPG1B/RPG2B = 18 kΩ oldu; 100 kΩ üst dirençlerle PG yaklaşık 1.678 V verir. PG uçlarında harici mantık yükü yoktur; ileride bağlanacak alıcının VIH değeri ayrıca kontrol edilir. U1–U4 MPN alanlarına mevcut Value alanındaki doğrulanmış parça kodları yazıldı. F1 MPN/footprint atanmadı; U1–U4 için daha sonra prototip footprint kabulü ve aktarım yapıldı.

Ana şema 77 sembol (73 fiziksel parça ve dört PWR_FLAG), 257 dışa aktarılan pin ve 46 ağ içerir; bunların beşi kasıtlı NC ağı, ikisi yeni bootstrap ara ağıdır. 39 adlandırılmış işlevsel ağ korunur. Önceden var olan pinlerden yalnızca CBOOT1.1 ve CBOOT2.1 yeni seri direnç ara ağına taşınmıştır. Mevcut diğer bağlantılar korunmuştur.

T3'ün [güncel güç bağlantısı belgesi](https://docs.t3gemstone.org/tr/boards/o1/peripherals/introduction#güç-bağlantısı) ve [hardware deposu](https://github.com/t3gemstone/hardware) DC giriş için 5–12 V / 5 A bilgisinde uyuşur. Bu değer gerçek yük veya açılış akımı değildir. Eski ArduPilot 3 A kaydı üreticinin iki güncel kaynağının önüne geçirilmez. Mevcut 301 Ω / 604 Ω eşikler değiştirilmedi; O1'e 5 A yük ataması yapılmadı.

`simulation/pdu-current.net` Konnect tarafından dışa aktarılır. `build_models.py` bütün parçaları ve pinleri buradan üretir; KiCad kaynak dosyalarını okumaz. İki motor aynı pasifleri, ağları ve uyaranları kullanır. Yalnızca ideal bobinin sözdizimi adaptörü ayrıdır: LTspice'ta Rser=0 ile gizli 1 mΩ sönüm direnci kapatılır. DCR iki motorda açıkça 23.3 mΩ'dur. 20 senaryo iki motorda koşturulur; motor uyumu, sayısal yakınsama ve elektriksel kabul ayrı denetlenir. 26 V ripple testi 2 ns ve 1 ns zaman adımlarında tekrarlanır. Güncel sonuçlar `simulation/results.md` ve `verification-results.json` içindedir.

**Açık kritik bulgu:** TPS259824O'nun 16.9 V aşırı gerilim eşiği O1'in belirtilen 12 V giriş üst sınırını korumaz. Eski OVP testi yalnızca çıkışın sonunda kapandığını denetliyordu; yeni O1_PEAK ölçümü bu kusuru görünür kılar. TPS3701 ile EN kapatma adayı incelendi: yaklaşık 9.9 µs gözetleyici ve 212 µs eFuse EN gecikmesi hızlı arıza için yeterli değildir; bu aday ana şemaya eklenmedi. Yeni koruma parçası, gerçek pin/footprint ve zamanlama doğrulaması tamamlanmadan uygulanmayacak. Konnect IPC bağlantısı düzeltildi. Prototip PCB yerleşimi kullanıcı izniyle yapıldı; O1 OVP kapanmadan gerçek O1 bağlantısı ve üretim onayı yok.

Üreticinin indirilebilir LM70880/TPS25982/LM74700 PSpice kütüphaneleri şifrelidir. Taşınabilir davranışsal modeller silikon, bootstrap anahtarlaması, gerçek COMP kararlılığı, CONFIG/SYNC zamanlaması, termal/SOA veya sigorta açma kanıtı değildir. 88 µF ve 44 µF Ceff senaryoları varsayımdır. O1/S2E açılış yükleri, kablo ve surge enerjisi ölçülmedi. Aşağıdaki önceki hesaplar bu sınırlar içinde okunmalıdır.

**Birim sistemi:** SI • **Ondalık ayırıcı:** nokta

> Bu çalışma, 6S bataryadan tek bir 11 V senkron Buck dönüştürücüyle iki korumalı çıkış üretmek için geçici bir tasarım tabanıdır. Güç bütçesi, koruma koordinasyonu ve termal davranış ölçülmedi; tasarım üretime hazır değildir.

## 1. Tasarım kararı

IDA PDU; 20–26 V tasarım giriş aralığında iki LM70880-Q1'i üreticinin desteklediği 180° interleaved bağlantıda kullanarak 11.0 V ortak bara üretmeyi hedefler. T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E ayrı eFuse korumalı kollara bağlanır. Çıkış gereksinimi 7 A / 77 W sürekli, ana güç katı ve iki portun toplam akım ayarı 7.5 A / 82.5 W tasarım kapasitesidir. 7.5 A'da faz başına ortalama 3.75 A kalır; bu, 8 A'lık her LM70880 için %80 derating karşılığı 6.4 A/faz değerinin altındadır. Bu hesap termal kapasiteyi kanıtlamaz. Mevcut 301 Ω / 604 Ω dirençler yaklaşık 4.96 A / 2.53 A nominal kesme eşiği verir. Bunlar korunmuş devre ayarlarıdır; gerçek cihaz yükü olarak kabul edilmez ve ölçüm olmadan son hedef sayılmaz.


## 2. Gereksinimler ve sınırlar

| Öğe | Referans hedef / kaynak değeri | Durum |
|---|---|---|
| Batarya | 6S; nominal 22.2 V; tasarım hesabı 20–26 V | 20–26 V proje varsayımı; gerçek hücre/ESC transient kaydı alınmalı |
| PDU ana çıkışı | 11.0 V, hedef tolerans ±2% | Tasarım hedefi; ölçüm yok |
| Çıkış gereksinimi | 7 A sürekli; 77 W @ 11 V | PDU hedefi; yük profili ve termal ölçüm henüz yok |
| Güç katı tasarım kapasitesi | 7.5 A; 82.5 W @ 11 V | İki faz × 8 A LM70880-Q1; hedef yükte 3.5 A/faz, 7.5 A kapasitede 3.75 A/faz; TI'nin iki cihazlı interleaved yapısı desteklediği katalog bilgisi kart termalini kanıtlamaz |
| Gemstone O1 giriş | T3 donanım deposunda DC 5–12 V / 5 A | Kapasite/rating; gerçek tüketim veya kalkış akımı değil |
| RPLIDAR S2E giriş | 9–28 V, tipik 12 V; 12 V'ta kalkış tipik 1.2 A, tabloda maks. 1.5 A; çalışma tipik 0.2 A, maks. 0.22 A | Resmî S2E veri sayfası; daha düşük başlatma geriliminde daha fazla akım uyarısı var |
| Topraklama | Ortak GND, izolesiz | Sistem arayüzü varsayımı; Ethernet ekran/toprak bağlantısı incelenmeli |
| Arayüzler | O1 besleme jakı; S2E güç kablosu; Ethernet RJ45/UDP | O1 jak geometrisi/polaritesi ve S2E kablo konnektörünün sipariş kodu doğrulanmalı |
| Çevre | Titreşimli batarya/ESC ortamı | EMC, titreşim, nem ve termal sınıf gereksinimleri tanımlı değil |

**Doğrulanmış kaynaklar:** T3 güncel güç bağlantısı belgesi ve hardware deposu DC giriş için 5–12 V / 5 A ratingi verir. Eski ArduPilot 3 A kaydı güncel üretici sınırının yerine kullanılmaz. Gerçek tüketim ve kalkış akımı ölçülmedi.

## 3. Mimari

    6S BAT (20–26 V)
      → giriş sigortası
      → TVS ve ters kutup koruması (parça/koordinasyon testi açık)
      → giriş filtre ve bulk kapasite
      → 2 × LM70880-Q1, 180° interleaved senkron Buck, 11.0 V
      → 11 V ortak bara (7 A gereksinim, 7.5 A güç katı/port tasarım kapasitesi)
           ├─ TPS25982 circuit-breaker eFuse, korunmuş nominal kesme eşiği 4.96 A → T3 Gemstone O1
           └─ TPS25982 circuit-breaker eFuse, ayar yaklaşık 2.5 A → RPLIDAR S2E
      → ortak GND; S2E Ethernet RJ45/UDP

O1 4.96 A ve S2E 2.53 A mevcut nominal kesme eşikleri yaklaşık 7.49 A toplam verir; tolerans, eFuse zaman davranışı ve eşzamanlı kalkış nedeniyle bu toplam sert bir akım sınırı değildir. Bu eşikler gerçek yük profili ölçülmeden onaylanmış cihaz akım hedefleri değildir. İki LM70880-Q1'in primary/secondary konfigürasyonu, ortak harici kompanzasyonu, eşzamanlı EN başlatması ve benzer güç yolu empedansı üretici şemasına göre kurulmalıdır. S2E'nin 11 V kalkışı ve her iki cihazın gerçek akımı ölçülmeden son limitler dondurulamaz.

## 4. Yük bütçesi

S2E veri sayfasında 12 V'ta ilk kalkış tipik 1.2 A, tabloda azami 1.5 A verilmiştir. S2E'nin düşük başlatma geriliminde daha fazla akım çekebileceği belirtilir. 11 V'a sabit güç dönüşümü yalnızca planlama varsayımıdır.

Katalog değerlerinden türetilen üst planlama zarfı (eşzamanlı gerçek yük ölçümü değildir):

- O1: 12 V × 5 A = 60 W (üretici giriş kapasitesinden türetilen üst zarf; kartın gerçek yükü değil).
- S2E: 12 V × 1.5 A = 18 W (datasheet start-current üst değeri; çalışma akımı tipik 2.4 W).
- Birlikte: 78 W.
- 11 V ortak barada: 78 W / 11 V = 7.091 A. Bu kataloglardan türetilmiş eşzamanlılık kanıtı olmayan yük zarfı, 7 A gereksiniminin az üzerindedir.
- 7 A tasarım gereksinimi 77 W'tır; 7.5 A güç katı/branch ayarı kapasitesi 82.5 W'tır. Bu değerler cihazın gerçek tüketim profilinin ölçümü değildir.

Bu hesapta O1 5 A ve S2E 1.5 A'nın eşzamanlı gerçek ölçüm olduğu iddia edilmez. Mevcut 4.96 A / 2.53 A nominal kesme eşikleri tasarım ayarlarıdır; gerçek cihaz akımları olarak kullanılmaz. S2E 1.5 A değeri 12 V içindir ve 11 V kalkışı ölçülmelidir. Prototip öncesi iki cihazın ayrı ayrı ve eşzamanlı giriş akımı, kalkış dalga şekli, minimum bataryada ve en ağır yazılım/çevre birimlerinde ölçülmelidir.

## 5. Topoloji seçimi

| Topoloji | Karar | Gerekçe |
|---|---|---|
| İki fazlı interleaved senkron Buck | Seçildi | 20–26 V'tan 11 V'a düşürme, 7 A gereksinim ve 7.5 A tasarım kapasitesi; iki LM70880-Q1 ile akım paylaşımı, 180° faz farkı ve ortak GND |
| Asenkron Buck | Elendi | Diyot kaybı yaklaşık (1−D) × 0.5 V × 7.5 A; ısı ve verim cezası |
| Boost | Elendi | Giriş hedef çıkıştan yüksek; gerekli dönüşüm yönünün tersi |
| Buck-Boost | Elendi | Giriş aralığında 11 V'un altına düşme yok; fazladan anahtar/kontrol kaybı ve maliyet |
| Flyback/forward | Elendi | İzolasyon gereksinimi yok; yaklaşık 60 W geçici plan için manyetik tasarım ve EMI karmaşıklığı gereksiz |

## 6. Ana Buck seçimi ve alternatifler

| Aday | Üretici sınırı | Karar |
|---|---|---|
| 2 × TI LM70880-Q1 | Her cihaz 4.5–80 V, 8 A, 200 kHz–2.2 MHz; üretici dual-phase/interleaved single-output bağlantısı 16 A'a kadar | Seçilen aday güç katı. 7.5 A toplamda 3.75 A/faz; primary/secondary ayarları ve harici kompanzasyon TI datasheet'ine göre yapılmalı |
| TI LM61495 | 3–36 V, 10 A; 42 V abs max yalnızca sınırlı transient koşulunda | ESC/batarya transienti ölçülmeden 36 V çalışma sınırı dar; 80 V aday tercih edildi |
| ADI LT8645S | 3.4–65 V, 8 A | Düşük EMI adayı; 8 A sınırı ve maliyet/tedarik karşılaştırması gerekir |
| TI LM5146-Q1 | 5.5–100 V kontrolcü; harici MOSFET | Daha yüksek transient ihtiyacında seçenek; güç elemanı ve sürücü tasarım yükü daha yüksek |

LM70880-Q1 içindeki anahtarlar entegredir. TI, iki cihazın dual-phase bağlantısını ve 16 A'a kadar akım paylaşımını destekler; üçüncü faz eklenemez. Secondary cihazda RT direnci osilatör değil slope compensation içindir ve primary ile aynı olmalıdır; EXTCOMP pinleri kısa bağlanmalı, harici kompanzasyon kullanılmalı ve iki EN aynı anda kalkmalıdır. TI'nin yayımladığı 48 V giriş, 12 V/8 A, 400 kHz örneği yalnızca başlangıç devresi/yerleşim referansıdır. Oradaki %95.6 verim IDA PDU verimi değildir. IDA PDU çalışma aralığı, 11 V çıkış, batarya empedansı ve PCB ısıl koşulları farklıdır.

## 7. İlk boyutlandırma

### 7.1 Duty ve giriş akımı

İdeal duty: D = Vout / Vin. Gereksinim gücü Pout = 11 V × 7 A = 77 W; güç katı/port ayarı kapasitesi 11 V × 7.5 A = 82.5 W. Aşağıdaki Iin tablosu 77 W gereksinim için %90–95 verim senaryosudur; ölçüm veya IDA PDU simülasyon sonucu değildir. Güç kaynağı, sigorta ve giriş konnektörü tasarımı 82.5 W kapasiteyi ayrıca dikkate almalıdır.

| Vin | D (ideal) | Iin @ η=95% | Iin @ η=90% |
|---:|---:|---:|---:|
| 20.0 V | 0.550 | 4.053 A | 4.278 A |
| 22.2 V | 0.495 | 3.651 A | 3.854 A |
| 25.2 V | 0.437 | 3.216 A | 3.395 A |
| 26.0 V | 0.423 | 3.117 A | 3.291 A |

Batarya, kablo, sigorta ve konnektör hesabında yalnızca nominal 22.2 V kullanılmamalı; 20 V ve transient testi dahil edilmelidir.

### 7.2 Endüktör

Ön seçim L = 6.8 µH, fs = 400 kHz. ΔIL = Vout × (1−D)/(L×fs).

| Vin | ΔIL p-p / faz | 7 A toplamda tepe / faz |
|---:|---:|---:|
| 20.0 V | 1.82 A | 4.41 A |
| 22.2 V | 2.04 A | 4.52 A |
| 25.2 V | 2.28 A | 4.64 A |
| 26.0 V | 2.33 A | 4.67 A |

İki fazın her birinde 6.8 µH ve 400 kHz minimum anahtarlama varsayımı kullanılır. 7.5 A toplam kapasitede faz başına 3.75 A ortalama ve nominal 26 V'ta 4.92 A tepe oluşur. 6.8 µH parçada −20% tolerans varsayımıyla tepe yaklaşık 5.21 A olur. LM70880-Q1'in current-sense eşiği 50–62 mV aralığındadır; faz başına 7.5 mΩ ±1% Kelvin şöntte minimum eşik/azami R ile current-limit yaklaşık 6.60 A olur ve worst-case hesap tepe akımının yaklaşık %27 üzerindedir. Maksimum eşik/minimum R ile limit ve 75 ns tipik comparator gecikmesi yaklaşık 8.56 A tepeye ulaşabilir; bu nedenle indüktörün sıcaklıktaki Isat değeri büyük marjla seçilmelidir.

Türkiye'de kart üzerinde kullanılacak ilk bobin adayı Vishay IHLP4040DZER6R8M01: Farnell Türkiye kataloğunda listeli ve arama görünümünde kesik bant fiyatı €1.10 görünür; ürün sayfasından Türkiye için güncel stok/teslim tarihi doğrulanamadı, bu yüzden sipariş edilebilirliği açık kabul etmiyorum. Vishay veri sayfasında 6.8 µH ±20%, DCR en çok 23.3 mΩ, 8 A 40 °C sıcaklık artışı akımı ve tipik 13.5 A'da %20 endüktans düşümü yazıyor. Bu akım bütçesindeki yaklaşık 3.84 A faz RMS akımında soğuk DCR ile bobin kaybı yaklaşık 0.34 W/fazdır; datasheet 8 A/40 °C-rise noktasına basit I² ölçeklemesi ~9 °C yükseliş verir, gerçek sıcaklık PCB bakırı, çevre sıcaklığı ve komşu güç kayıplarıyla ölçülmelidir. En kötü OCP/delay tepe hesabı ~8.56 A, %20 derating uygulanmış doyum akımı 10.8 A'ın altındadır. Yine de parça sıcaklığı ve akım paylaşımı prototipte ölçülmeli. 10.92×10.3×4 mm gövde, XAL1010 alternatifinden daha alçak ve PCB ayak izi farklıdır.

Daha yüksek akım marjlı Coilcraft XAL1010-682MED alternatifinin Mouser Türkiye sayfası geçen ay 55 stok gösterirken daha yeni seri listesi 0 stok, 599 siparişte ve Mart/Nisan 2027 tahmin tarihleri gösteriyor. Güncel erişimde stok çelişkili olduğundan bunu hazır bulunan parça saymıyorum; arama/tedarik teyidi yapılmadan BOM maliyeti veya kart seçimi buna dayandırılmamalı. Bu alternatif 18.5 A Irms, 21.8 A Isat, 8.9 mΩ DCR ve 10×10×11.3 mm gövdeye sahiptir. Her faz şönt kaybı yaklaşık 0.11 W; 1 W düşük endüktanslı ±1% direnç ve Kelvin yolları başlangıç seçimidir.

### 7.3 Çıkış ayarı ve filtre

LM70880-Q1 FB referansı 0.8 V. Vout = 0.8 × (1 + Rtop/Rbottom). 130 kΩ / 10.2 kΩ için hesaplanan hedef 10.996 V. Bu ideal direnç hesabıdır; gerçek tolerans, bias akımı, yük regülasyonu ve transient ölçümü kapsam dışı.

Başlangıç değerleri:

- CIN: iki IC'nin her biri için 4 × 4.7 µF, 100 V X7S seramik (toplam en az 8); her güç döngüsüne yakın yerel bypass ve kaynağa bağlı bulk kapasite ayrıca seçilecek.
- COUT: 8 × 22 µF, 25 V, aday GCM32EC71E226KE36 X7S; iki faz ortak çıkışına yakın dağıtılacak. Yayınlanmış veri sayfasında sayısal DC-bias noktası yoktur ve 11 V SimSurfing değeri alınamadı. Kompanzasyon, nominal 176 µF'ın %50'si olan 88 µF varsayımında kaldı.
- L1/L2: 6.8 µH/faz, Vishay IHLP4040DZER6R8M01 ana aday; Coilcraft XAL1010-682MED yüksek akım marjlı fakat güncel stok/lead-time belirsiz alternatif.
- Her IC: CBOOT 47 nF, CVCC 4.7 µF, CVDDA 0.1 µF, VIN-PGND yüksek di/dt kapasitesi 10 nF / 100 V / X7R / 0603. RT her iki fazda 49.9 kΩ. Datasheet tablosu bu dirençte 400/440/480 kHz verir; denklem (3) aynı dirençte 435 kHz verir. Ripple hesabı tablo minimumu 400 kHz ile yapılır.
- Kompanzasyon, SNVSBX7A denklem 42–44 ve paylaşılan COMP için RS/2 = 3.75 mΩ ile hesaplandı. fC = 40 kHz, Ceff = 88 µF varsayımı, gm = 1200 µS, GCS = 10, VREF = 0.8 V. RCOMP tam değer 9503 Ω, seçilen E96 9.53 kΩ. CCOMP tam değer 4.175 nF, seçilen 4.7 nF; sıfır 3553 Hz, 7.5 A yük kutbu 1233 Hz'in üstündedir. CHF, varsayılan ESR sıfırında negatif çıktığı için 47 pF seçildi; kutup yaklaşık 355 kHz ve COMP ile GND arasındadır. Bu bir ölçülmüş döngü kazancı değildir.
- Akım algılama: faz başına 7.5 mΩ, ±1%, 1 W düşük endüktanslı şönt ve Kelvin hatları. Minimum eşik 50 mV ve %1 yüksek dirençle faz limiti 6.60 A olur. 11 V ve %20 düşük endüktansta 75 ns gecikme buna yaklaşık 0.15 A ekler.
- Buck UVLO: 180 kΩ / 10.0 kΩ. Tipik açılış 19.0 V, eşik maksimum 1.05 V iken 19.95 V, tipik kapanış 17.1 V. İki EN aynı EN_BUCK düğümündedir.

Seramik kondansatörün üzerindeki nominal toplam kapasite DC bias altında geçerli olmayabilir. Üretici DC-bias eğrisi olmadan ripple hesabı tam nominal kapasite kabulüyle sonuçlandırılamaz.

## 8. Koruma ve arayüz

| Bölüm | Referans çözüm | Açık doğrulama |
|---|---|---|
| Batarya giriş sigortası | 10 A sınıfı, DC ve kesme kapasitesi uygun, bataryaya yakın | MPN, gecikme eğrisi, batarya kısa devre akımı ve kablo koordinasyonu |
| Giriş TVS | Littelfuse SMCJ33A: 33 V standoff, katalogdaki 28.2 A testinde 53.3 V max clamp | ESC transient enerjisi/akımı, gerçek clamp, sigorta ve koruma IC koordinasyonu |
| Ters kutup | LM74700 + BSC160N10NS3G, 100 V, 16 mΩ max; CVCAP 100 nF VCAP-ANODE. TVS korumalı VIN tarafında kalır | Surge enerjisi ölçülmedi. LM74700 ANODE mutlak sınırı 65 V; SMCJ33A kelepçe üstü 53.3 V |
| Port eFuse | TI TPS259824ONRGET: 2.7–24 V, 15 A class, 2.7 mΩ typical; circuit-breaker option, 16.9 V input OVP variant | Full-temperature limit accuracy, breaker timer, thermal layout, reset/fault, stock |
| O1 port | Mevcut 301 Ω ile yaklaşık 4.96 A kesme eşiği; gerçek yük hedefi değil | Resmî DC rating 5–12 V / 5 A; akım profili, jak, kablo ve konnektör ölçümü açık |
| S2E port | Yaklaşık 2.5 A eFuse nominal ayarı ilk deneme | 11 V start current, güç kablosu pinleri ve akım kapasitesi |
| Ethernet | RJ45, 10/100 Ethernet ve UDP cihaz arayüzü | Besleme dönüşü ve Ethernet ekranı topraklaması sistem seviyesinde |

TPS25982 veri sayfası akım limit bağıntısı RILIM[Ω] = 1460/(ILIM[A]−0.11): 301 Ω yaklaşık 4.96 A, 604 Ω yaklaşık 2.53 A verir. EN/UVLO mutlak üst sınırı 7 V, önerilen çalışma 6 V olduğundan EN doğrudan 11 V baraya bağlanmaz. Ortak bölücü 64.9 kΩ / 10.0 kΩ, tipik açılışı 8.99 V baraya ve 11 V'ta pin gerilimini 1.47 V'a koyar. PG mutlak üst sınırı da 7 V'tur. 100 kΩ pull-up ile 18 kΩ pulldown, 11 V'ta PG yüksek seviyesini 1.678 V yapar; harici alıcı bağlı değildir. IMON kazancı tipik 246 µA/A ve VIN > 5 V için önerilen üst gerilim 3.3 V'tur. O1 için 2.61 kΩ, 4.96 A'da tipik 3.19 V; S2E için 4.99 kΩ, 2.53 A'da tipik 3.10 V verir. CdVdt = 1.0 nF, SR = 4.6 V/ms, 11 V yükseliş yaklaşık 2.39 ms, kapasite başına kalkış akımı 4.6 mA/µF. Bunlar nominal hesaplardır; tam sıcaklık eFuse eşiği, circuit-breaker zamanlayıcısı ve gerçek port kapasitesi ayrıca kontrol edilmelidir. S2E datasheet'indeki 12 V × 1.5 A kalkış üst değerini sabit güç varsayımıyla 11 V'a taşımak 1.64 A verir; 2.53 A nominal ayara yaklaşık 54% fark bırakır, ancak üreticinin düşük kalkış geriliminde daha yüksek akım uyarısı nedeniyle bu bir 11 V marj garantisi değildir. TPS259824ONRGET varyantının 16.9 V OVP eşiği O1'in belirtilen 12 V giriş üst sınırını korumaz. Düzeltilmiş model bu testi iki motorda da geçemedi. Yeni hızlı koruma ve gerçek akım ölçümü kapanmadan PCB onayı yok.

Kart tarafı için üç adet 2-pin Molex Micro-Fit 3.0 43045-0200 başlık adayı seçildi: J1 giriş, J2 O1 çıkışı, J3 S2E çıkışı; kart tarafında pin 1 ilgili güç rayı, pin 2 GND olarak etiketlenecek. Bu seçim cihaz kablo eşleşmesi anlamına gelmez. O1 jakının dış/iç çapı ve kutup polaritesi, mekanik kilitleme ve adaptör kablosu; S2E dört pin konnektörünün üretici numarası doğrulanmalı. Datasheet S2E pin 1 VCC, pin 2 GND, pin 3/4 bağlantısız der; kablo yönü ve kart tarafı polaritesi ölçülmeli.

## 9. PCB yerleşim ve üretim

Güncel yönlendirme tabanı iki katman ve canlı kartla aynı35µm nominal dış bakırdır; hesap31.5µm alt kalınlık varsayımıyla yapıldı. Eski2oz/70µm önerisi opsiyonel yükseltmedir ve uygulanmış sayılmaz. Üstte güç katı ve kısa anahtarlama döngüsü; alt yüzde mümkün olduğunca kesintisiz GND dönüşü hedeflenir. Yüksek akım izleri için geniş bakır dolgu, termal via ve iki yüzde paralel akım yolları gerekir; SW bakır alanı küçük tutulur, FB/COMP/ISNS Kelvin hatları gürültülü düğümlerden uzak tutulur. 2 katmanlı yerleşimde GND düzleminin kesilmesi, EMI ve ısıl dağılım için ek risk oluşturur; tasarım boyutu/yerleşimi bunu karşılamazsa 4 katmanlı yığına geçiş tasarım kararı olarak yeniden açılmalıdır. 2 oz JLCPCB 2 katman üretiminde minimum iz/boşluk 0.16/0.16 mm; tasarım kuralı üretici minimumuna dayanmamalı, en az 0.20 mm seçilmeli. Güç izi genişliği akım ve kabul edilen sıcaklık artışından ayrıca hesaplanmalı.

Bu bir katman yığını siparişi veya bitmiş PCB değildir. TPS25982'nin RGE paketinde 24 çevre pini yanında iki ayrı exposed pad bulunur: pad 25=IN, pad 26=GND; tek exposed-pad ayak izi kullanılamaz. Her LM70880 için TI'nin RRX0029B üretici land pattern'i (29 çevre pini ve üç termal pad ilişkisi) izlenmeli; iki IC'nin phase bağlantıları da veri sayfasına uygun olmalıdır. KiCad 10 yerel kütüphanesinde `Inductor_SMD:L_Vishay_IHLP-4040` genel ayak izi bulundu; MPN'nin üretici land pattern'iyle ve 4 mm gövde yüksekliğiyle son karşılaştırma yapılmadan üretim ayak izi sayılmamalı. Buck ve eFuse ayak izlerinin üretici land pattern'leri doğrulanıp özel kütüphane nesneleri hazırlanmalı. Depodaki `hardware/functional-blocks.kicad_sch` yalnızca eski işlevsel blok sayfasıdır ve güncel şema değildir. Kök `PDU.kicad_sch`, 2026-10-18 kayıtlı elektrik şemasıdır: 77 sembol, 39 yerel ağ, bağlı olmayan pin yok, kısa devre yok. KiCad 10.0.7 ERC sonucu 0 hata ve 0 uyarıdır. Yerel `GND` etiketleri `#FLG02` ile sürülür. U1–U4 prototip ayak izleri doğrulanıp aktarıldı; F1 boş. `PDU.kicad_pcb`72 parçalı ilk blok yerleşimi ve geçici kenar çizgisi içerir; yönlendirme/üretim kabulü yok. RRX bakır yaklaşımı ve stencil üretim kontrolü ayrıca açık.

## 10. Ön BOM ve maliyet durumu

| Ref | Aday / MPN | Adet | Fiyat bilgisi (2026-10-17 erişimi) | Durum |
|---|---|---:|---|---|
| U1,U2 | TI LM70880QRRXRQ1 | 2 | Mouser global sayfası 29.390 gönderilebilir stok gösterdi; Türkiye yerel stok/teslim fiyatı doğrulanmadı | Dual-phase için üreticinin desteklediği iki cihaz; sipariş öncesi Türkiye sevkiyatı/vergisi kontrol edilmeli |
| L1,L2 | Vishay IHLP4040DZER6R8M01 | 2 | Farnell Türkiye kataloğu €1.10/kesik bant gösteriyor; Türkiye stok/teslim teyidi yok | 6.8 µH, 8 A (ΔT 40 °C), tipik 13.5 A Isat, 23.3 mΩ max; 10.92×10.3×4 mm; %20 Isat derating ile akım bütçesine uygun aday |
| U3,U4 | TI TPS259824ONRGET | 2 | Mouser Türkiye: 24 adet stok; €4.18 tekli, €3.16/10 adet | 15 A sınıfı circuit-breaker eFuse; 16.9 V OVP variant; stok sipariş öncesi doğrulanmalı |
| D1 | Littelfuse SMCJ33A | 1 | Mouser TR: €0.662 tekli sayfa fiyatı; vergi/taşıma hariç | Surge testi öncesi aday |
| Pasifler | Hesaplanan kompanzasyon, UVLO, eFuse EN/PG/IMON ve dVdt değerleri `hardware/bom.csv` ve `calculate.py` içinde | Set | Teklif gerekli | Ceff 88 µF varsayımdır; DC-bias eğrisi yok |
| F1 | 10 A DC sigorta ve tutucu | 1 | Seçilen eğri ve yerel fiyat gerekli | MPN açık |
| Q1, U5 | BSC160N10NS3G ve LM74700 | 1 + 1 | Fiyat açık | Şemada kurulu. 20 V, %90, 82.5 W için FET kaybı yaklaşık 0.34 W. Surge enerjisi ölçülmedi |
| J1–J3 | Molex Micro-Fit 3.0 board header 43045-0200 (3 adet), housing 43025-0200 (3 adet), 43030-0007 dişi krimp kontak (6 adet) | 3 arayüz | Farnell TR: header 9.917 stok/€0.807 (10+); housing Mouser TR: 327.388 stok/€0.284; kontak Farnell TR: 497.630 stok/€0.174 (10+) | Kilitli board-side aday; O1 jakı ve S2E cihaz kablosuyla eşleştiği doğrulanmadı. Adaptör kablosu ve polarite ölçülmeli; muhafazakâr bağlantı akım sınırı 5 A varsayımıdır |
| PCB+montaj | JLCPCB tercihi: 2 kat, 2 oz dış bakır | 1 | Kart boyutu ve üretim dosyasıyla teklif gerekli | Şema var; PCB yerleşimi ve LM70880/TPS25982 özel ayak izi yok. 2 oz 2 kat min iz/boşluk 0.16/0.16 mm, hedef tasarım kuralı ≥0.20 mm |

Bu snapshot tam maliyet hesabı değildir. Vishay bobin için Farnell Türkiye katalog fiyatı €1.10/adet kabul edilirse iki eFuse, iki bobin, üç header (Farnell minimum 10 adet), üç housing ve kontaklar (Farnell minimum 10 adet) alt kümesi yaklaşık €21.22 eder; bobinin Türkiye stoğu/teslimi doğrulanmadığı için bu yalnızca katalog fiyatına dayalı koşullu toplamdır. Coilcraft alternatifi €4.39/adet fiyatından hesaplanırsa alt küme yaklaşık €27.80 olur; ancak daha yeni Mouser listesi stok yok ve 2027 teslim tahmini gösteriyor. Kargo, vergi/gümrük koşulları, iki buck IC, pasifler, giriş koruması, PCB, montaj ve kablolar hiçbir toplama dahil değildir. LM70880 fiyatı global Mouser sayfasından görüldü; Türkiye'ye teslim maliyeti ayrıca doğrulanmalı. Farklı satıcıların fiyatlarını ve kur/vergi kalemlerini tek TL toplamı gibi sunmayın. Brief'teki 5000–7000 TL hedef bütçesi doğrulanmış değildir.

## 11. Riskler ve doğrulama kapıları

| ID | Risk | Etki | Kapatma ölçütü |
|---|---|---|---|
| R1 | O1 resmî DC ratingi doğrulandı; tüketim ve kalkış akımı bilinmiyor | PDU yetersiz veya aşırı boyutlu olabilir | Board etiketi/üretici yanıtı ve ağır yazılımda akım ölçümü |
| R2 | S2E 11 V başlatma akımı 12 V tablosundan farklı | eFuse trip veya bus droop | 9/10/11/12 V start ve eşzamanlı yük testi |
| R3 | ESC transient belirsiz | U1, TVS veya reverse guard hasarı | Giriş waveform/enerji ölçümü ve coordinated clamp hesabı |
| R4 | İki fazlı güç paylaşımı ve termal dengesi | Bir fazın diğerinden fazla akım taşıması, ısınma veya hiccup | 7.5 A, en düşük Vin ve sıcak ortamda faz akımlarını/termalini ölç; aynı anda EN, aynı RT, ortak EXTCOMP ve empedans eşleşmesini doğrula |
| R5 | Ceff/kompanzasyon varsayımı | Regülasyon/ringing/kararsızlık | DC-bias eğrisi, üretici model, load transient ve bench loop kontrolü |
| R6 | Konnektör/polarite/kablo tanımsız | Yanlış kablolama veya düşük uç gerilimi | Kart sürümü, kablo eşlemesi ve akımda uç voltajı |
| R7 | eFuse toleransı/ısı | Erken açma veya sıcak çalışma | Eşik ve RDS(on) sıcaklığını port başına ölç |
| R8 | KiCad/PCB henüz üretilmemiş | Üretim mümkün değil | IDA PDU şema, footprint, ERC/DRC ve Gerber kontrolü |
| R9 | Vishay bobin Türkiye stok teyidi yok; Coilcraft için daha yeni Mouser listesi 0 stok/2027 teslimi gösteriyor; iki footprint farklı | Satın alma gecikmesi veya yanlış pad/gövde uyumu | Sipariş öncesi exact MPN stok/teslim teyidi; MPN dondurulduktan sonra üretici land pattern ve yükseklik ile PCB footprint karşılaştırması |

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
- TI LM70880-Q1 product/datasheet: https://www.ti.com/product/LM70880-Q1 • https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf (dual-phase rules, OCP threshold, RRX0029B footprint)
- TI LM708x0-Q1 application examples: https://www.ti.com/lit/ds/symlink/lm70840-q1.pdf
- DigiKey LM70880QRRXRQ1 pricing/supply: https://www.digikey.com/en/products/detail/texas-instruments/LM70880QRRXRQ1/24420927
- TI LM61495: https://www.ti.com/product/LM61495
- ADI LT8645S datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/8645sf.pdf
- TI LM5146-Q1: https://www.ti.com/product/LM5146-Q1
- TI TPS25982 datasheet (D sürümü, May 2026): https://www.ti.com/lit/ds/symlink/tps25982.pdf
- Mouser Türkiye TPS259824ONRGET: https://www.mouser.com.tr/tr/ProductDetail/Texas-Instruments/TPS259824ONRGET
- Mouser global LM70880QRRXRQ1: https://www.mouser.com/en/ProductDetail/Texas-Instruments/LM70880QRRXRQ1
- Vishay IHLP-4040DZ-01 data sheet: https://www.vishay.com/docs/34193/ihlp-4040dz-01.pdf; Farnell Türkiye listings: https://tr.farnell.com/c/passive-components/inductors/power-inductors/smd-power-inductors?brand=vishay&product-range=ihlp-4040dz-01-series; Mouser Türkiye XAL1010-682MED series stock: https://www.mouser.com.tr/tr/c/passive-components/?series=XAL1010
- Farnell Türkiye Molex 43045-0200 header: https://tr.farnell.com/molex/43045-0200/conn-r-a-pcb-hdr-2pos-2row-3mm/dp/1012251
- Mouser Türkiye Molex 43025-0200 housing: https://www.mouser.com.tr/tr/ProductDetail/Molex/43025-0200
- Farnell Türkiye Molex 43030-0007 terminal: https://tr.farnell.com/molex/43030-0007/contact-socket-24-20awg-crimp/dp/2101869
- JLCPCB rigid PCB capabilities: https://jlcpcb.com/capabilities/Capabilities%2C/
- Littelfuse SMCJ33A: https://www.littelfuse.com/assetdocs/littelfuse-tvs-diode-smcj-datasheet?assetguid=8a337998-7c2c-4b8a-8c6d-8f2b6c5d3d8e
- Mouser TR SMCJ33A price page: https://www.mouser.com.tr/ProductDetail/Littelfuse/SMCJ33A

## 13. Olgunluk

İki fazlı şema `PDU.kicad_sch` üzerinde kuruludur. Kompanzasyon, UVLO, eFuse EN/PG/IMON ve ters kutup değerleri datasheet denklemleriyle hesaplanıp şemaya işlendi; Ceff hâlâ varsayımdır ve döngü kazancı ölçülmemiştir. LM70880 ve TPS25982 prototip ayak izleri ve72 parçalı ilk PCB yerleşimi vardır; laboratuvar testi, yönlendirme, üretim kabulü ve tam maliyet teklifi yoktur. Bu belge prototip veya üretim sonucu iddia etmez.

## 14. 2026-10-18 yeniden değerlendirme

Netlist pin pin datasheet kurallarıyla yeniden okundu. ERC 0 hata ve 0 uyarı, kısa devre yok, açık pin yok. Sembol çakışması yok. Bağlantı değiştirilmedi.

Parça kararı, katalog sınırı ve bu devredeki gerilim veya akım:

- LM70880-Q1: 4.5–80 V ve 8 A. Korunan giriş 20–26 V, faz ortalaması 3.75 A, 400 kHz'te tepe yaklaşık 4.92 A. Sınırın içinde, parça duruyor.
- IHLP4040DZER6R8M01: tipik 13.5 A doyum, 8 A / 40 °C. %20 düşük endüktansta tepe 5.21 A. Sınırın içinde, parça duruyor.
- 7.5 mΩ şönt: faz başına yaklaşık 0.11 W. 1 W sınıfının içinde.
- TPS259824ONRGET: 11 V, EN pini 1.47 V, PG 1.678 V, IMON yaklaşık 3.2 V. Üçü de 6 V ve 3.3 V önerilen sınırların içinde. 301 Ω ve 604 Ω duruyor; O1 5 A dondurulmadı.
- SMCJ33A: 33 V standoff, 26 V çalışma geriliminin üstünde. Kelepçe üstü 53.3 V, LM74700 ANODE sınırı 65 V ve FET 100 V altında. Surge enerjisi hâlâ ölçülmedi.
- BSC160N10NS3G: 20 V ve %90 verimde yaklaşık 4.58 A, kayıp yaklaşık 0.34 W. Parça duruyor.
- GCM32DC72A475KE02L giriş kapasitesi X7S ve 100 V. TI örneği X7R yazar; gerilim sınıfı kelepçeyi kapsadığı için parça değiştirilmedi.
- GCM32EC71E226KE36 çıkış kapasitesi X7S ve 25 V. Sayısal bias eğrisi yok; 88 µF varsayımı ve 9.53 kΩ / 4.7 nF / 47 pF duruyor.
- D2 ve D3 SS34: 40 V, 3 A, port çıkışına paralel kelepçe. Seri güç yolu değil. Kablo enerjisi hesaplanmadığı için daha büyük diyot konmadı. Sürekli 5 A taşıyamaz.
- F1, ölçülmüş giriş bulk ihtiyacı, hızlı O1 aşırı gerilim koruması ve IC ayak izleri açık kaldı.

Aynı davranışsal devre LTspice 26.1.1 ve ngspice-47 ile kabul toleransının içinde koştu. Ayrıntı `simulation/results.md` içindedir.
