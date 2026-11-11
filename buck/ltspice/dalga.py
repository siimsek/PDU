#!/usr/bin/env python3
"""LTspice ikili .raw okuyucu ve bagimsiz SVG dalga sekli cizici (matplotlib gerektirmez)."""
from __future__ import annotations

import numpy as np
from pathlib import Path


def read_raw(path) -> dict[str, np.ndarray]:
    b = Path(path).read_bytes()
    mark = "Binary:\n".encode("utf-16-le")
    k = b.index(mark)
    head = b[:k].decode("utf-16-le")
    data = b[k + len(mark):]
    nvar = npts = 0
    names: list[str] = []
    invars = False
    for line in head.splitlines():
        if line.startswith("No. Variables:"):
            nvar = int(line.split(":")[1])
        elif line.startswith("No. Points:"):
            npts = int(line.split(":")[1])
        elif line.startswith("Variables:"):
            invars = True
        elif invars and line.strip():
            names.append(line.split()[1])
    dbl = "double" in head.split("Flags:")[1].splitlines()[0]
    if dbl:
        arr = np.frombuffer(data, dtype="<f8", count=npts * nvar).reshape(npts, nvar)
        out = {n: arr[:, i].copy() for i, n in enumerate(names)}
    else:
        dt = np.dtype([("t", "<f8"), ("v", "<f4", (nvar - 1,))])
        arr = np.frombuffer(data, dtype=dt, count=npts)
        out = {names[0]: arr["t"].copy()}
        for i, n in enumerate(names[1:]):
            out[n] = arr["v"][:, i].astype(float)
    out[names[0]] = np.abs(out[names[0]])
    return out


def _ticks(lo, hi, n=5):
    span = hi - lo if hi > lo else 1.0
    step = 10 ** np.floor(np.log10(span / n))
    for m in (1, 2, 5, 10):
        if span / (step * m) <= n:
            step *= m
            break
    t0 = np.ceil(lo / step) * step
    return [t0 + i * step for i in range(int((hi - t0) / step) + 1)]


def svg_plot(path, title, t, panels, tscale=1e6, tunit="us", width=980, ph=170):
    """panels: [(ylabel, [(etiket, y_dizisi, renk), ...]), ...]; t saniye."""
    ml, mr, mt, gap = 70, 20, 40, 28
    H = mt + len(panels) * (ph + gap) + 20
    pw = width - ml - mr
    tt = (t - t[0]) * tscale
    # cizim icin en fazla ~4000 noktaya indir (min/max zarfi korunur)
    idx = np.arange(len(tt))
    if len(tt) > 6000:
        idx = np.unique(np.concatenate([np.linspace(0, len(tt) - 1, 6000).astype(int)]))
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{H}" font-family="Segoe UI,Arial" font-size="11">',
         f'<rect width="{width}" height="{H}" fill="white"/>',
         f'<text x="{ml}" y="22" font-size="14" font-weight="bold">{title}</text>']
    for pi, (ylabel, traces) in enumerate(panels):
        y0 = mt + pi * (ph + gap)
        lo = min(float(np.min(y)) for _, y, _ in traces)
        hi = max(float(np.max(y)) for _, y, _ in traces)
        pad = (hi - lo) * 0.08 or 0.5
        lo, hi = lo - pad, hi + pad
        s.append(f'<rect x="{ml}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="#888"/>')
        for v in _ticks(lo, hi):
            yy = y0 + ph - (v - lo) / (hi - lo) * ph
            s.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#ddd"/>')
            s.append(f'<text x="{ml - 6}" y="{yy + 4:.1f}" text-anchor="end">{v:.4g}</text>')
        for v in _ticks(tt[0], tt[-1], 10):
            xx = ml + (v - tt[0]) / (tt[-1] - tt[0]) * pw
            s.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{y0}" y2="{y0 + ph}" stroke="#eee"/>')
            s.append(f'<text x="{xx:.1f}" y="{y0 + ph + 13}" text-anchor="middle">{v:.4g}</text>')
        s.append(f'<text x="14" y="{y0 + ph / 2}" transform="rotate(-90 14 {y0 + ph / 2})" text-anchor="middle">{ylabel}</text>')
        for ti, (lab, y, col) in enumerate(traces):
            xs = ml + (tt[idx] - tt[0]) / (tt[-1] - tt[0]) * pw
            ys = y0 + ph - (np.asarray(y)[idx] - lo) / (hi - lo) * ph
            pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(xs, ys))
            s.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.1" points="{pts}"/>')
            s.append(f'<text x="{ml + 8 + ti * 150}" y="{y0 + 13}" fill="{col}">{lab}</text>')
    s.append(f'<text x="{ml + pw / 2}" y="{H - 4}" text-anchor="middle">zaman ({tunit})</text></svg>')
    Path(path).write_text("\n".join(s), encoding="utf-8")
