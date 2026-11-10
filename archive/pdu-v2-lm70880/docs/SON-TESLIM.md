> **SUPERSEDED (G3, 2026-11-07) → reports/g2/PCB-HANDOFF.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# PDU — şema ve yönlendirme teslimi

Güncel genel durum ve inceleme sırası: [PROJECT-STATE](PROJECT-STATE.md) ve [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md). Bu belge ayrıntılı yönlendirme kuralları ve teslim sınırları için korunur.

19 Ekim 2026. Ana şema: `PDU.kicad_sch`; proje: `PDU.kicad_pro`. Bu dosya eski çelişkili durum paragraflarının yerine geçen güncel karar ve iş listesidir.

## Hazır olanlar

- Şema görünümü: `PDU_schematic_finished.png` ve `.pdf`.23 parçanın referans/değer yazıları düzenlendi; güç akışı ve ortak iki fazın ilişkisi açıklandı. D1 yazıları antetten ayrıldı. Kablolu blokların yerleri korunmuştur: faz2 üstte, faz1 altta; giriş alttadır. Taşıma riski yaratmadan mevcut kısa bağlantılar korundu.
- Short0, ERC0 hata/0 uyarı, açık pin0, sembol/etiket örtüşmesi0, floating/orphan0.218 tel/86 etiket/77 sembol.73 fiziksel parçanın46 net/257 pin üyeliği korunmuştur. Sonraki RIMON1/2 değişikliği ve sekiz COUT footprint ataması [uygulama kaydında](../hardware/No-measurement-closeout.md) belirtilir. Bunlar fiziksel koruma veya termal kabulün yerine geçmez.
- RFB1=Panasonic ERA3AEB134V ve RFB2=ERA3AEB1022V seçildi ve şemaya işlendi:0.1%, en çok25ppm/K,0603,0.1W. Nominal130k/10.2k değişmedi. RIMON1/RIMON2, ERA3AEB8060V806ohm olarak şema ve PCB'de güncellendi. Akım kesme dirençleri301/604ohm korundu. Güncel dışa aktarım: `hardware/pdu-current-bom.csv`.
- PCB72 footprint içerir; F1 henüz yok. Geçici101.6x76.2mm sınır ve ilk blok yerleşimi vardır. İz sayısı0; yönlendirme tamamlanmış değildir.
-9 netclass ve46/46 tam ağ adı ataması proje dosyasına yazıldı ve Konnect ile geri okundu. Eşleşmeyen veya sahipsiz desen yok. Atama dosya kaynağından, ağ listesi canlı PCB'den doğrulandı; mevcut açık editörün önbelleğinin yenilendiği iddia edilmez.

## Netclass genişlikleri

Bunlar şematik yeşil telinin görsel kalınlığı değil, PCB router varsayılanlarıdır. KiCad netclass genişliği tek başına minimum DRC sınırı veya akım garantisi değildir. Güç pininden körlemesine geniş iz başlatma; aşağıdaki fanout/Kelvin istisnalarını uygula.

- INPUT_POWER:4.5mm, clearance0.30mm; `/VBAT`, `/ANODE`, `/VIN`.6A sürekli yönlendirme zarfı.
- BUS_POWER:6.0mm, clearance0.20mm; `/VOUT`, `/GND`.8A ortak bara/dönüş zarfı. GND için sürekli düzlem tercih edilir; düşük akımlı analog dönüş kolu6mm olmak zorunda değildir.
- PHASE_POWER:3.5mm, clearance0.20mm; `/SW_PH1`, `/SW_PH2`, `/ISNS1`, `/ISNS2`.5A/faz yönlendirme zarfı. SW alanını kısa ve yerel tut; geniş bir anten oluşturma.
- O1_POWER:4.5mm, clearance0.20mm; `/O1_11V`.6A yalnız iz boyutlandırma zarfıdır; O1 yükü6A/5A olarak atanmadı,301ohm ayarı değişmedi.
- S2E_POWER:2.5mm, clearance0.20mm; `/S2E_11V`.3.2A yönlendirme zarfı.
- AUX_LOCAL:0.5mm, clearance0.20mm; CBOOT1/2, bunların iki adsız ara ağı, SW4_PH1/2, VCAP, GATE, VCC1/2, VDDA1/2.0.6A RMS hesap zarfı ve en çok10mm yol; gerçek darbe akımı/loop davranışı ayrıca doğrulanır.
- CONTROL_SENSE:0.25mm, clearance0.20mm; CONFIG, COMP, DVDT, EN, FB, ILIM, IMON, PG, RT ve SYNC ağları. Tam isimler `hardware/netclasses.csv` ve `.konnect/diagnostics/netclass-plan.json` içindedir.
- NC_DO_NOT_ROUTE: beş kasıtlı NC ağı. U1.10,U2.10,U2.7,U3.7,U4.7 uçlarına hiçbir iz/testpoint/GND bağı yapma. Sınıf adı bir DRC yasağı değildir; gerçek NC kuralı manuel korunmalıdır.
- Default:0.25mm/0.20mm; yalnız gelecekte sınıflandırılmamış sinyal için emniyetli geri dönüş. Mevcut46 ağın tümü yukarıdaki sınıflardadır.

Güç sınıfları via pad/drill1.2/0.6mm; diğerleri0.8/0.4mm. Bunlar geometridir, tek via için tam bara akımı onayı değildir. Akım taşıyan katman geçişinde minimum kaplama, via sayısı ve dağılımı hesaplanmalıdır. İnce IC termal via dizisi ayrı üretici çizimi/şablon incelemesi gerektirir.

## Hesabın sınırları ve açık karar

Bu teslimde yönlendirme tabanı canlı kartla aynı olan **35µm nominal dış bakırdır**. Eski70µm/2oz önerisi uygulanmış ayar sayılmaz; artık yalnız opsiyonel üretim yükseltmesidir. Genişlikler31.5µm hesap kalınlığıyla (%10 mühendislik payı),20°C iz sıcaklık artışı bütçesi,50°C ortam varsayımı ve70°C bakır özdirenciyle hesaplandı. Bu %10 pay üreticinin garantili toleransı olarak sunulmaz; siparişte en az31.5µm bitmiş bakır şartı doğrulanmalıdır. Ortam/yol/akım/bakır farklıysa hesap yenilenir.

Yöntem: IPC-2221 dış katman ampirik ön hesabı ve Ohm kanunu. Güç gövdesi başına en çok50mm uzunluk ve50mV düşüm hedefi seçildi. Seçilen genişliklerde tahmini düşümler giriş43.66mV, bara43.66mV, faz46.77mV, O143.66mV, S2E41.91mV. Tüm gidiş/dönüş yollarının düşümleri toplanır;50mV tüm sistem bütçesi değildir. Yerel ısınma, kapalı kutu, IC kaybı, pulse/SOA, kusurlu akım paylaşımı ve arıza I²t bu basit hesabın kapsamında değildir.

`python calculate_routing_rules.py` yalnız plan JSON'unu okur; KiCad kaynağına dokunmadan hesabı tekrar üretir. Sonuç: `hardware/routing-width-calculations.json`.

Giriş6A zarfı82.5W/(20V×%80 varsayılan verim)=5.156A hesabına pay bırakır; %80 ölçülmüş verim değildir. Faz5A zarfı7.5A toplamın3.75A/faz noktasına pay bırakır. Port zarfları nominal eFuse ayarlarını hard limit kabul etmez. Bunlar arıza-kesme/konnektör veya gerçek yük kabulü değildir.

## Router kullanımı

1. PDU proje ayarlarını kaydetmeden önce yeni dosya profilini koru: açık KiCad eski ayarları önbellekten geri yazabilir. Tüm PDU editörleri ve Proje Yöneticisi temiz kapatıldıktan sonra gerekirse `python .konnect/ApplyRoutingRules.py` çalıştır. Bu araç profili ve ek menü listesini yalnız Konnect MCP üzerinden tekrar uygular ve geri okur. Kilit varsa hiç yazmaz; kilit silmez. Ardından `PDU.kicad_pro` aç.
2. Board Setup → Design Rules → Net Classes altında9 sınıfı kontrol et. İz/via seçimini **Use netclass values** yap; yoksa seçili manuel genişlik sınıfı geçersiz kılar. İsteğe bağlı menü listesi açık kartta Konnect tarafından reddedildi; bu liste henüz yazılmış kabul edilmez. Yukarıdaki kapalı-proje aracı veya aynı menüden manuel giriş kullanılır.
3. Fine-pitch pad kaçışını kısa ve yerel yap; geniş güç gövdesini pad komşularının dışına çıktıktan sonra aç.0.20/0.25mm kaçış bir güç gövdesi yerine geçmez. Paylaşılan güç padleri, boyun uzunluğu, akım bölüşümü ve kayıplar ayrıca incelenir.
4. U1/U2 ISNS+ dallarını ilgili RS1/RS2'nin bobin tarafına, VOUT algısını şöntün çıkış tarafına ayrı Kelvin dalıyla bağla. Bunlar aynı güç ağı üzerinde0.25mm düşük akımlı dallardır; şönt üzerinden yük akımını bu dallara taşıma. FB/COMP/RT/IMON hatlarını SW altından ve gürültülü dönüşten uzak tut. GND ağını bölme; analog dönüş noktasını güç döngüsünden ayırarak aynı düzleme bağla.
5. Varsayılan genişliği elle daraltınca KiCad bunun akım kapasitesini otomatik denetlemez. DRC0 tek başına bu tasarımın elektrik/termal kabulü değildir. Bağlantı kapatılmadan dolgu veya üretim çıktısı ile sonuç gizlenmez.

## Senin tamamlaman gerekenler — öncelik sırası

1. **O1'i bağlamadan önce aşırı gerilim koruması:** O1 DC girişi5–12V; mevcut TPS259824O eşiği16.32–17.31V. Eski iki motor testinde tepe~16.89V; test başarısızlığı korunuyor. Ayrı gözetleyici/seri kesici çözümü henüz kabul edilmedi. VIN20–26V, sıcaklık/tolerans, hot-plug, yük adımı, kısa devre toparlanması ve buck üst anahtar kısa devresi dahil gerçek O1 uçlarında12V üstünün engellendiği gösterilmeli. Aday simülasyonu veya tipik gecikme tek başına yeterli değil.
2. **F1 ve giriş arızası:** gerçek DC sigorta/yuva MPN'si, DC kesme kapasitesi, zaman–akım eğrisi ve I²t seçilmeli.10A yazısı bir seçim değildir. Batarya+hat empedansından olası kısa devre akımı belirlenmeli; sigortanın DC kesme kapasitesi bunu karşılamalı. Sigorta/kablo/TVS/MOSFET koordinasyonu kapanmadan F1 footprint atanmaz veya sigorta tel ile köprülenmez.
3. **Ham COUT seçimi tamamlandı; döngü kabulü açık:** COUT1–8, TDK C5750X7S2A226M280KB22uF100V X7S2220 olarak şema ve PCB'ye işlendi. Özel padler deneme kartında doğrulandı; büyük kılıflar için COUTbankları açıldı ve REN1/2 sağa1.27mm alındı.25V adayının26V arızasına dayanmama problemi parça gerilim sınıfıyla giderildi; gerçek TVS aşımı/enerjisi onaylanmadı. Üretici modeli11V25°C'de164.98uF/banka ve400kHz'de1.9204mOhm/parça ESR verir.44/88uF eski hassasiyet testleri korundu;165uF ve257.66uF ek model testleri eklendi. Ortak davranış modeli yük adımlarının geçmesi gerçek faz marjı veya termal kabul değildir. Ayrıntı `hardware/COUT-qualification.md`.
4. **Tolerans ve UVLO:** RFB kesin MPN seçimi tamamlandı. Direnç sıcaklığı−40..125°C varsayımı ve75nA FB bias üst sınırı dahil statik hesap10.8333–11.1605V; dinamik/stabilite kabulü değildir. RUV180k/10k1% ve EN1.05V üst eşiğiyle20.3318V'a kadar kalkış gerekebilir; EN sızıntısının garantili üst sınırı yayımlanmamış.20V yeniden başlatma için batarya UVLO politikası ve sızıntı sınırı gerekir. IMON dirençleri806ohm yapıldı; nominal dönüşüm0.198276V/A. Yayımlanmış kazanç/sıcaklık aralığının15A üst değerlendirmesinde3.07165V hesabı3.3V altında. Bu,75°C üzeri veya kısa devre darbesi garantisi değildir. Bağlı ADC yoktur; S2E2.53A noktası üreticinin3A altı doğruluk garantisinin dışındadır.
5. **Gerçek yük ve arıza ölçümleri:** O1/S2E açılış, sürekli ve tepe akımlarını ölç;301/604ohm ayarlarını ölçülmüş yük veya garantili akım tavanı sanma. Tam sıcaklık ILIM ve fasttrip değerlerinin tipik/garantili ayrımını `hardware/schematic-independent-audit-20261019.md` açıklar. Bu sonuçlarla kablo, konnektör, sigorta ve termal sınırları doğrula.
6. **Üretim/mekanik:** LM70880 prototip bakır parçalama/stencil ve termal via onayı; bobin tam MPN land pattern'i; konnektör mating/polarite/kablo akımı; kutu delikleri/gerçek kart ölçüsü; ısıl denge ve loop kazancı gerekir. Mevcut72 parçanın yerleşim skoru bu kabul değildir.
7. **Araçta kalan işler:** footprint referans/değer yazıları ve Description alanı mevcut Konnect API'sinde düzenlenemiyor; D1–D3 refresh'te desteklenmeyen `unlocked` alanı var. Bunları Konnect düzeltmesiyle kapat. COUT değişimi sonrası PCB DRC197unrouted/301uyarı; bakır kısa devresi/clearance/courtyard çakışması yok. Bu uyarılar gizlenmedi. Açık editörün kayıt işlemi proje sınıflarını eski önbellekten geri yazabiliyor; son PCB kaydından sonra9sınıf46ağ tekrarKonnectile uygulanır. Temiz kapatmadan sonra `.konnect/ApplyRoutingRules.py` tekrar uygulama aracını kullan.

## Kanıt ve kaynaklar

- `.konnect/diagnostics/schematic-finish-checks.json`, `schematic-finish-parity.json`, `schematic-titleblock-clearance.json`: şema, netlist eşliği ve metin açıklıkları.
- `.konnect/diagnostics/netclass-evidence.json`: önce/sonra kayıt,46 ağ ataması ve kaydedilmiş proje kaynağı. `hardware/netclasses.csv`: okunur sınıf dökümü.
- TI SNVA766 §11: https://www.ti.com/lit/an/snva766/snva766.pdf (ampirik iz ön hesabı). Üretim geometrisi referansı: https://jlcpcb.com/capabilities/pcb-capabilities/ . Bunlar bu kartın sipariş/termal onayı değildir.
- KiCad10 netclass davranışı: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html . Netclass genişliği varsayılandır; minimum/maksimum DRC genişliği ile aynı değildir.

Commit/push yok; kaynak dosyalara metin düzenlemesi yok. Koruma problemleri geçti veya bütün fiziksel belirsizlikler yok oldu iddiası yapılmıyor: kalan kararların nedeni, girdisi ve kabul ölçütü yukarıda ayrı ayrı belirtilmiştir.
