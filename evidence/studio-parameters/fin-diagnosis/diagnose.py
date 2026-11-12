import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from collections import Counter
from io import BytesIO
from unittest.mock import patch
import numpy as np
from PIL import Image
import resvg_py
from shapely import Polygon,Point
from scripts.studio.model import read,write
from scripts.studio.components import component_outline
from scripts.studio.render import drawing,global_depth_order,rasterize
s=read('evidence/studio-parameters/usability/rocket.json');out=Path('evidence/studio-parameters/fin-diagnosis');out.mkdir(exist_ok=True)
fin=next(n for n in s['nodes'] if n['id']=='right-fin')
poly=Polygon(component_outline(fin,s['canvas']))
front=[Polygon(component_outline(n,s['canvas'])) for n in s['nodes'] if n.get('depth',0)>-1]
visible=poly
for p in front:visible=visible.difference(p)
visible=visible.buffer(-2)
raw=Image.open('evidence/studio-parameters/usability/final/artwork.png').convert('RGBA');pixels=np.asarray(raw)
colours=Counter();unexpected=[]
for y in range(raw.height):
    for x in range(raw.width):
        if visible.contains(Point(x+.5,y+.5)):
            colour=tuple(map(int,pixels[y,x]));colours[colour]+=1
            if colour!=(188,97,80,255): unexpected.append([x,y,list(colour)])
left=Polygon(component_outline(next(n for n in s['nodes'] if n['id']=='left-fin'),s['canvas']))
assert left.disjoint(poly)
with patch('scripts.studio.render.global_depth_order',lambda _:sorted(s['nodes'],key=lambda n:n.get('depth',0))):
    reference=drawing(s)
(out/'noncrossing-reference.svg').write_text(reference,encoding='utf-8');rasterize(out/'noncrossing-reference.svg',out/'noncrossing-reference.png')
ref=np.asarray(Image.open(out/'noncrossing-reference.png').convert('RGBA'))
cleared=sum(tuple(ref[y,x])==(188,97,80,255) for x,y,c in unexpected)
write(out/'facts.json',dict(original_fastpath=global_depth_order(s),fins_projected_disjoint=True,unexpected_deep_interior_pixels=len(unexpected),cleared_by_proved_noncrossing_draw=cleared,examples=unexpected[:20],colour_counts={str(k):v for k,v in colours.items()},method='pure-red fin visible region eroded 2 pixels; compare actual RGBA, no target image or aesthetic metric'))
print(json.dumps(read(out/'facts.json'),indent=2))
