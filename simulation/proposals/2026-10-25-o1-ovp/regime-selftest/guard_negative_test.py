#!/usr/bin/env python3
"""Tur-4 P2-T4-01 / P2-T4-02 guard test (no ngspice, nothing written to the package).

Proves the two fail-closed guards added in Tur-4 actually reject incomplete or over-broken inputs:
 A. regime_selftest.synthetic(): a base run missing an injection window, or a missing case run -> None (exit 2 path);
    an injection that also breaks a NON-regime check (O1 global peak 13 V) -> that row selftest_pass=False.
 B. model-compare/rebind_rev3.py, run against MUTATED temporary copies of model-compare.json: a deleted case row,
    a duplicated row, a deleted delta key, a deleted rev3 judge key, a changed rev2 delta value -> exit 2 each;
    the unmodified copy -> exit 0. The real model-compare.json is never touched (M.OUT points to a temp dir).
Exit 0 = every guard behaved as expected; 1 otherwise.
"""
import copy, json, runpy, sys, tempfile
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PKG)); sys.path.insert(0, str(PKG/'model-compare'))
import regime_selftest as S
import model_compare as M
results = []
def check(label, ok): results.append((label, bool(ok))); print(('OK  ' if ok else 'BAD ') + label)

res = json.loads((PKG/'o1ovp-results.json').read_text())
rows = S.synthetic(copy.deepcopy(res)); check('A0 unmodified -> 12 rows, all pass', rows and len(rows) == 12 and all(r['selftest_pass'] for r in rows))
r1 = copy.deepcopy(res)
for r in r1['runs']:
    if r['engine'] == 'ng' and r['case'] == S.CASES[0]: r['measures'].pop('inp_recov_min')
check('A1 missing recovery window -> None', S.synthetic(r1) is None)
r2 = copy.deepcopy(res); r2['runs'] = [r for r in r2['runs'] if not (r['engine'] == 'ng' and r['case'] == S.CASES[1])]
try: v = S.synthetic(r2)
except KeyError: v = None
check('A2 missing case run -> None/KeyError', v is None)
saved = dict(S.SYN); S.SYN['pre-inp-low'] = {'inp_pre_min': 1.0, 'o1_global_peak': 13.0}
rows3 = S.synthetic(copy.deepcopy(res)); S.SYN.clear(); S.SYN.update(saved)
check('A3 injection that also breaks O1 global peak -> that row FAILS', rows3 and not all(r['selftest_pass'] for r in rows3 if r['injection'] == 'pre-inp-low')
      and all(r['selftest_pass'] for r in rows3 if r['injection'] != 'pre-inp-low'))

base = json.loads((M.OUT/'model-compare.json').read_text())
def rebind(mut):
    d = copy.deepcopy(base); mut(d)
    with tempfile.TemporaryDirectory() as tmp:
        old = M.OUT; M.OUT = Path(tmp); (M.OUT/'model-compare.json').write_text(json.dumps(d))
        try: runpy.run_path(str(PKG/'model-compare'/'rebind_rev3.py'), run_name='__main__'); code = 0
        except SystemExit as e: code = e.code
        finally: M.OUT = old
    return code
mi = next(i for i, r in enumerate(base['rows']) if not r.get('model_independent') and r['rev3'].get('completed') and r['kind'] != 'reference')
check('B0 unmodified copy -> exit 0', rebind(lambda d: None) == 0)
check('B1 deleted case row -> exit 2', rebind(lambda d: d['rows'].pop(mi)) == 2)
check('B2 duplicated row -> exit 2', rebind(lambda d: d['rows'].append(copy.deepcopy(d['rows'][mi]))) == 2)
check('B3 deleted delta key -> exit 2', rebind(lambda d: d['rows'][mi]['delta'].pop('o1_global_peak')) == 2)
check('B4 deleted rev3 judge key -> exit 2', rebind(lambda d: d['rows'][mi]['rev3'].pop('acc_fail')) == 2)
def b5(d): d['rows'][mi]['delta']['o1_global_peak']['rev2'] = 1.0
check('B5 changed rev2 delta value -> exit 2', rebind(b5) == 2)
print(f"{sum(k for _, k in results)}/{len(results)} guard checks OK")
sys.exit(0 if all(k for _, k in results) else 1)
