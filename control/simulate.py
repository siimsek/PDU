"""Python interface to the switched plant and firmware control core."""
import ctypes as ct
from pathlib import Path
import sys

import numpy as np

from .configure import METHODS
from .design import REFERENCE, SAMPLE

CR, CC, CP = range(3)
DISABLED, STALE_ADC, ADC_RAIL, SHORTED_S1, UVLO = (1, 2, 4, 8, 16)
CBC, OVP, WATCHDOG, ISOLATED, SOFT_UVLO, BAD_SAMPLE, DCM = (1, 2, 4, 8, 16, 32, 64)
PERIOD = REFERENCE.period


class Model(ct.Structure):
    _fields_ = [(name, ct.c_double) for name in (
        "l dcr c esr cd rd ron vf diode_r max_step sample_time adc_latency execute_time jitter "
        "noise_v noise_i turn_on turn_off limit_i blank_time ocp_delay limit_v ovp_delay "
        "isolate_delay leak_g lin_switch fixed_duty initial_v initial_i sense_delay").split()]
    _fields_ += [("watchdog_cycles", ct.c_uint), ("cbc_latch_cycles", ct.c_uint),
                 ("seed", ct.c_uint32), ("method", ct.c_int)]


class Cycle(ct.Structure):
    _fields_ = [("vin", ct.c_double), ("load", ct.c_double),
                ("kind", ct.c_int), ("flags", ct.c_int)]


class Result(ct.Structure):
    _fields_ = [(name, ct.c_double) for name in
                "low_v high_v mean_v low_i high_i rms_i pout loss duty ocp_latency ovp_latency".split()]
    _fields_ += [("flags", ct.c_uint)]


def model(method, plant=REFERENCE, **overrides):
    parameters = dict(l=plant.inductance, dcr=plant.dcr, c=plant.cout, esr=plant.esr,
                      cd=plant.cd, rd=plant.rd, ron=plant.ron, vf=plant.vf, diode_r=plant.diode_r,
                      max_step=100e-9, sample_time=SAMPLE, adc_latency=1.4e-6, execute_time=.65e-6,
                      jitter=35e-9, noise_v=.002, noise_i=.015, turn_on=45e-9, turn_off=60e-9,
                      limit_i=9.8, blank_time=.1e-6, ocp_delay=.18e-6,
                      limit_v=11.9, ovp_delay=.35e-6, isolate_delay=1e9,
                      leak_g=1/10000, lin_switch=60e-9, fixed_duty=-1.,
                      initial_v=0., initial_i=0., sense_delay=150e-9,
                      watchdog_cycles=3, cbc_latch_cycles=96, seed=474,
                      method=METHODS.index(method))
    unknown = overrides.keys() - parameters.keys()
    if unknown:
        raise ValueError(f"Unknown model parameters: {sorted(unknown)}")
    parameters.update(overrides)
    return Model(**parameters)


def host_library(build):
    build = Path(build).resolve()
    library = {"win32": "pdu_sim.dll", "darwin": "libpdu_sim.dylib"}.get(sys.platform, "libpdu_sim.so")
    impl = ct.CDLL(str(build / "bin" / library))
    run = impl.pdu_simulate
    run.argtypes = [ct.POINTER(Model), ct.POINTER(Cycle), ct.c_size_t, ct.POINTER(Result)]
    run.restype = ct.c_int
    return run


def run(library, config, stages):
    """Stages are (duration seconds, Vin, load in A at 11 V, load kind, flags)."""
    periods = [round(s[0] / PERIOD) for s in stages]
    if min(periods) <= 0:
        raise ValueError("A stage must last at least one period")
    cycles = (Cycle * sum(periods))()
    offset = 0
    for count, (_, vin, amps, kind, flags) in zip(periods, stages):
        load = {CR: amps / 11., CC: amps, CP: 11. * amps}[kind]
        cycles[offset:offset + count] = [Cycle(vin, load, kind, flags)] * count
        offset += count
    result = (Result * len(cycles))()
    if library(ct.byref(config), cycles, len(cycles), result):
        raise RuntimeError("The switched-model parameters were rejected")
    return np.ctypeslib.as_array(result).copy()


def mask(data, flag):
    return (data["flags"] & flag) != 0


def metrics(data, settle_cycles=300):
    tail = data[-settle_cycles:]
    tolerance = .11
    errors = np.flatnonzero((data["low_v"] < 11 - tolerance) | (data["high_v"] > 11 + tolerance))
    settled = (0 if not len(errors) else (int(errors[-1]) + 1))
    return {
        "min_v": float(min(data["low_v"])),
        "max_v": float(max(data["high_v"])),
        "mean_v": float(tail["mean_v"].mean()),
        "ripple_v": float(max(tail["high_v"] - tail["low_v"])),
        "peak_i": float(max(data["high_i"])),
        "rms_i": float(np.sqrt(np.mean(tail["rms_i"] ** 2))),
        "settle_ms": None if settled == len(data) else settled * PERIOD * 1000,
        "gain_efficiency": float(tail["pout"].mean() / max(1e-20, (tail["pout"] + tail["loss"]).mean())),
        "loss_w": float(tail["loss"].mean()),
        "fault_cycles": int(np.count_nonzero(data["flags"] & (OVP | WATCHDOG))),
        "cbc_cycles": int(np.count_nonzero(mask(data, CBC))),
        "dcm_cycles": int(np.count_nonzero(mask(data, DCM))),
    }
