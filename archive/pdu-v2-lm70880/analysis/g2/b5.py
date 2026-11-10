"""G4 B5: open assumptions - EA gm range for PM/GM, UVLO falling threshold range.

(ii) LM70880 gm: min 970 uS, typ 1200 uS, max NOT published (p.7). Sweep gm 500..3000 uS at all other loop corners and
     report the gm interval where worst PM >= 45 deg + 10 deg model margin and GM >= 6 dB.
(iii) UVLO falling: VEN-HYS 0.1 V typical only (p.6, '100 mV or 10 % of VEN-TH'); sweep hysteresis 0.05..0.15 V with the
     rising-threshold corners -> falling-threshold range; acceptance by bench measurement (BENCH T2).
Run: python -m analysis.g2.b5 -> reports/g4/b5-results.json
"""
from __future__ import annotations

import json
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2 import loop
from analysis.g2.params import v

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g4" / "b5-results.json"


def gm_sweep():
    rows = []
    for gm in (500e-6, 700e-6, 970e-6, 1200e-6, 1430e-6, 1800e-6, 2200e-6, 2600e-6, 3000e-6):
        worst_pm, worst_gm = 999.0, 999.0
        for k in loop.corners():
            k = dict(k, gm=gm)
            m = loop.margins(rc=D.RCOMP, cc=D.CCOMP, chf=D.CHF, **{x: k[x] for x in ("vin", "l", "c", "esr", "rload", "fsw", "gm")})
            worst_pm = min(worst_pm, m["pm_deg"] if m["pm_deg"] is not None else -999)
            worst_gm = min(worst_gm, m["gm_dB"])
        rows.append({"gm_S": gm, "pm_min_deg": worst_pm, "gm_min_dB": worst_gm,
                     "ok": worst_pm - loop.PM_MODEL_MARGIN >= loop.PM_TARGET and worst_gm >= loop.GM_TARGET})
    ok = [r["gm_S"] for r in rows if r["ok"]]
    return rows, (min(ok), max(ok)) if ok else None


def uvlo_falling():
    k = 1 + D.RUV1 / D.RUV2
    rows = []
    for hys in (0.05, 0.10, 0.15):
        lo = (v("VEN_R_MIN") - hys) * k * (1 - 0.0035)
        hi = (v("VEN_R_MAX") - hys) * k * (1 + 0.0035) + v("IEN_LEAK_MAX") * D.RUV1
        rows.append({"hys_V": hys, "falling_V": [lo, hi], "per_cell_V": [lo / 6, hi / 6]})
    return rows


def main():
    rows, ok = gm_sweep()
    res = {"classification": "HESAP (model sweep); gm max and VEN hysteresis not published -> bench acceptance",
           "gm_sweep": rows, "gm_ok_interval_S": ok, "uvlo_falling": uvlo_falling(),
           "cell_cutoff_default_V": 18.0}
    OUT.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"gm_ok_interval_S": ok, "uvlo_falling": res["uvlo_falling"]}))


if __name__ == "__main__":
    main()
