# PDU geliştirme kuralları

- [Yol haritasını](YOL-HARITASI.md) ve Git durumunu okuyarak başla. STM32 çalışmasını `stm32-digital-buck` dalında sürdür. `ANA-GUC-DEVRESI` ve açık çevrim etiketini koru. Uzak `main` geçmişi için ayrıca açık kullanıcı onayı gerekir.
- Esas devre tek fazlı asenkron buck ve yükler modüler çıkış zarfıyla tanımlanır. Güç katı referansı `6879e87` sürümüdür. Şematik, analitik hesap ve tarihî LTspice koşuları ilgili kanıtlardır. Parça ve değer değişiklikleri için ölçülebilir uyumluluk gerekçesi ve regresyon gerekir.
- Güç şematiğini değiştirmek gerekirse `buck/ltspice/sematik_uret.py` ile ASC/SVG yeniden üretilir. Hesap, netlist ve yeni modellerin değer uyumu sınanır.
- Araştır, hesapla, modelle, uygula, test et, doğrula ve gerekirse optimize et. Aşama geçişinde kritik testleri çalıştır. Açık hataları, model sınırlarını ve sonraki kapıyı yol haritasında güncelle.
- Windows 11 ve CachyOS için aynı kaynaklar ve Python/CMake giriş noktaları kullanılır. Göreli yollar ve UTF-8 kullan. Yerel ortam ve derleme çıktıları Git dışında kalır.
- Üretici açıklamasını, hesabı, simülasyonu, varsayımı ve fiziksel ölçümü ayrı ayrı belirt. Ölçütü başarısız bir koşuyu geçirmek için gevşetme. Çalıştırılan platformu ve araç sürümünü kaydet.
- Firmware kapı sürüşü, tanımlı donanım kilitleri ve fiziksel doğrulama tamamlanana kadar güvenli durumda tutulur. Prototipte bağımsız akım sınırı ve aşırı gerilim kapatma yolu sınanır.
