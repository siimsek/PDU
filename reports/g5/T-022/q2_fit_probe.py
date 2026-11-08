"""T-022 / D-010 physical-fit probe. Never writes PDU.kicad_pcb: every case is a temporary copy.

    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" reports/g5/T-022/q2_fit_probe.py

Runs KiCad 10.0.7 DRC (--severity-all --refill-zones --schematic-parity) on each case and writes q2-fit-probe.json.
Coordinates are D-006 (origin lower-left, y up). These are fit tests of single items, not a finished route:
`unconnected_items` are expected and are not counted. Lengths are centre-line, pad centre to pad centre.
"""
from __future__ import annotations

import collections
import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pcbnew as P

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
OX, OY, H = 30.0, 30.0, 85.0
GATE_W = 0.4     # PCB-HANDOFF §2 GATE; project class AUX_LOCAL
VIA_D, VIA_DRILL = 0.6, 0.3
LAYERS = {"F": P.F_Cu, "B": P.B_Cu}
U6_6 = (93.733, 47.49)


def kp(x, y):
    return P.VECTOR2I(P.FromMM(OX + x), P.FromMM(OY + H - y))


def d6(v):
    return P.ToMM(v.x) - OX, OY + H - P.ToMM(v.y)


def rotate_q2_with_vias(b, deg):
    """Rotate Q2 about its anchor and carry its T-021 via-in-pad array with it (positions only; nothing is removed)."""
    f = next(x for x in b.GetFootprints() if x.GetReference() == "Q2")
    cx, cy = d6(f.GetPosition())
    boxes = [p.GetBoundingBox() for p in f.Pads() if p.GetNumber() in ("1", "2", "3", "5")]
    a = math.radians(deg)
    moved = 0
    for t in b.GetTracks():
        if t.Type() == P.PCB_VIA_T and any(x.Contains(t.GetPosition()) for x in boxes):
            x, y = d6(t.GetPosition())
            dx, dy = x - cx, y - cy
            t.SetPosition(kp(cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
            moved += 1
    f.SetOrientationDegrees(deg)
    return f, moved


def add_track(b, pts, w, net, lay):
    for a, c in zip(pts, pts[1:]):
        t = P.PCB_TRACK(b)
        t.SetStart(kp(*a))
        t.SetEnd(kp(*c))
        t.SetWidth(P.FromMM(w))
        t.SetLayer(LAYERS[lay])
        t.SetNet(b.GetNetInfo().GetNetItem(net))
        b.Add(t)
    return sum(math.dist(a, c) for a, c in zip(pts, pts[1:]))


def add_via(b, x, y, net):
    v = P.PCB_VIA(b)
    v.SetPosition(kp(x, y))
    v.SetViaType(P.VIATYPE_THROUGH)
    v.SetLayerPair(P.F_Cu, P.B_Cu)
    v.SetDrill(P.FromMM(VIA_DRILL))
    v.SetWidth(P.F_Cu, P.FromMM(VIA_D))
    v.SetNet(b.GetNetInfo().GetNetItem(net))
    b.Add(v)


# Candidate geometry for rotation 90: pads read back from KiCad in this run; 90 deg puts sources south, gate SE, drain north.
DRAIN_90 = (93.995, 54.53)
EXTRA_DRAIN_90 = [(DRAIN_90[0] + i, DRAIN_90[1] + j) for i, j in ((-.6, -.6), (.6, -.6), (-.6, .6), (.6, .6), (-1.8, -.6), (1.8, -.6), (-1.8, .6), (1.8, .6))]
SOURCE_VIAS_90 = [(x, y) for x in (91.8, 92.55, 93.3, 94.05, 94.8) for y in (49.95, 50.7)] + [(91.05, 49.95), (91.05, 50.7)]

CASES = {
    "baseline_rot0": {"rot": 0, "tracks": []},
    "gate_rot180_east_as_short_as_clearance_allows_only_to_pads": {
        "rot": 180, "tracks": [("/ISO_GATE", GATE_W, "F", [U6_6, (94.8, 47.49), (97.55, 51.55), (97.55, 55.72), (96.747, 56.11)])]},
    "gate_rot180_east_clear_of_source_vias": {
        "rot": 180, "tracks": [("/ISO_GATE", GATE_W, "F", [U6_6, (94.8, 47.49), (97.9, 51.55), (97.9, 55.72), (96.747, 56.11)])]},
    "gate_rot90": {"rot": 90, "tracks": [("/ISO_GATE", GATE_W, "F", [U6_6, (94.8, 47.49), (95.9, 48.65), (95.9, 51.453)])]},
    "south_stripe_D010_7p0_y25_32": {"rot": 180, "tracks": [("/VOUT", 7.0, "F", [(96.0, 28.5), (60.0, 28.5)])]},
    "south_stripe_5p5_y26p5_32": {"rot": 180, "tracks": [("/VOUT", 5.5, "F", [(96.0, 29.25), (60.0, 29.25)])]},
    "rot90_candidate_buses": {
        "rot": 90,
        "tracks": [("/ISO_GATE", GATE_W, "F", [U6_6, (94.8, 47.49), (95.9, 48.65), (95.9, 51.453)]),
                   ("/VOUT", 7.0, "B", [(92.5, 55.5), (84.5, 55.5), (84.5, 44.2), (57.0, 44.2)]),
                   ("/VSAFE", 5.5, "B", [(92.0, 49.0), (98.5, 49.0), (98.5, 41.5), (108.0, 41.5)])],
        "vias": [(x, y, "/VOUT") for x, y in EXTRA_DRAIN_90] + [(x, y, "/VSAFE") for x, y in SOURCE_VIAS_90]},
}


def run(name, case, tmp):
    b = P.LoadBoard(str(ROOT / "PDU.kicad_pcb"))
    f, moved = rotate_q2_with_vias(b, case["rot"]) if case["rot"] else (next(x for x in b.GetFootprints() if x.GetReference() == "Q2"), 0)
    pads = {p.GetNumber(): [round(v, 3) for v in d6(p.GetPosition())] for p in f.Pads() if p.GetNumber() in ("1", "2", "3", "4")}
    lengths = {}
    for net, w, lay, pts in case["tracks"]:
        lengths[f"{net}@{w}mm/{lay}"] = round(add_track(b, pts, w, net, lay), 3)
    for x, y, net in case.get("vias", []):
        add_via(b, x, y, net)
    p = tmp / name
    p.mkdir()
    for fn in ("PDU.kicad_pro", "PDU.kicad_dru"):
        shutil.copy(ROOT / fn, p / fn)
    P.SaveBoard(str(p / "PDU.kicad_pcb"), b, True)
    out = p / "drc.json"
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "--refill-zones", "--schematic-parity", "-o", str(out), str(p / "PDU.kicad_pcb")],
                   check=True, capture_output=True)
    data = json.loads(out.read_text(encoding="utf-8"))
    return {"rotation_deg": case["rot"], "vias_carried_with_q2": moved, "q2_pads_d006": pads, "added_vias": len(case.get("vias", [])),
            "centre_line_length_mm": lengths,
            "violations_by_type": dict(collections.Counter(f"{v['severity']}:{v['type']}" for v in data["violations"])),
            "errors": [{"type": v["type"], "items": [i["description"] for i in v["items"]]} for v in data["violations"] if v["severity"] == "error"],
            "schematic_parity_issues": len(data.get("schematic_parity", []))}


def main():
    if P.GetBuildVersion().split("-")[0] != "10.0.7":
        raise SystemExit("KiCad 10.0.7 required (D-009): " + P.GetBuildVersion())
    res = {"kicad": P.GetBuildVersion(), "note": "Fit probe on temporary copies. Not a finished route; unconnected_items are expected and not counted.", "cases": {}}
    with tempfile.TemporaryDirectory() as td:
        for name, case in CASES.items():
            res["cases"][name] = run(name, case, Path(td))
    with (OUT / "q2-fit-probe.json").open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    for k, v in res["cases"].items():
        print(k, v["centre_line_length_mm"], "errors", len(v["errors"]), "parity", v["schematic_parity_issues"], v["violations_by_type"])
        for e in v["errors"]:
            print("    ", e["type"], e["items"])


if __name__ == "__main__":
    main()
