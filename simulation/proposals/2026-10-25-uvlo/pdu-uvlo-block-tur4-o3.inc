* REGRESSION BLOCK (Tur-4 RC-stretcher reset, superseded by the Tur-5 latch; used only by *tur4* decks)
* WP2 Tur-2 O3 CANDIDATE VARIANT (derived from C3 by gen_uvlo.py; ONLY change: RR1U fed by U23 REF5040 VREF_UV):
* C3: U20 TLV3202 (A = input UVLO, B = restart timer), U21 TMUX1102 hysteresis switch.
* Supplies: V5_OVP (U11 TPS7A1650) and VREF_OVP (U12 REF35409) from the WP1 OVP block. EN_BUCK = U20B via RDEN/RUV2.
* --- channel A: S_UV = VIN * divider; switched divider RXU+U21 adds hysteresis (switch ON while OUTA low = VIN not OK)
RTU VIN S_UV {RTU}
RBU S_UV 0 {RBU}
CFU S_UV 0 100n
IS_U S_UV 0 {IS_U}
RXU S_UV SWD_UV {RXU}
XU21 SWD_UV 0 0 OUTA_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C21 V5_OVP 0 100n
* U23 REF5040IDGK(T) (behavioral: VOUT = VREF_UV_P, dropout VIN-0.2 V, Iq 1.2 mA max, load regulation is inside the VREF_UV_P corner)
Bu23 VREF_UV_I 0 V=min({VREF_UV_P}, max(V(V5_OVP)-0.2,0))
Ru23 VREF_UV_I VREF_UV 1m
Iu23 V5_OVP 0 1.2m
CU23 VREF_UV 0 10u
RR1U VREF_UV REFD_UV {RR1U}
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
* --- Tur-3 UVLO-T3-02 (candidate): CTT fast reset + Schmitt timer comparator
* OUTA_D = OUTA stretched: rises slowly via RST/CST, falls fast via DST (BAT54A common anode at OUTA_D; cathodes to OUTA_UV
* and V5_OVP, the latter also discharges OUTA_D when V5 collapses). BAT54 parameters: generic (ASSUMPTION).
RST OUTA_UV OUTA_D {RST}
CST OUTA_D 0 {CST}
DST OUTA_D OUTA_UV UVLO_BAT54
DST2 OUTA_D V5_OVP UVLO_BAT54
* U24 TMUX1102: CTT -> RDSC -> GND while SEL24 = OUTA_D*RSB/(RSA+RSB) is below the TMUX logic threshold (VTHS corner).
* Holds CTT near 0 V until OUTA_D (and VIN-OK) has been stable for T_HOLD (>= 7.9 ms analytic), then the timer runs from ~0 V.
RSA OUTA_D SEL24_UV {RSA}
RSB SEL24_UV 0 {RSB}
RDSC T_UV DSC_UV {RDSC}
XU24 DSC_UV 0 0 SEL24_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0 VTH={VTHS}
C24 V5_OVP 0 100n
* U25 TMUX1102: RK1A in the upper threshold leg only while OUTB is LOW (switch ON when SEL low):
* OUTB low -> (RK1A+RON)||RK4 = RK1 eff 10.0k, threshold ~3.9 V (unchanged); OUTB high -> KTH = V5*RK2/(RK4+RK2) ~ 0.80 V,
* so after a PARTIAL CTT discharge the timer output stays high (no restart) until CTT < V_L, then a full ramp >= 67.8 ms follows.
RK1A V5_OVP K1_UV {RK1A}
XU25 K1_UV KTH_UV 0 OUTB_UV V5_OVP UVLO_TMUX1102 RON={RON_K} ILK=0 VTH={VTHS}
RK4 V5_OVP KTH_UV {RK4}
RK2 KTH_UV 0 {RK2}
CK KTH_UV 0 10n
XU20B T_UV KTH_UV V5_OVP 0 OUTB_UV UVLO_CMP VIO={VIOB} HINT={HINTB} VOHD={VOHD} VOL={VOL}
RDEN OUTB_UV EN_BUCK 10k
* U22 TMUX1102 (2026-10-25 fix, dip0v-300us-mbmin-tmin): EN_BUCK -> GND while OUTA_UV LOW (VIN not OK).
* Tur-3: SEL = OUTA_D (stretched) so EN also stays low during the reset hold.
* Stops the buck at once when UV is detected, instead of waiting for the timer comparator (CTT discharge, ~0.14 ms).
XU22 EN_BUCK 0 0 OUTA_D V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C22 V5_OVP 0 100n
* U26 TMUX1102 (Tur-4 T4-05): EN_BUCK -> GND directly while OUTA_UV LOW (no stretcher in the path; EN low <= 1 us gate M3).
XU26 EN_BUCK 0 0 OUTA_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C26 V5_OVP 0 100n
* 1N4148WS: generic small-signal diode parameters (ASSUMPTION, typical-class; reverse leakage is Bilkd)
.model UVLO_BAT54 D(Is=1e-7 N=1.05 Rs=2.4 Cjo=10p Bv=30 Ibv=2u)
.model UVLO_1N4148WS D(Is=2.52n N=1.752 Rs=0.568 Cjo=4p Bv=100 Ibv=100u)
