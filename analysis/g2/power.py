"""G2 Stage 3: power stage, ILIM/IMON/EN, UVLO and input protection calculations (two paths each).

Run: python -m analysis.g2.power -> reports/g2/power-results.json
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2.params import EF_ILIM_TABLE, v

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g2" / "power-results.json"

VOUT = 11.0
SHARE = 1.10            # VARSAYIM worst phase share (+10 %), RS 1 % mismatch + CS amp mismatch unknown
ETA_ASSUMED = 0.92      # VARSAYIM converter efficiency at 82.5 W (datasheet typical curve only)
CORE_LOSS_EACH = 0.15   # VARSAYIM IHLP core loss per inductor (vendor calculator not available) -> AÇIK
CU_TC = 0.00393         # copper resistance tempco 1/K (physics constant)


def _triangle(t, period, duty, i_avg, di):
    """inductor current at time t for a CCM buck phase starting at valley at t=0."""
    tp = (t % period) / period
    if tp < duty:
        return i_avg - di / 2 + di * tp / duty
    return i_avg + di / 2 - di * (tp - duty) / (1 - duty)


# ------------------------------------------------------------- inductor / sense
def ripple(vin, l, fsw, vout=VOUT):
    return (vin - vout) * vout / (vin * l * fsw)


def inductor(vin=None, i_total=None):
    vin = vin or v("VIN_MAX")
    i_total = i_total or v("I_BUS_CAP")
    l_min = v("L_NOM") * (1 - v("L_TOL"))
    fsw = v("FSW_MIN")
    di = ripple(vin, l_min, fsw)
    i_ph = i_total / 2 * SHARE
    i_pk = i_ph + di / 2
    irms_a = math.sqrt(i_ph ** 2 + di ** 2 / 12)
    # path B: numeric RMS and peak of the triangle
    n = 20000
    period = 1 / fsw
    d = VOUT / vin
    samples = [_triangle(k * period / n, period, d, i_ph, di) for k in range(n)]
    irms_b = math.sqrt(sum(s * s for s in samples) / n)
    pk_b = max(samples)
    # current limit peak (cycle-by-cycle) and overshoot from CS delay
    rs_min = v("RS_NOM") * (1 - v("RS_TOL")) * (1 - v("RS_TCR") * 65)   # cold
    i_lim_pk_max = v("VCS_TH_MAX") / rs_min + (v("VIN_CLAMP") - VOUT) / l_min * v("T_CS_DELAY")
    rs_max = v("RS_NOM") * (1 + v("RS_TOL")) * (1 + v("RS_TCR") * 100)
    di_max_l = ripple(vin, l_min, fsw)
    i_lim_avg_min_phase = v("VCS_TH_MIN") / rs_max - di_max_l / 2
    return {
        "vin_V": vin, "l_min_H": l_min, "fsw_min_Hz": fsw, "ripple_pp_A": di,
        "phase_avg_A": i_ph, "peak_A_pathA": i_pk, "peak_A_pathB": pk_b, "peak_diff_A": i_pk - pk_b,
        "irms_A_pathA": irms_a, "irms_A_pathB": irms_b, "irms_diff_A": irms_a - irms_b,
        "isat_typ_A": v("L_ISAT_TYP"), "ilim_peak_max_A": i_lim_pk_max,
        "isat_margin_at_ilim_A": v("L_ISAT_TYP") - i_lim_pk_max,
        "iheat_typ_A": v("L_IHEAT_TYP"), "irms_margin_A": v("L_IHEAT_TYP") - irms_a,
        "ocp_avg_min_total_A": 2 * i_lim_avg_min_phase,
        "ocp_above_capacity": 2 * i_lim_avg_min_phase > v("I_BUS_CAP"),
        "slope_comp_check": slope_comp(), "t_cs_delay_note": "75 ns is TYPICAL (LM70880 p.17); peak uses typ -> conditional",
        "status": "Isat/Iheat are TYPICAL datasheet values (Vishay doc 34509); core loss AÇIK",
    }


def slope_comp():
    """LM70880 Eq.7: L_sc[uH] = VOUT*RS[mOhm]/(24*Fsw[MHz]); ratio Se/Sn(downslope)."""
    l_sc = VOUT * v("RS_NOM") * 1e3 / (24 * v("FSW_NOM") / 1e6) * 1e-6
    # Se is fixed; sensed downslope Sn = VOUT*RS*GCS/L, and Se = Sn at L = L_sc  ->  Se/Sn = L / L_sc (G3 audit E3 fix)
    return {"l_for_1x_downslope_H": l_sc, "se_over_sn": v("L_NOM") / l_sc,
            "se_over_sn_l_min": v("L_NOM") * (1 - v("L_TOL")) / l_sc}


def sense_resistor():
    i = inductor()
    p = i["irms_A_pathA"] ** 2 * v("RS_NOM") * (1 + v("RS_TOL"))
    return {"mpn": "WSL25127L500FEA", "p_W": p, "p70_W": v("RS_P70"), "derating": p / v("RS_P70"),
            "v_sense_full_load_V": i["phase_avg_A"] * v("RS_NOM"),
            "kelvin": "4-terminal not required; Kelvin escape from pad inner edges (LM70880 p.16)"}


# ------------------------------------------------------------- capacitors
def cout(n=None):
    n = n or D.N_COUT
    cmin, ctyp, cmax = (n * v(k) for k in ("COUT_C_PART_MIN", "COUT_C_PART_TYP", "COUT_C_PART_MAX"))
    esr = v("COUT_ESR_PART") / n
    vin = v("VIN_MAX")
    di = ripple(vin, v("L_NOM") * (1 - v("L_TOL")), v("FSW_MIN"))
    d = VOUT / vin
    k_cancel = (1 - 2 * d) / (1 - d) if d < 0.5 else (2 * d - 1) / d
    di_out_a = di * k_cancel
    # path B: numeric two phases 180 deg apart
    fsw = v("FSW_MIN")
    period = 1 / fsw
    n_s = 20000
    tot = [_triangle(k * period / n_s, period, d, 0, di) + _triangle(k * period / n_s + period / 2, period, d, 0, di)
           for k in range(n_s)]
    di_out_b = max(tot) - min(tot)
    dv_a = di_out_a / (8 * 2 * fsw * cmin) + esr * di_out_a
    return {"n": n, "ceff_min_F": cmin, "ceff_typ_F": ctyp, "ceff_max_F": cmax, "esr_ohm": esr,
            "ripple_current_pp_A_pathA": di_out_a, "ripple_current_pp_A_pathB": di_out_b,
            "diff_A": di_out_a - di_out_b, "ripple_voltage_pp_V": dv_a,
            "voltage_derating": VOUT / 100.0, "dc_bias": "Ceff per part from TDK model at 11 V (G1); 100 V rating -> 11 % of rating"}


def cin(n=8, c_part_nom=4.7e-6, retained=0.5):
    vin = v("VIN_MIN")
    io = v("I_BUS_CAP")
    d = VOUT / vin
    irms_a = io / 2 * math.sqrt(2 * d * (1 - 2 * d)) if d <= 0.5 else io / 2 * math.sqrt((2 * d - 1) * (2 - 2 * d))
    fsw = v("FSW_MIN")
    period = 1 / fsw
    di = ripple(vin, v("L_NOM"), fsw)
    n_s = 40000
    iin = []
    for k in range(n_s):
        t = k * period / n_s
        s = 0.0
        for ph in (0.0, period / 2):
            tt = (t + ph) % period
            if tt / period < d:
                s += _triangle(tt, period, d, io / 2, di)
        iin.append(s)
    avg = sum(iin) / n_s
    irms_b = math.sqrt(sum((x - avg) ** 2 for x in iin) / n_s)
    worst = max((io / 2 * math.sqrt(2 * dd * (1 - 2 * dd)) if dd <= 0.5 else io / 2 * math.sqrt((2 * dd - 1) * (2 - 2 * dd)))
                for dd in (VOUT / x for x in (20, 21, 22, 23, 24, 25, 26)))
    c_eff = n * c_part_nom * retained
    dv = io / 2 * d * (1 - d) / (fsw * c_eff) / 2   # 2-phase approx
    return {"irms_A_pathA": irms_a, "irms_A_pathB_incl_ripple": irms_b, "diff_A": irms_a - irms_b,
            "irms_worst_over_vin_A": worst, "per_cap_A": max(irms_a, irms_b) / n,
            "ceff_assumed_F": c_eff, "retained_fraction_VARSAYIM": retained, "ripple_V_est": dv,
            "status": "CIN MPN/DC-bias doğrulanamadı (TDK/Murata datasheet erişimi 403) -> BOM-OPEN"}


# ------------------------------------------------------------- losses / thermal
def losses():
    ind = inductor(v("VIN_NOM"))
    irms = ind["irms_A_pathA"]
    p_out = VOUT * v("I_BUS_CAP")
    p_in = p_out / ETA_ASSUMED
    i_in_min_vin = p_in / v("VIN_MIN")
    pl = {
        "inductor_dcr_2x": 2 * irms ** 2 * v("L_DCR_MAX") * (1 + CU_TC * 40),
        "inductor_core_2x_VARSAYIM": 2 * CORE_LOSS_EACH,
        "shunt_2x": 2 * irms ** 2 * v("RS_NOM"),
        "q1_reverse_fet": i_in_min_vin ** 2 * 16e-3 * 1.8,
        "q_iso": v("I_BUS_CAP") ** 2 * v("QISO_RDS_MAX_10V") * v("QISO_RDS_HOT_FACTOR"),
        "efuse_o1": 7.0 ** 2 * 3.2e-3 * 1.5,
        "efuse_s2e": 0.5 ** 2 * 3.2e-3 * 1.5,
        "ldo5": (v("VIN_MAX") - 5.0) * 0.016,
    }
    p_conv_loss = p_in - p_out
    ext_in_conv = pl["inductor_dcr_2x"] + pl["inductor_core_2x_VARSAYIM"] + pl["shunt_2x"]
    p_ic_each = max(0.0, (p_conv_loss - ext_in_conv) / 2)
    tj_ic = {"jedec_33p5": v("T_AMB_MAX") + p_ic_each * 33.5, "evm_18p6": v("T_AMB_MAX") + p_ic_each * 18.6}
    ta_max_for_125 = {"jedec": 125 - p_ic_each * 33.5, "evm": 125 - p_ic_each * 18.6}
    total_board = p_conv_loss + sum(val for k, val in pl.items() if k not in ("inductor_dcr_2x", "inductor_core_2x_VARSAYIM", "shunt_2x"))
    # path B: efficiency from summed component losses (IC loss estimated as above)
    eta_b = p_out / (p_out + 2 * p_ic_each + ext_in_conv)
    board_area_m2 = 0.1016 * 0.0762
    h_conv = 10.0   # VARSAYIM natural convection W/m2K, both sides
    dt_board = total_board / (h_conv * 2 * board_area_m2)
    return {"p_out_W": p_out, "eta_assumed": ETA_ASSUMED, "p_conv_loss_W": p_conv_loss, "parts_W": pl,
            "ic_loss_each_W": p_ic_each, "tj_ic_C": tj_ic, "ta_max_for_tj125_C": ta_max_for_125,
            "eta_pathB": eta_b, "eta_diff": ETA_ASSUMED - eta_b,
            "board_total_W": total_board, "board_dT_K_VARSAYIM": dt_board,
            "status": "LM70880 RDS(on)/switching loss not tabulated in datasheet text; IC loss derived from assumed efficiency -> VARSAYIM/AÇIK"}


# ------------------------------------------------------------- eFuse
def efuse():
    o1 = EF_ILIM_TABLE[D.RILIM_O1]
    s2 = EF_ILIM_TABLE[D.RILIM_S2E]
    sum_min = o1[0] + s2[0]
    # path B: TPS25982 typ-point inverse fit I = K/R (K from 300 ohm typ) -> nominal cross-check only
    k_fit = 4.98 * 300.0
    sum_typ_b = k_fit / D.RILIM_O1 + k_fit / D.RILIM_S2E
    imon_max_v = D.RIMON * v("EF_GIMON_MAX") * o1[2]
    ren_ratio = (D.REN_EF1 + D.REN_EF2) / D.REN_EF2
    en_on = [v("EF_UVLO_R_MIN") * ren_ratio * (1 - 0.002), v("EF_UVLO_R_MAX") * ren_ratio * (1 + 0.002) + 0.1e-6 * D.REN_EF1]
    sr = 4600.0 / (D.CDVDT * 1e12)  # V/ms, TPS25982 Eq.3
    inrush = {f"{c*1e6:g}uF": c * sr * 1e3 for c in (10e-6, 100e-6, 470e-6)}
    o1_load_env = v("I_LOAD_STEP_HI") - 0.22
    return {"rilim_o1": D.RILIM_O1, "ilim_o1_A": o1, "rilim_s2e": D.RILIM_S2E, "ilim_s2e_A": s2,
            "sum_min_A": sum_min, "sum_min_ge_7p5": sum_min >= v("I_BUS_CAP"),
            "sum_typ_A_pathA": o1[1] + s2[1], "sum_typ_A_pathB_fit": sum_typ_b,
            "sum_max_A": o1[2] + s2[2],
            "o1_margin_over_load_envelope_A": o1[0] - o1_load_env, "o1_load_envelope_VARSAYIM_A": o1_load_env,
            "s2e_margin_over_start_A": s2[0] - 1.5,
            "imon_max_V": imon_max_v, "en_on_V": en_on, "slew_V_per_ms": sr, "inrush_A": inrush,
            "fast_trip_pct": 210, "connector_check": "Micro-Fit W-W 7 A / W-B 8.5 A (G1 record); Molex PS not readable this round -> AÇIK",
            "status": "ILIM only at datasheet table points (no interpolation credit)"}


# ------------------------------------------------------------- UVLO
def uvlo(rtop=None, rbot=None):
    rtop = rtop or D.RUV1
    rbot = rbot or D.RUV2
    dT = v("DT_DRIFT")
    vals = []
    for ven, st, sb, stc, sbc, il in itertools.product((v("VEN_R_MIN"), v("VEN_R_MAX")), (-1, 1), (-1, 1), (-1, 1), (-1, 1),
                                                       (0.0, v("IEN_LEAK_MAX"))):
        rt = rtop * (1 + st * D.RUV_TOL) * (1 + stc * D.RUV_TCR * dT)
        rb = rbot * (1 + sb * D.RUV_TOL) * (1 + sbc * D.RUV_TCR * dT)
        vals.append(ven * (1 + rt / rb) + il * rt)
    lo_a, hi_a = min(vals), max(vals)
    k = 1 + rtop / rbot
    span_ratio = (rtop / rbot) * 2 * (D.RUV_TOL + D.RUV_TCR * dT)
    lo_b = v("VEN_R_MIN") * (k - span_ratio)
    hi_b = v("VEN_R_MAX") * (k + span_ratio) + v("IEN_LEAK_MAX") * rtop * (1 + D.RUV_TOL + D.RUV_TCR * dT)
    fall_typ = (1.0 - v("VEN_HYS_TYP")) * k
    return {"rtop": rtop, "rbot": rbot, "rising_pathA": [lo_a, hi_a], "rising_pathB": [lo_b, hi_b],
            "diff_V": [lo_a - lo_b, hi_a - hi_b], "restart_at_20V": hi_a <= v("VIN_MIN"),
            "per_cell_rising_V": [lo_a / 6, hi_a / 6], "falling_typ_V": fall_typ, "falling_typ_per_cell_V": fall_typ / 6,
            "falling_note": "VEN-HYS 0.1 V is typical only (LM70880 p.6) -> falling threshold range AÇIK",
            "leakage_note": "EN leakage max not published; 1 uA screen (VARSAYIM) -> 0.174 V shift included",
            "old_180k": None}


# ------------------------------------------------------------- input protection
def input_protection():
    rows = []
    for r_src in (v("R_SRC_MIN"), 0.05, 0.1, v("R_SRC_MAX")):
        i_sc = v("VIN_MAX") / (r_src + 0.005)   # +5 mOhm board/fuse/Q1 VARSAYIM
        rows.append({"r_src_ohm": r_src, "i_short_A": i_sc})
    p_in_max = VOUT * v("I_BUS_CAP") / ETA_ASSUMED
    i_in_max = p_in_max / v("VIN_MIN")
    fuse = {"i_in_max_A": i_in_max, "rated_current_min_A": i_in_max / 0.75,
            "voltage_rating_min_VDC": v("VIN_CLAMP"), "breaking_capacity_min_A": max(r["i_short_A"] for r in rows),
            "selection": "AÇIK: fuse vendor datasheets not reachable (Littelfuse 403/DNS); requirement only"}
    q1 = {"mpn": "BSC160N10NS3G", "vds_V": 100.0, "vds_margin_to_clamp_V": 100.0 - v("VIN_CLAMP"),
          "p_cond_W": i_in_max ** 2 * 16e-3 * 1.8, "lm74700_anode_abs_V": 65.0,
          "lm74700_margin_V": 65.0 - v("VIN_CLAMP"), "reverse_polarity": "LM74700 blocks; Q1 body diode reverse-biased at -26 V (VDS 100 V)",
          "soa": "hot-plug inrush flows through Q1 body diode/channel into CIN; SOA graph not extracted -> AÇIK"}
    tvs = {"family": "SMCJ33A", "vrwm_V": 33.0, "vrwm_margin_V": 33.0 - v("VIN_MAX"), "vc_V": v("VIN_CLAMP"),
           "status": "TVS datasheet not reachable this round -> doğrulanamadı; G1 values used as VARSAYIM"}
    # hot-plug: energy in CIN charged through source resistance (all dissipated in R_src + Q1 path)
    c_in = 8 * 4.7e-6 * 0.5
    e_hot = 0.5 * c_in * v("VIN_MAX") ** 2
    return {"short_current_sweep": rows, "fuse_requirement": fuse, "q1": q1, "tvs": tvs,
            "hotplug_cin_energy_J": e_hot,
            "connector": {"j1_current_A": i_in_max, "j2_current_A": 7.0, "j3_current_A": 1.5,
                          "status": "Molex PS-43045 not readable (connection reset) -> AÇIK; G1 record W-W 7 A, W-B 8.5 A (18 AWG)"}}


def compute():
    return {"classification": "HESAP with DATASHEET inputs; no measurement",
            "inductor": inductor(), "inductor_vin_nom": inductor(v("VIN_NOM")), "sense": sense_resistor(),
            "cout": cout(), "cout_old_8": cout(8), "cin": cin(), "losses": losses(), "efuse": efuse(),
            "uvlo_174k": uvlo(), "uvlo_180k_old": uvlo(180e3, 10e3), "input": input_protection()}


def main():
    res = compute()
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"irms": res["inductor"]["irms_A_pathA"], "uvlo": res["uvlo_174k"]["rising_pathA"],
                      "ilim_sum_min": res["efuse"]["sum_min_A"], "tj_ic": res["losses"]["tj_ic_C"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
