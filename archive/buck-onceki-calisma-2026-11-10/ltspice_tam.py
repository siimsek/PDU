#!/usr/bin/env python3
"""Tum devre kapali cevrim LTspice sinamasi: transistor seviyesi surucu, davranissal op-amp/karsilastirici.

Calistir: python buck/ltspice_tam.py  ->  buck/ltspice-tam-sonuc.json ve buck/buck-tam.cir
MOSFET/BJT/diyot modelleri parca secilmeden once genel VARSAYIM modelleridir. Fiziksel olcum degildir.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import kontrol as K

LT = os.environ.get("PDU_LTSPICE", r"C:\Program Files\ADI\LTspice\LTspice.exe")
TMP = Path(tempfile.mkdtemp(prefix="buck-tam-"))


def netlist(vin: float, tam_yuk: bool) -> str:
    kontrol = "PWL(0 5 70m 5 70.001m 0 80m 0 80.001m 5)" if tam_yuk else "0"
    return f"""* Ayrik buck tam devre: Vin={vin} V
V1 src 0 PWL(0 0 100u {vin})
Ls src in 1u Rser=50m
Cin in 0 440u Rser=25m
Cc in 0 9.4u Rser=3m
* guc kati
M1 sw g in in MP
Ds 0 sw DS
L1 sw out 33u Rser=20m
Cout out 0 1360u Rser=20m
Cof out 0 20u Rser=3m
RL1 out 0 14.667
RL2 out y 1.6296
SL y 0 yk 0 SWL
VY yk 0 {kontrol}
* yardimci 11.3 V
Rv in zv {K.R_VCC}
Dv 0 zv DZ12
Qv in zv cc NB
Ccc cc 0 10u
Icc cc 0 12m
* referans ve yumusak baslatma
Rr cc vr {K.R_REF}
Dr 0 vr DZ25
Rss vr ss {K.R_SS}
Css ss 0 {K.C_SS}
* ucgen
Rm1 cc vm {K.R_M}
Rm2 vm 0 {K.R_M}
Cm vm 0 100n
XI vm ni tri cc OPA
Ri sq ni {K.R_I}
Ci ni tri {K.C_I}
Rh1 tri hy {K.RH1}
Rh2 sq hy {K.RH2}
Rpu cc sq {K.R_PU_TRI}
XC1 hy vm sq CMP
* hata yukselteci, Tip III
XE ss fb comp cc OPA
R1 out fb {K.R1}
Rb fb 0 {K.RB}
R3 out n3 {K.R3}
C3 n3 fb {K.C3}
R2 fb n2 {K.R2}
C2 n2 comp {K.C2}
C1 fb comp {K.C1}
* PWM
XC2 comp tri pw CMP
Rp cc pw {K.R_PU_PWM}
Rb2 pw 0 {K.R_B_PWM}
* seviye kaydirici ve totem
QL drv pw e NB
Re e 0 {K.R_E}
Rup in drv {K.R_UP}
Qn in drv g1 NP
Qp rail drv g1 PP
Rg g1 g {K.R_G}
Rgs g in {K.R_GS}
Rz rail 0 {K.R_RAIL}
Dz rail in DZ12
Crail rail in {K.C_RAIL}
.subckt OPA p m o cc
B1 0 x I=limit(1m*(V(p)-V(m)),-300u,300u)
Rx x 0 100Meg
Cx x 0 31.8p
Dh x hc DCL
Bh hc 0 V=V(cc)-1
Dl lc x DCL
Bl lc 0 V=0.05
Bo oo 0 V=V(x)
Ro oo o 50
.model DCL D(Ron=10 Roff=1G Vfwd=0)
.ends
.subckt CMP p m o
Bx x 0 V=if(V(p)>V(m),0,1)
Rd x y 1k
Cd y 0 144p
S1 o 0 y 0 SWC
.model SWC SW(Ron=20 Roff=10Meg Vt=0.5 Vh=0.1)
.ends
.model SWL SW(Ron=1m Roff=10Meg Vt=2.5 Vh=1)
.model MP VDMOS(pchan VTO=-3 Kp=40 Rd=15m Rs=8m Cgdmax=2n Cgdmin=0.3n a=0.5 Cgs=3n Cjo=1.5n m=0.5 Is=1e-9 Rb=10m)
.model DS D(Is=1e-5 Rs=0.033 N=1 Cjo=1n BV=100 IBV=100u)
.model NB NPN(IS=1e-14 BF=100 VAF=100 CJE=25p CJC=8p TF=0.5n TR=40n RB=5)
.model NP NPN(IS=1e-13 BF=100 VAF=100 CJE=60p CJC=25p TF=0.6n TR=40n RB=1 RC=0.05 RE=0.05)
.model PP PNP(IS=1e-13 BF=100 VAF=100 CJE=60p CJC=30p TF=0.8n TR=50n RB=1 RC=0.05 RE=0.05)
.model DZ12 D(Ron=2 Roff=10Meg Vfwd=0.7 Vrev=12 Rrev=2)
.model DZ25 D(Ron=1 Roff=10Meg Vfwd=0.7 Vrev=2.5 Rrev=0.2)
.tran 0 90m 0 200n uic
.save V(out) I(L1) V(tri) V(g) V(in) V(rail) V(cc) V(comp) V(ss) I(V1) V(src)
.meas tran VSS AVG V(out) FROM 60m TO 69.9m
.meas tran VSMAX MAX V(out) FROM 60m TO 69.9m
.meas tran VSMIN MIN V(out) FROM 60m TO 69.9m
.meas tran ILMAXS MAX I(L1) FROM 60m TO 69.9m
.meas tran ILMINS MIN I(L1) FROM 60m TO 69.9m
.meas tran KALKV MAX V(out) FROM 0 TO 69.9m
.meas tran KALKI MAX I(L1) FROM 0 TO 69.9m
.meas tran UST MAX V(out) FROM 70m TO 80m
.meas tran ALT MIN V(out) FROM 80m TO 90m
.meas tran PIN AVG -V(src)*I(V1) FROM 60m TO 69.9m
.meas tran VCC AVG V(cc) FROM 60m TO 69.9m
.meas tran VGMIN MIN V(g)-V(in) FROM 60m TO 69.9m
.meas tran VGMAX MAX V(g)-V(in) FROM 60m TO 69.9m
.meas tran VCOMP AVG V(comp) FROM 60m TO 69.9m
.meas tran TPER TRIG V(tri) VAL=5.65 RISE=5000 TARG V(tri) VAL=5.65 RISE=5001
.end
"""


AD = ["VSS", "VSMAX", "VSMIN", "ILMAXS", "ILMINS", "KALKV", "KALKI", "UST", "ALT", "PIN", "VCC", "VGMIN", "VGMAX", "VCOMP", "TPER"]


def main() -> None:
    durum = [("20V", 20.0, True), ("22p2V", 22.2, True), ("26V", 26.0, True), ("26V_hafif", 26.0, False)]
    Path(__file__).with_name("buck-tam.cir").write_text(netlist(22.2, True), encoding="utf-8", newline="\n")
    isler = {}
    for ad, v, y in durum:
        p = TMP / f"{ad}.cir"
        p.write_text(netlist(v, y), encoding="utf-8", newline="\n")
        isler[ad] = (p, subprocess.Popen([LT, "-b", str(p)]))
    sonuc = {"not": "SIM; genel transistor modelleri, davranissal op-amp/karsilastirici. Fiziksel olcum degildir."}
    for ad, v, y in durum:
        p, pr = isler[ad]
        pr.wait(timeout=570)
        ham = p.with_suffix(".log").read_bytes()
        log = ham.decode("utf-16") if b"\x00" in ham[:200] else ham.decode("utf-8", "replace")
        r = {}
        for a in AD:
            m = re.search(rf"^{a.lower()}(?::.*?=|=)\s*([-\d.eE+]+)", log, re.M | re.I)
            r[a] = float(m.group(1)) if m else None
        if r["VSS"] is None:
            print("LOG", ad, log[-1500:])
        io = r["VSS"] / 1.4667 if y and r["VSS"] else (r["VSS"] / 14.667 if r["VSS"] else None)
        if r["VSS"] and r["PIN"]:
            r["POUT"] = r["VSS"] * io
            r["VERIM"] = 100 * r["POUT"] / r["PIN"]
        sonuc[ad] = r
    Path(__file__).with_name("ltspice-tam-sonuc.json").write_text(json.dumps(sonuc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(sonuc, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
