"""T-013 board rules (stdlib only; run after scripts/pcb_setup.py):

    python scripts/pcb_rules.py           # writes stackup into PDU.kicad_pcb, netclasses into PDU.kicad_pro, PDU.kicad_dru
    python scripts/pcb_rules.py --check   # verify only; exit 1 on any mismatch (used by tests / pre-merge evidence)

Sources: reports/g2/routing-g2.json (selected widths, outer-layer minimum widths), reports/g2/PCB-HANDOFF.md §1
(4 layers, 1.6 mm, 1 oz all layers, L1-L2 0.2 mm dielectric), §5 (HV-logic 0.6 mm), decisions/D-006 (120 x 85 mm).
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PCB, PRO, DRU = ROOT / "PDU.kicad_pcb", ROOT / "PDU.kicad_pro", ROOT / "PDU.kicad_dru"
ROUTING = ROOT / "reports" / "g2" / "routing-g2.json"
NETLIST = ROOT / "reports" / "g5" / "T-013" / "netlist.net"
BOARD_MM = (120.0, 85.0)
CU_MM = 0.035                    # 1 oz finished copper, all layers (PCB-HANDOFF §1; manufacturer confirmation AÇIK)
# (name, type, thickness) — VARSAYIM symmetric 4-layer build, L1-L2 / L3-L4 prepreg 0.2 mm (PCB-HANDOFF §1 hot loop)
STACKUP = [("F.SilkS", "Top Silk Screen", None), ("F.Paste", "Top Solder Paste", None),
           ("F.Mask", "Top Solder Mask", 0.01), ("F.Cu", "copper", CU_MM), ("dielectric 1", "prepreg", 0.2),
           ("In1.Cu", "copper", CU_MM), ("dielectric 2", "core", 1.04), ("In2.Cu", "copper", CU_MM),
           ("dielectric 3", "prepreg", 0.2), ("B.Cu", "copper", CU_MM), ("B.Mask", "Bottom Solder Mask", 0.01),
           ("B.Paste", "Bottom Solder Paste", None), ("B.SilkS", "Bottom Silk Screen", None)]
CLASS_OF = {"INPUT_POWER": "INPUT_POWER", "BUS_POWER": "BUS_POWER", "PHASE_POWER": "PHASE_POWER",
            "O1_PORT": "O1_PORT", "S2E_PORT": "S2E_PORT"}          # routing-g2 row -> project netclass (same names)
RENAMED = {"O1_POWER": "O1_PORT", "S2E_POWER": "S2E_PORT"}        # G1 project names -> routing-g2 names
PATTERN_RENAMED = {"Net-(CBOOT1-Pad1)": "/CBOOT_R1", "Net-(CBOOT2-Pad1)": "/CBOOT_R2"}   # G5 T-007 named RBOOT nets
EXTRA_PATTERNS = {"/ISO_GATE": "AUX_LOCAL", "/ISO_VCAP": "AUX_LOCAL"}   # PCB-HANDOFF §2 GATE >= 0.4 mm (AUX 0.5)
NO_MIN_WIDTH_NETS = {"/GND"}     # GND return is the L2 plane (PCB-HANDOFF §1); pad stubs cannot be 4.9 mm
HV_NETS = ["/ANODE", "/VIN", "/VOUT", "/VSAFE"]                    # PCB-HANDOFF §5
HV_CLEARANCE_MM = 0.6
DFM_MIN_MM = 0.15                # PCB-HANDOFF §7 DFM VARSAYIM min track/space


def routing_rows() -> dict:
    return {r["name"]: r for r in json.loads(ROUTING.read_text(encoding="utf-8"))["rows"]}


def up(v: float, step: float = 0.01) -> float:
    return round(math.ceil(v / step - 1e-9) * step, 2)


def netlist_nets() -> set:
    root = ks.top(ks.parse(NETLIST.read_text(encoding="utf-8")))
    return {next(n.children("name")).atoms()[1].value for n in next(root.children("nets")).children("net")}


# --------------------------------------------------------------------------- stackup (PDU.kicad_pcb)
def stackup_text() -> str:
    t = "\t\t"
    out = ["(stackup"]
    for name, typ, th in STACKUP:
        extra = ""
        if th is not None:
            extra += f"\n{t}\t\t(thickness {th:g})"
        if typ in ("prepreg", "core"):
            extra += f'\n{t}\t\t(material "FR4")\n{t}\t\t(epsilon_r 4.5)\n{t}\t\t(loss_tangent 0.02)'
        out.append(f'\n{t}\t(layer "{name}"\n{t}\t\t(type "{typ}"){extra}\n{t}\t)')
    out.append(f'\n{t}\t(copper_finish "ENIG")\n{t}\t(dielectric_constraints no)\n{t})')
    return "".join(out)


def apply_stackup(text: str) -> str:
    root = ks.parse(text)
    pcb = ks.top(root)
    setup = next(pcb.children("setup"))
    old = next(setup.children("stackup"), None)
    if old is not None:
        ks.remove_node(setup, old)
    ks.insert_after(setup, setup[0] if not isinstance(setup[0], ks.WS) else setup[1], stackup_text(), indent="\n\t\t")
    gen = next(pcb.children("general"))
    th = next(gen.children("thickness"))
    th[th.index(th.atoms()[1])] = ks.Atom(f"{sum(t for _, _, t in STACKUP if t):g}")
    return ks.dumps(root)


# --------------------------------------------------------------------------- netclasses (PDU.kicad_pro)
def apply_netclasses(pro: dict, rows: dict, nets: set) -> list:
    log = []
    ns = pro["net_settings"]
    for c in ns["classes"]:
        if c["name"] in RENAMED:
            log.append(f"class {c['name']} -> {RENAMED[c['name']]}")
            c["name"] = RENAMED[c["name"]]
    by = {c["name"]: c for c in ns["classes"]}
    for row, cls in CLASS_OF.items():
        w = rows[row]["selected_width_mm"]
        if by[cls]["track_width"] != w:
            log.append(f"{cls} track_width {by[cls]['track_width']} -> {w}")
            by[cls]["track_width"] = w
    pats = []
    for p in ns["netclass_patterns"]:
        p["netclass"] = RENAMED.get(p["netclass"], p["netclass"])
        if p["pattern"] in PATTERN_RENAMED:
            log.append(f"pattern renamed: {p['pattern']} -> {PATTERN_RENAMED[p['pattern']]}")
            p["pattern"] = PATTERN_RENAMED[p["pattern"]]
        if p["pattern"] not in nets:
            log.append(f"pattern dropped (net not in netlist): {p['pattern']} [{p['netclass']}]")
            continue
        pats.append(p)
    have = {p["pattern"] for p in pats}
    for row, cls in CLASS_OF.items():
        for n in rows[row]["nets"]:
            if n not in have and n in nets:
                pats.append({"netclass": cls, "pattern": n})
                log.append(f"pattern added: {n} [{cls}]")
    for n, cls in EXTRA_PATTERNS.items():
        if n not in have and n in nets:
            pats.append({"netclass": cls, "pattern": n})
            log.append(f"pattern added: {n} [{cls}]")
    ns["netclass_patterns"] = pats
    return log


# --------------------------------------------------------------------------- rules (PDU.kicad_dru)
def dru_text(rows: dict) -> str:
    power = " || ".join(f"A.NetClass == '{c}'" for c in CLASS_OF.values())
    lines = ["(version 1)",
             "# T-013 generated by scripts/pcb_rules.py from reports/g2/routing-g2.json — do not edit by hand.",
             "# min = outer-layer minimum width (HESAP, IPC-2221 fit + 50 mV drop), opt = selected width (router default)."]
    for row, cls in CLASS_OF.items():
        r = rows[row]
        cond = f"A.NetClass == '{cls}'" + "".join(f" && A.NetName != '{n}'" for n in sorted(NO_MIN_WIDTH_NETS))
        lines.append(f'(rule "{cls} width"\n\t(condition "{cond}")\n'
                     f'\t(constraint track_width (min {up(r["outer_width_min_mm"]):g}mm) (opt {r["selected_width_mm"]:g}mm)))')
    lines.append("# Neck-down where a power track enters a footprint (fine-pitch pads); later rules take precedence.")
    lines.append(f'(rule "power neck-down inside courtyards"\n\t(condition "({power}) && A.intersectsCourtyard(\'*\')")\n'
                 f'\t(constraint track_width (min 0.25mm)))')
    lines.append("# Pads of one footprint: fine-pitch packages (SOT-23-6, VSSOP, SC-70) have 0.15 mm pad gaps by design;")
    lines.append("# netclass clearance (0.2-0.3 mm) applies between footprints. 0.15 mm = DFM minimum (PCB-HANDOFF §7 VARSAYIM).")
    lines.append('(rule "pads within one footprint"\n\t(condition "A.Type == \'Pad\' && B.Type == \'Pad\' && A.Parent == B.Parent")\n'
                 f'\t(constraint clearance (min {DFM_MIN_MM:g}mm)))')
    hv = " || ".join(f"A.NetName == '{n}'" for n in HV_NETS)
    hvb = " && ".join(f"B.NetName != '{n}'" for n in HV_NETS + ["/GND"])
    lines.append("# PCB-HANDOFF §5: fault voltage up to 53.3 V (TVS clamp) — HV copper to other nets >= 0.6 mm (tracks/zones).")
    lines.append(f'(rule "HV to logic clearance"\n\t(condition "({hv}) && {hvb} && A.Type != \'Pad\' && B.Type != \'Pad\'")\n'
                 f'\t(constraint clearance (min {HV_CLEARANCE_MM:g}mm)))')
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- check
def check() -> list:
    errs = []
    rows = routing_rows()
    pro = json.loads(PRO.read_text(encoding="utf-8"))
    by = {c["name"]: c for c in pro["net_settings"]["classes"]}
    pats = {p["pattern"]: p["netclass"] for p in pro["net_settings"]["netclass_patterns"]}
    dru = DRU.read_text(encoding="utf-8") if DRU.exists() else ""
    nets = netlist_nets()
    for row, cls in CLASS_OF.items():
        r = rows[row]
        if cls not in by:
            errs.append(f"netclass {cls} missing in PDU.kicad_pro")
            continue
        if by[cls]["track_width"] != r["selected_width_mm"]:
            errs.append(f"{cls}: pro track_width {by[cls]['track_width']} != routing-g2 {r['selected_width_mm']}")
        m = re.search(rf'\(rule "{cls} width".*?\(min ([\d.]+)mm\) \(opt ([\d.]+)mm\)', dru, re.S)
        if not m or float(m.group(2)) != r["selected_width_mm"] or float(m.group(1)) != up(r["outer_width_min_mm"]):
            errs.append(f"{cls}: PDU.kicad_dru width rule missing or != routing-g2")
        for n in r["nets"]:
            if n in nets and pats.get(n) != cls:
                errs.append(f"net {n} not assigned to {cls} (got {pats.get(n)})")
    for p, c in pats.items():
        if p not in nets:
            errs.append(f"stale netclass pattern {p} [{c}]")
    root = ks.top(ks.parse(PCB.read_text(encoding="utf-8")))
    cu = [c for c in next(root.children("layers")).children() if len(c.atoms()) > 2 and c.atoms()[2].value == "signal"]
    if len(cu) != 4:
        errs.append(f"copper layers {len(cu)} != 4")
    st = next(next(root.children("setup")).children("stackup"), None)
    if st is None:
        errs.append("no stackup in PDU.kicad_pcb")
    else:
        tot, cus = 0.0, []
        for lay in st.children("layer"):
            th = next(lay.children("thickness"), None)
            typ = next(lay.children("type")).atoms()[1].value
            if th is not None:
                tot += float(th.atoms()[1].value)
                if typ == "copper":
                    cus.append(float(th.atoms()[1].value))
        if abs(tot - 1.6) > 1e-6 or cus != [CU_MM] * 4:
            errs.append(f"stackup total {tot:.3f} mm, copper {cus}")
    pts = []
    for g in root.children("gr_line"):
        if next(g.children("layer")).atoms()[1].value == "Edge.Cuts":
            for k in ("start", "end"):
                a = next(g.children(k)).atoms()
                pts.append((float(a[1].value), float(a[2].value)))
    if pts:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        size = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3))
        if size != BOARD_MM:
            errs.append(f"outline {size} != D-006 {BOARD_MM}")
    else:
        errs.append("no Edge.Cuts outline")
    return errs


def main(argv) -> int:
    if "--check" not in argv:
        rows = routing_rows()
        PCB.write_bytes(apply_stackup(PCB.read_bytes().decode("utf-8")).encode("utf-8"))
        pro = json.loads(PRO.read_text(encoding="utf-8"))
        log = apply_netclasses(pro, rows, netlist_nets())
        with PRO.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(pro, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with DRU.open("w", encoding="utf-8", newline="\n") as f:
            f.write(dru_text(rows))
        print("\n".join(log))
    errs = check()
    print(json.dumps({"pass": not errs, "errors": errs}, ensure_ascii=False))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
