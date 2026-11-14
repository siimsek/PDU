# Datasheet arşivi

Bu klasör, 14 Kasım 2026 denetiminde doğrulanan üretici veri sayfasının yerel kopyasını ve kaynağını kaydeder.

## LM5137-Q1

- Dosya: [LM5137-Q1_SNVSCU2B_RevB_2025-08.pdf](LM5137-Q1_SNVSCU2B_RevB_2025-08.pdf)
- Üretici: Texas Instruments
- Üretici kaynağı: https://www.ti.com/lit/ds/symlink/lm5137-q1.pdf
- Belge kimliği / revizyonu: SNVSCU2B, Rev. B; Ağustos 2024, Ağustos 2025'te revize edildi.
- Arşivleme tarihi: 2026-11-14
- SHA-256: 11A14BB256E520D66F18CD5433507CF323FA11E96F9580E7A36A5D0B565DB09B
- İlgili proje notları: `buck/OPTIMIZASYON.md` §16.7 ve `buck/PARCA-HEDEFLERI.md` içindeki DCR akım algısı notu.

Veri sayfası LM5137-Q1'i çift kanallı senkron buck denetleyicisi olarak tanımlar. §7.3.11.2, bobin DCR algısını paralel RC ağıyla açıklar; `RCS × CCS = L / DCR` zaman sabitini verir ve oda sıcaklığında tipik %10–15 akım sınır doğruluğu belirtir. Aynı bölüm yöntemi hassas akım sınırı koruması gerektirmeyen uygulamalar için önerir. Bu tipik değer bir güvenlik sınırı garantisi değildir; senkron örnek de mevcut asenkron PDU ile doğrudan uyumluluk kanıtlamaz.

PDF, TI'nin resmi URL'sinden indirilmiştir. Yeniden doğrulama için üretici kaynağını kullanın; yerel kopya ve SHA-256 bu arşivleme anındaki sürümü tanımlar.
