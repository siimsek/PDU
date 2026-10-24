#!/usr/bin/env python3
"""WP1 rev3 P0-03 SOLVER STUDY (diagnostic only - NOT acceptance evidence).

Copies the two acceptance decks that fail with 'timestep too small' (pu_ovp) in the ordinary run
(decks/o1ovp-buck-short-c185-esr12m5-esl2n-typ.ng.cir, ...-c165-...) into this folder, changes ONLY
simulator options (model, circuit, stimulus, measurements and accuracy tolerances reltol/abstol are
unchanged), runs ngspice and records which linear solver the LOG says was used.
Variants that loosen accuracy (larger reltol/abstol/vntol, gmin increase, smoothing caps on PU) are NOT
tried: forbidden by the WP1 rules. A variant that completes here does NOT turn the acceptance decks into
PASS: they remain FAIL in o1ovp-results.json until they complete with the unchanged model and ordinary
options. Any completion here is 'solver-change evidence' and needs an independent cross-check (LTspice
on the owner's PC: pending).
Usage: PDU_NGSPICE=ngspice python3 solver_study.py  ->  ../results/solver-study/*.log + solver-study.json
"""
import hashlib, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent
PKG = HERE.parent
OUT = PKG/'results'/'solver-study'
DECKS = ['buck-short-c185-esr12m5-esl2n-typ', 'buck-short-c165-esr12m5-esl2n-typ']
OPT = '.options reltol=0.0001 abstol=1n method=gear\n'
TRAN = '.tran 100n 80m 0 100n uic\n'
VARIANTS = {   # name: (option lines appended after the ordinary OPT line, tran line)
    'v0-ordinary-sparse': ('', TRAN),
    'v1-klu': ('.options klu\n', TRAN),
    'v2-klu-tmax20n': ('.options klu\n', '.tran 20n 80m 0 20n uic\n'),
    'v3-sparse-tmax20n': ('', '.tran 20n 80m 0 20n uic\n'),
    'v4-klu-trap': ('.options klu method=trap\n', TRAN),
}
MEAS = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)(?::[^\r\n]*?=|\s*=)\s*([-+\d.eE]+)', re.M)
BAD = re.compile(r'(?:error|aborted|failed|tolerance relaxed|timestep too small)', re.I)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def git_head():
    try:
        h = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=PKG, capture_output=True, text=True).stdout.strip()
        d = subprocess.run(['git', 'status', '--porcelain', '--', '.'], cwd=PKG, capture_output=True, text=True).stdout.strip()
        return h, bool(d)
    except Exception as e: return f'unavailable: {e}', None

def one(job):
    deck, var = job; ex, tran = VARIANTS[var]
    src = PKG/'decks'/f'o1ovp-{deck}.ng.cir'; txt = src.read_text()
    assert txt.count(OPT) == 1 and txt.count(TRAN) == 1
    new = txt.replace(TRAN, tran).replace(OPT, OPT + ex)
    new = f'* SOLVER-STUDY COPY ({var}) of decks/{src.name} - diagnostic only, NOT acceptance evidence\n' + new
    f = HERE/f'{deck}.{var}.ng.cir'; f.write_text(new, newline='\n')
    log = OUT/f'{deck}.{var}.ng.log'
    t0 = time.time()
    p = subprocess.run([os.environ.get('PDU_NGSPICE', 'ngspice'), '-D', 'ngbehavior=ltpsa', '-b', '-o', str(log), f.name], cwd=HERE, capture_output=True, timeout=3600)
    t = log.read_text(errors='replace')
    want = [l.split()[2].lower() for l in new.splitlines() if l.lower().startswith('.meas')]
    m = {k.lower(): float(v) for k, v in MEAS.findall(t) if k.lower() in want}
    solver = re.findall(r'Using (.*?) as Direct Linear Solver', t)
    errs = [l for l in t.splitlines() if BAD.search(l)]
    return dict(deck=deck, variant=var, source_deck='decks/' + src.name, source_sha256=sha(src), study_deck=f.name, study_deck_sha256=sha(f),
                options_added=ex.strip(), tran=tran.strip(), log='results/solver-study/' + log.name, log_sha256=sha(log), rc=p.returncode,
                seconds=round(time.time()-t0, 1), solver_reported_in_log=solver, completed=(p.returncode == 0 and not errs and set(want) <= m.keys()),
                errors=errs[:3], missing=sorted(set(want)-m.keys()), measures=m)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head, dirty = git_head()
    jobs = [(d, v) for d in DECKS for v in VARIANTS]
    with ThreadPoolExecutor(int(os.environ.get('JOBS', '5'))) as ex: rs = list(ex.map(one, jobs))
    ng = subprocess.run([os.environ.get('PDU_NGSPICE', 'ngspice'), '-v'], capture_output=True, text=True).stdout.strip().splitlines()
    out = dict(_status='DIAGNOSTIC ONLY - solver-change evidence, NOT acceptance; acceptance decks stay FAIL', git_commit=head, git_dirty_package=dirty,
               ngspice=[l for l in ng if l.strip('* ')][:2], runs=rs)
    (PKG/'results'/'solver-study'/'solver-study.json').write_text(json.dumps(out, indent=1) + '\n')
    for r in rs:
        print(f"{r['deck']:36s} {r['variant']:18s} solver={r['solver_reported_in_log']} completed={r['completed']} {r['seconds']} s "
              f"o1_global={r['measures'].get('o1_global_peak')} o1_peak={r['measures'].get('o1_peak')} err={r['errors'][:1]}")
if __name__ == '__main__': main()
