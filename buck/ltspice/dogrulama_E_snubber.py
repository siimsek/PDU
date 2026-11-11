#!/usr/bin/env python3
"""Dogrulama E: tam parazitik model + giris/cikis MLCC; kapi direnci x RC sonumleyici (Vin=26 V)."""
import json
from pathlib import Path
from araclar import Case, tune, pmap, replace

BASE = Case(f=100e3, ind="WE-HCF 74436413300 33u", mos="BSZ065N06LS5", vin=26.0, full=True, nmlcc=2, nmlcc_out=2)
D0 = {"RBQ30NS45B": 0.4328, "RBR40NS60A": 0.4335}
SN = [(0, 0), (2.2, 1e-9), (3.3, 2.2e-9), (2.2, 4.7e-9)]
jobs = [("RBR40NS60A", rg, sn) for rg in (4.7, 10, 22) for sn in SN] + [("RBQ30NS45B", 10, sn) for sn in SN[1:]]

def job(j):
    d, rg, (sr, sc) = j
    _, r = tune(replace(BASE, dio=d, rg=rg, snub_r=sr, snub_c=sc, duty=D0[d]), f"vE_{d}_{rg:g}_{sr:g}_{sc*1e9:g}n".replace(".", "p"), tol=4e-3)
    return dict(dio=d, rg=rg, snub_r=sr, snub_c=sc, r=r)

res = pmap(job, jobs, workers=3)
Path("sonuc/dogrulama_E_snubber.json").write_text(json.dumps(res, indent=1))
for x in res:
    r = x["r"]
    print(f"{x['dio']:11} Rg={x['rg']:4} RC={x['snub_r']:g}ohm/{x['snub_c']*1e9:g}nF eta={r['eta_gate']*100:.3f} Vds_max={r['vdsmax']:.1f} Vr_max={r['vrmax']:.1f} Vsw_min={r['vswmin']:.2f} Vopp={r['vopp']*1e3:.0f}mV Vopp20={r['vopp20']*1e3:.1f}mV Vinpp={r['vinpp']*1e3:.0f}mV Pmos={r['pmos']:.2f} Pdio={r['pdio']:.2f} it={r['iters']} {r['solver_note']}")
