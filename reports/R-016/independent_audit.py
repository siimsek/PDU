from __future__ import annotations
import json, math, subprocess, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from kicad_sexpr import Atom, SList, parse, top, dumps, walk
import pcbnew

BOARD = Path('PDU.kicad_pcb')
OUT = Path('reports/R-016')

def kids(node, head=None):
    return [x for x in node if isinstance(x, SList) and (head is None or x.head == head)]
def one(node, head):
    return next((x for x in kids(node, head)), None)
def vals(node, head):
    x = one(node, head)
    return [a.value for a in x.atoms()[1:] if isinstance(a, Atom)] if x else []
def ref_of(fp):
    for p in kids(fp, 'property'):
        a=p.atoms()
        if len(a)>2 and a[1].value=='Reference': return a[2].value
    return None
def prop_of(fp, name):
    for p in kids(fp, 'property'):
        a=p.atoms()
        if len(a)>2 and a[1].value==name: return a[2].value
    return None
def ring_from_pts(pts):
    return [tuple(float(a.value) for a in xy.atoms()[1:3]) for xy in kids(pts,'xy')]
def ring_area(r):
    return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))/2) if len(r)>=3 else 0.0
def point_ring(x,y,ring):
    inside=False
    for i,(x1,y1) in enumerate(ring):
        x2,y2=ring[(i+1)%len(ring)]
        dx,dy=x2-x1,y2-y1
        cross=(x-x1)*dy-(y-y1)*dx
        if abs(cross)<1e-7 and min(x1,x2)-1e-7<=x<=max(x1,x2)+1e-7 and min(y1,y2)-1e-7<=y<=max(y1,y2)+1e-7:
            return True
        if (y1>y)!=(y2>y):
            xin=x1+(y-y1)*dx/dy
            if x<xin: inside=not inside
    return inside
def shape_from_fill(fill):
    outer=ring_from_pts(one(fill,'pts'))
    holes=[]
    for h in kids(fill,'hole'):
        pts=one(h,'pts')
        if pts: holes.append(ring_from_pts(pts))
    area=max(0.0,ring_area(outer)-sum(ring_area(h) for h in holes))
    return {'layer':vals(fill,'layer')[0], 'area_mm2':area, 'outer':outer,'holes':holes,
            'island_marker':bool(kids(fill,'island'))}
def contains(shape,x,y):
    return point_ring(x,y,shape['outer']) and not any(point_ring(x,y,h) for h in shape['holes'])
def value_from_net(n):
    a=n.atoms()
    return a[-1].value if len(a)>1 else ''
def board_footprints(expr):
    out={}
    for fp in kids(expr,'footprint'):
        ref=ref_of(fp)
        if not ref: continue
        a=one(fp,'at'); at=[x.value for x in a.atoms()[1:4]] if a else []
        layer=vals(fp,'layer')
        lib=fp.atoms()[1].value if len(fp.atoms())>1 else ''
        padnets=[]
        for p in kids(fp,'pad'):
            pa=p.atoms(); num=pa[1].value if len(pa)>1 else ''
            n=one(p,'net'); padnets.append((num,value_from_net(n) if n else ''))
        out[ref]={'lib':lib,'value':prop_of(fp,'Value'),'at':at,'layer':layer,
                  'padnets':sorted(set(padnets))}
    return out

board_expr=top(parse(BOARD.read_text(encoding='utf-8')))
commit=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
zone_records=[]
zone_shapes={}
for iz,z in enumerate(kids(board_expr,'zone'),1):
    name=vals(z,'name'); net=vals(z,'net'); layer=vals(z,'layer')
    fills=[shape_from_fill(f) for f in kids(z,'filled_polygon')]
    area=sum(f['area_mm2'] for f in fills)
    rec={'index':iz,'name':name[0] if name else '', 'net':net[0] if net else '',
         'layer':layer[0] if layer else '', 'filled_polygon_count':len(fills),
         'island_marker_count':sum(f['island_marker'] for f in fills),
         'hole_count':sum(len(f['holes']) for f in fills),
         'filled_area_mm2':round(area,3)}
    zone_records.append(rec)
    for f in fills:
        zone_shapes.setdefault((rec['net'],f['layer']),[]).append(f)

via_records=[]
for i,v in enumerate(kids(board_expr,'via'),1):
    at=vals(v,'at'); x,y=map(float,at[:2]); size=float(vals(v,'size')[0]); drill=float(vals(v,'drill')[0])
    layers=vals(v,'layers'); net=vals(v,'net')[0]
    connected=[]
    for (n,layer),shapes in zone_shapes.items():
        if n==net and any(contains(s,x,y) for s in shapes): connected.append(layer)
    via_records.append({'id':i,'x_mm':x,'y_mm':y,'pad_mm':size,'drill_mm':drill,
                        'layers':layers,'net':net,'filled_zone_layers_at_center':sorted(connected)})

# Copper-bearing zone/island and via-to-fill checks.
l2g=[z for z in zone_records if z['net']=='/GND' and z['layer']=='In1.Cu']
l4g=[z for z in zone_records if z['net']=='/GND' and z['layer']=='B.Cu']
via_conn_summary={}
for net,layer in [('/GND','In1.Cu'),('/GND','B.Cu'),('/GND','In2.Cu'),('/VIN','In2.Cu'),('/VOUT','In2.Cu'),('/VSAFE','In2.Cu')]:
    group=[v for v in via_records if v['net']==net]
    via_conn_summary[f'{net}@{layer}']={'via_count':len(group),'centers_in_filled_zone':sum(layer in v['filled_zone_layers_at_center'] for v in group)}

# Board-library geometry: pad identities/center locations and selected via-in-pad verification.
b=pcbnew.LoadBoard(str(BOARD))
fp_by_ref={f.GetReference():f for f in b.GetFootprints()}
def pick_pad(ref,num,net=None,largest=False):
    pads=[p for p in fp_by_ref[ref].Pads() if p.GetNumber()==num and (net is None or p.GetNetname()==net)]
    if not pads: raise RuntimeError(f'missing pad {ref}.{num} {net}')
    if largest:
        pads.sort(key=lambda p:p.GetSize().x*p.GetSize().y,reverse=True)
    p=pads[0]; pos=p.GetPosition(); size=p.GetSize()
    return {'ref':ref,'number':num,'net':p.GetNetname(),'x_mm':pos.x/1e6,'y_mm':pos.y/1e6,
            'width_mm':size.x/1e6,'height_mm':size.y/1e6}
def in_pad_box(v,p):
    return abs(v['x_mm']-p['x_mm']) <= p['width_mm']/2+1e-6 and abs(v['y_mm']-p['y_mm']) <= p['height_mm']/2+1e-6
pad_specs=[('U1','30','/GND',False),('U2','30','/GND',False),('Q1','5','/VIN',True),('Q2','5','/VOUT',True)]
pad_via_results=[]
for ref,num,net,largest in pad_specs:
    p=pick_pad(ref,num,net,largest)
    candidates=[v for v in via_records if v['net']==net and in_pad_box(v,p)]
    target_layer='In1.Cu' if net=='/GND' and ref in ('U1','U2') else 'In2.Cu'
    pad_via_results.append({**p,'via_count_inside_pad':len(candidates),
       'via_ids_inside_pad':[v['id'] for v in candidates],
       'same_net_filled_target_layer_count':sum(target_layer in v['filled_zone_layers_at_center'] for v in candidates),
       'target_layer':target_layer})

# Thermal regions tied to actual L3 fills; Q2 source and drain are both shown separately.
thermal=[]
for ref,padnum,net in [('Q1','5','/VIN'),('Q2','5','/VOUT'),('Q2','1','/VSAFE')]:
    recs=[z for z in zone_records if z['net']==net and z['layer']=='In2.Cu']
    area=sum(z['filled_area_mm2'] for z in recs)
    thermal.append({'device':ref,'pad':padnum,'net':net,'layer':'In2.Cu',
                    'area_mm2':round(area,3),'threshold_mm2':645.0,
                    'passes':area>=645.0,
                    'connected_vias':sum(1 for v in via_records if v['net']==net and 'In2.Cu' in v['filled_zone_layers_at_center'])})

q2=fp_by_ref['Q2']; u6=fp_by_ref['U6']
q2_gate=pick_pad('Q2','4','/ISO_GATE')
u6_gate=pick_pad('U6','6','/ISO_GATE')
gate_center=math.hypot(q2_gate['x_mm']-u6_gate['x_mm'],q2_gate['y_mm']-u6_gate['y_mm'])
q2_pos=q2.GetPosition()
q2_angle=q2.GetOrientationDegrees()
vsafe_shapes=zone_shapes.get(('/VSAFE','In2.Cu'),[])
vsafe_vertices=[pt for sh in vsafe_shapes for pt in sh['outer']]
vsafe_bbox=[min(p[0] for p in vsafe_vertices),min(p[1] for p in vsafe_vertices),max(p[0] for p in vsafe_vertices),max(p[1] for p in vsafe_vertices)] if vsafe_vertices else []
vsafe_pads=[]
seen=set()
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname()!='/VSAFE': continue
        pos=p.GetPosition(); x=pos.x/1e6; y=pos.y/1e6
        key=(fp.GetReference(),p.GetNumber(),round(x,5),round(y,5))
        if key in seen: continue
        seen.add(key)
        vsafe_pads.append({'ref':fp.GetReference(),'pad':p.GetNumber(),'x_mm':round(x,5),'y_mm':round(y,5),
                           'center_in_L3_zone':any(contains(s,x,y) for s in vsafe_shapes)})

# Compare invariants with main's board source, without importing Builder result files.
main_text=subprocess.run(['git','show','origin/main:PDU.kicad_pcb'],capture_output=True,text=True,encoding='utf-8',check=True).stdout
main_expr=top(parse(main_text))
main_fp=board_footprints(main_expr); review_fp=board_footprints(board_expr)
def named_node(expr,head):
    n=one(expr,head); return dumps(n) if n else None
edge_heads={'gr_line','gr_arc','gr_circle','gr_rect','gr_poly','dimension','target'}
def edge_items(expr):
    out=[]
    for n in kids(expr):
        if n.head not in edge_heads: continue
        if vals(n,'layer')==['Edge.Cuts']: out.append(dumps(n))
    return sorted(out)
moved=[]; changed_fp=[]
for ref in sorted(set(main_fp)|set(review_fp)):
    a=main_fp.get(ref); c=review_fp.get(ref)
    if a!=c:
        if a and c and a['lib']==c['lib'] and a['value']==c['value'] and a['padnets']==c['padnets'] and a['layer']==c['layer']:
            moved.append({'ref':ref,'main_at':a['at'],'review_at':c['at']})
        else: changed_fp.append(ref)
net_names=sorted({value_from_net(n) for n in walk(board_expr) if n.head=='net' and len(n.atoms())>1})
main_nets=sorted({value_from_net(n) for n in walk(main_expr) if n.head=='net' and len(n.atoms())>1})
stack=one(one(board_expr,'setup'),'stackup') if one(board_expr,'setup') else None
main_setup=one(main_expr,'setup'); main_stack=one(main_setup,'stackup') if main_setup else None
net_settings=one(board_expr,'net_settings'); main_net_settings=one(main_expr,'net_settings')
board_invariants={
 'edge_cuts_equal':edge_items(board_expr)==edge_items(main_expr),
 'edge_cut_item_count':len(edge_items(board_expr)),
 'footprint_ref_set_equal':set(main_fp)==set(review_fp),
 'footprint_definition_padnets_changes':changed_fp,
 'footprint_moved_refs':moved,
 'mechanical_and_connector_positions_equal':all(main_fp.get(r)==review_fp.get(r) for r in ('H1','H2','H3','H4','J1','J2','J3','J_OVP_INJ_BUS')),
 'net_name_set_equal':main_nets==net_names,
 'net_name_count_main':len(main_nets),'net_name_count_review':len(net_names),
 'copper_layer_count':b.GetCopperLayerCount(),
 'layer_table_equal':named_node(board_expr,'layers')==named_node(main_expr,'layers'),
 'stackup_equal':(dumps(stack) if stack else None)==(dumps(main_stack) if main_stack else None),
 'net_settings_equal':(dumps(net_settings) if net_settings else None)==(dumps(main_net_settings) if main_net_settings else None)
}
# CLI result generated independently above.
drc=json.loads((OUT/'pcb-drc-parity-refill.json').read_text(encoding='utf-8-sig'))
result={
 'reviewed_commit':commit,
 'board':'PDU.kicad_pcb',
 'method':'KiCad S-expression filled_polygon shoelace area in mm^2; point-in-polygon via center checks; pcbnew pad centers/sizes; source board and origin/main comparison',
 'drc':{'kicad_version':drc.get('kicad_version'),'violations':len(drc.get('violations',[])),
        'unconnected_items':len(drc.get('unconnected_items',[])),
        'schematic_parity':drc.get('schematic_parity')},
 'zone_count':len(zone_records),'zones':zone_records,
 'one_island_L2_GND':len(l2g)==1 and l2g[0]['filled_polygon_count']==1 and l2g[0]['island_marker_count']==0,
 'one_island_L4_GND':len(l4g)==1 and l4g[0]['filled_polygon_count']==1 and l4g[0]['island_marker_count']==0,
 'zone_via_center_connections':via_conn_summary,
 'vias':via_records,
 'pad_via_checks':pad_via_results,
 'thermal_regions':thermal,
 'q2_u6_gate':{'Q2_orientation_deg':q2_angle,'Q2_gate':q2_gate,'U6_gate':u6_gate,
               'center_distance_mm':round(gate_center,4),'edge_clear_distance_rectangular_mm':round(math.hypot(max(0,abs(q2_gate['x_mm']-u6_gate['x_mm'])-(q2_gate['width_mm']+u6_gate['width_mm'])/2),max(0,abs(q2_gate['y_mm']-u6_gate['y_mm'])-(q2_gate['height_mm']+u6_gate['height_mm'])/2)),4),
               'straight_center_distance_le_10mm':gate_center<=10},
 'L3_VSAFE':{'fill_polygon_count':len(vsafe_shapes),'area_mm2':round(sum(s['area_mm2'] for s in vsafe_shapes),3),
             'bbox_mm':[round(x,3) for x in vsafe_bbox],'pads':vsafe_pads},
 'main_invariants':board_invariants
}
(OUT/'independent-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(OUT/'via-audit.json').write_text(json.dumps(via_records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('vias','zones')},indent=2,ensure_ascii=False))
