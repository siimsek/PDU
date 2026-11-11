#!/usr/bin/env python3
"""Dogrulama D: tam parazitik modelde zil/asim - kapi direnci ve MLCC etkisi (Vin=26 V)."""
import json
from pathlib import Path
from araclar import Case, tune, pmap, replace

BASE = Case(f=100e3, ind="WE-HCF 74436413300 33u", mos="BSZ065N06LS5", vin=26.0, full=True)
D0 = {"RBQ30NS45B": 0.4328, "RBR40NS60A": 0.4335}
jobs = [(d, rg, n) for d in D0 for rg in (4.7, 10, 22, 47) for n in (0, 2)]

def job(j):
    d, rg, n = j
    _, r = tune(replace(BASE, dio=d, rg=rg, nmlcc=n, duty=D0[d]), f"vD_{d}_{rg:g}_{n}".replace(".", "p"), tol=4e-3)
    return dict(dio=d, rg=rg, nmlcc=n, r=r)

res = pmap(job, jobs, workers=3)
Path("sonuc/dogrulama_D_zil.json").write_text(json.dumps(res, indent=1))
for x in res:
    r = x["r"]
    print(f"{x['dio']:11} Rg={x['rg']:4} MLCC={x['nmlcc']} eta={r['eta_gate']*100:.3f} Vds_max={r['vdsmax']:.1f} Vr_max={r['vrmax']:.1f} Vsw_min={r['vswmin']:.2f} Vgs=[{r['vgsmin']:.1f},{r['vgsmax']:.1f}] Vopp={r['vopp']*1e3:.0f}mV Vopp20={r['vopp20']*1e3:.1f}mV Pmos={r['pmos']:.2f} Pdio={r['pdio']:.2f} it={r['iters']} {r['solver_note']}")
