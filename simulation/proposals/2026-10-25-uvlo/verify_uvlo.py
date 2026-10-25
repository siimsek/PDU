#!/usr/bin/env python3
"""Independent verifier for WP2 2026-10-25-uvlo. Parses ngspice logs (results/logs/), applies the acceptance rules
below (limits are FIXED constants, never relaxed), checks the known-failing regressions, records SHA-256 of every
input and the git HEAD. Exit: 0 = all acceptance PASS and all regressions FAIL as expected; 1 = any acceptance FAIL
or a regression that unexpectedly passes, or ANY non-regression case (PASS or INFO) breaching a hard limit
(O1 <= 12.0 V, stable-window bus/O1 <= 11.1605 V) or missing its hard-limit measurement, or an invalid case
classification; 2 = any deck missing/incomplete (acceptance cannot be decided).
"""
import json, re, sys, hashlib, subprocess, math
from pathlib import Path
HERE = Path(__file__).absolute().parent
O1_PEAK_MAX = 12.0          # O1 instantaneous peak (hard)
BUS_NORMAL_MAX = 11.1605    # normal-regime bus max (hard)
V_FALL_MIN = 18.0           # over-discharge: buck must be off before VIN < 18.0 V (3.0 V/cell under load, see REQUIREMENTS)
T_SEQ_MIN = 0.060           # buck restart delay after VIN OK >= 60 ms (> TDRV_EN worst 50.8 ms + margin)
RAW_REG = (10.8, BUS_NORMAL_MAX)
REG_OK = dict(en=2.0, vgs=6.0, inp=2.5)

def parse(log):
    t = log.read_text(errors='replace')
    m = {}
    for k, v in re.findall(r'^([a-z0-9_]+)\s+=\s+([-+0-9.eE]+)', t, re.M):
        m[k.upper()] = float(v)
    failed = set(k.upper() for k in re.findall(r'\.meas tran (\S+) .* failed!', t))
    # an aborted transient (e.g. 'Timestep too small') still prints 'Total analysis time': treat it as NOT done
    done = 'Total analysis time' in t and 'simulation(s) aborted' not in t and 'Timestep too small' not in t
    return m, failed, done, t

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def regime(m, w, f):
    """normal regime in window w: EN high, FETs enhanced, comparator high, RAW regulated, bus/O1 below the normal limit."""
    req = [f'{w}_BUS_MAX', f'{w}_O1_MAX', f'{w}_RAW_AVG', f'{w}_EN_MIN', f'{w}_VGS_MIN', f'{w}_INP_MIN']
    if any(k not in m for k in req):
        return ['window ' + w + ' measurements missing']
    e = []
    if m[f'{w}_EN_MIN'] < REG_OK['en']: e.append(f'{w}: EN low ({m[w+"_EN_MIN"]:.3f} V) -> not running')
    if m[f'{w}_VGS_MIN'] < REG_OK['vgs']: e.append(f'{w}: OVP FET not enhanced (VGS min {m[w+"_VGS_MIN"]:.3f} V)')
    if m[f'{w}_INP_MIN'] < REG_OK['inp']: e.append(f'{w}: OVP comparator low')
    if not (RAW_REG[0] <= m[f'{w}_RAW_AVG'] <= RAW_REG[1]): e.append(f'{w}: RAW avg {m[w+"_RAW_AVG"]:.4f} V not regulated')
    if m[f'{w}_BUS_MAX'] > BUS_NORMAL_MAX: e.append(f'{w}: bus max {m[w+"_BUS_MAX"]:.5f} > {BUS_NORMAL_MAX}')
    if m[f'{w}_O1_MAX'] > BUS_NORMAL_MAX: e.append(f'{w}: O1 max {m[w+"_O1_MAX"]:.5f} > {BUS_NORMAL_MAX}')
    return e

# Hard limits H1/H2 are enforced for EVERY non-regression case, independent of its PASS/INFO classification
# (ChatGPT review 6395284882, WP2 Tur-1 P0). Stable (normal-regime) windows defined per case kind:
HARD_WINDOWS = {'start': ('RUN',), 'ramp_up': ('RUN',), 'hotplug': ('RUN',), 'rsweep': ('RUN',), 'seq': ('RUN',),
                'ramp_down': ('PRE',), 'mb_hold': ('PRE',), 'dip': ('PRE', 'POST')}
VALID_EXPECT = ('PASS', 'INFO', 'FAIL')

def hard_limit_errors(c, m):
    """H1: O1_GLOBAL_PEAK <= 12.0 V; H2: bus and O1 max <= 11.1605 V in every stable window of the case kind.
    A missing or non-finite hard-limit measurement is an error (fail-closed)."""
    e = []
    v = m.get('O1_GLOBAL_PEAK')
    if v is None or not math.isfinite(v): e.append('HARD H1: O1_GLOBAL_PEAK missing/non-finite')
    elif v > O1_PEAK_MAX: e.append(f'HARD H1: O1 peak {v:.5f} > {O1_PEAK_MAX}')
    wins = HARD_WINDOWS.get(c.get('kind'))
    if wins is None:
        e.append(f'HARD: unknown case kind {c.get("kind")!r} (no stable windows defined)')
        return e
    for w in wins:
        for q in ('BUS_MAX', 'O1_MAX'):
            v = m.get(f'{w}_{q}')
            if v is None or not math.isfinite(v): e.append(f'HARD H2: {w}_{q} missing/non-finite')
            elif v > BUS_NORMAL_MAX: e.append(f'HARD H2: {w}_{q} {v:.5f} > {BUS_NORMAL_MAX}')
    return e

def judge(name, c, m, failed):
    e, info = [], {}
    has = lambda k: k in m and k not in failed
    if 'O1_GLOBAL_PEAK' not in m:
        return ['O1_GLOBAL_PEAK missing'], info
    if m['O1_GLOBAL_PEAK'] > O1_PEAK_MAX: e.append(f'O1 peak {m["O1_GLOBAL_PEAK"]:.5f} > {O1_PEAK_MAX}')
    info['O1_GLOBAL_PEAK'] = m['O1_GLOBAL_PEAK']
    for k in ('BUS_GLOBAL_MAX', 'RAW_GLOBAL_MAX', 'VIN_GLOBAL_MAX', 'S_MINUS_V5_MAX', 'SWD_MINUS_V5_MAX', 'EN_R1', 'EN_F1', 'EN_R2',
              'OUTA_R1', 'FET_ON1', 'FET_OFF1', 'FET_ON2'):
        if has(k): info[k] = m[k]
    k = c['kind']
    if k in ('start', 'ramp_up', 'hotplug', 'rsweep'):
        if not has('EN_R1'):
            e.append('buck never enabled (no start)')
        else:
            if 't_start_max' in c and m['EN_R1'] > c['t_start_max']: e.append(f'start late {m["EN_R1"]:.4f} s')
            if has('EN_F1'): e.append(f'EN fell at {m["EN_F1"]:.4f} s (shutdown/motorboat)')
            if has('OUTA_R1') and m['EN_R1'] - m['OUTA_R1'] < T_SEQ_MIN: e.append(f'restart delay {m["EN_R1"]-m["OUTA_R1"]:.4f} s < {T_SEQ_MIN}')
            if has('FET_ON1') and m['FET_ON1'] > m['EN_R1']: e.append('buck enabled before the OVP FET was on (sequencing)')
            if not has('FET_ON1'): e.append('OVP FET never on')
            info['delay_after_vin_ok'] = m['EN_R1'] - m['OUTA_R1'] if has('OUTA_R1') else None
            info['seq_margin_s'] = m['EN_R1'] - m['FET_ON1'] if has('FET_ON1') else None
        e += regime(m, 'RUN', failed)
        if 'RUN_VIN_MIN' in m:
            info['RUN_VIN_MIN'] = m['RUN_VIN_MIN']
            if c.get('vf') and m['RUN_VIN_MIN'] <= c['vf']: e.append(f'VIN under load {m["RUN_VIN_MIN"]:.4f} <= V_f {c["vf"]:.4f}')
            if c.get('vf'): info['run_margin_to_vf'] = m['RUN_VIN_MIN'] - c['vf']
        if 'VIN_PP_RUN' in m: info['VIN_PP_RUN'] = m['VIN_PP_RUN']
    elif k in ('ramp_down', 'mb_hold'):
        e += regime(m, 'PRE', failed)
        if k == 'ramp_down' and not has('EN_F1'): e.append('no shutdown at low input')
        if has('EN_F1'):
            info['VIN_AT_SHUTDOWN'] = m.get('VIN_AT_SHUTDOWN')
            if 'VIN_AT_SHUTDOWN' in m and m['VIN_AT_SHUTDOWN'] < V_FALL_MIN: e.append(f'shutdown at VIN {m["VIN_AT_SHUTDOWN"]:.4f} < {V_FALL_MIN}')
        if has('EN_R2'): e.append(f'restart at {m["EN_R2"]:.4f} s while E stays low (motorboat)')
        for x in ('EMF_AT_SHUTDOWN', 'VIN_AT_OUTA_FALL', 'VIN_MAX_AFTER', 'VIN_MIN_HOLD'):
            if x in m: info[x] = m[x]
        if k == 'mb_hold': info['shut_down'] = has('EN_F1'); info['e_hold'] = c['e_hold']
    elif k == 'dip':
        e += regime(m, 'PRE', failed) + regime(m, 'POST', failed)
        if has('EN_F2'): e.append('second shutdown after the dip (chatter)')
        if has('EN_R3'): e.append('third enable (chatter)')
        if has('EN_F1') and not has('EN_R2'): e.append('no restart after the dip')
        if has('EN_R2') and m['EN_R2'] - c['t1'] < 0: e.append('restart during the dip')
        for x in ('BUS_RESTART_MAX', 'RAW_RESTART_MAX', 'INP_RESTART_MIN', 'RAW_AT_DIP_END', 'T_AT_DIP_END', 'O1_DIP_MAX'):
            if x in m: info[x] = m[x]
        info['rode_through'] = not has('EN_F1')
        if has('EN_R2'):
            info['restart_delay_after_dip_end'] = m['EN_R2'] - c['t1']
            # P0-03 related INFO (open item, WP1-K): did the buck restart before the OVP FET was back on?
            if has('FET_OFF1'):
                info['P0_03_buck_before_fet'] = (not has('FET_ON2')) or m['FET_ON2'] > m['EN_R2']
    elif k == 'seq':
        if not has('FET_ON1'): e.append('FET never on')
        elif m['FET_ON1'] > c['delay'] and c['delay'] > 0: e.append('FET not on before DRIVE starts')
        if has('FET_OFF1'): e.append(f'FET turned off at {m["FET_OFF1"]:.5f} s (start-up false trip / P0-03)')
        if 'INP_MIN_AFTER_ON' in m and m['INP_MIN_AFTER_ON'] < 2.5: e.append('comparator tripped (INP low)')
        e += regime_seq(m)
        for x in ('RAW_MAX', 'BUS_STARTUP_MAX', 'INP_MIN_AFTER_ON'):
            if x in m: info[x] = m[x]
    return e, info

def regime_seq(m):
    e = []
    for x in ('RUN_BUS_MAX', 'RUN_O1_MAX', 'RUN_RAW_AVG', 'RUN_VGS_MIN', 'RUN_INP_MIN'):
        if x not in m: return [f'{x} missing']
    if m['RUN_VGS_MIN'] < 6 or m['RUN_INP_MIN'] < 2.5: e.append('RUN: FET/comparator not in normal state')
    if m['RUN_BUS_MAX'] > BUS_NORMAL_MAX or m['RUN_O1_MAX'] > BUS_NORMAL_MAX: e.append('RUN: bus/O1 above normal limit')
    return e

def main():
    cases = json.loads((HERE / 'test-cases-uvlo.json').read_text())['cases']
    out, acc_fail, reg_bad, incomplete = {}, [], [], []
    for name, c in cases.items():
        log = HERE / 'results' / 'logs' / f'uvlo-{name}.log'
        if not log.exists():
            out[name] = dict(status='INCOMPLETE', reason='log missing'); incomplete.append(name); continue
        m, failed, done, _ = parse(log)
        if not done:
            st = 'INCOMPLETE'
            res = dict(status=st, reason='simulation did not complete', last_meas=m)
            # strict (2026-10-25): an aborted/unfinished deck never counts as a reproduced regression
            incomplete.append(name)
            out[name] = res; continue
        errs, info = judge(name, c, m, failed)
        hard = hard_limit_errors(c, m)
        errs = errs + [h for h in hard if h not in errs]
        st = 'PASS' if not errs else 'FAIL'
        res = dict(status=st, errors=errs, info=info, expect=c.get('expect'), hard_limit_errors=hard)
        if c.get('expect') not in VALID_EXPECT or (c.get('expect') == 'FAIL') != bool(c.get('regression')):
            res['status'] = 'FAIL'; res['errors'] = errs + [f'invalid classification expect={c.get("expect")!r} regression={c.get("regression")!r}']
            acc_fail.append(name)
        elif c.get('regression'):
            res['regression_reproduced'] = st == 'FAIL'
            if st != 'FAIL': reg_bad.append(name)
        elif hard:
            # fail-closed (Tur-1 P0): PASS *and* INFO cases fail CI on any H1/H2 breach or missing hard-limit measurement
            acc_fail.append(name)
        elif c['expect'] == 'PASS' and st != 'PASS':
            acc_fail.append(name)
        out[name] = res
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain', '.'], cwd=HERE, capture_output=True, text=True).stdout.strip() != ''
    # inputs = everything in the package except results/ (logs are rewritten by run_uvlo.py before the verifier runs)
    inputs_dirty = subprocess.run(['git', 'status', '--porcelain', '--', '.', ':(exclude)results'], cwd=HERE, capture_output=True,
                                  text=True).stdout.strip() != ''
    files = sorted([p for p in HERE.glob('*.py')] + [p for p in HERE.glob('*.inc')] + [p for p in HERE.glob('*.lib')]
                   + [HERE / 'test-cases-uvlo.json', HERE / 'results' / 'uvlo-budget.json'] + list((HERE / 'decks').glob('*.cir'))
                   + [HERE.parent.parent / 'pdu-behavioral.lib', HERE.parent.parent / 'pdu-inductor-ng.lib',
                      HERE.parent / '2026-10-25-o1-ovp' / 'pdu-o1ovp-behavioral.lib', HERE.parent / '2026-10-25-o1-ovp' / 'pdu-o1ovp-block.inc',
                      HERE.parent / '2026-10-25-o1-ovp' / 'pdu-circuit-o1ovp.inc', HERE.parent / '2026-10-25-o1-ovp' / 'pdu-efuse-block-o1ovp.inc'])
    logs = sorted((HERE / 'results' / 'logs').glob('*.log'))
    code = 2 if incomplete else (1 if acc_fail or reg_bad else 0)
    summary = dict(exit_code=code, git_head=git, worktree_dirty_at_verify=dirty, package_inputs_dirty=inputs_dirty, n_cases=len(cases),
                   n_pass=sum(1 for r in out.values() if r['status'] == 'PASS'),
                   acceptance_fail=acc_fail, regression_not_reproduced=reg_bad, incomplete=incomplete,
                   info_cases=[n for n, c in cases.items() if c.get('expect') == 'INFO'],
                   hard_limit_gate='H1/H2 enforced for every non-regression case (PASS and INFO)',
                   limits=dict(O1_PEAK_MAX=O1_PEAK_MAX, BUS_NORMAL_MAX=BUS_NORMAL_MAX, V_FALL_MIN=V_FALL_MIN, T_SEQ_MIN=T_SEQ_MIN))
    (HERE / 'results' / 'uvlo-verify.json').write_text(json.dumps(dict(summary=summary, cases=out,
        input_sha256={str(p.relative_to(HERE.parent.parent)): sha(p) for p in files},
        log_sha256={p.name: sha(p) for p in logs}), indent=1, default=str))
    for n, r in out.items():
        print(f'{r["status"]:10s} {"(regression, reproduced)" if r.get("regression_reproduced") else ""} {n} {"; ".join(r.get("errors", [])) or r.get("reason", "")}')
    print(json.dumps(summary, indent=1))
    sys.exit(code)

if __name__ == '__main__':
    main()
