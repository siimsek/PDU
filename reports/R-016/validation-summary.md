# KiCad 10.0.7 validation summary

Source: PDU.kicad_pcb at commit 661f08cf5c379fed64507e1b767e69534951c4ac.

Command: kicad-cli pcb drc --schematic-parity --refill-zones --severity-all --format json -o reports/R-016/pcb-drc-parity-refill.json PDU.kicad_pcb

- Exit code: 0
- DRC violations: 0
- Schematic parity discrepancies: 0
- unconnected_items: 395

Command: python scripts/pcb_rules.py --check

- Exit code: 0
- Result: {"pass": true, "errors": []}

The DRC JSON is the command-generated output. The board source file remained unchanged; generated files are confined to reports/R-016/.