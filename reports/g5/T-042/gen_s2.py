#!/usr/bin/env python3
"""T-042 S2: Turkey sourcing record of the 20 G2 TDK capacitor references. Facts typed from pages read on 2026-11-09. No order, no quote request.
Run from the repo root: python reports/g5/T-042/gen_s2.py"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-042"
OPEN = "AÇIK"
TDK = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no="
OZ = "https://www.ozdisan.com/p/smt-smd-ve-mlcc-kapasitorler-184/tdk-c1608x7r1h104kt-l-526261"
NOTE = "Ozdisan alan aramasında tam MPN sayfası çıkmadı; yokluk kanıtı değil."
SPECIAL = {"C1608X7R1H104K080AA": ("Ozdisan (yalnız yakın kod)", OPEN, OPEN, OZ, "Tam MPN sayfası çıkmadı. Sayfa C1608X7R1H104KT-L: 100 nF 50 V ±%10 X7R 0603, üretici standart termin 5-6 hafta, gelecek stok yok; stok sayısı okunmadı. TDK kalem tanımı C1608X7R1H104KT**** ile benzer ama aynı sipariş kodu olduğu doğrulanamadı.")}
bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
group = json.loads((OUT / "coverage.json").read_text(encoding="utf-8"))["group_refs"]["S2"]
rows = []
for ref in group:
    mpn = bom[ref]["mpn"]
    seller, stock, moq, source, note = SPECIAL.get(mpn, ("Tam MPN için Türkiye satıcısı bulunamadı", OPEN, OPEN, "", NOTE))
    rows.append({"ref": ref, "mpn": mpn, "manufacturer": bom[ref]["manufacturer"], "official": TDK + mpn, "official_status": "Production", "tr_seller": seller, "tr_stock": stock, "moq": moq, "date": "2026-11-09", "source": source, "aec_q200": "NO", "note": note})
with (OUT / "sourcing-s2.csv").open("w", encoding="utf-8", newline="\n") as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(rows), len({r["mpn"] for r in rows}), sum(r["tr_stock"] != OPEN for r in rows))
