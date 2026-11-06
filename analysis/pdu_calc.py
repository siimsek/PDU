"""G1 reproducible PDU calculations. SI units internally; no KiCad reads.

Reported checks carry two numerical paths and a declaration of their
validation scope. Most paths are same-equation arithmetic cross-checks, not
independent physical models. Unavailable silicon/parasitic data remain open.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "g1"
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"simulation"))
from project_inputs import load_inputs, number, tolerance

def dual(name: str, unit: str, first: float, second: float,
         method1: str, method2: str, tag: str = "HESAP",
         validation_scope: str = "same_equation_arithmetic_crosscheck") -> dict:
    diff = abs(first-second)
    return {"name": name, "unit": unit, "value": first, "second_value": second,
            "method_1": method1, "method_2": method2,
            "validation_scope": validation_scope,
            "absolute_difference": diff,
            "relative_difference_percent": 0.0 if first == second else 100*diff/max(abs(first), abs(second)),
            "tag": tag}

def feedback_corner(vfb_lo=.794, vfb_hi=.806, rtop=130e3, rbot=10.2e3,
                    rtol=.001, tcr=25e-6, tmin=-40, tmax=125, ibias=75e-9):
    dt=max(abs(tmin-25),abs(tmax-25))
    e=rtol+tcr*dt
    values=[vf*(1+rtop*(1+a)/(rbot*(1+b)))+ib*rtop*(1+a)
            for vf,a,b,ib in product((vfb_lo,vfb_hi),(-e,e),(-e,e),(-ibias,ibias))]
    # Independent monotonic closed-form corner evaluation (all variables are
    # monotonic on the stated positive ranges).
    low=vfb_lo*(1+rtop*(1-e)/(rbot*(1+e)))-ibias*rtop*(1-e)
    high=vfb_hi*(1+rtop*(1+e)/(rbot*(1-e)))+ibias*rtop*(1+e)
    return {"min_V":min(values),"max_V":max(values),"second_min_V":low,
            "second_max_V":high,"resistor_fractional_error":e}

def uvlo_corner(rtop, rbot, rtol=.01, vth_lo=.95, vth_hi=1.05):
    pts=[vth*(1+rtop*(1+a)/(rbot*(1+b)))
         for vth,a,b in product((vth_lo,vth_hi),(-rtol,rtol),(-rtol,rtol))]
    # Closed-form extrema from monotonic divider ratio.
    lo=vth_lo*(1+rtop*(1-rtol)/(rbot*(1+rtol)))
    hi=vth_hi*(1+rtop*(1+rtol)/(rbot*(1-rtol)))
    return {"min_V":min(pts),"max_V":max(pts),"second_min_V":lo,"second_max_V":hi}

def build_results() -> dict:
    components,bom,provenance=load_inputs(ROOT)
    val=lambda ref:number(components[ref]["value"])
    vin, vout, phases = 26.0, 11.0, 2
    fs_min, l_nom, l_tol = 400e3, val("L1"), .20
    rs, rs_tol = val("RS1"), tolerance(bom["RS1"],.01)  # tolerance absent from BOM: explicit screening assumption
    dcr25, dcr_tcr = 23.3e-3, 3930e-6
    i_total, share_error = 7.5, .10  # ±10% phase-current deviation: not specified by IC
    duty=vout/vin
    ripple_a=vout*(1-duty)/(l_nom*(1-l_tol)*fs_min)
    ripple_b=(vin-vout)*duty/(l_nom*(1-l_tol)*fs_min)
    phase_mean=i_total/phases
    phase_worst=phase_mean*(1+share_error)
    peak=phase_worst+ripple_a/2
    ripple_peak=dual("inductor ripple at 26 V, minimum L and frequency", "A p-p", ripple_a, ripple_b,
                     "Vout*(1-Vout/Vin)/(Lmin*fmin)","(Vin-Vout)*D/(Lmin*fmin)")
    peak_second=(i_total*(1+share_error)/phases)+(ripple_b/2)
    peak_result=dual("phase peak current at 7.5 A total, +10% share", "A", peak, peak_second,
                     "Iphase_avg + deltaIL/2", "Iout*(1+share_error)/2 + deltaIL/2")
    dcr_hot=dcr25*(1+dcr_tcr*100) # 25 C to 125 C copper TCR sensitivity; coil max temp unknown
    i_rms=math.sqrt(phase_worst**2+ripple_a**2/12)
    dcr_loss_cold=i_rms*i_rms*dcr25
    dcr_loss_hot=i_rms*i_rms*dcr_hot
    shunt_cold=(phase_worst**2+ripple_a**2/12)*rs*(1+rs_tol)
    shunt_hot=(phase_worst**2+ripple_a**2/12)*rs*(1+rs_tol)*(1+100*100e-6) # unverified 100ppm/K sensitivity
    vendor=json.loads((ROOT/"hardware/validation/c5750/vendor-ac-summary.json").read_text(encoding="utf-8"))
    ctyp=vendor["C_11V_bank8_typ_uF"]*1e-6
    cmin=vendor["bank8_same_minus10pct_assumed_aging_uF"]*1e-6
    cmax=vendor["bank8_plus20pct_tolerance_plus22pct_temperature_uF"]*1e-6
    # Worst aligned, uncancelled two-phase ripple upper screen; ignores ESL.
    cap_ripple=2*ripple_a/(8*fs_min*cmin)
    cap_ripple_alt=(ripple_a/(4*fs_min*cmin))
    cap_res=dual("two-phase output ripple, aligned conservative capacitor-only", "V p-p", cap_ripple,
                 cap_ripple_alt,"(2*deltaIL)/(8*f*Cmin)","deltaIL/(4*f*Cmin)","VARSAYIM")
    rfb1,rfb2=val("RFB1"),val("RFB2")
    fb_tol=max(tolerance(bom["RFB1"]),tolerance(bom["RFB2"]))
    fb_tcr=25e-6 # ERA3AEB manufacturer maximum TCR in the documented selection
    vfb=feedback_corner(rtop=rfb1,rbot=rfb2,rtol=fb_tol,tcr=fb_tcr)
    vfb_nom=.8*(1+rfb1/rfb2)
    vfb_second=.8*(rfb1+rfb2)/rfb2
    fb_nom=dual("nominal feedback setpoint", "V", vfb_nom, vfb_second,
                "Vref*(1+Rtop/Rbottom)","Vref*(Rtop+Rbottom)/Rbottom")

    # Current-sense thresholds. Shunt tolerance is screened at ±1%; TCR is an
    # additional unverified ±100 ppm/K assumption over 100 K.
    rs_lo=rs*(1-rs_tol)*(1-100e-6*100)
    rs_hi=rs*(1+rs_tol)*(1+100e-6*100)
    i_sense_min=.050/rs_hi
    i_sense_max=.062/rs_lo
    sense_min=dual("cycle sense threshold lower-current corner", "A", i_sense_min,
                   .050/(rs*(1+rs_tol)*(1+.01)),"50mV/(Rmax incl. TCR)","50mV/(7.5mΩ*1.01*1.01)")
    sense_max=dual("cycle sense threshold upper-current corner", "A", i_sense_max,
                   .062/(rs*(1-rs_tol)*(1-.01)),"62mV/(Rmin incl. TCR)","62mV/(7.5mΩ*0.99*0.99)")

    rcomp=[]
    for label,ceff in (("low assumed Ceff",cmin),("vendor typical",ctyp),("high assumed Ceff",cmax)):
        # This is the inherited TI current-mode compensation equation with
        # assumed gm and 40 kHz target. It is not a measured loop solution.
        value=2*math.pi*40e3*(vout/.8)*(rs/phases*10/1.2e-3)*ceff
        alt=(40e3*2*math.pi*ceff)*(vout/.8)*(rs/(phases*1.2e-3))*10
        rcomp.append(dual(f"RCOMP for assumed 40 kHz target, {label}","ohm",value,alt,
                          "2π*fc*(Vout/Vref)*(Rs/N*10/gm)*Ceff",
                          "(fc*2π*Ceff)*(Vout/Vref)*(Rs/(N*gm))*10","VARSAYIM"))
    loop={"target_crossover_Hz":40000,"existing_RCOMP_ohm":val("RCOMP"),"existing_CCOMP_F":val("CCOMP"),
          "existing_CHF_F":val("CHF"),"estimated_RCOMP_range_ohm":[min(x["value"] for x in rcomp),max(x["value"] for x in rcomp)],
          "bench_adjustable_RCOMP_ohm":[6800,27000],"bench_adjustable_CCOMP_F":[2.2e-9,10e-9],
          "bench_adjustable_CHF_F":[22e-12,100e-12],"phase_margin_estimate_deg":None,
          "crossover_estimate_Hz":None,
          "reason":"The netlist behavioral current loop is not the LM70880 silicon transfer function; gm, sampled-data delay, plant parasitics, real Ceff/ESR distribution and measured loop gain are unavailable. 40 kHz is a design assumption only.",
          "rcomp_screens":rcomp,"tag":"VARSAYIM/AÇIK"}

    ruv1,ruv2=val("RUV1"),val("RUV2")
    uv_old=uvlo_corner(ruv1,ruv2)
    uv_new=uvlo_corner(174e3,ruv2)
    uv_ratio_limit=(20/1.05-1)*(.99/1.01)
    uv_top_limit=uv_ratio_limit*10e3
    uv_top_second=((20/1.05)-1)*10e3*.99/1.01
    uvlo={"existing_180k_10k":uv_old,"candidate_174k_10k":uv_new,
          "max_nominal_top_resistor_for_20V_worst_rising_ohm":uv_top_limit,
          "independent_limit_ohm":uv_top_second,
          "candidate_typical_rising_V":1.0*(1+174e3/ruv2),
          "candidate_typical_falling_V_assuming_0.9_ratio":.9*(1+174e3/ruv2),
          "candidate_rising_V_per_cell_6S_max":uv_new["max_V"]/6,
          "candidate_rising_V_per_cell_6S_typ":(1+174e3/ruv2)/6,
          "en_leak_shift_V_per_uA":174e3*1e-6,
          "leakage_max":"AÇIK: guaranteed LM70880 EN leakage bound not confirmed",
          "policy":"20 V restart is required to claim operation across the stated 20–26 V input envelope; battery disconnect/falling threshold policy remains open."}

    efuses={}
    for idx,name in ((1,"O1"),(2,"S2E")):
        rlim=val(f"RILIM{idx}"); cdvdt=val(f"CDVDT{idx}"); rimon=val(f"RIMON{idx}")
        ren_top,ren_bot=val("REN1"),val("REN2")
        rpg_top,rpg_bot=val(f"RPG{idx}"),val(f"RPG{idx}B")
        ilim=1460/rlim+.11
        cap_port=val(f"CEFOUT{idx}")
        eport=.5*cap_port*11.0**2
        short_i=3*ilim
        short_p=11.0*short_i
        rimon_hi=rimon*(1+tolerance(bom[f"RIMON{idx}"])+25e-6*50)
        imon_vmax15=15*253.4e-6*rimon_hi
        imon_pmax15=imon_vmax15**2/rimon_hi
        efuses[name]={"RILIM_ohm":rlim,"nominal_ILIM_A":ilim,
            "formula_second_A":1460*(1/rlim)+.11,
            "ILIM_screen_if_RILIM_1pct_assumption_A":[1460/(rlim*1.01)+.11,1460/(rlim*.99)+.11],
            "published_guaranteed_range_A":"AÇIK: no guarantee for exact resistor value located; TPS25982 table values are discrete. 300 Ω gives 4.36–5.66 A across temperature; do not interpolate to 301 Ω or 604 Ω.",
            "IMON_nominal_V_per_A":246e-6*rimon,"IMON_nominal_at_trip_V":246e-6*rimon*ilim,
            "IMON_gain_min_typ_max_uA_per_A":[238.6,246,253.4],
            "IMON_at_15A_V_max_gain_and_Rmax":imon_vmax15,"IMON_resistor_power_at_15A_W":imon_pmax15,
            "IMON_resistor_rating_W_manufacturer":.1,
            "IMON_resistor_fraction_of_rating_at_15A":imon_pmax15/.1,
            "IMON_accuracy_domain":"3 A..min(15 A, ILIM), -40..75 °C; S2E nominal ILIM is below 3 A, so gain accuracy not guaranteed at its trip.",
            "dVdt_typ_V_per_ms":4.6,"dVdt_min_max_V_per_ms":[2.0,6.33],
            "nominal_EN_rising_bus_V":1.2*(ren_top+ren_bot)/ren_bot,
            "EN_rising_bus_corner_V_assumed_1pct":[1.18*(1+ren_top*.99/(ren_bot*1.01)),1.23*(1+ren_top*1.01/(ren_bot*.99))],
            "EN_leak_shift_V_per_uA_assumed":ren_top*1e-6,
            "EN_trip_pin_V_at_11V":11*ren_bot/(ren_top+ren_bot),
            "PG_divider_V_at_11V":11*rpg_bot/(rpg_top+rpg_bot),
            "PG_divider_11V_corner_V_assumed_1pct":[11*rpg_bot*.99/(rpg_top*1.01+rpg_bot*.99),11*rpg_bot*1.01/(rpg_top*.99+rpg_bot*1.01)],
            "port_capacitance_nominal_F":cap_port,"charge_0to11V_C":cap_port*11.0,
            "port_cap_energy_0to11V_J":eport,
            "inrush_at_typ_dVdt_A":cap_port*4.6e3,
            "short_fault_sensitivity_at_3x_ILIM":{"current_A":short_i,"FET_power_W_at_11V":short_p,
                "energy_J_if_constant_for_400ns":short_p*400e-9,"tag":"VARSAYIM; not SOA proof"},
            "RON_max_ohm":4.5e-3,"RON_loss_at_nominal_ILIM_W":ilim**2*4.5e-3,
            "OVP_trip_V_min_typ_max":[16.32,16.9,17.31],"OVP_response_max_s":5e-6,
            "short_circuit_response_max_s":400e-9,"note":"SC response test condition and retry/latch behavior are not equivalent to normal overload. Thermal/SOA is not contained in the behavioral model."}

    input_currents={str(eff):82.5/(20*eff) for eff in (.8,.9,.95)}
    q1_i=82.5/(20*.8)
    q1_rds=.016
    q1_rds_loss=q1_i*q1_i*q1_rds
    q1_drop20=.020*q1_i
    q1_screen=dual("Q1 conduction loss at 82.5 W, 20 V, 80% efficiency", "W", q1_rds_loss,
                   q1_i*q1_i*.016,"I²*RDS(on), 25C datasheet max used as screen","(Pout/(Vin*η))²*16mΩ")
    inductor_total_loss=2*dcr_loss_hot
    shunt_total_loss=2*shunt_hot
    efuse_worst_loss=7.5**2*4.5e-3
    known_losses={"inductor_copper_two_phase_W_hot_TCR_assumption":inductor_total_loss,
                  "shunt_two_phase_W_tcr_assumption":shunt_total_loss,
                  "Q1_W_25C_RDS_max_screen":q1_rds_loss,
                  "Q1_ideal_diode_20mV_drop_W":q1_i*.020,
                  "eFuse_combined_one_branch_full_7p5A_W_upper":efuse_worst_loss,
                  "known_sum_W_not_including_buck_switching_or_controller":inductor_total_loss+shunt_total_loss+q1_rds_loss+efuse_worst_loss}
    eta={str(e):{"assumed_efficiency":e,"loss_W":82.5*(1/e-1)} for e in (.8,.9,.95)}
    thermal={"input_current_A_by_efficiency":input_currents,"known_loss_screens":known_losses,
             "efficiency_sensitivity":eta,"board_theta_assumption_C_per_W":{"2_layer":20,"4_layer":10},
             "board_temperature_rise_at_90pct_efficiency_C":{"2_layer":eta["0.9"]["loss_W"]*20,"4_layer":eta["0.9"]["loss_W"]*10},
             "ambient_reference_C":25,"design_ambient_C":"AÇIK",
             "limitations":"Board θ values are scenario assumptions only; copper area, layer stack, via field, airflow and enclosure are unknown. No junction-temperature result is certified."}

    routed=calculate_routing(phase_peak=peak, input_current=82.5/(20*.8))
    static_existing=json.loads((ROOT/"simulation/static-corner-results.json").read_text(encoding="utf-8"))
    calc_existing=json.loads((ROOT/"hardware/calculation-summary.json").read_text(encoding="utf-8"))
    c_min_dual=dual("COUT bank low sensitivity","F",cmin,
        vendor["C_11V_typ_uF"]*1e-6*8*.8*.78*.9,
        "vendor-summary Ceff × tolerance × X7S temp × assumed aging",
        "per-part vendor Ceff × 8 × tolerance × X7S temp × assumed aging","VARSAYIM")
    c_typ_dual=dual("COUT bank typical at 11 V","F",ctyp,vendor["C_11V_typ_uF"]*1e-6*8,
        "local vendor summary bank value","per-part vendor model × 8","SİM")
    c_max_dual=dual("COUT bank upper sensitivity","F",cmax,
        vendor["C_11V_typ_uF"]*1e-6*8*1.2*1.22,
        "vendor-summary upper bank sensitivity","per-part Ceff × 8 × tolerance × X7S temperature","VARSAYIM")
    fb_low_dual=dual("FB lower static corner","V",vfb["min_V"],vfb["second_min_V"],
        "16-corner vertex enumeration","monotonic closed-form corner",
        validation_scope="independent_algorithm_same_equation")
    fb_high_dual=dual("FB upper static corner","V",vfb["max_V"],vfb["second_max_V"],
        "16-corner vertex enumeration","monotonic closed-form corner",
        validation_scope="independent_algorithm_same_equation")
    uv_duals=[]
    for name,c in (("existing 180k/10k",uv_old),("candidate 174k/10k",uv_new)):
        uv_duals.extend([
          dual(name+" lower UVLO","V",c["min_V"],c["second_min_V"],"corner vertex enumeration","monotonic closed form",
               validation_scope="independent_algorithm_same_equation"),
          dual(name+" upper UVLO","V",c["max_V"],c["second_max_V"],"corner vertex enumeration","monotonic closed form",
               validation_scope="independent_algorithm_same_equation")])
    efuse_duals=[]
    for idx,name in ((1,"O1"),(2,"S2E")):
        rlim=val(f"RILIM{idx}"); cdvdt=val(f"CDVDT{idx}")
        e=efuses[name]
        efuse_duals.extend([
          dual(name+" nominal ILIM formula","A",1460/rlim+.11,1.460/(rlim/1000)+.11,
               "1460/R(ohm)+0.11","1.460/R(kΩ)+0.11","DATASHEET/HESAP"),
          dual(name+" dV/dt pin current","V/s",4.6e-6/cdvdt,4.6*1e3,
               "typical pin current / C_DVDT","4.6 V/ms converted to V/s","DATASHEET/HESAP"),
          dual(name+" port capacitor energy 0 to 11 V","J",.5*val(f"CEFOUT{idx}")*11**2,
               (val(f"CEFOUT{idx}")*11)*11/2,"0.5*C*V²","Q*V/2 where Q=C*V","HESAP"),
          dual(name+" eFuse short pulse FET energy sensitivity","J",e["short_fault_sensitivity_at_3x_ILIM"]["FET_power_W_at_11V"]*400e-9,
               11*3*e["nominal_ILIM_A"]*400e-9,"(Vin*Ishort)*t","Vin*t*Ishort","VARSAYIM")])
    for name,idx in (("O1",1),("S2E",2)):
        ren_top,ren_bot=val("REN1"),val("REN2")
        rpg_top,rpg_bot=val(f"RPG{idx}"),val(f"RPG{idx}B")
        efuse_duals += [dual(name+" EN nominal bus threshold","V",1.2*(ren_top+ren_bot)/ren_bot,
                             1.2*(1+ren_top/ren_bot),"Vth*(Rtop+Rbottom)/Rbottom","Vth*(1+Rtop/Rbottom)","DATASHEET/HESAP"),
                        dual(name+" PG divider at 11V","V",11*rpg_bot/(rpg_top+rpg_bot),
                             11/(1+rpg_top/rpg_bot),"Vin*Rbottom/(Rtop+Rbottom)","Vin/(1+Rtop/Rbottom)")]
    ilim_sum=efuses["O1"]["nominal_ILIM_A"]+efuses["S2E"]["nominal_ILIM_A"]
    ilim_sum_dual=dual("sum of nominal O1 and S2E current limits","A",ilim_sum,
                       (1460/val("RILIM1")+.11)+(1460/val("RILIM2")+.11),
                       "sum calculated channel limits","independent per-channel formula then sum")
    dcr_loss_dual=dual("inductor copper loss per phase, hot DCR sensitivity","W",dcr_loss_hot,
        (phase_worst**2+ripple_a**2/12)*dcr_hot,
        "I_rms² × hot DCR","(I_DC² + deltaI²/12) × hot DCR","VARSAYIM")
    shunt_loss_dual=dual("shunt power per phase, tolerance/TCR sensitivity","W",shunt_hot,
        (phase_worst**2+ripple_a**2/12)*rs*(1+rs_tol)*(1+100e-6*100),
        "I_rms² × Rmax(T)","(I_DC² + deltaI²/12) × Rnom × tolerance × TCR","VARSAYIM")
    input_i_dual=dual("battery input current at 82.5 W / 80%","A",82.5/(20*.8),(82.5/.8)/20,
        "Pout/(Vin×efficiency)","Pin/Vin","VARSAYIM")
    ovp_threshold=11.35*1.01
    ovp_delta=10*.5e-6/10e-6
    ovp_duals=[dual("proposed comparator high trip corner","V",ovp_threshold,11.35*(1+.01),
                    "Vtrip_nom × (1+tolerance)","nominal threshold plus relative error","VARSAYIM"),
               dual("O1 capacitive overshoot at 10 A / 0.5 us / 10 uF","V",ovp_delta,(10*.5e-6)/10e-6,
                    "I×t/C","(I×t) charge / C","VARSAYIM")]
    dual_checks=[ripple_peak,peak_result,cap_res,fb_nom,sense_min,sense_max,q1_screen,
                 c_min_dual,c_typ_dual,c_max_dual,fb_low_dual,fb_high_dual,*uv_duals,*efuse_duals,
                 ilim_sum_dual,*[x for x in rcomp],dcr_loss_dual,shunt_loss_dual,input_i_dual,*ovp_duals,
                 *routed["dual_path_checks"]]
    return {
        "title":"IDA PDU G1 AI calculation report","scope":"Static arithmetic and explicitly labeled sensitivity assumptions; no KiCad source reads.",
        "inputs":{"battery_V":[20,26],"nominal_V":22.2,"output_V":11,"load_target_A":7,"capacity_target_A":7.5,
                  "measured_port_currents":False,"ambient_assumption_C":25,"design_ambient":"not supplied",
                  "project_input_hashes":provenance,
                  "existing_calculation_crosscheck":{"setpoint_V":calc_existing["design"]["setpoint_nominal_V"],
                    "static_feedback_corner_V":[static_existing["feedback"]["minus40_to125C"]["min_V"],static_existing["feedback"]["minus40_to125C"]["max_V"]]},
                  "used_assets":["simulation/project_inputs.py","hardware/validation/c5750/vendor-ac-summary.json","simulation/static-corner-results.json","hardware/calculation-summary.json",".konnect/diagnostics/netclass-plan.json"]},
        "buck":{"duty":duty,"switching_frequency_Hz":1e9/(45*(val("RT1")/1e3)+53),
                "ripple":ripple_peak,"phase_peak":peak_result,"phase_average_at_equal_share_A":phase_mean,
                "assumed_share_error_fraction":share_error,"phase_average_worst_A":phase_worst,
                "IHLP_family_screen":{"inductance_nominal_H":6.8e-6,"minimum_inductance_H":l_nom*(1-l_tol),
                    "DCR_max_25C_ohm":dcr25,"DCR_125C_sensitivity_ohm":dcr_hot,
                "published_Isat_A_at_approx_20pct_L_drop":13.5,"published_Irms_A_at_40C_rise":8.0,
                    "peak_headroom_to_Isat_A":13.5-peak,"peak_fraction_of_Isat":peak/13.5,
                    "exact_orderable_MPN_candidate":"IHLP4040DZER6R8M01 (Vishay cross-reference candidate; BOM remains blank until approved)",
                    "exact_orderable_MPN":"AÇIK — not yet approved/entered into the canonical BOM",
                    "tag":"DATASHEET/VARSAYIM"},
                "inductor_loss_per_phase_W":{"25C_DCR":dcr_loss_cold,"125C_TCR_sensitivity":dcr_loss_hot},
                "shunt":{"assumed_tolerance_fraction":rs_tol,"assumed_TCR_ppm_K":100,
                    "power_per_phase_W_nominal_DCR":(phase_worst**2+ripple_a**2/12)*rs,
                    "power_per_phase_W_with_tolerance_TCR":shunt_hot,"minimum_part_power_for_50pct_rule_W":2*shunt_hot,
                    "sense_current_min_A":i_sense_min,"sense_min_dual":sense_min,
                    "sense_current_max_A":i_sense_max,"sense_max_dual":sense_max,
                    "share_error_effect_A_vs_equal":phase_worst-phase_mean,
                    "accuracy_limitation":"Shunt exact MPN, tolerance/TCR/power and controller ISNS comparator current error are open."},
                "output_capacitor":{"Ceff_min_uF":cmin*1e6,"Ceff_vendor_typ_uF":ctyp*1e6,"Ceff_max_uF":cmax*1e6,
                    "aging_assumption_fraction":.10,"ESR_bank_typ_400k_mohm":vendor["ESR_11V_400kHz_ohm"]*1e3/8,"ESR_corner":"AÇIK; vendor model typical only",
                    "conservative_aligned_capacitor_ripple":cap_res,"ESL_included":False}},
        "feedback":{"nominal":fb_nom,"corner":vfb,"static_corner_expected_V":[static_existing["feedback"]["minus40_to125C"]["min_V"],static_existing["feedback"]["minus40_to125C"]["max_V"]],
                    "source":"simulation/static-corner-results.json; independent vertex evaluation included here"},
        "loop":loop,"uvlo":uvlo,"efuses":efuses,
        "port_capacity_screen":{"nominal_ILIM_sum_A":ilim_sum,"7p5A_capacity_shortfall_A":7.5-ilim_sum,
            "screen_result":"FAIL by nominal arithmetic only: summed nominal channel limits are slightly below 7.5A; actual distribution and guaranteed min/max at 301Ω/604Ω are not established.",
            "required_action":"Measure O1/S2E loads and select RILIM values whose datasheet guaranteed minimum current limits cover the actual split with margin; do not claim 7.5A until then."},
        "input_protection":{"battery_input_current_A_at_82p5W":input_currents,
            "F1_fault_current_A":"AÇIK: Vbat/(Rbattery+Rcable+Rconnector+Rboard); source impedance, cable, interruption rating and I²t coordination unknown",
            "F1_i2t":"AÇIK: selected fuse time-current curve and prospective fault current absent",
            "TVS":{"family":"SMCJ33A","assumed_clamp_V":53.3,"standoff_V":33.0,"clamp_current_condition_A":28.0,
                   "LM74700_operating_abs_max_V":[60,65],"LM70880_recommended_abs_max_V":[80,87.5],
                   "Q1_VDS_rating_V":100,"conditional_margin_V":{"LM74700_operating":60-53.3,"LM74700_abs":65-53.3,
                      "LM70880_recommended":80-53.3,"LM70880_abs":87.5-53.3,"Q1":100-53.3},
                   "tag":"DATASHEET/VARSAYIM","limitations":"53.3 V is a pulse clamp datum at specified current; wiring ESL, surge duration/energy and actual TVS manufacturer not verified."},
            "Q1":{"RDSon_max_25C_ohm":.016,"estimated_input_A":q1_i,"conduction_loss_screen":q1_screen,
                  "ideal_diode_drop_loss_W":q1_drop20,"SOA":"AÇIK: data sheet SOA curve must be checked against the actual fault waveform; no board thermal proof."}},
        "thermal":thermal,"routing":routed,
        "datasheet_pages":{"LM70880-Q1":{"PDF_page_5":"absolute maximum ratings","PDF_page_6":"EN thresholds and thermal information; JESD thermal resistance is not application design value","PDF_page_7":"VFB 794/800/806mV, IFB 75nA, external gm 970/1200uS, 49.9kHz-frequency entry","PDF_page_8":"ISNS threshold 50/56/62mV, delay datum","PDF_page_14":"oscillator frequency equation","PDF_page_16":"external compensation/current sense description","PDF_page_34":"peak current overshoot warning and Kelvin routing"},
          "TPS25982":{"PDF_page_5":"pin functions and pins","PDF_page_7":"operating conditions","PDF_page_8":"thermal information and recommended limits","PDF_page_9":"ILIM/OVP electrical characteristics at listed resistor values","PDF_page_10":"OVP and short response timing","PDF_page_21":"OVP response behavior","PDF_page_23":"RILIM equation/current breaker","PDF_page_28":"IMON accuracy application range","PDF_page_35":"RILIM selection example"},
          "LM74700-Q1":{"PDF_page_5":"absolute maximum and recommended operating ratings","PDF_page_6":"thermal/electrical characteristics"},
          "Vishay_IHLP4040":{"PDF_page_1":"6.8uH row: DCRmax23.3mOhm, heat-rating current8A, saturation current13.5A at approximate20% drop; 75V rated operating voltage","PDF_page_2-3":"inductance and thermal performance graphs; exact application temperature must be checked"},
          "TDK_C5750":{"PDF_page_1":"22uF±20%,100V,X7S±22%,2220; DC-bias chart is typical only; vendor model AC numbers in hardware/validation/c5750/vendor-ac-summary.json"},
          "Molex_43045":{"PDF_page_8":"PS-43045-001 Rev P5 current-derating table; exact assembly wire/circuit configuration matters"},
          "Infineon_BSC160N10NS3G":{"PDF_page_1":"Product summary 100V/16mOhm/PG-TDSON-8; SOA page/operating waveform still requires exact package datasheet review"}},
        "dual_path_validation_summary":{
            "total_checks":len(dual_checks),
            "same_equation_arithmetic_crosschecks":sum(x["validation_scope"]=="same_equation_arithmetic_crosscheck" for x in dual_checks),
            "independent_algorithm_same_equation":sum(x["validation_scope"]=="independent_algorithm_same_equation" for x in dual_checks),
            "independent_physical_model_validations":0,
            "interpretation":"A second arithmetic path or algorithm is not independent model evidence. No calculation is independently validated against a production-silicon or measured physical model.",
        },
        "dual_path_checks":dual_checks,
        "status":"Calculations are screens; no physical acceptance."
    }

def calculate_routing(phase_peak: float, input_current: float) -> dict:
    plan=json.loads((ROOT/".konnect/diagnostics/netclass-plan.json").read_text(encoding="utf-8"))
    current_basis={
        "INPUT_POWER": (input_current, "82.5 W / (20 V × 80% assumed efficiency)"),
        "BUS_POWER": (7.5, "7.5 A total capacity target; measured load not available"),
        "PHASE_POWER": (phase_peak, "calculated phase peak; conservative continuous routing screen"),
        "O1_POWER": (7.5, "individual full-capacity branch envelope because port split is unmeasured; not simultaneous with S2E"),
        "S2E_POWER": (7.5, "individual full-capacity branch envelope because port split is unmeasured; not simultaneous with O1"),
    }
    for net_class in plan["classes"]:
        name=net_class["name"]
        if name in current_basis:
            net_class["current_A"],net_class["g1_current_basis"]=current_basis[name]
        elif "current_A" in net_class:
            net_class["g1_current_basis"]="Existing diagnostic plan envelope retained; not re-qualified in G1."
    plan["date"]="G1 calculation input; derived from canonical BOM/netlist and explicit assumptions"
    plan["assumed_via_current_A"]=.5
    plan["assumed_via_plating_um"]=25
    result=routing_rules_from_existing_plan(plan)
    route_duals=[]
    copper_um=plan["calculation_copper_um"]
    dt=plan["trace_deltaT_C"]
    rho=1.724e-8*(1+.00393*(plan["resistivity_temperature_C"]-20))
    drop_v=plan["drop_budget_mV_per_trunk"]/1000
    for row in result["rows"]:
        for label,current,widths in (
            ("2-layer",row["current_A_screen"],row["2_layer"]),
            ("4-layer path",row["4_layer_two_equal_paths"]["current_per_path_A"],row["4_layer_two_equal_paths"]),
        ):
            length=row["length_mm"]
            area_mil2=(current/(.048*dt**.44))**(1/.725)
            thermal_alt=area_mil2*.0254/(copper_um/25.4)
            route_duals.append(dual(
                f"{row['name']} {label} thermal width","mm",widths["thermal_width_mm" if label=="2-layer" else "thermal_width_per_path_mm"],thermal_alt,
                "IPC-2221 area then copper conversion","area in mil² divided by copper thickness in mil"))
            drop_alt=rho*(length/1000)/(copper_um*1e-6*(drop_v/current))*1000
            route_duals.append(dual(
                f"{row['name']} {label} IR-drop width","mm",widths["drop_width_mm" if label=="2-layer" else "drop_width_per_path_mm"],drop_alt,
                "rho*length*current/(copper*allowed_drop)","rho*length/(copper*(allowed_drop/current))"))
    return {"source_plan_path":".konnect/diagnostics/netclass-plan.json",
            "input_plan":plan,"current_envelopes":current_basis,
            "stackup_decision":"4 layers recommended for continuous ground return, thermal spreading, controlled power/analog separation and lower plane-path impedance. Equal sharing is a scenario only; no plane/via credit until actual connected copper and stackup are verified.",
            "calculation":result,"dual_path_checks":route_duals}

def routing_rules_from_existing_plan(plan: dict) -> dict:
    """Apply the existing calculate_routing_rules.py method to G1 inputs.

    The netclass plan and original empirical fit are reused, while all generated
    results are kept under reports/g1. The existing rule script is not edited.
    """
    copper_um=plan["calculation_copper_um"]
    dt=plan["trace_deltaT_C"]
    rho=1.724e-8*(1+.00393*(plan["resistivity_temperature_C"]-20))
    drop_v=plan["drop_budget_mV_per_trunk"]/1000
    rows=[]
    for net_class in plan["classes"]:
        if "current_A" not in net_class:
            continue
        current=float(net_class["current_A"])
        length=float(net_class["length_mm"])
        area_mil2=(current/(.048*dt**.44))**(1/.725)
        wth2=area_mil2/(copper_um/25.4)*.0254
        wdrop2=rho*(length/1000)*current/(copper_um*1e-6*drop_v)*1000
        width2=max(wth2,wdrop2)
        r2=rho*(length/1000)/(width2/1000*copper_um*1e-6)
        path_i=current/2
        area4_mil2=(path_i/(.048*dt**.44))**(1/.725)
        wth4=area4_mil2/(copper_um/25.4)*.0254
        wdrop4=rho*(length/1000)*path_i/(copper_um*1e-6*drop_v)*1000
        width4=max(wth4,wdrop4)
        r4=rho*(length/1000)/(width4/1000*copper_um*1e-6)
        via_r=rho*.0016/(math.pi*.0003*(plan.get("assumed_via_plating_um",25)*1e-6))
        via_limit=plan.get("assumed_via_current_A",.5)
        vias2=math.ceil(current/via_limit)
        vias4path=math.ceil(path_i/via_limit)
        rows.append({
            "name":net_class["name"],"current_A_screen":current,
            "current_basis":net_class.get("g1_current_basis","existing plan value; not requalified"),
            "length_mm":length,"existing_profile_width_mm":net_class.get("trace_width"),
            "2_layer":{"min_width_mm":width2,"thermal_width_mm":wth2,"drop_width_mm":wdrop2,
                "drop_mV":current*r2*1000,"loss_W":current*current*r2,
                "existing_profile_meets_screen":net_class.get("trace_width",0)>=width2,
                "via_count_per_transition_at_assumed_limit":vias2,
                "via_bank_drop_mV_per_transition":(current/vias2)*via_r*1000},
            "4_layer_two_equal_paths":{"current_per_path_A":path_i,"min_width_per_path_mm":width4,
                "thermal_width_per_path_mm":wth4,"drop_width_per_path_mm":wdrop4,
                "drop_mV":path_i*r4*1000,"loss_W":2*path_i*path_i*r4,
                "via_count_per_path_per_transition_at_assumed_limit":vias4path,
                "total_via_count_per_transition":2*vias4path,
                "via_bank_drop_mV_per_transition":(path_i/vias4path)*via_r*1000},
            "single_via_resistance_mohm_assumed":via_r*1000,"tag":"HESAP/VARSAYIM"})
    return {"plan":plan,
        "method":"Existing calculate_routing_rules.py method: IPC-2221 external empirical fit k=.048,b=.44,c=.725 plus copper Ohm-law IR drop.",
        "scope":"4-layer equal-path result uses the external-layer fit as sensitivity only; internal-plane thermal/current sharing, layout and fabrication require confirmation.",
        "via_assumption":f"{plan.get('assumed_via_current_A',.5):g} A/via and {plan.get('assumed_via_plating_um',25):g} µm assumed plating; counts per transition cluster.",
        "sources":["https://www.ti.com/lit/an/snva766/snva766.pdf","https://jlcpcb.com/capabilities/pcb-capabilities/","https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html"],"rows":rows}

def save_results() -> dict:
    data=build_results()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"calc-results.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"routing-input.json").write_text(json.dumps(data["routing"]["input_plan"],indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"routing-comparison.json").write_text(json.dumps(data["routing"]["calculation"],indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# G1 hesap sonuçları","","Birimli ve parametreli hesap kodu: `analysis/pdu_calc.py`. Her çift yolda mutlak ve yüzde fark raporlanır. Bu yolların çoğu aynı bağıntının aritmetik çapraz kontrolüdür; bağımsız fiziksel model doğrulaması değildir. Köşe enumerasyonu ile kapalı form yalnız algoritma çapraz kontrolüdür. Üretici silikonu veya ölçülmüş kartla bağımsız doğrulama sayısı sıfırdır; hesaplar fiziksel doğrulama değildir.","",
      "## İki yol doğrulama kapsamı","",
      f"{data['dual_path_validation_summary']['total_checks']} sayısal çift yol kaydı: {data['dual_path_validation_summary']['same_equation_arithmetic_crosschecks']} aynı denklem aritmetik çapraz kontrolü, {data['dual_path_validation_summary']['independent_algorithm_same_equation']} aynı denklem üzerinde farklı algoritma karşılaştırması, {data['dual_path_validation_summary']['independent_physical_model_validations']} bağımsız fiziksel model doğrulaması.",
      "Bu sınıflandırma `calc-results.json` içindeki `validation_scope` alanında her satır için ayrıca bulunur.","",
      "## Güç katı","",
      f"- 26 V, 400 kHz, Lmin=5.44 µH: bobin ripple {data['buck']['ripple']['value']:.4f} A p-p (iki yol farkı {data['buck']['ripple']['absolute_difference']:.3g} A).",
      f"- 7.5 A toplam ve varsayılan +10% faz paylaşım sapmasında tepe {data['buck']['phase_peak']['value']:.4f} A; Vishay tabloda Isat 13.5 A ile marj {data['buck']['IHLP_family_screen']['peak_headroom_to_Isat_A']:.3f} A. Exact aday var, BOM/stock onayı açık.",
      f"- Faz başı bobin bakır kaybı: 25°C DCR taraması {data['buck']['inductor_loss_per_phase_W']['25C_DCR']:.3f} W; 125°C TCR varsayımı {data['buck']['inductor_loss_per_phase_W']['125C_TCR_sensitivity']:.3f} W.",
      f"- RS: eşit olmayan paylaşım altında {data['buck']['shunt']['power_per_phase_W_with_tolerance_TCR']:.3f} W/faz; ≤50% güç kullanımı için parça en az {data['buck']['shunt']['minimum_part_power_for_50pct_rule_W']:.3f} W olmalı. MPN/TCR/tolerans açık.",
      f"- COUT etkin kapasite taraması {data['buck']['output_capacitor']['Ceff_min_uF']:.2f}–{data['buck']['output_capacitor']['Ceff_max_uF']:.2f} µF; 10% yaşlanma ek varsayımdır. Aligned-ripple konservatif hesap {data['buck']['output_capacitor']['conservative_aligned_capacitor_ripple']['value']*1e3:.2f} mVpp, ESR/ESL dahil değil.",
      "",
      "## Regülasyon, döngü ve UVLO","",
      f"- Nominal FB {data['feedback']['nominal']['value']:.6f} V; -40..125°C statik köşe {data['feedback']['corner']['min_V']:.4f}–{data['feedback']['corner']['max_V']:.4f} V (datasheet koşullu referans/bias ve direnç varsayımları).",
      f"- RCOMP 40 kHz varsayılan formülde {min(x['value'] for x in data['loop']['rcomp_screens'])/1e3:.2f}–{max(x['value'] for x in data['loop']['rcomp_screens'])/1e3:.2f} kΩ. Faz marjı ve gerçek crossover doğrulanamadı; COMP değerlerini fiziksel FRA ile ayarlayın.",
      f"- UVLO mevcut 180k/10k açma {data['uvlo']['existing_180k_10k']['min_V']:.3f}–{data['uvlo']['existing_180k_10k']['max_V']:.3f} V. 174k/10k varsayılan değişiklik {data['uvlo']['candidate_174k_10k']['max_V']:.3f} V üst köşe verir; EN sızıntısı ve TCR ayrıca açık. 20 V=3.33 V/hücre.",
      "",
      "## eFuse, giriş koruması ve termal","",
      f"- O1/S2E nominal ILIM formül değerleri {data['efuses']['O1']['nominal_ILIM_A']:.3f}/{data['efuses']['S2E']['nominal_ILIM_A']:.3f} A; kesin dirençlerde datasheet garantili min/max doğrulanamadı.",
      "- 53.3 V TVS clamp değeri varsayımsal sistem zarfıdır. Mutlak maksimum karşılaştırması pozitif marj verir, fakat transient/ESL/enerji/SOA koordinasyonu kanıtlanmadı. F1 akım/I²t/DC kesme değeri giriş empedansı bilinmediğinden hesaplanamadı.",
      "- 82.5 W çıkışta varsayım verimleri: " + ", ".join("%.0f%%: %.2f W" % (float(k)*100,v["loss_W"]) for k,v in data["thermal"]["efficiency_sensitivity"].items()) + ". Kart θ ve ortam koşulu açık olduğundan junction sıcaklık sonucu yok.",
      "",
      "## Yönlendirme","",
      "Mevcut `calculate_routing_rules.py` girdi profili ve IPC-2221/Ohm yöntemi, G1 akımlarıyla `analysis/pdu_calc.py` içinde yeniden hesaplandı; `routing-input.json` kaynağı, `routing-comparison.json` sonucu taşır. O1 ve S2E yük bölüşümü ölçülmediğinden iki dal ayrı ayrı 7.5 A zarfında boyutlandı; eşzamanlı 15 A çalışma iddiası yoktur.",
      "| Sınıf | Akım zarfı | 2L min iz | 2L IR drop | 4L min iz/yol | 4L IR drop | Via/geçiş 2L→4L |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for row in data["routing"]["calculation"]["rows"]:
        r2=row["2_layer"]; r4=row["4_layer_two_equal_paths"]
        lines.append(f"| {row['name']} | {row['current_A_screen']:.2f} A | {r2['min_width_mm']:.2f} mm | {r2['drop_mV']:.2f} mV | {r4['min_width_per_path_mm']:.2f} mm | {r4['drop_mV']:.2f} mV | {r2['via_count_per_transition_at_assumed_limit']} / {r4['total_via_count_per_transition']} |")
    lines += [
      "",
      "31.5 µm bakır, ΔT=20°C, 50 mm ve 50 mV varsayımı; 0.5 A/via ve 25 µm kaplama doğrulanmış fab değerleri değildir. 4L iç katman için dış iz fit'i yalnız duyarlılık taramasıdır.",
      "",
      "## Çift yol kayıtları","",
      "| Hesap | Yöntem 1 | Yöntem 2 | Doğrulama kapsamı | Mutlak fark | % fark |","|---|---|---|---|---:|---:|"]
    for x in data["dual_path_checks"]:
        lines.append(f"| {x['name']} | {x['method_1']} | {x['method_2']} | {x['validation_scope']} | {x['absolute_difference']:.6g} {x['unit']} | {x['relative_difference_percent']:.6g}% |")
    lines += ["","Tüm sayısal sınırlar `AÇIK` maddeler çözülmeden bileşen seçimi veya üretim onayı oluşturmaz."]
    (OUT/"calc-results.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return data

if __name__ == "__main__":
    save_results()
    print("Wrote G1 calculation and routing outputs under reports/g1.")
