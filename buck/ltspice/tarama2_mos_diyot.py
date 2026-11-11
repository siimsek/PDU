#!/usr/bin/env python3
"""Tarama 2: MOSFET x Schottky diyot (LTspice kutuphane modelleri), secilen f/L noktasinda.

Kullanim: python tarama2_mos_diyot.py <f_kHz> "<bobin anahtari>"
"""
import json
import sys
from pathlib import Path
from araclar import Case, tune, pmap

MOS = ["BSZ065N06LS5", "AON6264E", "AON7262E", "AONS66614", "AONS62614", "AONR62818",
       "BSC059N04LS6", "AON6144"]            # son ikisi 40 V: 26 V giriste pay dar
DIO = ["RB228NS-60", "RB238NS-60", "RBR40NS60A", "RBQ30NS65A", "RB218NS-60", "RBR30NS60A",
       "RBQ30NS45B", "RBR40NS40A", "MBRB2545CT"]  # son ucu 40-45 V
VINS = [20.0, 22.2, 26.0]

if __name__ == "__main__":
    f = float(sys.argv[1]) * 1e3
    ind = sys.argv[2]
    jobs = [(m, d, v) for m in MOS for d in DIO for v in VINS]

    def job(j):
        m, d, v = j
        name = f"t2_{int(f/1e3)}k_{m}_{d}_{v:g}".replace(".", "p")
        try:
            _, r = tune(Case(vin=v, f=f, ind=ind, mos=m, dio=d), name)
        except Exception as e:  # model kosmadiysa kaydet, uydurma
            return dict(mos=m, dio=d, vin=v, error=str(e)[:200])
        r.update(mos=m, dio=d, vin=v)
        return r

    res = pmap(job, jobs)
    out = Path(__file__).with_name("sonuc")
    out.mkdir(exist_ok=True)
    (out / "tarama2_mos_diyot.json").write_text(json.dumps(res, indent=1))
    key = {}
    for r in res:
        key.setdefault((r["mos"], r["dio"]), {})[r["vin"]] = r
    print(f"f={f/1e3:g} kHz, bobin={ind}")
    print(f"{'MOSFET':14} {'diyot':12} eta@20  eta@22.2 eta@26 | Pmos Pdio Pgate @26V | Vds_max Vr_max")
    ok = {k: d for k, d in key.items() if all("error" not in x for x in d.values())}
    for (m, d), x in sorted(ok.items(), key=lambda kv: -sum(y["eta_gate"] for y in kv[1].values())):
        h = x[26.0]
        print(f"{m:14} {d:12} " + " ".join(f"{x[v]['eta_gate']*100:7.3f}" for v in VINS)
              + f" | {h['pmos']:.2f} {h['pdio']:.2f} {h['pgate']:.3f} | {h['vdsmax']:.1f} {h['vrmax']:.1f}")
    for k, d in key.items():
        if k not in ok:
            print("HATA", k, [x.get("error") for x in d.values() if "error" in x][:1])
