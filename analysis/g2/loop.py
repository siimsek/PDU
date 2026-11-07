"""G2 Stage 4: LM70880 two-phase peak-current-mode loop - analytic (path A) and ngspice AC (path B).

Small-signal model (VARSAYIM, stated in LOOP-STABILITY.md):
  * Ridley peak-current-mode model, both phases share COMP: equivalent single phase with L/N and Ri/N.
  * Ri = RS * GCS (COMP compared directly with the CS-amplifier output; any internal COMP divider/offset is
    unknown -> model uncertainty margin).
  * External slope Se from LM70880 Eq.7 (input referred 24 mV/us per MHz of fsw).
  * Sampling double pole at fsw/2 per phase with Q = 1/(pi (mc D' - 0.5)).
  * Type-II gm compensator; EA output resistance REA (VARSAYIM 10 MOhm).
Path B builds the same transfer functions as a circuit (current source + Rcm + RLC sampling filter + gm stage)
and solves it in ngspice AC; it checks the algebra/numerics, not the model physics.

Run: python -m analysis.g2.loop -> reports/g2/loop-results.json
"""
from __future__ import annotations

import cmath
import hashlib
import itertools
import json
import math
import os

import numpy as np
import subprocess
from pathlib import Path

from analysis.g2 import design as D
from analysis.g2.params import v

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "g2" / "loop-results.json"
SIMDIR = ROOT / "reports" / "g2" / "sim" / "loop"
NGSPICE = Path(os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe"))

N_PH = 2
VOUT = 11.0
REA = 10e6
PM_MODEL_MARGIN = 10.0   # deg, VARSAYIM model-uncertainty allowance -> model PM target 55 deg
PM_TARGET = 45.0
GM_TARGET = 6.0
DIP_PROXY_MAX = 0.11   # V, G4 B4: stacked (trimmed) tolerance corners need dip <~0.11 V; real check = SIM family 3


def plant(s, vin, l, c, esr, rload, fsw, rs=None):
    rs = rs or v("RS_NOM")
    ri = rs * v("GCS")
    ts = 1 / fsw
    d = VOUT / vin
    dp = 1 - d
    sn = (vin - VOUT) / l * ri
    se = v("SLOPE_COMP_K") * 1e-3 / 1e-6 * (fsw / 1e6) * v("GCS")   # V/s at COMP scale
    mc = 1 + se / sn
    leq = l / N_PH
    rcm = leq / (ts * (mc * dp - 0.5))
    rp = rload * rcm / (rload + rcm)
    zc = esr + 1 / (s * c)
    zout = 1 / (1 / rp + 1 / zc)
    wn = math.pi / ts
    qp = 1 / (math.pi * (mc * dp - 0.5))
    fh = 1 / (1 + s / (wn * qp) + (s / wn) ** 2)
    return (N_PH / ri) * zout * fh, {"mc": mc, "qp": qp, "rcm": rcm, "ri": ri}


def comp(s, gm, rc, cc, chf):
    h = v("RFB2") / (v("RFB1") + v("RFB2"))
    z1 = rc + 1 / (s * cc)
    zc = 1 / (1 / z1 + s * chf + 1 / REA)
    return h * gm * zc


FREQ = np.logspace(1, 6.4, 1500)


def loop_gain(f, **k):
    s = 2j * np.pi * f
    g, _ = plant(s, k["vin"], k["l"], k["c"], k["esr"], k["rload"], k["fsw"])
    return g * comp(s, k["gm"], k["rc"], k["cc"], k["chf"])


def margins_from(fs, t):
    mag = 20 * np.log10(np.abs(t))
    ph = np.degrees(np.unwrap(np.angle(t)))
    fc = pm = None
    idx = np.where((mag[:-1] >= 0) & (mag[1:] < 0))[0]
    if len(idx):
        i = idx[0] + 1
        r = mag[i - 1] / (mag[i - 1] - mag[i])
        fc = float(fs[i - 1] * (fs[i] / fs[i - 1]) ** r)
        pc = ph[i - 1] + r * (ph[i] - ph[i - 1])
        pm = float(((pc + 180.0) + 180.0) % 360.0 - 180.0)
    gmarg = 99.0
    x = (ph + 180.0) % 360.0
    # phase crossing of -180 (mod 360) above fc
    for i in range(1, len(fs)):
        if fc and fs[i] > fc and ((ph[i - 1] + 180) // 360) != ((ph[i] + 180) // 360):
            gmarg = float(-mag[i])
            break
    return {"fc_Hz": fc, "pm_deg": pm, "gm_dB": gmarg}


def margins(**k):
    return margins_from(FREQ, loop_gain(FREQ, **k))


def corners(n_cout=None, reduced=False):
    n = n_cout or D.N_COUT
    cs = {"min": n * v("COUT_C_PART_MIN"), "typ": n * v("COUT_C_PART_TYP"), "max": n * v("COUT_C_PART_MAX")}
    esr = v("COUT_ESR_PART") / n
    for (cn, c), lf, gm, vin, il, fsw in itertools.product(
            cs.items(), (0.8, 1.2) if reduced else (0.8, 1.0, 1.2),
            (v("GM_EA_MIN"), v("GM_EA_MAX")) if reduced else (v("GM_EA_MIN"), v("GM_EA_TYP"), v("GM_EA_MAX")),
            (v("VIN_MIN"), v("VIN_MAX")), (0.75, 7.5), (v("FSW_MIN"), v("FSW_MAX"))):
        yield {"c_corner": cn, "c": c, "esr": esr, "l": v("L_NOM") * lf, "l_factor": lf, "gm": gm,
               "vin": vin, "rload": VOUT / il, "iload": il, "fsw": fsw}


def evaluate(rc, cc, chf, n_cout=None, reduced=False):
    rows = []
    for k in corners(n_cout, reduced):
        m = margins(rc=rc, cc=cc, chf=chf, **{x: k[x] for x in ("vin", "l", "c", "esr", "rload", "fsw", "gm")})
        dip = (v("I_LOAD_STEP_HI") - v("I_LOAD_STEP_LO")) / (2 * math.pi * m["fc_Hz"] * k["c"]) if m["fc_Hz"] else 9.9
        rows.append({**{x: k[x] for x in ("c_corner", "l_factor", "gm", "vin", "iload", "fsw")}, **m, "dip_proxy_V": dip})
    pms = [r["pm_deg"] for r in rows if r["pm_deg"] is not None]
    gms = [r["gm_dB"] for r in rows]
    fcs = [r["fc_Hz"] for r in rows if r["fc_Hz"]]
    return {"rows": rows, "pm_min": min(pms), "gm_min": min(gms), "fc_min": min(fcs), "fc_max": max(fcs),
            "dip_proxy_max_V": max(r["dip_proxy_V"] for r in rows),
            "all_crossed": len(pms) == len(rows)}


E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


def select():
    """Pick RCOMP / CCOMP / CHF: maximise worst PM subject to GM >= 9 dB, fc_max <= fsw_min/6 and
    first-order load-step dip proxy dI/(2 pi fc C) <= DIP_PROXY_MAX at every corner."""
    best = None
    for rc in (24.9e3, 27.4e3, 30.1e3, 33.2e3, 36.5e3, 40.2e3):
        for cc in (2.2e-9, 3.3e-9, 4.7e-9, 6.8e-9, 10e-9):
            for chf in (22e-12, 33e-12, 47e-12):
                ev = evaluate(rc, cc, chf, reduced=True)
                if (not ev["all_crossed"] or ev["gm_min"] < GM_TARGET + 3 or ev["fc_max"] > v("FSW_MIN") / 6
                        or ev["dip_proxy_max_V"] > DIP_PROXY_MAX):
                    continue
                score = (round(min(ev["pm_min"], 70.0), 1), -ev["dip_proxy_max_V"])
                if best is None or score > best[0]:
                    best = (score, rc, cc, chf, ev)
    return best


# ------------------------------------------------------------------ path B: ngspice AC
def spice_deck(k, rc, cc, chf, tag):
    _, aux = plant(1j, k["vin"], k["l"], k["c"], k["esr"], k["rload"], k["fsw"])
    wn = math.pi * k["fsw"]
    qp = aux["qp"]
    # series RLC low-pass with R=1, L, C such that wn and Q match: wn = 1/sqrt(LC), Q = sqrt(L/C)/R
    cf = 1 / (wn * qp)
    lf = qp / wn
    h = v("RFB2") / (v("RFB1") + v("RFB2"))
    lines = [f"* G2 loop AC check {tag}",
             "VDC vref 0 DC 0",
             # loop break: AC source between output and divider top
             "VAC vo vfbtop DC 0 AC 1",
             f"RFB1 vfbtop fb {v('RFB1')}", f"RFB2 fb 0 {v('RFB2')}",
             f"GEA 0 cmp fb 0 {-k['gm']}",       # gm stage: current into cmp = -gm*vfb (inverting)
             f"REA cmp 0 {REA}", f"RC cmp cmid {rc}", f"CC cmid 0 {cc}", f"CHF cmp 0 {chf}",
             "EBUF vb 0 cmp 0 1", "RS1 vb n1 1", f"LS1 n1 n2 {lf}", f"CS1 n2 0 {cf}",
             f"GMOD 0 vout n2 0 {N_PH / aux['ri']}",
             f"RCM vout 0 {aux['rcm']}", f"RLOAD vout 0 {k['rload']}",
             f"CO vout nesr {k['c']}", f"RESR nesr 0 {k['esr']}",
             "EVO vo 0 vout 0 1",
             ".ac dec 200 10 2.5meg",
             ".control", "run",
             f"wrdata {tag}.txt vdb(vo)-vdb(vfbtop) vp(vo)-vp(vfbtop)",
             ".endc", ".end"]
    return "\n".join(lines) + "\n"


def run_spice_case(k, rc, cc, chf, tag):
    SIMDIR.mkdir(parents=True, exist_ok=True)
    deck = SIMDIR / f"{tag}.cir"
    deck.write_text(spice_deck(k, rc, cc, chf, tag), encoding="utf-8", newline="\n")
    log = SIMDIR / f"{tag}.log"
    p = subprocess.run([str(NGSPICE), "-b", "-o", str(log), deck.name], cwd=SIMDIR, capture_output=True, text=True, timeout=120)
    data = SIMDIR / f"{tag}.txt"
    if p.returncode != 0 or not data.exists():
        return {"completed": False, "exit": p.returncode}
    # injection between vo (loop output) and vfbtop (feedback input): Vo/Vfb = -T_analytic because the gm
    # stage is inverting; hence PM = 180 + angle(T_analytic) = angle(Vo/Vfb) mapped to (-180, 180].
    fs, mag, ph = [], [], []
    for line in data.read_text().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            fs.append(float(parts[0]))
            mag.append(float(parts[1]))
            ph.append(math.degrees(float(parts[3])))
    # unwrap
    un = [ph[0]]
    for a in ph[1:]:
        while a - un[-1] > 180:
            a -= 360
        while a - un[-1] < -180:
            a += 360
        un.append(a)
    fc = pm = None
    for i in range(1, len(fs)):
        if mag[i - 1] >= 0 > mag[i]:
            r = mag[i - 1] / (mag[i - 1] - mag[i])
            fc = fs[i - 1] * (fs[i] / fs[i - 1]) ** r
            pc = un[i - 1] + r * (un[i] - un[i - 1])
            pm = (pc % 360.0)
            pm = pm if pm <= 180 else pm - 360
            break
    sha = hashlib.sha256(deck.read_bytes()).hexdigest()
    return {"completed": True, "fc_Hz": fc, "pm_deg": pm, "deck": str(deck.relative_to(ROOT)).replace("\\", "/"),
            "log": str(log.relative_to(ROOT)).replace("\\", "/"), "sha256": sha}


def compute(run_spice=True):
    best = select()
    if best is None:
        raise RuntimeError("no compensation meets constraints")
    _, rc, cc, chf, _ = best
    ev = evaluate(rc, cc, chf)
    old = evaluate(9.53e3, 4.7e-9, 47e-12)
    old8 = evaluate(9.53e3, 4.7e-9, 47e-12, n_cout=8)
    res = {"classification": "HESAP (analytic model) + SİM (ngspice AC of same model); bench FRA required",
           "selected": {"rcomp": rc, "ccomp": cc, "chf": chf, "n_cout": D.N_COUT},
           "pm_min_deg": ev["pm_min"], "gm_min_dB": ev["gm_min"], "fc_range_Hz": [ev["fc_min"], ev["fc_max"]],
           "dip_proxy_max_V": ev["dip_proxy_max_V"],
           "pm_after_model_margin_deg": ev["pm_min"] - PM_MODEL_MARGIN,
           "pass_pm": ev["pm_min"] - PM_MODEL_MARGIN >= PM_TARGET, "pass_gm": ev["gm_min"] >= GM_TARGET,
           "old_comp_16cout": {"pm_min": old["pm_min"], "gm_min": old["gm_min"], "fc": [old["fc_min"], old["fc_max"]]},
           "old_comp_8cout": {"pm_min": old8["pm_min"], "gm_min": old8["gm_min"], "fc": [old8["fc_min"], old8["fc_max"]]},
           "bench_adjust": {"rcomp_range": [10e3, 33e3], "ccomp_range": [2.2e-9, 10e-9], "chf_range": [22e-12, 100e-12],
                            "fra_injection": "R_INJ 49.9 ohm in RFB1 leg (0 ohm default), TP_FB_INJ_A/B"},
           "worst_rows": sorted(ev["rows"], key=lambda r: r["pm_deg"])[:5]}
    if run_spice:
        checks = []
        picks = sorted(ev["rows"], key=lambda r: r["pm_deg"])[:3] + sorted(ev["rows"], key=lambda r: -r["pm_deg"])[:2]
        allk = list(corners())
        for i, row in enumerate(picks):
            k = next(x for x in allk if all(x[f] == row[f] for f in ("c_corner", "l_factor", "gm", "vin", "iload", "fsw")))
            sp = run_spice_case(k, rc, cc, chf, f"ac_case{i}")
            checks.append({"corner": {f: row[f] for f in ("c_corner", "l_factor", "gm", "vin", "iload", "fsw")},
                           "analytic_fc_Hz": row["fc_Hz"], "analytic_pm_deg": row["pm_deg"], "spice": sp,
                           "diff_pm_deg": (row["pm_deg"] - sp["pm_deg"]) if sp.get("pm_deg") is not None else None,
                           "diff_fc_rel": (row["fc_Hz"] / sp["fc_Hz"] - 1) if sp.get("fc_Hz") else None})
        res["spice_checks"] = checks
    return res


def main():
    res = compute()
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("selected", "pm_min_deg", "gm_min_dB", "fc_range_Hz")}, ensure_ascii=True))
    for c in res.get("spice_checks", []):
        print(c["analytic_pm_deg"], c["spice"].get("pm_deg"), c["analytic_fc_Hz"], c["spice"].get("fc_Hz"))


if __name__ == "__main__":
    main()
