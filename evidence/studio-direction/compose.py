"""Original person-with-flower composition: named relations and a computed petal ring.
No image, traced vertices or mesh input. Initial structured authoring, not a public-CLI
creation claim; subsequent observed corrections use public operations.
"""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import validate,write
HERE=Path(__file__).resolve().parent

def compose(petal_layers=True):
 skin='#efd0b5';cloth='#6c8d98';ink='#445b63';green='#668367';grip_length=.125
 wrist=.44*grip_length/1.02;rod=.08*grip_length/1.02
 def attach(to,own='center',target='center',**kw):return dict(to=to,self=own,target=target,**kw)
 nodes=[
  dict(id='head',kind='head',intent='a gentle young person looks toward the flower at the right',length=.23,angle=-4,hair='side-part',expression='gentle',gaze=1,eye_scale=.87,depth=7,at=dict(anchor='center',offset=[-.20,-.27]),palette=dict(hair='#4c5965',skin=skin,iris='#7c6f53',ink='#4a4448')),
  dict(id='neck',kind='stroke',intent='a short neck joins chin to shirt beneath the head',length=.043,thickness=.055,angle=0,depth=2,attachment=attach('head','root','chin'),palette=dict(fill=skin)),
  dict(id='shirt',kind='shape',intent='a soft blue shirt reaches the foreground table',length=.40,width=.73,rounding=.40,taper=-.12,stroke=.006,depth=4,attachment=attach('neck','top','tip'),palette=dict(fill=cloth,ink=ink)),
  dict(id='resting-arm',kind='stroke',intent='the far sleeve falls beside the body and disappears behind the table',length=.34,thickness=.085,angle=-10,start_width=1.0,end_width=.85,start_cap='round',end_cap='flat',ink_width=.0025,depth=3,attachment=attach('shirt','root','left@.23',inset=.08),palette=dict(fill=cloth,ink=ink)),
  dict(id='flower-hand',kind='grip',intent='a small illustrated fist holds the green flower stem',length=grip_length,angle=-50,depth=8,at=dict(anchor='center',offset=[.13,-.03]),palette=dict(skin=skin,ink='#946d59',handle=green,handle_ink=green)),
  dict(id='reaching-sleeve',kind='stroke',intent='a forearm reaches out to the flower hand, leaving the wrist direction to be corrected visibly',thickness=wrist,start_width=1.55,end_width=1,start_cap='round',end_cap='flat',ink_width=.0025,bend=0,depth=3.5,endpoints=dict(root=dict(to='shirt',target='right@.27',inset=.03),tip=dict(to='flower-hand',target='wrist')),palette=dict(fill=cloth,ink=ink)),
  dict(id='upper-stem',kind='stroke',intent='the stem continues upward from the held segment to the blossom',length=.155,thickness=rod,angle=-140,depth=6,attachment=attach('flower-hand','root','handle_left'),palette=dict(fill=green)),
  dict(id='lower-stem',kind='stroke',intent='a short free stem end continues below the gripping hand',length=.06,thickness=rod,angle=40,depth=6,attachment=attach('flower-hand','root','handle_right'),palette=dict(fill=green)),
  dict(id='flower-heart',kind='shape',intent='a warm golden center joins the five pale petals',profile='oval',length=.039,width=1,stroke=.012,depth=10,attachment=attach('upper-stem','center','tip'),palette=dict(fill='#d4a34e',ink='#ae823e')),
 ]
 for i in range(5):
  angle=i*math.tau/5+math.pi/5
  nodes.append(dict(id='petal-'+str(i+1),kind='shape',intent='rounded daisy petal radiates from the actual blossom center',profile='oval',length=.067,width=.53,angle=((math.degrees(angle)+180)%360)-180,stroke=.018,depth=(9+i*.05 if petal_layers else 9),
      attachment=attach('flower-heart',offset=[math.sin(angle)*.030,math.cos(angle)*.030]),palette=dict(fill='#fff7df',ink='#baa58b')))
 nodes.extend([
  dict(id='stem-leaf',kind='shape',intent='one small leaf grows from the upper stem',profile='oval',length=.060,width=.42,angle=-75,stroke=0,depth=6.5,attachment=attach('upper-stem','bottom','center'),palette=dict(fill=green)),
  dict(id='table-front',kind='shape',intent='the foreground table continues out of frame and hides the lower body',length=.25,width=6,rounding=0,stroke=0,depth=20,attachment=attach('table-top','top','center',offset=[0,-.025/2]),palette=dict(fill='#d9c7aa')),
  dict(id='table-top',kind='stroke',intent='a quiet horizontal table edge grounds the person',length=1.3,thickness=.025,angle=90,start_cap='flat',end_cap='flat',depth=21,at=dict(anchor='center',offset=[-.52,.28]),palette=dict(fill='#9a8066')),
 ])
 return validate(dict(format='learn-draw/studio-1',canvas=[800,640],background='#f3ead9',nodes=nodes))
if __name__=='__main__':
 p=HERE/'working.json'
 if p.exists():raise SystemExit('preserve the current study; use a fresh location for replay')
 scene=compose();write(HERE/'initial-working.json',scene);write(p,scene)
 print('Original semantic context:',len(scene['nodes']),'nodes')
