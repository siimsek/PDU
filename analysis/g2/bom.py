"""G2 Stage 6: BOM v2, BOM-OPEN list and machine-readable schematic spec (single source: ROWS below).

Rules: an MPN is written only when the manufacturer document read in this G2 session (or the repo-verified
document noted in `ds`) confirms the series, value range/ordering code and package. Otherwise the MPN field is
empty and the row is listed in reports/g2/BOM-OPEN.md with the reason.

Net naming follows the exported netlist (/VOUT = raw buck bus "VRAW" in G2 reports). New nets: /VSAFE, /P5V_PROT,
/OVP_SENSE, /OVP_REF, /OVP_TRIP_N, /OVP_Q, /ISO_OV, /ISO_EN, /ISO_GATE, /ISO_VCAP, /CLR_N, /FB_INJ.
Run: python -m analysis.g2.bom
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from analysis.g2 import design as D

ROOT = Path(__file__).resolve().parents[2]
BOM = ROOT / "design" / "bom-v2.csv"
SPEC = ROOT / "design" / "pdu_v2_spec.yaml"
OPEN = ROOT / "reports" / "g2" / "BOM-OPEN.md"

DSD = {
    "TI_LM70880": "TI LM70880-Q1 SNVSBX7A p.1,4,6-8,16; addendum ACTIVE",
    "TI_TPS25982": "TI TPS25982 SLVSEI3D p.6-9,21; addendum ACTIVE",
    "TI_LM74700": "TI LM74700-Q1 datasheet p.5; addendum LM74700QDBVRQ1 Active/Production",
    "TI_LM74502": "TI LM74502/H SNOSDE5A p.3-6; addendum LM74502HDDFR Active/Production",
    "TI_TLV3601": "TI TLV360x SNOSDB1E p.3,5,7; addendum TLV3601DCKR Active/Production",
    "TI_REF5025A": "TI REF50xxA-Q1 SBOS456H p.4; addendum REF5025AQDRQ1 Active/Production",
    "TI_LVC1G74": "TI SN74LVC1G74 SCES794G p.4,7; addendum SN74LVC1G74DCUR Active/Production",
    "TI_TPS7A16": "TI TPS7A16-Q1 SBVS188E p.3-6; addendum TPS7A1650QDGNRQ1 Active/Production",
    "TI_CSD19531": "TI CSD19531Q5A SLPS406B p.1-2 (orderable CSD19531Q5A / CSD19531Q5AT)",
    "INF_BSC160": "Infineon BSC160N10NS3 G datasheet (repo hardware/_datasheets/bsc160n10ns3g.pdf) p.1",
    "VSH_IHLP": "Vishay doc 34509 p.1 (IHLP4040DZER6R8M01) + doc 34207",
    "VSH_WSL": "Vishay WSL doc 30100 p.1-2 (part numbering, 2512 1 W, TCR)",
    "VSH_TNPW": "Vishay TNPW e3 doc 28758 p.1-4 (0.1 % B, 15 ppm X / 25 ppm E; E96)",
    "VSH_CRCW": "Vishay CRCW e3 doc 20035 p.1-2 (1 % F, 100 ppm K; E24/E96)",
    "VSH_SS34": "Vishay SS32-SS36 doc 88751 p.1-2 (SMC; ordering pattern SS3x-E3/57T)",
    "TDK_C5750": "TDK C5750X7S2A226M280KB characterization sheet (repo) + G1 Ceff model",
    "PAN_ERA": "Panasonic ERA-3AEB (repo BOM 'manufacturer verified'; not re-read in G2)",
}

FP_LIB = "KiCad standard library footprint (IPC-7351 nominal)"


def r(ref, value, mpn, ds, tol, tcr, pkg, fp, fp_src, nets, p_applied, p_rating, note="", dnp=False, custom=False):
    return dict(ref=ref, kind="R", value=value, mpn=mpn, manufacturer="Vishay" if mpn.startswith(("TNPW", "CRCW", "WSL"))
                else ("Panasonic" if mpn.startswith("ERA") else ""), datasheet=DSD.get(ds, ds), tolerance=tol, tcr=tcr,
                package=pkg, footprint=fp, footprint_source=fp_src, custom_footprint=custom, nets=nets,
                v_applied="", v_rating="", p_applied_W=p_applied, p_rating_W=p_rating,
                derating=(p_applied / p_rating) if p_rating else None, lifecycle="doğrulanamadı (Vishay/Panasonic web stok sorgusu yapılmadı)",
                note=note, dnp=dnp)


def c(ref, value, mpn, ds, v_app, v_rat, pkg, fp, nets, note="", dielectric="X7R", dnp=False, custom=False, fp_src=FP_LIB):
    return dict(ref=ref, kind="C", value=value, mpn=mpn, manufacturer="TDK" if mpn.startswith("C5750") else "",
                datasheet=DSD.get(ds, ds), tolerance="", tcr=dielectric, package=pkg, footprint=fp, footprint_source=fp_src,
                custom_footprint=custom, nets=nets, v_applied=v_app, v_rating=v_rat, p_applied_W="", p_rating_W="",
                derating=(v_app / v_rat) if v_rat else None, lifecycle="doğrulanamadı" if not mpn else "doğrulanamadı (stok sorgusu yok)",
                note=note, dnp=dnp)


def u(ref, value, mpn, ds, pkg, fp, fp_src, pins, kind="U", v_app="", v_rat="", note="", custom=False, mfr="Texas Instruments"):
    life = "ACTIVE/Production (TI datasheet package addendum)" if mfr == "Texas Instruments" and "ACTIVE" in DSD.get(ds, ds).upper() + "ACTIVE" else ""
    return dict(ref=ref, kind=kind, value=value, mpn=mpn, manufacturer=mfr, datasheet=DSD.get(ds, ds), tolerance="", tcr="",
                package=pkg, footprint=fp, footprint_source=fp_src, custom_footprint=custom, nets=pins, v_applied=v_app,
                v_rating=v_rat, p_applied_W="", p_rating_W="",
                derating=(v_app / v_rat) if (v_app and v_rat) else None, lifecycle=life or "doğrulanamadı", note=note, dnp=False)


R0603 = "Resistor_SMD:R_0603_1608Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"


def tnpw(size, val_code, tcr="X"):
    return f"TNPW{size}{val_code}B{tcr}EA"


def crcw(size, val_code):
    return f"CRCW{size}{val_code}FKEA"


def rows():
    R = []
    # ---------------- input
    R.append(dict(ref="F1", kind="F", value="10 A DC, >=53.3 VDC, >=1040 A breaking", mpn="", manufacturer="", datasheet="",
                  tolerance="", tcr="", package="", footprint="", footprint_source="AÇIK", custom_footprint=True,
                  nets={"1": "/VBAT", "2": "/F1_OUT"}, v_applied=26.0, v_rating="", p_applied_W="", p_rating_W="",
                  derating=None, lifecycle="doğrulanamadı", note="Fuse vendor datasheets not reachable (403/DNS)", dnp=False))
    R.append(dict(ref="D1", kind="D", value="TVS SMCJ33A family (VRWM 33 V)", mpn="", manufacturer="", datasheet="",
                  tolerance="", tcr="", package="SMC", footprint="Diode_SMD:D_SMC", footprint_source=FP_LIB, custom_footprint=False,
                  nets={"A": "/GND", "K": "/ANODE"}, v_applied=26.0, v_rating=33.0, p_applied_W="", p_rating_W="",
                  derating=26.0 / 33.0, lifecycle="doğrulanamadı", note="Vishay/Littelfuse SMCJ datasheet not reachable; VRWM>VIN_max only", dnp=False))
    R.append(u("U5", "LM74700-Q1", "LM74700QDBVRQ1", "TI_LM74700", "SOT-23-6 (DBV)", "Package_TO_SOT_SMD:SOT-23-6", FP_LIB,
               {"1": "/VCAP", "2": "/GND", "3": "/ANODE(EN)", "4": "/GATE", "5": "/ANODE", "6": "/VIN(CATHODE)"},
               v_app=53.3, v_rat=65.0, note="pin map per TI DBV table; verify against KiCad symbol before transfer"))
    R.append(u("Q1", "100 V N-MOSFET", "BSC160N10NS3G", "INF_BSC160", "PG-TDSON-8", "PDU:TDSON-8-1_Konnect", "repo custom land (G1: adapted, final land/paste acceptance open)",
               {"S": "/ANODE", "G": "/GATE", "D": "/VIN"}, kind="Q", v_app=53.3, v_rat=100.0, mfr="Infineon", custom=True))
    R.append(c("CIN_U5", "22n", "", "", 26.0, 100.0, "0603", C0603, {"1": "/ANODE", "2": "/GND"}, note="rating >=53.3 V required"))
    for i in range(1, 9):
        R.append(c(f"CIN{i}", "4.7u", "", "", 26.0, 100.0, "1210", C1210, {"1": "/VIN", "2": "/GND"},
                   note="100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption)"))
    R.append(c("CBIN1", "10n", "", "", 26.0, 100.0, "0603", C0603, {"1": "/VIN", "2": "/GND"}))
    R.append(c("CBIN2", "10n", "", "", 26.0, 100.0, "0603", C0603, {"1": "/VIN", "2": "/GND"}))
    R.append(c("CVCAP", "100n", "", "", 15.0, 50.0, "0603", C0603, {"1": "/VCAP", "2": "/ANODE"}))
    # ---------------- buck
    for k in (1, 2):
        R.append(u(f"U{k}", "LM70880-Q1", "LM70880QRRXRQ1", "TI_LM70880", "VQFN-29 (RRX)", "PDU:LM70880_RRX0029B_RectLands",
                   "repo custom land (G1: copper approach/paste acceptance open)",
                   {"VIN": "/VIN", "SW": f"/SW_PH{k}", "CBOOT": f"/CBOOT{k}", "ISNS+": f"/ISNS{k}", "VOUT": "/VOUT",
                    "EN/UVLO": "/EN_BUCK", "EXTCOMP": "/COMP", "FB": "/FB", "RT": f"/RT_PH{k}", "VCC": f"/VCC{k}",
                    "VDDA": f"/VDDA{k}", "CONFIG": "/CFG_PRI" if k == 1 else "/CFG_SEC",
                    "PG/SYNCOUT": "/SYNC" if k == 1 else "NC", "PFM/SYNCIN": "/GND" if k == 1 else "/SYNC"},
                   v_app=53.3, v_rat=87.5, custom=True))
        R.append(dict(ref=f"L{k}", kind="L", value="6.8uH", mpn="IHLP4040DZER6R8M01", manufacturer="Vishay Dale",
                      datasheet=DSD["VSH_IHLP"], tolerance="20%", tcr="", package="IHLP-4040DZ", footprint="Inductor_SMD:L_Vishay_IHLP-4040",
                      footprint_source="KiCad lib vs Vishay doc 34207 typical pad layout p.1 (compare; G1 open)", custom_footprint=False,
                      nets={"1": f"/SW_PH{k}", "2": f"/ISNS{k}"}, v_applied=26.0, v_rating=75.0, p_applied_W=0.47,
                      p_rating_W="", derating=26.0 / 75.0, lifecycle="doğrulanamadı",
                      note="Irms 4.21 A vs Iheat 8 A typ; Ilim peak 8.97 A vs Isat 13.5 A typ", dnp=False))
        R.append(r(f"RS{k}", "7.5m", "WSL25127L500FEA", "VSH_WSL", "1%", "75ppm/K", "2512", "Resistor_SMD:R_2512_6332Metric",
                   FP_LIB + "; Kelvin escape per LM70880 p.16", {"1": f"/ISNS{k}", "2": "/VOUT"}, 0.134, 1.0))
        R.append(c(f"CBOOT{k}", "47n", "", "", 8.5, 25.0, "0603", C0603, {"1": f"/CBOOT{k}", "2": f"/SW4_PH{k}"},
                   note="LM70880 p.4 recommends 47 nF"))
        R.append(r(f"RBOOT{k}", "1", crcw("0603", "1R00"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/CBOOT{k}", "2": f"/SW4_PH{k}"}, 0.01, 0.1, note="series 1 ohm (VCC=8 V option, LM70880 p.4)"))
        R.append(r(f"RT{k}", "49.9k", crcw("0603", "49K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/RT_PH{k}", "2": "/GND"}, 1e-4, 0.1))
        R.append(c(f"CVCC{k}", "4.7u", "", "", 8.5, 25.0, "0805", C0805, {"1": f"/VCC{k}", "2": "/GND"}))
        R.append(c(f"CVDDA{k}", "100n", "", "", 5.25, 25.0, "0603", C0603, {"1": f"/VDDA{k}", "2": "/GND"}))
    R.append(r("RCFG1", "54.9k", crcw("0603", "54K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/CFG_PRI", "2": "/GND"}, 1e-4, 0.1))
    R.append(r("RCFG2", "90.9k", crcw("0603", "90K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/CFG_SEC", "2": "/GND"}, 1e-4, 0.1))
    R.append(r("RSYNC", "100k", crcw("0603", "100K"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/SYNC", "2": "/VDDA1"}, 1e-4, 0.1))
    R.append(r("RFB1", "130k", "ERA3AEB134V", "PAN_ERA", "0.1%", "25ppm/K", "0603", R0603, FP_LIB, {"1": "/VOUT", "2": "/FB_INJ"}, 1e-3, 0.1))
    R.append(r("R_INJ", "0", crcw("0603", "0000Z0"[:4]).replace("FKEA", "Z0EA"), "VSH_CRCW", "jumper", "", "0603", R0603, FP_LIB,
               {"1": "/FB_INJ", "2": "/FB"}, 0.0, 0.1, note="FRA injection: replace with 49.9 ohm for bench FRA (TP_FB_INJ_A/B)"))
    R.append(r("RFB2", "10.2k", "ERA3AEB1022V", "PAN_ERA", "0.1%", "25ppm/K", "0603", R0603, FP_LIB, {"1": "/FB", "2": "/GND"}, 1e-4, 0.1))
    R.append(r("RCOMP", "16.9k", crcw("0603", "16K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB,
               {"1": "/COMP", "2": "/COMP_MID"}, 1e-5, 0.1, note="G2 Stage 4; bench range 10-33k"))
    R.append(c("CCOMP", "10n", "", "", 2.1, 25.0, "0603", C0603, {"1": "/COMP_MID", "2": "/GND"}, note="G2 Stage 4; C0G/X7R; bench 2.2-10 nF"))
    R.append(c("CHF", "22p", "", "", 2.1, 50.0, "0603", C0603, {"1": "/COMP", "2": "/GND"}, dielectric="C0G", note="G2 Stage 4; bench 22-100 pF"))
    R.append(r("RUV1", "174k", tnpw("0603", "174K", "E"), "VSH_TNPW", "0.1%", "25ppm/K", "0603", R0603, FP_LIB,
               {"1": "/VIN", "2": "/EN_BUCK"}, 26 ** 2 / 184e3, 0.1, note="20 V restart: 17.365-19.623 V (power.py)"))
    R.append(r("RUV2", "10k", tnpw("0603", "10K0", "E"), "VSH_TNPW", "0.1%", "25ppm/K", "0603", R0603, FP_LIB,
               {"1": "/EN_BUCK", "2": "/GND"}, 2e-4, 0.1))
    for i in range(1, D.N_COUT + 1):
        R.append(c(f"COUT{i}", "22u", "C5750X7S2A226M280KB", "TDK_C5750", 11.16, 100.0, "2220", "PDU:TDK_C5750_2220_Recommended",
                   {"1": "/VOUT", "2": "/GND"}, dielectric="X7S", custom=True,
                   fp_src="repo custom land (TDK recommended; prototype-accepted per docs/design.md)",
                   note="new (G2: COUT9-16 added)" if i > 8 else "existing"))
    R.append(r("RRAWBL", "10k", crcw("0805", "10K0"), "VSH_CRCW", "1%", "100ppm/K", "0805", R0805, FP_LIB,
               {"1": "/VOUT", "2": "/GND"}, 26 ** 2 / 10e3, 0.125 * 1.0, note="raw bus bleeder (fault 26 V: 68 mW -> 0805 54 %: use 1206)" ))
    # ---------------- isolator chain
    R.append(u("U6", "LM74502H", "LM74502HDDFR", "TI_LM74502", "SOT-23-THIN-8 (DDF)", "Package_TO_SOT_SMD:SOT-23-8", FP_LIB + " (verify DDF land vs TI)",
               {"1": "/ISO_EN", "2": "/GND", "3": "NC", "4": "/ISO_VCAP", "5": "/VOUT", "6": "/ISO_GATE", "7": "/ISO_OV", "8": "/VSAFE"},
               v_app=53.3, v_rat=65.0))
    R.append(u("Q2", "100 V N-MOSFET", "CSD19531Q5A", "TI_CSD19531", "SON 5x6", "Package_SON:Texas_VSON-8-1EP_5x6mm", FP_LIB + " (verify vs TI land p.8)",
               {"1-3": "/VSAFE", "4": "/ISO_GATE", "5-8": "/VOUT"}, kind="Q", v_app=53.3, v_rat=100.0))
    R.append(r("R_GS", "100k", crcw("0603", "100K"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/ISO_GATE", "2": "/VSAFE"}, 0.002, 0.1))
    R.append(c("C_ISO_VCAP", "100n", "", "", 14.0, 50.0, "0603", C0603, {"1": "/ISO_VCAP", "2": "/VOUT"}, note="LM74502H VCAP-VS >=0.1 uF (p.4)"))
    R.append(c("C_ISO_VS", "100n", "", "", 11.16, 100.0, "0603", C0603, {"1": "/VOUT", "2": "/GND"}, note="LM74502H VS 100 nF (p.3); derating vs continuous bus, fault peak (SIM) < 100 V rating"))
    R.append(r("R_OVT", "8.25k", tnpw("1206", "8K25"), "VSH_TNPW", "0.1%", "15ppm/K", "1206", R1206, FP_LIB,
               {"1": "/VOUT", "2": "/OVP_SENSE"}, 0.050, 0.25, note="26 V continuous 0.050 W; 53.3 V transient 0.21 W"))
    R.append(r("R_OVB", "2.32k", tnpw("1206", "2K32"), "VSH_TNPW", "0.1%", "15ppm/K", "1206", R1206, FP_LIB,
               {"1": "/OVP_SENSE", "2": "/GND"}, 0.014, 0.25))
    R.append(u("U7", "TLV3601", "TLV3601DCKR", "TI_TLV3601", "SC70-5 (DCK)", "Package_TO_SOT_SMD:SOT-353_SC-70-5", FP_LIB,
               {"1": "/OVP_TRIP_N", "2": "/GND", "3": "/OVP_REF", "4": "/OVP_SENSE", "5": "/P5V_PROT"}))
    R.append(c("C_CMP", "100n", "", "", 5.1, 25.0, "0603", C0603, {"1": "/P5V_PROT", "2": "/GND"}))
    R.append(u("U8", "REF5025A-Q1", "REF5025AQDRQ1", "TI_REF5025A", "SOIC-8 (D)", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", FP_LIB,
               {"2": "/P5V_PROT", "3": "NC(TEMP)", "4": "/GND", "5": "/REF_NR", "6": "/OVP_REF", "1": "DNC", "7": "NC", "8": "DNC"}))
    R.append(c("C_REF_IN", "1u", "", "", 5.1, 25.0, "0603", C0603, {"1": "/P5V_PROT", "2": "/GND"}))
    R.append(c("C_REF_OUT", "1u", "", "", 2.5, 25.0, "0603", C0603, {"1": "/OVP_REF", "2": "/GND"}, note="datasheet test CL=1 uF (p.4)"))
    R.append(c("C_REF_NR", "1u", "", "", 2.5, 25.0, "0603", C0603, {"1": "/REF_NR", "2": "/GND"}, dnp=True, note="TRIM/NR optional"))
    R.append(u("U9", "SN74LVC1G74", "SN74LVC1G74DCUR", "TI_LVC1G74", "VSSOP-8 (DCU)", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", FP_LIB,
               {"1": "/GND(CLK)", "2": "/P5V_PROT(D)", "3": "NC(Qbar)", "4": "/GND", "5": "/OVP_Q", "6": "/CLR_N", "7": "/OVP_TRIP_N(PRE)", "8": "/P5V_PROT"}))
    R.append(c("C_LAT", "100n", "", "", 5.1, 25.0, "0603", C0603, {"1": "/P5V_PROT", "2": "/GND"}))
    R.append(r("R_CLR", "100k", crcw("0603", "100K"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/P5V_PROT", "2": "/CLR_N"}, 3e-4, 0.1))
    R.append(c("C_CLR", "1u", "", "", 5.1, 25.0, "0603", C0603, {"1": "/CLR_N", "2": "/GND"}, note="POR ~120 ms"))
    R.append(dict(ref="SW1", kind="SW", value="momentary reset, SPST-NO", mpn="", manufacturer="", datasheet="", tolerance="", tcr="",
                  package="", footprint="", footprint_source="AÇIK", custom_footprint=False, nets={"1": "/CLR_N", "2": "/GND"},
                  v_applied=5.0, v_rating="", p_applied_W="", p_rating_W="", derating=None, lifecycle="doğrulanamadı",
                  note="G1 candidate Omron B3U-1000P not re-read in G2", dnp=False))
    R.append(r("R_Q", "10k", crcw("0603", "10K0"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/OVP_Q", "2": "/ISO_OV"}, 1e-3, 0.1))
    R.append(r("R_OV2T", "64.9k", crcw("0603", "64K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/VOUT", "2": "/ISO_OV"},
               (26 - 2) ** 2 / 64.9e3, 0.1, note="coarse OV 11.55-13.70 V"))
    R.append(r("R_OV2B", "24.9k", crcw("0603", "24K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/ISO_OV", "2": "/GND"}, 3e-4, 0.1))
    R.append(r("R_EN1", "15k", crcw("0603", "15K0"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/P5V_PROT", "2": "/ISO_EN"}, 1e-3, 0.1))
    R.append(r("R_EN2", "10k", crcw("0603", "10K0"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/ISO_EN", "2": "/GND"}, 4e-4, 0.1))
    R.append(u("U10", "TPS7A1650-Q1", "TPS7A1650QDGNRQ1", "TI_TPS7A16", "HVSSOP-8 (DGN)", "Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm",
               FP_LIB + " (verify DGN exposed pad vs TI)", {"8": "/VIN", "1": "/P5V_PROT", "2": "NC", "3": "/CLR_N(PG)", "4": "/GND",
                                                            "5": "/VIN(EN)", "6": "NC", "7": "/LDO_DELAY"}, v_app=53.3, v_rat=60.0))
    R.append(c("C_LDO_IN", "1u", "", "", 26.0, 100.0, "1206", C1206, {"1": "/VIN", "2": "/GND"}, note="TI recommends 10 uF at IN (p.3); 1 uF local + CIN bank"))
    R.append(c("C_LDO_OUT", "2.2u", "", "", 5.1, 25.0, "0805", C0805, {"1": "/P5V_PROT", "2": "/GND"}, note="datasheet test COUT=2.2 uF"))
    R.append(c("C_LDO_DELAY", "10n", "", "", 5.0, 25.0, "0603", C0603, {"1": "/LDO_DELAY", "2": "/GND"}, dnp=True))
    R.append(r("R_BL5", "1k", crcw("1206", "1K00"), "VSH_CRCW", "1%", "100ppm/K", "1206", R1206, FP_LIB, {"1": "/P5V_PROT", "2": "/GND"},
               5.1 ** 2 / 1e3, 0.25, note="bleeder for clamp back-power (R07)"))
    # ---------------- VSAFE and eFuses
    R.append(r("R_BLS", "4.7k", crcw("1206", "4K70"), "VSH_CRCW", "1%", "100ppm/K", "1206", R1206, FP_LIB, {"1": "/VSAFE", "2": "/GND"},
               11.6 ** 2 / 4.7e3, 0.25, note="VSAFE bleeder (R16)"))
    for k, port, ilim, rl in ((3, "O1", D.RILIM_O1, "182R"), (4, "S2E", D.RILIM_S2E, "300R")):
        idx = 1 if port == "O1" else 2
        R.append(u(f"U{k}", "TPS259824O", "TPS259824ONRGER", "TI_TPS25982", "VQFN-24 (RGE)", "PDU:TPS25982_RGE0024M", "repo custom land",
                   {"IN": "/VSAFE", "OUT": f"/{port}_11V", "EN/UVLO": "/EN_EFUSE", "ILIM": f"/ILIM_{port}", "IMON": f"/IMON_{port}",
                    "dVdt": f"/DVDT_{port}", "PG": f"/PG_{port}", "GND": "/GND"}, v_app=11.6, v_rat=30.0, custom=True,
                   note="IN moved from /VOUT to /VSAFE (G2); repo had ...NRGET (250 pcs) - both orderables in TI addendum"))
        R.append(r(f"RILIM{idx}", str(int(ilim)), tnpw("0603", rl), "VSH_TNPW", "0.1%", "15ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/ILIM_{port}", "2": "/GND"}, 1e-4, 0.1, note="TPS25982 p.9 guaranteed table point"))
        R.append(r(f"RIMON{idx}", "806", "ERA3AEB8060V", "PAN_ERA", "0.1%", "25ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/IMON_{port}", "2": "/GND"}, 1e-3, 0.1))
        R.append(c(f"CDVDT{idx}", "1.0n", "", "", 15.6, 50.0, "0603", C0603, {"1": f"/DVDT_{port}", "2": "/GND"}, note="sees VIN+4 V (TPS25982 p.21)"))
        R.append(c(f"CEFIN{idx}", "100n", "", "", 11.6, 50.0, "0603", C0603, {"1": "/VSAFE", "2": "/GND"}))
        R.append(c(f"CEFOUT{idx}", "10u", "", "", 11.6, 25.0, "0805", C0805, {"1": f"/{port}_11V", "2": "/GND"},
                   note="25 V 0805: 46 % of rating; Ceff assumed 40 % (DC-bias datasheet not available)"))
        R.append(r(f"RPG{idx}", "100k", crcw("0603", "100K"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/{port}_11V", "2": f"/PG_{port}"}, 1e-3, 0.1))
        R.append(r(f"RPG{idx}B", "18k", crcw("0603", "18K0"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB,
                   {"1": f"/PG_{port}", "2": "/GND"}, 2e-4, 0.1))
        R.append(dict(ref=f"D_REV{idx}", kind="D", value="Schottky 40 V 3 A", mpn="SS34-E3/57T", manufacturer="Vishay General Semiconductor",
                      datasheet=DSD["VSH_SS34"], tolerance="", tcr="", package="SMC (DO-214AB)", footprint="Diode_SMD:D_SMC",
                      footprint_source=FP_LIB, custom_footprint=False, nets={"A": f"/{port}_11V", "K": "/VSAFE"},
                      v_applied=0.05, v_rating=40.0, p_applied_W="", p_rating_W="", derating=0.05 / 40, lifecycle="doğrulanamadı",
                      note="OUT->IN clamp for TPS25982 OUT<=VIN+0.3 V (R16); Vf at mA level typical only", dnp=False))
        R.append(dict(ref=f"D{1 + idx}", kind="D", value="Schottky 40 V 3 A", mpn="SS34-E3/57T", manufacturer="Vishay General Semiconductor",
                      datasheet=DSD["VSH_SS34"], tolerance="", tcr="", package="SMC (DO-214AB)", footprint="Diode_SMD:D_SMC",
                      footprint_source=FP_LIB, custom_footprint=False, nets={"A": "/GND", "K": f"/{port}_11V"},
                      v_applied=11.6, v_rating=40.0, p_applied_W="", p_rating_W="", derating=11.6 / 40, lifecycle="doğrulanamadı",
                      note="footprint changes SMA -> SMC (Vishay SS34 is SMC)", dnp=False))
    R.append(r("REN1", "64.9k", crcw("0603", "64K9"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/VSAFE", "2": "/EN_EFUSE"}, 2e-3, 0.1))
    R.append(r("REN2", "10k", crcw("0603", "10K0"), "VSH_CRCW", "1%", "100ppm/K", "0603", R0603, FP_LIB, {"1": "/EN_EFUSE", "2": "/GND"}, 3e-4, 0.1))
    # ---------------- connectors
    for ref, net, i_a in (("J1", "/VBAT", 4.48), ("J2", "/O1_11V", 7.0), ("J3", "/S2E_11V", 1.5)):
        R.append(dict(ref=ref, kind="J", value=f"2-pin power, >={i_a} A continuous", mpn="", manufacturer="Molex (Micro-Fit 3.0 family, G1)",
                      datasheet="Molex PS-43045-001 not reachable in G2", tolerance="", tcr="", package="",
                      footprint="Connector_Molex:Molex_Micro-Fit_3.0_43045-0200_2x01_P3.00mm_Horizontal", footprint_source=FP_LIB,
                      custom_footprint=False, nets={"1": net, "2": "/GND"}, v_applied=26.0 if ref == "J1" else 11.6, v_rating="",
                      p_applied_W="", p_rating_W="", derating=None, lifecycle="doğrulanamadı",
                      note="header + mating housing + crimp + wire gauge set must be selected together", dnp=False))
    return R


def fix_rows(R):
    for row in R:
        if row["ref"] == "RRAWBL":   # applied 68 mW -> use 1206 (0.25 W) for <=50 %
            row.update(package="1206", footprint=R1206, mpn=crcw("1206", "10K0"), p_rating_W=0.25,
                       derating=row["p_applied_W"] / 0.25, note="raw bus bleeder; 26 V fault 68 mW -> 27 %")
        if row["ref"] == "R_INJ":
            row["mpn"] = "CRCW06030000Z0EA"
            row["note"] = "jumper (0 ohm) per CRCW doc 20035 p.2 example; replace with 49.9 ohm for FRA"
    return R


def main():
    R = fix_rows(rows())
    cols = ["ref", "kind", "value", "mpn", "manufacturer", "datasheet", "tolerance", "tcr", "package", "footprint",
            "footprint_source", "custom_footprint", "v_applied", "v_rating", "p_applied_W", "p_rating_W", "derating",
            "derating_ok", "lifecycle", "dnp", "note"]
    for row in R:
        d = row["derating"]
        row["derating_ok"] = "" if d is None else ("yes" if d <= 0.5 else ("NO (>50 %)" if row["kind"] in ("R", "C") else f"{d:.0%} of abs max"))
    with BOM.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in R:
            w.writerow({k: (f"{row[k]:.4g}" if isinstance(row.get(k), float) else row.get(k, "")) for k in cols})
    open_rows = [row for row in R if not row["mpn"]]
    over = [row for row in R if row["derating_ok"].startswith("NO")]
    lines = ["# G2 BOM — MPN seçilemeyen satırlar", "",
             "Kaynak: [`design/bom-v2.csv`](../../design/bom-v2.csv), üretici: [`analysis/g2/bom.py`](../../analysis/g2/bom.py). "
             "MPN yalnız bu G2 oturumunda okunan resmi üretici belgesi seri/değer/paket/sipariş kodunu doğruladığında yazıldı.", "",
             f"Toplam satır: **{len(R)}**; MPN'li: **{len(R) - len(open_rows)}**; MPN AÇIK: **{len(open_rows)}**.", "",
             "| Ref | Değer / gereksinim | Neden seçilemedi | Gereken belge |", "|---|---|---|---|"]
    reason = {"C": ("MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu "
                    "kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok", "Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi"),
              "F": ("Sigorta üretici datasheet'leri erişilemedi (Littelfuse 403/DNS); kaynak kısa devre akımı 127–1040 A", "Sigorta + yuva datasheet'i (DC kesme, I²t)"),
              "D": ("TVS datasheet'i erişilemedi", "SMCJ33A resmi datasheet'i (Vishay/Littelfuse)"),
              "J": ("Molex PS-43045 sunucusu bağlantıyı reddetti", "Molex PS-43045-001 + mating housing/crimp"),
              "SW": ("G1 adayı bu turda okunmadı", "Buton datasheet'i")}
    for row in open_rows:
        rs, doc = reason.get(row["kind"], ("", ""))
        lines.append(f"| {row['ref']} | {row['value']} {('— ' + row['note']) if row['note'] else ''} | {rs} | {doc} |")
    lines += ["", "## Derating uyarıları", ""]
    if over:
        for row in over:
            lines.append(f"- {row['ref']}: {row['derating']:.0%} > %50")
    else:
        lines.append("- R/C satırlarında %50 sınırını aşan uygulama yok (MPN'siz C satırları için gereken anma gerilimi `v_rating` sütununda).")
    lines += ["", "## Özel footprint gereken satırlar", ""]
    for row in R:
        if row["custom_footprint"]:
            lines.append(f"- {row['ref']} ({row['mpn'] or row['value']}): {row['footprint'] or 'AÇIK'} — {row['footprint_source']}")
    OPEN.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    # spec yaml (hand-rolled, no dependency)
    y = ["# PDU v2 machine-readable schematic summary (generated by analysis/g2/bom.py)",
         "# /VOUT is the raw buck bus (VRAW in G2 reports); /VSAFE is the isolator output feeding both eFuse IN pins.",
         f"n_rows: {len(R)}", "parts:"]
    for row in R:
        y.append(f"  - ref: {row['ref']}")
        y.append(f"    value: \"{row['value']}\"")
        y.append(f"    mpn: \"{row['mpn']}\"")
        y.append(f"    footprint: \"{row['footprint']}\"")
        y.append(f"    dnp: {str(bool(row['dnp'])).lower()}")
        y.append("    pins:")
        for pin, net in row["nets"].items():
            y.append(f"      \"{pin}\": \"{net}\"")
    nets = {}
    for row in R:
        for pin, net in row["nets"].items():
            base = net.split("(")[0]
            if base.startswith("/"):
                nets.setdefault(base, []).append(f"{row['ref']}.{pin}")
    y.append("nets:")
    for n in sorted(nets):
        y.append(f"  \"{n}\": [{', '.join(nets[n])}]")
    SPEC.write_text("\n".join(y) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"rows": len(R), "mpn": len(R) - len(open_rows), "open": len(open_rows), "over_derating": len(over)}))


if __name__ == "__main__":
    main()
