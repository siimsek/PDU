#!/usr/bin/env python3
"""Independent verifier for WP1 2026-10-25-o1-ovp (stdlib only). Does NOT trust the runner's verdicts.

  python3 verify_candidate.py [--results o1ovp-results.json]
      1. recomputes sha256 of every input/deck listed in the results and of the baseline files,
         and requires that the baseline files are unchanged versus git HEAD (if git is available);
      2. re-verifies each log's sha256, re-extracts the .meas values from the LOG TEXT itself;
      3. re-applies the UNCHANGED acceptance limits (O1 <= 12.0 V instantaneous - verify_results.py
         L90-91; bus 10.78..11.22 V for the 0.45->4.5 A step - L79; 11 V +/-2 % levels; rev2: normal bus
         <= 11.1605 V (separate from the 11.22 V false-trip test level); FET off
         during the fault; device ratings) to every acceptance case.
      Exit 0 = all acceptance checks pass, 1 = a check failed, 2 = missing/mismatched evidence.
  python3 verify_candidate.py --baseline-regression
      applies the same O1 criterion to the log of the UNMODIFIED baseline deck
      simulation/pdu-efuse-ovp.ng.cir (run by run_o1ovp.py) -> expected to FAIL (~16.89 V), exit 1.
"""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).absolute().parent
SIM = HERE.parent.parent
REPO = SIM.parent
O1_MAX = 12.0
NORMAL_MAX = 11.1605   # rev2 P1-2: normal bus upper limit (static max); separate from the 11.22 V false-trip test level
FALSE_TRIP_TEST = 11.22
MEAS = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)(?::[^\r\n]*?=|\s*=)\s*([-+\d.eE]+)', re.M)
BAD = re.compile(r'(?:error|aborted|failed|tolerance relaxed|timestep too small)', re.I)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def measures(log, deck):
    want = [l.split()[2].lower() for l in Path(deck).read_text().splitlines() if l.lower().startswith('.meas')]
    txt = Path(log).read_text(errors='replace')
    m = {k.lower(): float(v) for k, v in MEAS.findall(txt) if k.lower() in want}
    return m, sorted(set(want) - m.keys()), bool(BAD.search(txt))

def git_unchanged(paths):
    try:
        out = subprocess.run(['git', 'status', '--porcelain', '--', *paths], cwd=REPO, capture_output=True, text=True, timeout=60)
        if out.returncode != 0: return None, out.stderr.strip()
        body = out.stdout.rstrip('\n')  # keep the leading status column (e.g. ' D path')
        return body.strip() == '', body
    except Exception as e:
        return None, str(e)

def rules(kind, m):
    """yield (name, ok, detail) - independent re-implementation of the acceptance limits."""
    lvl = lambda k: (k, 10.78 <= m[k] <= 11.22, f'{m[k]:.6g} V within 11 V +/-2 %')
    nrm = lambda k, w: (f'normal bus <= 11.1605 ({k})', m[k] <= NORMAL_MAX, f'{m[k]:.6g} V ({w})')
    if kind in ('ramp', 'sweep', 'mc-ramp', 'short', 'mc-short'):
        yield 'O1<=12V', m['o1_peak'] <= O1_MAX, f"O1 peak {m['o1_peak']:.6g} V"
        if 'inp_fault_max' in m: yield 'FET off in fault', m['inp_fault_max'] < 0.8, f"INP {m['inp_fault_max']:.3g} V"
        if 'vdsa_max' in m: yield 'VDS(QA)<=60V', m['vdsa_max'] <= 60, f"{m['vdsa_max']:.4g} V"
        if 'vdsb_max' in m: yield 'VDS(QB)<=60V', m['vdsb_max'] <= 60, f"{m['vdsb_max']:.4g} V"
        if 'iinm_max' in m: yield 'TLV3601 Iin<=10mA', m['iinm_max'] <= 10e-3, f"{m['iinm_max']*1e3:.3g} mA"
        for k in ('o1_pre', 'o1_reset', 's2e_reset', 'normal', 'o1_normal'):
            if k in m: yield lvl(k)
        for k in ('o1_pre', 'normal', 'o1_normal'):
            if k in m: yield nrm(k, 'before the fault')
        for k in ('o1_off', 's2e_off'):
            if k in m: yield k, abs(m[k]) < 0.1, f'{m[k]:.4g} V (off < 0.1 V)'
        if 'bus_peak' in m: yield 'U3/U4 IN <= 30 V', m['bus_peak'] <= 30, f"bus {m['bus_peak']:.5g} V"
    elif kind == 'board-average':
        yield 'O1<=12V', m['o1_max'] <= O1_MAX, f"O1 max {m['o1_max']:.6g} V"
        for k in ('bus_avg', 'o1_avg', 's2e_avg'): yield lvl(k)
        yield 'no trip', m['inp_min'] > 4 and m['vgs_min'] > 4.5, f"INP {m['inp_min']:.3g} VGS {m['vgs_min']:.3g}"
        yield 'startup bus <= 11.22', m['bus_max'] <= 11.22, f"{m['bus_max']:.6g} V"
        yield nrm('bus_max', 'startup/static max'); yield nrm('bus_avg', 'static average')
    elif kind == 'step':
        yield 'transient 10.78..11.22', 10.78 <= m['bus_min'] and m['bus_max'] <= 11.22, f"{m['bus_min']:.6g}..{m['bus_max']:.6g} V"
        yield nrm('bus_max', 'load step')
        yield 'no trip', m['inp_min'] > 4 and m['vgs_min'] > 4.5, f"INP {m['inp_min']:.3g} VGS {m['vgs_min']:.3g}"
    elif kind == 'step75':
        yield 'no trip', m['inp_min'] > 4 and m['vgs_min'] > 4.5, f"INP {m['inp_min']:.3g} VGS {m['vgs_min']:.3g}"
        for k in ('o1_final', 's2e_final'): yield lvl(k)
        yield nrm('bus_max', '7.5 A load step')
    elif kind in ('nofalse', 'mc-nofalse'):
        yield 'false-trip test level reached', m['raw_max'] >= FALSE_TRIP_TEST - 1e-3, f"RAW max {m['raw_max']:.6g} V vs {FALSE_TRIP_TEST} V test level"
        yield 'no false trip', m['inp_min'] > 4 and m['vgs_min'] > 4.5, f"RAW max {m['raw_max']:.5g} INP {m['inp_min']:.3g}"
        yield lvl('o1_avg')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--results', default='o1ovp-results.json')
    ap.add_argument('--baseline-regression', action='store_true'); a = ap.parse_args()
    res = json.loads((HERE/a.results).read_text())
    cases = {k: v for k, v in json.loads((HERE/'test-cases-o1ovp.json').read_text()).items() if not k.startswith('_')}
    fails, missing, n = [], [], 0
    if a.baseline_regression:
        r = res.get('baseline_regression') or {}
        log = HERE/r.get('log', 'results/baseline-regression-efuse-ovp.ng.log')
        if not log.exists() or sha(log) != r.get('log_sha256'):
            print('MISSING/MISMATCH baseline regression log'); sys.exit(2)
        m, miss, bad = measures(log, SIM/'pdu-efuse-ovp.ng.cir')
        if miss or bad: print('INCOMPLETE baseline log', miss); sys.exit(2)
        ok = m['o1_peak'] <= O1_MAX
        print(f"baseline simulation/pdu-efuse-ovp.ng.cir: O1_PEAK = {m['o1_peak']:.6g} V vs 12.0 V -> {'PASS' if ok else 'FAIL'}"
              f" (baseline deck sha256 {sha(SIM/'pdu-efuse-ovp.ng.cir')})")
        sys.exit(0 if ok else 1)
    for p, h in res['input_sha256'].items():
        if sha(HERE/p) != h: missing.append(f'input changed since run: {p}')
    for p, h in res['baseline_sha256'].items():
        if sha(SIM/p) != h: missing.append(f'baseline file changed since run: simulation/{p}')
    protected = ['simulation/pdu-current.net', 'hardware/pdu-current-bom.csv', 'simulation/verification-results.json',
                 'simulation/latest-run.json', 'simulation'] + [f'simulation/{p}' for p in res['baseline_sha256']]
    ok_git, detail = git_unchanged([p for p in protected if (REPO/p).exists()])
    if ok_git is False:
        # only changes (untracked or modified proposal files) under simulation/proposals/ are allowed
        bad = [l for l in detail.splitlines() if not l[3:].strip('"').startswith('simulation/proposals/')]
        if bad: missing.append(f'tracked baseline files modified: {bad}')
    elif ok_git is None:
        print('NOTE git status unavailable:', detail)
    runs = [r for r in res['runs'] if r['engine'] == 'ng']
    seen = {r['case'] for r in runs}
    for name, c in cases.items():
        if name not in seen: missing.append(f'no ngspice run for {name}'); continue
    for r in runs:
        c = cases[r['case']]
        log = HERE/r['log']
        if not log.exists() or sha(log) != r['log_sha256']:
            missing.append(f"log missing/mismatch {r['log']}"); continue
        m, miss, bad = measures(log, HERE/r['deck'])
        if miss or bad:
            (missing if c.get('acceptance', True) else []).append(f"{r['case']}: incomplete log {miss} err={bad}"); continue
        if not c.get('acceptance', True) or c['kind'] == 'reference': continue
        for nm, ok, d in rules(c['kind'], m):
            n += 1
            if not ok: fails.append(f"{r['case']}: {nm}: {d}")
    print(f'verify_candidate: {n} acceptance re-checks, {len(fails)} failed, {len(missing)} evidence problems; '
          f"runner label {res.get('label')!r}, finished {res.get('finished')}")
    for f in fails: print('FAIL', f)
    for x in missing: print('MISSING', x)
    sys.exit(2 if missing else (1 if fails else 0))

if __name__ == '__main__':
    main()
