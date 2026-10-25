#!/usr/bin/env python3
"""WP1 rev3 NEGATIVE SELF-TEST (diagnostic): runner and verifier must FAIL a deck whose OVP FET never turns on.

ChatGPT tur-2 P0-03 / owner rev3 request: a "fix" that keeps the FET off (e.g. a capacitor on the PU node) yields a
meaningless low O1 peak (~mV) that would look like a PASS.  rev3 added the pre-fault regime acceptance check
(INP_PRE_MIN > 2.5 V and VGS_PRE_MIN > 6 V) to run_o1ovp.py (evaluate) and verify_candidate.py (rules).

This script proves the check works: it copies acceptance decks and mutates ONLY a temporary copy of
pdu-o1ovp-block.inc (MUT: comparator sense input INM pulled to V5 by 10 ohm so INP is held low, or a large 1 uF diagnostic PU capacitor - INVALID as design fixes, never used in
the candidate), runs ngspice, and judges the result with BOTH run_o1ovp.evaluate and verify_candidate.rules.
Note: with the rev3 model the old 100 pF PU-cap diagnostic NO LONGER keeps the FET off (measured, O1 11.887 V), so the
self-test uses stronger mutations.  A 1 ohm pull-down directly on INP_OVP has no effect (ideal comparator output
source), so the INP mutation acts on the comparator input instead.  (Opening RPU10 to 1 G was tried and rejected: the ideal 1.69 A pull-up then has no
DC path and ngspice aborts - not a meaningful regime test.)  A broken deck may also lose its WHEN measures; the runner
then reports it INCOMPLETE (exit 2) and the verifier MISSING (exit 2) - both are non-pass, recorded per row.

Exit 0 = the self-test passed (FET stayed off AND both tools reported the regime check as FAIL and the case as not
passing); 1 = a tool accepted the broken deck (self-test FAILED); 2 = a deck could not be prepared or its regime
measures are absent (cannot judge).
Usage: PDU_NGSPICE=/usr/bin/ngspice python3 regime_selftest.py -> ../results/regime-selftest/regime-selftest.json + logs
"""
import hashlib, json, os, sys, tempfile
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent; SIM = PKG.parent.parent
sys.path.insert(0, str(PKG)); import run_o1ovp as R; import verify_candidate as V
OUT = PKG/'results'/'regime-selftest'
CASES = ['buck-short-c185-esr12m5-wchi', 'efuse-ovp-s023-wchi']
# mutations of a TEMPORARY block copy (never the candidate): name -> replacement for 'RPU10 PU_OVP G_OVP 10\n'
MUT = {'inp-forced-low': 'RPU10 PU_OVP G_OVP 10\nRINM_DIAG INM_OVP V5_OVP 10\n',  # sense input pulled to 5 V -> comparator holds INP low, FET off
       'pu-cap-1u': 'RPU10 PU_OVP G_OVP 10\nCPU_DIAG PU_OVP 0 1u\n'}  # PU-cap diagnostic (INVALID as a fix)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def one(name, mut, tmp):
    c = R.CASES[name]; src = R.DECKS/c['ng_file']; d = Path(tmp)/f'{name}.{mut}'; d.mkdir()
    blk = (PKG/'pdu-o1ovp-block.inc').read_text()
    if blk.count('RPU10 PU_OVP G_OVP 10\n') != 1: return None
    (d/'block.inc').write_text(blk.replace('RPU10 PU_OVP G_OVP 10\n', MUT[mut]))
    t = src.read_text().replace('.include ../pdu-o1ovp-block.inc\n', f'.include {d}/block.inc\n')
    t = t.replace('.include ../../../', f'.include {SIM}/').replace('.include ../', f'.include {PKG}/')
    if t.count(f'{d}/block.inc') != 1: return None
    deck = d/src.name; deck.write_text(t)
    r = R.run_deck('ng', os.environ.get('PDU_NGSPICE', 'ngspice'), deck, OUT/f'{name}.{mut}.ng.log', d)
    m = r['measures']
    run_chk = []
    try:
        R.evaluate(name, c, m, lambda n, ok, dd: run_chk.append((n, bool(ok), dd)))
    except KeyError as e:  # runner treats a missing required measure as INCOMPLETE (exit 2) - also a non-pass
        run_chk.append(('missing_measure', False, str(e)))
    run_regime = [x for x in run_chk if x[0] == 'pre_fault_regime_normal']
    try:
        ver = [(n, bool(ok), dd) for n, ok, dd in V.rules(c['kind'], m)]
    except KeyError as e:
        ver = [('missing', False, str(e))]
    ver_regime = [x for x in ver if x[0].startswith('pre-fault regime')]
    run_rej = (not r['execution_pass']) or any(not k for n, k, _ in run_chk if R.category(c, n) == 'acceptance')
    ver_rej = (not r['execution_pass']) or any(not k for _, k, _ in ver)
    regime_flagged = bool(run_regime and not run_regime[0][1] and ver_regime and not ver_regime[0][1])
    ok = run_rej and ver_rej and regime_flagged
    return dict(case=name, mutation=mut, mutation_line=MUT[mut].strip(), completed=r['execution_pass'], errors=r['errors'][:1], log=r['log'], log_sha256=r['log_sha256'],
                source_deck_sha256=sha(src), o1_global_peak=m.get('o1_global_peak'), o1_peak=m.get('o1_peak'),
                inp_pre_min=m.get('inp_pre_min'), vgs_pre_min=m.get('vgs_pre_min'),
                runner_regime_check=run_regime, runner_acceptance_fails=sum(1 for n, k, _ in run_chk if R.category(c, n) == 'acceptance' and not k),
                verifier_regime_check=ver_regime, verifier_fails=sum(1 for _, k, _ in ver if not k),
                runner_rejects=run_rej, verifier_rejects=ver_rej, regime_check_flagged=regime_flagged, selftest_pass=bool(ok))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        rows = [one(n, mu, tmp) for n in CASES for mu in MUT]
    if any(x is None for x in rows): print('could not prepare a deck'); return 2
    for x in rows:
        print(f"{x['case']:30s} {x['mutation']:14s} done={x['completed']} O1glob={x['o1_global_peak']} INPpre={x['inp_pre_min']} VGSpre={x['vgs_pre_min']} "
              f"runner={x['runner_regime_check']} verifier={x['verifier_regime_check']} selftest_pass={x['selftest_pass']}")
    (OUT/'regime-selftest.json').write_text(json.dumps(dict(
        _status='NEGATIVE SELF-TEST - temporary block mutations that keep the FET off; INVALID as design fixes; behavioral models',
        block_inc_sha256=sha(PKG/'pdu-o1ovp-block.inc'), lib_sha256=sha(PKG/'pdu-o1ovp-behavioral.lib'),
        run_o1ovp_sha256=sha(PKG/'run_o1ovp.py'), verify_candidate_sha256=sha(PKG/'verify_candidate.py'), rows=rows), indent=1) + '\n')
    # 2 only when the regime measures themselves are absent (cannot judge); an incomplete WHEN measure is an expected non-pass
    if any(x['inp_pre_min'] is None or x['vgs_pre_min'] is None for x in rows): return 2
    return 0 if all(x['selftest_pass'] for x in rows) else 1

if __name__ == '__main__':
    sys.exit(main())
