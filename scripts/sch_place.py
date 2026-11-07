"""Generic schematic part placement for the G5 block scripts (lossless S-expression edits, standard library only).

place_part(root, ref, lib_id, at, spec_row) adds one symbol instance:
  * copies the library symbol into the schematic lib_symbols cache (stock KiCad library or hardware/lib/PDU.kicad_sym,
    resolving `extends`),
  * writes Reference / Value / Footprint / Datasheet / MPN properties and the project instance path,
  * puts a local label with the spec net on every pin end ("/NET(comment)" -> "NET"), or a no_connect flag for spec
    nets "NC..." / "DNC" — no wires are drawn, so placement cannot short existing nets.
"""
from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

import kicad_sexpr as ks

ROOT = Path(__file__).resolve().parents[1]
STOCK = Path(os.environ.get("KICAD_SYM_DIR", "C:/Program Files/KiCad/10.0/share/kicad/symbols"))
PDU_LIB = ROOT / "hardware" / "lib" / "PDU.kicad_sym"
_LIB_CACHE: dict = {}


def uid(tag: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"PDU/G5/{tag}"))


def _lib(lib: str):
    path = PDU_LIB if lib == "PDU" else STOCK / f"{lib}.kicad_sym"
    if path not in _LIB_CACHE:
        _LIB_CACHE[path] = ks.top(ks.parse(path.read_text(encoding="utf-8")))
    return _LIB_CACHE[path]


def lib_symbol_text(lib_id: str) -> str:
    """Self-contained symbol text named lib_id (inner unit names keep the bare symbol name)."""
    lib, name = lib_id.split(":", 1)
    sym = next(s for s in _lib(lib).children("symbol") if s.atoms()[1].value == name)
    ext = next(sym.children("extends"), None)
    if ext is not None:  # derived symbol: body (units/pins) from the parent, properties from the child
        parent = next(s for s in _lib(lib).children("symbol") if s.atoms()[1].value == ext.atoms()[1].value)
        pname = parent.atoms()[1].value
        props = "".join("\n\t\t\t" + ks.dump(p) for p in sym.children("property"))
        others = [c for c in parent.children() if c.head not in ("property",)]
        body = "".join("\n\t\t\t" + ks.dump(c).replace(f'"{pname}_', f'"{name}_') for c in others)
        txt = f'(symbol "{lib_id}"{props}{body}\n\t\t)'
    else:
        txt = ks.dump(sym)
        txt = txt.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    return txt


def ensure_lib_symbol(sch, lib_id: str) -> None:
    cache = next(sch.children("lib_symbols"))
    if not any(s.atoms()[1].value == lib_id for s in cache.children("symbol")):
        last = list(cache.children("symbol"))[-1]
        ks.insert_after(cache, last, lib_symbol_text(lib_id), indent="\n\t\t")


def net_name(spec_net: str) -> str | None:
    n = spec_net.strip()
    if n.upper().startswith(("NC", "DNC")):
        return None
    return n.lstrip("/").split("(")[0]


def _prop(name, value, x, y, hide=False):
    h = "\n\t\t\t(hide yes)" if hide else ""
    return (f'\n\t\t(property "{name}" {ks.quote(value)}\n\t\t\t(at {x:g} {y:g} 0){h}\n\t\t\t(effects\n\t\t\t\t(font\n'
            f'\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)')


def _pin_names(sch, lib_id: str) -> dict:
    lib = ks.lib_symbol(sch, lib_id)
    out: dict = {}
    for p in ks.walk(lib):
        if p.head == "pin":
            out.setdefault(next(p.children("name")).atoms()[1].value, []).append(next(p.children("number")).atoms()[1].value)
    return out


def _set_at(root, ref: str, prop: str, x: float, y: float) -> None:
    sym = ks.symbol_by_ref(root, ref)
    for p in sym.children("property"):
        if p.atoms()[1].value == prop:
            at = next(p.children("at"))
            a = at.atoms()
            at[at.index(a[1])] = ks.Atom(f"{x:g}")
            at[at.index(a[2])] = ks.Atom(f"{y:g}")


def _place_texts(root, ref: str, lib_id: str, at, pins: dict) -> None:
    """Keep Reference/Value clear of the pin labels: beside two-pin parts, above/below the body of ICs."""
    x, y = at
    if lib_id.startswith(("Device:", "Switch:")):
        _set_at(root, ref, "Reference", x + 1.27, y - 1.27)
        _set_at(root, ref, "Value", x + 1.27, y + 1.27)
        return
    ys = [p[1] for p in pins.values()] or [y]
    _set_at(root, ref, "Reference", x, min(ys) - 3.81)
    _set_at(root, ref, "Value", x, max(ys) + 3.81)


def place_part(root, ref: str, lib_id: str, at, row: dict, ref_prefix: str = "U", rot: int = 0, in_bom: bool = True) -> dict:
    sch = ks.top(root)
    if ks.symbol_by_ref(root, ref) is not None:
        return {}
    ensure_lib_symbol(sch, lib_id)
    sheet = next(sch.children("uuid")).atoms()[1].value
    x, y = at
    txt = (f'(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {x:g} {y:g} {rot})\n\t\t(unit 1)\n\t\t(in_bom {"yes" if in_bom else "no"})\n\t\t(on_board yes)'
           f'\n\t\t(dnp no)\n\t\t(uuid "{uid(ref)}")'
           + _prop("Reference", ref, x + 2.54, y - 5.08) + _prop("Value", row["value"], x + 2.54, y + 5.08)
           + _prop("Footprint", row["footprint"], x, y, True) + _prop("Datasheet", "", x, y, True)
           + _prop("MPN", row["mpn"], x, y, True)
           + f'\n\t\t(instances\n\t\t\t(project "PDU"\n\t\t\t\t(path "/{sheet}"\n\t\t\t\t\t(reference "{ref}")\n'
             f'\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
    anchor = list(sch.children("symbol"))[-1]
    ks.insert_after(sch, anchor, txt)
    pins = ks.pin_points(sch, root, ref)
    _place_texts(root, ref, lib_id, (x, y), pins)
    label_anchor = next(sch.children("label"))
    placed = {}
    names = _pin_names(sch, lib_id)
    for key, net in row["pins"].items():
        if re.fullmatch(r"\d+-\d+", key):
            nums = [str(n) for n in range(int(key.split("-")[0]), int(key.split("-")[1]) + 1)]
        elif key in pins:
            nums = [key]
        else:                                   # named spec key (A/K, S/G/D ...)
            nums = names.get(key, [])
        for num in nums:
            if num not in pins:
                continue
            pt = pins[num]
            nm = net_name(net)
            side = 180 if pt[0] < x else 0
            if nm is None:
                ks.insert_after(sch, label_anchor, f'(no_connect\n\t\t(at {pt[0]:g} {pt[1]:g})\n\t\t(uuid "{uid(ref + "-nc-" + num)}")\n\t)')
            else:
                just = "right bottom" if side == 180 else "left bottom"
                ks.insert_after(sch, label_anchor,
                                f'(label "{nm}"\n\t\t(at {pt[0]:g} {pt[1]:g} {side})\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n'
                                f'\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{uid(ref + "-lbl-" + num)}")\n\t)')
            placed[num] = nm
    return placed
