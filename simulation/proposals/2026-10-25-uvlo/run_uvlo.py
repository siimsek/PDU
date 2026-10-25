#!/usr/bin/env python3
"""Run every WP2 UVLO ngspice deck (parallel), store logs in results/logs/, write results/run-manifest.json.
Usage: python3 run_uvlo.py [-j N] [--run-id ID] [name-substring ...]

Stale-output protection (ChatGPT review 6395614957, UVLO-04): BEFORE anything else the runner deletes every old log,
the old run-manifest.json and the old uvlo-verify.json, so a failed or partial run can never leave old logs behind for
the verifier. The manifest is rewritten from scratch (no merge with an older run) and binds the run to a run id
(--run-id, env UVLO_RUN_ID, or a random uuid), the git HEAD, the package-input dirty flag, the case table SHA-256,
and per deck: deck SHA-256, log SHA-256, process return code and completion flag. A name filter produces a manifest
flagged partial=true, which the verifier refuses.
Exit: 0 = every deck process returned 0 and completed; 2 = at least one deck failed/incomplete; 3 = ngspice not
runnable (no deck run). The verifier decides PASS/FAIL."""
import subprocess, sys, json, time, hashlib, os, uuid, datetime, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).absolute().parent
NG = os.environ.get('PDU_NGSPICE', 'ngspice')
DECKS = HERE / 'decks'; LOGS = HERE / 'results' / 'logs'
MF = HERE / 'results' / 'run-manifest.json'; VJ = HERE / 'results' / 'uvlo-verify.json'
CMD = ['-b', '-D', 'ngbehavior=ltpsa']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def completed(out):
    return 'Total analysis time' in out and 'simulation(s) aborted' not in out and 'Timestep too small' not in out


def git(*a):
    try:
        r = subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ''
    except OSError:
        return ''


def run(deck):
    log = LOGS / (deck.stem + '.log')
    t0 = time.time()
    try:
        r = subprocess.run([NG, *CMD, deck.name], cwd=DECKS, capture_output=True, text=True, timeout=3000)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or '') if isinstance(e.stdout, str) else '', 'timeout'
    except OSError as e:
        out, rc = f'runner: cannot execute {NG}: {e}\n', 'exec-error'
    log.write_text(out)
    return deck.stem, dict(rc=rc, completed=completed(out) and rc == 0, elapsed_s=round(time.time() - t0, 1),
                           deck_sha256=sha(deck), log_sha256=sha(log))


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def main():
    args = sys.argv[1:]; j = 6; run_id = os.environ.get('UVLO_RUN_ID') or ''
    while args[:1] and args[0] in ('-j', '--run-id'):
        if args[0] == '-j': j = int(args[1])
        else: run_id = args[1]
        args = args[2:]
    run_id = run_id or 'local-' + uuid.uuid4().hex[:12]
    # 1) remove every old output first (stale-log protection)
    LOGS.mkdir(parents=True, exist_ok=True)
    for p in LOGS.glob('*.log'):
        p.unlink()
    for p in (MF, VJ):
        if p.exists(): p.unlink()
    decks = sorted(d for d in DECKS.glob('*.cir') if not args or any(a in d.name for a in args))
    cases = HERE / 'test-cases-uvlo.json'
    mf = dict(run_id=run_id, started_utc=utc(), git_head=git('rev-parse', 'HEAD'),
              package_inputs_dirty_at_run=git('status', '--porcelain', '--', '.', ':(exclude)results') != '',
              cases_sha256=sha(cases) if cases.exists() else None, partial=bool(args), filters=args,
              command='ngspice ' + ' '.join(CMD) + ' <deck>', cpus=os.cpu_count(), ngspice=None, runs={})
    # 2) ngspice must be runnable, otherwise fail (no deck counted as run)
    exe = shutil.which(NG) if os.sep not in NG else (NG if os.access(NG, os.X_OK) else None)
    if exe is None:
        mf.update(error=f'ngspice not runnable: {NG!r}', runner_exit_code=3, finished_utc=utc())
        MF.write_text(json.dumps(mf, indent=1)); print(mf['error'], file=sys.stderr); sys.exit(3)
    try:
        v = subprocess.run([exe, '-v'], capture_output=True, text=True, timeout=60)
        mf['ngspice'] = [l for l in (v.stdout + v.stderr).splitlines() if 'ngspice' in l]
    except (OSError, subprocess.TimeoutExpired) as e:
        mf.update(error=f'ngspice -v failed: {e}', runner_exit_code=3, finished_utc=utc())
        MF.write_text(json.dumps(mf, indent=1)); print(mf['error'], file=sys.stderr); sys.exit(3)
    if not decks:
        mf.update(error='no decks', runner_exit_code=2, finished_utc=utc()); MF.write_text(json.dumps(mf, indent=1)); sys.exit(2)
    with ThreadPoolExecutor(j) as ex:
        for name, r in ex.map(run, decks):
            mf['runs'][name] = r; print(name, r['rc'], r['completed'], r['elapsed_s'], flush=True)
    code = 0 if all(r['rc'] == 0 and r['completed'] for r in mf['runs'].values()) else 2
    mf.update(runner_exit_code=code, finished_utc=utc())
    MF.write_text(json.dumps(mf, indent=1))
    sys.exit(code)


if __name__ == '__main__':
    main()
