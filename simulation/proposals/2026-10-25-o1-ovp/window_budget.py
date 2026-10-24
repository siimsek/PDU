#!/usr/bin/env python3
"""WP1 (2026-10-25-o1-ovp) MIN/MAX window budget for the hybrid global OVP (stdlib only).

Every number is tagged with its source. 'G' = datasheet MIN/MAX (guaranteed,
incl. 'ensured by characterization' where noted). 'T' = typical-only, NEVER
added to the guaranteed sum. 'A' = explicit engineering assumption (Varsayim); the result
is reported as 'G+A' when an assumption is needed to close it.
'I' = inference from a guaranteed spec (Cikarim). No criterion is loosened:
o1 limit stays 12 V instantaneous; no-false-trip floor stays >= 11.22 V.
Usage: python window_budget.py [--json out.json] [--md out.md]
"""
import json, math, sys, argparse

E96 = [1.00,1.02,1.05,1.07,1.10,1.13,1.15,1.18,1.21,1.24,1.27,1.30,1.33,1.37,1.40,1.43,1.47,1.50,
       1.54,1.58,1.62,1.65,1.69,1.74,1.78,1.82,1.87,1.91,1.96,2.00,2.05,2.10,2.15,2.21,2.26,2.32,
       2.37,2.43,2.49,2.55,2.61,2.67,2.74,2.80,2.87,2.94,3.01,3.09,3.16,3.24,3.32,3.40,3.48,3.57,
       3.65,3.74,3.83,3.92,4.02,4.12,4.22,4.32,4.42,4.53,4.64,4.75,4.87,4.99,5.11,5.23,5.36,5.49,
       5.62,5.76,5.90,6.04,6.19,6.34,6.49,6.65,6.81,6.98,7.15,7.32,7.50,7.68,7.87,8.06,8.25,8.45,
       8.66,8.87,9.09,9.31,9.53,9.76]

P = {
 # REF35409 (SNAS809C, Sep 2024, p5)
 'VREF_nom': (4.096, 'V', 'G', 'REF35409 nominal, SNAS809C p1/p5'),
 'VREF_init': (0.0005, '1', 'G', 'REF35 initial accuracy +/-0.05 % max @25C, SNAS809C p5'),
 'VREF_TC': (12e-6, '1/K', 'G', 'REF35 TC 12 ppm/K max (box) -40..105C SOT-23, SNAS809C p5'),
 'VREF_dT': (145.0, 'K', 'A', 'full -40..105C box span applied as deviation from 25C value (conservative)'),
 'VREF_line': (120e-6, '1/V', 'G', 'REF35 line regulation 120 ppm/V max (VREF>=2.5V), SNAS809C p5'),
 'VREF_dVin': (0.504, 'V', 'I', 'TPS7A1650 5V +/-2 % (SBVS171F p6) -> 4.9..5.1V vs test VIN=VREF+0.5=4.596V'),
 'VREF_load': (60e-6, '1/mA', 'G', 'REF35 load reg 60 ppm/mA max (sourcing), SNAS809C p5'),
 'VREF_longterm_typ': (40e-6, '1', 'T', 'REF35 long-term 40 ppm 1000h TYPICAL, SNAS809C p5'),
 'VREF_thyst_typ': (70e-6, '1', 'T', 'REF35 thermal hysteresis 70 ppm TYPICAL, SNAS809C p5'),
 # TLV3601 (SNOSDB1E, Apr 2023, p7-8)
 'VIO': (5e-3, 'V', 'G', 'TLV3601 VIO +/-5 mV max -40..125C @VCM=VEE+0.3V, SNOSDB1E p7'),
 'VHYST_min': (1.5e-3, 'V', 'G', 'TLV3601 VHYST min 1.5 mV, SNOSDB1E p7'),
 'VHYST_max': (5e-3, 'V', 'G', 'TLV3601 VHYST max 5 mV (ensured by characterization), SNOSDB1E p7'),
 'IB': (5e-6, 'A', 'G', 'TLV3601 IB 5 uA max -40..125C, SNOSDB1E p7'),
 'CMRR_typ_dB': (80, 'dB', 'T', 'TLV3601 CMRR 80 dB TYPICAL only; VIO not guaranteed at VCM=4.096V, SNOSDB1E p7'),
 'VCM_allow': (4.096e-3, 'V', 'A', 'ASSUMPTION A1: extra offset at VCM=4.096V <= 4.1 mV (= 60 dB CMRR over 4.1 V, 20 dB worse than the 80 dB typical). TLV3601 VIO is guaranteed only at VCM=VEE+0.3V (SNOSDB1E 6.5 conditions). Open guarantee gap G1.'),
 'tPD_cmp': (4.5e-9, 's', 'G', 'TLV3601 tPD 4.5 ns max -40..125C @50 mV overdrive (char.), SNOSDB1E p7'),
 'VOD_spec': (50e-3, 'V', 'G', 'overdrive at which tPD is specified, SNOSDB1E p7'),
 # TPS48000-Q1 (SLUSEZ1B, Mar 2026)
 'tPD_INP_L': (1.05e-6, 's', 'G', 'TPS4800 tPD(INP_L) 1.05 us max, INP low -> PD low (1V, Fig. p11), CL=47nF, TJ=-40..150C, test VS=48V, V(BST-SRC)=11V, SLUSEZ1B p7'),
 'VBST_TEST': (11.0, 'V', 'G', 'switching-table test condition V(BST-SRC)=11 V, SLUSEZ1B p7'),
 'IPD_typ': (2.0, 'A', 'T', 'TPS4800 I(PD) 2 A peak TYPICAL only, SLUSEZ1B p7'),
 'VBST_OFF_max': (13.86, 'V', 'G', 'charge pump turn-off 13.86 V max = max VGS, SLUSEZ1B p6'),
 'VBST_ON_min': (8.24, 'V', 'G', 'charge pump turn-on 8.24 V min = min VGS (steady), SLUSEZ1B p6'),
 't_gate_tail': (50e-9, 's', 'A', 'allowance from V(PD-SRC)=1V to channel cut-off at hot Vth (<1V possible)'),
 'Q_47nF_test': (470e-9, 'C', 'I', 'tPD(INP_L) test load 47 nF from V(BST-SRC)=11 V to 1 V = 470 nC; our gate charge (4 FETs, <=277 nC at 13.86 V) is smaller -> INFERENCE (not a TI guarantee) that tPD(INP_L) max still covers it'),
 # CSD18540Q5B (SLPS488B, Apr 2017, p3)
 'Qg10_max': (53e-9, 'C', 'G', 'CSD18540Q5B Qg(10V) 53 nC max, SLPS488B p3'),
 'Ciss_max': (4.23e-9, 'F', 'G', 'CSD18540Q5B Ciss 4230 pF max, SLPS488B p3'),
 'NFET': (4, '1', 'A', 'two parallel back-to-back pairs QA1/QA2 + QB1/QB2, one gate drive (PD tied to all gates)'),
 # Divider: Panasonic ERA-3ARB (AOA0000C307, 24-Apr-24, p2)
 'R_tol': (0.001, '1', 'G', 'ERA-3ARB +/-0.1 %, AOA0000C307 p2'),
 'R_TCR': (10e-6, '1/K', 'G', 'ERA-3ARB +/-10 ppm/K, AOA0000C307 p2'),
 'R_dT': (100.0, 'K', 'A', 'resistor at -40..125C, worst |T-25C|=100 K (no TCR tracking credited)'),
 'R_life': (0.001, '1', 'G', 'ERA-3A endurance/soldering/damp-heat test limit +/-0.1 % each (separate column)'),
 'RIN': (1000.0, 'ohm', 'A', 'series input resistor tap->IN- (abs-max current limit); IB flows through Rpar+RIN'),
 'Cf': (100e-12, 'F', 'A', 'C0G 100 pF filter at comparator IN- (Rpar*Cf lag added)'),
 'Cf_tol': (0.05, '1', 'G', 'C0G +/-5 % (GRM1885C1H101JA01, to be confirmed)'),
 # Window limits (requirements, unchanged)
 'V_O1_MAX': (12.0, 'V', 'G', 'O1 instantaneous absolute limit, requirement (not loosened)'),
 'V_FLOOR': (11.22, 'V', 'A', 'no-false-trip floor: 11.1605 V static max + 59.5 mV ripple/transient allowance = 11.22 V acceptance ceiling'),
 'V_STATIC_MAX': (11.1605, 'V', 'G', 'check_static_corners baseline static bus max'),
}
v = lambda k: P[k][0]
SLOPES = [0.07e6, 0.17e6, 0.23e6]  # V/s (0.07, 0.17, 0.23 V/us)

def vref_bounds():
    rel = v('VREF_init') + v('VREF_TC')*v('VREF_dT') + v('VREF_line')*v('VREF_dVin') + v('VREF_load')*v('IB')*1e3
    return v('VREF_nom')*(1-rel), v('VREF_nom')*(1+rel), rel

def trip_bounds(rt, rb, life=False):
    """Rising trip at RAW: comparator IN- (divided RAW) vs IN+ (VREF).
    Rising-trip input offset taken as [-VIO, +VIO+VHYST_max] (union of the
    possible VOS/VHYST conventions -> conservative). IB of 5 uA in either
    direction through Rt||Rb."""
    dr = v('R_tol') + v('R_TCR')*v('R_dT') + (v('R_life') if life else 0)
    vlo, vhi, _ = vref_bounds()
    off_lo, off_hi = -v('VIO') - v('VCM_allow'), v('VIO') + v('VCM_allow') + v('VHYST_max')
    res = []
    for st in (-1, 1):
        for sb in (-1, 1):
            Rt = rt*(1+st*dr); Rb = rb*(1+sb*dr)
            k = Rb/(Rt+Rb); rpar = Rt*Rb/(Rt+Rb)
            for vr in (vlo, vhi):
                for off in (off_lo, off_hi):
                    for ib in (-v('IB'), v('IB')):
                        # IN- node: V = k*VRAW - IB*Rpar (IB into pin, sign free)
                        res.append(((vr+off) + ib*(rpar+v('RIN')*(1+dr)))/k)
    return min(res), max(res)

def qgate_total():
    q1 = v('Qg10_max') + v('Ciss_max')*(v('VBST_OFF_max')-10)
    return q1, q1*v('NFET')

def dyn_overshoot(rt, rb, S, extra_t=0.0):
    dr = v('R_tol') + v('R_TCR')*v('R_dT')
    kmin = rb*(1-dr)/(rt*(1+dr)+rb*(1-dr))
    rpar = rt*rb/(rt+rb)*(1+dr)
    tau = rpar*v('Cf')*(1+v('Cf_tol'))
    v_od = v('VOD_spec')/kmin
    t = tau + v('tPD_cmp') + v('tPD_INP_L') + v('t_gate_tail') + extra_t
    return v_od, tau, t, v_od + S*t

def short_waveform(rt, rb, C, esr, hi, I0=7.5, V0=11.1605, VS=26.0, L=2.72e-6, R=0.0154, dt=1e-9, extra_t=0.0):
    """Buck high-side short bound (same bench shape as build_global_ovp_candidates.py):
    ideal 26 V through 2.72 uH + 15.4 mOhm into the RAW bank C (+ESR), all load removed at
    t=0, inductor current starts at the 7.5 A load current. RAW is the bus voltage while the
    FETs conduct, so V_RAW(t_off) bounds the bus and the O1 port (the eFuse path adds only
    R/C). Comparator trips when the RC-filtered divided RAW reaches the guaranteed-max trip
    plus the 50 mV spec overdrive (RAW-referred). Explicit Euler, 1 ns step."""
    dr = v('R_tol') + v('R_TCR')*v('R_dT')
    kmin = rb*(1-dr)/(rt*(1+dr)+rb*(1-dr))
    tau = rt*rb/(rt+rb)*(1+dr)*v('Cf')*(1+v('Cf_tol'))
    thr = hi + v('VOD_spec')/kmin
    chain = v('tPD_cmp') + v('tPD_INP_L') + v('t_gate_tail') + extra_t
    i, vc, vf, t, t_trip, vmax = I0, V0, V0, 0.0, None, V0
    while True:
        vraw = vc + i*esr
        di = (VS - R*i - vraw)/L
        i += di*dt; vc += i/C*dt; vf += (vraw - vf)/tau*dt; t += dt
        vraw = vc + i*esr; vmax = max(vmax, vraw)
        if t_trip is None and vf >= thr: t_trip = t
        if t_trip is not None and t >= t_trip + chain: break
        if t > 200e-6: break
    return dict(C=C, ESR=esr, t_trip_s=t_trip, t_off_s=t, thr_raw_V=thr, raw_at_off_V=vraw, raw_max_to_off_V=vmax,
                pass_upper=vmax <= v('V_O1_MAX'), margin_to_12V=v('V_O1_MAX')-vmax)

def evaluate(rt, rb, life=False):
    lo, hi = trip_bounds(rt, rb, life)
    rows = []
    for S in SLOPES:
        v_od, tau, t, dv = dyn_overshoot(rt, rb, S)
        peak = hi + dv
        _, _, t2, dv2 = dyn_overshoot(rt, rb, S, qgate_total()[1]/v('IPD_typ'))
        rows.append(dict(slope_V_per_us=S/1e6, overdrive_V=v_od, tau_s=tau, t_chain_s=t,
                         dv_dynamic_V=dv, peak_worst_V=peak, margin_to_12V=v('V_O1_MAX')-peak,
                         pass_upper=peak <= v('V_O1_MAX'),
                         peak_with_typ_gate_time_added_V=hi + dv2, note_typ_gate='sensitivity only: Qtot/IPD_typ added on top (typical, not guaranteed)'))
    return dict(Rt=rt, Rb=rb, k_nom=rb/(rt+rb), vtrip_nom=v('VREF_nom')*(rt+rb)/rb,
                vtrip_min=lo, vtrip_max=hi, floor=v('V_FLOOR'), margin_floor=lo-v('V_FLOOR'),
                pass_lower=lo >= v('V_FLOOR'), slopes=rows, life_drift_included=life)

def search():
    best = None
    for rb in [1000.0, 1020.0, 1050.0, 1100.0, 1130.0, 1150.0, 1180.0, 1210.0, 1240.0, 1270.0, 1300.0]:
        for dec in (1000.0, 10000.0):
            for m in E96:
                rt = m*dec
                if not 1000 <= rt <= 5000: continue
                e = evaluate(rt, rb)
                score = min(e['margin_floor'], min(r['margin_to_12V'] for r in e['slopes']))
                if best is None or score > best[0]: best = (score, rt, rb)
    return best

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--json'); ap.add_argument('--md')
    ap.add_argument('--rt', type=float, default=None); ap.add_argument('--rb', type=float, default=None)
    a = ap.parse_args()
    score, rt, rb = search()
    if a.rt: rt = a.rt
    if a.rb: rb = a.rb
    vlo, vhi, rel = vref_bounds()
    q1, qt = qgate_total()
    g = evaluate(rt, rb); gl = evaluate(rt, rb, life=True)
    cm_typ = v('VREF_nom')*10**(-v('CMRR_typ_dB')/20)
    out = dict(params={k: dict(value=x[0], unit=x[1], kind=x[2], source=x[3]) for k, x in P.items()},
               vref_bounds=[vlo, vhi], vref_rel=rel, qgate_per_fet=q1, qgate_total=qt,
               qgate_47nF_test_load_11V_to_1V=47e-9*(v('VBST_TEST')-1),
               t_gate_typ_2A=qt/v('IPD_typ'), guaranteed=g, guaranteed_with_life=gl,
               typical_only_terms=dict(cmrr_offset_V_at_pin=cm_typ, cmrr_offset_V_at_raw=cm_typ/g['k_nom'],
                                      vref_longterm_plus_thyst_V_at_raw=(v('VREF_longterm_typ')+v('VREF_thyst_typ'))*g['vtrip_nom']),
               closes_guaranteed=g['pass_lower'] and all(r['pass_upper'] for r in g['slopes']),
               closes_with_life=gl['pass_lower'] and all(r['pass_upper'] for r in gl['slopes']),
               closes_with_typical_terms_added=None)
    # Add typical-only terms on top (informative stress, not a guarantee)
    extra = out['typical_only_terms']['cmrr_offset_V_at_raw'] + out['typical_only_terms']['vref_longterm_plus_thyst_V_at_raw']
    out['closes_with_typical_terms_added'] = (g['vtrip_min']-extra >= v('V_FLOOR')) and all(r['peak_worst_V']+extra <= 12 for r in g['slopes'])
    out['typical_terms_extra_V'] = extra
    # Abs-max/clamp and OV backstop bookkeeping (TLV3601 SNOSDB1E p6; TPS4800 SLUSEZ1B p6)
    kmax = rb*(1+0.002)/(rt*(1-0.002)+rb*(1+0.002)); rth = rt*rb/(rt+rb)
    out['clamp'] = dict(raw_where_INm_exceeds_VCCmin_plus_0p2=5.1/kmax,
                        inj_current_at_RAW45V_A=(45*kmax-5.4)/(rth+v('RIN')),
                        abs_max_input_current_A=10e-3, bleed_min_current_A=4.9/(499*1.001))
    rov1, rov2 = 90.9e3, 10.0e3
    out['ov_backstop'] = dict(ROV1=rov1, ROV2=rov2,
        assert_max_V=1.28*(rov1*1.01+rov2*0.99)/(rov2*0.99) + 205e-9*rov1,
        assert_min_V=1.17*(rov1*0.99+rov2*1.01)/(rov2*1.01) - 205e-9*rov1,
        release_min_V=1.08*(rov1*0.99+rov2*1.01)/(rov2*1.01) - 205e-9*rov1,
        tPD_OV_OFF_max_s=5.55e-6, note='backstop only; slower than INP path; 1% resistors')
    out['cbst'] = dict(CBST=0.47e-6, dip_V=qt/0.47e-6, tdrv_en_typ_s=0.47e-6*9/345e-6, tdrv_en_worst_s=0.47e-6*10.81/100e-6)
    out['short_waveform'] = [short_waveform(rt, rb, C, esr, g['vtrip_max']) for C, esr in
                             ((92.65e-6, 0.001), (165e-6, 0.001), (92.65e-6, 0.0125), (92.65e-6, 0.1))]
    out['short_waveform_typ_gate_added'] = [short_waveform(rt, rb, C, esr, g['vtrip_max'], extra_t=qt/v('IPD_typ')) for C, esr in
                             ((92.65e-6, 0.001), (165e-6, 0.001), (92.65e-6, 0.0125), (92.65e-6, 0.1))]
    out['closes_short_waveform'] = all(r['pass_upper'] for r in out['short_waveform'][:3])
    out['short_waveform_note'] = ('rows 1-3 (ESR 1 m / 12.5 mOhm, ceramic-realistic) are acceptance rows; row 4 (100 mOhm bank ESR, '
                                  '-40C stress corner carried over from the LTC4365 study) is reported separately: its RAW step '
                                  'I*ESR is outside the 0.07-0.23 V/us slope assumption')
    txt = json.dumps(out, indent=2)
    if a.json: open(a.json, 'w').write(txt + '\n')
    print(txt)
    return 0

if __name__ == '__main__':
    sys.exit(main())
