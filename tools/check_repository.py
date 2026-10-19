"""Review documentation and saved checkpoint evidence, without running SPICE.

Never opens/parses/modifies KiCad source files. Electrical failures remain
explicit findings; repository consistency is a separate result.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from calculate import calculate
from simulation.project_inputs import load_inputs

ROOT = Path(__file__).resolve().parent.parent
errors = []
required = ['PDU.kicad_pro','PDU.kicad_sch','PDU.kicad_pcb','fp-lib-table',
            'sym-lib-table','PDU_schematic_finished.png','PDU_schematic_finished.pdf',
            'docs/PROJECT-STATE.md','docs/REVIEW-CHECKLIST.md','docs/REPOSITORY.md',
            'hardware/lib/LICENSE-KiCad.md','hardware/lib/CC-BY-SA-4.0.txt']
errors += [f'Missing required file: {p}' for p in required if not (ROOT/p).is_file()]

docs = [p for p in ROOT.rglob('*.md')
        if not any(part in {'.git','.history','__pycache__'} for part in p.parts)
        and 'docs/archive' not in p.relative_to(ROOT).as_posix()]
links_checked = 0
for p in docs:
    text = p.read_text(encoding='utf-8-sig')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        target = target.strip().strip('<>')
        if not target or target.startswith(('#','http:','https:','mailto:')):
            continue
        target = target.split('#')[0]
        links_checked += 1
        if not (p.parent/target).exists():
            errors.append(f'Broken link: {p.relative_to(ROOT)} -> {target}')

result = json.loads((ROOT/'simulation/verification-results.json').read_text())
attempt_path = ROOT/'simulation/latest-run.json'
if attempt_path.is_file():
    attempt = json.loads(attempt_path.read_text())
    if attempt.get('status')!='completed':
        errors.append('Latest simulation attempt is incomplete; old acceptance report is historical')
    elif attempt.get('export_sha256')!=result['artifact_sha256']['pdu-current.net']:
        errors.append('Latest simulation attempt does not match the saved acceptance report')
for name, expected in result['artifact_sha256'].items():
    path = ROOT/'simulation'/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        errors.append(f'Saved simulation artifact hash mismatch: {name}')
    staged = subprocess.run(['git','show',f':simulation/{name}'],cwd=ROOT,capture_output=True)
    if staged.returncode==0 and hashlib.sha256(staged.stdout).hexdigest()!=expected:
        errors.append(f'Git index simulation artifact hash mismatch: {name}; check line-ending attributes')
rows = list(csv.DictReader((ROOT/'hardware/pdu-current-bom.csv').open(encoding='utf-8',newline='')))
try:
    load_inputs()
    calculation = calculate()
    if calculation['inputs']['export_sha256']!=result['artifact_sha256']['pdu-current.net']:
        errors.append('Calculator export source differs from saved simulation source')
    summary_path = ROOT/'hardware/calculation-summary.json'
    if not summary_path.is_file() or json.loads(summary_path.read_text(encoding='utf-8'))!=calculation:
        errors.append('Calculation summary is missing or stale; regenerate with calculate.py --output')
    for name,expected in [('hardware/pdu-current-bom.csv',calculation['inputs']['bom_sha256']),
                          ('hardware/validation/c5750/vendor-ac-summary.json',calculation['output_bank']['vendor_summary_sha256'])]:
        staged = subprocess.run(['git','show',f':{name}'],cwd=ROOT,capture_output=True)
        if staged.returncode==0 and hashlib.sha256(staged.stdout).hexdigest()!=expected:
            errors.append(f'Git index calculation source hash mismatch: {name}')
except (ValueError,KeyError) as exc:
    errors.append(f'Calculation/BOM source mismatch: {exc}')
refs = [r['Reference'] for r in rows]
if len(rows)!=73 or len(set(refs))!=73 or any(r.endswith('?') for r in refs):
    errors.append('Canonical BOM reference count/uniqueness/alias check failed')
for i in range(1,9):
    row = next((r for r in rows if r['Reference']==f'COUT{i}'),{})
    if row.get('MPN')!='C5750X7S2A226M280KB' or row.get('Voltage')!='100V':
        errors.append(f'COUT{i} selection metadata mismatch')
for i in (1,2):
    row = next((r for r in rows if r['Reference']==f'RIMON{i}'),{})
    if row.get('Value')!='806' or row.get('MPN')!='ERA3AEB8060V':
        errors.append(f'RIMON{i} metadata mismatch')

report = dict(repository_consistent=not errors, errors=errors,
              local_document_links_checked=links_checked, bom_rows=len(rows),
              missing_MPN=sum(not r.get('MPN') for r in rows),
              saved_engine_runs=result['engine_runs'],
              saved_acceptance_passed=result['passed'],
              saved_acceptance_failed=result['failed'],
              electrical_acceptance_passed=result['failed']==0,
              scope='Saved-artifact/repository review only; no new simulation, ERC, DRC or hardware test')
print(json.dumps(report,indent=2,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
