#!/usr/bin/env python3
"""WP1 rev3 model-revision regression: behavioral model rev2 (OLD, `ov` node collided with pin `OV`) vs rev3 (NEW, `ovs`).

Only the model file differs. For every ngspice case in ../test-cases-o1ovp.json the CURRENT deck (decks/*.ng.cir, i.e. the
same circuit/stimulus/options/.meas as the rev3 acceptance run) is copied to a temporary directory with exactly ONE line
changed: `.include ../pdu-o1ovp-behavioral.lib` -> the unchanged rev2 copy `pdu-o1ovp-behavioral-rev2.lib` (this folder);
the other relative includes are rewritten to absolute paths so the copy runs outside decks/. The temporary decks are
not committed (deterministic: source deck sha256 + this rule). rev3 values are read from ../o1ovp-results.json (the rev3
acceptance run, which must be from the same deck set: deck sha256 checked). Both sets are judged with the SAME runner
rules (run_o1ovp.evaluate). Diagnostic/regression evidence only; acceptance is decided by run_o1ovp.py + verify_candidate.py.

Usage: PDU_NGSPICE=/usr/bin/ngspice python3 model_compare.py [--jobs N]
  -> ../results/model-compare/rev2/*.ng.log + ../results/model-compare/model-compare.json
Exit 0 = comparison complete (differences are data, not errors), 2 = rev3 results missing / deck mismatch.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent; SIM = PKG.parent.parent
sys.path.insert(0, str(PKG))
import run_o1ovp as R  # same evaluate()/regex/measure extraction as the acceptance runner
OUT = PKG/'results'/'model-compare'
OLD = HERE/'pdu-o1ovp-behavioral-rev2.lib'
KEYS = ['o1_peak', 'o1_global_peak', 'bus_peak', 'raw_peak', 'trip_raw', 'off_raw', 'normal', 'o1_normal', 'bus_normal_max',
        'bus_pre_max', 'o1_pre', 'inp_pre_min', 'vgs_pre_min', 'bus_recov_max', 'inp_recov_min', 'vgs_recov_min', 'o1_reset',
        'info_startup_inp_min', 'info_startup_vgs_fall_t', 'inp_min', 'vgs_min', 'bus_max', 'raw_max', 'o1_max', 'vdsa_max', 'vdsb_max']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def judge(name, c, m):
    out = []
    try: R.evaluate(name, c, m, lambda n, ok, d: out.append((n, bool(ok), d)))
    except KeyError as e: out.append((f'missing measurement {e}', False, 'KeyError'))
    acc = [x for x in out if R.category(c, x[0]) == 'acceptance']
    return dict(acc_checks=len(acc), acc_fail=[f'{n}: {d}' for n, ok, d in acc if not ok],
                info_fail=[f'{n}: {d}' for n, ok, d in out if R.category(c, n) != 'acceptance' and not ok])

def run_old(job):
    name, c, tmp = job
    src = R.DECKS/c['ng_file']; t = src.read_text()
    inc = '.include ../pdu-o1ovp-behavioral.lib\n'
    if inc not in t:  # baseline-reference decks do not use the O1OVP model -> model-independent, not re-run
        return dict(case=name, model_independent=True)
    assert t.count(inc) == 1, name
    new = t.replace(inc, f'.include {OLD}\n').replace('.include ../../../', f'.include {SIM}/').replace('.include ../', f'.include {PKG}/')
    d = Path(tmp)/c['ng_file']; d.write_text(new)
    log = OUT/'rev2'/f'{name}.ng.log'
    r = R.run_deck('ng', os.environ['PDU_NGSPICE'], d, log, Path(tmp))
    r['log'] = str(log.relative_to(PKG)); r.update(case=name, source_deck='decks/' + src.name, source_sha256=sha(src), tmp_deck_sha256=sha(d))
    return r

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2); a = ap.parse_args()
    res = json.loads((PKG/'o1ovp-results.json').read_text())
    new = {r['case']: r for r in res['runs'] if r['engine'] == 'ng'}
    bad = [n for n, c in R.CASES.items() if n not in new or new[n]['deck_sha256'] != sha(R.DECKS/c['ng_file'])]
    if bad: print('model_compare: rev3 results missing or from other decks:', bad[:5]); return 2
    (OUT/'rev2').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(max(1, a.jobs)) as ex:
        old = {r['case']: r for r in ex.map(run_old, [(n, c, tmp) for n, c in R.CASES.items()])}
    rows = []
    for n, c in R.CASES.items():
        o, w = old[n], new[n]
        if o.get('model_independent'):
            rows.append(dict(case=n, kind=c['kind'], acceptance=c.get('acceptance', True), model_independent=True, changed=False,
                             rev2=dict(verdict='MODEL-INDEPENDENT'), rev3=dict(verdict='MODEL-INDEPENDENT'), delta={}))
            continue
        row = dict(case=n, kind=c['kind'], acceptance=c.get('acceptance', True),
                   rev2=dict(completed=o['execution_pass'], errors=o['errors'][:1], log=o['log'], log_sha256=o['log_sha256']),
                   rev3=dict(completed=w['execution_pass'], errors=w['errors'][:1], log=w['log'], log_sha256=w['log_sha256']))
        if c['kind'] != 'reference':
            if o['execution_pass']: row['rev2'].update(judge(n, c, o['measures']))
            if w['execution_pass']: row['rev3'].update(judge(n, c, w['measures']))
        row['delta'] = {k: dict(rev2=o['measures'].get(k), rev3=w['measures'].get(k),
                                d=(w['measures'][k] - o['measures'][k]) if k in o['measures'] and k in w['measures'] else None)
                        for k in KEYS if k in o['measures'] or k in w['measures']}
        def verdict(s):
            if not s['completed']: return 'INCOMPLETE'
            if c['kind'] == 'reference': return 'REFERENCE'
            return 'FAIL' if s['acc_fail'] else 'PASS'
        row['rev2']['verdict'] = verdict(row['rev2']); row['rev3']['verdict'] = verdict(row['rev3'])
        row['changed'] = row['rev2']['verdict'] != row['rev3']['verdict'] or any(
            v['d'] is not None and abs(v['d']) > 1e-3 for v in row['delta'].values()) or row['rev2']['completed'] != row['rev3']['completed']
        rows.append(row)
    accs = [r for r in rows if r['acceptance'] and r['kind'] != 'reference' and not r.get('model_independent')]
    def mx(ver, key):
        v = [(r['delta'][key][ver], r['case']) for r in accs if r[ver]['completed'] and r['delta'].get(key, {}).get(ver) is not None]
        return max(v) if v else None
    summ = dict(cases=len(rows), acceptance_cases=len(accs),
                verdicts={ver: {v: sum(r[ver]['verdict'] == v for r in accs) for v in ('PASS', 'FAIL', 'INCOMPLETE')} for ver in ('rev2', 'rev3')},
                changed_verdict=[dict(case=r['case'], rev2=r['rev2']['verdict'], rev3=r['rev3']['verdict']) for r in rows if r['rev2']['verdict'] != r['rev3']['verdict']],
                changed_values=sum(r['changed'] for r in rows),
                o1_global_max={ver: mx(ver, 'o1_global_peak') for ver in ('rev2', 'rev3')},
                startup_info_trip={ver: sorted(r['case'] for r in accs if any('startup' in x for x in r[ver].get('info_fail', []))) for ver in ('rev2', 'rev3')})
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=PKG, capture_output=True, text=True).stdout.strip()
    out = dict(_status='MODEL-REVISION REGRESSION (rev2 vs rev3 behavioral model) - diagnostic; acceptance = run_o1ovp.py + verify_candidate.py',
               change='O1OVP_TPS48000 internal node ov -> ovs (case-insensitive collision with pin OV removed); nothing else',
               old_lib='model-compare/pdu-o1ovp-behavioral-rev2.lib', old_lib_sha256=sha(OLD), new_lib_sha256=sha(PKG/'pdu-o1ovp-behavioral.lib'),
               rev3_results_label=res.get('label'), rev3_results_sha256=sha(PKG/'o1ovp-results.json'), git_commit=head, summary=summ, rows=rows)
    (OUT/'model-compare.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(summ, indent=1))
    return 0

if __name__ == '__main__':
    sys.exit(main())
