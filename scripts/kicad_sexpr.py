"""Lossless S-expression reader/writer for KiCad files (standard library only).

Every byte (whitespace, quoting, newlines) is kept, so parse() -> dump() is byte-identical. Edits replace atoms or
insert/remove whole sub-lists; untouched text keeps KiCad's own formatting, which keeps git diffs minimal.

    python scripts/kicad_sexpr.py roundtrip PDU.kicad_sch          # exit 0 if byte-identical
    python scripts/kicad_sexpr.py set-prop PDU.kicad_sch R1 Value 10k --out tmp.kicad_sch
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


class Atom:
    __slots__ = ("raw",)

    def __init__(self, raw: str):
        self.raw = raw

    @property
    def value(self) -> str:
        r = self.raw
        if r.startswith('"'):
            return r[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        return r

    def __repr__(self):
        return f"Atom({self.raw!r})"


class WS(str):
    """Whitespace run between tokens (kept verbatim)."""


class SList(list):
    """A parenthesised list; elements are Atom, WS or SList."""

    @property
    def head(self) -> str:
        for x in self:
            if isinstance(x, Atom):
                return x.value
            if isinstance(x, SList):
                return ""
        return ""

    def atoms(self) -> list:
        return [x for x in self if not isinstance(x, WS)]

    def children(self, head: str | None = None):
        for x in self:
            if isinstance(x, SList) and (head is None or x.head == head):
                yield x


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse(text: str) -> SList:
    """Return a root SList holding top-level WS and lists."""
    root = SList()
    stack = [root]
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n":
            j = i
            while j < n and text[j] in " \t\r\n":
                j += 1
            stack[-1].append(WS(text[i:j]))
            i = j
        elif c == "(":
            lst = SList()
            stack[-1].append(lst)
            stack.append(lst)
            i += 1
        elif c == ")":
            if len(stack) == 1:
                raise ValueError(f"unbalanced ')' at offset {i}")
            stack.pop()
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            stack[-1].append(Atom(text[i:j + 1]))
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in ' \t\r\n()"':
                j += 1
            stack[-1].append(Atom(text[i:j]))
            i = j
    if len(stack) != 1:
        raise ValueError("unbalanced '(' at end of file")
    return root


def dump(node) -> str:
    if isinstance(node, Atom):
        return node.raw
    if isinstance(node, WS):
        return str(node)
    inner = "".join(dump(x) for x in node)
    return inner if node is getattr(node, "_root", None) else "(" + inner + ")"


def dumps(root: SList) -> str:
    return "".join(dump(x) for x in root)


def walk(node):
    if isinstance(node, SList):
        yield node
        for x in node:
            yield from walk(x)


def symbol_by_ref(root: SList, ref: str) -> SList | None:
    """Placed schematic symbol (or PCB footprint) whose Reference property equals ref."""
    for node in walk(root):
        if node.head in ("symbol", "footprint"):
            for prop in node.children("property"):
                a = prop.atoms()
                if len(a) >= 3 and a[1].value == "Reference" and a[2].value == ref:
                    return node
    return None


def set_property(root: SList, ref: str, name: str, value: str) -> bool:
    sym = symbol_by_ref(root, ref)
    if sym is None:
        return False
    for prop in sym.children("property"):
        a = prop.atoms()
        if len(a) >= 3 and a[1].value == name:
            idx = prop.index(a[2])
            prop[idx] = Atom(quote(value))
            return True
    return False


def top(root: SList) -> SList:
    """The single top-level list of a KiCad file (kicad_sch / kicad_pcb / footprint)."""
    return next(x for x in root if isinstance(x, SList))


def remove_node(parent: SList, node: SList) -> None:
    """Remove a child list together with the whitespace run in front of it (keeps formatting tidy)."""
    i = next(k for k, x in enumerate(parent) if x is node)
    j = i - 1 if i > 0 and isinstance(parent[i - 1], WS) else i
    del parent[j:i + 1]


def insert_after(parent: SList, anchor: SList, text: str, indent: str = "\n\t") -> SList:
    """Parse `text` (one S-expression) and insert it after `anchor` with KiCad-style indentation."""
    node = next(x for x in parse(text) if isinstance(x, SList))
    i = next(k for k, x in enumerate(parent) if x is anchor)
    parent[i + 1:i + 1] = [WS(indent), node]
    return node


def labels(sch: SList, text: str):
    return [n for n in sch.children("label") if n.atoms()[1].value == text]


def at_of(node: SList):
    a = next(node.children("at"), None)
    return tuple(float(x.value) for x in a.atoms()[1:3]) if a is not None else None


def wire_text(p1, p2, uuid: str) -> str:
    # same layout KiCad 10 writes in PDU.kicad_sch (default stroke omitted)
    return f'(wire\n\t\t(pts\n\t\t\t(xy {p1[0]:g} {p1[1]:g})\n\t\t\t(xy {p2[0]:g} {p2[1]:g})\n\t\t)\n\t\t(uuid "{uuid}")\n\t)'


def set_or_add_property(root: SList, ref: str, name: str, value: str) -> str:
    """Set a symbol property; add it (hidden, at the symbol origin) when missing. Returns 'set', 'added' or 'missing-ref'."""
    if set_property(root, ref, name, value):
        return "set"
    sym = symbol_by_ref(root, ref)
    if sym is None:
        return "missing-ref"
    x, y = at_of(sym)
    last = [p for p in sym.children("property")][-1]
    insert_after(sym, last, f'(property "{name}" {quote(value)}\n\t\t\t(at {x:g} {y:g} 0)\n\t\t\t(hide yes)\n'
                            f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)', indent="\n\t\t")
    return "added"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("roundtrip")
    r.add_argument("file")
    s = sub.add_parser("set-prop")
    s.add_argument("file")
    s.add_argument("ref")
    s.add_argument("name")
    s.add_argument("value")
    s.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    src = Path(a.file).read_bytes().decode("utf-8")
    root = parse(src)
    if a.cmd == "roundtrip":
        ok = dumps(root) == src
        print(f"{a.file}: {'byte-identical' if ok else 'DIFFERENT'} ({len(src)} chars)")
        return 0 if ok else 1
    if not set_property(root, a.ref, a.name, a.value):
        print(f"{a.ref}.{a.name} not found")
        return 1
    Path(a.out).write_bytes(dumps(root).encode("utf-8"))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
