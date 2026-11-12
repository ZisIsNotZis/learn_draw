"""An open-palm construction study, generated from knuckle and phalanx relations."""
from pathlib import Path
import json,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shapely import Point,Polygon,union_all,set_precision
from shapely.affinity import scale
from scripts.studio.render import path,rasterize


def capsule_chain(points,radii):
    pieces=[Point(*p).buffer(r,quad_segs=12) for p,r in zip(points,radii)]
    for a,b,ra,rb in zip(points,points[1:],radii,radii[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];distance=math.hypot(dx,dy);nx,ny=-dy/distance,dx/distance
        pieces.append(Polygon([(a[0]+nx*ra,a[1]+ny*ra),(b[0]+nx*rb,b[1]+ny*rb),
                               (b[0]-nx*rb,b[1]-ny*rb),(a[0]-nx*ra,a[1]-ny*ra)]))
    return union_all(pieces)


def construct(spread=1):
    digits={};knuckles=[]
    lengths=(.84,.96,.88,.65);radii=(.104,.110,.104,.085)
    angles=(-10,-2,8,20);camber=(3,1,-1,-4)
    for i,name in enumerate(('index','middle','ring','little')):
        u=(i-1.5)*.22
        v=.96-.1*(u/.43)**2-.08*(i/3)**3
        root=(u,v);knuckles.append(Point(*root).buffer(radii[i],quad_segs=12));points=[root]
        for j,share in enumerate((.45,.30,.25)):
            a=math.radians(angles[i]*spread+j*camber[i]);step=lengths[i]*share
            points.append((points[-1][0]+math.sin(a)*step,points[-1][1]+math.cos(a)*step))
        widths=[radii[i]*f for f in (1,1.02,.91,.82)]
        skin_points=[];skin_radii=[]
        for j,(a,b) in enumerate(zip(points,points[1:])):
            skin_points.extend([a,((a[0]+b[0])/2,(a[1]+b[1])/2)])
            skin_radii.extend([widths[j],min(widths[j],widths[j+1])*.88])
        skin_points.append(points[-1]);skin_radii.append(widths[-1])
        digits[name]=dict(points=points,radii=widths,shape=capsule_chain(skin_points,skin_radii))
    # Palm and knuckle row form one broad host, instead of radial petals at one point.
    palm=scale(Point(0,.44).buffer(1,quad_segs=32),.43,.49)
    palm=union_all([palm]+knuckles).convex_hull
    thenar=Point(-.23,.31).buffer(.205,quad_segs=24)
    thumb=[(-.28,.32)]
    for angle,length in ((-62,.34),(-52,.30)):
        a=math.radians(angle);thumb.append((thumb[-1][0]+math.sin(a)*length,thumb[-1][1]+math.cos(a)*length))
    digits['thumb']=dict(points=thumb,radii=[.12,.108,.096],shape=capsule_chain(thumb,[.12,.108,.096]))
    wrist=Polygon([(-.26,-.28),(.26,-.28),(.31,.12),(-.31,.12)]).buffer(.025,quad_segs=8)
    shape=union_all([palm,thenar,wrist]+[d['shape'] for d in digits.values()])
    before_type=shape.geom_type
    # A small tissue fillet rounds web roots and wrist joins without closing the
    # separated fingers. It is a shape relation, not an authored clipping patch.
    # Use one explicit construction precision. The unquantized closing produced
    # a 2.1e-11-area chip, about .005px across at this study size; do not silently
    # select a largest component and hide a genuine detached finger.
    shape=set_precision(shape,.0001)
    shape=set_precision(shape.buffer(.035,quad_segs=6).buffer(-.035,quad_segs=6),.0001).simplify(.0003,preserve_topology=True)
    if shape.geom_type!='Polygon' or shape.interiors or not shape.is_valid:
        raise ValueError(f'open hand must be one connected silhouette without holes: before={before_type}; {shape.geom_type}, valid={shape.is_valid}, holes={len(shape.interiors) if shape.geom_type=="Polygon" else "n/a"}; parts={[(p.area,p.bounds) for p in shape.geoms] if shape.geom_type=="MultiPolygon" else []}')
    return shape,digits


def render(directory):
    directory=Path(directory)
    if directory.exists() and any(directory.iterdir()): raise ValueError('choose a fresh output directory')
    directory.mkdir(parents=True,exist_ok=True)
    shape,digits=construct();x0,y0,x1,y1=shape.bounds
    unit=410/(y1-y0);cx=(x0+x1)/2;cy=(y0+y1)/2
    project=lambda p:(320+(p[0]-cx)*unit,320-(p[1]-cy)*unit)
    outer=[project(p) for p in list(shape.exterior.coords)[:-1]]
    header='<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640"><rect id="paper" width="640" height="640" fill="#f5eee4"/>'
    art=[header,'<!-- open-palm: one computed palm, four knuckle-based fingers and an opposed thumb -->',
         f'<path id="open-palm" d="{path(outer)}" fill="#f1d1b9" stroke="#493b40" stroke-width="2.8" stroke-linejoin="round"/>']
    creases={
        'thenar-crease':[(-.27+.23*math.cos(math.radians(a)),.32+.26*math.sin(math.radians(a))) for a in range(55,-51,-5)],
        'palm-crease':[(u,.66+.06*(u/.28)**2) for u in [-.28+i*.56/32 for i in range(33)]],
        'wrist-crease':[(u,-.09+.02*(u/.15)**2) for u in [-.15+i*.30/24 for i in range(25)]],
    }
    for name,points in creases.items():
        art.extend([f'<!-- {name}: a sparse anatomical grouping cue, not a capsule construction edge -->',
                    f'<path id="{name}" d="{path([project(p) for p in points],False)}" fill="none" stroke="#b17a68" stroke-width="1.6" stroke-linecap="round"/>'])
    for name,digit in digits.items():
        a,b=digit['points'][0:2];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
        radius=digit['radii'][1]*.58
        wrinkle=[(b[0]+nx*radius*t-dx/length*radius*.12*(1-t*t),
                  b[1]+ny*radius*t-dy/length*radius*.12*(1-t*t)) for t in [-1+i/8 for i in range(17)]]
        art.extend([f'<!-- {name}-crease: one subtle palmar flexion crease at the middle joint -->',
                    f'<path id="{name}-crease" d="{path([project(p) for p in wrinkle],False)}" fill="none" stroke="#b17a68" opacity=".7" stroke-width="1.2" stroke-linecap="round"/>'])
    clean='\n'.join(art+['</svg>']);(directory/'artwork.svg').write_text(clean,encoding='utf-8')
    rasterize(directory/'artwork.svg',directory/'artwork.png')
    guides=art.copy();colors=('#4b799d','#ab6b6c','#7c8d65','#9875a4','#bd8b4d')
    for (name,digit),color in zip(digits.items(),colors):
        guides.append(f'<path id="skeleton-{name}" d="{path([project(p) for p in digit["points"]],False)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for j,p in enumerate(digit['points']):
            x,y=project(p);guides.append(f'<circle id="joint-{name}-{j}" cx="{x}" cy="{y}" r="3" fill="#fffaf0" stroke="{color}"/>')
    (directory/'construction.svg').write_text('\n'.join(guides+['</svg>']),encoding='utf-8')
    rasterize(directory/'construction.svg',directory/'construction.png')
    (directory/'inputs.json').write_text(json.dumps(dict(spread=1,scope='open planar hand prototype, not a passed studio primitive',
        skeleton={name:dict(points=d['points'],radii=d['radii']) for name,d in digits.items()}),indent=2)+'\n',encoding='utf-8')
    (directory/'source.py').write_bytes(Path(__file__).read_bytes())
    print(directory/'artwork.png')


if __name__=='__main__': render('evidence/studio-hand/03-soft-webs')
