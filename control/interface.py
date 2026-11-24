"""First-pass hardware budgets. Inputs are targets, not component qualifications."""
from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Interface:
    current_shunt_ohm: float = 0.00412
    sense_gain: float = 50.0
    comparator_reference_v: float = 2.0188
    shunt_error: float = 0.0075
    gain_error: float = 0.003
    reference_error: float = 0.004
    comparator_error_v: float = 0.007
    input_offset_v: float = 50e-6
    ovp_reference_v: float = 2.500
    ovp_top_ohm: float = 37_400.
    ovp_bottom_ohm: float = 10_000.
    ovp_resistor_error: float = 0.001
    ovp_reference_error: float = 0.002
    ovp_comparator_error_v: float = .007
    nom_inductance: float = 33e-6
    min_inductance: float = 23.1e-6
    max_input_v: float = 26.0
    ocp_cutoff_seconds: float = .65e-6
    driver_gate_charge_c: float = 45e-9
    bootstrap_effective_f: float = 330e-9
    bootstrap_max_current_a: float = 150e-6
    frequency_hz: float = 100e3
    maximum_duty: float = .75

    def calculate(self):
        scale = self.sense_gain * self.current_shunt_ohm
        offset = self.comparator_error_v + self.sense_gain * self.input_offset_v
        ref = self.comparator_reference_v
        low_i = (ref * (1 - self.reference_error) - offset) / (scale * (1 + self.shunt_error) * (1 + self.gain_error))
        high_i = (ref * (1 + self.reference_error) + offset) / (scale * (1 - self.shunt_error) * (1 - self.gain_error))
        worst_slope = self.max_input_v / self.min_inductance

        tol = self.ovp_resistor_error
        top, bottom = self.ovp_top_ohm, self.ovp_bottom_ohm
        ref_v = self.ovp_reference_v
        low_v = (ref_v * (1 - self.ovp_reference_error) - self.ovp_comparator_error_v) * (
            1 + top * (1 - tol) / (bottom * (1 + tol)))
        high_v = (ref_v * (1 + self.ovp_reference_error) + self.ovp_comparator_error_v) * (
            1 + top * (1 + tol) / (bottom * (1 - tol)))

        ton = self.maximum_duty / self.frequency_hz
        t_off = (1 - self.maximum_duty) / self.frequency_hz
        return {
            "adc_v_per_amp": scale,
            "shunt_loss_w_at_7p5a": 7.5 ** 2 * self.current_shunt_ohm,
            "ocp_A": [low_i, high_i],
            "upper_peak_bound_A": high_i + worst_slope * self.ocp_cutoff_seconds,
            "ovp_V": [low_v, high_v],
            "bootstrap_droop_one_cycle_V": (
                self.driver_gate_charge_c + self.bootstrap_max_current_a * ton
            ) / self.bootstrap_effective_f,
            "bootstrap_charge_per_second_A": self.frequency_hz * self.driver_gate_charge_c,
            "minimum_off_time_us": 1e6 * t_off,
            "max_short_slope_A_per_us": worst_slope * 1e-6,
            "capacitor_energy_at_nominal_J": .5 * (1000e-6 + 470e-6) * 11 ** 2,
        }


if __name__ == "__main__":
    interface = Interface()
    print(json.dumps({"inputs": asdict(interface), "budgets": interface.calculate()}, indent=2))
