# G1 test record

All current command rows were run in Windows PowerShell unless marked historical. Every simulation row is model evidence only; none is a physical test.

| Date | Shell / command | Result | Scope and limits |
|---|---|---|---|
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 7 passed | G1 calculation tests (`analysis/test_pdu_calc.py`). |
| 2026-11-06 | PowerShell: `python analysis\run_g1_simulations.py family1_ovp` | exit 0; 1 family completed; model criterion PASS | TDELAY use corrected; 11.9741 V ideal model with 25.9 mV to 12 V. Not the buck high-side-short topology or physical evidence. |
| 2026-11-06 | PowerShell: `python analysis\run_g1_simulations.py --metadata-only` | exit 0; 0 ngspice runs | Refreshed five-family scope/status metadata; no measurements changed. |
| 2026-11-06 | PowerShell: `python analysis\verify_pr2_review.py` | exit 0; 8/8 evidence checks | Checks saved review/deck/log evidence; no SPICE execution and no electrical acceptance. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 10 passed | 7 calculation tests + 3 PR #2 evidence-scope tests. |
| 2026-11-06 | PowerShell: `python analysis\ovp_component_analysis.py` | exit 0 | Generated MPN-corner, Ceff and conditional delay calculations; analytical/numerical cross-check only. |
| 2026-11-06 | PowerShell: `python analysis\run_ovp_component_checks.py` | exit 0; 3/3 targeted SPICE cases completed | Family 1 ideal-switch edge and Family 2 high-side-short with candidate OVP, 10 µF/7 A and 4 µF/no-load behavioral corners. Existing Family 2/4 FAILs retained. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 14 passed | 7 calculation + 3 evidence-scope + 4 OVP component/timing/case tests. |
| 2026-11-06 | Historical shared-bus run: `python analysis\shared_bus_fault.py` with `PDU_NGSPICE` set to `F:\Spice64\bin\ngspice_con.exe` | exit 0; 4/4 cases reported completed | Prior overload, common-isolator and TPS1686x behavioral runs. This historical invocation is restated as PowerShell syntax below for reproducibility; it was not rerun in this turn. |
| 2026-11-06 | PowerShell: `python -m pytest -q analysis\test_shared_bus_fault.py` | exit 0; 8 passed | Shared-bus calculations, load classification, topology and threshold feasibility; not electrical acceptance. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 22 passed | Prior full suite: 14 earlier tests + 8 shared-bus tests. |
| 2026-11-06 | PowerShell: `python -m pytest -q analysis\test_ovp_sense_fail_safe.py` | exit 0; 10 passed | Reproduces 10.956 mA original-divider failure; tests candidate input-current/rail bounds, threshold corners, separate capacitor sensors, FAIL retention and 85 °C LDO thermal FAIL screen. |
| 2026-11-06 | PowerShell first run: `$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'; python analysis/ovp_sense_fail_safe.py` | Script exit 0; charge-balance deck completed; rail-loss current measurement **INCOMPLETE** | The first log did not expose `I(BCLAMP)` as a measurable current vector. Both first-run deck/logs are preserved as `*-attempt1.*`; the missing measurement was not counted complete. |
| 2026-11-06 | PowerShell corrected run: `$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'; python analysis/ovp_sense_fail_safe.py` | exit 0; 2/2 required-measurement sets completed; ngspice-47 | Separate IN/OUT capacitor, eFuse, switch and load currents with charge balance; static divider clamp/rail loss model with current sensor. See `sense-failsafe-results.json` and its linked decks/logs. No physical PASS. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 32 passed | Current complete suite: 22 earlier tests + 10 fail-safe sense/charge evidence tests. Formula/deck checks only; electrical and physical acceptance remain blocked. |

## PowerShell reproduction commands

```powershell
$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'
python analysis/shared_bus_fault.py
python analysis/ovp_sense_fail_safe.py
python -m pytest -q
```

`shared_bus_fault.py`'s historical 4/4 result and all its attempt logs remain unchanged. The new fail-safe report is [PR2-REVIEW-6692033623.md](PR2-REVIEW-6692033623.md). The baseline parity record remains Linux ngspice-44.2 O1=16.89 V vs Windows ngspice-47 O1=16.89 V, difference 0.0 V, in [SIMULATION-RESULTS.md](SIMULATION-RESULTS.md).
