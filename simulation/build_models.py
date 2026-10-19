"""Generate SPICE inputs ONLY from a Konnect-exported KiCad .net file.

Never reads or writes KiCad sources. IC models are engineering approximations,
not TI models. Run after export_netlist to keep both simulator inputs identical.
"""
from pathlib import Path
import hashlib
import json
import re
from footprint_policy import matches

HERE = Path(__file__).resolve().parent


def sexpr(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]', text)
    stack, root = [], None
    for token in tokens:
        if token == '(':
            item = []
            if stack:
                stack[-1].append(item)
            stack.append(item)
        elif token == ')':
            root = stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    return root


def children(node, name):
    return [v for v in node if isinstance(v, list) and v and v[0] == name]


def field(node, name, default=''):
    values = children(node, name)
    return values[0][1] if values and len(values[0]) > 1 else default


def exported(path):
    root = sexpr(path.read_text(encoding='utf-8'))
    comps = {}
    for c in children(root, 'components')[0][1:]:
        comps[field(c, 'ref')] = {'value': field(c, 'value'), 'footprint': field(c, 'footprint'), 'pins': {}}
    for n in children(root, 'nets')[0][1:]:
        for pin in children(n, 'node'):
            comps[field(pin, 'ref')]['pins'][field(pin, 'pin')] = field(n, 'name').removeprefix('/')
    return comps


def number(value):
    m = re.fullmatch(r'([\d.]+)([a-zA-Z]*)', value)
    base, suffix = float(m[1]), m[2].lower()
    return base * {'': 1, 'k': 1e3, 'm': 1e-3, 'u': 1e-6, 'uh': 1e-6, 'n': 1e-9, 'p': 1e-12}[suffix]


def build():
    source = HERE / 'pdu-current.net'
    comps = exported(source)
    netnames = sorted({n for c in comps.values() for n in c['pins'].values()})
    nodes = {n: ('0' if n == 'GND' else re.sub(r'[^A-Za-z0-9_]', '_', n)) for n in netnames}
    assert len(set(nodes.values())) == len(nodes), 'Node name normalization collision'
    val = lambda ref: number(comps[ref]['value'])
    lines = ['* AUTO-GENERATED from Konnect pdu-current.net; no KiCad source parsing.',
             '* Includes every component and exported pin. ICs/discretes are approximations.',
             '.include pdu-behavioral.lib']
    modeled = {}
    for ref, c in sorted(comps.items()):
        p = c['pins']
        ns = lambda pin: nodes[p[str(pin)]]
        if ref.startswith('J'):
            line = '* PORT ' + ref + ' ' + ' '.join(f'{k}={nodes[v]}' for k, v in p.items())
            kind = 'connector terminals'
        elif ref.startswith('R'):
            line = f'{ref} {ns(1)} {ns(2)} {val(ref):.12g}'
            kind = 'resistor'
        elif ref.startswith('C'):
            value = f'{{{val(ref):.12g}*CBIAS}}' if ref.startswith('COUT') else f'{val(ref):.12g}'
            line = f'{ref} {ns(1)} {ns(2)} {value}'
            kind = 'capacitor; COUT bias parameter explicit'
        elif ref.startswith('L'):
            # All simulator variants use an explicit series DCR, never implicit Rser.
            line = f'X{ref} {ns(1)} {ns(2)} PDU_L LVAL={val(ref):.12g}'
            kind = 'inductor + assumed 23.3mOhm DCR'
        elif ref == 'F1':
            line = f'R_F1 {ns(1)} {ns(2)} 10m'
            kind = '10mOhm assumed resistance ONLY; fuse opening NOT modeled'
        elif ref.startswith('D'):
            line = f'{ref} {ns(2)} {ns(1)} ' + ('PDU_TVS' if ref == 'D1' else 'PDU_SCHOTTKY')
            kind = 'generic diode approximation, NOT vendor model'
        elif ref == 'Q1':
            line = f'XQ1 ' + ' '.join(ns(i) for i in range(1, 6)) + ' PDU_Q1'
            kind = '16mOhm switch + body diode approximation'
        elif ref in ('U1', 'U2'):
            line = f'X{ref} ' + ' '.join(ns(i) for i in range(1, 31))
            line += f' PDU_BUCK MAIN={int(ref == "U1")} RSVAL={val("RS" + ref[-1]):.12g}'
            kind = 'average current controller approximation, not switching silicon'
        elif ref in ('U3', 'U4'):
            line = f'X{ref} ' + ' '.join(ns(i) for i in range(1, 27))
            line += f' PDU_EFUSE RLIM={val("RILIM" + str(int(ref[-1])-2)):.12g}'
            kind = 'nominal circuit breaker / latch / dVdt approximation'
        elif ref == 'U5':
            line = 'XU5 ' + ' '.join(ns(i) for i in range(1, 7)) + ' PDU_IDEAL_DIODE'
            kind = 'ideal-diode gate controller approximation'
        else:
            raise ValueError(f'Unmapped component {ref}')
        lines.append(line)
        modeled[ref] = dict(c, model=kind, spice=line)
    (HERE / 'pdu-circuit.inc').write_text('\n'.join(lines) + '\n', encoding='ascii')
    protection_refs = ['U3','U4','REN1','REN2','RILIM1','RILIM2','RIMON1','RIMON2',
        'RPG1','RPG1B','RPG2','RPG2B','CDVDT1','CDVDT2','CEFIN1','CEFIN2',
        'CEFOUT1','CEFOUT2','D2','D3','J2','J3']
    (HERE/'pdu-protection.inc').write_text('* Exact exported output-block subset; VOUT is the test boundary.\n.include pdu-behavioral.lib\n'+
        '\n'.join(modeled[r]['spice'] for r in protection_refs)+'\n',encoding='ascii')
    manifest = {'export_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'component_count': len(comps), 'pin_count': sum(len(c['pins']) for c in comps.values()),
                'net_count': len(nodes), 'net_map': nodes, 'components': modeled,
                'limitations': ['Encrypted TI vendor models cannot run in ngspice.',
                    'Behavioral IC models do not prove stability, switching, bootstrap operation, thermal or SOA.',
                    'CONFIG, RT, SYNC physical circuit is topology-checked, not simulated by average model.',
                    'COUT effective capacitance is a CBIAS assumption, not measured.',
                    'No measured O1/S2E startup load, cable model, TVS energy or fuse clearing model.']}
    (HERE / 'parity-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    # Structural invariant checks independent of simulator results.
    assert val('RBOOT1') == val('RBOOT2') == 1
    assert val('CIN_U5') >= 22e-9
    assert set(comps['CIN_U5']['pins'].values()) == {'ANODE', 'GND'}
    for i in (1, 2):
        cp = comps[f'CBOOT{i}']['pins']
        rp = comps[f'RBOOT{i}']['pins']
        assert cp['1'] == rp['1'] and rp['2'] == comps[f'U{i}']['pins']['4']
        assert cp['2'] == comps[f'U{i}']['pins']['5']
        assert comps[f'L{i}']['pins']['1'] == comps[f'U{i}']['pins']['20']
        assert comps[f'L{i}']['pins']['2'] == comps[f'RS{i}']['pins']['1']
        assert comps[f'RS{i}']['pins']['2'] == 'VOUT'
    assert comps['U1']['pins']['15'] == comps['U2']['pins']['15'] == 'COMP'
    assert comps['U1']['pins']['7'] == comps['U2']['pins']['8'] == 'SYNC'
    assert val('RT1') == val('RT2') and val('RS1') == val('RS2')
    assert val('RILIM1') == 301 and val('RILIM2') == 604
    assert val('RIMON1') == val('RIMON2') == 806
    assert matches(comps), 'Prototype footprint assignment or F1 hold changed'
    print(json.dumps({k:manifest[k] for k in ('component_count','pin_count','net_count','export_sha256')}))
    print('Structural/parity assertions: PASS')


if __name__ == '__main__':
    build()
