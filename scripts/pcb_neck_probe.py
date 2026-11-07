"""R-012 #2 evidence: does the neck-down rule + audit behave as intended on real tracks? (KiCad Python)

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" scripts/pcb_neck_probe.py   # -> reports/g5/T-013/neck-probe.json

Builds a temp copy of PDU.kicad_pcb (PDU.kicad_pcb itself is not modified) with four /VIN test tracks on F.Cu at
U1 pad 1 and runs kicad-cli DRC + scripts/pcb_drc.neck_audit on it:
  A  0.30 mm x 1.0 mm from the pad, inside the U1 courtyard          -> DRC ok,             audit ok
  B  0.30 mm x 3.0 mm from the pad, leaves the courtyard            -> DRC ok (KiCad applies the courtyard rule
                                                                        to the whole track), audit length -> FAIL
  C  0.30 mm x 1.0 mm in free board area (no fine-pitch footprint)  -> DRC track_width,    audit not pad-ended
  D  3.30 mm x 5.0 mm in free board area (class width)              -> DRC ok,             audit ignores
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew as P

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pcb_drc  # noqa: E402
import pcb_rules as pr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g5" / "T-013" / "neck-probe.json"
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        for f in ("PDU.kicad_pcb", "PDU.kicad_pro", "PDU.kicad_dru"):
            shutil.copy(ROOT / f, t / f)
        b = P.LoadBoard(str(t / "PDU.kicad_pcb"))
        u1 = b.FindFootprintByReference("U1")
        pad = next(p for p in u1.Pads() if p.GetNumber() == "1")
        net = pad.GetNet()
        x, y = P.ToMM(pad.GetPosition().x), P.ToMM(pad.GetPosition().y)
        # U1 is at 180 deg: pad 1 sits on its east edge (KiCad +x points out of the package there)
        free = (30 + 60.0, 30 + 85 - 27.8)        # D-006 (60, 27.8): between the COUT bank and the test-pad region
        tracks = {"A": ((x, y), (x + 1.0, y), 0.30), "B": ((x, y), (x + 3.0, y), 0.30),
                  "C": (free, (free[0] + 1.0, free[1]), 0.30),
                  "D": ((free[0] + 10.0, free[1]), (free[0] + 15.0, free[1]), 3.30)}
        made = {}
        for k, (a, e, w) in tracks.items():
            tr = P.PCB_TRACK(b)
            tr.SetStart(P.VECTOR2I(P.FromMM(a[0]), P.FromMM(a[1])))
            tr.SetEnd(P.VECTOR2I(P.FromMM(e[0]), P.FromMM(e[1])))
            tr.SetWidth(P.FromMM(w))
            tr.SetLayer(P.F_Cu)
            tr.SetNet(net)
            b.Add(tr)
            made[k] = {"start": a, "end": e, "width": w}
        P.SaveBoard(str(t / "PDU.kicad_pcb"), b, True)
        subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-error", "-o", str(t / "drc.json"),
                        str(t / "PDU.kicad_pcb")], check=True, capture_output=True)
        drc = json.loads((t / "drc.json").read_text(encoding="utf-8"))
        widths = [v for v in drc["violations"] if v["type"] == "track_width"]
        text = (t / "PDU.kicad_pcb").read_text(encoding="utf-8")
        audit = pcb_drc.neck_audit(text, pr.routing_rows())

    def near(pt, q):
        return abs(pt[0] - q[0]) < 1e-3 and abs(pt[1] - q[1]) < 1e-3

    res = {"net": net.GetNetname(), "tracks": made, "drc_track_width": {}, "audit": {}}
    for k, m in made.items():
        # DRC items carry the track position; match by start point text in the item description is fragile, so
        # match by the reported item position (mm).
        res["drc_track_width"][k] = any(
            any(near((i["pos"]["x"], i["pos"]["y"]), m["start"]) or near((i["pos"]["x"], i["pos"]["y"]), m["end"])
                or (min(m["start"][0], m["end"][0]) - 1e-3 <= i["pos"]["x"] <= max(m["start"][0], m["end"][0]) + 1e-3
                    and abs(i["pos"]["y"] - m["start"][1]) < 1e-3)
                for i in v["items"]) for v in widths)
        res["audit"][k] = next((a["why"] for a in audit if near(a["start"], m["start"]) and near(a["end"], m["end"])), [])
    res["expected"] = {"A": [False, []], "B": [False, ["length"]], "C": [True, ["not ended"]], "D": [False, []]}
    ok = (not res["drc_track_width"]["A"] and res["drc_track_width"]["C"]
          and not res["drc_track_width"]["D"] and res["audit"]["A"] == [] and res["audit"]["D"] == []
          and any("length" in w for w in res["audit"]["B"]) and any("not ended" in w for w in res["audit"]["C"]))
    res["pass"] = ok
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps({"drc_track_width": res["drc_track_width"], "audit": res["audit"], "pass": ok}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
