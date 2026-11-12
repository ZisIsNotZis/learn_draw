"""A compact editable colour mass, not a subject-specific template or raw SVG path."""
from dataclasses import dataclass
from functools import lru_cache
import json
import math

from shapely import Polygon
from .geometry import xml_comment,bounds,resolve_root,path,window

SIDES=('top','right','bottom','left')
DEFAULT_LENGTH=.32
SAMPLES=256


@dataclass(frozen=True)
class ShapeData:
    svg: str
    outline: tuple
    features: dict
    center: tuple
    angle: float
    boundary: tuple


def shape_data(node,canvas):
    return _data(json.dumps(node,sort_keys=True),tuple(canvas))


def span(node,canvas):
    return node.get('length',DEFAULT_LENGTH)*min(canvas)*min(1,node.get('width',.8))


def phase(side,t):
    # The four named arcs meet at their diagonal quarters. Direction is clockwise.
    return (SIDES.index(side)+t-.5)%4


def local_t(phase_value,side):
    center=SIDES.index(side)
    delta=(phase_value-center+2)%4-2
    return delta+.5


@lru_cache(maxsize=64)
def _data(encoded,canvas):
    node=json.loads(encoded);center=resolve_root(dict(node,at=node.get('at',{'anchor':'center'})),canvas)
    length=node.get('length',DEFAULT_LENGTH)*min(canvas);width=length*node.get('width',.8)
    angle=math.radians(node.get('angle',0));c=math.cos(angle);s=math.sin(angle)
    exponent=2 if node.get('profile','block')=='oval' else 2+22*(1-node.get('rounding',.65))
    taper=node.get('taper',0);rows=[]
    def nominal(q):
        theta=(q-1)*math.pi/2
        signed=lambda v: 0 if abs(v)<1e-12 else math.copysign(abs(v)**(2/exponent),v)
        y=signed(math.sin(theta))*.5
        factor=1-abs(taper)*(.5-y if taper>=0 else .5+y)
        x=signed(math.cos(theta))*.5*factor
        return (center[0]+x*width*c+y*length*s,center[1]-x*width*s+y*length*c)
    # Angular samples bunch up at corners of a block. Resample each named arc by
    # nominal length, so a small influence interval also means a small visible area.
    from shapely import LineString
    for side_index in range(4):
        arc=LineString([nominal(side_index-.5+i/128) for i in range(129)])
        for i in range(SAMPLES//4):
            t=i/(SAMPLES//4);q=(side_index-.5+t)%4
            p=arc.interpolate(t,normalized=True).coords[0];dx=dy=0
            for edit in node.get('edits',[]):
                weight=window(local_t(q,edit['side']),edit['at'],edit['radius'])
                dx+=(edit['dx']*c+edit['dy']*s)*span(node,canvas)*weight
                dy+=(-edit['dx']*s+edit['dy']*c)*span(node,canvas)*weight
            rows.append((q,(p[0]+dx,p[1]+dy)))
    boundary=tuple(p for q,p in rows);shape=Polygon(boundary)
    if not shape.is_valid or shape.area<length*width*.01:
        raise ValueError('shape contour crosses itself or collapses; reduce the edit')
    palette=node.get('palette',{});fill=palette.get('fill','#e9cba7');ink=palette.get('ink','#3d505a')
    stroke=node.get('stroke',.008)*length
    # Ink belongs to the opacity footprint; underlapping paint cannot leak through it.
    footprint=shape.buffer(stroke/2,quad_segs=3) if stroke else shape
    outline=tuple(footprint.exterior.coords)[:-1]
    sid=node['id'];d=path(boundary)
    controls=['intent','length','width','angle','profile','rounding','taper','stroke','depth','depth_slope','fill_color','ink_color']
    features={'object':dict(paths=[dict(d=d,transform='')],bounds=bounds(outline),controls=controls)}
    for side in SIDES:
        points=[p for q,p in sorted(rows,key=lambda row:local_t(row[0],side)) if 0<=local_t(q,side)<=1]
        features[side]=dict(paths=[dict(d=path(points,False),transform='')],bounds=bounds(points),controls=controls)
    svg=(xml_comment(f'{sid}-mass: {node["intent"]}')+'\n'+
         f'<path id="{sid}-mass" d="{d}" fill="{fill}" stroke="{ink}" stroke-width="{stroke:.4f}" stroke-linejoin="round"/>')
    return ShapeData(svg,outline,features,center,node.get('angle',0),tuple(rows))


def edge_selection(node,canvas,side,at,radius):
    data=shape_data(node,canvas)
    points=[p for q,p in sorted(data.boundary,key=lambda row:local_t(row[0],side)) if abs(local_t(q,side)-at)<=radius]
    if len(points)<2: raise ValueError('shape selection contains too few samples')
    def nearest(t):
        return min(data.boundary,key=lambda row:abs((row[0]-phase(side,t)+2)%4-2))[1]
    return dict(paths=[dict(d=path(points,False),transform='')],bounds=bounds(points),focus=nearest(at),
                locks={'arc-start':nearest(0),'arc-end':nearest(1)})
