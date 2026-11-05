#!/usr/bin/env python3
"""PKG-03 independent verifier provenance tests using a fake ngspice fixture.
NO real PDU simulation is performed; full electrical acceptance is not asserted.
"""
import importlib.util
import json
import shutil
import unittest
from pathlib import Path
import test_locked_runner as fixtures

HERE = Path(__file__).resolve().parent


class VerifierProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.LockedRunnerTests('test_acceptance_runner_isolated_and_uniform')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        shutil.copyfile(HERE / 'verify_uvlo.py', self.f.pkg / 'verify_uvlo.py')
        fixtures.call('git', 'add', '.', cwd=self.f.root)
        commit = fixtures.call('git', 'commit', '-qm', 'synthetic fixture verifier', cwd=self.f.root)
        self.assertEqual(commit.returncode, 0, commit.stderr)
        result = self.f.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        spec = importlib.util.spec_from_file_location('fixture_verifier', self.f.pkg / 'verify_uvlo.py')
        self.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.v)
        output = self.f.pkg / 'results/runs/safe-a'
        self.v.HERE = self.f.pkg
        self.v.MANIFEST = output / 'run-manifest.json'
        self.v.LOGS = output / 'logs'
        self.v.STAGED = output / 'staged'
        self.manifest = json.loads(self.v.MANIFEST.read_text())
        self.cases = json.loads((self.f.pkg / 'test-cases-uvlo.json').read_text())['cases']

    def errors(self):
        return self.v.provenance(self.cases, 'safe-a')[0]

    def patch_manifest(self, **updates):
        self.manifest.update(updates)
        self.v.MANIFEST.write_text(json.dumps(self.manifest))

    def test_clean_synthetic_manifest_has_only_valid_provenance(self):
        self.assertEqual(self.errors(), [])

    def test_incomplete_manifest_rejected(self):
        self.patch_manifest(status='RUNNING', runner_exit_code=None)
        self.assertTrue(self.errors())

    def test_tampered_staged_deck_rejected(self):
        path = self.v.STAGED / 'uvlo-case000.cir'
        path.write_text(path.read_text().replace('100n', '500n', 1))
        self.assertTrue(any('staged deck' in x for x in self.errors()))

    def test_tampered_log_rejected(self):
        (self.v.LOGS / 'uvlo-case000.log').write_text('bad log')
        self.assertTrue(any('log missing' in x for x in self.errors()))

    def test_wrong_solver_rejected(self):
        self.patch_manifest(method='trap')
        self.assertTrue(any('solver/tmax' in x for x in self.errors()))

    def test_missing_case_rejected(self):
        del self.manifest['runs']['uvlo-case000']
        self.v.MANIFEST.write_text(json.dumps(self.manifest))
        self.assertTrue(any('259-case' in x for x in self.errors()))

    def test_input_mutation_rejected(self):
        (self.f.pkg / 'pdu-uvlo-block.inc').write_text('modified during run')
        self.assertTrue(any('source verification failed' in x or 'dirty/untracked' in x
                            for x in self.errors()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
