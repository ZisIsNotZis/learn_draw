"""Root-authored relational draft: existing primitives, no reference or pixel generation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import validate,write
from scripts.studio.render import bundle
nodes=[]
def part(id,kind,intent,depth,**kw):
    n=dict(id=id,kind=kind,intent=intent,depth=depth,**kw);nodes.append(n);return n
def pin(to,own='center',target='center',**kw):return dict(to=to,self=own,target=target,**kw)
def mass(id,intent,depth,fill,**kw):return part(id,'shape',intent,depth,palette=dict(fill=fill,ink='#493f3b'),stroke=0,**kw)
def mark(id,intent,depth,fill,**kw):return part(id,'stroke',intent,depth,palette=dict(fill=fill),**kw)
mass('window-frame','warm wooden frame behind the tending figure',-30,'#b99a79',length=.68,width=1.12,rounding=.15,at=dict(anchor='center',offset=[.17,-.12]))
mass('window-glass','quiet pale daylight within the wooden frame',-29,'#c8e0dc',length=.63,width=1.12,rounding=.12,attachment=pin('window-frame'))
mass('window-upright','one upright divides the daylight panes',-28,'#b99a79',length=.63,width=.025,rounding=.1,attachment=pin('window-frame'))
mass('window-crossbar','one crossbar divides the quiet panes',-27,'#b99a79',length=.025,width=6,rounding=.1,attachment=pin('window-frame'))
mass('sill','a broad wooden sill supports the plant',-20,'#967960',length=.035,width=21,rounding=.15,attachment=pin('window-frame','top','bottom'))
part('gardener','head','a gentle blue-haired gardener looks toward the plant',20,length=.25,angle=-6,gaze=.65,expression='gentle',at=dict(anchor='center',offset=[-.23,-.16]))
mark('neck','short skin bridge from chin into the shirt',15,'#e7bda3',length=.035,thickness=.035,attachment=pin('gardener','root','chin',inset=.025))
mass('shirt','soft coral shirt cropped below the waist',5,'#c8846c',length=.47,width=.73,rounding=.62,taper=-.22,attachment=pin('neck','top','tip'))
mark('resting-sleeve','the relaxed sleeve descends out of the crop',6,'#c8846c',length=.45,thickness=.08,start_width=1.1,angle=-9,bend=.02,attachment=pin('shirt','root','left@.92',inset=.06))
mark('reaching-sleeve','one sleeve reaches right toward the watering can',8,'#c8846c',length=.23,thickness=.07,start_width=1.15,end_width=.8,angle=89,bend=-.14,attachment=pin('shirt','root','right@.09',inset=.05))
part('grip','hand','the existing open hand is a first grip hypothesis, not a claimed grip rig',30,length=.105,angle=-90,spread=.8,attachment=pin('reaching-sleeve','wrist','tip'))
mass('can-body','a golden watering vessel hangs below the hand',10,'#cfad54',length=.15,width=1.18,rounding=.35,taper=.16,angle=10,attachment=pin('grip','top','center',offset=[0,.05]))
mark('can-handle','a narrow arched handle rises to the carrying hand',11,'#b18d3f',length=.12,thickness=.014,bend=.42,angle=90,attachment=pin('can-body','root','top',offset=[-.06,0]))
mark('spout','a long tapered spout points above the plant',12,'#cfad54',length=.16,thickness=.032,start_width=1.25,end_width=.7,angle=58,attachment=pin('can-body','root','right@.3',inset=.08))
mark('water','a thin blue stream should land in the pot',13,'#669ca8',length=.16,thickness=.007,bend=.1,angle=25,attachment=pin('spout','root','tip'))
mass('plant-pot','a blue planter rests on the right end of the sill',3,'#467e88',length=.13,width=1.4,rounding=.4,taper=-.28,attachment=pin('sill','bottom','top@.83'))
mark('plant-stem','one upright stem emerges from the planter',0,'#426f50',length=.24,thickness=.012,angle=180,bend=-.025,attachment=pin('plant-pot','root','top',inset=.16))
for i,(side,height,angle) in enumerate([('left',.05,-35),('right',.09,38),('left',.15,-42),('right',.19,44)]):
    mass('leaf-'+str(i+1),'a broad '+side+' leaf opens from the stem',1+i*.1,'#5a8760',profile='oval',length=.11,width=.43,angle=angle,attachment=pin('plant-stem','bottom','root',offset=[0,-height]))
s=dict(format='learn-draw/studio-1',canvas=[960,720],background='#f6ecdf',nodes=nodes)
validate(s);write('evidence/studio-watering/working.json',s);bundle(s,'evidence/studio-watering/01-first')
print('first draft',len(nodes),'semantic parts')
