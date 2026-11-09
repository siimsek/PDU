#!/usr/bin/env python3
"""T-041: U5/U6 VCAP arithmetic. Run from the repo root: python reports/g5/T-041/calc_vcap.py  (writes results.json, report.md)"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-041"
bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
C_NF = {"U5": bom["CVCAP"]["value"], "U6": bom["C_ISO_VCAP"]["value"]}
assert C_NF == {"U5": "100n", "U6": "100n"}
C, TOL = 100e-9, 0.10          # C1608X7R1H104K: K = +/-10 %; DC-bias not read
I = (162e-6, 300e-6, 600e-6)   # A at VCAP-pin=7 V; LM74700 p.7, LM74502 p.5
PART = {"U5": ("LM74700-Q1", "SNOSD17G", "https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf", (5.8, 6.6, 7.7), "s.13 Eş.1", ("Q1 BSC160N10NS3 G", 19e-9, 25e-9, "Infineon Rev. 2.4 s.3")),
        "U6": ("LM74502H", "SNOSDE5A", "https://www.ti.com/lit/ds/symlink/lm74502.pdf", (5.7, 6.5, 7.5), "s.11 Eş.1", ("Q2 CSD19531Q5A", 37e-9, 48e-9, "SLPS406B s.1 tipik, params.py s.3 maks"))}
rows, share = [], []
for u, (mpn, doc, url, v, eq, q) in PART.items():
    typ = 75e-6 + C * v[1] / I[1]
    worst = 75e-6 + C * (1 + TOL) * v[2] / I[0]
    best = 75e-6 + C * (1 - TOL) * v[0] / I[2]
    rows.append({"ref": u, "mpn": mpn, "doc": doc, "url": url, "uvlo_V": v, "t_typ_ms": round(typ * 1e3, 3), "t_slow_ms": round(worst * 1e3, 3), "t_fast_ms": round(best * 1e3, 3), "eq": eq})
    share.append({"ref": u, "fet": q[0], "src": q[3], "qg_typ_nC": q[1] * 1e9, "qg_max_nC": q[2] * 1e9, "dV_typ_V": round(q[1] / C, 3), "dV_max_with_Cmin_V": round(q[2] / (C * (1 - TOL)), 3)})
(OUT / "results.json").write_text(json.dumps({"C_F": C, "tol": TOL, "I_A": I, "rows": rows, "gate_charge_share": share}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
t = "\n".join(f"| {r['ref']} ({r['mpn']}) | {r['doc']}, {r['eq']} | {r['uvlo_V'][0]} / {r['uvlo_V'][1]} / {r['uvlo_V'][2]} | {r['t_fast_ms']:.3f} | {r['t_typ_ms']:.3f} | {r['t_slow_ms']:.3f} |".replace(".", ",") for r in rows)
s = "\n".join(f"| {r['ref']} | {r['fet']} | {r['src']} | {r['qg_typ_nC']:.0f} / {r['qg_max_nC']:.0f} | {r['dV_typ_V']:.3f} | {r['dV_max_with_Cmin_V']:.3f} |".replace(".", ",") for r in share)
md = f"""# T-041 — U5/U6 VCAP ve kapı kalkış kapsamı

**Durum: Review. Şema, PCB ve model değişmedi.** Sayılar [results.json](results.json), üreten betik [calc_vcap.py](calc_vcap.py). Tipik değer garanti sayılmadı; tablo tipik ve uç değerleri ayrı verir.

## Girdiler

- U5: CVCAP 100 nF, C1608X7R1H104K080AA, VCAP–ANODE. U6: C_ISO_VCAP 100 nF, aynı MPN, VCAP–VS (BOM). Tolerans ±%10 (K); X7R DC-bias eğrisi okunmadı, **AÇIK**.
- Şarj pompası kaynak akımı 162 / 300 / 600 µA, VCAP farkı 7 V'ta (LM74700-Q1 SNOSD17G s.7, LM74502H SNOSDE5A s.5).
- Her iki belge C(VCAP) = 0,1 µF koşulunda karakterize eder (s.6–7, s.5–6). Veri sayfasında ayrı minimum C değeri okunmadı, **AÇIK**.
- Mutlak sınır: GATE ve VCAP pin farkı 15 V (s.5, s.4).

## Kapı sürücü etkinleşme gecikmesi

Formül: `T = 75 µs + C × V(VCAP_UVLOR) / 300 µA`, belgede tipik akımla verilir. Uç sütunlar aynı formüle sınır akım ve tolerans koyan HESAP'tır, üretici garantisi değildir.

| Ref | Kaynak | UVLO min/tip/maks V | Hızlı (ms) | Tipik (ms) | Yavaş (ms) |
|---|---|---:|---:|---:|---:|
{t}

## Kapı yükü ve VCAP düşümü (HESAP, ΔV = Qg / C)

| Ref | FET | Kaynak | Qg tip/maks nC | ΔV tipik (V) | ΔV maks, Cmin (V) |
|---|---|---|---:|---:|---:|
{s}

VCAP UVLO histerezisi ve pompanın gate şarjı sırasındaki katkısı dahil değil. UVLO düşüşüne yakınlık için ayrıntılı dinamik **AÇIK**.

## Model kapsamı

`design/pdu_v2.cir` içinde U5 ayrı eleman değil, `BQ1` ideal diyot (Q1 gate düğümü yok). U6 için `BCTL/CCTL/RCTL` yalnız `TDLY` gecikmeli kontrol üretir. VCAP düğümü, UVLO gecikmesi, EN/UVLO girişi, SRC/VS ve Qg yükü yoktur. Bu yüzden F aileleri giriş kalkışında kapı gecikmesini temsil etmez.

PCB: `/VCAP` yolu 28,76 mm (PR #70, birleşmemiş). Sayısal ihlal değil; gürültü ve etkisi **doğrulanamadı**.

Öneri (THINKER kararı): gerekirse VCAP/gate alt devre kartı. Tezgâh: VCAP şarj süresi, Q1/Q2 VGS rampası.
"""
(OUT / "report.md").write_text(md, encoding="utf-8", newline="\n")
print(json.dumps([{k: r[k] for k in ("ref", "t_fast_ms", "t_typ_ms", "t_slow_ms")} for r in rows]), share)
