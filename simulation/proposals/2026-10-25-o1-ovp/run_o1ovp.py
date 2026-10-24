#!/usr/bin/env python3
"""WP1 2026-10-25-o1-ovp runner (hybrid global OVP, O1 port). Python stdlib only.

Usage (inside the repo tree; decks in ./decks include ../../../pdu-*.lib|inc):
  PDU_NGSPICE=/usr/bin/ngspice [PDU_LTSPICE=<LTspice exe>] python3 run_o1ovp.py
         [--only SUBSTR] [--jobs N] [--label TEXT] [--out FILE] [--no-regression]
LTspice is optional: if PDU_LTSPICE is unset/missing it is SKIPPED and reported (not faked).
Also runs the UNMODIFIED baseline deck ../../pdu-efuse-ovp.ng.cir as a regression (it is expected
to violate the O1 12 V limit, ~16.89 V); its log goes to ./results, the baseline dir is not written.
Exit: 2 incomplete (ngspice missing, a deck did not run/converge, a measure missing, subset run);
      1 an ACCEPTANCE check failed; 0 otherwise. 'info' and 'tracking' checks never change the exit
      code but are printed. Limits are the baseline's (verify_results.py) and are NOT relaxed.
"""
import argparse, hashlib, json, os, platform, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from math import isfinite
from pathlib import Path

HERE = Path(__file__).absolute().parent
DECKS = HERE/'decks'
SIM = HERE.parent.parent
CASES = {k: v for k, v in json.loads((HERE/'test-cases-o1ovp.json').read_text()).items() if not k.startswith('_')}
META = json.loads((HERE/'test-cases-o1ovp.json').read_text()).get('_meta', {})
MEAS_RE = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)(?::[^\r\n]*?=|\s*=)\s*([-+\d.eE]+)', re.M)
ERR_RE = re.compile(r'^.*(?:error|aborted|failed|tolerance relaxed|timestep too small).*$', re.M | re.I)
VDS_MAX = 60.0        # CSD18540Q5B VDS abs max, SLPS488B p1/p3
IIN_MAX = 10e-3       # TLV3601 input current abs max, SNOSDB1E 6.1
VCC_REC_MAX = 5.5     # TLV3601 recommended VCC max, SNOSDB1E 6.3
INP_L_MAX = 0.8       # TPS48000 V(INP_L) guaranteed low threshold min, SLUSEZ1B 5.5
U34_VIN_ABS = 30.0    # TPS259824 IN abs max, SLVSEI3D 6.1
O1_MAX = 12.0         # O1 instantaneous limit (bom.csv L18, verify_results.py L90-91)
NORMAL_MAX = 11.1605  # normal bus/port upper limit = static max (owner hard criterion, rev2 P1-2)
FALSE_TRIP_TEST = 11.22  # OVP false-trip TEST level (+2 % band edge) - stimulus level, not a normal-bus limit
IST = timezone(timedelta(hours=3), 'Europe/Istanbul')
BASELINE_REG = 'pdu-efuse-ovp.ng.cir'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now_ist(): return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %z (Europe/Istanbul)')
def read_log(p):
    b = Path(p).read_bytes()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'): return b.decode('utf-16')
    if len(b) > 4 and b[1:2] == b'\x00' and b[3:4] == b'\x00': return b.decode('utf-16-le', errors='replace')
    return b.decode('utf-8', errors='replace')

def expected_measures(deck):
    return [l.split()[2].lower() for l in Path(deck).read_text().splitlines() if l.lower().startswith('.meas')]

def tool_versions(exe):
    v = {'python': sys.version.split()[0], 'platform': platform.platform()}
    if exe.get('ng'):
        try:
            out = subprocess.run([exe['ng'], '-v'], capture_output=True, text=True, timeout=60)
            v['ngspice'] = [l for l in (out.stdout + out.stderr).strip().splitlines() if l.strip('* ')][:2]
        except Exception as e: v['ngspice'] = f'unavailable: {e}'
        try: v['ngspice_sha256'] = sha(exe['ng'])
        except Exception: pass
    if exe.get('lt'):
        v['ltspice_path'] = exe['lt']
        v['ltspice_version_declared'] = os.environ.get('PDU_LTSPICE_VERSION', 'not declared (LTspice has no CLI version flag)')
        try: v['ltspice_sha256'] = sha(exe['lt'])
        except Exception as e: v['ltspice_sha256'] = f'unavailable: {e}'
    else:
        v['ltspice'] = 'SKIPPED: PDU_LTSPICE not set or file missing'
    return v

def run_deck(engine, exe, deck, log, cwd):
    t0 = time.time()
    try:
        if engine == 'lt':
            p = subprocess.run([exe, '-b', deck.name], cwd=cwd, capture_output=True, timeout=3600)
            src = deck.with_suffix('.log')
            if src.exists(): log.write_bytes(src.read_bytes()); src.unlink()
        else:
            p = subprocess.run([exe, '-D', 'ngbehavior=ltpsa', '-b', '-o', str(log), deck.name], cwd=cwd, capture_output=True, timeout=3600)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 'timeout'
    dt = time.time() - t0
    text = read_log(log) if log.exists() else ''
    want = expected_measures(deck)
    meas = {k.lower(): float(v) for k, v in MEAS_RE.findall(text) if k.lower() in want}
    errs = ERR_RE.findall(text)
    ok = rc == 0 and not errs and set(want) <= meas.keys()
    return dict(engine=engine, returncode=rc, seconds=round(dt, 1), deck_sha256=sha(deck),
                log=str(log.relative_to(HERE)), log_sha256=sha(log) if log.exists() else None,
                execution_pass=ok, missing=sorted(set(want) - meas.keys()), errors=errs[:4], measures=meas)

def run_one(engine, exe, name, c, outdir):
    deck = DECKS/(c['file'] if engine == 'lt' else c['ng_file'])
    r = run_deck(engine, exe, deck, outdir/f'{name}.{engine}.log', DECKS)
    r.update(case=name, deck='decks/' + deck.name)
    return r

def evaluate(name, c, m, chk):
    k = c['kind']
    def band(key, target=11):
        if key in m: chk(key, target*.98 <= m[key] <= target*1.02, f'{m[key]:.6g} V within {target} V +/-2%')
    def off(key):
        if key in m: chk(key, abs(m[key]) < .1, f'{m[key]:.6g} V; off <0.1 V')
    def o1(key='o1_peak'):
        chk('O1_input_rating', m[key] <= O1_MAX, f"{m[key]:.6g} V peak vs {O1_MAX} V instantaneous")
    def normal(key, what='normal-operation bus/port level'):
        # P1-2 (rev2): the NORMAL bus upper limit is 11.1605 V (static max, owner hard criterion); 11.22 V is only the
        # +2 % band edge and the OVP false-trip TEST level - kept as separate assertions, nothing loosened.
        if key in m: chk(f'NORMAL_BUS_MAX:{key}', m[key] <= NORMAL_MAX, f'{m[key]:.6g} V vs {NORMAL_MAX} V ({what})')
    def stress(fault_inp=True):
        if 'vdsa_max' in m: chk('QA_VDS_rating', m['vdsa_max'] <= VDS_MAX, f"{m['vdsa_max']:.4g} V vs 60 V abs max")
        if 'vdsb_max' in m: chk('QB_VDS_rating', m['vdsb_max'] <= VDS_MAX, f"{m['vdsb_max']:.4g} V vs 60 V abs max")
        if 'iinm_max' in m: chk('TLV3601_input_current', m['iinm_max'] <= IIN_MAX, f"{m['iinm_max']*1e3:.4g} mA vs 10 mA abs max")
        if 'v5_max' in m: chk('5V_rail_recommended', m['v5_max'] <= VCC_REC_MAX, f"{m['v5_max']:.4g} V vs 5.5 V")
        if 'bus_peak' in m: chk('U3_U4_VIN_abs_max', m['bus_peak'] <= U34_VIN_ABS, f"bus {m['bus_peak']:.5g} V vs TPS259824 IN 30 V abs max")
        if fault_inp and 'inp_fault_max' in m:
            chk('fet_stays_off', m['inp_fault_max'] < INP_L_MAX, f"INP max {m['inp_fault_max']:.3g} V during fault (< V(INP_L) 0.8 V guaranteed)")
    if k in ('ramp', 'sweep', 'mc-ramp'):
        normal('o1_pre', 'O1 before the fault'); band('o1_pre'); off('o1_off'); off('s2e_off'); band('o1_reset'); band('s2e_reset'); o1(); stress()
    if k in ('short', 'mc-short'):
        normal('normal', 'bus before the short'); normal('o1_normal', 'O1 before the short'); band('normal'); band('o1_normal'); o1(); stress()
        if 'o1_reset' in m: band('o1_reset'); band('s2e_reset')
    if k == 'board-average':
        band('bus_avg'); band('o1_avg'); band('s2e_avg'); o1('o1_max')
        chk('bus_max_startup', m['bus_max'] <= 11.22, f"bus max {m['bus_max']:.6g} V vs 11.22 V (+2 % band edge)")
        normal('bus_max', 'startup/static bus max incl. overshoot'); normal('bus_avg', 'static bus average')
        for key in ('pg1_max', 'pg2_max'):
            if key in m: chk(key, 0 <= m[key] < 6, f'{m[key]:.6g} V <6 V')
        for ch, load in ((1, 3), (2, 1.5)):
            key = f'imon{ch}_avg'
            if key in m:
                e = load*246e-6*806; chk(key, abs(m[key]-e) < .002, f'{m[key]:.6g} V vs {e:.6g} V')
        if 'iphase1_avg' in m:
            chk('sharing', abs(m['iphase1_avg']-m['iphase2_avg']) < .01, 'phase mismatch <10 mA')
            tot = m['iphase1_avg']+m['iphase2_avg']; e = 7.5 if name.startswith('bus-7p5a') else 4.5
            chk('total_current', abs(tot-e) < .02, f'{tot:.6g} A vs {e} A')
        if name.startswith('bus-7p5a'):
            chk('static_bus_7p5A', 10.78 <= m['bus_avg'] <= 11.22, f"{m['bus_avg']:.6g} V at 7.5 A")
        chk('no_trip', m['inp_min'] > 4.0 and m['vgs_min'] > 4.5, f"INP min {m['inp_min']:.4g} V, VGS min {m['vgs_min']:.4g} V")
    if k == 'step':
        band('o1_final'); band('s2e_final')
        chk('transient', 10.78 <= m['bus_min'] and m['bus_max'] <= 11.22, f"{m['bus_min']:.6g}..{m['bus_max']:.6g} V, 0.45->4.5 A (verify_results.py L79)")
        normal('bus_max', 'load-step bus max')
        chk('no_trip', m['inp_min'] > 4.0 and m['vgs_min'] > 4.5, f"INP min {m['inp_min']:.4g} V, VGS min {m['vgs_min']:.4g} V")
    if k == 'step75':
        band('o1_final'); band('s2e_final')
        chk('no_trip', m['inp_min'] > 4.0 and m['vgs_min'] > 4.5, f"INP min {m['inp_min']:.4g} V, VGS min {m['vgs_min']:.4g} V")
        normal('bus_max', '7.5 A load-step bus max (acceptance, separate from the WP3 tracking window)')
        chk('TRACKING:transient_7p5A_window', 10.78 <= m['bus_min'] and m['bus_max'] <= 11.22,
            f"{m['bus_min']:.6g}..{m['bus_max']:.6g} V (WP3 tracking, not a repo criterion)")
    if k in ('nofalse', 'mc-nofalse'):
        band('o1_avg'); band('s2e_avg')
        chk('FALSE_TRIP_TEST_LEVEL_reached', m['raw_max'] >= FALSE_TRIP_TEST - 1e-3, f"RAW max {m['raw_max']:.6g} V vs test level {FALSE_TRIP_TEST} V (stimulus validity; NOT a normal-bus limit)")
        chk('no_false_trip', m['inp_min'] > 4.0 and m['vgs_min'] > 4.5, f"RAW max {m['raw_max']:.5g} V; INP min {m['inp_min']:.4g} V; VGS min {m['vgs_min']:.4g} V")

def static_checks(chk):
    for name, c in CASES.items():
        a = (DECKS/c['file']).read_text().replace('pdu-inductor-lt.lib', 'pdu-inductor-ng.lib').replace(' Rser=0', '')
        chk(f'deck parity/{name}', a == (DECKS/c['ng_file']).read_text(), 'LT vs ng differ only by inductor lib and Rser=0')
    base = [l for l in (SIM/'pdu-protection.inc').read_text().splitlines() if l.strip() and not l.lower().startswith('.include')]
    copy = [l for l in (HERE/'pdu-efuse-block-o1ovp.inc').read_text().splitlines() if l.strip()]
    copy = [l for l in copy if not l.startswith('* COPY of') and 'run_o1ovp.py verifies' not in l]
    chk('efuse block identical to ../../pdu-protection.inc', copy == base, 'line-by-line, .include removed')
    b = [l.split() for l in (SIM/'pdu-circuit.inc').read_text().splitlines() if l.strip() and not l.startswith('*')]
    n = [l.split() for l in (HERE/'pdu-circuit-o1ovp.inc').read_text().splitlines() if l.strip() and not l.startswith('*')]
    b = [t for t in b if t[0] != '.include']
    # rev2: exactly 8 ADDED RAW capacitors COUT21-COUT28, identical in form to the baseline COUT lines
    added = [t for t in n if t[0] in {f'COUT{i}' for i in range(21, 29)}]
    chk('rev2 RAW bank: only COUT21-COUT28 added, same value as COUT1-8',
        len(added) == 8 and all(t[1:] == ['RAW', '0', '{2.2e-05*CBIAS}'] for t in added), str(added))
    n = [t for t in n if t not in added]
    diff = [(x[0], [i for i, (p, q) in enumerate(zip(x, y)) if p != q]) for x, y in zip(b, n) if x != y]
    exp = sorted([(f'COUT{i}', [1]) for i in range(1, 9)] + [('RS1', [2]), ('RS2', [2]), ('RFB1', [1]), ('XU1', [6, 12]), ('XU2', [6, 12])])
    chk('RAW split = only intended node edits', len(b) == len(n) and sorted(diff) == exp and all(y[i] == 'RAW' for x, y in zip(b, n) for i in range(len(x)) if x[i] != y[i]), str(diff))

def category(c, check_name):
    if check_name.split('/')[-1].startswith('TRACKING:'): return 'tracking'
    return 'acceptance' if c.get('acceptance', True) else 'info'

def mc_summary(runs):
    out = {}
    for kind, keys in (('mc-ramp', ('o1_peak', 'bus_peak', 'trip_raw', 'off_raw')), ('mc-short', ('o1_peak', 'bus_peak', 'trip_raw', 'off_raw', 'vdsa_max')),
                       ('mc-nofalse', ('inp_min', 'vgs_min', 'raw_max'))):
        rs = [r for r in runs if CASES[r['case']]['kind'] == kind and r['execution_pass']]
        if rs:
            out[kind] = dict(n_ok=len(rs), n_total=sum(CASES[r['case']]['kind'] == kind for r in runs), seed=META.get('mc_seed'),
                             **{k: dict(min=min(r['measures'][k] for r in rs), max=max(r['measures'][k] for r in rs)) for k in keys if all(k in r['measures'] for r in rs)})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=''); ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--label', default=''); ap.add_argument('--out', default='o1ovp-results.json')
    ap.add_argument('--no-regression', action='store_true')
    a = ap.parse_args()
    exe = {e: os.environ.get(v) for e, v in (('ng', 'PDU_NGSPICE'), ('lt', 'PDU_LTSPICE'))}
    exe = {e: (p if p and Path(p).exists() else None) for e, p in exe.items()}
    started = now_ist()
    outdir = HERE/'results'; outdir.mkdir(exist_ok=True)
    checks, incomplete, skipped = [], [], []
    def chk(name, ok, detail, cat='acceptance'): checks.append({'check': name, 'pass': bool(ok), 'category': cat, 'detail': detail})
    static_checks(chk)
    if not exe['ng']: incomplete.append('ngspice: PDU_NGSPICE not set or missing')
    if not exe['lt']: skipped.append('LTspice: PDU_LTSPICE not set or missing -> LTspice decks NOT run (no LTspice result is claimed)')
    engines = [e for e in ('ng', 'lt') if exe[e]]
    jobs = [(e, exe[e], n, c) for e in engines for n, c in CASES.items() if a.only in n]
    if a.only: incomplete.append(f'--only {a.only!r}: subset run')
    with ThreadPoolExecutor(max(1, a.jobs)) as pool:
        runs = list(pool.map(lambda j: run_one(*j, outdir), jobs))
    for r in runs:
        pre = f"{'LTspice' if r['engine']=='lt' else 'ngspice'}/{r['case']}"
        c = CASES[r['case']]
        cat0 = 'acceptance' if c.get('acceptance', True) else 'info'
        if not r['execution_pass']:
            incomplete.append(f"{pre}: did not complete (rc={r['returncode']}, missing={r['missing']}, {r['errors'][:1]})")
            chk(pre+'/execution', False, r['errors'][:2] or r['missing'], cat0); continue
        chk(pre+'/execution', True, f"{r['seconds']} s", cat0)
        m = r['measures']
        chk(pre+'/finite', all(isfinite(x) for x in m.values()), 'all finite', cat0)
        if c['kind'] == 'reference': continue
        evaluate(r['case'], c, m, lambda n, ok, d: chk(pre+'/'+n, ok, d, category(c, n)))
    by = {(r['engine'], r['case']): r for r in runs if r['execution_pass']}
    for n in CASES:
        if ('lt', n) in by and ('ng', n) in by:
            for k, x in by[('lt', n)]['measures'].items():
                y = by[('ng', n)]['measures'].get(k)
                lim = max(.02*max(abs(x), abs(y or 0)), .01)
                chk(f'parity/{n}/{k}', y is not None and abs(x-y) <= lim, f'LT {x:.6g} ng {y} limit {lim:.3g}')
    regression = None
    if not a.no_regression and exe['ng']:
        bdeck = SIM/BASELINE_REG
        before = sha(bdeck)
        r = run_deck('ng', exe['ng'], bdeck, outdir/'baseline-regression-efuse-ovp.ng.log', SIM)
        regression = dict(deck='simulation/' + BASELINE_REG, deck_sha256_before=before, deck_sha256_after=sha(bdeck), **r)
        if not r['execution_pass']:
            incomplete.append(f'baseline regression did not complete: {r["errors"][:1]} {r["missing"]}')
        else:
            pk = r['measures']['o1_peak']
            regression['o1_peak'] = pk
            regression['baseline_criterion_result'] = 'FAIL' if pk > O1_MAX else 'PASS'
            chk('regression/baseline efuse-ovp violates O1 12 V (expected, ~16.89 V)', pk > O1_MAX,
                f'baseline O1_PEAK {pk:.6g} V vs 12 V -> baseline criterion {regression["baseline_criterion_result"]}')
            chk('regression/baseline deck unchanged', before == regression['deck_sha256_after'], before)
    inputs = sorted(set(['pdu-o1ovp-behavioral.lib', 'pdu-o1ovp-block.inc', 'pdu-circuit-o1ovp.inc', 'pdu-efuse-block-o1ovp.inc',
                         'test-cases-o1ovp.json', 'net-split-changes.json', 'gen_o1ovp.py', 'run_o1ovp.py', 'window_budget.py'] +
                        ['decks/' + c['file'] for c in CASES.values()] + ['decks/' + c['ng_file'] for c in CASES.values()]))
    acc = [c for c in checks if c['category'] == 'acceptance']
    res = {'label': a.label or 'unlabelled', 'package': '2026-10-25-o1-ovp',
           'scope': 'BEHAVIORAL/IDEAL models only; not vendor silicon; not a bench/prototype result',
           'started': started, 'finished': now_ist(), 'tools': tool_versions(exe),
           'engines_run': engines, 'skipped': skipped,
           'input_sha256': {p: sha(HERE/p) for p in inputs},
           'baseline_sha256': {p: sha(SIM/p) for p in ('pdu-behavioral.lib', 'pdu-circuit.inc', 'pdu-protection.inc', 'pdu-inductor-lt.lib',
                                                       'pdu-inductor-ng.lib', BASELINE_REG, 'verify_results.py', 'test-cases.json')},
           'runs': runs, 'baseline_regression': regression, 'monte_carlo': mc_summary(runs), 'checks': checks,
           'acceptance_passed': sum(c['pass'] for c in acc), 'acceptance_failed': sum(not c['pass'] for c in acc),
           'info_or_tracking_failed': [c['check'] for c in checks if c['category'] != 'acceptance' and not c['pass']],
           'incomplete': incomplete}
    (HERE/a.out).write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('label', 'acceptance_passed', 'acceptance_failed')} | {'incomplete': len(incomplete), 'skipped': skipped}))
    for c in checks:
        if not c['pass']: print(('FAIL' if c['category'] == 'acceptance' else c['category'].upper() + '-FAIL'), c['check'], c['detail'])
    if regression and 'o1_peak' in regression:
        print(f"REGRESSION baseline {BASELINE_REG}: O1_PEAK {regression['o1_peak']:.6g} V -> baseline {regression['baseline_criterion_result']} (expected FAIL)")
    for i in incomplete: print('INCOMPLETE', i)
    sys.exit(2 if incomplete else (1 if res['acceptance_failed'] else 0))

if __name__ == '__main__':
    main()
