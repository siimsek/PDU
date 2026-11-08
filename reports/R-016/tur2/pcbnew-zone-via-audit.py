import json, math
from pathlib import Path
import pcbnew

OUT = Path('reports/R-016/tur2')
BOARD = Path('PDU.kicad_pcb')
b = pcbnew.LoadBoard(str(BOARD))
IU = 1_000_000
LAYER_IDS = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)


def mm(iu): return iu / IU
def bbox(item):
    r = item.GetBoundingBox()
    return [mm(r.GetX()), mm(r.GetY()), mm(r.GetX()+r.GetWidth()), mm(r.GetY()+r.GetHeight())]
def point_inside(pt, poly):
    x, y = pt; inside = False
    for (x1,y1),(x2,y2) in zip(poly, poly[1:]+poly[:1]):
        if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1) + x1):
            inside = not inside
    return inside
def zone_outline(z):
    if not z.IsFilled() or not z.HasFilledPolysForLayer(z.GetLayer()): return None
    ps = z.GetFilledPolysList(z.GetLayer())
    if ps.OutlineCount() != 1: return {'outlines':ps.OutlineCount(),'holes':sum(ps.HoleCount(i) for i in range(ps.OutlineCount())),'points':[]}
    o = ps.Outline(0)
    return {'outlines':1,'holes':ps.HoleCount(0),'points':[(mm(o.CPoint(i).x),mm(o.CPoint(i).y)) for i in range(o.PointCount())]}
def spans_at_y(poly, y):
    xs=[]
    for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
        if (y1<=y<y2) or (y2<=y<y1): xs.append(x1+(y-y1)*(x2-x1)/(y2-y1))
    xs.sort()
    return [[round(xs[i],3),round(xs[i+1],3),round(xs[i+1]-xs[i],3)] for i in range(0,len(xs)-1,2)]

zones=[]; zone_polys={}
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    lay=pcbnew.LayerName(z.GetLayer()); bb=bbox(z); outline=zone_outline(z)
    poly = outline['points'] if outline and len(outline.get('points',[])) else []
    row={'name':z.GetZoneName(),'net':z.GetNetname(),'layer':lay,'filled':z.IsFilled(),
         'filled_area_mm2':z.GetFilledArea()/1e12,'bbox_board_mm':bb,
         'outline_count':outline['outlines'] if outline else 0,'hole_count':outline['holes'] if outline else 0}
    if lay in ('In1.Cu','In2.Cu','B.Cu'): zone_polys[(z.GetNetname(),lay,z.GetZoneName())]=poly
    zones.append(row)

vias=[]
for v in b.GetTracks():
    if not isinstance(v,pcbnew.PCB_VIA): continue
    p=v.GetPosition(); pt=(mm(p.x),mm(p.y)); layer_set=v.GetLayerSet()
    connected=[]
    for (net,lay,name),poly in zone_polys.items():
        lid=next((l for l in LAYER_IDS if pcbnew.LayerName(l)==lay),None)
        if net==v.GetNetname() and lid is not None and layer_set.Contains(lid) and poly and point_inside(pt,poly): connected.append({'zone':name,'layer':lay,'net':net})
    vias.append({'x_mm':round(pt[0],6),'y_mm':round(pt[1],6),'net':v.GetNetname(),
                 'pad_mm':mm(v.GetWidth(pcbnew.F_Cu)),'drill_mm':mm(v.GetDrillValue()),
                 'layers':[pcbnew.LayerName(l) for l in LAYER_IDS if layer_set.Contains(l)],
                 'connects_to_filled_same_net_zones':connected})

fps={f.GetReference():f for f in b.GetFootprints()}
def matching_vias(pad):
    x1,y1,x2,y2=bbox(pad)
    return [v for v in vias if v['net']==pad.GetNetname() and x1-1e-6<=v['x_mm']<=x2+1e-6 and y1-1e-6<=v['y_mm']<=y2+1e-6]
def find_pad(ref,num,net=None,largest=False):
    ps=[p for p in fps[ref].Pads() if p.GetNumber()==str(num) and (net is None or p.GetNetname()==net)]
    return max(ps,key=lambda p:p.GetSize().x*p.GetSize().y) if largest else (ps[0] if ps else None)

pad_via_summary={}
for ref,num,net,label,largest in [
    ('U1','30','/GND','U1.30 EP',True),('U2','30','/GND','U2.30 EP',True),
    ('Q1','5','/VIN','Q1.5 drain',True),('Q2','5','/VOUT','Q2.5 drain',True)]:
    p=find_pad(ref,num,net,largest)
    pad_via_summary[label]={'pad_bbox_board_mm':bbox(p),'count':len(matching_vias(p)),
        'via_centers_mm':[[v['x_mm'],v['y_mm']] for v in matching_vias(p)],
        'zone_connections':[{k:v[k] for k in ('x_mm','y_mm','connects_to_filled_same_net_zones')} for v in matching_vias(p)]}
for n in ('1','2','3'):
    p=find_pad('Q2',n,'/VSAFE')
    pad_via_summary[f'Q2.{n} source']={'pad_bbox_board_mm':bbox(p),'count':len(matching_vias(p)),
        'via_centers_mm':[[v['x_mm'],v['y_mm']] for v in matching_vias(p)],
        'zone_connections':[{k:v[k] for k in ('x_mm','y_mm','connects_to_filled_same_net_zones')} for v in matching_vias(p)]}

# Thermal copper area uses each distinct connected same-net zone exactly once; no cross-net/layer summation.
zone_by_name={z['name']:z for z in zones}
thermal=[]
for ref,zname,net in [('Q1','L3_VIN','/VIN'),('Q2 drain','L3_VOUT','/VOUT'),('Q2 source','L3_VSAFE','/VSAFE')]:
    area=zone_by_name[zname]['filled_area_mm2']
    thermal.append({'component':ref,'net':net,'layer':'In2.Cu','zone':zname,'filled_area_mm2':area,
                    'target_mm2':645.16,'ratio_to_target':area/645.16,'shared_net_pour':True})

vsafe=zone_by_name['L3_VSAFE']
vsafe_poly=zone_polys[('/VSAFE','In2.Cu','L3_VSAFE')]
rows=[]
for y_d006 in (56.7,57.2,60.0,70.0,76.5):
    y_board=115-y_d006
    spans=[{'x_d006_mm':[round(a-30,3),round(b-30,3)],'width_mm':w} for a,b,w in spans_at_y(vsafe_poly,y_board)]
    rows.append({'y_d006_mm':y_d006,'y_board_mm':y_board,'spans':spans})

tracks=[x for x in b.GetTracks() if isinstance(x,pcbnew.PCB_TRACK) and not isinstance(x,pcbnew.PCB_VIA)]
result={'method':'KiCad pcbnew 10.0.7 read-only Board load; filled polygon vertices, areas and pad/via geometry; no board save',
        'board':'PDU.kicad_pcb','footprint_count':len(fps),'routed_track_count':len(tracks),
        'zones':zones,'via_count':len(vias),'via_net_counts':{n:sum(v['net']==n for v in vias) for n in sorted({v['net'] for v in vias})},
        'vias':vias,'pad_via_summary':pad_via_summary,'thermal_copper':thermal,
        'l3_vsafe_d006_scanlines':rows,
        'l3_vout_right_boundary_d006_x_mm':zone_by_name['L3_VOUT']['bbox_board_mm'][2]-30,
        'l3_vsafe_bbox_d006_mm':[vsafe['bbox_board_mm'][0]-30,115-vsafe['bbox_board_mm'][3],vsafe['bbox_board_mm'][2]-30,115-vsafe['bbox_board_mm'][1]]}
(OUT/'pcbnew-zone-via-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k=='zones' or k=='via_net_counts' or k=='pad_via_summary' or k=='thermal_copper' or k.startswith('l3_') or k in ('via_count','routed_track_count')},indent=2,ensure_ascii=False))
