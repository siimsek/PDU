#!/usr/bin/env python3
"""T-032 group 2: schematic <-> SPICE map of the 20 G2 capacitor references. Deck and schematic are read only.
A lumped element is mapped per reference and its value is recomputed from the formula in analysis/g2/sim_runner.py.
Run from the repo root: python reports/g5/T-032/gen_group2.py"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-032"
AVG = "Büyük işaret ortalama model; anahtarlama, ripple ve parazitikler yok"
NO = "Deck'te karşılık yok: "
CIN = (["CIN", "RCIN"], {"1": "vin", "2": "n_cin"}, "Giriş toplu kapasitesi", "EŞLEŞTİ", "CIN_EFF 8 parça için toplu; 8×4,7 µF×0,5, Ceff oranı VARSAYIM; 2. uç RCIN 5 mΩ üzerinden GND'ye")
EF = (["CEFIN"], {"1": "vsafe", "2": "0"}, "eFuse giriş dekuplajı", "EŞLEŞTİ", "CEFIN_EFF 2 parça için toplu; 2×100 nF×0,5, Ceff oranı VARSAYIM")
MAP = {
    **{f"CBIN{i}": ([], {}, "VIN HF dekuplaj", "AÇIK", NO + "CIN_EFF yalnız 8 adet CIN içerir; 10 nF ihmal edilmiş") for i in (1, 2)},
    **{f"CBOOT{i}": ([], {}, "Bootstrap", "AÇIK", NO + "ortalama anahtarda CBOOT ve SW4 yok") for i in (1, 2)},
    **{f"CDVDT{i}": ([], {}, "eFuse çıkış rampası", "AÇIK", NO + "BEF1/BEF2 dVdt rampası içermez") for i in (1, 2)},
    "CEFIN1": EF, "CEFIN2": EF,
    "CEFOUT1": (["CPO1"], {"1": "o1", "2": "0"}, "O1 çıkış kapasitesi", "EŞLEŞTİ", "CPORT_O1 = 10 µF×0,4; Ceff oranı VARSAYIM"),
    "CEFOUT2": (["CPS2"], {"1": "s2e", "2": "0"}, "S2E çıkış kapasitesi", "EŞLEŞTİ", "CPORT_S2E = 10 µF×0,4; Ceff oranı VARSAYIM"),
    **{f"CIN{i}": CIN for i in range(1, 9)},
    "CIN_U5": ([], {}, "LM74700 ANODE dekuplaj", "AÇIK", NO + "anode düğümünde kapasitör yok; 22 nF ihmal edilmiş"),
    "COUT1": (["COUT", "RESR", "LESL"], {"1": "vraw", "2": "ncout"}, "Çıkış toplu kapasitesi", "EŞLEŞTİ", "COUT_EFF = 32×20,622 µF tipik, köşeler sim_runner c_corner; 2. uç ESR/ESL üzerinden GND'ye; COUT2–32 G3+ grubunda"),
}


def main():
    cov = json.loads((OUT / "coverage.json").read_text(encoding="utf-8"))
    assert sorted(MAP) == sorted(cov["groups"]["G2"])
    deck = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8").splitlines()
    params = {m.group(1): float(m.group(2)) for m in re.finditer(r"^\.param (\w+)=([-+0-9.eE]+)\s*$", (ROOT / "design/pdu_v2_params.inc").read_text(encoding="utf-8"), re.M)}
    expect = {"CIN_EFF": 8 * 4.7e-6 * 0.5, "CEFIN_EFF": 2 * 100e-9 * 0.5, "CPORT_O1": 10e-6 * 0.4, "CPORT_S2E": 10e-6 * 0.4, "COUT_EFF": 32 * 20.622e-6}
    value_check = {k: {"inc": params[k], "formula": v, "equal": abs(params[k] - v) <= abs(v) * 1e-9} for k, v in expect.items()}
    assert all(v["equal"] for v in value_check.values()), value_check
    refs = {r["ref"]: r for r in csv.DictReader((ROOT / "reports/g5/T-027/ledger-references.csv").open(encoding="utf-8"))}
    pins = list(csv.DictReader((ROOT / "reports/g5/T-027/ledger-pins.csv").open(encoding="utf-8")))
    rows = []
    for ref, (el, nodes, purpose, status, why) in MAP.items():
        where = {e: next(i + 1 for i, t in enumerate(deck) if t.split()[:1] == [e]) for e in el}
        for p in sorted((p for p in pins if p["ref"] == ref), key=lambda x: int(x["pin"])):
            node = nodes.get(p["pin"], "(yok)")
            rows.append({"ref": ref, "value": refs[ref]["value"], "pin": p["pin"], "schematic_net": p["net"], "spice_elements": " ".join(el), "spice_lines": " ".join(f"{k}:{v}" for k, v in where.items()), "spice_node": node, "purpose": purpose, "ref_status": status, "pin_status": "AÇIK" if node == "(yok)" else "EŞLEŞTİ", "reason": why, "model_suitability": AVG})
    with (OUT / "group2-map.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    status = {s: sorted(k for k, v in MAP.items() if v[3] == s) for s in sorted({v[3] for v in MAP.values()})}
    rest = {k: v for k, v in cov["groups"].items() if k != "G2"}
    res = {"group": "G2", "refs": len(MAP), "pins": len(rows), "ref_status": {k: len(v) for k, v in status.items()}, "refs_by_status": status, "pin_status": {s: sum(1 for r in rows if r["pin_status"] == s) for s in sorted({r["pin_status"] for r in rows})}, "lumped_value_check": value_check, "remaining_groups": list(rest), "remaining_refs_ACIK": sum(len(v) for v in rest.values())}
    (OUT / "group2-coverage.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("refs", "pins", "ref_status", "pin_status", "remaining_groups", "remaining_refs_ACIK")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
