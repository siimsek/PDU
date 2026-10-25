#!/usr/bin/env python3
"""WP2 Tur-1 (ChatGPT review 6395284882) negative/regression tests. Exit 0 = all tests behave as required, 1 = a test failed.

G-tests  (P0 INFO gating): synthetic ngspice logs are fed to verify_uvlo.main() in a temporary tree. The hard limits
         O1 <= 12.0 V (instantaneous) and stable-window bus/O1 <= 11.1605 V must fail the run (exit 1) for EVERY
         non-regression case, also for cases classified INFO. A missing hard-limit measurement must not pass.
B-tests  (P0 startup budget): uvlo_budget.py must use the guaranteed TLV3202 VIO max over temperature
         (6 mV, TI SBOS561C rev. C, May 2024, p.5, table 6.5) and must not report the 20 V start as guaranteed
         while assumption/typical terms are in the start budget.
Usage: python3 tests/test_uvlo_gates.py [path/to/package_dir]   (default: the package dir that contains tests/)
No real file in the package is written (the verifier runs against a temporary copy of the tree layout).
"""
import hashlib, importlib.util, json, shutil, sys, tempfile, contextlib, io
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log_text(meas):
    lines = ['Circuit: synthetic', '']
    lines += [f'{k.lower():20s}=  {v:.6e}' for k, v in meas.items()]
    lines += ['', 'Total analysis time (seconds) = 1.0', '']
    return '\n'.join(lines)


GOOD_WIN = lambda w: {f'{w}_BUS_MAX': 11.00, f'{w}_O1_MAX': 10.98, f'{w}_RAW_AVG': 11.0, f'{w}_EN_MIN': 2.5,
                      f'{w}_VGS_MIN': 11.6, f'{w}_INP_MIN': 4.99}
DIP_CASE = {'kind': 'dip', 'expect': 'INFO', 't0': 0.26, 't1': 0.2602}
RS_CASE = {'kind': 'rsweep', 'expect': 'INFO', 'r': 0.30, 'vf': 18.26, 'vr': 19.72}
START_CASE = {'kind': 'start', 'expect': 'PASS', 'vf': 18.26}


def dip_meas(**over):
    m = {'O1_GLOBAL_PEAK': 10.978, 'BUS_GLOBAL_MAX': 11.0, 'EN_R1': 0.18, 'FET_ON1': 0.012}
    m.update(GOOD_WIN('PRE')); m.update(GOOD_WIN('POST')); m.update(over)
    return m


def rs_meas(**over):
    m = {'O1_GLOBAL_PEAK': 10.978, 'EN_R1': 0.18, 'OUTA_R1': 0.001, 'FET_ON1': 0.012, 'RUN_VIN_MIN': 18.5}
    m.update(GOOD_WIN('RUN')); m.update(over)
    return m


def run_verifier(cases, logs):
    """Run verify_uvlo.main() of PKG against a temporary tree; return (exit code, summary)."""
    tmp = Path(tempfile.mkdtemp(prefix='uvlo-gate-'))
    try:
        here = tmp / 'simulation' / 'proposals' / '2026-10-25-uvlo'
        (here / 'results' / 'logs').mkdir(parents=True)
        (here / 'decks').mkdir()
        shutil.copy(PKG / 'verify_uvlo.py', here / 'verify_uvlo.py')
        (here / 'test-cases-uvlo.json').write_text(json.dumps({'cases': cases}))
        (here / 'results' / 'uvlo-budget.json').write_text('{}')
        for p in ('pdu-behavioral.lib', 'pdu-inductor-ng.lib'):
            (tmp / 'simulation' / p).write_text('* dummy\n')
        o1 = tmp / 'simulation' / 'proposals' / '2026-10-25-o1-ovp'; o1.mkdir()
        for p in ('pdu-o1ovp-behavioral.lib', 'pdu-o1ovp-block.inc', 'pdu-circuit-o1ovp.inc', 'pdu-efuse-block-o1ovp.inc'):
            (o1 / p).write_text('* dummy\n')
        # Tur-2 (UVLO-04): the verifier only accepts logs bound to a fresh run manifest -> the fixture writes one
        # (decks + manifest with matching SHA-256); stale/failed-run negatives are in test_uvlo_tur2.py
        sh = lambda t: hashlib.sha256(t.encode()).hexdigest()
        runs = {}
        for n in cases:
            d = f'* deck {n}\n.end\n'; (here / 'decks').mkdir(exist_ok=True); (here / 'decks' / f'uvlo-{n}.cir').write_text(d)
            lt = log_text(logs[n]) if logs.get(n) is not None else None
            if lt is not None:
                (here / 'results' / 'logs' / f'uvlo-{n}.log').write_text(lt)
            runs[f'uvlo-{n}'] = dict(rc=0, completed=True, deck_sha256=sh(d), log_sha256=sh(lt) if lt else None)
        (here / 'results' / 'run-manifest.json').write_text(json.dumps(dict(
            run_id='fixture', git_head='', package_inputs_dirty_at_run=False, runner_exit_code=0,
            cases_sha256=sh((here / 'test-cases-uvlo.json').read_text()), runs=runs)))
        v = load('verify_uvlo_under_test', here / 'verify_uvlo.py')
        code = None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                v.main()
            except SystemExit as e:
                code = e.code
        summ = json.loads((here / 'results' / 'uvlo-verify.json').read_text())['summary']
        return code, summ
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gate_tests():
    T = []
    # G0 control: clean INFO dip + clean INFO rsweep + clean PASS start -> exit 0
    T.append(('G0 control: clean INFO/PASS cases -> exit 0',
              {'d': DIP_CASE, 'r': RS_CASE, 's': START_CASE}, {'d': dip_meas(), 'r': rs_meas(), 's': rs_meas()}, 0))
    # G1 INFO dip case, O1 instantaneous 12.01 V -> must FAIL (exit 1)
    T.append(('G1 INFO dip: O1_GLOBAL_PEAK 12.01 V -> exit 1',
              {'d': DIP_CASE}, {'d': dip_meas(O1_GLOBAL_PEAK=12.01)}, 1))
    # G2 INFO dip case, stable POST window bus 11.17 V -> must FAIL
    T.append(('G2 INFO dip: POST_BUS_MAX 11.17 V -> exit 1',
              {'d': DIP_CASE}, {'d': dip_meas(POST_BUS_MAX=11.17)}, 1))
    # G3 INFO rsweep, stable RUN window bus 11.17 V -> must FAIL
    T.append(('G3 INFO rsweep: RUN_BUS_MAX 11.17 V -> exit 1',
              {'r': RS_CASE}, {'r': rs_meas(RUN_BUS_MAX=11.17)}, 1))
    # G4 INFO rsweep, stable RUN window O1 11.17 V -> must FAIL
    T.append(('G4 INFO rsweep: RUN_O1_MAX 11.17 V -> exit 1',
              {'r': RS_CASE}, {'r': rs_meas(RUN_O1_MAX=11.17)}, 1))
    # G5 INFO case without the O1 measurement -> must not pass (exit != 0)
    m = dip_meas(); m.pop('O1_GLOBAL_PEAK')
    T.append(('G5 INFO dip: O1_GLOBAL_PEAK missing -> exit != 0', {'d': DIP_CASE}, {'d': m}, 'nonzero'))
    # G6 INFO dip without POST window bus measurement -> must not pass
    m = dip_meas(); m.pop('POST_BUS_MAX')
    T.append(('G6 INFO dip: POST_BUS_MAX missing -> exit != 0', {'d': DIP_CASE}, {'d': m}, 'nonzero'))
    # G7 unknown classification -> must not pass
    T.append(('G7 expect="MAYBE" -> exit != 0', {'d': dict(DIP_CASE, expect='MAYBE')}, {'d': dip_meas()}, 'nonzero'))
    # G8 INFO case that only fails a non-hard behavioural criterion (shutdown) stays INFO -> exit 0
    T.append(('G8 INFO rsweep: shutdown only (EN_F1 present, no hard-limit breach) -> exit 0',
              {'r': RS_CASE}, {'r': rs_meas(EN_F1=0.3)}, 0))
    # G9 PASS case with O1 12.01 -> exit 1 (sanity, old behaviour)
    T.append(('G9 PASS start: O1 12.01 V -> exit 1', {'s': START_CASE}, {'s': rs_meas(O1_GLOBAL_PEAK=12.01)}, 1))
    # G10 INFO dip, global transient bus 11.41 V outside the stable windows -> not a hard-limit breach (H2 windows), exit 0
    T.append(('G10 INFO dip: BUS_GLOBAL_MAX 11.41 V outside stable windows -> exit 0 (reported, not H2)',
              {'d': DIP_CASE}, {'d': dip_meas(BUS_GLOBAL_MAX=11.41)}, 0))
    res = []
    for name, cases, logs, want in T:
        try:
            code, summ = run_verifier(cases, logs)
        except Exception as e:  # a crash is not a pass
            code, summ = f'crash {type(e).__name__}: {e}', {}
        ok = (code != 0 and isinstance(code, int)) if want == 'nonzero' else code == want
        res.append((name, ok, f'exit {code} (want {want})'))
    return res


def budget_tests():
    res = []
    with contextlib.redirect_stdout(io.StringIO()):
        b = load('uvlo_budget_under_test', PKG / 'uvlo_budget.py')
    vio = b.DS['TLV3202_VIO'][0]
    res.append(('B1 TLV3202 VIO max over temp = 6 mV (SBOS561C p.5)', abs(vio - 0.006) < 1e-12, f'VIO={vio*1e3:.3f} mV'))
    # B2 budget must expose the start-guarantee status and must not call it guaranteed while A/T terms are used
    st = getattr(b, 'start_guarantee_status', None)
    if st is None:
        res.append(('B2 start-guarantee status reported', False, 'no start_guarantee_status()'))
    else:
        s = st()
        res.append(('B2 start-guarantee status != GUARANTEED while A/T terms in start budget',
                    s['status'] != 'GUARANTEED' and len(s['non_guaranteed_terms']) > 0, s['status']))
    return res


def main():
    rows = gate_tests() + budget_tests()
    for n, ok, d in rows:
        print(('OK  ' if ok else 'BAD ') + n + '  -> ' + d)
    bad = sum(1 for _, ok, _ in rows if not ok)
    print(f'{len(rows) - bad}/{len(rows)} OK')
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
