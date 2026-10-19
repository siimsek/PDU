# Raw output capacitor qualification — 2026-10-19

## Result

TDK **C5750X7S2A226M280KB** is a real22 µF/100 Vcandidate that resolves the present25 Vraw capacitor rating conflict with a26 Vbuck-short fault, within the project's assumed53.3 Vclamp envelope. It is2220, not1210. Manufacturer data and an isolated manufacturer-model AC run are now available locally. **This is a part/model/land-pattern qualification note, not converter stability or production approval.** No KiCad source was read or mutated by this reviewer.

## Manufacturer files obtained

All files were downloaded unchanged from exact links on the [TDK product page](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB). Ordinary requests returnedAkamaiHTTP403; the already installed `curl_cffi` client with its normal Chrome TLS profile downloaded them successfully. No authentication or model decryption was used.

- `hardware/_datasheets/tdk-c5750-charasheet.pdf`: [public characterization](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c5750x7s2a226m280kb.pdf),2019-03-28.
- `hardware/_datasheets/tdk-c5750-precision.mod`: [precision model](https://product.tdk.com/system/files/dam/tvcl/capacitor/ceramic/mlcc/spice_p/commercial_midvoltage/c5750/c5750x7s2a226m280kb_p.mod),2022-06-16. Plaintext linearRLCmodel, explicitly25°C,0 Vbias,small-signal only.
- `hardware/_datasheets/tdk-c5750-bias-ltspice.zip`: [DC-bias LTspice model archive](https://product.tdk.com/system/files/dam/tvcl/capacitor/ceramic/mlcc/ltspice/commercial_midvoltage/c5750/c5750x7s2a226m280kb_b_ltspice.zip). Its model is encrypted; it was simulated unchanged using its supplied two-pin symbol interface.
- `hardware/_datasheets/tdk-c5750-ecm.pdf`: [equivalent-circuit table](https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/capacitor_mlcc_com_midvoltage_c5750_ecm.pdf),2026-02-27. Simple model row:22 µF,0.650 nH,1.9 mΩ,22 MΩ.
- `hardware/_datasheets/tdk-mlcc-delivery-spec.pdf`: [delivery specificationGC11010030](https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_commercial_general_midvoltage_en.pdf),2026-09. Land dimensions/drawing on printedp18/PDFpage19.

SHA256and byte counts are recorded in `hardware/validation/c5750/vendor-file-hashes.json`. Manufacturer models are reference data, not guaranteed minimum capacitance.

## Actual isolated AC run

`hardware/validation/c5750/vendor-bias-ac.cir` excites the unchanged vendor bias-model with1 VAC about0 Vand11 VDCat25°C. LTspice26.1.1completed both steps in0.114 s. Results are in its `.log` and `vendor-ac-summary.json`. Capacitance is derived from−Im(Isource)/(2πf) at1 kHz; ESRisRe(−1/Isource).

- At0 V: **21.73297 µF** per part.
- At11 V: **20.62219 µF** per part; eight in parallel **164.9775 µF** before tolerance/temperature/aging adjustments.
- At11 V: ESRper part **1.92040 mΩat400 kHz**, **1.91458 mΩat440 kHz**, **1.89195 mΩat1 MHz**. Ideal parallel division by8would give~0.240 mΩat400 kHz; real interconnect parasitics are not included.

The public2019DC-bias chart was independently read using its PDFvector marker coordinates. Linear interpolation of the drawn10–16 Vsegment at11 Vgives−3.31%, or21.2717 µFper nominal22 µFpart. `public-dc-bias-digitized.csv` preserves marker extraction and `public-curve-summary.json` states an assumed±0.5 percentage-point reading uncertainty. The newer vendor model gives~3.1%less capacitance than that curve estimate. This difference is visible evidence of typical-data limitations; the lower20.6222 µFmodel result is the preferred nominal simulation starting point.

## Conservative software envelope

Taking the11 Vvendor-model bank164.9775 µF:

- −20%initial tolerance and−22%X7Stemperature variation: **102.9460 µF**.
- Applying an additional **assumed10%aging sensitivity**, rather than claiming a manufacturer aging guarantee: **92.6514 µF**.
- +20%initial tolerance and+22%temperature: **241.5271 µF**.

These multiplicative combinations are engineering sensitivity cases; manufacturer data does not guarantee independent or joint extrema at11 Voveralltemperatures. Existing44/88 µFcases remain useful pessimistic checks; add a165 µFnominal and~242 µFhigh-capacitance case rather than silently replacing the old coverage. An88 µFminimum assumption should not be called a vendor guarantee merely because these typical-data combinations exceed it. The assembled rating is limited to125°Cby this capacitor and the eFuses, even though the buck ICallows150°C.

## Exact land interpretation and proposed geometry

The manufacturer drawing was rendered and inspected in `hardware/validation/c5750-land-definition.png`; characterization is `c5750-characteristics.png`.

- **PA/A = inner edge gap between pads**, allowed4.1–4.8 mm.
- **PB/B = each pad length along the capacitor length axis**, allowed1.2–1.4 mm.
- **PC/C = pad width perpendicular to that axis**, allowed4.0–5.0 mm.

A central choice isA4.45 mm,B1.30 mm,C4.50 mm. Therefore each rectangular pad is1.30×4.50 mm, centered atx=±(A+B)/2=**±2.875 mm**,y=0. Outer copper span isA+2B=7.05 mm. PAis **not** center pitch. Part nominal body5.7×5.0 mm, maximum6.1×5.4 mm,height3.1 mm maximum. Body and solder lands both need courtyard allowance. A resulting7.55×5.90 mmcourtyard with0.25 mmclearance around the maximum body/copper envelope is a reasonable provisional choice; it is an engineering courtyard, not a TDKdrawing claim.

Nonpolar capacitor: either logical end may be pad1provided the schematic/PCBpair is consistent. Before replacing COUT1–8, perform the required disposable footprint placement/render/readback, assign the verified2220footprint and exact part metadata through Konnect, then update placement/DRC and re-export connectivity. Do not assume an arbitrary stock2220land conforms to this drawing.

## Why this does not prove compensation stability

The current PDU_BUCK model includes the shared external COMPnetwork, but its inner current loop is an explicit approximate500 V/Vsource, plus assumedgm,outputresistance,bandwidthpole andideal clamp behavior. It is not the TIcontroller transistor/driver/sampling model. The vendor capacitor model improves passive impedance accuracy; it cannot supply missing buck-controller dynamics, real current-sampling delay, board parasitics, saturation behavior or two-phase mismatch.

LTspice/ngspiceagreement checks implementation parity of the shared engineering equations. Passing load steps with those equations is a valid model test but does not establish real phase margin. Software progress still available: analyze the TIaveraged small-signal equations with the164.98 µFnominal and broadC/ESRcorners, performACloop-gain/phase-margin analysis with stated model assumptions, then preserve a later measured loop/load-transient acceptance gate. The existingRCOMP9.53k/CCOMP4.7n/CHF47pvalues were selected around88 µF; they must be evaluated at both low and highCcases after a capacitor change, not declared unchanged-stable by inspection.

## Bounded conclusion

The part's identity,100 Vrating,package,land interpretation,typical11 Vcapacitance and typical frequency-dependentESRare now concrete. Applying it can close the capacitor voltage-selection defect within the defined fault envelope. TVSovershoot/energy, O1fastOVP, actual loop/thermal/EMCbehavior and manufacturing acceptance remain separate open requirements.
