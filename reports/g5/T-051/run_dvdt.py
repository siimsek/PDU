#!/usr/bin/env python3
"""T-051: isolated behavioural dVdt subcircuit vs the T-039 hand calculation. Run from repo root: python reports/g5/T-051/run_dvdt.py
Not a TI model: a current source into CdVdt, output tracking V(dvdt) with a current limit. Does not touch design/pdu_v2.cir."""
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-051"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
VBUS = 11.1605
CASES = [("hızlı", 6.33e-6, 0.95e-9), ("tipik", 4.6e-6, 1.0e-9), ("yavaş", 2.0e-6, 1.05e-9)]
LOADS = [4e-6, 10e-6, 100e-6, 470e-6]
RUNS = [(n, i, c, cl, 8.13, "serbest") for n, i, c in CASES for cl in LOADS] + [("hızlı", 6.33e-6, 0.95e-9, 1000e-6, 4.36, "ILIM sınırında (S2E min)")]
rows = []
def run(tag, i, c, cl, ilim):
    sr = i / c
    t = VBUS / sr
    tstop = max(t, cl * VBUS / ilim) * 1.6
    deck = f"""* T-051 isolated dVdt behaviour {tag}
.param ID={i} CD={c} CL={cl} ILIM={ilim} VBUS={VBUS}
VIN vin 0 DC {{VBUS}}
BID 0 dv I = {{ID}}*min(max(({{VBUS}}-V(dv))/10m,0),1)
CDV dv 0 {{CD}} IC=0
BFET vin out I = min({{ILIM}}, max(10*(V(dv)-V(out)),0))
CLD out 0 {{CL}} IC=0
RLK out 0 1G
.tran {tstop / 4000} {tstop} 0 {tstop / 4000} UIC
.meas tran t10 WHEN V(out)={0.1 * VBUS} RISE=1
.meas tran t90 WHEN V(out)={0.9 * VBUS} RISE=1
.meas tran vend MAX V(out)
.meas tran ipk MAX par('min(10*(V(dv)-V(out)),{ilim})')
.end
"""
    f = OUT / f"{tag}.cir"
    f.write_text(deck, encoding="utf-8", newline="\n")
    lg = f.with_suffix(".log")
    code = subprocess.run([NG, "-b", "-o", lg.name, f.name], cwd=OUT, capture_output=True, timeout=120).returncode
    tx = lg.read_text(errors="replace")
    v = {k: (float(m.group(1)) if (m := re.search(rf"^{k}\s*=\s*([-+0-9.eE]+)", tx, re.M)) else None) for k in ("t10", "t90", "vend", "ipk")}
    return code, v
for k, (name, i, c, cl, ilim, note) in enumerate(RUNS):
    code, v = run(f"run{k:02d}", i, c, cl, ilim)
    hand_sr = i / c / 1000
    hand_i = hand_sr * cl * 1000
    sim_sr = (0.8 * VBUS) / (v["t90"] - v["t10"]) / 1000 if v["t10"] and v["t90"] else None
    rows.append({"case": name, "note": note, "Id_uA": i * 1e6, "Cd_nF": c * 1e9, "CL_uF": round(cl * 1e6), "ILIM_A": ilim, "exit": code, "hand_SR_V_ms": round(hand_sr, 4), "sim_SR_V_ms": None if sim_sr is None else round(sim_sr, 4), "err_pct": None if sim_sr is None else round(100 * (sim_sr - hand_sr) / hand_sr, 3), "hand_inrush_A": round(hand_i, 4), "sim_ipk_A": v["ipk"] and round(v["ipk"], 4), "vend": v["vend"] and round(v["vend"], 4)})
(OUT / "results.json").write_text(json.dumps({"model": "İzole davranışsal; TI modeli değil", "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
T = "\n".join(f"| {r['case']} | {r['CL_uF']} | {r['ILIM_A']} | {r['exit']} | {r['hand_SR_V_ms']} | {r['sim_SR_V_ms']} | {r['err_pct']} | {r['hand_inrush_A']} | {r['sim_ipk_A']} |".replace(".", ",") for r in rows)
(OUT / "report.md").write_text(f"""# T-051 — İzole dVdt alt devresi ve T-039 karşılaştırması

**Durum: Review. Ana deck, F5 kanıtı, şema, PCB ve BOM değişmedi.** Etiket SİM; bu üretici modeli değildir ve fiziksel kanıt değildir. Devre: `IdVdt` akımı CdVdt'yi doldurur, çıkış V(dvdt)'yi akım sınırıyla izler. Girdi değerleri T-039 ve TI SLVSEI3D s.10, s.22 Eş.3'tür. Sonuç [results.json](results.json), deck'ler `run*.cir`.

| Durum | CL µF | ILIM A | exit | El SR V/ms | SİM SR V/ms | Hata % | El akım A | SİM tepe A |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{T}

Son satırda el hesabı ILIM'i yok sayar; SİM akımı ILIM'e kilitler ve SR düşer. Diğer satırlarda fark yalnız izleme kazancı ve sayısal adımdan gelir.

AÇIK: CEFOUT Ceff, dış yük, IdVdt sıcaklık değişimi, TI iç rampa gerçek davranışı, kalkış ısısı. F5 sonuçları bu modelle doğrulanmış sayılmaz.
""", encoding="utf-8", newline="\n")
for r in rows:
    print(r["case"], r["CL_uF"], r["exit"], r["hand_SR_V_ms"], r["sim_SR_V_ms"], r["err_pct"], r["hand_inrush_A"], r["sim_ipk_A"])
