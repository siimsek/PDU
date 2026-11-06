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
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 32 passed | Historical suite at that commit: 22 earlier tests + 10 fail-safe sense/charge evidence tests; superseded by the new 42-test run below. Formula/deck checks only; electrical and physical acceptance remain blocked. |
| 2026-11-06 | PowerShell: `$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'; python analysis/ovp_fail_safe_audit.py` | exit 0; ngspice-47; 1/1 negative fixture completed | Stuck-high LTC7001 INP fault injection with logic-rail loss: no independent clamp leaves INP=4.541 V and both modeled gates=9.996 V; ideal driver-side clamp gives INP about 0.001 V and both gates about 0 V. Behavioral fixture only; supervisor is ideal and no component/hardware PASS. |
| 2026-11-06 | PowerShell: `python -m pytest -q analysis\test_ovp_fail_safe_audit.py analysis\test_ovp_sense_fail_safe.py` | exit 0; 20 passed | Pin-level latch state contract, unsafe simultaneous PRE/CLR, below-1.65-V unspecified latch behavior, thermal scenario separation, input-loss classification and negative-fixture scope. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 42 passed | Current full suite. Checks calculations and saved negative fixture evidence; not electrical or physical acceptance. |
| 2026-11-06 | PowerShell: `$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'; python analysis/ovp_control_chain_followup.py` | exit 0; 2/2 targeted fixture families completed | Dual 5 V/12 V rail loss with TS-referenced gate voltages and separate passive/active screens; common disconnect OUT−IN plus separate precharged-output/input-loss corner. Behavioral fixtures only; silicon behavior remains OPEN. Preliminary attempt 1 lacks VGS measurement vectors; attempts 2–3 completed with superseded fixture conditions. All are preserved but excluded from final results. See [R6 report](PR2-REVIEW-6693550928.md) and [results JSON](ovp-control-chain-followup.json). |
| 2026-11-06 | PowerShell: `python -m pytest -q analysis/test_ovp_control_chain_followup.py analysis/test_ovp_fail_safe_audit.py` | exit 0; 22 passed | Targeted candidate pin map, nominal sense calculation, two rail-loss models, eFuse differential corners and Q=None temporal logic contract. No electrical/device or physical PASS. |
| 2026-11-06 | PowerShell: `python -m pytest -q` | exit 0; 54 passed | Full current suite after R6 changes. Automated tests validate saved fixture evidence and logical/calculation contracts; ngspice and pytest remain nonphysical evidence. |
| 2026-11-06 | PowerShell: `python analysis/ovp_timing_budget.py` | exit 0 | R7 targeted calculation: comparator threshold/timing, input-overdrive build-up, BJT current screen and LTC7001 BST capacitance inequality. Generated `reports/g1/ovp-r7-calculations.json`; conditional assumptions only. |
| 2026-11-06 | PowerShell initial targeted run: `python -m pytest -q analysis/test_ovp_timing_budget.py analysis/test_ovp_control_chain_followup.py analysis/test_ovp_fail_safe_audit.py` | exit 1; 30 passed, 1 failed | New test assertion expected six rows for the common electrical node; candidate table has five. Assertion corrected; engineering criteria unchanged. |
| 2026-11-06 | PowerShell second targeted run: same focused pytest command | exit 1; 30 passed, 1 failed | New test expected outdated wording for the existing single pull-up row. Expectation corrected; electrical criteria unchanged. |
| 2026-11-06 | PowerShell final targeted run: `python -m pytest -q analysis/test_ovp_timing_budget.py analysis/test_ovp_control_chain_followup.py analysis/test_ovp_fail_safe_audit.py` | exit 0; **31 passed** | R7 calculation and evidence-scope tests; not a silicon or physical acceptance test. See [R7 review report](PR2-REVIEW-6694409747.md). |
| 2026-11-06 | R7 SPICE decision | no run | No verified ngspice-compatible comparator/eFuse silicon model was available; TI TPS259824O PSpice model is encrypted and PSpice/Cadence was unavailable. Existing R6 behavioral fixtures remain unchanged and are not physical evidence. |

## PowerShell reproduction commands

```powershell
$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'
python analysis/shared_bus_fault.py
python analysis/ovp_sense_fail_safe.py
python analysis/ovp_fail_safe_audit.py
python -m pytest -q
```

`shared_bus_fault.py`'s historical 4/4 result and all its attempt logs remain unchanged. The prior clamp report is [PR2-REVIEW-6692033623.md](PR2-REVIEW-6692033623.md); the current fail-safe audit is [PR2-REVIEW-6692825552.md](PR2-REVIEW-6692825552.md). The baseline parity record remains Linux ngspice-44.2 O1=16.89 V vs Windows ngspice-47 O1=16.89 V, difference 0.0 V, in [SIMULATION-RESULTS.md](SIMULATION-RESULTS.md).
