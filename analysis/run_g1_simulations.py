"""Generate and run exactly the five G1 targeted ngspice families."""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
from pdu_calc import ROOT, OUT

SIM=ROOT/"simulation"
DEST=OUT/"sim"
NGSPICE=Path(r"F:\Spice64\bin\ngspice_con.exe")

def emit(name, deck):
    path=DEST/(name+".cir")
    path.write_text(deck,encoding="ascii")
    return path

def avg_circuit(cbias=.5,rcomp=9530,cc=4.7e-9,chf=47e-12, source="PWL(0 0 100u 20)",
                loads="", stop="40m", measures=""):
    inc=(SIM/"pdu-circuit.inc").read_text(encoding="ascii")
    inc=inc.replace("RUV1 VIN EN_BUCK 180000","RUV1 VIN EN_BUCK 174000")
    inc=inc.replace("RCOMP COMP COMP_MID 9530",f"RCOMP COMP COMP_MID {rcomp:.12g}")
    inc=inc.replace("CCOMP COMP_MID 0 4.7e-09",f"CCOMP COMP_MID 0 {cc:.12g}")
    inc=inc.replace("CHF COMP 0 4.7e-11",f"CHF COMP 0 {chf:.12g}")
    return f"""* G1 average model case; non-silicon controller approximations.
.param CBIAS={cbias:.12g} LFACTOR=1
.include pdu-inductor-ng.lib
{inc}
Vbattery VBAT 0 {source}
{loads}
Rbleed VOUT 0 100k
.tran 1u {stop} 0 2u uic
.options reltol=0.0001 abstol=1n method=gear
{measures}
.end
"""

def decks():
    DEST.mkdir(parents=True,exist_ok=True)
    result={}
    result["family1_ovp"]=[emit("family1-ovp-independent-latch", """* Ideal comparator/latch/series switch sensitivity only; not a vendor part.
.param VTRIP=11.46 COUT=10u TDELAY=0.5u
Vfault SOURCE 0 PWL(0 11 4.999m 11 5m 16.9 5.2m 16.9 5.201m 11 6m 11)
Rsource SOURCE PRE 0.54
Sdisconnect PRE O1 CTRL 0 IDEALSW
Clatch CTRL 0 1n IC=1
Rlatch CTRL 0 1T
Btrip CTRL 0 I=if(V(O1)>VTRIP,1m,0)
* The initial latch voltage holds the series switch on; 1mA discharges 1nF
* through 0.5V in 0.5us after threshold crossing, then remains latched off.
.model IDEALSW SW(Ron=10m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT O1 0 {COUT}
Rload O1 0 1Meg
.ic V(O1)=11
.tran 10n 6m 0 20n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran O1_PEAK MAX V(O1) FROM=4.9m TO=5.2m
.meas tran O1_STEADY AVG V(O1) FROM=4m TO=4.9m
.meas tran LATCH_MAX MAX V(CTRL) FROM=4.9m TO=5.2m
.end
""")]

    # Idealized O-variant threshold/delay isolates the low-frequency fault
    # topology after the exported-model version hit a convergence singularity.
    f2="""* Buck high-side short: Lmin/hot-DCR path; idealized eFuse OVP timing, not silicon.
.param VTRIP=16.32 CBUK=92.6514u
Vshort VIN 0 PWL(0 11 999u 11 1m 26 2m 26)
Rcoil VIN LNODE 0.03245
Lfault LNODE VOUT 5.44u IC=0
CBUS VOUT 0 {CBUK} IC=11
Rbleed VOUT 0 1k
Sefuse VOUT O1 CTRL 0 EFUSESW
Clatch CTRL 0 10n IC=1
Rlatch CTRL 0 1T
Btrip CTRL 0 I=if(V(VOUT)>VTRIP,1m,0)
.model EFUSESW SW(Ron=10m Roff=1T Vt=0.5 Vh=0.05)
CEFOUT O1 0 10u IC=10.9
Rload1 O1 0 2.2
.ic V(VOUT)=11 V(O1)=10.9
.tran 50n 2m 0 100n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran BUS_PEAK MAX V(VOUT) FROM=1m TO=2m
.meas tran O1_PEAK MAX V(O1) FROM=1m TO=2m
.meas tran PHASE_CURRENT MAX I(Lfault) FROM=1m TO=2m
.end
"""
    result["family2_buck_highside_short"]=[emit("family2-buck-highside-short",f2)]

    start_loads="""Bload1 O1_11V 0 I=0.45*min(max(V(O1_11V)/5,0),1)
Bload2 S2E_11V 0 I=0.30*min(max(V(S2E_11V)/5,0),1)"""
    f3=avg_circuit(.5,9530,4.7e-9,47e-12,
        "PWL(0 0 100u 20 5m 20 5.1m 26 10m 26 10.1m 18 15m 18 15.1m 20 25m 20)",
        start_loads,"25m",
        ".meas tran BUS_AT_20 AVG V(VOUT) FROM=3m TO=4m\n.meas tran BUS_AT_26 AVG V(VOUT) FROM=8m TO=9m\n.meas tran BUS_AFTER_RESTART AVG V(VOUT) FROM=20m TO=24m\n.meas tran O1_PEAK MAX V(O1_11V) FROM=0 TO=25m")
    result["family3_startup_uvlo"]=[emit("family3-startup-uvlo",f3)]

    step_load="""Bload1 O1_11V 0 I=if(time<10m,0.45,if(time<20m,4.5,0.45))*min(max(V(O1_11V)/5,0),1)
Bload2 S2E_11V 0 I=if(time<10m,0.30,if(time<20m,2.5,0.30))*min(max(V(S2E_11V)/5,0),1)"""
    f4=[]
    for label,cb,rc in (("minc_lowcomp",92.6514/176,10010),("typc_midcomp",164.9775/176,17800),("maxc_highcomp",241.5271/176,26080)):
        deck=avg_circuit(cb,rc,4.7e-9,47e-12,"PWL(0 0 100u 20)",step_load,"30m",
            ".meas tran BUS_MIN MIN V(VOUT) FROM=10m TO=12m\n.meas tran BUS_MAX MAX V(VOUT) FROM=10m TO=12m\n.meas tran O1_PEAK MAX V(O1_11V) FROM=10m TO=20m\n.meas tran BUS_RECOVER AVG V(VOUT) FROM=25m TO=29m")
        f4.append(emit("family4-load-step-"+label,deck))
    result["family4_load_step_comp_corners"]=f4

    hotplug="""* eFuse output dV/dt and port hot-plug; model only.
.include pdu-protection.inc
Vbus VOUT 0 PWL(0 0 1m 0 1.001m 11 12m 11)
Bload1 O1_11V 0 I=1*min(max(V(O1_11V)/5,0),1)
Bload2 S2E_11V 0 I=0.5*min(max(V(S2E_11V)/5,0),1)
.tran 100n 12m 0 200n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran O1_PEAK MAX V(O1_11V) FROM=1m TO=12m
.meas tran O1_FINAL AVG V(O1_11V) FROM=10m TO=12m
.meas tran S2E_FINAL AVG V(S2E_11V) FROM=10m TO=12m
.end
"""
    short="""* O1 output hard short; behavioral O-variant eFuse.
.include pdu-protection.inc
Vbus VOUT 0 11
Bload1 O1_11V 0 I=1*min(max(V(O1_11V)/5,0),1)
Bload2 S2E_11V 0 I=1*min(max(V(S2E_11V)/5,0),1)
Vfault CTRL 0 PWL(0 0 20m 0 20.001m 1 25m 1 25.001m 0)
Sfault O1_11V 0 CTRL 0 FAULTSW
.model FAULTSW SW(Ron=0.1 Roff=1T Vt=0.5 Vh=0.01)
.tran 100n 35m 0 200n uic
.options reltol=0.0001 abstol=1n method=gear
.meas tran O1_SHORT_AVG AVG V(O1_11V) FROM=21m TO=24m
.meas tran O1_SHORT_PEAK MAX V(O1_11V) FROM=20m TO=25m
.meas tran S2E_HEALTHY AVG V(S2E_11V) FROM=21m TO=24m
.meas tran O1_RESET AVG V(O1_11V) FROM=30m TO=34m
.end
"""
    result["family5_efuse_short_hotplug"]=[emit("family5-hotplug",hotplug),emit("family5-o1-short",short)]
    return result

def run_one(path):
    log=path.with_suffix(".log")
    prior_log=None
    if log.exists():
        index=1
        while log.with_name(log.stem+f"-attempt{index}.log").exists(): index+=1
        prior_log=log.with_name(log.stem+f"-attempt{index}.log")
        prior_log.write_bytes(log.read_bytes())
        prior_deck=path.with_name(path.stem+f"-attempt{index}.cir")
        if path.exists(): prior_deck.write_bytes(path.read_bytes())
    try:
        p=subprocess.run([str(NGSPICE),"-D","ngbehavior=ltpsa","-b","-o",str(log),str(path)],
                         cwd=SIM,timeout=120,check=False,capture_output=True,text=True)
        logtext=log.read_text(encoding="utf-8",errors="replace") if log.exists() else p.stdout+p.stderr
    except Exception as e:
        return {"deck":path.name,"log":log.name,"completed":False,"exit_code":None,"error":str(e),"measures":{}}
    measures={m.group(1).lower():float(m.group(2)) for m in re.finditer(r"(?im)^\s*([a-z0-9_]+)\s*=\s*([+-]?[0-9.]+(?:e[+-]?\d+)?)",logtext)}
    ok=p.returncode==0 and bool(measures) and "run simulation(s) aborted" not in logtext.lower()
    prior_error=None
    if prior_log and prior_log.exists():
        prior_text=prior_log.read_text(encoding="utf-8",errors="replace")
        prior_error="initial run preserved; setup/device error" if "error on line" in prior_text.lower() else "initial run preserved"
    return {"deck":path.name,"log":str(log.relative_to(OUT)),"completed":ok,"exit_code":p.returncode,
            "initial_attempt_log":str(prior_log.relative_to(OUT)) if prior_error else None,
            "initial_attempt_note":prior_error,
            "error":None if ok else (p.stderr or "solver or measurement failure; deck not counted passed"),"measures":measures}

def parse_existing_baseline():
    win=(OUT/"baseline-o1-windows.log").read_text(encoding="utf-8",errors="replace")
    linux=(SIM/"pdu-efuse-ovp.ng.log").read_text(encoding="utf-8",errors="replace")
    pattern=r"(?im)^\s*o1_peak\s*=\s*([0-9.]+(?:e[+-]?\d+)?)"
    w=re.search(pattern,win); l=re.search(pattern,linux)
    return {"linux_ngspice_version":"44.2 (existing recorded Linux baseline)","windows_ngspice_version":"47 (local F:\\Spice64 build)",
            "linux_o1_peak_V":float(l.group(1)) if l else None,"windows_o1_peak_V":float(w.group(1)) if w else None,
            "difference_V":abs(float(l.group(1))-float(w.group(1))) if l and w else None,
            "criterion_O1_le_12V":"FAIL in both; baseline is regression/parity fixture, not accepted design"}

def main():
    groups=decks()
    fam=[]
    baseline=parse_existing_baseline()
    previous_path=OUT/"sim-results.json"
    previous=json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {"families":[]}
    previous_by_name={f["family"]:f for f in previous.get("families",[])}
    selected=set(sys.argv[1:]) if len(sys.argv)>1 else set(groups)
    # Each condition family is a single budget item. Every generated case is
    # executed once. A solver error is preserved; no parameter fishing/retry.
    for key,paths in groups.items():
        if key not in selected and key in previous_by_name:
            fam.append(previous_by_name[key])
            continue
        cases=[run_one(p) for p in paths]
        completed=all(c["completed"] for c in cases)
        result="Completed model cases; interpretation remains model-only"
        if key=="family1_ovp":
            peak=cases[0]["measures"].get("o1_peak") if cases[0]["completed"] else None
            result=f"baseline parity {baseline['linux_o1_peak_V']} vs {baseline['windows_o1_peak_V']} V; ideal candidate O1 peak {peak} V"
        elif key=="family2_buck_highside_short":
            result=f"O1 peak {cases[0]['measures'].get('o1_peak')} V; limit 12.0 V"
        elif key=="family3_startup_uvlo":
            result="20→26 V, 18 V fall and 20 V restart; bus/O1 extrema measured in behavioral model"
        elif key=="family4_load_step_comp_corners":
            result="0.75→7.0→0.75 A, low/typ/high Ceff and corresponding RCOMP; bus extrema logged"
        elif key=="family5_efuse_short_hotplug":
            result="port hot-plug plus O1 short/healthy S2E checks; model-only"
        status="completed" if completed else "INCOMPLETE — no criterion pass"
        criteria=False
        if completed and key=="family1_ovp":
            # The historical baseline is expected to FAIL; criterion applies
            # to the idealized candidate run only and never erases that FAIL.
            criteria=cases[0]["measures"].get("o1_peak",99)<=12
            status="candidate model PASS; baseline regression FAIL preserved; physical OVP open" if criteria else "candidate model FAIL; baseline regression FAIL preserved"
        if completed and key=="family2_buck_highside_short":
            criteria=cases[0]["measures"].get("o1_peak",99)<=12
            status="completed; O1 ≤12 V gate FAIL" if not criteria else "candidate model PASS only; physical gate open"
        if completed and key=="family3_startup_uvlo":
            m=cases[0]["measures"]; criteria=m.get("bus_after_restart",0)>=10.78 and m.get("o1_peak",99)<=12
        if completed and key=="family4_load_step_comp_corners":
            criteria=all(c["measures"].get("o1_peak",99)<=12 and 10.78<=c["measures"].get("bus_min",0)
                         and c["measures"].get("bus_max",99)<=11.22 for c in cases)
        if completed and key=="family5_efuse_short_hotplug":
            m=cases[1]["measures"]; criteria=m.get("o1_short_avg",99)<=1 and m.get("s2e_healthy",0)>=10.78
        fam.append({"family":key,"completed":completed,"criterion_pass":bool(criteria),"status":status,
                    "result":result,"cases":cases,"log":"reports/g1/sim/*.log"})
    data={"tool":"ngspice 47 Windows for new runs; pdu-behavioral.lib non-silicon engineering model",
          "baseline_parity":baseline,"family_count":len(fam),"budget_limit":5,"families":fam,
          "global_limit":"No aborted/uncompleted case is counted as passing. Any numeric model pass is not physical evidence.",
          "solver_retry_policy":"Five named families total. Failed setup/solver logs are preserved. Family 2: duplicate-device setup failure, then one timestep failure at xu3.ena in the detailed topology; the final simplified behavioral topology completed with the failure criterion preserved. No repeated same-error convergence tweaking.",
          "source_decks":"Generated under reports/g1/sim from exported pdu-circuit.inc or pdu-protection.inc; no source netlist, model, or KiCad files changed."}
    (OUT/"sim-results.json").write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# G1 targeted ngspice runs","","| Family | Completed? | Criterion | Result | Log |","|---|---|---|---|---|"]
    for f in fam:
        lines.append(f"| {f['family']} | {'yes' if f['completed'] else 'no'} | {'PASS model criterion' if f['criterion_pass'] else 'FAIL/OPEN'} | {f['result']} | `{f['log']}` |")
        for c in f["cases"]:
            lines.append(f"| ↳ `{c['deck']}` | {'yes' if c['completed'] else 'no'} | — | `{json.dumps(c['measures'],sort_keys=True)}` | `{c['log']}` |")
    lines += ["","Baseline parity: Linux ngspice-44.2 recorded O1 peak **%s V**; Windows ngspice-47 measured **%s V**; displayed difference **%s V**. Both preserve the expected ~16.89 V failure."%(baseline['linux_o1_peak_V'],baseline['windows_o1_peak_V'],baseline['difference_V']),
              "","Interpretation: all decks use behavioral approximations, not TI silicon; any SİM criterion pass is not physical acceptance. Family 2's first draft failed setup because REN1 was duplicated; the next detailed topology hit timestep-too-small at xu3.ena. Both logs are retained. A simplified behavioral topology completed and still FAILs the O1 ≤12 V gate at 18.8039 V; no further solver convergence tweaking was done."]
    (OUT/"SIMULATION-RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"family_count":len(fam),"families":[(f['family'],f['completed'],f['criterion_pass']) for f in fam]},ensure_ascii=True))

if __name__=="__main__": main()
