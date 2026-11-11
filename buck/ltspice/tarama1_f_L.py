#!/usr/bin/env python3
"""Tarama 1: frekans x bobin (gercek parca kayitlari), 11 V / 7,5 A sabit, duty her noktada ayarli."""
import json
from pathlib import Path
from araclar import Case, INDUCTORS, tune, pmap

FREQS = [50e3, 75e3, 100e3, 150e3, 200e3, 300e3, 400e3]
VINS = [20.0, 22.2, 26.0]
jobs = []
for f in FREQS:
    for ind, (L, *_ ) in INDUCTORS.items():
        dil = 11 * (1 - 11 / 26) / (L * f)
        if dil > 0.6 * 7.5 or dil < 0.08 * 7.5:   # asiri/gereksiz kucuk ripple adaylarini kosma
            continue
        for vin in VINS:
            jobs.append((f, ind, vin))


def job(j):
    f, ind, vin = j
    name = f"t1_{int(f/1e3)}k_{ind.split()[-1]}_{ind.split()[0][:2]}_{ind.split()[1][-4:]}_{vin:g}".replace(".", "p")
    c, r = tune(Case(vin=vin, f=f, ind=ind), name)
    r.update(f=f, ind=ind, vin=vin)
    return r


if __name__ == "__main__":
    res = pmap(job, jobs)
    Path(__file__).with_name("sonuc").mkdir(exist_ok=True)
    Path(__file__).with_name("sonuc").joinpath("tarama1_f_L.json").write_text(json.dumps(res, indent=1))
    print(f"{'f':>5} {'bobin':28} " + " ".join(f"eta@{v:g}".rjust(8) for v in VINS) + "   dIL@26  Vopp20@26 Vinpp  Pmos Pdio Pind (22.2V)")
    key = {}
    for r in res:
        key.setdefault((r["f"], r["ind"]), {})[r["vin"]] = r
    for (f, ind), d in sorted(key.items(), key=lambda kv: -sum(x["eta_gate"] for x in kv[1].values())):
        n = d[22.2]; h = d[26.0]
        print(f"{f/1e3:5.0f} {ind:28} " + " ".join(f"{d[v]['eta_gate']*100:8.3f}" for v in VINS)
              + f"  {h['ilmax']-h['ilmin']:6.2f} {h['vopp20']*1e3:8.1f} {max(x['vinpp'] for x in d.values())*1e3:6.0f}"
              + f"  {n['pmos']:.2f} {n['pdio']:.2f} {n['pind']:.2f}  it={max(x['iters'] for x in d.values())} set={max(x['settled'] for x in d.values())*1e3:.1f}mV")
