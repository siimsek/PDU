#!/usr/bin/env python3
"""LTspice batch yardimcilari: netlist uret, kos, .meas sonuclarini oku, duty'yi 11 V'a ayarla.

Buradaki her sayi LTspice kosusundan okunur; analitik hesap degildir.
Parca parametreleri LTspice 26.1.1 kutuphanesindeki (standard.mos/.dio/.ind/.cap) kayitlardir;
uretici veri sayfasiyla ayrica dogrulanmamistir.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from pathlib import Path

LTSPICE = r"C:\Program Files\ADI\LTspice\LTspice.exe"
WORK = Path(__file__).with_name("calisma")
VO, IO = 11.0, 7.5
RLOAD = VO / IO

# --- LTspice kutuphane kayitlari (L[H], DCR[ohm], Rpar[ohm], Cpar[F], Ipk[A]) ---
INDUCTORS = {
    "WE-HCF 7443641000B 10u": (10e-6, 0.88e-3, 1140, 12.4e-12, 47.5),
    "WE-HCF 74436411500 15u": (15e-6, 1.33e-3, 1294, 15.0e-12, 36.0),
    "WE-HCF 74436412200 22u": (22e-6, 1.33e-3, 1395, 17.1e-12, 36.0),
    "Coilcraft AGP2923-223 22u": (22e-6, 2.24e-3, 2072, 0.0, 16.4),
    "WE-HCF 74436413300 33u": (33e-6, 1.33e-3, 1543, 18.4e-12, 36.0),
    "Coilcraft AGP4233-333 33u": (33e-6, 2.80e-3, 3109, 0.0, 25.8),
    "Coilcraft AGP4233-473 47u": (47e-6, 2.80e-3, 4427, 0.0, 18.6),
    "Coilcraft AGP4233-683 68u": (68e-6, 2.80e-3, 6406, 0.0, 13.0),
    "Bourns SRP1770TA-390M 39u": (39e-6, 40e-3, 7433, 42.7e-12, 18.0),
}
# (C[F], ESR[ohm], ESL[H], Irms[A], V)
CAPS = {
    "WCAP-PSLC 875075661008 220u/35V": (220e-6, 11.1e-3, 4.9e-9, 4.1, 35),
    "WCAP-PSLC 875075661009 270u/35V": (270e-6, 14.0e-3, 5.3e-9, 4.4, 35),
    "WCAP-PT5H 870235675007 150u/35V": (150e-6, 8.6e-3, 4.6e-9, 4.0, 35),
    "WCAP-PSLC 875075661004 100u/35V": (100e-6, 8.6e-3, 5.5e-9, 3.8, 35),
    "WCAP-PTG5 870025575009 330u/25V": (330e-6, 9.2e-3, 5.9e-9, 4.9, 25),
    "WCAP-PTG5 870025575008 270u/25V": (270e-6, 7.6e-3, 5.3e-9, 4.9, 25),
    "WCAP-PTG5 870025575007 220u/25V": (220e-6, 10.7e-3, 6.5e-9, 4.9, 25),
    "WCAP-PSLC 875075561006 150u/25V": (150e-6, 11.8e-3, 5.7e-9, 4.8, 25),
    "WCAP-PSLC 875075561005 100u/25V": (100e-6, 10.8e-3, 7.8e-9, 4.8, 25),
}


@dataclass
class Case:
    vin: float = 22.2
    f: float = 100e3
    duty: float | None = None
    ind: str = "WE-HCF 74436413300 33u"
    mos: str = "BSZ065N06LS5"
    dio: str = "RB228NS-60"
    cin: str = "WCAP-PSLC 875075661008 220u/35V"
    ncin: int = 2
    cout: str = "WCAP-PTG5 870025575009 330u/25V"
    ncout: int = 1
    rload: float = RLOAD
    vdrv: float = 10.0
    rg: float = 4.7
    rsrc: float = 20e-3      # varsayim: batarya + kablo direnci
    lsrc: float = 300e-9     # varsayim: kablo enduktansi
    lscale: float = 1.0      # tolerans carpanlari
    cscale: float = 1.0
    esrscale: float = 1.0
    dcrscale: float = 1.0
    full: bool = False       # True: ESL + 5 nH sicak cevrim enduktansi (yavas)
    lloop: float = 5e-9      # varsayim
    nmlcc: int = 0           # full modelde anahtara yakin MLCC sayisi (0 = yok)
    cmlcc: float = 4.7e-6    # varsayim: 10 uF/50 V X7R'nin 26 V DC on gerilimdeki etkin degeri
    esr_mlcc: float = 3e-3   # varsayim
    esl_mlcc: float = 0.8e-9 # varsayim
    snub_r: float = 0.0      # diyot uzerinde RC sonumleyici (0 = yok); yalniz full modelde
    snub_c: float = 0.0
    nmlcc_out: int = 0       # cikista MLCC (varsayim: 10 uF/25 V X7R, 11 V'ta etkin 8 uF, 3 mohm, 0.8 nH)
    lbulk: float = 5e-9      # varsayim: bulk kondansator ile MLCC arasi iz enduktansi
    lhot: float = 3e-9       # varsayim: MLCC-MOSFET-diyot sicak cevrimi (kilif dahil)
    cpar_off: bool = False   # True: L1 Cpar'i kaldir (kalkista I(L1) olcumunu Cpar igne akimindan arindirmak icin)
    startup: bool = False    # True: sifirdan sert kalkis
    tsim: float = 6e-3
    maxstep: float = 20e-9   # 5 ns ile karsilastirildi: verim farki <0,01 puan
    twin: float = 1e-3
    temp: float = 27.0
    extra: str = ""
    save: str = ""           # .save satiri (dalga sekli icin)
    tag: str = field(default="", compare=False)


def netlist(c: Case) -> str:
    L, dcr, rpar, cpar, _ = INDUCTORS[c.ind]
    ci, esri, esli, _, _ = CAPS[c.cin]
    co, esro, eslo, _, _ = CAPS[c.cout]
    T = 1 / c.f
    tr = 10e-9
    lpar = f"Rser={dcr * c.dcrscale:g} Rpar={rpar:g}" + (f" Cpar={cpar:g}" if cpar and not c.cpar_off else "")
    esl_i = f" Lser={esli:g}" if c.full else ""
    esl_o = f" Lser={eslo:g}" if c.full else ""
    if c.full and c.nmlcc:
        loop = (f"Lbulk vin vinh {c.lbulk:g} Rser=0.5m" + chr(10)
                + f"Cmlcc vinh 0 {c.cmlcc:g} Rser={c.esr_mlcc:g} Lser={c.esl_mlcc:g} m={c.nmlcc}" + chr(10)
                + f"Lloop vinh d {c.lhot:g} Rser=0.5m")
    elif c.full:
        loop = f"Lloop vin d {c.lloop:g} Rser=0.5m"
    else:
        loop = "Rloop vin d 0.5m"
    xtra = ''
    if c.full and c.snub_c:
        xtra += f'Rsn sw nsn {c.snub_r:g}' + chr(10) + f'Csn nsn 0 {c.snub_c:g} Lser=0.5n' + chr(10)
    if c.full and c.nmlcc_out:
        xtra += f'Coutm out 0 8u Rser=3m Lser=0.8n m={c.nmlcc_out}' + chr(10)
    iin = VO * IO / c.vin
    t0 = c.tsim - c.twin
    if c.startup:
        ic = ".ic V(out)=0 I(L1)=0 V(vin)={:g}".format(c.vin)
        tran = f".tran 0 {c.tsim:g} 0 uic"
        win = f"FROM 0 TO {c.tsim:g}"
    else:
        ic = f".ic V(out)={VO} I(L1)={VO / c.rload:g} V(vin)={c.vin - iin * c.rsrc:g} I(Lsrc)={iin:g}"
        tran = f".tran 0 {c.tsim:g} {t0 - c.twin:g} uic"
        win = f"FROM {t0:g} TO {c.tsim:g}"
    prev = f"FROM {t0 - c.twin:g} TO {t0:g}"
    m = [
        ("vo", f"avg V(out) {win}"), ("voprev", f"avg V(out) {prev}"),
        ("pin", f"avg V(vin)*I(Lsrc) {win}"), ("pout", f"avg V(out)*I(Rload) {win}"),
        ("pgate", f"avg -V(gp,sw)*I(Vdrv) {win}"),
        ("pmos", f"avg V(d,sw)*Id(M1)+V(g,sw)*Ig(M1) {win}"),
        ("pdio", f"avg -V(sw)*I(D1) {win}"), ("pind", f"avg V(sw,out)*I(L1) {win}"),
        ("pcin", f"avg V(vin)*I(Cin) {win}"), ("pcout", f"avg V(out)*I(Cout) {win}"),
        ("ilavg", f"avg I(L1) {win}"), ("ilmax", f"max I(L1) {win}"), ("ilmin", f"min I(L1) {win}"),
        ("ilrms", f"rms I(L1) {win}"), ("icinrms", f"rms I(Cin) {win}"), ("icoutrms", f"rms I(Cout) {win}"),
        ("vopp", f"pp V(out) {win}"), ("vopp20", f"pp V(outbw) {win}"), ("vinpp", f"pp V(vin) {win}"),
        ("vomax", f"max V(out) {win}"), ("vdsmax", f"max V(d,sw) {win}"), ("vgsmax", f"max V(g,sw) {win}"), ("vgsmin", f"min V(g,sw) {win}"), ("vrmax", f"max V(sw) {win}"),
        ("vswmin", f"min V(sw) {win}"), ("idmax", f"max Id(M1) {win}"), ("idrms", f"rms Id(M1) {win}"),
        ("idioavg", f"avg I(D1) {win}"), ("iinavg", f"avg I(Lsrc) {win}"), ("iinmax", f"max I(Lsrc) {win}"),
    ]
    meas = "\n".join(f".meas tran {k} {v}" for k, v in m)
    return f"""* Acik cevrim asenkron buck guc kati - araclar.py tarafindan uretildi
* vin={c.vin} f={c.f} duty={c.duty} full={c.full} startup={c.startup}
Vbat bat 0 {c.vin:g}
Rsrc bat n1 {c.rsrc:g}
Lsrc n1 vin {c.lsrc:g} Rser=1m
Cin vin 0 {ci * c.cscale:g} Rser={esri * c.esrscale:g}{esl_i} m={c.ncin}
{loop}
M1 d g sw sw {c.mos}
Vdrv gp sw PULSE(0 {c.vdrv:g} 0 {tr:g} {tr:g} {c.duty * T - tr:.6g} {T:.9g})
Rg gp g {c.rg:g}
D1 0 sw {c.dio}
L1 sw out {L * c.lscale:g} {lpar}
Cout out 0 {co * c.cscale:g} Rser={esro * c.esrscale:g}{esl_o} m={c.ncout}
Rload out 0 {c.rload:.6g}
{xtra}
* 20 MHz olcum bant siniri (osiloskop BW limit esdegeri); devreyi yuklemez
Ebw nbw 0 out 0 1
Rbw nbw outbw 1k
Cbw outbw 0 7.96p
{ic}
.lib standard.mos
.lib standard.dio
.temp {c.temp:g}
.options maxstep={c.maxstep:g}
{tran}
{c.save}
{c.extra}
{meas}
.end
"""


_MEAS = re.compile(r"^(\w+):\s.*?=\s*([-+0-9.eE]+)", re.M)


def _spice(c: Case, name: str) -> tuple[dict[str, float], str]:
    """Bir kosu. Zaman adimi kilitlenirse (nadir) once maxstep, sonra gear ile yeniden dener."""
    cir = WORK / f"{name}.cir"
    limit = (1500 if c.full else (300 if c.startup else 90)) * max(1.0, c.tsim / 6e-3)
    # Not: ayni netlist tek basina <1 s kosar; takilma paralel LTspice sureclerinde rastlantisal goruldu.
    variants = ["", "", "", ".options method=gear"]
    for k, opt in enumerate(variants):
        cir.write_text(netlist(replace(c, extra=c.extra + "\n" + opt)), encoding="latin-1")
        try:
            subprocess.run([LTSPICE, "-b", str(cir)], check=False, timeout=limit)
        except subprocess.TimeoutExpired:
            continue
        log = (WORK / f"{name}.log").read_text(encoding="latin-1", errors="replace")
        r = {a: float(b) for a, b in _MEAS.findall(log)}
        if "vo" in r and "pin" in r:
            return r, opt
    raise RuntimeError(f"{name}: kosu tamamlanamadi")


def run(c: Case, name: str, keep_raw: bool = False) -> dict[str, float]:
    WORK.mkdir(exist_ok=True)
    r, opt = _spice(c, name)
    if not keep_raw:
        for ext in (".raw", ".op.raw", ".db"):
            p = WORK / f"{name}{ext}"
            if p.exists():
                p.unlink()
    r["eta"] = r["pout"] / r["pin"]
    r["eta_gate"] = r["pout"] / (r["pin"] + r["pgate"])
    r["ploss"] = r["pin"] + r["pgate"] - r["pout"]
    r["duty"] = c.duty
    r["solver_note"] = opt
    return r


def tune(c: Case, name: str, tol: float = 2e-3, target: float = VO, keep_raw: bool = False):
    """Duty'yi ortalama cikis = target olacak sekilde ayarla (fiziksel geri besleme degil)."""
    cache = WORK / f"{name}.json"
    keyc = repr(replace(c, duty=None))
    if cache.exists() and not keep_raw:
        j = json.loads(cache.read_text())
        if j["key"] == keyc and abs(j["r"]["vo"] - target) < tol:
            return replace(c, duty=j["r"]["duty"]), j["r"]
    d = c.duty if c.duty else min(0.95, (target + 0.25) / c.vin)
    r = None
    hist = []
    for i in range(14):
        cc = replace(c, duty=d)
        r = run(cc, name, keep_raw=keep_raw)
        if abs(r["vo"] - target) < tol and abs(r["vo"] - r["voprev"]) < 2 * tol:
            break
        hist.append((d, r["vo"]))
        lo = max((h for h in hist if h[1] < target), key=lambda h: h[1], default=None)   # hedefin altindaki en yakin nokta
        hi = min((h for h in hist if h[1] > target), key=lambda h: h[1], default=None)   # hedefin ustundeki en yakin nokta
        if lo and hi:
            # hedef parantez icinde: regula falsi (CCM/DCM sinirindaki kirik egride de yakinsar)
            d = lo[0] + (target - lo[1]) * (hi[0] - lo[0]) / (hi[1] - lo[1])
            if i % 3 == 2:
                d = 0.5 * (lo[0] + hi[0])
        else:
            gain = c.vin
            if len(hist) >= 2 and abs(hist[-1][0] - hist[-2][0]) > 1e-6:
                g = (hist[-1][1] - hist[-2][1]) / (hist[-1][0] - hist[-2][0])
                if g > 0.3 * c.vin:
                    gain = g
            d = d + (target - r["vo"]) / gain
        d = min(0.98, max(0.02, d))
    r["iters"] = i + 1
    r["settled"] = abs(r["vo"] - r["voprev"])
    cache.write_text(json.dumps({"key": keyc, "r": r}))
    return cc, r


def pmap(fn, items, workers: int = 3):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, items))
