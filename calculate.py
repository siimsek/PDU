#!/usr/bin/env python3
"""First-order IDA PDU calculations; no vendor model."""
from math import sqrt
VOUT, LOAD_A, L_H, FS_HZ = 11.0, 7.5, 6.8e-6, 400e3
VINS = (20.0, 22.2, 25.2, 26.0)
print("Vin_V,D_ideal,Iin_at90_A,Iin_at95_A,dIL_pp_A,Ipk_at7p5A_A,IL_rms_A")
for vin in VINS:
    duty = VOUT / vin
    pout = VOUT * LOAD_A
    iin90, iin95 = pout/(vin*0.90), pout/(vin*0.95)
    ripple = VOUT*(1-duty)/(L_H*FS_HZ)
    peak = LOAD_A + ripple/2
    irms = sqrt(LOAD_A**2 + ripple**2/12)
    print(f"{vin:.1f},{duty:.4f},{iin90:.3f},{iin95:.3f},{ripple:.3f},{peak:.3f},{irms:.3f}")
plan_power = 12*5 + 12*1.5
print(f"planning_power_W={plan_power:.1f}")
print(f"planning_current_at_11V_A={plan_power/VOUT:.3f}")
print(f"target_power_W={VOUT*LOAD_A:.1f}")
print(f"power_headroom_percent={(VOUT*LOAD_A/plan_power-1)*100:.2f}")
print(f"feedback_vout_130k_10p2k_V={0.8*(1+130/10.2):.3f}")
