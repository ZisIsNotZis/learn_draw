"""CPU-only articulated mesh study; third-party bind mesh remains byte-identical.

This tests an established continuous hand surface instead of independent tubes.
No target image, diffusion model, GPU, or texture is used. It is not a studio preset.
"""
from pathlib import Path
import sys, json, struct, math, time
import numpy as np
from shapely import Polygon, LineString, union_all, set_precision

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.vector_visibility import visible_fragments
from scripts.studio.geometry import path,xml_comment
from scripts.studio.render import rasterize

HERE=Path(__file__).resolve().parent
ASSET=HERE/'third-party/webxr-generic-hand-1.0.20/right.glb'
OUT=HERE/'11-mesh-contact-contours'

def load():
    raw=ASSET.read_bytes()
    magic,version,total=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and total==len(raw)
    size,kind=struct.unpack_from('<II',raw,12)
    assert kind==0x4e4f534a
    g=json.loads(raw[20:20+size]);offset=20+size
    size,kind=struct.unpack_from('<II',raw,offset)
    assert kind==0x004e4942
    binary=raw[offset+8:offset+8+size]
    def accessor(i):
        a=g['accessors'][i];v=g['bufferViews'][a['bufferView']]
        dtype={5121:'u1',5123:'<u2',5126:'<f4'}[a['componentType']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        assert 'byteStride' not in v and 'sparse' not in a
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        return np.frombuffer(binary,dtype=dtype,count=a['count']*width,offset=start).reshape(-1,width).astype(float)
    p=g['meshes'][0]['primitives'][0];attrs=p['attributes']
    joints=g['skins'][0]['joints'];nodes=[g['nodes'][i] for i in joints]
    positions=accessor(attrs['POSITION']);normals=accessor(attrs['NORMAL'])
    weights=accessor(attrs['WEIGHTS_0']);indices=accessor(attrs['JOINTS_0']).astype(int)
    faces=accessor(p['indices']).astype(int).reshape(-1,3)
    bind=np.array([n['translation'] for n in nodes])
    inverse_bind=accessor(g['skins'][0]['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
    matrices=[]
    for node in nodes:
        x,y,z,w=node['rotation'];m=np.eye(4)
        m[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],
                            [2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],
                            [2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(node.get('scale',[1,1,1]))
        m[:3,3]=node['translation'];matrices.append(m)
    bind_error=float(np.max(np.abs(np.array(matrices)@inverse_bind-np.eye(4))))
    assert bind_error<1e-6, 'delta skinning requires the declared glTF pose to be the actual bind pose'
    assert np.max(np.abs(weights.sum(axis=1)-1))<1e-6
    # A hand ruler is recovered from semantic skeleton landmarks.
    origin=bind[0];forward=bind[11]-origin;forward/=np.linalg.norm(forward)
    lateral=bind[21]-bind[6];lateral-=forward*np.dot(lateral,forward);lateral/=np.linalg.norm(lateral)
    palmar=-np.cross(lateral,forward);basis=np.array([lateral,forward,palmar])
    return dict(vertices=(positions-origin)@basis.T,normals=normals@basis.T,
                bind=(bind-origin)@basis.T,weights=weights,indices=indices,faces=faces,
                names=[n['name'] for n in nodes],gltf=g,bind_matrix_error=bind_error)

def rotation(axis,degrees):
    t=math.radians(degrees);c,s=math.cos(t),math.sin(t)
    if axis=='x':return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if axis=='y':return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

def pose(data,closed):
    bind=data['bind'];positions=bind.copy();deltas=np.tile(np.eye(3),(25,1,1))
    for chain in [range(1,5),range(5,10),range(10,15),range(15,20),range(20,25)]:
        parent=0
        for step,j in enumerate(chain):
            positions[j]=positions[parent]+deltas[parent]@(bind[j]-bind[parent])
            turn=np.eye(3)
            if closed:
                if j<=4:
                    turn=rotation('z',-55)@rotation('y',45) if step==0 else rotation('x',(0,35,40,0)[step])
                else:
                    turn=rotation('x',(0,55,90,50,0)[step])
            deltas[j]=deltas[parent]@turn;parent=j
    vertices=np.zeros_like(data['vertices']);normals=np.zeros_like(vertices)
    for slot in range(4):
        js=data['indices'][:,slot];weight=data['weights'][:,slot,None]
        vertices+=weight*(np.einsum('nij,nj->ni',deltas[js],data['vertices']-bind[js])+positions[js])
        normals+=weight*np.einsum('nij,nj->ni',deltas[js],data['normals'])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    if not closed:
        assert np.max(np.abs(vertices-data['vertices']))<1e-7
    return vertices,normals,positions

def polygon_path(g):
    if g.is_empty:return ''
    if hasattr(g,'geoms'):return ' '.join(polygon_path(p) for p in g.geoms)
    if g.geom_type!='Polygon':return ''
    return ' '.join([path(list(g.exterior.coords)[:-1])]+[path(list(r.coords)[:-1]) for r in g.interiors])

def run(closed=False,yaw=-30):
    data=load();v,n,j=pose(data,closed)
    a,b=map(math.radians,(yaw,15))
    right=np.array([math.cos(a),0,-math.sin(a)])
    up=np.array([-math.sin(b)*math.sin(a),math.cos(b),-math.sin(b)*math.cos(a)])
    camera=np.array([right,-up,np.cross(right,up)])
    projected=v@camera.T*2400
    # The contact axis follows the knuckle row; its offset is a hand-space grip
    # hypothesis, not a screen-coordinate patch or a solved contact claim.
    axis=j[21]-j[6];axis/=np.linalg.norm(axis)
    bar_center=j[11]+np.array([0,-.005,.030])
    normal=np.cross(axis,[0,1,0]);normal/=np.linalg.norm(normal)
    tangent=np.cross(axis,normal);rbar=.011
    rings=[]
    for end in (-.085,.085):
        rings.append([bar_center+axis*end+rbar*(normal*math.cos(a)+tangent*math.sin(a)) for a in np.linspace(0,2*math.pi,24,endpoint=False)])
    bar_triangles=[]
    for k in range(24):
        m=(k+1)%24;a,b=rings
        bar_triangles.extend([(a[k],b[k],b[m]),(a[k],b[m],a[m]),(bar_center-axis*.085,a[m],a[k]),(bar_center+axis*.085,b[k],b[m])])
    bar_projection=np.array(bar_triangles)@camera.T*2400
    lo=projected[:,:2].min(axis=0);hi=projected[:,:2].max(axis=0);center=(lo+hi)/2
    projected[:,:2]+=320-center
    bar_projection[:,:,:2]+=320-center
    light=np.array([-.35,.50,1.]);light/=np.linalg.norm(light)
    tones=['#bc8c70','#ddb394','#f1d0b8']
    faces=[]
    facing=[]
    for i,ids in enumerate(data['faces']):
        normal=n[ids].mean(axis=0);shade=float(np.dot(normal,light))
        tone='#f1d0b8'
        facing.append(float(np.dot(normal,camera[2]))>0)
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
    OUT.mkdir(parents=True,exist_ok=True);name='closed' if closed else 'open'
    dest=OUT/(name+'.svg');dest.write_text('\n'.join(svg),encoding='utf8');rasterize(dest,OUT/(name+'.png'))
    axial=(v-bar_center)@axis
    radial=np.linalg.norm(v-bar_center-axial[:,None]*axis,axis=1)
    inside=(np.abs(axial)<.085)&(radial<rbar)
    (OUT/(name+'.json')).write_text(json.dumps(dict(vertices=len(v),faces=len(faces),seconds=time.perf_counter()-started,closed=closed,yaw=yaw,joints=dict(zip(data['names'],j.tolist())),bind_matrix_error=data['bind_matrix_error'],
        bar=dict(center=bar_center.tolist(),axis=axis.tolist(),radius=rbar,half_length=.085,skin_vertices_inside=int(inside.sum()),max_vertex_penetration=float(np.max(np.where(inside,rbar-radial,0))),contact_solved=False),
        note='Vertex penetration is a diagnostic only; zero would not prove surface clearance or enclosure.'),indent=2),encoding='utf8')
    print(name,len(v),len(faces),round(time.perf_counter()-started,2),flush=True)

if __name__=='__main__':
    run(True)
