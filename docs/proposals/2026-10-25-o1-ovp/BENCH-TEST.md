# WP1 – Tezgâh test planı

> **DURUM: YAPILMADI.** Fiziksel test yapılmamıştır. Tüm sonuçlar ngspice davranışsal simülasyonudur (sim ≠ silikon).

| # | Test | Düzen | Ölçüm | Kabul (değiştirilmeyen kriter) |
|---|---|---|---|---|
| B1 | Trip/release eşiği | RAW'a programlanabilir kaynak, 10 mV/s yavaş rampa, -40/25/85 °C | INP düşüş anındaki RAW | 11,2929–11,5167 V içinde; 11,22 V'ta tetik yok |
| B2 | G1 – TLV3601 VIO @ VCM≈4,1 V | Komparatör tek başına, VCM 4,096 V, ofset tarama | VIO | ≤ 5 mV + 4,1 mV (A1); aşarsa bütçe tekrar hesaplanır |
| B3 | Rampa 0,07/0,17/0,23 V/µs | Güç kaynağı + MOSFET rampa üreteci RAW'da | O1 portu tepe (≥ 200 MHz prob, kısa toprak yayı) | O1 ≤ 12,0 V anlık |
| B4 | Buck high-side short | Buck üst FET'i köprüleyerek (kontrollü, sigortalı) 26 V | O1/bus/RAW tepe, VDS, INP | O1 ≤ 12,0 V; VDS ≤ 60 V |
| B5 | tPD(INP_L) gerçek kapı yükünde | 4× CSD18540Q5B takılı, INP adımı | INP↓ → VGS < 1 V süresi | ≤ 1,05 µs (aksi halde marj kapanmaz) |
| B6 | Startup 20 / 22,2 / 26 V | Batarya emülatörü, 4,5 A yük | bus max, FET_ON süresi | bus ≤ 11,22 V; O1 ≤ 12 V |
| B7 | Yanlış tetik | 11,1605 V + 10 mV/870 kHz ripple, 11,21 V | INP | Tetik yok |
| B8 | 0,45→4,5 A ve 7,5 A basamak | Elektronik yük | bus min/max | 10,78–11,22 V (7,5 A: tracking) |
| B9 | Toparlanma | B3/B4 sonrası | O1/S2E reset | 11 V ±2 % |
| B10 | -40 °C RAW bank ESR | Soğuk oda | ESR ölçümü + B4 tekrarı | 100 mΩ köşe raporlanır (stres) |
