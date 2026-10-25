#!/usr/bin/env python3
"""WP2 Tur-3 (ChatGPT combined review 6396616875, WP2 part) tests, written BEFORE the fixes (first run on 4548d44).
Exit 0 = every test behaves as required, 1 = at least one test failed. Stdlib only.

V01  (UVLO-T3-01) INFO cases are NOT exempt from the mandatory gates: a 60 ms VIN-OK -> EN violation (cold start or
     restart), a V_f < 18.0 V shutdown, or a missing / failed / non-finite gate measurement fails the verifier for PASS
     *and* INFO cases. The restart gate applies to EVERY EN rise (also without a measured EN_F1), measured from the latest
     OUTA rise before it (after the dip start for dip cases); untracked OUTA / EN rises are fail-closed.
V05  (UVLO-T3-05) the case kind is validated before the regression classification (unknown kind + regression FAIL).
V06  (UVLO-T3-06) NaN / +Inf / -Inf in VIN_AT_SHUTDOWN, OUTA_R1, EN_R1 fail (and never crash the verifier);
     runner_exit_code must be present and exactly 0.
D    (UVLO-T3-02) CTT fast-reset design: block topology, budget, case set (dips, double dips, no-reset regressions),
     deck measurements (V(T_UV) at every OUTA / EN rise and at reset release).
B    (UVLO-T3-07) per-corner CMRR/VIO + REF load; vertex counts recorded. (UVLO-T3-04) ACAS DF endurance / solder terms
     are assumptions (AE-only figures). BOM (UVLO-T3-08) candidate MPNs present. R9 (UVLO-T3-09) naming.
Usage: python3 tests/test_uvlo_tur3.py [path/to/package_dir]
"""
import importlib.util, json, sys, contextlib, io, re, csv
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent
REPO = PKG.parent.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T2 = load('t2_helpers', PKG / 'tests' / 'test_uvlo_tur2.py')
vt, start_meas, rdown_meas, dip_meas = T2.vt, T2.start_meas, T2.rdown_meas, T2.dip_meas
GOOD_WIN = T2.GOOD_WIN
RS_INFO = {'kind': 'rsweep', 'expect': 'INFO', 'r': 0.30}
RD_INFO = {'kind': 'ramp_down', 'expect': 'INFO'}
DIP_INFO = {'kind': 'dip', 'expect': 'INFO', 't0': 0.26, 't1': 0.2603}
DIP = T2.DIP
DIP2 = {'kind': 'dip2', 'expect': 'PASS', 't0': 0.26, 't1': 0.2603, 'dips': [[0.26, 0.2603], [0.30, 0.3003]]}


def in_acc_fail(name):
    def f(out):
        af = out.get('summary', {}).get('acceptance_fail', [])
        return name in af, f'acceptance_fail={af}'
    return f


def dip2_meas(delay=0.0605, **o):
    """double dip: EN falls at both dips; OUTA restored at 0.2604 and 0.3004; final EN rise `delay` after the last OUTA rise."""
    m = {'O1_GLOBAL_PEAK': 10.98, 'BUS_GLOBAL_MAX': 11.0, 'EN_R1': 0.09, 'OUTA_R1': 0.001, 'FET_ON1': 0.012,
         'EN_F1': 0.2601, 'OUTA_F1': 0.26008, 'OUTA_R2': 0.2604, 'OUTA_R3': 0.3004, 'OUTA_RLAST': 0.3004,
         'EN_R2': 0.3004 + delay, 'BUS_RESTART_MAX': 11.0}
    m.update(GOOD_WIN('PRE')); m.update(GOOD_WIN('POST')); m.update(o); return m


def verifier_tests():
    T = []
    T.append(vt('V00 control: INFO rsweep start 89 ms after VIN-OK + PASS start -> exit 0', {'i': RS_INFO, 's': T2.START},
                {'i': start_meas(), 's': start_meas()}, 0))
    T.append(vt('V01a INFO rsweep: cold start 59 ms after VIN-OK -> exit != 0, in acceptance_fail', {'i': RS_INFO},
                {'i': start_meas(EN_R1=0.060, OUTA_R1=0.001)}, 'nonzero', check=in_acc_fail('i')))
    T.append(vt('V01b INFO dip: restart 0 ms after VIN-OK -> exit != 0, in acceptance_fail', {'i': DIP_INFO},
                {'i': dip_meas(delay=0.0)}, 'nonzero', check=in_acc_fail('i')))
    T.append(vt('V01c INFO ramp_down: shutdown at VIN 17.9 V -> exit != 0, in acceptance_fail', {'i': RD_INFO},
                {'i': rdown_meas(VIN_AT_SHUTDOWN=17.9)}, 'nonzero', check=in_acc_fail('i')))
    m = start_meas(); m.pop('OUTA_R1')
    T.append(vt('V01d INFO rsweep: OUTA_R1 missing -> exit != 0', {'i': RS_INFO}, {'i': m}, 'nonzero', check=in_acc_fail('i')))
    m = start_meas(); m.pop('OUTA_R1')
    T.append(vt('V01e INFO rsweep: OUTA_R1 failed! -> exit != 0', {'i': RS_INFO}, {'i': m}, 'nonzero', failed={'i': ['OUTA_R1']},
                check=in_acc_fail('i')))
    T.append(vt('V01f INFO ramp_down: VIN_AT_SHUTDOWN NaN -> exit != 0', {'i': RD_INFO},
                {'i': rdown_meas(VIN_AT_SHUTDOWN=float('nan'))}, 'nonzero', check=in_acc_fail('i')))
    m = dip_meas(delay=0.010); m.pop('EN_F1')
    T.append(vt('V01g PASS dip: EN_R2 10 ms after VIN-OK but EN_F1 missing -> exit != 0 (gate not conditional on EN_F1)',
                {'d': DIP}, {'d': m}, 'nonzero'))
    m = dip_meas(delay=0.010); m.pop('EN_F1')
    T.append(vt('V01h INFO dip: EN_R2 without EN_F1, 10 ms after VIN-OK -> exit != 0', {'i': DIP_INFO}, {'i': m}, 'nonzero',
                check=in_acc_fail('i')))
    T.append(vt('V01i control double dip (kind dip2): final EN rise 60.5 ms after the 2nd VIN-OK -> exit 0', {'d': DIP2},
                {'d': dip2_meas()}, 0))
    T.append(vt('V01j double dip: final EN rise 30 ms after the 2nd VIN-OK (39.7 ms after the 1st) -> exit != 0', {'d': DIP2},
                {'d': dip2_meas(delay=0.030)}, 'nonzero'))
    T.append(vt('V01k double dip: EN re-rises 20 ms after the 1st VIN-OK, before the 2nd dip -> exit != 0', {'d': DIP2},
                {'d': dip2_meas(EN_R2=0.2804, EN_F2=0.3001, EN_R3=0.3004 + 0.0605)}, 'nonzero'))
    m = start_meas(OUTA_R2=0.002, OUTA_R3=0.003, OUTA_R4=0.004, OUTA_R5=0.005, OUTA_RLAST=0.050, EN_R1=0.090)
    T.append(vt('V01l > 5 OUTA rises, EN rise between OUTA_R5 and OUTA_RLAST (untracked rises) -> exit != 0',
                {'s': T2.START}, {'s': m}, 'nonzero'))
    m = dip_meas(); m.update(EN_R3=0.40, EN_R4=0.45, EN_RLAST=0.47, EN_F2=0.39, EN_F3=0.44)
    T.append(vt('V01m > 4 EN rises (EN_RLAST after EN_R4, untracked) -> exit != 0', {'d': DIP}, {'d': m}, 'nonzero'))
    # ---- T3-05
    T.append(vt('V05a unknown kind with regression=true/expect=FAIL -> exit != 0 (kind validated first)',
                {'x': {'kind': 'bogus', 'expect': 'FAIL', 'regression': True}}, {'x': start_meas(O1_GLOBAL_PEAK=13.0)}, 'nonzero',
                check=in_acc_fail('x')))
    T.append(vt('V05b missing kind with regression=true/expect=FAIL -> exit != 0',
                {'x': {'expect': 'FAIL', 'regression': True}}, {'x': start_meas(O1_GLOBAL_PEAK=13.0)}, 'nonzero', check=in_acc_fail('x')))
    # ---- T3-06 non-finite values (ngspice prints nan / inf / -inf)
    for key, mk, case in (('VIN_AT_SHUTDOWN', rdown_meas, T2.RDOWN), ('OUTA_R1', start_meas, T2.START), ('EN_R1', start_meas, T2.START)):
        for val, lab in ((float('nan'), 'NaN'), (float('inf'), '+Inf'), (float('-inf'), '-Inf')):
            T.append(vt(f'V06 {key} = {lab} -> exit != 0 (no crash)', {'c': case}, {'c': mk(**{key: val})}, 'nonzero'))

    def no_rc(mf):
        mf.pop('runner_exit_code'); return mf

    def null_rc(mf):
        mf['runner_exit_code'] = None; return mf
    T.append(vt('V06j manifest without runner_exit_code -> exit != 0', {'s': T2.START}, {'s': start_meas()}, 'nonzero', manifest=no_rc))
    T.append(vt('V06k manifest runner_exit_code null -> exit != 0', {'s': T2.START}, {'s': start_meas()}, 'nonzero', manifest=null_rc))
    return T


def design_tests():
    res = []
    blk = (PKG / 'pdu-uvlo-block.inc').read_text()
    blko = (PKG / 'pdu-uvlo-block-o3.inc').read_text()
    lines = {l.split()[0]: l.split() for l in blk.splitlines() if l.strip() and not l.startswith(('*', '.'))}
    ok = ('XU24' in lines and lines['XU24'][3] == 'SEL24_UV' and 'RDSC' in lines and 'T_UV' in lines['RDSC']
          and lines.get('XU22', [None] * 4)[3] == 'OUTA_D' and 'DST' in lines and 'CST' in lines and 'RST' in lines
          and lines.get('XU25', [None] * 4)[3] == 'OUTB_UV')
    res.append(('D1 C3 block: CTT reset switch U24 (SEL = scaled stretched OUTA_D) + RDSC, U22 gated by OUTA_D, '
                'Schmitt threshold switch U25 (SEL = OUTB)', ok, 'present' if ok else 'missing'))
    ok = all(x in blko for x in ('XU24 ', 'XU25 ', 'DST ', 'XU22 EN_BUCK 0 0 OUTA_D'))
    res.append(('D1b O3 block carries the same reset/Schmitt topology', ok, 'present' if ok else 'missing'))
    B = json.loads((PKG / 'results' / 'uvlo-budget.json').read_text())
    rs = B.get('timer', {}).get('reset')
    if not rs:
        res.append(('D2 budget timer.reset analysis present', False, 'missing')); rs = {}
    else:
        m = rs.get('margins', {})
        ok = (rs.get('ok') is True and all(v >= 0 for v in m.values()) and rs['v_rel_max'] <= rs['v_l_min'] - 0.1
              and rs['t_after_short_dip_min'] >= 0.065 and rs['i_peak_max'] <= 0.180)
        res.append(('D2 budget: CTT at reset release <= V_L,min - 0.1 V, delay after any reset >= 65 ms target, TMUX peak <= 180 mA',
                    ok, {k: rs.get(k) for k in ('v_rel_max', 'v_l_min', 't_after_short_dip_min', 'i_peak_max')}))
    tm = B.get('timer', {})
    ok = tm.get('t_cold_max', 1) <= 0.300 and tm.get('t_cold_min', 0) >= 0.065
    res.append(('D5 cold-start delay range within [65 ms target, 300 ms latency]', ok, (tm.get('t_cold_min'), tm.get('t_cold_max'))))
    C = json.loads((PKG / 'test-cases-uvlo.json').read_text())['cases']
    need = []
    for pre in ('', 'o3-'):
        for d in ('dip0v-100us', 'dip0v-200us', 'dip0v-250us', 'dip0v-300us', 'dip0v-1ms', 'dip0v-50ms', 'dip15v-20ms', 'dip19v-50ms'):
            for cn in ('typ-ttyp', 'mbmin-tmin'):
                need.append(f'{pre}{d}-{cn}')
        for cn in ('typ-ttyp', 'mbmin-tmin'):
            need.append(f'{pre}dbldip0v-300us-20ms-{cn}'); need.append(f'{pre}dbldip0v-1ms-40ms-{cn}')
    miss = [n for n in need if n not in C]
    res.append(('D3 dip set incl. 0 V 100/200/250/300 us, 1 ms, 50 ms (full load), 15 V/20 ms, 19 V/50 ms, double dips; C3 + O3',
                not miss, f'missing {miss[:6]}' if miss else f'{len(need)} present'))
    regs = {n: c for n, c in C.items() if 'noreset' in n}
    ok = (any(not n.startswith('o3-') for n in regs) and any(n.startswith('o3-') for n in regs)
          and all(c.get('regression') and c.get('expect') == 'FAIL' for c in regs.values()))
    res.append(('D3b no-reset (Tur-2 timer) regressions for C3 and O3, expect FAIL', ok, sorted(regs)))
    dk = PKG / 'decks' / 'uvlo-dip0v-300us-mbmin-tmin.cir'
    t = dk.read_text() if dk.exists() else ''
    ok = all(f'VT_AT_OUTA_R{i}' in t for i in (1, 2, 3)) and 'VT_AT_OUTA_RLAST' in t and 'VT_AT_EN_R2' in t and 'VT_AT_REL' in t \
        and 'OUTA_R5' in t and 'EN_RLAST' in t and 'V5_MIN_DIP' in t
    res.append(('D4 dip deck measures V(T_UV) at every OUTA / EN rise and at reset release, OUTA_R5/EN_RLAST, V5 min', ok,
                'ok' if ok else 'missing'))
    return res


def budget_tests():
    res = []
    with contextlib.redirect_stdout(io.StringIO()):
        b = load('uvlo_budget_t3', PKG / 'uvlo_budget.py')
    ch = b.CHOSEN_C3
    V = b.c3_vertices(ch['Rt'], ch['Rb'], ch['Rx'], RR1=ch['RR1'], RR2=ch['RR2'], detail=True)
    mags = {round(abs(v['VIOA']), 12) for v in V}
    res.append(('B7a C3: VIO/CMRR evaluated per corner (|VIO| varies with RR1/RR2 vertex)', len(mags) > 1, f'{len(mags)} distinct |VIO|'))
    BJ = json.loads((PKG / 'results' / 'uvlo-budget.json').read_text())
    nv = BJ.get('n_vertices', {})
    res.append(('B7b vertex counts recorded: C3 4096, O3 16384', nv.get('c3') == 4096 and nv.get('o3') == 16384, nv))
    O = BJ['o3_variant']
    bad = [k for k in list(O['net_abs_terms']) + list(O['net_rel_terms'])
           if re.search(r'endurance|solder', k, re.I) and not re.search(r'\(A[,:)]|\bA:', k)]
    res.append(('B4a ACAS DF endurance / soldering-heat terms (abs + rel) labelled assumption (AE-only figures)', not bad, bad))
    terms = [t['term'] for t in O['start_guarantee']['non_guaranteed_terms']]
    ok = any('absolute' in t.lower() and 'DF' in t for t in terms)
    res.append(('B4b O3 start-guarantee lists the DF absolute endurance/solder term as non-guaranteed', ok, terms[-3:]))
    bom = (REPO / 'hardware' / 'proposals' / '2026-10-25-uvlo' / 'candidate-bom.csv').read_text()
    ok = 'ACASN5361U2432P1AT' in bom and 'ACASN1002U4122P1AT' in bom
    res.append(('BOM1 candidate MPNs ACASN5361U2432P1AT (5.36k/24.3k) and ACASN1002U4122P1AT (10.0k/41.2k) present', ok, ''))
    v = (PKG / 'verify_uvlo.py').read_text()
    res.append(('R9 R-DIP screen reports the last downward threshold crossing (renamed)', 'last_downward_crossing' in v, ''))
    return res


def main():
    rows = verifier_tests() + design_tests() + budget_tests()
    for n, ok, d in rows:
        print(('OK  ' if ok else 'BAD ') + n + '  -> ' + str(d))
    bad = sum(1 for _, ok, _ in rows if not ok)
    print(f'{len(rows) - bad}/{len(rows)} OK')
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
