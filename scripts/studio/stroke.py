"""An editable gesture mark: useful round line first, optional width profile and colour plane."""
from dataclasses import dataclass
from functools import lru_cache
import copy
import json
import math

from shapely import Polygon
from .geometry import xml_comment,Row,bounds,path,resolve_root,window

DEFAULT_LENGTH=.4
DEFAULT_THICKNESS=.045
SAMPLES=80


@dataclass(frozen=True)
class StrokeData:
    svg: str
    outline: tuple
    features: dict
    center: tuple
    angle: float
    rows: tuple
    tangents: tuple


def root_position(node,canvas):
    return resolve_root(dict(node,at=node.get('at',{'anchor':'center','offset':[0,-.2]})),canvas)


def clean(points):
    result=[]
    for p in points:
        if not result or math.dist(result[-1],p)>1e-10: result.append(tuple(p))
    if len(result)>1 and math.dist(result[0],result[-1])<1e-10: result.pop()
    return result


def stroke_data(node,canvas):
    if 'endpoints' in node: raise ValueError('resolve the scene before compiling endpoint-bound stroke geometry')
    return _data(json.dumps(node,sort_keys=True),tuple(canvas))


@lru_cache(maxsize=64)
def _data(encoded,canvas):
    node=json.loads(encoded);root=root_position(node,canvas);unit=min(canvas)
    length=node.get('length',DEFAULT_LENGTH)*unit;thickness=node.get('thickness',DEFAULT_THICKNESS)*unit
    angle=math.radians(node.get('angle',0));c=math.cos(angle);s=math.sin(angle);bend=node.get('bend',0)
    rows=[];tangents=[]
    for i in range(SAMPLES+1):
        t=i/SAMPLES;u=length*bend*4*t*(1-t);v=length*t;du=length*bend*4*(1-2*t);dv=length
        for edit in node.get('edits',[]):
            weight=window(t,edit['at'],edit['radius']);d=(t-edit['at'])/edit['radius']
            derivative=-.5*math.pi/edit['radius']*math.sin(math.pi*d) if abs(d)<1 else 0
            u+=edit['dx']*thickness*weight;v+=edit['dy']*thickness*weight
            du+=edit['dx']*thickness*derivative;dv+=edit['dy']*thickness*derivative
        dx,dy=du*c+dv*s,-du*s+dv*c;speed=math.hypot(dx,dy)
        if speed<1e-10: raise ValueError('stroke gesture stalls; reduce this local push')
        tangent=(dx/speed,dy/speed);normal=(-tangent[1],tangent[0])
        center=(root[0]+u*c+v*s,root[1]-u*s+v*c)
        ease=t*t*(3-2*t)
        radius=thickness*((1-ease)*node.get('start_width',1)+ease*node.get('end_width',1))/2
        rows.append(Row(t,(center[0]+normal[0]*radius,center[1]+normal[1]*radius),(center[0]-normal[0]*radius,center[1]-normal[1]*radius),center));tangents.append(tangent)
    def cap(end,theta):
        i=-1 if end else 0;r=math.dist(rows[i].left,rows[i].right)/2;p=rows[i].spine;tx,ty=tangents[i];nx,ny=-ty,tx
        if end: return (p[0]+r*(nx*math.cos(theta)+tx*math.sin(theta)),p[1]+r*(ny*math.cos(theta)+ty*math.sin(theta)))
        return (p[0]-r*(nx*math.cos(theta)+tx*math.sin(theta)),p[1]-r*(ny*math.cos(theta)+ty*math.sin(theta)))
    start_round=node.get('start_cap','round')=='round';end_round=node.get('end_cap','round')=='round'
    points=[r.left for r in rows]+([cap(True,i*math.pi/24) for i in range(1,24)] if end_round else [])
    points += [r.right for r in reversed(rows)]+([cap(False,i*math.pi/24) for i in range(1,24)] if start_round else [])
    points=clean(points);shape=Polygon(points)
    if not shape.is_valid or shape.area<max(length*thickness*1e-6,1e-10):
        raise ValueError('stroke outline crosses or collapses; reduce bend/width/push')
    palette=node.get('palette',{});fill=palette.get('fill','#496b73');ink=palette.get('ink','#304950')
    shade=palette.get('shade','#'+''.join(f'{round(int(fill[i:i+2],16)*.78):02x}' for i in (1,3,5)))
    sid=node['id'];comment=node['intent']
    svg=[xml_comment(f'{sid}-paint: {comment}'),f'<path id="{sid}-paint" d="{path(points)}" fill="{fill}"/>']
    side=node.get('shade','none')
    if side!='none':
        if side=='right':
            tone=[r.spine for r in rows]+([cap(True,i*math.pi/24) for i in range(12,25)] if end_round else [])
            tone += [r.right for r in reversed(rows)]+([cap(False,i*math.pi/24) for i in range(1,13)] if start_round else [])
        else:
            tone=[r.left for r in rows]+([cap(True,i*math.pi/24) for i in range(1,13)] if end_round else [])
            tone += [r.spine for r in reversed(rows)]+([cap(False,i*math.pi/24) for i in range(12,25)] if start_round else [])
        tone=clean(tone);field=Polygon(tone)
        if not field.is_valid or not shape.buffer(1e-7).covers(field): raise ValueError('stroke colour plane crosses; reduce this gesture')
        svg += [xml_comment(f'{sid}-tone: one deliberate colour plane follows the gesture and caps'),f'<path id="{sid}-tone" d="{path(tone)}" fill="{shade}"/>']
    ink_width=node.get('ink_width',0)*unit
    if ink_width:
        svg += [xml_comment(f'{sid}-ink: intentional outer line, separate from the interior colour plane'),f'<path id="{sid}-ink" d="{path(points)}" fill="none" stroke="{ink}" stroke-width="{ink_width:.4f}" stroke-linejoin="round"/>']
    footprint=shape.buffer(ink_width/2,quad_segs=4) if ink_width else shape
    if footprint.geom_type!='Polygon' or footprint.interiors: raise ValueError('stroke ink closes a cavity; reduce width or ink')
    outline=tuple(footprint.exterior.coords)[:-1]
    controls=['intent','length','thickness','angle','bend','start_width','end_width','start_cap','end_cap','shade','ink_width','depth','depth_slope','fill_color','shade_color','ink_color']
    features={'object':dict(paths=[dict(d=path(points),transform='')],bounds=bounds(outline),controls=controls),
              'spine':dict(paths=[dict(d=path([r.spine for r in rows],False),transform='')],bounds=bounds([r.spine for r in rows]),controls=controls)}
    for name,i,other in [('root',0,-1),('tip',-1,0)]:
        focus=rows[i].spine;pad=max(thickness*max(node.get('start_width',1),node.get('end_width',1))/2,12)
        features[name]=dict(paths=[dict(d=path([r.spine for r in rows],False),transform='')],bounds=[focus[0]-pad,focus[1]-pad,focus[0]+pad,focus[1]+pad],controls=controls,
                            focus=rows[i].spine,locks={('tip' if name=='root' else 'root'):rows[other].spine},interaction='stroke-terminal',
                            units='screen terminal movement as fraction of shorter canvas dimension; opposite terminal fixed')
    return StrokeData('\n'.join(svg),outline,features,root,node.get('angle',0),tuple(rows),tuple(tangents))


def spine_selection(node,canvas,at,radius):
    data=stroke_data(node,canvas);selected=[r.spine for r in data.rows if abs(r.t-at)<=radius]
    focus=min(data.rows,key=lambda row:abs(row.t-at)).spine
    return dict(paths=[dict(d=path(selected,False),transform='')],bounds=bounds(selected),focus=focus,locks={'root':data.rows[0].spine,'tip':data.rows[-1].spine})


def move_terminal(node,canvas,name,direction,amount):
    data=stroke_data(node,canvas);root=data.rows[0].spine;tip=data.rows[-1].spine
    dx,dy={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}[direction];delta=(dx*amount*min(canvas),dy*amount*min(canvas))
    if name=='root': root=(root[0]+delta[0],root[1]+delta[1])
    elif name=='tip': tip=(tip[0]+delta[0],tip[1]+delta[1])
    else: raise ValueError('select the root or tip terminal')
    vx,vy=tip[0]-root[0],tip[1]-root[1]
    changed=copy.deepcopy(node);changed.update(length=math.hypot(vx,vy)/min(canvas),angle=math.degrees(math.atan2(vx,vy)))
    changed['at']=dict(anchor='center',offset=[root[0]/canvas[0]-.5,root[1]/canvas[1]-.5])
    return changed
