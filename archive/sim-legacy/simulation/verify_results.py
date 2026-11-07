"""Independent bounded acceptance and cross-engine comparison of saved logs."""
from pathlib import Path
from math import isfinite
import hashlib
import json
import re
from build_models import exported, number
from footprint_policy import matches, EXPECTED_FOOTPRINTS

HERE=Path(__file__).resolve().parent
cases=json.loads((HERE/'test-cases.json').read_text())
ng=json.loads((HERE/'ngspice-results.json').read_text())
lt={}
for name,c in cases.items():
    log=(HERE/Path(c['file']).with_suffix('.log')).read_bytes()
    text=log.decode('utf-16') if log[:2] in (b'\xff\xfe',b'\xfe\xff') else log.decode('utf-8',errors='replace')
    measures={}
    for key,value in re.findall(r'^([A-Za-z][A-Za-z0-9_]*)(?::[^\r\n]*?=|\s*=)\s*([-+\d.eE]+)',text,re.M):
        if key.lower() in c['measures']:
            measures[key.lower()]=float(value)
    errors=re.findall(r'^.*(?:error|failed|tolerance relaxed|floating|timestep too small).*$' ,text,re.M|re.I)
    lt[name]={'execution_pass':not errors and set(c['measures'])<=measures.keys(),'measures':measures,'errors':errors[:4]}
(HERE/'ltspice-results.json').write_text(json.dumps(lt,indent=2))

checks=[]
def check(name,ok,detail):
    checks.append({'check':name,'pass':bool(ok),'detail':detail})

before=exported(HERE/'schematic-before-fixes.net')
after=exported(HERE/'pdu-current.net')
added=sorted(after.keys()-before.keys())
check('Only expected new parts',added==['CIN_U5','RBOOT1','RBOOT2'],added)
pin_changes=[]
value_changes=[]
for ref,c in before.items():
    for pin,net in c['pins'].items():
        if after[ref]['pins'][pin]!=net:
            pin_changes.append([ref,pin,net,after[ref]['pins'][pin]])
    if after[ref]['value']!=c['value']:
        value_changes.append([ref,c['value'],after[ref]['value']])
check('Only intended existing pin changes', {(r,p) for r,p,_,_ in pin_changes}=={('CBOOT1','1'),('CBOOT2','1')}, pin_changes)
expected_values = {('RPG1B','82.5k','18k'),('RPG2B','82.5k','18k'),
                   ('RIMON1','2.61k','806'),('RIMON2','4.99k','806')}
check('Only intended existing value changes',set(map(tuple,value_changes))==expected_values,value_changes)
check('Approved prototype footprint assignments',matches(after), EXPECTED_FOOTPRINTS)
rs=number(after['RS1']['value'])
vtarget=.8*(1+number(after['RFB1']['value'])/number(after['RFB2']['value']))

for engine,data in [('LTspice',lt),('ngspice',ng)]:
    for name,c in cases.items():
        r=data[name];m=r['measures'];prefix=f'{engine}/{name}'
        check(prefix+'/execution',r['execution_pass'],r.get('errors',[]))
        if not r['execution_pass']:
            continue
        check(prefix+'/finite',all(isfinite(x) for x in m.values()), 'all numeric measurements finite')
        for k in ('bus_avg','o1_avg','s2e_avg','o1_final','s2e_final','bus_after','bus_hold','o1_reset','s2e_reset','reset_out','healthy'):
            if k in m:
                target=10 if name=='efuse-uvlo' and k=='o1_reset' else 11
                check(prefix+'/'+k,target*.98<=m[k]<=target*1.02,f'{m[k]:.9g} V within {target}V +/-2%')
        for k in ('fault_off','bus_before','bus_off','o1_off','s2e_off'):
            if k in m:
                check(prefix+'/'+k,abs(m[k])<.1,f'{m[k]:.9g} V; off <0.1V')
        for k in ('pg1_max','pg2_max'):
            if k in m:
                check(prefix+'/'+k,0<=m[k]<6,f'{m[k]:.6g} V <6V recommended pin limit')
        for channel in (1,2):
            key=f'imon{channel}_avg'
            if key in m:
                load=(3 if channel==1 else 1.5) if name!='no-load' else 0
                expected=load*246e-6*number(after[f'RIMON{channel}']['value'])
                check(prefix+'/'+key,abs(m[key]-expected)<.002,
                      f'{m[key]:.6g}V vs nominal gain/resistor {expected:.6g}V; behavioral model only')
        if 'iphase1_avg' in m:
            check(prefix+'/sharing',abs(m['iphase1_avg']-m['iphase2_avg'])<.01,'phase average mismatch <10mA')
            total=m['iphase1_avg']+m['iphase2_avg']
            expected=7.5 if name=='bus-7p5a' else (0 if name=='no-load' else 4.5)
            check(prefix+'/total_current',abs(total-expected)<.02,f'{total:.6g} A vs {expected:g} A artificial load')
        if name=='load-step' or name.startswith('cout-candidate-') and name.endswith('-load-step'):
            check(prefix+'/transient',10.78<=m['bus_min'] and m['bus_max']<=11.22, f"{m['bus_min']:.6g}..{m['bus_max']:.6g} V, specified 0.45->4.5A step")
        if name=='reverse':
            check(prefix+'/blocked',abs(m['vin_max'])<.1 and abs(m['bus_max'])<.1 and abs(m['ibat_max'])<100e-6, 'negative battery, protected rail <0.1V and leakage <100uA')
        if name=='backfeed':
            check(prefix+'/blocked',abs(m['ibat_max'])<100e-6 and abs(m['vin_avg']-26)<.01, f"battery reverse current={m['ibat_max']:.6g} A")
        if name=='efuse-uvlo':
            # Unit block has a 10V input after reset, not the 11V system rail.
            # Override the universal reset check below by using a separate key.
            check(prefix+'/hold',8.5<m['o1_hold']<8.7, f"{m['o1_hold']:.6g} V, held at 8.6V input")
        if name=='efuse-ovp':
            check(prefix+'/O1_input_rating',m['o1_peak']<=12,f"{m['o1_peak']:.6g} V peak; O1 documented DC input maximum12V. This check must fail until protection is corrected.")
        if c['type']=='ideal-interleaved':
            vin=20 if '20v' in name else 26
            ideal=vtarget*(1-vtarget/vin)/(number(after['L1']['value'])*c['frequency'])
            check(prefix+'/sharing',abs(m['i1_avg']-m['i2_avg'])<.01,'phase average mismatch <10mA')
            check(prefix+'/current',abs(m['i1_avg']-3.75)<.03 and abs(m['i2_avg']-3.75)<.03,'3.75A per phase +/-30mA')
            check(prefix+'/ripple_formula',abs(m['i1_pp']/ideal-1)<.05 and abs(m['i2_pp']/ideal-1)<.05, f"{m['i1_pp']:.6g} A pp; ideal formula {ideal:.6g} A, +/-5%")
            check(prefix+'/phase',abs(m['phase_delay']*c['frequency']-.5)<.001, f"{m['phase_delay']:.9g} s, 180deg +/-0.36deg")

comparisons=[]
for name,c in cases.items():
    for key in c['measures']:
        a=lt[name]['measures'].get(key);b=ng[name]['measures'].get(key)
        if a is None or b is None:
            check(f'parity/{name}/{key}',False,'missing measurement');continue
        # For near-zero outputs use a physical absolute floor, not a meaningless ratio.
        floor=1e-10 if 'delay' in key else (.000001 if 'max' in key and name in ('reverse','backfeed') else .01)
        limit=max(.02*max(abs(a),abs(b)),floor)
        delta=abs(a-b)
        comparisons.append({'case':name,'measurement':key,'ltspice':a,'ngspice':b,'delta':delta,'limit':limit,'pass':delta<=limit})
        check(f'parity/{name}/{key}',delta<=limit,f'difference {delta:.6g}, limit {limit:.6g}')

pgmax=30*(18e3*1.01)/(100e3*.99+18e3*1.01)
check('PG divider worst-case 30V',pgmax<6,f'{pgmax:.6g} V at 30V rail, adverse 1% resistors; does not approve device operation at 30V')
for name,c in cases.items():
    a=(HERE/c['file']).read_text().replace('pdu-inductor-lt.lib','pdu-inductor-ng.lib')
    check('deck parity/'+name,a==(HERE/c['ng_file']).read_text(),'only the inductor syntax adapter differs')
clean=lambda p:[s.strip().replace(' Rser=0','') for s in p.read_text().splitlines() if s.strip() and not s.startswith('*')]
check('Inductor physical model parity',clean(HERE/'pdu-inductor-lt.lib')==clean(HERE/'pdu-inductor-ng.lib'),'same L and explicit 23.3mOhm DCR; LT implicit damping disabled')
for engine,data in [('LTspice',lt),('ngspice',ng)]:
    a=data['interleaved-26v']['measures'];b=data['interleaved-26v-refined']['measures']
    for k in ('bus_avg','i1_avg','i2_avg','i1_pp','i2_pp'):
        check(engine+'/timestep-refinement/'+k,abs(a[k]-b[k])<.01*abs(b[k]),'2ns and 1ns max-step results agree within 1%')
for alias,target in json.loads((HERE/'model-aliases.json').read_text()).items():
    check('entry point/'+alias,(HERE/alias).read_text()==(HERE/target).read_text(),'legacy entry point is byte-identical to current test, old sources archived')
result={'scope':'behavioral tests only; not vendor silicon or PCB/manufacturing approval',
        'case_count':len(cases),'engine_runs':len(cases)*2,'checks':checks,'comparisons':comparisons,
        'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),
        'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'pdu-current.net',HERE/'pdu-circuit.inc',HERE/'pdu-behavioral.lib',HERE/'pdu-inductor-lt.lib',HERE/'pdu-inductor-ng.lib']},
        'pin_changes':pin_changes,'value_changes':value_changes}
(HERE/'verification-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['case_count','engine_runs','passed','failed']}))
for c in checks:
    if not c['pass']:
        print('FAIL',c['check'],c['detail'])
raise SystemExit(1 if result['failed'] else 0)
