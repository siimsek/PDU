#!/usr/bin/env python3
"""T-032 group 1: schematic reference <-> SPICE element map for 20 references.

Inputs: reports/g5/T-027/ledger-*.csv, design/pdu_v2.cir, design/pdu_v2_params.inc, reports/g2/sim-results.json. Writes group1-map.csv, coverage.json.
Name equality is not treated as model validation: suitability is a separate column. Run from the repo root: python reports/g5/T-032/gen_map.py
"""
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-032"
AVG = "Büyük işaret ortalama model; anahtarlama, ripple ve parazitikler yok"
# ref: (deck element prefixes, {schematic pin: deck node}, purpose, status, reason)
MAP = {
    "D1": (["DTVS"], {"1": "vin", "2": "0"}, "Giriş TVS kelepçesi", "EŞLEŞTİ", "DTVSM BV/RS parametreli diyot; üretici modeli değil"),
    "Q1": (["BQ1"], {"1": "anode", "2": "anode", "3": "anode", "4": "(yok)", "5": "vin"}, "Ters polarite FET'i", "AÇIK", "BQ1 ideal diyot davranışı; gate ve FET modeli yok, pin 4 düğümü yok"),
    "U5": ([], {}, "İdeal diyot denetleyici", "AÇIK", "Ayrı eleman yok; işlev BQ1 içinde varsayılıyor; VCAP şarj pompası ve EN modellenmemiş"),
    "RS1": (["RS1"], {"1": "l1c", "2": "vraw"}, "Faz 1 akım algı", "EŞLEŞTİ", "Değer RS=7,5 mΩ, schematic ile eşit"),
    "RS2": (["RS2"], {"1": "l2c", "2": "vraw"}, "Faz 2 akım algı", "EŞLEŞTİ", "Değer RS=7,5 mΩ, schematic ile eşit"),
    "L1": (["B1L", "BIL1", "CIL1", "RL1"], {"1": "l1a", "2": "l1c"}, "Faz 1 endüktans", "EŞLEŞTİ", "LPH=6,8 µH, doygunluk eğrisi pwl; RDCR ayrı; IHLP üretici modeli değil"),
    "L2": (["B2L", "BIL2", "CIL2", "RL2"], {"1": "l2a", "2": "l2c"}, "Faz 2 endüktans", "EŞLEŞTİ", "LPH=6,8 µH; L1 ile aynı model yapısı"),
    "U1": (["BSW1", "VM1", "BIN1"], {"11": "l1c", "12": "vraw", "16": "fb", "15": "comp", "9": "ven"}, "Faz 1 regülatör", "AÇIK", "Yalnız ortalama anahtar ve tepe akım kuralı; VCC, VDDA, BIAS, CBOOT, SW4, RT, CONFIG yok"),
    "U2": (["BSW2", "VM2", "BIN2"], {"11": "l2c", "12": "vraw"}, "Faz 2 regülatör", "AÇIK", "U1 ile aynı sınır; FB/COMP U1 tarafında ortak"),
    "RFB1": (["RFB1"], {"1": "vraw", "2": "fb"}, "FB üst", "EŞLEŞTİ", "130 kΩ eşit; şema pin 1 /FB_INJ, R_INJ deck'te yok (vraw ile aynı varsayılıyor)"),
    "RFB2": (["RFB2"], {"1": "fb", "2": "(yok)"}, "FB alt", "EŞLEŞTİ", "SPICE 10,2 kΩ = şema RFB2 9,76 kΩ + R_TRIM 442 Ω (10,202 kΩ; 2 Ω fark)"),
    "R_TRIM": (["RFB2"], {"1": "(yok)", "2": "0"}, "FB alt seri", "EŞLEŞTİ", "RFB2 elemanı içinde toplu; ayrı düğüm yok"),
    "RCOMP": (["RCOMP"], {"1": "comp", "2": "cmid"}, "Kompanzasyon", "EŞLEŞTİ", "33,2 kΩ eşit"),
    "CCOMP": (["CCOMP"], {"1": "cmid", "2": "0"}, "Kompanzasyon", "EŞLEŞTİ", "10 nF eşit"),
    "CHF": (["CHF"], {"1": "comp", "2": "0"}, "HF kutbu", "EŞLEŞTİ", "22 pF eşit"),
    "Q2": (["SISO", "DBODY"], {"1": "vsafe", "2": "vsafe", "3": "vsafe", "4": "ctl", "5": "nisod"}, "Ortak bara ayırıcı", "AÇIK", "Anahtar + gövde diyotu; Ron parametreli, Qg/SOA/gate zamanlaması TDLY ile soyut"),
    "U6": (["BCTL", "CCTL", "RCTL"], {"7": "(ovreq)", "6": "ctl"}, "Ayırıcı denetleyici", "AÇIK", "Davranışsal gecikme; VCAP, EN/UVLO, SRC, VS modellenmemiş"),
    "RUV1": (["BVEN"], {"1": "vin", "2": "ven"}, "EN/UVLO üst", "EŞLEŞTİ", "Fiziksel direnç yok; BVEN ifadesinde 174 kΩ"),
    "RUV2": (["BVEN"], {"1": "ven", "2": "0"}, "EN/UVLO alt", "EŞLEŞTİ", "Fiziksel direnç yok; BVEN ifadesinde 10 kΩ"),
    "U3": (["BEF1", "DREV1", "BEFS"], {"16": "vsafe", "17": "o1"}, "O1 eFuse", "AÇIK", "Akım sınırı/UVLO/OVLO; dVdt rampası, ITIMER, IMON, PG, LDSTRT yok"),
}


def main():
    deck = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8").splitlines()
    params = {m.group(1): m.group(2) for m in re.finditer(r"^\.param (\w+)=(\S+)", (ROOT / "design/pdu_v2_params.inc").read_text(encoding="utf-8"), re.M)}
    refs = {r["ref"]: r for r in csv.DictReader((ROOT / "reports/g5/T-027/ledger-references.csv").open(encoding="utf-8"))}
    pins = list(csv.DictReader((ROOT / "reports/g5/T-027/ledger-pins.csv").open(encoding="utf-8")))
    rows = []
    for ref, (el, nodes, purpose, status, why) in MAP.items():
        lines = {}
        for e in el:
            ln = [i + 1 for i, t in enumerate(deck) if t.split()[:1] == [e]]
            assert ln, (ref, e)
            lines[e] = ln[0]
        for p in sorted((p for p in pins if p["ref"] == ref), key=lambda x: int(x["pin"])):
            node = nodes.get(p["pin"], "(yok)")
            rows.append({"ref": ref, "value": refs[ref]["value"], "pin": p["pin"], "schematic_net": p["net"], "spice_elements": " ".join(el), "spice_lines": " ".join(f"{k}:{v}" for k, v in lines.items()), "spice_node": node, "purpose": purpose, "ref_status": status, "pin_status": "EŞLEŞTİ" if node != "(yok)" and not node.startswith("(") else "AÇIK", "reason": why, "model_suitability": AVG})
    with (OUT / "group1-map.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    remaining = sorted(r for r in refs if r not in MAP)
    n = math.ceil(len(remaining) / 20)
    agg = {"COUT*": ("COUT", sum(1 for r in remaining if r.startswith("COUT"))), "CIN*": ("CIN", sum(1 for r in remaining if r.startswith("CIN"))), "CEF*": ("CEFIN", sum(1 for r in remaining if r.startswith("CEF")))}
    na = [r for r in remaining if r.startswith(("TP_", "JP_", "J_"))]
    sims = json.loads((ROOT / "reports/g2/sim-results.json").read_text(encoding="utf-8"))
    runs = sims["runs"] if isinstance(sims["runs"], list) else [dict(name=k, **v) for k, v in sims["runs"].items()]
    bad = [{"name": r["name"], "family": r["family"], "completed": r["completed"], "pass": r["pass"], "missing": r.get("missing")} for r in runs if not (r["completed"] and r["pass"])]
    cov = {"group1": list(MAP), "group1_status": {s: sum(1 for v in MAP.values() if v[3] == s) for s in {v[3] for v in MAP.values()}}, "group1_pins": len(rows), "remaining_refs_ACIK": len(remaining), "remaining_groups_max20": n, "groups": {f"G{i + 2}": remaining[i * 20:(i + 1) * 20] for i in range(n)}, "aggregated_model_refs": agg, "likely_not_applicable_test_or_mechanical": na, "runs_total": len(runs), "runs_not_complete_or_not_pass": bad}
    (OUT / "coverage.json").write_text(json.dumps(cov, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: cov[k] for k in ("group1_status", "group1_pins", "remaining_refs_ACIK", "remaining_groups_max20", "aggregated_model_refs", "runs_total")}, ensure_ascii=False), len(na))
    for b in bad:
        print(b)


if __name__ == "__main__":
    main()
