#!/usr/bin/env python3
"""First-order screens using the current Konnect-exported netlist and BOM.

No KiCad source access. Controller constants/operating envelopes below remain
explicit engineering inputs. Arithmetic is not silicon, loop, SOA or bench proof.
"""
from itertools import product
from math import pi
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'simulation'))
from project_inputs import load_inputs, number, tolerance


def calculate():
    components, bom, provenance = load_inputs()
    val = lambda ref: number(components[ref]['value'])
    for a,b in [('L1','L2'),('RS1','RS2'),('RT1','RT2')]:
        if val(a)!=val(b):
            raise ValueError(f'Equal-phase assumption does not hold: {a}/{b}')
    target, reference, capacity, phases = 11.0,.8,7.5,2
    setpoint = reference*(1+val('RFB1')/val('RFB2'))
    l_nom, rs, rcomp = val('L1'),val('RS1'),val('RCOMP')
    ceff_legacy = 88e-6  # Retained calculation basis, not current measured Ceff.
    vendor_path = ROOT/'hardware/validation/c5750/vendor-ac-summary.json'
    vendor = json.loads(vendor_path.read_text(encoding='utf-8'))
    if not all(bom[f'COUT{i}']['MPN']=='C5750X7S2A226M280KB' and
               bom[f'COUT{i}']['Voltage']=='100V' and
               val(f'COUT{i}')==22e-6 for i in range(1,9)):
        raise ValueError('Saved TDK characterization does not match current COUT selection')
    ceff_vendor = vendor['C_11V_bank8_typ_uF']*1e-6
    ceff_high = sum(val(f'COUT{i}') for i in range(1,9))*1.2*1.22
    corners = []
    for vin in (20.0,22.2,25.2,26.0):
        duty = target/vin
        ripple = target*(1-duty)/(l_nom*400e3)
        corners.append(dict(input_V=vin,duty=duty,
            assumed_input_A={str(e):target*capacity/(vin*e) for e in (.8,.9,.95)},
            phase_average_A=capacity/phases,ripple_400kHz_pp_A=ripple,
            steady_peak_A=capacity/phases+ripple/2,
            steady_peak_minus20pct_L_A=capacity/phases+ripple/(2*.8)))
    comp = []
    for name,ceff in [('retained_88uF_basis',ceff_legacy),('vendor_typical_11V',ceff_vendor),
                       ('nominal_tolerance_temperature_upper',ceff_high)]:
        comp.append(dict(case=name,ceff_uF=ceff*1e6,
            equation_RCOMP_for_assumed40kHz_ohm=2*pi*40e3*(target/reference)*(rs/phases*10/1200e-6)*ceff,
            load_pole_at7p5A_Hz=1/(2*pi*(target/capacity)*ceff)))
    rt,rb = val('RUV1'),val('RUV2')
    et,eb = tolerance(bom['RUV1'],.01),tolerance(bom['RUV2'],.01)
    uv = [th*(1+rt*(1+a)/(rb*(1+b)))
          for th,a,b in product((.95,1.05),(-et,et),(-eb,eb))]
    ports = {}
    for i,name in [(1,'O1'),(2,'S2E')]:
        monitor,rlim = val(f'RIMON{i}'),val(f'RILIM{i}')
        ilim = 1460/rlim+.11
        ports[name] = dict(rlim_ohm=rlim,nominal_trip_A=ilim,
            rimon_ohm=monitor,nominal_monitor_V_per_A=246e-6*monitor,
            nominal_monitor_at_trip_V=246e-6*ilim*monitor,
            monitor_gain_max_screen_at_nominal_trip_V=253.4e-6*ilim*monitor,
            gain_spec_lower_current_bound_met=ilim>=3,
            cdvdt_nF=val(f'CDVDT{i}')*1e9,
            typical_slew_V_per_ms=4.6e-6/val(f'CDVDT{i}')/1000,
            limitations='Trip is nominal, not load or hard ceiling; monitor gain accuracy only3A..min(15A,ILIM),-40..75C; not guaranteed below3A or above75C')
    return dict(scope=__doc__,inputs=provenance,
        design=dict(target_V=target,setpoint_nominal_V=setpoint,requirement_A=7,
                    requirement_W=77,capacity_envelope_A=capacity,capacity_envelope_W=82.5,
                    measured_O1_S2E_loads=False),
        assumptions=dict(inductance_tolerance=.2,minimum_frequency_Hz=400e3,
            frequency_table_anchor_Hz=[400e3,440e3,480e3],shunt_tolerance=tolerance(bom['RS1'],.01),
            efficiency_values=[.8,.9,.95],current_sense_thresholds_mV=[50,62],
            limits='Unspecified tolerances, frequency/load/current-sharing/thermal/fault assumptions require qualification'),
        switching_frequency_equation_Hz=1e9/(val('RT1')/1000*45+53),
        steady_state=corners,
        current_sense_thresholds_A=dict(
            minimum=50e-3/(rs*(1+tolerance(bom['RS1'],.01))),
            maximum=62e-3/(rs*(1-tolerance(bom['RS1'],.01))),
            limitation='Sense thresholds only; not cycle peak, delay, saturation or fault-current bounds'),
        output_bank=dict(mpn=bom['COUT1']['MPN'],rated_V=100,nominal_uF=176,
            vendor_typical_11V_25C_uF=ceff_vendor*1e6,
            vendor_summary_sha256=hashlib.sha256(vendor_path.read_bytes()).hexdigest(),
            capacitance_screens=comp,
            limitation='Typical vendor characterization and broad sensitivity assumptions; no guaranteed jointCeff or converter stability'),
        compensation=dict(installed_RCOMP_ohm=rcomp,installed_CCOMP_nF=val('CCOMP')*1e9,
            installed_CHF_pF=val('CHF')*1e12,
            zero_Hz=1/(2*pi*rcomp*val('CCOMP')),hf_pole_Hz=1/(2*pi*rcomp*val('CHF')),
            accepted_physical_phase_margin=False,
            limitation='40kHz crossover and gm/GCS are earlier equation inputs; computed alternativeRCOMP values are NOT applied or qualified'),
        buck_uvlo=dict(typical_on_V=1+rt/rb,typical_off_V=.9*(1+rt/rb),
            threshold_and_resistor_corner_start_V=[min(uv),max(uv)],
            resistor_tolerances=[et,eb],resistor_threshold20V_screen_pass=max(uv)<=20,
            guaranteed20V_restart=False,
            limitation='Includes assumed1% resistors; excludes unspecified EN leakage and TCR. Falling threshold is typical only'),
        efuse_enable=dict(typical_rail_on_V=1.2*(1+val('REN1')/val('REN2')),
            nominal_pin_at11V_V=target/(1+val('REN1')/val('REN2'))),
        pg_nominal_at11V_V=target*val('RPG1B')/(val('RPG1')+val('RPG1B')),
        bootstrap_series_ohm=[val('RBOOT1'),val('RBOOT2')],
        lm74700_input_bypass_nF=val('CIN_U5')*1e9,ports=ports,
        loss_screens=dict(q1_assumed16mohm_at20V90pct_W=(target*capacity/(20*.9))**2*.016,
            inductor_assumed23p3mohm_per_phase_W=(capacity/phases)**2*.0233,
            limitation='Illustrative resistive loss; no switching loss, hot resistance, thermal or SOA proof'),
        electrical_acceptance=False,
        open_items=['O1OVP12V','actual loop stability','UVLO policy','F1coordination',
                    'remainingMPNs','PCB routing','physical qualification'])


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Optional ordinary JSON report path')
    args = parser.parse_args()
    result = calculate()
    text = json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.write_text(text,encoding='utf-8',newline='\n')
    print(text,end='')
