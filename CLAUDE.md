# Çalışma kuralları

Kullanıcı Claude'a veya Codex'e istediği işi doğrudan söyler, ajan onu yapar. Thinker/builder rolü, görev kartı ve röle düzeni yoktur. Tek dal `main`'dir.

## Proje
6S LiPo (20–26 V) girişinden 11 V / 7,5 A üreten ayrık buck dönüştürücü. Tek geçerli tasarım: [buck/TASARIM-HESABI.md](buck/TASARIM-HESABI.md). Eski LM70880 tasarımı `archive/pdu-v2-lm70880/` altındadır, kullanılmaz.

## Tasarım sınırları
- Hazır buck veya PWM kontrolcü entegresi ve hazır kapı sürücü entegresi yok. Genel amaçlı op-amp, karşılaştırıcı ve gerilim referansı kullanılabilir.
- İstenmeden korumalar, ikinci faz veya yeni özellik eklenmez.
- O1 çıkışı hiçbir koşulda 12,0 V'u geçmemelidir. Gerçek yük, korumalar test edilmeden bağlanmaz.

## Sayılar ve doğruluk
- Değerler `buck/hesap.py`, `buck/kontrol.py` ve LTspice çıktılarından gelir, elle sayı yazılmaz. Değer değişirse betikler ve `buck/rapor_uret.py` yeniden koşulur.
- Hesap, varsayım, simülasyon ve ölçüm ayrı yazılır. Simülasyon fiziksel kanıt değildir.
- MPN ve parça değeri uydurulmaz, üretici verisinden alınır.

## Araçlar
- LTspice: `C:\Program Files\ADI\LTspice\LTspice.exe`.
- Metin dosyaları BOM'suz UTF-8'dir, Türkçe karakterler korunur.
