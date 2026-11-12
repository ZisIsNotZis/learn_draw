import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import write
from scripts.studio.render import bundle
nodes=[]
def mass(name,intent,x,y,h,aspect,fill,**optional):
    nodes.append(dict(id=name,kind='shape',intent=intent,at=dict(anchor='center',offset=[x-.5,y-.5]),length=h,width=aspect,palette=dict(fill=fill,ink='#344b57'),depth=len(nodes),stroke=0,**optional))
nodes.append(dict(id='evening-sky',kind='sky',intent='warm late-afternoon sky',style='day',stars=0,depth=-20,palette=dict(top='#9ebbc0',bottom='#f7dfb9')))
nodes.append(dict(id='low-sun',kind='sun',intent='a quiet pale sun balances the tower',length=.16,at=dict(anchor='upper_left',offset=[.01,.16]),rays=0,depth=-10,palette=dict(fill='#f9e7bd')))
mass('distant-water','a calm blue horizon',.5,.85,.68,4,'#86a8ad',rounding=0)
mass('water-light','a lighter sweep toward the foreground',.25,1.04,.70,3.9,'#b3c8c6',profile='oval')
mass('far-island','a low distant headland below the sun',.14,.526,.036,5.8,'#739499',rounding=.92)
# Tower pieces share one named composition ruler; no per-contour coordinates.
tower_x=.70;base=.78;tower_h=.36;top=base-tower_h
mass('rock-platform','dark headland holding the tower',tower_x+.015,.96,.34,2.1,'#536b70',rounding=.35,taper=-.12,angle=-5)
mass('rock-light','sunward rock plane',tower_x-.10,.975,.27,.92,'#6f8580',rounding=.28,taper=-.35,angle=-13
)
mass('rock-top','the illuminated top plane supports the tower',tower_x+.01,.782,.135,3.65,'#929c8d',rounding=.88,angle=-5
)
mass('tower-foot','a pale footing visibly rests on the rock',tower_x,.788,.021,6,'#e0d5bf',rounding=.12)
mass('tower-body','ivory tower narrows toward the lantern',tower_x,(base+top)/2,tower_h,.34,'#f5e7ce',rounding=.08,taper=.32)
mass('tower-side','subordinate shadow plane on the tower right',tower_x+.023,(base+top)/2,tower_h,.09,'#d4cbb6',rounding=.08,taper=.32)
lantern_h=.085;lantern_y=top-lantern_h/2
mass('lantern-frame','dark frame holds the warm glass',tower_x,lantern_y,lantern_h,1.15,'#3f5c63',rounding=.15)
mass('lantern-glass','the lit pane is the focal warm note',tower_x,lantern_y,lantern_h*.69,1.12,'#f3cb7d',rounding=.12)
mass('lantern-mullion','a slim upright divides the glass',tower_x,lantern_y,lantern_h*.72,.1,'#3f5c63',rounding=0)
mass('balcony','one clear dark balcony shelf',tower_x,top+.006,.018,5.8,'#3f5c63',rounding=.1)
roof_h=.06
mass('roof','coral pitched roof crowns the lamp',tower_x,top-lantern_h-roof_h/2+.007,roof_h,2.15,'#ba6550',rounding=.03,taper=.96)
for i in range(2):
    mass('window-'+str(i+1),'a small dark tower opening',tower_x-.005,top+.09+i*.09,.026,.54,'#4e6d76',rounding=.72)
mass('door','a grounded doorway meets the rocky platform',tower_x,base-.028,.06,.36,'#4e6d76',rounding=.65)
mass('foreground-stone','a dark rounded stone breaks the near water',.17,.91,.06,2,'#6b8586',profile='oval',angle=9)
mass('water-ripple-a','a thin pale ripple identifies the open water',.29,.65,.17,.05,'#bfd0ca',profile='oval',angle=90)
mass('water-ripple-b','a second shorter ripple sits further out',.39,.60,.10,.05,'#aec4c1',profile='oval',angle=90)
mass('near-ripple','a short ripple separates the foreground stone from land',.27,.925,.14,.05,'#d1ddcf',profile='oval',angle=90)
scene=dict(format='learn-draw/studio-1',canvas=[960,640],background='#f7dfb9',nodes=nodes)
write('evidence/studio-shape/coast-refined/scene.json',scene)
bundle(scene,'evidence/studio-shape/coast-refined',png=True)
print('coast rendered',len(nodes),'named parts')
