"""T-003 floorplan area budget: courtyard area of every BOM footprint vs board outline options.

    python scripts/floorplan.py      # writes reports/g5/floorplan.json, prints summary

Courtyard = bounding box of F.CrtYd/B.CrtYd graphics in the footprint file (conservative for non-rectangular yards).
Fallback when no courtyard: bounding box of pads/fab + 0.25 mm (VARSAYIM, flagged). Parts without a footprint (F1)
use an explicit VARSAYIM area. Fill = sum(courtyard) / board area (one side); routing/via/keep-out space is not
included, so fill is a lower bound on real density.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STOCK = Path(os.environ.get("KICAD_FP_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\footprints"))
CUSTOM = ROOT / "hardware" / "lib" / "PDU.pretty"
OUT = ROOT / "reports" / "g5" / "floorplan.json"
FILL_LIMIT = 0.55  # T-003 card: above this (one side, current outline) -> user decision on board size

# Parts without a footprint yet (VARSAYIM, replaced when the part is selected).
NO_FP_AREA = {"F1": (25.0, 10.0, "VARSAYIM: 5x20 mm fuse-clip/holder class footprint until D-001/T-004 select F1")}

BOARDS = {"current 101.6 x 76.2": (101.6, 76.2), "PCB-HANDOFF estimate 120 x 85": (120.0, 85.0),
          "130 x 90": (130.0, 90.0), "140 x 100": (140.0, 100.0)}

GROUPS = [  # PCB-HANDOFF §3 groups; first match wins
    ("Giriş (J1, F1, TVS, ters kutup, CIN)", r"^(J1|F1|D1|U5|Q1|CIN.*|CBIN\d|CVCAP)$"),
    ("Buck faz 1", r"^(U1|L1|RS1|CBOOT1|RBOOT1|RT1|CVCC1|CVDDA1)$"),
    ("Buck faz 2", r"^(U2|L2|RS2|CBOOT2|RBOOT2|RT2|CVCC2|CVDDA2)$"),
    ("Buck ortak kontrol (FB/COMP/UV/CFG)", r"^(RCFG\d|RSYNC|RFB\d|R_INJ|R_TRIM|RCOMP|CCOMP|CHF|RUV\d)$"),
    ("COUT bankası (32× C5750)", r"^(COUT\d+|RRAWBL)$"),
    ("Ortak bara ayırıcı", r"^(U6|Q2|R_GS|C_ISO_.*)$"),
    ("OVP + OC mantık, REF, mandal, LDO", r"^(R_OV.*|U7|U8|U9|U10|U1[1-5]|C_INA\d|C_OCC\d|C_AND|R_OC[TB]|C_CMP|C_REF_.*|C_LAT|R_CLR|C_CLR|SW1|R_Q|R_EN\d|C_LDO_.*|R_BL5|R_BLS)$"),
    ("eFuse + çıkış konnektörleri", r"^(U3|U4|RILIM\d|RIMON\d|CDVDT\d|CEFIN\d|CEFOUT\d|RPG\d.*|D_REV\d|D2|D3|REN\d|J2|J3)$"),
]


def _xy(node: ks.SList):
    a = node.atoms()
    try:
        return float(a[1].value), float(a[2].value)
    except (IndexError, ValueError):
        return None


def footprint_file(fp: str) -> Path | None:
    lib, name = fp.split(":", 1)
    p = (CUSTOM if lib == "PDU" else STOCK / f"{lib}.pretty") / f"{name}.kicad_mod"
    return p if p.exists() else None


def bbox(path: Path, layers=("F.CrtYd", "B.CrtYd")):
    root = ks.parse(path.read_text(encoding="utf-8"))
    pts = []
    for node in ks.walk(root):
        if node.head in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc"):
            lay = next((c.atoms()[1].value for c in node.children("layer") if len(c.atoms()) > 1), "")
            if lay not in layers:
                continue
            for sub in ks.walk(node):
                if sub.head in ("start", "end", "xy", "mid", "center"):
                    p = _xy(sub)
                    if p:
                        pts.append(p)
            if node.head == "fp_circle":  # radius from center/end
                c = next((_xy(s) for s in node.children("center")), None)
                e = next((_xy(s) for s in node.children("end")), None)
                if c and e:
                    r = ((c[0] - e[0]) ** 2 + (c[1] - e[1]) ** 2) ** 0.5
                    pts += [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) - min(xs), max(ys) - min(ys)


def fallback_bbox(path: Path):
    b = bbox(path, ("F.Fab", "B.Fab", "F.SilkS", "B.SilkS"))
    return (b[0] + 0.5, b[1] + 0.5) if b else None


def compute():
    rows = []
    with (ROOT / "design" / "footprint-map.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ref, fp = r["ref"], r["footprint"]
            entry = {"ref": ref, "footprint": fp, "source": "", "w_mm": None, "h_mm": None, "area_mm2": None, "flag": ""}
            if ref in NO_FP_AREA:
                w, h, why = NO_FP_AREA[ref]
                entry.update(w_mm=w, h_mm=h, area_mm2=w * h, flag=why, source="—")
            else:
                p = footprint_file(fp) if fp else None
                b = bbox(p) if p else None
                if p and b is None:
                    b = fallback_bbox(p)
                    entry["flag"] = "VARSAYIM: no courtyard; fab/silk bbox + 0.25 mm"
                if b is None:
                    entry["flag"] = "footprint file not found"
                else:
                    entry.update(w_mm=round(b[0], 3), h_mm=round(b[1], 3), area_mm2=round(b[0] * b[1], 3),
                                 source=p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else f"<KiCad stock>/{p.parent.name}/{p.name}")
            entry["group"] = next((g for g, rx in GROUPS if re.match(rx, ref)), "diğer")
            rows.append(entry)
    total = sum(r["area_mm2"] or 0 for r in rows)
    groups = {}
    for r in rows:
        g = groups.setdefault(r["group"], {"parts": 0, "area_mm2": 0.0})
        g["parts"] += 1
        g["area_mm2"] = round(g["area_mm2"] + (r["area_mm2"] or 0), 2)
    boards = {k: {"w_mm": w, "h_mm": h, "area_mm2": round(w * h, 1), "fill_one_side": round(total / (w * h), 4),
                  "fill_two_side": round(total / (2 * w * h), 4)} for k, (w, h) in BOARDS.items()}
    min_area_for_limit = total / FILL_LIMIT
    return {"classification": "HESAP (courtyard bbox from footprint files) + VARSAYIM (flagged rows)",
            "fill_limit_one_side": FILL_LIMIT, "parts": len(rows), "total_courtyard_mm2": round(total, 1),
            "missing": [r["ref"] for r in rows if r["area_mm2"] is None],
            "flagged": {r["ref"]: r["flag"] for r in rows if r["flag"]},
            "min_board_area_for_limit_mm2": round(min_area_for_limit, 1),
            "groups": groups, "boards": boards, "rows": rows}


def main() -> int:
    res = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    cur = res["boards"]["current 101.6 x 76.2"]
    print(json.dumps({"parts": res["parts"], "total_mm2": res["total_courtyard_mm2"], "missing": res["missing"],
                      "fill_current_one_side": cur["fill_one_side"], "over_limit": cur["fill_one_side"] > FILL_LIMIT}))
    return 0 if not res["missing"] else 1


if __name__ == "__main__":
    sys.exit(main())
