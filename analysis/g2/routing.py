"""G2 routing inputs and widths (updates the G1 routing-input with G2 currents/nets).

Path A: IPC-2221 empirical fit (same constants as calculate_routing_rules.py): I = k*dT^0.44*A^0.725 (A in mil^2),
        k = 0.048 external / 0.024 internal.
Path B: ohmic drop budget: width so that I*R over the segment length <= drop budget.
The routed width must satisfy both. Via count: G1 0.5 A/via screen (path A) vs barrel cross-section current density
(path B, 20 um plating, 0.3 mm drill, 30 A/mm2 screen VARSAYIM).
Run: python -m analysis.g2.routing -> reports/g2/routing-input-g2.json, reports/g2/routing-g2.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from analysis.g2.params import EF_ILIM_TABLE
from analysis.g2 import design as D

ROOT = Path(__file__).resolve().parents[2]
CU_UM = 31.5          # VARSAYIM 35 um nominal minus 10 % (G1 basis)
CU_INNER_UM = 15.75   # VARSAYIM 0.5 oz inner layers (4L stackup option) -> fabricator to confirm
DT = 20.0
T_RHO = 70.0
DROP_MV = 50.0
RHO = 1.724e-8 * (1 + 0.00393 * (T_RHO - 20))

CLASSES = [
    {"name": "INPUT_POWER", "nets": ["/VBAT", "/F1_OUT", "/ANODE", "/VIN"], "current_A": 82.5 / 0.92 / 20.0, "length_mm": 50,
     "basis": "82.5 W / 92 % (VARSAYIM) / 20 V"},
    {"name": "BUS_POWER", "nets": ["/VOUT", "/VSAFE", "/GND"], "current_A": 7.5, "length_mm": 50,
     "basis": "7.5 A capacity target; VSAFE carries the same current through Q2"},
    {"name": "PHASE_POWER", "nets": ["/SW_PH1", "/SW_PH2", "/ISNS1", "/ISNS2"], "current_A": 5.583, "length_mm": 30,
     "basis": "phase peak 5.583 A (power.py, +10 % share, VIN 26 V)"},
    {"name": "O1_PORT", "nets": ["/O1_11V"], "current_A": EF_ILIM_TABLE[D.RILIM_O1][2], "length_mm": 40,
     "basis": "ILIM_O1 max 9.07 A (could flow continuously just below trip in a max-corner part)"},
    {"name": "S2E_PORT", "nets": ["/S2E_11V"], "current_A": EF_ILIM_TABLE[D.RILIM_S2E][2], "length_mm": 40,
     "basis": "ILIM_S2E max 5.66 A"},
]


def ipc_width_mm(i, cu_um, k):
    area_mil2 = (i / (k * DT ** 0.44)) ** (1 / 0.725)
    return area_mil2 / (cu_um / 25.4) * 0.0254


def drop_width_mm(i, cu_um, length_mm):
    return RHO * (length_mm / 1000) * i / ((cu_um * 1e-6) * (DROP_MV / 1000)) * 1000


def vias(i):
    a = math.ceil(i / 0.5)
    barrel_mm2 = math.pi * 0.3 * 0.020
    b = math.ceil(i / (30.0 * barrel_mm2))
    return a, b


def compute():
    rows = []
    for c in CLASSES:
        i = c["current_A"]
        ext_a = ipc_width_mm(i, CU_UM, 0.048)
        ext_b = drop_width_mm(i, CU_UM, c["length_mm"])
        inn_a = ipc_width_mm(i, CU_INNER_UM, 0.024)
        inn_b = drop_width_mm(i, CU_INNER_UM, c["length_mm"])
        va, vb = vias(i)
        rows.append({**c, "outer_width_ipc_mm": ext_a, "outer_width_drop_mm": ext_b, "outer_width_min_mm": max(ext_a, ext_b),
                     "inner_width_ipc_mm": inn_a, "inner_width_drop_mm": inn_b, "inner_width_min_mm": max(inn_a, inn_b),
                     "vias_0p5A_each": va, "vias_barrel_density": vb, "vias_min": max(va, vb)})
    inp = {"nominal_copper_um": 35, "calculation_copper_um": CU_UM, "inner_copper_um_VARSAYIM": CU_INNER_UM,
           "trace_deltaT_C": DT, "resistivity_temperature_C": T_RHO, "drop_budget_mV_per_trunk": DROP_MV,
           "classes": CLASSES, "source": "G2 analysis/g2/routing.py (replaces G1 routing-input for transfer)"}
    (ROOT / "reports" / "g2" / "routing-input-g2.json").write_text(json.dumps(inp, indent=2), encoding="utf-8", newline="\n")
    out = {"method": "IPC-2221 fit (k=.048 ext/.024 int, b=.44, c=.725) and ohmic drop; screening only, not IPC-2152",
           "rows": rows}
    (ROOT / "reports" / "g2" / "routing-g2.json").write_text(json.dumps(out, indent=2), encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    for r in compute()["rows"]:
        print(f"{r['name']:12s} {r['current_A']:.2f} A outer {r['outer_width_min_mm']:.2f} mm inner {r['inner_width_min_mm']:.2f} mm vias {r['vias_min']}")
