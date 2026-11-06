# G2 Aşama 4 — döngü kararlılığı (LM70880 ×2, ortak COMP)

Hesap: [`analysis/g2/loop.py`](../../analysis/g2/loop.py) → [`loop-results.json`](loop-results.json); SPICE AC deck/log: [`sim/loop/`](sim/loop/); testler [`test_loop.py`](../../analysis/g2/test_loop.py).

## Model (VARSAYIM'lar açık)

1. Ridley tepe akım modu modeli; iki faz ortak COMP sürdüğü için eşdeğer tek faz L/2, Ri/2.
2. Ri = RS·GCS = 7.5 mΩ × 10 = 0.075 V/A (GCS DATASHEET p.8/p.17, "by design"). COMP'un akım karşılaştırıcısına iç bölücü/ofset ile bağlanıp bağlanmadığı datasheet'te yok → **model belirsizliği**; PM'den 10° pay düşülür.
3. Dış eğim Se: LM70880 Eq.7 (p.16) → giriş-referanslı 24 mV/µs × fsw[MHz]; mc = 1 + Se/Sn.
4. Örnekleme çift kutbu fsw/2, Q = 1/(π(mc·D′−0.5)).
5. gm 970 µS min / 1200 µS typ (DATASHEET p.7); maksimum yayımlanmamış → 1430 µS (VARSAYIM).
6. EA çıkış direnci 10 MΩ (VARSAYIM; yalnız düşük frekans kazancını etkiler).
7. COUT Ceff min/typ/max = 185.3 / 330.0 / 515.3 µF (16× C5750, Aşama 3); ESR 0.12 mΩ.

Köşeler: Ceff {min, typ, max} × L {0.8, 1.0, 1.2} × gm {970, 1200, 1430 µS} × VIN {20, 26 V} × yük {0.75, 7.5 A} × fsw {400, 480 kHz} = **432 köşe**.

## Seçim

Kısıtlar: tüm köşelerde kesişim, GM ≥ 9 dB (6 dB + 3 dB tasarım payı), fc_max ≤ fsw_min/6, birinci derece yük adımı göstergesi ΔI/(2π·fc·C) ≤ 0.20 V; amaç en kötü PM'yi büyütmek.

| | Eski (9.53 kΩ / 4.7 nF / 47 pF) 8× COUT | Eski, 16× COUT | **Yeni (16.9 kΩ / 10 nF / 22 pF) 16× COUT** |
|---|---|---|---|
| fc aralığı | 11.4–46.0 kHz | 6.3–22.9 kHz | **9.8–40.9 kHz** |
| En kötü PM (model) | 60.2° | 58.0° | **66.9°** |
| PM − 10° model payı | 50.2° | 48.0° | **56.9° ≥ 45° ✓** |
| En kötü GM | 10.4 dB | 16.4 dB | **11.7 dB ≥ 6 dB ✓** |
| Yük adımı göstergesi (maks) | — | — | 0.199 V |

**Yeni nominal değerler:** RCOMP = **16.9 kΩ**, CCOMP = **10 nF**, CHF = **22 pF** (0603, C0G önerilir). Eski COMP değerleri 16× COUT ile fc'yi 6 kHz'e düşürüp yük adımını büyütür; bu yüzden değiştirildi.

## İki yol karşılaştırması (SİM)

Aynı model ngspice AC ile devre olarak çözüldü (akım kaynağı + Rcm + RLC örnekleme filtresi + gm katı; döngü, çıkış ile bölücü arasına seri AC kaynağıyla kırıldı).

| Köşe | Analitik PM / fc | ngspice PM / fc | Fark |
|---|---|---|---|
| En kötü 1 (Ceff min, L 1.2, gm 1430 µS, VIN 26 V, 0.75 A, 400 kHz) | 66.860° / 39.718 kHz | 66.859° / 39.718 kHz | <0.001° / <0.001 % |
| En kötü 2 | 67.048° / 39.764 kHz | 67.047° / 39.764 kHz | <0.001° |
| En kötü 3 | 67.233° / 39.274 kHz | 67.233° / 39.274 kHz | <0.001° |
| En iyi 1 / 2 | 82.52° / 9.83 kHz, 82.46° / 9.83 kHz | aynı | <0.001° |

Bu uyum cebir/sayısal çözümü doğrular; **modelin fiziksel doğruluğunu doğrulamaz**.

## Tezgâhta ayar ve FRA

- RCOMP footprint'i 10–33 kΩ, CCOMP 2.2–10 nF, CHF 22–100 pF seçeneklerine uygun (0603).
- FRA enjeksiyonu: RFB1 koluna seri `R_INJ` (varsayılan 0 Ω, FRA için 49.9 Ω), `TP_FB_INJ_A/B`.
- **Tezgâh FRA şart** (BENCH T3): PM ≥45°, GM ≥6 dB en az VIN 20/26 V ve 0.75/7 A'da.

## Yük adımı

0.75→7→0.75 A transient kontrolü büyük-sinyal ortalama modelle SİM Aile 3'te yapılır ([`SIM-RESULTS.md`](SIM-RESULTS.md)); kriter bara min ≥10.78 V ve aşım < trip_min 11.2737 V.
