"""G3 independent re-derivation of 10 key G2 numbers. Written without reading analysis/g2 code:
inputs are datasheet values typed here directly; methods deliberately differ (Monte Carlo, Euler, closed forms).
Run: python reports/g3/rederive.py  -> reports/g3/rederive-results.json
"""
import json
import math
import random
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_name("rederive-results.json")
random.seed(7)

# ---------------- 1/2: protection threshold (Monte Carlo corners) + timing + O1 peak by Euler
Rt, Rb = 8250.0, 2320.0
def trip(vref, rt, rb, vos, hys, ib):
    node_target = vref + vos + hys / 2
    # divider node loaded by ib into pin: Vbus*rb/(rt+rb) - ib*(rt||rb) = target
    return (node_target + ib * rt * rb / (rt + rb)) * (rt + rb) / rb
vals = []
for _ in range(200000):
    s = lambda: random.choice((-1, 1))
    dT = 100
    vref = 2.5 * (1 + s() * 0.001) * (1 + s() * 8e-6 * dT)
    rt = Rt * (1 + s() * 0.001) * (1 + s() * 15e-6 * dT)
    rb = Rb * (1 + s() * 0.001) * (1 + s() * 15e-6 * dT)
    vals.append(trip(vref, rt, rb, s() * 5e-3, random.choice((1.5e-3, 5e-3)), s() * 5e-6))
tmin, tmax = min(vals), max(vals)
k = (Rt + Rb) / Rb
t_chain = 4.5e-9 + 6.4e-9 + 40e-9 + 1.0e-6      # TLV3601 + LVC1G74 + ~RC allowance + LM74502H (all max)
vg = tmax + 0.050 * k

def o1_peak_euler(vin=26.0, v0=10.8333, L=6.8e-6 * 0.8, C=16 * 92.6514e-6 / 8 + 8.1e-6, R=0.02 + 0.0233 + 0.0075, dt=2e-10):
    i, v, t = 0.0, v0, 0.0
    t_hit = None
    while True:
        di = (vin - v - i * R) / L
        i += di * dt
        v += i / C * dt
        t += dt
        if t_hit is None and v >= vg:
            t_hit = t
        if t_hit is not None and t >= t_hit + t_chain:
            return v
o1 = o1_peak_euler()

# ---------------- 3: ILIM guaranteed sum (TPS25982 p.9 table points)
ilim_sum = 7.23 + 4.36

# ---------------- 4: UVLO rising max corner (RUV1 174k, RUV2 10k, 0.1 %, 25 ppm, EN 1.05 V max, 1 uA leak screen)
uv_hi = 1.05 * (1 + 174e3 * 1.001 * 1.0025 / (10e3 * 0.999 * 0.9975)) + 1e-6 * 174e3 * 1.001 * 1.0025
uv_lo = 0.95 * (1 + 174e3 * 0.999 * 0.9975 / (10e3 * 1.001 * 1.0025))

# ---------------- 5: inductor Isat margin at current-limit peak
rs_min = 7.5e-3 * 0.99 * (1 - 75e-6 * 65)
ipk = 0.062 / rs_min + (53.3 - 11.0) / (6.8e-6 * 0.8) * 75e-9
isat_margin = 13.5 - ipk

# ---------------- 6: F1 fault current / breaking requirement
isc = 26.0 / (0.020 + 0.005)

# ---------------- 7: PM/GM worst corners (independent Ridley implementation, numpy)
def pm_gm(vin, L, C, iload, gm, fsw, Rc=16.9e3, Cc=10e-9, Chf=22e-12):
    f = np.logspace(1, 6.3, 4000)
    s = 2j * np.pi * f
    Ri = 7.5e-3 * 10 / 2            # two phases share COMP
    Leq = L / 2
    Ts = 1 / fsw
    D = 11.0 / vin
    Sn = (vin - 11.0) / L * 7.5e-3 * 10
    Se = 24e-3 / 1e-6 * fsw / 1e6 * 10
    mc = 1 + Se / Sn
    R = 11.0 / iload
    wn = np.pi / Ts
    Q = 1 / (np.pi * (mc * (1 - D) - 0.5))
    Kp = (R / Ri) / (1 + R * Ts / Leq * (mc * (1 - D) - 0.5))
    wp = 1 / (R * C) + Ts / (Leq * C) * (mc * (1 - D) - 0.5)
    esr = 1.9204e-3 / 16
    G = Kp * (1 + s * C * esr) / (1 + s / wp) / (1 + s / (wn * Q) + (s / wn) ** 2)
    H = 10.2 / 140.2
    Zc = 1 / (1 / (Rc + 1 / (s * Cc)) + s * Chf + 1 / 10e6)
    T = G * H * gm * Zc
    mag = 20 * np.log10(abs(T))
    ph = np.degrees(np.unwrap(np.angle(T)))
    i = np.where((mag[:-1] > 0) & (mag[1:] <= 0))[0][0]
    pm = 180 + ph[i]
    j = np.where(ph < -180)[0]
    gmar = -mag[j[0]] if len(j) else 99
    return pm, gmar, f[i]
corners = []
for C in (16 * 92.6514e-6 / 8, 16 * 20.622e-6, 16 * 257.664e-6 / 8):
    for L in (6.8e-6 * 0.8, 6.8e-6 * 1.2):
        for gm in (970e-6, 1430e-6):
            for vin in (20, 26):
                for il in (0.75, 7.5):
                    for fs in (400e3, 480e3):
                        corners.append(pm_gm(vin, L, C, il, gm, fs))
pm_min = min(c[0] for c in corners)
gm_min = min(c[1] for c in corners)

# ---------------- 8: load-step bus minimum (first-order: dV = dI/(2 pi fc C) at worst corner fc*C)
fcC = min(c[2] for c in corners if True) * 16 * 257.664e-6 / 8   # lowest fc goes with largest C
dip = 6.25 / (2 * math.pi * fcC)
bus_min_est = 10.996 - dip

# ---------------- 9: loss budget: converter loss at 92 % plus external parts
pout = 11 * 7.5
conv_loss = pout / 0.92 - pout
q1 = (pout / 0.92 / 20) ** 2 * 16e-3 * 1.8
qiso = 7.5 ** 2 * 6.4e-3 * 1.8
ef = 7 ** 2 * 3.2e-3 * 1.5 + 0.5 ** 2 * 3.2e-3 * 1.5
ldo = (26 - 5) * 0.016
board = conv_loss + q1 + qiso + ef + ldo

res = {
    "trip_min_V": tmin, "trip_max_V": tmax, "t_chain_s": t_chain, "o1_peak_euler_V": o1,
    "u3u4_in_peak_V": o1, "ilim_sum_min_A": ilim_sum, "uvlo_rising_V": [uv_lo, uv_hi],
    "ilim_peak_A": ipk, "isat_margin_A": isat_margin, "f1_isc_A": isc, "pm_min_deg": pm_min, "gm_min_dB": gm_min,
    "bus_min_est_V": bus_min_est, "board_loss_W": board,
}
OUT.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
print(json.dumps(res, indent=1))
