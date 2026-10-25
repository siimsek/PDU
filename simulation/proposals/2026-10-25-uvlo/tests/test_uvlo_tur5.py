#!/usr/bin/env python3
"""WP2 Tur-5 (ChatGPT combined review 6400663804, WP2 part) tests, written BEFORE the fixes (first run on a543883).
Exit 0 = every test behaves as required, 1 = at least one test failed. Stdlib only (+ ngspice for the two unit benches).

V51 (UVLO-T5-03) M3 fail-closed: when VIN-OK is lost (OUTA fall) while EN is high, the direct TRIG/TARG lag EN_LAG_F<k>
    is REQUIRED; missing / ngspice 'failed' / NaN / +-Inf / negative / inconsistent with the printed absolute times ->
    FAIL even if the 6-digit absolute difference is <= 1 us. Not applicable when EN was already low or OUTA never fell.
V52 (UVLO-T5-07) M1 printed-time resolution: an EN rise passes only if (t_EN - t_OUTA) - (half_ulp6(t_EN) +
    half_ulp6(t_OUTA)) >= 60 ms; an interval that is >= 60 ms only within the print resolution FAILS. The stimulus-only
    seq delay schema stays exact and inclusive (60.000 ms -> PASS).
V53 (UVLO-T5-03) acceptance mode requires --run-id (or UVLO_RUN_ID); no run id -> exit 2 (provenance); --historical is
    the explicit review mode (never reported as acceptance; summary.mode = 'historical').
V54 (UVLO-T5-03) the (disabled) workflow YAML runs the Tur-4 and Tur-5 test files.
D5x design (UVLO-T5-01/02/05): reset-dominant latch U27 (SN74LVC1G74, PRE = OUTA_UV) + U29 release comparator; OUTA_UV
    drives only high-impedance inputs and RTT (no diode / RDIS / stretcher load); U22/U24 (TMUX1101) follow the latch;
    U28 gate-ready EN qualifier (VGS >= 7 V for >= 5 ms, behavioural, part TBD); forced OUTA pulse matrix 1 us .. 20 ms,
    double forced pulses, double VIN us dips; no-reset forced-pulse regressions 1 .. 100 us and Tur-4 stretcher
    regressions (expect FAIL); regression blocks unchanged.
L5x ngspice unit benches: latch truth table (incl. PRE+CLR low -> Q high) and gate-ready qualification / fast drop.
B5x budget: latch release level above the CTT equilibrium while U24 holds it, ramp after release >= 60 ms (65 ms target
    reported), VIN-OK -> EN <= 300 ms, discharge peak current recorded against the review target.
Usage: python3 tests/test_uvlo_tur5.py [path/to/package_dir]
"""
import importlib.util, json, sys, os, re, subprocess, tempfile, shutil
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent
REPO = PKG.parent.parent.parent
os.environ.pop('UVLO_RUN_ID', None)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T2 = load('t2_helpers_t5', PKG / 'tests' / 'test_uvlo_tur2.py')
vt0, dip_meas, DIP = T2.vt, T2.dip_meas, T2.DIP
T4 = load('t4_helpers_t5', PKG / 'tests' / 'test_uvlo_tur4.py')
seq_meas, SEQ, in_acc_fail = T4.seq_meas, T4.SEQ, T4.in_acc_fail
RID = ['--run-id', 'run-123']


def vt(name, cases, logs, want, failed=None, argv=RID, check=None):
    return vt0(name, cases, logs, want, failed=failed, argv=argv, check=check)


def summ(key, want):
    def f(out):
        v = out.get('summary', {}).get(key)
        return v == want, f'{key}={v!r}'
    return f


def prov_has(txt):
    def f(out):
        pe = out.get('summary', {}).get('provenance_errors') or []
        return any(txt in x for x in pe), f'provenance_errors={pe}'
    return f


def verifier_tests():
    T = []
    DIPF = dict(DIP, en_force_max=1e-6, vgs_at_en_min=6.0)

    def dipf(**o):
        m = dip_meas(); m.update(OUTA_F1=0.2601, EN_F1=0.2601 + 0.4e-6, EN_LAG_F1=0.4e-6, VGS_AT_EN_R1=12.0, VGS_AT_EN_R2=12.0)
        m.update(o); return m
    T.append(vt('V51a control: EN_LAG_F1 0.4 us, consistent with the printed times -> exit 0', {'d': DIPF}, {'d': dipf()}, 0))
    m = dipf(); m.pop('EN_LAG_F1')
    T.append(vt('V51b EN_LAG_F1 missing, printed |EN_F1-OUTA_F1| 0.4 us -> exit != 0 (direct lag required)', {'d': DIPF}, {'d': m},
                'nonzero', check=in_acc_fail('d')))
    m = dipf(OUTA_F1=0.275436, EN_F1=0.275436); m.pop('EN_LAG_F1')
    T.append(vt('V51c EN_LAG_F1 missing, printed times identical (0 us) -> exit != 0', {'d': DIPF}, {'d': m}, 'nonzero',
                check=in_acc_fail('d')))
    m = dipf(OUTA_F1=0.275436, EN_F1=0.275436); m.pop('EN_LAG_F1')
    T.append(vt('V51d EN_LAG_F1 ngspice failed -> exit != 0', {'d': DIPF}, {'d': m}, 'nonzero', failed={'d': ['EN_LAG_F1']},
                check=in_acc_fail('d')))
    for val, lab in ((float('nan'), 'NaN'), (float('inf'), '+Inf'), (float('-inf'), '-Inf'), (-0.2e-6, 'negative')):
        T.append(vt(f'V51e EN_LAG_F1 {lab}, printed times identical -> exit != 0', {'d': DIPF},
                    {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275436, EN_LAG_F1=val)}, 'nonzero', check=in_acc_fail('d')))
    T.append(vt('V51f EN_LAG_F1 0.3 us inconsistent with 5 us printed difference -> exit != 0', {'d': DIPF},
                {'d': dipf(OUTA_F1=0.275436, EN_F1=0.275441, EN_LAG_F1=0.3e-6)}, 'nonzero', check=in_acc_fail('d')))
    m = dipf(); [m.pop(k) for k in ('OUTA_F1', 'EN_F1', 'EN_LAG_F1', 'OUTA_R2', 'OUTA_RLAST', 'EN_R2', 'VGS_AT_EN_R2')]
    T.append(vt('V51g ride-through (OUTA never fell) -> no lag required, exit 0', {'d': DIPF}, {'d': m}, 0,
                failed={'d': ['OUTA_F1', 'EN_F1', 'EN_R2', 'EN_LAG_F1']}))
    m = dipf(EN_F1=0.2600, OUTA_F1=0.26008); m.pop('EN_LAG_F1')
    T.append(vt('V51h EN already low before the OUTA fall -> M3 not applicable, no lag required, exit 0', {'d': DIPF}, {'d': m}, 0))
    # ---- V52 M1 print resolution (half_ulp6(0.26) = half_ulp6(0.32) = 0.5 us -> 1 us)
    for d, want in ((0.0600005, 'nonzero'), (0.0600009, 'nonzero'), (0.060002, 0), (0.0605, 0)):
        T.append(vt(f'V52 dip restart {d*1e3:.4f} ms after OUTA_R2 (printed, +-1 us) -> exit {want}', {'d': DIP},
                    {'d': dip_meas(delay=d)}, want))
    T.append(vt('V52s seq stimulus-only configured delay 60.000 ms stays inclusive -> exit 0', {'q': dict(SEQ, delay=0.060)},
                {'q': seq_meas()}, 0))
    # ---- V53 acceptance mode requires a run id
    T.append(vt('V53a no --run-id, no UVLO_RUN_ID -> exit 2 (acceptance needs a run id)', {'d': DIP}, {'d': dip_meas()}, 2, argv=[],
                check=prov_has('--run-id')))
    T.append(vt('V53b --historical -> exit 0, summary.mode = historical', {'d': DIP}, {'d': dip_meas()}, 0, argv=['--historical'],
                check=summ('mode', 'historical')))
    T.append(vt('V53c --run-id run-123 -> exit 0, summary.mode = acceptance', {'d': DIP}, {'d': dip_meas()}, 0,
                check=summ('mode', 'acceptance')))
    T.append(vt('V53d --historical together with --run-id -> exit 2 (ambiguous mode)', {'d': DIP}, {'d': dip_meas()}, 2,
                argv=['--historical', '--run-id', 'run-123']))
    return T


def block_elems(text):
    els = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s[0] in '*.+':
            continue
        els.append(s.split())
    return els


def design_tests():
    res = []
    lib = (PKG / 'pdu-uvlo-behavioral.lib').read_text()
    for fn in ('pdu-uvlo-block.inc', 'pdu-uvlo-block-o3.inc'):
        t = (PKG / fn).read_text(); els = block_elems(t)
        users = sorted({e[0] for e in els if 'OUTA_UV' in e[1:] and not e[0].startswith('B') or (e[0].startswith('B') and 'OUTA_UV' in ' '.join(e))})
        ok = set(users) <= {'XU20A', 'XU21', 'XU26', 'XU27', 'RTT'} and 'XU27' in users
        res.append((f'D51 {fn}: OUTA_UV drives only U20A out, U21/U26 SEL, U27 PRE and RTT (no diode/RDIS/stretcher load)', ok, users))
        x27 = [e for e in els if e[0] == 'XU27']
        ok = len(x27) == 1 and x27[0][1] == 'OUTA_UV' and 'UVLO_LVC1G74' in x27[0]
        res.append((f'D52 {fn}: U27 SN74LVC1G74 reset-dominant latch, PRE = OUTA_UV', ok, x27))
        x29 = [e for e in els if e[0] == 'XU29']
        ok = len(x29) == 1 and x29[0][1] == 'T_UV' and x29[0][5] == x27[0][2] if x27 and x29 else False
        res.append((f'D52b {fn}: U29 release comparator (CTT < V_CLR) drives the latch CLR', ok, x29))
        q = x27[0][3] if x27 else None
        x22 = [e for e in els if e[0] == 'XU22']; x24 = [e for e in els if e[0] == 'XU24']
        ok = bool(q) and len(x22) == 1 and x22[0][1:5] == ['EN_BUCK', '0', '0', q] and 'UVLO_TMUX1101' in x22[0] \
            and len(x24) == 1 and x24[0][4] == q and 'UVLO_TMUX1101' in x24[0]
        res.append((f'D52c {fn}: U22 (EN->GND) and U24 (CTT discharge) TMUX1101 follow the latch output', ok, (x22, x24)))
        ok = not any(e[0] in ('RST', 'CST', 'DST', 'DST2', 'DTT', 'RDIS', 'Bilkd') for e in els)
        res.append((f'D51b {fn}: Tur-3/4 stretcher + DTT/RDIS fast path removed from the candidate', ok, ''))
        x28 = [e for e in els if e[0] == 'XU28']; g = [e for e in els if 'UVLO_GRDY' in e]
        ok = len(x28) == 1 and x28[0][1:5] == ['EN_BUCK', '0', '0', 'GRDY_UV'] and len(g) == 1 and g[0][3] == 'GRDY_UV'
        res.append((f'D53 {fn}: U28 gate-ready EN qualifier (EN low until GRDY)', ok, (x28, g)))
        x26 = [e for e in els if e[0] == 'XU26']
        res.append((f'D53b {fn}: U26 direct OUTA_UV -> EN pull-down kept', len(x26) == 1 and x26[0][4] == 'OUTA_UV', x26))
    ok = all(s in lib for s in ('.subckt UVLO_LVC1G74', '.subckt UVLO_TMUX1101', '.subckt UVLO_GRDY'))
    res.append(('D54 lib: UVLO_LVC1G74 / UVLO_TMUX1101 / UVLO_GRDY models present', ok, ''))
    m = re.search(r'\.subckt UVLO_GRDY[^\n]*', lib)
    ok = bool(m) and re.search(r'VRDY=7(\.0)?\b', m.group(0)) and re.search(r'TQ=5m\b', m.group(0))
    res.append(('D54b gate-ready default VGS >= 7.0 V qualified for 5 ms', bool(ok), m.group(0) if m else ''))
    for fn in ('pdu-uvlo-block-noreset.inc', 'pdu-uvlo-block-noreset-o3.inc'):
        t = (PKG / fn).read_text()
        ok = 'RDIS DTK_UV OUTA_UV 100' in t and 'XU22 EN_BUCK 0 0 OUTA_UV' in t and 'XU27' not in t and 'XU28' not in t
        res.append((f'D55 {fn}: Tur-2 regression block unchanged (no latch / gate-ready)', ok, ''))
    for fn in ('pdu-uvlo-block-tur4.inc', 'pdu-uvlo-block-tur4-o3.inc'):
        p = PKG / fn; t = p.read_text() if p.exists() else ''
        ok = 'DST OUTA_D OUTA_UV UVLO_BAT54' in t and 'XU26 EN_BUCK 0 0 OUTA_UV' in t and 'XU27' not in t
        res.append((f'D55b {fn}: Tur-4 stretcher block kept as regression', ok, ''))
    C = json.loads((PKG / 'test-cases-uvlo.json').read_text())['cases']
    ws = ('1us', '5us', '10us', '50us', '100us', '200us', '225us', '250us', '300us', '20ms')
    need = [f'{p}fpulse-{w}-{cn}' for p in ('', 'o3-') for w in ws for cn in ('typ-ttyp', 'mbmin-tmin')]
    miss = [n for n in need if n not in C]
    bad = [n for n in need if n in C and (C[n].get('expect') != 'PASS' or not C[n].get('forced_outa') or C[n].get('en_force_max') != 1e-6
                                          or C[n].get('vgs_at_en_min') != 6.0)]
    res.append(('D56 forced OUTA pulse matrix 1 us .. 20 ms, C3 + O3, typ + mbmin, PASS + M3/M4', not miss and not bad, (miss[:4], bad[:4])))
    need = [f'{p}fpulse2-{w}-gap{g}-{cn}' for p in ('', 'o3-') for w in ('10us', '300us') for g in ('50us', '30ms') for cn in ('typ-ttyp', 'mbmin-tmin')]
    miss = [n for n in need if n not in C]
    res.append(('D56b double forced OUTA pulses (10/300 us, gap 50 us / 30 ms), C3 + O3', not miss, miss[:4]))
    need = [f'{p}dbldip0v-{w}-gap{g}-{cn}' for p in ('', 'o3-') for w, g in (('50us', '100us'), ('50us', '30ms'), ('300us', '100us'))
            for cn in ('typ-ttyp', 'mbmin-tmin')]
    miss = [n for n in need if n not in C]
    res.append(('D56c double VIN us dips (50 us gap 100 us / 30 ms, 300 us gap 100 us), C3 + O3', not miss, miss[:4]))
    need = [f'{p}noreset-fpulse-{w}-typ-ttyp' for p in ('', 'o3-') for w in ('1us', '5us', '10us', '50us', '100us')]
    miss = [n for n in need if n not in C]
    bad = [n for n in need if n in C and not (C[n].get('regression') and C[n].get('expect') == 'FAIL')]
    res.append(('D57 no-reset forced-pulse regressions 1/5/10/50/100 us (C3 + O3, expect FAIL)', not miss and not bad, (miss[:4], bad)))
    need = [f'{p}tur4-fpulse-{w}-typ-ttyp' for p in ('', 'o3-') for w in ('1us', '50us')]
    miss = [n for n in need if n not in C]
    bad = [n for n in need if n in C and not (C[n].get('regression') and C[n].get('expect') == 'FAIL')]
    res.append(('D57b Tur-4 stretcher forced-pulse regressions (C3 + O3, expect FAIL)', not miss and not bad, (miss, bad)))
    dk = PKG / 'decks' / 'uvlo-fpulse-1us-typ-ttyp.cir'
    t = dk.read_text() if dk.exists() else ''
    ok = 'Bfp OUTA_UV 0' in t and 'EN_LAG_F1' in t and 'QINH' in t.upper()
    res.append(('D58 forced-pulse deck: OUTA_UV pull-down injection, EN_LAG and latch instrumentation', ok, ''))
    wf = (REPO / '.github' / 'workflows' / 'proposal-ngspice.yml').read_text()
    ok = 'python3 tests/test_uvlo_tur4.py' in wf and 'python3 tests/test_uvlo_tur5.py' in wf
    res.append(('V54 workflow YAML (disabled) runs tests/test_uvlo_tur4.py and tests/test_uvlo_tur5.py', ok, ''))
    return res


def ngspice():
    for c in (os.environ.get('PDU_NGSPICE'), shutil.which('ngspice')):
        if c and Path(c).exists():
            return c
    return None


def run_bench(text):
    ng = ngspice()
    if not ng:
        return None, 'ngspice not found'
    d = Path(tempfile.mkdtemp(prefix='uvlo-t5-'))
    try:
        (d / 'b.cir').write_text(text)
        r = subprocess.run([ng, '-b', '-D', 'ngbehavior=ltpsa', 'b.cir'], cwd=d, capture_output=True, text=True, timeout=300)
        m = {}
        for ln in (r.stdout + r.stderr).splitlines():
            mm = re.match(r'^\s*([a-z0-9_]+)\s*=\s*([-+0-9.eE]+)', ln)
            if mm:
                m[mm.group(1).upper()] = float(mm.group(2))
        return m, r.returncode
    finally:
        shutil.rmtree(d, ignore_errors=True)


def unit_tests():
    res = []
    lib = str(PKG / 'pdu-uvlo-behavioral.lib')
    if '.subckt UVLO_LVC1G74' not in Path(lib).read_text():
        return [('L51 latch truth table (ngspice)', False, 'UVLO_LVC1G74 missing'), ('L52 gate-ready bench (ngspice)', False, 'UVLO_GRDY missing')]
    # PRE/CLR sequence (1 us steps): (P,C) = (0,1) (1,1) (1,0) (1,1) (0,1) (0,0) (1,0) ; expected Q = H H L L H H L
    seq = [(0, 1), (1, 1), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0)]
    def pwl(ix):
        s = '0 %g' % (5 * seq[0][ix])
        for i in range(1, len(seq)):
            s += ' %gu %g %gu %g' % (i, 5 * seq[i - 1][ix], i + 0.01, 5 * seq[i][ix])
        return s
    b = (f'* latch truth table\n.include {lib}\nVCC VCC 0 5\nVP P 0 PWL({pwl(0)})\nVC C 0 PWL({pwl(1)})\n'
         'XL P C Q QN VCC 0 UVLO_LVC1G74\nRLQ Q 0 100k\nRLN QN 0 100k\n.tran 1n 7u 0 5n uic\n'
         + ''.join(f'.meas tran Q{i} FIND V(Q) AT={i + 0.9}u\n.meas tran QN{i} FIND V(QN) AT={i + 0.9}u\n' for i in range(len(seq))) + '.end\n')
    m, rc = run_bench(b)
    want = [1, 1, 0, 0, 1, 1, 0]; wqn = [0, 0, 1, 1, 0, 1, 1]
    if m is None:
        res.append(('L51 latch truth table (ngspice)', False, rc))
    else:
        got = [m.get(f'Q{i}') for i in range(len(seq))]; gqn = [m.get(f'QN{i}') for i in range(len(seq))]
        ok = all(g is not None and (g > 4.5 if w else g < 0.5) for g, w in zip(got, want)) and \
            all(g is not None and (g > 4.5 if w else g < 0.5) for g, w in zip(gqn, wqn))
        res.append(('L51 latch truth table incl. PRE+CLR low -> Q = QN = H (preset dominates the inhibit)', ok, (got, gqn)))
    b = (f'* gate-ready bench\n.include {lib}\nVCC VCC 0 5\nVS S 0 0\n'
         'VG G 0 PWL(0 0 1m 0 1.01m 10 20m 10 20.001m 5 30m 5 30.01m 6.9 50m 6.9)\n'
         'XG G S GRDY VCC 0 UVLO_GRDY\nRL GRDY 0 100k\n.tran 1u 50m 0 1u uic\n'
         '.meas tran TR WHEN V(GRDY)=2.5 RISE=1\n.meas tran TF WHEN V(GRDY)=2.5 FALL=1\n'
         '.meas tran GMAX_LATE MAX V(GRDY) FROM=30.5m TO=50m\n.end\n')
    m, rc = run_bench(b)
    if m is None:
        res.append(('L52 gate-ready bench (ngspice)', False, rc))
    else:
        tr, tf, gl = m.get('TR'), m.get('TF'), m.get('GMAX_LATE')
        ok = tr is not None and 0.00599 <= tr <= 0.0062 and tf is not None and 0.020 <= tf <= 0.020050 and gl is not None and gl < 0.5
        res.append(('L52 gate-ready: rises 5 ms after VGS >= 7 V, falls <= 50 us after VGS loss, 6.9 V never qualifies', ok, (tr, tf, gl)))
    return res


def budget_tests():
    res = []
    BJ = json.loads((PKG / 'results' / 'uvlo-budget.json').read_text())
    L = BJ.get('timer', {}).get('latch') or {}
    ok = bool(L) and L.get('v_eq_max', 9) < L.get('v_clr_min', 0) and L.get('release_margin_V', -1) > 0
    res.append(('B51 latch release level V_CLR,min above the CTT equilibrium while U24 holds it (no deadlock)', ok,
                {k: L.get(k) for k in ('v_eq_max', 'v_clr_min', 'v_clr_max', 'release_margin_V')}))
    ok = L.get('t_after_release_min', 0) >= 0.060 and 't_target_65ms_margin_s' in L
    res.append(('B52 ramp after latch release >= 60 ms (65 ms target margin reported)', ok, (L.get('t_after_release_min'), L.get('t_target_65ms_margin_s'))))
    ok = 0 < L.get('t_vinok_to_en_max', 1) <= 0.300
    res.append(('B53 VIN-OK -> EN max (discharge + ramp + gate-ready) <= 300 ms', ok, L.get('t_vinok_to_en_max')))
    ok = 'i_peak_max' in L and L.get('i_peak_review_target') == 0.030 and isinstance(L.get('i_peak_target_met'), bool)
    res.append(('B54 discharge peak current vs the unchanged 30 mA review target recorded', ok, (L.get('i_peak_max'), L.get('i_peak_target_met'))))
    return res


def main():
    rows = verifier_tests() + design_tests() + unit_tests() + budget_tests()
    for n, ok, d in rows:
        print(('OK  ' if ok else 'BAD ') + n + '  -> ' + str(d)[:300])
    bad = sum(1 for _, ok, _ in rows if not ok)
    print(f'{len(rows) - bad}/{len(rows)} OK')
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
