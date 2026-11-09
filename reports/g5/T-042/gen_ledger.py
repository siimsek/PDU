#!/usr/bin/env python3
"""T-042 sourcing ledger: first 20 critical references. Facts are typed from pages read on 2026-11-09. Run: python reports/g5/T-042/gen_ledger.py"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-042"
AOPEN = "AÇIK"
# mpn: (official page, TR seller/channel, TR stock, MOQ, source, status)
FACT = {
    "LM70880QRRXRQ1": ("https://www.ti.com/product/LM70880-Q1", "Türkiye satıcısı bulunamadı", AOPEN, AOPEN, "https://www.digikey.com/en/products/detail/texas-instruments/LM70880QRRXRQ1/24420927", "DigiKey (global, Türkiye stoğu değil): stok 0; 28.12.2026 için 2990 beklenen; üretici standart termin 26 hafta; Active"),
    "LM74700QDBVRQ1": ("https://www.ti.com/product/LM74700-Q1", "Ozdisan", "0 (In Stock: 0, On Order: No)", "1", "https://www.ozdisan.com/en/p/or-controllers-and-ideal-diodes-280/texas-lm74700qdbvrq1-1588786", "Sayfa 'Manufacturer Standard Lead Time 1-2 Weeks' yazıyor, fiyat talep üzerine; teslim teyidi yok"),
}
for m, slug in (("TPS259824LNRGER", "TPS25982"), ("LM74502HDDFR", "LM74502"), ("TLV3601DCKR", "TLV3601"), ("REF5025AQDRQ1", "REF5025A-Q1"), ("SN74LVC1G74DCUR", "SN74LVC1G74"), ("TPS7A1650QDGNRQ1", "TPS7A16-Q1"), ("INA296A2QDGKRQ1", "INA296A-Q1"), ("SN74LVC1G11DBVR", "SN74LVC1G11"), ("CSD19531Q5A", "CSD19531Q5A")):
    FACT[m] = (f"https://www.ti.com/product/{slug}", "Bu taramada satıcı sayfası okunmadı", AOPEN, AOPEN, "", "Doğrulanamadı")
FACT["BSC160N10NS3G"] = ("https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc160n10ns3-ds-en.pdf", "Bu taramada satıcı sayfası okunmadı", AOPEN, AOPEN, "", "Doğrulanamadı")
FACT["IHLP4040DZER6R8M01"] = ("Vishay Dale (BOM)", "Bu taramada satıcı sayfası okunmadı", AOPEN, AOPEN, "", "Doğrulanamadı")
FACT["SMCJ33A-E3/57T"] = ("Vishay 88394 (BOM)", "Bu taramada satıcı sayfası okunmadı", AOPEN, AOPEN, "", "Doğrulanamadı")
REFS = "U1 U2 U3 U4 U5 U6 U7 U13 U14 U8 U9 U10 U11 U12 U15 Q1 Q2 L1 L2 D1".split()
bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
rows = [{"ref": r, "mpn": bom[r]["mpn"], "manufacturer": bom[r]["manufacturer"], "official": FACT[bom[r]["mpn"]][0], "tr_seller": FACT[bom[r]["mpn"]][1], "tr_stock": FACT[bom[r]["mpn"]][2], "moq": FACT[bom[r]["mpn"]][3], "date": "2026-11-09", "source": FACT[bom[r]["mpn"]][4], "note": FACT[bom[r]["mpn"]][5]} for r in REFS]
with (OUT / "sourcing-20.csv").open("w", encoding="utf-8", newline="\n") as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
rest = sorted(r for r in bom if r not in REFS)
n = math.ceil(len(rest) / 20)
(OUT / "coverage.json").write_text(json.dumps({"bom_refs": len(bom), "this_ledger": len(REFS), "remaining": len(rest), "groups": n, "group_refs": {f"S{i + 2}": rest[i * 20:(i + 1) * 20] for i in range(n)}}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(len(rows), len(rest), n)
