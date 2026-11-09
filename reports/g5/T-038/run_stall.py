#!/usr/bin/env python3
"""T-038: per-corner identified raw evidence of the two F5 stalls. Run from repo root: python reports/g5/T-038/run_stall.py
Each corner's tracked deck runs unchanged for LIMIT_S seconds with an incremental ASCII raw file. Only a decimated CSV and a JSON summary are kept."""
import csv
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-038/stall"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
CORNERS = ("f5_vt11.487_td300ns_ctyp_r200m_l0.8", "f5_vt11.765_td300ns_ctyp_r200m_l0.8")
LIMIT_S = 75
COLS = ("time", "v(ens)", "v(ven)", "v(vin)", "v(q)", "v(ctl)", "v(vraw)", "v(vsafe)", "v(o1)", "i(vm1)")
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT.mkdir(parents=True, exist_ok=True)
ver = subprocess.run([NG, "--version"], capture_output=True, text=True).stdout
ver = next((l.strip("* \r") for l in ver.splitlines() if "ngspice-" in l), "doğrulanamadı")
summary = {}
for c in CORNERS:
    src = ROOT / f"reports/g2/sim/f5/{c}.cir"
    data = src.read_bytes()
    deck = OUT / f"{c}.cir"
    deck.write_bytes(data)
    raw = OUT / f"{c}.raw"; log = OUT / f"{c}.diag.log"
    for f in (raw, log):
        f.unlink(missing_ok=True)
    cmd = [NG, "-b", "-o", log.name, "-r", raw.name, deck.name]
    t0 = time.time()
    try:
        code = subprocess.run(cmd, cwd=OUT, capture_output=True, timeout=LIMIT_S).returncode
    except subprocess.TimeoutExpired:
        code = "timeout"
    took = round(time.time() - t0, 2)
    d = raw.read_bytes()
    he = d.find(b"Values:")
    names = re.findall(r"^\s*\d+\s+(\S+)\s+\S+", d[:he].decode("latin1"), re.M)
    nv = len(names); ix = {m.lower(): k for k, m in enumerate(names)}
    toks = d[he + 7:].split()
    n = len(toks) // (nv + 1)
    g = lambda k, a: float(toks[k * (nv + 1) + 1 + ix[a]])
    W = 3000
    tail = range(n - W, n)
    t = [g(k, "time") for k in tail]
    dt = [b - a for a, b in zip(t, t[1:])]
    def flips(a, th):
        s = [g(k, a) > th for k in tail]
        return sum(1 for x, y in zip(s, s[1:]) if x != y)
    def rng(a):
        v = [g(k, a) for k in tail]
        return [min(v), max(v)]
    kept, nxt = [], 0.0
    for k in range(n):
        tt = g(k, "time")
        if tt >= nxt:
            kept.append(k); nxt = tt + 1e-6
    kept += list(range(n - 300, n))
    with (OUT / f"{c}.wave.csv").open("w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(COLS)
        for k in sorted(set(kept)):
            w.writerow([f"{g(k, a):.12e}" for a in COLS])
    res = {"corner": c, "deck_path": str(src.relative_to(ROOT)).replace("\\", "/"), "deck_sha256": sha(data), "netlist_sha256": sha((ROOT / "design/pdu_v2.cir").read_bytes()), "simulator": ver, "command": " ".join(cmd[1:]), "limit_s": LIMIT_S, "seconds": took, "exit": code, "points": n, "t_last_s": t[-1],
           "last_window_points": W, "dt_min_s": min(dt), "dt_max_s": max(dt), "t_span_of_window_s": t[-1] - t[0], "raw_bytes": len(d), "raw_sha256": sha(d),
           "window_range": {a: rng(a) for a in COLS[1:]}, "sign_flips_in_window": {"ens>0.5": flips("v(ens)", 0.5), "ven>VEN_R(1.0)": flips("v(ven)", 1.0), "ven>VEN_R-VEN_H(0.9)": flips("v(ven)", 0.9), "fault1>0.5": flips("v(fault1)", 0.5), "q>0.5": flips("v(q)", 0.5)}}
    (OUT / f"{c}.stall.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    summary[c] = res
    raw.unlink()
    print(c[6:13], code, took, n, res["t_last_s"], res["dt_min_s"], res["dt_max_s"], res["sign_flips_in_window"], res["window_range"]["v(ens)"], res["window_range"]["v(ven)"])
