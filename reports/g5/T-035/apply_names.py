#!/usr/bin/env python3
"""T-035: fill the empty pin names of the 74LVC1G11 library symbol (U15). Run from the repo root once: python reports/g5/T-035/apply_names.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import kicad_sexpr as ks  # noqa: E402

NAMES = {"1": "A", "3": "B", "4": "Y", "6": "C"}       # TI SN74LVC1G11 SCES487I p.3, DBV package
SCH = ROOT / "PDU.kicad_sch"
tree = ks.parse(SCH.read_text(encoding="utf-8", newline=""))
top = ks.top(tree)
lib = next(top.children("lib_symbols"))
sym = next(s for s in lib.children("symbol") if s.atoms()[1].value == "74xGxx:74LVC1G11")
done = {}


def walk(node):
    for ch in node.children():
        if ch.head == "pin":
            num = next(ch.children("number")).atoms()[1].value
            if num in NAMES:
                name = next(ch.children("name"))
                a = name.atoms()[1]
                assert a.value == "", (num, a.value)
                name[name.index(a)] = ks.Atom(ks.quote(NAMES[num]))
                done[num] = NAMES[num]
        elif ch.head == "symbol":
            walk(ch)


walk(sym)
assert done == NAMES, done
SCH.write_text(ks.dumps(tree), encoding="utf-8", newline="")
print(done)
