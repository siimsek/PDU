#!/usr/bin/env python3
"""PKG-03 synthetic preflight/runner tests. Fake ngspice is NOT a PDU simulation."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().with_name('run_uvlo.py')


def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def call(*a, cwd):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=False)


class LockedRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = self.root = Path(self.tmp.name) / 'repo'
        self.pkg = root / 'simulation/proposals/2026-10-25-uvlo'
        self.decks = self.pkg / 'decks'
        self.decks.mkdir(parents=True)
        self.runner = self.pkg / 'run_uvlo.py'
        shutil.copyfile(SOURCE, self.runner)
        (self.pkg / 'pdu-uvlo-block.inc').write_text('* stub\n')
        self.old = self.pkg / 'results/logs/historical.log'
        self.old.parent.mkdir(parents=True)
        self.old.write_text('historical preserved')
        (self.pkg / 'results/run-manifest.json').write_text('{"run_id":"history"}\n')
        self.case_keys = [f'case{i:03d}' for i in range(259)]
        for k in self.case_keys:
            (self.decks / f'uvlo-{k}.cir').write_text(
                '* source\n.options reltol=0.0001 abstol=1n method=gear\n'
                '.include ../pdu-uvlo-block.inc\n.tran 100n 0.3 0 1u\n.end\n')
        (self.pkg / 'test-cases-uvlo.json').write_text(json.dumps(dict(cases={k: dict() for k in self.case_keys})))
        lf = self.root / 'docs/proposals/2026-10-25-uvlo/PKG02-PROTOCOL-LOCK.json'
        lf.parent.mkdir(parents=True)
        self.lock = lf
        self.write_lock()
        self.exe = Path(self.tmp.name) / 'ngspice-fake'
        self.exe.write_text('#!/bin/sh\ncase "$*" in\n  *-v*) echo "ngspice-44.2 TEST STUB";;\n  *case000*) if [ "$FAKE_ABORT" = "1" ]; then echo "Timestep too small"; else echo "Total analysis time: 0.02"; fi;;\n  *) echo "Total analysis time: 0.02";;\nesac\n')
        self.exe.chmod(0o755)
        call('git', 'init', '-q', cwd=root)
        call('git', 'config', 'user.name', 'Fixture', cwd=root)
        call('git', 'config', 'user.email', 'fixture@localhost', cwd=root)
        (root / '.gitignore').write_text('**/__pycache__/\n**/*.pyc\n')
        call('git', 'add', '.', cwd=root)
        commit = call('git', 'commit', '-qm', 'fixture', cwd=root)
        assert commit.returncode == 0, commit.stderr
        self.env = dict(os.environ, PDU_NGSPICE=str(self.exe), PYTHONDONTWRITEBYTECODE='1')

    def write_lock(self):
        self.lock.write_text(json.dumps(dict(
            schema='pdu-pkg02-static-input-lock-v1',
            full_acceptance=dict(expected_decks=259, candidate_method='gear', max_internal_timestep='100n',
                                 decks={p.name: blob(p) for p in self.decks.glob('*.cir')}),
            source_inputs_git_blobs=[dict(path=str(self.runner.relative_to(self.root)), git_blob_sha1=blob(self.runner)),
                                     dict(path=str((self.pkg / 'pdu-uvlo-block.inc').relative_to(self.root)),
                                          git_blob_sha1=blob(self.pkg / 'pdu-uvlo-block.inc'))]
        ), indent=2))

    def execute(self, ident='safe-a', **more_env):
        env=dict(self.env, **more_env)
        return subprocess.run([sys.executable, str(self.runner), '--run-id', ident, '-j', '3'],
                              cwd=self.root, capture_output=True, text=True, env=env)

    def preserve(self):
        self.assertEqual(self.old.read_text(), 'historical preserved')
        self.assertEqual((self.pkg / 'results/run-manifest.json').read_text(), '{"run_id":"history"}\n')

    def test_acceptance_runner_isolated_and_uniform(self):
        p=self.execute()
        self.assertEqual(p.returncode,0,p.stderr+p.stdout[-500:])
        dst=self.pkg/'results/runs/safe-a'
        mf=json.loads((dst/'run-manifest.json').read_text())
        self.assertEqual(mf['runner_exit_code'],0)
        self.assertEqual(mf['status'],'COMPLETE')
        self.assertEqual(len(mf['runs']),259)
        self.assertFalse((dst.parent/'.active-acceptance.lock').exists())
        self.assertTrue(all(r['completed'] and r['tmax']=='100n' for r in mf['runs'].values()))
        st=(dst/'staged/uvlo-case000.cir').read_text()
        self.assertIn('.tran 100n 0.3 0 100n',st)
        self.assertIn(str(self.pkg/'pdu-uvlo-block.inc'),st)
        self.assertEqual((self.decks/'uvlo-case000.cir').read_text().splitlines()[3],'.tran 100n 0.3 0 1u')
        self.preserve()
        # Existing runs are NEVER overwritten.
        p2=self.execute()
        self.assertEqual(p2.returncode,3)
        self.assertEqual(mf,json.loads((dst/'run-manifest.json').read_text()))
        self.preserve()

    def test_timestep_abort_retained_and_never_complete(self):
        p=self.execute(FAKE_ABORT='1')
        self.assertEqual(p.returncode,2,p.stderr)
        mf=json.loads((self.pkg/'results/runs/safe-a/run-manifest.json').read_text())
        self.assertEqual(mf['status'],'INCOMPLETE')
        self.assertEqual(mf['runner_exit_code'],2)
        self.assertFalse(mf['runs']['uvlo-case000']['completed'])
        self.preserve()

    def test_missing_ngspice_fails_without_output(self):
        p=self.execute(PDU_NGSPICE='/nonexistent/ngspice')
        self.assertEqual(p.returncode,3)
        self.assertFalse((self.pkg/'results/runs/safe-a').exists())
        self.preserve()

    def test_dirty_input_fails_closed(self):
        with (self.pkg/'pdu-uvlo-block.inc').open('a') as f: f.write('changed\n')
        p=self.execute()
        self.assertEqual(p.returncode,3)
        self.assertFalse((self.pkg/'results/runs/safe-a').exists())
        self.preserve()

    def test_untracked_input_fails_closed(self):
        (self.pkg/'untracked.in').write_text('unexpected')
        self.assertEqual(self.execute().returncode,3)
        self.preserve()

    def test_deck_sha_mismatch_fails_closed_even_if_clean(self):
        deck=self.decks/'uvlo-case000.cir'
        deck.write_text(deck.read_text().replace('1u','2u'))
        call('git','add','.',cwd=self.root)
        call('git','commit','-qm','malicious deck',cwd=self.root)
        p=self.execute()
        self.assertEqual(p.returncode,3)
        self.assertIn('deck blob differs',p.stderr)
        self.preserve()

    def test_missing_deck_fails_closed(self):
        (self.decks/'uvlo-case010.cir').unlink()
        p=self.execute()
        self.assertEqual(p.returncode,3)
        self.preserve()

    def test_lock_prevents_concurrent_or_unresolved_run(self):
        runs=self.pkg/'results/runs';runs.mkdir(parents=True)
        active=runs/'.active-acceptance.lock'
        active.write_text('{"run_id":"previous"}')
        p=self.execute()
        self.assertEqual(p.returncode,3)
        self.assertTrue(active.exists())
        self.assertFalse((runs/'safe-a').exists())
        self.preserve()

    def test_run_id_traversal_and_filter_arguments_rejected(self):
        p=subprocess.run([sys.executable, str(self.runner), '--run-id','../../foo'],cwd=self.root,env=self.env,capture_output=True)
        self.assertNotEqual(p.returncode,0)
        p=subprocess.run([sys.executable, str(self.runner), '--run-id','safe-a','case000'],cwd=self.root,env=self.env,capture_output=True)
        self.assertNotEqual(p.returncode,0)
        self.preserve()


if __name__=='__main__':
    unittest.main(verbosity=2)
