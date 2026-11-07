# LTspice sonuçları

## Güncel ortalama akım-mod yük adımı

- Araç: LTspice 26.1.1
- Tarih: 2026-10-18
- Girdi: `compensation-step.cir`
- Model: iki faz, paylaşılan COMP, denklem 42 akım kazancı. Her faz `I = V(COMP) / (7.5 mΩ × 10)`, 0–8 A sınırlı. Çıkış kapasitesi varsayılan 88 µF. Geri besleme 130 kΩ / 10.2 kΩ. Kompanzasyon 9.53 kΩ, 4.7 nF, 47 pF. Anahtarlama, akım çevrimi örnekleme kutupları ve LM70880 silikonu yoktur.
- Koşul: 2 ms'de yük 0.75 A'dan 7.5 A'a çıkar. Ölçüm penceresi adımdan sonra 2–5 ms; yerleşmiş değer 4–5 ms.

| Ölçüm | Sonuç |
|---|---:|
| Vout ortalama, 4–5 ms | 10.996028 V |
| Vout minimum, 2–5 ms | 10.72126 V |
| Vout maksimum, 2–5 ms | 10.996028 V |
| V(COMP), 4.5 ms | 0.281253 V |
| Faz akımı, 4.5 ms | 3.750039 A |

Yerleşmiş gerilim, 0.8 × (1 + 130/10.2) = 10.996 V hesabıyla aynıdır. 7.5 A'da faz başına 3.75 A, paylaşılan COMP modelinin beklediği değerdir. Adımda bara 0.275 V düşer ve 150 µs sonra 10.987 V'a döner; ölçüm penceresinde setpoint üstüne aşım yoktur. Bu, 88 µF varsayımı ve ideal akım kaynağı modeli için bir yük adımıdır. Ölçülmüş döngü kazancı veya verim değildir.

## Tek fazlı anahtarlama ripple kontrolü

- Araç: LTspice 26.1.1
- Tarih: 2026-10-18
- Girdi: `phase-ripple.cir` (26 V) ve aynı devrenin 20 V darbe değerleri. Loglar `phase-ripple-20v.log` ve `phase-ripple-26v.log`.
- Model: ideal darbe kaynağı, 50 mΩ seri direnç, 6.8 µH / 23.3 mΩ, 88 µF, 2.933 Ω yük, 440 kHz, Gear, yerleşmiş başlangıç akımı. LM70880 silikonu, akım modu ve iki faz yoktur.
- Karşılaştırma: `Vout_avg × (1−D) / (L × 440 kHz)`. Kabul sınırı %15.

| Vin | D | Vout ort. | IL ort. | IL tepeden tepeye | Kapalı form | Fark |
|---:|---:|---:|---:|---:|---:|---:|
| 20 V | 0.550 | 10.871 V | 3.741 A | 1.806 A | 1.635 A | %10.5 |
| 26 V | 0.423 | 10.921 V | 3.719 A | 2.361 A | 2.105 A | %12.1 |

İki nokta da %15 içindedir. Çıkış gerilimi tepeden tepeye 31 mV ve 25 mV'tur; modelde kondansatör ESR'si yoktur, bu yüzden gerilim ripple'ı kart tahmini değildir. Worst-case tasarım ripple'ı hâlâ `calculate.py` içindeki 400 kHz minimum hesabıdır: 26 V'ta 2.333 A tepeden tepeye, tepe 4.917 A.

## LTspice 26.1.1 ve ngspice-47 karşılaştırması

- Tarih: 2026-10-18
- LTspice: 26.1.1, `C:\Program Files\ADI\LTspice\LTspice.exe`
- spice64: ngspice-47, 11 Ağustos 2026, `F:\Spice64\bin\ngspice_con.exe`
- Karar: kabul. Şema değeri değişmedi.

Ortalama model. LTspice `compensation-step.cir`. ngspice `ngspice-compensation.cir`. ngspice'da `tstep` sıfır olamaz, `limit()` kelepçe değildir ve 64 MΩ hata yükselteci işletim noktasında yakınsamadığı için `uic` kullanılır. Akım `min(max(...),8)` ile sınırlanır. Denklemler aynıdır.

| Ölçüm | LTspice 26.1.1 | ngspice-47 | Fark |
|---|---:|---:|---:|
| Vout, 4–5 ms | 10.996028 V | 10.9960 V | %0.0003 |
| Vout minimum | 10.72126 V | 10.7218 V | %0.005 |
| Faz akımı, 4.5 ms | 3.750039 A | 3.75004 A | %0.00003 |

Kabul sınırı %2 idi.

Ripple. LTspice `phase-ripple-20v.cir` ve `phase-ripple.cir`. ngspice `ngspice-ripple-20v.cir` ve `ngspice-ripple-26v.cir`. ngspice bobin `Rser` kabul etmez; 23.3 mΩ seri direnç olarak yazıldı.

| Koşul | LTspice IL pp | ngspice IL pp | Motor farkı | Forma göre LTspice |
|---|---:|---:|---:|---:|
| 20 V | 1.80621 A | 1.81146 A | %0.29 | %10.5 |
| 26 V | 2.3607 A | 2.36561 A | %0.21 | %12.1 |

Motorlar %5 içinde, formül %15 içinde. Bu LM70880 kanıtı değildir.



## Tarihsel tek fazlı ortalama model

- Tarih: 2026-10-14
- Girdi: `buck-average.cir`
- Durum: tek fazlı ideal ortalama model, 7.5 A toplam akımı tek endüktöre yükler. Güncel iki fazlı şemayı temsil etmez.

| Vin | Vout ort. | Vout min | Vout maks. | Endüktör akımı maks. | Endüktör akımı min |
|---:|---:|---:|---:|---:|---:|
| 20.0 V | 11.00009 V | 10.98386 V | 11.01665 V | 7.62911 A | 7.36686 A |
| 22.2 V | 10.99996 V | 10.98711 V | 11.01249 V | 7.60697 A | 7.39632 A |
| 25.2 V | 11.00003 V | 10.99170 V | 11.00857 V | 7.57214 A | 7.42551 A |
| 26.0 V | 11.00002 V | 10.99599 V | 11.00415 V | 7.53767 A | 7.46353 A |

Ripple ve tepe akımın tasarım sayıları 400 kHz minimum kapalı formdadır. 440 kHz ideal anahtar modeli yukarıdaki tablodadır; o tablo 400 kHz worst-case hesabının yerine geçmez.
