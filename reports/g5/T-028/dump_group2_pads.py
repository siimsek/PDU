#!/usr/bin/env python3
"""T-028 group 2: reads pad geometry of the G2 references from the board, read only.
Run from the repo root with KiCad's Python: "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" reports/g5/T-028/dump_group2_pads.py"""
import hashlib
import json
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-028"
PCB = ROOT / "PDU.kicad_pcb"
group = json.loads((OUT / "coverage-plan.json").read_text(encoding="utf-8"))["groups"]["G2"]
board = P.LoadBoard(str(PCB))
rows = {}
for ref in group:
    fp = board.FindFootprintByReference(ref)
    rows[ref] = {p.GetNumber(): {"x": round(P.ToMM(p.GetFPRelativePosition().x), 4), "w": round(P.ToMM(p.GetSize(P.F_Cu).x), 4), "h": round(P.ToMM(p.GetSize(P.F_Cu).y), 4)} for p in fp.Pads()}
doc = {"board": "PDU.kicad_pcb", "board_sha256": hashlib.sha256(PCB.read_bytes()).hexdigest(), "refs": rows}
(OUT / "group2-board-pads.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(len(rows))
