"""PKG-06: no acceptance simulation; verify synthetic fixture stdout parsing."""
import unittest
from fixture_summary import summary_from_stdout


class SummaryFixtureTests(unittest.TestCase):
    def test_valid_terminal_summary(self):
        text = 'PASS sample {}\nPROVENANCE none\n{\n "mode": "historical", "exit_code": 0, "n_cases": 1, "provenance_errors": []\n}\n'
        self.assertEqual(summary_from_stdout(text)['summary']['mode'], 'historical')

    def test_no_summary_never_passes(self):
        self.assertEqual(summary_from_stdout('PASS: sample\n'), {})

    def test_unrelated_json_never_passes(self):
        self.assertEqual(summary_from_stdout('{"result": "PASS"}\n'), {})

    def test_invalid_or_partial_json_never_passes(self):
        self.assertEqual(summary_from_stdout('{"mode": "historical"\n'), {})

    def test_diagnostic_before_final_summary(self):
        text = '{"foo": 3}\nERROR sample\n{"mode":"historical","exit_code":2,"n_cases":2,"provenance_errors":["failed"]}\n'
        self.assertEqual(summary_from_stdout(text)['summary']['exit_code'], 2)

    def test_summary_requires_provenance_fields(self):
        text = '{"mode":"historical","exit_code":0,"n_cases":2}\n'
        self.assertEqual(summary_from_stdout(text), {})


if __name__ == '__main__':
    unittest.main(verbosity=2)
