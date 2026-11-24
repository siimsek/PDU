"""Native ngspice reference and replay of firmware-generated gate pulses."""
import math
import os
from pathlib import Path
import re
import subprocess

from .plant import schematic


def netlist(p, vin, gate, load, ending, measure_from, max_step):
    # LTspice's Vfwd/Ron device is translated explicitly. Standard ngspice
    # diode models do not support those LTspice-only parameters.
    return f"""PDU frozen power stage
V1 vin 0 {vin}
Rci vin ci {p.cin_esr}
Ci ci 0 {p.cin}
{gate}
S1 vin sw g 0 POWER_SW
.model POWER_SW SW(Ron={p.ron} Roff=1e9 Vt=5 Vh=0)
Bd 0 sw I=max((v(0,sw)-{p.vf})/{p.diode_r},0)
Rl sw left {p.dcr}
L1 left out {p.inductance}
Rco out co {p.esr}
Co co 0 {p.cout}
Rd out cd {p.rd}
Cd cd 0 {p.cd}
{load}
.options method=gear reltol=1e-5
.tran 20n {ending} 0 {max_step}
.meas tran mean_v AVG v(out) FROM={measure_from} TO={ending}
.meas tran ripple_v PP v(out) FROM={measure_from} TO={ending}
.meas tran peak_i MAX i(L1) FROM={measure_from} TO={ending}
.meas tran min_i MIN i(L1) FROM={measure_from} TO={ending}
.end
"""


def execute(work, circuit, names=("mean_v", "ripple_v", "peak_i", "min_i")):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    (work / "power.cir").write_text(circuit, encoding="ascii")
    command = [os.environ.get("NGSPICE", "ngspice"), "-b", "-o", "power.log", "power.cir"]
    process = subprocess.run(command, cwd=work, capture_output=True, text=True,
                             errors="replace", timeout=120)
    log_path = work / "power.log"
    if process.returncode != 0 or not log_path.exists():
        raise RuntimeError(f"ngspice failed in {work}: {process.stderr or process.stdout}")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"^\s*(?:error|fatal)|simulation\(s\) aborted", log, re.I | re.M):
        raise RuntimeError(f"ngspice reported an error in {log_path}")
    metrics = {}
    for name in names:
        match = re.search(rf"^{name}\s*=\s*([-+.\deE]+)", log, re.M)
        if not match:
            raise RuntimeError(f"{name} missing from {log_path}")
        metrics[name] = float(match[1])
    return metrics


def run(work, vin=None, ton=None, max_step=25e-9):
    p = schematic()
    vin = p.vin if vin is None else vin
    ton = p.ton if ton is None else ton
    gate = f"Vgate g 0 PULSE(0 10 0 10n 10n {ton} {p.period})"
    return execute(work, netlist(p, vin, gate, f"Rload out 0 {p.load_r}", .02, .019, max_step))


def replay(work, duty, turn_on, turn_off, amps_before, amps_after, load_step):
    """Independent circuit integration with recorded PWM. Feedback is in the C run."""
    p = schematic()
    gate = ["Vgate g 0 PWL(0 0"]
    for k, pulse in enumerate(duty):
        if pulse <= 0:
            continue
        rise = k * p.period + turn_on
        fall = (k + float(pulse)) * p.period + turn_off
        gate.append(f"+ {rise - 1e-9:.13g} 0 {rise + 1e-9:.13g} 10"
                    f" {fall - 1e-9:.13g} 10 {fall + 1e-9:.13g} 0")
    gate.append("+ )")
    load = (f"Vload conductance 0 PWL(0 {amps_before / 11} "
            f"{load_step - 1e-9} {amps_before / 11} {load_step} {amps_after / 11})\n"
            "Bload out 0 I=v(conductance)*v(out)\nRfeedback out 0 10000")
    ending = len(duty) * p.period
    return execute(work, netlist(p, p.vin, "\n".join(gate), load, ending, ending - .001, 75e-9))


def hotplug(work):
    """Input cable-energy sensitivity with the buck disabled and Cin discharged."""
    p = schematic()
    results = {}
    for name, cable_l, cable_r in (("inductive", 5e-6, .005), ("damped", 5e-6, .12)):
        circuit = f"""PDU ideal hot-plug cable and installed Cin
Vbattery src 0 PULSE(0 26 100n 1u 1u 4m 8m)
Lwire src wire {cable_l}
Rwire wire vin {cable_r}
Resr vin ci {p.cin_esr}
Cin ci 0 {p.cin}
.tran .25u 3m 0 .25u
.meas tran peak_v MAX v(vin) FROM=0 TO=3m
.meas tran peak_i MAX i(Lwire) FROM=0 TO=3m
.end
"""
        samples = execute(Path(work) / name, circuit, ("peak_v", "peak_i"))
        # Ideal step approximation for the capacitor, excluding the instantaneous ESR voltage.
        zeta = (cable_r + p.cin_esr) / 2 * math.sqrt(p.cin / cable_l)
        cap_peak = 26 * (1 + math.exp(-math.pi * zeta / math.sqrt(1 - zeta ** 2))) if zeta < 1 else 26.
        results[name] = {**samples, "capacitor_ideal_step_v": cap_peak}
    return results


if __name__ == "__main__":
    print(run(Path("build/spice")))
