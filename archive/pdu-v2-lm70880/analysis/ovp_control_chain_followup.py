"""Targeted R6 follow-up for common disconnect gate loss and eFuse OUT-IN.

The SPICE decks are behavioral fixtures, not manufacturer macromodels. They
use datasheet-derived charge/resistance screens only where called out and
retain every unmodeled device behavior as OPEN.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "reports" / "g1" / "sim"
RESULT_PATH = ROOT / "reports" / "g1" / "ovp-control-chain-followup.json"
GATE_DECK = SIM_DIR / "r6-dual-rail-gate-loss.cir"
GATE_LOG = SIM_DIR / "r6-dual-rail-gate-loss.log"
EFUSE_DECK = SIM_DIR / "r6-efuse-out-in.cir"
EFUSE_LOG = SIM_DIR / "r6-efuse-out-in.log"

FET_QG_MAX_C = 153e-9
FET_QG_TEST_V = 10.0
FET_CEQ_PROXY_F = FET_QG_MAX_C / FET_QG_TEST_V
GATE_BLEED_OHM = 10_000.0
GATE_INITIAL_V = 10.0
GATE_SCREEN_V = 2.1
LTC_TGDN_R_MAX_AT_12V_OHM = 4.0
FAULT_TIME_S = 10e-6


CONTROL_CHAIN_CANDIDATE: dict[str, Any] = {
    "classification": "REAL-MPN pin-level candidate; not wired, no physical acceptance",
    "sense": {
        "U_OVP": {"mpn": "TLV1701QDBVRQ1", "package": "SOT-23-5", "IN+": 1, "V-": 2, "IN-": 3, "OUT_open_collector": 4, "V+": 5},
        "U_REF": {"mpn": "REF5025AQDRQ1", "package": "SOIC-8", "VIN": 2, "TEMP": 3, "GND": 4, "TRIM_NR": 5, "VOUT": 6, "NC": 7, "DNC": [1, 8]},
        "R_SENSE_TOP_OHM": 17_950,
        "R_SENSE_BOTTOM_OHM": 5_000,
        "nominal_trip_V": 2.5 * (1 + 17_950 / 5_000),
        "sense_net": "REF5025 VOUT to TLV1701-Q1 IN+ pin 1; VRAW to IN- pin 3 through R_SENSE_TOP; IN- to GND through R_SENSE_BOTTOM; comparator V+ pin 5 from 12V OVP rail and V- pin 2 to GND",
        "fault_path": "When VRAW sense exceeds reference, TLV1701-Q1 open-collector OUT pin 4 sinks CLR_n directly; output is released below threshold. U5/U12 PG open-drain pins also sink CLR_n on rail fault.",
        "nominal_sense_fault_screen": {
            "divider_ratio": 5_000 / (17_950 + 5_000),
            "VRAW_11p1605V_sense_V": 11.1605 * 5_000 / (17_950 + 5_000),
            "VRAW_trip_11p475V_sense_V": 11.475 * 5_000 / (17_950 + 5_000),
            "VRAW_40p709V_sense_V": 40.709 * 5_000 / (17_950 + 5_000),
            "VRAW_40p709V_margin_to_nominal_12V_rail_V": 12.0 - 40.709 * 5_000 / (17_950 + 5_000),
            "status": "nominal divider math only; 12V rail min, resistor tolerance/TCR, reference error, comparator offset/noise and TVS clamp corner not combined"
        },
        "limits": "TLV1701-Q1 is 2.2-36V supply with rail-to-rail input; input node at 40.709V VRAW is nominally below the 12V rail. Its propagation delay has no guaranteed maximum in the cited conditions; threshold tolerance and input behavior at a higher TVS-clamped VRAW remain OPEN.",
    },
    "logic_and_pg": {
        "U_5V": {"mpn": "TPS7A1650QDGNRQ1", "package": "DGN-8", "OUT": 1, "NC": 2, "PG": 3, "GND": 4, "EN": 5, "NC2": 6, "DELAY": 7, "IN": 8},
        "U_12V": {"mpn": "TPS7A1601QDGNRQ1", "package": "DGN-8", "OUT": 1, "FB": 2, "PG": 3, "GND": 4, "EN": 5, "NC": 6, "DELAY": 7, "IN": 8},
        "12V_setpoint": "TI datasheet 12V example: R1=14.3Mohm OUT-to-FB, R2=1.58Mohm FB-to-GND; 1.193V typical VREF gives 12.00V nominal. Feedback current/resistor TCR and exact passives remain open.",
        "U_LATCH": {"mpn": "SN74LVC1G74DCUR", "package": "VSSOP-8", "CLK": 1, "D": 2, "Qbar": 3, "GND": 4, "Q": 5, "CLR_n": 6, "PRE_n": 7, "VCC": 8},
        "PG_wired_AND": "Both TPS7A16-Q1 open-drain PG pins join PG_OK; 10k pull-up to 5V. PG_OK drives the Q_INP_RELEASE base resistor. PG pins are low-dominant only while their datasheet conditions are valid.",
        "CLR_n": "10k pull-up to 5V; U5/U12 PG open drains and TLV1701-Q1 OUT pin 4 share CLR_n, each sinks it low on rail fault or OVP. CLR dominates CLK/ARM.",
        "PRE_n": "pin 7 independently pulled to 5V; never connected to CLR_n; both-low is prohibited while latch VCC is in range.",
        "ARM": "B3U-1000P SPST-NO switch from 5V to CLK pin 1; 100k CLK-to-GND pull-down; D pin 2 tied to 5V. Contact bounce cannot clear a fault while CLR is asserted; bounce/debounce at recovery remains a bench check.",
        "feedback": "Q pin 5 drives LTC7001 INP through 1k; Qbar pin 3 NC; latch VCC pin 8 from 5V; GND pin 4 to GND.",
        "rail_policy": "Both LDOs are powered from protected battery VIN, outside the buck output fault path. U5 powers reference and latch; U12 powers TLV1701-Q1 and LTC7001. Rail sequencing and PG behavior below LDO VIN validity remain OPEN.",
    },
    "driver_and_disconnect": {
        "U_DRIVER": {"mpn": "LTC7001EMSE#PBF", "package": "MSOP-10+EP", "VCC": 1, "VCCUV": 2, "GND": 3, "INP": 4, "OVLO": 5, "TGDN": 6, "TGUP": 7, "TS": 8, "BST": 9, "NC": 10, "EP_GND": 11},
        "VCCUV": "pin 2 to GND: minimum rising UVLO selection (datasheet 3.1-3.7V rising, 2.8-3.4V falling table limits; exact switching point is not used as a timing guarantee)",
        "OVLO": "pin 5 to GND; divider-to-OVLO is not used because threshold tolerance has not been closed against the 11.1605V normal-bus limit",
        "C_BOOT": "0.1uF minimum between BST pin 9 and TS pin 8",
        "Q1_Q2": {"mpn_each": "CSD19536KTTT", "package": "D2PAK / TO-263", "G": 1, "D": 2, "S": 3, "tab": "D"},
        "topology": "Q1 drain to VRAW; Q2 drain to VSAFE/eFuse IN; both sources tied at TS; both gates tied to TGDN pin 6; TGUP pin 7 reaches each gate through its own 10ohm turn-on resistor; each gate has a separate 10k gate-to-its-own-source bleed.",
        "fail_low_clamp": {
            "Q_INP_CLAMP": "MMBT3904LT1G SOT-23: base pin 1 fed from 12V_DRIVER through 22k; emitter pin 2 to GND; collector pin 3 to INP",
            "Q_INP_RELEASE": "MMBT3904LT1G SOT-23: base pin 1 from PG_OK through 82k; emitter pin 2 to GND; collector pin 3 to Q_INP_CLAMP base. Valid PG_OK turns clamp transistor off; bad/missing PG releases its base and clamps INP low",
            "status": "candidate-only bias sizing; beta corners, clamp VIL margin and transistor pin-level macromodel not simulated",
        },
        "limits": "LTC7001 pull-down is 4ohm maximum only at VCC=VBST=12V; propagation/fall values are specified for stated datasheet loads, not this two-FET load. Gate SOA and simultaneous 5V/12V loss behavior are OPEN; 10k G-S bleeds alone are too slow for the previous sub-microsecond screen.",
    },
    "unfrozen_passives": ["R divider parts and TCR", "LDO FB ratio parts", "PG/CLR/PRE/ARM resistors", "gate resistors/bleeds", "base resistors", "capacitor voltage/DC-bias/temperature derating"],
}


CONTROL_SEQUENCE_INPUTS = [
    # event, logic rail, driver rail, both PG-good, raw-safe, healthy, ARM level
    ("cold-start", 0.0, 0.0, False, False, False, False),
    ("reset asserted while rails become valid", 5.0, 12.0, False, False, False, False),
    ("PG valid / disarmed", 5.0, 12.0, True, True, True, False),
    ("manual ARM press", 5.0, 12.0, True, True, True, True),
    ("OVP fault while button remains held", 5.0, 12.0, True, False, False, True),
    ("fault recovery while button remains held", 5.0, 12.0, True, True, True, True),
    ("manual button released", 5.0, 12.0, True, True, True, False),
    ("fresh manual rearm press", 5.0, 12.0, True, True, True, True),
]


def next_q(q: bool | None, *, vcc_v: float, pg_ok: bool, raw_safe: bool,
           monitors_ok: bool, arm_edge: bool) -> bool | None:
    """DFF event contract: unknown below VCC minimum; async clear dominates."""
    if vcc_v < 1.65:
        return None
    fault_clear = pg_ok and raw_safe and monitors_ok
    if not fault_clear:
        return False
    if q is None:
        # Valid rails without a prior active-low clear cannot initialize state.
        return None
    if arm_edge:
        return True
    return q


def simulate_control_sequence() -> list[dict[str, Any]]:
    """Run the complete event sequence from Q=None; never seed Q by case."""
    q: bool | None = None
    prior_arm = False
    rows: list[dict[str, Any]] = []
    for event, vcc, driver_vcc, pg_ok, raw_safe, monitors_ok, arm_level in CONTROL_SEQUENCE_INPUTS:
        arm_edge = arm_level and not prior_arm
        q_before = q
        q = next_q(q, vcc_v=vcc, pg_ok=pg_ok, raw_safe=raw_safe,
                    monitors_ok=monitors_ok, arm_edge=arm_edge)
        clr_n = pg_ok and raw_safe and monitors_ok
        if driver_vcc < 3.4:
            inp = "NOT_CREDITED; DRIVER_RAIL_BELOW_UVLO; G-S_BLEEDS_ONLY"
        elif vcc < 1.65:
            inp = "LOW_BY_EXTERNAL_FAIL_LOW_CLAMP; Q_UNSPECIFIED"
        else:
            inp = "HIGH" if q is True and clr_n else "LOW"
        rows.append({
            "event": event,
            "logic_VCC_V": vcc,
            "driver_VCC_V": driver_vcc,
            "PG_OK": pg_ok,
            "RAW_safe": raw_safe,
            "monitors_ok": monitors_ok,
            "ARM_level": arm_level,
            "ARM_rising_edge": arm_edge,
            "PRE_n": 1,
            "CLR_n": int(clr_n) if vcc >= 1.65 else "not relied on",
            "Q_before": q_before,
            "Q_after": q,
            "INP_policy": inp,
        })
        prior_arm = arm_level
    return rows


def build_gate_loss_deck() -> str:
    """Active LTC sink screen versus simultaneous-rail-loss passive bleeds."""
    return r"""* R6 targeted dual-rail loss: all gate voltages are measured relative to TS.
* Behavioral charge proxy: Ceff=Qg,max/Vtest=153nC/10V per CSD19536KTT.
* Active path: idealized 4ohm TGDN resistance, valid only at VCC=VBST-TS=12V.
* Passive path: no driver sink after abrupt simultaneous 5V/12V rail loss.
VTS_A TSA 0 26
VTS_P TSP 0 26
VLOGIC_A LOGA 0 PWL(0 5 10u 5 20u 0 1m 0)
VDRV_A VDA 0 PWL(0 12 10u 12 20u 0 1m 0)
VBST_A BSTA TSA PWL(0 12 10u 12 20u 0 1m 0)
VLOGIC_P LOGP 0 PWL(0 5 10u 5 10.001u 0 1m 0)
VDRV_P VDP 0 PWL(0 12 10u 12 10.001u 0 1m 0)
VBST_P BSTP TSP PWL(0 12 10u 12 10.001u 0 1m 0)
* Gate charge is initially held at 10V above the floating TS reference.
VHOLD_A HN_A TSA 10
SHOLD_A HN_A GA HOLD_A 0 FASTSW
VCHOLD_A HOLD_A 0 PWL(0 5 9.999u 5 10u 0 1m 0)
VHOLD_P HN_P TSP 10
SHOLD_P HN_P GP HOLD_P 0 FASTSW
VCHOLD_P HOLD_P 0 PWL(0 5 9.999u 5 10u 0 1m 0)
* Two CSD19536KTT devices share the common gate node and common-source TS.
CG_A1 GA TSA 15.3n IC=10
CG_A2 GA TSA 15.3n IC=10
CG_P1 GP TSP 15.3n IC=10
CG_P2 GP TSP 15.3n IC=10
BVGS_A VGS_A 0 V=V(GA)-V(TSA)
BVGS_P VGS_P 0 V=V(GP)-V(TSP)
VRGSA1 GA NGA1 0
RGSA1 NGA1 TSA 10k
VRGSA2 GA NGA2 0
RGSA2 NGA2 TSA 10k
VRGSP1 GP NGP1 0
RGSP1 NGP1 TSP 10k
VRGSP2 GP NGP2 0
RGSP2 NGP2 TSP 10k
* This arm assumes an OVP command at 10us, then sink remains active only
* while the falling driver rail is above the 3.4V upper UVLO screen.
VIA GA NPD_A 0
RPD_A NPD_A NPD_SW_A 4
SDN_A NPD_SW_A TSA CTRL_A 0 FASTSW
BDRV_EN CTRL_A 0 V=if(time<10u,0,if(V(VDA)>3.4,5,0))
* The abrupt-loss arm deliberately credits no active driver action after 10us.
.model FASTSW SW(Ron=0.001 Roff=1T Vt=2.5 Vh=0.1)
.tran 20n 1m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran VGS1_ACTIVE_0P5US FIND V(VGS_A) AT=10.5u
.meas tran VGS2_ACTIVE_0P5US FIND V(VGS_A) AT=10.5u
.meas tran VGS1_ACTIVE_1US FIND V(VGS_A) AT=11u
.meas tran VGS2_ACTIVE_1US FIND V(VGS_A) AT=11u
.meas tran VGS1_ACTIVE_100US FIND V(VGS_A) AT=100u
.meas tran IACTIVE_MAX MAX I(VIA) FROM=10u TO=18u
.meas tran TACTIVE_TO_2P1 WHEN V(VGS_A)=2.1 FALL=1
.meas tran VGS1_PASSIVE_0P5US FIND V(VGS_P) AT=10.5u
.meas tran VGS2_PASSIVE_0P5US FIND V(VGS_P) AT=10.5u
.meas tran VGS1_PASSIVE_100US FIND V(VGS_P) AT=110u
.meas tran VGS2_PASSIVE_100US FIND V(VGS_P) AT=110u
.meas tran IGS1_PASSIVE_0P5US FIND I(VRGSP1) AT=10.5u
.meas tran IGS2_PASSIVE_0P5US FIND I(VRGSP2) AT=10.5u
.meas tran TPASSIVE_TO_2P1 WHEN V(VGS_P)=2.1 FALL=1
.end
"""


def _efuse_group(prefix: str, *, common_fault: bool, bilateral_mask: bool) -> str:
    vin = f"VIN_{prefix}"
    o1 = f"O1_{prefix}"
    s2e = f"S2E_{prefix}"
    if common_fault:
        raw = f"VRAW_{prefix}"
        bus_ctrl = f"BUSCTRL_{prefix}"
        bus_sw = f"SBUS_{prefix}"
        src_and_bus = (
            f"{raw} SRC_{prefix} 0 PWL(0 11 1m 11 1.001m 40.709 12m 40.709)\n"
            f"VBC_{prefix} {bus_ctrl} 0 PWL(0 5 899u 5 900u 0 12m 0)\n"
            f"{bus_sw} SRC_{prefix} {vin} {bus_ctrl} 0 EFUSESW\n"
            f"CIN_{prefix}1 {vin} 0 200n IC=11\nCIN_{prefix}2 {vin} 0 200n IC=11\n"
            f"RIN_{prefix} {vin} 0 100\n"
        )
        ef_ctrl = f"CTRL_{prefix}"
        if bilateral_mask:
            src_and_bus += f"VEC_{prefix} {ef_ctrl} 0 5\n"
        else:
            src_and_bus += f"VEC_{prefix} {ef_ctrl} 0 PWL(0 5 899u 5 900u 0 12m 0)\n"
        sim_from = "0"
    else:
        # Separate precharged-output / input-loss corner: VIN=0 at t=0.
        src_and_bus = (
            f"VZERO_{prefix} {vin} 0 0\n"
            f"CIN_{prefix}1 {vin} 0 200n IC=0\nCIN_{prefix}2 {vin} 0 200n IC=0\n"
        )
        ef_ctrl = f"CTRL_{prefix}"
        src_and_bus += f"VEC_{prefix} {ef_ctrl} 0 0\n"
        sim_from = "0"

    efuse_open = ef_ctrl
    output = (
        f"COUT_{prefix}_O1a {o1} 0 10u IC=11\nCOUT_{prefix}_O1b {o1} 0 10u IC=11\n"
        f"COUT_{prefix}_S2Ea {s2e} 0 10u IC=11\nCOUT_{prefix}_S2Eb {s2e} 0 10u IC=11\n"
        f"RLOAD_{prefix}_O1 {o1} 0 100k\nRLOAD_{prefix}_S2E {s2e} 0 54.5\n"
        f"SEF_{prefix}_O1 {vin} {o1} {efuse_open} 0 EFUSESW\n"
        f"SEF_{prefix}_S2E {vin} {s2e} {efuse_open} 0 EFUSESW\n"
        f"BDIFF_{prefix}_O1 DIFF_{prefix}_O1 0 V=V({o1},{vin})\n"
        f"BDIFF_{prefix}_S2E DIFF_{prefix}_S2E 0 V=V({s2e},{vin})\n"
        f"BFLAG_{prefix}_O1 FLAG_{prefix}_O1 0 V=if(V(DIFF_{prefix}_O1)>0.3,1,0)\n"
        f"BFLAG_{prefix}_S2E FLAG_{prefix}_S2E 0 V=if(V(DIFF_{prefix}_S2E)>0.3,1,0)\n"
        f".meas tran MAX_{prefix}_O1 MAX V(DIFF_{prefix}_O1) FROM={sim_from} TO=12m\n"
        f".meas tran DUR_{prefix}_O1 INTEG V(FLAG_{prefix}_O1) FROM={sim_from} TO=12m\n"
        f".meas tran MAX_{prefix}_S2E MAX V(DIFF_{prefix}_S2E) FROM={sim_from} TO=12m\n"
        f".meas tran DUR_{prefix}_S2E INTEG V(FLAG_{prefix}_S2E) FROM={sim_from} TO=12m\n"
    )
    return src_and_bus + output


def build_efuse_out_in_deck() -> str:
    groups = [
        _efuse_group("CO_OPEN", common_fault=True, bilateral_mask=False),
        _efuse_group("CO_MASK", common_fault=True, bilateral_mask=True),
        _efuse_group("INPUT_LOSS", common_fault=False, bilateral_mask=False),
    ]
    return """* R6 TPS259824O differential stress diagnostic, NOT a silicon model.
* 2x100nF input C per eFuse and 2x10uF output C per port are review-fixture values.
* 100ohm common VIN bleed and 100k O1/54.5ohm S2E loads are explicit assumptions.
* CO_OPEN models the common switch/eFuse opening together; CO_MASK keeps an
* ideal bilateral eFuse SW on to expose the prior reverse-feed masking artifact.
* INPUT_LOSS is a separate precharged-output, VIN=0, eFuse-open corner.
* Only OUT-IN >0.3V voltage/duration is measured; no internal current is inferred.
.model EFUSESW SW(Ron=1m Roff=1T Vt=2.5 Vh=0.1)
""" + "\n".join(groups) + "\n.tran 10u 12m 0 10u uic\n.options reltol=0.0001 abstol=1n method=gear\n.end\n"


def run_deck(deck_path: Path, log_path: Path, deck_text: str,
             required_measures: set[str]) -> dict[str, Any]:
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    deck_path.write_text(deck_text, encoding="utf-8", newline="\n")
    ngspice = Path(os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe"))
    proc = subprocess.run([str(ngspice), "-D", "ngbehavior=ltpsa", "-b", "-o",
                           str(log_path), str(deck_path)], cwd=SIM_DIR,
                          capture_output=True, text=True, check=False)
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else proc.stdout + proc.stderr
    if not log_path.exists():
        log_path.write_text(log, encoding="utf-8", newline="\n")
    measures: dict[str, float] = {}
    for line in log.splitlines():
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([-+0-9.eE]+)", line)
        if m:
            measures[m.group(1).lower()] = float(m.group(2))
    missing = sorted(x.lower() for x in required_measures if x.lower() not in measures)
    completed = proc.returncode == 0 and "No. of Data Rows" in log and not missing
    return {
        "deck": deck_path.relative_to(ROOT).as_posix(),
        "log": log_path.relative_to(ROOT).as_posix(),
        "solver": "ngspice Windows build selected by PDU_NGSPICE",
        "solver_exit_code": proc.returncode,
        "completed": completed,
        "missing_measures": missing,
        "measures": measures,
        "stderr": proc.stderr.strip(),
    }


def run_targeted_fixtures() -> dict[str, Any]:
    gate_required = {
        "vgs1_active_0p5us", "vgs2_active_0p5us", "vgs1_active_1us",
        "vgs2_active_1us", "vgs1_active_100us", "iactive_max",
        "tactive_to_2p1", "vgs1_passive_0p5us", "vgs2_passive_0p5us",
        "vgs1_passive_100us", "vgs2_passive_100us", "igs1_passive_0p5us",
        "igs2_passive_0p5us", "tpassive_to_2p1",
    }
    efuse_required = {
        f"{prefix}_{port}"
        for prefix in ("max_co_open", "dur_co_open", "max_co_mask", "dur_co_mask", "max_input_loss", "dur_input_loss")
        for port in ("o1", "s2e")
    }
    gate = run_deck(GATE_DECK, GATE_LOG, build_gate_loss_deck(), gate_required)
    efuse = run_deck(EFUSE_DECK, EFUSE_LOG, build_efuse_out_in_deck(), efuse_required)
    passive_tau = GATE_BLEED_OHM * FET_CEQ_PROXY_F
    passive_t_to_screen = passive_tau * math.log(GATE_INITIAL_V / GATE_SCREEN_V)
    active_tau = (LTC_TGDN_R_MAX_AT_12V_OHM * FET_CEQ_PROXY_F * 2)
    active_t_to_screen = active_tau * math.log(GATE_INITIAL_V / GATE_SCREEN_V)
    gm = gate["measures"]
    em = efuse["measures"]
    efuse_duration_interpretation: dict[str, dict[str, Any]] = {}
    for prefix, event_start in (("co_open", 0.9e-3), ("co_mask", 0.9e-3), ("input_loss", 0.0)):
        for port in ("o1", "s2e"):
            max_diff = em.get(f"max_{prefix}_{port}")
            duration = em.get(f"dur_{prefix}_{port}")
            window_cap = 12e-3 - event_start
            censored = bool(duration is not None and duration >= window_cap - 20e-6)
            efuse_duration_interpretation[f"{prefix}_{port}"] = {
                "max_OUT_minus_IN_V": max_diff,
                "duration_above_0p3V_measured_s": duration,
                "duration_is_right_censored": censored,
                "duration_statement": f">={duration * 1e3:.3f} ms (simulation window ends before differential falls below 0.3V)" if censored and duration is not None else f"{duration * 1e3:.3f} ms within this fixture" if duration is not None else "INCOMPLETE: no duration measurement",
                "fixture_boundary_status": "EXCEEDS 0.3V" if max_diff is not None and max_diff > 0.3 else "does not exceed 0.3V in this behavioral fixture" if max_diff is not None else "INCOMPLETE",
            }
    output_cap_f = 20e-6
    output_drop_factor = math.log(11.0 / 0.3)
    output_r_o1 = 100_000.0
    output_r_s2e = 54.5
    return {
        "classification": "SİM behavioral diagnostic + HESAP scale checks + DATASHEET limits; no physical PASS",
        "source_head": "8cdb0d57605ef3f42c44dc3d461950920521f989",
        "gate_loss": {
            **gate,
            "simulated_rails": {"logic_5V": "falls with VCC driver from 10us to 20us", "driver_12V": "same falling interval", "TS": 26.0},
            "gate_proxy": {"Qg_max_C_per_FET": FET_QG_MAX_C, "test_V": FET_QG_TEST_V, "Ceq_proxy_F_per_FET": FET_CEQ_PROXY_F, "initial_VGS_V": GATE_INITIAL_V, "screen_threshold_V": GATE_SCREEN_V},
            "analytical_crosscheck": {"passive_tau_s": passive_tau, "passive_to_2p1V_s": passive_t_to_screen, "active_tau_s_at_4ohm_valid_rail_s": active_tau, "active_to_2p1V_s_at_4ohm_valid_rail": active_t_to_screen},
            "ngspice_vs_calculation": {
                "passive_to_2p1V_percent_delta": 100 * (gm.get("tpassive_to_2p1", math.nan) - FAULT_TIME_S - passive_t_to_screen) / passive_t_to_screen if "tpassive_to_2p1" in gm else None,
                "active_to_2p1V_percent_delta": 100 * (gm.get("tactive_to_2p1", math.nan) - FAULT_TIME_S - active_t_to_screen) / active_t_to_screen if "tactive_to_2p1" in gm else None,
            },
            "status": "OPEN: active resistor approximation is only specified at VCC=VBST-TS=12V; simultaneous total rail loss after UVLO is not guaranteed. Passive 10k path misses the previous 0.5us OVP turn-off screen by orders of magnitude.",
        },
        "efuse_out_in": {
            **efuse,
            "threshold_V": 0.3,
            "corners": {
                "common_disconnect_open": "upstream switch opens, eFuse paths open; local CIN=400nF total drains through assumed 100ohm, output caps are precharged to 11V",
                "common_disconnect_bilateral_mask": "same upstream event, ideal bilateral eFuse switches remain closed; demonstrates only an artifact that can mask OUT-IN",
                "precharged_output_input_loss": "separate VIN=0 from t=0, output caps start at 11V, ideal eFuse switches open",
            },
            "simulated_loads": {"O1": "100kΩ assumption; duration is window-censored", "S2E": "54.5Ω derived from 12V/0.22A manufacturer working-current datum; applied at 11V as a resistive model"},
            "analytical_crosscheck": {
                "COUT_per_port_F": output_cap_f,
                "CIN_total_common_F": 400e-9,
                "RIN_bleed_ohm_assumption": 100.0,
                "RIN_tau_s": 100.0 * 400e-9,
                "O1_Rload_ohm_assumption": output_r_o1,
                "O1_RC_time_to_0p3V_s": output_r_o1 * output_cap_f * output_drop_factor,
                "S2E_Rload_ohm_assumption": output_r_s2e,
                "S2E_RC_time_to_0p3V_s": output_r_s2e * output_cap_f * output_drop_factor,
                "ngspice_direct_input_loss_S2E_delta_percent": 100 * (em.get("dur_input_loss_s2e", math.nan) - output_r_s2e * output_cap_f * output_drop_factor) / (output_r_s2e * output_cap_f * output_drop_factor) if "dur_input_loss_s2e" in em else None,
            },
            "duration_and_boundary_register": efuse_duration_interpretation,
            "interpretation": "Any measured OUT-IN >0.3V is a DATASHEET-boundary violation in the fixture. The measured interval is not a TPS259824O transient prediction because its internal pass-FET/reverse-current behavior is not modeled. The bilateral-mask row is not admissible as device evidence.",
        },
        "temporal_state_sequence": simulate_control_sequence(),
        "candidate_chain": CONTROL_CHAIN_CANDIDATE,
        "preserved_status": {
            "Family2_O1_18p8039V": "FAIL retained",
            "Family4_bus_10p7109V": "FAIL retained",
            "common_bus_TPS25982_IN_40p709V": "FAIL retained",
            "O1_peak_le_12V_physical": "OPEN",
            "normal_bus_le_11p1605V_physical": "OPEN",
            "WP1": "4 ESL incomplete; N-01 open",
            "WP2": "69 FAIL / 6 incomplete",
            "TPS259824O_reverse_current_and_OUT_IN": "OPEN; not guaranteed by behavioral fixture",
            "two_FET_SOA_and_physical_dual_rail_gate_off": "OPEN",
        },
    }


def main() -> int:
    result = run_targeted_fixtures()
    RESULT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": RESULT_PATH.relative_to(ROOT).as_posix(),
        "gate_completed": result["gate_loss"]["completed"],
        "efuse_completed": result["efuse_out_in"]["completed"],
        "gate_status": result["gate_loss"]["status"],
        "family2_fail_retained": result["preserved_status"]["Family2_O1_18p8039V"],
    }, indent=2, ensure_ascii=False))
    return 0 if result["gate_loss"]["completed"] and result["efuse_out_in"]["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
