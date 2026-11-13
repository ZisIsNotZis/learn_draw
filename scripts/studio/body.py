"""Owned graphic upper body: cloth continuity, semantic joints and independently visible planes."""
from types import SimpleNamespace
import math
import numpy as np
from shapely import Polygon,LineString,union_all
from .grip import polygon_path,line_path
from .geometry import path,xml_comment,bounds,resolve_root
from functools import lru_cache
import json
from .sleeve import arm_data

def bezier(a,b,c,d,n=28):
 a,b,c,d=map(np.array,(a,b,c,d))
 return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in np.linspace(0,1,n,endpoint=False)]

def _construct(node,canvas):
 host=SimpleNamespace(center=resolve_root(dict(node,at=node.get('at',{'anchor':'center'})),canvas),angle=0)
 h=node.get('length',.4)*min(canvas);w=h*node.get('width',.9);wrist_width=node.get('sleeve_width',.14)*node.get('length',.4)
 stroke=node.get('stroke',.006)*h;origin=np.array([host.center[0],host.center[1]-h/2-stroke/2])
 neck=w*.18;drop=h*.11;collar=h*.045
 nl=(-neck/2,0);sl=(-w*.41,h*.34);hl=(-w*.40,h);hr=(w*.40,h);sr=(w*.41,h*.34);nr=(neck/2,0)
 points=bezier(nl,(-neck/2-w*.08,h*.10),(-w*.41,h*.20),sl)
 points+=bezier(sl,(-w*.45,h*.55),(-w*.41,h*.80),hl)
 points+=[hl,hr]
 points+=bezier(hr,(w*.41,h*.80),(w*.45,h*.55),sr)
 points+=bezier(sr,(w*.41,h*.20),(neck/2+w*.08,h*.10),nr)
 points+=bezier(nr,(neck/2*.55,collar*1.33),(-neck/2*.55,collar*1.33),nl)
 body=Polygon([tuple(origin+np.array(p)) for p in points])
 if not body.is_valid:raise ValueError('torso contour invalid')
 joints={};arms=[];arm_data_by_side={}
 for side in ('left','right'):
  shoulder_radius=wrist_width*min(canvas)*1.55/2
  p=origin+np.array([(-1 if side=='left' else 1)*(w/2-shoulder_radius),drop+shoulder_radius])
  config=arm_configuration(node,side)
  q=origin+np.array([w*config['wrist_spread'],h*config['wrist_height']])
  delta=q-p;length=float(np.linalg.norm(delta));angle=math.degrees(math.atan2(delta[0],delta[1]))
  arm=dict(id=node['id']+'-'+side,kind='stroke',intent=side+' owned sleeve',length=length/min(canvas),thickness=wrist_width,
      start_width=1.55,end_width=1,angle=angle,start_cap='flat',ink_width=0,at=dict(anchor='center',offset=[p[0]/canvas[0]-.5,p[1]/canvas[1]-.5]),palette=node.get('palette',{}))
  data=arm_data(arm,canvas,elbow_at=config['elbow_at'],elbow_bend=config['elbow_bend'],rounding=2)
  arms.append(data.material);joints[side]=data.joints;arm_data_by_side[side]=data
 bridges=[]
 for side,data in arm_data_by_side.items():
  rows=data.rows;index=0;outer=[r.left if side=='left' else r.right for r in rows];inner=[r.right if side=='left' else r.left for r in rows]
  a=origin+np.array([(-1 if side=='left' else 1)*neck/2,0]);b=np.array(outer[index])
  tangent=np.array(outer[index+1])-np.array(outer[max(0,index-1)]);tangent/=np.linalg.norm(tangent);distance=float(np.linalg.norm(b-a))
  first=a+np.array([(-1 if side=='left' else 1)*distance*.30,0]);last=b-tangent*distance*.25
  edge=bezier(a,first,last,b,n=40)
  patch=Polygon([*edge,tuple(b),inner[index],tuple(origin+np.array([0,h*.30]))])
  if not patch.is_valid:raise ValueError('shoulder pattern bridge invalid')
  bridges.append(patch)
 body=union_all([body,*bridges])
 cloth=union_all([body,*arms])
 # Sewn cloth has rounded inner junctions, rather than mathematical needle armpits.
 seam_radius=wrist_width*min(canvas)*.12
 cloth=cloth.buffer(seam_radius,join_style='round').buffer(-seam_radius,join_style='round')
 cloth=cloth.buffer(-seam_radius,join_style='round').buffer(seam_radius,join_style='round')
 if cloth.geom_type!='Polygon' or not cloth.is_valid or cloth.interiors:raise ValueError('garment is not one connected cloth region')
 sid=node['id'];palette=node.get('palette',{});ink=palette.get('ink','#445b63');colour=palette.get('fill','#6c8d98')
 d=path(list(cloth.exterior.coords)[:-1])
 footprint=cloth.buffer(stroke/2,join_style='round');outline=tuple(footprint.exterior.coords)[:-1]
 mounts={'neck':dict(point=tuple(origin),normal=None,direction=(0,-1))};features={'object':dict(paths=[dict(d=d,transform='')],bounds=bounds(outline),controls=[])}
 for side,j in joints.items():
  for name in ('shoulder','elbow','wrist'):
   p=j[name];key=side+'-'+name;mounts[key]=dict(point=p,normal=None)
   if name=='wrist':mounts[key]['direction']=arm_data_by_side[side].mounts['wrist']['direction']
   features[key]=dict(paths=[dict(d=path([j['shoulder'],j['elbow'],j['wrist']],False),transform='')],bounds=[p[0]-20,p[1]-20,p[0]+20,p[1]+20],controls=[],focus=p,locks={'neck':tuple(origin)},units='computed garment joint')
 # Each surface carries its own exterior/overlap ink. Global depth also sees these
 # surfaces, allowing an external object between torso and front sleeve.
 surfaces=[]
 for name,material,depth in [('left',arms[0],-1),('torso',body,0),('right',arms[1],1)]:
  # The same closing radius that sews cloth must cover its added junction material.
  # Dilation distributes over union: these overlapping local surfaces cover all cloth.
  material=material.buffer(seam_radius).intersection(cloth)
  contour=cloth.boundary.intersection(material.buffer(stroke))
  extra=[]
  if name in arm_data_by_side:
   data=arm_data_by_side[name];rows=data.rows
   band=[r for r in rows if r.t>=1-node.get('cuff',.055)]
   if node.get('cuff',.055) and len(band)<2:band=list(rows[-2:])
   if node.get('cuff',.055):
    bandshape=Polygon([r.left for r in band]+[r.right for r in reversed(band)])
    dark='#'+''.join(f'{round(int(colour[i:i+2],16)*.86):02x}' for i in (1,3,5))
    extra=[xml_comment(sid+'-'+name+'-cuff: colour follows owned sleeve'),f'<path id="{sid}--{name}-band" d="{polygon_path(bandshape)}" fill="{dark}"/>']
   # Only the front forearm needs a deliberate internal side contour.
   if name=='right':
    edge=LineString([r.left for r in rows]+[r.right for r in reversed(rows)])
    at=min(range(len(rows)),key=lambda i:math.dist(rows[i].spine,data.joints['elbow']))
    forearm=Polygon([r.left for r in rows[at:]]+[r.right for r in reversed(rows[at:])])
    if forearm.intersection(body).area>1e-6:contour=union_all([contour,edge.intersection(body.buffer(-stroke/2))])
  sidpart=sid+'.plane-'+name
  paint='\n'.join([xml_comment(sidpart+': computed cloth surface'),f'<path id="{sidpart}-material" d="{polygon_path(material)}" fill="{colour}"/>',*extra,xml_comment(sidpart+'-ink: intentional visible cloth contour'),f'<path id="{sidpart}-ink" d="{line_path(contour)}" fill="none" stroke="{ink}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>'])
  aperture=material.buffer(stroke/2,join_style='round').simplify(h*.0003,preserve_topology=True)
  if aperture.geom_type!='Polygon' or aperture.interiors:raise ValueError('body surface must remain a solid polygon')
  surfaces.append(SimpleNamespace(name=name,svg=paint,outline=tuple(aperture.exterior.coords)[:-1],depth=depth))
 return SimpleNamespace(svg='\n'.join(s.svg for s in surfaces),outline=outline,features=features,center=host.center,angle=host.angle,mounts=mounts,joints=joints,surfaces=surfaces)


DEFAULT_LENGTH=.40

def arm_configuration(node,side):
 config=dict(wrist_spread=(-.59 if side=='left' else .59),wrist_height=1.07,elbow_at=.5,elbow_bend=(-.06 if side=='left' else .06))
 if side=='right' and node.get('pose','relaxed')=='offering':config.update(wrist_spread=.95,wrist_height=.50,elbow_at=.6,elbow_bend=-.4)
 if side=='right' and node.get('pose','relaxed')=='folded':config.update(wrist_spread=.05,wrist_height=.65,elbow_at=.6,elbow_bend=.5)
 return config|node.get('arms',{}).get(side,{})

def body_data(node,canvas):return _data(json.dumps(node,sort_keys=True),tuple(canvas))

@lru_cache(maxsize=32)
def _data(encoded,canvas):
 node=json.loads(encoded);base=dict(node);base.pop('attachment',None)
 base.setdefault('length',DEFAULT_LENGTH);base.setdefault('width',.9)
 data=_construct(base,canvas)
 center=data.center;a=math.radians(node.get('angle',0));c,s=math.cos(a),math.sin(a);cx,cy=center
 def point(p):return (cx+c*(p[0]-cx)+s*(p[1]-cy),cy-s*(p[0]-cx)+c*(p[1]-cy))
 transform=f'rotate({-node.get("angle",0)} {cx} {cy})'
 data.outline=tuple(point(p) for p in data.outline);data.angle=node.get('angle',0)
 data.svg=f'<g transform="{transform}">'+data.svg+'</g>'
 for surface in data.surfaces:
  surface.outline=tuple(point(p) for p in surface.outline);surface.svg=f'<g transform="{transform}">'+surface.svg+'</g>'
 for m in data.mounts.values():
  m['point']=point(m['point'])
  if m.get('direction'):
   x,y=m['direction'];m['direction']=(c*x+s*y,-s*x+c*y)
 common=['fill_color','ink_color']
 for pathinfo in data.features['object']['paths']:pathinfo['transform']=transform
 data.features['object'].update(bounds=bounds(data.outline),controls=['intent','length','width','angle','depth','depth_slope','pose','sleeve_width','cuff',*common])
 for side,j in data.joints.items():
  for name in ('shoulder','elbow','wrist'):j[name]=point(j[name])
  for name in ('shoulder','elbow','wrist'):
   f=data.features[side+'-'+name];p=j[name];pad=max(12,base['length']*min(canvas)*.08)
   f.update(bounds=[p[0]-pad,p[1]-pad,p[0]+pad,p[1]+pad],focus=p,locks={'neck':data.mounts['neck']['point'],'shoulder':j['shoulder'],**({'wrist':j['wrist']} if name=='elbow' else {})},controls=[side+'_'+k for k in ('wrist_spread','wrist_height','elbow_at','elbow_bend')],units='screen move in torso height; elbow preserves shoulder/wrist; wrist preserves shoulder and bend ratios')
   for pathinfo in f['paths']:pathinfo['transform']=transform
   if name in ('elbow','wrist'):f['interaction']='body-joint'
 return data

def move_joint(node,canvas,feature,direction,amount):
 import copy
 data=body_data(node,canvas);side,name=feature.split('-');h=node.get('length',DEFAULT_LENGTH)*min(canvas);w=h*node.get('width',.9)
 dx,dy={'left':(-amount*h,0),'right':(amount*h,0),'up':(0,-amount*h),'down':(0,amount*h)}[direction]
 a=math.radians(node.get('angle',0));dx,dy=dx*math.cos(a)-dy*math.sin(a),dx*math.sin(a)+dy*math.cos(a)
 config=arm_configuration(node,side);changed=copy.deepcopy(node)
 if name=='wrist':config.update(wrist_spread=config['wrist_spread']+dx/w,wrist_height=config['wrist_height']+dy/h)
 elif name=='elbow':
  j=data.joints[side];p=np.array(j['shoulder']);q=np.array(j['wrist']);e=np.array(j['elbow']);delta=q-p;length=float(np.linalg.norm(delta));axis=delta/length;right=np.array([axis[1],-axis[0]])
  # Inverse screen rotation above is only needed for wrist's local frame.
  sx,sy={'left':(-amount*h,0),'right':(amount*h,0),'up':(0,-amount*h),'down':(0,amount*h)}[direction]
  moved=e+np.array([sx,sy])-p;config.update(elbow_at=float(moved@axis)/length,elbow_bend=float(moved@right)/length)
 else:raise ValueError('select a body elbow or wrist')
 changed.setdefault('arms',{})[side]=config
 return changed
