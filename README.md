# Bitirme Projesi — Ayrık Buck Dönüştürücü (Aşama 1)

**Aktif tasarım:** 20–26 V 6S LiPo girişinden 11 V / 7.5 A hedefleyen **tek faz asenkron açık çevrim buck güç katı**.

LTspice'ta direkt görüp değiştirilebilen devre çizimleri:

- **[İdeal buck devresi (.asc)](buck/buck-ideal.asc)**
- **[Kayıplı buck devresi (.asc)](buck/buck-kayipli.asc)**

Hesap ve testler: [Proje Tanımı](buck/PROJE-TANIMI.md) · [Tasarım Hesabı](buck/TASARIM-HESABI.md) · [Hesaplama betiği](buck/hesap.py) · [LTspice test betiği](buck/ltspice_sina.py).

Bu aşamada PWM kontrolcü, MOSFET sürücü, op-amp/geri besleme, kompanzasyon, soft-start, ikinci faz, korumalar veya PCB **yoktur**. Sadece anahtarlama için LTspice `PULSE` kaynağı vardır.

**Not:** Yeni `.asc` dosyalarının pin–net bağlantıları statik olarak doğrulandı, LTspice uygulamasında gerçek yeniden çalıştırma henüz yapılmadı. Fiziksel ölçüm yoktur. Açık çevrim 12 V güvenlik sınırını garanti etmez; O1/S2E gerçek yükleri bağlanmaz.

Eski LM70880/çok çıkışlı PDU: [arşiv](archive/pdu-v2-lm70880/ARSIV-NOTU.md). Önceki kontrolcü/çift faz buck çalışmaları: [arşiv](archive/buck-onceki-calisma-2026-11-10/README.md).
