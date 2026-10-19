# TDK C5750X7S2A226M280KB physical acceptance

2026-10-19. Exact unpolarized22uF100V X7S2220 part. TDKdelivery specification p18 land definition and exact product page were inspected; sources and checksums are in `hardware/COUT-qualification.md`. No manufacturer polarity or numbered lead ordering exists for this symmetric MLCC.

- Physical left end (arbitrary orientation of symmetric body): electrical terminal, Device:C passive pin1, footprint pad1 at(-2.875,0)mm.
- Physical right end: electrical terminal, Device:C passive pin2, footprint pad2 at(+2.875,0)mm.
- Component-side view. Flipping or rotating the nonpolarized body exchanges identical electrodes; no electrical orientation dependency. Two physical terminals, two symbol pins, two copper pads; no duplicate or mechanical pads.
- `PDU:TDK_C5750_2220_Recommended`: rectangular copper/paste/mask pads1.30x4.50mm; innergap4.45mm. This matches TDK A4.1..4.8/B1.2..1.4/C4..5mm. Stock KiCad2220 has1.8x5.4mm lands and was not substituted.
- F.Fab nominal5.7x5.0mm rectangle; maximum body6.1x5.4mm. Courtyard7.85x6.20mm includes maximum body and copper plus0.4mm. No polarity notch or dot retained. 3Dmodel absent; body-height maximum3.1mm remains a mechanical requirement.
- Library pads queried viaKonnect. Disposable symbol C_HV_ACCEPT placed/read back in Pinmap.kicad_sch; Device:C pin1/2 verified passive. Disposable footprint C_HV_ACCEPT placed, refreshed, saved and read back through live IPC: pad1(97.125,110),pad2(102.875,110)mm at origin(100,110), correct1.3x4.5 geometry/layers, no drill.
- Evidence `.konnect/diagnostics/cout-hv-refresh-apply-results.json`; rendered `../ltc4365/cout-hv-detail.png` and `../ltc4365/cout-hv-symbol.png` visually inspected. Symmetric pads, fab/silk/courtyard checked. Reference text is still centered because API lacks a text-position setter; that is a board silkscreen issue, not a polarity ambiguity.

Accepted for prototype electrical placement. Stencil process, reflow profile, flex cracking, thermal behavior, final keepouts and converter loop stability remain separate qualifications.
