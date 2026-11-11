# Çalışma Kuralları — Buck güç katı

Aktif dal `main`. Tamamlanan aşamalar ayrı dalda saklanır: `ANA-GUC-DEVRESI` (etiket `ana-guc-devresi-v2`) ana güç devresinin doğrulanmış son hâlidir; o dala yeni iş yazılmaz. Kullanıcı işi doğrudan verir; thinker/builder, rol, kart veya röle düzeni yoktur.

**Aktif amaç:** 20–26 V → 11 V / 7,5 A (82,5 W), 100 kHz tek faz asenkron, açık çevrim buck güç katısını kullanıcıyla birlikte LTspice'ta **yalnız değerler üzerinden** incelemek. Ana çalışma noktası 24,6 V; yükler T3 Gemstone O1 (5–12 V) ve RPLIDAR S2E (9–28 V).

## Şu anki durum (11 Kasım 2026)

- Şematik değerleri: L1 33 µH / 15 mΩ, Cout 1000 µF / 25 mΩ, Cin 2 × 1000 µF / 20 mΩ, S1 `Ron=12m`, D1 `Vf=0.5 Ron=10m`, 100 kHz, Ton 4,65 µs, V1 24,6 V.
- Bu değerler **parça numarasından bağımsız hedeflerdir**. Belirli parça (MPN) seçilmedi. Her değerin kabul aralığı ve nedeni [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) dosyasındadır; nasıl seçildikleri ve test sonuçları [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) dosyasındadır.
- Tek doğruluk kaynağı: şematik değerleri `buck/ltspice/sematik_uret.py`, `buck/hesap.py` ve `buck/dogrula.py` (`SECILEN`) içinde **aynı** olmalıdır. Biri değişirse üçü birlikte değişir, testler yeniden koşulur ve belgelerdeki sayılar yenilenir.
- Bir değeri değiştirmeden önce nedenini PARCA-HEDEFLERI.md'de oku: örneğin Cout ESR'sinin alt sınırı da vardır (düşük ESR sönümü bozar), 22 µH ve 680 µF bilerek elenmiştir.

## Kurallar

- Devre kapsamı: DC kaynak, anahtar S1, serbest geçiş diyodu D1, bobin L1, giriş/çıkış kondansatörleri ve direnç yükü. Anahtar LTspice `PULSE` kaynağıyla sürülür; gerçek PWM üreteci kurulmaz.
- Ana şematik yalnız değer tabanlıdır: ideal anahtar/diyot, L/C + ESR/DCR. `.param`, `.meas`, `.ic`, açıklama notu veya gerçek parça modeli eklenmez. Şematikte tek yönerge `.tran` satırıdır (LTspice onu yalnız şematik yazısından kabul eder); S1 ve D1 değerleri (`Ron=`, `Vf=`) diğer parçalar gibi parçanın üstünde yazar ve `anahtar.asy` / `diyot.asy` / `idealler.lib` ile tanımlanır. Kullanıcı ekranda `.model`, `.param` gibi yönerge görmek istemiyor.
- Gerçek parçaları (MPN) kullanıcı kendisi bulur; belirli parça numarası **seçme veya şematiğe yazma**. Parça arama yalnız kullanıcı isterse yapılır ve sonuç "kriteri tutan örnek" olarak yazılır. Kullanıcı bir parça getirdiğinde veri sayfası değeri kriterlerle karşılaştırılır, uygunsa şematiğe ve `hesap.py` / `dogrula.py` sabitlerine yazılıp yeniden koşulur.
- PWM kontrolcü, op-amp, sürücü, geri besleme, kompanzasyon, soft-start, ikinci faz, korumalar, PCB veya başka özellik ekleme.
- Analitik hesap, varsayım, LTspice sonucu ve fiziksel ölçümü ayrı tut. LTspice çalıştırılmadıysa simülasyon tamamlandı/PASS deme; değer, sonuç veya fiziksel test uydurma.
- Açık çevrim devre 11 V regülasyonu veya 12 V üst sınırını garanti etmez. Gerçek O1, RPLIDAR S2E ya da başka hassas yük bağlama.
- Dosya yapısı sade tutulur: yeni rapor, tarama betiği, sonuç klasörü veya arşiv kullanıcı istemeden oluşturulmaz. Önceki parça taramaları ve raporlar kullanıcı isteğiyle kaldırıldı (git geçmişinde `066e28a`).
- Sonraki aşamaya (PWM / geri besleme) yalnız kullanıcı istediğinde geç.

## Araçlar

Şematik: `python buck/ltspice/sematik_uret.py [Ton_us]` `buck_guc_kati.asc` ve `buck_guc_kati.svg` dosyalarını birlikte üretir. Şematik LTspice'ta elle değişirse aynı değişiklikte `python buck/ltspice/asc_gorsel.py` ile görsel yenilenir ve birlikte commit edilir; README bu görseli gösterir.

`python buck/hesap.py` analitik özeti ekrana yazar (LTspice veya laboratuvar sonucu değildir).

`python buck/dogrula.py secilen|pencere|tarama|mevcut|grafik` LTspice'ı toplu kipte koşar: `secilen` şematik değerleriyle tüm testler (5 giriş noktası, gerçek yük senaryoları, kalkış, tolerans; ≈ 15 dk), `pencere` L/Cout/ESR kabul aralıklarının kenarları, `tarama` ilk 9 adaylık karşılaştırma, `mevcut` en baştaki eski değerler, `grafik` `buck/grafik/*.svg`. Test netlistleri geçici klasörde kalır, ana şematiğe yönerge eklenmez. LTspice görünmeyen ayrı bir Windows masaüstünde başlatılır; kullanıcının pencere odağını almaz.

Dosyalar UTF-8'dir. Windows kabuğunda Türkçe karakter içeren metni heredoc ile Python'a verme (bozulur); dosyaya yazıp çalıştır.
