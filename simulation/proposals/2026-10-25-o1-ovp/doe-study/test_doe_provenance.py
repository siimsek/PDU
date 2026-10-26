#!/usr/bin/env python3
"""WP1 Tur-12 (review 6416795114, WP1-T12-02) tests, written BEFORE the fix (first run on 927d7cd).
The DOE runner must record its own provenance: runner SHA-256, git HEAD and package git status at start AND end, the full
command line; and a consistency verdict (same HEAD, same runner hash, runner tracked and clean, inputs clean) that is
False whenever any of these differ. Exit 0 = all OK. Stdlib only."""
import importlib.util, sys
from pathlib import Path
HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('doe_t12', HERE / 'doe_study.py'); ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
res = []
f = getattr(ds, 'provenance', None)
p = f() if f else {}
need = {'runner_sha256', 'git_head', 'git_status_porcelain', 'runner_tracked', 'argv', 'time'}
res.append(('P1 provenance() records runner sha256 / HEAD / git status / tracked / argv / time', need <= set(p), sorted(p)))
c = getattr(ds, 'provenance_consistent', None)
ok = False
if c and p:
    good = dict(p, git_status_porcelain='', runner_tracked=True)
    ok = (c(good, dict(good)) is True and c(good, dict(good, git_head='x')) is False
          and c(good, dict(good, runner_sha256='y')) is False and c(dict(good, runner_tracked=False), dict(good, runner_tracked=False)) is False
          and c(dict(good, git_status_porcelain=' M doe_study.py'), dict(good)) is False)
res.append(('P2 provenance_consistent(): True only for same HEAD + same runner hash + tracked + clean', ok, None))
for n, ok, d in res:
    print(('OK   ' if ok else 'FAIL ') + n + (f'  [{d}]' if not ok and d is not None else ''))
print(f"{sum(r[1] for r in res)}/{len(res)} OK")
sys.exit(0 if all(r[1] for r in res) else 1)
