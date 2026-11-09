#!/usr/bin/env python3
"""T-039: TPS25982 dVdt and start-up arithmetic. Run from the repo root: python reports/g5/T-039/calc_dvdt.py  (writes results.json, report.md)"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-039"
DS = "TI TPS25982 SLVSEI3D Rev. D (MAY 2026) https://www.ti.com/lit/ds/symlink/tps25982.pdf"
ID = {"min": 2.0, "typ": 4.6, "max": 6.33}          # uA, p.10 IdVdt
ILIM = {"O1 (RILIM 182)": (7.23, 8.13, 9.07), "S2E (RILIM 300)": (4.36, 4.98, 5.66)}     # A, analysis/g2/params.py EF_ILIM_TABLE, p.9
bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
C_NOM_NF = 1.0
assert bom["CDVDT1"]["value"] == "1.0n" and bom["CDVDT2"]["value"] == "1.0n"
TOL = 0.05                                          # C1608C0G1H102J: J = +/-5 %
VBUS = 11.1605                                      # steady bus limit (project criterion), used as the ramp height
fast, typ, slow = ID["max"] / (C_NOM_NF * (1 - TOL)), ID["typ"] / C_NOM_NF, ID["min"] / (C_NOM_NF * (1 + TOL))   # V/ms: uA/nF
sr = {"en hızlı (Imax, C-%5)": fast, "tipik": typ, "en yavaş (Imin, C+%5)": slow}
loads = {"4 µF (deck CPORT, VARSAYIM)": 4.0, "10 µF (CEFOUT nominal; Ceff bilinmiyor)": 10.0, "100 µF (örnek)": 100.0, "470 µF (örnek)": 470.0}
rows = []
for name, s in sr.items():
    for ln, c in loads.items():
        rows.append({"case": name, "sr_V_ms": round(s, 3), "ramp_ms": round(VBUS / s, 3), "load": ln, "inrush_mA": round(s * c, 1), "energy_mJ": round(0.5 * c * VBUS ** 2 / 1000, 3)})
cmax = {k: round(v[0] * 1000 / fast, 1) for k, v in ILIM.items()}      # uF where inrush reaches ILIM min at the fastest slew
deck = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8").lower()
res = {"doc": DS, "IdVdt_uA": ID, "CdVdt_nF": C_NOM_NF, "tolerance": TOL, "bus_V": VBUS, "rows": rows, "cload_uF_at_ilim_min_fastest": cmax, "vcdvdt_startup_V": round(VBUS + 4, 3), "deck_dvdt_mentions": deck.count("dvdt")}
(OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
t = "\n".join(f"| {r['case']} | {r['sr_V_ms']:.3f} | {r['ramp_ms']:.3f} | {r['load']} | {r['inrush_mA']:.1f} | {r['energy_mJ']:.3f} |".replace(".", ",") for r in rows)
md = f"""# T-039 — TPS25982 dVdt ve kalkış hesabı

**Durum: Review. Şema, PCB, BOM ve model değişmedi.** Etiketler: DATASHEET / HESAP / VARSAYIM / AÇIK. Sonuç fiziksel kanıt değildir; ham sayı [results.json](results.json), üreten betik [calc_dvdt.py](calc_dvdt.py).

Kaynak: {DS}. Formül s.22 Eş. 3: `CdVdt[pF] = 4600 / SR[V/ms]`; s.22 Eş. 2: `SR[V/ms] = IINRUSH[mA] / COUT[µF]`. IdVdt 2 / 4,6 / 6,33 µA (s.10). dVdt kapasitörü kalkışta tipik VIN+4 V görür (s.37).

## Girdiler

- CDVDT1, CDVDT2: 1,0 nF, C1608C0G1H102J080AA (C0G, ±%5, BOM). C0G'de DC-bias ihmal edildi, VARSAYIM.
- Rampa yüksekliği: kararlı bara üst sınırı {VBUS} V.
- Çıkış kapasitesi: CEFOUT1/2 nominal 10 µF X7R 1206 25 V (BOM), Ceff **bilinmiyor**. Port dışı yük kapasitesi **AÇIK**. Deck `CPORT` 4 µF VARSAYIM.

## Sonuç

SR için HESAP `IdVdt/CdVdt`; Eş. 3 ile tipikte aynı (1 nF → 4,6 V/ms).

| Durum | SR (V/ms) | Rampa (ms) | Yük | Kalkış akımı (mA) | CV²/2 (mJ) |
|---|---:|---:|---|---:|---:|
{t}

Hesap, IdVdt'in sabit olduğunu ve SR'nin yalnız CdVdt ile belirlendiğini varsayar. Fiziksel rampa FET sınırlarına ve yüke bağlıdır, **doğrulanamadı**.

- En hızlı SR'de kalkış akımının garanti ILIM alt sınırına ulaştığı C: O1 {cmax['O1 (RILIM 182)']} µF, S2E {cmax['S2E (RILIM 300)']} µF (HESAP). Dış yük kapasitesi bilinmeden kullanılamaz, AÇIK.
- CdVdt gerilimi: {VBUS}+4 = {res['vcdvdt_startup_V']} V, 50 V C0G içinde.
- U3/U4 IN < 30 V ve O1 ≤ 12,0 V kriteri bu hesapla kontrol edilmez: rampa kalkış davranışıdır, hata tepesi T-038/F aileleridir.
- Isı: FET'teki kalkış enerjisi CV²/2 ile mertebedir, güvenli çalışma alanı ve TJ **AÇIK**.
- `/DVDT_S2E` iz uzunluğu 70,1 mm (PR #70, birleşmemiş): 10 pF ek kapasite %1 etkidir (HESAP); gerçek pF ve kuplaj **doğrulanamadı**.

## Model kapsamı

`design/pdu_v2.cir` içinde dVdt ifadesi {res['deck_dvdt_mentions']} kez geçiyor. `BEF1/BEF2` yalnız etkinleştirme, akım sınırı ve Ron içerir, çıkış rampası yoktur. Bu yüzden F aileleri CDVDT kalkışını temsil etmez.

Öneri (THINKER kararı): dış yük kapasitesi belirlenince ayrı dVdt alt devre kartı. Tezgâh: kalkışta VOUT eğimi ve giriş akımı ölçümü.
"""
(OUT / "report.md").write_text(md, encoding="utf-8", newline="\n")
print(json.dumps({"sr": {k: round(v, 3) for k, v in sr.items()}, "cmax": cmax}, ensure_ascii=False))
