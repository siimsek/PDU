"""G2 Stage 2: common-bus series isolator - threshold, timing, fault ramp, FET and fail-safe calculations.

Selected chain (see reports/g2/PROTECTION-DECISION.md):
  VRAW --Rt/Rb--> TLV3601 IN- ; REF5025A -> IN+ ; OUT (low = overvoltage) -> SN74LVC1G74 PRE_n
  Q -> Rq -> LM74502H OV pin (also fed by an independent coarse VRAW divider Rt2/Rb2)
  LM74502H GATE -> CSD19531Q5A (drain VRAW, source VSAFE); EN/UVLO <- 5 V rail divider.

Every headline number is produced twice (path A / path B) and the difference is reported.
Run: python -m analysis.g2.protection  -> reports/g2/protection-results.json
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2.params import v

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g2" / "protection-results.json"

E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43,
       1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10,
       2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
       3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53,
       4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
       6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]

# ---- design values (selected in this module; tests pin them)
RB = 2.32e3            # precision divider bottom, TNPW1206 0.1 % 15 ppm/K (pair search, see PROTECTION-DECISION)
R_TOL = 0.001          # 0.1 %
R_TCR = 15e-6          # 15 ppm/K: TNPW "X" code with 0.1 % (doc 28758 p.3; 10 ppm needs TNPU series)
TRIP_MIN_TARGET = v("BUS_TRANSIENT_MAX") + 0.030   # R03: 11.25 V
RT2 = 60.4e3           # coarse divider top (CRCW 1 %); pair search: coarse_min >= precision trip_max + 30 mV (G3 fix)
RB2 = 19.6e3           # coarse divider bottom (CRCW 1 %)
RQ = 10.0e3            # latch Q -> OV pin
COARSE_TOL = 0.01
REN_TOP = 15.0e3       # 5 V rail -> LM74502H EN/UVLO
REN_BOT = 10.0e3
R_BLEED_5V = 1.0e3     # 5 V rail bleeder
T_OV_RC = 50e-9        # OV node RC allowance (HESAP below)
C_OV_PAR = 10e-12      # VARSAYIM pin + trace capacitance


def e96_values(lo, hi):
    out = []
    dec = 1.0
    while dec <= hi:
        for m in E96:
            r = m * dec
            if lo <= r <= hi:
                out.append(round(r, 6))
        dec *= 10
    return out


# ---------------------------------------------------------------- threshold
def _trip(vref, rt, rb, voff, ib):
    """Bus voltage at which IN- (divider node, loaded by bias ib into the pin) equals vref+voff."""
    rth = rt * rb / (rt + rb)
    return (vref + voff + ib * rth) * (rt + rb) / rb


def trip_corners_enumerated(rt, rb=RB, tol=R_TOL, tcr=R_TCR):
    """Path A: exhaustive vertex enumeration (temperature shared by all drift terms)."""
    dT = v("DT_DRIFT")
    vals = []
    for sref, sdr, st, sb, stt, stb, sos, hys, sib in itertools.product(
            (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1),
            (v("CMP_HYS_MIN"), v("CMP_HYS_MAX")), (-1, 1)):
        vref = v("VREF") * (1 + sref * v("VREF_TOL")) * (1 + sdr * v("VREF_TC") * v("DT_REF_BOX"))
        rt_ = rt * (1 + st * tol) * (1 + stt * tcr * dT)
        rb_ = rb * (1 + sb * tol) * (1 + stb * tcr * dT)
        voff = sos * v("CMP_VOS") + hys / 2.0  # rising threshold sits half the hysteresis above offset
        vals.append(_trip(vref, rt_, rb_, voff, sib * v("CMP_IB")))
    return min(vals), max(vals)


def trip_corners_interval(rt, rb=RB, tol=R_TOL, tcr=R_TCR):
    """Path B: first-order worst-case sensitivity sum around nominal (independent arithmetic)."""
    dT = v("DT_DRIFT")
    k = (rt + rb) / rb
    rth = rt * rb / (rt + rb)
    vnom_in = v("VREF") + (v("CMP_HYS_MIN") + v("CMP_HYS_MAX")) / 4.0
    nom = vnom_in * k
    d_ref = v("VREF") * (v("VREF_TOL") + v("VREF_TC") * v("DT_REF_BOX")) * k
    d_ratio = vnom_in * (rt / rb) * 2 * (tol + tcr * dT)       # dk = (rt/rb)*(drt/rt - drb/rb)
    d_os = v("CMP_VOS") * k
    d_hys = (v("CMP_HYS_MAX") - v("CMP_HYS_MIN")) / 4.0 * k
    d_ib = v("CMP_IB") * rth * k
    span = d_ref + d_ratio + d_os + d_hys + d_ib
    return nom - span, nom + span, {"ref": d_ref, "ratio": d_ratio, "offset": d_os, "hyst": d_hys, "bias": d_ib}


def select_rt():
    for rt in e96_values(5e3, 20e3):
        lo, hi = trip_corners_enumerated(rt)
        if lo >= TRIP_MIN_TARGET:
            return rt, lo, hi
    raise RuntimeError("no E96 value meets trip_min target")


# ---------------------------------------------------------------- input clamp / rail back-power
def clamp_current(vraw, vcc, rt, rb=RB, vclamp_over=0.3):
    vth = vraw * rb / (rt + rb)
    rth = rt * rb / (rt + rb)
    return max(0.0, (vth - (vcc + vclamp_over)) / rth)


def clamp_current_worst(vraw, vcc, rt):
    """Path B: resistor-tolerance corners and clamp at the rail itself (0 V over-rail, conservative)."""
    worst = 0.0
    for st, sb in itertools.product((-1, 1), (-1, 1)):
        rt_ = rt * (1 + st * R_TOL)
        rb_ = RB * (1 + sb * R_TOL)
        worst = max(worst, clamp_current(vraw, vcc, rt_, rb_, vclamp_over=0.0))
    return worst


def rail_backpower(vraw, rt, r_bleed=R_BLEED_5V):
    """5 V rail with LDO absent: injected clamp current only sinks into bleeder. Solve Vrail."""
    vth = vraw * RB / (rt + RB)
    rth = rt * RB / (rt + RB)
    # (vth - vrail - 0.3)/rth = vrail/r_bleed
    vrail = (vth - 0.3) / (1 + rth / r_bleed)
    return max(0.0, vrail)


# ---------------------------------------------------------------- coarse OV and latch drive at LM74502H OV pin
def ov_node(vraw, vq, rt2=RT2, rb2=RB2, rq=RQ):
    g = 1 / rt2 + 1 / rb2 + 1 / rq
    return (vraw / rt2 + vq / rq) / g


def coarse_trip_corners():
    """VRAW at which OV pin reaches V(OVR) with latch Q low (VQ=0). Path A enumeration."""
    vals = []
    for ovr in (v("DRV_OVR_MIN"), v("DRV_OVR_MAX")):
        for st, sb, sq in itertools.product((-1, 1), repeat=3):
            rt2 = RT2 * (1 + st * COARSE_TOL)
            rb2 = RB2 * (1 + sb * COARSE_TOL)
            rq = RQ * (1 + sq * COARSE_TOL)
            g = 1 / rt2 + 1 / rb2 + 1 / rq
            vals.append(ovr * g * rt2)
    return min(vals), max(vals)


def coarse_trip_interval():
    """Path B: nominal ratio x threshold bounds x combined resistor tolerance (first order)."""
    g = 1 / RT2 + 1 / RB2 + 1 / RQ
    k = g * RT2
    dk = 2 * COARSE_TOL * (k - 1)  # conservative first-order bound on ratio change
    return v("DRV_OVR_MIN") * (k - dk), v("DRV_OVR_MAX") * (k + dk)


def latch_drive_margin(vq_min):
    """OV pin with VRAW=0 and Q high (worst: resistor corners)."""
    worst = min(ov_node(0.0, vq_min, RT2 * (1 + a * COARSE_TOL), RB2 * (1 + b * COARSE_TOL), RQ * (1 + c * COARSE_TOL))
                for a, b, c in itertools.product((-1, 1), repeat=3))
    return worst, worst - v("DRV_OVR_MAX")


def ov_rc_time():
    rth = 1 / (1 / RT2 + 1 / RB2 + 1 / RQ)
    tau = rth * C_OV_PAR
    # Q step drives node from ~0 toward vfinal; need to cross OVR_MAX
    vq = 5.0 * (1 - v("LDO5_VOUT_TOL")) - 0.1
    vfinal = ov_node(0.0, vq)
    frac = v("DRV_OVR_MAX") / vfinal
    return tau, -tau * math.log(1 - frac)


# ---------------------------------------------------------------- EN/UVLO rail gating
def en_gate_thresholds():
    r = REN_BOT / (REN_TOP + REN_BOT)
    rth = REN_TOP * REN_BOT / (REN_TOP + REN_BOT)
    isink = v("DRV_EN_ISINK_MAX")
    on_max = (v("DRV_EN_R_MAX") + isink * rth) / r
    off_min = v("DRV_EN_F_MIN") / r
    off_max = (v("DRV_EN_F_MAX") + isink * rth) / r
    return {"ratio": r, "rail_on_max_V": on_max, "rail_off_min_V": off_min, "rail_off_max_V": off_max,
            "latch_vcc_min_V": v("LAT_VCC_MIN"), "comparator_por_V": v("CMP_POR"),
            "gate_off_before_latch_undefined": off_min > v("LAT_VCC_MIN"),
            "gate_off_before_comparator_por": off_min > v("CMP_POR"),
            "rail_on_below_5V_min": on_max < 5.0 * (1 - v("LDO5_VOUT_TOL"))}


# ---------------------------------------------------------------- timing
def chain_delay():
    tau, t_rc = ov_rc_time()
    parts = {"comparator_tpd_max": v("CMP_TPD_MAX"), "latch_pre_to_q_max": v("LAT_TPD_MAX"),
             "ov_node_rc": max(t_rc, 0.0), "lm74502h_tovp_off_max": v("DRV_TOVP_OFF_MAX")}
    return sum(parts.values()), parts, tau


def gate_equivalence():
    vgs_max = v("DRV_VCAP_MAX")
    qg_at_vgs = v("QISO_QG_MAX_10V") + v("QISO_CISS_MAX") * (vgs_max - 10.0)
    q_test = v("DRV_TOVP_TEST_CGS") * vgs_max
    return {"vgs_max_V": vgs_max, "fet_qg_at_vgs_max_C": qg_at_vgs, "test_load_charge_C": q_test,
            "ratio": qg_at_vgs / q_test, "ciss_max_F": v("QISO_CISS_MAX"),
            "status": "conditional: lumped 4.7 nF test load vs real FET charge ratio near 1; bench measurement required"}


# ---------------------------------------------------------------- high-side short ramp (one phase shorted)
def ramp_closed_form(t, vin, v0, l, c):
    """Path A: lossless LC from rest (i_excess(0)=0): v(t) = vin - (vin-v0) cos(w t)."""
    w = 1 / math.sqrt(l * c)
    return vin - (vin - v0) * math.cos(w * t)


def ramp_numeric(t_end, vin, v0, l, c, r, dt=1e-9):
    """Path B: RK4 of L di/dt = vin - v - i r ; C dv/dt = i (no load: worst)."""
    i, vv, t = 0.0, v0, 0.0
    traj = [(0.0, v0)]

    def f(i_, v_):
        return (vin - v_ - i_ * r) / l, i_ / c
    while t < t_end - 1e-15:
        h = min(dt, t_end - t)
        k1 = f(i, vv)
        k2 = f(i + h / 2 * k1[0], vv + h / 2 * k1[1])
        k3 = f(i + h / 2 * k2[0], vv + h / 2 * k2[1])
        k4 = f(i + h * k3[0], vv + h * k3[1])
        i += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        vv += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += h
        traj.append((t, vv))
    return traj


def time_to_reach_closed(vtarget, vin, v0, l, c):
    w = 1 / math.sqrt(l * c)
    x = (vin - vtarget) / (vin - v0)
    return math.acos(x) / w


def o1_peak_bound(vtrip_max, k_div, t_chain, vin, v0, l, c, r):
    """Bus (=VSAFE=O1 upper bound) when the isolator is guaranteed open."""
    vg = vtrip_max + v("CMP_OD") * k_div          # bus level where comparator delay guarantee applies
    # path A (closed form, r=0)
    t_g = time_to_reach_closed(vg, vin, v0, l, c)
    peak_a = ramp_closed_form(t_g + t_chain, vin, v0, l, c)
    # path B (numeric with r)
    traj = ramp_numeric(t_g * 1.5 + t_chain + 2e-6, vin, v0, l, c, r)
    t_gb = next(t for t, vv in traj if vv >= vg)
    peak_b = next(vv for t, vv in traj if t >= t_gb + t_chain)
    slope_a = (vin - v0) / math.sqrt(l * c) * math.sin(t_g / math.sqrt(l * c))
    return {"v_guarantee_V": vg, "t_to_guarantee_s": t_g, "dvdt_at_guarantee_V_per_s": slope_a,
            "peak_closed_form_V": peak_a, "peak_numeric_V": peak_b, "diff_V": peak_a - peak_b}


def bus_c_min(n_cout):
    c_safe_min = 2 * 100e-9 * 0.5 + 2 * 10e-6 * 0.4   # VARSAYIM CEFIN/CEFOUT retained at 11 V
    return n_cout * v("COUT_C_PART_MIN") + c_safe_min, c_safe_min


# ---------------------------------------------------------------- FET
def fet_checks(i_cont=None, i_fault=15.0):
    i_cont = i_cont or v("I_BUS_CAP")
    rds_hot = v("QISO_RDS_MAX_10V") * v("QISO_RDS_HOT_FACTOR")
    p = i_cont ** 2 * rds_hot
    tj = v("T_AMB_MAX") + p * v("QISO_RTH_JA")
    vds_max = v("VIN_CLAMP")
    e_off = 0.5 * i_fault * vds_max * v("DRV_TOVP_OFF_MAX")     # triangle bound, conservative
    return {"rds_hot_ohm": rds_hot, "p_cond_W": p, "tj_est_C": tj, "vds_max_V": vds_max,
            "vds_margin_V": v("QISO_VDS") - vds_max, "vgs_max_V": v("DRV_VCAP_MAX"),
            "vgs_rating_ok": v("QISO_VGS_ABS") >= v("DRV_VGS_MIN_RATING") and v("DRV_VCAP_MAX") < v("QISO_VGS_ABS"),
            "turnoff_energy_bound_J": e_off, "eas_J": v("QISO_EAS"), "energy_ratio": e_off / v("QISO_EAS"),
            "soa_graph": "AÇIK: SOA graph not numerically extractable; energy bound vs EAS only"}


def divider_power(rt):
    out = {}
    for vraw in (26.0, v("VIN_CLAMP")):
        i = vraw / (rt + RB)
        out[f"{vraw:g}V"] = {"rt_W": i * i * rt, "rb_W": i * i * RB}
    i2 = 26.0 / (RT2 + RB2)
    out["coarse_26V_rt2_W"] = i2 * i2 * RT2
    return out


def por_clear():
    """CLR_n RC POR: 100k/1uF to 5 V; CLR released when V > 0.7*VCC (VIH, LVC family)."""
    r, c = 100e3, 1e-6
    t_rel = -r * c * math.log(1 - 0.7)
    return {"r_ohm": r, "c_F": c, "t_release_s": t_rel,
            "note": "VIH=0.7*VCC used as LVC screen; capacitor tolerance +/-10% -> +/-10% time (HESAP)"}


def compute(n_cout=None):
    n_cout = n_cout or D.N_COUT
    rt, lo, hi = select_rt()
    lo_b, hi_b, contrib = trip_corners_interval(rt)
    k_div = (rt + RB) / RB
    t_chain, parts, tau = chain_delay()
    c_min, c_safe = bus_c_min(n_cout)
    cases = []
    for vin in (v("VIN_MIN"), v("VIN_MAX")):
        for v0 in (10.8333, v("BUS_STEADY_MAX")):
            for rsrc in (v("R_SRC_MIN"), v("R_SRC_MAX")):
                for lf in (1 - v("L_TOL"), 1.0):
                    r = rsrc + v("L_DCR_MAX") + v("RS_NOM")
                    res = o1_peak_bound(hi, k_div, t_chain, vin, v0, v("L_NOM") * lf, c_min, r)
                    res.update({"vin": vin, "v0": v0, "r_src": rsrc, "l_factor": lf})
                    cases.append(res)
    worst = max(cases, key=lambda d: max(d["peak_closed_form_V"], d["peak_numeric_V"]))
    worst_peak = max(worst["peak_closed_form_V"], worst["peak_numeric_V"])
    ctl, cth = coarse_trip_corners()
    ctl_b, cth_b = coarse_trip_interval()
    vq_min = 5.0 * (1 - v("LDO5_VOUT_TOL")) - 0.55   # LVC VOH at 8 mA screen (conservative)
    ov_latched, ov_margin = latch_drive_margin(vq_min)
    res = {
        "classification": "HESAP with DATASHEET inputs; no physical measurement",
        "precision_divider": {"rt_ohm": rt, "rb_ohm": RB, "tolerance": R_TOL, "tcr_per_K": R_TCR,
                              "k": k_div, "trip_min_target_V": TRIP_MIN_TARGET},
        "trip_threshold": {"path_a_enumerated": [lo, hi], "path_b_interval": [lo_b, hi_b],
                           "diff_V": [lo - lo_b, hi - hi_b], "contributions_V": contrib,
                           "margin_above_transient_band_V": lo - v("BUS_TRANSIENT_MAX"),
                           "comparator_vcm_at_trip_V": hi / k_div},
        "clamp_current": {
            "vcc0_vraw_clamp_A_pathA": clamp_current(v("VIN_CLAMP"), 0.0, rt),
            "vcc0_vraw_clamp_A_pathB_worst": clamp_current_worst(v("VIN_CLAMP"), 0.0, rt),
            "vcc5_vraw_clamp_A": clamp_current(v("VIN_CLAMP"), 5.0, rt),
            "limit_A": v("CMP_ICLAMP_MAX"),
            "vcm_out_of_range_above_vraw_V": (5.0 * (1 - v("LDO5_VOUT_TOL")) + v("CMP_VCM_HI")) * k_div},
        "rail_backpower_ldo_absent": {f"{x:g}V": rail_backpower(x, rt) for x in (26.0, 40.709, v("VIN_CLAMP"))},
        "divider_power_W": divider_power(rt),
        "coarse_ov": {"path_a": [ctl, cth], "path_b": [ctl_b, cth_b], "diff_V": [ctl - ctl_b, cth - cth_b],
                      "above_transient_band": ctl > v("BUS_TRANSIENT_MAX"),
                      "below_efuse_in_recommended": cth < v("EF_IN_REC"),
                      "latched_ov_pin_min_V": ov_latched, "latched_margin_over_ovr_max_V": ov_margin},
        "en_gating": en_gate_thresholds(),
        "timing": {"total_max_s": t_chain, "parts_s": parts, "ov_node_tau_s": tau,
                   "status": "comparator max valid only at 50 mV OD and VCM=VEE+0.3 V; driver max valid at 4.7 nF lumped load"},
        "gate_equivalence": gate_equivalence(),
        "bus_c_min_F": c_min, "c_safe_min_F": c_safe, "n_cout": n_cout,
        "o1_peak_cases": cases,
        "o1_peak_worst": {"case": worst, "peak_V": worst_peak, "limit_V": v("O1_PEAK_MAX"),
                          "margin_V": v("O1_PEAK_MAX") - worst_peak, "pass_hesap": worst_peak <= v("O1_PEAK_MAX")},
        "fet": fet_checks(),
        "por_clear": por_clear(),
    }
    return res


def main():
    res = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    w = res["o1_peak_worst"]
    print(json.dumps({"rt": res["precision_divider"]["rt_ohm"], "trip": res["trip_threshold"]["path_a_enumerated"],
                      "o1_peak_worst_V": w["peak_V"], "margin_V": w["margin_V"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
