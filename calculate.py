#!/usr/bin/env python3
"""IDA PDU first-order calculations.

Datasheet equations are labeled. Ceff = 88 uF is an assumption (50% of
8 x 22 uF). The candidate GCM32EC71E226KE36 is 22 uF, 25 V, X7S; its
public datasheet has no numeric DC-bias point, and no SimSurfing value
at 11 V was obtained on 2026-10-18, so RCOMP/CCOMP/CHF stay at the
88 uF result. Dual-phase RCOMP uses RS/2 because both phases share one
COMP pin. Nothing here is a bench measurement or an LM70880 loop-gain result.
"""
from math import pi, sqrt

VOUT = 11.0
VREF = 0.8
LOAD_A = 7.5
PHASES = 2
L_H = 6.8e-6
L_TOL = 0.20
FS_MIN = 400e3
FS_TYP = 440e3
RS = 7.5e-3
RS_TOL = 0.01
VCS_MIN = 50e-3
VCS_MAX = 62e-3
TDELAY = 75e-9
GCS = 10.0
GM = 1200e-6
CBW = 38e-12
FC = 40e3
CEFF = 88e-6
RCOMP = 9.53e3
CCOMP = 4.7e-9
CHF = 47e-12
VINS = (20.0, 22.2, 25.2, 26.0)


def rrt_khz(r_kohm):
    return 1e6 / (r_kohm * 45.0 + 53.0)


print("feedback_V", round(VREF * (1 + 130 / 10.2), 4))
print("rt_49k9_equation_kHz", round(rrt_khz(49.9), 2))
print("rt_table_min_typ_max_kHz", "400/440/480")

print("vin_V,duty,iin90_A,iin95_A,dil_400k_A,peak_400k_A,peak_Ltol_A,dil_440k_A")
for vin in VINS:
    duty = VOUT / vin
    pout = VOUT * LOAD_A
    i_phase = LOAD_A / PHASES
    dil400 = VOUT * (1 - duty) / (L_H * FS_MIN)
    dil440 = VOUT * (1 - duty) / (L_H * FS_TYP)
    peak = i_phase + dil400 / 2
    peak_tol = i_phase + (dil400 / (1 - L_TOL)) / 2
    print(
        f"{vin:.1f},{duty:.4f},{pout/(vin*0.90):.3f},{pout/(vin*0.95):.3f},"
        f"{dil400:.3f},{peak:.3f},{peak_tol:.3f},{dil440:.3f}"
    )

ocp_min = VCS_MIN / (RS * (1 + RS_TOL))
di_delay = VOUT * TDELAY / (L_H * (1 - L_TOL))
print("ocp_min_threshold_A", round(ocp_min, 3))
print("delay_add_at_11V_Ltol_A", round(di_delay, 3))
print("ocp_plus_delay_A", round(ocp_min + di_delay, 3))

rs_eff = RS / PHASES
rcomp_exact = 2 * pi * FC * (VOUT / VREF) * (rs_eff * GCS / GM) * CEFF
ccomp_exact = 10 / (2 * pi * FC * RCOMP)
fz = 1 / (2 * pi * RCOMP * CCOMP)
fp_load = 1 / (2 * pi * (VOUT / LOAD_A) * CEFF)
f_hf = 1 / (2 * pi * RCOMP * CHF)
print("rcomp_exact_ohm", round(rcomp_exact, 1))
print("ccomp_for_fc_over_10_nF", round(ccomp_exact * 1e9, 3))
print("zero_with_4n7_Hz", round(fz, 1))
print("load_pole_7p5A_Hz", round(fp_load, 1))
print("chf_pole_Hz", round(f_hf, 1))

ratio_uv = (180e3 + 10e3) / 10e3
print("buck_uvlo_typ_on_V", round(1.00 * ratio_uv, 3))
print("buck_uvlo_max_threshold_on_V", round(1.05 * ratio_uv, 3))
print("buck_uvlo_min_threshold_on_V", round(0.95 * ratio_uv, 3))
print("buck_uvlo_typ_off_V", round(0.90 * ratio_uv, 3))

efuse_div = (64.9e3 + 10e3) / 10e3
print("efuse_en_typ_on_V", round(1.20 * efuse_div, 3))
print("efuse_en_max_threshold_on_V", round(1.23 * efuse_div, 3))
print("efuse_en_at_11V_V", round(11 * 10 / 74.9, 3))
print("pg_high_at_11V_V", round(11 * 18 / 118, 3))
print("pg_high_at_26V_V", round(26 * 18 / 118, 3))
print("pg_high_at_30V_1pct_worst_V", round(30 * 18.18 / (99 + 18.18), 3))
print("bootstrap_series_ohm_per_phase", 1.0)
print("lm74700_input_bypass_nF", 22.0)

for name, rlim, rimon in (("O1", 301, 2610), ("S2E", 604, 4990)):
    ilim = 1460 / rlim + 0.11
    vmon = 246e-6 * ilim * rimon
    vmon_maxg = 253.4e-6 * ilim * rimon
    print(name, "ilim_A", round(ilim, 3), "vimon_typ_V", round(vmon, 3), "vimon_maxgain_V", round(vmon_maxg, 3))

print("dvdt_1nF_V_per_ms", round(4600 / 1000, 3))
print("dvdt_rise_11V_ms", round(11 / 4.6, 3))
print("inrush_mA_per_uF", 4.6)
i_in = (VOUT * LOAD_A) / (20 * 0.90)
print("q1_loss_at_20V_90pct_W", round(i_in ** 2 * 16e-3, 3))
print("inductor_dcr_loss_per_phase_W", round((LOAD_A / PHASES) ** 2 * 23.3e-3, 3))
print("planning_envelope_A", round((12 * 5 + 12 * 1.5) / VOUT, 3))
