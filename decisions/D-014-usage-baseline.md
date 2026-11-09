# D-014 — IDA PDU için geçici kullanım ve tasarım temeli

- **Kart:** `tasks/D-014.md`; **durum:** Review.
- **Kaynak:** `reviews/R-025.md`; main `c69c77cf529c8d7698f7a8c7b4448b8e7f59d601`.

## Soru
Sistemden gelen profil alanları henüz tamamlanmadığında teknik iş, standart kapsamı ve şema/simülasyon nasıl yürütülsün?

## Seçenekler
1. Araç boyu, montaj ve test seviyelerini gerçekmiş gibi belirlemek: RED.
2. Bütün mühendisliği kullanıcıdan açıklama bekleyerek durdurmak: RED; kullanıcı yalnız fiziksel işler üstlenir.
3. Kaynaklı devre girdilerini kullanıp deniz tehlikelerini ihtiyatlı tasarım varsayımı olarak işaretlemek, sayısal ve yasal bilinmeyenleri AÇIK izlemek: SEÇİLDİ.

## Karar — geçici temel
- **OLGU:** `docs/START-HERE.md:1,5` IDA PDU, 6S LiPo, 20–26 V giriş ve ortak 11 V/7,5 A tasarım hedefini verir. `README.md:3` O1 yükünü T3 Gemstone O1, S2E yükünü SLAMTEC RPLIDAR S2E olarak adlandırır. `tasks/BLOCKED-ON-USER.md:20` O1 için motor/ESC kalkışından bahseder; bunun sevk motoru olduğu gösterilmez.
- **VARSAYIM:** İnsansız deniz aracı senaryosunu tasarım riski olarak kabul et; su sıçraması, yoğuşma, tuz, titreşim ve giriş transiyentlerini göz ardı etme. Bunlar seçilmiş test şiddeti, ortam sınıfı, IP derecesi veya denizde işletim kanıtı değildir.
- **OLGU/VARSAYIM:** `reports/g2/BENCH-ACCEPTANCE.md:31` 50 °C termal test koşulu ve 125 °C Tj hedefi içerir; `analysis/g2/params.py:65` 85 °C tarama varsayımıdır. 85 °C taramasındaki FAIL ve sınırların durumu korunur; 50 °C hedefinin tek gerçek servis koşulu olduğu varsayılmaz.
- **AÇIK:** Tekne tipi/boyu ve hangi ülke/kural, yüklerin sevkle ilişkisi, kapalı muhafaza, gerçek sıcaklık/nem/tuz/titreşim spektrumu, batarya kimliği, kapasite ve yanıcı gaz atmosferi. Bu alanları var olmayan kullanıcı veya üretici onayıyla kapatma. Elde edilebilen repo/belge kaynakları, mühendislik analizi ve daha sonra fiziksel testlerle ilerle.
- **Kapsam kararı:** ISO 13297/16315/8846 ve IEC deniz/EMC standartları için gerçek sistem sınıfı ve sözleşme AÇIK olduğundan uygulanabilirlik koşulludur; “uygun” veya “uygulanmaz” kesin beyanı verilmez. ISO 9001 kuruluş QMS'idir.
- **Sıra:** T-050 güç/BIAS hesabı düzeltmesi; T-051 eFuse dVdt modeli; T-052 VCAP/gate model tanımı; T-028/T-032 diğer envanter grupları paralel. T-038 iki F5 sonucu ayrı kanıttır. Fiziksel PCB routing bekler.

## Sınırlar
Bu karar çalışma varsayımıdır; sertifikasyon, test seviyesi veya fiziksel başarı kanıtı değildir. Karar alınan varsayımın gerçek dünyada teyidi olmadan kesin sevk ve standart sınıfı seçilmez. Mevcut elektriksel güvenlik sınırları ve kayıtlı FAIL'ler gevşetilmez.
