"""Convert continuous gains to the exact coefficients used on host and target."""
from pathlib import Path
import json
import math
import sys

METHODS = ("pi", "ff_pi", "type_ii", "type_iii", "cascade")


HRTIM_CLOCK_HZ = 170_000_000
HRTIM_TICKS_HZ = 32 * HRTIM_CLOCK_HZ
ADC_CLOCK_HZ = HRTIM_CLOCK_HZ / 4
ADC_TRIGGER_TICKS = 32_912
UPDATE_DEADLINE_TICKS = 52_224
ADC_RANKS = 6
ADC_SAMPLE_CYCLES = 6.5
ADC_RANK_CYCLES = ADC_SAMPLE_CYCLES + 12.5
# Allow two ADC clocks for trigger synchronization. Measure the actual latency on target.
ADC_SYNC_CYCLES = 2

ADC_TRIGGER_S = ADC_TRIGGER_TICKS / HRTIM_TICKS_HZ
UPDATE_DEADLINE_S = UPDATE_DEADLINE_TICKS / HRTIM_TICKS_HZ
CURRENT_APERTURE_S = (ADC_SYNC_CYCLES + ADC_SAMPLE_CYCLES) / ADC_CLOCK_HZ
VOUT_APERTURE_S = CURRENT_APERTURE_S + 2 * ADC_RANK_CYCLES / ADC_CLOCK_HZ
ADC_FRAME_S = (ADC_SYNC_CYCLES + ADC_RANKS * ADC_RANK_CYCLES) / ADC_CLOCK_HZ
ADC_EARLIEST_TICKS = ADC_TRIGGER_TICKS + int(ADC_RANKS * ADC_RANK_CYCLES * HRTIM_TICKS_HZ / ADC_CLOCK_HZ)


def config(method, gains, period=1e-5):
    def section(pole, zero=None):
        if pole is None:
            return (1., 0., 0.)
        a = 1 / (math.pi * pole * period)
        b = 1 / (math.pi * zero * period) if zero else 0
        return ((1 + b) / (1 + a), (1 - b) / (1 + a), (1 - a) / (1 + a))

    return (gains["kp"], gains["ki"] * period / 2, gains.get("outer_kp", 0.),
            gains.get("outer_ki", 0.) * period / 2,
            section(gains.get("pole_hz")), section(gains.get("second_pole_hz"), gains.get("zero_hz")))


def generate(path):
    gains = json.loads(Path(__file__).with_name("gains.json").read_text(encoding="ascii"))

    def literal(value):
        return f"{value:.9e}f"

    def row(method):
        kp, ki, op, oi, pole, lead = config(method, gains[method])
        fields = [literal(value) for value in (kp, ki, op, oi)]
        fields.extend("{" + ", ".join(map(literal, section)) + "}" for section in (pole, lead))
        fields.append("PDU_" + method.upper())
        return "    {" + ", ".join(fields) + "},\n"

    content = ("#include \"control.h\"\n\n"
               "static const ControlConfig pdu_configs[] = {\n"
               + "".join(row(method) for method in METHODS) + "};\n")
    Path(path).write_text(content, encoding="ascii", newline="\n")


def generate_timing(path):
    values = {
        "CORE_HZ": HRTIM_CLOCK_HZ, "ADC_TRIGGER_TICKS": ADC_TRIGGER_TICKS,
        "UPDATE_DEADLINE_TICKS": UPDATE_DEADLINE_TICKS, "ADC_RANKS": ADC_RANKS,
        "ADC_EARLIEST_TICKS": ADC_EARLIEST_TICKS,
        "CURRENT_APERTURE_S": CURRENT_APERTURE_S, "VOUT_APERTURE_S": VOUT_APERTURE_S,
        "UPDATE_DEADLINE_S": UPDATE_DEADLINE_S,
    }
    definitions = [f"#define PDU_{key} {v}u" if isinstance(v, int) else f"#define PDU_{key} {v:.15e}"
                   for key, v in values.items()]
    Path(path).write_text("#ifndef PDU_TIMING_H\n#define PDU_TIMING_H\n\n"
                          + "\n".join(definitions) + "\n\n#endif\n", encoding="ascii", newline="\n")


if __name__ == "__main__":
    generate(sys.argv[1])
    if len(sys.argv) == 3:
        generate_timing(sys.argv[2])
