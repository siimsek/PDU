> **SUPERSEDED (G3, 2026-11-07) → docs/START-HERE.md ve reports/g2/.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# IDA PDU — güncel teknik tasarım

19 Ekim2026. Kaynaklar: ana KiCad projesi, Konnect export'u ve doğrulanmış BOM. Eski hesap/karar metni [arşivde](archive/design-before-calculation-sync-20261019.md) korunur. Güncel devam noktası [PROJECT-STATE](PROJECT-STATE.md), özel parça kabulü [kontrol listesi](REVIEW-CHECKLIST.md).

## Gereksinim ve mimari

- Giriş tasarım zarfı20–26 V,6S LiPo. Nominal kaynak22,2 V; gerçek batarya/kablo transienti ve hata empedansı kesinleştirilmedi.
- Ortak11 V/7 A/77 W hedef; iki fazlı güç katı kapasite hedefi7,5 A. Bu değerler ölçülmüş O1/S2E yükleri değildir.
- J1 → F1 → LM74700/Q1 ters polarite/ideal diyot → VIN → iki LM70880 ortak VOUT → iki TPS259824O ile O1/S2E portları.
- Motor/ESC besleme kapsam dışı. F1 kesin MPN/yuva ve koordinasyonu açık.

## İki faz ve kontrol

- U1/U2=LM70880QRRXRQ1. COMP/EN/VOUT ortak; U1 SYNCOUT → U2 SYNCIN. CONFIG54,9k/90,9k; RT1/2=49,9k. Denklemle yaklaşık435,066 kHz; önceki veri sayfası tablo dayanağı400/440/480 kHz. Tolerans/koşul kabulü ayrı.
- L1/2=6,8 µH; RS1/2=7,5 mΩ. Eşit paylaşımda7,5 A toplam için3,75 A/faz.400 kHz/26 V'da nominal tepe4,917 A;−20% L varsayımında5,208 A. Bunlar sürekli durum hesabı; kısa devre/akım algılama gecikmesi sınırı değildir.
- RFB1=130k ERA3AEB134V, RFB2=10,2k ERA3AEB1022V;0,1%,≤25 ppm/K. Nominal hedef10,99608 V. Statik referans/tolerans/TCR/bias hesabı10,8333–11,1605 V; dinamik kabul değildir.
- RCOMP=9,53k, CCOMP=4,7 nF, CHF=47 pF kuruludur. Bu seçim88 µF kabulüyle önceki40 kHz crossover hesabına dayanıyordu. Yeni Ceff için gerçek döngü kararlılığı hâlâ açık; hesapta çıkan alternatif dirençler şemaya uygulanmış sayılmaz.
- RBOOT1/2=1 Ω, CBOOT1/2=47 nF; VCC4,7 µF/VDDA100 nF yerel bypass değerleri. Bootstrap ve gerçek yerleşim davranışı ortalama modelle kanıtlanmaz.

## Ham çıkış kapasitörleri

COUT1–8=TDK C5750X7S2A226M280KB22 µF100 V X7S2220. Eski25 V Murata adayı değiştirilmiştir. Özel footprint prototip kabulünden sonra şema/PCB'ye aktarılmıştır.

- Nominal toplam176 µF. Üretici bias modeli11 V/25°C'de164,9775 µF verir; bu tipik karakterizasyondur.
- İlk tolerans/ısı ve ayrıca varsayılan10% yaşlanma duyarlılığıyla92,6514 µF hesabı bir garanti değildir.
- Ortak modelde44/88 µF eski düşük kapasite taramaları korundu;165 µF ve nominal tolerans/ısı üst zarfı257,664 µF senaryoları eklendi.
- Üretici modelinin400 kHz ESR'si1,9204 mΩ/parça. Ortak davranış devresindeki ideal kapasitör taraması tam üretici frekans modelinin karşılığı değildir.
- 100 V sınıfı varsayılan53,3 V giriş clamp zarfının üzerindedir. Gerçek overshoot/enerji, döngü veya termal kabulü sağlamaz.

Ayrıntı: [COUT qualification](../hardware/COUT-qualification.md), [fiziksel kabul](../hardware/validation/c5750/physical-acceptance.md).

## Port koruma ve izleme

- U3/U4=TPS259824ONRGET. RILIM1/2=301/604 Ω; nominal kesme eşiği4,9605/2,5272 A. Gerçek yük, garantili akım tavanı veya tam sıcaklık interpolasyonu değildir.
- RIMON1/2=806 Ω ERA3AEB8060V;0,1%,≤25 ppm/K. Dönüşüm0,198276 V/A; nominal tripte O1~0,98355 V, S2E~0,50109 V. Eski2,61k/4,99k seçimi geçersizdir.
- IMON maksimum kazanç değerlendirmesi yalnız yayımlanmış3 A..min(15 A,ILIM),−40..75°C aralığındadır. S2E nominal tripi3 A altında; burada doğruluk garantisi verilmez. Harici ADC bağlı değil.
- EN bölücüsü64,9k/10k; tipik açılış8,988 V. PG100k/18k bölücüsü11 V'ta1,678 V; alıcı mantık eşiği kabulü yok. DVDT1/2=1 nF, tipik4,6 V/ms; gerçek yük/SOA kabulü açık.
- **O1 OVP başarısız:** mevcut16,9 V eFuse eşiği12 V O1 sınırını sağlamıyor; iki motor16,89 V tepe veriyor. LTC4365 adayı da bütün taramaları geçmedi ve ana devreye aktarılmadı.

## Giriş ve UVLO

- Q1=BSC160N10NS3G; U5 LM74700, giriş bypass22 nF. D1 SMCJ33A. Sigorta/TVS/kablo/MOSFET hata enerjisi ve SOA koordinasyonu açık.
- RUV180k/10k: tipik açılış19 V, tipik kapanış17,1 V.1% direnç ve0,95..1,05 V eşik taraması17,7114..20,3318 V açılış verir. Bu sonuç EN sızıntısı/TCR içermiyor;20 V yeniden kalkışı garanti etmiyor. Batarya kesme politikası ayrıca belirlenmeli.

## PCB ve üretim durumu

72 footprint ve geçici101,6×76,2 mm sınır; iz0. Son kayıt DRC197 unrouted/301 uyarı; bakır açıklığı/courtyard hatası raporlanmıyor. U1/U2 bakır yaklaşımı, paste/termal kabulü; Q1 stock land uyarlaması; bobin exact-MPN land ve konnektör eş/polaritesi açık.

Bakır tabanı35 µm nominal; iz ön hesabı31,5 µm mühendislik payı kullanır.70 µm opsiyonel üretim yükseltmesidir.9 sınıf/46 ağ ataması vardır; sınıf genişliği akım veya minimum DRC sınırı garantisi değildir. [Yönlendirme sınırları](SON-TESLIM.md).

## Hesap ve kanıt

`calculate.py` güncel export/BOM değerlerini okur; [hesap özeti](../hardware/calculation-summary.json) bu girdilere hash ile bağlıdır. Veri sayfası sabitleri,1% gibi boş alan varsayımları ve önceki kontrol denklemi girdileri açık etiketlenir. Üretici verileri ve araştırma bağlantıları [önceki ayrıntılı kayıtta](archive/design-before-calculation-sync-20261019.md) korunur.

[Doğrulama durumu](verification.md):24 senaryo/48 koşu,512 geçen/2 başarısız O1 kontrolü. Gerçek LM70880 iç döngüsü, bootstrap/SOA/termal/EMI veya üretim kabulü tamamlanmadı.
