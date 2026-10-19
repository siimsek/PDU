> Son ek: COUT1–8 artık doğrulanmış TDK100V2220; REN1/2 sağa1.27mm alındı. RIMON1/2=806ohm. Son DRC197bağlantısız/301uyarı; ayrıntı No-measurement-closeout.md. Aşağıdaki299uyarı ve eski parça değerleri önceki yerleşim kaydıdır.

# PDU preliminary PCB placement — 2026-10-19

**Later schematic/rule handoff:** `docs/SON-TESLIM.md` records improved schematic,9 saved netclasses/46 exact assignments and routing calculations using35um nominal/31.5um calculation copper. The earlier70um preference below is now an optional upgrade; no live stackup change was assumed. Existing routing/manufacturing blockers remain.

This supersedes the earlier initial-transfer status. It is not a routed or fabrication-ready board.

## Applied and read back

- User authorized assigning verified U1–U4 footprints; F1 remains pending when its real part is uncertain.
- U3/U4: PDU:TPS25982_RGE0024M, separate VIN pad25 and GND pad26. Disposable symbol/footprint inspection and live readback accepted.
- U1/U2: PDU:LM70880_RRX0029B_RectLands, prototype-compatible representation. VIN/SW boundaries use overlapping same-number rectangular pad pieces with measured deviation below0.007mm. Reduced lower-left VIN stencil aperture and thermal vias require production review; exact manufacturer CAD is not claimed.
- Four IC footprints transferred, library-refreshed and saved.72 total footprints. F1 remains absent/unassigned without an invented MPN.
- Provisional101.6x76.2mm rectangular Edge.Cuts at(50.8,50.8)mm added. Enclosure approval is pending. Minimum project clearance changed from0 to0.20mm, matching the existing design target; fabrication approval remains pending.
- Explicit bounded placement groups: input/reverse-polarity; phase1; phase2; output-capacitor banks; O1 output; S2E output; shared control. Every move was read back through live IPC, with placement/DRC checks after each group. No held/locked footprints were reported by the saved-board diagnostic. No automatic whole-board placement was applied.
- All72 footprints,977 electrical copper pad objects and255 logical pad numbers audited through live IPC: expected net assignments match. Three NPTHs are mechanical. Two missing F1 pins explain257 schematic pins versus255 PCB logical pins.
- Exported before/after netlists agree on all73 values and257 pin-net assignments. Only Q1/U1/U2/U3/U4 footprint fields differ from the simulation baseline. No value, reference, wire, label or net changed.

## Checks

- Schematic short_count0; ERC errors0/warnings0;218 wires and86 labels retained.
- Final schematic-to-PCB dry run: noop; unassigned onlyF1.
- Live placement scorer:100/pass, no courtyard overlaps or outside-outline parts. This certifies only the tool's placement criteria, not hot loops, thermal behavior, stability, EMI or custom-IC decoupling intent.
- Final DRC:197 errors,299 warnings. All errors are unconnected items. No reported copper short, clearance violation, solder-mask bridge, invalid outline or courtyard collision remains. Trace query count0: placement is complete, routing is not.
- Warnings:199 silk-over-copper,19 silk-overlap,3 silk-edge-clearance,5 library-footprint mismatch,72 schematic/PCB Description mismatch,1 missingF1.

## Remaining work and tool limits

1. O1 overvoltage acceptance still fails in the prior shared behavioral simulation suite. No protection candidate has been accepted into the main circuit. This remains a circuit blocker.
2. F1 exact MPN, breaking capacity, time-current curve and battery/wire/TVS coordination remain unresolved; user explicitly allowed waiting.
3. Live stackup reports two0.035mm copper layers and1.6mm board. Existing BOM requests2oz (~0.070mm). This mismatch is unresolved. Konnect get_board_stackup explicitly states KiCad10 UpdateBoardStackup is unimplemented. Power tracks must not be sized as if70um were configured; power/thermal sizing and fabrication contract are open.
4. Installed edit_component exposes only Value. No Konnect argument moves/hides placed footprint Reference/Value text or writes PCB Description. The resulting warnings are preserved, not suppressed; no source-text or Computer Use workaround was used.
5. D1–D3 library refresh remains refused on the unsupported Datasheet unlocked clause. U1/U2 retain mismatch warnings too; live pad coordinates/shapes/layers match library readback at0.0001mm comparison precision, but this does not waive the warning.

## Evidence

- hardware/PDU_blocks_placed.png and .svg: final72-part preliminary placement, visually inspected.
- ../docs/archive/renders/PDU_footprints_assigned.png: new main schematic render.
- hardware/validation/power-ics/: datasheet pages, disposable renders, pin-map records and RRX approximation metrics.
- .konnect/diagnostics/layout-blocks-evidence.json, layout-blocks-pad-audit.json, layout-blocks-final-drc.json, layout-blocks-final-erc.json, power-ics-assigned.net. Earlier per-group DRC files preserve transient staging collisions; those were removed.

No traces, vias, copper zones, fabrication exports, commit, push, lock deletion or direct KiCad source edits were performed.
