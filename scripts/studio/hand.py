"""A front-view open hand from a knuckle row and smooth phalanx tubes.

Geometry is independent of references and rendering. The public workbench exposes
semantic finger controls and visible tip handles, never generated path points.
"""
from dataclasses import dataclass
from functools import lru_cache
import copy
import json
import math

from shapely import Point,Polygon,union_all,set_precision
from shapely.affinity import scale

from .geometry import xml_comment,bounds,resolve_root,path

DEFAULT_LENGTH=.64
GEOMETRY_GRID=.0001
WRIST_BASE=-.28
DIGITS=("index","middle","ring","little","thumb")

def smooth_finger(points,radius,taper=.16):
    """C1 bone interpolation with a continuous, gently jointed width field."""
    times=[0]
    for a,b in zip(points,points[1:]): times.append(times[-1]+math.dist(a,b))
    total=times[-1];times=[t/total for t in times]
    tangents=[]
    for i in range(len(points)):
        lo=max(0,i-1);hi=min(len(points)-1,i+1);dt=times[hi]-times[lo]
        tangents.append(tuple((points[hi][k]-points[lo][k])/dt for k in (0,1)))
    def sample(t):
        i=next((i for i in range(len(times)-1) if t<=times[i+1]),len(times)-2)
        dt=times[i+1]-times[i];s=(t-times[i])/dt
        h=(2*s**3-3*s**2+1,s**3-2*s**2+s,-2*s**3+3*s**2,s**3-s**2)
        dh=(6*s*s-6*s,3*s*s-4*s+1,-6*s*s+6*s,3*s*s-2*s)
        p=tuple(h[0]*points[i][k]+h[1]*dt*tangents[i][k]+h[2]*points[i+1][k]+h[3]*dt*tangents[i+1][k] for k in (0,1))
        d=tuple((dh[0]*points[i][k]+dh[1]*dt*tangents[i][k]+dh[2]*points[i+1][k]+dh[3]*dt*tangents[i+1][k])/dt for k in (0,1))
        length=math.hypot(*d)
        if length<1e-10: raise ValueError('finger centerline stalled')
        d=(d[0]/length,d[1]/length);n=(-d[1],d[0])
        r=radius*(1-taper*t+.03*math.exp(-((t-.45)/.12)**2)+.02*math.exp(-((t-.75)/.1)**2))
        return p,d,n,r
    rows=[sample(i/48) for i in range(49)]
    left=[(p[0]+n[0]*r,p[1]+n[1]*r) for p,d,n,r in rows]
    right=[(p[0]-n[0]*r,p[1]-n[1]*r) for p,d,n,r in rows]
    p,d,n,r=rows[-1]
    tip=[(p[0]+r*(n[0]*math.cos(a)+d[0]*math.sin(a)),p[1]+r*(n[1]*math.cos(a)+d[1]*math.sin(a))) for a in [i*math.pi/16 for i in range(1,16)]]
    p,d,n,r=rows[0]
    root=[(p[0]-r*(n[0]*math.cos(a)+d[0]*math.sin(a)),p[1]-r*(n[1]*math.cos(a)+d[1]*math.sin(a))) for a in [i*math.pi/16 for i in range(1,16)]]
    shape=Polygon(left+tip+list(reversed(right))+root)
    if not shape.is_valid: raise ValueError('finger tube crosses itself')
    return shape


def digit_points(name,spread=1,length=1,lean=0):
    if name=='thumb':
        points=[(-.28,.32)]
        steps=((-62,.34),(-52,.30))
    else:
        i=DIGITS.index(name)
        u=(i-1.5)*.22
        v=.96-.1*(u/.43)**2-.08*(i/3)**3
        points=[(u,v)]
        size=(.84,.96,.88,.65)[i]
        angle=(-10,-2,8,20)[i]*spread
        camber=(3,1,-1,-4)[i]
        steps=[(angle+j*camber,size*share) for j,share in enumerate((.45,.30,.25))]
    for angle,step in steps:
        a=math.radians(angle+lean)
        points.append((points[-1][0]+math.sin(a)*step*length,points[-1][1]+math.cos(a)*step*length))
    return points


def construct(spread=1,adjustments=None):
    adjustments=adjustments or {}
    digits={};knuckles=[]
    radii=(.104,.110,.104,.085)
    for i,name in enumerate(('index','middle','ring','little')):
        control=adjustments.get(name,{})
        points=digit_points(name,spread,control.get('length',1),control.get('lean',0))
        knuckles.append(Point(*points[0]).buffer(radii[i],quad_segs=12))
        widths=[radii[i]*f for f in (1,1.02,.91,.82)]
        digits[name]=dict(points=points,radii=widths,shape=smooth_finger(points,radii[i]))
    # Palm and knuckle row form one broad host, instead of radial petals at one point.
    palm=scale(Point(0,.44).buffer(1,quad_segs=32),.43,.49)
    palm=union_all([palm]+knuckles).convex_hull
    thenar=Point(-.23,.31).buffer(.205,quad_segs=24)
    control=adjustments.get('thumb',{})
    thumb=digit_points('thumb',spread,control.get('length',1),control.get('lean',0))
    digits['thumb']=dict(points=thumb,radii=[.12,.108,.096],shape=smooth_finger(thumb,.12,.20))
    wrist=Polygon([(-.26,WRIST_BASE),(.26,WRIST_BASE),(.31,.12),(-.31,.12)]).buffer(.025,quad_segs=8)
    host=union_all([palm,thenar,wrist])
    free={name:d['shape'].difference(host.buffer(.04)) for name,d in digits.items()}
    for i,name in enumerate(DIGITS):
        for other in DIGITS[i+1:]:
            if free[name].intersection(free[other]).area>1e-5:
                raise ValueError(f'{name} and {other} overlap above the knuckle row; reduce lean or increase spread')
    # All boolean operands share a declared precision. Shared-outline locality
    # is measured at that resolution, not as pixel identity after re-tessellation.
    shape=union_all([set_precision(p,GEOMETRY_GRID) for p in [palm,thenar,wrist]+[d['shape'] for d in digits.values()]])
    # A small tissue fillet rounds web roots and wrist joins without closing the
    # separated fingers. It is a shape relation, not an authored clipping patch.
    # Use one explicit construction precision. The unquantized closing produced
    # a 2.1e-11-area chip, about .005px across at this study size; do not silently
    # select a largest component and hide a genuine detached finger.
    shape=set_precision(shape,GEOMETRY_GRID)
    shape=set_precision(shape.buffer(.035,quad_segs=6).buffer(-.035,quad_segs=6),GEOMETRY_GRID)
    if shape.geom_type!='Polygon' or shape.interiors or not shape.is_valid:
        raise ValueError('open hand must remain one connected silhouette without holes')
    return shape,digits,host


@lru_cache(maxsize=32)
def _rig(encoded,spread):
    return construct(spread,json.loads(encoded))


@lru_cache(maxsize=1)
def ruler():
    """A fixed nominal ruler prevents a finger edit from recentering the hand."""
    shape,_digits,_host=_rig('{}',1)
    x0,y0,x1,y1=shape.bounds
    return (x0+x1)/2,(y0+y1)/2,y1-y0


def transforms(node,canvas):
    cx,cy,height=ruler()
    unit=node.get('length',DEFAULT_LENGTH)*min(canvas)/height
    width=node.get('width',1)
    sign=-1 if node.get('handedness','right')=='left' else 1
    center=resolve_root({'at':{'anchor':'center'}|node.get('at',{})},canvas)
    angle=math.radians(-node.get('angle',0));ca,sa=math.cos(angle),math.sin(angle)
    def project(p):
        x=(p[0]-cx)*unit*width*sign;y=-(p[1]-cy)*unit
        return (center[0]+x*ca-y*sa,center[1]+x*sa+y*ca)
    def inverse(p):
        x,y=p[0]-center[0],p[1]-center[1]
        return (cx+(x*ca+y*sa)/(unit*width*sign),cy-(-x*sa+y*ca)/unit)
    return project,inverse,unit,center


def crease_lines(digits):
    lines={
        'thenar-crease':[(-.27+.23*math.cos(math.radians(a)),.32+.26*math.sin(math.radians(a))) for a in range(55,-51,-5)],
        'palm-crease':[(u,.66+.06*(u/.28)**2) for u in [-.28+i*.56/32 for i in range(33)]],
        'wrist-crease':[(u,-.09+.02*(u/.15)**2) for u in [-.15+i*.30/24 for i in range(25)]],
    }
    for name,digit in digits.items():
        a,b=digit['points'][0:2];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
        radius=digit['radii'][1]*.58
        lines[name+'-crease']=[(b[0]+nx*radius*t-dx/length*radius*.12*(1-t*t),
                               b[1]+ny*radius*t-dy/length*radius*.12*(1-t*t)) for t in [-1+i/8 for i in range(17)]]
    return lines


@dataclass(frozen=True)
class HandData:
    svg: str
    outline: tuple
    features: dict
    center: tuple
    angle: float
    digits: dict
    mounts: dict


def hand_data(node,canvas):
    return _hand_data(json.dumps(node,sort_keys=True),tuple(canvas))


@lru_cache(maxsize=32)
def _hand_data(encoded,canvas):
    node=json.loads(encoded);sid=node['id'];spread=node.get('spread',1)
    shape,digits,host=_rig(json.dumps(node.get('digits',{}),sort_keys=True),spread)
    project,_inverse,unit,center=transforms(node,canvas)
    surface=[project(p) for p in list(shape.exterior.coords)[:-1]]
    ink_width=unit*.016
    footprint=Polygon(surface).buffer(ink_width/2,quad_segs=3).simplify(.04,preserve_topology=True)
    if footprint.geom_type!='Polygon' or footprint.interiors or not footprint.is_valid:
        raise ValueError('finger gaps are too narrow for this open-hand outline; increase spread')
    outer=tuple(footprint.exterior.coords)[:-1]
    palette=node.get('palette',{})
    skin=palette.get('skin','#f1d1b9');ink=palette.get('ink','#493b40')
    crease='#b17a68' if 'skin' not in palette else '#'+''.join(f'{round(int(skin[i:i+2],16)*.70):02x}' for i in (1,3,5))
    crease=palette.get('crease',crease)
    d=path(surface)
    svg=[xml_comment(sid+'-silhouette: one open palm with four knuckle-based fingers and an opposed thumb'),
         f'<path id="{sid}--silhouette" d="{d}" fill="{skin}" stroke="{ink}" stroke-width="{ink_width}" stroke-linejoin="round"/>',
         xml_comment(f'{sid}-skin-aperture: flexion marks stay on the generated hand surface'),
         f'<defs><clipPath id="{sid}--skin-clip" clipPathUnits="userSpaceOnUse"><path id="{sid}--skin-aperture" d="{d}"/></clipPath></defs>',
         f'<g id="{sid}--creases" clip-path="url(#{sid}--skin-clip)">']
    for name,points in crease_lines(digits).items():
        is_digit=name.removesuffix('-crease') in DIGITS
        svg.extend([xml_comment(f'{sid}-{name}: a sparse palmar flexion cue, not a skeleton edge'),
                    f'<path id="{sid}--{name}" d="{path([project(p) for p in points],False)}" fill="none" stroke="{crease}" opacity="{.7 if is_digit else 1}" stroke-width="{unit*(.007 if is_digit else .009)}" stroke-linecap="round"/>'])
    svg.append('</g>')
    features={'object':dict(paths=[dict(d=path(outer),transform='')],bounds=bounds(outer),
                           controls=['intent','length','width','angle','depth','depth_slope','spread','handedness',
                                     'skin_color','ink_color','crease_color'])}
    for name,digit in digits.items():
        points=[project(p) for p in list(digit['shape'].exterior.coords)[:-1]]
        nominal=digit_points(name,spread)
        features[name]=dict(paths=[dict(d=path(points),transform='')],bounds=bounds(points),
                            controls=['finger_length','finger_lean'],interaction='digit-tip',
                            focus=project(digit['points'][-1]),locks={'knuckle':project(digit['points'][0])},
                            nominal_span=math.dist(project(nominal[0]),project(nominal[-1])),
                            units="tip move amount = fraction of this digit's nominal span; directions are screen directions")
    from shapely import LineString
    wrist_span=shape.intersection(LineString([(shape.bounds[0]-1,WRIST_BASE),(shape.bounds[2]+1,WRIST_BASE)])).length*unit*node.get('width',1)
    angle=math.radians(node.get('angle',0))
    return HandData('\n'.join(svg),outer,features,center,node.get('angle',0),digits,{'wrist':dict(point=project((0,WRIST_BASE)),normal=None,direction=(math.sin(angle),math.cos(angle)),span=wrist_span)})


def move_tip(node,canvas,name,direction,amount):
    if name not in DIGITS: raise ValueError('select a named digit tip')
    data=hand_data(node,canvas);feature=data.features[name]
    dx,dy={'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}[direction]
    x,y=feature['focus'];span=feature['nominal_span']
    _project,inverse,_unit,_center=transforms(node,canvas)
    target=inverse((x+dx*amount*span,y+dy*amount*span))
    base=digit_points(name,node.get('spread',1));root=base[0]
    bx,by=base[-1][0]-root[0],base[-1][1]-root[1]
    tx,ty=target[0]-root[0],target[1]-root[1]
    length=math.hypot(tx,ty)/math.hypot(bx,by)
    lean=math.degrees(math.atan2(tx,ty)-math.atan2(bx,by))
    lean=(lean+180)%360-180
    changed=copy.deepcopy(node)
    changed.setdefault('digits',{}).setdefault(name,{}).update(length=length,lean=lean)
    return changed,dict(length=length,lean=lean)
