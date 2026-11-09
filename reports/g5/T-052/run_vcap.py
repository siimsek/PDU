#!/usr/bin/env python3
"""T-052: isolated charge-pump/gate-share experiment vs the T-041 hand calculation. Run from repo root: python reports/g5/T-052/run_vcap.py
Behavioural, not a TI model. Does not touch design/pdu_v2.cir."""
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-052"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
C0, TOL = 100e-9, 0.10
PARTS = {"U5": {"uvlo": (5.8, 6.6, 7.7), "stop": (11.6, 13.0, 13.9), "src": "LM74700-Q1 SNOSD17G s.7, s.13 Eş.1", "qg": (19e-9, 25e-9), "fet": "Q1"},
         "U6": {"uvlo": (5.7, 6.5, 7.5), "stop": (None, 12.4, None), "src": "LM74502H SNOSDE5A s.5-6, s.11 Eş.1", "qg": (37e-9, 48e-9), "fet": "Q2"}}
COND = [("hızlı", 600e-6, C0 * (1 - TOL), 0), ("tipik", 300e-6, C0, 1), ("yavaş", 162e-6, C0 * (1 + TOL), 2)]
rows = []
for u, p in PARTS.items():
    for name, i, c, k in COND:
        vu = p["uvlo"][k]
        stop = p["stop"][1]
        qg = p["qg"][1]
        cg = qg / stop
        hand_t = 75e-6 + c * vu / i
        hand_dv = qg / c
        tq = 2 * c * stop / i
        tag = f"{u}_{name}".replace("ı", "i").replace("ş", "s")
        deck = f"""* T-052 isolated charge pump {tag}
.param IP={i} C={c} VSTOP={stop} CG={cg} TG={tq}
BCP 0 vcap I = {{IP}}*min(max(({{VSTOP}}-V(vcap))/10m,0),1)*(1-(time>{{TG}}))
CV vcap 0 {{C}} IC=0
SW1 vcap g ctrl 0 SWG
.model SWG SW(Ron=1 Roff=1e9 Vt=0.5 Vh=0.01)
VC ctrl 0 PWL(0 0 {{TG}} 0 {{TG*1.001}} 1)
CGL g 0 {{CG}} IC=0
RGL g 0 1G
.tran {tq / 8000} {tq * 1.2} 0 {tq / 8000} UIC
.meas tran tuv WHEN V(vcap)={vu} RISE=1
.meas tran vpre FIND V(vcap) AT={tq * 0.99}
.meas tran vend FIND V(vcap) AT={tq * 1.19}
.end
"""
        f = OUT / f"{tag}.cir"
        f.write_text(deck, encoding="utf-8", newline="\n")
        lg = f.with_suffix(".log")
        code = subprocess.run([NG, "-b", "-o", lg.name, f.name], cwd=OUT, capture_output=True, timeout=120).returncode
        tx = lg.read_text(errors="replace")
        v = {m: (float(x.group(1)) if (x := re.search(rf"^{m}\s*=\s*([-+0-9.eE]+)", tx, re.M)) else None) for m in ("tuv", "vpre", "vend")}
        sim_t = v["tuv"] + 75e-6 if v["tuv"] else None
        sim_dv = v["vpre"] - v["vend"] if v["vpre"] and v["vend"] else None
        rows.append({"ref": u, "case": name, "I_uA": i * 1e6, "C_nF": round(c * 1e9, 1), "uvlo_V": vu, "exit": code, "hand_t_ms": round(hand_t * 1e3, 4), "sim_t_ms": None if sim_t is None else round(sim_t * 1e3, 4), "t_err_pct": None if sim_t is None else round(100 * (sim_t - hand_t) / hand_t, 3), "hand_dV_V": round(hand_dv, 4), "sim_dV_V": None if sim_dv is None else round(sim_dv, 4), "src": p["src"], "qg_nC_max": qg * 1e9, "vstop_V": stop})
(OUT / "results.json").write_text(json.dumps({"model": "İzole davranışsal; TI modeli değil", "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
T = "\n".join(f"| {r['ref']} | {r['case']} | {r['I_uA']:.0f} | {r['C_nF']} | {r['uvlo_V']} | {r['exit']} | {r['hand_t_ms']} | {r['sim_t_ms']} | {r['t_err_pct']} | {r['hand_dV_V']} | {r['sim_dV_V']} |".replace(".", ",") for r in rows)
(OUT / "report.md").write_text(f"""# T-052 — İzole U5/U6 VCAP ve kapı yükü deneyi

**Durum: Review. Ana deck, F5 kanıtı, şema, PCB ve BOM değişmedi.** Etiket SİM; TI modeli veya fiziksel kanıt değildir. Şarj pompası sabit akımlı kaynak, 75 µs veri sayfası gecikmesi sonradan eklendi. Kapı yükü Cg = Qg_maks / Vdur eşdeğer kapasitesidir. Sonuç [results.json](results.json), deck'ler `U*.cir`.

Girdiler: LM74700-Q1 SNOSD17G s.7 ve s.13; LM74502H SNOSDE5A s.5–6 ve s.11; Qg maks Q1 25 nC (Infineon Rev. 2.4 s.3), Q2 48 nC (SLPS406B, params.py). Akım 162/300/600 µA veri sayfasında VCAP farkı 7 V koşulundadır.

| Ref | Durum | I µA | C nF | UVLOR V | exit | El t ms | SİM t ms | Hata % | El ΔV V | SİM ΔV V |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{T}

Fark: SİM kapasiteye yük paylaşımıyla düşüm verir, el hesabı `Qg/C` yaklaşıklığıdır. Tipik ve sınır satırları ayrıdır; uç akımlar garanti zaman değildir.

AÇIK: X7R DC-bias, VCAP'e bağlı akımın 7 V dışı değeri, gerçek kapı eğrisi, pompanın kapı şarjı sırasındaki katkısı, F5 ile etkileşim. Tezgâh gerekir.
""", encoding="utf-8", newline="\n")
for r in rows:
    print(r["ref"], r["case"], r["exit"], r["hand_t_ms"], r["sim_t_ms"], r["t_err_pct"], r["hand_dV_V"], r["sim_dV_V"])
