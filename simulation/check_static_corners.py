"""Reproducible datasheet corner screens from Konnect's exported netlist.

No KiCad sources are read. These bounded static calculations do not replace
switching-loop, SOA, surge, measurement or component-aging qualification.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import csv
from build_models import exported, number

HERE = Path(__file__).resolve().parent
source = HERE/'pdu-current.net'
c = exported(source)
bom = {r['Reference']:r for r in csv.DictReader(
    (HERE.parent/'hardware/pdu-current-bom.csv').open(encoding='utf-8',newline=''))}
cout_selected = all(bom[f'COUT{i}']['MPN']=='C5750X7S2A226M280KB' and
                    bom[f'COUT{i}']['Voltage']=='100V' for i in range(1,9))
v = lambda ref: number(c[ref]['value'])
fb = {}
for label, delta_t in [('25C',0), ('minus40_to125C',100)]:
    error = .001 + 25e-6*delta_t
    # Independent adverse drift; no matched tracking specification assumed.
    points = [vf*(1+v('RFB1')*(1+e1)/(v('RFB2')*(1+e2))) +
              ib*v('RFB1')*(1+e1)
              for vf,e1,e2,ib in product((.794,.806),(-error,error),(-error,error),(-75e-9,75e-9))]
    fb[label] = dict(min_V=min(points), max_V=max(points), resistor_error=error)

imon = {}
for i in (1,2):
    r = v(f'RIMON{i}')
    rmax = r*(1+.001+65*25e-6)
    ilim = 1460/v(f'RILIM{i}')+.11
    imax = 15*253.4e-6
    imon[f'channel{i}'] = dict(resistor_ohm=r, nominal_V_per_A=246e-6*r,
        nominal_trip_A=ilim, nominal_V_at_trip=ilim*246e-6*r,
        screen15A_max_V=imax*rmax, screen_resistor_max_W=imax**2*rmax,
        screen_pass=imax*rmax<3.3,
        accuracy_domain='3A..min(15A, actual ILIM); -40..75C only; no accuracy claim below3A or >75C; not a transient current bound')

rt, rb = v('RUV1'), v('RUV2')
uv = [threshold*(1+rt*(1+et)/(rb*(1+eb)))
      for threshold,et,eb in product((.95,1.05),(-.01,.01),(-.01,.01))]
uvlo = dict(resistor_tolerance_assumption=.01, min_start_V=min(uv), max_start_V=max(uv),
            worst_case_20V_restart_pass=max(uv)<=20,
            extra_battery_threshold_shift_per_1uA_per_EN_V=2*rt*1e-6,
            limitation='EN leakage guaranteed maximum not found; above results exclude it. Shared two inputs. Do not certify20V restart.')
corners = dict(scope=__doc__, export_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               feedback=fb, imon=imon, buck_uvlo=uvlo,
               raw_COUT=dict(current_selected_V=100 if cout_selected else None,
                             stated_battery_fault_V=26, assumed_TVS_clamp_V=53.3,
                             exact_parts_and_voltage_fields_verified=cout_selected,
                             direct26V_fault_rating_pass=cout_selected,
                             limitation='100V above assumed53.3V envelope; no guarantee of real fault overshoot, energy or loop stability'),
               sources=[
                   'https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf',
                   'https://www.ti.com/lit/ds/symlink/tps25982.pdf',
                   'https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB134V',
                   'https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB1022V',
                   'https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA3AEB8060V'])
(HERE/'static-corner-results.json').write_text(json.dumps(corners,indent=2))
print(json.dumps(dict(feedback=fb,imon=imon,buck_uvlo=uvlo),indent=2))
# Known electrical blockers remain hard failures, separately from engine execution.
raise SystemExit(0 if uvlo['worst_case_20V_restart_pass'] and corners['raw_COUT']['direct26V_fault_rating_pass'] else 1)
