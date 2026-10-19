"""Run the exact shared benches; a zero exit code alone is not a passing test."""
from pathlib import Path
import json
import os
import re
import subprocess

HERE = Path(__file__).resolve().parent
NGSPICE = Path(os.environ.get('PDU_NGSPICE', r'F:\Spice64\bin\ngspice_con.exe'))
if not NGSPICE.is_file():
    raise SystemExit(f'ngspice executable missing: {NGSPICE}; set PDU_NGSPICE.')
cases = json.loads((HERE / 'test-cases.json').read_text())
results = {}
for name, case in cases.items():
    logfile = HERE / f'pdu-{name}.ng.log'
    proc = subprocess.run([str(NGSPICE), '-D', 'ngbehavior=ltpsa', '-b', '-o', str(logfile), case['ng_file']],
                          cwd=HERE, capture_output=True, text=True, timeout=60)
    log = logfile.read_text(errors='replace')
    measurements = {k.lower():float(v) for k,v in re.findall(r'^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([-+\d.eE]+)',log,re.M)}
    missing = sorted(set(case['measures'])-measurements.keys())
    errors = re.findall(r'^.*(?:error|aborted|timestep too small|failed).*$' ,log,re.M|re.I)
    ok = proc.returncode == 0 and not missing and not errors
    results[name] = {'execution_pass':ok, 'exit_code':proc.returncode, 'measures':measurements,
                     'missing':missing, 'errors':errors, 'log':logfile.name}
    print(name, 'EXECUTION_PASS' if ok else 'FAIL', measurements, flush=True)
(HERE/'ngspice-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['execution_pass'] for r in results.values()) else 1)
