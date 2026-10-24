#!/usr/bin/env python3
"""WP1 rev3 P1-01: per-FET VDS / ID / power / energy from the ngspice model vs CSD18540Q5B SOA (SLPS488B Fig. 10).

DIAGNOSTIC (information), not an acceptance test. Copies selected acceptance decks unchanged and only APPENDS
B-sources + .meas lines (no circuit/stimulus/option change). Channel current is recomputed with the exact
O1OVP_NFET expression (pdu-o1ovp-behavioral.lib: I = V(D,S)*(1n + min(max((VGS-VTH)/(4.5-VTH),0),1)/RON)),
for side A (XQ10: RAW->SRC) and side B (XQ11: VOUT->SRC). Body-diode and Cds currents are NOT included
(limitation, stated). The FET model has no saturation (conducts more during turn-off = conservative energy).
Per-FET values: (a) ideal sharing /NPAR, (b) STRICT: one FET takes the whole side current (assumption A-SHARE).
SOA: graph reading of SLPS488B Fig. 10 (single pulse, Tc = 25 C, RthJC 0.8 C/W), digitized by eye from the
PDF rendered on the box (reading accuracy assumed +/-25 %); derated linearly to Tc = 125 C (x (175-125)/150,
assumption A-TC: strictest plausible board case temperature; TJ max 175 C). Pulse width = next SOA curve
>= t_eq = E/P_max. Check: I_strict at VDS_max (both taken as window maxima, rectangle = conservative) <= I_SOA.
Usage: PDU_NGSPICE=ngspice python3 fet_soa_study.py -> ../results/soa-study/*.log + fet-soa-study.json
"""
import hashlib, json, math, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).absolute().parent; PKG = HERE.parent; OUT = PKG/'results'/'soa-study'
DECKS = ['buck-short-c185-wchi', 'buck-short-c483-esr12m5-wchi', 'buck-short-c165-esr12m5-wchi', 'buck-short-c185-esr100m-wchi',
         'efuse-ovp-s023-wchi', 'efuse-ovp-s007-wchi', 'startup-26v', 'startup-20v-ibstmin', 'startup-26v-c165',
         'load-step-7p5a-par1-ron5m28', 'bus-7p5a-par1-ron5m28']
# SLPS488B Fig. 10 graph reading (VDS V, ID A) per pulse width; Tc = 25 C single pulse
SOA = {'10us': [(1.8, 400), (40, 400), (60, 250)],
       '100us': [(1.8, 400), (10, 400), (27, 150), (60, 25)],
       '1ms': [(2.5, 400), (10, 120), (60, 4)],
       '10ms': [(1.3, 280), (1.8, 280), (4.5, 120), (60, 1.5)],
       '100ms': [(0.5, 100), (1.1, 100), (10, 9), (60, 1.1)]}
PW = [(10e-6, '10us'), (100e-6, '100us'), (1e-3, '1ms'), (10e-3, '10ms'), (100e-3, '100ms')]
TC, TJMAX = 125.0, 175.0; DER = (TJMAX - TC)/(TJMAX - 25)
MEAS = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)(?::[^\r\n]*?=|\s*=)\s*([-+\d.eE]+)', re.M)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ms = lambda s: float(s[:-1])*1e-3 if s.endswith('m') else float(s)

def soa_i(curve, v):
    pts = SOA[curve]
    if v <= pts[0][0]: return pts[0][1]
    for (v0, i0), (v1, i1) in zip(pts, pts[1:]):
        if v <= v1: return math.exp(math.log(i0) + (math.log(i1)-math.log(i0))*(math.log(v)-math.log(v0))/(math.log(v1)-math.log(v0)))
    return 0.0

def windows(name, stop):
    if name.startswith('buck-short'): w = [('startup', '0', '29m'), ('fault', '29m', '45m'), ('postfault', '45m', '55m'), ('restart', '55m', '80m')]
    elif name.startswith('efuse-ovp'): w = [('startup', '0', '14.9m'), ('fault', '14.9m', '25.1m'), ('recovery', '25.1m', '40m')]
    else: w = [('whole', '0', stop)]
    return [x for x in w if ms(x[1]) < ms(stop)]

def one(name):
    src = PKG/'decks'/f'o1ovp-{name}.ng.cir'; t = src.read_text()
    stop = [l.split()[2] for l in t.splitlines() if l.lower().startswith('.tran')][0]
    add = ['* --- SOA study probes (appended; circuit unchanged) ---',
           'Bga M_GA 0 V=(1n+min(max((V(G_OVP,SRC_OVP)-{VTH_P})/(4.5-{VTH_P}),0),1)/{RON_P/NPAR})',
           'Bia M_IA 0 V=V(RAW,SRC_OVP)*V(M_GA)', 'Bib M_IB 0 V=V(VOUT,SRC_OVP)*V(M_GA)',
           'Bpa M_PA 0 V=V(RAW,SRC_OVP)*V(M_IA)', 'Bpb M_PB 0 V=V(VOUT,SRC_OVP)*V(M_IB)']
    W = windows(name, stop)
    for w, a, b in W:
        for s in 'AB':
            add += [f'.meas tran {w}_P{s}_MAX MAX V(M_P{s}) FROM={a} TO={b}', f'.meas tran {w}_E{s} INTEG V(M_P{s}) FROM={a} TO={b}',
                    f'.meas tran {w}_I{s}_MAX MAX V(M_I{s}) FROM={a} TO={b}',
                    f'.meas tran {w}_I{s}_MIN MIN V(M_I{s}) FROM={a} TO={b}', f'.meas tran {w}_V{s}_MAX MAX V(M_VDS{s}) FROM={a} TO={b}',
                    f'.meas tran {w}_V{s}_MIN MIN V(M_VDS{s}) FROM={a} TO={b}']
    i = t.rindex('.end'); new = f'* SOA-STUDY COPY of decks/{src.name} (probes appended only) - information, NOT acceptance\n' + t[:i] + '\n'.join(add) + '\n' + t[i:]
    f = HERE/f'{name}.soa.ng.cir'; f.write_text(new, newline='\n'); log = OUT/f'{name}.soa.ng.log'
    p = subprocess.run([os.environ.get('PDU_NGSPICE', 'ngspice'), '-D', 'ngbehavior=ltpsa', '-b', '-o', str(log), f.name], cwd=HERE, capture_output=True, timeout=7200)
    lt = log.read_text(errors='replace'); m = {k.lower(): float(v) for k, v in MEAS.findall(lt)}
    npar = float(re.search(r'NPAR=(\d+)', t).group(1))
    rows = []
    for w, a, b in W:
        for s in 'AB':
            k = lambda q: m.get(f'{w}_{q}'.lower())
            P, E = k(f'P{s}_MAX'), k(f'E{s}')
            if P is None: rows.append(dict(window=w, side=s, missing=True)); continue
            I = max(abs(k(f'I{s}_MAX')), abs(k(f'I{s}_MIN'))); V = max(abs(k(f'V{s}_MAX')), abs(k(f'V{s}_MIN')))
            teq = E/P if P > 0 else 0.0
            curve = next((c for tpw, c in PW if teq <= tpw), '100ms')
            Isoa = soa_i(curve, max(V, 0.1))*DER
            I_from_P = P/max(V, 1e-3)   # current at VDS_max implied by P_max (less conservative than the rectangle)
            rows.append(dict(window=f'{w} {a}..{b}', side='QA (RAW side)' if s == 'A' else 'QB (VOUT side)',
                             side_Pmax_W=P, side_E_J=E, side_Imax_A=I, VDS_max_V=V, t_eq_s=teq, soa_curve=curve,
                             per_fet_ideal=dict(P_W=P/npar, E_J=E/npar, I_A=I/npar), per_fet_strict=dict(P_W=P, E_J=E, I_A=I),
                             I_SOA_at_VDSmax_Tc125_A=Isoa, rectangle_ok=I <= Isoa, pmax_point_ok=I_from_P <= Isoa,
                             margin_rect_x=(Isoa/I if I > 0 else None)))
    return dict(case=name, npar=npar, tran_stop=stop, source_deck='decks/' + src.name, source_sha256=sha(src), study_deck=f.name,
                study_deck_sha256=sha(f), log='results/soa-study/' + log.name, log_sha256=sha(log), rc=p.returncode,
                solver=re.findall(r'Using (.*?) as Direct Linear Solver', lt), errors=[l for l in lt.splitlines() if re.search(r'error|abort|too small', l, re.I)][:3], rows=rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=PKG, capture_output=True, text=True).stdout.strip()
    with ThreadPoolExecutor(int(os.environ.get('JOBS', '6'))) as ex: rs = list(ex.map(one, DECKS))
    allrows = [r for c in rs for r in c['rows'] if not r.get('missing')]
    drows = [r for c in rs if c['npar'] == 2 for r in c['rows'] if not r.get('missing')]
    dirty = bool(subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no', '--', '.', ':!results', ':!o1ovp-results.json'], cwd=PKG, capture_output=True, text=True).stdout.strip())
    out = dict(_status='INFORMATION (P1-01) - model-based, not acceptance; SOA from graph reading; bench B18 required', git_commit=head,
               assumptions=dict(A_SHARE='strict per-FET = whole side current (no sharing credit); ideal = /NPAR', A_TC=f'Tc = {TC} C, SOA derated x{DER:.3f}',
                                A_READ='Fig. 10 graph reading +/-25 %', limits='body diode, Cds current, thermal coupling between events not modelled'),
               soa_digitized_Tc25=SOA, all_rectangle_ok=all(r['rectangle_ok'] for r in allrows), all_pmax_point_ok=all(r['pmax_point_ok'] for r in allrows),
               min_rect_margin_x=min((r['margin_rect_x'] for r in allrows if r['margin_rect_x']), default=None),
               design_npar2=dict(note='design decks only (NPAR=2); par1 decks are INFO (single pair, shows why 2 pairs are used)',
                                 rectangle_ok=all(r['rectangle_ok'] for r in drows), pmax_point_ok=all(r['pmax_point_ok'] for r in drows),
                                 min_rect_margin_x=min((r['margin_rect_x'] for r in drows if r['margin_rect_x']), default=None)),
               git_dirty=dirty, cases=rs)
    (OUT/'fet-soa-study.json').write_text(json.dumps(out, indent=1) + '\n')
    for c in rs:
        for r in c['rows']:
            if r.get('missing'): print(c['case'], r['window'], 'MISSING', c['errors'][:1]); continue
            print(f"{c['case']:30s} {r['window']:22s} {r['side'][:2]} P={r['side_Pmax_W']:.4g}W E={r['side_E_J']:.4g}J I={r['side_Imax_A']:.4g}A V={r['VDS_max_V']:.4g}V teq={r['t_eq_s']:.3g}s {r['soa_curve']} Isoa={r['I_SOA_at_VDSmax_Tc125_A']:.4g} rect={r['rectangle_ok']} pt={r['pmax_point_ok']}")
    print('design_npar2', out['design_npar2'])
    print('all_rectangle_ok', out['all_rectangle_ok'], 'all_pmax_point_ok', out['all_pmax_point_ok'], 'min_rect_margin_x', out['min_rect_margin_x'])
if __name__ == '__main__': main()
