"""Small art-directed sky, ridge and celestial recipes; no reference or pixel input."""
from dataclasses import dataclass
from functools import lru_cache
import json
import math
import random

from .geometry import bounds, resolve_root


KINDS=('sky','hills','moon','sun')
DEFAULT_DEPTH={'sky':-20,'hills':10,'moon':0,'sun':0}
DEFAULT_LENGTH={'sky':1,'hills':1,'moon':.22,'sun':.20}


def path(points):
    return 'M '+' L '.join(f'{x:.4f},{y:.4f}' for x,y in points)+' Z'


@dataclass(frozen=True)
class SceneryData:
    svg: str
    outline: tuple
    features: dict
    center: tuple
    angle: float=0


def scenery_data(node,canvas):
    return _data(json.dumps(node,sort_keys=True),tuple(canvas))


@lru_cache(maxsize=64)
def _data(encoded,canvas):
    node=json.loads(encoded);kind=node['kind'];sid=node['id']
    w,h=canvas;unit=min(canvas);palette=node.get('palette',{})
    out=[]
    def add(name,intent,markup):
        out.extend([f'<!-- {sid}-{name}: {intent} -->',markup.replace('ID',sid+'-'+name)])
    controls=['depth','depth_slope']
    if kind=='sky':
        is_day=node.get('style','dusk')=='day'
        top=palette.get('top','#7ab6c9' if is_day else '#293754')
        bottom=palette.get('bottom','#f9dfab' if is_day else '#d49394')
        polygon=((0,0),(w,0),(w,h),(0,h));center=(w/2,h/2)
        add('gradient','a quiet vertical atmosphere',f'<defs><linearGradient id="ID" x2="0" y2="1"><stop stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>')
        add('field','sky fills the entire canvas',f'<rect id="ID" width="{w}" height="{h}" fill="url(#{sid}-gradient)"/>')
        rng=random.Random(node.get('seed',4))
        for i in range(int(node.get('stars',0 if is_day else 28))):
            x=rng.uniform(.04,.96)*w;y=rng.uniform(.04,.57)*h;r=rng.uniform(.0012,.0026)*unit
            add(f'star-{i}','small seeded star, subordinate to the moon',f'<circle id="ID" cx="{x}" cy="{y}" r="{r}" fill="{palette.get("stars","#fae4be")}" opacity="{rng.uniform(.45,.85)}"/>')
        controls+=['style','stars','seed','top_color','bottom_color','stars_color']
    elif kind=='hills':
        horizon=node.get('horizon',.64);relief=node.get('relief',.11)
        rng=random.Random(node.get('seed',4));phase=rng.uniform(-math.pi,math.pi)
        colors=[palette.get(k,v) for k,v in zip(('far','middle','near'),('#78667e','#4d536c','#303c50'))]
        polygon=None;near_line=None
        for i,color in enumerate(colors):
            # A shared broad rhythm and weaker harmonic avoid random jagged noise.
            line=[(w*j/96,h*(horizon+i*(1-horizon)*.28+relief*(math.sin(j/96*math.tau*.72+phase+i*.95)*.65+
                         math.sin(j/96*math.tau*1.38+phase*.4+i*.7)*.23))) for j in range(97)]
            poly=tuple(line+[(w,h),(0,h)])
            from shapely import Polygon
            polygon=Polygon(poly) if polygon is None else polygon.union(Polygon(poly))
            add(f'ridge-{i}','overlapping smooth ridge '+str(i),f'<path id="ID" d="{path(poly)}" fill="{color}"/>')
            near_line=line
        for i in range(int(node.get('trees',0))):
            # A foreground grove supplies scale and a secondary focal group. Its
            # feet attach to the computed near ridge; it cannot float if relief changes.
            t=(.12+i*.095 if node.get('tree_side','left')=='left' else .88-i*.095)
            x=t*w;index=min(95,int(t*96));fraction=t*96-index
            foot=near_line[index][1]*(1-fraction)+near_line[index+1][1]*fraction
            height=node.get('tree_scale',.18)*h*rng.uniform(.72,1.10)
            width=height*.40
            shapes=[Polygon([(x-width*.06,foot-height*.55),(x+width*.06,foot-height*.55),
                             (x+width*.06,foot+1),(x-width*.06,foot+1)])]
            for top,bottom,spread in ((0,.45,.54),(.22,.70,.78),(.44,.91,1)):
                shapes.append(Polygon([(x,foot-height*(1-top)),(x+width*spread/2,foot-height*(1-bottom)),
                                       (x-width*spread/2,foot-height*(1-bottom))]))
            from shapely import union_all
            tree=union_all(shapes)
            polygon=polygon.union(tree)
            add(f'pine-{i}','a tapered evergreen rooted on the near ridge',
                f'<path id="ID" d="{path(tuple(tree.exterior.coords)[:-1])}" fill="{colors[-1]}"/>')
        polygon=tuple(polygon.exterior.coords)[:-1]
        center=(w/2,h/2)
        controls+=['horizon','relief','seed','trees','tree_scale','tree_side','far_color','middle_color','near_color']
    else:
        placement={'anchor':'upper_right'}|node.get('at',{'anchor':'upper_right','offset':[0,.10]})
        center=resolve_root({'at':placement},canvas);cx,cy=center
        radius=node.get('length',DEFAULT_LENGTH[kind])*unit/2
        angle=node.get('angle',-20 if kind=='moon' else 0)
        from shapely import Polygon
        circle=Polygon([(cx+radius*math.cos(i*math.tau/192),cy+radius*math.sin(i*math.tau/192)) for i in range(192)])
        if kind=='moon':
            fullness=node.get('fullness',.42)
            distance=2*radius*fullness
            cut=Polygon([(cx+distance+radius*math.cos(i*math.tau/192),cy+radius*math.sin(i*math.tau/192)) for i in range(192)])
            shape=circle.difference(cut)
            from shapely.affinity import rotate
            shape=rotate(shape,-angle,origin=center)
            polygon=tuple(shape.exterior.coords)[:-1]
            add('disc','a computed crescent; fullness controls the illuminated width',f'<path id="ID" d="{path(polygon)}" fill="{palette.get("fill","#f8e3b8")}"/>')
            controls+=['length','angle','fullness','fill_color']
        else:
            polygon=tuple(circle.exterior.coords)[:-1]
            rays=int(node.get('rays',12))
            if rays:
                # Attached rays keep one true opaque silhouette, without an invisible
                # support disc that would incorrectly hide things through ray gaps.
                polygon=tuple((cx+radius*(1.24 if i%2 else .98)*math.cos(i*math.pi/rays-math.radians(angle)),
                               cy+radius*(1.24 if i%2 else .98)*math.sin(i*math.pi/rays-math.radians(angle))) for i in range(2*rays))
                shape=Polygon(polygon).union(circle)
                polygon=tuple(shape.exterior.coords)[:-1]
                add('rays','an attached radial sun crown',f'<path id="ID" d="{path(polygon)}" fill="{palette.get("rays","#f8da99")}"/>')
            add('disc','a warm simple sun',f'<circle id="ID" cx="{cx}" cy="{cy}" r="{radius}" fill="{palette.get("fill","#f7cf83")}"/>')
            controls+=['length','angle','rays','fill_color','rays_color']
    feature=dict(paths=[dict(d=path(polygon),transform='')],bounds=bounds(polygon),controls=controls)
    return SceneryData('\n'.join(out),tuple(polygon),{'object':feature},center)
