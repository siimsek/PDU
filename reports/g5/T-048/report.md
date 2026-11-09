# T-048 — Sürüm ve gözden geçirme formu

**Durum: Review. Şema, PCB, tasarım ve kuyruk değişmedi. Ürün veya kuruluş için sertifika, uygunluk ya da test geçişi iddiası yoktur.** Kaynak: `reviews/R-024.md`, `decisions/D-013-standards-scope.md` (PR #86, birleşmemiş). Lisanslı standart metinleri okunmadı; madde uyumu değerlendirilmedi.

[release-form-template.csv](release-form-template.csv) 15 alanlı boş formdur. Hazırlayan, gözden geçiren ve onaylayan gerçek kişi olmadan **AÇIK** kalır.

DRC, ERC ve CAM sonuçları T-024 kapısından gelir, burada çalıştırılmadı. Akış: T-024 kanıtı → form → gözden geçirme → etiket. Mevcut durumda form doldurulamaz: T-023 Done değil, PCB routing bekliyor.
