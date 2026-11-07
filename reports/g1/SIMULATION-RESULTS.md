> **SUPERSEDED (G3, 2026-11-07) → reports/g2/SIM-RESULTS.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# G1 targeted ngspice runs

| Family | Completed? | Criterion | Result | Model scope | Log |
|---|---|---|---|---|---|
| family1_ovp | yes | PASS model criterion | baseline parity 16.89 vs 16.89 V; ideal source-pulse latch O1 peak 11.9741 V; not the buck high-side-short topology | Ideal source-pulse + behavioral latch + ideal series switch. TDELAY is an ideal parameter. Not connected to family 2 buck high-side-short case and not a selected component topology. | `reports/g1/sim/*.log` |
| ↳ `family1-ovp-independent-latch.cir` | yes | — | `{"latch_max": 0.999995, "o1_peak": 11.9741, "o1_steady": 11.0}` | — | `sim\family1-ovp-independent-latch.log` |
| family2_buck_highside_short | yes | FAIL/OPEN | O1 peak 18.8039 V; limit 12.0 V | High-side-short sensitivity with an idealized 16.32 V eFuse switch only. No independent comparator/latch/disconnect candidate is present. | `reports/g1/sim/*.log` |
| ↳ `family2-buck-highside-short.cir` | yes | — | `{"bus_peak": 39.812, "o1_peak": 18.8039, "phase_current": 63.6654}` | — | `sim\family2-buck-highside-short.log` |
| family3_startup_uvlo | yes | PASS model criterion | 20→26 V, 18 V fall and 20 V restart; bus/O1 extrema measured in behavioral model | Average behavioral buck model over input startup/fall/restart. Does not exercise WP2 VIN-OK delay, M1-per-EN-rise, dip, or double-pulse gates. | `reports/g1/sim/*.log` |
| ↳ `family3-startup-uvlo.cir` | yes | — | `{"bus_after_restart": 10.9961, "bus_at_20": 10.9954, "bus_at_26": 10.9961, "o1_peak": 10.9996}` | — | `sim\family3-startup-uvlo.log` |
| family4_load_step_comp_corners | yes | FAIL/OPEN | 0.75→7.0→0.75 A, low/typ/high Ceff and corresponding RCOMP; bus extrema logged | Average behavioral controller model with Ceff 92.6514 µF, RCOMP 10.01 kΩ, CCOMP 4.7 nF and CHF 47 pF in the low corner; BUS_MIN is measured 10–12 ms. Internal phase currents/COMP error are not logged; loop gain, phase margin and silicon transient are not validated. | `reports/g1/sim/*.log` |
| ↳ `family4-load-step-minc_lowcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.7109, "bus_recover": 10.9961, "o1_peak": 10.9839}` | — | `sim\family4-load-step-minc_lowcomp.log` |
| ↳ `family4-load-step-typc_midcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.8148, "bus_recover": 10.9961, "o1_peak": 10.9839}` | — | `sim\family4-load-step-typc_midcomp.log` |
| ↳ `family4-load-step-maxc_highcomp.cir` | yes | — | `{"bus_max": 10.996, "bus_min": 10.8596, "bus_recover": 10.9961, "o1_peak": 10.9839}` | — | `sim\family4-load-step-maxc_highcomp.log` |
| family5_efuse_short_hotplug | yes | PASS model criterion | port hot-plug plus O1 short/healthy S2E checks; model-only | Behavioral eFuse switch/latch topology only; no production device timing, MOSFET SOA, thermal, or fixture validation. | `reports/g1/sim/*.log` |
| ↳ `family5-hotplug.cir` | yes | — | `{"o1_final": 10.9973, "o1_peak": 10.9975, "s2e_final": 10.9986}` | — | `sim\family5-hotplug.log` |
| ↳ `family5-o1-short.cir` | yes | — | `{"o1_reset": 5.48046e-11, "o1_short_avg": 1.07836e-12, "o1_short_peak": 10.9973, "s2e_healthy": 10.9973}` | — | `sim\family5-o1-short.log` |

Baseline parity: Linux ngspice-44.2 recorded O1 peak **16.89 V**; Windows ngspice-47 measured **16.89 V**; displayed difference **0.0 V**. Both preserve the expected ~16.89 V failure.

Interpretation: all decks use behavioral approximations, not TI silicon; any SİM criterion pass is not physical acceptance. Family 1 is an ideal source-pulse/latch case; it does not include the proposed independent OVP in Family 2's high-side-short case. Family 1's 11.9741 V remains a narrow model-only result. Family 2's first draft failed setup because REN1 was duplicated; the next detailed topology hit timestep-too-small at xu3.ena. Both logs are retained. A simplified behavioral topology completed and still FAILs the O1 ≤12 V gate at 18.8039 V; no further solver convergence tweaking was done. Family 4 low-Ceff/low-RCOMP minimum remains 10.7109 V, 69.1 mV below the 10.78 V floor; the behavioral model does not validate silicon loop gain or phase margin.

## Targeted real-component OVP screen (existing families rerun)

These are targeted Family 1 timing and Family 2 combined buck-high-side-short + O1-branch OVP reruns. They do not create a sixth G1 condition family. See [OVP engineering result](OVP-ENGINEERING-RESULT.md), [calculation JSON](ovp-component-calculation.json), [simulation JSON](ovp-component-sim.json), and the named decks/logs under `sim/`.

| Condition | Completed / exit | Measurement | Classification |
|---|---|---|---|
| Family 1 ideal switch-off measurement | yes / 0 | Trip-to-series-current-below-1mA = 557.183 ns; analytic ideal-switch edge = 550 ns; O1 peak 11.9741 V | **SİM only.** Ideal B source + switch, not the selected component chain and not a physical measurement. |
| Family 2 short + candidate OVP, 10 µF / 7 A | yes / 0 | O1 11.6900 V; shared bus 40.709 V; S2E 19.0809 V; branch current peak 9.6575 A; series-current turnoff 326.123 ns | O1 is within 12 V in this behavioral case only; design acceptance **BLOCKED**. |
| Family 2 short + candidate OVP, 4 µF / no load | yes / 0 | O1 11.6857 V; shared bus 39.841 V; S2E 18.8274 V. Current-threshold timing is invalid because current is below 1 mA before trip; control-threshold interval is 325.262 ns. | O1 is within 12 V in this behavioral case only; design acceptance **BLOCKED**. |

The 10 µF case is below the provisional 10.332 µF charge-balance screen (11.965 A fast-trip *threshold screen*, 325.4 ns estimated delay, 11.6232 V threshold corner). Its lower SPICE peak does not override that result: the netlist has an ideal eFuse switch, omits the eFuse current-limiter/fast-trip waveform, uses zero ESR/ESL and an ideal controlled FET switch. That current screen is not a guaranteed maximum, so no finite physical Ceff PASS can be issued. The new candidate runs do not replace the retained Family 2 original 18.8039 V **FAIL**, Family 4 10.7109 V **FAIL**, WP1 ESL/N-01 findings, or WP2 69 FAIL / 6 incomplete.
