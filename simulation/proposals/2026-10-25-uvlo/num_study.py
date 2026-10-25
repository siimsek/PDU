#!/usr/bin/env python3
"""UVLO-T5-04 / WP1-T11-01 uniform numerical-sensitivity study (UVLO side) - diagnostic only, nothing adopted.

Predeclared set (not only the aborting decks): every 0 V dip of 10 / 50 / 100 us and the 50 us double dips
(gap 100 us and 30 ms), C3 and O3, typ-ttyp and mbmin-tmin = 20 decks. Each deck is run twice from IDENTICAL copies that
differ ONLY in `.options ... method=` (gear = acceptance setting, trap = trapezoidal); tmax (1 us print / 100 ns step
setting of the deck), reltol 1e-4 and abstol 1n are unchanged. No gmin / edge / per-deck tuning.

Protocol (review): every deck must complete in both methods with zero missing measurements; voltages (peaks, thresholds,
V(T_UV) samples) must agree within 5 mV and edge times / lags within 0.1 us; otherwise the difference is REPORTED and the
worse value of the two methods is the envelope - a failure is retained, never removed. Acceptance pass/fail stays the
verify_uvlo.py result of the committed acceptance run (gear); this study does not change any deck, limit or result.

Usage: python3 num_study.py [-j N] -> results/num-study/num-study.json + logs (exit 0 when it ran; it is data, not a gate)
Behavioural models; numerical convergence check, not physical validation.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent; DECKS = HERE / 'decks'; OUT = HERE / 'results' / 'num-study'
NAMES = [f'{p}{k}-{c}' for p in ('', 'o3-') for c in ('typ-ttyp', 'mbmin-tmin')
         for k in ('dip0v-10us', 'dip0v-50us', 'dip0v-100us', 'dbldip0v-50us-gap100us', 'dbldip0v-50us-gap30ms')]
MEAS_RE = re.compile(r'^\s*([a-z_][a-z0-9_]*)\s*=\s*([-+0-9.eE]+)', re.M)
ERR_RE = re.compile(r'(Timestep too small|simulation\(s\) aborted|singular matrix|Error:.*)', re.I)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
V_TOL, T_TOL = 5e-3, 0.1e-6

def is_time(k):
    return k.startswith(('en_r', 'en_f', 'outa_r', 'outa_f', 'en_lag', 'fet_on', 't_', 'ts_')) or k.endswith(('_t', '_time'))

def run(a):
    name, method, tmp = a
    src = DECKS / f'uvlo-{name}.cir'; t = src.read_text()
    assert t.count('method=gear') == 1, name
    t = t.replace('method=gear', f'method={method}').replace('.include ../', f'.include {HERE}/')
    d = Path(tmp) / method; d.mkdir(parents=True, exist_ok=True); deck = d / src.name; deck.write_text(t)
    log = OUT / f'{name}.{method}.log'; t0 = time.time()
    p = subprocess.run(['ngspice', '-b', '-D', 'ngbehavior=ltpsa', '-o', str(log), deck.name], cwd=d, capture_output=True, timeout=7200)
    txt = log.read_text(errors='replace') if log.exists() else ''
    want = [l.split()[2].lower() for l in t.splitlines() if l.lower().startswith('.meas')]
    m = {k.lower(): float(v) for k, v in MEAS_RE.findall(txt) if k.lower() in want}
    errs = ERR_RE.findall(txt)
    return dict(case=name, method=method, rc=p.returncode, seconds=round(time.time() - t0, 1), completed=p.returncode == 0 and not errs,
                errors=errs[:2], missing=sorted(set(want) - m.keys()), measures=m, source_deck_sha256=sha(src), deck_sha256=sha(deck),
                log=str(log.relative_to(HERE)), log_sha256=sha(log) if log.exists() else None)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('-j', type=int, default=os.cpu_count() or 2); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(a.j) as ex:
        rows = list(ex.map(run, [(n, m, tmp) for n in NAMES for m in ('gear', 'trap')]))
    cmp_ = {}
    for n in NAMES:
        g, t = [next(r for r in rows if r['case'] == n and r['method'] == m) for m in ('gear', 'trap')]
        diffs = []
        for k in sorted(set(g['measures']) & set(t['measures'])):
            dv = abs(g['measures'][k] - t['measures'][k]); tol = T_TOL if is_time(k) else V_TOL
            if dv > tol: diffs.append(dict(meas=k, gear=g['measures'][k], trap=t['measures'][k], diff=dv, tol=tol))
        ok = g['completed'] and t['completed'] and not g['missing'] and not t['missing'] and not diffs
        cmp_[n] = dict(both_complete=g['completed'] and t['completed'], gear_complete=g['completed'], trap_complete=t['completed'],
                       gear_missing=len(g['missing']), trap_missing=len(t['missing']), n_out_of_tol=len(diffs), out_of_tol=diffs[:12],
                       protocol_pass=ok)
        print(f"{n:42s} gear={g['completed']!s:5s} trap={t['completed']!s:5s} miss={len(g['missing'])}/{len(t['missing'])} "
              f"outtol={len(diffs)} {'PASS' if ok else 'NOT-PASS'} {(g['errors'] or t['errors'])[:1]}")
    res = dict(_status='UVLO-T5-04 numerical sensitivity (gear vs trap), diagnostic only; acceptance = verify_uvlo.py (gear)',
               git_head=head, tolerances=dict(voltage=V_TOL, time=T_TOL), cases=NAMES, compare=cmp_, rows=rows,
               n_protocol_pass=sum(v['protocol_pass'] for v in cmp_.values()), n=len(NAMES))
    (OUT / 'num-study.json').write_text(json.dumps(res, indent=1) + '\n')
    print(f"protocol pass {res['n_protocol_pass']}/{res['n']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
