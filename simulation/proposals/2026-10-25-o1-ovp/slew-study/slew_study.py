#!/usr/bin/env python3
"""WP2 OPTION EXPLORATION (diagnostic, NOT adopted): controlled-slew OVP turn-on via a larger PU series resistor.

Question (ChatGPT tur-2, P0-03): the ideal hard turn-on (PU 1.69 A peak through RPU10 = 10 ohm into ~10 nF lumped CGS)
rings RAW through the 2 nH bank ESL (~7.8 MHz, RAW ~13.3 V), the comparator chatters and ngspice collapses the timestep.
Does a slower turn-on (RPU10 = 100 / 330 / 1000 ohm; PD path unchanged -> turn-off / O1 budget unaffected) remove the
ringing, the start-up trip and the non-convergence, and what does it cost (turn-on time)?

Only RPU10 changes (in a temporary copy of pdu-o1ovp-block.inc); decks are the current acceptance decks plus 3 extra
.meas lines (turn-on time, RAW peak around turn-on). The candidate keeps RPU10 = 10 ohm; any change is a WP2 decision
that needs this comparison + bench (B-test) + gate-driver datasheet limits (PU sink capability is not a concern; the
resistor dissipates <= Qg x V_BST per turn-on). Behavioral models only; sim != silicon.

Start-up probe: the RPU10 = 10 ohm ESL decks are additionally re-run with .tran stopped just before the acceptance-run
abort instant (12.2644 ms typ / 12.2695 ms wchi) and start-up-only .meas, to document the start-up comparator trip
(INP < 2.5 V during the turn-on ringing) that precedes the timestep collapse (P0-03 finding).

Usage: PDU_NGSPICE=/usr/bin/ngspice python3 slew_study.py -> ../results/slew-study/slew-study.json (+ logs). Exit 0 always
when it ran (data, not a gate); 2 if a deck/include could not be prepared.
"""
import hashlib, json, os, re, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent; SIM = PKG.parent.parent
sys.path.insert(0, str(PKG)); import run_o1ovp as R
OUT = PKG/'results'/'slew-study'
RPU = ['10', '100', '330', '1k']
CASES = ['buck-short-c185-esr12m5-esl2n-typ', 'buck-short-c185-esr12m5-esl2n-wchi', 'buck-short-c165-esr12m5-esl2n-typ',
         'buck-short-c185-esr12m5-wchi', 'buck-short-rev1-c92-esr12m5-wchi', 'efuse-ovp-s023-wchi']
EXTRA = ('.meas tran SLEW_VGS_1_6_T TRIG V(M_VGS) VAL=1 RISE=1 TARG V(M_VGS) VAL=6 RISE=1\n'
         '.meas tran SLEW_FET_ON_T WHEN V(M_VGS)=6 RISE=1\n'
         '.meas tran SLEW_RAW_MAX_STARTUP MAX V(RAW) FROM=1m TO={stop}\n')
KEYS = ['slew_vgs_1_6_t', 'slew_fet_on_t', 'slew_raw_max_startup', 'info_startup_inp_min', 'info_startup_vgs_fall_t',
        'o1_global_peak', 'o1_peak', 'bus_peak', 'inp_pre_min', 'vgs_pre_min', 'bus_normal_max', 'bus_pre_max']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Start-up probe (P0-03 finding): the RPU10 = 10 ohm ESL decks abort at 12.2645 ms (typ) / 12.2699 ms (wchi) in the
# acceptance run, so their .meas are lost.  The same deck is re-run with .tran stopped just before the abort and only
# start-up .meas -> documents whether the comparator (INP) already fired during the turn-on ringing (start-up false trip).
PROBE_STOP = {'typ': '12.2644m', 'wchi': '12.2695m'}
PROBE_MEAS = ('.meas tran PROBE_INP_MIN MIN V(INP_OVP) FROM=12m TO={stop}\n'
              '.meas tran PROBE_INP_FALL_T WHEN V(INP_OVP)=2.5 FALL=1\n'
              '.meas tran PROBE_RAW_MAX MAX V(RAW) FROM=12m TO={stop}\n'
              '.meas tran PROBE_VGS_MAX MAX V(M_VGS) FROM=12m TO={stop}\n'
              '.meas tran PROBE_FET_ON_T WHEN V(M_VGS)=6 RISE=1\n'
              '.meas tran PROBE_O1_MAX MAX V(O1_11V) FROM=0 TO={stop}\n'
              '.meas tran PROBE_BUS_MAX MAX V(VOUT) FROM=0 TO={stop}\n')

def probe(a):
    name, tmp = a
    c = R.CASES[name]; src = R.DECKS/c['ng_file']; d = Path(tmp)/'probe'; d.mkdir(exist_ok=True)
    stop = PROBE_STOP[name.rsplit('-', 1)[1]]
    lines = [l for l in src.read_text().split('\n') if not l.lower().startswith('.meas')]
    t = '\n'.join(lines)
    assert t.count('.tran 100n 80m 0 100n uic') == 1, name
    t = t.replace('.tran 100n 80m 0 100n uic', f'.tran 100n {stop} 0 100n uic')
    t = t.replace('.include ../../../', f'.include {SIM}/').replace('.include ../', f'.include {PKG}/')
    t = t.replace('\n.end', '\n' + PROBE_MEAS.format(stop=stop) + '.end', 1)
    deck = d/src.name; deck.write_text(t)
    r = R.run_deck('ng', os.environ['PDU_NGSPICE'], deck, OUT/f'{name}.probe-startup.ng.log', d)
    m = r['measures']
    return dict(case=name, rpu10='10', tran_stop=stop, completed=r['execution_pass'], errors=r['errors'][:1], log=r['log'],
                log_sha256=r['log_sha256'], source_deck_sha256=sha(src), measures=m,
                startup_comparator_fired=(m.get('probe_inp_min') is not None and m['probe_inp_min'] < 2.5))

def job(a):
    rpu, name, tmp = a
    c = R.CASES[name]; src = R.DECKS/c['ng_file']; d = Path(tmp)/rpu; d.mkdir(exist_ok=True)
    blk = (PKG/'pdu-o1ovp-block.inc').read_text()
    assert blk.count('RPU10 PU_OVP G_OVP 10\n') == 1
    (d/'block.inc').write_text(blk.replace('RPU10 PU_OVP G_OVP 10\n', f'RPU10 PU_OVP G_OVP {rpu}\n'))
    t = src.read_text()
    stop = '24m' if 'short' in name else '13m'
    t = t.replace('.include ../pdu-o1ovp-block.inc\n', f'.include {d}/block.inc\n').replace('.include ../../../', f'.include {SIM}/').replace('.include ../', f'.include {PKG}/')
    t = t.replace('\n.end', '\n' + EXTRA.format(stop=stop) + '.end', 1) if '\n.end' in t else None
    assert t and t.count(f'{d}/block.inc') == 1, name
    deck = d/src.name; deck.write_text(t)
    r = R.run_deck('ng', os.environ['PDU_NGSPICE'], deck, OUT/f'{name}.rpu{rpu}.ng.log', d)
    out = []
    if r['execution_pass'] and c['kind'] != 'reference':
        R.evaluate(name, c, r['measures'], lambda n, ok, dd: out.append((n, bool(ok), dd)))
    return dict(case=name, rpu10=rpu, completed=r['execution_pass'], errors=r['errors'][:1], log=r['log'], log_sha256=r['log_sha256'],
                source_deck_sha256=sha(src), measures={k: r['measures'].get(k) for k in KEYS if k in r['measures']},
                acceptance_fail=[f'{n}: {dd}' for n, ok, dd in out if R.category(c, n) == 'acceptance' and not ok],
                info_fail=[f'{n}: {dd}' for n, ok, dd in out if R.category(c, n) != 'acceptance' and not ok])

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        rows = list(ex.map(job, [(r, n, tmp) for n in CASES for r in RPU]))
        probes = list(ex.map(probe, [(n, tmp) for n in CASES if 'esl2n' in n] + [('buck-short-c165-esr12m5-esl2n-wchi', tmp)]))
    for x in rows:
        m = x['measures']
        print(f"{x['case']:40s} RPU10={x['rpu10']:>4s} done={x['completed']!s:5s} t1-6V={m.get('slew_vgs_1_6_t', float('nan'))*1e6:8.2f}us "
              f"RAWmax_su={m.get('slew_raw_max_startup', float('nan')):7.4f} O1glob={m.get('o1_global_peak', float('nan')):7.4f} "
              f"acc_fail={len(x['acceptance_fail'])} info_fail={len(x['info_fail'])} {x['errors'][:1]}")
    for x in probes:
        m = x['measures']
        print(f"PROBE {x['case']:40s} stop={x['tran_stop']} done={x['completed']} INPmin={m.get('probe_inp_min')} "
              f"INPfall={m.get('probe_inp_fall_t')} RAWmax={m.get('probe_raw_max')} O1max={m.get('probe_o1_max')} BUSmax={m.get('probe_bus_max')} FETon={m.get('probe_fet_on_t')} fired={x['startup_comparator_fired']}")
    (OUT/'slew-study.json').write_text(json.dumps(dict(
        _status='WP2 OPTION EXPLORATION - diagnostic only, NOT adopted (candidate RPU10 = 10 ohm); behavioral models; sim != silicon',
        variable='RPU10 (PU_OVP -> G_OVP series resistor); PD path (RPD10) unchanged so turn-off/O1 budget unaffected',
        block_inc_sha256=sha(PKG/'pdu-o1ovp-block.inc'), lib_sha256=sha(PKG/'pdu-o1ovp-behavioral.lib'), rows=rows, startup_probes=probes), indent=1) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
