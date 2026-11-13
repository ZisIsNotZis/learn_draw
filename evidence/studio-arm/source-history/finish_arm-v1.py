"""Optional sleeve finish, kept separate from the computed joint structure."""
from dataclasses import replace
import math
import numpy as np
from shapely import Polygon,LineString
from scripts.studio.geometry import path,xml_comment

def finish_arm(node,data,cuff=.055,crease=.65):
 rows=data.rows;sid=node['id'];colour=node.get('palette',{}).get('fill','#6c8d98');ink=node.get('palette',{}).get('ink','#445b63')
 dark='#'+''.join(f'{round(int(colour[i:i+2],16)*.86):02x}' for i in (1,3,5))
 root=np.array(rows[0].spine);wrist=np.array(rows[-1].spine);e=np.array(data.joints['elbow'])
 fill=Polygon([r.left for r in rows]+[r.right for r in reversed(rows)])
 additions=[]
 if cuff:
  band=[r for r in rows if r.t>=1-cuff]
  if len(band)<2:band=list(rows[-2:])
  points=[r.left for r in band]+[r.right for r in reversed(band)]
  shape=Polygon(points)
  if not fill.buffer(1e-7).covers(shape):raise ValueError('cuff finish escaped the sleeve')
  additions=[xml_comment(sid+'-cuff: a short cloth band follows the actual forearm, not a separate floating block'),f'<path id="{sid}--cuff" d="{path(points)}" fill="{dark}"/>']
 crease_svg=[]
 if crease:
  index=min(range(len(rows)),key=lambda i:math.dist(rows[i].spine,e))
  row=rows[index];mid=np.array(row.spine);toward=e-mid;size=float(np.linalg.norm(toward))
  if size>1e-7:
   toward/=size;radius=math.dist(row.left,row.right)/2
   a=mid-toward*radius*.82;b=mid-toward*radius*(.82-.85*crease)
   mark=LineString([a,b]);stroke=max(math.dist(rows[-1].left,rows[-1].right)*.032,.5)
   if not fill.buffer(1e-7).covers(mark.buffer(stroke/2)):raise ValueError('elbow crease escaped the sleeve')
   crease_svg=[xml_comment(sid+'-crease: one short fold at the inside of the computed elbow'),f'<path id="{sid}--crease" d="{path([a,b],False)}" fill="none" stroke="{ink}" stroke-width="{stroke}" stroke-linecap="round"/>']
 parts=data.svg.split('\n');svg='\n'.join(parts[:2]+additions+parts[2:]+crease_svg)
 return replace(data,svg=svg)
