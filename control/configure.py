"""Convert continuous gains to the exact coefficients used on host and target."""
from pathlib import Path
import json
import math
import sys

METHODS = ("pi", "ff_pi", "type_ii", "type_iii", "cascade")


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


if __name__ == "__main__":
    generate(sys.argv[1])
