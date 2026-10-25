#!/usr/bin/env python3
"""WP2 Tur-4 (ChatGPT combined review 6398375361, WP2 part) tests, written BEFORE the fixes (first run on a6a3d99).
Exit 0 = every test behaves as required, 1 = at least one test failed. Stdlib only.

W01  (UVLO-T4-01) regime() / regime_seq() fail-closed: NaN / +Inf / -Inf / missing / ngspice 'failed' in EVERY regime
     metric fails the verifier for PASS *and* INFO cases (start window RUN, dip windows PRE/POST, seq RUN); RUN_VIN_MIN
     (V_f gate of start cases) and INP_MIN_AFTER_ON (seq) are fail-closed too.
W01s (UVLO-T4-01) seq cases are STIMULUS-ONLY benches (ideal DRIVE, no UVLO block): the configured DRIVE delay is
     schema-validated (finite, >= T_SEQ_MIN = 60 ms, inclusive) for every non-regression seq case and the evidence is
     labelled 'stimulus-only' in the verifier output. 59.999 ms -> FAIL, 60.000 ms -> PASS (>= 60 ms is inclusive; the
     review text says the first two must fail - that contradicts its own >= 60 ms criterion, see CHATGPT_REVIEW_RESPONSE),
     60.001 ms -> PASS, missing / NaN / +-Inf -> FAIL. The delay-0 reference regression still reproduces.
W05  (UVLO-T4-05) M3: every VIN-OK loss (OUTA fall) while EN is high forces EN low within en_force_max (1 us) when the
     case table requests it; M4: VGS >= 6 V at every EN rise when the case table requests it (TDRV_EN / FET rearm).
     Both fail-closed (missing / non-finite measurements are errors).
W06  (UVLO-T4-06) R-DIP report classifies every dip case as rode_through / restart.
D4x  design: direct OUTA -> EN pull-down (U26) in C3 + O3 blocks; us dips 1/5/10/50 us and 20 ms for C3 + O3; TDRV_EN
     50.8 ms conservative model decks; RDSC 180 ohm exploratory decks; every candidate dip case requests M3/M4.
B4x  budget: (T4-02) RDSC sweep 100/150/180/220 ohm recorded with Ipk, t_dsc, V_rel, hold separation and the reviewer
     targets; (T4-03) ACAS DF assumption terms (absolute AND relative endurance / soldering) are ONE consistently
     unbounded group, grade-U relative TCR is a separate datasheet-supported term; O3 has exactly 4 unbounded terms.
Usage: python3 tests/test_uvlo_tur4.py [path/to/package_dir]
"""
import importlib.util, json, sys, contextlib, io, re
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent
REPO = PKG.parent.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T2 = load('t2_helpers_t4', PKG / 'tests' / 'test_uvlo_tur2.py')
vt, start_meas, dip_meas, GOOD_WIN = T2.vt, T2.start_meas, T2.dip_meas, T2.GOOD_WIN
START, DIP = T2.START, T2.DIP
START_INFO = {'kind': 'rsweep', 'expect': 'INFO', 'r': 0.30, 'vf': 18.26}
DIP_INFO = {'kind': 'dip', 'expect': 'INFO', 't0': 0.26, 't1': 0.2603}
SEQ = {'kind': 'seq', 'expect': 'PASS', 'delay': 0.0777, 'ramp': 0.0019}
SEQ_REG = {'kind': 'seq', 'expect': 'FAIL', 'regression': True, 'delay': 0.0, 'ramp': 0.0019}
VALS = ((float('nan'), 'NaN'), (float('inf'), '+Inf'), (float('-inf'), '-Inf'), (None, 'missing'), ('failed', 'failed'))
REGIME = ('BUS_MAX', 'O1_MAX', 'RAW_AVG', 'EN_MIN', 'VGS_MIN', 'INP_MIN')
SEQ_REGIME = ('RUN_BUS_MAX', 'RUN_O1_MAX', 'RUN_RAW_AVG', 'RUN_VGS_MIN', 'RUN_INP_MIN')


def seq_meas(**o):
    m = {'O1_GLOBAL_PEAK': 11.0, 'FET_ON1': 0.012, 'INP_MIN_AFTER_ON': 4.9, 'RAW_MAX': 11.2, 'BUS_STARTUP_MAX': 11.1}
    m.update(GOOD_WIN('RUN')); m.update(o); return m


def perturb(meas, key, val):
    """returns (meas, failed list) with key set to val / removed / marked ngspice 'failed!'"""
    m = dict(meas); f = []
    if val is None: m.pop(key, None)
    elif val == 'failed': f = [key]
    else: m[key] = val
    return m, f


def in_acc_fail(name):
    def f(out):
        af = out.get('summary', {}).get('acceptance_fail', [])
        return name in af, f'acceptance_fail={af}'
    return f


def case_info(name, key, want):
    def f(out):
        v = out.get('cases', {}).get(name, {}).get('info', {}).get(key)
        return v == want, f'{key}={v!r}'
    return f


def rdip_event(name, want):
    def f(out):
        v = (out.get('cases', {}).get(name, {}).get('info', {}).get('provisional_rdip_screen') or {}).get('event')
        return v == want, f'event={v!r}'
    return f


def verifier_tests():
    T = []
    # ---- W01 regime metrics, PASS and INFO, start (RUN) and dip (PRE / POST)
    for cname, case, mk, wins in (('s', START, start_meas, ('RUN',)), ('i', START_INFO, start_meas, ('RUN',)),
                                  ('d', DIP, dip_meas, ('PRE', 'POST')), ('j', DIP_INFO, dip_meas, ('PRE', 'POST'))):
        for w in wins:
            for q in REGIME:
                for val, lab in VALS:
                    m, f = perturb(mk(), f'{w}_{q}', val)
                    T.append(vt(f'W01 {case["expect"]} {case["kind"]}: {w}_{q} {lab} -> exit != 0, acceptance FAIL',
                                {cname: case}, {cname: m}, 'nonzero', failed={cname: f}, check=in_acc_fail(cname)))
    for val, lab in VALS:
        m, f = perturb(start_meas(), 'RUN_VIN_MIN', val)
        T.append(vt(f'W01v PASS start (vf set): RUN_VIN_MIN {lab} -> exit != 0 (V_f run margin fail-closed)', {'s': START}, {'s': m},
                    'nonzero', failed={'s': f}, check=in_acc_fail('s')))
    # ---- W01 seq regime + INP_MIN_AFTER_ON
    T.append(vt('W01s0 control: seq PASS (delay 77.7 ms, stimulus-only) + delay-0 regression reproduced -> exit 0',
                {'q': SEQ, 'r': SEQ_REG}, {'q': seq_meas(), 'r': seq_meas(FET_OFF1=0.0123)}, 0,
                check=case_info('q', 'seq_evidence', 'stimulus-only')))
    for q in SEQ_REGIME + ('INP_MIN_AFTER_ON',):
        for val, lab in VALS:
            m, f = perturb(seq_meas(), q, val)
            T.append(vt(f'W01s seq PASS: {q} {lab} -> exit != 0', {'q': SEQ}, {'q': m}, 'nonzero', failed={'q': f},
                        check=in_acc_fail('q')))
    T.append(vt('W01s seq PASS: RUN_RAW_AVG 12.0 V (not regulated) -> exit != 0', {'q': SEQ}, {'q': seq_meas(RUN_RAW_AVG=12.0)},
                'nonzero'))
    # ---- W01 seq configured delay (schema), boundary at T_SEQ_MIN = 60 ms inclusive
    for d, want in ((0.059999, 'nonzero'), (0.060000, 0), (0.060001, 0)):
        T.append(vt(f'W01d seq PASS configured delay {d*1e3:.3f} ms -> exit {want}', {'q': dict(SEQ, delay=d)},
                    {'q': seq_meas(FET_ON1=0.012)}, want))
    c = dict(SEQ); c.pop('delay')
    T.append(vt('W01d seq PASS without configured delay -> exit != 0', {'q': c}, {'q': seq_meas()}, 'nonzero'))
    for val, lab in ((float('nan'), 'NaN'), (float('inf'), '+Inf'), (float('-inf'), '-Inf'), ('77.7m', 'string')):
        T.append(vt(f'W01d seq PASS configured delay {lab} -> exit != 0', {'q': dict(SEQ, delay=val)}, {'q': seq_meas()}, 'nonzero'))
    # ---- W05 M3 EN forced low within en_force_max after VIN-OK loss; M4 VGS >= 6 V at every EN rise
    DIPF = dict(DIP, en_force_max=1e-6, vgs_at_en_min=6.0)

    def dipf(**o):
        # Tur-5 UVLO-T5-03: M3 now REQUIRES the direct lag -> the control set carries a consistent EN_LAG_F1 (0.4 us);
        # tests that override EN_F1 without EN_LAG_F1 still expect FAIL (now also for the missing/inconsistent lag)
        m = dip_meas(); m.update(OUTA_F1=0.2601, EN_F1=0.2601 + 0.4e-6, EN_LAG_F1=0.4e-6, VGS_AT_EN_R1=12.0, VGS_AT_EN_R2=12.0); m.update(o); return m
    T.append(vt('W05a control: EN low 0.4 us after OUTA fall, VGS 12 V at both EN rises -> exit 0', {'d': DIPF}, {'d': dipf()}, 0))
    T.append(vt('W05b EN low 2.0 us after OUTA fall (> 1 us) -> exit != 0', {'d': DIPF}, {'d': dipf(EN_F1=0.2601 + 2e-6)}, 'nonzero',
                check=in_acc_fail('d')))
    m = dipf(); m.pop('EN_F1')
    T.append(vt('W05c OUTA fell while EN high, EN_F1 missing -> exit != 0', {'d': DIPF}, {'d': m}, 'nonzero'))
    T.append(vt('W05d OUTA_F1 NaN -> exit != 0', {'d': DIPF}, {'d': dipf(OUTA_F1=float('nan'))}, 'nonzero'))
    m = dipf(); [m.pop(k) for k in ('OUTA_F1', 'EN_F1', 'OUTA_R2', 'OUTA_RLAST', 'EN_R2', 'VGS_AT_EN_R2')]
    T.append(vt('W05e ride-through (OUTA never fell, OUTA_F1 failed) -> M3 not applicable, exit 0', {'d': DIPF}, {'d': m}, 0,
                failed={'d': ['OUTA_F1', 'EN_F1', 'EN_R2']}))
    T.append(vt('W05f VGS 5.9 V at EN_R2 (FET not rearmed, TDRV_EN) -> exit != 0', {'d': DIPF}, {'d': dipf(VGS_AT_EN_R2=5.9)},
                'nonzero', check=in_acc_fail('d')))
    m = dipf(); m.pop('VGS_AT_EN_R2')
    T.append(vt('W05g VGS_AT_EN_R2 missing while EN_R2 present -> exit != 0', {'d': DIPF}, {'d': m}, 'nonzero'))
    T.append(vt('W05h VGS_AT_EN_R1 +Inf -> exit != 0', {'d': DIPF}, {'d': dipf(VGS_AT_EN_R1=float('inf'))}, 'nonzero'))
    T.append(vt('W05i INFO dip with en_force_max: EN low 3 us after OUTA fall -> exit != 0', {'j': dict(DIPF, expect='INFO')},
                {'j': dipf(EN_F1=0.2601 + 3e-6)}, 'nonzero', check=in_acc_fail('j')))
    # ---- W05j-n (Tur-4 smoke finding): ngspice prints .meas results with 6 significant digits, i.e. 1 us resolution at
    # t ~ 0.27 s - M3 must use the direct TRIG/TARG lag EN_LAG_F<k> (OUTA fall k -> EN fall k) when it is consistent with
    # the absolute times within their print resolution; otherwise (missing / inconsistent) the absolute difference decides.
    T.append(vt('W05j printed times 1 us apart (rounding), direct EN_LAG_F1 0.3 us consistent -> exit 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275437, EN_LAG_F1=0.3e-6)}, 0))
    T.append(vt('W05k direct EN_LAG_F1 2.5 us -> exit != 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275438, EN_LAG_F1=2.5e-6)}, 'nonzero', check=in_acc_fail('d')))
    T.append(vt('W05l EN_LAG_F1 0.3 us inconsistent with 5 us absolute difference -> exit != 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275441, EN_LAG_F1=0.3e-6)}, 'nonzero', check=in_acc_fail('d')))
    T.append(vt('W05m EN_LAG_F1 NaN -> M3 not provable (Tur-5 fail-closed; absolute 2 us also > 1 us) -> exit != 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275438, EN_LAG_F1=float('nan'))}, 'nonzero', check=in_acc_fail('d')))
    T.append(vt('W05n negative EN_LAG_F1 (EN fell before OUTA) -> M3 not provable (Tur-5 fail-closed) -> exit != 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275438, EN_LAG_F1=-1e-6)}, 'nonzero', check=in_acc_fail('d')))
    # ---- W06 R-DIP event classification
    T.append(vt('W06a R-DIP: restart case classified event=restart', {'d': DIP}, {'d': dip_meas(RD_PEAK=11.0)}, 0,
                check=rdip_event('d', 'restart')))
    T.append(vt('W06b R-DIP: ride-through case classified event=rode_through', {'d': DIP}, {'d': dip_meas(restart=False, RD_PEAK=11.0)},
                0, check=rdip_event('d', 'rode_through')))
    return T


def design_tests():
    res = []
    for fn in ('pdu-uvlo-block.inc', 'pdu-uvlo-block-o3.inc'):
        t = (PKG / fn).read_text()
        ok = re.search(r'^XU26 EN_BUCK 0 0 OUTA_UV V5_OVP UVLO_TMUX1102', t, re.M) is not None
        res.append((f'D41 {fn}: direct VIN-OK loss -> EN pull-down U26 (SEL = OUTA_UV, unstretched) next to U22 (OUTA_D)', ok, ''))
    C = json.loads((PKG / 'test-cases-uvlo.json').read_text())['cases']
    need = [f'{p}dip0v-{d}-{cn}' for p in ('', 'o3-') for d in ('1us', '5us', '10us', '50us', '20ms') for cn in ('typ-ttyp', 'mbmin-tmin')]
    miss = [n for n in need if n not in C]
    res.append(('D42 us dips 0 V 1/5/10/50 us and 20 ms, C3 + O3, typ + mbmin', not miss, f'missing {miss[:6]}' if miss else len(need)))
    td = [n for n, c in C.items() if c.get('tdrv_en') == 0.0508]
    ok = any(n.startswith('o3-') for n in td) and any(not n.startswith('o3-') for n in td)
    res.append(('D43 TDRV_EN 50.8 ms conservative FET-rearm model cases (C3 + O3)', ok, sorted(td)))
    inc = PKG / 'pdu-tdrv-en.inc'
    res.append(('D43b pdu-tdrv-en.inc exists (EN_OVP held low until VIN-EN high for TDRV)', inc.exists() and 'TDRV' in inc.read_text(), ''))
    r180 = [n for n, c in C.items() if c.get('rdsc') == 180.0]
    res.append(('D44 RDSC 180 ohm exploratory decks (C3 + O3)', any(n.startswith('o3-') for n in r180) and
                any(not n.startswith('o3-') for n in r180), sorted(r180)))
    bad = [n for n, c in C.items() if c['kind'] in ('dip', 'dip2') and not c.get('regression')
           and (c.get('en_force_max') != 1e-6 or c.get('vgs_at_en_min') != 6.0)]
    res.append(('D45 every candidate dip case requests M3 (EN low <= 1 us) and M4 (VGS >= 6 V at EN rise)', not bad, bad[:5]))
    dk = PKG / 'decks' / 'uvlo-dip0v-5us-typ-ttyp.cir'
    t = dk.read_text() if dk.exists() else ''
    # Tur-5 RETARGET (UVLO-T5-01): OUTA_D only exists in the Tur-4 stretcher block. The candidate dip deck must carry the
    # same VGS/OUTA measurements plus the latch-state equivalent (QINH_MAX); OUTAD_MIN is required in the Tur-4 regression deck.
    t4 = PKG / 'decks' / 'uvlo-tur4-fpulse-1us-typ-ttyp.cir'
    t4 = t4.read_text() if t4.exists() else ''
    ok = (all(f'VGS_AT_EN_R{i}' in t for i in (1, 2, 3)) and 'VGS_AT_EN_RLAST' in t and 'OUTA_F2' in t and 'QINH_MAX' in t
          and 'OUTAD_MIN' in t4)
    res.append(('D46 dip deck measures VGS at every EN rise, OUTA falls and the latch state (Tur-4 regression deck: OUTA_D min)', ok, 'ok' if ok else 'missing'))
    reg = [n for n, c in C.items() if c.get('regression')]
    res.append(('D47 regressions kept (>= 9, all expect FAIL)', len(reg) >= 9 and all(C[n]['expect'] == 'FAIL' for n in reg), len(reg)))
    return res


def budget_tests():
    res = []
    BJ = json.loads((PKG / 'results' / 'uvlo-budget.json').read_text())
    sw = BJ.get('timer', {}).get('rdsc_sweep') or []
    rs = sorted(r.get('RDSC') for r in sw)
    res.append(('B41 RDSC sweep 100/150/180/220 ohm recorded', rs == [100.0, 150.0, 180.0, 220.0], rs))
    keys = ('i_peak_max', 't_dsc_max', 'v_rel_max', 'hold_min', 'hold_separation', 'meets_review_targets')
    ok = bool(sw) and all(all(k in r for k in keys) for r in sw)
    res.append(('B41b each sweep row: Ipk, t_dsc, V_rel, hold_min, hold separation, target verdict', ok, ''))
    tg = BJ.get('timer', {}).get('rdsc_review_targets') or {}
    ok = tg.get('i_peak_max') == 0.030 and tg.get('t_dsc_max') == 0.0055 and tg.get('hold_separation_min') == 0.0024 \
        and tg.get('v_rel_max') == 0.0535
    res.append(('B41c review targets recorded unchanged (Ipk <= 30 mA, t_dsc <= 5.5 ms, sep >= 2.4 ms, V_rel <= 53.5 mV)', ok, tg))
    O = BJ['o3_variant']['start_guarantee']
    terms = O['non_guaranteed_terms']
    acas = [t for t in terms if 'ACAS' in t['term']]
    ass = [t for t in acas if re.search(r'endurance|solder|drift', t['term'], re.I)]
    ok = len(ass) == 1 and ass[0]['unbounded'] is True and re.search(r'relative', ass[0]['term']) and re.search(r'absolute', ass[0]['term'])
    res.append(('B42 ACAS DF endurance/solder/drift (absolute + relative) = ONE unbounded group', bool(ok), [t['term'] for t in acas]))
    tcr = [t for t in acas if 'TCR' in t['term']]
    ok = len(tcr) == 1 and tcr[0]['unbounded'] is False and not re.search(r'endurance|solder|drift', tcr[0]['term'], re.I)
    res.append(('B42b grade-U relative TCR: separate datasheet-supported (bounded) term', ok, [t['term'] for t in tcr]))
    res.append(('B42c O3 unbounded terms = 4 (REF5040 long-term, REF5040 solder, TLV3202 Hint, ACAS DF group)',
                len(O['unbounded_terms']) == 4, O['unbounded_terms']))
    t = (PKG / 'decks' / 'uvlo-dip0v-5us-typ-ttyp.cir').read_text().upper()
    ok = all(f'.MEAS TRAN EN_LAG_F{k} TRIG V(OUTA_UV) VAL=2.5 FALL={k} TARG V(EN_BUCK) VAL=1.0 FALL={k}' in t for k in (1, 2))
    res.append(('D48 dip decks measure the direct OUTA fall -> EN fall lag EN_LAG_F1/F2 (1 us gate needs sub-us resolution)', ok, ''))
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
