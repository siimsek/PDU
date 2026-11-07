"""Validate an exported CSV against Konnect's exported netlist, then publish it.

KiCad CSV export appends '?' to seven non-numeric reference names on this
project. Only an exact, unique netlist identity/value/footprint match permits
removing that trailing character. Never reads or writes KiCad sources.
"""
from pathlib import Path
import csv
import json
from build_models import exported

ROOT = Path(__file__).resolve().parent.parent
net = exported(ROOT/'simulation/pdu-current.net')
raw = ROOT/'hardware/pdu-current-bom.raw.csv'
rows = list(csv.DictReader(raw.open(encoding='utf-8',newline='')))
columns = list(rows[0])
mapping = []
seen = set()
for row in rows:
    original = row['Reference']
    ref = original if original in net else original.removesuffix('?')
    if ref not in net or ref in seen:
        raise SystemExit(f'Unresolved/duplicate reference: {original}')
    if row['Value'] != net[ref]['value'] or row['Footprint'] != net[ref]['footprint']:
        raise SystemExit(f'Value/footprint mismatch: {original}')
    seen.add(ref)
    if original != ref:
        mapping.append(dict(raw=original,canonical=ref))
        row['Reference'] = ref
if seen != net.keys():
    raise SystemExit(f'BOM coverage mismatch: missing{net.keys()-seen}')
with (ROOT/'hardware/pdu-current-bom.csv').open('w',encoding='utf-8',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
evidence = dict(raw_export=str(raw),reference_count=len(seen),
                normalized_references=mapping,
                missing_MPN=[r['Reference'] for r in rows if not r.get('MPN','')],
                all_reference_value_footprint_rows_match_netlist=True)
(ROOT/'.konnect/diagnostics/canonical-bom-evidence.json').write_text(json.dumps(evidence,indent=2))
print(f'Validated{len(seen)} BOMrows; corrected{len(mapping)} exported aliases; '
      f'{len(evidence["missing_MPN"])} MPN fields remain empty.')
