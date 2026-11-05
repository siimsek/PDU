#!/usr/bin/env python3
"""Synthetic, no-ngspice tests: exact limits, log hashes and provenance fail-closed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import hashlib
import re
import sys

modpath = Path(__file__).with_name('study_integrity.py')
spec = importlib.util.spec_from_file_location('study_integrity_t7', modpath)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
results = []

def check(name, condition):
    results.append((name, bool(condition)))
    print(('OK   ' if condition else 'FAIL ') + name)

def rejected(fn):
    try:
        fn()
        return False
    except (ValueError, FileNotFoundError, KeyError):
        return True

check('N01 exactly 100 ns is inclusive', s.compare_printed('0.0920405', '0.0920404', 'time') == (s.LIMITS['time'], False, True))
check('N02 99 ns PASS', s.compare_printed('0.092040499', '0.092040400', 'time')[1] is False)
check('N03 101 ns FAIL', s.compare_printed('0.092040501', '0.092040400', 'time')[1] is True)
check('N04 negative printed values work as signed times', s.compare_printed('-0.000000050', '0', 'time')[1] is False)
check('N05 voltage 5 mV inclusive', s.compare_printed('10.005', '10.000', 'voltage')[1:] == (False, True))
check('N06 voltage >5 mV FAIL', s.compare_printed('10.005001', '10.000', 'voltage')[1] is True)
check('N07 NaN rejected', rejected(lambda: s.compare_printed('NaN', '1', 'time')))
check('N08 Inf rejected', rejected(lambda: s.compare_printed('Inf', '1', 'time')))
check('N09 malformed rejected', rejected(lambda: s.compare_printed('missing', '1', 'time')))
check('N10 missing raw string rejected', rejected(lambda: s.compare_printed(None, '1', 'time')))
check('N11 unknown measurement kind rejected', rejected(lambda: s.compare_printed('1', '1', 'current')))

with TemporaryDirectory() as td:
    root = Path(td); pkg = root / 'simulation' / 'proposals' / '2026-10-25-uvlo'
    out = pkg / 'results' / 'run-X'; out.mkdir(parents=True)
    log = out / 'case.gear.log'; log.write_text(' en_r1 = 9.20405e-2\n')
    digest = hashlib.sha256(log.read_bytes()).hexdigest()
    rows = [{'log': 'results/run-X/case.gear.log', 'log_sha256': digest}]
    p0 = dict(git_head='head', git_root=str(root), runner_sha256='runner', helper_sha256='helper', git_status_porcelain='', runner_tracked=True, helper_tracked=True)
    p1 = dict(p0, git_status_porcelain='?? simulation/proposals/2026-10-25-uvlo/results/run-X/case.gear.log\n')
    check('P01 new output with matching log SHA allowed', s.consistent(p0,p1,rows,pkg,out))
    check('P02 changed HEAD rejected', not s.consistent(p0,dict(p1,git_head='other'),rows,pkg,out))
    check('P03 changed runner rejected', not s.consistent(p0,dict(p1,runner_sha256='changed'),rows,pkg,out))
    check('P04 changed helper rejected', not s.consistent(p0,dict(p1,helper_sha256='changed'),rows,pkg,out))
    check('P05 untracked input rejected at start', not s.consistent(dict(p0,git_status_porcelain='?? simulation/proposals/new_input.cir\n'),p1,rows,pkg,out))
    check('P06 untracked extra output rejected', not s.consistent(p0,dict(p1,git_status_porcelain=p1['git_status_porcelain']+'?? simulation/proposals/2026-10-25-uvlo/results/run-X/extra.log\n'),rows,pkg,out))
    check('P07 modified tracked log rejected', not s.consistent(p0,dict(p1,git_status_porcelain=' M simulation/proposals/2026-10-25-uvlo/results/run-X/case.gear.log\n'),rows,pkg,out))
    check('P08 untracked input at end rejected', not s.consistent(p0,dict(p1,git_status_porcelain='?? simulation/proposals/new_input.cir\n'),rows,pkg,out))
    check('P09 untracked runner rejected', not s.consistent(dict(p0,runner_tracked=False),p1,rows,pkg,out))
    check('P10 hash mismatch rejected', not s.consistent(p0,p1,[dict(rows[0],log_sha256='a'*64)],pkg,out))
    check('P11 missing output rejected', not s.consistent(p0,p1,[dict(rows[0],log='results/run-X/missing.log')],pkg,out))
    check('P12 duplicate rows rejected', not s.consistent(p0,p1,rows+rows,pkg,out))
    check('P13 path traversal rejected', not s.consistent(p0,p1,[dict(rows[0],log='../evil.log')],pkg,out))
    check('P14 no rows rejected', not s.consistent(p0,p1,[],pkg,out))
    rex=re.compile(r'^\s*([a-z_][a-z0-9_]*)\s*=\s*([-+0-9.eE]+)',re.M)
    check('N12 older run raw readings reconstructed from hash-verified log', s.raw_measures(rows[0],pkg,rex)=={'en_r1':'9.20405e-2'})
    log.write_text(' en_r1 = 9.20406e-2\n')
    check('N13 altered historical log rejected', rejected(lambda:s.raw_measures(rows[0],pkg,rex)))

bad=[n for n,ok in results if not ok]
print(f'{len(results)-len(bad)}/{len(results)} PASS')
if bad:
    print('FAILED:',', '.join(bad))
sys.exit(bool(bad))
