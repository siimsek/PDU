#!/usr/bin/env python3
"""T-028 group 2: 20 capacitor references against the official TDK part pages. Design files are read only.

Inputs: T-027 ledgers, design/bom-v2.csv, group2-board-pads.json (from dump_group2_pads.py) and the TDK values typed below.
TDK pages were read with a browser on 2026-11-09. The land figure on the page defines PA = gap, PB = pad length, PC = pad width.
Run from the repo root: python reports/g5/T-028/gen_group2.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-028"
URL = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no="
# MPN: C F, tolerance %, V, dielectric, EIA, L, W, T, land reflow PA, PB, PC, soldering, DF or Q, IR Mohm, automotive pointer on the page
TDK = {
    "C1608X7R2A103K080AA": (10e-9, 10, 100, "X7R", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "DF≤3%", 10000, "CGA3E2X7R2A103K080AA"),
    "C1608X7R1H473K080AA": (47e-9, 10, 50, "X7R", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "DF≤3%", 10000, "CGA3E2X7R1H473K080AA"),
    "C1608C0G1H103J080AA": (10e-9, 5, 50, "C0G", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "Q≥1000", 10000, "CGA3E2C0G1H103J080AA"),
    "C1608C0G1H102J080AA": (1e-9, 5, 50, "C0G", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "Q≥1000", 10000, "CGA3E2C0G1H102J080AA"),
    "C1608X7R1H104K080AA": (100e-9, 10, 50, "X7R", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "DF≤3%", 5000, "CGA3E2X7R1H104K080AA"),
    "C3216X7R1E106K160AB": (10e-6, 10, 25, "X7R", "1206", "3.20±0.20", "1.60±0.20", "1.60±0.20", (2.0, 2.4), (1.0, 1.2), (1.1, 1.6), "Wave+Reflow", "DF≤7.5%", 50, "CGA5L1X7R1E106K160AC"),
    "C1608C0G1H220J080AA": (22e-12, 5, 50, "C0G", "0603", "1.60±0.10", "0.80±0.10", "0.80±0.10", (0.6, 0.8), (0.6, 0.8), (0.6, 0.8), "Wave+Reflow", "Q≥840", 10000, "CGA3E2C0G1H220J080AA"),
    "C3225X7S2A475K200AB": (4.7e-6, 10, 100, "X7S", "1210", "3.20±0.40", "2.50±0.30", "2.00±0.20", (2.0, 2.4), (1.0, 1.2), (1.9, 2.5), "Reflow", "DF≤5%", 106, "CGA6M3X7S2A475K200AB"),
}
UNIT = {"p": 1e-12, "n": 1e-9, "u": 1e-6}


def farad(v):
    m = re.fullmatch(r"([0-9.]+)([pnu])", v)
    return float(m.group(1)) * UNIT[m.group(2)]


def main():
    plan = json.loads((OUT / "coverage-plan.json").read_text(encoding="utf-8"))
    group = plan["groups"]["G2"]
    refs = {r["ref"]: r for r in csv.DictReader((ROOT / "reports/g5/T-027/ledger-references.csv").open(encoding="utf-8"))}
    pins = list(csv.DictReader((ROOT / "reports/g5/T-027/ledger-pins.csv").open(encoding="utf-8")))
    bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
    pads = json.loads((OUT / "group2-board-pads.json").read_text(encoding="utf-8"))["refs"]
    out_p, out_r = [], []
    for ref in group:
        b, t = bom[ref], TDK[bom[ref]["mpn"]]
        rows = sorted((p for p in pins if p["ref"] == ref), key=lambda x: int(x["pin"]))
        assert [p["pin"] for p in rows] == ["1", "2"], ref
        pp = pads[ref]
        assert sorted(pp) == ["1", "2"], ref
        for p in rows:
            good = p["state"] == "EŞLEŞTİ" and p["net"] != "" and p["nc"] == ""
            out_p.append({"ref": ref, "pin": p["pin"], "schematic_name": p["name"], "manufacturer_function": "kutupsuz MLCC terminali", "net": p["net"], "t027_pcb_state": p["state"], "board_pad_mm": f"{pp[p['pin']]['w']}x{pp[p['pin']]['h']}", "doc": URL + b["mpn"], "status": "PASS" if good else "FAIL", "note": "Üretici belgesi pin numarası tanımlamaz; 1/2 yer değiştirebilir."})
        span = round(abs(pp["2"]["x"] - pp["1"]["x"]), 3)
        pb, pc = pp["1"]["w"], pp["1"]["h"]
        gap = round(span - pb, 3)
        lands = (("PA boşluk", gap, t[8]), ("PB uzunluk", pb, t[9]), ("PC genişlik", pc, t[10]))
        diff = [f"{n} {v} mm [{r[0]}–{r[1]}], {'+' if v > r[1] else ''}{round(v - r[1] if v > r[1] else v - r[0], 3)} mm" for n, v, r in lands if not r[0] <= v <= r[1]]
        checks = {"value": abs(farad(b["value"]) - t[0]) < t[0] * 1e-6, "voltage": float(b["v_rating"]) == t[2], "dielectric": b["tcr"] == t[3], "package": b["package"] == t[4], "ledger_value": refs[ref]["value"] == b["value"], "ledger_mpn": refs[ref]["mpn"] in ("", b["mpn"]), "ledger_footprint": refs[ref]["footprint"] == b["footprint"], "dnp_false": b["dnp"] == "False"}
        bad = [k for k, v in checks.items() if not v]
        applied = float(b["v_applied"]) / t[2]
        status = "FAIL" if bad or any(r["status"] == "FAIL" and r["ref"] == ref for r in out_p) else ("AÇIK" if diff else "PASS")
        out_r.append({"ref": ref, "bom_mpn": b["mpn"], "manufacturer": "TDK", "tdk_status": "Production", "doc": URL + b["mpn"], "doc_rev": "ürün sayfası, sürüm numarası yok; okuma 2026-11-09", "bom_value": b["value"], "tdk_value_F": t[0], "tdk_tolerance_pct": t[1], "bom_tolerance": b["tolerance"], "tdk_voltage_V": t[2], "v_applied_V": b["v_applied"], "applied_ratio": round(applied, 4), "dielectric": t[3], "package": t[4], "L_mm": t[5], "W_mm": t[6], "T_mm": t[7], "footprint": b["footprint"], "land_reflow_PA_PB_PC_mm": f"{t[8][0]}–{t[8][1]} / {t[9][0]}–{t[9][1]} / {t[10][0]}–{t[10][1]}", "board_PA_PB_PC_mm": f"{gap} / {pb} / {pc}", "land_status": "PASS" if not diff else "AÇIK", "land_note": "; ".join(diff) or "Üç ölçü aralıkta", "soldering": t[11], "df_or_q": t[12], "ir_min_Mohm": t[13], "aec_q200": "NO", "tdk_automotive_pointer": t[14], "failed_checks": ",".join(bad), "reference_status": status})
    for name, rows in (("group2-pins.csv", out_p), ("group2-refs.csv", out_r)):
        with (OUT / name).open("w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    count = lambda rows, k: {s: sum(1 for r in rows if r[k] == s) for s in sorted({r[k] for r in rows})}
    print(json.dumps({"refs": len(out_r), "pins": len(out_p), "pin_status": count(out_p, "status"), "ref_status": count(out_r, "reference_status"), "land": count(out_r, "land_status"), "by_land": sorted({(r["package"], r["board_PA_PB_PC_mm"], r["land_note"]) for r in out_r})}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
