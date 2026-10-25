#!/usr/bin/env python3
"""WP2 2026-10-25-uvlo: analytic UVLO window / restart / sequencing budget (worst-case vertex enumeration).

All parameter sources are tagged:  G = datasheet guaranteed (min/max), T = datasheet typical,
A = assumption (marked, strictest safe reading), I = inference (derived from G/T values by stated reasoning).
Output: results/uvlo-budget.json.  Exit 0 = chosen design passes every analytic criterion, 1 = a criterion fails.
"""
import itertools, json, math, sys

E96 = [1.00,1.02,1.05,1.07,1.10,1.13,1.15,1.18,1.21,1.24,1.27,1.30,1.33,1.37,1.40,1.43,1.47,1.50,1.54,1.58,1.62,1.65,
       1.69,1.74,1.78,1.82,1.87,1.91,1.96,2.00,2.05,2.10,2.15,2.21,2.26,2.32,2.37,2.43,2.49,2.55,2.61,2.67,2.74,2.80,
       2.87,2.94,3.01,3.09,3.16,3.24,3.32,3.40,3.48,3.57,3.65,3.74,3.83,3.92,4.02,4.12,4.22,4.32,4.42,4.53,4.64,4.75,
       4.87,4.99,5.11,5.23,5.36,5.49,5.62,5.76,5.90,6.04,6.19,6.34,6.49,6.65,6.81,6.98,7.15,7.32,7.50,7.68,7.87,8.06,
       8.25,8.45,8.66,8.87,9.09,9.31,9.53,9.76]

# ---------------- requirements (REQUIREMENTS.md) ----------------
REQ = dict(
    E_START=20.0,          # A: battery EMF (open-circuit) at which start AND sustained run must be guaranteed (strictest reading of "20 V input")
    V_FALL_MIN=18.0,       # A: board-level VIN shutdown must stay >= 3.00 V/cell under load (over-discharge floor)
    P_OUT=82.5,            # power-stage target 7.5 A x 11 V (brief)
    ETA=0.88,              # A: buck efficiency floor at 18-20 V, 82.5 W (no TI-guaranteed value; LM70880 has only typical curves)
    P_HK=0.30,             # A: housekeeping input power (LDO bleed 10 mA + controllers + comparators)
    R_TOTAL_MAX=0.25,      # A: battery (ohmic+polarisation) + harness + connectors + F1 + Q1(hot) + PCB, see R_BREAKDOWN
    I_Q_PRESTART=0.015,    # A: input current before the buck starts (LDO bleed 10 mA + TPS48000 + LM74700 + REF/comparators)
    MARGIN_DYN=0.10,       # A: dynamic margin (ripple, load steps, inrush) required on every hysteresis/operating comparison
    T_SEQ_MIN=0.060,       # I: buck EN delay must exceed TPS48000 worst TDRV_EN 50.8 ms (WP1 window-budget) + ~18 % margin
    T_SEQ_MAX=0.300,       # A: start latency acceptable to the user (not a safety limit; reported)
)
R_BREAKDOWN = {  # ohm; every entry is an assumption unless noted
    'lipo_6s_ohmic_new_to_aged (6 x 16.7 mOhm)': 0.100,
    'lipo_polarisation R1 (tau ~10 s, 6 x 8.3 mOhm)': 0.050,
    'battery lead + harness 2 x 0.3 m 12 AWG': 0.020,
    'battery-side connector (XT60 class)': 0.002,
    'J1 Micro-Fit (+ and - path, 2 x 10 mOhm max per path, A)': 0.020,
    'F1 10 A fuse cold resistance (A, <=10 mOhm; model R_F1)': 0.010,
    'Q1 LM74700 FET at Tj hot (A, 30 mOhm vs 16 mOhm model)': 0.030,
    'PCB copper VBAT->VIN': 0.005,
}
assert abs(sum(R_BREAKDOWN.values()) - 0.237) < 1e-9 and sum(R_BREAKDOWN.values()) <= REQ['R_TOTAL_MAX']

# ---------------- component data (datasheet tags) ----------------
DS = dict(
    LM70880_VEN_TH=(0.95, 1.05, 'G SNVSBX7A p6 VEN-TH rising 0.95/1.0/1.05 V'),
    LM70880_VEN_HYS_TYP=(0.10, 'T SNVSBX7A p6 (no min/max -> falling threshold NOT guaranteed)'),
    LM70880_EN_LOW_LOGIC=(0.40, 'T/descr SNVSBX7A p13 section 7.3.3: <0.4 V disables (description, not EC table)'),
    LM70880_IEN=(1e-6, 'A: EN/UVLO input current not specified in SNVSBX7A; +/-1 uA assumed'),
    TLV3202_VIO=(0.004, 'G SBOS561C p5 VIO max -40..125 C, VCC=5 V, VCM=VCC/2'),
    TLV3202_CMRR_DB=(60, 'G SBOS561C p5 CMRR min'),
    TLV3202_PSRR_DB=(65, 'G SBOS561C p5 PSRR min'),
    TLV3202_HINT=(0.0, 0.005, 'T SBOS561C p5 1.2 mV typ; A: 0..5 mV range'),
    TLV3202_IIB=(5e-9, 'G SBOS561C p5 over temperature'),
    TLV3202_VOH_DROP=(0.0, 0.170, 'G SBOS561C p5 VCC-VOH <=170 mV @4 mA over T (our load <=1 mA: conservative)'),
    TLV3202_VOL=(0.0, 0.225, 'G SBOS561C p5 VOL <=225 mV @4 mA over T'),
    TPS7A1650_V5=(4.90, 5.10, 'G SBVS171F p6 overall accuracy +/-2 %'),
    REF35409=(4.096, 'G SNAS809C p5'),
    D_LEAK=(30e-6, 'G DS30097 Rev.27 (Diodes 1N4148WSQ) IRM 30 uA @VR=25 V, TJ=150 C; I: bound for VR<=5.1 V, TJ<=125 C'),
    D_VF_RESID=(0.85, 'I: 1N4148WS VFM 0.715 V max @1 mA, 25 C (DS30097) + ~0.13 V at -40 C (A)'),
)
# REF35 total error (fraction) - each term from SNAS809C p5 unless marked
REF_TERMS = {
    'initial +/-0.05 % (G)': 0.0005,
    'TC 12 ppm/K box over -40..105 C = 145 K (G, box -> +/- full band)': 12e-6 * 145,
    'TC extrapolated 105->125 C, 20 K x 12 ppm (I, outside spec range)': 12e-6 * 20,
    'long-term 40 ppm/1000 h @35 C, x10 linear for 10 kh (A)': 400e-6,
    'thermal hysteresis 70 ppm (T cycle 1, used as bound - A)': 70e-6,
    'line regulation 120 ppm/V x 0.1 V (G)': 120e-6 * 0.1,
    'solder shift: not specified (A: 0, bench B-U07)': 0.0,
}
E_REF = sum(REF_TERMS.values())
# ERA-3ARB (Panasonic AOA0000C307) fractional error per part, linear sum (strict)
RES_TERMS = {
    'tolerance +/-0.1 % (G)': 0.001,
    'TCR +/-10 ppm/K x 100 K (25->125 C) (G)': 10e-6 * 100,
    'endurance 85 C 1000 h +/-0.1 % (G, test limit)': 0.001,
    'resistance to soldering heat +/-0.1 % (G, test limit)': 0.001,
}
E_RES = sum(RES_TERMS.values())
E_RES_1PCT = 0.01 + 100e-6 * 100 + 0.01  # A: generic 1 % thick film 100 ppm/K (baseline RUV1/RUV2 have no MPN in BOM)
E_RHB = E_RES_1PCT  # RHB 1 M is outside the ERA-3ARB 1k..100k range -> generic 1 % / 100 ppm/K thick film, strict 3 %

VIO_TOT = DS['TLV3202_VIO'][0] + (4.096 - 2.5) * 10 ** (-DS['TLV3202_CMRR_DB'][0] / 20) + 0.1 * 10 ** (-DS['TLV3202_PSRR_DB'][0] / 20)


def vin_operating(E, R, P):
    d = E * E - 4 * P * R
    return None if d < 0 else (E + math.sqrt(d)) / 2


P_IN = REQ['P_OUT'] / REQ['ETA'] + REQ['P_HK']


# ---------------- option C: TLV3202 A (VIN) ----------------
def option_c_vertices(Rt, Rb, Rh, e_res=E_RES, e_ref=E_REF, vio=VIO_TOT):
    out = []
    axes = [(-1, 1)] * 9
    for s in itertools.product(*axes):
        rt = Rt * (1 + s[0] * e_res); rb = Rb * (1 + s[1] * e_res); rh = Rh * (1 + s[2] * e_res)
        vref = 4.096 * (1 + s[3] * e_ref); vio_ = s[4] * vio
        hint = DS['TLV3202_HINT'][1] if s[5] > 0 else DS['TLV3202_HINT'][0]
        v5 = DS['TPS7A1650_V5'][1] if s[6] > 0 else DS['TPS7A1650_V5'][0]
        voh = v5 - (DS['TLV3202_VOH_DROP'][1] if s[7] > 0 else 0.0)
        vol = DS['TLV3202_VOL'][1] if s[8] > 0 else 0.0
        for iib in (-DS['TLV3202_IIB'][0], DS['TLV3202_IIB'][0]):
            G = 1 / rt + 1 / rb + 1 / rh
            vr = rt * ((vref + vio_ + hint / 2) * G - vol / rh + iib)
            vf = rt * ((vref + vio_ - hint / 2) * G - voh / rh + iib)
            out.append((vr, vf))
    return out


def eval_c(Rt, Rb, Rh, **kw):
    V = option_c_vertices(Rt, Rb, Rh, **kw)
    R = REQ['R_TOTAL_MAX']
    vr_max = max(v[0] for v in V); vr_min = min(v[0] for v in V)
    vf_max = max(v[1] for v in V); vf_min = min(v[1] for v in V)
    h_min = min(v[0] - v[1] for v in V)
    # per-vertex (same board, same temperature) motorboating margin: after shutdown at VIN=Vf the EMF is Vf + I*R
    mb = min((v[0] - v[1]) - (P_IN / v[1]) * R for v in V)
    vin_op = vin_operating(REQ['E_START'], R, P_IN)
    m = dict(
        a_start_margin=REQ['E_START'] - REQ['I_Q_PRESTART'] * R - vr_max,
        b_overdischarge_margin=vf_min - REQ['V_FALL_MIN'],
        c_motorboat_margin=mb - REQ['MARGIN_DYN'],
        d_run_at_20V_margin=vin_op - vf_max - REQ['MARGIN_DYN'],
    )
    return dict(Rt=Rt, Rb=Rb, Rh=Rh, vr_min=vr_min, vr_max=vr_max, vf_min=vf_min, vf_max=vf_max, h_min=h_min,
                h_max=max(v[0] - v[1] for v in V), vin_op_20V=vin_op, cross_corner_rmin_minus_fmax=vr_min - vf_max,
                margins=m, ok=all(x >= 0 for x in m.values()), worst=min(m.values()))


def search_c2(max_eval=1500):
    """C2 = push-pull positive-feedback hysteresis (Rh from OUTA). E96, ERA-3ARB range 1 k..100 k."""
    dec = lambda lo, hi: [m * d for d in (1e3, 1e4, 1e5) for m in E96 if lo <= m * d <= hi]
    cands = []
    for rb in dec(4.99e3, 30e3):
        for rt in dec(10e3, 100e3):
            for rh in dec(10e3, 100e3):
                G = 1 / rt + 1 / rb + 1 / rh
                vf = rt * (4.096 * G - 4.9 / rh); h = rt * 4.8 / rh
                if 18.0 < vf < 18.5 and 1.38 < h < 1.55:
                    cands.append((abs(vf - 18.2) + abs(h - 1.46), rt, rb, rh))
    cands.sort(); best = None
    for _, rt, rb, rh in cands[:max_eval]:
        r = eval_c(rt, rb, rh)
        if best is None or r['worst'] > best['worst']:
            best = r
    return best, len(cands)


# ---------------- option C3 (CHOSEN): TLV3202 A + TMUX1102 switched-divider hysteresis ----------------
# IN+A = S (Rt from VIN, Rb to GND, Rx + TMUX1102 to GND while OUTA LOW), IN-A = VREF*m (RR1 VREF->IN-, RR2 IN-->GND).
# Thresholds depend only on VREF, resistor ratios, VIO, Hint, bias/leakage currents and TMUX RON - not on VOH/VOL/V5.
RR1_NOM, RR2_NOM = 10.0e3, 40.2e3
DS.update(
    TMUX1102_RON=(0.0, 4.9, 'G SCDS410D p5 RON max -40..125 C, VDD 5 V +/-10 %'),
    TMUX1102_ILEAK=(2e-9, 'G SCDS410D p5 ID(ON)/IS(ON) +/-2 nA (OFF +/-0.9 nA) -40..125 C'),
    TMUX1102_VIH_VIL=((1.49, 0.87), 'G SCDS410D p5 VIH min 1.49 V, VIL max 0.87 V (VDD 5 V)'),
    REF35_LOADREG=(20e-6, 'T SNAS809C p1 20 ppm/mA (used as bound, A)'),
)
def vio_c3(RR1, RR2):
    """VIO max + CMRR term at the actual common-mode REFD = 4.096*RR2/(RR1+RR2) + PSRR term (0.1 V supply shift)."""
    return DS['TLV3202_VIO'][0] + abs(4.096 * RR2 / (RR1 + RR2) - 2.5) * 10 ** (-DS['TLV3202_CMRR_DB'][0] / 20) + 0.1 * 10 ** (-DS['TLV3202_PSRR_DB'][0] / 20)


# fixed 2026-10-25: the CMRR term was computed at RR2_NOM 40.2k instead of the chosen 46.4k (0.09 mV too optimistic)
VIO_C3 = vio_c3(10.0e3, 46.4e3)


def c3_vertices(Rt, Rb, Rx, RR1=RR1_NOM, RR2=RR2_NOM, e_res=E_RES, e_ref=E_REF, vio=None, detail=False):
    vio = vio_c3(RR1, RR2) if vio is None else vio
    out = []
    iib = DS['TLV3202_IIB'][0]; ilk = DS['TMUX1102_ILEAK'][0]
    for s in itertools.product((-1, 1), repeat=10):
        rt = Rt * (1 + s[0] * e_res); rb = Rb * (1 + s[1] * e_res); rx = Rx * (1 + s[2] * e_res)
        rr1 = RR1 * (1 + s[3] * e_res); rr2 = RR2 * (1 + s[4] * e_res)
        vref = 4.096 * (1 + s[5] * (e_ref + DS['REF35_LOADREG'][0] * 4.096 / (RR1 + RR2) * 1e3))
        vio_ = s[6] * vio
        hint = DS['TLV3202_HINT'][1] if s[7] > 0 else 0.0
        icur = s[8] * (iib + ilk)                      # current leaving node S (IIB + switch leakage), sign enumerated
        ron = DS['TMUX1102_RON'][1] if s[9] > 0 else 0.0
        vm = vref * rr2 / (rr1 + rr2) + s[8] * iib * (rr1 * rr2 / (rr1 + rr2))   # IN- incl. its own bias current
        # rising: OUTA low, switch ON -> Rx+RON in parallel with Rb
        th_r = vm + vio_ + hint / 2
        vr = rt * (th_r * (1 / rt + 1 / rb + 1 / (rx + ron)) + icur)
        th_f = vm + vio_ - hint / 2
        vf = rt * (th_f * (1 / rt + 1 / rb) + icur)
        if detail:
            out.append(dict(vr=vr, vf=vf, RTU=rt, RBU=rb, RXU=rx, RR1U=rr1, RR2U=rr2, VREF_P=vref, VIOA=vio_, HINTA=hint,
                            IS_U=icur, IM_U=s[8] * iib, RON_U=max(ron, 1e-3)))
        else:
            out.append((vr, vf))
    return out


def c3_spice_corners(ch):
    """Budget vertices handed to gen_uvlo.py (the SPICE corners are the analytic extreme vertices, not invented)."""
    V = c3_vertices(ch['Rt'], ch['Rb'], ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'], detail=True)
    R = REQ['R_TOTAL_MAX']
    pick = dict(vrmax=max(V, key=lambda v: v['vr']), vfmin=min(V, key=lambda v: v['vf']), vfmax=max(V, key=lambda v: v['vf']),
                mbmin=min(V, key=lambda v: (v['vr'] - v['vf']) - (P_IN / v['vf']) * R))
    typ = dict(vr=None, vf=None, RTU=ch['Rt'], RBU=ch['Rb'], RXU=ch['Rx'], RR1U=ch['RR1'], RR2U=ch['RR2'], VREF_P=4.096,
               VIOA=0.0, HINTA=1.2e-3,   # Hint typ 1.2 mV (SBOS561C p5)
               IS_U=0.0, IM_U=0.0, RON_U=1.8)
    vm = 4.096 * ch['RR2'] / (ch['RR1'] + ch['RR2'])
    typ['vr'] = ch['Rt'] * ((vm + 0.6e-3) * (1 / ch['Rt'] + 1 / ch['Rb'] + 1 / (ch['Rx'] + 1.8)))
    typ['vf'] = ch['Rt'] * ((vm - 0.6e-3) * (1 / ch['Rt'] + 1 / ch['Rb']))
    pick['typ'] = typ
    return pick


def timer_spice_corners(T):
    """Fastest / slowest cold-start timer vertices (parameters for SPICE)."""
    out = {}
    for name, key in (('tmin', min), ('tmax', max)):
        best = None
        for s in itertools.product((-1, 1), repeat=10):
            rt = T['RT'] * (1 + s[0] * E_RES); rhb = T['RHB'] * (1 + s[1] * E_RHB)
            rk1 = T['RK1'] * (1 + s[2] * E_RES); rk2 = T['RK2'] * (1 + s[3] * E_RES)
            ct = T['CT'] * (1.10 * 1.15 if s[4] > 0 else 0.90 * 0.85 * 0.70 * 0.95)
            v5 = DS['TPS7A1650_V5'][1] if s[5] > 0 else DS['TPS7A1650_V5'][0]
            vohd = DS['TLV3202_VOH_DROP'][1] if s[6] > 0 else 0.0
            leak = DS['D_LEAK'][0] if s[7] > 0 else 0.0
            vio = s[8] * VIO_TOT; hint = DS['TLV3202_HINT'][1] if s[9] > 0 else 0.0
            rth = 1 / (1 / rt + 1 / rhb); vinf = ((v5 - vohd) / rt + leak) * rth
            vth = rk2 / (rk1 + rk2) * v5 + vio + hint / 2
            t = rth * ct * math.log(vinf / (vinf - vth)) if vinf - vth > 0.05 else float('inf')
            d = dict(t=t, RTT=rt, RHB=rhb, RK1=rk1, RK2=rk2, CTT=ct, V5_P=v5, VOHD=vohd, ILKD=leak, VIOB=vio, HINTB=hint)
            if best is None or key(t, best['t']) == t and t != best['t']:
                best = d
        out[name] = best
    return out


def eval_c3(Rt, Rb, Rx, **kw):
    V = c3_vertices(Rt, Rb, Rx, **kw)
    RR1 = kw.get('RR1', RR1_NOM); RR2 = kw.get('RR2', RR2_NOM)
    R = REQ['R_TOTAL_MAX']
    vr_max = max(v[0] for v in V); vf_min = min(v[1] for v in V); vf_max = max(v[1] for v in V)
    mb = min((v[0] - v[1]) - (P_IN / v[1]) * R for v in V)
    vin_op = vin_operating(REQ['E_START'], R, P_IN)
    s26 = 26.0 * Rb * (1 + E_RES) / (Rt * (1 - E_RES) + Rb * (1 + E_RES))
    m = dict(a_start_margin=REQ['E_START'] - REQ['I_Q_PRESTART'] * R - vr_max,
             b_overdischarge_margin=vf_min - REQ['V_FALL_MIN'],
             c_motorboat_margin=mb - REQ['MARGIN_DYN'],
             d_run_at_20V_margin=vin_op - vf_max - REQ['MARGIN_DYN'],
             e_sense_26V_cm_margin=(DS['TPS7A1650_V5'][0]) - s26)   # S must stay <= VCC_min (comparator VCM, TMUX VS<=VDD)
    return dict(Rt=Rt, Rb=Rb, Rx=Rx, RR1=kw.get('RR1', RR1_NOM), RR2=kw.get('RR2', RR2_NOM),
                vr_min=min(v[0] for v in V), vr_max=vr_max, vf_min=vf_min, vf_max=vf_max,
                h_min=min(v[0] - v[1] for v in V), h_max=max(v[0] - v[1] for v in V), vin_op_20V=vin_op,
                s_at_26V_max=s26, cross_corner_rmin_minus_fmax=min(v[0] for v in V) - vf_max,
                margins=m, ok=all(x >= 0 for x in m.values()), worst=min(m.values()))


def search_c3(max_eval=4000):
    """E96, every precision resistor inside the ERA-3ARB range 1 k..100 k (AOA0000C307 p2 ratings table)."""
    dec = lambda lo, hi: [m * d for d in (1e3, 1e4, 1e5) for m in E96 if lo <= m * d <= hi]
    cands = []
    for rr2 in dec(20e3, 100e3):
        for rr1 in (10.0e3,):
            vm = 4.096 * rr2 / (rr1 + rr2)
            if not (0.70 < rr2 / (rr1 + rr2) < 0.86):
                continue
            for rb in dec(4.99e3, 30e3):
                for rt in dec(10e3, 100e3):
                    vf = vm * (1 + rt / rb)
                    if not (18.05 < vf < 18.40):
                        continue
                    for rx in dec(10e3, 100e3):
                        h = vm * rt / rx
                        if 1.42 < h < 1.52:
                            # nominal score: centre of the feasible window (V_f ~ 18.2, H ~ 1.46)
                            cands.append((abs(vf - 18.20) + abs(h - 1.46), rt, rb, rx, rr2))
    cands.sort()
    best = None
    for _, rt, rb, rx, rr2 in cands[:max_eval]:
        r = eval_c3(rt, rb, rx, RR2=rr2)
        if best is None or r['worst'] > best['worst']:
            best = r
    return best, len(cands)

# ---------------- timer (TLV3202 B) + EN drive ----------------
def timer_vertices(RT, CT, RHB, RK1, RK2, RD, RUV2, v0_list=(0.0,)):
    res = []
    for s in itertools.product((-1, 1), repeat=10):
        rt = RT * (1 + s[0] * E_RES); rhb = RHB * (1 + s[1] * E_RHB)
        rk1 = RK1 * (1 + s[2] * E_RES); rk2 = RK2 * (1 + s[3] * E_RES)
        # CT: X7R 10 uF 25 V 1206: tol +/-10 % (G, MPN), X7R +/-15 % over -55..125 C (G, EIA class), DC bias at 5 V 0..-30 % (A), aging -5 % (A)
        ct = CT * (1.10 * 1.15 if s[4] > 0 else 0.90 * 0.85 * 0.70 * 0.95)
        v5 = DS['TPS7A1650_V5'][1] if s[5] > 0 else DS['TPS7A1650_V5'][0]
        voha = v5 - (DS['TLV3202_VOH_DROP'][1] if s[6] > 0 else 0.0)
        leak = DS['D_LEAK'][0] if s[7] > 0 else 0.0
        vio = s[8] * VIO_TOT
        hint = DS['TLV3202_HINT'][1] if s[9] > 0 else 0.0
        rth = 1 / (1 / rt + 1 / rhb)
        vinf = (voha / rt + 0.0 / rhb + leak) * rth          # OUTB low (VOL>=0 only raises vinf; 0 is the slow case)
        kb = rk2 / (rk1 + rk2)
        vth = kb * v5 + vio + hint / 2
        tau = rth * ct
        for v0 in v0_list:
            if vinf - vth <= 0.05:
                res.append(dict(t=float('inf'), vinf=vinf, vth=vth))
            else:
                res.append(dict(t=tau * math.log((vinf - v0) / (vinf - vth)), vinf=vinf, vth=vth, v0=v0))
    return res


def eval_timer(RT, CT, RHB=1e6, RK1=10e3, RK2=40.2e3, RD=10e3, RUV2=10e3):
    cold = timer_vertices(RT, CT, RHB, RK1, RK2, RD, RUV2, (0.0,))
    dip = timer_vertices(RT, CT, RHB, RK1, RK2, RD, RUV2, (DS['D_VF_RESID'][0] + DS['TLV3202_VOL'][1],))
    tmin = min(x['t'] for x in cold); tmax = max(x['t'] for x in cold)
    headroom = min(x['vinf'] - x['vth'] for x in cold)
    # EN drive from OUTB through RD/RUV2 (both ERA-3ARB). EN high/low worst values
    # RD (RDEN) and RUV2 are generic 1 % parts (RUV2 = unchanged baseline 1 %): strict E_RES_1PCT (fixed 2026-10-25, was ERA E_RES)
    E_EN = E_RES_1PCT
    en_hi_min = (DS['TPS7A1650_V5'][0] - DS['TLV3202_VOH_DROP'][1]) * RUV2 * (1 - E_EN) / (RD * (1 + E_EN) + RUV2 * (1 - E_EN)) - DS['LM70880_IEN'][0] * (RD * RUV2 / (RD + RUV2))
    en_hi_max = DS['TPS7A1650_V5'][1] * RUV2 * (1 + E_EN) / (RD * (1 - E_EN) + RUV2 * (1 + E_EN)) + DS['LM70880_IEN'][0] * (RD * RUV2 / (RD + RUV2))
    en_lo_max = DS['TLV3202_VOL'][1] * RUV2 * (1 + E_EN) / (RD * (1 - E_EN) + RUV2 * (1 + E_EN)) + DS['LM70880_IEN'][0] * (RD * RUV2 / (RD + RUV2))
    # U22 (second TMUX1102, 2026-10-25 fix for dip0v-300us-mbmin-tmin): EN_BUCK -> GND while OUTA_UV is LOW.
    # OFF leakage (2 nA, conservative ON/OFF bound) loads EN in the high state; ON state: EN = I(RDEN) * RON.
    en_hi_min -= DS['TMUX1102_ILEAK'][0] * (RD * RUV2 / (RD + RUV2))
    en_lo_gated_max = (DS['TPS7A1650_V5'][1] / (RD * (1 - E_EN)) + DS['LM70880_IEN'][0]) * DS['TMUX1102_RON'][1]
    m = dict(seq_min_margin_s=tmin - REQ['T_SEQ_MIN'], latency_margin_s=REQ['T_SEQ_MAX'] - tmax,
             seq_after_full_dip_margin_s=min(x['t'] for x in dip) - REQ['T_SEQ_MIN'],
             timer_headroom_margin_V=headroom - 0.2, en_high_margin_V=en_hi_min - DS['LM70880_VEN_TH'][1] - 0.5,
             en_low_margin_V=DS['LM70880_EN_LOW_LOGIC'][0] - en_lo_max,
             en_low_gated_margin_V=DS['LM70880_EN_LOW_LOGIC'][0] - en_lo_gated_max)
    return dict(RT=RT, CT=CT, RHB=RHB, RK1=RK1, RK2=RK2, RD=RD, RUV2=RUV2, t_cold_min=tmin, t_cold_max=tmax,
                t_after_dip_min=min(x['t'] for x in dip), t_after_dip_max=max(x['t'] for x in dip),
                timer_headroom_min=headroom, en_high_min=en_hi_min, en_high_max=en_hi_max, en_low_max=en_lo_max, en_low_gated_max=en_lo_gated_max,
                margins=m, ok=all(v >= 0 for v in m.values()))


# ---------------- alternatives ----------------
def divider_range(vth_lo, vth_hi, Rtop, Rbot, e):
    lo = vth_lo * (1 + Rtop * (1 - e) / (Rbot * (1 + e)))
    hi = vth_hi * (1 + Rtop * (1 + e) / (Rbot * (1 - e)))
    return lo, hi


def alternatives():
    R = REQ['R_TOTAL_MAX']; alt = {}
    lo, hi = divider_range(0.95, 1.05, 180e3, 10e3, E_RES_1PCT)
    alt['A0_baseline_180k_10k'] = dict(desc='LM70880 EN/UVLO native, RUV1 180k / RUV2 10.0k (1 %, A: 100 ppm/K)', rise_min=lo, rise_max=hi,
        fall='NOT guaranteed (VEN-HYS typ only); typ ~0.9*rise', fall_typ_mid=0.9 * 19.0,
        verdict='FAIL: rise_max > 20.0 V (no guaranteed start at 20 V) and fall not guaranteed', pass_=hi <= 20.0 - 0.00375)
    # A1: retune divider only so rise_max <= 19.99 V
    ratio = (19.99 - 0.00375) / 1.05 / (1 + 2 * E_RES_1PCT) - 1
    lo1, hi1 = divider_range(0.95, 1.05, ratio * 10e3, 10e3, E_RES_1PCT)
    alt['A1_divider_retune'] = dict(desc=f'native EN, RUV1 = {ratio*10:.1f}k (ideal, 1 %)', rise_min=lo1, rise_max=hi1,
        fall_typ_nominal=0.9 * (1 + ratio), verdict='FAIL: falling threshold typ (nominal) ~%.2f V < 18.0 V and never guaranteed' % (0.9 * (1 + ratio)), pass_=False)
    # B: TPS3700 window detector (G: VIT+ 396/404 mV, VIT- 387/400 mV, Vhys 5.5 typ, 12 max, min not specified)
    eB = 2 * E_RES
    ratioB = (19.99 - 0.00375) / 0.404 / (1 + eB)
    alt['B_TPS3700'] = dict(desc='TPS3700 (SBVS187G p6) + ERA-3ARB divider, native hysteresis', rise_max=0.404 * ratioB * (1 + eB),
        rise_min=0.396 * ratioB * (1 - eB), fall_min=0.387 * ratioB * (1 - eB), fall_max=0.400 * ratioB * (1 + eB),
        hyst_typ=0.0055 * ratioB, need_h=P_IN / 18.0 * R + REQ['MARGIN_DYN'],
        verdict='FAIL: hysteresis typ %.2f V (min not specified) << I*R + margin %.2f V -> motorboating' % (0.0055 * ratioB, P_IN / 18.0 * R + 0.1), pass_=False)
    # D: LM7480 EN/UVLO (SNOSD95C p5 G: rise 1.195/1.267, fall 1.091/1.159)
    ratioD = (19.99 - 0.00375) / 1.267 / (1 + eB)
    alt['D_LM7480_EN_UVLO'] = dict(desc='LM74800/LM74810 EN/UVLO comparator (SNOSD95C p5) replacing LM74700', rise_max=1.267 * ratioD * (1 + eB),
        fall_min=1.091 * ratioD * (1 - eB), verdict='FAIL: fall_min %.2f V < 18.0 V (over-discharge)' % (1.091 * ratioD * (1 - eB)), pass_=False)
    return alt


CHOSEN_C3 = dict(Rt=39.2e3, Rb=8.87e3, Rx=90.9e3, RR1=10.0e3, RR2=46.4e3)   # frozen from search_c3() output
CHOSEN_TIMER = dict(RT=11.0e3, CT=10e-6, RHB=1.0e6, RK1=10.0e3, RK2=40.2e3, RD=10.0e3, RUV2=10.0e3)


def main():
    c3_best, n3 = search_c3()
    c2_best, n2 = search_c2()
    ch = CHOSEN_C3
    chosen = eval_c3(ch['Rt'], ch['Rb'], ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'])
    tm = eval_timer(**CHOSEN_TIMER)
    rss = eval_c3(ch['Rt'], ch['Rb'], ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'],
                  e_res=math.sqrt(sum(v * v for v in RES_TERMS.values())), e_ref=math.sqrt(sum(v * v for v in REF_TERMS.values())))
    mis_rb = eval_c3(ch['Rt'], 8.66e3, ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'])      # Rb one E96 step low -> must FAIL
    mis_rx = eval_c3(ch['Rt'], ch['Rb'], 100e3, RR1=ch['RR1'], RR2=ch['RR2'])       # Rx one-two steps high -> must FAIL
    alt = alternatives()
    alt['C2_TLV3202_pushpull_Rh'] = dict(desc='TLV3202 A with Rh from OUTA (hysteresis ~ VOH-VOL)', best=c2_best, n_candidates=n2,
                                          verdict=('PASS' if c2_best['ok'] else 'FAIL: best E96 worst margin %.3f V (VOH/VOL spread)' % c2_best['worst']),
                                          pass_=c2_best['ok'])
    alt['C3_TLV3202_TMUX1102_switched_divider'] = dict(desc='CHOSEN', best_search=c3_best, n_candidates=n3, chosen=chosen, pass_=chosen['ok'])
    out = dict(requirements=REQ, r_breakdown=R_BREAKDOWN, r_breakdown_sum=sum(R_BREAKDOWN.values()), p_in=P_IN,
               i_in_at_18V=P_IN / 18.0, iR_at_18V=P_IN / 18.0 * REQ['R_TOTAL_MAX'],
               ds=DS, ref_terms=REF_TERMS, e_ref=E_REF, res_terms=RES_TERMS, e_res=E_RES, vio_c2=VIO_TOT, vio_c3=VIO_C3,
               chosen_c3_values=CHOSEN_C3, chosen_c3=chosen, chosen_c3_rss_info=rss, timer_values=CHOSEN_TIMER, timer=tm,
               spice_corners_c3=c3_spice_corners(ch), spice_corners_timer=timer_spice_corners(CHOSEN_TIMER),
               regression_misset_rb_8k66=mis_rb, regression_misset_rx_100k=mis_rx, alternatives=alt)
    json.dump(out, open('results/uvlo-budget.json', 'w'), indent=1, default=str)
    checks = {'C3 chosen all margins >= 0': chosen['ok'], 'timer all margins >= 0': tm['ok'],
              'regression A0 baseline fails': not alt['A0_baseline_180k_10k']['pass_'],
              'regression mis-set Rb 8.66k fails': not mis_rb['ok'], 'regression mis-set Rx 100k fails': not mis_rx['ok']}
    for k, v in checks.items():
        print(('PASS ' if v else 'FAIL ') + k)
    print('C3 chosen: Vr %.3f..%.3f  Vf %.3f..%.3f  H %.3f..%.3f  margins %s' % (chosen['vr_min'], chosen['vr_max'], chosen['vf_min'],
          chosen['vf_max'], chosen['h_min'], chosen['h_max'], {k: round(v, 4) for k, v in chosen['margins'].items()}))
    print('timer cold %.1f..%.1f ms, after deep dip %.1f..%.1f ms, EN hi>=%.3f V lo<=%.3f V' % (tm['t_cold_min'] * 1e3, tm['t_cold_max'] * 1e3,
          tm['t_after_dip_min'] * 1e3, tm['t_after_dip_max'] * 1e3, tm['en_high_min'], tm['en_low_max']))
    print('C2 best worst margin %.4f V ; mis Rb worst %.4f ; mis Rx worst %.4f' % (c2_best['worst'], mis_rb['worst'], mis_rx['worst']))
    for k, v in alt.items():
        print(k, '->', v.get('verdict', v.get('desc')))
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == '__main__':
    main()
