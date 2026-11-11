#!/usr/bin/env python3
"""Nihai tasarimin dogrulamasi: hat/yuk/tolerans/sicaklik, sabit duty, sert kalkis, tam parazitik model.

Butun sayilar LTspice 26.1.1 batch kosularindan okunur.
"""
import json
from pathlib import Path
import numpy as np
from araclar import Case, tune, run, pmap, replace, WORK, RLOAD
from dalga import read_raw, svg_plot

FINAL = Case(f=100e3, ind="WE-HCF 74436413300 33u", mos="BSZ065N06LS5", dio="RBR40NS60A", rg=10.0,
             cin="WCAP-PSLC 875075661008 220u/35V", ncin=2, cout="WCAP-PTG5 870025575009 330u/25V", ncout=1)
FULL = replace(FINAL, full=True, nmlcc=2, nmlcc_out=2, snub_r=2.2, snub_c=1e-9)
out = {}
S = Path("sonuc"); S.mkdir(exist_ok=True)
W = Path("dalga_sekilleri"); W.mkdir(exist_ok=True)

# 1) hat x yuk (hizli model, duty her noktada 11 V'a ayarli)
def j1(j):
    vin, k = j
    R = RLOAD / k
    ts = max(6e-3, 9 * R * 330e-6)   # hafif yukte LC sonumu yavas
    _, r = tune(replace(FINAL, vin=vin, rload=R, tsim=round(ts, 4)), f"n1_{vin:g}_{int(k*100)}".replace(".", "p"))
    return dict(vin=vin, load=k, r=r)
out["hat_yuk"] = pmap(j1, [(v, k) for v in (20.0, 22.2, 26.0) for k in (0.25, 0.5, 1.0, 1.2)] + [(22.2, 0.1)])

# 2) tolerans koseleri (hizli model)
TOL = {"nominal": {}, "L-20%": dict(lscale=0.8), "L+20%": dict(lscale=1.2), "C-20% ESRx1.5": dict(cscale=0.8, esrscale=1.5),
       "L-20% C-20% ESRx1.5 DCRx1.3": dict(lscale=0.8, cscale=0.8, esrscale=1.5, dcrscale=1.3)}
def j2(j):
    name, vin = j
    _, r = tune(replace(FINAL, vin=vin, **TOL[name]), f"n2_{list(TOL).index(name)}_{vin:g}".replace(".", "p"))
    return dict(kose=name, vin=vin, r=r)
out["tolerans"] = pmap(j2, [(n, v) for n in TOL for v in (20.0, 26.0)])

# 3) sicaklik (hizli model, Vin=22.2)
def j3(T):
    _, r = tune(replace(FINAL, vin=22.2, temp=T), f"n3_{T}")
    return dict(temp=T, r=r)
out["sicaklik"] = pmap(j3, [27, 85, 125])

# 4) sabit duty (acik cevrim) davranisi: duty 22.2 V / tam yuk icin ayarlanir, sonra sabit
cn, rn = tune(replace(FINAL, vin=22.2), "n1_22p2_100")
def j4(j):
    vin, k = j
    R = RLOAD / k
    r = run(replace(cn, vin=vin, rload=R, tsim=round(max(6e-3, 9 * R * 330e-6), 4)), f"n4_{vin:g}_{int(k*100)}".replace(".", "p"))
    return dict(vin=vin, load=k, r=r)
out["sabit_duty"] = pmap(j4, [(20.0, 1.0), (22.2, 1.0), (26.0, 1.0), (22.2, 0.5), (22.2, 0.1), (26.0, 0.1)])

# 5) tam parazitik model, 3 giris
def j5(vin):
    d0 = [x for x in out["hat_yuk"] if x["vin"] == vin and x["load"] == 1.0][0]["r"]["duty"]
    _, r = tune(replace(FULL, vin=vin, duty=d0), f"n5_full_{vin:g}".replace(".", "p"), tol=4e-3)
    return dict(vin=vin, r=r)
out["tam_parazitik"] = pmap(j5, [20.0, 22.2, 26.0], workers=3)

S.joinpath("nihai_dogrulama.json").write_text(json.dumps(out, indent=1))

# 6) dalga sekilleri: tam parazitik 26 V kararli durum + sert kalkis (hizli model)
def clip(d, t0, t1):
    t = d["time"]; m = (t >= t0) & (t <= t1)
    return {k: v[m] for k, v in d.items()}

d26 = [x for x in out["tam_parazitik"] if x["vin"] == 26.0][0]["r"]["duty"]
c = replace(FULL, vin=26.0, duty=d26, tsim=3e-3, twin=0.5e-3)
r = run(c, "w_full26", keep_raw=True)
raw = read_raw(WORK / "w_full26.raw")
te = raw["time"][-1]
w = clip(raw, te - 25e-6, te)
svg_plot(W / "kararli_durum_26V_tam_parazitik.svg", "Kararli durum, Vin=26 V, 11 V / 7,5 A, tam parazitik model (LTspice)", w["time"],
         [("V(sw), V(d,sw) [V]", [("V(sw) = diyot ters gerilimi", w["V(sw)"], "#1f77b4"), ("Vds(M1)", w["V(d)"] - w["V(sw)"], "#d62728")]),
          ("I(L1) [A]", [("I(L1)", w["I(L1)"], "#2ca02c")]),
          ("V(out) [V]", [("V(out) tam bant", w["V(out)"], "#bbbbbb"), ("V(out) 20 MHz", w["V(outbw)"], "#9467bd")]),
          ("Id(M1), I(D1) [A]", [("Id(M1)", w["Id(M1)"], "#d62728"), ("I(D1)", w["I(D1)"], "#1f77b4")])])
z = clip(raw, te - 10e-6 + (1 - 0) * 0, te)  # son periyot; acma kenari yakin plan
ton = te - 10e-6
z = clip(raw, ton - 0.05e-6, ton + 0.25e-6)
svg_plot(W / "acma_kenari_26V_tam_parazitik.svg", "M1 acma kenari, Vin=26 V, tam parazitik model (LTspice)", z["time"],
         [("[V]", [("V(sw)", z["V(sw)"], "#1f77b4"), ("Vds(M1)", z["V(d)"] - z["V(sw)"], "#d62728"), ("Vgs(M1)", z["V(g)"] - z["V(sw)"], "#ff7f0e")]),
          ("[A]", [("Id(M1)", z["Id(M1)"], "#d62728"), ("I(D1)", z["I(D1)"], "#1f77b4")])], tscale=1e9, tunit="ns")
np.savez_compressed(W / "kararli_durum_26V_tam_parazitik.npz", **{k: v.astype("f4") if k != "time" else v for k, v in w.items()})
(WORK / "w_full26.raw").unlink()
out["dalga_full26"] = r

start = {}
for vin in (20.0, 22.2, 26.0):
    dd = [x for x in out["hat_yuk"] if x["vin"] == vin and x["load"] == 1.0][0]["r"]["duty"]
    nm = "w_start" + str(vin).replace(".", "p")
    c = replace(FINAL, vin=vin, duty=dd, startup=True, cpar_off=True, tsim=8e-3, maxstep=50e-9)
    r = run(c, nm, keep_raw=True)
    raw = read_raw(WORK / (nm + ".raw"))
    n = max(1, len(raw["time"]) // 20000)
    ds = {k: v[::n] for k, v in raw.items()}
    r["t_ilmax_ms"] = float(raw["time"][int(np.argmax(raw["I(L1)"]))] * 1e3)
    r["t_vomax_ms"] = float(raw["time"][int(np.argmax(raw["V(out)"]))] * 1e3)
    svg_plot(W / ("sert_kalkis_%sV.svg" % str(vin).replace(".", "p")),
             f"Sert kalkis (soft-start yok), Vin={vin:g} V, 1,467 ohm yuk, hizli model (LTspice)", ds["time"],
             [("V(out) [V]", [("V(out)", ds["V(out)"], "#9467bd")]), ("I(L1) [A]", [("I(L1)", ds["I(L1)"], "#2ca02c")]),
              ("I(Lsrc) [A]", [("giris akimi", ds["I(Lsrc)"], "#d62728")])], tscale=1e3, tunit="ms")
    (WORK / (nm + ".raw")).unlink()
    start[vin] = r
out["sert_kalkis"] = [dict(vin=v, r=r) for v, r in start.items()]
S.joinpath("nihai_dogrulama.json").write_text(json.dumps(out, indent=1))

P = lambda *a: print(*a)
P("1) hat x yuk (duty ayarli)")
for x in sorted(out["hat_yuk"], key=lambda x: (x["vin"], x["load"])):
    r = x["r"]
    P(f" Vin={x['vin']:4} yuk={x['load']*100:3.0f}% D={r['duty']:.4f} Vo={r['vo']:.4f} eta={r['eta_gate']*100:.2f}% Pkayip={r['ploss']:.2f}W Pmos={r['pmos']:.2f} Pdio={r['pdio']:.2f} Pind={r['pind']:.2f} ILmin={r['ilmin']:.2f} ILmax={r['ilmax']:.2f} Vopp20={r['vopp20']*1e3:.1f}mV Vinpp={r['vinpp']*1e3:.0f}mV ICin={r['icinrms']:.2f}A it={r['iters']} set={r['settled']*1e3:.1f}mV")
P("2) tolerans")
for x in out["tolerans"]:
    r = x["r"]
    P(f" {x['kose']:30} Vin={x['vin']:4} eta={r['eta_gate']*100:.2f}% ILmax={r['ilmax']:.2f} Vopp20={r['vopp20']*1e3:.1f}mV Vinpp={r['vinpp']*1e3:.0f}mV ICin={r['icinrms']:.2f} ICout={r['icoutrms']:.2f}")
P("3) sicaklik (22.2 V)")
for x in out["sicaklik"]:
    r = x["r"]; P(f" T={x['temp']:3} eta={r['eta_gate']*100:.2f}% Pmos={r['pmos']:.2f} Pdio={r['pdio']:.2f} D={r['duty']:.4f}")
P(f"4) sabit duty D={cn.duty:.4f}")
for x in out["sabit_duty"]:
    r = x["r"]; P(f" Vin={x['vin']:4} yuk={x['load']*100:3.0f}% Vo={r['vo']:.3f} (onceki pencere {r['voprev']:.3f}) Vo_max={r['vomax']:.3f} Io={r['vo']/(RLOAD/x['load']):.2f}A")
P("5) tam parazitik (MLCC giris/cikis, Rg=10, RC 2.2ohm/1nF)")
for x in out["tam_parazitik"]:
    r = x["r"]
    P(f" Vin={x['vin']:4} D={r['duty']:.4f} Vo={r['vo']:.4f} eta={r['eta_gate']*100:.2f}% Vds_max={r['vdsmax']:.1f} Vr_max={r['vrmax']:.1f}"
      f" Vgs=[{r['vgsmin']:.1f},{r['vgsmax']:.1f}] Vopp={r['vopp']*1e3:.0f}mV Vopp20={r['vopp20']*1e3:.1f}mV"
      f" Pmos={r['pmos']:.2f} Pdio={r['pdio']:.2f} Pind={r['pind']:.2f} Id_max={r['idmax']:.1f}")
P("6) sert kalkis")
for x in out["sert_kalkis"]:
    r = x["r"]
    P(f" Vin={x['vin']:4} IL_max={r['ilmax']:.1f}A Vo_max={r['vomax']:.2f}V Iin_max={r['iinmax']:.1f}A Vds_max={r['vdsmax']:.1f} t_ILmax={r['t_ilmax_ms']:.2f}ms t_Vomax={r['t_vomax_ms']:.2f}ms")
