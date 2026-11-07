import pymupdf
from collections import Counter
from shapely.geometry import LineString
from shapely.ops import polygonize,unary_union
p=pymupdf.open('hardware/_datasheets/lm70880-q1.pdf')[51]
gs=[d for d in p.get_drawings() if d.get('color') and d['color'][1]>.9 and d['color'][0]<.5]
print(Counter(i[0] for d in gs for i in d['items']))
lines=[]
for d in gs:
 for item in d['items']:
  if item[0]=='l':
   pts=[tuple(item[j]) for j in [1,2]]
  elif item[0]=='c':
   a,b,c,e=item[1:];pts=[]
   for j in range(17):
    t=j/16;u=1-t;pts.append((u**3*a.x+3*u*u*t*b.x+3*u*t*t*c.x+t**3*e.x,u**3*a.y+3*u*u*t*b.y+3*u*t*t*c.y+t**3*e.y))
  else:print('unknown',item);continue
  lines.append(LineString([(round(x,3),round(y,3)) for x,y in pts]))
polys=list(polygonize(unary_union(lines)))
print([(round(p.area,2),p.bounds) for p in polys])
from shapely.ops import snap
u=unary_union(lines)
pts=[c for l in lines for c in [l.coords[0],l.coords[-1]]]
reps=[]
for q in pts:
 if not any((q[0]-r[0])**2+(q[1]-r[1])**2<.01**2 for r in reps):reps.append(q)
def nearest(q):return min(reps,key=lambda r:(r[0]-q[0])**2+(r[1]-q[1])**2)
ls=[LineString([nearest(l.coords[0]),*list(l.coords)[1:-1],nearest(l.coords[-1])]) for l in lines]
polys=list(polygonize(unary_union(ls)))
print('snapped polygons',[(round(p.area,2),p.bounds) for p in polys])
import json
from pathlib import Path
Path('.konnect/diagnostics/rrx-copper-polygons.json').write_text(json.dumps([list(p.exterior.coords) for p in polys if p.area>1000]))
