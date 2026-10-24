#!/usr/bin/env python3
"""WP1 (2026-10-25-o1-ovp) MIN/MAX window budget for the hybrid global OVP (stdlib only).

Every number is tagged with its source. 'G' = datasheet MIN/MAX (guaranteed,
incl. 'ensured by characterization' where noted). 'T' = typical-only, NEVER
added to the guaranteed sum. 'V' = explicit engineering assumption (Varsayim; was 'A' in rev1);
the result is reported as 'G+V' when an assumption is needed to close it.
'C' = inference from a guaranteed spec (Cikarim; was 'I' in rev1). No criterion is loosened:
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
 'VREF_dT': (145.0, 'K', 'V', 'full -40..105C box span applied as deviation from 25C value (conservative)'),
 'VREF_line': (120e-6, '1/V', 'G', 'REF35 line regulation 120 ppm/V max (VREF>=2.5V), SNAS809C p5'),
 'VREF_dVin': (0.504, 'V', 'C', 'TPS7A1650 5V +/-2 % (SBVS171F p6) -> 4.9..5.1V vs test VIN=VREF+0.5=4.596V'),
 'VREF_load': (60e-6, '1/mA', 'G', 'REF35 load reg 60 ppm/mA max (sourcing), SNAS809C p5'),
 'VREF_longterm_typ': (40e-6, '1', 'T', 'REF35 long-term 40 ppm 1000h TYPICAL, SNAS809C p5'),
 'VREF_thyst_typ': (70e-6, '1', 'T', 'REF35 thermal hysteresis 70 ppm TYPICAL, SNAS809C p5'),
 # TLV3601 (SNOSDB1E, Apr 2023, p7-8)
 'VIO': (5e-3, 'V', 'G', 'TLV3601 VIO +/-5 mV max -40..125C @VCM=VEE+0.3V, SNOSDB1E p7'),
 'VHYST_min': (1.5e-3, 'V', 'G', 'TLV3601 VHYST min 1.5 mV, SNOSDB1E p7'),
 'VHYST_max': (5e-3, 'V', 'G', 'TLV3601 VHYST max 5 mV (ensured by characterization), SNOSDB1E p7'),
 'IB': (5e-6, 'V', 'G', 'TLV3601 IB 5 uA max -40..125C, SNOSDB1E p7'),
 'CMRR_typ_dB': (80, 'dB', 'T', 'TLV3601 CMRR 80 dB TYPICAL only; VIO not guaranteed at VCM=4.096V, SNOSDB1E p7'),
 'VCM_allow': (4.096e-3, 'V', 'V', 'ASSUMPTION A1 (V, NOT guaranteed): extra offset at VCM=4.096V <= 4.1 mV (= 60 dB CMRR over 4.1 V, 20 dB worse than the 80 dB typical). TLV3601 VIO is guaranteed only at VCM=VEE+0.3V (SNOSDB1E 6.5 conditions). Open guarantee gap G1.'),
 'tPD_cmp': (4.5e-9, 's', 'G', 'TLV3601 tPD 4.5 ns max -40..125C @50 mV overdrive (char.), SNOSDB1E p7'),
 'VOD_spec': (50e-3, 'V', 'G', 'overdrive at which tPD is specified, SNOSDB1E p7'),
 # TPS48000-Q1 (SLUSEZ1B, Mar 2026)
 'tPD_INP_L': (1.05e-6, 's', 'G', 'TPS4800 tPD(INP_L) 1.05 us max, INP low -> PD low (1V, Fig. p11), CL=47nF, TJ=-40..150C, test VS=48V, V(BST-SRC)=11V, SLUSEZ1B p7'),
 'VBST_TEST': (11.0, 'V', 'G', 'switching-table test condition V(BST-SRC)=11 V, SLUSEZ1B p7'),
 'IPD_typ': (2.0, 'V', 'T', 'TPS4800 I(PD) 2 A peak TYPICAL only, SLUSEZ1B p7'),
 'VBST_OFF_max': (13.86, 'V', 'G', 'charge pump turn-off 13.86 V max = max VGS, SLUSEZ1B p6'),
 'VBST_ON_min': (8.24, 'V', 'G', 'charge pump turn-on 8.24 V min = min VGS (steady), SLUSEZ1B p6'),
 't_gate_tail': (50e-9, 's', 'V', 'allowance from V(PD-SRC)=1V to channel cut-off at hot Vth (<1V possible)'),
 'Q_47nF_test': (470e-9, 'C', 'C', 'tPD(INP_L) test load 47 nF from V(BST-SRC)=11 V to 1 V = 470 nC; INFERENCE (not a TI guarantee) that tPD(INP_L) max covers our 4-FET gate: gate_discharge_wc.py bounds a resistive-sink model at <=0.97x the test-load time incl. Qg max scaling, Qgd x2, plateau at an assumed hot Vth 1.1 V, VBST 13.86 V, RG max (gate-discharge-wc.json)'),
 # CSD18540Q5B (SLPS488B, Apr 2017, p3)
 'Qg10_max': (53e-9, 'C', 'G', 'CSD18540Q5B Qg(10V) 53 nC max, SLPS488B p3'),
 'Ciss_max': (4.23e-9, 'F', 'G', 'CSD18540Q5B Ciss 4230 pF max, SLPS488B p3'),
 'NFET': (4, '1', 'V', 'two parallel back-to-back pairs QA1/QA2 + QB1/QB2, one gate drive (PD tied to all gates)'),
 # Divider: Panasonic ERA-3ARB (AOA0000C307, 24-Apr-24, p2)
 'R_tol': (0.001, '1', 'G', 'ERA-3ARB +/-0.1 %, AOA0000C307 p2'),
 'R_TCR': (10e-6, '1/K', 'G', 'ERA-3ARB +/-10 ppm/K, AOA0000C307 p2'),
 'R_dT': (100.0, 'K', 'V', 'resistor at -40..125C, worst |T-25C|=100 K (no TCR tracking credited)'),
 'R_life': (0.001, '1', 'G', 'ERA-3A endurance/soldering/damp-heat test limit +/-0.1 % each (separate column)'),
 'RIN': (1000.0, 'ohm', 'V', 'series input resistor tap->IN- (abs-max current limit); IB flows through Rpar+RIN'),
 'Cf': (100e-12, 'F', 'V', 'C0G 100 pF filter at comparator IN- (Rpar*Cf lag added)'),
 'Cf_tol': (0.05, '1', 'G', 'C0G +/-5 % (GRM1885C1H101JA01, to be confirmed)'),
 # Window limits (requirements, unchanged)
 'V_O1_MAX': (12.0, 'V', 'G', 'O1 instantaneous absolute limit, requirement (not loosened)'),
 'V_FLOOR': (11.22, 'V', 'V', 'no-false-trip floor: OVP must NOT trip at the 11.22 V false-trip TEST level (+2 % band edge; = 11.1605 V normal-bus max + 59.5 mV). Normal-bus limit itself is 11.1605 V (rev2 P1-2)'),
 'V_STATIC_MAX': (11.1605, 'V', 'G', 'check_static_corners baseline static bus max'),
 # WP1 rev2 RAW bank: COUT1-8 + COUT21-28 = 16 x TDK C5750X7S2A226M280KB (22 uF/100 V X7S 2220, +/-20 %)
 'N_RAW': (16, '1', 'V', 'rev2 design choice: 8 existing + 8 added RAW capacitors, same MPN/footprint (hardware/COUT-qualification.md)'),
 'C_11V_typ': (20.62219e-6, 'F', 'T', 'TDK vendor DC-bias model @11 V 25C, 20.62219 uF per part (hardware/COUT-qualification.md; typical model, not a MIN)'),
 'C_tol': (0.20, '1', 'G', 'C5750X7S2A226M280KB capacitance tolerance +/-20 % (M), TDK part number / DigiKey 2026-10-25'),
 'C_temp': (0.22, '1', 'G', 'X7S class: +/-22 % over -55..125C (EIA X7S definition, at 0 V bias)'),
 'C_aging': (0.10, '1', 'V', 'ASSUMED 10 % aging sensitivity (no TDK guarantee; same as hardware/COUT-qualification.md)'),
 'ESR_corner': (0.0125, 'ohm', 'V', '12.5 mOhm bank ESR corner kept UNCHANGED from rev1 although 16 parts lower it (pessimistic)'),
 'MARGIN_TARGET': (0.050, 'V', 'V', 'rev2 design target: >= ~50 mV guaranteed margin to the 12.0 V O1 limit at every acceptance corner (target, not a new criterion)'),
 'ESL_bank': (2e-9, 'H', 'V', 'ASSUMED total RAW-bank ESL incl. mounting (16 parallel 2220 parts; TDK ESL not read -> deliberately pessimistic 2 nH); adds L*di/dt to RAW in the esl2n short rows'),
 'C_honest_min': (165e-6, 'F', 'V', 'independent-review honest minimum effective C (extra ~11 % below the 185.3 uF product bound for DC-bias x temperature interaction); acceptance row, not a datasheet value'),
 'C_cbias05': (176e-6, 'F', 'C', '16 x 22 uF x CBIAS 0.5 = 176 uF: the C used by the startup/load board decks (baseline CBIAS convention); acceptance row'),
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

def raw_bank():
    n, c = v('N_RAW'), v('C_11V_typ')
    lo = n*c*(1-v('C_tol'))*(1-v('C_temp'))*(1-v('C_aging'))
    hi = n*c*(1+v('C_tol'))*(1+v('C_temp'))
    return dict(n=n, typ_11V=n*c, min_eff=lo, max_eff=hi, per_part_min=lo/n, per_part_max=hi/n,
                note='min/max are multiplicative sensitivity bounds on a TYPICAL DC-bias model value (+ assumed aging); not a TDK joint guarantee')

# (name, C: 'min'/'max'/farad, ESR, ESL). Acceptance rows: product bound min/max, CBIAS-0.5 board value 176 uF,
# review 'honest minimum' 165 uF, and a pessimistic 2 nH bank ESL row.
ACC_SHORTS = (('c185', 'min', 0.001, 0.0), ('c185-esr12m5', 'min', 0.0125, 0.0), ('c483', 'max', 0.001, 0.0), ('c483-esr12m5', 'max', 0.0125, 0.0),
              ('c176', 176e-6, 0.001, 0.0), ('c176-esr12m5', 176e-6, 0.0125, 0.0), ('c165', 165e-6, 0.001, 0.0), ('c165-esr12m5', 165e-6, 0.0125, 0.0),
              ('c185-esr12m5-esl2n', 'min', 0.0125, 2e-9), ('c165-esr12m5-esl2n', 165e-6, 0.0125, 2e-9))
INFO_SHORTS = (('rev1-c92 (superseded)', 92.65e-6, 0.001, 0.0), ('rev1-c92-esr12m5 (superseded)', 92.65e-6, 0.0125, 0.0),
               ('c120-esr12m5 (info, below every bound)', 120e-6, 0.0125, 0.0), ('c130-esr12m5 (info, below every bound)', 130e-6, 0.0125, 0.0))

def short_waveform(rt, rb, C, esr, hi, I0=7.5, V0=11.1605, VS=26.0, L=2.72e-6, R=0.0154, dt=1e-9, extra_t=0.0, esl=0.0):
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
        # RAW = Vc + I*ESR + ESL*dI/dt  ->  dI/dt = (VS - R*I - Vc - I*ESR)/(L + ESL)
        di = (VS - R*i - vc - i*esr)/(L + esl)
        vraw = vc + i*esr + esl*di
        i += di*dt; vc += i/C*dt; vf += (vraw - vf)/tau*dt; t += dt
        di = (VS - R*i - vc - i*esr)/(L + esl)
        vraw = vc + i*esr + esl*di; vmax = max(vmax, vraw)
        if t_trip is None and vf >= thr: t_trip = t
        if t_trip is not None and t >= t_trip + chain: break
        if t > 200e-6: break
    return dict(C=C, ESR=esr, ESL=esl, t_trip_s=t_trip, t_off_s=t, thr_raw_V=thr, raw_at_off_V=vraw, raw_max_to_off_V=vmax,
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
    bank = raw_bank(); out['raw_bank'] = bank
    cap = lambda w: bank['min_eff'] if w == 'min' else (bank['max_eff'] if w == 'max' else w)
    tgt = v('MARGIN_TARGET')
    def rows(hi, extra=0.0):
        r = [dict(case=n, **short_waveform(rt, rb, cap(w), esr, hi, extra_t=extra, esl=l)) for n, w, esr, l in ACC_SHORTS]
        return r + [dict(case=n, **short_waveform(rt, rb, C, esr, hi, extra_t=extra, esl=l)) for n, C, esr, l in INFO_SHORTS]
    out['short_waveform'] = rows(g['vtrip_max'])
    out['short_waveform_with_life'] = rows(gl['vtrip_max'])
    out['short_waveform_typ_gate_added'] = rows(g['vtrip_max'], qt/v('IPD_typ'))
    out['short_stress_esr100m'] = short_waveform(rt, rb, bank['min_eff'], 0.1, g['vtrip_max'])
    nacc = len(ACC_SHORTS)
    out['closes_short_waveform'] = all(r['pass_upper'] for r in out['short_waveform'][:nacc])
    acc_margins = ([('slope %.2f V/us' % r['slope_V_per_us'], r['margin_to_12V']) for r in g['slopes']] +
                   [('short ' + r['case'], r['margin_to_12V']) for r in out['short_waveform'][:nacc]] + [('floor 11.22 V', g['margin_floor'])])
    acc_life = ([('slope %.2f V/us' % r['slope_V_per_us'], r['margin_to_12V']) for r in gl['slopes']] +
                [('short ' + r['case'], r['margin_to_12V']) for r in out['short_waveform_with_life'][:nacc]] + [('floor 11.22 V', gl['margin_floor'])])
    out['margin_summary'] = dict(target_V=tgt, guaranteed=acc_margins, guaranteed_with_life=acc_life,
                                 min_guaranteed_V=min(m for _, m in acc_margins), min_with_life_V=min(m for _, m in acc_life),
                                 meets_target=min(m for _, m in acc_margins) >= tgt, meets_target_with_life=min(m for _, m in acc_life) >= tgt)
    # rev2 option study (same guaranteed chain; only the named lever changes)
    def need_dt(C, esr):
        for k in range(0, 1001):
            dtt = -k*1e-9
            if short_waveform(rt, rb, C, esr, g['vtrip_max'], extra_t=dtt)['margin_to_12V'] >= tgt: return -dtt
        return None
    out['option_study'] = dict(
        A_more_C=dict(desc='16 x C5750X7S2A226M280KB (rev2 choice)', c_min_eff=bank['min_eff'],
                      margins=[(r['case'], r['margin_to_12V']) for r in out['short_waveform'][:nacc]]),
        A_min_C_for_target_esr12m5=next(C*1e-6 for C in range(93, 400) if short_waveform(rt, rb, C*1e-6, 0.0125, g['vtrip_max'])['margin_to_12V'] >= tgt),
        B_faster_turnoff_required_chain_reduction_s_at_c92=dict(esr1m=need_dt(92.65e-6, 0.001), esr12m5=need_dt(92.65e-6, 0.0125),
            note='guaranteed turn-off chain must be this much shorter than tPD_cmp+tPD(INP_L)+tail = %.4g s to reach the target with the rev1 bank' % (v('tPD_cmp')+v('tPD_INP_L')+v('t_gate_tail'))),
        C_lower_Qg=dict(guaranteed_gain_V=0.0, note='guaranteed chain uses tPD(INP_L) max which is specified at a 470 nC load (> our 277 nC): '
                        'a lower-Qg FET does not shorten any GUARANTEED term; only the typical-gate sensitivity row improves'))
    # P0-2: how much EXTRA comparator offset (pin-referred, beyond VIO + A1) the design tolerates
    def min_margin_with(extra_pin):
        old = P['VCM_allow']; P['VCM_allow'] = (old[0] + extra_pin,) + old[1:]
        try:
            gg = evaluate(rt, rb); m = [r['margin_to_12V'] for r in gg['slopes']] + [gg['margin_floor']]
            m += [short_waveform(rt, rb, cap(w), esr, gg['vtrip_max'], esl=l)['margin_to_12V'] for _, w, esr, l in ACC_SHORTS]
            return min(m)
        finally:
            P['VCM_allow'] = old
    def max_extra(target):
        lo_, hi_ = -v('VCM_allow'), 0.05
        for _ in range(40):
            mid = (lo_ + hi_)/2
            if min_margin_with(mid) >= target: lo_ = mid
            else: hi_ = mid
        return lo_
    x0, x50 = max_extra(0.0), max_extra(tgt)
    span = v('VREF_nom') - 0.3
    def cmrr_equiv(x):
        tot = v('VCM_allow') + x
        return 20*math.log10(span/tot) if tot > 0 else None
    out['vcm_tolerance'] = dict(
        vcm_operating_V=v('VREF_nom'), vio_spec_vcm_V=0.3, vcm_shift_V=span, assumed_allow_pin_V=v('VCM_allow'),
        extra_pin_offset_for_zero_margin_V=x0, extra_pin_offset_for_target_V=x50,
        total_vcm_term_pin_for_zero_margin_V=v('VCM_allow') + x0, total_vcm_term_pin_for_target_V=v('VCM_allow') + x50,
        cmrr_equivalent_dB_zero_margin=cmrr_equiv(x0), cmrr_equivalent_dB_target=cmrr_equiv(x50),
        cmrr_typ_dB=v('CMRR_typ_dB'),
        note='VCM term is an ASSUMPTION (V): TLV3601 gives no MIN CMRR and VIO only at VCM=VEE+0.3 V. Margins stay >= 0 '
             'for a VCM-induced offset up to total_vcm_term_pin_for_zero_margin_V (both the 12 V side and the 11.22 V floor checked); bench test B2.')
    out['short_waveform_note'] = ('rows c185/c185-esr12m5/c483/c483-esr12m5 are acceptance rows (rev2 16-cap bank, min/max effective C); '
                                  'rev1-c92 rows are the superseded 8-cap bank (information). short_stress_esr100m (100 mOhm bank ESR, '
                                  '-40C stress corner carried over from the LTC4365 study) is reported separately: its RAW step '
                                  'I*ESR is outside the 0.07-0.23 V/us slope assumption')
    txt = json.dumps(out, indent=2)
    if a.json: open(a.json, 'w').write(txt + '\n')
    print(txt)
    return 0

if __name__ == '__main__':
    sys.exit(main())
