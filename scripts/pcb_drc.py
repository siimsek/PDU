"""T-013 PCB DRC gate (stdlib + kicad-cli; run after pcb_setup.py and pcb_rules.py):

    python scripts/pcb_drc.py          # writes reports/g5/T-013/drc-empty.json, drc-placed.json, drc-summary.json, placement.svg

* Empty board = PDU.kicad_pcb with every schematic footprint removed (outline, stackup, mounting holes, keep-outs,
  region marks kept), checked in a temp copy next to PDU.kicad_pro / PDU.kicad_dru -> must have 0 errors (T-013).
* Neck-down audit (R-012 #2): every power-class track narrower than its class min must be >= 0.25 mm, <= 1.5 mm
  long and end on a fine-pitch pad of the same net whose footprint is in that class's neck-down list.
* Placed board = PDU.kicad_pcb with --schematic-parity -> parity issues must be 0; the only allowed errors are
  unconnected items (no routing in T-013, PCB-HANDOFF §8); warnings (silkscreen) are listed, not gated.
"""
from __future__ import annotations

import collections
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
import pcb_rules as pr  # noqa: E402

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


def _rot(x: float, y: float, deg: float):
    """KiCad rotation (y down, positive = counter-clockwise on screen)."""
    c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return x * c + y * s_, -x * s_ + y * c


def fine_pads(text: str, rows: dict) -> list:
    """[(cls, ref, net, cx, cy, w, h, rot)] absolute fine-pitch power pads of the neck-down footprints."""
    neck, ncls = pr.neck_refs(rows, text), pr.power_net_class(rows)
    out = []
    for ref, (fx, fy, frot), pads in pr.footprint_pads(text):
        for _, (px, py, w, h, prot), net in pads:
            cls = ncls.get(net)
            if cls and ref in neck[cls] and min(w, h) <= pr.FINE_PITCH_PAD_MM + 1e-9:
                dx, dy = _rot(px, py, frot)
                out.append((cls, ref, net, fx + dx, fy + dy, w, h, prot))
    return out


def _in_pad(x: float, y: float, pad) -> bool:
    _, _, _, cx, cy, w, h, rot = pad
    lx, ly = _rot(x - cx, y - cy, -rot)
    return abs(lx) <= w / 2 + 1e-6 and abs(ly) <= h / 2 + 1e-6


def neck_audit(text: str, rows: dict) -> list:
    ncls = pr.power_net_class(rows)
    mins = {cls: pr.up(rows[row]["outer_width_min_mm"]) for row, cls in pr.CLASS_OF.items()}
    pads = fine_pads(text, rows)
    bad = []
    for seg in ks.top(ks.parse(text)).children():
        if seg.head not in ("segment", "arc"):
            continue
        net = next(seg.children("net"), None)
        net = net.atoms()[-1].value if net is not None else ""
        cls = ncls.get(net)
        w = float(next(seg.children("width")).atoms()[1].value)
        if not cls or w >= mins[cls] - 1e-6:
            continue
        a, b = (tuple(float(v.value) for v in next(seg.children(k)).atoms()[1:3]) for k in ("start", "end"))
        length = math.dist(a, b)
        ends = any(_in_pad(*pt, pd) for pt in (a, b) for pd in pads if pd[0] == cls and pd[2] == net)
        why = [m for m, ok in (("width < neck min", w >= pr.NECK_MIN_MM - 1e-6),
                               (f"length {length:.2f} > {pr.NECK_MAX_LEN_MM:g} mm", length <= pr.NECK_MAX_LEN_MM + 1e-6),
                               ("not ended on a fine-pitch pad of the same net", ends)) if not ok]
        if why:
            bad.append({"net": net, "class": cls, "width": w, "start": a, "end": b, "why": why})
    return bad


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
    text = (ROOT / "PDU.kicad_pcb").read_text(encoding="utf-8")
    rows = pr.routing_rows()
    neck = neck_audit(text, rows)
    res = {"kicad_cli": CLI.split("\\")[-1], "empty_board": empty, "placed_board": placed,
           "empty_errors": errors(empty), "placed_errors_not_allowed": errors(placed, ALLOWED_PLACED_ERRORS),
           "schematic_parity_issues": n_parity,
           "neck_down": {"refs": pr.neck_refs(rows, text), "fine_pitch_pads": len(fine_pads(text, rows)),
                         "max_len_mm": pr.NECK_MAX_LEN_MM, "min_mm": pr.NECK_MIN_MM, "violations": neck}}
    res["pass"] = not res["empty_errors"] and not res["placed_errors_not_allowed"] and n_parity == 0 and not neck
    with (OUT / "drc-summary.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    subprocess.run([CLI, "pcb", "export", "svg", "--layers", "Edge.Cuts,F.CrtYd,F.Fab,Dwgs.User",
                    "--mode-single", "--exclude-drawing-sheet", "--fit-page-to-board", "-o", str(OUT / "placement.svg"),
                    str(ROOT / "PDU.kicad_pcb")], check=True, capture_output=True)
    print(json.dumps({k: res[k] for k in ("empty_errors", "placed_errors_not_allowed", "schematic_parity_issues", "pass")} | {"neck_violations": len(neck)}))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
