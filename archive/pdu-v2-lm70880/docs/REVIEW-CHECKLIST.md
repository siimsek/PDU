> **SUPERSEDED (G3, 2026-11-07) → reports/g2/DESIGN-RULES.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# Kullanıcının kontrolü: kalan işler ve özel hazırlanan parçalar

19 Ekim2026. Kullanıcının “kesin olarak ne kaldı, hangi parçaları kendin hazırladın veya tasarımından emin değilsin?” sorusunun kontrol kaydı. **Önce O1 korumasını ve U1/U2 footprintini incele.**

## A. Kesin kalan işler

- [ ] **O1 OVP:**12 V üst sınır sağlanmalı. Mevcut eFuse yaklaşık16,9 V'ta kesiyor; iki motor16,89 V tepe gösteriyor. Yeni mimari bütün tolerans/gecikme/arıza senaryolarıyla kabul edilmeli. Mevcut LTC4365 adayı aktarılmadı; bir köşede12,4055 V gördü.
- [ ] **Gerçek döngü kararlılığı:** RCOMP9,53 kΩ/CCOMP4,7 nF/CHF47 pF, iki faz ve yeni çıkış bankasıyla kazanç/faz marjı açısından doğrulanmalı. Davranış modelindeki yaklaşık iç döngü yeterli kanıt değil.
- [ ] **Kesin BOM:**57/73 MPN alanı boş. Kod, değer, tolerans, TCR, gerilim/güç, paket ve footprint eşliği tamamlanmalı. Q1 gibi bazı kesin kodlar zaten Value alanında bulunuyor.
- [ ] **F1:**10 A yazısı onaylanmış sigorta seçimi değil. Batarya/kablo hata akımı, DC kesme kapasitesi, zaman-akım/I²t ve TVS/MOSFET koordinasyonu gerekiyor. MPN/footprint boş.
- [ ] **UVLO:** İstenen açma/kapama politikası belirlenmeli. Mevcut oran20 V'ta yeniden kalkışı garanti etmiyor; tolerans hesabı20,3318 V'a çıkıyor, garantili EN sızıntı üst sınırı bulunmadı.
- [ ] **PCB:** Güç döngüleri, Kelvin algılama, sürekli toprak, termal vialar, yönlendirme ve üretilebilir yazılar tamamlanmalı. İz0;197 unrouted hata/301 uyarı var.
- [ ] **Mekanik/arayüz:** Geçici101,6×76,2 mm ölçü, kasa/delikler, konnektör eşleri, polarite, kablo akımı ve ortam sıcaklığı kesinleştirilmeli.
- [ ] **Fiziksel kabul:** Gerçek açılış/sürekli/tepe yükleri, O1 ucunda transient gerilim, döngü/paylaşım, sıcaklık, EMI ve sigorta/TVS arıza enerjisi doğrulanmalı.

İlk maddelerde ölçümsüz tasarım işi hâlâ yapılabilir. F1/mekanik için eksik sistem girdileri vardır; bunların tümü zorunlu olarak ölçüm gerektirmez. Fiziksel kabul ise simülasyonla kapanmaz.

## B. Özel çizilen veya uyarlanan KiCad temsilleri

Gerçek üretici parçaları için özel sembol/ayak izleri hazırlandı. Aşağıdaki prototip kabulü; lehimleme, stencil, termal veya üretim onayı anlamına gelmiyor.

### U1/U2 — en önemli geometrik inceleme

- Gerçek parça **TI LM70880QRRXRQ1**, RRX0029B. Özel sembol `PDU:LM70880QRRXRQ1`; footprint `PDU:LM70880_RRX0029B_RectLands`.
- Konnect özel şekilli pad desteklemediği için VIN/SW güç bakırı üst üste binen küçük dikdörtgenlerle yaklaşık temsil edildi.30 mantıksal pin numarası için406 pad nesnesi var.
- Üretici PDF vektörüne karşı bakır sınırı farkı<0,007 mm, alan fazlası<%0,35 ölçüldü. **Birebir üretici CAD'i değildir.** Daraltılmış VIN paste açıklığı özellikle incelenmeli.
- Kontrol: pin1/yön, VIN-SW-PGND ayrımı, tekrar eden aynı numaralı padlerin ağı, PGND pad30, paste/stencil ve termal via düzeni.
- [Pin/pad ve yaklaşım kaydı](../hardware/validation/power-ics/LM70880-pinmap-acceptance.md). Kaynak: [TI datasheet](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf), pinler3–4, çizimler51–53.sayfalar.

### U3/U4 — iki exposed pad ayrımı kritik

- Gerçek parça **TI TPS259824ONRGET**, RGE0024M. Özel sembol `PDU:TPS259824ONRGET`; footprint `PDU:TPS25982_RGE0024M`.
- 24 çevre uç + iki elektriksel exposed pad var: **25=IN,26=GND**. Bunlar tek ortak termal pad yapılamaz.26 numaralı bakır pad ve dört numarasız paste açıklığı kullanıldı.
- Pin/pad eşliği ve boyutlar üretici çiziminden deneme kartında doğrulandı. Termal via/stencil kabulü açık. Doğru footprint,16,9 V OVP'nin O1 için yetersiz olmasını çözmüyor.
- [Kabul kaydı](../hardware/validation/power-ics/TPS25982-pinmap-acceptance.md). Kaynak: [TI datasheet](https://www.ti.com/lit/ds/symlink/tps25982.pdf), pinler5, mekanik55–57.sayfalar.

### Q1 — stock ayak izinden uyarlama

- Gerçek parça **Infineon BSC160N10NS3 G**, PG-TDSON-8. Stock sembol `Transistor_FET:BSC160N10NS3G`; uyarlanan footprint `PDU:TDSON-8-1_Konnect`.
- Stock bakır/paste korundu; desteklenmeyen mask-only şekil dolu maske dikdörtgenleriyle temsil edildi. Fiziksel1/2/3=source,4=gate,5–8 ve exposed drain ortak mantıksal pad5.
- Seçili stock land, eski üretici önerisinin birebir kopyası değil. **Üretim land-pattern incelemesi açık.**
- [Q1 kabul kaydı](../hardware/validation/ltc4365/BSC160-pinmap-acceptance.md).

### COUT1–8 — üretici önerisinden özel footprint

- Gerçek parça **TDK C5750X7S2A226M280KB**,22 µF100 V X7S2220. Stock `Device:C` sembolü; özel footprint `PDU:TDK_C5750_2220_Recommended`.
- Her pad1,30×4,50 mm; merkezler arası5,75 mm, iç boşluk4,45 mm. Üretici land aralıklarına göre seçildi; deneme kartı render/canlı geri okuması yapıldı.
- Courtyard7,85×6,20 mm; maksimum parça yüksekliği3,1 mm.3D model yok. İki uç kutupsuz ve eşdeğer; stencil/mekanik/flex-crack/reflow kabulü açık.
- [Fiziksel kabul](../hardware/validation/c5750/physical-acceptance.md), [kapasite/ESR ve üretici modeli](../hardware/COUT-qualification.md).

### Ana kartta olmayan denemeler

`hardware/validation/ltc4365/` ve `simulation/candidate-*` koruma adayları/deneme projeleridir. `CSD18534Q5A_Q5A` footprinti ve LTC4365 çalışmaları ana devreye kabul edilmiş bir koruma katı değildir. Altı bulk kapasitörlü bir eski koşu da arıza öncesi yerleşmediği için geçerli kabul edilmedi. Bu dosyalardan sonuç seçip tamamlanmış devre gibi kullanma.

## C. Kendim yazdığım yaklaşık simülasyonlar

Ortak [pdu-behavioral.lib](../simulation/pdu-behavioral.lib) içinde LM70880, TPS25982 ve LM74700/Q1 davranışları ile genel diyot/TVS modelleri mühendislik yaklaşımı olarak yazıldı. Bobin için açık23,3 mΩ DCR varsayımı ve kapasite için CBIAS hassasiyetleri kullanılıyor. Bunlar üretici silikon modellerinin tam karşılığı değildir.

Bu modellerle48 koşunun512 kontrolü geçmesi; gerçek iç döngü, propagation delay, bootstrap, SOA, EMI veya termal onayı sağlamaz. İki O1 kontrolü hâlâ başarısız. Ayrı çalışmada gerçek TDK bias modeli değiştirilmeden kullanıldı; LTC4365 adayında native üretici kontrolcü modeliyle yaklaşık MOSFETler birlikte kullanıldı.

## D. İnceleme sırası ve kabul kaydı

1. O1 koruması: gereksinim → worst-case hesap → model → pin/pad → bütün arıza testleri.
2. U1/U2 karmaşık ayak izi: TI çizimleri → bakır/paste → termal/üretici incelemesi.
3. U3/U4 exposed padleri ve Q1 land önerisi.
4. Gerçek MPN/BOM ve mekanik/konnektör/polarite eşliği.
5. Kontrol döngüsü ve ardından PCB yönlendirme/üretim incelemesi.

Bir maddeyi kapatırken tarih, kaynak/revizyon, tam parça kodu, yapılan kontrol, sonuç ve kalan sınırı yaz. Güncel [bağımsız denetim](../hardware/no-measurement-final-audit.md) ve [devam noktası](PROJECT-STATE.md) birlikte güncellensin.
