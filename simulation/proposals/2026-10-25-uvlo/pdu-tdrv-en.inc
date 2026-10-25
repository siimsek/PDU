* WP2 Tur-4 T4-05 (ChatGPT review 6398375361): CONSERVATIVE TPS48000-Q1 EN -> gate-drive enable delay (TDRV_EN) model.
* ASSUMPTION (A): TDRV = 50.8 ms treated as the maximum EN-high -> gate-drive delay, restarted after EVERY VIN-EN loss
* (VIN*REN11/(REN10+REN11) < VENF 1.14 V); the WP1 behavioral TPS48000 has no such delay. Used ONLY by tdrv-* decks (INFO).
* Mechanism: TDRV_C integrates 1 V per TDRV while the sensed VIN-EN level is above VENR 1.23 V, is discharged (tau 100 us)
* while it is below VENF 1.14 V, and a 10 ohm clamp holds EN_OVP low until TDRV_C reaches 1 V. Simulation only.
.param TDRV=50.8m
Bten TDRV_ON 0 V=min(max((V(VIN)*10/110-1.23)/0.01,0),1)
Btoff TDRV_OFF 0 V=min(max((1.14-V(VIN)*10/110)/0.01,0),1)
Btchg 0 TDRV_C I=1u/{TDRV}*V(TDRV_ON)*min(max((1.2-V(TDRV_C))/0.05,0),1)
Btdis TDRV_C 0 I=V(TDRV_C)*1e-2*V(TDRV_OFF)
Ctdrv TDRV_C 0 1u
Rtdrv TDRV_C 0 1G
Btclamp EN_OVP 0 I=V(EN_OVP)/10*(1-min(max((V(TDRV_C)-0.99)/0.01,0),1))
.meas tran TDRV_REL1 WHEN V(TDRV_C)=0.995 RISE=1
.meas tran TDRV_REL2 WHEN V(TDRV_C)=0.995 RISE=2
.meas tran TDRV_REL_LAST WHEN V(TDRV_C)=0.995 RISE=LAST
