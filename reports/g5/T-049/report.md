# T-049 — Tekne tesisatı, sevk ve yanıcı gaz kapsamı

**Durum: Review. Şema, PCB, tasarım ve kuyruk değişmedi. Ürün veya kuruluş için sertifika, uygunluk ya da test geçişi iddiası yoktur.** Kaynak: `reviews/R-024.md`, `decisions/D-013-standards-scope.md` (PR #86, birleşmemiş). Lisanslı standart metinleri okunmadı; madde uyumu değerlendirilmedi.

[scope-split.csv](scope-split.csv): 4 sorunun hepsi **AÇIK**.

| Standart | Kapsam bilgisi | Kaynak durumu |
|---|---|---|
| ISO 13297 | Küçük teknede AC/DC tesisat; elektrikli sevk hariç | R-024/R-025 özeti; iso.org sayfası bu ortamda 403 |
| ISO 16315:2026 | Elektrikli sevk sistemleri, <1500 V DC, gövde boyu 24 m'ye kadar | [Resmi sayfa](https://committee.iso.org/standard/84203.html) okundu |
| ISO 8846:2025 | Çevredeki yanıcı gazın tutuşması; hidrojen-hava ve arızalı cihaz hariç | R-024/R-025 özeti; iso.org sayfası bu ortamda 403 |

Yük adları README.md:3'te kayıtlı (T3 Gemstone O1, SLAMTEC RPLIDAR S2E), ancak yük adı sevk tesisatı olduğunu kanıtlamaz.

Sonuç: PDU'nun sevk gücüyle ilişkisi bilinmeden ISO 13297 ile ISO 16315 arasında seçim yapılamaz. Yanıcı ortam bilinmeden ISO 8846 uygulanamaz; gaz derecesi veya madde yazılmadı.
