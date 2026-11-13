"""A compact 2.5D grip grammar, authored in hand-relative relations.

Four short folded pads, a compact palm, and one opposed bent thumb. This is an
independent procedural construction: it does not load the OpenMoji teaching SVG,
its paths, a reference image, the WebXR mesh, or a generation model.
"""
from pathlib import Path
import sys,json,math
import numpy as np
from shapely import Point,LineString,box,union_all
from shapely.geometry import mapping
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.studio.geometry import path,xml_comment
from scripts.studio.render import rasterize

HERE=Path(__file__).resolve().parent
UNIT=420
SKIN='#f1d0b8';INK='#77513f';BAR='#bba150'

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
        i=min(int(np.searchsorted(t,v,side='right'))-1,len(p)-2);i=max(0,i)
        dt=t[i+1]-t[i];q=(v-t[i])/dt
        result.append((2*q**3-3*q*q+1)*p[i]+(q**3-2*q*q+q)*dt*tangents[i]+(-2*q**3+3*q*q)*p[i+1]+(q**3-q*q)*dt*tangents[i+1])
    return result

def build():
    # One host ruler, no frame-coordinate point editing. Rounded box and capsule
    # generators receive only their defining corners or terminals.
    palm=box(-.27,.40,.27,.70).buffer(.20,quad_segs=18)
    wrist=box(-.22,.72,.22,1.02)
    palm=palm.union(wrist)
    parts=[dict(name='palm',shape=palm,depth=-2,intent='compact palm and short wrist, behind the held bar')]
    rod=LineString([(-.90,.25),(.90,.25)]).buffer(.04,quad_segs=18)
    parts.append(dict(name='rod',shape=rod,depth=0,intent='one cylindrical contact segment through the folded hand'))
    for i,(name,top,bottom,radius) in enumerate(zip(('little','ring','middle','index'),(.12,.035,0,.045),(.44,.48,.47,.43),(.11,.12,.12,.11))):
        x=(i-1.5)*.22
        pad=LineString([(x,top+radius),(x,bottom-radius)]).buffer(radius,quad_segs=18)
        parts.append(dict(name=name,shape=pad,depth=2+i*.05,intent=name+' short folded pad closes in front of the handle'))
    thumb_points=[(.30,.68),(.48,.32),(.08,.29)]
    thumb=LineString(smooth(thumb_points)).buffer(.11,quad_segs=18)
    parts.append(dict(name='thumb',shape=thumb,depth=3,intent='opposed bent thumb across the folded pads; root joins inside the palm'))
    # Constant-depth opaque surfaces: painter order and subtraction are exactly
    # their visibility rule, with no authored cuts or special bar concealment.
    ordered=sorted(parts,key=lambda p:p['depth'])
    for i,part in enumerate(ordered):
        above=union_all([p['shape'] for p in ordered[i+1:]])
        part['visible']=part['shape'].difference(above)
    hand=union_all([p['shape'] for p in parts if p['name']!='rod'])
    by_name={p['name']:p for p in parts}
    return parts,ordered,by_name,hand,thumb_points

def run(out='01-compact'):
    from shapely.affinity import scale as resize
    parts,ordered,nodes,hand,thumb_points=build()
    total=union_all([p['shape'] for p in parts]);bounds=total.bounds
    span=max(bounds[2]-bounds[0],bounds[3]-bounds[1])+.20
    ox,oy=(bounds[0]+bounds[2]-span)/2,(bounds[1]+bounds[3]-span)/2
    def pp(g):return polygon_path(resize(g,xfact=UNIT,yfact=UNIT,origin=(0,0)))
    def lp(g):return line_path(resize(g,xfact=UNIT,yfact=UNIT,origin=(0,0)))
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="{ox*UNIT} {oy*UNIT} {span*UNIT} {span*UNIT}">',
        xml_comment('paper: neutral study field'),f'<rect id="paper" x="{ox*UNIT}" y="{oy*UNIT}" width="{span*UNIT}" height="{span*UNIT}" fill="#f6ecdf"/>','<defs>']
    for part in parts:
        svg.extend([xml_comment(part['name']+'-visibility: computed from declared surface depths'),f'<clipPath id="visible-{part["name"]}"><path id="{part["name"]}-aperture" d="{pp(part["visible"])}" fill-rule="evenodd"/></clipPath>'])
    svg.append('</defs>')
    for part in ordered:
        colour=BAR if part['name']=='rod' else SKIN
        svg.extend([xml_comment(part['name']+': '+part['intent']),f'<path id="{part["name"]}-material" d="{pp(part["shape"])}" fill="{colour}" fill-rule="evenodd"/>'])
    skin_visible=hand.difference(nodes['rod']['visible'])
    svg.extend(['<defs>',xml_comment('skin-ink-aperture: outer skin contour obeys the same depth as its fill'),f'<clipPath id="skin-ink"><path id="skin-ink-aperture" d="{pp(skin_visible)}" fill-rule="evenodd"/></clipPath></defs>'])
    svg.extend([xml_comment('rod-exterior: held segment contour stops behind front pads'),f'<path id="rod-exterior" d="{pp(nodes["rod"]["shape"])}" fill="none" stroke="#7b692f" stroke-width="{UNIT*.035}" clip-path="url(#visible-rod)"/>'])
    for name in ('little','ring','middle','index'):
        part=nodes[name]
        svg.extend([xml_comment(name+'-folded-contour: one short closed pad, not a long extended phalanx'),f'<path id="{name}-folded-contour" d="{lp(part["shape"].boundary)}" fill="none" stroke="{INK}" stroke-width="{UNIT*.018}" stroke-linejoin="round" clip-path="url(#visible-{name})"/>'])
    root=Point(thumb_points[0]).buffer(.22)
    thumb_edge=nodes['thumb']['shape'].boundary.difference(root)
    svg.extend([xml_comment('thumb-contour: explain the bend and opposed tip; omit the tissue attachment seam'),f'<path id="thumb-contour" d="{lp(thumb_edge)}" fill="none" stroke="{INK}" stroke-width="{UNIT*.018}" stroke-linejoin="round" clip-path="url(#visible-thumb)"/>',
        xml_comment('hand-exterior: one continuous compact silhouette around all skin parts'),f'<path id="hand-contour" d="{lp(hand.boundary)}" fill="none" stroke="{INK}" stroke-width="{UNIT*.036}" stroke-linejoin="round" clip-path="url(#skin-ink)"/>','</svg>'])
    out=HERE/out;out.mkdir(parents=True,exist_ok=True)
    dest=out/'grasp.svg';dest.write_text('\n'.join(svg),encoding='utf8');rasterize(dest,out/'grasp.png')
    meta=dict(status='procedural 2.5D drawing study, not an anatomical or physical grasp solver',hand_bounds=[v*UNIT for v in hand.bounds],
        mounts={k:[x*UNIT,y*UNIT] for k,(x,y) in dict(wrist=(0,1.02),grip=(0,.25),handle_left=(-.90,.25),handle_right=(.90,.25)).items()},
        bar_thickness=.08*UNIT,parts=[dict(name=p['name'],depth=p['depth'],intent=p['intent']) for p in ordered],footprint=mapping(resize(total,xfact=UNIT,yfact=UNIT,origin=(0,0))),
        external_art_paths_loaded=False,reference_images_loaded=False)
    (out/'grasp-render.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(out,flush=True)

if __name__=='__main__':run()
