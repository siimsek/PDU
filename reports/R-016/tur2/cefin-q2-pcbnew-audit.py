import json, math
from pathlib import Path
import pcbnew

out = Path('reports/R-016/tur2')
b = pcbnew.LoadBoard('PDU.kicad_pcb')
fps = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, num, net=None):
    a=[p for p in fps[ref].Pads() if p.GetNumber()==str(num) and (net is None or p.GetNetname()==net)]
    if not a: raise RuntimeError(f'missing {ref}.{num} {net}')
    return a[0]
def rec(p):
    q=p.GetPosition(); s=p.GetSize(); r=p.GetBoundingBox()
    return {'ref':p.GetParentFootprint().GetReference(),'number':p.GetNumber(),'net':p.GetNetname(),
        'center_mm':[q.x/1e6,q.y/1e6],'size_mm':[s.x/1e6,s.y/1e6],
        'rotation_deg':p.GetOrientationDegrees(),'bbox_mm':[r.GetX()/1e6,r.GetY()/1e6,r.GetWidth()/1e6,r.GetHeight()/1e6]}
def boxgap(a,b):
    ax,ay,aw,ah=a['bbox_mm']; bx,by,bw,bh=b['bbox_mm']
    dx=max(0.0,ax-(bx+bw),bx-(ax+aw)); dy=max(0.0,ay-(by+bh),by-(ay+ah))
    return math.hypot(dx,dy)
def distance(a,b): return math.dist(a['center_mm'],b['center_mm'])
pairs=[]
for cref,uref,ins,gnds in [('CEFIN1','U3',['1','2','3'],['4','5']),('CEFIN2','U4',['16'],['14'])]:
    capin=rec(pad(cref,'1','/VSAFE')); capgnd=rec(pad(cref,'2','/GND'))
    pinrows=[]
    for n in ins:
        p=rec(pad(uref,n,'/VSAFE')); pinrows.append({'signal':'IN','pin':n,'pad':p,
            'edge_gap_mm':boxgap(capin,p),'center_mm':distance(capin,p)})
    for n in gnds:
        p=rec(pad(uref,n,'/GND')); pinrows.append({'signal':'GND','pin':n,'pad':p,
            'edge_gap_mm':boxgap(capgnd,p),'center_mm':distance(capgnd,p)})
    pairs.append({'capacitor':cref,'efuse':uref,'value':fps[cref].GetValue(),
                  'efuse_rotation_deg':fps[uref].GetOrientationDegrees(),
                  'cap_in':capin,'cap_gnd':capgnd,'per_pin_gaps':pinrows,
                  'max_edge_gap_mm':max(r['edge_gap_mm'] for r in pinrows),
                  'meets_1_50mm':max(r['edge_gap_mm'] for r in pinrows)<=1.5})
# Via inventory and endpoint/via coverage.
vias=[]
for tr in b.GetTracks():
    if isinstance(tr,pcbnew.PCB_VIA):
        q=tr.GetPosition()
        vias.append({'x_mm':q.x/1e6,'y_mm':q.y/1e6,'net':tr.GetNetname(),
                     'pad_mm':tr.GetWidth(pcbnew.F_Cu)/1e6,'drill_mm':tr.GetDrillValue()/1e6})
# Pad bbox coverage by vias (use for endpoint presence, not route connectivity).
def in_box(v,p):
    x,y,w,h=p['bbox_mm']; return x-1e-6<=v['x_mm']<=x+w+1e-6 and y-1e-6<=v['y_mm']<=y+h+1e-6
endpoint_counts={}
for ref in [f'COUT{i}' for i in range(1,33)]+['U3','U4','CEFIN1','CEFIN2']:
    f=fps[ref]
    for p in f.Pads():
        if p.GetNetname() not in ('/VOUT','/VSAFE','/GND'): continue
        pr=rec(p)
        if ref.startswith('COUT') and p.GetNumber()!='1': continue
        if ref in ('U3','U4') and p.GetNumber() not in (('1','2','3','4','5') if ref=='U3' else ('14','16')): continue
        if ref.startswith('CEFIN') and p.GetNumber() not in ('1','2'): continue
        endpoint_counts[f'{ref}.{p.GetNumber()}:{p.GetNetname()}']=sum(in_box(v,pr) and v['net']==p.GetNetname() for v in vias)
# Q2, U6 and capacitor bank distances.
q2gate=rec(pad('Q2','4','/ISO_GATE')); u6gate=rec(pad('U6','6','/ISO_GATE'))
q2drain=rec(pad('Q2','5','/VOUT'))
q2origin=fps['Q2'].GetPosition()
relx=q2gate['center_mm'][0]-q2origin.x/1e6
rely=q2gate['center_mm'][1]-q2origin.y/1e6
flip_gate={'center_mm':[q2origin.x/1e6-relx,q2origin.y/1e6-rely]}
flip_gate['distance_to_U6_center_mm']=math.dist(flip_gate['center_mm'],u6gate['center_mm'])
cout=[]
for i in range(1,33):
    p=rec(pad(f'COUT{i}','1','/VOUT')); cout.append({'ref':f'COUT{i}',**p})
cent=[sum(c['center_mm'][j] for c in cout)/len(cout) for j in range(2)]
distances=[{'ref':c['ref'],'mm':math.dist(q2drain['center_mm'],c['center_mm'])} for c in cout]
vias_q2_d=sum(1 for v in vias if v['net']=='/VOUT' and in_box(v,q2drain))
q2srcpads=[rec(pad('Q2',n,'/VSAFE')) for n in ('1','2','3')]
vias_q2_s=sum(1 for v in vias if v['net']=='/VSAFE' and any(in_box(v,p) for p in q2srcpads))
tracks=[x for x in b.GetTracks() if isinstance(x,pcbnew.PCB_TRACK) and not isinstance(x,pcbnew.PCB_VIA)]
result={
 'method':'KiCad pcbnew global pad centers, pad bounding boxes, via coordinates; no PCB save',
 'cefin_pair_distances':pairs,
 'via_count':len(vias),
 'via_net_counts':{n:sum(v['net']==n for v in vias) for n in sorted({v['net'] for v in vias})},
 'q2_drain_pad5_vias_in_pad':vias_q2_d,
 'q2_source_pad1_3_vias_in_pads':vias_q2_s,
 'endpoint_via_counts':endpoint_counts,
 'q2':{'orientation_deg':fps['Q2'].GetOrientationDegrees(),'drain_pad5':q2drain,'source_pads1_3':q2srcpads,
       'gate_pad4':q2gate,'gate_U6_center_distance_mm':distance(q2gate,u6gate),
       'flip180_gate_center':[round(x,6) for x in flip_gate['center_mm']],
       'flip180_gate_to_U6_center_mm':flip_gate['distance_to_U6_center_mm'],
       'direct_to_drain_centroid_COUT_mm':distance(q2drain,{'center_mm':cent}),
       'nearest_COUT_pad':min(distances,key=lambda x:x['mm']),
       'farthest_COUT_pad_straight':max(distances,key=lambda x:x['mm'])},
 'footprint_component_count':len(list(b.GetFootprints())),
 'routed_tracks_excluding_vias':len(tracks),
 'through_vias':vias
}
(out/'cefin-q2-pcbnew-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='through_vias'},indent=2,ensure_ascii=False))
