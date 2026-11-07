# G2 tam sistem SPICE sonuçları

Netlist: [`design/pdu_v2.cir`](../../design/pdu_v2.cir) (SHA256 `1756b7e33556f9c7…`), parametre kaynağı `analysis/g2/params.py` + `design.py` → her deck'te `.param` bloğu; koşucu [`analysis/g2/sim_runner.py`](../../analysis/g2/sim_runner.py). Araç: ngspice (ngspice_con.exe). **behavioral average model, NOT silicon; no physical evidence.**

Bir koşu yalnız ngspice çıkış kodu 0 ve istenen bütün `.meas` değerleri varsa *tamamlandı* sayılır; tamamlanmayan koşu PASS sayılmaz. Deck/log/girdi SHA256 `sim-results.json` içindedir; deck değiştiğinde önceki deck/log `-attemptN` olarak korunur.

| Aile | Koşu | Tamamlanan | Kriter PASS |
|---|---:|---:|---:|
| F1 | 7 | 7 | 6 |
| F2 | 4 | 4 | 4 |
| F3 | 13 | 13 | 11 |
| F4 | 3 | 3 | 2 |
| F5 | 49 | 49 | 49 |

## Aile 1 — üst anahtar kısa devresi + ortak bara ayırıcı

| Koşu | Tamam | Ölçümler (kriterli) | Kriterler | Sonuç | Not |
|---|---|---|---|---|---|
| [f1_worst](sim/f1/f1_worst.log) | True | o1_max_fault=11.04, vsafe_max_fault=11.04, vds_iso_max=23.54, vraw_max_fault=34.4 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |
| [f1_worst_nominal_setpoint](sim/f1/f1_worst_nominal_setpoint.log) | True | o1_max_fault=11.2, vsafe_max_fault=11.2, vds_iso_max=16.98, vraw_max_fault=28.03 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |
| [f1_typ_loaded](sim/f1/f1_typ_loaded.log) | True | o1_max_fault=10.99, vsafe_max_fault=11.01, vds_iso_max=24.12, vraw_max_fault=26.5 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |
| [f1_noprot_baseline](sim/f1/f1_noprot_baseline.log) | True | o1_max_fault=19.35, vsafe_max_fault=27.87, vds_iso_max=0.028, vraw_max_fault=27.87 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **FAIL** | korumasız referans: G1 FAIL'inin yeni netlistte yeniden üretimi (silinmez) |
| [f1_worst_lfloor0p05](sim/f1/f1_worst_lfloor0p05.log) | True | o1_max_fault=11.04, vsafe_max_fault=11.04, vds_iso_max=22.25, vraw_max_fault=33.11 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |
| [f1_worst_highsetpoint_lfloor0p05](sim/f1/f1_worst_highsetpoint_lfloor0p05.log) | True | o1_max_fault=11.37, vsafe_max_fault=11.37, vds_iso_max=16.45, vraw_max_fault=27.65 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |
| [f1_voltage_trip_only_g3_design](sim/f1/f1_voltage_trip_only_g3_design.log) | True | o1_max_fault=11.96, vsafe_max_fault=11.96, vds_iso_max=16.14, vraw_max_fault=27.9 | o1_max_fault <= 12, vsafe_max_fault < 30, vds_iso_max < 100, vraw_max_fault < 60 | **PASS** |  |

## Aile 2 — 20–26 V açılış, UVLO kalkışı, hot-plug, dip

| Koşu | Tamam | Ölçümler (kriterli) | Kriterler | Sonuç | Not |
|---|---|---|---|---|---|
| [f2_hotplug_26V](sim/f2/f2_hotplug_26V.log) | True | vraw_max=11.01, q_end=0, vraw_end=11, vraw_end_hi=11, vin_max=42.09 | vraw_max < 11.22, q_end < 0.5, vraw_end >= 10.83, vraw_end_hi <= 11.16, vin_max < 65 | **PASS** |  |
| [f2_hotplug_20V_full_load](sim/f2/f2_hotplug_20V_full_load.log) | True | vraw_max=11.01, q_end=0, vraw_end=11, vraw_end_hi=11, vin_max=28.23 | vraw_max < 11.22, q_end < 0.5, vraw_end >= 10.83, vraw_end_hi <= 11.16, vin_max < 65 | **PASS** |  |
| [f2_ramp_to_20V_uvlo_high_corner](sim/f2/f2_ramp_to_20V_uvlo_high_corner.log) | True | vraw_max=11.02, q_end=0, vraw_end=11, vraw_end_hi=11, vin_max=19.97 | vraw_max < 11.22, q_end < 0.5, vraw_end >= 10.83, vraw_end_hi <= 11.16, vin_max < 65 | **PASS** |  |
| [f2_dip_22V_to_15V_restart](sim/f2/f2_dip_22V_to_15V_restart.log) | True | vraw_max=11.02, q_end=0, vraw_end=11, vraw_end_hi=11, vin_max=31.34, ens_min_dip=-2.389e-216 | vraw_max < 11.22, q_end < 0.5, vraw_end >= 10.83, vraw_end_hi <= 11.16, vin_max < 65, ens_min_dip < 0.5 | **PASS** |  |

## Aile 3 — yük adımı 0.75→7→0.75 A, COMP/Ceff köşeleri

| Koşu | Tamam | Ölçümler (kriterli) | Kriterler | Sonuç | Not |
|---|---|---|---|---|---|
| [f3_nominal_cmin_gm_ea_min](sim/f3/f3_nominal_cmin_gm_ea_min.log) | True | bus_min=10.9, bus_max_release=11.09, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_cmin_gm_ea_max](sim/f3/f3_nominal_cmin_gm_ea_max.log) | True | bus_min=10.92, bus_max_release=11.07, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_ctyp_gm_ea_min](sim/f3/f3_nominal_ctyp_gm_ea_min.log) | True | bus_min=10.9, bus_max_release=11.09, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_ctyp_gm_ea_max](sim/f3/f3_nominal_ctyp_gm_ea_max.log) | True | bus_min=10.93, bus_max_release=11.06, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_cmax_gm_ea_min](sim/f3/f3_nominal_cmax_gm_ea_min.log) | True | bus_min=10.9, bus_max_release=11.08, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_cmax_gm_ea_max](sim/f3/f3_nominal_cmax_gm_ea_max.log) | True | bus_min=10.93, bus_max_release=11.06, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_stacked_low_setpoint_cmin_gmmin](sim/f3/f3_stacked_low_setpoint_cmin_gmmin.log) | True | bus_min=10.73, bus_max_release=10.93, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **FAIL** | statik alt köşe + transient yığılması |
| [f3_stacked_high_setpoint_cmin_gmmin](sim/f3/f3_stacked_high_setpoint_cmin_gmmin.log) | True | bus_min=11.06, bus_max_release=11.26, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **FAIL** | statik üst köşe + yük bırakma yığılması |
| [f3_nominal_cmin_gmmin_vin20_l0.8](sim/f3/f3_nominal_cmin_gmmin_vin20_l0.8.log) | True | bus_min=10.9, bus_max_release=11.09, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_nominal_cmin_gmmin_vin26_l1.2](sim/f3/f3_nominal_cmin_gmmin_vin26_l1.2.log) | True | bus_min=10.89, bus_max_release=11.09, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_trimmed_low_setpoint_cmin_gmmin](sim/f3/f3_trimmed_low_setpoint_cmin_gmmin.log) | True | bus_min=10.79, bus_max_release=10.98, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_trimmed_high_setpoint_cmin_gmmin](sim/f3/f3_trimmed_high_setpoint_cmin_gmmin.log) | True | bus_min=11, bus_max_release=11.2, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |
| [f3_trimmed_low_setpoint_cmin_gmmin_vin20_l0.8](sim/f3/f3_trimmed_low_setpoint_cmin_gmmin_vin20_l0.8.log) | True | bus_min=10.79, bus_max_release=10.98, q_end=0 | bus_min >= 10.78, bus_max_release < 11.22, q_end < 0.5 | **PASS** |  |

## Aile 4 — eFuse kısa devresi, O1/S2E izolasyonu, giriş kaybı / OUT>IN

| Koşu | Tamam | Ölçümler (kriterli) | Kriterler | Sonuç | Not |
|---|---|---|---|---|---|
| [f4_o1_short_s2e_isolation](sim/f4/f4_o1_short_s2e_isolation.log) | True | s2e_min_fault=10.84, q_end=0, io1_max=9.293 | s2e_min_fault >= 9, q_end < 0.5, io1_max <= 9.79 | **PASS** |  |
| [f4_input_loss_with_drev](sim/f4/f4_input_loss_with_drev.log) | True | o1_minus_in_max=0.1146, s2e_minus_in_max=-0.000273 | o1_minus_in_max <= 0.3, s2e_minus_in_max <= 0.3 | **PASS** |  |
| [f4_input_loss_without_drev](sim/f4/f4_input_loss_without_drev.log) | True | o1_minus_in_max=0.7584, s2e_minus_in_max=-0.0009606 | o1_minus_in_max <= 0.3, s2e_minus_in_max <= 0.3 | **FAIL** | D_REV'siz karşılaştırma (D_REV gerekçesi) |

## Aile 5 — koruma köşe taraması (eşik, gecikme, Ceff, hata akımı, L) + hassas yol açık artık riski

Tarama: VTRIP_EFF {trip_min, trip_max} + 50 mV×k overdrive × gecikme {0.3 µs, max} × Ceff {min, typ, max} × Rsrc {20, 200 mΩ} × L {0.8, 1.2} = 48 koşu; ön-hata barası statik alt köşe (10.8333 V), VIN 26 V, yüksüz.

- Tamamlanan: 48/48; kriter PASS: 48.
- O1 tepe aralığı: 10.8920 – 11.0718 V (sınır 12.0 V).
- VSAFE (U3/U4 IN) tepe maks: 11.0723 V (sınır 30 V abs, 24 V önerilen).
- En kötü köşe: [f5_vt11.487_td1048ns_cmin_r20m_l1.2](sim/f5/f5_vt11.487_td1048ns_cmin_r20m_l1.2.log).

Hassas yol açık (R_OVT açık devre, yalnız kaba OV): O1 tepe 11.2 V, VSAFE tepe 11.2 V → PASS (artık risk; PROTECTION-DECISION §4).

## Model sınırları

- Ortalama (anahtarlamasız) model: tepe akım komutu + sınırlı ortalama anahtar, akım döngüsü ~100 kHz eşdeğer; örnekleme etkisi ve LM70880 iç devresi yok. eFuse: tek yönlü, aktif akım sınırı, UVLO histerezisi, 16.9 V OVLO; ITIMER/termal kapanma yok.
- Koruma zinciri: karşılaştırıcı+mandal+LM74502H tek toplu gecikme (`TDLY`) ile; eşik garantili-gecikme seviyesinde (trip + 50 mV overdrive×k). FET ideal anahtar + gövde diyotu; SOA/termal yok.
- Kapasitörler toplu Ceff + ESR/ESL; CIN/CEFOUT Ceff VARSAYIM (datasheet yok).
- Bu sonuçlar tezgâh ölçümünün yerini tutmaz (BENCH-ACCEPTANCE).
