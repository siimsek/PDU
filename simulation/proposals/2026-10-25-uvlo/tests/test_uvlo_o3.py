#!/usr/bin/env python3
"""WP2 Tur-2 O3 candidate variant self-tests (review 6395614957 item 3). Stdlib only; reads the committed budget JSON/decks."""
import json, sys
from pathlib import Path
HERE = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(HERE))
B = json.loads((HERE / 'results' / 'uvlo-budget.json').read_text())
O = B['o3_variant']; CASES = json.loads((HERE / 'test-cases-uvlo.json').read_text())['cases']
res = []
def check(name, ok, detail=''):
    res.append(ok); print(('OK  ' if ok else 'FAIL') + f' {name}  -> {detail}')

sg = O['start_guarantee']
check('O1 O3 start guarantee is NOT reported as GUARANTEED (A/T terms remain)', sg['status'] != 'GUARANTEED' and len(sg['unbounded_terms']) >= 1,
      f"{sg['status']} unbounded={len(sg['unbounded_terms'])}")
check('O2 O3 margins are evaluated with the strict (sum) budget and are >= 0', O['chosen']['ok'], O['o3_margins_mV'])
check('O3 O3 mis-set Rb 5.23k regression FAILS analytically', not B['o3_regression_misset_rb_5k23']['ok'],
      round(B['o3_regression_misset_rb_5k23']['worst'], 4))
check('O4 O3 I_Q_PRESTART includes REF5040 IQ 1.2 mA', abs(O['i_q_prestart'] - (B['requirements']['I_Q_PRESTART'] + 1.2e-3)) < 1e-12, O['i_q_prestart'])
check('O5 ACAS relative bound includes solder heat (abs 0.1 % used as relative)', O['e_net_rel'] >= 0.0025 - 1e-12, O['e_net_rel'])
check('O6 limits unchanged (requirements block identical to C3 budget)', B['requirements']['E_START'] == 20.0 and B['requirements']['V_FALL_MIN'] == 18.0
      and B['requirements']['R_TOTAL_MAX'] == 0.25, B['requirements'])
blk3 = (HERE / 'pdu-uvlo-block.inc').read_text().splitlines(); blko = (HERE / 'pdu-uvlo-block-o3.inc').read_text().splitlines()
d = sorted(set(blko) - set(blk3)); gone = sorted(set(blk3) - set(blko))
check('O7 O3 block differs from C3 only by header + U23 reference + RR1U node', gone == ['* WP2 2026-10-25-uvlo candidate C3: U20 TLV3202 (A = input UVLO, B = restart timer), U21 TMUX1102 hysteresis switch.',
      'RR1U VREF_OVP REFD_UV {RR1U}'] and all(x.startswith(('*', 'Bu23', 'Ru23', 'Iu23', 'CU23', 'RR1U VREF_UV ')) for x in d), (gone, d))
o3c = {n: c for n, c in CASES.items() if c.get('variant') == 'O3'}
check('O8 O3 cases exist incl. start20 / dips / mbhold and one O3 regression expected FAIL',
      any(n.startswith('o3-start20') for n in o3c) and any(n.startswith('o3-dip0v-300us') for n in o3c) and any(n.startswith('o3-mbhold') for n in o3c)
      and [n for n, c in o3c.items() if c.get('regression')] == ['o3-reg-misset-rbu-5k23-vrmax'] and o3c['o3-reg-misset-rbu-5k23-vrmax']['expect'] == 'FAIL', len(o3c))
deck = (HERE / 'decks' / 'uvlo-o3-start20-vrmax-tmax.cir').read_text()
check('O9 O3 decks include the O3 block and set VREF_UV_P from the O3 corner', '.include ../pdu-uvlo-block-o3.inc' in deck
      and f"VREF_UV_P={O['spice_corners']['vrmax']['VREF_UV_P']:.7g}" in deck, '')
c3deck = (HERE / 'decks' / 'uvlo-start20-vrmax-tmax.cir').read_text()
check('O10 C3 decks still use the C3 block (comparison kept)', '.include ../pdu-uvlo-block.inc' in c3deck and 'VREF_UV_P' not in c3deck, '')
print(f'{sum(res)}/{len(res)} OK'); sys.exit(0 if all(res) else 1)
