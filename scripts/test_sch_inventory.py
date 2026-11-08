"""Tests for the T-027 inventory joins (standard library only; no KiCad needed)."""
from __future__ import annotations

import sys
from pathlib import Path

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
