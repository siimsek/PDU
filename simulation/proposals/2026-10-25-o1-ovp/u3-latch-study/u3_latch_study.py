#!/usr/bin/env python3
"""WP1 rev3 - NEW finding N-01 (not raised by the review): U3/U4 behavioral breaker latch masks O1.

DIAGNOSTIC ONLY. Nothing here changes an acceptance deck, a limit or a result.

The baseline behavioral eFuse PDU_EFUSE (simulation/pdu-behavioral.lib, unchanged) is a latching
circuit breaker (ITRIP = 1460/RLIM + 0.11 A = 4.96 A for U3).  In fast-ramp / stress decks the CEFOUT1
inrush trips it, U3 opens and V(O1_11V) stops following VOUT.  The O1 value measured in such a deck is
then set by the baseline eFuse model, not by the new O1 OVP block.  The real TPS259824O behaviour in
this situation is NOT known here (bench B13).

Strictest safe ASSUMPTION used for the bound: U3 does not open (ideal pass element), so
O1 <= VOUT peak in the same window (BUS_PEAK).  Under that assumption every acceptance deck is
re-judged against the unchanged 12.0 V instantaneous limit.

Steps
 1. from ../o1ovp-results.json: every run with BUS_PEAK and O1_PEAK; gap = BUS_PEAK - O1_PEAK.
 2. probe decks (copies, this folder): selected decks + .meas of V(xu3.latch) / V(xu4.latch)
    -> confirms the latch instant by simulation (not inferred).
 3. u3-latch-study.json; exit 1 if any acceptance deck fails under the assumption, else 0.
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
LIMIT = 12.0
GAP_SUSPECT = 0.02  # V; O1 more than 20 mV below VOUT peak => U3 latch suspected (confirmed by probes)
PROBES = ['efuse-ovp-s023-wchi', 'buck-short-c185-esr100m-wchi', 'efuse-ovp-s017-wchi', 'buck-short-c165-esr12m5-wchi']
NGSPICE = os.environ.get('PDU_NGSPICE', 'ngspice')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git_head():
    try:
        c = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=PKG, capture_output=True, text=True).stdout.strip()
        d = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no', '--', '.', ':!results', ':!o1ovp-results.json'],
                           cwd=PKG, capture_output=True, text=True).stdout.strip()
        return c, bool(d)
    except Exception:
        return None, None


def probe(case):
    src = PKG / 'decks' / f'o1ovp-{case}.ng.cir'
    text = src.read_text()
    assert text.rstrip().endswith('.end')
    body = text.rstrip()[:-4]
    body += ('* u3-latch-study probe (diagnostic copy; added .meas only)\n'
             '.meas tran U3LATCH_T WHEN V(xu3.latch)=0.5 RISE=1\n'
             '.meas tran U4LATCH_T WHEN V(xu4.latch)=0.5 RISE=1\n'
             '.end\n')
    deck = HERE / f'{case}.probe.ng.cir'
    deck.write_text(body)
    out = PKG / 'results' / 'u3-latch-study'
    out.mkdir(parents=True, exist_ok=True)
    log = out / f'{case}.probe.ng.log'
    r = subprocess.run([NGSPICE, '-D', 'ngbehavior=ltpsa', '-b', deck.name], cwd=HERE, capture_output=True, text=True)
    log.write_text(r.stdout + r.stderr)
    meas = {}
    for line in (r.stdout + r.stderr).splitlines():
        m = re.match(r'^\s*(u3latch_t|u4latch_t|o1_peak|bus_peak)\s*=\s*([-+0-9.eE]+)', line)
        if m:
            meas[m.group(1)] = float(m.group(2))
    return {'case': case, 'source_deck': str(src.relative_to(PKG)), 'source_sha256': sha(src),
            'probe_deck': deck.name, 'probe_deck_sha256': sha(deck), 'log': str(log.relative_to(PKG)),
            'rc': r.returncode, 'u3_latch_t_ms': meas.get('u3latch_t', None) and round(meas['u3latch_t'] * 1e3, 5),
            'u4_latch_t_ms': meas.get('u4latch_t', None) and round(meas['u4latch_t'] * 1e3, 5),
            'o1_peak': meas.get('o1_peak'), 'bus_peak': meas.get('bus_peak'),
            'u3_latched': 'u3latch_t' in meas}


def main():
    res = json.loads((PKG / 'o1ovp-results.json').read_text())
    acc = {c['check'].split('/')[1] for c in res['checks']
           if c['category'] == 'acceptance' and c['check'].startswith('ngspice/')}
    rows = []
    for r in res['runs']:
        m = r['measures']
        if m.get('bus_peak') is None or m.get('o1_peak') is None:
            continue
        gap = m['bus_peak'] - m['o1_peak']
        suspect = gap > GAP_SUSPECT
        bound = m['bus_peak'] if suspect else max(m['o1_peak'], m.get('o1_global_peak') or 0)
        rows.append({'case': r['case'], 'acceptance': r['case'] in acc, 'o1_peak': m['o1_peak'],
                     'o1_global_peak': m.get('o1_global_peak'), 'bus_peak': m['bus_peak'],
                     'gap_V': round(gap, 5), 'u3_latch_suspected': suspect,
                     'o1_bound_assume_u3_closed_V': bound, 'pass_under_assumption': bound <= LIMIT})
    rows.sort(key=lambda x: -x['o1_bound_assume_u3_closed_V'])
    probes = [probe(c) for c in PROBES]
    acc_rows = [x for x in rows if x['acceptance']]
    fails = [x['case'] for x in acc_rows if not x['pass_under_assumption']]
    commit, dirty = git_head()
    out = {
        '_status': 'DIAGNOSTIC / OPEN finding N-01 - not an acceptance result; acceptance decks and limits unchanged',
        'assumption': 'U3 (TPS259824O) does not open during the event (ideal pass) -> O1 <= VOUT peak; real behaviour: bench B13',
        'limit_V': LIMIT, 'gap_suspect_V': GAP_SUSPECT, 'git_commit': commit, 'git_dirty_package': dirty,
        'results_json_sha256': sha(PKG / 'o1ovp-results.json'), 'results_label': res.get('label'),
        'results_git': res.get('git'),
        'acceptance_decks': len(acc_rows),
        'acceptance_latch_suspected': sum(x['u3_latch_suspected'] for x in acc_rows),
        'acceptance_fail_under_assumption': fails,
        'worst_acceptance_bound': acc_rows[0] if acc_rows else None,
        'worst_acceptance_bound_excl_esr100m': next((x for x in acc_rows if 'esr100m' not in x['case']), None),
        'probes': probes, 'rows': rows,
    }
    (HERE.parent / 'results' / 'u3-latch-study').mkdir(parents=True, exist_ok=True)
    (PKG / 'results' / 'u3-latch-study' / 'u3-latch-study.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(f"u3_latch_study: {len(acc_rows)} acceptance decks, {out['acceptance_latch_suspected']} latch-suspected, "
          f"fail under assumption: {fails}")
    for p in probes:
        print(f"  probe {p['case']}: rc={p['rc']} U3 latch t={p['u3_latch_t_ms']} ms, U4 latch t={p['u4_latch_t_ms']} ms, "
              f"O1 {p['o1_peak']} V, VOUT {p['bus_peak']} V")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
