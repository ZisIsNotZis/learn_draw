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
    bar_axis=unit(bind[21]-bind[6])
    records={}
    for chain in [(1,2,3,4)]+CHAINS:
        own=np.isin(dominant,chain)
        for a,b in zip(chain,chain[1:]):
            axis=unit(bind[b]-bind[a]);length=np.linalg.norm(bind[b]-bind[a]);delta=v-bind[a]
            t=delta@axis/length;rad=np.linalg.norm(delta-(delta@axis)[:,None]*axis,axis=1)
            mask=own&(t>.25)&(t<.75)
            ring=rad[mask]
            if not len(ring):raise ValueError('no skin ring for '+data['names'][a])
            inward=frame(bar_axis,axis)[:,2]
            # The frame's palmar normal becomes the cylinder-facing side after
            # tangent placement. An oval pad needs its actual directional support,
            # not the median of its round-the-bone radii.
            support=float(np.max(delta[mask]@inward))
            records[a]=dict(radius=float(np.median(ring)),inward_support=support,minimum=float(ring.min()),maximum=float(ring.max()),samples=len(ring),length=float(length))
    return records

def frame(axis,forward):
    forward=unit(forward);side=unit(axis-forward*np.dot(axis,forward))
    return np.column_stack([side,forward,np.cross(side,forward)])

def joint_palmar_normals(data):
    """WebXR joint -Y is outward from the palm; retain the asset's actual roll.

    https://www.w3.org/TR/webxr-hand-input-1/#xrjointspace
    Inferring thumb roll from the rod axis is wrong even if its bone points in the
    correct direction. Reconstruct the same canonical basis as the fixed importer.
    """
    nodes=data['gltf']['nodes'];bind=np.array([n['translation'] for n in nodes[:25]])
    forward=unit(bind[11]-bind[0]);side=bind[21]-bind[6];side=unit(side-forward*np.dot(side,forward))
    basis=np.array([side,forward,-np.cross(side,forward)])
    normals=[]
    for node in nodes[:25]:
        x,y,z,w=node['rotation']
        normals.append(np.array([-(2*x*y-2*z*w),-(1-2*x*x-2*z*z),-(2*y*z+2*x*w)])@basis.T)
    return np.array(normals)

def palmar_frame(forward,normal):
    forward=unit(forward);normal=unit(normal-forward*np.dot(normal,forward))
    return np.column_stack([np.cross(forward,normal),forward,normal])

def bind_frame(data,a,b):
    return palmar_frame(data['bind'][b]-data['bind'][a],joint_palmar_normals(data)[a])

def skin(data,positions,deltas):
    vertices=np.zeros_like(data['vertices']);normals=np.zeros_like(vertices)
    for slot in range(data['indices'].shape[1]):
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

def oppose_thumb(data,positions,deltas,pads,axis,forward,palmar):
    """Two-link CMC/MCP reach plus a declared distal contact direction.

    The thumb pad opposes the front of the curled index/middle tips. This is a
    geometric target hypothesis; actual deformed skin contact is checked later.
    """
    bind=data['bind'];base=bind[1]
    finger_radius=(pads[8]['radius']+pads[13]['radius'])/2
    contact=(positions[9]+positions[14])/2+palmar*(finger_radius+pads[3]['radius'])-forward*finger_radius*.5
    distal_direction=unit(axis*.6+forward*.6+palmar*.45)
    l0,l1=pads[1]['length'],pads[2]['length']
    to_contact=contact-base;contact_distance=np.linalg.norm(to_contact);toward=unit(to_contact)
    effective_distal=pads[3]['length']*.7
    required=(contact_distance**2+effective_distal**2-(l0+l1-1e-5)**2)/(2*contact_distance*effective_distal)
    if required>1:raise ValueError('thumb contact is outside its full reachable pad envelope')
    # Closest distal direction within the reach cone. Preserve the intended
    # cross-finger direction whenever the actual hand lengths permit it.
    if np.dot(distal_direction,toward)<required:
        side=unit(distal_direction-toward*np.dot(distal_direction,toward))
        distal_direction=toward*required+side*math.sqrt(1-required*required)
    target=contact+distal_direction*pads[3]['length']*.3
    wrist=contact-distal_direction*effective_distal
    delta=wrist-base;distance=np.linalg.norm(delta);direction=unit(delta)
    if not abs(l0-l1)<distance<l0+l1:
        raise ValueError('thumb target is outside the two-link reach')
    along=(l0*l0-l1*l1+distance*distance)/(2*distance)
    height=math.sqrt(max(0,l0*l0-along*along))
    pole=-axis*.7+palmar*.7;pole=unit(pole-direction*np.dot(pole,direction))
    elbow=base+direction*along+pole*height
    for a,b,p,q in [(1,2,base,elbow),(2,3,elbow,wrist),(3,4,wrist,target)]:
        positions[a]=p;positions[b]=q
        deltas[a]=palmar_frame(q-p,-palmar)@bind_frame(data,a,b).T
    deltas[4]=deltas[3]
    return dict(target=target.tolist(),contact=contact.tolist(),middle_index_tip_contact=True,reach=float(distance),
                maximum_reach=l0+l1,contact_solved=False)

def build(data,rod_radius=.011,clearance=.001,reserves=None):
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
            radius=rod_radius+pads[a]['radius']+clearance+(reserves or {}).get(a,0)
            endpoint,direction,info=tangent_step(p,radius,pads[a]['length'])
            direction3=forward*direction[0]+palmar*direction[1]
            positions[b]=current+direction3*pads[a]['length']
            deltas[a]=frame(axis,direction3)@bind_frame(data,a,b).T
            reports[data['names'][a]]=info|dict(pad_radius=pads[a]['radius'],reserve=(reserves or {}).get(a,0),offset_radius=radius)
        deltas[chain[-1]]=deltas[chain[-2]]
    thumb=oppose_thumb(data,positions,deltas,pads,axis,forward,palmar)
    v,n=skin(data,positions,deltas)
    return dict(vertices=v,normals=n,joints=positions,axis=axis,forward=forward,palmar=palmar,center=center,
                radius=rod_radius,half_length=.085,pads=pads,tangents=reports,thumb=thumb)

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
    """Radial clearance after finite axial slab clipping, not a full cylinder SDF.

    Each clipped triangle's radial projection is a convex polygon. Its nearest
    point to the axis is the origin if enclosed, otherwise a boundary projection.
    This tests strict rod-volume/skin intersection, unlike a vertex-only sample.
    A cap-only touch is not penetration. The returned radial overlap is not a
    Euclidean penetration depth near a cap, nor an exterior distance to the cap.
    """
    from shapely import Polygon,Point
    basis=np.array([result['axis'],result['forward'],result['palmar']])
    points=(result['vertices']-result['center'])@basis.T
    distances=[];bad=[];collisions=[]
    for i,tri in enumerate(data['faces']):
        poly=clip_slab(points[tri],result['half_length'])
        if len(poly)<3:continue
        if np.all(np.abs(poly[:,0]-result['half_length'])<1e-10) or np.all(np.abs(poly[:,0]+result['half_length'])<1e-10):continue
        shape=Polygon(poly[:,1:]);distance=shape.distance(Point(0,0))
        distances.append(distance-result['radius'])
        if distance<result['radius']-1e-7:
            bad.append(i)
            weights=np.zeros(25)
            for vertex in tri:
                for joint,weight in zip(data['indices'][vertex],data['weights'][vertex]):weights[joint]+=weight
            collisions.append(dict(triangle=i,dominant_bone=int(weights.argmax()),penetration=float(result['radius']-distance)))
    axial=points[:,0];radial=np.linalg.norm(points[:,1:],axis=1)
    vertices=(np.abs(axial)<result['half_length'])&(radial<result['radius']-1e-7)
    return dict(minimum_radial_clearance_in_slab=float(min(distances)) if distances else None,intersecting_triangles=len(bad),
                skin_vertices_inside=int(vertices.sum()),triangle_ids=bad,collisions=collisions,
                note='Strict rod-volume/skin-surface intersection in the finite axial slab; radial clearance is not a full finite-cylinder signed distance. Hand self-contact and thumb opposition are not certified.')

def solve(data,rod_radius=.011,clearance=.001):
    """Bounded collision response on the actual deformed skin, not on an image.

    A median capsule initializes contact. If its real skin enters the rod, reserve
    extra space for the responsible phalanx and reconstruct the tangent chain.
    Keep the iterations and reject unsupported joint/palm collisions explicitly.
    """
    reserves={};iterations=[];pads=pad_radii(data)
    for step in range(12):
        result=build(data,rod_radius,clearance,reserves)
        diagnostic=surface_clearance(data,result)
        iterations.append(dict(step=step,reserves=dict(reserves),diagnostic=diagnostic))
        if not diagnostic['collisions']:
            result['iterations']=iterations;result['diagnostic']=diagnostic
            return result
        needed={}
        for collision in diagnostic['collisions']:
            joint=collision['dominant_bone']
            if joint not in pads or joint<=4:raise ValueError('collision is outside a supported finger phalanx: '+data['names'][joint])
            needed[joint]=max(needed.get(joint,0),collision['penetration'])
        for joint,penetration in needed.items():
            reserves[joint]=reserves.get(joint,0)+penetration+1e-5
            if reserves[joint]>pads[joint]['maximum']-pads[joint]['radius']+clearance:
                raise ValueError('collision response exceeds the measured skin envelope')
    raise ValueError('contact response did not converge; do not export a grasp')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',required=True)
    parser.add_argument('--radius',type=float,default=.011)
    args=parser.parse_args();destination=Path(args.outdir).resolve()
    if destination.exists():raise SystemExit('output exists; preserve frozen studies and choose a fresh directory')
    data=PREVIOUS['load']()
    result=solve(data,rod_radius=args.radius)
    diagnostic=result['diagnostic']
    print(json.dumps(diagnostic,indent=2))
    destination.mkdir(parents=True)
    np.savez_compressed(destination/'pose.npz',**{k:result[k] for k in ('vertices','normals','joints','axis','forward','palmar','center','radius','half_length')})
    (destination/'diagnostic.json').write_text(json.dumps(dict(pads=result['pads'],tangents=result['tangents'],thumb=result['thumb'],diagnostic=diagnostic,iterations=result['iterations']),indent=2),encoding='utf8')
