#!/usr/bin/env python3
"""T-038 diagnostic variants of the two F5 corners that never finish. NOT the official result.

The unchanged decks stall at t = 214.114 us (see stall-evidence.json). Variants add one RC filter between node ens and the
three V(ens)>0.5 comparisons, for sensitivity only. design/pdu_v2.cir and the original decks are not touched.
Run from the repo root: python reports/g5/T-038/run_variant.py
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-038"
VDIR = OUT / "variant"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
CORNERS = ("f5_vt11.487_td300ns_ctyp_r200m_l0.8", "f5_vt11.765_td300ns_ctyp_r200m_l0.8")
TAUS = (0.2e-6, 1e-6, 5e-6)
CRIT = {"o1_max_fault": ("<=", 12.0), "vsafe_max_fault": ("<", 30.0), "vraw_max_fault": ("<", 60.0)}   # analysis/g2/sim_runner.py F5
VDIR.mkdir(parents=True, exist_ok=True)
base = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8")
assert base.count("V(ens)>0.5") >= 3
rows = []
for tau in TAUS:
    tag = f"tau{tau * 1e6:g}us".replace(".", "p")
    net = base.replace("V(ens)>0.5", "V(ensf)>0.5")
    a = "RENS ens 0 1G\n"
    assert net.count(a) == 1
    net = net.replace(a, a + f"* DIAGNOSTIC ONLY (T-038): RC filter between ens and the enable comparisons\nRENSF ens ensf {tau / 1e-9:g}\nCENSF ensf 0 1n\nRENSFL ensf 0 1G\n")
    nf = VDIR / f"netlist_{tag}.cir"
    nf.write_text(net, encoding="utf-8", newline="\n")
    for c in CORNERS:
        deck = (ROOT / f"reports/g2/sim/f5/{c}.cir").read_text(encoding="utf-8")
        deck = deck.replace(".include ../../../../design/pdu_v2.cir", f".include netlist_{tag}.cir")
        m = re.search(r"^\.ic .*$", deck, re.M); assert m
        ens = re.search(r"V\(ens\)=(\S+)", m.group(0))
        deck = deck.replace(m.group(0), m.group(0) + f" V(ensf)={ens.group(1) if ens else 0}")
        f = VDIR / f"{c}_{tag}.cir"
        f.write_text(deck, encoding="utf-8", newline="\n")
        log = f.with_suffix(".log")
        t0 = time.time()
        try:
            code = subprocess.run([NG, "-b", "-o", log.name, f.name], cwd=VDIR, capture_output=True, timeout=600).returncode
        except subprocess.TimeoutExpired:
            code = -9
        lt = log.read_text(errors="replace") if log.exists() else ""
        names = re.findall(r"^\.meas tran (\S+)", deck, re.M)
        vals = {n: float(x.group(1)) for n in names if (x := re.search(rf"^{n}\s*=\s*([-+0-9.eE]+)", lt, re.M))}
        done = code == 0 and len(vals) == len(names)
        ver = {k: (vals[k] <= l if o == "<=" else vals[k] < l) if k in vals else None for k, (o, l) in CRIT.items()}
        rows.append({"corner": c, "tau_s": tau, "exit": code, "seconds": round(time.time() - t0, 2), "measures_found": len(vals), "measures_total": len(names), "completed": done, "criteria": ver, "measures": vals})
(OUT / "variant-results.json").write_text(json.dumps({"status": "TANI AMAÇLI, RESMİ SONUÇ DEĞİL", "ngspice": NG, "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
for r in rows:
    print(r["corner"][6:14], r["tau_s"], r["exit"], r["seconds"], r["completed"], r["criteria"], {k: round(r["measures"][k], 3) for k in ("vraw_max_fault", "vsafe_max_fault", "o1_max_fault") if k in r["measures"]})
