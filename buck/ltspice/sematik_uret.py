#!/usr/bin/env python3
"""buck_guc_kati.asc dosyasini uretir (LTspice sematigi, Windows-1252/ASCII).

Kullanim: python sematik_uret.py <D_22.2V> <D_20V> <D_26V>
Duty degerleri nihai_dogrulama.py LTspice kosularindan gelir.
"""
import sys
from pathlib import Path

d_nom, d_lo, d_hi = (float(x) for x in sys.argv[1:4])

W = []  # wires
def wire(*pts):
    for a, b in zip(pts, pts[1:]):
        W.append(f"WIRE {a[0]} {a[1]} {b[0]} {b[1]}")

TOP, GND = 64, 336
# ust hat
wire((-320, 128), (-320, TOP))
wire((-240, TOP), (-176, TOP))
wire((-96, TOP), (-16, TOP), (80, TOP), (128, TOP), (176, TOP))
wire((272, TOP), (336, TOP), (368, TOP), (400, TOP), (432, TOP))
wire((512, TOP), (592, TOP), (656, TOP), (704, TOP))
# dikeyler
wire((-320, 208), (-320, GND))
wire((-16, TOP), (-16, 144)); wire((-16, 208), (-16, GND))
wire((80, TOP), (80, 144)); wire((80, 208), (80, GND))
wire((256, 112), (256, 128)); wire((256, 208), (256, 224), (256, 240))
wire((336, 240), (336, TOP))
wire((400, TOP), (400, 144)); wire((400, 208), (400, GND))
wire((592, TOP), (592, 144)); wire((592, 208), (592, GND))
wire((704, TOP), (704, 144)); wire((704, 224), (704, GND))
# toprak hatti
wire((-320, GND), (-16, GND), (80, GND), (400, GND), (592, GND), (704, GND))

FLAGS = [(-320, GND, "0"), (-320, TOP, "bat"), (128, TOP, "vin"), (368, TOP, "sw"), (656, TOP, "out"),
         (256, 112, "g"), (256, 224, "gp")]

SYMS = [
    ("voltage", -320, 112, "R0", "V1", "{Vin}", None),
    ("res", -224, 48, "R90", "Rsrc", "20m", None),
    ("ind", -192, 80, "R270", "Lsrc", "300n", "Rser=1m"),
    ("polcap", -32, 144, "R0", "Cin1", "220u", "Rser=11.1m"),
    ("polcap", 64, 144, "R0", "Cin2", "220u", "Rser=11.1m"),
    ("nmos", 176, 112, "R270", "M1", "BSZ065N06LS5", None),
    ("res", 240, 112, "R0", "Rg", "10", None),
    ("voltage", 240, 240, "R270", "Vdrv", "PULSE(0 10 0 10n 10n {Ton} {Tsw})", None),
    ("schottky", 416, 208, "R180", "D1", "RBR40NS60A", None),
    ("ind", 416, 80, "R270", "L1", "33u", "Rser=1.33m Rpar=1543 Cpar=18.4p"),
    ("polcap", 576, 144, "R0", "Cout", "330u", "Rser=9.2m"),
    ("res", 688, 128, "R0", "Rload", "{RL}", None),
]

TEXT = [
    (-336, -160, 3, ";Acik cevrim asenkron buck guc kati  -  20-26 V -> 11 V / 7,5 A (82,5 W), fsw = 100 kHz"),
    (-336, -120, 2, ";M1 = BSZ065N06LS5 (60 V), D1 = RBR40NS60A (60 V Schottky), L1 = 33 uH (WE-HCF 74436413300),"
                    "\\nCIN = 2 x 220 uF/35 V polimer, COUT = 330 uF/25 V polimer. Parca degerleri LTspice kutuphane kayitlaridir."),
    (-336, -56, 2, ";Vdrv: yuzer PULSE kaynagi (gercek PWM/surucu degil). Rsrc/Lsrc: batarya+kablo varsayimi."),
    (-336, 400, 2, f"!.param Vin=22.2 fsw=100k D={d_nom:.4f} RL=1.466667\\n.param Ton=D/fsw-10n Tsw=1/fsw"),
    (-336, 464, 2, ";11,00 V icin LTspice ile ayarlanan duty:"
                   f"\\n  Vin = 20 V   -> D = {d_lo:.4f}\\n  Vin = 22,2 V -> D = {d_nom:.4f}\\n  Vin = 26 V   -> D = {d_hi:.4f}"
                   "\\nAcik cevrim: D sabitken Vin veya yuk degisirse cikis"
                   "\\n11 V'ta kalmaz. Hassas yuk baglamayin."),
    (-336, 592, 2, "!.ic V(out)=11 I(L1)=7.5 V(vin)={Vin-0.08} I(Lsrc)={82.5/Vin}\\n.tran 0 6m 5m uic\\n.options maxstep=20n"),
    (-336, 672, 2, ";Sifirdan sert kalkis icin: .ic satirini silin ve .tran 0 8m kullanin"
                   "\\n(soft-start yoktur; IL tepe ve asim buyuktur)."),
    (240, 400, 2, "!.meas tran Vo_avg avg V(out)\\n.meas tran Vo_pp pp V(out)\\n.meas tran IL_max max I(L1)\\n.meas tran IL_min min I(L1)"
                  "\\n.meas tran Pin avg V(vin)*I(Lsrc)\\n.meas tran Pout avg V(out)*I(Rload)\\n.meas tran Pgate avg -V(gp,sw)*I(Vdrv)"
                  "\\n.meas tran verim param Pout/(Pin+Pgate)\\n.meas tran P_M1 avg V(vin,sw)*Id(M1)+V(g,sw)*Ig(M1)\\n.meas tran P_D1 avg -V(sw)*I(D1)"
                  "\\n.meas tran P_L1 avg V(sw,out)*I(L1)"),
]

out = ["Version 4", "SHEET 1 1400 900"] + W
out += [f"FLAG {x} {y} {n}" for x, y, n in FLAGS]
for sym, x, y, rot, name, val, line in SYMS:
    out.append(f"SYMBOL {sym} {x} {y} {rot}")
    out.append(f"SYMATTR InstName {name}")
    out.append(f"SYMATTR Value {val}")
    if line:
        out.append(f"SYMATTR SpiceLine {line}")
for x, y, sz, t in TEXT:
    out.append(f"TEXT {x} {y} Left {sz} {t}")
p = Path(__file__).with_name("buck_guc_kati.asc")
p.write_bytes(("\r\n".join(out) + "\r\n").encode("cp1252"))
print(p)

# gorseli de guncelle: sematik ve README'deki resim ayni kaynaktan uretilir
from asc_gorsel import render
print(render(p))
