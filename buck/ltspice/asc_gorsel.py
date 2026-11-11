#!/usr/bin/env python3
"""LTspice .asc sematigini SVG gorsele cevirir (GitHub'da goruntulenebilsin diye).

Kullanim: python asc_gorsel.py [sematik.asc]   ->  ayni adla .svg
Semboller LTspice kurulumundaki lib/sym/*.asy dosyalarindan okunur; LTspice acilmaz.
.asc her degistiginde bu betik yeniden kosulmalidir (sematik_uret.py bunu kendisi yapar).
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

SYM = Path(os.environ.get("LOCALAPPDATA", "")) / "LTspice" / "lib" / "sym"
FS = {0: 8, 1: 10, 2: 13, 3: 17, 4: 22, 5: 28, 6: 36, 7: 46}   # LTspice yazi boyutu -> px


def rot(rt: str, x: float, y: float) -> tuple[float, float]:
    mir = rt.startswith("M")
    a = int(rt[1:])
    if a == 90:
        x, y = -y, x
    elif a == 180:
        x, y = -x, -y
    elif a == 270:
        x, y = y, -x
    if mir:
        x = -x
    return x, y


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_symbol(name: str):
    local = Path(__file__).with_name(f"{name}.asy")      # once sematigin yanindaki ozel semboller
    raw = (local if local.exists() else SYM / f"{name}.asy").read_bytes()
    txt = raw.decode("utf-16-le") if raw[1:2] == b"\x00" else raw.decode("latin-1")
    prim, win = [], {}
    for ln in txt.splitlines():
        p = ln.split()
        if not p:
            continue
        if p[0] in ("LINE", "RECTANGLE", "CIRCLE", "ARC"):
            prim.append((p[0], [float(v) for v in p[2:]]))
        elif p[0] == "WINDOW":
            win[int(p[1])] = (float(p[2]), float(p[3]), p[4], int(p[5]))
    return prim, win


class Canvas:
    def __init__(self):
        self.el: list[str] = []
        self.x0 = self.y0 = 1e9
        self.x1 = self.y1 = -1e9

    def ext(self, x, y):
        self.x0, self.y0 = min(self.x0, x), min(self.y0, y)
        self.x1, self.y1 = max(self.x1, x), max(self.y1, y)

    def line(self, pts, color="#1a1a1a", w=1.6):
        for x, y in pts:
            self.ext(x, y)
        self.el.append(f'<polyline fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" '
                       f'stroke-linejoin="round" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>')

    def text(self, x, y, s, size=13, color="#1a1a1a", anchor="start", bold=False):
        lines = s.split("\\n")
        for i, t in enumerate(lines):
            yy = y + i * size * 1.35
            wpx = 0.56 * size * len(t)
            xa = x if anchor == "start" else (x - wpx if anchor == "end" else x - wpx / 2)
            self.ext(xa, yy - size)
            self.ext(xa + wpx, yy + size * 0.4)
            self.el.append(f'<text x="{x:.1f}" y="{yy:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}"'
                           f'{" font-weight=\"bold\"" if bold else ""} dominant-baseline="middle">{esc(t)}</text>')

    def dot(self, x, y, r=3.2, color="#1a1a1a"):
        self.el.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def svg(self, pad=24) -> str:
        w, h = self.x1 - self.x0 + 2 * pad, self.y1 - self.y0 + 2 * pad
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{self.x0 - pad:.0f} {self.y0 - pad:.0f} {w:.0f} {h:.0f}" '
                f'width="{w:.0f}" height="{h:.0f}" font-family="Consolas,Menlo,monospace">\n'
                f'<rect x="{self.x0 - pad:.0f}" y="{self.y0 - pad:.0f}" width="{w:.0f}" height="{h:.0f}" fill="white"/>\n'
                + "\n".join(self.el) + "\n</svg>\n")


def render(asc: Path) -> Path:
    raw = asc.read_bytes()
    txt = raw.decode("utf-16-le") if raw[1:2] == b"\x00" else raw.decode("cp1252")
    cv = Canvas()
    wires, flags, syms, texts = [], [], [], []
    for ln in txt.splitlines():
        p = ln.split()
        if not p:
            continue
        if p[0] == "WIRE":
            wires.append(tuple(int(v) for v in p[1:5]))
        elif p[0] == "FLAG":
            flags.append((int(p[1]), int(p[2]), p[3]))
        elif p[0] == "SYMBOL":
            syms.append(dict(name=p[1], x=int(p[2]), y=int(p[3]), rot=p[4], attr={}, win={}))
        elif p[0] == "WINDOW" and syms:
            syms[-1]["win"][int(p[1])] = (float(p[2]), float(p[3]), p[4], int(p[5]))
        elif p[0] == "SYMATTR" and syms:
            syms[-1]["attr"][p[1]] = ln.split(None, 2)[2] if len(p) > 2 else ""
        elif p[0] == "TEXT":
            body = ln.split(None, 5)[5]
            texts.append((int(p[1]), int(p[2]), int(p[4]), body))

    # teller ve baglanti noktalari
    ends: dict[tuple[int, int], int] = {}
    for x1, y1, x2, y2 in wires:
        cv.line([(x1, y1), (x2, y2)], color="#0b3d91")
        for pt in ((x1, y1), (x2, y2)):
            ends[pt] = ends.get(pt, 0) + 1
    for (x, y), n in ends.items():
        if n >= 3:
            cv.dot(x, y, color="#0b3d91")

    # semboller
    for s in syms:
        prim, win = load_symbol(s["name"])
        show_value = 3 in win                              # sembolde Value penceresi yoksa (alt devre adi) gosterme
        win = {**win, **s["win"]}
        T = lambda x, y: tuple(a + b for a, b in zip((s["x"], s["y"]), rot(s["rot"], x, y)))
        for kind, v in prim:
            if kind == "LINE":
                cv.line([T(v[0], v[1]), T(v[2], v[3])])
            elif kind == "RECTANGLE":
                cv.line([T(v[0], v[1]), T(v[2], v[1]), T(v[2], v[3]), T(v[0], v[3]), T(v[0], v[1])])
            else:
                cx, cy, rx, ry = (v[0] + v[2]) / 2, (v[1] + v[3]) / 2, abs(v[2] - v[0]) / 2, abs(v[3] - v[1]) / 2
                a0, a1 = 0.0, 2 * math.pi
                if kind == "ARC":   # ekranda saat yonunun tersine, baslangictan bitise
                    a0 = math.atan2(-(v[5] - cy), v[4] - cx)
                    a1 = math.atan2(-(v[7] - cy), v[6] - cx)
                    if a1 <= a0:
                        a1 += 2 * math.pi
                n = 40
                cv.line([T(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy - ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)])
        horiz = s["rot"] in ("R90", "R270", "M90", "M270")
        labels = [(0, s["attr"].get("InstName", ""), True)]
        if show_value:
            labels.append((3, s["attr"].get("Value", ""), False))
        if s["attr"].get("SpiceLine"):
            labels.append((39, s["attr"]["SpiceLine"], False))
        # sembolun dunya koordinatlarindaki kutusu (etiketleri govdeye carpmadan yerlestirmek icin)
        pts = [T(v[i], v[i + 1]) for _, v in prim for i in (0, 2)]
        bx0, by0 = min(p[0] for p in pts), min(p[1] for p in pts)
        bx1, by1 = max(p[0] for p in pts), max(p[1] for p in pts)
        for k, (wid, val, bold) in enumerate(labels):
            if not val:
                continue
            if horiz and s["name"] == "voltage":   # yatay kaynak: etiketler govdenin altina, saga yasli
                cv.text(bx1, by1 + 14 + k * 16, val, 12, anchor="end", bold=bold)
            elif horiz:    # yatay parca: etiketler govdenin ustune, ortali
                cv.text((bx0 + bx1) / 2, by0 - 12 - (len(labels) - 1 - k) * 16, val, 12, anchor="middle", bold=bold)
            else:          # dikey parca: etiketler govdenin sagina
                cv.text(bx1 + 8, (by0 + by1) / 2 - 16 + k * 16, val, 12, bold=bold)

    # dugum etiketleri ve toprak
    for x, y, name in flags:
        if name == "0":
            cv.line([(x, y), (x, y + 10)], color="#0b3d91")
            cv.line([(x - 12, y + 10), (x + 12, y + 10), (x, y + 24), (x - 12, y + 10)], color="#0b3d91")
        else:
            cv.dot(x, y, 2.6, "#b00020")
            on_h = any(y1 == y2 == y and min(x1, x2) <= x <= max(x1, x2) for x1, y1, x2, y2 in wires)
            if on_h:       # yatay hat uzerinde: etiket ustte
                cv.text(x + 5, y - 11, name, 12, color="#b00020", bold=True)
            else:          # dikey hat uzerinde: etiket solda
                cv.text(x - 7, y + 3, name, 12, color="#b00020", anchor="end", bold=True)

    # yazilar: ';' yorum, '!' SPICE yonergesi
    for x, y, size, body in texts:
        kind, body = body[0], body[1:]
        cv.text(x, y, body, FS.get(size, 13) * 0.9, color="#1a1a1a" if kind == "!" else "#2e6b2e", bold=(size >= 3))

    out = asc.with_suffix(".svg")
    out.write_text(cv.svg(), encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    a = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("buck_guc_kati.asc")
    print(render(a))
