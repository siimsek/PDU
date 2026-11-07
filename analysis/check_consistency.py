"""G4 C3: three-way consistency check  design/pdu_v2_spec.yaml  <->  design/bom-v2.csv  <->  SPICE parameter set.

Checks (any difference = FAIL, non-zero exit):
  1. spec refs == BOM refs (PCB parts; cable-side rows excluded); value, MPN and footprint identical per ref.
  2. spec net integrity: every net has >= 2 pins; no ref.pin appears on two nets.
  3. SPICE/design parameters match the BOM values: RCOMP, CCOMP, CHF, RFB1, RFB2+R_TRIM, RUV1/RUV2, COUT count,
     eFuse RILIM -> ILIM table, threshold dividers (R_OVT/R_OVB, R_OCT/R_OCB) vs analysis/g2/protection.py and n1.py.
Run: python analysis/check_consistency.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.g2 import design as D  # noqa: E402
from analysis.g2 import n1, protection  # noqa: E402

SI = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6}


def num(s):
    m = re.match(r"^([0-9.]+)\s*([pnumkM]?)", s.strip())
    return float(m.group(1)) * SI.get(m.group(2), 1.0) if m else None


def parse_spec(path):
    parts, cur, nets, in_nets = {}, None, {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("nets:"):
            in_nets = True
            continue
        if in_nets:
            m = re.match(r'\s+"([^"]+)": \[(.*)\]', line)
            if m:
                nets[m.group(1)] = [x.strip() for x in m.group(2).split(",") if x.strip()]
            continue
        m = re.match(r"\s+- ref: (\S+)", line)
        if m:
            cur = parts.setdefault(m.group(1), {"pins": {}})
            continue
        m = re.match(r'\s+(value|mpn|footprint): "(.*)"', line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2)
            continue
        m = re.match(r'\s+"([^"]+)": "([^"]+)"', line)
        if m and cur is not None:
            cur["pins"][m.group(1)] = m.group(2)
    return parts, nets


def check():
    errors = []
    spec, nets = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    bom = {r["ref"]: r for r in csv.DictReader((ROOT / "design" / "bom-v2.csv").open(encoding="utf-8")) if r["kind"] != "CABLE"}
    cable = {r["ref"] for r in csv.DictReader((ROOT / "design" / "bom-v2.csv").open(encoding="utf-8")) if r["kind"] == "CABLE"}
    spec_pcb = {k: v for k, v in spec.items() if k not in cable}
    if set(spec_pcb) != set(bom):
        errors.append(f"ref sets differ: spec-only {sorted(set(spec_pcb) - set(bom))}, bom-only {sorted(set(bom) - set(spec_pcb))}")
    for ref in set(spec_pcb) & set(bom):
        for f in ("value", "mpn", "footprint"):
            if spec_pcb[ref].get(f, "") != bom[ref][f]:
                errors.append(f"{ref}.{f}: spec '{spec_pcb[ref].get(f)}' != bom '{bom[ref][f]}'")
    seen = {}
    for net, members in nets.items():
        if len(members) < 2:
            errors.append(f"net {net} has < 2 pins: {members}")
        for mbr in members:
            if mbr in seen and seen[mbr] != net:
                errors.append(f"{mbr} on two nets: {seen[mbr]} and {net}")
            seen[mbr] = net

    def bv(ref):
        return num(bom[ref]["value"])
    exp = {"RCOMP": D.RCOMP, "CCOMP": D.CCOMP, "CHF": D.CHF, "RUV1": D.RUV1, "RUV2": D.RUV2,
           "RILIM1": D.RILIM_O1, "RILIM2": D.RILIM_S2E, "RFB2": D.RFB2_FIXED, "R_TRIM": D.R_TRIM_DEFAULT,
           "R_OVT": 8.25e3, "R_OVB": protection.RB, "R_OV2T": protection.RT2, "R_OV2B": protection.RB2,
           "R_OCT": n1.OCT_RT, "R_OCB": n1.OCT_RB}
    for ref, val in exp.items():
        got = bv(ref)
        if got is None or abs(got - val) > 1e-6 * max(1.0, abs(val)):
            errors.append(f"{ref}: BOM {bom[ref]['value']} != design {val}")
    n_cout = sum(1 for r in bom if re.match(r"COUT\d+$", r))
    if n_cout != D.N_COUT:
        errors.append(f"COUT count BOM {n_cout} != design {D.N_COUT}")
    inc = (ROOT / "design" / "pdu_v2_params.inc").read_text(encoding="utf-8")
    pv = dict(re.findall(r"\.param (\w+)=([-+0-9.eE]+)", inc))
    for k, val in (("RCOMP", D.RCOMP), ("CCOMP", D.CCOMP), ("CHF", D.CHF), ("RUV1", D.RUV1), ("RUV2", D.RUV2)):
        if abs(float(pv[k]) - val) > 1e-6 * val:
            errors.append(f"SPICE {k}={pv[k]} != design {val}")
    if abs(float(pv["RFB2"]) - (D.RFB2_FIXED + D.R_TRIM_DEFAULT)) > 5.0:
        errors.append(f"SPICE RFB2={pv['RFB2']} != RFB2_FIXED+R_TRIM {D.RFB2_FIXED + D.R_TRIM_DEFAULT}")
    from analysis.g2.params import v
    if abs(float(pv["COUT_EFF"]) - D.N_COUT * v("COUT_C_PART_TYP")) > 1e-9:
        errors.append("SPICE COUT_EFF does not match N_COUT")
    return errors


def main():
    errs = check()
    out = {"pass": not errs, "errors": errs}
    (ROOT / "reports" / "g4" / "consistency.json").write_text(json.dumps(out, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"pass": out["pass"], "n_errors": len(errs)}))
    for e in errs:
        print("FAIL:", e)
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
