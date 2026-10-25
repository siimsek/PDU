#!/usr/bin/env python3
"""Tur-3: re-bind the rev3 side of model-compare.json to a NEW clean acceptance run (../o1ovp-results.json) WITHOUT
re-running the rev2 decks and WITHOUT changing model_compare.py (a runner input; changing it would invalidate the run).

Rules (fail closed, exit 2): every stored rev2 log must still match its recorded sha256; for every rev3 row the new run
must be from the same deck (deck_sha256), have the same completed/errors state, EXACTLY the same measures as the stored
row (delta.rev3) and the same judge() result. Only rev3 log/log_sha256, rev3_results_label/sha256 change; the
summary is recomputed with model_compare.summarize (Tur-3 P2-A counter).
Usage: python3 model-compare/rebind_rev3.py   -> exit 0 rebound, 2 mismatch (nothing written)
"""
import json, sys
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PKG))
import model_compare as M
f = M.OUT/'model-compare.json'; d = json.loads(f.read_text())
res = json.loads((PKG/'o1ovp-results.json').read_text())
new = {r['case']: r for r in res['runs'] if r['engine'] == 'ng'}
bad = []
for r in d['rows']:
    if r.get('model_independent'): continue
    o2 = r['rev2']
    if o2.get('log') and M.sha(PKG/o2['log']) != o2['log_sha256']: bad.append(f"rev2 log sha {r['case']}")
    w = new.get(r['case'])
    if not w: bad.append(f"missing {r['case']}"); continue
    c = M.R.CASES[r['case']]
    if w['deck_sha256'] != M.sha(M.R.DECKS/c['ng_file']): bad.append(f"deck {r['case']}")
    if w['execution_pass'] != r['rev3']['completed'] or w['errors'][:1] != r['rev3']['errors']: bad.append(f"state {r['case']}")
    for k, v in r['delta'].items():
        if w['measures'].get(k) != v['rev3']: bad.append(f"measure {r['case']}/{k}: {v['rev3']} -> {w['measures'].get(k)}")
    if w['execution_pass'] and c['kind'] != 'reference':
        j = M.judge(r['case'], c, w['measures'])
        if any(r['rev3'].get(x) != j[x] for x in j): bad.append(f"verdict detail {r['case']}")
if bad: print('rebind_rev3: refused:', bad[:10], len(bad)); sys.exit(2)
for r in d['rows']:
    if r.get('model_independent'): continue
    w = new[r['case']]; r['rev3']['log'] = w['log']; r['rev3']['log_sha256'] = w['log_sha256']
d['rev3_results_label_previous'] = d.get('rev3_results_label'); d['rev3_results_sha256_previous'] = d.get('rev3_results_sha256')
d['rev3_results_label'] = res.get('label'); d['rev3_results_sha256'] = M.sha(PKG/'o1ovp-results.json')
d['summary'] = M.summarize(d['rows'])
d['rev3_rebound'] = dict(by='model-compare/rebind_rev3.py', script_sha256=M.sha(Path(__file__)), rev3_commit=res['git']['commit'],
                         rule='rev2 rows/logs untouched; rev3 measures/verdicts identical to the previous rows; only rev3 log hashes re-bound')
f.write_text(json.dumps(d, indent=1) + '\n'); print(json.dumps(d['summary']['verdicts']), 'startup_info_trip', d['summary']['startup_info_trip']); sys.exit(0)
