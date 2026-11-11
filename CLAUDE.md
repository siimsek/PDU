# Çalışma Kuralları — Buck güç katı

Aktif dal `main`. Tamamlanan aşamalar ayrı dalda saklanır: `ANA-GUC-DEVRESI` (etiket `ana-guc-devresi-v1`) ana güç devresinin parça seçimiyle birlikte son hâlidir; o dala yeni iş yazılmaz. Kullanıcı işi doğrudan verir; thinker/builder, rol, kart veya röle düzeni yoktur.

**Aktif amaç:** 20–26 V → 11 V / 7,5 A (82,5 W), 100 kHz tek faz asenkron, açık çevrim buck güç katısını kullanıcıyla birlikte LTspice'ta **yalnız değerler üzerinden** incelemek. Ana çalışma noktası 24,6 V; yükler T3 Gemstone O1 ve RPLIDAR S2E.

- Devre kapsamı: DC kaynak, anahtar S1, serbest geçiş diyodu D1, bobin L1, giriş/çıkış kondansatörleri ve direnç yükü. Anahtar LTspice `PULSE` kaynağıyla sürülür; gerçek PWM üreteci kurulmaz.
- Ana şematik yalnız değer tabanlıdır: ideal anahtar/diyot, L/C + ESR/DCR. `.param`, `.meas`, `.ic`, açıklama notu veya gerçek parça modeli eklenmez. Şematikte tek yönerge `.tran` satırıdır (LTspice onu yalnız şematik yazısından kabul eder); S1 ve D1 değerleri (`Ron=`, `Vf=`) diğer parçalar gibi parçanın üstünde yazar ve `anahtar.asy` / `diyot.asy` / `idealler.lib` ile tanımlanır. Kullanıcı ekranda `.model`, `.param` gibi yönerge görmek istemiyor.
- Parçalar seçildi (11 Kasım 2026, kullanıcı isteğiyle): liste, veri sayfası değerleri, bulunurluk ve yedekler [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) dosyasındadır. Şematikteki değerler bu parçaların veri sayfası değerleridir; şematik yine ideal elemanlıdır. Yeni parça arama/önerme yalnız kullanıcı isterse yapılır. Parça değişirse veri sayfası değeri şematiğe, `buck/hesap.py` ve `buck/dogrula.py` sabitlerine yazılıp yeniden koşulur.
- PWM kontrolcü, op-amp, sürücü, geri besleme, kompanzasyon, soft-start, ikinci faz, korumalar, PCB veya başka özellik ekleme.
- Analitik hesap, varsayım, LTspice sonucu ve fiziksel ölçümü ayrı tut. LTspice çalıştırılmadıysa simülasyon tamamlandı/PASS deme; değer, sonuç veya fiziksel test uydurma.
- Açık çevrim devre 11 V regülasyonu veya 12 V üst sınırını garanti etmez. Gerçek O1, RPLIDAR S2E ya da başka hassas yük bağlama.
- Dosya yapısı sade tutulur: yeni rapor, tarama betiği, sonuç klasörü veya arşiv kullanıcı istemeden oluşturulmaz. Önceki parça taramaları ve raporlar kullanıcı isteğiyle kaldırıldı (git geçmişinde `066e28a`).
- Sonraki aşamaya yalnız kullanıcı istediğinde geç.

Şematik: `python buck/ltspice/sematik_uret.py [Ton_us]` `buck_guc_kati.asc` ve `buck_guc_kati.svg` dosyalarını birlikte üretir. Şematik LTspice'ta elle değişirse aynı değişiklikte `python buck/ltspice/asc_gorsel.py` ile görsel yenilenir ve birlikte commit edilir; README bu görseli gösterir.

`python buck/hesap.py` analitik özeti ekrana yazar (LTspice veya laboratuvar sonucu değildir). `python buck/dogrula.py secilen|tarama|mevcut|grafik` LTspice'ı toplu kipte koşar (5 giriş noktası, gerçek yük senaryoları, kalkış, tolerans); test netlistleri geçici klasörde kalır, ana şematiğe yönerge eklenmez. Yükler, gerekçeler ve sonuçlar [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) dosyasındadır; şematik değeri değişirse `hesap.py` ve `dogrula.py` sabitleri de güncellenip yeniden koşulur. Dosyalar UTF-8'dir.
