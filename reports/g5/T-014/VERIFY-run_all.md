# G2 doğrulama kaydı (run_all)

Tarih: 2026-11-07T23:41:56. Komut: `python analysis/run_all.py`.

| Adım | Çıkış kodu | Süre (s) | Son satır |
|---|---|---:|---|
| protection (Stage 2) | 0 | 0.8 | `{"rt": 8250.0, "trip": [11.25900482897285, 11.53684858334995], "o1_peak_worst_V": 11.88929155626314, "margin_V": 0.11070844373685951}` |
| power stage / ILIM / UVLO / input (Stage 3) | 0 | 0.2 | `{"irms": 4.210038299027773, "uvlo": [17.36469385975621, 19.62294830018097], "ilim_sum_min": 11.59, "tj_ic": {"jedec_33p5": 179.86769751039537, "evm_18p6": 137.6728111550255}}` |
| loop analytic + ngspice AC (Stage 4) | 0 | 6.2 | `83.0926658731276 83.09263667172772 9601.299549814723 9601.299660942364` |
| N1 phase-OC trip / L(i) (G4 B1) | 0 | 4.6 | `0.05 12.1464 11.0368 11.3539 23.4 OC` |
| stacked tolerance + trim (G4 B4) | 0 | 0.1 | `{'window': 'trimmed', 'static_lo_V': 10.887614705882353, 'static_hi_V': 11.104542156862744, 'step_min_V': 10.785314705882351, 'release_max_V': 11.202142156862744, 'min_ok': True, 'max_ok_band': True, ` |
| gm / UVLO open assumptions (G4 B5) | 0 | 1.3 | `{"gm_ok_interval_S": [0.0005, 0.0018], "uvlo_falling": [{"hys_V": 0.05, "falling_V": [16.50204, 18.6384], "per_cell_V": [2.75034, 3.1064000000000003]}, {"hys_V": 0.1, "falling_V": [15.58526, 17.71518]` |
| routing inputs (Stage 6) | 0 | 0.1 | `S2E_PORT     5.66 A outer 2.97 mm inner 12.46 mm vias 12` |
| BOM v2 / spec / footprint map (Stage 6, G4 C) | 0 | 0.1 | `{"rows": 187, "mpn": 187, "open": 0, "over_derating": 0}` |
| spec <-> BOM <-> SPICE consistency (G4 C3) | 0 | 0.1 | `{"pass": true, "n_errors": 0}` |
| full-system ngspice families F1-F5 (Stage 5) | 0 | 2222.3 | `{"F1": {"runs": 7, "completed": 7, "pass": 6}, "F2": {"runs": 4, "completed": 4, "pass": 4}, "F3": {"runs": 13, "completed": 13, "pass": 11}, "F4": {"runs": 3, "completed": 3, "pass": 2}, "F5": {"runs` |
| workflow check (W0) | 0 | 0.2 | `check_workflow: 0 hata, 1 uyarı` |
| pytest (all) | 0 | 11.4 | `133 passed in 10.88s` |

## Simülasyon aile özeti (`reports/g2/sim-results.json`)

| Aile | Koşu | Tamamlanan | Kriter PASS |
|---|---:|---:|---:|
| F1 | 7 | 7 | 6 |
| F2 | 4 | 4 | 4 |
| F3 | 13 | 13 | 11 |
| F4 | 3 | 3 | 2 |
| F5 | 49 | 47 | 47 |

Simülasyon davranışsal ortalama modeldir; fiziksel kanıt değildir. Ayrıntı: [`SIM-RESULTS.md`](SIM-RESULTS.md).
