#!/usr/bin/env python3
"""buck_guc_kati.asc dosyasini uretir (LTspice sematigi, Windows-1252/ASCII).

Sade surum: yalniz deger tabanli ideal elemanlar; gercek parca modeli, .param, .meas, .ic yok.
Kullanim: python sematik_uret.py [Ton_us]     (varsayilan asagidaki TON_US)
Ton, 22,2 V giriste ortalama cikis 11 V olacak sekilde LTspice kosusuyla ayarlanmistir.
"""
import sys
from pathlib import Path

TON_US = 5.14          # 22,2 V -> 11 V icin LTspice ile ayarli iletim suresi (T = 10 us)
ton = float(sys.argv[1]) if len(sys.argv) > 1 else TON_US

W = []  # wires
def wire(*pts):
    for a, b in zip(pts, pts[1:]):
        W.append(f"WIRE {a[0]} {a[1]} {b[0]} {b[1]}")

TOP, GND = 64, 336
# ust hat
wire((-176, 128), (-176, TOP), (-16, TOP), (80, TOP), (128, TOP), (192, TOP))
wire((272, TOP), (560, TOP), (592, TOP), (624, TOP))
wire((704, TOP), (784, TOP), (848, TOP), (896, TOP))
# dikeyler
wire((-176, 208), (-176, GND))
wire((-16, TOP), (-16, 144)); wire((-16, 208), (-16, GND))
wire((80, TOP), (80, 144)); wire((80, 208), (80, GND))
wire((208, 112), (208, GND))                      # S1 kontrol (-)
wire((256, 112), (256, 176)); wire((256, 256), (256, GND))   # S1 kontrol (+) ve Vdrv
wire((592, TOP), (592, 144)); wire((592, 208), (592, GND))
wire((784, TOP), (784, 144)); wire((784, 208), (784, GND))
wire((896, TOP), (896, 144)); wire((896, 224), (896, GND))
# toprak hatti
wire((-176, GND), (-16, GND), (80, GND), (208, GND), (256, GND), (592, GND), (784, GND), (896, GND))

FLAGS = [(-176, GND, "0"), (128, TOP, "vin"), (560, TOP, "sw"), (848, TOP, "out"), (256, 144, "pwm")]

SYMS = [
    ("voltage", -176, 112, "R0", "V1", "22.2", None),
    ("polcap", -32, 144, "R0", "Cin1", "220u", "Rser=20m"),
    ("polcap", 64, 144, "R0", "Cin2", "220u", "Rser=20m"),
    ("sw", 176, 64, "R270", "S1", "SW_10m", None),
    ("voltage", 256, 160, "R0", "Vdrv", f"PULSE(0 10 0 10n 10n {ton:g}u 10u)", None),
    ("schottky", 608, 208, "R180", "D1", "D_0V5", None),
    ("ind", 608, 80, "R270", "L1", "33u", "Rser=15m"),
    ("polcap", 768, 144, "R0", "Cout", "330u", "Rser=15m"),
    ("res", 880, 128, "R0", "Rload", "1.4667", None),
]

# LTspice'in calismasi icin gereken en az yonerge: sure + ideal anahtar/diyot degerleri (parcalarin altinda)
TEXT = [
    (-192, -48, 3, ";Acik cevrim asenkron buck  -  22,2 V -> 11 V / 7,5 A, 100 kHz"),
    (-128, 384, 2, "!.tran 10m"),
    (144, 384, 2, "!.model SW_10m SW(Ron=10m Vt=5)"),
    (512, 384, 2, "!.model D_0V5 D(Ron=10m Vfwd=0.5)"),
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
