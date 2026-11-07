"""Compare only exported netlists; never opens KiCad source files."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def parse(path):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', path.read_text(encoding='utf-8'))
    stack = [[]]
    for token in tokens:
        if token == '(':
            child = []
            stack[-1].append(child)
            stack.append(child)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    return stack[0][0]

def children(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def field(node, name):
    found = children(node, name)
    return found[0][1] if found and len(found[0]) > 1 else ''

def semantic(path):
    doc = parse(path)
    components = {}
    for comp in children(children(doc, 'components')[0], 'comp'):
        source = children(comp, 'libsource')[0]
        components[field(comp, 'ref')] = {
            'value': field(comp, 'value'), 'footprint': field(comp, 'footprint'),
            'library': field(source, 'lib'), 'part': field(source, 'part'),
        }
    nets = {}
    for net in children(children(doc, 'nets')[0], 'net'):
        nets[field(net, 'name')] = sorted((field(n, 'ref'), field(n, 'pin')) for n in children(net, 'node'))
    return components, nets

before = ROOT / '.konnect/diagnostics/power-ics-assigned.net'
after = ROOT / '.konnect/diagnostics/schematic-finished.net'
a, an = semantic(before)
b, bn = semantic(after)
report = {
    'baseline': str(before), 'current': str(after),
    'same_components_values_footprints_libraries': a == b,
    'same_named_nets_and_ref_pin_membership': an == bn,
    'component_count': len(b), 'net_count': len(bn),
    'exported_pin_count': sum(len(v) for v in bn.values()),
    'component_differences': {k: [a.get(k), b.get(k)] for k in a.keys() | b.keys() if a.get(k) != b.get(k)},
    'net_differences': {k: [an.get(k), bn.get(k)] for k in an.keys() | bn.keys() if an.get(k) != bn.get(k)},
}
(ROOT / '.konnect/diagnostics/schematic-finish-parity.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
assert report['same_components_values_footprints_libraries']
assert report['same_named_nets_and_ref_pin_membership']
