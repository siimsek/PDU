# OVP targeted validation record

Date: 2026-11-06 (Europe/Istanbul)

## Reproduction commands and exit codes

| Command | Exit | Result |
|---|---:|---|
| `python analysis/ovp_component_analysis.py` | 0 | Calculation artifacts generated. Threshold enumerated 11.328127…11.623169 V; candidate 3.59 kΩ divider exceeds prior 11.46 V trip target; compliant idealized divider interval is only 3.742 Ω wide and excludes ripple/noise margin. Estimated but unguaranteed chain timing 325.4 ns; provisional fault-current threshold screen 11.964615 A; charge-balance Ceff screen 10.331645 µF. Decision remains BLOCKED. |
| `python analysis/run_ovp_component_checks.py` | 0 | Three targeted ngspice cases completed; deck/log pairs are linked in [OVP-ENGINEERING-RESULT.md](OVP-ENGINEERING-RESULT.md). Final metadata refresh reused logs from the immediately preceding solver execution of these exact decks. |
| `python -m pytest -q` | 0 | **14 passed**: 7 calculation tests, 3 PR #2 review evidence tests, 4 OVP component/measurement tests. |

## Simulation evidence summary

| Deck | Completed | ngspice exit | Key result |
|---|---:|---:|---|
| `family1-switch-off-measurement.cir` | yes | 0 | `OVP_TO_CURRENT_OFF=5.57183e-7 s`; ideal behavioral current edge, not physical hardware |
| `family2-buck-short-independent-ovp-final-10uF-7A.cir` | yes | 0 | O1 peak 11.6900 V; design acceptance BLOCKED |
| `family2-buck-short-independent-ovp-final-4uF-no-load.cir` | yes | 0 | O1 peak 11.6857 V; current-edge crossing occurs before trip and is invalid as an off-time measure; design acceptance BLOCKED |

The 3 outputs are behavioral simulation evidence. The original Family 2 18.8039 V FAIL, Family 4 10.7109 V FAIL, WP1 findings and WP2 FAIL/incomplete counts remain unchanged. No board-level test was performed.

Development note: one intermediate report-generation invocation exited 1 with a `NameError` for the newly added divider-window rendering variable. The renderer binding was corrected; the final standalone calculation run above exited 0 and regenerated the JSON/Markdown artifacts. No circuit deck or prior failure log was changed by that report-render error.

The 12 newly added ngspice text logs have only trailing spaces and excess end-of-file blank lines normalized for Git review; their measurement and diagnostic lines are unchanged.
