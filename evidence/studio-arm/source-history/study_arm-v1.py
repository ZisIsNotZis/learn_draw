"""Study-only sleeve grammar: three computed joints, a rounded elbow, independent line art.
No mesh/image input. Adoption awaits actual image/use evidence; this is not a native kind yet.
"""
from dataclasses import dataclass
import math
import numpy as np
from shapely import Polygon,LineString,union_all
from scripts.studio.geometry import Row,path,bounds,xml_comment
from scripts.studio.stroke import root_position,DEFAULT_LENGTH,DEFAULT_THICKNESS


def unit(v):
 size=float(np.linalg.norm(v))
 if size<1e-10:raise ValueError('arm segment collapses')
 return np.asarray(v)/size

@dataclass
class ArmData:
 svg:str
 outline:tuple
 features:dict
 center:tuple
 angle:float
 rows:tuple
 tangents:tuple
 mounts:dict
 joints:dict


def arm_data(node,canvas,*,mode='default',elbow_at=.5,elbow_bend=-.30,rounding=1.3,wrist_direction=None):
 scale=min(canvas);length=node.get('length',DEFAULT_LENGTH)*scale
 angle=math.radians(node.get('angle',0));c=np.array([math.sin(angle),math.cos(angle)]);right=np.array([c[1],-c[0]])
 p=np.array(root_position(node,canvas));q=p+length*c
 if mode=='wrist-fit':
  if wrist_direction is None:raise ValueError('wrist-fit requires an observed outward wrist direction')
  desired=-unit(wrist_direction);forward=float(desired@c)
  if forward<=.05:raise ValueError('wrist direction cannot fit this forward arm chord')
  elbow_bend=-(1-elbow_at)*float(desired@right)/forward
 if not .2<=elbow_at<=.8 or abs(elbow_bend)>.9:raise ValueError('elbow pose outside bounded study range')
 e=p+length*(elbow_at*c+elbow_bend*right);u=unit(e-p);v=unit(q-e)
 upper=float(np.linalg.norm(e-p));fore=float(np.linalg.norm(q-e))
 turn=math.atan2(float(u[0]*v[1]-u[1]*v[0]),float(u@v))
 thickness=node.get('thickness',DEFAULT_THICKNESS)*scale
 r0=thickness*node.get('start_width',1.55)/2;r1=thickness*node.get('end_width',1)/2
 re=math.sqrt(r0*r1)*.90
 samples=[]
 if abs(turn)<1e-5:
  for t in np.linspace(0,1,81):samples.append((p+t*(q-p),c,t*length))
  mid=length*elbow_at;total=length
 else:
  sign=1 if turn>0 else -1
  radius=re*rounding;trim=radius*math.tan(abs(turn)/2)
  if trim>.43*min(upper,fore):
   trim=.43*min(upper,fore);radius=trim/math.tan(abs(turn)/2)
  if radius<re*1.05:raise ValueError('arm too thick for this fold; reduce width or unfold the elbow')
  a=e-u*trim;b=e+v*trim;normal=np.array([-u[1],u[0]])*sign;center=a+normal*radius
  theta=math.atan2(a[1]-center[1],a[0]-center[0]);first=upper-trim;arc=abs(turn)*radius;last=fore-trim
  for t in np.linspace(0,1,25,endpoint=False):samples.append((p+t*(a-p),u,t*first))
  for t in np.linspace(0,1,33,endpoint=False):
   phi=theta+turn*t;point=center+radius*np.array([math.cos(phi),math.sin(phi)])
   tangent=sign*np.array([-math.sin(phi),math.cos(phi)])
   samples.append((point,tangent,first+t*arc))
  for t in np.linspace(0,1,25):samples.append((b+t*(q-b),v,first+arc+t*last))
  mid=first+arc/2;total=first+arc+last
 def ease(t):return t*t*(3-2*t)
 rows=[];tangents=[]
 for point,tangent,s in samples:
  radius=r0+(re-r0)*ease(s/mid) if s<=mid else re+(r1-re)*ease((s-mid)/(total-mid))
  normal=np.array([-tangent[1],tangent[0]])
  rows.append(Row(s/total,tuple(point+normal*radius),tuple(point-normal*radius),tuple(point)));tangents.append(tuple(tangent))
 # A root cap supplies overlap into the torso. The cap is fill, not a sealed tissue seam.
 cap=[]
 if node.get('start_cap','round')=='round':
  n=np.array([-u[1],u[0]])
  for phi in np.linspace(0,math.pi,25)[1:-1]:cap.append(tuple(p-r0*(n*math.cos(phi)+u*math.sin(phi))))
 points=[r.left for r in rows]+[r.right for r in reversed(rows)]+cap
 fill=Polygon(points)
 if not fill.is_valid or fill.interiors:raise ValueError('jointed arm contour crosses; revise pose/width')
 palette=node.get('palette',{});colour=palette.get('fill','#6c8d98');ink=palette.get('ink','#445b63');sw=node.get('ink_width',.0025)*scale
 contour=LineString([r.left for r in rows]+[r.right for r in reversed(rows)])
 footprint=fill.union(contour.buffer(sw/2,cap_style='flat',join_style='round')) if sw else fill
 if footprint.geom_type!='Polygon' or footprint.interiors:raise ValueError('jointed arm ink forms a cavity')
 sid=node['id'];svg='\n'.join([xml_comment(sid+'-cloth: upper arm and forearm meet at a computed elbow'),
  f'<path id="{sid}--cloth" d="{path(points)}" fill="{colour}"/>',
  xml_comment(sid+'-ink: intentional side/cuff contour; root stays open into torso'),
  f'<path id="{sid}--ink" d="{path(list(contour.coords),False)}" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>'])
 outer=tuple(footprint.exterior.coords)[:-1]
 features={'object':dict(paths=[dict(d=path(points),transform='')],bounds=bounds(outer),controls=[])}
 for name,point,other in [('root',p,q),('tip',q,p),('elbow',e,None)]:
  pad=max(r0,12);features[name]=dict(paths=[dict(d=path([p,e,q],False),transform='')],bounds=[point[0]-pad,point[1]-pad,point[0]+pad,point[1]+pad],controls=[],focus=tuple(point),locks={'shoulder':tuple(p),'wrist':tuple(q)},units='study-only computed joints; not a public editable arm kind')
  if name in ('root','tip'):features[name]['interaction']='stroke-terminal'
 mounts=dict(shoulder=dict(point=tuple(p),normal=None,direction=tuple(-u)),wrist=dict(point=tuple(q),normal=None,direction=tuple(v)),elbow=dict(point=tuple(e),normal=None))
 return ArmData(svg,outer,features,tuple(p),node.get('angle',0),tuple(rows),tuple(tangents),mounts,
                dict(shoulder=tuple(p),elbow=tuple(e),wrist=tuple(q),elbow_at=elbow_at,elbow_bend=elbow_bend,upper_length=upper,forearm_length=fore))
