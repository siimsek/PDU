"""Read the frozen power-stage values directly from the LTspice schematic."""
from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VIN_POINTS = (20.0, 22.2, 24.6, 25.2, 26.0)
VREF = 11.0
IRATED = 7.5


def quantity(value):
    match = re.fullmatch(r"([0-9.]+)(meg|[munp])?", value, re.I)
    if not match:
        raise ValueError(f"Unsupported schematic quantity: {value}")
    magnitude, suffix = match.groups()
    return float(magnitude) * {None: 1, "meg": 1e6, "m": 1e-3, "u": 1e-6,
                               "n": 1e-9, "p": 1e-12}[suffix.lower() if suffix else None]


@dataclass(frozen=True)
class Plant:
    vin: float
    period: float
    ton: float
    inductance: float
    dcr: float
    cout: float
    esr: float
    cd: float
    rd: float
    ron: float
    vf: float
    diode_r: float
    cin: float
    cin_esr: float
    load_r: float

    def duty(self, vin, current=IRATED, voltage=VREF):
        return (voltage + self.vf + current * (self.dcr + self.diode_r)) / self.drive(vin, current)

    def drive(self, vin, current):
        return vin + self.vf + current * (self.diode_r - self.ron)


def schematic():
    asc = ROOT / "buck/ltspice/buck_guc_kati.asc"
    components = {}
    for symbol in asc.read_text(encoding="ascii").split("SYMBOL ")[1:]:
        fields = dict(re.findall(r"^SYMATTR (\w+) (.*)$", symbol, re.M))
        components[fields.pop("InstName")] = fields

    def value(name):
        return quantity(components[name]["Value"])

    def extra(name, key):
        tokens = dict(item.split("=") for item in components[name]["SpiceLine"].split())
        return quantity(tokens[key])

    pulse = components["Vdrv"]["Value"].removeprefix("PULSE(").removesuffix(")").split()
    cin1, cin2 = value("Cin1"), value("Cin2")
    esr1, esr2 = extra("Cin1", "Rser"), extra("Cin2", "Rser")
    if cin1 != cin2 or esr1 != esr2:
        raise ValueError("Input capacitor lumping requires identical parallel branches")
    return Plant(value("V1"), quantity(pulse[6]), quantity(pulse[5]), value("L1"),
                 extra("L1", "Rser"), value("Cout"), extra("Cout", "Rser"), value("Cd"),
                 value("Rd"), extra("S1", "Ron"), extra("D1", "Vf"), extra("D1", "Ron"),
                 cin1 + cin2, esr1 / 2, value("Rload"))
