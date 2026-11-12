import json,sys,math
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from shapely import Polygon
from scripts.studio.shape import shape_data,phase
from scripts.studio.model import read,write
out=Path('evidence/studio-attachment');out.mkdir(exist_ok=True)
def data(scene,name): return shape_data(next(n for n in scene['nodes'] if n['id']==name),scene['canvas'])
def point(d,side): return min(d.boundary,key=lambda row:abs((row[0]-phase(side,.5)+2)%4-2))[1]
results={}
for label,path,parent,pside,child,cside in [('lamp-elbow','evidence/studio-shape/usability/lamp-book.json','lamp-stem','top','lamp-arm','bottom'),('rocket-cap','evidence/studio-parameters/usability/rocket.json','body','top','nose','bottom')]:
    scene=read(path);a=data(scene,parent);b=data(scene,child)
    ap=point(a,pside);bp=point(b,cside)
    results[label]=dict(parent_anchor=ap,child_anchor=bp,distance_pixels=math.dist(ap,bp),paint_footprints_overlap_area=Polygon(a.outline).intersection(Polygon(b.outline)).area,meaning='overlap exists; appearance critique is not proof of a detached geometric joint')
scene=read('examples/studio/coast.json');foot=data(scene,'tower-foot');top=data(scene,'rock-top')
results['cliff-contact']=dict(footprint_overlap_area=Polygon(foot.outline).intersection(Polygon(top.outline)).area,footing_area=Polygon(foot.outline).area,meaning='footing is already on the top patch; flatness/contact-cue critique does not establish a placement gap')
write(out/'prior-joint-facts.json',results)
print(json.dumps(results,indent=2))
