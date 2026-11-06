# G1 targeted ngspice runs

| Family | Completed? | Criterion | Result | Log |
|---|---|---|---|---|
| family1_ovp | yes | PASS model criterion | baseline parity 16.89 vs 16.89 V; ideal candidate O1 peak 11.9741 V | `reports/g1/sim/*.log` |
| ↳ `family1-ovp-independent-latch.cir` | yes | — | `{"latch_max": 0.999995, "o1_peak": 11.9741, "o1_steady": 11.0}` | `sim\family1-ovp-independent-latch.log` |
| family2_buck_highside_short | yes | FAIL/OPEN | O1 peak 18.8039 V; limit 12.0 V | `reports/g1/sim/*.log` |
| ↳ `family2-buck-highside-short.cir` | yes | — | `{"bus_peak": 39.812, "o1_peak": 18.8039, "phase_current": 63.6654}` | `sim\family2-buck-highside-short.log` |
| family3_startup_uvlo | yes | PASS model criterion | 20→26 V, 18 V fall and 20 V restart; bus/O1 extrema measured in behavioral model | `reports/g1/sim/*.log` |
| ↳ `family3-startup-uvlo.cir` | yes | — | `{"bus_after_restart": 10.9961, "bus_at_20": 10.9954, "bus_at_26": 10.9961, "o1_peak": 10.9996}` | `sim\family3-startup-uvlo.log` |
| family4_load_step_comp_corners | yes | FAIL/OPEN | 0.75→7.0→0.75 A, low/typ/high Ceff and corresponding RCOMP; bus extrema logged | `reports/g1/sim/*.log` |
| ↳ `family4-load-step-minc_lowcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.7109, "bus_recover": 10.9961, "o1_peak": 10.9839}` | `sim\family4-load-step-minc_lowcomp.log` |
| ↳ `family4-load-step-typc_midcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.8148, "bus_recover": 10.9961, "o1_peak": 10.9839}` | `sim\family4-load-step-typc_midcomp.log` |
| ↳ `family4-load-step-maxc_highcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.8596, "bus_recover": 10.9961, "o1_peak": 10.9839}` | `sim\family4-load-step-maxc_highcomp.log` |
| family5_efuse_short_hotplug | yes | PASS model criterion | port hot-plug plus O1 short/healthy S2E checks; model-only | `reports/g1/sim/*.log` |
| ↳ `family5-hotplug.cir` | yes | — | `{"o1_final": 10.9973, "o1_peak": 10.9975, "s2e_final": 10.9986}` | `sim\family5-hotplug.log` |
| ↳ `family5-o1-short.cir` | yes | — | `{"o1_reset": 5.48046e-11, "o1_short_avg": 1.07836e-12, "o1_short_peak": 10.9973, "s2e_healthy": 10.9973}` | `sim\family5-o1-short.log` |

Baseline parity: Linux ngspice-44.2 recorded O1 peak **16.89 V**; Windows ngspice-47 measured **16.89 V**; displayed difference **0.0 V**. Both preserve the expected ~16.89 V failure.

Interpretation: all decks use behavioral approximations, not TI silicon; any SİM criterion pass is not physical acceptance. Family 2's first draft failed setup because REN1 was duplicated; the next detailed topology hit timestep-too-small at xu3.ena. Both logs are retained. A simplified behavioral topology completed and still FAILs the O1 ≤12 V gate at 18.8039 V; no further solver convergence tweaking was done.
