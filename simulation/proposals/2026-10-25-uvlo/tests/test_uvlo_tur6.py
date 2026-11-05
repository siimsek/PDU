#!/usr/bin/env python3
"""WP2 Tur-6 (ChatGPT combined review 6416795114, WP2 part) tests, written BEFORE the fixes (first run on 927d7cd).
Exit 0 = every test behaves as required, 1 = at least one test failed. Stdlib only.

V61 (UVLO-T6-01) M3 event order / boundary: direct lag 0.999 us PASS, 1.000 us PASS (inclusive), 1.001 us FAIL;
    0 us (coincident) PASS; ANY negative direct lag (EN fell before the VIN-OK loss) FAILS - causality not proven
    (Tur-5 accepted -0.1 us .. 0 as 'coincident within one solver step'; withdrawn, stricter); missing/NaN/+-Inf FAIL.
V62 (UVLO-T6-04) R-DIP report: the screen metric is labelled as the bus TRANSIENT peak (RD_PEAK = MAX V(VOUT)), NOT the
    H2 stable-window limit; the O1 transient peak RD_PEAK_O1 is published per case and checked separately against the
    12.0 V instantaneous O1 limit (o1_instant_status PASS / FAIL / UNDETERMINED, never PASS when missing).
N61 (UVLO-T6-02) num_study measurement kinds come from the .meas syntax, not from the name: WHEN / TRIG-TARG / INTEG of an
    indicator -> time; FIND / MAX / MIN / AVG / PP -> voltage (T_AT_DIP_END = FIND V(T_UV) is a voltage).
N62 (UVLO-T6-02) num_study tmax is applied uniformly: every deck's .tran tmax is replaced by the study tmax (default 100 ns).
Usage: python3 tests/test_uvlo_tur6.py [path/to/package_dir]
"""
import importlib.util, math, sys, os
from pathlib import Path

PKG = Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path(__file__).absolute().parent.parent
os.environ.pop('UVLO_RUN_ID', None)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T2 = load('t2_helpers_t6', PKG / 'tests' / 'test_uvlo_tur2.py')
vt0, dip_meas, DIP = T2.vt, T2.dip_meas, T2.DIP
T4 = load('t4_helpers_t6', PKG / 'tests' / 'test_uvlo_tur4.py')
in_acc_fail = T4.in_acc_fail
RID = ['--historical']  # evaluate numerical gates, not a fake acceptance run


def vt(name, cases, logs, want, failed=None, check=None):
    return vt0(name, cases, logs, want, failed=failed, argv=RID, check=check)


def rd_case(name, pred, label):
    def f(out):
        v = ((out.get('summary', {}).get('provisional_rdip_screen') or {}).get('cases') or {}).get(name) or {}
        return pred(v), f'{label}: {v!r}'[:300]
    return f


def rd_summary(pred, label):
    def f(out):
        v = out.get('summary', {}).get('provisional_rdip_screen') or {}
        return pred(v), f'{label}: metric={v.get("metric")!r}'[:300]
    return f


def verifier_tests():
    T = []
    DIPF = dict(DIP, en_force_max=1e-6, vgs_at_en_min=6.0)

    def dipf(**o):
        m = dip_meas(); m.update(OUTA_F1=0.2601, EN_F1=0.260101, EN_LAG_F1=1.0e-6, VGS_AT_EN_R1=12.0, VGS_AT_EN_R2=12.0)
        m.update(o); return m
    for lag, want in ((0.999e-6, 0), (1.000e-6, 0), (1.001e-6, 'nonzero')):
        T.append(vt(f'V61 direct EN_LAG_F1 {lag*1e6:.3f} us -> exit {want}', {'d': DIPF}, {'d': dipf(EN_LAG_F1=lag)}, want,
                    check=in_acc_fail('d') if want != 0 else None))
    T.append(vt('V61z EN_LAG_F1 0 us (coincident), printed times identical -> exit 0', {'d': DIPF},
                {'d': dipf(EN_F1=0.2601, EN_LAG_F1=0.0)}, 0))
    for lag in (-1e-12, -0.04e-6, -0.0305e-6):
        T.append(vt(f'V61n EN_LAG_F1 {lag*1e6:.6f} us (EN before VIN-OK loss, causality unproven) -> exit != 0', {'d': DIPF},
                    {'d': dipf(EN_F1=0.2601, EN_LAG_F1=lag)}, 'nonzero', check=in_acc_fail('d')))
    for val, lab in ((float('nan'), 'NaN'), (float('inf'), '+Inf'), (float('-inf'), '-Inf')):
        T.append(vt(f'V61f EN_LAG_F1 {lab} -> exit != 0', {'d': DIPF}, {'d': dipf(EN_LAG_F1=val)}, 'nonzero', check=in_acc_fail('d')))
    # ---- V62 R-DIP metric labelling and O1 transient peak
    base = dict(RD_PEAK=11.30, RD_T_ABOVE=0.2e-3, RD_ABOVE_FIRST=0.2603, RD_ABOVE_LAST=0.2605)
    T.append(vt('V62a R-DIP summary labels the metric as bus transient peak, not H2', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK_O1=11.2, **base)}, 0,
                check=rd_summary(lambda v: 'transient' in str(v.get('metric', '')).lower() and 'not h2' in str(v.get('metric', '')).lower(),
                                 'metric')))
    T.append(vt('V62b R-DIP case publishes peak_bus and peak_o1, O1 11.2 V <= 12.0 -> o1_instant_status PASS', {'d': DIP},
                {'d': dip_meas(restart=False, RD_PEAK_O1=11.2, **base)}, 0,
                check=rd_case('d', lambda v: v.get('peak_bus') == 11.30 and v.get('peak_o1') == 11.2 and v.get('o1_instant_status') == 'PASS',
                              'case')))
    T.append(vt('V62c R-DIP O1 transient 12.05 V > 12.0 -> o1_instant_status FAIL (acceptance also FAILs on O1_GLOBAL_PEAK)',
                {'d': DIP}, {'d': dip_meas(restart=False, RD_PEAK_O1=12.05, O1_GLOBAL_PEAK=12.05, **base)}, 'nonzero',
                check=rd_case('d', lambda v: v.get('o1_instant_status') == 'FAIL', 'case')))
    T.append(vt('V62d R-DIP RD_PEAK_O1 missing -> o1_instant_status UNDETERMINED (never PASS)', {'d': DIP},
                {'d': dip_meas(restart=False, **base)}, 0,
                check=rd_case('d', lambda v: v.get('o1_instant_status') == 'UNDETERMINED', 'case')))
    return T


def num_tests():
    res = []
    try:
        ns = load('num_study_t6', PKG / 'num_study.py')
    except Exception as e:
        return [('N6x num_study importable', False, repr(e))]
    deck = ('.tran 100n 0.556093 0 1u uic\n'
            '.meas tran EN_R1 WHEN V(EN_BUCK)=1.0 RISE=1\n'
            '.meas tran EN_LAG_F1 TRIG V(OUTA_UV) VAL=2.5 FALL=1 TARG V(EN_BUCK) VAL=1.0 FALL=1\n'
            '.meas tran RD_T_ABOVE INTEG V(M_RDB) FROM=0.26 TO=0.5\n'
            '.meas tran T_AT_DIP_END FIND V(T_UV) AT=0.170539\n'
            '.meas tran BUS_GLOBAL_MAX MAX V(VOUT) FROM=0 TO=0.556093\n'
            '.meas tran PRE_RAW_AVG AVG V(RAW) FROM=0.2 TO=0.26\n'
            '.meas tran PRE_EN_MIN MIN V(EN_BUCK) FROM=0.2 TO=0.26\n'
            '.meas tran RIP PP V(VOUT) FROM=0.2 TO=0.26\n')
    want = dict(en_r1='time', en_lag_f1='time', rd_t_above='time', t_at_dip_end='voltage', bus_global_max='voltage',
                pre_raw_avg='voltage', pre_en_min='voltage', rip='voltage')
    f = getattr(ns, 'meas_kinds', None)
    got = f(deck) if f else None
    res.append(('N61 num_study.meas_kinds() classifies from .meas syntax (T_AT_DIP_END = FIND V -> voltage)', got == want, got))
    g = getattr(ns, 'set_tmax', None)
    out = g(deck, '100n') if g else ''
    ok = '.tran 100n 0.556093 0 100n uic' in out and out.count('.tran') == 1
    res.append(('N62 num_study.set_tmax() replaces the .tran tmax uniformly (1u -> 100n)', ok, out.splitlines()[0] if out else None))
    ok = bool(g) and all(g(d, '100n').splitlines()[0] == '.tran 100n 0.3 0 100n uic' for d in ('.tran 100n 0.3 0 1u uic\n', '.tran 100n 0.3 0 10u uic\n'))
    res.append(('N62b set_tmax independent of the original tmax value', ok, None))
    return res


def main():
    res = verifier_tests() + num_tests()
    bad = [r for r in res if not r[1]]
    for n, ok, d in res:
        print(('OK   ' if ok else 'FAIL ') + n + (f'  [{d}]' if d is not None and not ok else ''))
    print(f'{len(res) - len(bad)}/{len(res)} OK')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
