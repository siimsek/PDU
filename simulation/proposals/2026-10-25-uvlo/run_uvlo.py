#!/usr/bin/env python3
"""Locked WP2 259-deck Gear/tmax=100 ns runner. Historical results are read-only.

Usage: python3 run_uvlo.py --run-id UNIQUE [-j N]
Outputs: results/runs/UNIQUE/{staged,logs,run-manifest.json}.
A RUNNING/partial/failed manifest is never an acceptance result. Real ngspice and
independent verify_uvlo.py --run-id UNIQUE are required for acceptance.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DECKS = HERE / 'decks'
RUN_ROOT = HERE / 'results' / 'runs'
LOCK = ROOT / 'docs/proposals/2026-10-25-uvlo/PKG02-PROTOCOL-LOCK.json'
CMD = ['-b', '-D', 'ngbehavior=ltpsa']
TRAN = re.compile(r'^(\s*\.tran\s+\S+\s+\S+\s+\S+\s+)(\S+)([^\r\n]*)$', re.I | re.M)
INCLUDE = re.compile(r'^(\s*\.include\s+)(\S+)([^\r\n]*)$', re.I | re.M)
RUN_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def blob(p):
    data = Path(p).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def git(*args):
    proc = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if proc.returncode:
        raise RuntimeError('git ' + ' '.join(args) + ': ' + proc.stderr.strip())
    return proc.stdout.strip()


def clean_status():
    # Exclude ONLY new immutable run outputs. Untracked inputs, old results, model
    # or script edits anywhere else remain fatal. --untracked-files=all is required.
    return git('status', '--porcelain', '--untracked-files=all', '--', '.',
               ':(exclude)simulation/proposals/2026-10-25-uvlo/results/runs')


def locked_inputs(lock):
    if lock.get('schema') != 'pdu-pkg02-static-input-lock-v1':
        raise ValueError('unexpected protocol lock schema')
    desc = lock.get('full_acceptance') or {}
    expected = desc.get('decks') or {}
    if desc.get('expected_decks') != 259 or len(expected) != 259:
        raise ValueError('fixed 259 deck matrix missing')
    if desc.get('candidate_method') != 'gear' or desc.get('max_internal_timestep') != '100n':
        raise ValueError('Gear/100n matrix lock mismatch')
    found = {p.name: p for p in DECKS.glob('*.cir')}
    if set(expected) != set(found):
        raise ValueError('missing/extra decks vs locked 259 matrix')
    cases_path = HERE / 'test-cases-uvlo.json'
    actual = json.loads(cases_path.read_text())['cases']
    if {f'uvlo-{x}.cir' for x in actual} != set(expected):
        raise ValueError('case-table vs locked 259 deck names mismatch')
    for name, expected_sha in expected.items():
        if blob(found[name]) != expected_sha:
            raise ValueError('deck blob differs from PKG-02 lock: ' + name)
    for entry in lock.get('source_inputs_git_blobs', []):
        path = (ROOT / entry['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or blob(path) != entry['git_blob_sha1']:
            raise ValueError('input blob differs from PKG-02 lock: ' + entry['path'])
    return [found[n] for n in sorted(found)]


def stage_text(source):
    if len(TRAN.findall(source)) != 1:
        raise ValueError('expected exactly one explicit .tran with tmax')
    if len(re.findall(r'^\s*\.options\s+.*method=gear\b', source, re.I | re.M)) != 1:
        raise ValueError('expected exactly one Gear solver option')
    rendered = TRAN.sub(lambda m: m.group(1) + '100n' + m.group(3), source)

    def absolute_include(m):
        original = m.group(2)
        path = original.strip('"\'')
        target = Path(path)
        if not target.is_absolute():
            target = (DECKS / target).resolve()
        if not target.is_relative_to(ROOT) or not target.is_file():
            raise ValueError('invalid or missing include: ' + original)
        return m.group(1) + str(target) + m.group(3)

    rendered = INCLUDE.sub(absolute_include, rendered)
    if len(TRAN.findall(rendered)) != 1 or TRAN.search(rendered).group(2).lower() != '100n':
        raise ValueError('uniform tmax 100n staging failed')
    return rendered


def completed(log_text, rc):
    return rc == 0 and 'Total analysis time' in log_text and not any(
        s in log_text for s in ('simulation(s) aborted', 'Timestep too small', 'singular matrix'))


def run_one(job):
    name, staged, logdir, exe = job
    t0 = time.monotonic()
    try:
        p = subprocess.run([exe, *CMD, staged.name], cwd=staged.parent, capture_output=True,
                           text=True, timeout=3000, check=False)
        stdout, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, rc = f'runner timeout: {exc}\n', 'timeout'
    except OSError as exc:
        stdout, rc = f'runner execution error: {exc}\n', 'exec-error'
    log = logdir / f'{name}.log'
    with log.open('x') as fd:
        fd.write(stdout)
    return name, dict(rc=rc, completed=completed(stdout, rc),
                      elapsed_s=round(time.monotonic() - t0, 2),
                      source_deck_sha256=sha(DECKS / staged.name),
                      deck_sha256=sha(staged), log_sha256=sha(log),
                      source_deck_git_blob=blob(DECKS / staged.name),
                      tmax='100n', method='gear')


def write_json(path, obj):
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('-j', type=int, default=6)
    args = ap.parse_args(argv)
    if not RUN_ID.fullmatch(args.run_id) or args.j < 1 or args.j > 32:
        ap.error('invalid run-id or workers (must be 1..32)')
    dst = RUN_ROOT / args.run_id
    if dst.exists():
        print('run-id already exists; refusing any overwrite: ' + str(dst), file=sys.stderr)
        return 3
    try:
        if clean_status():
            raise ValueError('dirty/untracked repository inputs: ' + clean_status()[:350])
        head = git('rev-parse', 'HEAD')
        lock = json.loads(LOCK.read_text())
        decks = locked_inputs(lock)
        exe_name = os.environ.get('PDU_NGSPICE', 'ngspice')
        exe = shutil.which(exe_name)
        if exe is None:
            raise ValueError('ngspice unavailable: ' + exe_name)
        ver = subprocess.run([exe, '-v'], capture_output=True, text=True, timeout=60, check=False)
        version = (ver.stdout + ver.stderr).strip()
        if ver.returncode != 0 or 'ngspice' not in version.lower():
            raise ValueError('ngspice version probe failed')
    except (ValueError, OSError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print('PRECONDITION FAILED: ' + str(exc), file=sys.stderr)
        return 3

    # Atomic single-writer guard. Interrupted runs retain this guard for inspection;
    # never infer that an interrupted acceptance run is complete.
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    active = RUN_ROOT / '.active-acceptance.lock'
    try:
        with active.open('x') as file:
            file.write(json.dumps(dict(run_id=args.run_id, head=head, started_utc=utc(), pid=os.getpid())))
    except FileExistsError:
        print('another run / unresolved interrupted run exists: ' + str(active), file=sys.stderr)
        return 3
    try:
        dst.mkdir(exist_ok=False)
        staged_dir = dst / 'staged'
        staged_dir.mkdir()
        logs_dir = dst / 'logs'
        logs_dir.mkdir()
        manifest_path = dst / 'run-manifest.json'
        mf = dict(run_id=args.run_id, status='RUNNING', git_head=head, started_utc=utc(),
                  package_inputs_dirty_at_run=False, cases_sha256=sha(HERE / 'test-cases-uvlo.json'),
                  protocol_lock_sha256=sha(LOCK), tmax='100n', method='gear',
                  partial=False, filters=[], command='ngspice -b -D ngbehavior=ltpsa <staged-deck>',
                  ngspice=version.splitlines(), runner_sha256=sha(__file__),
                  expected_decks=259, runner_exit_code=None, runs={})
        # Stage all 259 before any ngspice. No mutation of the immutable source decks.
        for deck in decks:
            (staged_dir / deck.name).write_text(stage_text(deck.read_text()))
        write_json(manifest_path, mf)
        jobs = [(d.stem, staged_dir / d.name, logs_dir, exe) for d in decks]
        with ThreadPoolExecutor(max_workers=args.j) as pool:
            for name, result in pool.map(run_one, jobs):
                mf['runs'][name] = result
                write_json(manifest_path, mf)  # Retain partial progress on disk.
                print(name, result['rc'], result['completed'], flush=True)
        if git('rev-parse', 'HEAD') != head or clean_status() or sha(__file__) != mf['runner_sha256']:
            mf['error'] = 'HEAD/inputs/runner changed during run'
            code = 2
        else:
            try:
                locked_inputs(lock)
                code = 0 if len(mf['runs']) == 259 and all(
                    type(r['rc']) is int and r['rc'] == 0 and r['completed'] for r in mf['runs'].values()) else 2
            except (ValueError, KeyError) as exc:
                mf['error'] = 'input hash changed during run: ' + str(exc)
                code = 2
        mf.update(status='COMPLETE' if code == 0 else 'INCOMPLETE', runner_exit_code=code, finished_utc=utc())
        write_json(manifest_path, mf)
        active.unlink()
        return code
    except BaseException as exc:
        if 'mf' in locals() and 'manifest_path' in locals() and manifest_path.exists():
            mf.update(status='INTERRUPTED', error=str(exc), runner_exit_code=2, finished_utc=utc())
            write_json(manifest_path, mf)
        # Intentional: leave .active-acceptance.lock for forensic inspection on interruption.
        print('RUN INTERRUPTED (lock retained): ' + repr(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
