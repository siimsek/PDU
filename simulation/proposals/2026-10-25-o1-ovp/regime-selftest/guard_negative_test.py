#!/usr/bin/env python3
"""Tur-4 P2-T4-01 / P2-T4-02 + Tur-5 P2-T5-01 / P2-T5-02 guard test (no ngspice, nothing written to the package).

Proves the two fail-closed guards added in Tur-4 actually reject incomplete or over-broken inputs:
 A. regime_selftest.synthetic(): a base run missing an injection window, or a missing case run -> None (exit 2 path);
    an injection that also breaks a NON-regime check (O1 global peak 13 V) -> that row selftest_pass=False.
 B. model-compare/rebind_rev3.py, run against MUTATED temporary copies of model-compare.json: a deleted case row,
    a duplicated row, a deleted delta key, a deleted rev3 judge key, a changed rev2 delta value -> exit 2 each;
    the unmodified copy -> exit 0. The real model-compare.json is never touched (M.OUT points to a temp dir).
 C. Tur-5 P2-T5-01 / P2-T5-02 (same harness): a corrupted derived delta `d`, a `d` set where one side is None, a
    corrupted stored rev3 / rev2 `verdict`, a flipped `changed` (model-dependent and model-independent row) -> exit 2;
    a duplicated RAW ng run row in a temp copy of o1ovp-results.json (M.REBIND_RESULTS) -> exit 2. The real
    o1ovp-results.json is never touched.
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
def rebind(mut, mut_res=None):
    d = copy.deepcopy(base); mut(d)
    with tempfile.TemporaryDirectory() as tmp:
        old = M.OUT; M.OUT = Path(tmp); (M.OUT/'model-compare.json').write_text(json.dumps(d))
        if mut_res is not None:  # Tur-5 P2-T5-02: mutated temp copy of the raw results
            rr = copy.deepcopy(res); mut_res(rr); (Path(tmp)/'o1ovp-results.json').write_text(json.dumps(rr))
            M.REBIND_RESULTS = Path(tmp)/'o1ovp-results.json'
        try: runpy.run_path(str(PKG/'model-compare'/'rebind_rev3.py'), run_name='__main__'); code = 0
        except SystemExit as e: code = e.code
        finally:
            M.OUT = old
            if hasattr(M, 'REBIND_RESULTS'): del M.REBIND_RESULTS
    return code
mi = next(i for i, r in enumerate(base['rows']) if not r.get('model_independent') and r['rev3'].get('completed') and r['kind'] != 'reference')
check('B0 unmodified copy -> exit 0', rebind(lambda d: None) == 0)
check('B1 deleted case row -> exit 2', rebind(lambda d: d['rows'].pop(mi)) == 2)
check('B2 duplicated row -> exit 2', rebind(lambda d: d['rows'].append(copy.deepcopy(d['rows'][mi]))) == 2)
check('B3 deleted delta key -> exit 2', rebind(lambda d: d['rows'][mi]['delta'].pop('o1_global_peak')) == 2)
check('B4 deleted rev3 judge key -> exit 2', rebind(lambda d: d['rows'][mi]['rev3'].pop('acc_fail')) == 2)
def b5(d): d['rows'][mi]['delta']['o1_global_peak']['rev2'] = 1.0
check('B5 changed rev2 delta value -> exit 2', rebind(b5) == 2)
# Tur-5 P2-T5-01: derived fields (d, verdict, changed) must be recomputed, not just present
row = base['rows'][mi]; dk = next(k for k, v in row['delta'].items() if v['rev2'] is not None and v['rev3'] is not None)
nk = next(((i, k) for i, r in enumerate(base['rows']) if not r.get('model_independent')
           for k, v in r['delta'].items() if (v['rev2'] is None) != (v['rev3'] is None)), None)
ri = next(i for i, r in enumerate(base['rows']) if r.get('model_independent'))
def c1(d): d['rows'][mi]['delta'][dk]['d'] += 1e-3
check(f'C1 corrupted delta d ({base["rows"][mi]["case"]}/{dk} +1 mV) -> exit 2', rebind(c1) == 2)
def c1b(d): d['rows'][mi]['delta'][dk]['d'] = -d['rows'][mi]['delta'][dk]['d'] - 1.0
check('C1b sign-flipped/offset delta d -> exit 2', rebind(c1b) == 2)
if nk:
    def c2(d): d['rows'][nk[0]]['delta'][nk[1]]['d'] = 0.0
    check(f'C2 d set where one side is None ({base["rows"][nk[0]]["case"]}/{nk[1]}) -> exit 2', rebind(c2) == 2)
def c3(d): s = d['rows'][mi]['rev3']; s['verdict'] = 'FAIL' if s['verdict'] == 'PASS' else 'PASS'
check('C3 corrupted rev3 verdict -> exit 2', rebind(c3) == 2)
def c4(d): s = d['rows'][mi]['rev2']; s['verdict'] = 'FAIL' if s['verdict'] == 'PASS' else 'PASS'
check('C4 corrupted rev2 verdict -> exit 2', rebind(c4) == 2)
def c5(d): d['rows'][mi]['changed'] = not d['rows'][mi]['changed']
check('C5 flipped changed -> exit 2', rebind(c5) == 2)
def c6(d): d['rows'][ri]['changed'] = True
check('C6 changed=True on model-independent row -> exit 2', rebind(c6) == 2)
# Tur-5 P2-T5-02: duplicated RAW ng run row must be rejected before the case-keyed dict merges it
def c7(rr): rr['runs'].append(copy.deepcopy(next(r for r in rr['runs'] if r['engine'] == 'ng' and r['case'] == base['rows'][mi]['case'])))
check('C7 duplicated raw ng run row in o1ovp-results -> exit 2', rebind(lambda d: None, c7) == 2)
def c8(rr):
    i = next(i for i, r in enumerate(rr['runs']) if r['engine'] == 'ng' and r['case'] == base['rows'][mi]['case'])
    rr['runs'].insert(0, copy.deepcopy(rr['runs'][i]))  # duplicate placed FIRST (dict would keep the original last)
check('C8 duplicated raw ng row placed first -> exit 2', rebind(lambda d: None, c8) == 2)
check('C9 unmodified results copy via M.REBIND_RESULTS -> exit 0', rebind(lambda d: None, lambda rr: None) == 0)
print(f"{sum(k for _, k in results)}/{len(results)} guard checks OK")
sys.exit(0 if all(k for _, k in results) else 1)
