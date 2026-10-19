"""Repeatable routing-envelope arithmetic; no KiCad source access.

Inputs: Konnect-derived explicit plan JSON. Output: JSON calculation evidence.
The IPC-2221 external-layer empirical fit is a preliminary screening estimate,
not an IPC-2152 thermal simulation, fault proof, or fabrication certificate.
"""
import json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'.konnect/diagnostics/netclass-plan.json').read_text(encoding='utf-8'))
t_mm=plan['calculation_copper_um']/1000
dt=plan['trace_deltaT_C']
temp=plan['resistivity_temperature_C']
rho=1.724e-8*(1+.00393*(temp-20))
rows=[]
for cls in plan['classes']:
    if 'current_A' not in cls:continue
    i=cls['current_A'];w=cls['trace_width'];length=cls['length_mm']/1000
    area_mil2=(i/(.048*dt**.44))**(1/.725)
    thermal_width_mm=area_mil2/(t_mm/.0254)*.0254
    drop_width_mm=rho*length*i/(t_mm/1000*(plan['drop_budget_mV_per_trunk']/1000))*1000
    area_actual=(w/.0254)*(t_mm/.0254)
    screening_rise=(i/(.048*area_actual**.725))**(1/.44)
    r=rho*length/(w/1000*t_mm/1000)
    row=dict(name=cls['name'],current_A=i,length_mm=cls['length_mm'],selected_width_mm=w,thermal_width_mm=thermal_width_mm,drop_width_mm=drop_width_mm,calculated_rise_C=screening_rise,resistance_mohm=r*1000,voltage_drop_mV=i*r*1000,loss_W=i*i*r)
    assert w>=thermal_width_mm and w>=drop_width_mm,row
    assert screening_rise<=dt and i*r*1000<=plan['drop_budget_mV_per_trunk'],row
    rows.append(row)
result=dict(plan=plan,method='IPC-2221 external empirical fit k=.048,b=.44,c=.725; Ohmic drop with Cu rho20=1.724e-8 ohm*m and alpha=.00393/K',scope='Uniform exterior copper, no plane credit,31.5um lower-bound design assumption. No IC thermal/EMI/fault or neck/via current guarantee.',sources=['https://www.ti.com/lit/an/snva766/snva766.pdf','https://jlcpcb.com/capabilities/pcb-capabilities/','https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html'],rows=rows)
(ROOT/'hardware/routing-width-calculations.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for r in rows:print(f"{r['name']}: {r['selected_width_mm']:.2f}mm, {r['current_A']:.2f}A envelope, rise{r['calculated_rise_C']:.2f}C estimate, drop{r['voltage_drop_mV']:.2f}mV over{r['length_mm']}mm")
