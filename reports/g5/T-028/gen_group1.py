#!/usr/bin/env python3
"""T-028 group 1: pin-by-pin record of 17 active references against manufacturer datasheets.

Inputs: reports/g5/T-027/ledger-references.csv, ledger-pins.csv, design/bom-v2.csv and the datasheet tables typed below
(document, revision and page recorded; read from the PDF text of the URL given). Writes group1-refs.csv, group1-pins.csv, coverage-plan.json.
Run from the repo root: python reports/g5/T-028/gen_group1.py
"""
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-028"
TI = "https://www.ti.com/lit/ds/symlink/"
DOC = {  # key: (manufacturer, document, revision date, url, package text)
    "LM70880": ("Texas Instruments", "SNVSBX7A", "JUNE 2024", TI + "lm70880-q1.pdf", "VQFN-29 RRX0029B"),
    "TPS25982": ("Texas Instruments", "SLVSEI3D", "MAY 2026", TI + "tps25982.pdf", "VQFN RGE0024M"),
    "LM74700": ("Texas Instruments", "SNOSD17G", "DECEMBER 2020", TI + "lm74700-q1.pdf", "SOT-23-6 DBV0006A"),
    "LM74502": ("Texas Instruments", "SNOSDE5A", "MAY 2022", TI + "lm74502.pdf", "SOT-23-8 DDF0008A"),
    "TLV3601": ("Texas Instruments", "SNOSDB1E", "APRIL 2023", TI + "tlv3601.pdf", "SC70-5 DCK0005A"),
    "REF50": ("Texas Instruments", "SBOS456H", "FEBRUARY 2015", TI + "ref5025a-q1.pdf", "SOIC-8 D"),
    "G74": ("Texas Instruments", "SCES794G", "SEPTEMBER 2021", TI + "sn74lvc1g74.pdf", "VSSOP-8 DCU0008A"),
    "TPS7A16": ("Texas Instruments", "SBVS188E", "MAY 2023", TI + "tps7a16-q1.pdf", "HVSSOP-8 DGN"),
    "INA296": ("Texas Instruments", "SBOSA32D", "JUNE 2025", TI + "ina296a-q1.pdf", "VSSOP-8 DGK0008A"),
    "G11": ("Texas Instruments", "SCES487I", "NOVEMBER 2024", TI + "sn74lvc1g11.pdf", "SOT-23-6 DBV0006A"),
    "CSD19531": ("Texas Instruments", "SLPS406B", "MAY 2014", TI + "csd19531q5a.pdf", "SON 5x6 Q5A"),
    "BSC160": ("Infineon", "BSC160N10NS3 G Rev. 2.4", "2009-10-30", "https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc160n10ns3-ds-en.pdf", "PG-TDSON-8"),
}
# pin -> datasheet name; page = PDF page of the pin table
TABLE = {
    "LM70880": ({1: "VIN4", 2: "VIN5", 3: "VIN6", 4: "CBOOT", 5: "SW4", 6: "BIAS", 7: "PG/SYNCOUT", 8: "PFM/SYNCIN", 9: "EN/UVLO", 10: "NC", 11: "ISNS+", 12: "VOUT", 13: "CONFIG", 14: "RT", 15: "EXTCOMP", 16: "FB", 17: "AGND", 18: "VDDA", 19: "VCC", 20: "SW1", 21: "SW2", 22: "SW3", 23: "PGND1", 24: "PGND2", 25: "PGND3", 26: "PGND4", 27: "VIN1", 28: "VIN2", 29: "VIN3", 30: "PGND"}, "3-4"),
    "TPS25982": ({1: "IN", 2: "IN", 3: "IN", 4: "GND", 5: "GND", 6: "EN/UVLO", 7: "ITIMER", 8: "ILIM", 9: "IMON", 10: "RETRY_DLY", 11: "NRETRY", 12: "LDSTRT", 13: "PG", 14: "GND", 15: "dVdt", 16: "IN", **{i: "OUT" for i in range(17, 25)}, 25: "IN_EP", 26: "GND_EP"}, "5-6"),
    "LM74700": ({1: "VCAP", 2: "GND", 3: "EN", 4: "CATHODE", 5: "GATE", 6: "ANODE"}, "3"),
    "LM74502": ({1: "EN/UVLO", 2: "GND", 3: "NC", 4: "VCAP", 5: "VS", 6: "GATE", 7: "OV", 8: "SRC"}, "3"),
    "TLV3601": ({1: "OUT", 2: "VEE", 3: "IN+", 4: "IN-", 5: "VCC"}, "3"),
    "REF50": ({1: "DNC", 2: "VIN", 3: "TEMP", 4: "GND", 5: "TRIM/NR", 6: "VOUT", 7: "NC", 8: "DNC"}, "4"),
    "G74": ({1: "CLK", 2: "D", 3: "Q_N", 4: "GND", 5: "Q", 6: "CLR_N", 7: "PRE_N", 8: "VCC"}, "4"),
    "TPS7A16": ({1: "OUT", 2: "FB/NC", 3: "PG", 4: "GND", 5: "EN", 6: "NC", 7: "DELAY", 8: "IN", 9: "EP"}, "3"),
    "INA296": ({1: "IN-", 2: "GND", 3: "REF2", 4: "NC", 5: "OUT", 6: "VS", 7: "REF1", 8: "IN+"}, "2-3"),
    "G11": ({1: "A", 2: "GND", 3: "B", 4: "Y", 5: "VCC", 6: "C"}, "3"),
    "CSD19531": ({1: "S", 2: "S", 3: "S", 4: "G", 5: "D"}, "1 (Top View); pad 5 = pins 5-8"),
    "BSC160": ({1: "S", 2: "S", 3: "S", 4: "G", 5: "D"}, "1 (S 1-3, G 4, D 5-8 sembol görseli); kart pad 5 = pin 5-8"),
}
REFS = {"U1": "LM70880", "U2": "LM70880", "U3": "TPS25982", "U4": "TPS25982", "U5": "LM74700", "U6": "LM74502", "U7": "TLV3601", "U13": "TLV3601", "U14": "TLV3601", "U8": "REF50", "U9": "G74", "U10": "TPS7A16", "U11": "INA296", "U12": "INA296", "U15": "G11", "Q1": "BSC160", "Q2": "CSD19531"}
# (pitch, pad width, pad length, centre span) from the TI example board layout, PDF page
LAND = {"LM74700": (0.95, 0.6, 1.1, 2.6, 34), "LM74502": (0.65, 0.45, 1.05, 2.6, 28), "TLV3601": (0.65, 0.4, 0.95, 2.2, 34), "REF50": (1.27, 0.6, 1.55, 5.4, 24), "G74": (0.5, 0.3, 0.85, 3.1, 23), "TPS7A16": (0.65, 0.45, 1.4, 4.4, 28), "INA296": (0.65, 0.45, 1.4, 4.4, 38), "G11": (0.95, 0.6, 1.1, 2.6, 22)}
# measured from the footprints on the board (local pad coordinates): pitch, width, length, centre span
BOARD = {"LM74700": (0.95, 0.6, 1.325, 2.274), "LM74502": (0.65, 0.5, 1.325, 2.274), "TLV3601": (0.65, 0.35, 1.025, 1.676), "REF50": (1.27, 0.6, 1.95, 4.95), "G74": (0.5, 0.35, 1.25, 2.8), "TPS7A16": (0.65, 0.5, 1.45, 4.3), "INA296": (0.65, 0.5, 1.625, 4.224), "G11": (0.95, 0.6, 1.325, 2.274)}
CUSTOM = {"LM70880": ("repo özel land; analysis/check_footprints.py PASS (30 pad)", "AÇIK", "Pad ölçüsü betik PASS; bakır yaklaşımı ve pasta kabulü bom.py notunda açık, üretici onayı yok"),
          "TPS25982": ("repo özel land; analysis/check_footprints.py PASS (26 pad)", "AÇIK", "Pad ölçüsü betik PASS; kabul açık"),
          "CSD19531": ("TI SLPS406B 7.2 p.10 F1..F11; analysis/check_footprints.py PASS (5 pad, 1 polygon)", "PASS", "TI F bantları betikle kontrol edildi"),
          "BSC160": ("Veri sayfasında önerilen land sayfası bulunamadı; repo özel land, check_footprints PASS (5 pad)", "AÇIK", "Üretici land kaynağı doğrulanamadı; bom.py: final land/paste kabulü açık")}
NOTES = {("LM70880", 6): "/GND: p.13 'Tie the BIAS pin to AGND if unused'. p.3 tablosu 12 V/ayarlı çıkışta VOUT veya 10-30 V bias önerir; BIAS kullanmama ek LDO kaybı getirir (power.py VARSAYIM).",
         ("LM70880", 10): "NC: p.4 boş bırak veya GND.", ("LM70880", 8): "/GND=FPWM (U1) ya da /SYNC girişi (U2): p.4.",
         ("TPS25982", 7): "NC: p.5 açık bırakılırsa en hızlı tepki.", ("TPS25982", 10): "/GND: p.5 latch-off.", ("TPS25982", 11): "/GND: p.5; RETRY_DLY GND iken latch-off.", ("TPS25982", 12): "/GND: p.5 LDSTRT kullanılmıyorsa GND.",
         ("LM74502", 3): "NC.", ("REF50", 1): "DNC: bağlı değil.", ("REF50", 8): "DNC: bağlı değil.", ("REF50", 7): "NC: bağlı değil.", ("REF50", 3): "TEMP çıkışı kullanılmıyor.",
         ("TPS7A16", 2): "FB/NC sabit çıkışta açık bırakılabilir (p.3).", ("TPS7A16", 6): "NC.", ("INA296", 4): "/GND: p.2 'Reserved. Connect to ground'.", ("G74", 3): "Q̄ kullanılmıyor (kasıtlı NC).", ("G11", 1): "Şema sembolünde pin adı boş; numara A işlevine karşılık gelir.", ("G11", 3): "Şema sembolünde pin adı boş; numara B işlevine karşılık gelir.", ("G11", 4): "Şema sembolünde pin adı boş; numara Y çıkışına karşılık gelir.", ("G11", 6): "Şema sembolünde pin adı boş; numara C işlevine karşılık gelir."}
ALIAS = {"Q_N": "~{Q}", "CLR_N": "~{CLR}", "PRE_N": "~{PRE}", "VIN": "VIN"}


def norm(s):
    return re.sub(r"[\s_.]", "", s.replace("–", "-")).upper().replace("~{", "").replace("}", "")


def main():
    refs = {r["ref"]: r for r in csv.DictReader((ROOT / "reports/g5/T-027/ledger-references.csv").open(encoding="utf-8"))}
    pins = list(csv.DictReader((ROOT / "reports/g5/T-027/ledger-pins.csv").open(encoding="utf-8")))
    bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
    out_p, out_r = [], []
    for ref, key in REFS.items():
        tb, page = TABLE[key]
        rows = [p for p in pins if p["ref"] == ref]
        assert sorted(int(p["pin"]) for p in rows) == sorted(tb), ref
        for p in sorted(rows, key=lambda x: int(x["pin"])):
            n = int(p["pin"])
            sch = re.sub(r"_\d+$", "", p["name"])
            ds = tb[n]
            named = sch != ""
            ok = norm(ALIAS.get(ds, ds)) == norm(sch) or not named
            pcb = p["state"] == "EŞLEŞTİ"
            status = ("PASS" if named else "AÇIK") if ok and pcb else "FAIL"
            note = NOTES.get((key, n), "")
            out_p.append({"ref": ref, "pin": n, "schematic_name": sch, "datasheet_name": ds, "net": p["net"], "nc": p["nc"], "t027_pcb_state": p["state"], "doc": DOC[key][1], "pdf_page": page, "status": status, "note": note})
        doc = DOC[key]
        if key in CUSTOM:
            land, st, why = CUSTOM[key]
        else:
            ti, b = LAND[key], BOARD[key]
            dl, ds_ = round(b[2] - ti[2], 3), round(b[3] - ti[3], 3)
            pitch_ok = abs(ti[0] - b[0]) < 0.01
            st = "FAIL" if not pitch_ok else "AÇIK"
            land = f"TI p.{ti[4]}: pitch {ti[0]}, pad {ti[1]}x{ti[2]}, span {ti[3]}; kart: pitch {b[0]}, pad {b[1]}x{b[2]}, span {b[3]}"
            why = f"Pitch eşit; pad boyu farkı {dl:+} mm, span farkı {ds_:+} mm. KiCad IPC-7351 kütüphanesi TI örneğinden farklı; üretici/montaj kabulü yok."
        status = "FAIL" if any(r["status"] == "FAIL" for r in out_p if r["ref"] == ref) else ("AÇIK" if st != "PASS" or doc[2] == "doğrulanamadı" else "PASS")
        out_r.append({"ref": ref, "bom_mpn": bom[ref]["mpn"], "manufacturer": doc[0], "doc": doc[1], "doc_rev": doc[2], "url": doc[3], "package_ds": doc[4], "footprint": refs[ref]["footprint"], "pin_count": len(rows), "pin_table_page": page, "land_compare": land, "land_status": st, "land_note": why, "reference_status": status})
    with (OUT / "group1-pins.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, list(out_p[0]), lineterminator="\n"); w.writeheader(); w.writerows(out_p)
    with (OUT / "group1-refs.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, list(out_r[0]), lineterminator="\n"); w.writeheader(); w.writerows(out_r)
    remaining = sorted(r for r in refs if r not in REFS)
    n = math.ceil(len(remaining) / 20)
    plan = {"total_schematic_refs": len(refs), "group1_refs": list(REFS), "group1_pins": len(out_p), "remaining_refs": len(remaining), "remaining_groups_max20": n, "groups": {f"G{i + 2}": remaining[i * 20:(i + 1) * 20] for i in range(n)}}
    (OUT / "coverage-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    c = {}
    for r in out_p: c[r["status"]] = c.get(r["status"], 0) + 1
    d = {}
    for r in out_r: d[r["reference_status"]] = d.get(r["reference_status"], 0) + 1
    print(json.dumps({"pins": len(out_p), "pin_status": c, "refs": len(out_r), "ref_status": d, "land": {r["ref"]: r["land_status"] for r in out_r}, "remaining": len(remaining), "groups": n}, ensure_ascii=False))
    for r in out_p:
        if r["status"] != "PASS":
            print("!!", r)


if __name__ == "__main__":
    main()
