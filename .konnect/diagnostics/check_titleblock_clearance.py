"""Read exported SVG stroke paths, never KiCad sources."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[2]
svg = ET.parse(root / 'hardware/schematic-finish/PDU.svg').getroot()
ns = {'s': 'http://www.w3.org/2000/svg'}
frame = {'x_min': 474.0044, 'x_max': 582.0044, 'y_min': 375.9890, 'y_max': 407.9890}
report = {'titleblock_mm': frame, 'stroke_inflation_mm': 0.15, 'text_bounds': {}}
for name in ['D1', 'SMCJ33A', 'Q1', 'BSC160N10NS3G', 'U5', 'LM74700']:
    pts = []
    for group in svg.findall('.//s:g', ns):
        desc = group.find('s:desc', ns)
        if group.attrib.get('class') != 'stroked-text' or desc is None or desc.text != name:
            continue
        for path in group.findall('s:path', ns):
            nums = list(map(float, re.findall(r'-?\d+(?:\.\d+)?', path.attrib.get('d', ''))))
            pts.extend(zip(nums[::2], nums[1::2]))
    assert pts, name
    b = {'x_min': min(p[0] for p in pts) - .15, 'x_max': max(p[0] for p in pts) + .15,
         'y_min': min(p[1] for p in pts) - .15, 'y_max': max(p[1] for p in pts) + .15}
    b['titleblock_intersection'] = b['x_max'] >= frame['x_min'] and b['y_max'] >= frame['y_min']
    b['left_clearance_mm'] = frame['x_min'] - b['x_max']
    b['inside_A2_drawing_border'] = b['x_min'] > 12 and b['x_max'] < 582.0044 and b['y_min'] > 12 and b['y_max'] < 407.989
    report['text_bounds'][name] = b
    assert not b['titleblock_intersection'], name
    assert b['inside_A2_drawing_border'], name
report['D1_body_pin_bounds_mm'] = [468.63, 377.19, 471.17, 384.81]
report['GND_wire_rightmost_mm'] = 469.9
report['GND_wire_titleblock_clearance_mm'] = frame['x_min'] - 469.9
(root / '.konnect/diagnostics/schematic-titleblock-clearance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
