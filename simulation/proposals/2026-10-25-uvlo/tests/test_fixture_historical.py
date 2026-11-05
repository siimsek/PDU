"""Regression tests for historical fixture real Git provenance (no ngspice)."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from fixture_historical import bind_historical_fixture_git


class HistoricalGitFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.here = self.root / 'simulation/proposals/2026-10-25-uvlo'
        self.here.mkdir(parents=True)
        (self.here / 'results').mkdir()
        (self.here / 'test-cases-uvlo.json').write_text('{"cases":{"s":{"kind":"start"}}}')
        self.manifest = self.here / 'results' / 'run-manifest.json'
        self.manifest.write_text('{"git_head":"","runs":{"uvlo-s":{"rc":0}},"runner_exit_code":0}')

    def git(self, *args):
        p = subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True)
        return p.stdout.strip()

    def test_bound_head_is_real_first_commit(self):
        base = bind_historical_fixture_git(self.here)
        self.assertEqual(base, json.loads(self.manifest.read_text())['git_head'])
        self.assertEqual(len(base), 40)
        self.assertNotEqual(base, self.git('rev-parse', 'HEAD'))

    def test_only_historical_result_manifest_committed_after_base(self):
        base = bind_historical_fixture_git(self.here)
        self.assertEqual(self.git('diff', '--name-only', base, 'HEAD'),
                         'simulation/proposals/2026-10-25-uvlo/results/run-manifest.json')
        self.assertEqual(subprocess.run(['git','diff','--name-only',base,'HEAD','--','.',':(exclude)results'],
                         cwd=self.here, capture_output=True, text=True).stdout.strip(), '')

    def test_no_dirty_or_untracked_inputs(self):
        bind_historical_fixture_git(self.here)
        self.assertEqual(self.git('status', '--porcelain', '--untracked-files=all'), '')

    def test_cannot_rebind_existing_test_repo(self):
        bind_historical_fixture_git(self.here)
        with self.assertRaises(ValueError):
            bind_historical_fixture_git(self.here)

    def test_missing_manifest_stays_missing(self):
        self.manifest.unlink()
        base = bind_historical_fixture_git(self.here)
        self.assertEqual(self.git('rev-parse', 'HEAD'), base)
        self.assertFalse(self.manifest.exists())

    def test_malformed_manifest_rejected(self):
        self.manifest.write_text('{bad-json')
        with self.assertRaises(json.JSONDecodeError):
            bind_historical_fixture_git(self.here)

    def test_wrong_directory_rejected(self):
        with self.assertRaises(ValueError):
            bind_historical_fixture_git(self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
