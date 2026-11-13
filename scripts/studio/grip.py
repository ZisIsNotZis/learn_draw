"""A compact illustrative grip: short folded pads, opposed thumb, owned handle.

This is a 2.5D vector vocabulary item, not a physical hand/prop contact solver.
All geometry comes from the hand ruler and named relations; no study asset is read.
"""
from dataclasses import dataclass
from functools import lru_cache
import json,math
import numpy as np
from shapely import Point,LineString,Polygon,box,union_all
from shapely.affinity import affine_transform,scale as resize
from .geometry import bounds,path,resolve_root,xml_comment

DEFAULT_LENGTH=.38
HAND_HEIGHT=1.02
ORIGIN=(0,.50)

def polygon_path(g):
    if g.is_empty:return ''
    if hasattr(g,'geoms'):return ' '.join(polygon_path(p) for p in g.geoms)
    return ' '.join([path(list(g.exterior.coords)[:-1])]+[path(list(r.coords)[:-1]) for r in g.interiors])

def line_path(g):
    if g.is_empty:return ''
    if hasattr(g,'geoms'):return ' '.join(line_path(p) for p in g.geoms)
    return path(list(g.coords),False) if g.geom_type in ('LineString','LinearRing') else ''

def smooth(points,count=48):
    p=np.array(points);t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];t/=t[-1]
    tangents=[]
    for i in range(len(p)):
        a=max(0,i-1);b=min(len(p)-1,i+1);tangents.append((p[b]-p[a])/(t[b]-t[a]))
    result=[]
    for v in np.linspace(0,1,count):
        i=max(0,min(int(np.searchsorted(t,v,side='right'))-1,len(p)-2));dt=t[i+1]-t[i];q=(v-t[i])/dt
        result.append((2*q**3-3*q*q+1)*p[i]+(q**3-2*q*q+q)*dt*tangents[i]+(-2*q**3+3*q*q)*p[i+1]+(q**3-q*q)*dt*tangents[i+1])
    return result

def construction(node):
    width=node.get('width',1);fold=node.get('fold_length',1)
    palm=box(-.27,.40,.27,.70).buffer(.20,quad_segs=18).union(box(-.22,.72,.22,HAND_HEIGHT))
    # Round the two palm/wrist concavities; the terminal stays a flat cuff mount.
    palm=palm.buffer(.065,quad_segs=12).buffer(-.065,quad_segs=12)
    parts=[dict(name='palm',shape=palm,depth=-2,intent='compact palm and short wrist behind the held handle')]
    span=node.get('handle_span',1.8);thickness=node.get('handle_thickness',.08)
    rod=LineString([(-span/2,.25),(span/2,.25)]).buffer(thickness/2,quad_segs=18)
    parts.append(dict(name='handle',shape=rod,depth=0,intent='owned contact segment through the folded hand'))
    for i,(name,top,end,radius) in enumerate(zip(('little','ring','middle','index'),(.12,.035,0,.045),(.44,.48,.47,.43),(.11,.12,.12,.11))):
        x=(i-1.5)*.22;end=top+(end-top)*fold
        pad=LineString([(x,top+radius),(x,end-radius)]).buffer(radius,quad_segs=18)
        parts.append(dict(name=name,shape=pad,depth=2+i*.05,intent=name+' short folded pad closes in front of the handle',ink_minimum=radius*1.8))
    thumb_points=[(.30,.68),(.48,.32),(.48-.40*node.get('thumb_reach',.9),.29)]
    thumb_radius=node.get('thumb_thickness',.10)
    thumb=LineString(smooth(thumb_points)).buffer(thumb_radius,quad_segs=18)
    parts.append(dict(name='thumb',shape=thumb,depth=3,intent='bent opposed thumb across the folded pads; tissue root is inside the palm',ink_minimum=thumb_radius*2))
    for p in parts:
        if p['name']!='handle':p['shape']=resize(p['shape'],xfact=width,yfact=1,origin=(0,0))
    hand=union_all([p['shape'] for p in parts if p['name']!='handle'])
    if span/2<=max(abs(hand.bounds[0]),abs(hand.bounds[2]))+.02:
        raise ValueError('grip.handle_span must expose both ends beyond the hand; increase span or reduce width')
    ordered=sorted(parts,key=lambda p:p['depth'])
    for i,p in enumerate(ordered):p['visible']=p['shape'].difference(union_all([q['shape'] for q in ordered[i+1:]]))
    return parts,ordered,{p['name']:p for p in parts},hand,thumb_points

def transforms(node,canvas):
    center=resolve_root(dict(node,at=node.get('at',{'anchor':'center'})),canvas)
    unit=node.get('length',DEFAULT_LENGTH)*min(canvas)/HAND_HEIGHT
    sign=-1 if node.get('thumb_side','right')=='left' else 1
    a=math.radians(node.get('angle',0));c,s=math.cos(a),math.sin(a)
    def project(p):
        x=(p[0]-ORIGIN[0])*sign;y=p[1]-ORIGIN[1]
        return (center[0]+unit*(x*c+y*s),center[1]+unit*(-x*s+y*c))
    origin=project((0,0));matrix=[unit*sign*c,unit*s,-unit*sign*s,unit*c,*origin]
    def shape(g):return affine_transform(g,matrix)
    def normal(p):
        x,y=p[0]*sign,p[1]
        return (x*c+y*s,-x*s+y*c)
    return project,shape,normal,unit,center

@dataclass(frozen=True)
class GripData:
    svg:str
    outline:tuple
    features:dict
    center:tuple
    angle:float
    mounts:dict
    dimensions:dict

def grip_data(node,canvas):return _data(json.dumps(node,sort_keys=True),tuple(canvas))

@lru_cache(maxsize=32)
def _data(encoded,canvas):
    node=json.loads(encoded);sid=node['id'];parts,ordered,nodes,hand,thumb_points=construction(node)
    project,shape,normal,unit,center=transforms(node,canvas)
    full=union_all([p['shape'] for p in parts])
    if full.geom_type!='Polygon' or not full.is_valid or full.interiors:
        raise ValueError('grip projection must stay one solid footprint; revise thickness/width/fold controls')
    palette=dict(skin='#f1d0b8',ink='#77513f',handle='#bba150',handle_ink='#7b692f')|node.get('palette',{})
    ink=unit*.018
    def pp(g):return polygon_path(shape(g))
    def lp(g):return line_path(shape(g))
    svg=[xml_comment(sid+': '+node['intent']),'<defs>']
    for part in parts:
        name=part['name']
        svg.extend([xml_comment(sid+'-'+name+'-visibility: constant support depths determine actual occlusion'),f'<clipPath id="{sid}--visible-{name}"><path id="{sid}--{name}-aperture" d="{pp(part["visible"])}" fill-rule="evenodd"/></clipPath>'])
    svg.append('</defs>')
    for part in ordered:
        name=part['name'];colour=palette['handle'] if name=='handle' else palette['skin']
        svg.extend([xml_comment(sid+'-'+name+': '+part['intent']),f'<path id="{sid}--{name}-material" d="{pp(part["shape"])}" fill="{colour}" fill-rule="evenodd"/>'])
    visible_skin=hand.difference(nodes['handle']['visible'])
    svg.extend(['<defs>',xml_comment(sid+'-skin-ink-aperture: exterior ink obeys the material visibility'),f'<clipPath id="{sid}--skin-ink"><path id="{sid}--skin-ink-aperture" d="{pp(visible_skin)}" fill-rule="evenodd"/></clipPath></defs>',
        xml_comment(sid+'-handle-contour: exposed held segment, never through front fingers'),f'<path id="{sid}--handle-contour" d="{pp(nodes["handle"]["shape"])}" fill="none" stroke="{palette["handle_ink"]}" stroke-width="{ink*2}" clip-path="url(#{sid}--visible-handle)"/>'])
    def visible_ink(part,edge):
        # Small isolated boundary fragments do not become stray finger creases.
        edge=edge.intersection(part['visible'].buffer(1e-7))
        segments=list(edge.geoms) if hasattr(edge,'geoms') else [edge]
        return union_all([g for g in segments if g.length>=part['ink_minimum']])
    for name in ('little','ring','middle','index'):
        part=nodes[name];line=visible_ink(part,part['shape'].boundary)
        svg.extend([xml_comment(sid+'-'+name+'-fold: explain a short closed pad, omitting isolated slivers'),f'<path id="{sid}--{name}-fold" d="{lp(line)}" fill="none" stroke="{palette["ink"]}" stroke-width="{ink}" stroke-linejoin="round" clip-path="url(#{sid}--visible-{name})"/>'])
    root=resize(Point(thumb_points[0]).buffer(node.get('thumb_thickness',.10)*2),xfact=node.get('width',1),yfact=1,origin=(0,0))
    thumb_line=visible_ink(nodes['thumb'],nodes['thumb']['shape'].boundary.difference(root))
    svg.extend([xml_comment(sid+'-thumb-fold: bent opposed pad, no sealed root seam'),f'<path id="{sid}--thumb-fold" d="{lp(thumb_line)}" fill="none" stroke="{palette["ink"]}" stroke-width="{ink}" stroke-linejoin="round" clip-path="url(#{sid}--visible-thumb)"/>',
        xml_comment(sid+'-exterior: continuous hand around all skin parts'),f'<path id="{sid}--hand-contour" d="{lp(hand.boundary)}" fill="none" stroke="{palette["ink"]}" stroke-width="{ink*2}" stroke-linejoin="round" clip-path="url(#{sid}--skin-ink)"/>'])
    outer=tuple(shape(full).exterior.coords)[:-1]
    controls=['intent','length','width','angle','depth','depth_slope','thumb_side','fold_length','thumb_reach','thumb_thickness','handle_span','handle_thickness','skin_color','ink_color','handle_color','handle_ink_color']
    def feature(g,controls,**extra):
        points=shape(g)
        return dict(paths=[dict(d=polygon_path(points),transform='')],bounds=list(points.bounds),controls=controls,**extra)
    features={'object':feature(full,controls),'thumb':feature(nodes['thumb']['shape'],['thumb_reach','thumb_thickness','skin_color','ink_color'],focus=project((thumb_points[-1][0]*node.get('width',1),thumb_points[-1][1])),locks={'wrist':project((0,HAND_HEIGHT)),'grip':project((0,.25))}),
        'fingers':feature(union_all([nodes[n]['shape'] for n in ('little','ring','middle','index')]),['fold_length','skin_color','ink_color']),
        'palm':feature(nodes['palm']['shape'],['width','skin_color','ink_color']),
        'handle':feature(nodes['handle']['shape'],['handle_span','handle_thickness','handle_color','handle_ink_color'])}
    span=node.get('handle_span',1.8);h=node.get('handle_thickness',.08)
    mounts={name:dict(point=project(p),normal=normal(n) if n is not None else None) for name,p,n in [
        ('wrist',(0,HAND_HEIGHT),None),('grip',(0,.25),None),('handle_left',(-span/2,.25),None),('handle_right',(span/2,.25),None),
        ('handle_top',(0,.25-h/2),(0,-1)),('handle_bottom',(0,.25+h/2),(0,1))]}
    return GripData('\n'.join(svg),outer,features,center,node.get('angle',0),mounts,
        dict(wrist_width=.44*node.get('width',1)*unit,handle_thickness=h*unit,nominal_hand_height=HAND_HEIGHT*unit))
