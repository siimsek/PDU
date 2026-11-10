# Çalışma Kuralları — Buck güç katı

Tek aktif dal `main`. Kullanıcı işi doğrudan verir; thinker/builder, rol, kart veya röle düzeni yoktur.

**Aktif amaç:** [buck/PROJE-TANIMI.md](buck/PROJE-TANIMI.md) ve [buck/TASARIM-HESABI.md](buck/TASARIM-HESABI.md) kapsamındaki tek faz asenkron, açık çevrim buck güç katısını kullanıcıyla birlikte LTspice'ta sıfırdan kurmak.

- Devre kapsamı: DC kaynak, anahtar S1, serbest geçiş diyodu D1, bobin L1, giriş/çıkış kondansatörleri ve direnç yükü. Anahtar LTspice `PULSE` kaynağıyla sürülür; gerçek PWM üreteci kurulmaz.
- Yeni şematiği kullanıcıyla adım adım kur. Kullanıcı istemeden şematiği veya fiziksel parça modelini önceden oluşturma.
- PWM kontrolcü, op-amp, sürücü, geri besleme, kompanzasyon, soft-start, ikinci faz, korumalar, PCB veya başka özellik ekleme.
- Analitik hesap, varsayım, LTspice sonucu ve fiziksel ölçümü ayrı tut. LTspice çalıştırılmadıysa simülasyon tamamlandı/PASS deme.
- L, CIN, COUT ve frekans adaylarını aynı 11 V / 7,5 A / 82,5 W çıkış hedefinde karşılaştır. Kayıplı karşılaştırmada her çalışma noktası için duty'yi hedef çıkışa ayarla; bu, fiziksel geri besleme eklemek değildir.
- Verim sıralamasında gerçek parçalara ait anahtarlama, bakır/çekirdek ve ESR kayıplarını kullan. Ripple ön elemesini verim optimizasyonu diye sunma.
- Gerçek MPN/veri sayfası doğrulaması yapılmadan parça seçimini tamamlanmış sayma; değer, sonuç veya fiziksel test uydurma.
- Açık çevrim devre 11 V regülasyonu veya 12 V üst sınırını garanti etmez. Gerçek O1, RPLIDAR S2E ya da başka hassas yük bağlama.
- Bu temizlikte önceki devreler ve `archive/` kullanıcı isteğiyle kaldırıldı. Yeni arşiv oluşturma.
- Sonraki aşamaya yalnız kullanıcı istediğinde geç.

`python buck/hesap.py` referans noktasını hesaplar. `python buck/parametre_taramasi.py` sabit çıkış hedefinde analitik taramayı, `buck/tarama-sonuc.json` ve `buck/PARAMETRE-KARSILASTIRMA.md` dosyalarını üretir. Bu çıktılar LTspice veya laboratuvar sonucu değildir. Dosyalar UTF-8'dir.
