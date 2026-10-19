> 19 Ekim güncellemesi: kesin RFB parçaları,806ohm IMON ve100V COUT şema/PCB içinde işlendi. Güncel uygulama ve açık kabul maddeleri: [ölçümsüz tamamlamalar](hardware/No-measurement-closeout.md). O1 OVP kabulü başarısız; PCB yönlendirme/üretim kabulü tamamlanmadı.

# IDA_PDU

## Güncel durum — 2026-10-19

Güncel şema [PNG](PDU_schematic_finished.png) / [PDF](PDU_schematic_finished.pdf) olarak düzenlendi: short0, ERC0/0, açık pin/örtüşme0.46 ağın tamamına9 netclass üzerinden PCB iz genişliği/clearance/via ayarı kaydedildi. Hesap tabanı canlı kartla aynı35µm nominal bakırdır;31,5µm hesap payı kullanıldı,70µm varsayılmadı.72 parçalı prototip PCB yerleşimi var; yönlendirme yok. O1 OVP ve F1 dahil kalan işleri, araç sınırlarını ve kabul ölçütlerini [son teslim](docs/SON-TESLIM.md) tek yerde açıklar. Üretim onayı yok.

6S LiPo bataryadan tek bir 11 V Buck barası üretip T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'yi ayrı korumalı çıkışlardan besleyecek bitirme projesi. Repo, tasarım kararlarını, hesapları, simülasyonu ve doğrulama kanıtlarını tek sade yerde tutar.

**GitHub kaynak deposu:** [IDA_PDU — siimsek/PDU](https://github.com/siimsek/PDU) (Private, `main`).

## Projede yapılacaklar

- Kartların giriş sınırlarını ve gerçek akım profillerini kaynak ve ölçümle netleştirmek.
- 11 V ortak güç katını, giriş ve port korumasını hesaplamak ve gerekçelendirmek.
- KiCad elektrik şeması/PCB'sini çizmek; ERC/DRC ve üretim dosyalarını incelemek.
- Hesapları ve uygun modelleri simüle etmek; prototipte gerilim, akım, transient, termal ve arıza davranışını ölçmek.
- BOM, tedarik ve yerel üretim maliyetini gerçek tekliflerle tamamlamak.

## Kapsam dışında

Motor/ESC ve başka yükleri beslemek bu PDU'nun işi değil. ESC'den gelen giriş transienti ve EMI, PDU tasarımında dikkate alınacak sistem girdileridir. Prototip ve ölçüm kanıtları olmadan güvenli, EMC uyumlu veya üretime hazır olduğu iddia edilmeyecek.

## Mevcut durum ve ilk görev

**Açık kritik hata:** Mevcut eFuse'un 16.9 V OVP eşiği O1'in belgelenen 12 V giriş üst sınırını korumuyor. Düzeltilmiş ortak modelde iki motor da yaklaşık 16.89 V tepe gösterdi. Koruma düzeltilip doğrulanmadan O1 bağlanmayacak ve üretim onayı verilmeyecek. MCP/API çalışıyor; prototip yerleşim yapıldı, koruma kabulü tamamlanmadı.

Elektrik şemasındaki eksik bootstrap dirençleri ve LM74700 giriş kondansatörü eklendi; PG bölücüleri düzeltildi. Güncel şema 77 sembol içerir. LTspice/ngspice için aynı Konnect netlistinden üretilen ortak devre ve testler `simulation/` içindedir. Güncel sonuçlar `simulation/results.md`, makine tarafından denetlenen kabul sonuçları `simulation/verification-results.json` dosyasındadır. PCB ayak izleri, gerçek yük ölçümleri ve termal/EMC doğrulaması henüz tamamlanmadı.

T3'ün güncel O1 güç bağlantısı belgesi ve `t3gemstone/hardware` deposu DC giriş için 5–12 V / 5 A bilgisinde uyuşuyor. Bu rating gerçek tüketim değildir. O1 ve S2E'nin açılış-sürekli akım profilleri ölçülmedi. Mevcut 301 Ω / 604 Ω koruma dirençleri değişmedi; nominal kesme eşikleri yaklaşık 4.96 A / 2.53 A'dır.

**Çıkış gereksinimi:** 11 V / 7 A / 77 W; güç katı için 7.5 A kapasite hedefi. İki LM70880-Q1 ortak COMP ve 180° senkronizasyonla paralel tek baraya bağlıdır. Modeldeki 3 A O1 / 1.5 A S2E yükleri test uyaranlarıdır; ölçülmüş cihaz akımları değildir. Yeni kullanıcı izniyle U1–U4 prototip footprintleri atandı;72 parça aktarıldı. F1 footprint/MPN seçimi bekliyor.

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
