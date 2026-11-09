#!/usr/bin/env python3
"""T-040: LM70880 BIAS option arithmetic. Run from the repo root: python reports/g5/T-040/calc_bias.py  (writes results.json, report.md)"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-040"
DS = "TI LM70880-Q1 SNVSBX7A (JUNE 2024) https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf"
VCC_DS, VCC_CODE = 8.0, 5.0        # p.12 adjustable output -> 8 V; analysis/g2/power.py:173 uses 5 V
VOUT = 11.0                         # VARSAYIM nominal bus for the BIAS=VOUT option
VINS = (20.0, 22.2, 26.0)
IVCC = (5e-3, 10e-3, 20e-3)         # VARSAYIM: no IVCC table value read; power.py uses 10 mA
RTH = {"EVM 18,6": 18.6, "JEDEC 33,5": 33.5}   # p.6
BIAS_ABS = 32.0                     # p.5
sim = json.loads((ROOT / "reports/g2/sim-results.json").read_text(encoding="utf-8"))
runs = sim["runs"] if isinstance(sim["runs"], list) else [dict(name=k, **v) for k, v in sim["runs"].items()]
peak = {}
for r in runs:
    v = r["measures"].get("vraw_max_fault")
    if v is not None and "noprot" not in r["name"]:
        if v > peak.get(r["family"], (0, ""))[0]:
            peak[r["family"]] = (round(v, 2), r["name"])
bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design/bom-v2.csv").open(encoding="utf-8"))}
rows = []
for vin in VINS:
    for i in IVCC:
        a8, a5, b = (vin - VCC_DS) * i, (vin - VCC_CODE) * i, (VOUT - VCC_DS) * i
        rows.append({"VIN": vin, "IVCC_mA": i * 1000, "AGND_VCC8_W": round(a8, 4), "AGND_VCC5_code_W": round(a5, 4), "BIAS_VOUT_W": round(b, 4), "saving_W": round(a8 - b, 4), "dTj_EVM_saving_C": round((a8 - b) * 18.6, 2), "dTj_JEDEC_saving_C": round((a8 - b) * 33.5, 2)})
res = {"doc": DS, "VCC_datasheet_V": VCC_DS, "VCC_power_py_V": VCC_CODE, "rows": rows, "vraw_peak_sim_by_family": peak, "bias_abs_V": BIAS_ABS, "rboot1": bom["RBOOT1"]["value"], "cboot1": bom["CBOOT1"]["value"], "cvcc1": bom["CVCC1"]["value"]}
(OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
t = "\n".join(f"| {r['VIN']} | {r['IVCC_mA']:.0f} | {r['AGND_VCC8_W']:.3f} | {r['AGND_VCC5_code_W']:.3f} | {r['BIAS_VOUT_W']:.3f} | {r['saving_W']:.3f} | {r['dTj_EVM_saving_C']:.2f} | {r['dTj_JEDEC_saving_C']:.2f} |".replace(".", ",") for r in rows)
f1 = peak.get("F1", (None, ""))
f5 = peak.get("F5", (None, ""))
md = f"""# T-040 — LM70880 BIAS kayıp ve seçenek analizi

**Durum: Review. Şema, PCB ve değer değişmedi.** Karar THINKER'ındır. Sayılar [results.json](results.json), üreten betik [calc_bias.py](calc_bias.py).

Kaynak: {DS}.

## Veri sayfası

- s.12: "12V fixed output or an adjustable output" için VCC **8 V**; BIAS VOUT'a veya 10–30 V kaynağa bağlanabilir.
- s.13: BIAS kullanılmıyorsa AGND'ye; BIAS > 9,1 V (tipik) iken VCC regülatör girişi VIN'den BIAS'a geçer. BIAS 32 V'u aşamaz (s.13, s.5). Harici kaynakta VIN her koşulda BIAS'tan büyük olmalı.
- s.3/CBOOT: VCC = 8 V seçilirse bootstrap'a 1 Ω seri direnç. BOM: RBOOT1 {res['rboot1']}, CBOOT1 {res['cboot1']}, CVCC1 {res['cvcc1']}.

## Bulgu: `power.py` VCC değeri

`analysis/g2/power.py:173` kaybı `(VIN − 5 V) × 10 mA` ile alır. Ayarlı çıkışta veri sayfası VCC'yi 8 V verir. Kod kaybı fazla hesaplıyor; yönü güvenli tarafta, değer yanlış. 10 mA IVCC kaynaklı değildir, **VARSAYIM**. Gerçek IVCC (kapı yükü × fsw dahil) veri sayfası tablosundan okunamadı, **AÇIK**.

## Karşılaştırma (HESAP, IVCC varsayımlarıyla)

P = (VBesleme − VCC) × IVCC. BIAS=VOUT için VOUT = {VOUT} V VARSAYIM. ΔTj = P × RθJA (s.6 değerleri; tasarım kullanımı için s.6 uyarısı geçerli).

| VIN | IVCC mA | AGND, VCC 8 V (W) | Kod 5 V (W) | BIAS=VOUT (W) | Kazanç (W) | ΔTj EVM (°C) | ΔTj JEDEC (°C) |
|---:|---:|---:|---:|---:|---:|---:|---:|
{t}

Kayıplar akım varsayımına bağlıdır, ölçüm veya garanti değildir.

## Seçenekler

| Seçenek | Kalkış | Sınır | Durum |
|---|---|---|---|
| A: BIAS=AGND (mevcut) | VCC VIN'den, s.13'e uygun | BIAS mutlak riski yok | Geçerli; kayıp hesabı düzeltilmeli |
| B: BIAS=VOUT | Çıkış yükselene kadar VIN'den; BIAS>9,1 V geçişi | VOUT hatada BIAS'ı da yükseltir. SİM VRAW tepe: F1 {f1[0]} V ({f1[1]}), F5 {f5[0]} V ({f5[1]}; 47/49, iki köşe T-038'de). F1 değeri 32 V mutlak sınırı aşıyor | **Mevcut hata senaryosunda sığmıyor**, kelepçe gerektirir; AÇIK |
| C: Harici 10–30 V | Kartta uygun kaynak yok | VIN > BIAS her koşulda | AÇIK |

Isı sonucu: kazanç ΔTj tabloda; karar için gerçek IVCC ve kart RθJA gerekir. Tasarım değişikliği gerekirse ayrı THINKER kararı. SİM fiziksel kanıt değildir; tezgâh: VCC gerilimi, U1/U2 sıcaklığı.
"""
(OUT / "report.md").write_text(md, encoding="utf-8", newline="\n")
print(json.dumps({"peak": peak, "rboot": res["rboot1"]}, ensure_ascii=False))
