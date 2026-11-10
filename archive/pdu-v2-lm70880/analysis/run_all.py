"""Reproduce every G2/G4 calculation, simulation and test with one command.

    python analysis/run_all.py            # all calculations + all 5 ngspice families + pytest
    python analysis/run_all.py --skip-sim # calculations + pytest using the stored sim-results.json

Writes reports/g2/VERIFY.md with exit codes and a summary table. Does NOT run analysis/generate_g1_reports.py.
Solver: PDU_NGSPICE env var (Windows) or `ngspice` on PATH (Linux); default F:\\Spice64\\bin\\ngspice_con.exe.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "reports" / "g2" / "VERIFY.md"

STEPS = [
    ("protection (Stage 2)", [sys.executable, "-m", "analysis.g2.protection"]),
    ("power stage / ILIM / UVLO / input (Stage 3)", [sys.executable, "-m", "analysis.g2.power"]),
    ("loop analytic + ngspice AC (Stage 4)", [sys.executable, "-m", "analysis.g2.loop"]),
    ("N1 phase-OC trip / L(i) (G4 B1)", [sys.executable, "-m", "analysis.g2.n1"]),
    ("stacked tolerance + trim (G4 B4)", [sys.executable, "-m", "analysis.g2.b4"]),
    ("gm / UVLO open assumptions (G4 B5)", [sys.executable, "-m", "analysis.g2.b5"]),
    ("routing inputs (Stage 6)", [sys.executable, "-m", "analysis.g2.routing"]),
    ("BOM v2 / spec / footprint map (Stage 6, G4 C)", [sys.executable, "-m", "analysis.g2.bom"]),
    ("spec <-> BOM <-> SPICE consistency (G4 C3)", [sys.executable, "analysis/check_consistency.py"]),
    ("full-system ngspice families F1-F5 (Stage 5)", [sys.executable, "-m", "analysis.g2.sim_runner"]),
    ("workflow check (W0)", [sys.executable, "scripts/check_workflow.py"]),
    ("pytest (all)", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]),
]


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")   # T-025: never print through the console code page
    skip_sim = "--skip-sim" in argv
    rows = []
    for name, cmd in STEPS:
        if skip_sim and "sim_runner" in " ".join(cmd):
            rows.append((name, "skipped (--skip-sim)", 0.0, ""))
            continue
        t = time.time()
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env={**os.environ, "PYTHONUTF8": "1"})   # T-025: children write UTF-8, decoded as UTF-8
        tail = (p.stdout.strip().splitlines() or [""])[-1][:200]
        rows.append((name, p.returncode, time.time() - t, tail))
        print(f"{name}: exit {p.returncode} ({time.time() - t:.1f} s) {tail}", flush=True)
    sim = json.loads((ROOT / "reports" / "g2" / "sim-results.json").read_text(encoding="utf-8"))
    lines = ["# G2 doğrulama kaydı (run_all)", "",
             f"Tarih: {dt.datetime.now().isoformat(timespec='seconds')}. Komut: `python analysis/run_all.py{' --skip-sim' if skip_sim else ''}`.", "",
             "| Adım | Çıkış kodu | Süre (s) | Son satır |", "|---|---|---:|---|"]
    for name, code, sec, tail in rows:
        lines.append(f"| {name} | {code} | {sec:.1f} | `{tail.replace('|', '/')}` |")
    lines += ["", "## Simülasyon aile özeti (`reports/g2/sim-results.json`)", "", "| Aile | Koşu | Tamamlanan | Kriter PASS |", "|---|---:|---:|---:|"]
    for fam, s in sim["summary"].items():
        lines.append(f"| {fam} | {s['runs']} | {s['completed']} | {s['pass']} |")
    lines += ["", "Simülasyon davranışsal ortalama modeldir; fiziksel kanıt değildir. Ayrıntı: [`SIM-RESULTS.md`](SIM-RESULTS.md)."]
    VERIFY.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    bad = [r for r in rows if r[1] not in (0, "skipped (--skip-sim)")]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
