# Çalışma Kuralları — güncel ilk aşama

Tek aktif dal `main`. Kullanıcı Claude/Codex'e işi doğrudan verir; thinker/builder, rol, kart ve röle düzeni yok.

**Aktif amaç:** `buck/PROJE-TANIMI.md` ve `buck/TASARIM-HESABI.md` kapsamındaki **yalnız açık çevrim, tek faz asenkron buck güç katı**. İdeal ve kayıplı simülasyonun ana dosyaları görsel, düzenlenebilir **`buck/buck-ideal.asc`** ve **`buck/buck-kayipli.asc`**; metin `.cir` bunların karşılaştırma kopyasıdır.

- Güç katı: DC kaynak, S1, D1, L1, CIN, COUT, RLOAD. Anahtar için LTspice PULSE sinyali kullanılır; **gerçek PWM üreteci devresi kurulmaz**.
- Elektronik PWM/PWM kontrolcü, op-amp, karşılaştırıcı, ayrık MOSFET sürücü, kompanzasyon, geri besleme, soft-start, ikinci faz, korumalar, PCB ve yeni özellikler **istenmeden eklenmez**.
- Eski LM70880/iki faz ve eski kontrolcü tasarımları `archive/` altında tutulur, yeni projenin aktif kaynakları değildir.
- Hesap ve simülasyonu, varsayımları ve fiziksel ölçümleri ayrı tut. Yeni LTspice koşusu yapılmadıysa tamamlandı/PASS denmez.
- Bileşen seçimi ve gerçek veri sayfası validasyonu daha sonraki adımdır. MPN, hesap, sonuç veya fiziksel test uydurulmaz.
- **O1 için 12 V üst sınırı mevcut Aşama 1'de garanti edilmez; gerçek O1 veya RPLIDAR S2E yükü bağlama.**
- Kullanıcı onayı olmadan sonraki aşamaya ilerleme veya gereksiz karmaşıklık ekleme.

LTspice Windows örnek yolu: `C:\Program Files\ADI\LTspice\LTspice.exe`. `python buck/hesap.py` ile hesap JSON'u; `python buck/ltspice_sina.py` ile Windows'ta gerçek `.asc` batch simülasyon sonuçları üretilir. Dosyalar UTF-8.
