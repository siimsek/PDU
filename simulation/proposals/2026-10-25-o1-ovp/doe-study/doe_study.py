#!/usr/bin/env python3
"""WP1 Tur-11 (WP1-T11-01 / WP1-T11-02 / UVLO-T5-04) EXPLORATION DOE - diagnostic only, NOTHING is adopted.

Exploration values only (review DOE points), NOT a BOM change; the candidate block (RPU10 = 10 ohm, no CGS slew cap,
no RAW snubber, latched behavioural U3) is unchanged. Acceptance decks, limits and results are NOT modified: every
variant is a temporary copy of an acceptance deck with ONE study change.

 A  turn-on slope only : RPU10 in {10,22,33,47,68,100} ohm x CGS10 (G_OVP-SRC_OVP) in {0,1n,2.2n,4.7n};
                         RPD10 (fast turn-off path) unchanged, no common resistor in the discharge path.
 B  RAW damping only   : series RC RAW -> Rsn -> Csn -> 0, Csn in {4.7,10,22} uF x Rsn in {1,2.2,4.7} ohm; gate drive
                         unchanged (RPU10 10 ohm). Rsn energy/peak current measured.
 C  combined           : only A x B pairs that each pass the preliminary screen (all screen decks complete, no
                         acceptance FAIL, no start-up false trip) - none if no single-axis candidate passes.
 U3 three-way          : (1) latched U3 (baseline model), (2) same power path, latch disabled (Btrip never sets
                         the latch -> current-limit / no breaker), (3) U3 bypassed (1 mohm VOUT -> O1_11V, no hidden
                         latch). Study-local subckt copies; simulation/pdu-behavioral.lib is READ only.
 NUM  numerical        : identical baseline-candidate decks with method=gear (acceptance setting) and method=trap,
                         same tmax 100 ns and tolerances, uniform over the whole screen set (not only aborting decks).

U3 set: c185 ESR 100 mohm typ/wchi (no c165 ESR 100 mohm acceptance deck exists -> c165 ESR 12.5 mohm used), s023 typ/wchi.
Screen set: the 4 ESL 2 nH decks + their ESL = 0 controls, s023 typ/wchi, startup-20v, startup-26v, no-false-trip.
Pass/fail of a variant uses the unchanged run_o1ovp.evaluate() acceptance checks of each deck.

Usage: PDU_NGSPICE=ngspice python3 doe_study.py [-j N] [--only A,B,C,U3,NUM]
       -> ../results/doe-study/doe-study-<parts>.json + logs. Exit 0 when it ran (data, not a gate); 2 on preparation error.
Behavioural models only; simulation != silicon / bench.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent; SIM = PKG.parent.parent
sys.path.insert(0, str(PKG)); import run_o1ovp as R
OUT = PKG / 'results' / 'doe-study'
ESL = ['buck-short-c165-esr12m5-esl2n-typ', 'buck-short-c165-esr12m5-esl2n-wchi',
       'buck-short-c185-esr12m5-esl2n-typ', 'buck-short-c185-esr12m5-esl2n-wchi']
SCREEN = ESL + [n.replace('-esl2n', '') for n in ESL] + ['efuse-ovp-s023-typ', 'efuse-ovp-s023-wchi', 'startup-20v',
                                                        'startup-26v', 'no-false-trip']
U3CASES = ['buck-short-c165-esr12m5-typ', 'buck-short-c165-esr12m5-wchi', 'buck-short-c185-esr100m-typ',
           'buck-short-c185-esr100m-wchi', 'efuse-ovp-s023-typ', 'efuse-ovp-s023-wchi']
RPU = ['10', '22', '33', '47', '68', '100']; CGS = ['0', '1n', '2.2n', '4.7n']
CSN = ['4.7u', '10u', '22u']; RSN = ['1', '2.2', '4.7']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXTRA = ('.meas tran DOE_RAW_MAX MAX V(RAW)\n'
         '.meas tran DOE_O1_MAX MAX V(O1_11V)\n'
         '.meas tran DOE_VOUT_MAX MAX V(VOUT)\n')   # MAX-only (cannot fail -> no spurious 'missing')
SNUB = ('* DOE-B RAW series-RC damping branch (study only)\nRsnDOE RAW SN_DOE {rsn}\nCsnDOE SN_DOE 0 {csn}\n'
        'Bpsn PSN_DOE 0 V=V(RAW,SN_DOE)*V(RAW,SN_DOE)/{rsn}\nBisn ISN_DOE 0 V=abs(V(RAW,SN_DOE))/{rsn}\n')
SNUB_MEAS = ('.meas tran DOE_ESN INTEG V(PSN_DOE)\n.meas tran DOE_PSN_MAX MAX V(PSN_DOE)\n'
             '.meas tran DOE_ISN_MAX MAX V(ISN_DOE)\n')

def base_text(name):
    c = R.CASES[name]; return c, (R.DECKS / c['ng_file']).read_text()

def efuse_variant(kind):
    """study-local copy of the baseline PDU_EFUSE subckt: 'nolatch' (latch never set) - READ-only use of the lib"""
    lib = (SIM / 'pdu-behavioral.lib').read_text()
    i = lib.index('.subckt PDU_EFUSE '); j = lib.index('.ends', i) + len('.ends')
    sub = lib[i:j]
    old = [l for l in sub.split('\n') if l.startswith('Btrip ')]; assert len(old) == 1
    sub = sub.replace(old[0], 'Btrip P4 latch I=-V(latch,P4)/100   ; DOE U3 variant 2: breaker latch disabled')
    return sub.replace('.subckt PDU_EFUSE ', '.subckt PDU_EFUSE_NOLATCH ', 1)

def make(name, tag, tmp, rpu='10', cgs='0', csn=None, rsn=None, method='gear', u3='latched'):
    c, t = base_text(name)
    d = Path(tmp) / tag; d.mkdir(parents=True, exist_ok=True)
    blk = (PKG / 'pdu-o1ovp-block.inc').read_text()
    assert blk.count('RPU10 PU_OVP G_OVP 10\n') == 1
    blk = blk.replace('RPU10 PU_OVP G_OVP 10\n', f'RPU10 PU_OVP G_OVP {rpu}\n' +
                      (f'CGS10DOE G_OVP SRC_OVP {cgs}\n' if cgs != '0' else ''))
    if csn: blk += SNUB.format(rsn=rsn, csn=csn)
    (d / 'block.inc').write_text(blk)
    efb = (PKG / 'pdu-efuse-block-o1ovp.inc').read_text()
    xu3 = [l for l in efb.split('\n') if l.startswith('XU3 ')]; assert len(xu3) == 1
    if u3 == 'nolatch':
        efb = efb.replace(xu3[0], xu3[0].replace(' PDU_EFUSE ', ' PDU_EFUSE_NOLATCH ')) + '\n' + efuse_variant('nolatch') + '\n'
    elif u3 == 'bypass':
        efb = efb.replace(xu3[0], '* DOE U3 variant 3: U3 bypassed (explicit 1 mohm VOUT -> O1_11V, no latch)\nRU3BYP VOUT O1_11V 1m')
    (d / 'efuse.inc').write_text(efb)
    assert t.count('.include ../pdu-o1ovp-block.inc\n') == 1, name
    ne = t.count('.include ../pdu-efuse-block-o1ovp.inc\n'); assert ne == 1 or (ne == 0 and u3 == 'latched'), name
    t = t.replace('.include ../pdu-o1ovp-block.inc\n', f'.include {d}/block.inc\n')
    t = t.replace('.include ../pdu-efuse-block-o1ovp.inc\n', f'.include {d}/efuse.inc\n')   # board decks: own U3 (baseline)
    t = t.replace('.include ../../../', f'.include {SIM}/').replace('.include ../', f'.include {PKG}/')
    assert t.count('method=gear') == 1, name
    t = t.replace('method=gear', f'method={method}')
    ex = EXTRA + (SNUB_MEAS if csn else '')
    assert '\n.end' in t; t = t.replace('\n.end', '\n' + ex + '.end', 1)
    deck = d / (R.DECKS / c['ng_file']).name; deck.write_text(t)
    return c, deck, d

def job(a):
    name, tag, kw, tmp = a
    c, deck, d = make(name, tag, tmp, **kw)
    r = R.run_deck('ng', os.environ.get('PDU_NGSPICE', 'ngspice'), deck, OUT / f'{name}.{tag}.ng.log', d)
    out = []
    if r['execution_pass'] and c['kind'] != 'reference':
        R.evaluate(name, c, r['measures'], lambda n, ok, dd: out.append((n, bool(ok), dd)))
    m = r['measures']
    acc = [f'{n}: {dd}' for n, ok, dd in out if R.category(c, n) == 'acceptance' and not ok]
    inp = m.get('info_startup_inp_min')   # the deck's own start-up comparator window (short 1-24 ms, ramp 1-13 ms)
    return dict(case=name, tag=tag, params=kw, completed=r['execution_pass'], seconds=r['seconds'], errors=r['errors'][:1],
                missing=r['missing'][:6], log=r['log'], log_sha256=r['log_sha256'], deck_sha256=r['deck_sha256'],
                source_deck_sha256=sha(R.DECKS / c['ng_file']),
                measures={k: v for k, v in m.items() if k.startswith('doe_') or k in R_KEYS},
                acceptance_fail=acc, startup_false_trip=(inp is not None and inp < 2.5))
R_KEYS = {'info_startup_inp_min', 'info_startup_vgs_fall_t', 'o1_global_peak', 'o1_peak', 'bus_peak', 'raw_peak', 'bus_normal_max', 'vgs_rec_min', 'vgs_post_min', 'o1_stable_max'}

def screen_ok(rows):
    return all(x['completed'] and not x['acceptance_fail'] and not x['startup_false_trip'] for x in rows)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('-j', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--only', default='A,B,C,U3,NUM'); a = ap.parse_args(); only = set(a.only.split(','))
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=PKG, capture_output=True, text=True).stdout.strip()
    res = dict(_status='WP1 Tur-11 EXPLORATION DOE - diagnostic only, NOT adopted; behavioural models; sim != silicon',
               git_head=head, started=time.strftime('%Y-%m-%d %H:%M:%S %z'), screen_cases=SCREEN, u3_cases=U3CASES,
               block_inc_sha256=sha(PKG / 'pdu-o1ovp-block.inc'), efuse_inc_sha256=sha(PKG / 'pdu-efuse-block-o1ovp.inc'),
               baseline_lib_sha256=sha(SIM / 'pdu-behavioral.lib'), lib_sha256=sha(PKG / 'pdu-o1ovp-behavioral.lib'))
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(a.j) as ex:
        jobs = []
        if 'A' in only:
            jobs += [(n, f'A-rpu{r}-cgs{g}', dict(rpu=r, cgs=g), tmp) for r in RPU for g in CGS for n in SCREEN]
        if 'B' in only:
            jobs += [(n, f'B-csn{c}-rsn{r}', dict(csn=c, rsn=r), tmp) for c in CSN for r in RSN for n in SCREEN]
        if 'NUM' in only:
            jobs += [(n, f'NUM-{m}', dict(method=m), tmp) for m in ('gear', 'trap') for n in SCREEN]
        if 'U3' in only:
            jobs += [(n, f'U3-{v}', dict(u3=v), tmp) for v in ('latched', 'nolatch', 'bypass') for n in U3CASES]
        rows = list(ex.map(job, jobs))
        by = {}
        for x in rows: by.setdefault(x['tag'], []).append(x)
        res['variants'] = {t: dict(screen_pass=screen_ok(v), completed=sum(x['completed'] for x in v), n=len(v),
                                   acceptance_fail=sum(bool(x['acceptance_fail']) for x in v),
                                   startup_false_trip=sum(x['startup_false_trip'] for x in v)) for t, v in by.items()}
        if 'C' in only:
            pa = [t for t, s in res['variants'].items() if t.startswith('A-') and s['screen_pass']]
            pb = [t for t, s in res['variants'].items() if t.startswith('B-') and s['screen_pass']]
            res['C_candidates'] = dict(A=pa, B=pb)
            cj = []
            for ta in pa:
                r_, g_ = re.match(r'A-rpu(.+)-cgs(.+)', ta).groups()
                for tb_ in pb:
                    c_, s_ = re.match(r'B-csn(.+)-rsn(.+)', tb_).groups()
                    cj += [(n, f'C-rpu{r_}-cgs{g_}-csn{c_}-rsn{s_}', dict(rpu=r_, cgs=g_, csn=c_, rsn=s_), tmp) for n in SCREEN]
            crow = list(ex.map(job, cj)); rows += crow
            for x in crow: by.setdefault(x['tag'], []).append(x)
            for t in {x['tag'] for x in crow}:
                v = by[t]; res['variants'][t] = dict(screen_pass=screen_ok(v), completed=sum(x['completed'] for x in v), n=len(v),
                                                       acceptance_fail=sum(bool(x['acceptance_fail']) for x in v),
                                                       startup_false_trip=sum(x['startup_false_trip'] for x in v))
    res['rows'] = rows; res['finished'] = time.strftime('%Y-%m-%d %H:%M:%S %z')
    for t, s in sorted(res['variants'].items()):
        print(f"{t:34s} pass={s['screen_pass']!s:5s} done={s['completed']}/{s['n']} accFAIL={s['acceptance_fail']} falsetrip={s['startup_false_trip']}")
    (OUT / f"doe-study-{'-'.join(sorted(only))}.json").write_text(json.dumps(res, indent=1) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
