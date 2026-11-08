"""Tests for the T-027 inventory joins (standard library only; no KiCad needed)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sch_inventory as si  # noqa: E402

NET = """(export (version "E")
 (components
  (comp (ref "R1") (value "1k") (footprint "F:R")
   (fields (field (name "MPN") "ABC"))
   (sheetpath (names "/") (tstamps "/"))
   (tstamps "u1 u2"))
  (comp (ref "TP_A") (value "TP") (footprint "F:TP") (sheetpath (names "/") (tstamps "/")) (tstamps "u3")))
 (nets
  (net (code "1") (name "/A") (node (ref "R1") (pin "1") (pinfunction "") (pintype "passive")) (node (ref "TP_A") (pin "1") (pintype "passive")))
  (net (code "2") (name "unconnected-(R1-Pad2)") (node (ref "R1") (pin "2") (pintype "passive+no_connect")))))
"""
PCB = {"R1": {"footprint": "F:R", "pads": {"1": ["/A"], "2": ["unconnected-(R1-Pad2)"]}}, "TP_A": {"footprint": "F:TP", "pads": {"1": ["/A"]}}}
BOM = {"R1": [{"ref": "R1", "value": "1k", "mpn": "ABC", "footprint": "F:R", "dnp": "False", "kind": "R"}]}


def run(pcb=PCB, bom=BOM):
    comps, pins = si.parse_netlist(NET)
    return si.build(comps, pins, pcb, bom, {"R1": [{}]}, {"R1"}, {"R1"}, None, "R1")


def test_multi_unit_symbol_is_one_reference_with_all_uuids():
    comps, _ = si.parse_netlist(NET)
    assert list(comps) == ["R1", "TP_A"] and comps["R1"]["uuids"] == ["u1", "u2"] and comps["R1"]["fields"]["MPN"] == "ABC"


def test_clean_join_has_every_reference_and_pin_once():
    refs, pins = run()
    assert [r["status"] for r in refs] == ["KAYITLI", "KAYITLI"]
    assert sorted((p["ref"], p["pin"]) for p in pins) == [("R1", "1"), ("R1", "2"), ("TP_A", "1")]
    assert all(p["state"] == "EŞLEŞTİ" for p in pins)


def test_no_connect_pin_is_marked_intentional():
    _, pins = run()
    assert next(p for p in pins if p["pin"] == "2")["nc"] == "kasıtlı NC"


def test_test_pad_is_bom_exempt_and_not_an_issue():
    refs, _ = run()
    tp = next(r for r in refs if r["ref"] == "TP_A")
    assert tp["class"].startswith("test") and tp["issues"] == ""


def test_pad_net_mismatch_and_missing_footprint_are_recorded():
    bad = {"R1": {"footprint": "F:R", "pads": {"1": ["/B"], "2": ["unconnected-(R1-Pad2)"]}}}
    refs, pins = run(pcb=bad)
    assert next(p for p in pins if p["ref"] == "R1" and p["pin"] == "1")["state"] == "UYUŞMAZ"
    assert next(p for p in pins if p["ref"] == "TP_A")["state"] == "AÇIK"
    assert next(r for r in refs if r["ref"] == "TP_A")["status"] == "UYUŞMAZ"


def test_value_mismatch_and_bom_dnp_are_recorded():
    bom = {"R1": [{"ref": "R1", "value": "2k", "mpn": "ABC", "footprint": "F:R", "dnp": "True", "kind": "R"}]}
    refs, _ = run(bom=bom)
    r = next(x for x in refs if x["ref"] == "R1")
    assert r["class"] == "DNP" and "değer farkı" in r["issues"] and "DNP farkı" in r["issues"]


def _nodes(*rows):
    return {(r, p): {"ref": r, "pin": p, "name": n, "type": "passive", "net": "/A"} for r, p, n in rows}


def test_expansion_one_key_covers_several_pins_and_test_pins_stay_inside_the_keys():
    pins = _nodes(("U1", "1", "VIN_1"), ("U1", "2", "VIN_2"), ("U1", "3", "EN_3"), ("U1", "4", "SPARE_4"), ("TP_A", "1", ""))
    x = si.spec_expansion(pins, {"U1": ["VIN", "EN"], "TP_A": ["1"]}, {"TP_A"})
    assert x["spec_pin_keys"] == 3 and x["nodes_matched_to_a_key"] == 4 and x["multi_pin_expansion"] == 1
    assert x["nodes_without_spec_key"] == 1 and x["nodes_without_spec_key_list"] == ["U1.4"] and x["total_nodes"] == 5
    assert x["test_injection_spec_keys_inside_the_key_count"] == 1 and x["keys_covering_several_pins"] == 1


def test_expansion_counts_add_up_to_all_nodes():
    pins = _nodes(("U1", "1", "VIN_1"), ("U1", "2", "VIN_2"), ("U1", "3", "X_3"))
    x = si.spec_expansion(pins, {"U1": ["VIN"]}, set())
    assert x["spec_pin_keys"] + x["multi_pin_expansion"] + x["nodes_without_spec_key"] == x["total_nodes"]


def test_spec_pin_keys_parser_stops_at_nets():
    text = 'parts:\n  - ref: R1\n    value: "1k"\n    pins:\n      "1": "/A"\n      "2": "/B"\n  - ref: F1\n    value: "x"\nnets:\n  "/A":\n    "1": "z"\n'
    assert si.spec_pin_keys(text) == {"R1": ["1", "2"]}


def test_normalize_replaces_the_absolute_source_path():
    text = '(design (source "C:\\\\Users\\\\me\\\\PDU\\\\PDU.kicad_sch") (date "d"))'
    out = si.normalize_netlist(text, Path("D:/elsewhere"))
    assert '(source "PDU.kicad_sch")' in out and "Users" not in out


def test_normalize_refuses_a_personal_path_that_survives():
    with pytest.raises(SystemExit):
        si.normalize_netlist('(design (source "a")) (x "C:\\\\Users\\\\me\\\\f")', Path("D:/elsewhere"))


def test_committed_netlist_has_no_personal_path():
    assert not si.PERSONAL_PATH.search((si.OUT / "netlist.net").read_text(encoding="utf-8"))

