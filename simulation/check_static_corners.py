"""Reproducible datasheet corner screens from Konnect's exported netlist.

No KiCad sources are read. These bounded static calculations do not replace
switching-loop, SOA, surge, measurement or component-aging qualification.
"""
from itertools import product
from pathlib import Path
import json
from project_inputs import load_inputs, number, tolerance, tcr_ppm

HERE = Path(__file__).resolve().parent
c, bom, provenance = load_inputs()
cout_selected = all(bom[f'COUT{i}']['MPN']=='C5750X7S2A226M280KB' and
                    bom[f'COUT{i}']['Voltage']=='100V' for i in range(1,9))
v = lambda ref: number(c[ref]['value'])
fb = {}
for label, delta_t in [('25C',0), ('minus40_to125C',100)]:
    error1 = tolerance(bom['RFB1'])+tcr_ppm(bom['RFB1'])*1e-6*delta_t
    error2 = tolerance(bom['RFB2'])+tcr_ppm(bom['RFB2'])*1e-6*delta_t
    # Independent adverse drift; no matched tracking specification assumed.
    points = [vf*(1+v('RFB1')*(1+e1)/(v('RFB2')*(1+e2))) +
              ib*v('RFB1')*(1+e1)
              for vf,e1,e2,ib in product((.794,.806),(-error1,error1),(-error2,error2),(-75e-9,75e-9))]
    fb[label] = dict(min_V=min(points), max_V=max(points), resistor_errors=[error1,error2])

imon = {}
for i in (1,2):
    r = v(f'RIMON{i}')
    rmax = r*(1+tolerance(bom[f'RIMON{i}'])+65*tcr_ppm(bom[f'RIMON{i}'])*1e-6)
    ilim = 1460/v(f'RILIM{i}')+.11
    imax = 15*253.4e-6
    imon[f'channel{i}'] = dict(resistor_ohm=r, nominal_V_per_A=246e-6*r,
        nominal_trip_A=ilim, nominal_V_at_trip=ilim*246e-6*r,
        screen15A_max_V=imax*rmax, screen_resistor_max_W=imax**2*rmax,
        screen_pass=imax*rmax<3.3,
        accuracy_domain='3A..min(15A, actual ILIM); -40..75C only; no accuracy claim below3A or >75C; not a transient current bound')

rt, rb = v('RUV1'), v('RUV2')
et, eb = tolerance(bom['RUV1'],.01),tolerance(bom['RUV2'],.01)
uv = [threshold*(1+rt*(1+et)/(rb*(1+eb)))
      for threshold,et,eb in product((.95,1.05),(-et,et),(-eb,eb))]
uvlo = dict(resistor_tolerances=[et,eb], missing_tolerance_assumption=.01,
            min_start_V=min(uv), max_start_V=max(uv),
            worst_case_20V_restart_pass=max(uv)<=20,
            extra_battery_threshold_shift_per_1uA_per_EN_V=2*rt*1e-6,
            limitation='EN leakage guaranteed maximum not found; above results exclude it. Shared two inputs. Do not certify20V restart.')
corners = dict(scope=__doc__, **provenance,
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
gates = dict(feedback_static2pct=all(p['min_V']>=10.78 and p['max_V']<=11.22 for p in fb.values()),
             imon_headroom=all(p['screen_pass'] for p in imon.values()),
             uvlo20V_restart=uvlo['worst_case_20V_restart_pass'],
             selected_COUT_rating=corners['raw_COUT']['direct26V_fault_rating_pass'])
corners.update(gates=gates,all_static_screens_pass=all(gates.values()),
               physical_electrical_acceptance=False)
(HERE/'static-corner-results.json').write_text(json.dumps(corners,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(feedback=fb,imon=imon,buck_uvlo=uvlo),indent=2))
# Known electrical blockers remain hard failures, separately from engine execution.
raise SystemExit(0 if all(gates.values()) else 1)
