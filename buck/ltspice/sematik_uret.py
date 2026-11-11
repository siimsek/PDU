#!/usr/bin/env python3
"""buck_guc_kati.asc dosyasini uretir (LTspice sematigi, Windows-1252/ASCII).

Sade surum: yalniz deger tabanli ideal elemanlar; degerler parca numarasindan bagimsiz hedeflerdir
(buck/PARCA-HEDEFLERI.md). Gercek parca SPICE modeli, .param, .meas, .ic yok.
Kullanim: python sematik_uret.py [Ton_us]     (varsayilan asagidaki TON_US)
Ton, 24,6 V giriste (ana calisma noktasi) ortalama cikis 11 V olacak sekilde LTspice kosusuyla ayarlanmistir.
"""
import sys
from pathlib import Path

TON_US = 4.65          # 24,6 V -> 11 V icin LTspice ile ayarli iletim suresi (T = 10 us)
ton = float(sys.argv[1]) if len(sys.argv) > 1 else TON_US

W = []  # wires
def wire(*pts):
    for a, b in zip(pts, pts[1:]):
        W.append(f"WIRE {a[0]} {a[1]} {b[0]} {b[1]}")

TOP, GND = 64, 336
# ust hat
wire((-320, 128), (-320, TOP), (-160, TOP), (0, TOP), (96, TOP), (192, TOP))
wire((272, TOP), (704, TOP), (752, TOP), (784, TOP))
wire((864, TOP), (944, TOP), (1024, TOP), (1104, TOP))
# dikeyler
wire((-320, 208), (-320, GND))
wire((-160, TOP), (-160, 144)); wire((-160, 208), (-160, GND))
wire((0, TOP), (0, 144)); wire((0, 208), (0, GND))
wire((208, 112), (208, GND))                      # S1 kontrol (-)
wire((256, 112), (256, 176)); wire((256, 256), (256, GND))   # S1 kontrol (+) ve Vdrv
wire((752, TOP), (752, 144)); wire((752, 208), (752, GND))
wire((944, TOP), (944, 144)); wire((944, 208), (944, GND))
wire((1104, TOP), (1104, 144)); wire((1104, 224), (1104, GND))
# toprak hatti
wire((-320, GND), (-160, GND), (0, GND), (208, GND), (256, GND), (752, GND), (944, GND), (1104, GND))

FLAGS = [(-320, GND, "0"), (96, TOP, "vin"), (704, TOP, "sw"), (1024, TOP, "out"), (256, 144, "pwm")]

# WINDOW 39 = SpiceLine (Rser) yazisini gorunur yapar; R270 parcalarda V* hizalama yaziyi yatay tutar
CAPW = ["WINDOW 39 24 85 Left 2"]
SYMS = [
    ("voltage", -320, 112, "R0", "V1", "24.6", None, []),
    ("polcap", -176, 144, "R0", "Cin1", "1000u", "Rser=20m", CAPW),
    ("polcap", -16, 144, "R0", "Cin2", "1000u", "Rser=20m", CAPW),
    ("anahtar", 176, 64, "R270", "S1", "anahtar", "Ron=12m", ["WINDOW 0 64 56 VTop 2", "WINDOW 39 40 56 VTop 2"]),
    ("voltage", 256, 160, "R0", "Vdrv", f"PULSE(0 10 0 10n 10n {ton:g}u 10u)", None, []),
    ("diyot", 768, 208, "R180", "D1", "diyot", "Vf=0.5 Ron=10m", []),
    ("ind", 768, 80, "R270", "L1", "33u", "Rser=15m",
     ["WINDOW 0 32 56 VTop 2", "WINDOW 3 5 56 VBottom 2", "WINDOW 39 -20 56 VBottom 2"]),
    ("polcap", 928, 144, "R0", "Cout", "1000u", "Rser=25m", CAPW),
    ("res", 1088, 128, "R0", "Rload", "1.4667", None, []),
]

# Ideal anahtar/diyot tanimlari idealler.lib icindedir (anahtar.asy / diyot.asy bu dosyayi kendiliginden ekler).
# .tran sematikte kalmak zorunda: LTspice simulasyon komutunu yalniz sematik yazisindan kabul ediyor
# (lib dosyasina veya sembole tasimak denendi, Run calismadi).
TEXT = [
    (-336, -96, 3, ";Acik cevrim asenkron buck  -  24,6 V -> 11 V / 7,5 A, 100 kHz"),
    (-336, 400, 2, "!.tran 20m"),
]

out = ["Version 4", "SHEET 1 1400 900"] + W
out += [f"FLAG {x} {y} {n}" for x, y, n in FLAGS]
for sym, x, y, rot, name, val, line, win in SYMS:
    out.append(f"SYMBOL {sym} {x} {y} {rot}")
    out += win
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
