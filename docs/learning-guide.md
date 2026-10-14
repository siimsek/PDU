# Uygulayarak öğrenme rehberi

Bu rehber, IDA_PDU üzerinde gerçek mühendislik işi yaparken öğrenmeyi düzenler. Her oturum şu sırayı izler: **problem → gereken bilgi → seçenekler → öğrencinin hesabı/kararı → teknik kontrol → uygulama → doğrulama → sonraki adım**. Önce küçük bir görev verilir; cevap anahtarı baştan dökülmez. Varsayım, üretici verisi, hesap, simülasyon ve ölçüm birbirinden ayrı tutulur.

## Proje tabanı

- 6S LiPo; ön tasarım hesabı 20–26 V, nominal 22.2 V.
- O1 ve RPLIDAR S2E için tek 11.0 V senkron Buck barası ve iki ayrı korumalı port.
- TI LM70880-Q1 ve TPS259824 eFuse parçaları adaydır; kesinleşmiş parça listesi değildir.
- İlk talep 7 A / 77 W idi. Ön çalışma 78 W katalog değerlerine dayalı planlama zarfı nedeniyle geçici 7.5 A / 82.5 W hedef kullanıyor. Gerçek yük ölçümü olmadan ikisi de kesinleşmez.
- Motor/ESC beslemesi ve diğer yükler kapsam dışıdır. ESC kaynaklı giriş transienti ve EMI tasarım girdisidir.

## İlk 20–30 dakikalık görev

1. O1'in tam kart kimliğini bul; üretici etiketi/kılavuzuyla giriş gerilimi ve soket/polarite bilgisini kaydet. Bulunmayan alanı açık soru olarak bırak.
2. T3 donanım deposundaki 5–12 V / 5 A bilgisini ve ArduPilot sayfasındaki 5–12 V / 3 A bilgisini yan yana yaz. 5 A kapasitenin gerçek tüketim olmadığını belirt.
3. S2E veri sayfasından 9–28 V aralığını, 12 V'taki 1.2 A tipik / 1.5 A üst kalkış değerini ve 0.2 A tipik / 0.22 A üst çalışma değerini aktar. 11 V açılış akımını bilinmiyor olarak işaretle.
4. Varsayımsal güç zarfı için P=VI, ardından I=P/11 V hesabını yap. Hangi girişlerin katalog sınırı, hangilerinin varsayım olduğunu yaz.
5. En az üç açık soru ve bunları kapatacak ölçüm/kaynak adımını listele.

İlk görev teknik rehberde hazır hesapla cevaplanmaz; öğrenci kendi sonucu ve kaynaklarıyla geldikten sonra birlikte kontrol edilir.

## Uygulama sırası ve geçiş ölçütleri

1. **Gereksinim ve kaynak:** kart kimliği, batarya aralığı, soketler, kablo, ortam ve ESC transientlerini kaynak/varsayım/açık soru olarak sınıflandır.
2. **Yük profili:** her cihazın açılış, sürekli ve geçici akımını ayrı ve eşzamanlı koşullarda ölçecek güvenli düzenek ve kayıt hızını tanımla.
3. **Güç bütçesi:** 20, 22.2, 25.2 ve 26 V girişleri; verim senaryoları; cihaz sınırı ile gerçek tüketim farkını hesapla. Kaynak kodu `calculate.py` başlangıç örneğidir.
4. **Topoloji ve kontrolcü:** senkron/asenkron Buck ve anlamlı alternatifleri kayıp, giriş aralığı, termal, EMI, maliyet ve uygulanabilirlikle karşılaştır.
5. **Koruma:** giriş sigortası, TVS, ters kutup, eFuse akım limiti, fault davranışı ve kablo sınırlarını ölçülen profile göre koordine et.
6. **Güç katı:** duty, endüktör ripple/tepe akımı, DC-bias altında etkin kapasite, geri besleme ve kompanzasyonu üretici verileriyle hesapla.
7. **BOM ve maliyet:** her pozisyon için MPN, footprint, rating, adet, kaynak, tarih ve Türkiye teslim maliyetini kaydet.
8. **Elektriksel şema:** pin/net, fault/PG, test noktaları, konnektör ve BOM referanslarını KiCad'de çiz; ERC sonucunu ekle.
9. **Simülasyon:** mümkünse üretici makromodelini kullan; değilse model sınırını yaz. Kalkış, giriş süpürmesi, yük adımı ve arıza koşullarını incele.
10. **PCB:** sıcak akım döngüsü, geri besleme, Kelvin algılama, bakır, termal yollar, üretici kuralı ve DRC üzerinde çalış.
11. **Prototip:** akım sınırlı beslemeyle kademeli bring-up yap; cihaz uçlarında gerilim/akım, transient ve sıcaklığı ham veriyle kaydet.
12. **Kapanış:** EMC/termal, koruma, Gerber, BOM ve yerel teklif kontrollerini kanıtla kapat. Açık gereksinim varsa sahibi ve sonraki adımı belli kalsın.

Elektriksel şema ve PCB tamamlanmadan prototip üretilmez. İdeal ortalama model gerçek entegre, EMI, kararlılık veya termal güvenlik kanıtı değildir. Ölçülmemiş sonuç üretim hazır gibi sunulmaz.

## Oturum ve karar kaydı

Her oturum sonunda doldur:

- Tarih/hedef:
- Üretici kaynağı ve belge tarihi:
- Kendi hesabım/şemam:
- Kanıt etiketi: `[KAYNAK] [HESAP] [SİMÜLASYON] [ÖLÇÜM] [VARSAYIM] [AÇIK SORU]`
- Öğrendiğim ve düzelttiğim:
- Kararım ve gerekçesi:
- Kararı değiştirecek veri:
- Sonraki küçük görev:

Bir tasarım kararı için ayrıca soru, seçenekler, kullanılan kaynak/model, varsayımlar, seçilen yol, açık risk ve kapatma ölçütünü yaz.

## Test kaydı alanları

Tarih/operatör; test amacı ve ID; kart kimliği; araç/kalibrasyon; giriş ve çıkış koşulları; yük durumu; bağlantı çizimi/fotoğrafı; ham veri; ölçüm band genişliği/belirsizliği; geçti/kaldı; sınır ve tekrar testi.
