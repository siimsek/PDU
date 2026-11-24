import json
from pathlib import Path
import unittest

import numpy as np

from control.configure import config
from control.design import METHODS, MIN_GM, MIN_PM, controller, evaluate


class ControllerDesign(unittest.TestCase):
    gains = json.loads(Path("control/gains.json").read_text(encoding="ascii"))

    def test_target_sections_match_analysis(self):
        period = 1e-5
        z = np.exp(2j * np.pi * np.array([60, 800, 3500, 15000]) * period)
        s = 2 / period * (1 - 1 / z) / (1 + 1 / z)
        for method in METHODS:
            with self.subTest(method=method):
                gains = self.gains[method]
                kp, ki, _, _, pole, lead = config(method, gains, period)
                response = kp + ki * (1 + 1 / z) / (1 - 1 / z)
                for b0, b1, a1 in (pole, lead):
                    response *= (b0 + b1 / z) / (1 + a1 / z)
                np.testing.assert_allclose(response, controller(s, gains), rtol=1e-10)

    def test_type_iii_passes_sampled_ccm_gate(self):
        result = evaluate("type_iii", self.gains["type_iii"])
        self.assertGreater(result["voltage"]["phase_deg"], MIN_PM)
        self.assertGreater(result["voltage"]["gain_db"], MIN_GM)
        self.assertGreater(result["voltage"]["min_crossover_hz"], 2500)
        self.assertLess(result["max_pole"], 1)


class TimingBudget(unittest.TestCase):
    def test_scan_pair_apertures_and_deadline(self):
        from control.configure import (
            ADC_CLOCK_HZ, ADC_FRAME_S, ADC_RANK_CYCLES, ADC_TRIGGER_S, EXECUTION_BUDGET_S,
            CURRENT_APERTURE_S, UPDATE_DEADLINE_S, VOUT_APERTURE_S,
        )
        self.assertAlmostEqual(VOUT_APERTURE_S - CURRENT_APERTURE_S,
                               2 * ADC_RANK_CYCLES / ADC_CLOCK_HZ, places=12)
        ready = ADC_TRIGGER_S + ADC_FRAME_S
        self.assertLess(ready + EXECUTION_BUDGET_S + 120e-9, UPDATE_DEADLINE_S)
        self.assertGreaterEqual(ready + 1.60e-6, UPDATE_DEADLINE_S)
