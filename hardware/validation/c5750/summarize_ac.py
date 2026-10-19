"""Summarize isolated vendor model AC measurements, no model decryption."""
from pathlib import Path
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
text = (HERE / 'vendor-bias-ac.log').read_text(encoding='utf8')
tables = {}
for name, body in re.findall(r'Measurement: (\w+)\s*(.*?)(?=Measurement:|\Z)', text, re.S):
    tables[name] = {int(i): 10 ** (float(db) / 20) * math.cos(math.radians(float(ph)))
                    for i, db, ph in re.findall(r'^\s*(\d+)\s*\(([-\d.]+)dB,([-\d.]+)°\)', body, re.M)}
cap0 = -tables['imag_1k'][1] / (2 * math.pi * 1000)
cap11 = -tables['imag_1k'][2] / (2 * math.pi * 1000)
results = {'source': 'TDK encrypted DC-bias LTspice model used unchanged',
           'simulator': 'LTspice 26.1.1', 'temperature_C': 25,
           'measurement_frequency_Hz': 1000,
           'C_0V_typ_uF': cap0 * 1e6, 'C_11V_typ_uF': cap11 * 1e6,
           'C_11V_bank8_typ_uF': cap11 * 8e6,
           'ratio_11V_to_0V': cap11 / cap0,
           'ESR_11V_400kHz_ohm': tables['esr_400k'][2],
           'ESR_11V_440kHz_ohm': tables['esr_440k'][2],
           'ESR_11V_1MHz_ohm': tables['esr_1meg'][2],
           'bank8_minus20pct_tolerance_minus22pct_temperature_uF': cap11 * 8e6 * .8 * .78,
           'bank8_same_minus10pct_assumed_aging_uF': cap11 * 8e6 * .8 * .78 * .9,
           'bank8_plus20pct_tolerance_plus22pct_temperature_uF': cap11 * 8e6 * 1.2 * 1.22,
           'limits': ['typical passive component model only',
                      'multiplicative temperature/bias/aging combination is an engineering sensitivity, not guaranteed joint statistics',
                      '10% aging is assumed, not a published guaranteed aging limit',
                      'does not validate converter control-loop stability']}
(HERE / 'vendor-ac-summary.json').write_text(json.dumps(results, indent=2), encoding='utf8')
provenance = []
for path in sorted((ROOT / 'hardware/_datasheets').glob('tdk-c5750*')):
    provenance.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
path = ROOT / 'hardware/_datasheets/tdk-mlcc-delivery-spec.pdf'
provenance.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
(HERE / 'vendor-file-hashes.json').write_text(json.dumps(provenance, indent=2), encoding='utf8')
print(json.dumps(results, indent=2))
