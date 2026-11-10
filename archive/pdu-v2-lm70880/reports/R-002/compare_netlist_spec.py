#!/usr/bin/env python3
"""Independent checker for T-014's recorded KiCad netlist against the pin/value/MPN/footprint spec."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+')
PIN_NUM_SUFFIX = re.compile(r"^(.+)\((\d+)\)$")


def parse_sexpr(text):
    tokens = TOKEN.findall(text)
    pos = 0

    def parse_one():
        nonlocal pos
        if tokens[pos] != "(":
            raise ValueError(f"expected '(' at token {pos}")
        pos += 1
        out = []
        while tokens[pos] != ")":
            token = tokens[pos]
            if token == "(":
                out.append(parse_one())
            else:
                pos += 1
                out.append(json.loads(token) if token.startswith('"') else token)
        pos += 1
        return out

    root = parse_one()
    if pos != len(tokens):
        raise ValueError("trailing tokens")
    return root


def children(node, name):
    return [item for item in node if isinstance(item, list) and item and item[0] == name]


def child_value(node, name, default=""):
    found = children(node, name)
    return found[0][1] if found and len(found[0]) > 1 else default


def canonical_expected_net(net):
    if net.startswith("/"):
        return "/" + net.lstrip("/").split("(", 1)[0]
    return net


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--netlist", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root_dir = Path(__file__).resolve().parents[2]
    spec_path = args.spec or root_dir / "design/pdu_v2_spec.yaml"
    netlist_path = args.netlist or root_dir / "reports/R-002/t014-builder-netlist-input.net"
    output_path = args.json

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    net_root = parse_sexpr(netlist_path.read_text(encoding="utf-8"))
    comp_section = children(net_root, "components")[0]
    net_section = children(net_root, "nets")[0]

    components = {}
    for comp in children(comp_section, "comp"):
        ref = child_value(comp, "ref")
        fields = {}
        for section in children(comp, "fields"):
            for field in children(section, "field"):
                name = child_value(field, "name")
                vals = [x for x in field[1:] if not isinstance(x, list)]
                fields[name] = vals[-1] if vals else ""
        components[ref] = {
            "value": child_value(comp, "value"),
            "footprint": child_value(comp, "footprint"),
            "mpn": fields.get("MPN", ""),
            "by_pin_number": {},
            "by_pin_name": {},
            "all_nodes": [],
        }

    for net in children(net_section, "net"):
        net_name = child_value(net, "name")
        for node in children(net, "node"):
            ref = child_value(node, "ref")
            pin = child_value(node, "pin")
            if ref not in components:
                continue
            components[ref]["by_pin_number"].setdefault(pin, set()).add(net_name)
            pinfunction = child_value(node, "pinfunction")
            name = re.sub(rf"_{re.escape(pin)}$", "", pinfunction) if pinfunction else ""
            components[ref]["all_nodes"].append({"pin": pin, "name": name, "net": net_name})
            if name:
                components[ref]["by_pin_name"].setdefault(name, set()).add(net_name)

    spec_parts = spec["parts"]
    pcb_parts = [part for part in spec_parts if part.get("pins")]
    spec_refs = {part["ref"] for part in pcb_parts}
    net_refs = set(components)
    mismatches = []

    if spec_refs != net_refs:
        mismatches.append({
            "kind": "ref_set",
            "spec_only": sorted(spec_refs - net_refs),
            "netlist_only": sorted(net_refs - spec_refs),
        })

    compared_components = 0
    compared_pin_keys = 0
    for part in pcb_parts:
        ref = part["ref"]
        actual = components.get(ref)
        if actual is None:
            continue
        compared_components += 1
        for field in ("value", "mpn", "footprint"):
            expected = part.get(field, "")
            got = actual[field]
            if got != expected:
                mismatches.append({"kind": field, "ref": ref, "expected": expected, "actual": got})

        for key, raw_net in (part.get("pins") or {}).items():
            compared_pin_keys += 1
            key = str(key)
            number_match = PIN_NUM_SUFFIX.fullmatch(key)
            if key.isdigit():
                hits = actual["by_pin_number"].get(key, set())
            elif number_match:
                hits = actual["by_pin_number"].get(number_match.group(2), set())
            else:
                hits = actual["by_pin_name"].get(key.replace(" ", ""), set())
                if not hits:
                    hits = set()
                    for name, nets in actual["by_pin_name"].items():
                        if re.fullmatch(re.escape(key.replace(" ", "")) + r"\d+", name.replace(" ", "")) and name not in (part.get("pins") or {}):
                            hits.update(nets)

            actual_nets = sorted(net for net in hits if not net.startswith("unconnected-"))
            want = canonical_expected_net(str(raw_net))
            is_nc = want.upper().startswith(("NC", "DNC", "/NC", "/DNC"))
            if is_nc:
                if actual_nets:
                    mismatches.append({"kind": "pin_net", "ref": ref, "pin": key, "expected": "NC", "actual": actual_nets})
            else:
                got = actual_nets[0] if len(actual_nets) == 1 else actual_nets or None
                if got != want:
                    mismatches.append({"kind": "pin_net", "ref": ref, "pin": key, "expected": want, "actual": got})

    unmapped_nodes = []
    for part in pcb_parts:
        ref = part["ref"]
        actual = components.get(ref)
        if actual is None:
            continue
        spec_keys = [str(key) for key in (part.get("pins") or {})]
        for node in actual["all_nodes"]:
            pin, name = node["pin"], node["name"]
            matched = False
            for key in spec_keys:
                number_match = PIN_NUM_SUFFIX.fullmatch(key)
                if key.isdigit() and key == pin:
                    matched = True
                elif number_match and number_match.group(2) == pin:
                    matched = True
                elif name.replace(" ", "") == key.replace(" ", ""):
                    matched = True
                elif name and re.fullmatch(re.escape(key.replace(" ", "")) + r"\d+", name.replace(" ", "")) and name not in spec_keys:
                    matched = True
            if not matched:
                unmapped_nodes.append({"ref": ref, "pin": pin, "pinfunction": name, "net": node["net"]})

    result = {
        "spec_rows_total": len(spec_parts),
        "spec_pcb_refs": len(pcb_parts),
        "spec_nonpcb_rows_without_pin_map": len(spec_parts) - len(pcb_parts),
        "netlist_components": len(components),
        "ref_set_match": spec_refs == net_refs,
        "components_checked_value_mpn_footprint": compared_components,
        "pin_keys_checked": compared_pin_keys,
        "netlist_nodes_checked": sum(len(components[ref]["all_nodes"]) for ref in net_refs),
        "netlist_nodes_without_spec_pin_key": len(unmapped_nodes),
        "unmapped_netlist_nodes": unmapped_nodes,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "input_spec": str(spec_path.relative_to(root_dir)),
        "input_netlist": str(netlist_path.relative_to(root_dir)),
        "note": "Netlist input is the committed T-014 KiCad 10.0.7 export; this script does not claim to freshly export it.",
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    if output_path:
        output_path.write_text(rendered, encoding="utf-8")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
