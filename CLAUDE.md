# Çalışma Kuralları — Buck güç katı

Tek aktif dal `main`. Kullanıcı işi doğrudan verir; thinker/builder, rol, kart veya röle düzeni yoktur.

**Aktif amaç:** 20–26 V → 11 V / 7,5 A (82,5 W), 100 kHz tek faz asenkron, açık çevrim buck güç katısını kullanıcıyla birlikte LTspice'ta **yalnız değerler üzerinden** incelemek.

- Devre kapsamı: DC kaynak, anahtar S1, serbest geçiş diyodu D1, bobin L1, giriş/çıkış kondansatörleri ve direnç yükü. Anahtar LTspice `PULSE` kaynağıyla sürülür; gerçek PWM üreteci kurulmaz.
- Ana şematik yalnız değer tabanlıdır: ideal anahtar/diyot, L/C + ESR/DCR. `.param`, `.meas`, `.ic`, açıklama notu veya gerçek parça modeli eklenmez. Şematikte yalnız `.tran` ve iki `.model` satırı bulunur.
- Gerçek parçaları (MPN) kullanıcı kendisi bulur. Parça önerme/arama yalnız kullanıcı isterse yapılır; aranacak hedef değerler [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) dosyasındadır. Kullanıcı bir parça getirdiğinde veri sayfası değeri şematiğe ve `buck/hesap.py` sabitlerine yazılıp yeniden koşulur.
- PWM kontrolcü, op-amp, sürücü, geri besleme, kompanzasyon, soft-start, ikinci faz, korumalar, PCB veya başka özellik ekleme.
- Analitik hesap, varsayım, LTspice sonucu ve fiziksel ölçümü ayrı tut. LTspice çalıştırılmadıysa simülasyon tamamlandı/PASS deme; değer, sonuç veya fiziksel test uydurma.
- Açık çevrim devre 11 V regülasyonu veya 12 V üst sınırını garanti etmez. Gerçek O1, RPLIDAR S2E ya da başka hassas yük bağlama.
- Dosya yapısı sade tutulur: yeni rapor, tarama betiği, sonuç klasörü veya arşiv kullanıcı istemeden oluşturulmaz. Önceki parça taramaları ve raporlar kullanıcı isteğiyle kaldırıldı (git geçmişinde `066e28a`).
- Sonraki aşamaya yalnız kullanıcı istediğinde geç.

Şematik: `python buck/ltspice/sematik_uret.py [Ton_us]` `buck_guc_kati.asc` ve `buck_guc_kati.svg` dosyalarını birlikte üretir. Şematik LTspice'ta elle değişirse aynı değişiklikte `python buck/ltspice/asc_gorsel.py` ile görsel yenilenir ve birlikte commit edilir; README bu görseli gösterir.

`python buck/hesap.py` analitik özeti ekrana yazar (LTspice veya laboratuvar sonucu değildir). Dosyalar UTF-8'dir.
