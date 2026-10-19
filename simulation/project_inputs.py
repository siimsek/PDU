"""Load matching exported netlist/BOM data; never access KiCad sources."""
from pathlib import Path
import csv
import hashlib
import re
from build_models import exported, number

ROOT = Path(__file__).resolve().parent.parent


def load_inputs(root=ROOT):
    root = Path(root)
    net = root/'simulation/pdu-current.net'
    bom_path = root/'hardware/pdu-current-bom.csv'
    components = exported(net)
    rows = list(csv.DictReader(bom_path.open(encoding='utf-8-sig',newline='')))
    bom = {row['Reference']:row for row in rows}
    if len(bom)!=len(rows) or bom.keys()!=components.keys():
        raise ValueError('BOM references must be unique and match the exported netlist')
    for ref, component in components.items():
        row = bom[ref]
        if row['Value']!=component['value'] or row['Footprint']!=component['footprint']:
            raise ValueError(f'BOM/netlist value or footprint mismatch: {ref}')
    return components, bom, dict(
        export_sha256=hashlib.sha256(net.read_bytes()).hexdigest(),
        bom_sha256=hashlib.sha256(bom_path.read_bytes()).hexdigest(),
        component_count=len(components),
        pin_count=sum(len(c['pins']) for c in components.values()))


def tolerance(row, assumed=None):
    """Return fractional stated tolerance, or an explicitly supplied assumption."""
    text = row.get('Tolerance','').strip()
    if text.endswith('%'):
        result = float(text[:-1])/100
        if not 0<=result<1:
            raise ValueError(f'Invalid tolerance: {row["Reference"]}')
        return result
    if assumed is None:
        raise ValueError(f'Missing numeric tolerance: {row["Reference"]}')
    return assumed


def tcr_ppm(row):
    match = re.search(r'(\d+(?:\.\d+)?)\s*ppm',row.get('TCR',''),re.I)
    if not match:
        raise ValueError(f'Missing numeric TCR: {row["Reference"]}')
    return float(match[1])
