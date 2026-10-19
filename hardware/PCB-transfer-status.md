# PDU initial PCB transfer — 2026-10-19

**Superseded:** See `PCB-layout-status.md` for the later72-footprint placement, U1–U4 assignments, provisional outline and current DRC. Below is the earlier68-footprint transfer.

MCP/API connection is restored. This is an initial component staging transfer, not a completed layout or production approval.

- Q1 footprint changed from stock TDSON-8-1 to PDU:TDSON-8-1_Konnect after disposable live pin-map validation. Copper and paste geometry match the stock selection; mask representation is compatible with Konnect typed placement.
- Exported netlists before/after agree on all 73 component values and all 257 pin-net assignments. Q1's footprint is the only footprint field difference. Existing simulation electrical inputs remain equivalent; simulations were not rerun for this footprint-only change.
- Main schematic short_count 0, ERC errors 0 / warnings 0. No schematic wire, label, reference or value was changed during this transfer.
- 68 footprints added and saved through live IPC. All 143 electrical pads match the reviewed transfer plan; three unnumbered connector mounting holes remain without nets. A subsequent sync dry run reports noop.
- F1 and U1–U4 remain unassigned/absent from the PCB as instructed. F1 has no invented MPN. O1 current settings are unchanged.
- Initial placement is Konnect's vertical staging column (approximately y=0.73–540.56 mm), not a functional PCB arrangement. There are no routed traces or board outline yet.
- Library refresh corrected 65 placed footprints. D1–D3 refresh was refused before mutation because the library Datasheet property has an unsupported `unlocked` clause. Three library-mismatch warnings remain; they have not been waived.

Final DRC: **103 errors, 77 warnings**, 180 total findings:

- 1 invalid outline error (no Edge.Cuts).
- 102 unconnected-item errors (unrouted).
- 3 library footprint mismatch warnings (D1–D3).
- 1 Q1 reference silkscreen-over-mask warning.
- 68 schematic/PCB Description field mismatch warnings (Konnect sync does not transfer this field).
- 5 missing-footprint warnings (F1, U1–U4).

The last full electrical simulation suite still has an O1 overvoltage acceptance failure. This transfer does not resolve or approve that condition. Pin-map acceptance is separate from SOA, thermal, stability and protection qualification.

Evidence: `.konnect/diagnostics/pcb-transfer-evidence.json`, `pcb-transfer-pad-audit.json`, `pcb-transfer-final-drc.json`, `pcb-transfer-erc.json`, `pcb-transfer.net`; `hardware/validation/ltc4365/BSC160-pinmap-acceptance.md`.

Updated schematic image: `../docs/archive/renders/PDU_after_pcb_transfer.png`. PCB export: `hardware/PDU_initial_transfer.svg`; its page-sized view clips the long staging column, so `hardware/PDU_initial_transfer-staging.png` expands the exported SVG viewport to show all staged parts. No source geometry is changed by that image conversion.

No commit, push, lock deletion, routing or fabrication export was performed.
