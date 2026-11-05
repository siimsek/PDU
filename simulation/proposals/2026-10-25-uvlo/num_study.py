#!/usr/bin/env python3
"""UVLO-T5-04 / WP1-T11-01 uniform numerical-sensitivity study (UVLO side) - diagnostic only, nothing adopted.

Tur-6 (UVLO-T6-02): (1) measurement kinds come from the .meas SYNTAX (meas_kinds): WHEN / TRIG-TARG / INTEG of a 0/1
indicator -> time (tol 0.1 us); FIND / MAX / MIN / AVG / PP -> voltage (tol 5 mV). The Tur-5 name-prefix rule misclassified
e.g. T_AT_DIP_END (= FIND V(T_UV), a voltage) as a time. (2) --tmax (default 100n) replaces the deck .tran tmax UNIFORMLY for
every deck and both methods (set_tmax); nothing else is changed. (3) provenance: runner SHA-256, git HEAD + package git
status at start and end, full argv. (4) --reanalyse JSON: recompare an earlier run's stored measures with the new kinds
(no simulation). Output dir: results/num-study-tmax<tmax>/ (the Tur-5 results/num-study/ run is kept unchanged).

Predeclared set (not only the aborting decks): every 0 V dip of 10 / 50 / 100 us and the 50 us double dips
(gap 100 us and 30 ms), C3 and O3, typ-ttyp and mbmin-tmin = 20 decks. Each deck is run twice from IDENTICAL copies that
differ ONLY in `.options ... method=` (gear = acceptance setting, trap = trapezoidal); the deck `.tran 100n <stop> 0 1u`
(print step 100 ns, tmax 1 us - NOTE: NOT the review's tmax <= 100 ns; deviation reported), reltol 1e-4 and abstol 1n
are unchanged. No gmin / edge / per-deck tuning.

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
sys.path.insert(0, str(HERE.parent)); import study_integrity as SI
NAMES = [f'{p}{k}-{c}' for p in ('', 'o3-') for c in ('typ-ttyp', 'mbmin-tmin')
         for k in ('dip0v-10us', 'dip0v-50us', 'dip0v-100us', 'dbldip0v-50us-gap100us', 'dbldip0v-50us-gap30ms')]
MEAS_RE = re.compile(r'^\s*([a-z_][a-z0-9_]*)\s*=\s*([-+0-9.eE]+)', re.M)
# abort = solver failure; ngspice 'Error: measure ... out of interval' only means the event did not occur (e.g. EN never
# falls in a ride-through) and is recorded as no_value, compared between methods (Tur-5 fix: b072f63 counted it as abort).
ERR_RE = re.compile(r'(Timestep too small|simulation\(s\) aborted|singular matrix|doAnalyses: .*|run simulation\(s\) aborted)', re.I)
NOEV_RE = re.compile(r'Error: measure\s+([a-z_][a-z0-9_]*)\s+.*out of interval', re.I)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
V_TOL, T_TOL = 5e-3, 0.1e-6

def meas_kinds(deck_text):
    """{meas_name: 'time' | 'voltage'} from the .meas syntax (Tur-6): WHEN, TRIG..TARG and INTEG (of a 0/1 indicator node,
    giving seconds) -> time; FIND / MAX / MIN / AVG / PP / RMS of V(...) -> voltage. Unknown forms raise (fail-closed)."""
    k = {}
    for l in deck_text.splitlines():
        w = l.split()
        if not w or not w[0].lower().startswith('.meas'): continue
        name, op = w[2].lower(), w[3].upper()
        if op in ('WHEN', 'TRIG', 'INTEG'): k[name] = 'time'
        elif op in ('FIND', 'MAX', 'MIN', 'AVG', 'PP', 'RMS') and w[4].upper().startswith('V('): k[name] = 'voltage'
        else: raise ValueError(f'unclassified .meas form: {l.strip()}')
    return k

TRAN_RE = re.compile(r'^(\.tran\s+\S+\s+\S+\s+\S+\s+)(\S+)', re.M | re.I)

def set_tmax(deck_text, tmax):
    """Replace the .tran tmax (4th argument) of the single .tran line by `tmax` (uniform for every deck and method)."""
    assert len(TRAN_RE.findall(deck_text)) == 1, 'expected exactly one .tran line with an explicit tmax'
    return TRAN_RE.sub(lambda m: m.group(1) + tmax, deck_text)

def git(*a):
    return subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True).stdout

def provenance():
    return SI.snapshot(HERE, __file__)

def compare(rows, kinds_of):
    """Gear/Trap comparison uses SHA-verified raw .meas decimal strings (exact inclusive boundaries)."""
    cmp_ = {}
    for n in NAMES:
        g, t = [next(r for r in rows if r['case'] == n and r['method'] == m) for m in ('gear', 'trap')]
        kinds = kinds_of(n); diffs = []; boundaries = []
        gr, tr = SI.raw_measures(g, HERE, MEAS_RE), SI.raw_measures(t, HERE, MEAS_RE)
        for k in sorted(set(g['measures']) & set(t['measures'])):
            if k not in kinds or k not in gr or k not in tr:
                raise ValueError(f'missing kind/raw measurement for {n}:{k}')
            dv, over, equal = SI.compare_printed(gr[k], tr[k], kinds[k])
            tol = SI.LIMITS[kinds[k]]
            if equal:
                boundaries.append(k)  # equality is PASS but numerically resolution-sensitive
            if over:
                diffs.append(dict(meas=k, kind=kinds[k], gear=g['measures'][k], trap=t['measures'][k],
                                  diff=float(dv), diff_exact=str(dv), tol=float(tol)))
        asym = sorted(set(g['no_value']) ^ set(t['no_value']))
        ok = g['completed'] and t['completed'] and not g['missing'] and not t['missing'] and not asym and not diffs
        cmp_[n] = dict(both_complete=g['completed'] and t['completed'], gear_complete=g['completed'], trap_complete=t['completed'],
                       gear_missing=len(g['missing']), trap_missing=len(t['missing']), no_value_asymmetric=asym, n_out_of_tol=len(diffs),
                       out_of_tol_by_kind={x: sum(1 for d in diffs if d['kind'] == x) for x in ('time', 'voltage')},
                       out_of_tol=diffs[:12], n_resolution_sensitive=len(boundaries), resolution_sensitive=boundaries,
                       gear_errors=g['errors'], trap_errors=t['errors'], protocol_pass=ok)
        print(f"{n:42s} gear={g['completed']!s:5s} trap={t['completed']!s:5s} miss={len(g['missing'])}/{len(t['missing'])} asym={len(asym)} "
              f"outtol={len(diffs)} {'PASS' if ok else 'NOT-PASS'} {(g['errors'] or t['errors'])[:1]}")
    return cmp_

def run(a):
    name, method, tmp, tmax, out = a
    src = DECKS / f'uvlo-{name}.cir'; t = src.read_text()
    assert t.count('method=gear') == 1, name
    t = set_tmax(t, tmax).replace('method=gear', f'method={method}').replace('.include ../', f'.include {HERE}/')
    d = Path(tmp) / method; d.mkdir(parents=True, exist_ok=True); deck = d / src.name; deck.write_text(t)
    log = out / f'{name}.{method}.log'; t0 = time.time()
    p = subprocess.run(['ngspice', '-b', '-D', 'ngbehavior=ltpsa', '-o', str(log), deck.name], cwd=d, capture_output=True, timeout=7200)
    txt = log.read_text(errors='replace') if log.exists() else ''
    want = [l.split()[2].lower() for l in t.splitlines() if l.lower().startswith('.meas')]
    mraw = {k.lower(): v for k, v in MEAS_RE.findall(txt) if k.lower() in want}
    m = {k: float(v) for k, v in mraw.items()}
    errs = ERR_RE.findall(txt); noev = sorted({x.lower() for x in NOEV_RE.findall(txt)})
    return dict(case=name, method=method, rc=p.returncode, seconds=round(time.time() - t0, 1), completed=p.returncode == 0 and not errs,
                errors=errs[:2], no_value=sorted(set(want) - m.keys()), no_event=noev,
                missing=sorted(set(want) - m.keys() - set(noev)), measures=m, measures_raw=mraw, source_deck_sha256=sha(src), deck_sha256=sha(deck),
                log=str(log.relative_to(HERE)), log_sha256=sha(log) if log.exists() else None)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('-j', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--tmax', default='100n'); ap.add_argument('--run-id', default=None, help='unique immutable study run label')
    ap.add_argument('--reanalyse', default=None, help='earlier num-study JSON')
    a = ap.parse_args()
    if a.run_id is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', a.run_id):
        ap.error('--run-id must be 1..64 safe ASCII characters')
    kinds_of = lambda n: meas_kinds((DECKS / f'uvlo-{n}.cir').read_text())
    tol = dict(voltage=V_TOL, time=T_TOL)
    if a.reanalyse:
        src = Path(a.reanalyse).absolute(); old = json.loads(src.read_text())
        cmp_ = compare(old['rows'], kinds_of)
        res = dict(_status='UVLO-T6-02 RE-ANALYSIS of stored measures with .meas-syntax kinds (no simulation); diagnostic only',
                   source=str(src.relative_to(HERE)), source_sha256=sha(src), source_git_head=old.get('git_head'),
                   provenance=provenance(), tolerances=tol, cases=NAMES, compare=cmp_,
                   n_protocol_pass=sum(v['protocol_pass'] for v in cmp_.values()), n=len(NAMES))
        dst = src.with_name(src.stem + '-reanalysed-t7-decimal.json')
        if dst.exists(): raise FileExistsError(f'refusing to overwrite historical re-analysis: {dst}')
        dst.write_text(json.dumps(res, indent=1) + '\n')
        print(f"re-analysis protocol pass {res['n_protocol_pass']}/{res['n']} -> {dst.relative_to(HERE)}"); return 0
    suffix = f'-{a.run_id}' if a.run_id else ''
    out = HERE / 'results' / f'num-study-tmax{a.tmax}{suffix}'
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f'refusing to overwrite historical study outputs: {out}; pass a fresh --run-id')
    out.mkdir(parents=True, exist_ok=True)
    p0 = provenance()
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(a.j) as ex:
        rows = list(ex.map(run, [(n, m, tmp, a.tmax, out) for n in NAMES for m in ('gear', 'trap')]))
    cmp_ = compare(rows, kinds_of)
    p1 = provenance()
    res = dict(_status=f'UVLO-T6-02 numerical sensitivity (gear vs trap, tmax {a.tmax} uniform), diagnostic only; acceptance = verify_uvlo.py (gear)',
               git_head=p0['git_head'], provenance_start=p0, provenance_end=p1,
               provenance_consistent=SI.consistent(p0, p1, rows, HERE, out),
               tmax=a.tmax, tolerances=tol, cases=NAMES, compare=cmp_, rows=rows,
               n_protocol_pass=sum(v['protocol_pass'] for v in cmp_.values()), n=len(NAMES))
    (out / 'num-study.json').write_text(json.dumps(res, indent=1) + '\n')
    print(f"protocol pass {res['n_protocol_pass']}/{res['n']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
