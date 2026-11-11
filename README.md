# Açık çevrim buck güç katı

20–26 V girişten (6S batarya, ana çalışma noktası 24,6 V) 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron, açık çevrim buck güç katı. Beslenecek yükler T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'dir.

**Aşama: ANA GÜÇ DEVRESİ** — güç katının değerleri ve parçaları belirlendi; PWM/geri besleme henüz yok. Bu aşamanın son hâli `ANA-GUC-DEVRESI` dalında saklanır.

![LTspice şematiği](buck/ltspice/buck_guc_kati.svg)

## Devre değerleri ve parçalar

| Eleman | Şematikteki değer | Parça |
|---|---|---|
| V1 | 24,6 V (aralık 20–26 V) | 6S batarya |
| Cin1, Cin2 | 2 × 680 µF, ESR 20 mΩ | Panasonic EEUFR1V681B (35 V) |
| S1 | ideal anahtar, `Ron=11m`; Vdrv `PULSE` ile 100 kHz, Ton = 4,63 µs | STP75NF75 (75 V, TO-220) |
| D1 | ideal diyot, `Vf=0.46 Ron=3.1m` | IXYS DSB60C60HB (60 V, 2 × 30 A, iki bacak paralel) |
| L1 | 33 µH, DCR 15 mΩ | Bourns 2300HT-330 (13,6 A toroid) |
| Cout | 680 µF, ESR 28 mΩ | Rubycon 25ZLH680MEFC10X16 (25 V) |
| Rload | 1,467 Ω | ≥ 100 W direnç yükü |

Şematik hâlâ ideal elemanlıdır; değerler seçilen parçaların veri sayfasından alınmıştır. Parçaların payları, bulunurluğu ve yedekleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Değerlerin gerekçesi ve test sonuçları: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

LTspice sonucu (24,6 V giriş, kararlı durum, 19–20 ms): Vo = 11,004 V, çıkış ripple'ı 51,8 mV t-t, bobin akımı 6,56–8,44 A. Fiziksel ölçüm yoktur.

Açık çevrim: Ton sabitken giriş veya yük değişirse çıkış 11 V'ta kalmaz; soft-start yoktur (sert kalkışta LTspice 45,8 A / 17,2 V gösterir). **Gerçek O1 veya S2E bağlanmaz.**

## LTspice'ta deneme

1. `buck/ltspice/buck_guc_kati.asc` dosyasını aç, **Run** (koşan adam simgesi) düğmesine bas.
2. `out` telinin üstüne tıkla → çıkış gerilimi. L1'in gövdesine tıkla → bobin akımı.
3. İlk ~10 ms kalkış salınımıdır; kararlı durum için 19–20 ms arasını büyüt (fareyle sürükle).
4. Grafikte iz adına (`V(out)`) **Ctrl + sol tık** → ortalama ve RMS değeri.
5. Değer değiştirmek için parçanın üstündeki değere sağ tıkla, yaz, yeniden Run. S1 ve D1 de aynı şekilde değişir (`Ron=…`, `Vf=…`).

Şematikteki tek yönerge `.tran 20m` satırıdır (simülasyon süresi); LTspice bunu şematikte ister.

Beklenen (24,6 V giriş, 19–20 ms): V(out) ortalama ≈ 11,00 V, ripple ≈ 52 mV t-t, I(L1) ≈ 6,6–8,4 A.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc) | LTspice şematiği (çift tıkla aç, Run) |
| [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) | Seçilen parçalar, veri sayfası değerleri, bulunurluk, yedekler, sonraki aşama notları |
| [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) | Yük gereksinimleri, aday karşılaştırması, test sonuçları, açık riskler |
| [buck/hesap.py](buck/hesap.py) | Analitik hesap: ripple, akımlar, kayıplar, LC dinamiği (`python buck/hesap.py`) |
| [buck/dogrula.py](buck/dogrula.py) | LTspice doğrulama koşuları: 5 giriş, yük adımı, kalkış, tolerans (`python buck/dogrula.py secilen`) |
| `buck/grafik/*.svg` | `dogrula.py grafik` ile üretilen dalga şekilleri |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar ve diyot parçaları; şematikle aynı klasörde durmalı, elle açmak gerekmez |
| [buck/ltspice/sematik_uret.py](buck/ltspice/sematik_uret.py), [asc_gorsel.py](buck/ltspice/asc_gorsel.py) | Şematiği ve yukarıdaki görseli üretir |
| [CLAUDE.md](CLAUDE.md) | Çalışma kuralları |
