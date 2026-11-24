import unittest

import numpy as np

from control.simulate import CR, Result
from control.verify import compare, stage_results


class VerificationLogic(unittest.TestCase):
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
