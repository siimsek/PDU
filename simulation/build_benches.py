"""Identical portable test benches for LTspice and ngspice."""
from pathlib import Path
import json
import re
import shutil
from build_models import exported, number

HERE = Path(__file__).resolve().parent
comps = exported(HERE / 'pdu-current.net')
cases = {}


def emit(name, text, meta):
    # Only syntax adapter differs. Physical values, topology and stimuli match.
    signals=sorted(set(re.findall(r'\b[VI]\([A-Za-z0-9_]+\)', '\n'.join(x for x in text.splitlines() if x.startswith('.meas')),re.I)))
    text=text.replace('.end\n','.options plotwinsize=0\n.save '+' '.join(signals)+'\n.end\n')
    ngtext=text.replace('pdu-inductor-lt.lib','pdu-inductor-ng.lib')
    (HERE/f'pdu-{name}.cir').write_text(text,encoding='ascii')
    (HERE/f'pdu-{name}.ng.cir').write_text(ngtext,encoding='ascii')
    cases[name]=dict(meta,file=f'pdu-{name}.cir',ng_file=f'pdu-{name}.ng.cir')


def board(name, supply, extra='', load1='3', load2='1.5', measurements=None, stop='40m', bias=.5, protection=False):
    text = f'''* PDU full-connectivity BEHAVIORAL bench: {name}; NOT vendor silicon.
.include {'pdu-protection.inc' if protection else 'pdu-circuit.inc'}
.include pdu-inductor-lt.lib
.param CBIAS={bias} LFACTOR=1
Vbattery {'VOUT' if protection else 'VBAT'} 0 {supply}
Bload1 O1_11V 0 I=({load1})*min(max(V(O1_11V)/5,0),1)
Bload2 S2E_11V 0 I=({load2})*min(max(V(S2E_11V)/5,0),1)
Rbleed VOUT 0 100k
{extra}
.tran 100n {stop} 0 1u uic
.options reltol=0.0001 abstol=1n method=gear
'''
    ms = measurements or [('BUS_AVG','AVG V(VOUT) FROM=35m TO=40m'),
            ('O1_AVG','AVG V(O1_11V) FROM=35m TO=40m'),('S2E_AVG','AVG V(S2E_11V) FROM=35m TO=40m'),
            ('IPHASE1_AVG','AVG V(M_ISNS1) FROM=35m TO=40m'),('IPHASE2_AVG','AVG V(M_ISNS2) FROM=35m TO=40m'),
            ('PG1_MAX','MAX V(PG_O1) FROM=0 TO=40m'),('PG2_MAX','MAX V(PG_S2E) FROM=0 TO=40m'),
            ('IMON1_AVG','AVG V(IMON_O1) FROM=35m TO=40m'),
            ('IMON2_AVG','AVG V(IMON_S2E) FROM=35m TO=40m')]
    if not protection:
        text+=f'Bmeasure1 M_ISNS1 0 V=V(ISNS1,VOUT)/{number(comps["RS1"]["value"]):.12g}\n'
        text+=f'Bmeasure2 M_ISNS2 0 V=V(ISNS2,VOUT)/{number(comps["RS2"]["value"]):.12g}\n'
    for key, expr in ms:
        text += f'.meas tran {key} {expr}\n'
    text += '.end\n'
    emit(name,text,{'type':'output-block' if protection else 'board-average', 'measures':[k.lower() for k,_ in ms], 'cbias':bias})


for vin in (20,22.2,26):
    board(f'startup-{vin:g}v', f'PWL(0 0 100u {vin})')
board('no-load','PWL(0 0 100u 22.2)',load1='0',load2='0')
board('load-step','PWL(0 0 100u 20)', load1='if(time<20m,0.3,3)',load2='if(time<20m,0.15,1.5)',
      measurements=[('BUS_MIN','MIN V(VOUT) FROM=20m TO=22m'),('BUS_MAX','MAX V(VOUT) FROM=20m TO=22m'),
                    ('O1_FINAL','AVG V(O1_11V) FROM=35m TO=40m'),('S2E_FINAL','AVG V(S2E_11V) FROM=35m TO=40m')])
board('bus-7p5a','PWL(0 0 100u 20)',extra='Bextra VOUT 0 I=3*min(max(V(VOUT)/5,0),1)')
board('low-ceff','PWL(0 0 100u 26)',bias=.25)
# Candidate100V bank sensitivity: manufacturer model typical165uF at11V,
# and176uF*1.2*1.22 upper initial/temperature envelope. Not main BOM approval.
for suffix,bias in [('typical',164.9775/176),('upper',1.2*1.22)]:
    board(f'cout-candidate-{suffix}-startup','PWL(0 0 100u 26)',bias=bias)
    board(f'cout-candidate-{suffix}-load-step','PWL(0 0 100u 20)',
          load1='if(time<20m,0.3,3)',load2='if(time<20m,0.15,1.5)',bias=bias,
          measurements=[('BUS_MIN','MIN V(VOUT) FROM=20m TO=22m'),
                        ('BUS_MAX','MAX V(VOUT) FROM=20m TO=22m'),
                        ('O1_FINAL','AVG V(O1_11V) FROM=35m TO=40m'),
                        ('S2E_FINAL','AVG V(S2E_11V) FROM=35m TO=40m')])
board('reverse','PWL(0 0 100u -26)',load1='0',load2='0',
      measurements=[('VIN_MAX','MAX V(VIN) FROM=1m TO=40m'),('BUS_MAX','MAX V(VOUT) FROM=1m TO=40m'),('IBAT_MAX','MAX I(Vbattery) FROM=1m TO=40m')])
board('uvlo','PWL(0 0 100u 17 10m 17 10.1m 20)',
      measurements=[('BUS_BEFORE','MAX V(VOUT) FROM=1m TO=9m'),('BUS_AFTER','AVG V(VOUT) FROM=35m TO=40m')])
board('uvlo-falling','PWL(0 0 100u 20 10m 20 10.1m 18 20m 18 20.1m 16)',
      measurements=[('BUS_HOLD','AVG V(VOUT) FROM=16m TO=19m'),('BUS_OFF','MAX V(VOUT) FROM=30m TO=40m')])
board('backfeed','PWL(0 0 100u 20)',extra='Vback VIN 0 PWL(0 0 100u 26)',load1='0',load2='0',
      measurements=[('IBAT_MAX','MAX I(Vbattery) FROM=10m TO=40m'),('VIN_AVG','AVG V(VIN) FROM=35m TO=40m')])
board('efuse-ovp','PWL(0 0 100u 11 15m 11 15.1m 18 25m 18 25.1m 11)',protection=True,
      measurements=[('O1_OFF','MAX V(O1_11V) FROM=19m TO=24m'),('S2E_OFF','MAX V(S2E_11V) FROM=19m TO=24m'),
                    ('O1_RESET','AVG V(O1_11V) FROM=35m TO=40m'),('S2E_RESET','AVG V(S2E_11V) FROM=35m TO=40m'),
                    ('O1_PEAK','MAX V(O1_11V) FROM=14m TO=19m')])
board('efuse-uvlo','PWL(0 0 100u 10 10m 10 10.1m 8.6 20m 8.6 20.1m 8 30m 8 30.1m 10)',protection=True,
      measurements=[('O1_HOLD','AVG V(O1_11V) FROM=15m TO=19m'),('O1_OFF','MAX V(O1_11V) FROM=25m TO=29m'),
                    ('O1_RESET','AVG V(O1_11V) FROM=35m TO=40m')])
for port in ('o1','s2e'):
    a='if(time<15m,3,6)' if port=='o1' else '3'
    b='if(time<15m,1.5,3)' if port=='s2e' else '1.5'
    node,healthy=('O1_11V','S2E_11V') if port=='o1' else ('S2E_11V','O1_11V')
    board(f'{port}-overload','PWL(0 0 100u 11)',load1=a,load2=b,protection=True,
          measurements=[('FAULT_OFF',f'MAX V({node}) FROM=20m TO=40m'),('HEALTHY',f'AVG V({healthy}) FROM=35m TO=40m')])
for port,node,healthy in [('o1','O1_11V','S2E_11V'),('s2e','S2E_11V','O1_11V')]:
    board(f'{port}-short-latch-reset','PWL(0 0 100u 22.2 25m 22.2 25.01m 0 26m 0 26.1m 22.2)',
          extra=f'Vfault ctl 0 PWL(0 0 15m 0 15.001m 1 18m 1 18.001m 0)\nSfault {node} 0 ctl 0 FAULTSW\n.model FAULTSW SW(Ron=0.1 Roff=1T Vt=.5 Vh=.01)',
          measurements=[('FAULT_OFF',f'AVG V({node}) FROM=19m TO=24m'),('HEALTHY',f'AVG V({healthy}) FROM=19m TO=24m'),
                        ('RESET_OUT',f'AVG V({node}) FROM=35m TO=40m')])

# A separate switching bench checks actual two-phase interleaving and passives.
# It does not claim to implement the manufacturer peak-current controller.
vset=.8*(1+number(comps['RFB1']['value'])/number(comps['RFB2']['value']))
freq=1e12/(number(comps['RT1']['value'])*45+53000)
for vin in (20,26):
    period=1/freq
    width=(vset+3.75*(.05+.0233+.0075))/vin*period-20e-9
    text=f'''* Two actual parallel phases, 180 degrees; ideal PWM, NOT TI controller.
.param CBIAS=.5 LFACTOR=1
.include pdu-behavioral.lib
.include pdu-inductor-lt.lib
Vsw1 drive1 0 PULSE(0 {vin} 0 20n 20n {width:.12g} {period:.12g})
Vsw2 drive2 0 PULSE(0 {vin} {period/2:.12g} 20n 20n {width:.12g} {period:.12g})
Rsw1 drive1 SW_PH1 50m
Rsw2 drive2 SW_PH2 50m
XL1 SW_PH1 ISNS1 PDU_L LVAL={number(comps['L1']['value']):.12g}
XL2 SW_PH2 ISNS2 PDU_L LVAL={number(comps['L2']['value']):.12g}
RS1 ISNS1 VOUT {number(comps['RS1']['value']):.12g}
RS2 ISNS2 VOUT {number(comps['RS2']['value']):.12g}
Bmeasure1 M_ISNS1 0 V=V(ISNS1,VOUT)/{number(comps['RS1']['value']):.12g}
Bmeasure2 M_ISNS2 0 V=V(ISNS2,VOUT)/{number(comps['RS2']['value']):.12g}
'''
    for i in range(1,9):
        text+=f'COUT{i} VOUT 0 {{{number(comps[f"COUT{i}"]["value"]):.12g}*CBIAS}}\n'
    text+=f'''Rload VOUT 0 {vset/7.5:.12g}
.ic V(VOUT)={vset}
.tran 1n {period*1000:.12g} 0 2n uic
.options method=gear reltol=0.0001
.meas tran BUS_AVG AVG V(VOUT) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran BUS_PP PP V(VOUT) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran I1_AVG AVG V(M_ISNS1) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran I2_AVG AVG V(M_ISNS2) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran I1_PP PP V(M_ISNS1) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran I2_PP PP V(M_ISNS2) FROM={period*800:.12g} TO={period*1000:.12g}
.meas tran PHASE_DELAY TRIG V(drive1) VAL={vin/2} RISE=2 TARG V(drive2) VAL={vin/2} RISE=2
.end
'''
    name=f'interleaved-{vin}v'
    emit(name,text,{'type':'ideal-interleaved','frequency':freq,'measures':['bus_avg','bus_pp','i1_avg','i2_avg','i1_pp','i2_pp','phase_delay']})
    if vin==26:
        emit('interleaved-26v-refined',text.replace('0 2n uic','0 1n uic'),
             {'type':'ideal-interleaved','frequency':freq,'measures':['bus_avg','bus_pp','i1_avg','i2_avg','i1_pp','i2_pp','phase_delay']})

# Existing entry points now resolve to the current two-phase/protection tests.
# Preserve their former sources/logs once as historical evidence.
aliases={'compensation-step.cir':'pdu-load-step.cir','ngspice-compensation.cir':'pdu-load-step.ng.cir',
         'phase-ripple.cir':'pdu-interleaved-26v.cir','phase-ripple-20v.cir':'pdu-interleaved-20v.cir',
         'ngspice-ripple-26v.cir':'pdu-interleaved-26v.ng.cir','ngspice-ripple-20v.cir':'pdu-interleaved-20v.ng.cir'}
archive=HERE/'legacy_models'
archive.mkdir(exist_ok=True)
for alias,target in aliases.items():
    for original in (HERE/alias,(HERE/alias).with_suffix('.log')):
        if original.exists() and not (archive/original.name).exists():
            shutil.copy2(original,archive/original.name)
    (HERE/alias).write_text((HERE/target).read_text(),encoding='ascii')
(HERE/'model-aliases.json').write_text(json.dumps(aliases,indent=2))

(HERE/'test-cases.json').write_text(json.dumps(cases,indent=2))
print(f'Generated {len(cases)} identical dual-engine benches; fs={freq:.3f}Hz')
