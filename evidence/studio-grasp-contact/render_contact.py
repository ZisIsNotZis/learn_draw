"""Contact study renderer: flat materials and geometric apparent contours, CPU only."""
from pathlib import Path
import sys,json,math,time
import numpy as np
from shapely import Polygon,LineString,union_all,set_precision,line_merge
from shapely.geometry import mapping
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

def run(data,result,out,name='grasp',yaw=-30,pitch=15,ink_width=.0018,palette=None):
    v,n,j=result['vertices'],result['normals'],result['joints']
    palette=dict(skin='#f1d0b8',ink='#77513f',bar='#bba150',bar_ink='#7b692f')|(palette or {})
    ink=ink_width*2400
    a,b=map(math.radians,(yaw,pitch))
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
        tone=palette['skin']
        # A silhouette is a front/back transition of the actual facets. Smooth
        # lighting normals can disagree and create false interior triangle ink.
        geometric=outward_sign*np.cross(v[ids[1]]-v[ids[0]],v[ids[2]]-v[ids[0]])
        facing.append(float(np.dot(geometric,camera[2]))>0)
        faces.append((tuple(map(tuple,projected[ids])),tone,'skin-'+str(i)))
    for tri in bar_projection:faces.append((tuple(map(tuple,tri)),palette['bar'],'bar'))
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
    bar_full=union_all([Polygon(tri[:,:2]) for tri in bar_projection])
    # Two opaque materials partition the compound projection. Unfragmented hand
    # fill prevents tessellation cracks from turning into white skin highlights;
    # only the depth-computed front rod regions overwrite that skin. Outside the
    # hand projection, the rod is wholly visible by construction.
    bar_visible=union_all(visible.get('bar',[])).union(bar_full.difference(full))
    hand_visible=full.difference(bar_visible)
    svg += [xml_comment('opaque-material-partition: hand projection plus actually frontmost rod'),
        f'<path id="skin-material" d="{polygon_path(full)}" fill="{palette["skin"]}" fill-rule="evenodd"/>',
        f'<path id="rod-material" d="{polygon_path(bar_visible)}" fill="{palette["bar"]}" fill-rule="evenodd"/>',
        '<defs>',xml_comment('visible-ink-apertures: every contour obeys actual object depth'),
        f'<clipPath id="bar-visible"><path id="bar-ink-aperture" d="{polygon_path(bar_visible)}" fill-rule="evenodd"/></clipPath>',
        f'<clipPath id="hand-visible"><path id="hand-ink-aperture" d="{polygon_path(hand_visible)}" fill-rule="evenodd"/></clipPath></defs>',
        xml_comment('bar-contour: cylinder exterior clipped by actual hand/bar depth'),
        f'<path id="rod-exterior" d="{polygon_path(bar_full)}" fill="none" stroke="{palette["bar_ink"]}" stroke-width="{ink*2}" stroke-linejoin="round" clip-path="url(#bar-visible)"/>']
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
        if line.length>.05:lines.append(line)
    merged=line_merge(union_all(lines))
    pieces=list(merged.geoms) if hasattr(merged,'geoms') else [merged]
    d=' '.join(line_path(g.simplify(ink*.06)) for g in pieces if g.length>=ink*1.5)
    svg.extend([xml_comment('apparent-contours: connected visible folds, isolated sub-ink specks omitted'),f'<path id="self-occlusion-contours" d="{d}" fill="none" stroke="{palette["ink"]}" stroke-width="{ink*.72}" stroke-linecap="round" stroke-linejoin="round" clip-path="url(#hand-visible)"/>'])
    parts=list(full.geoms) if hasattr(full,'geoms') else [full]
    contour=' '.join(path(list(p.exterior.coords)[:-1]) for p in parts)
    svg.extend([xml_comment('hand-contour: continuous exterior, including its depth occlusion by the rod'),f'<path id="hand-contour" d="{contour}" fill="none" stroke="{palette["ink"]}" stroke-width="{ink*2}" stroke-linejoin="round" clip-path="url(#hand-visible)"/>','</svg>'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    dest=out/(name+'.svg');dest.write_text('\n'.join(svg),encoding='utf8');rasterize(dest,out/(name+'.png'))
    def point(p):return ((p@camera.T*2400)[:2]+320-center).tolist()
    metadata=dict(vertices=len(v),faces=len(faces),visibility_seconds=time.perf_counter()-started,yaw=yaw,pitch=pitch,ink_width_metres=ink_width,palette=palette,
        mounts=dict(wrist=point(j[0]),grip=point(bar_center),handle_left=point(bar_center-axis*result['half_length']),handle_right=point(bar_center+axis*result['half_length'])),
        hand_bounds=list(full.bounds),footprint=mapping(full.union(bar_full)),projection_scale=2400)
    (out/(name+'-render.json')).write_text(json.dumps(metadata,indent=2),encoding='utf8')
    print(name,len(v),len(faces),round(time.perf_counter()-started,2),flush=True)
    return metadata

if __name__=='__main__':
    import argparse
    from contact import PREVIOUS,OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pose',required=True)
    parser.add_argument('--outdir',required=True)
    parser.add_argument('--bind',help='optional computed refined bind NPZ, e.g. bind-06.npz')
    parser.add_argument('--yaw',type=float,default=-30)
    parser.add_argument('--pitch',type=float,default=15)
    args=parser.parse_args();destination=Path(args.outdir).resolve()
    if destination.exists():raise SystemExit('output exists; choose a fresh render directory')
    data=PREVIOUS['load']()
    if args.bind:data.update(dict(np.load(args.bind)))
    result=dict(np.load(args.pose))
    run(data,result,destination,yaw=args.yaw,pitch=args.pitch)
