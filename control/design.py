"""Sampled-data CCM linearization and repeatable robust compensator synthesis."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm
from scipy.optimize import differential_evolution
from scipy.signal import ss2tf

from .plant import IRATED, VIN_POINTS, VREF, schematic

SAMPLE = 7.1e-6
METHODS = ("pi", "ff_pi", "type_ii", "type_iii", "cascade")
FREQUENCY = np.geomspace(10, 49_980, 1100)
MIN_PM, MIN_GM = 40, 6
REFERENCE = schematic()


def corners():
    p = REFERENCE
    return {
        "nominal": p,
        "low_damping": replace(p, inductance=p.inductance * 1.20, cout=p.cout * .8,
                               cd=p.cd * .8, esr=.010, dcr=.0065, rd=.60),
        "low_lc": replace(p, inductance=p.inductance * .70, cout=p.cout * .8,
                          cd=p.cd * .8, rd=.15),
        "high_lc": replace(p, inductance=p.inductance * 1.20, cout=p.cout * 1.20,
                           cd=p.cd * 1.20, rd=.60),
        "cold_esr": replace(p, esr=.120, cout=p.cout * .8, cd=p.cd * .8, vf=.415),
        "hot": replace(p, esr=.015, dcr=.015, vf=.265, ron=.010, diode_r=.006),
    }


def plant_model(p, vin, current, load):
    """Inputs are the perturbation in average switch voltage and load current."""
    duty = p.duty(vin, current)
    resistance = p.dcr + duty * p.ron + (1 - duty) * p.diode_r
    g_load = {"cc": 0, "cr": current / VREF, "cp": -current / VREF}[load]
    conductance = 1 / p.esr + 1 / p.rd + g_load
    y = np.array([[1, 1 / p.esr, 1 / p.rd], [1, 0, 0]]) / np.array([[conductance], [1]])
    a = np.array([[resistance / p.inductance, 0, 0],
                  [0, 1 / (p.esr * p.cout), 0],
                  [0, 0, 1 / (p.rd * p.cd)]])
    a = -a + np.outer([-1 / p.inductance, 1 / (p.esr * p.cout), 1 / (p.rd * p.cd)], y[0])
    b = np.array([[1 / p.inductance], [0], [0]])
    return a, b, y


def sampled(p, vin, current, load):
    a, b, y = plant_model(p, vin, current, load)
    ab = np.block([[a, b], [np.zeros((1, 4))]])
    period = expm(ab * p.period)
    sample = expm(ab * SAMPLE)
    # State at the start of the period, measurement at SAMPLE within it.
    c = y @ sample[:3, :3]
    d = y @ sample[:3, 3:]
    return ss2tf(period[:3, :3], period[:3, 3:], c, d)


def parameters(method, raw):
    values = list(10 ** np.asarray(raw))
    if method == "cascade":
        return dict(outer_kp=values[0], outer_ki=values[1], kp=values[2], ki=values[3])
    result = dict(kp=values[0], ki=values[1])
    if method in ("type_ii", "type_iii"):
        result["pole_hz"] = values[2]
    if method == "type_iii":
        result.update(zero_hz=values[3], second_pole_hz=values[4])
    return result


def controller(s, gains):
    c = gains["kp"] + gains["ki"] / s
    if "pole_hz" in gains:
        c /= 1 + s / (2 * np.pi * gains["pole_hz"])
    if "zero_hz" in gains:
        c *= (1 + s / (2 * np.pi * gains["zero_hz"])) / (1 + s / (2 * np.pi * gains["second_pole_hz"]))
    return c


def loops(method, gains, gv, gi, vin, frequency=FREQUENCY):
    phase = np.pi * frequency * REFERENCE.period
    delay = np.exp(-2j * phase)
    s = 2j / REFERENCE.period * np.tan(phase)
    comp = controller(s, gains) * delay
    if method == "cascade":
        inner = gi * comp
        outer = (gains["outer_kp"] + gains["outer_ki"] / s) * gv * comp / (1 + inner)
        return {"current": inner, "voltage": outer}
    return {"voltage": gv * comp * (vin + REFERENCE.vf if method == "pi" else 1)}


def margins(loop, frequency=FREQUENCY):
    """All gain crosses and all negative-real-axis crossings of the Nyquist curve."""
    magnitude = 20 * np.log10(np.maximum(np.abs(loop), 1e-20))
    phase = np.unwrap(np.angle(loop)) * 180 / np.pi
    gain_cross = np.flatnonzero(np.signbit(magnitude[:-1]) != np.signbit(magnitude[1:]))
    real_cross = np.flatnonzero((np.signbit(loop.imag[:-1]) != np.signbit(loop.imag[1:]))
                                & (loop.real[:-1] < 0) & (loop.real[1:] < 0))
    if not len(gain_cross):
        return -180.0, -100.0, 0.0
    mix = -magnitude[gain_cross] / np.diff(magnitude)[gain_cross]
    pm = 180 + phase[gain_cross] + mix * np.diff(phase)[gain_cross]
    crossover = frequency[gain_cross] * (frequency[gain_cross + 1] / frequency[gain_cross]) ** mix
    gm = -magnitude[real_cross] if len(real_cross) else np.array([100.0])
    return float(min(pm)), float(min(gm)), float(min(crossover))


def cases(full=True):
    for name, p in corners().items():
        for vin in VIN_POINTS if full else (VIN_POINTS[0], VIN_POINTS[-1]):
            for load in ("cr", "cc", "cp") if full else ("cr", "cp"):
                for current in (2.0, IRATED) if full else (IRATED,):
                    num, den = sampled(p, vin, current, load)
                    yield name, vin, load, current, num, den


def responses(cases_to_run, frequency):
    z = np.exp(2j * np.pi * frequency * REFERENCE.period)
    rows = list(cases_to_run)
    channels = np.array([[np.polyval(n, z) / np.polyval(den, z) for n in num]
                         for _, _, _, _, num, den in rows])
    return rows, channels


BOUNDS = {
    "pi": ((-4, -1), (-0.5, 3)),
    "ff_pi": ((-2, 0.5), (0, 4)),
    "type_ii": ((-2, 0.5), (0, 4), (3, 4.4)),
    "type_iii": ((-2, 0.5), (3, 4.7), (3.2, 4.5), (2.35, 3.3), (3.2, 4.5)),
    "cascade": ((0.65, 1.35), (3.2, 4.3), (-0.23, 0.6), (3.8, 4.7)),
}


def optimize(method):
    frequency = FREQUENCY[::3]
    rows, channels = responses(cases(full=False), frequency)
    vins = np.array([row[1] for row in rows])[:, None]

    def objective(raw):
        gains = parameters(method, raw)
        result = []
        for label, loop in loops(method, gains, channels[:, 0], channels[:, 1], vins, frequency).items():
            pm, gm, fc = np.min([margins(row, frequency) for row in loop], axis=0)
            target_pm = 52 if label == "current" else 50
            if label == "current":
                result.append(10 * max(0., (3800 - fc) / 3800) ** 2)
            result.append(6 * max(0., (target_pm - pm) / 20) ** 2
                          + 6 * max(0., (8 - gm) / 6) ** 2
                          - (1 if label == "voltage" else .35) * np.log(max(1., fc)))
        return sum(result)

    best = differential_evolution(objective, BOUNDS[method], seed=474, popsize=8,
                                  maxiter=70, tol=0.001, polish=False)
    return parameters(method, best.x)


def closed_poles(method, gains, vin, num, den):
    """Characteristic polynomial, including the explicit z^-1 command delay."""
    p = np.polynomial.polynomial
    # Polynomials use ascending powers of z.
    s_num = np.array([-1., 1.]) * 2 / REFERENCE.period
    s_den = np.array([1., 1.])
    cn = p.polyadd(gains["kp"] * s_num, gains["ki"] * s_den)
    cd = p.polymul(s_num, [0., 1.])
    if "pole_hz" in gains:
        cn = p.polymul(cn, s_den)
        cd = p.polymul(cd, p.polyadd(s_den, s_num / (2 * np.pi * gains["pole_hz"])))
    if "zero_hz" in gains:
        cn = p.polymul(cn, p.polyadd(s_den, s_num / (2 * np.pi * gains["zero_hz"])))
        cd = p.polymul(cd, p.polyadd(s_den, s_num / (2 * np.pi * gains["second_pole_hz"])))
    plant_den = den[::-1]
    vn, i_n = num[:, ::-1]
    common = p.polymul(cd, plant_den)
    if method == "cascade":
        inner = p.polyadd(common, p.polymul(cn, i_n))
        on = p.polyadd(gains["outer_kp"] * s_num, gains["outer_ki"] * s_den)
        return p.polyroots(p.polyadd(p.polymul(inner, s_num), p.polymul(p.polymul(on, cn), vn)))
    scale = vin + REFERENCE.vf if method == "pi" else 1.
    return p.polyroots(p.polyadd(common, scale * p.polymul(cn, vn)))


def evaluate(method, gains):
    rows, channels = responses(cases(), FREQUENCY)
    vins = np.array([row[1] for row in rows])[:, None]
    outputs = {}
    for label, loop in loops(method, gains, channels[:, 0], channels[:, 1], vins).items():
        values = np.array([margins(row) for row in loop])
        outputs[label] = dict(zip(("phase_deg", "gain_db", "min_crossover_hz"), map(float, values.min(axis=0))))
    outputs["max_pole"] = float(max(max(abs(closed_poles(method, gains, vin, n, d)))
                                   for _, vin, _, _, n, d in rows))
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optimize", action="store_true")
    args = parser.parse_args()
    path = Path(__file__).with_name("gains.json")
    gains = {method: optimize(method) for method in METHODS} if args.optimize else json.loads(path.read_text())
    print(json.dumps({method: evaluate(method, gains[method]) for method in METHODS}, indent=2))
    if args.optimize:
        path.write_text(json.dumps(gains, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
