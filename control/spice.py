"""Native ngspice circuit reference for independent switching measurements."""
import os
from pathlib import Path
import re
import subprocess

from .plant import schematic


def run(work, vin=None, ton=None, max_step=25e-9):
    p = schematic()
    vin = p.vin if vin is None else vin
    ton = p.ton if ton is None else ton
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    # LTspice's Vfwd/Ron diode is a piecewise-linear device. ngspice's
    # ordinary diode does not accept this LTspice model definition.
    circuit = f"""PDU frozen open-loop power stage
V1 vin 0 {vin}
Rci vin ci {p.cin_esr}
Ci ci 0 {p.cin}
Vgate g 0 PULSE(0 10 0 10n 10n {ton} {p.period})
S1 vin sw g 0 POWER_SW
.model POWER_SW SW(Ron={p.ron} Roff=1e9 Vt=5 Vh=0)
Bd 0 sw I=max((v(0,sw)-{p.vf})/{p.diode_r},0)
Rl sw left {p.dcr}
L1 left out {p.inductance}
Rco out co {p.esr}
Co co 0 {p.cout}
Rd out cd {p.rd}
Cd cd 0 {p.cd}
Rload out 0 {p.load_r}
.options method=gear reltol=1e-5
.tran 20n 20m 0 {max_step}
.meas tran mean_v AVG v(out) FROM=19m TO=20m
.meas tran ripple_v PP v(out) FROM=19m TO=20m
.meas tran peak_i MAX i(L1) FROM=19m TO=20m
.meas tran min_i MIN i(L1) FROM=19m TO=20m
.end
"""
    (work / "baseline.cir").write_text(circuit, encoding="ascii")
    command = [os.environ.get("NGSPICE", "ngspice"), "-b", "-o", "baseline.log", "baseline.cir"]
    subprocess.run(command, cwd=work, check=True, timeout=90)
    log = (work / "baseline.log").read_text(encoding="utf-8", errors="replace")
    metrics = {}
    for name in ("mean_v", "ripple_v", "peak_i", "min_i"):
        match = re.search(rf"^{name}\s*=\s*([-+.\deE]+)", log, re.M)
        if not match:
            raise RuntimeError(f"{name} missing from {work / 'baseline.log'}")
        metrics[name] = float(match[1])
    return metrics


if __name__ == "__main__":
    print(run(Path("build/spice")))
