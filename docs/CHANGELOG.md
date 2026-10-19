# Değişiklik kaydı

## 19 Ekim2026 — hesap ve rapor eşliği düzeltmesi

- `calculate.py` eski2,61k/4,99k IMON ve25 V COUT bilgileri yerine güncel Konnect export/BOM verisine bağlandı.88 µF önceki kompanzasyon dayanağı,164,98 µF tipik üretici verisi ve257,664 µF üst hassasiyet ayrı etiketlendi; yeni direnç önerileri uygulanmış sayılmıyor.
- Ortak giriş doğrulayıcısı ref/değer/footprint farkında duruyor. Tolerans/TCR alanları okunuyor;1% gibi eksik alan varsayımları açık yazılıyor. Statik çıkış kodu tüm statik ekranları kapsıyor.
- Koşu durumu/hatayı kaydeden `latest-run.json` eklendi. Eksik/eski log, tamamlanmamış motor veya eksik yürütme kapsamı önceki raporla başarı gibi gösterilmiyor.
- Güncel tasarım, doğrulama ve PCB belgeleri yeniden yazıldı; önceki ayrıntılı kayıtlar arşivlendi. Sonuçlar ve başarısız O1 kabulü korunuyor.
- CAD kaynaklarına bu düzeltmede dokunulmadı. Tamamlanmamış O1/kararlılık/F1/BOM/PCB ve fiziksel kabul işleri açık.

## 19 Ekim2026 — prototip checkpoint ve repo düzeni

- Bootstrap/giriş/PG düzeltmeleri ve ortak LTspice/ngspice modeli kayda alındı.
- Kesin RFB seçimi,806 Ω IMON ve100 V TDK COUT atamaları; pin-net eşliği korunarak ilk PCB yerleşimi güncellendi.
- U1/U2 yaklaşık güç bakırı, U3/U4 iki exposed pad, Q1 mask uyarlaması ve TDK özel land kayıtları açıklandı.
- Son denetim: short0, ERC0/0; PCB197 unrouted/301 uyarı;48 koşu512 geçen/2 başarısız O1 kontrolü. Üretime hazır değil.
- Kullanıcının kontrol isteği açık iş/özel parça kontrol listesine eklendi. Amaç, devam noktası ve kanıt önceliği ayrı giriş belgelerine taşındı.
- Eski kök görsel/netlistler silinmeden arşivlendi. Aktif KiCad ve simülasyon yolları korundu.
- Kilit/raw/cache/yerel IPC config ve yeniden dağıtımı kısıtlı üretici modelleri Git dışında bırakıldı. Makineye bağlı çalıştırıcı yollarına ortam değişkeni desteği eklendi.
- Eski dokümantasyon güncelleyicisi yeni kararları ezmemesi için devre dışı bırakıldı.

## Başlangıç geçmişi

- `c24ead8`: temiz başlangıç referans projesi.
- `40c853b`: GitHub kaynak deposu eşleşmesinin kaydı.

Bu checkpoint daha sonraki gerçek donanım/üretim kabulünün yerine geçmez. Tam commit kimliği Git geçmişinde bulunur.
