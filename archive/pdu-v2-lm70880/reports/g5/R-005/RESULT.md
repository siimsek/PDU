# R-005 — iki F5 köşesinin sonucu (2026-11-07)

Köşeler: `f5_vt11.487_td300ns_ctyp_r200m_l0.8`, `f5_vt11.765_td300ns_ctyp_r200m_l0.8` (VIN 26 V, Rsrc 200 mΩ, Ceff typ, L 0,8; TVS /VIN'de — D-007).

## Denemeler (FAIL/zaman aşımı kayıtları silinmez)
| # | Ayar | Sonuç |
|---|---|---|
| 1–2 | sim_runner timeout 300 s | tamamlanmadı (exit −9) |
| 3 | timeout 900 s (R-005 tur 1) | tamamlanmadı |
| 4 | BIL1/BIL2 abs/max düzgünleştirme (R-005 tur 2, Iε 10 mA, εg 1e-3), 900 s | tamamlanmadı (rc 124) → düzgünleştirme geri alındı (kök neden değil) |

## Tanı
Aynı deck `.tran` bitişi kısaltılarak koşuldu: 95–214 µs arası her bitiş < 1 s'de tamamlanıyor; **216 µs ve sonrası 60–240 s'de bitmiyor** → çözücü tıkanması 214–216 µs'de (hatadan ~115 µs sonra). 214 µs anlık durum: ayırıcı açık (Q = 1), arızalı faz akımı 32,0 A ve yavaş azalıyor, VIN 18,42 V (200 mΩ kaynakta çökme), VRAW 17,78 V → VIN'e yaklaşıyor; `ctl` ≈ 0, `oct` 1,2 V. Şüphe: VRAW ≈ VIN yakınında Q1 (`BQ1` ters yön 1 nS) / faz akımı sıfıra yaklaşırken sert geçiş. Kesin kök neden **kanıt yok**.

## Kısaltılmış pencere kanıtı (SİM, pencere 100–214 µs)
Deck: [`..._w214.cir`](f5_vt11.487_td300ns_ctyp_r200m_l0.8_w214.cir) (yalnız `.tran` bitişi ve `.meas` üst sınırı 214 µs; model, adım, Gear, toleranslar aynı). Log: [`..._w214.log`](f5_vt11.487_td300ns_ctyp_r200m_l0.8_w214.log).

| Ölçüm | vt11.487 | vt11.765 | Kriter | Not |
|---|---:|---:|---|---|
| O1 tepe | **10,924 V** @ 106,8 µs | **10,924 V** @ 106,8 µs | ≤ 12,0 V | tepe pencere içinde; ayırıcı açık ve mandallı (Q = 1) → sonrasında O1 yükselemez |
| VSAFE tepe | 10,925 V | 10,925 V | < 30 V | |
| Ayırıcı açılırken faz akımı | 19,38 A | 19,38 A | — | OC tetiği (iki eşik köşesi aynı sonucu veriyor) |
| VRAW tepe | 17,79 V (pencere sonu, yükseliyor) | aynı | < 60 V | **tam pencere değeri kanıt yok**; komşu tamamlanan köşeler ≤ 29,1 V |

Sonuç: O1 ≤ 12,0 V bu iki köşe için **SİM (kısaltılmış pencere)** kanıtıyla sağlanıyor. `sim-results.json`'da koşular tamamlanmamış (PASS sayılmadı) olarak kalır; VRAW tam pencere tepesi ve 216 µs sonrası çözücü tıkanması AÇIK (backlog).
