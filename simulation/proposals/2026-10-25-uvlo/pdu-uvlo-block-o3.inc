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
* --- channel B: ratiometric restart timer. CT charges from OUTA via RTT; discharged ONLY by U24 while the U27 latch is set (Tur-5).
RTT OUTA_UV T_UV {RTT}
CTT T_UV 0 {CTT}
RHB OUTB_UV T_UV {RHB}
* --- Tur-5 UVLO-T5-01/02 (candidate): reset-dominant latch U27 instead of the Tur-3/4 RC stretcher.
* U27 SN74LVC1G74 (only the asynchronous inputs are used; D and CLK tied to GND): PRE# = OUTA_UV -> ANY VIN-OK loss,
* however short, sets Q_INH high. CLR# = U29 output, low only while CTT < V_CLR. PRE#=CLR#=L -> Q high (function table),
* so the inhibit dominates while VIN is not OK. The latch clears only when VIN is OK AND CTT has been discharged below
* V_CLR -> every restart ramps from <= V_CLR,max (no partial-reset path, no pulse-width dependence).
XU27 OUTA_UV CLR_UV QINH_UV QNINH_UV V5_OVP 0 UVLO_LVC1G74 VTR={VTRL}
C27 V5_OVP 0 100n
* U29 TLV3201 (SBOS561C, TLV3202 rows used): CLR# = (CTT > REFC_UV); REFC_UV = VREF_OVP * RC2/(RC1+RC2)
RC1 VREF_OVP REFC_UV {RC1}
RC2 REFC_UV 0 {RC2}
CRC REFC_UV 0 10n
XU29 T_UV REFC_UV V5_OVP 0 CLR_UV UVLO_CMP VIO={VIOC} HINT={HINTC} VOHD={VOHD} VOL={VOL}
C29 V5_OVP 0 100n
* U24 TMUX1101 (ON while SEL high): CTT -> RDSC -> GND while Q_INH is high
RDSC T_UV DSC_UV {RDSCL}
XU24 DSC_UV 0 0 QINH_UV V5_OVP UVLO_TMUX1101 RON={RON_U} ILK=0 VTH={VTHS}
C24 V5_OVP 0 100n
* U25 TMUX1102: RK1A in the upper threshold leg only while OUTB is LOW (Tur-3 Schmitt, unchanged)
RK1A V5_OVP K1_UV {RK1A}
XU25 K1_UV KTH_UV 0 OUTB_UV V5_OVP UVLO_TMUX1102 RON={RON_K} ILK=0 VTH={VTHS}
RK4 V5_OVP KTH_UV {RK4}
RK2 KTH_UV 0 {RK2}
CK KTH_UV 0 10n
XU20B T_UV KTH_UV V5_OVP 0 OUTB_UV UVLO_CMP VIO={VIOB} HINT={HINTB} VOHD={VOHD} VOL={VOL}
RDEN OUTB_UV EN_BUCK 10k
* U22 TMUX1102 (2026-10-25 fix, dip0v-300us-mbmin-tmin): EN_BUCK -> GND while OUTA_UV LOW (VIN not OK).
* Tur-5: U22 is a TMUX1101 driven by the latch Q_INH (EN held low until the latch clears).
XU22 EN_BUCK 0 0 QINH_UV V5_OVP UVLO_TMUX1101 RON={RON_U} ILK=0 VTH={VTHS}
C22 V5_OVP 0 100n
* U26 TMUX1102 (Tur-4 T4-05): EN_BUCK -> GND directly while OUTA_UV LOW (no latch/stretcher in the path; M3 gate).
XU26 EN_BUCK 0 0 OUTA_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C26 V5_OVP 0 100n
* U28 TMUX1102 + gate-ready qualifier (Tur-5 UVLO-T5-03): EN_BUCK -> GND until VGS(Q OVP FET) >= VRDY for TQ_GRDY.
* The qualifier is BEHAVIOURAL / ASSUMPTION (UVLO_GRDYL): its physical detector and part are NOT designed (open item).
* Latched flag: cleared while Q_INH is high, set after VGS >= VRDY for TQ_GRDY, then held until the next Q_INH.
XG28 G_OVP SRC_OVP GRDY_UV V5_OVP 0 QINH_UV UVLO_GRDYL VRDY={VRDY} TQ={TQ_GRDY}
XU28 EN_BUCK 0 0 GRDY_UV V5_OVP UVLO_TMUX1102 RON={RON_U} ILK=0
C28 V5_OVP 0 100n
