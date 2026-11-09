# T-047 — Lot ve seri izlenebilirlik modeli

**Durum: Review. Şema, PCB, tasarım ve kuyruk değişmedi. Ürün veya kuruluş için sertifika, uygunluk ya da test geçişi iddiası yoktur.** Kaynak: `reviews/R-024.md`, `decisions/D-013-standards-scope.md` (PR #86, birleşmemiş). Lisanslı standart metinleri okunmadı; madde uyumu değerlendirilmedi.

[traceability-records-template.csv](traceability-records-template.csv) boş şablondur. Fiziksel kart veya lot olmadığından hiçbir kayıt girilmedi; seri veya lot üretilmedi.

Bağlantı: `kart_seri_no` bir kartı tanımlar; `ref`+`mpn` `design/bom-v2.csv` ile, `lot_date_code`+`satın_alma_belge_no` satın alma kaydıyla, `test_raporu_id` T-024 ve tezgâh raporlarıyla eşleşir. SHA alanları T-048 formuna bağlanır.

Varsayımlar: seri numara biçimi seçilmedi (**AÇIK**). Kayıtlarda kişi adı yerine rol veya kod kullanılması önerilir; gizlilik kuralı kuruluşça belirlenir.
