#!/usr/bin/env python3
"""T-053 recheck: repeatability of the vraw_max_fault outliers and the reason of the two f2_dip exit-1 runs. No new variant.
Run from the repo root after run_t053.py: python reports/g5/T-053/recheck.py   (writes recheck.json)"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "reports/g5/T-053/run"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
sim = json.loads((ROOT / "reports/g2/sim-results.json").read_text(encoding="utf-8"))
runs = {r["name"]: r for r in (sim["runs"] if isinstance(sim["runs"], list) else [dict(name=k, **v) for k, v in sim["runs"].items()])}
CASES = [("f5_vt11.487_td300ns_ctyp_r200m_l1.2", "rc1us", 3), ("f5_vt11.487_td300ns_ctyp_r200m_l1.2", "sch0p3_0p7", 2), ("f2_dip_22V_to_15V_restart", "rc0p05us", 1), ("f2_dip_22V_to_15V_restart", "rc2us", 1)]


def run(name, tag, n):
    deck = (ROOT / runs[name]["deck"]).read_text(encoding="utf-8").replace(".include ../../../../design/pdu_v2.cir", f".include netlist_{tag}.cir")
    m = re.search(r"^\.ic .*$", deck, re.M)
    if m:
        e = re.search(r"V\(ens\)=(\S+)", m.group(0))
        deck = deck.replace(m.group(0), m.group(0) + f" V(ensf)={e.group(1) if e else 0}")
    f = RUN / f"recheck_{name}__{tag}_{n}.cir"
    f.write_text(deck, encoding="utf-8", newline="\n")
    log = f.with_suffix(".log")
    t0 = time.time()
    try:
        p = subprocess.run([NG, "-b", "-o", log.name, f.name], cwd=RUN, capture_output=True, text=True, timeout=180)
        code, err = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        code, err = -9, ""
    text = log.read_text(errors="replace") if log.exists() else ""
    vm = re.search(r"^vraw_max_fault\s*=\s*([-+0-9.eE]+)", text, re.M)
    keep = [l for l in (text + "\n" + err).splitlines() if re.search(r"error|abort|too small|singular|fail", l, re.I)]
    f.unlink(missing_ok=True); log.unlink(missing_ok=True)
    return {"scenario": name, "variant": tag, "repeat": n, "exit": code, "seconds": round(time.time() - t0, 2), "vraw_max_fault": float(vm.group(1)) if vm else None, "error_lines": keep[-6:]}


rows = [run(s, t, i) for s, t, k in CASES for i in range(1, k + 1)]
(ROOT / "reports/g5/T-053/recheck.json").write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
for r in rows:
    print(r["variant"], r["scenario"][:24], r["repeat"], r["exit"], r["seconds"], r["vraw_max_fault"], r["error_lines"][-3:])
