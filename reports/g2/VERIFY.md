# G2 doğrulama kaydı (run_all)

Tarih: 2026-11-07T09:17:28. Komut: `python analysis/run_all.py`.

| Adım | Çıkış kodu | Süre (s) | Son satır |
|---|---|---:|---|
| protection (Stage 2) | 0 | 0.5 | `{"rt": 8250.0, "trip": [11.25900482897285, 11.53684858334995], "o1_peak_worst_V": 11.941170906542286, "margin_V": 0.05882909345771381}` |
| power stage / ILIM / UVLO / input (Stage 3) | 0 | 0.1 | `{"irms": 4.210038299027773, "uvlo": [17.36469385975621, 19.62294830018097], "ilim_sum_min": 11.59, "tj_ic": {"jedec_33p5": 179.86769751039537, "evm_18p6": 137.6728111550255}}` |
| loop analytic + ngspice AC (Stage 4) | 0 | 6.1 | `82.46495520828563 82.46494778519698 9826.494199400982 9826.494360880146` |
| routing inputs (Stage 6) | 0 | 0.1 | `S2E_PORT     5.66 A outer 2.97 mm inner 12.46 mm vias 12` |
| BOM v2 / spec / BOM-OPEN (Stage 6) | 0 | 0.1 | `{"rows": 114, "mpn": 71, "open": 43, "over_derating": 0}` |
| full-system ngspice families F1-F5 (Stage 5) | 0 | 248.5 | `{"F1": {"runs": 4, "completed": 4, "pass": 3}, "F2": {"runs": 4, "completed": 4, "pass": 4}, "F3": {"runs": 10, "completed": 10, "pass": 8}, "F4": {"runs": 3, "completed": 3, "pass": 2}, "F5": {"runs"` |
| pytest (all) | 0 | 2.7 | `95 passed in 2.30s` |

## Simülasyon aile özeti (`reports/g2/sim-results.json`)

| Aile | Koşu | Tamamlanan | Kriter PASS |
|---|---:|---:|---:|
| F1 | 4 | 4 | 3 |
| F2 | 4 | 4 | 4 |
| F3 | 10 | 10 | 8 |
| F4 | 3 | 3 | 2 |
| F5 | 49 | 49 | 48 |

Simülasyon davranışsal ortalama modeldir; fiziksel kanıt değildir. Ayrıntı: [`SIM-RESULTS.md`](SIM-RESULTS.md).
