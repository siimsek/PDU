#!/usr/bin/env python3
"""T-053 isolated EN/ens bench. Uses the BVEN/BENS/CENS/RENS lines of design/pdu_v2.cir unchanged and adds the same internal-comparison variants as run_t053.py.
Measures rising and falling VIN thresholds of the decoded state and short-dip behaviour. Physical EN thresholds are not changed by any internal variant.
Run from the repo root: python reports/g5/T-053/run_isolated.py   (writes isolated.json)"""
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-053"
WORK = OUT / "iso"
NG = os.environ.get("PDU_NGSPICE", r"F:\Spice64\bin\ngspice_con.exe")
BASE = (ROOT / "design/pdu_v2.cir").read_text(encoding="utf-8")
LINES = [next(l for l in BASE.splitlines() if l.split()[:1] == [e]) for e in ("BVEN", "BENS", "CENS", "RENS")]
VARIANTS = [("base", None)] + [("rc", x) for x in (0.05e-6, 0.2e-6, 1e-6, 2e-6, 5e-6)] + [("schmitt", x) for x in ((0.45, 0.55), (0.4, 0.6), (0.3, 0.7))]
RATIO = (174000 + 10000) / 10000


def add(kind, x):
    if kind == "base":
        return "ens", "", "base"
    if kind == "rc":
        return "ensf", f"RENSF ens ensf {x / 1e-9:g}\nCENSF ensf 0 1n\nRENSFL ensf 0 1G\n", f"rc{x * 1e6:g}us"
    return "ensf", f"BENSF 0 ensf I = 1e-3*(V(ens)>{x[1]})*(1-V(ensf)) - 1e-3*(V(ens)<{x[0]})*V(ensf)\nCENSF ensf 0 1n\nRENSFL ensf 0 1G\n", f"schmitt{x[0]:g}_{x[1]:g}"


def run(name, deck):
    f = WORK / f"{name}.cir"
    f.write_text(deck, encoding="utf-8", newline="\n")
    log = f.with_suffix(".log")
    code = subprocess.run([NG, "-b", "-o", log.name, f.name], cwd=WORK, capture_output=True, timeout=60).returncode
    return code, log.read_text(errors="replace")


def value(text, name):
    m = re.search(rf"^{name}\s*=\s*([-+0-9.eE]+)", text, re.M | re.I)
    return float(m.group(1)) if m else None


def deck(vr, vh, extra, src, tran, meas):
    body = "\n".join(LINES)
    return f"* T-053 isolated EN bench\n.param VEN_R={vr} VEN_H={vh} RUV1=174000 RUV2=10000\nVIN vin 0 {src}\n{body}\n{extra}.ic V(ens)=0 V(ensf)=0\n.tran {tran} uic\n{meas}\n.end\n"


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    rows = []
    ramp = "PWL(0 0 2m 26 3m 26 5m 0)"
    for kind, x in VARIANTS:
        node, extra, tag = add(kind, x)
        for vr in (0.95, 1.0, 1.05):
            m = f".meas tran rise FIND v(vin) WHEN v({node})=0.5 RISE=1\n.meas tran fall FIND v(vin) WHEN v({node})=0.5 FALL=1\n"
            code, text = run(f"ramp_{tag}_{vr}", deck(vr, 0.1, extra, ramp, "20n 5m 0 2u", m))
            ris, fal = value(text, "rise"), value(text, "fall")
            rows.append({"test": "ramp", "variant": tag, "VEN_R": vr, "VEN_H": 0.1, "exit": code, "vin_rise": ris, "vin_fall": fal, "ideal_rise": round(vr * RATIO, 4), "ideal_fall": round((vr - 0.1) * RATIO, 4)})
        for width in (0.2e-6, 0.5e-6, 1e-6, 2e-6, 5e-6, 20e-6):
            src = f"PWL(0 26 100u 26 100.01u 10 {100.01e-6 + width:.9g} 10 {100.02e-6 + width:.9g} 26 200u 26)"
            m = f".meas tran dmin MIN v({node}) FROM=100u TO=200u\n"
            code, text = run(f"dip_{tag}_{width * 1e6:g}", deck(1.0, 0.1, extra, src, "5n 200u 0 50n", m).replace(".ic V(ens)=0 V(ensf)=0", ".ic V(ens)=1 V(ensf)=1"))
            dm = value(text, "dmin")
            rows.append({"test": "dip_26V_to_10V", "variant": tag, "width_us": width * 1e6, "exit": code, "decoded_min": dm, "disabled": None if dm is None else dm < 0.5})
    doc = {"status": "İzole deney; resmi sonuç değil. Girişler ideal.", "netlist_sha256": hashlib.sha256(BASE.encode()).hexdigest(), "lines_used": LINES, "source_note": "VEN_R 0,95/1,00/1,05 ve VEN_H 0,1 tipik: TI SNVSBX7A s.6, s.13 §7.3.3. VEN_H için min/maks okunmadı.", "rows": rows}
    (OUT / "isolated.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    shutil.rmtree(WORK)
    for r in rows:
        if r["test"] == "ramp" and r["VEN_R"] == 1.0:
            print(r["variant"], r["exit"], r["vin_rise"], r["vin_fall"])
    tags = sorted({r["variant"] for r in rows})
    print({t: [r["width_us"] for r in rows if r["test"] != "ramp" and r["variant"] == t and r["disabled"]] for t in tags})
    print("bad", [r for r in rows if r["exit"] != 0 or r.get("decoded_min", 0) is None or r.get("vin_rise", 0) is None])


if __name__ == "__main__":
    main()
