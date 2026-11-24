import unittest

from control.interface import Interface


class InterfaceBudgets(unittest.TestCase):
    def test_analog_thresholds_inside_swept_limits(self):
        result = Interface().calculate()
        self.assertGreaterEqual(result["ocp_A"][0], 9.55)
        self.assertLessEqual(result["ocp_A"][1], 10.05)
        self.assertGreaterEqual(result["ovp_V"][0], 11.75)
        self.assertLessEqual(result["ovp_V"][1], 11.95)
        self.assertLess(result["upper_peak_bound_A"], 11)
        self.assertAlmostEqual(result["bootstrap_charge_per_second_A"], 4.5e-3)
