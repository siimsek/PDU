#!/usr/bin/env python3
"""T-053 controlled experiment: internal ens comparison, EN pin hysteresis untouched. design/pdu_v2.cir is NOT changed.
Run from repo root: python reports/g5/T-053/run_t053.py   (writes variants.json and logs of the two stalled corners)"""
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-053/run"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
LIMIT = 120
STUCK = ["f5_vt11.487_td300ns_ctyp_r200m_l0.8", "f5_vt11.765_td300ns_ctyp_r200m_l0.8"]
NEIGH = ["f5_vt11.487_td300ns_ctyp_r200m_l1.2", "f5_vt11.487_td300ns_ctyp_r20m_l0.8", "f5_vt11.765_td1048ns_cmin_r20m_l1.2", "f1_worst", "f2_hotplug_26V", "f2_ramp_to_20V_uvlo_high_corner", "f2_dip_22V_to_15V_restart"]
V = [("rc", x) for x in (0.05e-6, 0.2e-6, 1e-6, 2e-6, 5e-6)] + [("schmitt", x) for x in ((0.45, 0.55), (0.4, 0.6), (0.3, 0.7))]
OUT.mkdir(parents=True, exist_ok=True)
sim = json.loads((ROOT / "reports/g2/sim-results.json").read_text(encoding="utf-8"))
runs = {r["name"]: r for r in (sim["runs"] if isinstance(sim["runs"], list) else [dict(name=k, **v) for k, v in sim["runs"].items()])}
base = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8")
assert base.count("V(ens)>0.5") >= 3
def netlist(kind, x):
    if kind == "rc":
        tag = f"rc{x * 1e6:g}us".replace(".", "p")
        add = f"RENSF ens ensf {x / 1e-9:g}\nCENSF ensf 0 1n\nRENSFL ensf 0 1G\n"
    else:
        tag = f"sch{x[0]:g}_{x[1]:g}".replace(".", "p")
        add = f"BENSF 0 ensf I = 1e-3*(V(ens)>{x[1]})*(1-V(ensf)) - 1e-3*(V(ens)<{x[0]})*V(ensf)\nCENSF ensf 0 1n\nRENSFL ensf 0 1G\n"
    a = "RENS ens 0 1G\n"
    assert base.count(a) == 1
    n = base.replace("V(ens)>0.5", "V(ensf)>0.5").replace(a, a + "* T-053 experiment: separate internal comparison\n" + add)
    (OUT / f"netlist_{tag}.cir").write_text(n, encoding="utf-8", newline="\n")
    return tag
def one(name, tag, netfile):
    r = runs[name]
    deck = (ROOT / r["deck"]).read_text(encoding="utf-8")
    deck = deck.replace(".include ../../../../design/pdu_v2.cir", f".include {netfile}")
    m = re.search(r"^\.ic .*$", deck, re.M)
    if netfile != "BASE" and m:
        e = re.search(r"V\(ens\)=(\S+)", m.group(0))
        deck = deck.replace(m.group(0), m.group(0) + f" V(ensf)={e.group(1) if e else 0}")
    f = OUT / f"{name}__{tag}.cir"
    f.write_text(deck, encoding="utf-8", newline="\n")
    log = f.with_suffix(".log"); t0 = time.time()
    try:
        code = subprocess.run([NG, "-b", "-o", log.name, f.name], cwd=OUT, capture_output=True, timeout=LIMIT).returncode
    except subprocess.TimeoutExpired:
        code = -9
    lt = log.read_text(errors="replace") if log.exists() else ""
    names = re.findall(r"^\.meas tran (\S+)", deck, re.M)
    vals = {n: float(x.group(1)) for n in names if (x := re.search(rf"^{n}\s*=\s*([-+0-9.eE]+)", lt, re.M))}
    done = code == 0 and len(vals) == len(names)
    crit = {}
    for k, c in r["criteria"].items():
        crit[k] = None if k not in vals else {"<": vals[k] < c["limit"], "<=": vals[k] <= c["limit"], ">": vals[k] > c["limit"], ">=": vals[k] >= c["limit"]}[c["op"]]
    base_m = r["measures"]
    delta = {k: round(vals[k] - base_m[k], 6) for k in r["criteria"] if k in vals and k in base_m}
    if name not in STUCK:
        log.unlink(missing_ok=True); f.unlink(missing_ok=True)
    return {"scenario": name, "variant": tag, "exit": code, "seconds": round(time.time() - t0, 2), "found": len(vals), "total": len(names), "completed": done, "criteria": crit, "original_pass": r["pass"], "delta_vs_original_criteria_measures": delta, "measures": vals}
rows = []
for kind, x in V:
    tag = netlist(kind, x)
    for name in STUCK + NEIGH:
        rows.append(one(name, tag, f"netlist_{tag}.cir"))
        print(tag, name[:32], rows[-1]["exit"], rows[-1]["seconds"], rows[-1]["completed"], rows[-1]["delta_vs_original_criteria_measures"], flush=True)
(OUT.parent / "variants.json").write_text(json.dumps({"status": "DENEY; ana deck değişmedi; resmi sonuç değil", "netlist_sha256": hashlib.sha256(base.encode()).hexdigest(), "limit_s": LIMIT, "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
