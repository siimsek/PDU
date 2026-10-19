"""Rebuild/run both engines from a fresh Konnect-exported netlist.

Does not export or modify KiCad sources. Export pdu-current.net with Konnect
first. Returns nonzero for failed electrical acceptance, even if engines ran.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ltspice', default=os.environ.get(
    'PDU_LTSPICE', r'C:\Program Files\ADI\LTspice\LTspice.exe'))
parser.add_argument('--timeout', type=int, default=300,
                    help='Per-deck process deadline; elapsed time is not acceptance')
args = parser.parse_args()
lt = Path(args.ltspice)
if not lt.is_file():
    raise SystemExit(f'LTspice executable missing: {lt}')


def script(name):
    subprocess.run([sys.executable, str(HERE/name)], cwd=HERE, check=True)


script('build_models.py')
script('build_benches.py')
cases = json.loads((HERE/'test-cases.json').read_text())
for name, case in cases.items():
    deck = HERE/case['file']
    started = time.time_ns()
    proc = subprocess.run([str(lt), '-b', str(deck)], cwd=HERE,
                          timeout=args.timeout, capture_output=True)
    log = deck.with_suffix('.log')
    if proc.returncode or not log.exists() or log.stat().st_mtime_ns < started:
        raise SystemExit(f'{name}: LTspice failed or log is stale')
    print(name, 'LTspice finished; acceptance checked below', flush=True)
script('run_ngspice.py')
verdict = subprocess.run([sys.executable, str(HERE/'verify_results.py')], cwd=HERE)
raise SystemExit(verdict.returncode)
