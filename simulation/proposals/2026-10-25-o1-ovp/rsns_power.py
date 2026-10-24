#!/usr/bin/env python3
"""WP1 rev3 P0-01: RAW sense divider (RSNS10/RSNS11) power / voltage / derating study.

Deterministic, no simulator. Writes rsns-power.json; `--check` exits 1 if the selected
option violates the acceptance rule. Sources (Panasonic ERA-A, AOA0000C307, 24-Apr-24,
read 2026-10-25 via pdftotext): power rating at 85 C ambient ERA-3A 0.1 W / 75 V LEV,
ERA-6A 0.125 W / 100 V, ERA-8A 0.25 W / 150 V; derating linear from 100 % at 85 C to 0 %
at 155 C (power derating curve, p2); RCWV = min(sqrt(P*R), LEV) (note *2); ERA-xARB
+/-0.1 %, +/-10 ppm/K, 1 k..100 k (E24/E96); performance table (endurance / damp heat
+/-0.1 % for R >= 47 ohm) is common to all sizes.

ASSUMPTIONS (strictest safe, labelled):
  A-TA : board ambient around the divider up to 125 C (same span as the budget's R_dT =
         100 K; the PDU ambient is NOT specified anywhere in the repo).
  A-RAW: sustained RAW = 26 V (VIN max, buck high-side short with OVP FETs off).
  A-CLP: TLV3601 IN- clamps to VCC + 0.2..0.7 V with VCC = 4.9..5.1 V (TPS7A1650 +/-2 %);
         window_budget.py uses VCCmin + 0.2 = 5.1 V. A 'no clamp' row is kept as an upper
         bound for RSNS11; a 0.6 V clamp row (comparator unpowered = double fault) is info.
"""
import json, math, sys, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
VRAW = 26.0
RIN = 1000.0
RT, RB = 2050.0, 1150.0
SPLIT = (1000.0, 1050.0)           # E24 1.0k + E96 1.05k = 2050 ohm exactly
TA_ACCEPT = 125.0
FAM = {'0603': ('ERA-3A', 0.100, 75.0), '0805': ('ERA-6A', 0.125, 100.0), '1206': ('ERA-8A', 0.250, 150.0)}
CLAMPS = {'no_clamp_upper_bound_RSNS11': None, 'clamp_5V1_VCCmin+0.2': 5.1,
          'clamp_5V8_VCCmax+0.7': 5.8, 'INFO_double_fault_unpowered_0V6': 0.6}

def derate(p85, ta):
    return p85 if ta <= 85 else max(0.0, p85*(155.0-ta)/70.0)

def node(vclamp):
    """returns (V_SNS, I_top, I_RIN)"""
    if vclamp is None:
        vs = VRAW*RB/(RT+RB); return vs, VRAW/(RT+RB), 0.0
    vs = (VRAW/RT + vclamp/RIN)/(1/RT + 1/RB + 1/RIN)
    if vs <= vclamp:   # clamp not conducting
        vs = VRAW*RB/(RT+RB); return vs, VRAW/(RT+RB), 0.0
    return vs, (VRAW-vs)/RT, (vs-vclamp)/RIN

def option(name, size, parts):
    fam, p85, lev = FAM[size]
    rows = {}
    for cn, vc in CLAMPS.items():
        vs, it, irin = node(vc)
        per = []
        for r in parts:
            p = it*it*r; v = it*r; rcwv = min(math.sqrt(p85*r), lev)
            per.append(dict(R=r, P_W=p, V_V=v, RCWV_V=rcwv, V_ok=v <= rcwv,
                            pct_of_85C=100*p/p85, pct_of_derated={str(t): (100*p/derate(p85, t) if derate(p85, t) else None) for t in (85, 105, 125)}))
        rows[cn] = dict(V_SNS=vs, I_top_A=it, I_RIN_A=irin, P_RIN_W=irin*irin*RIN, P_RSNS11_W=vs*vs/RB, parts=per)
    design = [c for c in CLAMPS if not c.startswith('INFO')]
    worst = max(p['P_W'] for c in design for p in rows[c]['parts'])
    ok = all(p['P_W'] <= derate(p85, TA_ACCEPT) and p['V_ok'] for c in design for p in rows[c]['parts'])
    return dict(option=name, size=size, family=fam, P85_W=p85, LEV_V=lev, parts_ohm=list(parts),
                P_allowed_125C_W=derate(p85, TA_ACCEPT), worst_part_P_W=worst,
                worst_pct_of_derated_125C=100*worst/derate(p85, TA_ACCEPT), worst_pct_of_85C=100*worst/p85,
                meets_rule_125C=ok, cases=rows)

def bottom(size):
    fam, p85, lev = FAM[size]
    pw = {c: node(v)[0]**2/RB for c, v in CLAMPS.items()}
    design = max(v for c, v in pw.items() if not c.startswith('INFO'))
    return dict(size=size, family=fam, P_W=pw, worst_design_P_W=design, P_allowed_125C_W=derate(p85, TA_ACCEPT),
                pct_of_derated_125C=100*design/derate(p85, TA_ACCEPT), meets_rule_125C=design <= derate(p85, TA_ACCEPT))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    top = [option('1x0603 ERA-3ARB2051V (rev2)', '0603', (RT,)), option('1x0805 ERA-6ARB2051V', '0805', (RT,)),
           option('1x1206 ERA-8ARB2051V', '1206', (RT,)), option('2x0603 1.0k+1.05k', '0603', SPLIT),
           option('2x0805 1.0k+1.05k', '0805', SPLIT), option('2x1206 1.0k+1.05k (SELECTED)', '1206', SPLIT)]
    bot = [bottom(s) for s in ('0603', '0805', '1206')]
    sel_top = top[-1]; sel_bot = bot[-1]
    out = dict(_note=__doc__.strip().splitlines()[0], VRAW=VRAW, RT=RT, RB=RB, RIN=RIN, split=SPLIT,
               ratio_k=RB/(RT+RB), ratio_k_split=RB/(sum(SPLIT)+RB), TA_accept_C=TA_ACCEPT,
               rule='every part: P <= derated rating at TA=125 C and V <= RCWV, for all design clamp cases (A-TA, A-RAW, A-CLP)',
               trip_budget_effect=('series split with the SAME per-part spec (+/-0.1 %, +/-10 ppm/K, life +/-0.1 %): worst-case '
                                   'Rt deviation = per-part deviation, so window_budget dr is unchanged; nominal k unchanged '
                                   '(1000+1050 = 2050). SPICE corners scale both parts together (correlated = worst case).'),
               top_options=top, bottom_options=bot,
               selected=dict(RSNS10A='ERA-8ARB102V (1.0 k, 1206)', RSNS10B='ERA-8ARB1051V (1.05 k, 1206)',
                             RSNS11='ERA-8ARB1151V (1.15 k, 1206)', top_ok=sel_top['meets_rule_125C'], bottom_ok=sel_bot['meets_rule_125C'],
                             mpn_note='MPN coding per AOA0000C307 (E24 value 1.0 k uses 3-digit code); stock/availability NOT verified'))
    (HERE/'rsns-power.json').write_text(json.dumps(out, indent=1) + '\n')
    for o in top:
        print(f"{o['option']:32s} worst part {o['worst_part_P_W']*1e3:6.1f} mW  allowed@125C {o['P_allowed_125C_W']*1e3:6.1f} mW "
              f"({o['worst_pct_of_derated_125C']:5.1f} %)  @85C {o['worst_pct_of_85C']:5.1f} %  -> {'OK' if o['meets_rule_125C'] else 'FAIL'}")
    for b in bot:
        print(f"RSNS11 {b['size']} worst {b['worst_design_P_W']*1e3:6.1f} mW allowed@125C {b['P_allowed_125C_W']*1e3:6.1f} -> {'OK' if b['meets_rule_125C'] else 'FAIL'}")
    if a.check and not (sel_top['meets_rule_125C'] and sel_bot['meets_rule_125C']):
        print('rsns_power: selected option violates rule'); return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
