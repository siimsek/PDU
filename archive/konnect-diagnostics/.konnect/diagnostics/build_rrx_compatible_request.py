"""Derive prototype land geometry from TI's exported package drawing.

Writes MCP request JSON/evidence only. Never reads/writes KiCad source.
Run extract_rrx_lands.py first. Rounded/diagonal edges are bounded rectangular
approximations because Konnect 0.13 cannot place custom-shaped pads.
"""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
polys=json.loads((HERE/'rrx-copper-polygons.json').read_text())[:2]
# PDF points per nominal millimetre from the drawing's 15:1 scale.
S=15*72/25.4
X0=174.175+3.2*S
Y0=167.706+3.2*S
nominal=[Polygon([((x-X0)/S,(y-Y0)/S) for x,y in poly]) for poly in polys]
pads=[]
def pad(n,x,y,w,h,layers,shape='rect',r=0):
    pads.append(dict(number=str(n),type='smd',shape=shape,x=round(x,6),y=round(y,6),width=round(w,6),height=round(h,6),layers=layers,roundrect_rratio=r))
CU=['F.Cu','F.Mask']
ALL=['F.Cu','F.Mask','F.Paste']
PASTE=['F.Paste']
metrics=[]
for num,poly in zip([29,22],nominal):
    # Scan strips 0.005 mm high; merge equal-width consecutive strips.
    lo,hi=poly.bounds[1],poly.bounds[3]
    ys=[lo+i*.005 for i in range(math.ceil((hi-lo)/.005))]+[hi]
    strips=[]
    for a,b in zip(ys,ys[1:]):
        cut=poly.intersection(box(-10,a,10,b))
        if cut.is_empty: continue
        for part in (list(cut.geoms) if hasattr(cut,'geoms') else [cut]):
            if part.area<1e-10:continue
            x1,_,x2,_=part.bounds
            # Outward rounding <=1 um; strip boundary approximation <5 um.
            x1=math.floor(x1*1000)/1000;x2=math.ceil(x2*1000)/1000
            prior=next((i for i,s in enumerate(strips) if s[0]==x1 and s[2]==x2 and abs(s[3]-a)<1e-8),None)
            if prior is not None:strips[prior]=(x1,strips[prior][1],x2,b)
            else:strips.append((x1,a,x2,b))
    pieces=[]
    for x1,a,x2,b in strips:
        # 0.002 mm common overlap avoids line-only connectivity at strip seams.
        a=max(lo,a-.001);b=min(hi,b+.001)
        pad(num,(x1+x2)/2,(a+b)/2,x2-x1,b-a,CU)
        pieces.append(box(x1,a,x2,b))
    union=unary_union(pieces)
    metric=dict(number=num,pieces=len(pieces),bounds=list(poly.bounds),target_area_mm2=poly.area,represented_area_mm2=union.area,hausdorff_mm=poly.hausdorff_distance(union),symmetric_difference_mm2=poly.symmetric_difference(union).area)
    assert metric['hausdorff_mm']<.007,metric
    metrics.append(metric)

contacts={}
for n,y in enumerate([-2.25,-1.75,-1.25,-.25,.25,1.25,1.75,2.25],1):contacts[n]=(-2.9,y,.6,.25)
for n,x in enumerate([-2,-1.5,-1,0,.5,1,1.5,2],9):contacts[n]=(x,2.9,.25,.6)
for n,y in enumerate([1.75,1.25,.75,-.75,-1.25,-1.75],17):contacts[n]=(2.9,y,.6,.25)
for n,x in enumerate([2,1.5,1,.5,-1,-1.5,-2],23):contacts[n]=(x,-2.9,.25,.6)
for n,(x,y,w,h) in contacts.items():
    layers=CU if n in [1,2,20,21,22,27,28,29] else ALL
    pad(n,x,y,w,h,layers,'roundrect',.05/min(w,h))
pad(30,.037,1.308,3.125,1.584,CU,'roundrect',.05/1.584)
# Manufacturer split stencil for shared VIN/SW lands and PGND die-attach pad.
for n in [1,2]:pad('',-3.066,contacts[n][1],.267,.25,PASTE,'roundrect',.05/.25)
for n in [27,28,29]:pad('',contacts[n][0],-3.071,.25,.258,PASTE,'roundrect',.05/.25)
for n in [20,21,22]:pad('',3.054,contacts[n][1],.293,.25,PASTE,'roundrect',.05/.25)
for x,y,w,h in [(-2.573,-2.192,.32,.9),(-1.463,-2.242,1.5,1),(-1.463,-1.042,1.5,1),(.602,-1.095,1.27,1.75),(2.072,-1.095,1.27,1.75),(-.738,1.308,1.42,1.42),(.812,1.308,1.42,1.42)]:pad('',x,y,w,h,PASTE,'roundrect',.05/min(w,h))
# A 0.3 mm chamfer is required on the lower-left VIN paste aperture.
# Keep this prototype stencil conservatively inside the recommended chamfer:
# use 0.3-mm narrower lower aperture until production stencil is qualified.
lower=[p for p in pads if p['layers']==PASTE and p['x']==-1.463 and p['y']==-1.042][0]
lower['width']=1.2;lower['x']=-1.313

name='LM70880_RRX0029B_RectLands'
args=dict(name=name,output=str(ROOT/'hardware/lib/PDU.pretty'/f'{name}.kicad_mod'),body_width=6,body_height=6,courtyard_clearance=.25,package_type='smd',description='TI LM70880QRRXRQ1 RRX0029B 4228757/D 04/2024. Prototype compatible rectangular land decomposition <7um boundary deviation. VIN29/SW22 repeated pads are intentional common copper. Production stencil/thermal-via qualification pending.',pads=pads)
(HERE/'rrx-create-calls.json').write_text(json.dumps([dict(name='create_footprint',arguments=args)]),encoding='utf-8')
(ROOT/'hardware/validation/power-ics/rrx-geometry-evidence.json').write_text(json.dumps(dict(metrics=metrics,contacts=contacts,pad_object_count=len(pads),notes='Prototype copper representation; lower-left VIN paste aperture intentionally narrowed within recommended chamfer. Stencil review pending.'),indent=2),encoding='utf-8')
print(json.dumps(dict(pad_objects=len(pads),metrics=metrics),indent=2))
