#!/usr/bin/env python3
"""Tur-6 / Tur-12 diagnostic (review 6416795114: UVLO-T6-02 / WP1-T12-01) - NOT acceptance, nothing adopted.

Hypothesis under test (review): the 'Timestep too small ... trouble with node imon_*' aborts come from the
Bmon I=246u*max(I(Vsense),0) kink of the BASELINE eFuse model (simulation/pdu-behavioral.lib, read only). Step 1 of the
review protocol: log I(Vsense), IMON, the latch / done / ena states and the bus/output voltages around the abort; if the
current does not cross zero the hypothesis is rejected.

Each case re-runs the COMMITTED deck unchanged except: .meas lines removed, .tran print step 10n with tstart shortly before
the known abort (the solution itself is identical up to output: same tstop-independent step control, same tmax), and one
.print line. Output: results/imon-diag-t6/<case>.{log,csv} + imon-diag.json. Behavioural models; sim != silicon.
"""
import json, re, subprocess, sys, tempfile, time, hashlib
from pathlib import Path
HERE = Path(__file__).absolute().parent; OUT = HERE / 'results' / 'imon-diag-t6'
WP1 = HERE.parent / '2026-10-25-o1-ovp'
CASES = [  # name, deck, eFuse instance, IMON node, output node, tstart, tstop
    ('wp2-dip0v-50us-typ-ttyp', HERE / 'decks' / 'uvlo-dip0v-50us-typ-ttyp.cir', 'xu3', 'IMON_O1', 'O1_11V', 0.26045, 0.2606),
    ('wp1-buck-short-c165-esr12m5-esl2n-typ', WP1 / 'decks' / 'o1ovp-buck-short-c165-esr12m5-esl2n-typ.ng.cir', 'xu4', 'IMON_S2E',
     'S2E_11V', 0.01224, 0.012275),
]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
git = lambda *a: subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True).stdout

def parse(txt):
    cols, data = None, {}
    for l in txt.splitlines():
        if l.startswith('Index'): cols = [c.lower() for c in l.split()[1:]]; continue
        w = l.split()
        if cols and w and w[0].isdigit() and len(w) == len(cols) + 1:
            d = data.setdefault(int(w[0]), {})
            for c, v in zip(cols, w[1:]): d[c] = float(v)
    return [data[i] for i in sorted(data)]

def one(c, tmp):
    name, deck, x, imon, onode, t0, t1 = c
    t = deck.read_text().replace('.include ../', f'.include {deck.parent.parent}/')
    t = re.sub(r'^\.meas.*\n', '', t, flags=re.M | re.I)
    assert len(re.findall(r'^\.tran', t, flags=re.M | re.I)) == 1
    t = re.sub(r'^\.tran\s+\S+\s+\S+\s+\S+\s+(\S+)', lambda m: f'.tran 10n {t1} {t0} {m.group(1)}', t, flags=re.M | re.I)
    pr = f'.print tran V({imon}) i(v.{x}.vsense) V({x}.latch) V(VOUT) V({onode}) V({x}.done) V({x}.ena)\n'
    t = re.sub(r'^\.end\s*$', pr + '.end', t, count=1, flags=re.M | re.I)
    d = Path(tmp) / name; d.mkdir(); (d / 'd.cir').write_text(t)
    log = OUT / f'{name}.log'; t_0 = time.time()
    subprocess.run(['ngspice', '-b', '-D', 'ngbehavior=ltpsa', '-o', str(log), 'd.cir'], cwd=d, capture_output=True, timeout=3600)
    txt = log.read_text(errors='replace'); rows = parse(txt)
    ab = re.search(r'Timestep too small; time = ([0-9.eE+-]+), timestep = ([0-9.eE+-]+): trouble with node "([^"]+)"', txt)
    ik, ek, vk = f'v.{x}.vsense#br', f'v({x}.ena)', 'v(vout)'
    I = [r.get(ik) for r in rows]
    zc = [dict(t=rows[k]['time'], i_before=I[k - 1], i_after=I[k]) for k in range(1, len(rows))
          if I[k] is not None and I[k - 1] is not None and (I[k] > 0) != (I[k - 1] > 0)]
    ena_tog = [rows[k]['time'] for k in range(1, len(rows)) if rows[k].get(ek) != rows[k - 1].get(ek)]
    hdr = sorted({k for r in rows for k in r}, key=lambda k: (k != 'time', k))
    (OUT / f'{name}.csv').write_text(','.join(hdr) + '\n' + ''.join(','.join(repr(r.get(k)) for k in hdr) + '\n' for r in rows))
    return dict(case=name, deck=str(deck.relative_to(HERE.parent.parent.parent)), deck_sha256=sha(deck), efuse=x, imon=imon,
                seconds=round(time.time() - t_0, 1), window=[t0, t1], n_points=len(rows),
                abort=dict(time=float(ab.group(1)), timestep=float(ab.group(2)), node=ab.group(3)) if ab else None,
                i_vsense_min=min(i for i in I if i is not None) if rows else None, i_vsense_max=max(i for i in I if i is not None) if rows else None,
                zero_crossings=zc, ena_toggles=ena_tog[:50], n_ena_toggles=len(ena_tog),
                vout_max=max(r.get(vk, float('-inf')) for r in rows) if rows else None,
                last_points=rows[-6:], log_sha256=sha(log))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p0 = dict(runner_sha256=sha(__file__), git_head=git('rev-parse', 'HEAD').strip(), git_status_porcelain=git('status', '--porcelain', '--', '.', '../2026-10-25-o1-ovp'),
              baseline_lib_sha256=sha(HERE.parent.parent / 'pdu-behavioral.lib'), argv=[sys.executable] + sys.argv, time=time.strftime('%Y-%m-%d %H:%M:%S %z'))
    with tempfile.TemporaryDirectory() as tmp:
        res = [one(c, tmp) for c in CASES]
    (OUT / 'imon-diag.json').write_text(json.dumps(dict(_status='Tur-6/Tur-12 IMON-kink hypothesis diagnostic (review step 1), NOT acceptance',
                                                        provenance=p0, cases=res), indent=1) + '\n')
    for r in res:
        print(r['case'], r['abort'], 'zc', len(r['zero_crossings']), 'Imin/max', r['i_vsense_min'], r['i_vsense_max'], 'ena tog', r['n_ena_toggles'], 'vout_max', r['vout_max'])
    return 0

if __name__ == '__main__':
    sys.exit(main())
