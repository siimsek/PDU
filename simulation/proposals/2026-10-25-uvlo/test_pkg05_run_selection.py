#!/usr/bin/env python3
"""PKG-05: isolated verifier path selection; no ngspice or PDU acceptance."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('pkg05_verify', HERE / 'verify_uvlo.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class LockedRunSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_here = V.HERE
        self.addCleanup(lambda: setattr(V, 'HERE', self.old_here))
        V.HERE = Path(self.tmp.name) / 'repo' / 'simulation' / 'proposals' / '2026-10-25-uvlo'
        self.legacy = V.HERE / 'results' / 'uvlo-verify.json'
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_text('SENTINEL: historical evidence must be preserved\n')
        self.run = V.HERE / 'results' / 'runs' / 'clean-id'
        self.run.mkdir(parents=True)
        (self.run / 'logs').mkdir()
        (self.run / 'staged').mkdir()
        (self.run / 'run-manifest.json').write_text('{"status":"COMPLETE"}\n')

    def test_valid_locked_root_selects_isolated_paths(self):
        self.assertEqual(V.select_locked_run('clean-id'), (
            self.run / 'logs', self.run / 'run-manifest.json',
            self.run / 'uvlo-verify.json', self.run / 'staged'))
        self.assertEqual(self.legacy.read_text(), 'SENTINEL: historical evidence must be preserved\n')

    def test_missing_run_is_rejected_and_legacy_untouched(self):
        with self.assertRaises(FileNotFoundError):
            V.select_locked_run('absent')
        self.assertEqual(self.legacy.read_text(), 'SENTINEL: historical evidence must be preserved\n')

    def test_missing_manifest_fails_closed(self):
        (self.run / 'run-manifest.json').unlink()
        with self.assertRaises(FileNotFoundError):
            V.select_locked_run('clean-id')

    def test_missing_log_or_staged_directory_fails_closed(self):
        (self.run / 'logs').rmdir()
        with self.assertRaises(FileNotFoundError):
            V.select_locked_run('clean-id')
        (self.run / 'logs').mkdir()
        (self.run / 'staged').rmdir()
        with self.assertRaises(FileNotFoundError):
            V.select_locked_run('clean-id')

    def test_path_traversal_and_invalid_ids_rejected(self):
        for name in ('../history', '../../', '.hidden', 'bad/slash', '', 'space id', 'a' * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                V.select_locked_run(name)

    def test_symlinked_run_directory_rejected(self):
        (V.HERE / 'results' / 'runs' / 'evil').symlink_to(self.run, target_is_directory=True)
        with self.assertRaises(ValueError):
            V.select_locked_run('evil')

    def test_symlinked_manifest_rejected(self):
        (self.run / 'run-manifest.json').unlink()
        (self.run / 'run-manifest.json').symlink_to(self.legacy)
        with self.assertRaises(ValueError):
            V.select_locked_run('clean-id')

    def test_symlinked_verify_destination_rejected(self):
        (self.run / 'uvlo-verify.json').symlink_to(self.legacy)
        with self.assertRaises(ValueError):
            V.select_locked_run('clean-id')

    def test_symlinked_parent_and_staging_rejected(self):
        (self.run / 'staged').rmdir()
        (self.run / 'staged').symlink_to(self.legacy.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            V.select_locked_run('clean-id')
        (self.run / 'staged').unlink()
        (self.run / 'staged').mkdir()
        another = V.HERE / 'shadow-runs'
        another.mkdir()
        (V.HERE / 'results' / 'runs' / 'clean-id').rename(another / 'clean-id')
        (V.HERE / 'results' / 'runs').rmdir()
        (V.HERE / 'results' / 'runs').symlink_to(another, target_is_directory=True)
        with self.assertRaises(ValueError):
            V.select_locked_run('clean-id')


if __name__ == '__main__':
    unittest.main(verbosity=2)
