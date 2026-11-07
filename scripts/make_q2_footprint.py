"""R-009 fix: CSD19531Q5A footprint from the TI recommended PCB pattern (SLPS406B §7.2 p.10), pads numbered for the
stock KiCad CSD19531Q5A symbol (1-3 S, 4 G, 5 D incl. exposed pad + drain fingers).

    python scripts/make_q2_footprint.py   # writes hardware/lib/PDU.pretty/TI_CSD19531Q5A_Q5A.kicad_mod

Nominal = midpoint of each TI min/max (mm): F1 6.255 (overall width), F10 4.95 (drain pad incl. fingers), F6 0.655
(finger depth), F7 0.75 (S/G land width), F4/F8 0.675 and F5/F9 0.645 (land/finger heights), F2/F3/F11 4.51.
Land height used: 0.66 (centre of the F4/F5 bands); pitch 1.27. Orientation as KiCad TDSON/VSONP: pin 1 top-left.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware" / "lib" / "PDU.pretty" / "TI_CSD19531Q5A_Q5A.kicad_mod"

F1, F10, F6, F7, H, HB = 6.255, 4.95, 0.655, 0.75, 0.66, 4.51
XL, XR = -F1 / 2, F1 / 2
X_SG = XL + F7 / 2                          # S/G land centre
GAP = F1 - F10 - F7
BODY_L = XL + F7 + GAP
BODY_R = XR - F6
YS = (-1.905, -0.635, 0.635, 1.905)
OVERLAP = 0.10                               # finger overlaps the drain body for one continuous copper area


def pads():
    out = []
    for n, y in zip(("1", "2", "3", "4"), YS):
        out.append((n, X_SG, y, F7, H, "F.Cu F.Paste F.Mask"))
    out.append(("5", (BODY_L + BODY_R) / 2, 0.0, BODY_R - BODY_L, HB, "F.Cu F.Mask"))
    fw = F6 + OVERLAP
    for y in YS:
        out.append(("5", BODY_R - OVERLAP + fw / 2, y, fw, H, "F.Cu F.Paste F.Mask"))
    return out


def text() -> str:
    L = ['(footprint "TI_CSD19531Q5A_Q5A"', '\t(version 20241229)', '\t(generator "pdu_make_q2_footprint")',
         '\t(layer "F.Cu")',
         '\t(descr "TI CSD19531Q5A SON 5x6 (Q5A), recommended PCB pattern SLPS406B 7.2 p.10 (nominal of min/max); '
         'pads 1-3 S, 4 G, 5 D (exposed pad + fingers) for the stock KiCad CSD19531Q5A symbol. G5 R-009.")',
         '\t(tags "CSD19531Q5A SON 5x6 Q5A")', '\t(attr smd)',
         '\t(property "Reference" "REF**" (at 0 -3.6 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
         '\t(property "Value" "TI_CSD19531Q5A_Q5A" (at 0 3.6 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
         '\t(fp_rect (start -3 -2.5) (end 3 2.5) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
         '\t(fp_rect (start -3.45 -2.75) (end 3.45 2.75) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
         '\t(fp_line (start -3.11 -2.61) (end 3.11 -2.61) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
         '\t(fp_line (start -3.11 2.61) (end 3.11 2.61) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
         '\t(fp_circle (center -3.5 -2.3) (end -3.35 -2.3) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS"))']
    for n, x, y, w, h, lay in pads():
        layers = " ".join(f'"{l}"' for l in lay.split())
        L.append(f'\t(pad "{n}" smd rect (at {x:.4f} {y:.4f}) (size {w:.4f} {h:.4f}) (layers {layers}))')
    # drain body paste: 4 windows ~ 60 % coverage (TI recommends a segmented stencil for large thermal pads)
    bx0, bx1 = BODY_L, BODY_R
    wx, wy = (bx1 - bx0) / 2 - 0.25, HB / 2 - 0.35
    for cx in (bx0 + (bx1 - bx0) / 4, bx0 + 3 * (bx1 - bx0) / 4):
        for cy in (-HB / 4, HB / 4):
            L.append(f'\t(pad "" smd rect (at {cx:.4f} {cy:.4f}) (size {wx:.4f} {wy:.4f}) (layers "F.Paste"))')
    L.append(')')
    return "\n".join(L) + "\n"


def main() -> int:
    OUT.write_text(text(), encoding="utf-8", newline="\n")
    print(OUT.relative_to(ROOT), "GAP", round(GAP, 4), "BODY", round(BODY_L, 4), round(BODY_R, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
