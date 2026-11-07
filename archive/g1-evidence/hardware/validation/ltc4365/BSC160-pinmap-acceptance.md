# BSC160N10NS3 G physical pin map

2026-10-19: accepted for prototype connectivity and Konnect placement. This is not manufacturing qualification.

- Manufacturer: Infineon; exact MPN BSC160N10NS3 G, PG-TDSON-8.
- Datasheet: Rev. 2.4, 2009-10-30; pages 1 and 8. Package drawing ZB800003332, revision 03.
- Source: https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc160n10ns3-ds-en.pdf
- Symbol: `Transistor_FET:BSC160N10NS3G`.
- Footprint: `PDU:TDSON-8-1_Konnect`.
- Orientation: component top view, pin-1 marker upper left. Left side runs 1,2,3,4 downward; right side runs 5,6,7,8 upward. Page 8 view-Z land drawing is rotated 180 degrees relative to this canonical KiCad orientation, not mirrored.

Physical lead mapping:

- Lead 1: Source -> symbol pin 1 S -> footprint pad 1, left top.
- Lead 2: Source -> symbol pin 2 S -> footprint pad 2, second left.
- Lead 3: Source -> symbol pin 3 S -> footprint pad 3, third left.
- Lead 4: Gate -> symbol pin 4 G -> footprint pad 4, left bottom.
- Lead 5: Drain -> symbol pin 5 D -> common footprint pad 5, right bottom.
- Lead 6: Drain -> symbol pin 5 D -> common footprint pad 5, second right from bottom.
- Lead 7: Drain -> symbol pin 5 D -> common footprint pad 5, third right from bottom.
- Lead 8: Drain -> symbol pin 5 D -> common footprint pad 5, right top.
- Exposed drain metal: Drain -> symbol pin 5 D -> same continuous copper pad 5.

Eight package leads plus exposed drain reconcile to five electrical symbol pins and five numbered copper pads. The drain is intentionally one continuous land; there are no separate symbol pins 6-8. The eight unnumbered objects are paste-only apertures, not electrical leads. No drills or mechanical pads exist.

The five copper pads and all eight paste apertures match the already selected stock `Package_TO_SOT_SMD:TDSON-8-1` numerically (Konnect query comparison). The unsupported custom mask-only pad was replaced by overlapping filled F.Mask rectangles. Silk, fab, courtyard and STEP association retain the stock geometry. This preserves an inherited stock land choice, not an exact copy of the older datasheet recommended land dimensions. Manufacturing land-pattern review remains open.

Evidence:

- `.konnect/diagnostics/exact-q1-results.json`: library symbol pin readback.
- `.konnect/diagnostics/q1-create-results.json`: created footprint readback and disposable Q_TEST symbol field readback.
- `.konnect/diagnostics/q1-place-live-results.json`: actual live placement of Q_BSC_ACCEPT at 106.68,83.82 mm, rotation 0.
- `.konnect/diagnostics/q1-read-live-results.json`: live IPC readback of 13 pad objects, save success and SVG export success.
- `q1-symbols.png`: disposable symbol render, inspected.
- `q1-accepted.svg` and `q1-accepted-detail.png`: saved disposable board render, inspected; upper-left pin-1 marker, left source/gate lands and continuous right drain land agree with the physical map. Reference text overlaps the disposable footprint in this inspection render; that is not a lead mapping change.
- `bsc160-p1.png` and `bsc160-p8.png`: inspected manufacturer figures.

No claim is made that this pin-map check resolves PDU overvoltage, thermal, SOA, loop stability or manufacturing readiness.
