"""T-027 schematic reference and pin coverage inventory (standard library + kicad-cli; read-only for the design).

    python scripts/sch_inventory.py                       # uses PDU.kicad_sch and PDU.kicad_pcb of the checked-out commit
    python scripts/sch_inventory.py --alt-pcb <git-rev>   # also compares pad nets against PDU.kicad_pcb of another commit

Source of truth: `kicad-cli sch export netlist --format kicadsexpr` (one component per reference, multi-unit symbols are not counted twice; every pin
appears on a net, no-connects on `unconnected-*`). Joined per reference and per pin with design/bom-v2.csv, design/footprint-map.csv, design/pdu_v2_spec.yaml,
PDU.kicad_pcb and design/pdu_v2.cir. Writes reports/g5/T-027/. A join that cannot be proven is recorded, never counted as a match.
"""
from __future__ import annotations

import collections
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402
import pcb_rules as pr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g5" / "T-027"
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
BOARD_ONLY_BOM = re.compile(r"^(TP_|J_OVP_INJ_BUS$|JP_EN_BUCK$)")     # D-008: test pads and injection/solder-jumper parts are placed but not bought


def field(node, head):
    n = next(node.children(head), None)
    a = n.atoms() if n is not None else []
    return a[1].value if len(a) > 1 else ""


def parse_netlist(text: str):
    """-> ({ref: component}, {(ref, pin): pin record})"""
    root = ks.top(ks.parse(text))
    comps = {}
    for c in next(root.children("components")).children("comp"):
        ref = field(c, "ref")
        fields = {}
        fs = next(c.children("fields"), None)
        if fs is not None:
            for f in fs.children("field"):
                a = f.atoms()
                name = next((x for x in f.children("name")), None)
                key = name.atoms()[1].value if name is not None else (a[1].value if len(a) > 1 else "")
                vals = [x.value for x in a[1:] if hasattr(x, "value")]
                fields[key] = vals[-1] if vals else ""
        props = {}
        for p in c.children("property"):
            nm, vl = next(p.children("name"), None), next(p.children("value"), None)
            props[nm.atoms()[1].value if nm is not None else ""] = vl.atoms()[1].value if vl is not None else ""
        sheet = next(c.children("sheetpath"), None)
        ts = next(c.children("tstamps"), None)
        lib = next(c.children("libsource"), None)
        comps[ref] = {"ref": ref, "value": field(c, "value"), "footprint": field(c, "footprint"), "fields": fields, "properties": props,
                      "sheet": field(sheet, "names") if sheet is not None else "", "uuids": [u for x in ts.atoms()[1:] for u in x.value.split()] if ts is not None else [],
                      "lib_part": field(lib, "part") if lib is not None else ""}
    pins = {}
    for n in next(root.children("nets")).children("net"):
        name = field(n, "name")
        for nd in n.children("node"):
            ref, pin = field(nd, "ref"), field(nd, "pin")
            pins[(ref, pin)] = {"ref": ref, "pin": pin, "name": field(nd, "pinfunction"), "type": field(nd, "pintype"), "net": name}
    return comps, pins


def parse_pcb(text: str):
    """-> {ref: {'footprint': lib id, 'pads': {pad number: set of nets}}} (unnumbered paste/mechanical pads are skipped)"""
    out = {}
    for fp in ks.top(ks.parse(text)).children("footprint"):
        ref = next((p.atoms()[2].value for p in fp.children("property") if p.atoms()[1].value == "Reference"), "")
        pads = collections.defaultdict(set)
        for pd in fp.children("pad"):
            num = pd.atoms()[1].value
            if not num:
                continue
            net = next(pd.children("net"), None)
            pads[num].add(net.atoms()[-1].value if net is not None else "")
        out[ref] = {"footprint": fp.atoms()[1].value, "pads": {k: sorted(v) for k, v in pads.items()}}
    return out


def read_csv(path: Path, key="ref"):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by = collections.defaultdict(list)
    for r in rows:
        by[r[key]].append(r)
    return rows, by


def spec_refs(text: str):
    return set(re.findall(r"^\s*-\s*ref:\s*(\S+)\s*$", text, re.M))


def cir_elements(text: str):
    names = set()
    for line in text.splitlines():
        s = line.strip()
        if s and s[0] not in "*.+":
            names.add(s.split()[0])
    return names


def sch_dnp(comp: dict) -> bool:
    return "dnp" in comp["properties"] or bool(comp["fields"].get("DNP"))


def classify(ref: str, comp: dict, pcb_refs: set, bom_dnp: bool = False) -> str:
    if BOARD_ONLY_BOM.match(ref):
        return "test/injection (BOM dışı, D-008)"
    if bom_dnp or sch_dnp(comp):
        return "DNP"
    if ref not in pcb_refs:
        return "kart ayak izi yok"
    return "elektriksel parça"


def build(comps, pins, pcb, bom_by, map_by, spec, cir, alt=None, cir_text=""):
    pcb_refs = set(pcb)
    refs, pin_rows = [], []
    for ref in sorted(comps):
        c = comps[ref]
        bom = bom_by.get(ref, [])
        bom_dnp = any(b.get("dnp", "").strip().lower() == "true" for b in bom)
        cls = classify(ref, c, pcb_refs, bom_dnp)
        issues = []
        if bom and bom_dnp != sch_dnp(c):
            issues.append(f"DNP farkı: şema {sch_dnp(c)}, BOM {bom_dnp}")
        if not bom:
            bom_state = "BOM dışı (D-008)" if BOARD_ONLY_BOM.match(ref) else "BOM'da yok: doğrulanamadı"
            if not BOARD_ONLY_BOM.match(ref):
                issues.append("BOM satırı yok")
        elif len(bom) > 1:
            bom_state = f"{len(bom)} BOM satırı"
            issues.append("aynı referans birden çok BOM satırında")
        else:
            bom_state = "BOM eşleşti"
            if bom[0]["value"] != c["value"]:
                issues.append(f"değer farkı: şema {c['value']!r}, BOM {bom[0]['value']!r}")
            if bom[0]["footprint"] != c["footprint"]:
                issues.append(f"footprint farkı: şema {c['footprint']!r}, BOM {bom[0]['footprint']!r}")
        mpn = c["fields"].get("MPN", "")
        bom_mpn = bom[0]["mpn"] if len(bom) == 1 else ""
        if bom and len(bom) == 1 and mpn != bom_mpn:
            issues.append(f"MPN farkı: şema {mpn!r}, BOM {bom_mpn!r}")
        fm = map_by.get(ref, [])
        p = pcb.get(ref)
        if p is None:
            issues.append("kartta ayak izi yok")
        elif p["footprint"] != c["footprint"]:
            issues.append(f"kart footprint farkı: şema {c['footprint']!r}, kart {p['footprint']!r}")
        if ref in cir:
            spice = "SPICE elemanı (ad eşit)"
        elif re.search(r"(?<![A-Za-z0-9_])" + re.escape(ref) + r"(?![A-Za-z0-9_])", cir_text):
            spice = "SPICE metninde geçiyor, eleman adı değil: doğrulanamadı"
        else:
            spice = "SPICE'ta ad eşleşmesi yok: doğrulanamadı"
        cp = [v for k, v in pins.items() if k[0] == ref]
        refs.append({"ref": ref, "uuids": " ".join(c["uuids"]), "units": len(c["uuids"]), "sheet": c["sheet"], "value": c["value"], "mpn": mpn, "footprint": c["footprint"], "class": cls, "pins": len(cp),
                     "bom": bom_state, "footprint_map": "var" if fm else "yok", "spec": "var" if ref in spec else "yok", "pcb": "var" if p else "yok", "spice": spice, "issues": "; ".join(issues), "status": "UYUŞMAZ" if issues else "KAYITLI"})
        for r in sorted(cp, key=lambda x: (len(x["pin"]), x["pin"])):
            pads = p["pads"].get(r["pin"]) if p else None
            nc = r["type"] == "no_connect" or r["net"].startswith("unconnected-")
            if p is None:
                state, why = "AÇIK", "kartta ayak izi yok"
            elif pads is None:
                state, why = "UYUŞMAZ", "kartta bu numarada pad yok"
            elif pads == [r["net"]]:
                state, why = "EŞLEŞTİ", ""
            else:
                state, why = "UYUŞMAZ", f"kart pad ağı {pads}"
            alt_state = ""
            if alt is not None:
                ap = alt.get(ref, {}).get("pads", {}).get(r["pin"])
                alt_state = "aynı" if ap == pads else f"farklı: {ap}"
            pin_rows.append({"ref": ref, "uuid": c["uuids"][0] if c["uuids"] else "", "pin": r["pin"], "name": r["name"], "type": r["type"], "net": r["net"], "nc": "kasıtlı NC" if nc else "", "pcb_pads": "|".join(pads or []), "state": state, "why": why, "alt_pcb": alt_state})
    return refs, pin_rows


def main(argv) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        net = Path(td) / "n.net"
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(net), str(ROOT / "PDU.kicad_sch")], check=True, capture_output=True)
        text = net.read_text(encoding="utf-8")
    (OUT / "netlist.net").write_text(text, encoding="utf-8", newline="\n")
    comps, pins = parse_netlist(text)
    pcb = parse_pcb((ROOT / "PDU.kicad_pcb").read_text(encoding="utf-8"))
    alt, alt_rev = None, ""
    if "--alt-pcb" in argv:
        alt_rev = argv[argv.index("--alt-pcb") + 1]
        alt = parse_pcb(subprocess.run(["git", "show", f"{alt_rev}:PDU.kicad_pcb"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8"))
    bom, bom_by = read_csv(ROOT / "design" / "bom-v2.csv")
    fmap, map_by = read_csv(ROOT / "design" / "footprint-map.csv")
    spec = spec_refs((ROOT / "design" / "pdu_v2_spec.yaml").read_text(encoding="utf-8"))
    cir = cir_elements((ROOT / "design" / "pdu_v2.cir").read_text(encoding="utf-8"))
    cir_text = (ROOT / "design" / "pdu_v2.cir").read_text(encoding="utf-8")
    refs, pin_rows = build(comps, pins, pcb, bom_by, map_by, spec, cir, alt, cir_text)
    spec_text = (ROOT / "design" / "pdu_v2_spec.yaml").read_text(encoding="utf-8")
    spec_pin_keys = len(re.findall(r'^\s+"[^"]+":\s+"[^"]*"\s*$', spec_text, re.M))
    known = {r["ref"] for r in refs}
    no_sch = {"bom_refs_not_in_schematic": sorted(set(bom_by) - known), "pcb_refs_not_in_schematic": sorted(set(pcb) - known), "footprint_map_refs_not_in_schematic": sorted(set(map_by) - known), "spec_refs_not_in_schematic": sorted(spec - known)}
    summary = {"input_commit": head, "kicad_cli": subprocess.run([CLI, "version"], capture_output=True, text=True, encoding="utf-8").stdout.strip(), "alt_pcb": alt_rev,
               "schematic_references": len(refs), "schematic_pins": len(pin_rows), "symbol_uuids": sum(r["units"] for r in refs), "bom_rows": len(bom), "footprint_map_rows": len(fmap), "spec_refs": len(spec), "pcb_footprints": len(pcb), "spice_element_names": len(cir),
               "references_by_class": dict(collections.Counter(r["class"] for r in refs)), "references_by_status": dict(collections.Counter(r["status"] for r in refs)), "pins_by_state": dict(collections.Counter(p["state"] for p in pin_rows)),
               "intentional_nc_pins": sum(1 for p in pin_rows if p["nc"]), "references_without_ledger_row": 0, "pins_without_ledger_row": len(set(pins) - {(p["ref"], p["pin"]) for p in pin_rows}),
               "spice_by_state": dict(collections.Counter(r["spice"] for r in refs)), "spec_pin_keys": spec_pin_keys, "dnp_references": sorted(r["ref"] for r in refs if r["class"] == "DNP"),
               "bom_only_kinds": {r: bom_by[r][0]["kind"] for r in no_sch["bom_refs_not_in_schematic"]}, **no_sch,
               "alt_pcb_pad_differences": sum(1 for p in pin_rows if p["alt_pcb"].startswith("farklı")) if alt is not None else None}
    for fn, rows in (("ledger-references.csv", refs), ("ledger-pins.csv", pin_rows)):
        with (OUT / fn).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    with (OUT / "inventory-summary.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=0))
    return 0 if summary["pins_without_ledger_row"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
