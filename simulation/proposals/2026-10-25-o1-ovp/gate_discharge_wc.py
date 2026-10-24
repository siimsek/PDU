#!/usr/bin/env python3
"""WP1 rev2 P0-3: worst-case gate-discharge (turn-off) bound for U10 TPS48000-Q1 driving 4x CSD18540Q5B.

ANALYTIC (inference, class C in BUDGET.md), stdlib only, deterministic. No vendor model is used or bundled.

Datasheet facts (guaranteed = G, typical = T):
  SLUSEZ1B (TPS4800-Q1, rev B, Mar 2026) sec 5.6 / Fig 6-1:
    tPD(INP_L) <= 1.05 us (G, TJ -40..150 C), INP falling -> V(PD)-V(SRC) < 1 V, CL = 47 nF, V(BST-SRC) = 11 V.
    I(PD) 2 A peak sink: TYP only (no min) -> not used.
    V(BST-SRC_OFF) <= 13.86 V (G): highest gate start voltage.
  SLPS488B (CSD18540Q5B) sec 5.1 (TA = 25 C):
    Qg(10 V) 41 typ / 53 max nC, Qg(4.5 V) 20 typ / 26 max nC (G for max), Qgd 6.7 nC, Qgs 8.8 nC, Qg(th) 6.3 nC (T only),
    VGS(th) 1.5 min / 2.3 max V @ 250 uA (G at 25 C), RG 0.8 typ / 1.6 max Ohm (G).

Model (assumption V1): the PD sink is no weaker than a linear resistor R_wc that just meets the 47 nF test with ZERO
internal delay: R_wc = 1.05 us / (47 nF * ln(11/1)). For any split between internal delay t_d and a resistive sink the
time to discharge a load with charge integral F = int dQ/V is t_d + (1.05us - t_d) * F/F_test, whose maximum over
t_d in [0, 1.05 us] is 1.05 us * max(1, F/F_test). (A constant-current sink gives Q/Q_test, smaller here.)
Gate-charge curve (assumption V2): piecewise from the typical Qg curve points, every segment scaled by Qg max/typ
(53/41), Qgd additionally x2 (no max given), plateau at the LOWEST threshold (hot Vth assumed 1.1 V, below the 1.5 V
25 C min), end point 1.0 V (same as the TPS48000 test). Internal RG max/4 added to R_wc.
"""
import json, math, sys
from pathlib import Path

T_PD_MAX = 1.05e-6; CL_TEST = 47e-9; V_TEST0, V_END = 11.0, 1.0
VBST_MAX = 13.86; NFET = 4
QG10_TYP, QG10_MAX = 41e-9, 53e-9; QG45_TYP = 20e-9
QGD_TYP, QGS_TYP, QGTH_TYP = 6.7e-9, 8.8e-9, 6.3e-9
VTH_TYP, VTH_HOT_ASSUMED = 1.9, 1.1
RG_MAX = 1.6
QGD_EXTRA = 2.0

def F_test():
    return CL_TEST * math.log(V_TEST0 / V_END)

def F_fet(v_plateau, qgd_factor, scale):
    """int dQ/V per FET from VBST_MAX down to V_END for the piecewise typical curve x scale."""
    c_hi = (QG10_TYP - QG45_TYP) / (10 - 4.5)                    # 3.82 nF above 4.5 V (typ curve slope)
    q_pl_end = QGS_TYP + QGD_TYP                                  # 15.5 nC at end of plateau (typ)
    c_mid = (QG45_TYP - q_pl_end) / (4.5 - 2.65)                  # 4.5 V .. plateau (2.65 V @28 A, typ curve)
    c_lo = QGTH_TYP / VTH_TYP                                     # below threshold
    f = c_hi * math.log(VBST_MAX / 4.5)
    f += c_mid * math.log(4.5 / v_plateau)
    f += QGD_TYP * qgd_factor / v_plateau
    if v_plateau > V_END:
        f += c_lo * math.log(v_plateau / V_END)
    return f * scale

def main():
    ft = F_test(); r_wc = T_PD_MAX / ft
    scale = QG10_MAX / QG10_TYP
    rows = []
    for name, vpl, qgdf in [('typ-curve x max-scale, plateau 2.65 V', 2.65, 1.0),
                            ('plateau at Vth min 25C 1.5 V', 1.5, 1.0),
                            ('plateau at assumed hot Vth 1.1 V, Qgd x2', VTH_HOT_ASSUMED, QGD_EXTRA)]:
        ff = NFET * F_fet(vpl, qgdf, scale)
        r_tot = r_wc + RG_MAX / NFET + 0.01   # + RPD10 10 mOhm
        ratio = ff * r_tot / (ft * r_wc)
        t_wc = T_PD_MAX * max(1.0, ratio)
        rows.append(dict(case=name, v_plateau=vpl, qgd_factor=qgdf, F_fet_nF=round(ff * 1e9, 3),
                         ratio_vs_test=round(ratio, 4), t_off_wc_us=round(t_wc * 1e6, 4)))
    q_total_max = NFET * (QG10_MAX + (QG10_TYP - QG45_TYP) / 5.5 * scale * (VBST_MAX - 10))
    out = dict(source='gate_discharge_wc.py (analytic, inference class C; not a simulation)',
               F_test_nF=round(ft * 1e9, 3), R_wc_ohm=round(r_wc, 4),
               Q_test_nC=round(CL_TEST * (V_TEST0 - V_END) * 1e9, 1), Q_fet_total_max_nC=round(q_total_max * 1e9, 1),
               rows=rows, t_off_wc_us=max(r['t_off_wc_us'] for r in rows),
               budget_chain_assumed_us=1.1045,
               conclusion_ok=max(r['ratio_vs_test'] for r in rows) <= 1.0)
    txt = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if len(sys.argv) > 2 and sys.argv[1] == '--json':
        Path(sys.argv[2]).write_text(txt)
    print(txt, end='')
    return 0 if out['conclusion_ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
