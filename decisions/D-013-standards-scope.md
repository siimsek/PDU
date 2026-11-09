# D-013 — PDU standart kapsamı ve doğrulama önceliği

- **Kart:** `tasks/D-013.md`
- **Durum:** Review
- **Dayanak:** `reviews/R-024.md`, kaynak commit `c69c77cf529c8d7698f7a8c7b4448b8e7f59d601`.

## Soru
Kuruluş kalite yönetimi ve PDU'nun ürün/deniz ortamı standartları arasında hangi kapsam seçilmeli; uygunluk kanıtı ve sahipliği nasıl izlenmeli?

## Seçenekler
1. Bütün ISO/otomotiv/deniz standartlarını doğrudan zorunlu ve mevcut projeyi uyumlu ilan etmek: RED; kapsam ve kanıt bilinmiyor.
2. ISO 9001'i tek ürün standardı saymak: RED; kuruluş QMS gereksinimleri ürün testlerinin yerine geçmez.
3. Ürün ve kullanım profilini kaynakla tanımlamak; resmi kapsamı doğrulanmış standartları koşullu matriste tutmak, uygulanabilirlik/versiyon/sözleşme ve kanıtları ayrı kapatmak: SEÇİLDİ.

## Karar
- ISO 9001:2026 kuruluş QMS kapsamıdır; repo, kurumun süreç yönetimi veya bağımsız belgelendirmesini kanıtlamaz. [ISO yayımı](https://www.iso.org/news/2026/09/ISO9001-2026). Eski 2015 sertifika ve geçiş durumu kuruluşa özeldir; bilinmiyor.
- PDU'nun 6S LiPo ve IDA adı kaynakta görülür, deniz aracı teriminin tam sistem sınırı, tekne boyu/sınıfı, mevzuat alanı, muhafaza ve görev profili **AÇIK**. Dolayısıyla ISO 13297/16315/8846, IEC 60092-504/60533 ve 60945 otomatik zorunlu ilan edilmez; koşullu değerlendirme `T-043/T-049`.
- ISO 26262, 7637 ve 16750 karayolu kapsamındadır; bu proje için otomatik şart değil. Talep/sistem arayüzüyle sonradan geçerli olabilir. `D-007`'nin load-dump dışlama varsayımı fiziksel geçici gerilim testinin karşılığı değildir.
- IPC-2221/2152/7351 mevcut tasarım kanıtlarıdır; IPC-A-610/J-STD-001 montaj sınıfı ve kriterleri, IEC 60664 izolasyon çevre girdileri eksiktir. 0,6 mm mevcut kural korunur; IEC veya IPC uyumu sonucu varsayılmaz. `T-045`, mevcut `T-024` son kapısına girdi sağlar.
- EMC/çevre ve muhafaza planı `T-044`; satın alma/tedarikçi değerlendirmesi `T-046` (stok araştırması için `T-042` ile çakışmadan), lot/seri `T-047`, revizyon/üretim onayı `T-048`. Bütün bu kartlar Draft'tır.
- Ürün ve kuruluş için hiçbir sertifika, yasal uygunluk, test geçişi veya resmi onay iddia edilmiyor. Lisanslı standart metinleri ve gerçek testler erişilemediğinde AÇIK; fiziksel testler gerçek test laboratuvarına/üreticiye aittir.

## Kanıt ve sınırlar
Standart bazında resmi URL, repo kanıtı, eksik ve sorumlu matrisi `reviews/R-024.md` içindedir. Kapsam bilgisi standart maddelerinin tamamına veya hukuki uygulanabilirliğe eşit değildir. Devre/simülasyon/Türkiye tedariki önceliklidir; PCB routing bekler.
