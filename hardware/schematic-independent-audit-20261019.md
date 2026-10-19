# Independent electrical audit — 2026-10-19

Post-audit update: RFB1/2 now carry a hidden required-selection specification0.1%,≤25ppm/K; exact MPN is still unselected. `docs/SON-TESLIM.md` includes the resulting static error budget and preserves the unresolved UVLO/IMON/fault/protection findings below. This audit otherwise records its read-only snapshot.

Verdict: **NOT READY**. This is a read-only review, not an electrical acceptance certificate. No design, rule or PCB mutation was made by this reviewer.

## Direct evidence collected in this run

Konnect generated `.konnect/diagnostics/audit-current.net` from the saved main schematic. `find_shorted_nets` returned0; ERC returned0errors/0warnings (`audit-erc.json`). Hierarchy-aware connection audit completed for1/1sheet and77symbols with0findings. Decoupling connectivity completed17/17power pins; PCB distance was explicitly not checked. Single-pin net check returned0.

Export confirms primary CONFIG54.9k, secondary90.9k, matching RT49.9k, shared COMP, shared EN, primary SYNCOUT to secondary SYNCIN, primary PFM grounded, secondary FB grounded. These agree with TI SNVSBX7A §7.3.14–15 FPWM dual-phase configuration. Each bootstrap47nF has a series1ohm resistor and returns to its dedicated SW4 pin. SW4 is internally connected to SW1–3; separate schematic SW4 net is intentional, not a missing external wire (pin table p3). BIAS to11Voutput, VCC4.7uF and VDDA0.1uF agree with the pin table. eFuse ITIMER intentionally open selects fastest response; RETRY_DLY grounded selects latch-off; LDSTRT grounded disables handshake; NRETRY grounded is consistent with this unused auto-retry configuration. No newly proven wrong pin/net connection was found in these checks.

## Confirmed blocker

O1 is specified for DC5–12V. Main TPS259824O fixed OVP is16.9Vtypical,16.32–17.31Vdatasheet range; shared behavioral tests peak16.8899746V/16.89V. Even minimum threshold exceeds12V. Existing tests do not model the real5usOVPresponse and cannot bound physical peak. No candidate OVP solution has completed acceptance or been installed. Do not remove this failing test or call the circuit safe to connect to O1.

## New tolerance findings requiring a decision/specification

1. **20V cold startup is not guaranteed by present UVLO.** Nominal RUV180k/10k and maximum EN threshold1.05V give19.95V only with exact resistors. Assuming1%parts,1.05*(1+181800/9900)=20.3318V before shared-EN loading. DatasheetSNVSBX7A electrical characteristics p6 specifies0.95/1.00/1.05V. Exported passive fields do not specify tolerance/MPN. Decide whether guaranteed restart at20V is required, then lower the ratio or narrow resistor tolerance and document battery cutoff/hysteresis. A nominal simulation is insufficient to close this requirement.

2. **11V±2% is not guaranteed with1%feedback resistors.** FB reference0.794–0.806V with130k/10.2k±1% gives10.7132–11.2861V, before bias, temperature and dynamic errors. A0.1%pair gives10.8934–11.0991V before those errors. Specify exact low-TC0.1%MPNs if this is the intended budget, then verify the remaining error terms; do not describe0.1%as already installed.

3. **O1 IMON headroom is nominally narrow.** At nominal4.9605A,2.61k gives~3.185V. Combining the datasheet25°C300ohmcurrent-limit maximum5.23A, scaling to301ohm, maximum GIMON253.4uA/A and+1%RIMON gives~3.48V. TI§7.3.5Table7-2 recommendsIMON<=3.3VforVIN>5Vforlinear headroom. This is a monitor-linearity issue, not an established absolute-maximum violation. No external ADC is connected. Define required monitor range/full-temperature envelope and select lower RIMON accordingly. GIMON accuracy is specified3A–min(15A,ILIM),-40..75°C; S2E2.53Anominal is below this accuracy window, so do not promise3%absolute monitoring accuracy there.

4. **4.96A/2.53A are nominal trip settings.** The exact300ohm datasheet table spans4.36–5.66Aover-40..125°C.301ohmis nearby but the nominal equation is not a guaranteed tolerance. Do not use4.96Aas a hard worst-case connector/trace/load ceiling. The O1actual current remains unknown; no5Aload was assigned.

## Other open gates, distinguished from observed miswiring

### Exact tolerance evidence addendum

LM70880recommendedTJrangeis-40..150°C. The published electrical table contains no guaranteed EN leakage entry. EN hysteresis0.1Vis typical, with no min/max; do not give a guaranteed falling battery cutoff from that number. FBbias75nAis a maximum (p7);130kproduces at most~9.75mVoutput-equivalent contribution, so the0.1%feedback interval above should be widened by~9.76mVbefore resistorTCanddynamicerrors.

TPS25982TJrangeis-40..125°C. ENleakage0.1uAis a maximum (p9MAXcolumn), not a typical value. Two shared ENinputs therefore add up to0.2uA; across64.9kupperRENthis is~12.98mVrail-equivalent threshold shift. Full-temperature ILIMguarantees are tabulated only atR300ohm(4.36–5.66A),773ohm(1.53–2.43A),182ohm(7.23–9.07A),100ohm(12.85–15.99A). No guaranteed interpolation rule for301or604ohmis stated. Equation1460/R+0.11gives only the nominal relation. With1%resistor variation alone,301ohmproduces4.91247–5.00949Aand604ohm2.50329–2.55163A; these intervals omit silicon tolerances. Fasttrip210%ILIMand400nsresponse appear in TYPcolumns, without a guaranteed min/max factor/delay. Nominal fasttrip values10.417Aand5.307Aare not hard safety ceilings. Get TIconfirmation or measure relevant voltage/temperature/part corners before freezing fault-current protection, wireI2tand connectorlimits.

- F1 exact part, DCbreaking capacity/time-current/I2t and cable/TVS coordination remain unselected. Its10Avalue alone is not an engineering acceptance.
- Main COUT25Vparts are exposed to the raw buck output. A high-side short can expose them to20–26Vbattery or higher input transient. A downstream output disconnect does not protect those capacitors. Fault voltage/energy must be bounded before retaining25Vrated parts for that fault requirement.
- COUTeffective capacitance under11Vbias, ESR/temperature, compensation/stability, current sharing, thermal and EMC remain measurement/model gates. Existing behavioral models do not prove them.
- IC footprints are accepted only for prototype mapping. LM70880 copper decomposition/stencil and thermal vias still require manufacturing review. F1missing means thePCBcannotbecomplete.
- Connector exact current/temperature derating, mating cable gauge, polarity and enclosure are not fixed by schematic connectivity. Use worst-case measured/protected current, not nominaltrip, for final wiring.
- Passive MPNs/tolerance/voltage/power ratings are absent in the exported BOM. Documented candidate names and assumedratings are not populated part specifications.

## Heuristic findings reconciled with datasheets

Power-rail audit completed but sees onlyGND,VCC1,VCC2,VDDA1,VDDA2. Its four warnings request>=10uFbulk on every LDOrail; do not apply them blindly: TI explicitly calls forVCC4.7uFandVDDA0.1uF, which are present. Four missingtestpoint suggestions are optional access improvements. Audit scope does not independently inspectVIN/VOUTor physical decoupling distances.

## Documentation contradictions

`docs/design.md` current top update says72placedfootprints, but older paragraphs still claimU1–U4footprintsblank, IPCblocked, noPCB andnofootprints. `simulation/results.md` old footprintblank statement is superseded by the2026-10-19transfer. Clarify these as historical or update them. Electrical parity can remain valid because footprint-only changes do not change pin/net equations.

## Sources and limits

Exact local TI PDFs: `hardware/_datasheets/lm70880-q1.pdf`SNVSBX7A, `hardware/_datasheets/tps25982.pdf`SLVSEI3D. Official source URLs: https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf and https://www.ti.com/lit/ds/symlink/tps25982.pdf . O1 requirement: https://docs.t3gemstone.org/tr/boards/o1/peripherals/introduction (power section). Existing simulator result authority remains `simulation/verification-results.json` and `simulation/results.md`; this reviewer did not rerun a simulation or evaluate candidate-globalOVPtests.
