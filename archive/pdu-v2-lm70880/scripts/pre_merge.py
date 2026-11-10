"""Pre-merge gate: every check must exit 0 before a PR is merged (BUILDER rule, WORKFLOW kural 6).

    python scripts/pre_merge.py                 # pytest + check_workflow + check_consistency
    python scripts/pre_merge.py --schematic B1 B2   # + schematic blocks vs spec (needs KiCad 10 kicad-cli)

Added after PR #33 was merged while `check_workflow | tail -1` hid a non-zero exit code.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")   # T-025: the Windows console code page turned "ı" into a 0xFD byte
    argv = list(sys.argv[1:] if argv is None else argv)
    steps = [
        ("pytest", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]),
        ("check_workflow", [sys.executable, "scripts/check_workflow.py"]),
        ("check_consistency", [sys.executable, "analysis/check_consistency.py"]),
    ]
    if "--schematic" in argv:
        blocks = [a for a in argv if a != "--schematic"]
        steps.append(("schematic " + " ".join(blocks), [sys.executable, "analysis/check_consistency.py", "--schematic", *blocks]))
    bad = []
    for name, cmd in steps:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env={**os.environ, "PYTHONUTF8": "1"})
        last = (p.stdout.strip().splitlines() or [""])[-1]
        print(f"[{'OK' if p.returncode == 0 else 'FAIL'}] {name}: {last[:160]}")
        if p.returncode != 0:
            bad.append(name)
    print("pre_merge:", "PASS" if not bad else "FAIL -> " + ", ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
