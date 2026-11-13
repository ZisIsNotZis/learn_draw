"""A CPU vector grasp experiment: procedural curved tubes around a declared cylindrical prop.
No mesh edge is automatically ink. The existing opaque depth solver decides every visible fragment.
"""
import sys,math,time,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from shapely import Polygon,union_all
from scripts.vector_visibility import visible_fragments
from scripts.studio.geometry import xml_comment,path
from scripts.studio.render import rasterize
OUT=Path('evidence/studio-grasp/01-cylindrical');OUT.mkdir(parents=True,exist_ok=True)
SKIN='#edc8ac';INK='#77513f';BAR='#bba150';CREASE='#bd8d73'

def unit(x):
    x=np.array(x,dtype=float);return x/np.linalg.norm(x)

def tube(points,radius,name,radial=8):
    pts=np.array(points);normals=[];rings=[];normal=None
    for i,p in enumerate(pts):
        tangent=unit(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)])
        trial=np.array([1.,0,0]) if normal is None else normal
        normal=trial-tangent*np.dot(trial,tangent)
        if np.linalg.norm(normal)<1e-5:
            trial=np.array([0.,1.,0]);normal=trial-tangent*np.dot(trial,tangent)
        normal=unit(normal);binormal=np.cross(tangent,normal);r=radius*(1-.12*i/(len(pts)-1))
        rings.append([p+r*(normal*math.cos(a)+binormal*math.sin(a)) for a in np.linspace(0,2*math.pi,radial,endpoint=False)])
    faces=[]
    for a,b in zip(rings,rings[1:]):
        for j in range(radial):
            k=(j+1)%radial;faces += [(a[j],b[j],b[k]),(a[j],b[k],a[k])]
    for i,ring in [(0,rings[0]),(-1,rings[-1])]:
        for j in range(radial):faces.append((pts[i],ring[j],ring[(j+1)%radial]))
    return [(tri,SKIN,name) for tri in faces]

def ellipsoid(center,radii,name,rings=8,radial=12):
    c=np.array(center);r=np.array(radii);mesh=[]
    for phi in np.linspace(-math.pi/2,math.pi/2,rings+1):
        mesh.append([c+r*np.array([math.cos(phi)*math.cos(a),math.sin(phi),math.cos(phi)*math.sin(a)]) for a in np.linspace(0,2*math.pi,radial,endpoint=False)])
    f=[]
    for a,b in zip(mesh,mesh[1:]):
        for j in range(radial):
            k=(j+1)%radial
            for tri in ((a[j],b[j],b[k]),(a[j],b[k],a[k])):
                if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-9:f.append((tri,SKIN,name))
    return f

def smooth(points,n=14):
    p=np.array(points);ts=np.array([0]+list(np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))));ts/=ts[-1]
    tangents=[]
    for i in range(len(p)):
        lo=max(0,i-1);hi=min(len(p)-1,i+1);tangents.append((p[hi]-p[lo])/(ts[hi]-ts[lo]))
    out=[]
    for t in np.linspace(0,1,n):
        i=next((i for i in range(len(ts)-1) if t<=ts[i+1]),len(ts)-2);d=ts[i+1]-ts[i];s=(t-ts[i])/d
        out.append((2*s**3-3*s*s+1)*p[i]+(s**3-2*s*s+s)*d*tangents[i]+(-2*s**3+3*s*s)*p[i+1]+(s**3-s*s)*d*tangents[i+1])
    return out

def build():
    faces=ellipsoid((0,-.08,-.05),(.43,.55,.14),'palm')
    faces+=tube([(0,-.83,-.045),(0,-.48,-.045)],.25,'wrist',12)
    digits={};rbar=.13;cy=.35;cz=.23
    for name,x,r,start,end in zip(('index','middle','ring','little'),(-.315,-.105,.105,.315),(.095,.10,.095,.08),(-60,-52,-56,-65),(210,230,220,190)):
        radius=rbar+r
        pts=[(x,cy+radius*math.cos(a),cz+radius*math.sin(a)) for a in np.linspace(math.radians(start),math.radians(end),13)]
        faces+=tube(pts,r,name);digits[name]=(x,r,cy,cz,radius)
    thumb=smooth([(-.37,-.18,.05),(-.49,.10,.20),(-.22,.28,.52),(.12,.13,.53)])
    faces+=tube(thumb,.115,'thumb',10)
    bar=tube([(-1.05,cy,cz),(1.05,cy,cz)],rbar,'bar',12)
    faces += [(tri,BAR,name) for tri,_,name in bar]
    return faces,digits,thumb

def project(p,yaw=22,pitch=15):
    a,b=map(math.radians,(yaw,pitch));right=np.array([math.cos(a),0,-math.sin(a)]);up=np.array([-math.sin(b)*math.sin(a),math.cos(b),-math.sin(b)*math.cos(a)]);depth=np.cross(right,up)
    return (320+235*np.dot(right,p),310-235*np.dot(up,p),235*np.dot(depth,p))

def polygons_path(shape):
    if shape.is_empty:return ''
    parts=list(shape.geoms) if hasattr(shape,'geoms') else [shape];out=[]
    for p in parts:
        if p.geom_type!='Polygon':continue
        out.append(path(list(p.exterior.coords)[:-1]))
        out.extend(path(list(r.coords)[:-1]) for r in p.interiors)
    return ' '.join(out)

def run(yaw=22,pitch=15,name='default'):
    faces,digits,thumb=build();projected=[(tuple(project(p,yaw,pitch) for p in tri),color,part) for tri,color,part in faces]
    t=time.perf_counter();regions={}
    for poly,color,part in visible_fragments(projected):
        q=Polygon([(p[0],p[1]) for p in poly])
        if q.is_valid and q.area>1e-8:regions.setdefault(part,[]).append(q)
    shapes={k:union_all(v) for k,v in regions.items()};skin=union_all([g for k,g in shapes.items() if k!='bar'])
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="0 0 640 640">','<rect width="640" height="640" fill="#f6ecdf"/>',xml_comment('bar: declared cylindrical prop, visible parts determined by depth'),f'<path id="bar" d="{polygons_path(shapes.get("bar",Polygon()))}" fill="{BAR}" stroke="#7b692f" stroke-width="1.5" fill-rule="evenodd"/>',xml_comment('hand: merged visible skin removes internal mesh edges'),f'<path id="hand" d="{polygons_path(skin)}" fill="{SKIN}" stroke="{INK}" stroke-width="1.7" stroke-linejoin="round" fill-rule="evenodd"/>']
    for digit,(x,r,cy,cz,R) in digits.items():
        a=math.radians(105);p=np.array([x,cy+R*math.cos(a),cz+R*math.sin(a)])
        line=[project(p+[t*r*.62,0,.005],yaw,pitch)[:2] for t in np.linspace(-1,1,9)]
        svg += [xml_comment(digit+'-fold: one intentional palmar flexion cue clipped to the actually visible digit'),f'<defs><clipPath id="clip-{digit}"><path d="{polygons_path(shapes.get(digit,Polygon()))}" fill-rule="evenodd"/></clipPath></defs>',f'<path id="{digit}-fold" d="{path(line,False)}" fill="none" stroke="{CREASE}" stroke-width="1.4" stroke-linecap="round" clip-path="url(#clip-{digit})"/>']
    svg.append('</svg>');p=OUT/(name+'.svg');p.write_text('\n'.join(svg),encoding='utf-8');rasterize(p,OUT/(name+'.png'))
    (OUT/(name+'.json')).write_text(json.dumps(dict(faces=len(faces),visibility_seconds=time.perf_counter()-t,yaw=yaw,pitch=pitch,parts=list(shapes)),indent=2))
    print(name,'faces',len(faces),'seconds',round(time.perf_counter()-t,2))

if __name__=='__main__':run()
