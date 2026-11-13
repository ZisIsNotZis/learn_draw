"""Hand-space cylindrical contact experiment; CPU geometry, no image target.

The established mesh is a fixed licensed bind surface. Poses derive from its bone
lengths, its skin thickness, and a declared rod rather than screen-space points.
"""
from pathlib import Path
import sys,runpy,json,math
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
PREVIOUS=runpy.run_path(str(ROOT/'evidence/studio-grasp/probe_webxr.py'))
OUT=Path(__file__).resolve().parent
CHAINS=[(6,7,8,9),(11,12,13,14),(16,17,18,19),(21,22,23,24)]

def unit(v):
    v=np.array(v,dtype=float);length=np.linalg.norm(v)
    if length<1e-12:raise ValueError('degenerate direction')
    return v/length

def pad_radii(data):
    """Measure bind skin cross-sections at each phalanx midpoint.

    Radius uses the median of the nearby actual skin ring, excluding end caps and
    other digits by dominant bone membership. This is a geometry diagnostic, not
    proof that the deformed pad will stay spherical or preserve this thickness.
    """
    bind=data['bind'];v=data['vertices'];dominant=data['indices'][np.arange(len(v)),data['weights'].argmax(axis=1)]
    records={}
    for chain in [(1,2,3,4)]+CHAINS:
        own=np.isin(dominant,chain)
        for a,b in zip(chain,chain[1:]):
            axis=unit(bind[b]-bind[a]);length=np.linalg.norm(bind[b]-bind[a]);delta=v-bind[a]
            t=delta@axis/length;rad=np.linalg.norm(delta-(delta@axis)[:,None]*axis,axis=1)
            ring=rad[own&(t>.25)&(t<.75)]
            if not len(ring):raise ValueError('no skin ring for '+data['names'][a])
            records[a]=dict(radius=float(np.median(ring)),minimum=float(ring.min()),maximum=float(ring.max()),samples=len(ring),length=float(length))
    return records

def frame(axis,forward):
    forward=unit(forward);side=unit(axis-forward*np.dot(axis,forward))
    return np.column_stack([side,forward,np.cross(side,forward)])

def skin(data,positions,deltas):
    vertices=np.zeros_like(data['vertices']);normals=np.zeros_like(vertices)
    for slot in range(4):
        js=data['indices'][:,slot];weight=data['weights'][:,slot,None]
        vertices+=weight*(np.einsum('nij,nj->ni',deltas[js],data['vertices']-data['bind'][js])+positions[js])
        normals+=weight*np.einsum('nij,nj->ni',deltas[js],data['normals'])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    return vertices,normals

def tangent_step(point,radius,length):
    """The forward counterclockwise tangent of an offset circular contact surface."""
    distance=np.linalg.norm(point)
    if distance<=radius:raise ValueError('joint lies inside the padded contact circle')
    angle=math.atan2(point[1],point[0])+math.acos(radius/distance)
    direction=np.array([-math.sin(angle),math.cos(angle)])
    return point+direction*length,direction,dict(angle_degrees=math.degrees(angle),
        distance_to_contact=math.sqrt(distance*distance-radius*radius),bone_length=length)

def build(data,rod_radius=.011,clearance=.001):
    bind=data['bind'];pads=pad_radii(data);positions=bind.copy();deltas=np.tile(np.eye(3),(25,1,1))
    axis=unit(bind[21]-bind[6]);forward=unit(np.array([0.,1.,0.])-axis*axis[1]);palmar=unit(np.cross(axis,forward))
    middle_length=pads[11]['length'];center=bind[11]-forward*middle_length*.12
    # Palm support is measured near the intended bar row, excluding digit vertices.
    dominant=data['indices'][np.arange(len(data['vertices'])),data['weights'].argmax(axis=1)]
    palm=np.isin(dominant,[0,5,10,15,20]);offset=data['vertices']-center
    band=palm&(np.abs(offset@forward)<rod_radius*1.5)
    if not band.any():raise ValueError('no palm surface near the grip row')
    front=float(np.max(offset[band]@palmar))
    center+=palmar*(front+rod_radius+clearance)
    reports={}
    for chain in CHAINS:
        for a,b in zip(chain,chain[1:]):
            current=positions[a];delta=current-center
            p=np.array([np.dot(delta,forward),np.dot(delta,palmar)])
            radius=rod_radius+pads[a]['radius']+clearance
            endpoint,direction,info=tangent_step(p,radius,pads[a]['length'])
            direction3=forward*direction[0]+palmar*direction[1]
            positions[b]=current+direction3*pads[a]['length']
            deltas[a]=frame(axis,direction3)@frame(axis,bind[b]-bind[a]).T
            reports[data['names'][a]]=info|dict(pad_radius=pads[a]['radius'],offset_radius=radius)
        deltas[chain[-1]]=deltas[chain[-2]]
    # First isolate the four-finger tangent construction; retain the known thumb
    # hypothesis rather than claiming that an unimplemented opposition solver works.
    _,_,old=PREVIOUS['pose'](data,True)
    parent=0
    for step,j in enumerate(range(1,5)):
        positions[j]=positions[parent]+deltas[parent]@(bind[j]-bind[parent])
        turn=PREVIOUS['rotation']('z',-55)@PREVIOUS['rotation']('y',45) if step==0 else PREVIOUS['rotation']('x',(0,35,40,0)[step])
        deltas[j]=deltas[parent]@turn;parent=j
    v,n=skin(data,positions,deltas)
    return dict(vertices=v,normals=n,joints=positions,axis=axis,forward=forward,palmar=palmar,center=center,
                radius=rod_radius,half_length=.085,pads=pads,tangents=reports)

def clip_slab(poly,half_length):
    for sign in (1,-1):
        out=[]
        for a,b in zip(poly,np.roll(poly,-1,axis=0)):
            da=half_length-sign*a[0];db=half_length-sign*b[0]
            if da>=0:out.append(a)
            if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
        poly=np.array(out)
        if not len(poly):break
    return poly

def surface_clearance(data,result):
    """Exact triangle/infinite-cylinder distance after finite axial slab clipping.

    Each clipped triangle's radial projection is a convex polygon. Its nearest
    point to the axis is the origin if enclosed, otherwise a boundary projection.
    This tests skin surface penetration, unlike a vertex-only sample.
    """
    from shapely import Polygon,Point
    basis=np.array([result['axis'],result['forward'],result['palmar']])
    points=(result['vertices']-result['center'])@basis.T
    distances=[];bad=[]
    for i,tri in enumerate(data['faces']):
        poly=clip_slab(points[tri],result['half_length'])
        if len(poly)<3:continue
        shape=Polygon(poly[:,1:]);distance=shape.distance(Point(0,0))
        distances.append(distance-result['radius'])
        if distance<result['radius']-1e-7:bad.append(i)
    axial=points[:,0];radial=np.linalg.norm(points[:,1:],axis=1)
    vertices=(np.abs(axial)<result['half_length'])&(radial<result['radius']-1e-7)
    return dict(minimum_surface_clearance=float(min(distances)),intersecting_triangles=len(bad),
                skin_vertices_inside=int(vertices.sum()),triangle_ids=bad,
                note='Surface test covers the finite rod axial slab; it does not certify hand self-contact or thumb opposition.')

if __name__=='__main__':
    data=PREVIOUS['load']()
    print(json.dumps({data['names'][k]:v for k,v in pad_radii(data).items()},indent=2))
    result=build(data)
    diagnostic=surface_clearance(data,result)
    print(json.dumps(diagnostic,indent=2))
    np.savez(OUT/'pose-01.npz',**{k:result[k] for k in ('vertices','normals','joints','axis','forward','palmar','center','radius','half_length')})
    (OUT/'pose-01.json').write_text(json.dumps(dict(pads=result['pads'],tangents=result['tangents'],diagnostic=diagnostic),indent=2),encoding='utf8')
