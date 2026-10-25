#!/usr/bin/env python3
"""Tur-3: re-bind the rev3 side of model-compare.json to a NEW clean acceptance run (../o1ovp-results.json) WITHOUT
re-running the rev2 decks and WITHOUT changing model_compare.py (a runner input; changing it would invalidate the run).

Rules (fail closed, exit 2): every stored rev2 log must still match its recorded sha256; for every rev3 row the new run
must be from the same deck (deck_sha256), have the same completed/errors state, EXACTLY the same measures as the stored
row (delta.rev3) and the same judge() result. Only rev3 log/log_sha256, rev3_results_label/sha256 change; the
summary is recomputed with model_compare.summarize (Tur-3 P2-A counter). Tur-4 P2-T4-02: the row set must equal
model_compare.R.CASES exactly and every row's key/measure set must be complete (see the coverage block) - else exit 2.
Tur-5 P2-T5-02: the RAW o1ovp-results run rows are counted before the case-keyed dict is built; a duplicated CASE (or
(engine, case) pair) or a row count != len(CASES) -> exit 2 (a dict would otherwise merge duplicates silently).
Tur-5 P2-T5-01: the DERIVED fields are recomputed and compared, fail closed: every delta `d` must equal rev3 - rev2
(|err| <= D_ABS + D_REL*max(|rev2|,|rev3|,1); None iff one side is None), every stored rev2/rev3 `verdict` must equal
the verdict re-derived exactly as model_compare.main() does (INCOMPLETE / REFERENCE / FAIL if judge() acc_fail else
PASS, judge() re-run on the rev2 log measures and on the new rev3 run measures) and `changed` must equal the
model_compare.main() expression re-evaluated on the recomputed verdicts/deltas; model-independent rows must keep
changed=False, delta={} and verdict MODEL-INDEPENDENT.
Tur-6: P2-T6-01 num() rejects NaN/Inf and the d tolerance test is NaN-safe; P2-T6-02 rev2 completed/errors are
re-derived from the sha-pinned rev2 log (runner rule) instead of trusted; P2-T6-03 raw-row check = M.raw_run_problems().
Usage: python3 model-compare/rebind_rev3.py   -> exit 0 rebound, 2 mismatch (nothing written)
"""
import json, math, sys
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(PKG))
import model_compare as M
f = M.OUT/'model-compare.json'; d = json.loads(f.read_text())
# RES_PATH: the real package results; guard_negative_test.py may point M.REBIND_RESULTS at a mutated temp copy.
RES_PATH = Path(getattr(M, 'REBIND_RESULTS', PKG/'o1ovp-results.json'))
res = json.loads(RES_PATH.read_text())
bad = []
D_ABS, D_REL, CHG = 1e-12, 1e-9, 1e-3  # d tolerance (float re-subtraction); CHG = model_compare.main() 'changed' threshold
# Tur-5 P2-T5-02 / Tur-6 P2-T6-03: RAW rows validated BEFORE the case-keyed dict (shared with model_compare.main()).
bad += M.raw_run_problems(res, M.R.CASES)
new = {r['case']: r for r in res['runs'] if r['engine'] == 'ng'}
def num(x): return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)  # Tur-6 P2-T6-01: NaN/Inf rejected
def want_verdict(s, c, j):  # identical rule to model_compare.main() verdict(); j = judge() recomputed now (or None)
    if not s.get('completed'): return 'INCOMPLETE'
    if c['kind'] == 'reference': return 'REFERENCE'
    if j is None: return None
    return 'FAIL' if j['acc_fail'] else 'PASS'
# Tur-4 P2-T4-02: fail-closed COVERAGE before any per-row check - the stored row set must equal model_compare.R.CASES
# exactly (no missing/extra/duplicate case), kind/acceptance must match the case table, every non-model-independent
# row must carry the full rev2/rev3 key sets, and its delta key set must equal the KEYS present in the rev2 log
# (re-parsed with the runner's MEAS_RE + the source deck's .meas list) or in the new rev3 run, with identical rev2 values.
names = [r.get('case') for r in d['rows']]
if len(names) != len(set(names)): bad.append('duplicate case rows')
if set(names) != set(M.R.CASES): bad.append(f"case set != CASES: missing {sorted(set(M.R.CASES) - set(names))[:5]} extra {sorted(set(names) - set(M.R.CASES))[:5]}")
if set(new) != set(M.R.CASES): bad.append('o1ovp-results ng run set != CASES')
VK = {'completed', 'errors', 'log', 'log_sha256', 'verdict'}; JK = {'acc_checks', 'acc_fail', 'info_fail'}
for r in d['rows']:
    c = M.R.CASES.get(r.get('case'))
    if c is None: continue
    if r.get('kind') != c['kind'] or r.get('acceptance') != c.get('acceptance', True): bad.append(f"kind/acceptance {r['case']}")
    if r.get('model_independent'):
        if '.include ../pdu-o1ovp-behavioral.lib\n' in (M.R.DECKS/c['ng_file']).read_text(): bad.append(f"model_independent but uses model {r['case']}")
        # Tur-5 P2-T5-01: derived fields of a model-independent row are fixed by model_compare.main()
        if r.get('changed') is not False or r.get('delta') != {} or r.get('rev2', {}).get('verdict') != 'MODEL-INDEPENDENT' \
           or r.get('rev3', {}).get('verdict') != 'MODEL-INDEPENDENT': bad.append(f"model_independent derived fields {r['case']}")
        continue
    if 'delta' not in r: bad.append(f"no delta {r['case']}"); continue
    for ver in ('rev2', 'rev3'):
        s = r.get(ver, {}); need = VK | (JK if s.get('completed') and c['kind'] != 'reference' else set())
        if not need <= s.keys(): bad.append(f"{ver} keys {r['case']}: missing {sorted(need - s.keys())}")
    lg = r.get('rev2', {}).get('log')
    if not lg or not (PKG/lg).exists(): bad.append(f"rev2 log absent {r['case']}"); continue
    want = M.R.expected_measures(M.R.DECKS/c['ng_file'])
    txt2 = M.R.read_log(PKG/lg)
    m2 = {k.lower(): float(v) for k, v in M.R.MEAS_RE.findall(txt2) if k.lower() in want}
    # Tur-6 P2-T6-02: rev2 `completed`/`errors` are NOT trusted as stored; re-derived from the sha-pinned rev2 log with the
    # runner's own rule (run_o1ovp.run_deck: no ERR_RE match and every deck .meas present; the exit code is not in the log,
    # so a stored completed=True is additionally required to agree with the log, never the other way round).
    e2 = M.R.ERR_RE.findall(txt2); log_ok = not e2 and set(want) <= m2.keys()
    if r['rev2'].get('completed') is not log_ok: bad.append(f"rev2 completed {r['case']}: stored {r['rev2'].get('completed')} != log-derived {log_ok}")
    if r['rev2'].get('errors') != e2[:1]: bad.append(f"rev2 errors {r['case']}: stored {r['rev2'].get('errors')} != log {e2[:1]}")
    if any(not num(x) for x in m2.values()): bad.append(f"rev2 log non-finite measure {r['case']}")
    w = new.get(r['case'], {}); m3 = w.get('measures', {})
    exp = {k for k in M.KEYS if k in m2 or k in m3}
    if set(r['delta']) != exp: bad.append(f"delta keys {r['case']}: missing {sorted(exp - set(r['delta']))} extra {sorted(set(r['delta']) - exp)}")
    dd = {}  # recomputed d per key (Tur-5 P2-T5-01)
    for k, v in r['delta'].items():
        if not {'rev2', 'rev3', 'd'} <= v.keys(): bad.append(f"delta fields {r['case']}/{k}"); continue
        if v['rev2'] != m2.get(k): bad.append(f"rev2 measure {r['case']}/{k}: {v['rev2']} vs log {m2.get(k)}")
        a, b = v['rev2'], v['rev3']
        if (a is not None and not num(a)) or (b is not None and not num(b)): bad.append(f"delta value type {r['case']}/{k}"); continue
        e = (b - a) if a is not None and b is not None else None; dd[k] = e
        if e is None:
            if v['d'] is not None: bad.append(f"delta d {r['case']}/{k}: {v['d']} but one side is None")
        elif not num(v['d']) or not (abs(v['d'] - e) <= D_ABS + D_REL * max(abs(a), abs(b), 1.0)):  # NaN-safe (Tur-6 P2-T6-01)
            bad.append(f"delta d {r['case']}/{k}: stored {v['d']} != rev3-rev2 {e}")
    j2 = None
    if r['rev2'].get('completed') and c['kind'] != 'reference':
        j2 = M.judge(r['case'], c, m2)
        if any(r['rev2'].get(x) != j2[x] for x in j2): bad.append(f"rev2 verdict detail {r['case']}")
    v2 = want_verdict(r['rev2'], c, j2)
    if r['rev2'].get('verdict') != v2: bad.append(f"rev2 verdict {r['case']}: stored {r['rev2'].get('verdict')} != recomputed {v2}")
    j3 = M.judge(r['case'], c, m3) if w.get('execution_pass') and c['kind'] != 'reference' else None
    v3 = want_verdict(dict(completed=w.get('execution_pass')), c, j3)
    if r['rev3'].get('verdict') != v3: bad.append(f"rev3 verdict {r['case']}: stored {r['rev3'].get('verdict')} != recomputed {v3}")
    chg = v2 != v3 or any(e is not None and abs(e) > CHG for e in dd.values()) or r['rev2'].get('completed') != w.get('execution_pass')
    if r.get('changed') is not chg: bad.append(f"changed {r['case']}: stored {r.get('changed')} != recomputed {chg}")
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
d['rev3_results_label'] = res.get('label'); d['rev3_results_sha256'] = M.sha(RES_PATH)
d['summary'] = M.summarize(d['rows'])
d['rev3_rebound'] = dict(by='model-compare/rebind_rev3.py', script_sha256=M.sha(Path(__file__)), rev3_commit=res['git']['commit'],
                         rule='rev2 rows/logs untouched; rev3 measures/verdicts identical to the previous rows; only rev3 log hashes re-bound')
f.write_text(json.dumps(d, indent=1) + '\n'); print(json.dumps(d['summary']['verdicts']), 'startup_info_trip', d['summary']['startup_info_trip']); sys.exit(0)
