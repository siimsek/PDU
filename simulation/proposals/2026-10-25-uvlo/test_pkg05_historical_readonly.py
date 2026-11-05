#!/usr/bin/env python3
"""Focused verifier artifact-output tests; no ngspice or acceptance simulation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('pdu_verify_output_test', ROOT / 'verify_uvlo.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class ArtifactOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.saved = (V.VERIFY_OUTPUT, V.STAGED)
        self.addCleanup(self.restore)
        self.output = Path(self.temp.name) / 'results' / 'uvlo-verify.json'
        self.output.parent.mkdir()
        V.VERIFY_OUTPUT = self.output
        V.STAGED = None
        self.report = {'summary': {'mode': 'historical', 'exit_code': 1}, 'cases': {'test': {'status': 'FAIL'}}}

    def restore(self):
        V.VERIFY_OUTPUT, V.STAGED = self.saved

    def test_historical_does_not_create_output(self):
        self.assertIs(V.write_verification('historical', self.report), False)
        self.assertFalse(self.output.exists())

    def test_historical_preserves_existing_evidence(self):
        self.output.write_bytes(b'ORIGINAL HISTORICAL EVIDENCE\n')
        self.assertIs(V.write_verification('historical', self.report), False)
        self.assertEqual(self.output.read_bytes(), b'ORIGINAL HISTORICAL EVIDENCE\n')

    def test_historical_preserves_symlink_target(self):
        other = Path(self.temp.name) / 'original.json'
        other.write_bytes(b'ORIGINAL\n')
        self.output.symlink_to(other)
        self.assertIs(V.write_verification('historical', self.report), False)
        self.assertEqual(other.read_bytes(), b'ORIGINAL\n')

    def test_acceptance_without_locked_run_is_rejected(self):
        with self.assertRaises(ValueError):
            V.write_verification('acceptance', self.report)
        self.assertFalse(self.output.exists())

    def test_acceptance_creates_new_report_exclusively(self):
        V.STAGED = Path(self.temp.name) / 'runs' / 'id' / 'staged'
        self.assertIs(V.write_verification('acceptance', self.report), True)
        self.assertEqual(json.loads(self.output.read_text()), self.report)

    def test_acceptance_never_overwrites_existing_report(self):
        V.STAGED = Path(self.temp.name) / 'runs' / 'id' / 'staged'
        self.output.write_bytes(b'IMMUTABLE\n')
        with self.assertRaises(FileExistsError):
            V.write_verification('acceptance', self.report)
        self.assertEqual(self.output.read_bytes(), b'IMMUTABLE\n')

    def test_acceptance_symlink_is_rejected(self):
        V.STAGED = Path(self.temp.name) / 'runs' / 'id' / 'staged'
        target = Path(self.temp.name) / 'evidence.json'
        target.write_bytes(b'NOT MODIFIED\n')
        self.output.symlink_to(target)
        with self.assertRaises((FileExistsError, ValueError)):
            V.write_verification('acceptance', self.report)
        self.assertEqual(target.read_bytes(), b'NOT MODIFIED\n')

    def test_unknown_mode_cannot_write(self):
        V.STAGED = Path(self.temp.name) / 'runs' / 'id' / 'staged'
        with self.assertRaises(ValueError):
            V.write_verification('untrusted', self.report)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
