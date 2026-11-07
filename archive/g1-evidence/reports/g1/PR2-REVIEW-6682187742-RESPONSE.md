# PR #2 comment 6682187742 — technical response

Reference: [independent review comment](https://github.com/siimsek/PDU/pull/2#issuecomment-6682187742). The findings are valid; the additions below keep design acceptance **BLOCKED**.

## Finding-by-finding

| Review finding | Verification / response | Status |
|---|---|---|
| G1-R2-01: measure the actual switch-off edge, not just `TDELAY` | Added a direct ngspice measurement from O1 trip crossing to series current below 1 mA. In the ideal Family 1 switch model this is 557.183 ns; analytic control-threshold crossing is 550 ns. Model current goes 4.48628 A to 4.93 pA. This is **not** a physical component or board measurement. | SİM measured; hardware **AÇIK** |
| G1-R2-02: size minimum Ceff and fault-current margin at worst case | Updated upper threshold corner is 11.6232 V. A provisional 11.965 A fast-trip *threshold screen* and 325.4 ns estimated switch timing imply 10.332 µF ideal Ceff. At the 557.183 ns ideal-switch timing screen the same current implies 17.691 µF. The 10 µF model corner is below the shorter-delay screen. TPS259824O fast-trip threshold is not a hard current clamp, so the physical fault current/time envelope and finite worst-case Ceff are **not established**. ESR/ESL, turn-off tail, probe uncertainty, COUT DC-bias/tolerance/aging also remain outside the equation. | HESAP screen; physical min **AÇIK** |
| G1-R2-03: select actual comparator/reference/latch/driver/FET MPNs | Candidate chain: `TLV3601DCKR`, `REF5025AQDRQ1`, `SN74LVC1G74DCUR`, `LTC7001EMSE#PBF`, 2× `CSD19536KTTT`, `TPS7A1601QDGNRQ1`, `TPS7A1650QDGNRQ1`; packages, datasheet pages, limits and availability caveats are in [OVP-ENGINEERING-RESULT.md](OVP-ENGINEERING-RESULT.md) and [OVP-COMPONENT-REVIEW.md](OVP-COMPONENT-REVIEW.md). Several delay numbers are conditional on different datasheet test loads/overdrive. CSD19536KTTT's SOA graph begins at 100 µs and does not verify the ~0.325 µs estimate. Exact divider resistor MPN and startup/reset/ARM schematic remain open. | Candidate for lab engineering; no design PASS |
| G1-R2-03: test high-side short and proposed OVP in the same electrical model | Two completed Family 2 behavioral cases add the O1 branch switch to the same high-side-short scenario. At 10 µF/7 A: O1 11.6900 V, bus 40.709 V, S2E 19.0809 V, OVP branch current peak 9.6575 A, measured series-current cutoff 326.123 ns. At 4 µF/no-load: O1 11.6857 V and S2E 18.8274 V; the 1 mA current crossing occurs before the trip window, so that current-based turnoff measure is marked invalid and only the control-threshold interval is shown. Both model O1 peaks are below 12 V, but the result is **not worst case**: eFuse current dynamics and parasitics are absent. | SİM behavioral screen only; design acceptance **BLOCKED** |
| G1-R2-04: keep test boundaries fail-closed | Automated checks require the current-edge measurement, keep original Family 2/4 FAIL flags, require the two combined scenarios to remain BLOCKED, and reject a negative current-crossing delay as valid. Full test suite result is recorded in [TEST-RESULTS.md](TEST-RESULTS.md). | Test result is not electrical acceptance |

## Retained findings and limits

- Original Family 2 without independent OVP remains **18.8039 V FAIL**. The Family 2 behavioral scenario with candidate OVP does not replace that historical failure.
- The proposed 3.59 kΩ / 1.00 kΩ threshold divider produces 11.6232 V at its upper corner, 163.2 mV above the previous provisional 11.46 V target. The computed continuous Rtop window for trip-min ≥11.1605 V and trip-max ≤11.46 V is only 3.52195…3.52569 kΩ (3.74 Ω wide) and leaves no ripple/noise margin; no divider MPN was selected.
- Family 4 load step remains **10.7109 V FAIL**. WP1 four incomplete ESL cases and N-01 remain open. WP2 remains **69 FAIL / 6 incomplete**.
- The candidate O1 switch cannot protect S2E from shared-bus overvoltage; the model shows about 19 V on S2E and its numeric device limit is still missing.
- The 10 µF behavioral combined run is below the provisional 10.332 µF ideal charge-balance screen, even though its simulated O1 peak is 11.6900 V. This difference reflects the model's limited current profile; it does not justify changing the calculation or accepting the design.
- No board, oscilloscope capture, physical fault injection, FET SOA proof, purchaseable stock reservation, or thermal proof was available. No physical measurement was performed.

Detailed calculation, official manufacturer datasheets, model scope, simulation logs and open engineering closure inputs are linked from [OVP-ENGINEERING-RESULT.md](OVP-ENGINEERING-RESULT.md). `main`, PR #1, and all KiCad files were left untouched. No merge was made.
