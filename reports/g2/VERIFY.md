# G2 doğrulama kaydı (run_all)

Tarih: 2026-11-07T03:57:22. Komut: `python analysis/run_all.py`.

| Adım | Çıkış kodu | Süre (s) | Son satır |
|---|---|---:|---|
| protection (Stage 2) | 0 | 0.5 | `{"rt": 8250.0, "trip": [11.264898717463973, 11.530896620385738], "o1_peak_worst_V": 11.934522138417405, "margin_V": 0.06547786158259505}` |
| power stage / ILIM / UVLO / input (Stage 3) | 0 | 0.1 | `{"irms": 4.210038299027773, "uvlo": [17.36469385975621, 19.62294830018097], "ilim_sum_min": 11.59, "tj_ic": {"jedec_33p5": 179.86769751039537, "evm_18p6": 137.6728111550255}}` |
| loop analytic + ngspice AC (Stage 4) | 0 | 5.9 | `82.46495520828563 82.46494778519698 9826.494199400982 9826.494360880146` |
| routing inputs (Stage 6) | 0 | 0.1 | `S2E_PORT     5.66 A outer 2.97 mm inner 12.46 mm vias 12` |
| BOM v2 / spec / BOM-OPEN (Stage 6) | 0 | 0.1 | `{"rows": 114, "mpn": 71, "open": 43, "over_derating": 0}` |
| full-system ngspice families F1-F5 (Stage 5) | 0 | 243.4 | `{"F1": {"runs": 4, "completed": 4, "pass": 3}, "F2": {"runs": 4, "completed": 4, "pass": 4}, "F3": {"runs": 8, "completed": 8, "pass": 6}, "F4": {"runs": 3, "completed": 3, "pass": 2}, "F5": {"runs": ` |
| pytest (all) | 0 | 2.5 | `91 passed in 2.15s` |

## Simülasyon aile özeti (`reports/g2/sim-results.json`)

| Aile | Koşu | Tamamlanan | Kriter PASS |
|---|---:|---:|---:|
| F1 | 4 | 4 | 3 |
| F2 | 4 | 4 | 4 |
| F3 | 8 | 8 | 6 |
| F4 | 3 | 3 | 2 |
| F5 | 49 | 49 | 48 |

Simülasyon davranışsal ortalama modeldir; fiziksel kanıt değildir. Ayrıntı: [`SIM-RESULTS.md`](SIM-RESULTS.md).
