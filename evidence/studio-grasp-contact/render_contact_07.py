"""Contact study renderer: flat materials and geometric apparent contours, CPU only."""
from pathlib import Path
import sys,json,math,time
import numpy as np
from shapely import Polygon,LineString,union_all,set_precision
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.vector_visibility import visible_fragments
from scripts.studio.geometry import path,xml_comment
from scripts.studio.render import rasterize

def polygon_path(g):
    if g.is_empty:return ''
    if hasattr(g,'geoms'):return ' '.join(polygon_path(p) for p in g.geoms)
    if g.geom_type!='Polygon':return ''
    return ' '.join([path(list(g.exterior.coords)[:-1])]+[path(list(r.coords)[:-1]) for r in g.interiors])

def run(data,result,out,name='grasp',yaw=-30):
    v,n,j=result['vertices'],result['normals'],result['joints']
    a,b=map(math.radians,(yaw,15))
    right=np.array([math.cos(a),0,-math.sin(a)])
    up=np.array([-math.sin(b)*math.sin(a),math.cos(b),-math.sin(b)*math.cos(a)])
    camera=np.array([right,-up,np.cross(right,up)])
    projected=v@camera.T*2400
    axis=result['axis'];bar_center=result['center'];rbar=result['radius']
    normal=result['palmar'];tangent=result['forward']
    rings=[]
    for end in (-result['half_length'],result['half_length']):
        rings.append([bar_center+axis*end+rbar*(normal*math.cos(a)+tangent*math.sin(a)) for a in np.linspace(0,2*math.pi,24,endpoint=False)])
    bar_triangles=[]
    for k in range(24):
        m=(k+1)%24;a,b=rings
        bar_triangles.extend([(a[k],b[k],b[m]),(a[k],b[m],a[m]),(bar_center-axis*result['half_length'],a[m],a[k]),(bar_center+axis*result['half_length'],b[k],b[m])])
    bar_projection=np.array(bar_triangles)@camera.T*2400
    lo=projected[:,:2].min(axis=0);hi=projected[:,:2].max(axis=0);center=(lo+hi)/2
    projected[:,:2]+=320-center
    bar_projection[:,:,:2]+=320-center
    light=np.array([-.35,.50,1.]);light/=np.linalg.norm(light)
    tones=['#bc8c70','#ddb394','#f1d0b8']
    faces=[]
    facing=[]
    original=data['vertices'][data['faces']]
    cross=np.cross(original[:,1]-original[:,0],original[:,2]-original[:,0])
    signed=np.einsum('ij,ij->i',cross,data['normals'][data['faces']].mean(axis=1))
    outward_sign=1 if np.median(signed)>0 else -1
    for i,ids in enumerate(data['faces']):
        normal=n[ids].mean(axis=0);shade=float(np.dot(normal,light))
        tone='#f1d0b8'
        # A silhouette is a front/back transition of the actual facets. Smooth
        # lighting normals can disagree and create false interior triangle ink.
        geometric=outward_sign*np.cross(v[ids[1]]-v[ids[0]],v[ids[2]]-v[ids[0]])
        facing.append(float(np.dot(geometric,camera[2]))>0)
        faces.append((tuple(map(tuple,projected[ids])),tone,'skin-'+str(i)))
    for tri in bar_projection:faces.append((tuple(map(tuple,tri)),'#bba150','bar'))
    started=time.perf_counter();regions={};visible={}
    for poly,color,part in visible_fragments(faces):
        p=Polygon([q[:2] for q in poly])
        if p.is_valid and p.area>1e-9:
            regions.setdefault(color,[]).append(p);visible.setdefault(part,[]).append(p)
    full=set_precision(union_all([Polygon(projected[ids,:2]) for ids in data['faces'] if Polygon(projected[ids,:2]).area>1e-9]),.0001)
    combined=np.concatenate([projected[:,:2],bar_projection[:,:,:2].reshape(-1,2)])
    low=combined.min(axis=0);high=combined.max(axis=0);span=max(high-low)+75
    ox,oy=(low+high-span)/2
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="{ox} {oy} {span} {span}">',
         f'<rect x="{ox}" y="{oy}" width="{span}" height="{span}" fill="#f6ecdf"/>',
         xml_comment('established-surface: mathematically posed licensed bind mesh, with no texture or generated pixels')]
    for color,polys in regions.items():
        svg.extend([xml_comment('material-'+color[1:]+': one flat material, no automatic mesh edge ink'),f'<path id="material-{color[1:]}" d="{polygon_path(union_all(polys))}" fill="{color}" fill-rule="evenodd"/>'])
    bar_full=union_all([Polygon(tri[:,:2]) for tri in bar_projection])
    svg += [f'<defs><clipPath id="bar-visible"><path d="{polygon_path(union_all(visible.get("bar",[])))}"/></clipPath></defs>',xml_comment('bar-contour: cylinder exterior clipped by actual hand/bar depth'),f'<path d="{polygon_path(bar_full)}" fill="none" stroke="#7b692f" stroke-width="1.7" clip-path="url(#bar-visible)"/>']
    # Recover edge adjacency after UV-seam duplication. Apparent contours are
    # front/back surface transitions, never every projected triangle edge.
    edges={}
    for i,ids in enumerate(data['faces']):
        for u,w in zip(ids,np.roll(ids,-1)):
            keys=[tuple(np.round(data['vertices'][k],7)) for k in (u,w)]
            key=tuple(sorted(keys));edges.setdefault(key,[]).append((i,int(u),int(w)))
    def line_path(g):
        if g.is_empty:return ''
        if hasattr(g,'geoms'):return ' '.join(line_path(p) for p in g.geoms)
        return path(list(g.coords),False) if g.geom_type in ('LineString','LinearRing') else ''
    lines=[]
    for adjacency in edges.values():
        if len(adjacency)!=2 or facing[adjacency[0][0]]==facing[adjacency[1][0]]:continue
        i,u,w=adjacency[0]
        polys=[p for face,_,_ in adjacency for p in visible.get('skin-'+str(face),[])]
        if not polys:continue
        mask=union_all(polys).buffer(.002)
        line=LineString(projected[[u,w],:2]).intersection(mask)
        if line.length>.05:lines.append(line_path(line))
    svg.extend([xml_comment('apparent-contours: only visible front/back skin transitions'),f'<path id="self-occlusion-contours" d="{" ".join(lines)}" fill="none" stroke="#77513f" stroke-width="1.5" stroke-linecap="round"/>'])
    parts=list(full.geoms) if hasattr(full,'geoms') else [full]
    contour=' '.join(path(list(p.exterior.coords)[:-1]) for p in parts)
    svg.extend([xml_comment('hand-contour: projected continuous skin exterior only'),f'<path id="hand-contour" d="{contour}" fill="none" stroke="#77513f" stroke-width="1.7" stroke-linejoin="round"/>','</svg>'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    dest=out/(name+'.svg');dest.write_text('\n'.join(svg),encoding='utf8');rasterize(dest,out/(name+'.png'))
    (out/(name+'-render.json')).write_text(json.dumps(dict(vertices=len(v),faces=len(faces),visibility_seconds=time.perf_counter()-started,yaw=yaw),indent=2),encoding='utf8')
    print(name,len(v),len(faces),round(time.perf_counter()-started,2),flush=True)

if __name__=='__main__':
    from contact import PREVIOUS,OUT
    data=PREVIOUS['load']();result=dict(np.load(OUT/'pose-01.npz'))
    run(data,result,OUT/'01-tangent-phalanges')
