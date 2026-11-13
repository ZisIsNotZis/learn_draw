"""Computed two-segment sleeve with a rounded elbow and separate intentional ink."""
from types import SimpleNamespace
import math
import numpy as np
from shapely import Polygon
from .geometry import Row
from .stroke import root_position,DEFAULT_LENGTH,DEFAULT_THICKNESS


def unit(v):
 size=float(np.linalg.norm(v))
 if size<1e-10:raise ValueError('arm segment collapses')
 return np.asarray(v)/size

def arm_data(node,canvas,*,mode='default',elbow_at=.5,elbow_bend=-.30,rounding=1.3,wrist_direction=None,elbow_reference_width=None):
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
 reference=r1 if elbow_reference_width is None else thickness*elbow_reference_width/2
 re=math.sqrt(r0*reference)*.90
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
 mounts=dict(shoulder=dict(point=tuple(p),normal=None,direction=tuple(-u)),wrist=dict(point=tuple(q),normal=None,direction=tuple(v)),elbow=dict(point=tuple(e),normal=None))
 return SimpleNamespace(rows=tuple(rows),tangents=tuple(tangents),mounts=mounts,
                joints=dict(shoulder=tuple(p),elbow=tuple(e),wrist=tuple(q),elbow_at=elbow_at,elbow_bend=elbow_bend,upper_length=upper,forearm_length=fore),material=fill)
