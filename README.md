# IDA_PDU

6S LiPo bataryadan tek bir 11 V Buck barası üretip T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'yi ayrı korumalı çıkışlardan besleyecek bitirme projesi. Repo, tasarım kararlarını, hesapları, simülasyonu ve doğrulama kanıtlarını tek sade yerde tutar.

## Projede yapılacaklar

- Kartların giriş sınırlarını ve gerçek akım profillerini kaynak ve ölçümle netleştirmek.
- 11 V ortak güç katını, giriş ve port korumasını hesaplamak ve gerekçelendirmek.
- KiCad elektrik şeması/PCB'sini çizmek; ERC/DRC ve üretim dosyalarını incelemek.
- Hesapları ve uygun modelleri simüle etmek; prototipte gerilim, akım, transient, termal ve arıza davranışını ölçmek.
- BOM, tedarik ve yerel üretim maliyetini gerçek tekliflerle tamamlamak.

## Kapsam dışında

Motor/ESC ve başka yükleri beslemek bu PDU'nun işi değil. ESC'den gelen giriş transienti ve EMI, PDU tasarımında dikkate alınacak sistem girdileridir. Prototip ve ölçüm kanıtları olmadan güvenli, EMC uyumlu veya üretime hazır olduğu iddia edilmeyecek.

## Mevcut durum ve ilk görev

Mimari, ilk hesaplar, aday BOM, işlevsel blok çizimi ve ideal ortalama Buck simülasyonu hazır. Elektriksel şema, PCB, gerçek yük ölçümleri, termal/EMC doğrulaması ve yerel maliyet henüz tamamlanmadı.

İlk iş O1 kartının tam kimliğini/güç girişini doğrulamak ve O1 ile S2E'nin açılış-sürekli akım profillerini ölçmek. O1 için kaynaklarda 5 A ve 3 A sınırları çelişiyor; kapasite gerçek tüketim olarak alınmayacak. Ölçüm bitmeden port limitleri ve nihai güç sınıfı sabitlenmeyecek.

**Başlangıç gereksinimi:** 11 V / 7 A / 77 W. **Geçici planlama hedefi:** 11 V / 7.5 A / 82.5 W. Bu, katalog sınırlarından oluşturulmuş ölçülmemiş bir üst zarf varsayımıdır.

## Dosyalar

- `docs/design.md` — tek teknik tasarım kaynağı, kararlar ve açık riskler.
- `docs/learning-guide.md` — öğrenme sırası ve ilk görev.
- `docs/verification.md` — kanıt ve açık maddelerin durumu.
- `docs/test-plan.md` — prototip doğrulama adımları.
- `hardware/` — BOM, blok diyagramı ve yalnızca işlevsel blokları gösteren KiCad sayfası.
- `simulation/` — LTspice kaynak modeli, yeniden üretilebilir metin logu ve sonuç özeti.
- `calculate.py` — ilk mertebe güç bütçesi hesabı.

## Çalışma düzeni

Her oturumda önce açık maddeleri oku; tek bir sonraki küçük görevi seç; üretici kaynağını, hesabı, simülasyonu, ölçümü ve varsayımı ayrı etiketle. Yeni kanıt geldikçe tasarım, doğrulama tablosu ve öğrenme kaydını birlikte güncelle. İlerleme kaynağa eklenip sürüm geçmişinde izlenecek. Ana dosya ve oturum düzeni bu klasörde kalır.
