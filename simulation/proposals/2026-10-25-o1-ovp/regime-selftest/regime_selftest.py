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

rev3 Tur-3 (ChatGPT "Ek P1"): every ngspice mutation above ends INCOMPLETE (a WHEN measure is lost), so it does not
prove rejection of a run that COMPLETES with a wrong regime. Part B therefore takes the real, COMPLETED rev3 acceptance
measures of each CASE from ../o1ovp-results.json (completed=True, accepted as PASS by both tools) and injects ONLY the
regime measures (synthetic, labelled as such, no ngspice): INP low / VGS low / both low, in the pre-fault window and - where
the deck has one - in the recovery window. Both tools must FAIL exactly the injected regime check and reject the case;
the unmodified control must pass. Tur-4 P2-T4-01: the 2x6 matrix is mandatory (missing window or row -> exit 2), and
each injection must fail ONLY its own regime check (other window PASS, no other failure). This is a synthetic unit test of the judging rules, not simulation evidence.

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

SYN = {  # Part B: synthetic wrong-regime values injected into COMPLETED measures (INVALID physically; tests the judges only)
    'control-unmodified': {},
    'pre-inp-low': {'inp_pre_min': 1.0}, 'pre-vgs-low': {'vgs_pre_min': 4.0}, 'pre-both-low': {'inp_pre_min': 1.0, 'vgs_pre_min': 4.0},
    'recov-inp-low': {'inp_recov_min': 1.0}, 'recov-vgs-low': {'vgs_recov_min': 4.0}}

def synthetic(res=None):  # res: optional pre-loaded results (guard_negative_test.py feeds mutated copies)
    res = res if res is not None else json.loads((PKG/'o1ovp-results.json').read_text())
    runs = {r['case']: r for r in res['runs'] if r['engine'] == 'ng'}
    rows = []
    for name in CASES:
        c = R.CASES[name]; base = runs.get(name)
        if base is None: return None  # Tur-4: every CASE must have a base run
        if not base['execution_pass']: return None  # base must be a completed run
        if any(k not in base['measures'] for inj in SYN.values() for k in inj): return None  # Tur-4: both windows mandatory
        for lab, inj in SYN.items():
            # Tur-4 P2-T4-01: fail closed - every expected (case, injection) must be judgeable; no silent skip
            if any(k not in base['measures'] for k in inj): return None
            m = dict(base['measures']); m.update(inj)
            run_chk = []; R.evaluate(name, c, m, lambda n, ok, dd: run_chk.append((n, bool(ok), dd)))
            ver = [(n, bool(ok), dd) for n, ok, dd in V.rules(c['kind'], m)]
            run_reg = {n: k for n, k, _ in run_chk if n in ('pre_fault_regime_normal', 'recovery_regime_normal')}
            ver_reg = {n: k for n, k, _ in ver if 'regime normal' in n}
            run_acc_fail = [n for n, k, _ in run_chk if R.category(c, n) == 'acceptance' and not k]
            ver_fail = [n for n, k, _ in ver if not k]
            want = 'pre' if lab.startswith('pre') else 'recov' if lab.startswith('recov') else None
            # Tur-4 P2-T4-01: both regime windows must be present in both tools; the injected window must FAIL and
            # be the ONLY failing check (runner acceptance fails == [it], verifier fails == its regime checks), the
            # other window must PASS; the control must have both windows PASS and no failure at all.
            have = ('pre_fault_regime_normal' in run_reg and 'recovery_regime_normal' in run_reg
                    and any(n.startswith('pre-fault') for n in ver_reg) and any(n.startswith('recovery') for n in ver_reg))
            if want is None:
                ok = (have and not run_acc_fail and not ver_fail and all(v is True for v in run_reg.values())
                      and all(v is True for v in ver_reg.values()))
            else:
                rk = 'pre_fault_regime_normal' if want == 'pre' else 'recovery_regime_normal'
                ok_rk = 'recovery_regime_normal' if want == 'pre' else 'pre_fault_regime_normal'
                vk = [n for n in ver_reg if n.startswith('pre-fault' if want == 'pre' else 'recovery')]
                vother = [n for n in ver_reg if n not in vk]
                ok = (have and run_reg[rk] is False and run_reg[ok_rk] is True and run_acc_fail == [rk]
                      and bool(vk) and all(ver_reg[n] is False for n in vk) and sorted(ver_fail) == sorted(vk)
                      and bool(vother) and all(ver_reg[n] is True for n in vother))
            rows.append(dict(case=name, injection=lab, injected=inj, base_completed=True, base_log_sha256=base.get('log_sha256'),
                             runner_regime=run_reg, verifier_regime=ver_reg, runner_acceptance_fails=run_acc_fail,
                             verifier_fails=ver_fail, selftest_pass=bool(ok)))
    got = sorted((r['case'], r['injection']) for r in rows)
    if got != sorted(EXPECTED_SYN): return None  # Tur-4 P2-T4-01: exact 2x6 matrix, no missing/extra rows
    return rows

EXPECTED_SYN = [(n, lab) for n in CASES for lab in SYN]  # 2 cases x 6 injections = 12 rows, all mandatory

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        rows = [one(n, mu, tmp) for n in CASES for mu in MUT]
    if any(x is None for x in rows): print('could not prepare a deck'); return 2
    syn = synthetic()
    if syn is None: print('synthetic part: base run incomplete, injection window absent or row set != expected 2x6'); return 2
    for x in syn:
        print(f"SYN {x['case']:30s} {x['injection']:18s} runner={x['runner_regime']} verifier={x['verifier_regime']} selftest_pass={x['selftest_pass']}")
    for x in rows:
        print(f"{x['case']:30s} {x['mutation']:14s} done={x['completed']} O1glob={x['o1_global_peak']} INPpre={x['inp_pre_min']} VGSpre={x['vgs_pre_min']} "
              f"runner={x['runner_regime_check']} verifier={x['verifier_regime_check']} selftest_pass={x['selftest_pass']}")
    (OUT/'regime-selftest.json').write_text(json.dumps(dict(
        _status='NEGATIVE SELF-TEST - temporary block mutations that keep the FET off; INVALID as design fixes; behavioral models',
        block_inc_sha256=sha(PKG/'pdu-o1ovp-block.inc'), lib_sha256=sha(PKG/'pdu-o1ovp-behavioral.lib'),
        run_o1ovp_sha256=sha(PKG/'run_o1ovp.py'), verify_candidate_sha256=sha(PKG/'verify_candidate.py'), rows=rows,
        synthetic_status='PART B - SYNTHETIC: completed rev3 measures with ONLY regime values injected (no ngspice); tests judging rules',
        o1ovp_results_sha256=sha(PKG/'o1ovp-results.json'), synthetic_rows=syn), indent=1) + '\n')
    # 2 only when the regime measures themselves are absent (cannot judge); an incomplete WHEN measure is an expected non-pass
    if any(x['inp_pre_min'] is None or x['vgs_pre_min'] is None for x in rows): return 2
    return 0 if all(x['selftest_pass'] for x in rows + syn) else 1

if __name__ == '__main__':
    sys.exit(main())
