#!/usr/bin/env python3
"""Dogrulama A-C: tam parazitik model, sicaklik, kondansator/tolerans. Hepsi LTspice kosusu."""
import json
from pathlib import Path
from araclar import Case, tune, pmap, replace

BASE = Case(f=100e3, ind="WE-HCF 74436413300 33u", mos="BSZ065N06LS5")
out = {}

# A) tam parazitik model (ESL + 5 nH sicak cevrim), iki diyot adayi
def jobA(j):
    dio, vin = j
    _, fast = tune(replace(BASE, dio=dio, vin=vin), f"vA_fast_{dio}_{vin:g}".replace(".", "p"))
    _, r = tune(replace(BASE, dio=dio, vin=vin, full=True, duty=fast["duty"]), f"vA_full_{dio}_{vin:g}".replace(".", "p"), tol=3e-3)
    return dict(dio=dio, vin=vin, fast=fast, full=r)
out["A_full"] = pmap(jobA, [(d, v) for d in ("RBQ30NS45B", "RBR40NS60A") for v in (20.0, 22.2, 26.0)], workers=2)

# B) sicaklik (LTspice .temp; VDMOS Ron sicaklik katsayisi modele baglidir)
def jobB(j):
    dio, T = j
    _, r = tune(replace(BASE, dio=dio, vin=26.0, temp=T), f"vB_{dio}_{T:g}")
    return dict(dio=dio, temp=T, r=r)
out["B_temp"] = pmap(jobB, [(d, T) for d in ("RBQ30NS45B", "RBR40NS60A") for T in (27, 85, 125)])

# C) kondansator secenekleri, L ve C -%20, ESR x1.5, Vin=26 V (en kotu ripple) ve 20 V
CINS = [("WCAP-PSLC 875075661008 220u/35V", 2), ("WCAP-PSLC 875075661008 220u/35V", 1),
        ("WCAP-PT5H 870235675007 150u/35V", 2), ("WCAP-PSLC 875075661004 100u/35V", 2)]
COUTS = [("WCAP-PTG5 870025575009 330u/25V", 1), ("WCAP-PTG5 870025575007 220u/25V", 1),
         ("WCAP-PSLC 875075561006 150u/25V", 1), ("WCAP-PSLC 875075561005 100u/25V", 1),
         ("WCAP-PSLC 875075561005 100u/25V", 2)]
def jobC(j):
    kind, (part, n), vin = j
    kw = dict(cin=part, ncin=n) if kind == "cin" else dict(cout=part, ncout=n)
    c = replace(BASE, dio="RBR40NS60A", vin=vin, lscale=0.8, cscale=0.8, esrscale=1.5, **kw)
    _, r = tune(c, f"vC_{kind}_{part.split()[1]}_{n}_{vin:g}")
    return dict(kind=kind, part=part, n=n, vin=vin, r=r)
out["C_caps"] = pmap(jobC, [("cin", x, v) for x in CINS for v in (20.0, 26.0)] + [("cout", x, v) for x in COUTS for v in (20.0, 26.0)])

Path("sonuc").mkdir(exist_ok=True)
Path("sonuc/dogrulama_A.json").write_text(json.dumps(out, indent=1))
print("A) tam parazitik model")
for x in out["A_full"]:
    a, b = x["fast"], x["full"]
    print(f" {x['dio']:11} Vin={x['vin']:4} eta hizli={a['eta_gate']*100:.3f} tam={b['eta_gate']*100:.3f} D={b['duty']:.4f} | tam: Vds_max={b['vdsmax']:.1f} Vr_max={b['vrmax']:.1f} Vsw_min={b['vswmin']:.1f} Vopp={b['vopp']*1e3:.0f}mV Vopp20MHz={b['vopp20']*1e3:.1f}mV Vinpp={b['vinpp']*1e3:.0f}mV Pmos={b['pmos']:.2f} Pdio={b['pdio']:.2f} it={b['iters']} note={b['solver_note']!r}")
print("B) sicaklik, Vin=26")
for x in out["B_temp"]:
    r = x["r"]; print(f" {x['dio']:11} T={x['temp']:3} eta={r['eta_gate']*100:.3f} Pmos={r['pmos']:.3f} Pdio={r['pdio']:.3f} D={r['duty']:.4f}")
print("C) kondansator (L,C -%20, ESR x1.5)")
for x in out["C_caps"]:
    r = x["r"]; print(f" {x['kind']:4} {x['n']}x {x['part']:34} Vin={x['vin']:4} Vopp20={r['vopp20']*1e3:5.1f}mV Vinpp={r['vinpp']*1e3:5.0f}mV ICin_rms={r['icinrms']:.2f} ICout_rms={r['icoutrms']:.2f} eta={r['eta_gate']*100:.3f}")
