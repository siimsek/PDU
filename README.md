# Açık çevrim buck güç katı

20–26 V girişten (6S batarya, ana çalışma noktası 24,6 V) 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron, açık çevrim buck güç katı. Beslenecek yükler T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'dir. Şu an yalnız **değerlerle** çalışılıyor; gerçek parça seçimi sonraki iştir.

![LTspice şematiği](buck/ltspice/buck_guc_kati.svg)

## Devre değerleri

| Eleman | Değer |
|---|---|
| V1 | 24,6 V (aralık 20–26 V) |
| Cin1, Cin2 | 2 × 220 µF, ESR 20 mΩ |
| S1 | ideal anahtar, `Ron=10m`; Vdrv `PULSE` ile 100 kHz, Ton = 4,65 µs |
| D1 | ideal diyot, `Vf=0.5 Ron=10m` |
| L1 | 33 µH, DCR 15 mΩ |
| Cout | 680 µF, ESR 25 mΩ |
| Rload | 1,467 Ω |

LTspice sonucu (24,6 V giriş, kararlı durum, 19–20 ms): Vo = 11,008 V, çıkış ripple'ı 46,6 mV t-t, bobin akımı 6,56–8,45 A. Fiziksel ölçüm yoktur.

Değerlerin gerekçesi, gerçek yük senaryoları ve tüm test sonuçları: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

Açık çevrim: Ton sabitken giriş veya yük değişirse çıkış 11 V'ta kalmaz; soft-start yoktur (sert kalkışta LTspice 45,8 A / 17,1 V gösterir). **Gerçek O1 veya S2E bağlanmaz.**

## LTspice'ta deneme

1. `buck/ltspice/buck_guc_kati.asc` dosyasını aç, **Run** (koşan adam simgesi) düğmesine bas.
2. `out` telinin üstüne tıkla → çıkış gerilimi. L1'in gövdesine tıkla → bobin akımı.
3. İlk ~10 ms kalkış salınımıdır; kararlı durum için 19–20 ms arasını büyüt (fareyle sürükle).
4. Grafikte iz adına (`V(out)`) **Ctrl + sol tık** → ortalama ve RMS değeri.
5. Değer değiştirmek için parçanın üstündeki değere sağ tıkla, yaz, yeniden Run. S1 ve D1 de aynı şekilde değişir (`Ron=…`, `Vf=…`).

Şematikteki tek yönerge `.tran 20m` satırıdır (simülasyon süresi); LTspice bunu şematikte ister.

Beklenen (24,6 V giriş, 19–20 ms): V(out) ortalama ≈ 11,01 V, ripple ≈ 47 mV t-t, I(L1) ≈ 6,6–8,5 A.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc) | LTspice şematiği (çift tıkla aç, Run) |
| [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) | Yük gereksinimleri, aday karşılaştırması, test sonuçları, açık riskler |
| [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) | Parça ararken aranacak hedef değerler |
| [buck/hesap.py](buck/hesap.py) | Analitik hesap: ripple, akımlar, kayıplar, LC dinamiği (`python buck/hesap.py`) |
| [buck/dogrula.py](buck/dogrula.py) | LTspice doğrulama koşuları: 5 giriş, yük adımı, kalkış, tolerans (`python buck/dogrula.py secilen`) |
| `buck/grafik/*.svg` | `dogrula.py grafik` ile üretilen dalga şekilleri |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar ve diyot parçaları; şematikle aynı klasörde durmalı, elle açmak gerekmez |
| [buck/ltspice/sematik_uret.py](buck/ltspice/sematik_uret.py), [asc_gorsel.py](buck/ltspice/asc_gorsel.py) | Şematiği ve yukarıdaki görseli üretir |
| [CLAUDE.md](CLAUDE.md) | Çalışma kuralları |
