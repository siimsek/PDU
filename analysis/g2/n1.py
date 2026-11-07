"""G4 B1: N1 inductor saturation during a phase high-side switch short - energy/current balance and fix selection.

Inductor L(I): Vishay IHLP-4040DZ 6.8 uH typical curve, doc 34207 p.3 (read from the graph, typical only), normalised to
its 0 A value; datasheet curve ends at 16 A. Beyond 16 A there is NO manufacturer data: the last slope is extrapolated
down to a floor F (swept 0.5 ... 0.05 of nominal) - VARSAYIM; the result is reported for every floor.
Tolerance: the whole curve is scaled by L_TOL (-20 %).

Trip paths:
  V  : bus voltage reaches trip_max + 50 mV overdrive*k (comparator guarantee level), then t_V (protection.py chain)
  OC : faulted-phase current reaches the INA296 + TLV3601 threshold (max corner), then t_OC = INA296 settling
       (1 us TYPICAL, budget 1.5 us VARSAYIM) + TLV3601 + LVC1G11 + LVC1G74 + OV node RC + LM74502H 1 us (CONDITIONAL).
Isolation happens at the earlier of the two. O1 peak = VSAFE at isolation (no load, worst).
Path A: RK4 with L(i).  Path B: charge bound Q = integral of i dt with i(t) <= chord bounds; dV = Q/C.
Run: python -m analysis.g2.n1 -> reports/g4/n1-results.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2.params import v

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g4" / "n1-results.json"

CURVE = [(0.0, 1.0), (4.0, 0.977), (8.0, 0.924), (12.0, 0.826), (16.0, 0.735)]   # doc 34207 p.3, typical
SLOPE_EXT = (CURVE[-1][1] - CURVE[-2][1]) / (CURVE[-1][0] - CURVE[-2][0])          # per A, beyond 16 A (VARSAYIM)
FLOORS = (0.5, 0.3, 0.15, 0.10, 0.05)

# Phase overcurrent trip: INA296A2-Q1 (G=20, CM -5..110 V; SBOS... p.4-6) -> TLV3601 (IN- = INA out, IN+ = threshold
# from REF5025A via 255 ohm / 1.00 kohm TNPW 0.1 %) -> SN74LVC1G11 3-input AND with the bus-OV comparator -> latch PRE.
INA_G = 20.0
INA_G_TOL = 0.001                    # VARSAYIM screen (datasheet gain error is smaller)
INA_VOS = 25e-6                      # VARSAYIM screen RTI (A3+ max 10 uV in datasheet table)
INA_SETTLE_TYP = 1.0e-6              # DATASHEET settling to 1 % TYPICAL only (no max)
INA_DELAY_SCREEN = 1.5e-6            # VARSAYIM: 1.5 x typical used in the budget -> OC path timing is CONDITIONAL
OCT_RT, OCT_RB = 255.0, 1000.0       # threshold divider from 2.5 V reference
LVC1G11_TPD = 7.8e-9                 # SN74LVC1G11 tpd max (worst column, -40..125 C)


def g(i, floor):
    i = abs(i)
    if i <= CURVE[-1][0]:
        for (i0, g0), (i1, g1) in zip(CURVE, CURVE[1:]):
            if i <= i1:
                return g0 + (g1 - g0) * (i - i0) / (i1 - i0)
    return max(floor, CURVE[-1][1] + SLOPE_EXT * (i - CURVE[-1][0]))


def oc_threshold():
    """Faulted-phase current at which the TLV3601 trips (all corners)."""
    import itertools
    vals = []
    for sr, sd, st, sb, stt, stb, so, h, sg, srs, srst, sv in itertools.product(
            (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (v("CMP_HYS_MIN"), v("CMP_HYS_MAX")),
            (-1, 1), (-1, 1), (-1, 1), (-1, 1)):
        vref = v("VREF") * (1 + sr * v("VREF_TOL")) * (1 + sd * v("VREF_TC") * v("DT_REF_BOX"))
        rt = OCT_RT * (1 + st * 0.001) * (1 + stt * 15e-6 * 100)
        rb = OCT_RB * (1 + sb * 0.001) * (1 + stb * 15e-6 * 100)
        vth = vref * rb / (rt + rb) + so * v("CMP_VOS") + h / 2 + v("CMP_IB") * (rt * rb / (rt + rb))
        rs = v("RS_NOM") * (1 + srs * v("RS_TOL")) * (1 + (srst * v("RS_TCR") * (100 if srst > 0 else 65)))
        vals.append(vth / (INA_G * (1 + sg * INA_G_TOL) * rs) + sv * INA_VOS / rs)
    i_nom = v("VREF") * OCT_RB / (OCT_RT + OCT_RB) / (INA_G * v("RS_NOM"))
    return min(vals), i_nom, max(vals)


def chains():
    p = json.loads((ROOT / "reports" / "g2" / "protection-results.json").read_text(encoding="utf-8"))
    t_v = p["timing"]["total_max_s"]
    rest = t_v - v("CMP_TPD_MAX")              # latch + OV RC + LM74502H
    t_oc = INA_DELAY_SCREEN + v("CMP_TPD_MAX") + LVC1G11_TPD + rest
    vg = p["trip_threshold"]["path_a_enumerated"][1] + v("CMP_OD") * p["precision_divider"]["k"]
    return t_v, t_oc, vg, p["bus_c_min_F"]


def simulate(floor, use_oc=True, vin=26.0, v0=10.8333, lf=1 - 0.20, r=0.02 + 0.0233 + 0.0075, dt=2e-10):
    """Path A: RK4 (inductor current via di/dt = (vin - v - i r)/L(i)), no load."""
    t_v, t_oc, vg, c = chains()
    i_oc = oc_threshold()[2]
    L0 = v("L_NOM") * lf
    i, vv, t = 0.0, v0, 0.0
    t_open = None
    t_trip_v = t_trip_oc = None

    def f(i_, v_):
        return (vin - v_ - i_ * r) / (L0 * g(i_, floor)), i_ / c
    while True:
        k1 = f(i, vv)
        k2 = f(i + dt / 2 * k1[0], vv + dt / 2 * k1[1])
        k3 = f(i + dt / 2 * k2[0], vv + dt / 2 * k2[1])
        k4 = f(i + dt * k3[0], vv + dt * k3[1])
        i += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        vv += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt
        if t_trip_v is None and vv >= vg:
            t_trip_v = t
        if use_oc and t_trip_oc is None and i >= i_oc:
            t_trip_oc = t
        cand = [x for x in ((t_trip_v + t_v) if t_trip_v else None, (t_trip_oc + t_oc) if t_trip_oc else None) if x]
        if cand and t >= min(cand):
            t_open = t
            break
    energy = 0.0
    # stored inductor energy at opening: integral of i dL-weighted flux = sum L(i) i di
    n = 400
    for k in range(n):
        ii = i * (k + 0.5) / n
        energy += L0 * g(ii, floor) * ii * (i / n)
    path = "OC" if (t_trip_oc and t_trip_oc + t_oc <= (t_trip_v + t_v if t_trip_v else 1)) else "V"
    return {"floor": floor, "use_oc": use_oc, "o1_peak_V": vv, "i_at_open_A": i, "t_open_s": t_open,
            "trip_path": path, "t_trip_v_s": t_trip_v, "t_trip_oc_s": t_trip_oc, "E_L_at_open_J": energy}


def charge_bound(floor, vin=26.0, v0=10.8333, lf=1 - 0.20):
    """Path B: OC-path upper bound by fastest admissible current growth.
    Before trip: i(t) convex (L non-increasing) -> Q1 <= 0.5*I_oc*t1_max, t1_max with L_max (+20 %, 0 A value).
    During t_oc: di/dt <= (vin - v0)/L_low, L_low = curve(16 A)*L_nom*lf below 16 A (datasheet range, monotone curve)
    and floor*L_nom*lf above 16 A (VARSAYIM); charge = integral of that fastest i(t)."""
    t_v, t_oc, vg, c = chains()
    i_oc = oc_threshold()[2]
    t1_max = i_oc * v("L_NOM") * 1.20 / (vin - 12.0)
    q1 = 0.5 * i_oc * t1_max
    s1 = (vin - v0) / (v("L_NOM") * lf * CURVE[-1][1])
    s2 = (vin - v0) / (v("L_NOM") * lf * floor)
    ta = min(t_oc, max(0.0, (CURVE[-1][0] - i_oc) / s1))
    q2a = i_oc * ta + 0.5 * s1 * ta * ta
    i_a = i_oc + s1 * ta
    tb = t_oc - ta
    q2b = i_a * tb + 0.5 * s2 * tb * tb
    return {"floor": floor, "o1_peak_bound_V": v0 + (q1 + q2a + q2b) / c, "q1_C": q1, "q2_C": q2a + q2b,
            "i_end_bound_A": i_a + s2 * tb}


def compute():
    i_min, i_nom, i_max = oc_threshold()
    t_v, t_oc, vg, c = chains()
    rows = []
    for fl in FLOORS:
        a_v = simulate(fl, use_oc=False)
        a_oc = simulate(fl, use_oc=True)
        b = charge_bound(fl)
        rows.append({"floor": fl, "voltage_trip_only": a_v, "with_oc_trip": a_oc, "oc_bound": b,
                     "diff_A_vs_B_V": b["o1_peak_bound_V"] - a_oc["o1_peak_V"]})
    # vin / v0 corners with the OC trip at the most pessimistic floor
    corners = [simulate(0.05, True, vin=vi, v0=v0) | {"vin": vi, "v0": v0} for vi in (20.0, 26.0) for v0 in (10.8333, 11.1605)]
    normal_peak_max = 8.974   # power.py inductor peak at cycle-by-cycle limit (VCS max, RS min cold, 53.3 V overshoot)
    sens = []
    global INA_DELAY_SCREEN
    keep = INA_DELAY_SCREEN
    for d in (1.0e-6, 1.5e-6, 2.0e-6, 3.0e-6, 4.0e-6):
        INA_DELAY_SCREEN = d
        r_ = simulate(0.05, True, v0=11.1605)
        sens.append({"ina_delay_s": d, "o1_peak_V": r_["o1_peak_V"], "i_at_open_A": r_["i_at_open_A"], "trip_path": r_["trip_path"]})
    INA_DELAY_SCREEN = keep
    res = {
        "ina_delay_sensitivity_floor0p05_v0high": sens,
        "classification": "HESAP; L(I) typical curve to 16 A (DATASHEET doc 34207 p.3) + swept floor beyond (VARSAYIM)",
        "curve_points": CURVE, "slope_beyond_16A_per_A": SLOPE_EXT,
        "oc_threshold_A": {"min": i_min, "nom": i_nom, "max": i_max, "divider_ohm": [OCT_RT, OCT_RB],
                           "margin_over_normal_peak": i_min / normal_peak_max},
        "t_voltage_chain_s": t_v, "t_oc_chain_s": t_oc, "v_guarantee_V": vg, "bus_c_min_F": c,
        "rows": rows, "oc_corners_floor_0p05": corners,
        "worst_with_oc_V": max(max(r["with_oc_trip"]["o1_peak_V"] for r in rows), max(cn["o1_peak_V"] for cn in corners)),
        "worst_voltage_only_V": max(r["voltage_trip_only"]["o1_peak_V"] for r in rows),
    }
    return res


def main():
    res = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"oc_threshold": res["oc_threshold_A"], "worst_with_oc_V": res["worst_with_oc_V"],
                      "worst_voltage_only_V": res["worst_voltage_only_V"]}))
    for r in res["rows"]:
        print(r["floor"], round(r["voltage_trip_only"]["o1_peak_V"], 4), round(r["with_oc_trip"]["o1_peak_V"], 4),
              round(r["oc_bound"]["o1_peak_bound_V"], 4), round(r["with_oc_trip"]["i_at_open_A"], 1), r["with_oc_trip"]["trip_path"])


if __name__ == "__main__":
    main()
