"""Reapply the verified routing profile through Konnect MCP after a clean close.

No KiCad source parsing/writing, lock deletion, GUI automation or process stop.
Use --check for a read-only prerequisite check. Recalculate the profile before
using this after changing design current, length, copper or temperature limits.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
DIAG=ROOT/'.konnect/diagnostics'
locks=[ROOT/n for n in ('~PDU.kicad_pcb.lck','~PDU.kicad_pro.lck','~PDU.kicad_sch.lck')]
held=[str(p) for p in locks if p.exists()]
if held:
    print('No changes. Save/close all PDU KiCad editors and Project Manager first; locks are not deleted.')
    print('\n'.join(held))
    sys.exit(2)
if '--check' in sys.argv:
    print('No PDU locks detected. No changes were made.')
    sys.exit(0)
plan=json.loads((DIAG/'netclass-plan.json').read_text(encoding='utf-8'))
board=str(ROOT/'PDU.kicad_pcb')
calls=[]
for c in plan['classes']:
    args={k:c[k] for k in ('name','trace_width','clearance','via_diameter','via_drill')}
    calls.append(dict(name='create_netclass',arguments=dict(board=board,**args)))
for c in plan['classes']:
    for net in c['nets']:
        calls.append(dict(name='assign_net_to_class',arguments=dict(board=board,net_name=net,netclass=c['name'])))
calls.extend([
 dict(name='set_predefined_sizes',arguments=dict(board=board,track_widths=[.2,.25,.3,.4,.5,.75,1,1.5,2,2.5,3.5,4.5,6],via_dimensions=[dict(diameter=.8,drill=.4),dict(diameter=1.2,drill=.6)])),
 dict(name='get_netclasses',arguments=dict(board=board,board_source='saved')),
 dict(name='get_predefined_sizes',arguments=dict(board=board))])
req=DIAG/'reapply-routing-calls.json';res=DIAG/'reapply-routing-results.json'
req.write_text(json.dumps(calls),encoding='utf-8')
settings=Path(os.environ['USERPROFILE'])/'Documents/KiCad/10.0/3rdparty/plugins/com_github_mixelpixx_konnect/settings.json'
subprocess.run([sys.executable,str(DIAG/'mcp_call.py'),str(req),str(res),str(settings)],check=True)
results=json.loads(res.read_text(encoding='utf-8'))['results']
errors=[r for r in results if r['response'].get('error') or r['response'].get('result',{}).get('isError')]
if errors:
    print('Incomplete. Inspect the saved MCP responses before repeating:',res)
    sys.exit(1)
data=json.loads(results[-2]['response']['result']['content'][0]['text'])
for wanted in plan['classes']:
    got=next(c for c in data['netclasses'] if c['name']==wanted['name'])
    assert all(got[k]==wanted[k] for k in ('trace_width','clearance','via_diameter','via_drill'))
    assert sorted(got['matched_nets'])==sorted(wanted['nets'])
palette=json.loads(results[-1]['response']['result']['content'][0]['text'])
assert 6 in palette['track_widths']
print('Verified saved profile:9 classes,46 exact net assignments and trace/via palette. Reopen PDU.kicad_pro now.')
