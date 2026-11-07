"""T-013 PCB DRC gate (stdlib + kicad-cli; run after pcb_setup.py and pcb_rules.py):

    python scripts/pcb_drc.py          # writes reports/g5/T-013/drc-empty.json, drc-placed.json, drc-summary.json, placement.svg

* Empty board = PDU.kicad_pcb with every schematic footprint removed (outline, stackup, mounting holes, keep-outs,
  region marks kept), checked in a temp copy next to PDU.kicad_pro / PDU.kicad_dru -> must have 0 errors (T-013).
* Placed board = PDU.kicad_pcb with --schematic-parity -> parity issues must be 0; the only allowed errors are
  unconnected items (no routing in T-013, PCB-HANDOFF §8); warnings (silkscreen) are listed, not gated.
"""
from __future__ import annotations

import collections
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g5" / "T-013"
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
ALLOWED_PLACED_ERRORS = {"unconnected_items"}


def strip_footprints(text: str) -> str:
    root = ks.parse(text)
    pcb = ks.top(root)
    for fp in list(pcb.children("footprint")):
        if next(fp.children("path"), None) is not None:      # schematic footprint (mounting holes have no path)
            i = next(k for k, x in enumerate(pcb) if x is fp)
            if i > 0 and isinstance(pcb[i - 1], ks.WS):
                del pcb[i - 1]
            ks.remove_node(pcb, fp)
    return ks.dumps(root)


def drc(pcb: Path, out: Path, parity: bool) -> dict:
    cmd = [CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", str(out), str(pcb)]
    if parity:
        cmd.insert(3, "--schematic-parity")
    subprocess.run(cmd, check=True, capture_output=True)
    d = json.loads(out.read_text(encoding="utf-8"))
    return {k: dict(collections.Counter(f"{x['severity']}:{x['type']}" for x in d.get(k, [])))
            for k in ("violations", "unconnected_items", "schematic_parity")}


def errors(summary: dict, allowed=frozenset()) -> dict:
    return {f"{k}/{t}": n for k, c in summary.items() for t, n in c.items()
            if t.startswith("error:") and t.split(":", 1)[1] not in allowed}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for f in ("PDU.kicad_pro", "PDU.kicad_dru"):
            shutil.copy(ROOT / f, t / f)
        (t / "PDU.kicad_pcb").write_bytes(strip_footprints((ROOT / "PDU.kicad_pcb").read_bytes().decode("utf-8")).encode("utf-8"))
        empty = drc(t / "PDU.kicad_pcb", OUT / "drc-empty.json", parity=False)
    placed = drc(ROOT / "PDU.kicad_pcb", OUT / "drc-placed.json", parity=True)
    n_parity = sum(placed["schematic_parity"].values())
    res = {"kicad_cli": CLI.split("\\")[-1], "empty_board": empty, "placed_board": placed,
           "empty_errors": errors(empty), "placed_errors_not_allowed": errors(placed, ALLOWED_PLACED_ERRORS),
           "schematic_parity_issues": n_parity}
    res["pass"] = not res["empty_errors"] and not res["placed_errors_not_allowed"] and n_parity == 0
    with (OUT / "drc-summary.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    subprocess.run([CLI, "pcb", "export", "svg", "--layers", "Edge.Cuts,F.CrtYd,F.Fab,Dwgs.User",
                    "--mode-single", "--exclude-drawing-sheet", "--fit-page-to-board", "-o", str(OUT / "placement.svg"),
                    str(ROOT / "PDU.kicad_pcb")], check=True, capture_output=True)
    print(json.dumps({k: res[k] for k in ("empty_errors", "placed_errors_not_allowed", "schematic_parity_issues", "pass")}))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
