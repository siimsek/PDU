* REGRESSION BLOCK (Tur-2 timer WITHOUT the Tur-3 CTT reset / Schmitt; used only by *noreset* decks, expect FAIL)
* WP2 2026-10-25-uvlo candidate C3: U20 TLV3202 (A = input UVLO, B = restart timer), U21 TMUX1102 hysteresis switch.
* Supplies: V5_OVP (U11 TPS7A1650) and VREF_OVP (U12 REF35409) from the WP1 OVP block. EN_BUCK = U20B via RDEN/RUV2.
* --- channel A: S_UV = VIN * divider; switched divider RXU+U21 adds hysteresis (switch ON while OUTA low = VIN not OK)
RTU VIN S_UV {RTU}
RBU S_UV 0 {RBU}
CFU S_UV 0 100n
IS_U S_UV 0 {IS_U}
RXU S_UV SWD_UV {RXU}
XU21 SWD_UV 0 0 OUTA_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C21 V5_OVP 0 100n
RR1U VREF_OVP REFD_UV {RR1U}
RR2U REFD_UV 0 {RR2U}
CRU REFD_UV 0 10n
XU20A S_UV REFD_UV V5_OVP 0 OUTA_UV UVLO_CMP VIO={VIOA} HINT={HINTA} VOHD={VOHD} VOL={VOL} IBP=0 IBN={-IM_U}
C20 V5_OVP 0 100n
* --- channel B: ratiometric restart timer. CT charges from OUTA via RTT, discharged fast by DTT+RDIS when OUTA drops.
RTT OUTA_UV T_UV {RTT}
CTT T_UV 0 {CTT}
DTT T_UV DTK_UV UVLO_1N4148WS
RDIS DTK_UV OUTA_UV 100
Bilkd OUTA_UV T_UV I={ILKD}*min(max(V(OUTA_UV,T_UV)/0.5,0),1)
RHB OUTB_UV T_UV {RHB}
RK1 V5_OVP KTH_UV {RK1}
RK2 KTH_UV 0 {RK2}
CK KTH_UV 0 10n
XU20B T_UV KTH_UV V5_OVP 0 OUTB_UV UVLO_CMP VIO={VIOB} HINT={HINTB} VOHD={VOHD} VOL={VOL}
RDEN OUTB_UV EN_BUCK 10k
* U22 TMUX1102 (2026-10-25 fix, dip0v-300us-mbmin-tmin): EN_BUCK -> GND while OUTA_UV LOW (VIN not OK).
* Stops the buck at once when UV is detected, instead of waiting for the timer comparator (CTT discharge, ~0.14 ms).
XU22 EN_BUCK 0 0 OUTA_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C22 V5_OVP 0 100n
* 1N4148WS: generic small-signal diode parameters (ASSUMPTION, typical-class; reverse leakage is Bilkd)
.model UVLO_1N4148WS D(Is=2.52n N=1.752 Rs=0.568 Cjo=4p Bv=100 Ibv=100u)
