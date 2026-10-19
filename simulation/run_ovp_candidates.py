"""Run isolated native ADI OVP studies without changing the PDU design.

Checks are screening gates, not component SOA/thermal/vendor model approval.
Insufficient pre-fault settling invalidates a case instead of passing its peak.
"""
from pathlib import Path
import json
import math
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
LT = Path(r'C:\Program Files\ADI\LTspice\LTspice.exe')
cases = json.loads((HERE/'global-ovp-candidate-cases.json').read_text())
results = {}
for name, case in cases.items():
    deck = HERE/case['file']
    start = time.time_ns()
    proc = subprocess.run([str(LT), '-b', str(deck)], cwd=HERE,
                          capture_output=True, timeout=60)
    log = deck.with_suffix('.log')
    fresh = log.is_file() and log.stat().st_mtime_ns >= start
    text = log.read_text(errors='replace') if fresh else ''
    measures = {k.lower(): float(v) for k, v in re.findall(
        r'^([A-Za-z][A-Za-z0-9_]*):[^\r\n]*?=\s*([-+\d.eE]+)', text, re.M)}
    required = {'normal','peak','rawpeak','vdspeak','vgs_min','vgs_max',
                'reset','inrush','mos1_i','mos1_p','mos1_e'}
    errors = re.findall(r'^.*(?:error|failed|tolerance relaxed|timestep too small).*$', text, re.M|re.I)
    executed = (proc.returncode == 0 and fresh and not errors and
                required <= measures.keys() and all(math.isfinite(v) for v in measures.values()))
    gates = {'execution': executed}
    if executed:
        # A hot plug at 26V starts in protection; no normal pre-fault rail expected.
        if case['fault'] != 'hotplug':
            gates['pre_fault_rail'] = 10.78 <= measures['normal'] <= 11.30
        gates['protected_peak_12V'] = measures['peak'] <= 12
        gates['reset_rail'] = 10.78 <= measures['reset'] <= 11.30
        # Engineering absolute ceiling, not proof of raw capacitor derating.
        gates['existing_raw_25V_cap_rating'] = measures['rawpeak'] <= 25
        gates['FET_gate_20V_abs_screen'] = measures['vgs_max'] <= 20
    results[name] = dict(execution_pass=executed, gates=gates, measures=measures,
                         screening_pass=all(gates.values()), errors=errors,
                         deck=deck.name)
    print(name, json.dumps(gates), flush=True)
out = dict(scope='Isolated candidate only; approximate MOSFETs and assumed capacitance/ESR; not main schematic or SOA approval',
           cases=results, all_screening_pass=all(r['screening_pass'] for r in results.values()))
(HERE/'global-ovp-candidate-results.json').write_text(json.dumps(out, indent=2))
raise SystemExit(0 if out['all_screening_pass'] else 1)
