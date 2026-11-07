"""Single source parameter table for G2.

Every value carries an evidence label:
  DATASHEET(doc, page) - manufacturer document read in this G2 session
  HESAP                - derived in analysis/g2
  VARSAYIM             - explicit design assumption (see "if_changes")
  KULLANICI            - user requirement (not relaxed)

All SI units: V, A, ohm, F, H, s, W, K.
The ngspice include file design/pdu_v2_params.inc is generated from this table
(analysis/g2/sim_runner.py), so the SPICE decks and the hand calculations share
one source.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class P:
    value: float
    unit: str
    label: str
    source: str
    if_changes: str = ""


DS = {
    "LM70880": "TI LM70880-Q1 SNVSBX7A (Jun 2024)",
    "TPS25982": "TI TPS25982 SLVSEI3D (May 2026)",
    "INA296": "TI INA296A-Q1/INA296B-Q1 datasheet (downloaded 2026-11-07)",
    "LVC1G11": "TI SN74LVC1G11 datasheet (downloaded 2026-11-07)",
    "SMCJ": "Vishay SMCJ5.0A thru SMCJ188CA doc 88394 (Rev 09-Jan-2024)",
    "LM74502H": "TI LM74502/LM74502H SNOSDE5A (May 2022)",
    "TLV3601": "TI TLV360x Rev E (2023)",
    "REF5025A": "TI REF50xxA-Q1 SBOS456H (Feb 2015)",
    "LVC1G74": "TI SN74LVC1G74 SCES794G (Sep 2021)",
    "TPS7A16": "TI TPS7A16-Q1 SBVS188E (May 2023)",
    "CSD19531Q5A": "TI CSD19531Q5A SLPS406B (May 2014)",
    "LM74700": "TI LM74700-Q1 datasheet (downloaded 2026-11-07)",
    "BSC160N10NS3G": "Infineon BSC160N10NS3 G datasheet (repo hardware/_datasheets)",
    "IHLP4040": "Vishay doc 34509 cross reference (Rev 20-Dec-2018) + IHLP-4040DZ-L1 doc 34207",
    "WSL": "Vishay WSL doc 30100 (Rev 23-Nov-2023)",
    "TNPW": "Vishay TNPW e3 doc 28758 (Rev 10-Apr-2026)",
    "CRCW": "Vishay CRCW e3 doc 20035 (Rev 14-Apr-2026)",
    "C5750": "TDK C5750X7S2A226M280KB characterization sheet (repo hardware/_datasheets) + G1 Ceff model",
}

PARAMS: dict[str, P] = {
    # ---- requirements (never relaxed)
    "O1_PEAK_MAX": P(12.0, "V", "KULLANICI", "REQUIREMENTS.md"),
    "BUS_STEADY_MAX": P(11.1605, "V", "KULLANICI", "REQUIREMENTS.md static FB corner"),
    "BUS_TRANSIENT_MAX": P(11.22, "V", "KULLANICI", "REQUIREMENTS.md conflict note 2 (PR#1 band upper)"),
    "BUS_MIN_STEP": P(10.78, "V", "KULLANICI", "G1 Family 4 criterion"),
    "VIN_MIN": P(20.0, "V", "KULLANICI", "6S, 20-26 V envelope"),
    "VIN_NOM": P(22.2, "V", "KULLANICI", "6S nominal"),
    "VIN_MAX": P(26.0, "V", "KULLANICI", "6S, 20-26 V envelope"),
    "VIN_CLAMP": P(53.3, "V", "DATASHEET", "Vishay SMCJ33A VC max 53.3 V @ IPPM 28.1 A, doc 88394 Rev 09-Jan-2024 p.2 (G4: verified)",
                   "Higher clamp raises Q_ISO VDS, divider clamp current, LDO/LM74502H VS stress."),
    "I_BUS_CAP": P(7.5, "A", "KULLANICI", "power-stage capacity target"),
    "I_LOAD_STEP_LO": P(0.75, "A", "KULLANICI", "Family 4 step"),
    "I_LOAD_STEP_HI": P(7.0, "A", "KULLANICI", "Family 4 step"),
    "R_SRC_MIN": P(0.020, "ohm", "VARSAYIM", "battery+cable sweep", "Fault current, F1 I2t, Q1 SOA."),
    "R_SRC_MAX": P(0.200, "ohm", "VARSAYIM", "battery+cable sweep", "Fault current, F1 I2t, Q1 SOA."),
    "T_AMB_MAX": P(85.0, "C", "VARSAYIM", "G1 thermal screen ambient", "Thermal margins of every part."),
    "DT_REF_BOX": P(165.0, "K", "VARSAYIM", "REF5025A drift is a box-method spec over -40..125 C; full 165 K span used (G3 audit D4)",
                     "Reference drift corner; long-term drift/solder shift not included."),
    "DT_DRIFT": P(100.0, "K", "VARSAYIM", "25 C -> 125 C worst drift span", "Reference/resistor drift corners."),

    # ---- buck controller
    "VFB_MIN": P(0.794, "V", "DATASHEET", DS["LM70880"] + " p.7 table 6.5"),
    "VFB_NOM": P(0.800, "V", "DATASHEET", DS["LM70880"] + " p.7"),
    "VFB_MAX": P(0.806, "V", "DATASHEET", DS["LM70880"] + " p.7"),
    "GM_EA_MIN": P(970e-6, "S", "DATASHEET", DS["LM70880"] + " p.7 gm-EXTERNAL min"),
    "GM_EA_TYP": P(1200e-6, "S", "DATASHEET", DS["LM70880"] + " p.7 gm-EXTERNAL typ (no max published)"),
    "GM_EA_MAX": P(1430e-6, "S", "VARSAYIM", "no max published; typ + (typ-min)",
                   "Higher gm raises crossover; PM/GM corners in loop analysis."),
    "IFB_MAX": P(75e-9, "A", "DATASHEET", DS["LM70880"] + " p.7"),
    "VEN_R_MIN": P(0.95, "V", "DATASHEET", DS["LM70880"] + " p.6 VEN-TH"),
    "VEN_R_MAX": P(1.05, "V", "DATASHEET", DS["LM70880"] + " p.6 VEN-TH"),
    "VEN_HYS_TYP": P(0.10, "V", "DATASHEET", DS["LM70880"] + " p.6 VEN-HYS typ only"),
    "IEN_LEAK_MAX": P(1.0e-6, "A", "VARSAYIM", "LM70880 EN leakage max not found in datasheet; 1 uA screen",
                      "Each 1 uA shifts UVLO rising by 1 uA*RUV1 (0.174 V at 174k)."),
    "VCS_TH_MIN": P(0.050, "V", "DATASHEET", DS["LM70880"] + " p.8 VCS-TH"),
    "VCS_TH_TYP": P(0.056, "V", "DATASHEET", DS["LM70880"] + " p.8/p.16"),
    "VCS_TH_MAX": P(0.062, "V", "DATASHEET", DS["LM70880"] + " p.8 VCS-TH"),
    "GCS": P(10.0, "V/V", "DATASHEET", DS["LM70880"] + " p.8/p.17 CS amplifier gain (by design)"),
    "T_CS_DELAY": P(75e-9, "s", "DATASHEET", DS["LM70880"] + " p.17 typical only"),
    "SLOPE_COMP_K": P(24.0, "mV/us per MHz", "DATASHEET", DS["LM70880"] + " p.16 Eq.7 (L = VOUT*RS/(24*Fsw))"),
    "FSW_NOM": P(435.066e3, "Hz", "HESAP", "RT=49.9k equation (docs/design.md)"),
    "FSW_MIN": P(400e3, "Hz", "DATASHEET", "previous datasheet table basis 400/440/480 kHz (docs/design.md)"),
    "FSW_MAX": P(480e3, "Hz", "DATASHEET", "previous datasheet table basis 400/440/480 kHz (docs/design.md)"),
    "RFB1": P(130e3, "ohm", "DATASHEET", "ERA3AEB134V repo BOM, 0.1%"),
    "RFB2": P(10.2e3, "ohm", "DATASHEET", "ERA3AEB1022V repo BOM, 0.1%"),

    # ---- magnetics / sense / caps
    "L_NOM": P(6.8e-6, "H", "DATASHEET", DS["IHLP4040"] + " p.1"),
    "L_TOL": P(0.20, "-", "DATASHEET", DS["IHLP4040"] + " +/-20%"),
    "L_DCR_MAX": P(23.3e-3, "ohm", "DATASHEET", DS["IHLP4040"] + " p.1"),
    "L_ISAT_TYP": P(13.5, "A", "DATASHEET", DS["IHLP4040"] + " p.1 (~20% L drop, typ)"),
    "L_IHEAT_TYP": P(8.0, "A", "DATASHEET", DS["IHLP4040"] + " p.1 (40 C rise, typ)"),
    "RS_NOM": P(7.5e-3, "ohm", "DATASHEET", DS["WSL"] + " WSL2512, 1 W P70, 1%"),
    "RS_TOL": P(0.01, "-", "DATASHEET", DS["WSL"]),
    "RS_TCR": P(75e-6, "1/K", "DATASHEET", DS["WSL"] + " p.2 component TCR 7-500 mOhm"),
    "RS_P70": P(1.0, "W", "DATASHEET", DS["WSL"] + " p.1"),
    "COUT_C_PART_TYP": P(20.622e-6, "F", "DATASHEET", DS["C5750"] + " Ceff typical 11 V 25 C"),
    "COUT_C_PART_MIN": P(92.6514e-6 / 8, "F", "HESAP", "G1 corner (tolerance+temp+10% aging) per part"),
    "COUT_C_PART_MAX": P(257.664e-6 / 8, "F", "HESAP", "G1 upper envelope per part"),
    "COUT_ESR_PART": P(1.9204e-3, "ohm", "DATASHEET", DS["C5750"] + " vendor model at 400 kHz"),
    "COUT_ESL_PART": P(0.5e-9, "H", "VARSAYIM", "2220 MLCC ESL screen", "ESL affects >10 MHz only."),
    "N_COUT_OLD": P(8, "-", "DATASHEET", "repo BOM COUT1-8"),

    # ---- protection chain
    "VREF": P(2.5, "V", "DATASHEET", DS["REF5025A"] + " p.5"),
    "VREF_TOL": P(0.001, "-", "DATASHEET", DS["REF5025A"] + " p.5 standard grade +/-0.1%"),
    "VREF_TC": P(8e-6, "1/K", "DATASHEET", DS["REF5025A"] + " standard grade drift max (G1-cited)"),
    "CMP_VOS": P(5e-3, "V", "DATASHEET", DS["TLV3601"] + " p.7 -40..125 C"),
    "CMP_HYS_MIN": P(1.5e-3, "V", "DATASHEET", DS["TLV3601"] + " p.7"),
    "CMP_HYS_MAX": P(5e-3, "V", "DATASHEET", DS["TLV3601"] + " p.7"),
    "CMP_IB": P(5e-6, "A", "DATASHEET", DS["TLV3601"] + " p.7 -40..125 C"),
    "CMP_TPD_MAX": P(4.5e-9, "s", "DATASHEET", DS["TLV3601"] + " p.7, 50 mV overdrive, VCM=VEE+0.3V, CL=5pF"),
    "CMP_OD": P(50e-3, "V", "DATASHEET", DS["TLV3601"] + " p.7 delay test overdrive"),
    "CMP_VCM_HI": P(0.2, "V", "DATASHEET", DS["TLV3601"] + " p.7 VCM up to VCC+0.2"),
    "CMP_ICLAMP_MAX": P(10e-3, "A", "DATASHEET", DS["TLV3601"] + " p.5 note: limit input current to 10 mA"),
    "CMP_ICC_MAX": P(7e-3, "A", "DATASHEET", DS["TLV3601"] + " p.7"),
    "CMP_POR": P(2.1, "V", "DATASHEET", DS["TLV3601"] + " p.7 VPOR (typ)"),
    "LAT_TPD_MAX": P(6.4e-9, "s", "DATASHEET", DS["LVC1G74"] + " p.7 PRE/CLR->Q, VCC=5V, -40..125 C"),
    "LAT_VCC_MIN": P(1.65, "V", "DATASHEET", DS["LVC1G74"] + " p.4"),
    "DRV_OVR_MIN": P(1.165, "V", "DATASHEET", DS["LM74502H"] + " p.6"),
    "DRV_OVR_MAX": P(1.333, "V", "DATASHEET", DS["LM74502H"] + " p.6"),
    "DRV_OVF_MIN": P(1.063, "V", "DATASHEET", DS["LM74502H"] + " p.6"),
    "DRV_TOVP_OFF_MAX": P(1.0e-6, "s", "DATASHEET", DS["LM74502H"] + " p.6, OV to VGS<1V, C(GATE-SRC)=4.7nF"),
    "DRV_TOVP_TEST_CGS": P(4.7e-9, "F", "DATASHEET", DS["LM74502H"] + " p.6 test condition"),
    "DRV_EN_R_MIN": P(1.16, "V", "DATASHEET", DS["LM74502H"] + " p.5"),
    "DRV_EN_R_MAX": P(1.32, "V", "DATASHEET", DS["LM74502H"] + " p.5"),
    "DRV_EN_F_MIN": P(1.027, "V", "DATASHEET", DS["LM74502H"] + " p.5"),
    "DRV_EN_F_MAX": P(1.235, "V", "DATASHEET", DS["LM74502H"] + " p.5"),
    "DRV_EN_ISINK_MAX": P(5e-6, "A", "DATASHEET", DS["LM74502H"] + " p.5 at 12 V"),
    "DRV_OV_LEAK_MAX": P(110e-9, "A", "DATASHEET", DS["LM74502H"] + " p.6"),
    "DRV_VS_MAX_OP": P(60.0, "V", "DATASHEET", DS["LM74502H"] + " p.4/p.5"),
    "DRV_VS_ABS": P(65.0, "V", "DATASHEET", DS["LM74502H"] + " p.4"),
    "DRV_VGS_MIN_RATING": P(15.0, "V", "DATASHEET", DS["LM74502H"] + " p.4 external MOSFET VGS rating min"),
    "DRV_VCAP_MAX": P(13.9, "V", "DATASHEET", DS["LM74502H"] + " p.5 charge pump turn-off max"),
    "QISO_VDS": P(100.0, "V", "DATASHEET", DS["CSD19531Q5A"] + " p.1"),
    "QISO_VGS_ABS": P(20.0, "V", "DATASHEET", DS["CSD19531Q5A"] + " p.1"),
    "QISO_RDS_MAX_10V": P(6.4e-3, "ohm", "DATASHEET", DS["CSD19531Q5A"] + " p.3, VGS=10V, 25 C"),
    "QISO_CISS_MAX": P(3.87e-9, "F", "DATASHEET", DS["CSD19531Q5A"] + " p.3"),
    "QISO_QG_MAX_10V": P(48e-9, "C", "DATASHEET", DS["CSD19531Q5A"] + " p.3"),
    "QISO_EAS": P(0.180, "J", "DATASHEET", DS["CSD19531Q5A"] + " p.1 single pulse avalanche"),
    "QISO_RTH_JA": P(50.0, "K/W", "DATASHEET", DS["CSD19531Q5A"] + " p.3, 1 in2 2 oz Cu"),
    "QISO_RDS_HOT_FACTOR": P(1.8, "-", "VARSAYIM", "RDS(on) at Tj~125 C relative to 25 C (graph not numerically extracted)",
                             "Conduction loss and Tj."),
    "LDO5_VOUT_TOL": P(0.02, "-", "DATASHEET", DS["TPS7A16"] + " +/-2% (G1-cited)"),
    "LDO5_PG_MIN": P(0.85, "-", "DATASHEET", DS["TPS7A16"] + " p.6 VIT 85..95 %VOUT"),
    "LDO5_PG_MAX": P(0.95, "-", "DATASHEET", DS["TPS7A16"] + " p.6"),
    "LDO5_IDELAY_MIN": P(1e-6, "A", "DATASHEET", DS["TPS7A16"] + " p.6 (column extraction: 1 typ / 2 max; 1 uA used as min screen)"),
    "LDO5_RTH_JA": P(66.2, "K/W", "DATASHEET", DS["TPS7A16"] + " p.5 DGN"),

    # ---- eFuse
    "EF_IN_ABS": P(30.0, "V", "DATASHEET", DS["TPS25982"] + " p.7"),
    "EF_IN_REC": P(24.0, "V", "DATASHEET", DS["TPS25982"] + " p.7"),
    "EF_OUT_OVER_IN": P(0.3, "V", "DATASHEET", DS["TPS25982"] + " p.7 OUT max min(30, VIN+0.3)"),
    "EF_UVLO_R_MIN": P(1.18, "V", "DATASHEET", DS["TPS25982"] + " p.9"),
    "EF_UVLO_R_MAX": P(1.23, "V", "DATASHEET", DS["TPS25982"] + " p.9"),
    "EF_GIMON_MIN": P(238.6e-6, "A/A", "DATASHEET", DS["TPS25982"] + " p.8 (3 A..min(15A,ILIM))"),
    "EF_GIMON_MAX": P(253.4e-6, "A/A", "DATASHEET", DS["TPS25982"] + " p.8"),

    # ---- G4 additions: eFuse constants used by the netlist (TPS259824L), TVS clamps, phase-overcurrent trip
    "EF_UVLO_R_TYP": P(1.20, "V", "DATASHEET", DS["TPS25982"] + " p.9 VUVLO(R) 1.18/1.20/1.23"),
    "EF_UVLO_F_TYP": P(1.10, "V", "DATASHEET", DS["TPS25982"] + " p.9 VUVLO(F) 1.08/1.10/1.13"),
    "EF_OVLO_TYP": P(16.9, "V", "DATASHEET", DS["TPS25982"] + " p.4/p.8 '4' variant OVLO 16.32/16.9/17.31 V"),
    "EF_RON_MAX_25C": P(3.2e-3, "ohm", "DATASHEET", DS["TPS25982"] + " p.9 RON max, TJ=25 C"),
    "EF_RON_HOT_FACTOR": P(1.5, "-", "VARSAYIM", "RON at hot TJ relative to 25 C max (graph p.11 not numerically extracted)",
                           "eFuse conduction loss and VSAFE->port drop"),
    "TVS_IN_VBR_MIN": P(36.7, "V", "DATASHEET", "Vishay SMCJ33A VBR min, doc 88394 p.2"),
    "TVS_IN_IPPM": P(28.1, "A", "DATASHEET", "Vishay SMCJ33A IPPM (10/1000 us), doc 88394 p.2"),
    "TVS_IN_VWM": P(33.0, "V", "DATASHEET", "Vishay SMCJ33A VWM, doc 88394 p.2"),
    "OC_INA_VCM_MAX": P(110.0, "V", "DATASHEET", DS["INA296"] + " p.5 VCM -5..110 V (survival -20..120 V)"),
    "OC_INA_SETTLE_TYP": P(1.0e-6, "s", "DATASHEET", DS["INA296"] + " p.6 settling to 1 % TYPICAL (no max)"),
    "OC_INA_DELAY_SCREEN": P(1.5e-6, "s", "VARSAYIM", "1.5 x typical settling used in budget; O1 <= 11.94 V even at 4 us (n1-results.json)",
                             "OC path timing; voltage path remains the guaranteed-delay backup"),
    "LM70880_VOUT_ABS": P(60.0, "V", "DATASHEET", DS["LM70880"] + " p.5 VOUT, ISNS+ abs max"),
    "LM70880_BIAS_ABS": P(32.0, "V", "DATASHEET", DS["LM70880"] + " p.5 BIAS abs max (G4: BIAS tied to AGND, p.13)"),
    "LFLOOR_BEYOND_16A": P(0.15, "-", "VARSAYIM", "L(I) above 16 A not published (doc 34207 p.3 ends at 16 A); floor swept 0.05-0.5",
                           "O1 peak with OC trip: path B bound 11.50 V at 0.15, 11.87 V at 0.05 (low static corner)"),
}

# TPS25982 datasheet guaranteed ILIM points, TJ -40..125 C (p.9): RILIM -> (min, typ, max)
EF_ILIM_TABLE = {
    773.0: (1.53, 2.00, 2.43),
    300.0: (4.36, 4.98, 5.66),
    182.0: (7.23, 8.13, 9.07),
    100.0: (12.85, 14.71, 15.99),
}


def v(name: str) -> float:
    return PARAMS[name].value


def table_rows():
    return [{"name": k, "value": p.value, "unit": p.unit, "label": p.label, "source": p.source,
             "if_changes": p.if_changes} for k, p in PARAMS.items()]
