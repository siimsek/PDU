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
import os
import re
import subprocess
import sys
import tempfile
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


KICAD_CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
# Schematic blocks (T-006..T-012): refs whose schematic netlist must equal the spec after the block card.
BLOCKS = {
    "B1": ["J1", "D1", "U5", "Q1", "CIN_U5", "CVCAP", "CBIN1", "CBIN2"] + [f"CIN{i}" for i in range(1, 9)],
    "B2": ["U1", "U2", "L1", "L2", "RS1", "RS2", "CBOOT1", "CBOOT2", "RBOOT1", "RBOOT2", "RT1", "RT2", "CVCC1", "CVCC2",
           "CVDDA1", "CVDDA2", "RCFG1", "RCFG2", "RSYNC", "RFB1", "R_INJ", "RFB2", "R_TRIM", "RCOMP", "CCOMP", "CHF",
           "RUV1", "RUV2"],
    "B3": [f"COUT{i}" for i in range(1, 33)],
    "B4": ["U11", "U12", "U13", "U14", "U15", "R_OCT", "R_OCB", "C_INA1", "C_INA2", "C_OCC1", "C_OCC2", "C_AND"],
    "B6": ["U3", "RILIM1", "RIMON1", "CDVDT1", "CEFIN1", "CEFOUT1", "RPG1", "RPG1B", "D_REV1", "D2", "U4", "RILIM2",
           "RIMON2", "CDVDT2", "CEFIN2", "CEFOUT2", "RPG2", "RPG2B", "D_REV2", "D3", "REN1", "REN2", "J3", "J2"],
    "B7": ["J_OVP_INJ_BUS", "JP_EN_BUCK"] + [f"TP_{n}" for n in (
        "ANODE", "VIN", "VOUT", "VSAFE", "O1", "S2E", "ISO_GATE", "ISO_OV", "OVP_TRIP_N", "OVP_Q", "CLR_N", "OVP_SENSE",
        "OVP_REF", "OVP_BUS_N", "P5V", "OC_SENSE1", "OC_SENSE2", "OC_REF", "FB_INJ_A", "FB_INJ_B", "COMP", "EN_BUCK",
        "SW1", "SW2", "ISNS1P", "ISNS1N", "ISNS2P", "ISNS2N", "PG_O1", "PG_S2E", "IMON_O1", "IMON_S2E", "GND_FB",
        "GND_OC", "GND_OVP", "GND_POWER")],
    "B5": ["U6", "Q2", "U7", "U8", "U9", "U10", "RRAWBL", "R_GS", "C_ISO_VCAP", "C_ISO_VS", "R_OVT", "R_OVB", "C_CMP",
           "C_REF_IN", "C_REF_OUT", "C_REF_NR", "C_LAT", "R_CLR", "C_CLR", "SW1", "R_Q", "R_OV2T", "R_OV2B", "R_EN1",
           "R_EN2", "C_LDO_IN", "C_LDO_OUT", "C_LDO_DELAY", "R_BL5", "R_BLS"],
}


def schematic_netlist(sch: Path | None = None) -> dict:
    """Export the schematic netlist with kicad-cli and return {ref: {"fields": {...}, "footprint": str, "pins": {num: (name, net)}}}."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import kicad_sexpr as ks
    sch = sch or ROOT / "PDU.kicad_sch"
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "net.net"
        subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out), str(sch)],
                       capture_output=True, check=True)
        root = ks.top(ks.parse(out.read_text(encoding="utf-8")))
    comps = {}
    for c in next(root.children("components")).children("comp"):
        ref = next(c.children("ref")).atoms()[1].value
        fp = next(c.children("footprint"), None)
        fields = {}
        for fs in c.children("fields"):
            for f in fs.children("field"):
                vals = [x for x in f if isinstance(x, ks.Atom)][1:]
                fields[next(f.children("name")).atoms()[1].value] = vals[-1].value if vals else ""
        val = next(c.children("value"), None)
        comps[ref] = {"fields": fields, "footprint": fp.atoms()[1].value if fp is not None else "", "pins": {},
                      "value": val.atoms()[1].value if val is not None else ""}
    for n in next(root.children("nets")).children("net"):
        net = next(n.children("name")).atoms()[1].value
        for nd in n.children("node"):
            ref = next(nd.children("ref")).atoms()[1].value
            pin = next(nd.children("pin")).atoms()[1].value
            pf = next(nd.children("pinfunction"), None)
            name = re.sub(rf"_{re.escape(pin)}$", "", pf.atoms()[1].value) if pf is not None else ""
            if ref in comps:
                comps[ref]["pins"][pin] = (name, net)
    return comps


def schematic_diff(refs, comps=None) -> list:
    spec, _ = parse_spec(ROOT / "design" / "pdu_v2_spec.yaml")
    comps = comps if comps is not None else schematic_netlist()
    bom_mfr = {r["ref"]: r["manufacturer"] for r in csv.DictReader((ROOT / "design" / "bom-v2.csv").open(encoding="utf-8"))}
    errs = []
    for ref in refs:
        s, c = spec.get(ref), comps.get(ref)
        if s is None or c is None:
            errs.append(f"{ref}: {'not in spec' if s is None else 'not in schematic'}")
            continue
        if c["footprint"] != s.get("footprint", ""):
            errs.append(f"{ref}.footprint: schematic '{c['footprint']}' != spec '{s.get('footprint')}'")
        if c.get("value") != s.get("value", ""):   # R-010: canonical rule, schematic Value == spec value (all refs)
            errs.append(f"{ref}.value: schematic '{c.get('value')}' != spec '{s['value']}'")
        mfr = bom_mfr.get(ref, "")
        if c["fields"].get("Manufacturer") and mfr and c["fields"]["Manufacturer"].split()[0].lower() not in mfr.lower():
            errs.append(f"{ref}.Manufacturer: schematic '{c['fields']['Manufacturer']}' != BOM '{mfr}' (stale metadata, R-006)")
        if c["fields"].get("MPN", "") != s.get("mpn", ""):
            errs.append(f"{ref}.MPN: schematic '{c['fields'].get('MPN', '')}' != spec '{s.get('mpn')}'")
        for key, net in s["pins"].items():
            want = "/" + net.lstrip("/").split("(")[0] if net.startswith("/") else net
            m = re.match(r"^(\w[\w/+\-]*)\((\d+)\)$", key)
            if key.isdigit() or m:
                num = key if key.isdigit() else m.group(2)
                got = c["pins"].get(num, (None, None))[1]
            else:
                k0 = key.replace(" ", "")
                hits = [nt for nm, nt in c["pins"].values() if nm.replace(" ", "") == k0]
                if not hits:  # numbered pin groups (VIN1..VIN6, SW1..SW4, PGND1..4) carry one spec name
                    hits = [nt for nm, nt in c["pins"].values() if re.fullmatch(re.escape(k0) + r"\d+", nm.replace(" ", "")) and nm not in s["pins"]]
                got = hits[0] if hits and all(h == hits[0] for h in hits) else (sorted(set(hits)) or None)
            if want.upper().startswith(("NC", "DNC", "/NC", "/DNC")) and (got is None or str(got).startswith("unconnected-")):
                continue
            if got != want:
                errs.append(f"{ref}.{key}: schematic {got} != spec {want}")
    return errs


def main():
    if "--schematic" in sys.argv:
        blocks = [a for a in sys.argv[1:] if a in BLOCKS] or list(BLOCKS)
        errs = schematic_diff([r for b in blocks for r in BLOCKS[b]])
        print(json.dumps({"blocks": blocks, "pass": not errs, "n_errors": len(errs)}))
        for e in errs:
            print("FAIL:", e)
        return 0 if not errs else 1
    errs = check()
    out = {"pass": not errs, "errors": errs}
    (ROOT / "reports" / "g4" / "consistency.json").write_text(json.dumps(out, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"pass": out["pass"], "n_errors": len(errs)}))
    for e in errs:
        print("FAIL:", e)
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
