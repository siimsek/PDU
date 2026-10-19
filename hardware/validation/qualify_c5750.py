"""Read vendor model/data, create isolated capacitor AC bench; no KiCad IO."""
from pathlib import Path
import json
import math
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/validation/c5750'
OUT.mkdir(exist_ok=True)
z = zipfile.ZipFile(ROOT / 'hardware/_datasheets/tdk-c5750-bias-ltspice.zip')
for name in ['C5750X7S2A226M280KB_b_LTspice.mod', 'readme_ltspice_en.txt']:
    (OUT / name).write_bytes(z.read(name))

bench = '''* Isolated manufacturer capacitor model; not converter stability proof
.include "C5750X7S2A226M280KB_b_LTspice.mod"
Vtest cap 0 DC {VB} AC 1
Xcap cap 0 C5750X7S2A226M280KB_b
.step param VB list 0 11
.temp 25
.ac list 1k 400k 440k 1Meg
.meas AC imag_1k FIND im(I(Vtest)) AT=1k
.meas AC esr_400k FIND re(-1/I(Vtest)) AT=400k
.meas AC esr_440k FIND re(-1/I(Vtest)) AT=440k
.meas AC esr_1meg FIND re(-1/I(Vtest)) AT=1Meg
.end
'''
(OUT / 'vendor-bias-ac.cir').write_text(bench, encoding='ascii')

# Read only public chart geometry; never decode the encrypted SPICE model.
page = pymupdf.open(ROOT / 'hardware/_datasheets/tdk-c5750-charasheet.pdf')[0]
drawings = page.get_drawings()
markers = []
for index in range(25, 45, 2):
    box = drawings[index]['rect'] * page.rotation_matrix
    px, py = (box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2
    # Grid: x=0..120 V at570.951..780.231, y=+10..-90% at79.32..189.72.
    volts = (px - 570.95099) * 120 / (780.23096 - 570.95099)
    delta = 10 - (py - 79.319984) * 100 / (189.720001 - 79.319984)
    markers.append({'pdf_drawing_index': index, 'voltage_V': volts, 'delta_pct': delta})
with (OUT / 'public-dc-bias-digitized.csv').open('w', encoding='utf8') as fh:
    fh.write('voltage_V,delta_pct,pdf_drawing_index\n')
    for row in markers:
        fh.write(f"{row['voltage_V']:.6f},{row['delta_pct']:.6f},{row['pdf_drawing_index']}\n")
v = 11.0
left, right = next((a, b) for a, b in zip(markers, markers[1:])
                   if a['voltage_V'] <= v <= b['voltage_V'])
delta = left['delta_pct'] + (right['delta_pct'] - left['delta_pct']) * (
    v - left['voltage_V']) / (right['voltage_V'] - left['voltage_V'])
factor = 1 + delta / 100
result = {'method': 'linear interpolation of public PDF red marker centers; not guaranteed data',
          'chart_interpolation_error_assumption_pct_points': 0.5,
          'dc_bias_V': 11, 'delta_pct': delta, 'C_each_typ_uF': 22 * factor,
          'C_bank_typ_uF': 176 * factor,
          'C_bank_minus20pct_tolerance_minus22pct_temperature_uF': 176 * factor * .8 * .78,
          'C_bank_same_plus10pct_aging_assumption_uF': 176 * factor * .8 * .78 * .9,
          'C_bank_plus20pct_tolerance_plus22pct_temperature_uF': 176 * factor * 1.2 * 1.22,
          'aging_note': '10% is an engineering sensitivity assumption, not a guaranteed manufacturer aging spec'}
(OUT / 'public-curve-summary.json').write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps(result, indent=2))
