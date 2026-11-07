"""Candidate studies only; these devices are NOT accepted in the PDU schematic.

Uses the installed encrypted ADI LTC4365-1 macro-model in LTspice. MOSFETs
are bounded engineering approximations, not Infineon silicon models.
"""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
base=(HERE/'candidate-ltc4365-native.cir').read_text()
cases={
 'nominal': {'cg':2e-9,'offset':0,'top':219e3,'bottom':10e3,'temp':25},
 'high-threshold': {'cg':4e-9,'offset':7.5e-3,'top':219e3*1.001,'bottom':10e3*.999,'temp':85},
 'normal-high-rail': {'cg':4e-9,'offset':-7.5e-3,'top':219e3*.999,'bottom':10e3*1.001,'temp':-40},
 'buck-highside-short': {'cg':4e-9,'offset':7.5e-3,'top':219e3*1.001,'bottom':10e3*.999,'temp':85},
}
for name,p in cases.items():
    text=base.replace('.param CG=2n',f".param CG={p['cg']:.12g}\n.temp {p['temp']}")
    text=text.replace('Rovt VIN OV 219k',f"Rovt VIN OV_RAW {p['top']:.12g}")
    text=text.replace('Rovb OV 0 10k',f"Rovb OV_RAW 0 {p['bottom']:.12g}\nVoffset OV_RAW OV {p['offset']:.12g}")
    if name=='normal-high-rail':
        text=text.replace('100u 11 15m 11 15.1m 18 25m 18 25.1m 11',
                          '100u 11.22 15m 11.22 25m 11.22 25.1m 11.22')
    if name=='buck-highside-short':
        text=text.replace('Vsource VIN 0 PWL(0 0 100u 11 15m 11 15.1m 18 25m 18 25.1m 11 30m 11 30.1m 0 32m 0 32.1m 11)',
        '''* Both high sides stuck ON: 2 parallel6.8uH paths, each23.3m+7.5m.
* Lowest modeled common bus Ceff44uF; O1 port10uF and ideal S2E1.5A load.
Vsource DRIVE 0 PWL(0 0 5m 11.0693 15m 11.0693 15.00001m 26 25m 26 25.00001m 11.0693 30m 11.0693 30.1m 0 32m 0 35m 11.0693)
Lfault DRIVE LDCR 3.4u Rser=0
RfaultDCR LDCR VIN 15.4m
Cbus VIN 0 44u
Bother VIN 0 I=1.5*min(max(V(VIN)/5,0),1)''')
    text=text.replace('.meas tran RESET', '.meas tran AFTER_FAULT MAX V(OUT) FROM=27m TO=29m\n.meas tran RESET')
    path=HERE/f'candidate-ltc4365-{name}.cir'
    if name=='nominal':path=HERE/'candidate-ltc4365-nominal.cir'
    path.write_text(text)
    p['file']=path.name
(HERE/'ovp-candidate-cases.json').write_text(json.dumps(cases,indent=2))
print('Created4candidate studies; main schematic and common20test suite unchanged.')
