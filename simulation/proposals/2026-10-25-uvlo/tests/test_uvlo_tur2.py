#!/usr/bin/env python3
"""WP2 Tur-2 (ChatGPT review 6395614957) negative/regression tests, written BEFORE the fixes (run on f923347 first).
Exit 0 = every test behaves as required, 1 = at least one test failed.

U03  fail-closed missing measurements: a start/ramp/hotplug/rsweep case without a usable OUTA_R1 (missing or
     'failed!') must not pass the 60 ms restart-delay check; a ramp_down/mb_hold case with EN_F1 but without a usable
     VIN_AT_SHUTDOWN must not pass the V_f >= 18.0 V check.
U05  dip restarts: EN re-rise after a dip must come >= T_SEQ_MIN = 60 ms after the last valid-VIN (OUTA) rise;
     a restart without the OUTA restoration measurement must not pass.
M/W  (UVLO-04) stale-log / failed-run protection: the verifier must refuse logs that are not bound to a fresh
     run-manifest (run id, deck/case set, deck and log SHA-256, rc == 0); the runner must preserve old outputs before
     a new isolated run, record git HEAD + run id and return non-zero on any failed deck; the CI job must not swallow failures.
R    provisional R-DIP screen (UVLO-06, review proposal, NOT a requirement change): reported per dip case, does not
     change the exit code; missing measurement -> UNDETERMINED (never PASS).
B3   (UVLO-01) the budget enumerates the IN+ bias, IN- bias and TMUX leakage signs independently.
Usage: python3 tests/test_uvlo_tur2.py [path/to/package_dir]
"""
import importlib.util, json, shutil, sys, tempfile, contextlib, io, os, subprocess, hashlib, re, math
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent
REPO = PKG.parent.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha_text(t):
    return hashlib.sha256(t.encode()).hexdigest()


def log_text(meas, failed=()):
    lines = ['Circuit: synthetic', '']
    lines += [f'{k.lower():20s}=  {v:.6e}' for k, v in meas.items()]
    lines += [f'.meas tran {k.lower()} when v(x)=1 rise=1 failed!' for k in failed]
    lines += ['', 'Total analysis time (seconds) = 1.0', '']
    return '\n'.join(lines)


GOOD_WIN = lambda w: {f'{w}_BUS_MAX': 11.00, f'{w}_O1_MAX': 10.98, f'{w}_RAW_AVG': 11.0, f'{w}_EN_MIN': 2.5,
                      f'{w}_VGS_MIN': 11.6, f'{w}_INP_MIN': 4.99}
START = {'kind': 'start', 'expect': 'PASS', 'vf': 18.26, 't_start_max': 0.2}
RDOWN = {'kind': 'ramp_down', 'expect': 'PASS'}
MBH = {'kind': 'mb_hold', 'expect': 'PASS', 'e_hold': 18.5}
DIP = {'kind': 'dip', 'expect': 'PASS', 't0': 0.26, 't1': 0.2603}


def start_meas(**o):
    m = {'O1_GLOBAL_PEAK': 10.98, 'EN_R1': 0.09, 'OUTA_R1': 0.001, 'FET_ON1': 0.012, 'RUN_VIN_MIN': 18.5}
    m.update(GOOD_WIN('RUN')); m.update(o); return m


def rdown_meas(**o):
    m = {'O1_GLOBAL_PEAK': 10.98, 'EN_R1': 0.09, 'OUTA_R1': 0.001, 'FET_ON1': 0.012, 'EN_F1': 0.5, 'VIN_AT_SHUTDOWN': 18.1}
    m.update(GOOD_WIN('PRE')); m.update(o); return m


def dip_meas(restart=True, delay=0.0605, **o):
    m = {'O1_GLOBAL_PEAK': 10.98, 'BUS_GLOBAL_MAX': 11.0, 'EN_R1': 0.09, 'OUTA_R1': 0.001, 'FET_ON1': 0.012,
         'BUS_RESTART_MAX': 11.0}
    if restart:
        m.update(EN_F1=0.2601, OUTA_F1=0.26008, OUTA_R2=0.2604, OUTA_RLAST=0.2604, EN_R2=0.2604 + delay)
    m.update(GOOD_WIN('PRE')); m.update(GOOD_WIN('POST')); m.update(o); return m


def build_tree(cases, logs, failed=None, manifest='fresh', run_id='run-123'):
    """Temporary package tree. manifest: 'fresh' | None | callable(dict)->dict (perturbation of a fresh manifest)."""
    failed = failed or {}
    tmp = Path(tempfile.mkdtemp(prefix='uvlo-t2-'))
    here = tmp / 'simulation' / 'proposals' / '2026-10-25-uvlo'
    (here / 'results' / 'logs').mkdir(parents=True); (here / 'decks').mkdir()
    shutil.copy(PKG / 'verify_uvlo.py', here / 'verify_uvlo.py')
    ct = json.dumps({'cases': cases}); (here / 'test-cases-uvlo.json').write_text(ct)
    (here / 'results' / 'uvlo-budget.json').write_text('{}')
    for p in ('pdu-behavioral.lib', 'pdu-inductor-ng.lib'):
        (tmp / 'simulation' / p).write_text('* dummy\n')
    o1 = tmp / 'simulation' / 'proposals' / '2026-10-25-o1-ovp'; o1.mkdir()
    for p in ('pdu-o1ovp-behavioral.lib', 'pdu-o1ovp-block.inc', 'pdu-circuit-o1ovp.inc', 'pdu-efuse-block-o1ovp.inc'):
        (o1 / p).write_text('* dummy\n')
    runs = {}
    for n in cases:
        d = f'* deck {n}\n.end\n'; (here / 'decks' / f'uvlo-{n}.cir').write_text(d)
        lt = log_text(logs[n], failed.get(n, ())) if logs.get(n) is not None else None
        if lt is not None:
            (here / 'results' / 'logs' / f'uvlo-{n}.log').write_text(lt)
        runs[f'uvlo-{n}'] = dict(rc=0, completed=True, deck_sha256=sha_text(d), log_sha256=sha_text(lt) if lt else None)
    mf = dict(run_id=run_id, git_head='', package_inputs_dirty_at_run=False, cases_sha256=sha_text(ct), runs=runs,
              runner_exit_code=0)
    if manifest is not None:
        if callable(manifest):
            mf = manifest(mf)
        (here / 'results' / 'run-manifest.json').write_text(json.dumps(mf))
    # Historical mode compares manifest HEAD to the real checkout. Empty git_head
    # would make even healthy gate-control tests fail at provenance preflight.
    from fixture_historical import bind_historical_fixture_git
    bind_historical_fixture_git(here)
    return tmp, here


def run_verifier(here, argv=None):
    # Small synthetic fixtures exercise the ELECTRICAL JUDGEMENT in read-only
    # historical mode. They are not a 259-deck locked acceptance run.
    # Locked acceptance is tested separately in test_locked_verifier.py.
    if argv is None:
        argv = ['--historical']
    from fixture_summary import summary_from_stdout
    v = load('verify_uvlo_t2', here / 'verify_uvlo.py')
    code, old = None, sys.argv
    stdout, stderr = io.StringIO(), io.StringIO()
    sys.argv = ['verify_uvlo.py'] + list(argv)
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                v.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = old
    out = summary_from_stdout(stdout.getvalue())
    out['_stderr'] = stderr.getvalue()
    if argv == ['--historical'] and not out.get('summary'):
        return 'missing historical stdout summary', out
    return code, out


def vt(name, cases, logs, want, failed=None, manifest='fresh', argv=None, check=None):
    tmp, here = build_tree(cases, logs, failed, manifest)
    try:
        code, out = run_verifier(here, argv)
    except Exception as e:
        code, out = f'crash {type(e).__name__}: {e}', {}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = (isinstance(code, int) and code != 0) if want == 'nonzero' else code == want
    det = f'exit {code} (want {want})'
    if ok and check is not None:
        ok, d2 = check(out); det += '; ' + d2
    return (name, ok, det)


def verifier_tests():
    T = []
    T.append(vt('U00 control: clean start + ramp_down + dip restart 60.5 ms with fresh manifest -> exit 0',
                {'s': START, 'r': RDOWN, 'd': DIP}, {'s': start_meas(), 'r': rdown_meas(), 'd': dip_meas()}, 0))
    m = start_meas(); m.pop('OUTA_R1')
    T.append(vt('U03a start: OUTA_R1 missing -> exit != 0 (60 ms check must not be skipped)', {'s': START}, {'s': m}, 'nonzero'))
    m = start_meas(); m.pop('OUTA_R1')
    T.append(vt('U03b start: OUTA_R1 failed! -> exit != 0', {'s': START}, {'s': m}, 'nonzero', failed={'s': ['OUTA_R1']}))
    T.append(vt('U03c start: EN_R1 - OUTA_R1 = 59 ms -> exit != 0 (control of the gate itself)',
                {'s': START}, {'s': start_meas(EN_R1=0.060, OUTA_R1=0.001)}, 'nonzero'))
    m = rdown_meas(); m.pop('VIN_AT_SHUTDOWN')
    T.append(vt('U03d ramp_down: EN_F1 present, VIN_AT_SHUTDOWN missing -> exit != 0', {'r': RDOWN}, {'r': m}, 'nonzero'))
    m = rdown_meas(); m.pop('VIN_AT_SHUTDOWN')
    T.append(vt('U03e ramp_down: VIN_AT_SHUTDOWN failed! -> exit != 0', {'r': RDOWN}, {'r': m}, 'nonzero',
                failed={'r': ['VIN_AT_SHUTDOWN']}))
    m = rdown_meas(); m.pop('VIN_AT_SHUTDOWN')
    T.append(vt('U03f mb_hold: EN_F1 present, VIN_AT_SHUTDOWN missing -> exit != 0', {'h': MBH}, {'h': m}, 'nonzero'))
    T.append(vt('U05a dip: restart 16.1 ms after VIN restoration -> exit != 0', {'d': DIP}, {'d': dip_meas(delay=0.0161)}, 'nonzero'))
    T.append(vt('U05b dip: restart 21 us (EN pulse) after VIN restoration -> exit != 0', {'d': DIP}, {'d': dip_meas(delay=21e-6)}, 'nonzero'))
    m = dip_meas(); m.pop('OUTA_R2'); m.pop('OUTA_RLAST')
    T.append(vt('U05c dip: restart without OUTA restoration measurement -> exit != 0', {'d': DIP}, {'d': m}, 'nonzero'))
    T.append(vt('U05d dip: ride-through (no EN fall) -> no restart gate, exit 0', {'d': DIP}, {'d': dip_meas(restart=False)}, 0))
    # ---- UVLO-04 stale logs / failed run
    T.append(vt('M1 no run-manifest.json -> exit != 0', {'s': START}, {'s': start_meas()}, 'nonzero', manifest=None))

    def bad_log(mf):
        mf['runs']['uvlo-s']['log_sha256'] = '0' * 64; return mf
    T.append(vt('M2 log SHA-256 differs from the manifest (stale/replaced log) -> exit != 0', {'s': START}, {'s': start_meas()}, 'nonzero',
                manifest=bad_log))

    def bad_deck(mf):
        mf['runs']['uvlo-s']['deck_sha256'] = '1' * 64; return mf
    T.append(vt('M3 deck SHA-256 differs from the manifest (log from an older deck) -> exit != 0', {'s': START}, {'s': start_meas()},
                'nonzero', manifest=bad_deck))
    T.append(vt('M4 unknown locked run id -> exit 2 with precheck error', {'s': START},
                {'s': start_meas()}, 2, argv=['--run-id', 'run-999'],
                check=lambda out: ('LOCKED_RUN_PRECHECK' in out.get('_stderr', ''),
                                   'unknown locked run must be rejected before legacy input is parsed')))
    T.append(vt('M4b legacy manifest run id is NOT a locked 259-deck run -> exit 2',
                {'s': START}, {'s': start_meas()}, 2, argv=['--run-id', 'run-123'],
                check=lambda out: ('LOCKED_RUN_PRECHECK' in out.get('_stderr', ''),
                                   'missing locked run must be rejected before any historical output write')))

    def bad_rc(mf):
        mf['runs']['uvlo-s']['rc'] = 1; return mf
    T.append(vt('M5 manifest rc = 1 for a deck (ngspice failed) -> exit != 0', {'s': START}, {'s': start_meas()}, 'nonzero', manifest=bad_rc))

    def missing_entry(mf):
        mf['runs'].pop('uvlo-r'); return mf
    T.append(vt('M6 deck/case missing from the manifest (partial run) -> exit != 0', {'s': START, 'r': RDOWN},
                {'s': start_meas(), 'r': rdown_meas()}, 'nonzero', manifest=missing_entry))

    def bad_cases(mf):
        mf['cases_sha256'] = '2' * 64; return mf
    T.append(vt('M6b case table changed after the run -> exit != 0', {'s': START}, {'s': start_meas()}, 'nonzero', manifest=bad_cases))
    # ---- provisional R-DIP screen (report-only)
    def screen(want):
        def f(out):
            s = out.get('summary', {}).get('provisional_rdip_screen', {})
            got = s.get('cases', {}).get('d', {}).get('status') if isinstance(s, dict) else None
            return got == want, f'screen={got} (want {want})'
        return f
    T.append(vt('R1 R-DIP screen: peak 11.41 V, 0.5 ms above, back in 3 ms -> PASS, exit 0', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK=11.41, RD_ABOVE_FIRST=0.2604, RD_ABOVE_LAST=0.2609, RD_T_ABOVE=0.0005)}, 0,
                check=screen('PASS')))
    T.append(vt('R2 R-DIP screen: 1.5 ms above 11.1605 V -> FAIL (report-only, exit 0)', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK=11.41, RD_ABOVE_FIRST=0.2604, RD_ABOVE_LAST=0.2619, RD_T_ABOVE=0.0015)}, 0,
                check=screen('FAIL')))
    T.append(vt('R3 R-DIP screen: peak 11.6 V -> FAIL (report-only, exit 0)', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK=11.6, RD_ABOVE_FIRST=0.2604, RD_ABOVE_LAST=0.2606, RD_T_ABOVE=0.0002)}, 0,
                check=screen('FAIL')))
    T.append(vt('R4 R-DIP screen: above-threshold timing missing while peak > 11.1605 V -> UNDETERMINED', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK=11.41)}, 0, check=screen('UNDETERMINED')))
    return T


FAKE_NG = '''#!/bin/sh
if [ "$1" = "-v" ]; then echo "** ngspice-fake : test"; exit 0; fi
echo "fake run"
%s
exit %d
'''


def runner_test(name, fake, code=0, exists=True, want_nonzero=True):
    """Re-use the fixed 259-deck synthetic runner fixture; historical outputs are immutable."""
    fixture = load('uvlo_locked_runner_fixture_t2', PKG / 'test_locked_runner.py')
    obj = fixture.LockedRunnerTests('test_acceptance_runner_isolated_and_uniform')
    obj.setUp()
    try:
        if not exists:
            result = obj.execute(ident='rid-1', PDU_NGSPICE='/nonexistent/runner')
        elif code:
            result = obj.execute(ident='rid-1', FAKE_ABORT='1')
        else:
            result = obj.execute(ident='rid-1')
        dst = obj.pkg / 'results/runs/rid-1'
        mf = dst / 'run-manifest.json'
        problems = []
        if want_nonzero and result.returncode == 0:
            problems.append('failed/absent solver reported rc 0')
        if not want_nonzero and result.returncode != 0:
            problems.append(f'complete synthetic run reported rc {result.returncode}')
        if obj.old.read_text() != 'historical preserved':
            problems.append('historical log changed')
        if (obj.pkg / 'results/run-manifest.json').read_text() != '{"run_id":"history"}' + chr(10):
            problems.append('historical manifest changed')
        if not exists:
            if dst.exists():
                problems.append('failed preflight created a run')
        else:
            if not mf.is_file():
                problems.append('isolated run manifest missing')
            else:
                data = json.loads(mf.read_text())
                if data.get('run_id') != 'rid-1' or len(data.get('runs', {})) != 259:
                    problems.append('wrong locked run id/deck count')
                expected_status = 'INCOMPLETE' if code else 'COMPLETE'
                if data.get('status') != expected_status:
                    problems.append('wrong incomplete/complete status')
                if code and data.get('runner_exit_code') != 2:
                    problems.append('incomplete run not flagged rc 2')
                if not code and not all(r.get('tmax') == '100n' and r.get('method') == 'gear'
                                        for r in data['runs'].values()):
                    problems.append('unlocked solver/tmax')
        return name, not problems, f'rc {result.returncode}; ' + ('; '.join(problems) or 'ok')
    except Exception as exc:
        return name, False, f'crash {type(exc).__name__}: {exc}'
    finally:
        obj.doCleanups()


def runner_tests():
    return [
        runner_test('M7a runner: missing ngspice -> no new run, historical files preserved', '', exists=False),
        runner_test('M7b runner: aborted fake solver -> isolated INCOMPLETE, history preserved',
                    'fake abort', 1),
        runner_test('M8 runner: 259 fixed synthetic decks -> isolated COMPLETE, history preserved',
                    'fake completion', 0, want_nonzero=False),
    ]


def workflow_tests():
    wf = (REPO / '.github' / 'workflows' / 'proposal-ngspice.yml').read_text()
    job = wf[wf.index('\n  uvlo:'):]
    res = []
    res.append(('W1 CI uvlo job: no "|| true" (install failure must fail the job)', '|| true' not in job,
                'found' if '|| true' in job else 'absent'))
    res.append(('W2 CI uvlo job: no continue-on-error (failed ngspice run must fail the job)', 'continue-on-error' not in job,
                'found' if 'continue-on-error' in job else 'absent'))
    res.append(('W3 CI uvlo job: verifier bound to this run (--run-id)', bool(re.search(r'verify_uvlo\.py[^\n]*--run-id', job)),
                'ok' if re.search(r'verify_uvlo\.py[^\n]*--run-id', job) else 'missing'))
    res.append(('W4 CI uvlo job: runner gets the same run id', bool(re.search(r'run_uvlo\.py[^\n]*--run-id', job)),
                'ok' if re.search(r'run_uvlo\.py[^\n]*--run-id', job) else 'missing'))
    return res


def budget_tests():
    with contextlib.redirect_stdout(io.StringIO()):
        b = load('uvlo_budget_t2', PKG / 'uvlo_budget.py')
    ch = b.CHOSEN_C3
    V = b.c3_vertices(ch['Rt'], ch['Rb'], ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'], detail=True)
    opp = any((v['IS_U'] != 0 and v['IM_U'] != 0 and (v['IS_U'] > 0) != (v['IM_U'] > 0)) for v in V)
    res = [('B3 UVLO-01: IN+ / IN- bias and leakage signs independent (opposite-sign vertices exist)', opp,
            f'{len(V)} vertices, opposite-sign vertex present={opp}')]
    return res


def main():
    rows = verifier_tests() + runner_tests() + workflow_tests() + budget_tests()
    for n, ok, d in rows:
        print(('OK  ' if ok else 'BAD ') + n + '  -> ' + d)
    bad = sum(1 for _, ok, _ in rows if not ok)
    print(f'{len(rows) - bad}/{len(rows)} OK')
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
