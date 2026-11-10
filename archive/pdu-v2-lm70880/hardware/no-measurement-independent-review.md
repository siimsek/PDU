> This is a historical pre-application review. FB/IMON/COUT choices were subsequently applied; currentstatus: docs/PROJECT-STATE.md and hardware/no-measurement-final-audit.md.

# Independent choices that can be resolved without measurements

2026-10-19. Read-only reviewer: no schematic, PCB or rule mutation. Component specifications below were checked against exact manufacturer pages, rather than inferred from distributor search titles. They are choices for the design owner to apply through Konnect.

**Follow-up:** the TDKdownload/model-data obstacle described in section3was subsequently resolved. Exact files, land drawing, public-chart extraction and an actual encrypted-vendor-model LTspiceACrun are now documented in `hardware/COUT-qualification.md`. The measured model value is20.62219 µFper part at11 V/25°C/1 kHz. EarlierHTTP403remarks below are historical, not a current blocker.

## 1. Feedback pair: exact selection ready to apply

- RFB1: **Panasonic ERA3AEB134V**, 130 kΩ, 0.1%, ±25 ppm/K, 0603, 0.100 W. [Exact manufacturer page](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB134V).
- RFB2: **Panasonic ERA3AEB1022V**, 10.2 kΩ, otherwise the same specification. [Exact manufacturer page](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB1022V).

These match the existing nominal values and footprint. MPN/datasheet/tolerance/TCR/power metadata can be populated now without changing the circuit. ERA3AEB134V uses the E24 code134; the unverified code ERA3AEB1303V must not be invented. No claim about current stock, price or delivery is made.

The nominal setpoint is0.8*(1+130000/10200)=10.99608 V. Using the LM70880 FB-reference limits0.794–0.806 V, independent0.1% initial resistor errors, and maximum75 nA FB bias gives approximately10.8836–11.1089 V at25°C. Conservatively adding independent opposing ±25 ppm/K resistor drift over100 K (25→125°C) gives10.8332–11.1605 V, or−1.516%/+1.459% relative to11 V. This assumes both resistors stay within the specified temperature range; aging, solder drift and dynamic ripple/load error are separate. This closes the previously unspecified static initial tolerance; it does not prove total±2% operation under every transient.

Calculation: eR=0.001+25e-6*100; Vmin=0.794*(1+130000*(1-eR)/(10200*(1+eR)))-75e-9*130000*(1+eR); Vmax uses opposite resistor extremes and adds the bias term. A130k/10.2kpair is retained; substituting125k changes the nominal target to10.6039 V and is not equivalent.

## 2. IMON: concrete conservative resistor option

Recommended monitor-headroom option: **RIMON1=RIMON2=806 Ω**, Panasonic **ERA3AEB8060V**,0.1%,±25 ppm/K,0603,0.100 W. [Exact manufacturer page](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB8060V).

This changes monitor conversion gain only. It does not change ILIM301/604 Ω or assign a5 A O1load. There is no external ADC tied to these nets in the reviewed export. Nominal conversion is0.198276 V/A; nominal voltages at the existing nominal trip settings are0.98355 V for O1and0.50109 V for S2E.

The TPS25982 published GIMONmaximum is253.4 µA/A, specified only for3 A≤IOUT≤min(15 A,ILIM) and−40..75°C. Using15 A as a conservative upper evaluation point for that specified domain,806 Ω and0.1%+65 K*25 ppm/K yields3.07165 V, below TI's3.3 V recommended monitor headroom. The calculation is15*253.4e-6*806*(1+0.001+65*25e-6). Actual accuracy above the configured ILIMor below3 A is not promised. In particular the S2E2.53 Asetting falls below the published accuracy window. The15 Acalculation does not imply the configured branch is permitted to supply15 A.

The present2.61kΩ O1monitor can exceed3.3 Vunder a25°C high-current-limit corner.806 Ω resolves the narrow nominal conversion range without relying on guessed full-temperature301/604 Ω trip maxima. A2kΩ/3.83kΩpair gives more ADC resolution but still relies on an incomplete branch-current envelope; with no ADC specified, the broader806 Ωchoice is easier to justify.

Limits: GIMONhas no guaranteed bound over75..125°C in this datasheet. Fasttrip current and transient monitor clipping are not certified by this calculation. Lowering RIMONdoes not fix the O1overvoltage path. If applied, regenerate both SPICE models/test expectations and rerun the common suite; retain the existing failing OVP acceptance.

## 3. Raw COUT: exact voltage candidate, footprint work required

Verified candidate: **TDK C5750X7S2A226M280KB**,22 µF±20%,100 VDC,X7S,2220,5.7×5.0×2.8 mm,−55..125°C,commercial grade (not AEC-Q200). [Exact manufacturer page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB). [Manufacturer characterization PDF](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c5750x7s2a226m280kb.pdf).

This retains22 µFnominal per capacitor and provides voltage rating above the project's assumed53.3 Vinput TVS clamp. The existing25 Vraw COUTcannot cover the stated26 Vbuck-high-side-short condition;50 Vdoes not cover53.3 V.100 Vrating addresses this capacitor voltage-selection defect within that defined fault-voltage envelope. It does not prove the TVS energy/overshoot envelope or protect O1.

It is **not** a drop-in1210part. The design owner must validate the2220land pattern through the disposable footprint workflow, change only COUT1–8footprints/MPNs and voltage metadata, update placement and run DRC. Manufacturer recommended lands are provided on the product page; the existing2220generic footprint cannot simply be assumed accepted. No protected source-text edits are justified.

DC-bias/ESR curves exist in the linked PDF and manufacturer model links are provided on the product page. These are typical characterization, not guaranteed minimum Ceff. This review's direct PDF download returnedHTTP403; no numeric curve point was extracted or invented. Before electrical acceptance, obtain the curve/model, compute Ceff at11 Vwith tolerance/temperature/aging and check compensation/load steps with the resulting range. Nominal8*22 µF=176 µFmust not replace the previous88/44 µFmodel assumptions without evidence. The new candidate permits software progress, but its nominal capacity and larger case alone do not close stability.

## 4. Application order and bounded outcome

1. Apply exact FB metadata now; verify values and nets unchanged.
2. Apply806 Ωmonitor option only if the design owner accepts the explicit lower conversion gain; this is a bounded electrical change, so export, rebuild both simulator inputs and rerun acceptance.
3. Complete manufacturer-model/land-pattern validation for100 Vraw COUT, then apply and check its revised capacitance/compensation envelope. Do not stop merely because physical measurement is unavailable; numeric manufacturer characterization and footprint acceptance can be pursued now.
4. Keep O1fast OVP, F1fault coordination, temperature/loop/EMCbench evidence and actual load profiles explicitly open. None is silently resolved by these part selections.

This document selects real parts and quantifies software-solvable changes. It does not claim the design is complete or production-ready.
