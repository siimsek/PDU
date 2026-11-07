"""Native ADI controller studies; NOT yet accepted in the main schematic.

MOSFETs are explicit engineering approximations, not TI models. ESR/cold/hot
bounds are sensitivity assumptions, not manufacturer guarantees. No KiCad
source is read or written. Failure logs are retained under distinct filenames.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
BASE = dict(temp=25, offset=0, rt=219000, rb=10000, ileak=0,
            cap=660e-6, esr=.007, cgate=10e-9, cg=2e-9, rd=.005,
            load=4.5, fault='ramp', one=False, iup_extra=0, inductance=3.4e-6,
            ceramic=22e-6)
cases = {
    'ramp-nominal': {},
    'ramp-high-threshold': dict(offset=.0075, rt=219000*1.001, rb=10000*.999,
                                ileak=10e-9, cap=422.4e-6, cg=4e-9),
    'buck-cold-4m': dict(fault='buck', temp=-40, offset=.0075, rt=219000*1.001,
                       rb=10000*.999, ileak=10e-9, cap=422.4e-6, esr=.004,
                       rd=.002, cg=4e-9, load=7.5, inductance=2.72e-6),
    'buck-cold-100m': dict(fault='buck', temp=-40, offset=.0075, rt=219000*1.001,
                         rb=10000*.999, ileak=10e-9, cap=422.4e-6, esr=.1,
                         rd=.002, cg=4e-9, load=7.5, inductance=2.72e-6),
    'buck-hot-20m': dict(fault='buck', temp=125, offset=.0075, rt=219000*1.001,
                       rb=10000*.999, ileak=10e-9, cap=422.4e-6, esr=.02,
                       rd=.011, cg=4e-9, load=7.5, inductance=2.72e-6),
    'normal-high-rail': dict(fault='none', offset=-.0075, rt=219000*.999,
                             rb=10000*1.001, ileak=-10e-9, load=0),
    'startup-one-hot': dict(fault='none', temp=125, one=True, load=4.5,
                            cap=792e-6, cgate=9.5e-9, cg=.6e-9, rd=.011,
                            iup_extra=10e-6),
    'hotplug-26v': dict(fault='hotplug', load=0),
}

for name, updates in cases.items():
    p = BASE | updates
    if p['fault'] == 'buck':
        # Equivalent of two 6.8uH paths at -20% L, each23.3m+7.5m.
        # All7.5A is removed exactly at fault: worst stored current, no sink.
        # Regulated RAW pre-fault11.22V, compensate series DCR at7.5A.
        drive = 11.22 + p['load'] * .0154
        source = f'''Vsource DRIVE 0 PWL(0 0 5m {drive} 30m {drive} 30.00001m 26 45m 26 45.00001m {drive} 50m {drive} 50.1m 0 55m 0 60m {drive})
Lfault DRIVE LDCR {p['inductance']} Rser=0
RfaultDCR LDCR RAW .0154
Craw RAW 0 44u'''
        load = f"if(time<30m,{p['load']},if(time<50m,0,{p['load']}))"
    else:
        points = {'ramp': '0 0 100u 11 30m 11 30.1m 18 45m 18 45.1m 11 50m 11 50.1m 0 55m 0 55.1m 11',
                  'none': '0 0 100u 11.22 50m 11.22 50.1m 0 55m 0 55.1m 11.22',
                  'hotplug': '0 0 1u 26 50m 26 50.1m 0 55m 0 55.1m 11'}[p['fault']]
        source = f'Vsource RAW 0 PWL({points})'
        load = str(p['load'])
    text = f'''* CANDIDATE ONLY: global two PARALLEL same-direction CSD18534Q5A approximations.
* Actual ADI native LTC4365-1; exact installed symbol port order verified.
* Not a whole converter or qualified TI transistor model. No PCB approval.
.lib "C:\\Users\\SK\\AppData\\Local\\LTspice\\lib\\sub\\LTC4365-1.sub"
.temp {p['temp']}
{source}
Rovt RAW OV_RAW {p['rt']}
Rovb OV_RAW 0 {p['rb']}
Voffset OV_RAW OV {p['offset']}
Ileak OV 0 {p['ileak']}
Ruv RAW UV 100k
Rsh RAW SHDN 100k
Xcontroller 0 OV UV RAW GATE OUT FAULT SHDN LTC4365-1
Rfault RAW FAULT 100k
Rg1 GATE GM1 10
Rg2 GATE GM2 10
Vsense1 RAW D1 0
Vsense2 RAW D2 0
Mpass1 D1 GM1 OUT OUT QN W=1 L=1
{'' if p['one'] else 'Mpass2 D2 GM2 OUT OUT QN W=1 L=1'}
Cgs1 GM1 OUT {p['cg']}
Cgs2 GM2 OUT {p['cg']}
Cgd1 GM1 RAW 250p
Cgd2 GM2 RAW 250p
.model QN NMOS(Level=1 VTO=2.3 KP=200 RD={p['rd']} RS={p['rd']} TNOM={p['temp']})
* Small intrinsic capacitance maximizes startup inrush; larger is an OFF stress.
Bup_stress RAW GATE I={p['iup_extra']}*min(max((7.4-V(GATE,OUT))/.2,0),1)
Rsoft GATE SOFT 5.1k
Csoft SOFT 0 {p['cgate']}
Cin RAW 0 100n
* Equivalent of2 equal parallel330u25V polymer branches with explicit ESR.
Rbulk OUT CAP {p['esr']}
Cbulk CAP 0 {p['cap']}
* Protected-side four22uF MLCCs, deliberately assumed25%effectiveC.
* Sensitivity assumption, requires bias/temperature/vendor qualification.
Rcer OUT CER .002
Ccer CER 0 {p['ceramic']}
Bload OUT 0 I=({load})*min(max(V(OUT)/5,0),1)
Rbleed OUT 0 100k
.tran 100n 80m 0 250n uic
.options reltol=.0001 plotwinsize=0
.meas tran NORMAL AVG V(OUT) FROM=24m TO=29m
.meas tran PEAK MAX V(OUT) FROM=29m TO=45m
.meas tran RAWPEAK MAX V(RAW) FROM=29m TO=45m
.meas tran VDSPEAK MAX V(RAW,OUT) FROM=29m TO=45m
.meas tran VGS_MIN MIN V(GM1,OUT) FROM=24m TO=29m
.meas tran VGS_MAX MAX V(GM1,OUT) FROM=0 TO=80m
.meas tran RESET AVG V(OUT) FROM=75m TO=80m
.meas tran INRUSH MAX I(Cbulk) FROM=0 TO=24m
.meas tran MOS1_I MAX I(Vsense1) FROM=0 TO=24m
.meas tran MOS1_P MAX (V(D1,OUT)*I(Vsense1)) FROM=0 TO=24m
.meas tran MOS1_E INTEG (V(D1,OUT)*I(Vsense1)) FROM=0 TO=24m
.save V(RAW) V(OUT) V(GATE) V(GM1) V(GM2) V(OV) V(D1) I(Vsense1) I(Vsense2) I(Cbulk)
.end
'''
    filename = f'candidate-global-{name}-r3.cir'
    (HERE / filename).write_text(text, encoding='ascii')
    cases[name] = p | {'file': filename}
(HERE / 'global-ovp-candidate-cases.json').write_text(json.dumps(cases, indent=2))
print(f'Created{len(cases)} native candidate decks. Main schematic/common model unchanged.')
