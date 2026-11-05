#!/usr/bin/env python3
"""PKG-03 independent verifier provenance tests using a fake ngspice fixture.
NO real PDU simulation is performed; full electrical acceptance is not asserted.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
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
        # Full verifier serializes SHA-256 for these tracked model/budget fixtures.
        # Stub content is intentionally NOT a real circuit or ngspice result.
        sim = self.f.root / 'simulation'
        for name in ('pdu-behavioral.lib', 'pdu-inductor-ng.lib'):
            (sim / name).write_text('* fake model fixture' + chr(10))
        o1 = sim / 'proposals' / '2026-10-25-o1-ovp'
        o1.mkdir(parents=True, exist_ok=True)
        for name in ('pdu-o1ovp-behavioral.lib', 'pdu-o1ovp-block.inc',
                     'pdu-circuit-o1ovp.inc', 'pdu-efuse-block-o1ovp.inc'):
            (o1 / name).write_text('* fake O1 model fixture' + chr(10))
        (self.f.pkg / 'results' / 'uvlo-budget.json').write_text('{}' + chr(10))
        # Historical sentinel is tracked BEFORE runner manifest captures the clean HEAD.
        (self.f.pkg / 'results' / 'uvlo-verify.json').write_bytes(b'IMMUTABLE EVIDENCE' + bytes([10]))
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

    def test_full_verifier_cli_fails_closed_on_unmeasured_fake_decks(self):
        """All 259 fake deck logs are complete, but missing electrical metrics MUST fail."""
        historical = self.f.pkg / 'results/uvlo-verify.json'
        historical.write_bytes(b'IMMUTABLE EVIDENCE' + bytes([10]))
        run = subprocess.run(
            [sys.executable, str(self.f.pkg / 'verify_uvlo.py'), '--run-id', 'safe-a'],
            cwd=self.f.root, env=self.f.env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 1, run.stdout[-1000:] + run.stderr)
        artifact = self.f.pkg / 'results/runs/safe-a/uvlo-verify.json'
        self.assertTrue(artifact.is_file(), run.stderr)
        summary = json.loads(artifact.read_text())['summary']
        self.assertEqual(summary['mode'], 'acceptance')
        self.assertEqual(summary['n_cases'], 259)
        self.assertEqual(len(summary['acceptance_fail']), 259)
        self.assertEqual(summary['provenance_errors'], [])
        self.assertEqual(historical.read_bytes(), b'IMMUTABLE EVIDENCE' + bytes([10]))

    def test_full_verifier_cli_rejects_incomplete_manifest(self):
        self.patch_manifest(status='INCOMPLETE', runner_exit_code=2)
        run = subprocess.run(
            [sys.executable, str(self.f.pkg / 'verify_uvlo.py'), '--run-id', 'safe-a'],
            cwd=self.f.root, env=self.f.env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stdout[-1000:] + run.stderr)
        summary = json.loads((self.f.pkg / 'results/runs/safe-a/uvlo-verify.json').read_text())['summary']
        self.assertTrue(summary['provenance_errors'])
        self.assertEqual(summary['exit_code'], 2)

    def test_unknown_run_id_returns_2_without_overwriting_legacy_evidence(self):
        historical = self.f.pkg / 'results/uvlo-verify.json'
        historical.write_text('IMMUTABLE HISTORICAL SUMMARY\\n')
        result = subprocess.run(
            [sys.executable, str(self.f.pkg / 'verify_uvlo.py'), '--run-id', 'absent-pkg05'],
            cwd=self.f.root, env=self.f.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('LOCKED_RUN_PRECHECK', result.stderr)
        self.assertEqual(historical.read_text(), 'IMMUTABLE HISTORICAL SUMMARY\\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
