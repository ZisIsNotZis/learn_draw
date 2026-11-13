"""Study upper-body garment: computed collar/shoulders plus owned sleeves and one cloth contour."""
from types import SimpleNamespace
import math
import numpy as np
from shapely import Polygon,LineString,union_all
from scripts.studio.grip import polygon_path,line_path
from scripts.studio.geometry import path,xml_comment,bounds
from study_arm import arm_data
from finish_arm import finish_arm
import xml.etree.ElementTree as ET

def bezier(a,b,c,d,n=28):
 a,b,c,d=map(np.array,(a,b,c,d))
 return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d) for t in np.linspace(0,1,n,endpoint=False)]

def upper_body(node,canvas,original,right_target,wrist_direction,wrist_width,base_origin,front_contours=False):
 host=original(node,canvas);h=node.get('length',.4)*min(canvas);w=h*node.get('width',.9)
 stroke=node.get('stroke',.006)*h;origin=np.array([host.center[0],host.center[1]-h/2-stroke/2]);shift=origin-np.array(base_origin)
 neck=w*.18;drop=h*.11;collar=h*.045
 nl=(-neck/2,0);sl=(-w/2,drop);hl=(-w*.40,h);hr=(w*.40,h);sr=(w/2,drop);nr=(neck/2,0)
 points=bezier(nl,(-neck/2-w*.10,0),(-w/2,drop-h*.06),sl)
 points+=bezier(sl,(-w/2,drop+h*.22),(-w*.43,h*.75),hl)
 points+=[hl,hr]
 points+=bezier(hr,(w*.43,h*.75),(w/2,drop+h*.22),sr)
 points+=bezier(sr,(w/2,drop-h*.06),(neck/2+w*.10,0),nr)
 points+=bezier(nr,(neck/2*.55,collar*1.33),(-neck/2*.55,collar*1.33),nl)
 body=Polygon([tuple(origin+np.array(p)) for p in points])
 if not body.is_valid:raise ValueError('torso contour invalid')
 joints={};arms=[];bands=[];arm_data_by_side={}
 for side in ('left','right'):
  shoulder_radius=wrist_width*min(canvas)*1.55/2
  p=origin+np.array([(-1 if side=='left' else 1)*(w/2-shoulder_radius),drop+shoulder_radius])
  q=(origin+np.array([-w*.59,h*1.07]) if side=='left' else
     origin+np.array([w*.59,h*1.07]) if right_target is None else np.array(right_target)+shift)
  delta=q-p;length=float(np.linalg.norm(delta));angle=math.degrees(math.atan2(delta[0],delta[1]))
  arm=dict(id=node['id']+'-'+side,kind='stroke',intent=side+' owned sleeve',length=length/min(canvas),thickness=wrist_width,
      start_width=1.55,end_width=1,angle=angle,ink_width=0,at=dict(anchor='center',offset=[p[0]/canvas[0]-.5,p[1]/canvas[1]-.5]),palette=node.get('palette',{}))
  data=arm_data(arm,canvas,mode='wrist-fit' if side=='right' else 'default',elbow_at=.60 if side=='right' else .50,elbow_bend=-.06,rounding=2,wrist_direction=wrist_direction or (0,-1))
  arms.append(data.material);joints[side]=data.joints;arm_data_by_side[side]=data
  finished=finish_arm(arm,data,crease=0)
  root=ET.fromstring('<svg>'+finished.svg+'</svg>')
  for element in root:
   if element.get('id','').endswith('--cuff'):bands.append((side,ET.tostring(element,encoding='unicode')))
 cloth=union_all([body,*arms])
 # Sewn cloth has rounded inner junctions, rather than mathematical needle armpits.
 seam_radius=wrist_width*min(canvas)*.12
 cloth=cloth.buffer(seam_radius,join_style='round').buffer(-seam_radius,join_style='round')
 cloth=cloth.buffer(-seam_radius,join_style='round').buffer(seam_radius,join_style='round')
 if cloth.geom_type!='Polygon' or not cloth.is_valid or cloth.interiors:raise ValueError('garment is not one connected cloth region')
 sid=node['id'];palette=node.get('palette',{});ink=palette.get('ink','#445b63');colour=palette.get('fill','#6c8d98')
 d=path(list(cloth.exterior.coords)[:-1])
 visible={'right':arms[1],'left':arms[0].difference(body.union(arms[1]))}
 decorations=[]
 for side,band in bands:
  mask=visible[side].intersection(cloth) if front_contours else cloth
  decorations.extend([xml_comment(sid+'-'+side+'-cuff-visibility: local surface depth clips its colour field'),f'<defs><clipPath id="{sid}--{side}-colour-mask"><path id="{sid}--{side}-colour-aperture" d="{polygon_path(mask)}"/></clipPath></defs>',f'<g id="{sid}--{side}-cuff" clip-path="url(#{sid}--{side}-colour-mask)">',band,'</g>'])
 internal=[]
 if front_contours:
  data=arm_data_by_side['right'];rows=data.rows;elbow=np.array(data.joints['elbow'])
  at=min(range(len(rows)),key=lambda i:math.dist(rows[i].spine,elbow))
  forearm=Polygon([r.left for r in rows[at:]]+[r.right for r in reversed(rows[at:])])
  # A front forearm crossing the body needs an intentional sleeve contour. Root
  # attachment alone does not add it; pure external silhouettes were insufficient.
  if forearm.intersection(body).area>1e-6:
   contour=LineString([r.left for r in rows]+[r.right for r in reversed(rows)])
   ink_region=body.buffer(-stroke/2).intersection(visible['right'])
   line=contour.intersection(ink_region)
   internal=[xml_comment(sid+'-front-arm-line: deliberate sleeve contour where its nearer surface crosses torso'),f'<path id="{sid}--front-arm-line" d="{line_path(line)}" fill="none" stroke="{ink}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>']
 svg='\n'.join([xml_comment(sid+'-cloth: collar, shoulders and both sleeves form one computed material region'),f'<path id="{sid}--cloth" d="{d}" fill="{colour}"/>',*decorations,
      xml_comment(sid+'-contour: shared cloth suppresses assembled interior shoulder boundaries'),f'<path id="{sid}--contour" d="{d}" fill="none" stroke="{ink}" stroke-width="{stroke}" stroke-linejoin="round"/>',*internal])
 footprint=cloth.buffer(stroke/2,join_style='round');outline=tuple(footprint.exterior.coords)[:-1]
 mounts={'neck':dict(point=tuple(origin),normal=None)};features={'object':dict(paths=[dict(d=d,transform='')],bounds=bounds(outline),controls=[])}
 for side,j in joints.items():
  for name in ('shoulder','elbow','wrist'):
   p=j[name];key=side+'-'+name;mounts[key]=dict(point=p,normal=None)
   features[key]=dict(paths=[dict(d=path([j['shoulder'],j['elbow'],j['wrist']],False),transform='')],bounds=[p[0]-20,p[1]-20,p[0]+20,p[1]+20],controls=[],focus=p,locks={'neck':tuple(origin)},units='study-only garment pose port')
 return SimpleNamespace(svg=svg,outline=outline,features=features,center=host.center,angle=host.angle,boundary=host.boundary,mounts=mounts,joints=joints)
