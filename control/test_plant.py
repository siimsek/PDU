"""Cross-check the inherited schematic, calculation, and simulation model."""
import unittest

from buck import dogrula, hesap
from control.plant import IRATED, VIN_POINTS, VREF, schematic


class FrozenPlant(unittest.TestCase):
    def test_independent_sources(self):
        p = schematic()
        self.assertEqual((p.vin, VREF, IRATED, VIN_POINTS),
                         (hesap.VIN_ANA_V, hesap.VO_V, hesap.IO_A, hesap.VIN_V))
        self.assertAlmostEqual(VREF / p.load_r, IRATED, places=3)
        for field, calculated, simulated in (
            (p.inductance, hesap.L_H, dogrula.SECILEN["L"]),
            (p.dcr, hesap.DCR_OHM, dogrula.SECILEN["DCR"]),
            (p.cout, hesap.COUT_F, dogrula.SECILEN["Cout"]),
            (p.esr, hesap.ESR_OUT_OHM, dogrula.SECILEN["ESRo"]),
            (p.cd, hesap.CD_F, dogrula.SECILEN["Cd"]),
            (p.rd, hesap.RDAL_OHM, dogrula.SECILEN["Rdal"]),
            (p.ron, hesap.RON_OHM, dogrula.SECILEN["Ron"]),
            (p.vf, hesap.VF_V, dogrula.SECILEN["Vf"]),
            (p.diode_r, hesap.RD_OHM, dogrula.SECILEN["Rd"]),
            (p.cin, hesap.CIN_F, 2 * dogrula.SECILEN["Cin"]),
            (p.cin_esr, hesap.ESR_IN_OHM, dogrula.SECILEN["ESRi"] / 2),
            (1 / p.period, hesap.FSW_HZ, dogrula.SECILEN["f"]),
        ):
            with self.subTest(value=field):
                self.assertAlmostEqual(field, calculated, delta=abs(field) * 1e-12)
                self.assertAlmostEqual(field, simulated, delta=abs(field) * 1e-12)

    def test_rated_duty(self):
        p = schematic()
        self.assertAlmostEqual((p.ton + 10e-9) / p.period, p.duty(p.vin), delta=0.0002)
        for vin in VIN_POINTS:
            self.assertAlmostEqual(p.duty(vin), hesap.duty(vin, IRATED), places=12)
