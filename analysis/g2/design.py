"""G2 design decisions (component values chosen by the analysis modules). Single source for SPICE, BOM and reports."""

N_COUT = 16            # TDK C5750X7S2A226M280KB; 8 existing + 8 added (Stage 4 load step + Stage 2 O1 budget)
RUV1 = 174e3           # buck EN/UVLO top (TNPW 0.1 %, 25 ppm/K)
RUV2 = 10.0e3          # buck EN/UVLO bottom
RUV_TOL = 0.001
RUV_TCR = 25e-6
RILIM_O1 = 182.0       # TPS25982 datasheet guaranteed point (7.23-9.07 A)
RILIM_S2E = 300.0      # TPS25982 datasheet guaranteed point (4.36-5.66 A)
RIMON = 806.0          # existing ERA3AEB8060V
REN_EF1 = 64.9e3       # eFuse EN/UVLO divider from VSAFE
REN_EF2 = 10.0e3
RPG_TOP = 100e3
RPG_BOT = 18e3
CDVDT = 1.0e-9
# loop compensation (Stage 4 may overwrite via loop.py results; keep in sync with tests)
RCOMP = 16.9e3         # Stage 4 selection (loop.py)
CCOMP = 10e-9
CHF = 22e-12
R_INJ = 0.0            # FRA injection resistor footprint in RFB1 leg (default 0 ohm; 49.9 ohm for FRA)
