"""R-010: canonical Value rule — every schematic symbol's Value equals the spec value (single source analysis/g2/bom.py).

    python scripts/sch_values.py      # sets Value for every spec ref present in PDU.kicad_sch
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "PDU.kicad_sch"


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from analysis.check_consistency import parse_spec
    spec, _ = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    root = ks.parse(SCH.read_bytes().decode("utf-8"))
    changed = []
    for ref, row in spec.items():
        sym = ks.symbol_by_ref(root, ref)
        if sym is None:
            continue
        old = next((p.atoms()[2].value for p in sym.children("property") if p.atoms()[1].value == "Value"), None)
        if old != row["value"]:
            ks.set_property(root, ref, "Value", row["value"])
            changed.append(f"{ref}: {old!r} -> {row['value']!r}")
    SCH.write_bytes(ks.dumps(root).encode("utf-8"))
    print(f"{len(changed)} values set"); print("\n".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
