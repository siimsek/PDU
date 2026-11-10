> **SUPERSEDED (G3, 2026-11-07) → reports/g2/PROTECTION-DECISION.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# O1 OVP: component and timing feasibility screen

Etiketler: **DATASHEET** = manufacturer specification; **HESAP** = reproducible calculation; **SİM** = ngspice model; **AÇIK** = unbounded or unmeasured; **VARSAYIM** = explicit scenario input.

## Conclusion

**AÇIK / BLOCKED.** A concrete component chain is identified below, but this analysis does not produce a guaranteed end-to-end switch-off time or a bounded fault current. The 12.0 V O1 maximum therefore cannot be accepted. The Family 2 and Family 4 FAILs remain unchanged.

## Candidate chain (datasheets and exact orderables)

| Function | Candidate MPN | Package | Evidence / limit |
|---|---|---|---|
| Comparator | `TLV3601DCKR` | SC70-5 | DATASHEET: ±5 mV offset, 5 µA max input bias, 4.5 ns max only at 50 mV overdrive, −40…125 °C. |
| Precision reference | `REF5025AQDRQ1` | SOIC-8 | DATASHEET: 2.5 V, 0.1% initial accuracy, 8 ppm/K max drift, −40…125 °C. |
| Set/reset memory | `SN74LVC1G74DCUR` | VSSOP-8 | Active-low asynchronous CLR/PRE; CLR-to-Q max 6.1 ns at 5 V and −40…125 °C. Requires a fail-safe power-up clear, one-way fault injection to CLR and deliberate manual ARM through PRE. |
| High-side driver | `LTC7001EMSE#PBF` | 10-lead MSOP with exposed pad | DATASHEET: VCC 3.5…15 V, 70 ns max input-to-output at 1 nF, pull-down 4 Ω max at VCC=VBST=12 V. |
| Back-to-back FETs | `CSD19536KTTT` ×2 | TO-263 / D2PAK | DATASHEET: 100 V, 2.8 mΩ max at VGS=6 V, Qg 153 nC max at VGS=10 V; SOA plot's shortest curve is 100 µs. |
| 12 V driver rail | `TPS7A1601QDGNRQ1` | HVSSOP-8 / DGN | Adjustable high-voltage LDO candidate; exact divider, startup and power-good reset must be designed. |
| 5 V analog/logic rail | `TPS7A1650QDGNRQ1` | HVSSOP-8 / DGN | Fixed 5 V high-voltage LDO candidate. |
| Threshold divider | 3.59 kΩ / 1.00 kΩ, each 0.1%, ≤25 ppm/K | TBD | **VARSAYIM** component class; exact resistor MPN and layout not selected. Nominal trip 11.475 V. |

No distributor stock claim is made. TI's live pages showed `TLV3601DCKR`, `REF5025AQDRQ1`, and `CSD19536KTTT` as out of stock when checked; exact purchaseable stock for the other candidates was not verified. TI marks `SN74LVC1G74DCUR` active; the candidate's availability is not confirmed. Manufacturer status is not a BOM purchase reservation. The previous dual-NOR proposal `SN74LVC2G02` was dropped because TI's product page says it is in production to support existing customers and is not recommended for new designs.

## Trip threshold corner

| Quantity | Result | Label |
|---|---:|---|
| Nominal threshold | 11.4750 V | HESAP |
| Enumerated threshold minimum | 11.3281 V | HESAP |
| Enumerated threshold maximum | 11.6232 V | HESAP |
| Conservative interval maximum | 11.6233 V | HESAP cross-check |
| Minimum trip margin above 11.1605 V bus limit | 167.6 mV | HESAP; O1 ripple/noise not included |
| Maximum headroom to 12.0 V | 376.8 mV | HESAP; ESR/ESL excluded |
| Previous provisional upper trip target | Candidate exceeds 11.46 V by 0.163 V | HESAP; 3.59 kΩ divider does not meet that earlier target |
| Theoretical Rtop interval for trip-min >= bus max and trip-max <= 11.46 V | 3521.95…3525.69 Ω | HESAP only; 3.74 Ω total width and no ripple/noise margin |
| Difference: corner enumeration vs interval propagation | 0.099 mV | independent bound check |

Corner includes reference initial accuracy and temperature drift, resistor tolerance/TCR, comparator offset, maximum hysteresis and maximum input bias current. Resistors were assumed 0.1%/25 ppm/K because the proposed design class is not yet selected; O1's actual ripple and noise are not supplied.

## Switch-off time and Ceff/fault-current margins

The older ideal Family 1 deck has an ideal timer nominally set to 0.500 µs. The model's switch opens when CTRL falls below `Vt−Vh = 0.45 V`; CTRL begins at 1 V and discharges at 1 V/µs. Therefore the **calculated ideal-model trip-to-open is 0.550 µs**, and the new measurement deck measures the same edge pair. This is not a physical measurement.

| Timing contribution | Value | Source / limit |
|---|---:|---|
| Comparator | 4.5 ns | DATASHEET max only at 50 mV overdrive; low-overdrive delay not bounded |
| FF asynchronous clear | 6.1 ns | DATASHEET CLR→Q max at 5 V, −40…125 °C |
| Gate driver | 70.0 ns | DATASHEET max with 1 nF load, not the selected FET pair |
| Pair gate discharge screen | 244.8 ns | HESAP: 306 nC ÷ (5 V / 4 Ω); 5 V Miller plateau is an assumption |
| Summed engineering estimate | 325.4 ns | HESAP only; **not a guaranteed upper bound** |
| Physical switch-off measurement | Not performed | AÇIK: no assembled board / probe capture in this workspace |

**Ceff screen.** Using the threshold upper corner 11.6232 V and a provisional 11.96 A current screen from the existing O1 eFuse's high-temperature ILIM maximum and nominal 2.1× fast-trip threshold, the calculated Ceff minimum is **10.33 µF** for the 325.4 ns timing estimate. Closed-form charge balance and numerical bisection of the same overshoot inequality differ by 0.000 pF; this is an algorithmic cross-check, not independent physical evidence. At 10 µF the idealized peak screen is 12.012 V; at 4 µF it is 12.596 V. These omit ESR, ESL, turn-off tail and measurement error.

This is **not** a bounded worst-case result: the eFuse is a circuit-breaker part, and 2.1×ILIM is a fast-trip trigger, not a current clamp. The 400 ns short-circuit response is not accepted as a maximum fault-current bound for this OVP chain. With the old Family 2 model's 63.6654 A phase-current stress, the same idealized formula requires 55.0 µF; that phase current is not an O1 output-current measurement. Thus no finite physical Ceff minimum can be signed off until the fault current/time envelope and actual port capacitor part are established.

## MOSFET and SOA screen

Two `CSD19536KTTT` devices give a 5.6 mΩ pair at the datasheet's 6 V gate-drive test point and about 0.315 W at 7.5 A at that test corner. Hot RDS(on) needs the datasheet's curve and the selected board thermal path; it is not folded into a guaranteed thermal result. Qg max is 153 nC each at 10 V. The estimated 0.325 µs turn-off lies far below the datasheet SOA plot's 100 µs shortest pulse curve. The fault VDS/current division across the two FETs is not known. **SOA: AÇIK; no PASS.**

## S2E and fault-source separation

This OVP switch is on the O1 branch only. A buck high-side short raises the shared VOUT feeding both eFuses; an O1 series disconnect does not isolate S2E. TPS259824O's internal 16.9 V nominal OVLO (16.32…17.31 V rising datasheet range) is above 12 V and its 5 µs OVP response cannot establish S2E protection without a numeric S2E input/absolute-maximum limit. Direct external O1 backfeed also bypasses an upstream-only disconnect unless the candidate switch is physically placed at the port connector. These are separate unresolved fault paths.

## Official manufacturer references

- [TI TLV360x datasheet](https://www.ti.com/lit/ds/symlink/tlv3601.pdf), pp. 1, 3, 7 (package, limits, propagation/offset/bias).
- [TI REF50xxA-Q1 datasheet](https://www.ti.com/lit/ds/symlink/ref5025a-q1.pdf), pp. 1, 5–6 (accuracy, drift, load/line and temperature range).
- [TI SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), pp. 1, 4, 7 (asynchronous preset/clear, package, CLR-to-Q delay).
- [ADI LTC7001 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc7001.pdf), pp. 1–3, 8–9 (supply, gate drive, propagation and output resistance).
- [TI CSD19536KTT datasheet](https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf), pp. 1–2, 5–6 (ratings, gate charge, RDS(on), SOA).
- [TI TPS7A16-Q1 datasheet](https://www.ti.com/lit/ds/symlink/tps7a16-q1.pdf), pp. 1, 6 (input/output range and accuracy).
- [TI TPS25982 datasheet](https://www.ti.com/lit/ds/symlink/tps25982.pdf), pp. 1, 8–10, 23–26 (current threshold, trip response and circuit-breaker behavior).

Reproduce with `python analysis/ovp_component_analysis.py`; tests are in `analysis/test_ovp_component_analysis.py`.
