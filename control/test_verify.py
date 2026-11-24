import unittest

import numpy as np

from control.simulate import CR, Result
from control.verify import compare, is_windows_11_x64, stage_results


class VerificationLogic(unittest.TestCase):
    def test_windows_11_guard_requires_x64_workstation(self):
        desktop = {"system": "Windows", "system_release": "11", "windows_product_type": 1,
                   "machine": "AMD64", "python_bits": 64}
        self.assertTrue(is_windows_11_x64(desktop))
        for key, value in (("system", "Linux"), ("system_release", "10"),
                           ("windows_product_type", 3), ("machine", "ARM64"), ("python_bits", 32)):
            with self.subTest(key=key):
                self.assertFalse(is_windows_11_x64({**desktop, key: value}))

    def test_numeric_comparison_rejects_outside_tolerance_and_nan(self):
        compare({"sample": 11.004}, {"sample": 11.}, {"sample": .005})
        for value in (11.006, float("nan")):
            with self.assertRaisesRegex(RuntimeError, "sample"):
                compare({"sample": value}, {"sample": 11.}, {"sample": .005})

    def test_short_pulse_and_steady_ripple_are_distinct(self):
        trace = np.ctypeslib.as_array((Result * 2200)())
        trace["low_v"], trace["high_v"], trace["mean_v"] = 10.9, 11.05, 11.0
        trace["low_v"][-100:] = 10.7
        startup = (.021, 26., 2., CR, 0)
        pulse = (.001, 26., 7.5, CR, 0)
        result = list(stage_results(trace, [startup, pulse]))
        self.assertIn("max_cycle_excursion_v", result[-1])
        self.assertNotIn("ripple_v", result[-1])
        trace["low_v"][:2100] = 10.7
        with self.assertRaisesRegex(RuntimeError, "steady PWM ripple"):
            list(stage_results(trace, [startup, pulse]))

    def test_window_catches_ripple_between_switching_periods(self):
        trace = np.ctypeslib.as_array((Result * 2100)())
        trace["mean_v"], trace["low_v"], trace["high_v"] = 11.0, 10.96, 11.04
        trace["low_v"][-1], trace["high_v"][-1] = 11.05, 11.13
        summary = next(stage_results(trace, [(.021, 26., 2., CR, 0)]))
        self.assertAlmostEqual(summary["ripple_v"], .08)
        self.assertAlmostEqual(summary["window_pp_v"], .17)
        trace["mean_v"][-1] = float("nan")
        with self.assertRaisesRegex(RuntimeError, "Non-finite"):
            list(stage_results(trace, [(.021, 26., 2., CR, 0)]))
