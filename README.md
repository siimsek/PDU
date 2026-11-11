# Açık çevrim buck güç katı

20–26 V girişten 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron, açık çevrim buck güç katı. Şu an yalnız **değerlerle** çalışılıyor; gerçek parça seçimi sonraki iştir.

![LTspice şematiği](buck/ltspice/buck_guc_kati.svg)

## Devre değerleri

| Eleman | Değer |
|---|---|
| V1 | 22,2 V (aralık 20–26 V) |
| Cin1, Cin2 | 2 × 220 µF, ESR 20 mΩ |
| S1 | ideal anahtar, `Ron=10m`; Vdrv `PULSE` ile 100 kHz, Ton = 5,14 µs |
| D1 | ideal diyot, `Vf=0.5 Ron=10m` |
| L1 | 33 µH, DCR 15 mΩ |
| Cout | 330 µF, ESR 15 mΩ |
| Rload | 1,467 Ω |

LTspice sonucu (22,2 V giriş, kararlı durum): Vo = 11,003 V, çıkış ripple'ı 25,5 mV p-p, bobin akımı 6,64–8,36 A. Fiziksel ölçüm yoktur.

Açık çevrim: Ton sabitken giriş veya yük değişirse çıkış 11 V'ta kalmaz; soft-start yoktur. Hassas yük bağlanmaz.

## LTspice'ta deneme

1. `buck/ltspice/buck_guc_kati.asc` dosyasını aç, **Run** (koşan adam simgesi) düğmesine bas.
2. `out` telinin üstüne tıkla → çıkış gerilimi. L1'in gövdesine tıkla → bobin akımı.
3. İlk ~5 ms kalkış salınımıdır; kararlı durum için 9–10 ms arasını büyüt (fareyle sürükle).
4. Grafikte iz adına (`V(out)`) **Ctrl + sol tık** → ortalama ve RMS değeri.
5. Değer değiştirmek için parçanın üstündeki değere sağ tıkla, yaz, yeniden Run. S1 ve D1 de aynı şekilde değişir (`Ron=…`, `Vf=…`).

Şematikteki tek yönerge `.tran 10m` satırıdır (simülasyon süresi); LTspice bunu şematikte ister.

Beklenen (22,2 V giriş, 9–10 ms): V(out) ortalama ≈ 11,00 V, ripple ≈ 25 mV p-p, I(L1) ≈ 6,6–8,4 A.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc) | LTspice şematiği (çift tıkla aç, Run) |
| [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) | Parça ararken aranacak hedef değerler |
| [buck/hesap.py](buck/hesap.py) | Ripple, tepe/RMS akım analitik hesabı (`python buck/hesap.py`) |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar ve diyot parçaları; şematikle aynı klasörde durmalı, elle açmak gerekmez |
| [buck/ltspice/sematik_uret.py](buck/ltspice/sematik_uret.py), [asc_gorsel.py](buck/ltspice/asc_gorsel.py) | Şematiği ve yukarıdaki görseli üretir |
| [CLAUDE.md](CLAUDE.md) | Çalışma kuralları |
