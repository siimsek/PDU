"""G4 B4: stacked static tolerance + load-step corners, FB trim footprint design.

Static window (untrimmed): VFB 794..806 mV (LM70880 p.7, -40..150 C, includes initial + temperature), RFB1/RFB2
0.1 % / 25 ppm/K, IFB 75 nA.  Trim: RFB2 split into RFB2 = 9.76 kOhm (fixed) + R_TRIM (series, default 442 Ohm,
selected per board from the table; parallel trims were rejected: trim-down needed 8-48 MOhm). Board-level acceptance: measure VOUT at 25 C, no load, DMM 0.05 %, fit the table value.
Trimmed window = measurement uncertainty + half step + temperature-only part of VFB and resistor TCR.
VARSAYIM: the temperature-only part of the VFB tolerance is half of the full +/-0.75 % (datasheet does not split
initial vs. temperature) -> if it is larger, the trimmed window widens (sensitivity printed).
Run: python -m analysis.g2.b4 -> reports/g4/b4-results.json
"""
from __future__ import annotations

import json
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2.params import v
from analysis.g2.protection import e96_values

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g4" / "b4-results.json"

R1, R2 = v("RFB1"), v("RFB2")
VNOM = v("VFB_NOM") * (1 + R1 / R2)
STEP = 0.0025          # 0.25 % trim step
DMM = 0.0005           # VARSAYIM 6.5-digit DMM accuracy
VFB_TEMP_FRACTION = 0.5


def static_window():
    lo = v("VFB_MIN") * (1 + R1 * 0.999 * (1 - 25e-6 * 100) / (R2 * 1.001 * (1 + 25e-6 * 100))) - v("IFB_MAX") * R1
    hi = v("VFB_MAX") * (1 + R1 * 1.001 * (1 + 25e-6 * 100) / (R2 * 0.999 * (1 - 25e-6 * 100))) + v("IFB_MAX") * R1
    return lo, hi


RFB2_FIXED = 9.76e3          # TNPW 0.1 %
R_TRIM_DEFAULT = 442.0       # TNPW 0.1 %, 9.76k + 442 = 10.202k (nominal unchanged)


def trim_table():
    """Series trim resistor R_TRIM in the RFB2 leg: VOUT = VFB*(1 + RFB1/(RFB2_FIXED + R_TRIM))."""
    rows = []
    e96 = sorted(set(e96_values(100.0, 1000.0) + [442.0]))
    for k in range(-6, 7):
        target = VNOM * (1 + k * STEP)
        r2 = R1 / (target / v("VFB_NOM") - 1)
        rt = r2 - RFB2_FIXED
        rt_e = min(e96, key=lambda r: abs(r - rt))
        vout = v("VFB_NOM") * (1 + R1 / (RFB2_FIXED + rt_e))
        rows.append({"step_pct": k * STEP * 100, "R_TRIM_ohm": rt_e, "vout_V": vout, "error_pct": (vout / target - 1) * 100})
    return rows


def trimmed_window(temp_fraction=VFB_TEMP_FRACTION):
    vfb_temp = (v("VFB_MAX") - v("VFB_NOM")) / v("VFB_NOM") * temp_fraction
    r_tcr = 2 * 25e-6 * 75          # both resistors, 25 C -> 100 C ambient span (VARSAYIM 75 K)
    half = DMM + STEP / 2 + vfb_temp + r_tcr * (1 - 1 / (1 + R1 / R2)) + v("IFB_MAX") * R1 / VNOM
    return VNOM * (1 - half), VNOM * (1 + half), half


def corner_table(dip_v, overshoot_v):
    lo_u, hi_u = static_window()
    lo_t, hi_t, _ = trimmed_window()
    t = []
    for name, lo, hi in (("untrimmed", lo_u, hi_u), ("trimmed", lo_t, hi_t)):
        t.append({"window": name, "static_lo_V": lo, "static_hi_V": hi, "step_min_V": lo - dip_v,
                  "release_max_V": hi + overshoot_v,
                  "min_ok": lo - dip_v >= v("BUS_MIN_STEP"), "max_ok_band": hi + overshoot_v < v("BUS_TRANSIENT_MAX"),
                  "steady_ok": hi <= v("BUS_STEADY_MAX")})
    return t


def compute(dip_v=None, overshoot_v=None):
    sim = json.loads((ROOT / "reports" / "g2" / "sim-results.json").read_text(encoding="utf-8"))
    runs = sim["runs"]
    if dip_v is None:
        noms = [r for n, r in runs.items() if n.startswith("f3_nominal")]
        pre = [r["measures"]["bus_pre"] for r in noms]
        dip_v = max(r["measures"]["bus_pre"] - r["measures"]["bus_min"] for r in noms)
        overshoot_v = max(r["measures"]["bus_max_release"] - r["measures"]["bus_pre"] for r in noms)
    res = {"classification": "HESAP + SİM (dip/overshoot from F3 nominal runs)", "vnom_V": VNOM,
           "static_window_untrimmed_V": static_window(), "trim_table": trim_table(),
           "trimmed_window_V": trimmed_window()[:2], "trimmed_half_width": trimmed_window()[2],
           "trimmed_window_if_vfb_temp_full": trimmed_window(1.0)[:2],
           "f3_dip_V": dip_v, "f3_overshoot_V": overshoot_v, "corners": corner_table(dip_v, overshoot_v),
           "n_cout": D.N_COUT, "rcomp": D.RCOMP}
    return res


def main():
    res = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("static_window_untrimmed_V", "trimmed_window_V", "f3_dip_V", "f3_overshoot_V")}))
    for c in res["corners"]:
        print(c)


if __name__ == "__main__":
    main()
