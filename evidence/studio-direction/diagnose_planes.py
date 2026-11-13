"""Read-only diagnosis of intersecting equal-depth projections; never moves visibility cuts."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read
from scripts.studio.attachment import resolve_scene
from scripts.studio.components import component_outline,depth_bounds
from shapely import Polygon
s=resolve_scene(read(Path(__file__).with_name('working.json')));c=s['canvas'];rows=[]
for i,a in enumerate(s['nodes']):
 alo,ahi=depth_bounds(a,c);pa=Polygon(component_outline(a,c))
 for b in s['nodes'][i+1:]:
  blo,bhi=depth_bounds(b,c)
  if ahi<blo-1e-7 or bhi<alo-1e-7:continue
  overlap=pa.intersection(Polygon(component_outline(b,c)))
  if not overlap.is_empty:rows.append(dict(a=a['id'],b=b['id'],depths=[alo,ahi,blo,bhi],area=overlap.area))
text=json.dumps(rows,indent=2)
if len(sys.argv)>1:
 p=Path(sys.argv[1])
 if p.exists():raise SystemExit('diagnostic output exists')
 p.write_text(text+'\n',encoding='utf8')
print(text)
