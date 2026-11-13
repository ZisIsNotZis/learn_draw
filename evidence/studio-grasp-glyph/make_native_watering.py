"""Author the first fully native grip replacement from semantic relations.

This is an authoring record. Its output is a normal editable studio scene, with
no SVG import, private macro, runtime teaching/reference data or external mesh.
"""
from pathlib import Path
import copy,math,sys
import numpy as np
from shapely import LineString
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,node_by_id,validate,select
from scripts.studio.components import component_data
from scripts.studio.attachment import resolve_scene,get_anchor,mount_scale
from scripts.studio.grip import construction,transforms
from scripts.studio.render import bundle
HERE=Path(__file__).resolve().parent

def angle(value):return (value+180)%360-180

def build():
    old=read(ROOT/'examples/studio/watering_bound.json');placed=resolve_scene(old);canvas=old['canvas'];unit=min(canvas)
    old_grip=component_data(node_by_id(placed,'carrying-hand'),canvas).center
    goal=np.array(old_grip)+[0,unit*.10]
    body_old=node_by_id(placed,'can-body');normal=np.array(get_anchor(body_old,canvas,'top')['normal'])
    body_axis=np.array(get_anchor(body_old,canvas,'top@.8')['point'])-get_anchor(body_old,canvas,'top@.2')['point']
    root=np.array(get_anchor(node_by_id(placed,'reaching-sleeve'),canvas,'root')['point'])
    scene=copy.deepcopy(old)
    scene['nodes']=[n for n in scene['nodes'] if n['id'] not in ('carrying-hand','grip-thumb','grip-fold','can-handle')]
    body=node_by_id(scene,'can-body');body.pop('attachment');body['at']=copy.deepcopy(body_old['at'])
    grip=dict(id='carrying-hand',kind='grip',intent='a compact closed hand holds the actual top segment of the can handle',
        depth=30,length=node_by_id(old,'gardener')['length']*.36,palette=dict(handle='#b18d3f',handle_ink='#8f7232'))
    base_angle=-math.degrees(math.atan2(body_axis[1],body_axis[0]))
    def wrist_distance(a):
        data=component_data(dict(grip,angle=angle(a)),canvas)
        return np.linalg.norm(goal+np.array(data.mounts['wrist']['point'])-data.mounts['grip']['point']-root)
    grip['angle']=angle(base_angle if wrist_distance(base_angle)<wrist_distance(base_angle+180) else base_angle+180)
    point=get_anchor(grip,canvas,'grip')['point'];grip['at']=dict(anchor='center',offset=((goal-point)/canvas).tolist())
    wrist=np.array(get_anchor(grip,canvas,'wrist')['point'])
    sleeve=node_by_id(scene,'reaching-sleeve');delta=wrist-root
    sleeve.update(length=float(np.linalg.norm(delta)/unit),angle=math.degrees(math.atan2(delta[0],delta[1])),end_cap='flat',depth=31)
    grip.pop('at');grip['attachment']=dict(to='reaching-sleeve',self='wrist',target='tip')
    scene['nodes'].append(grip)
    current=resolve_scene(scene);g=node_by_id(current,'carrying-hand');data=component_data(g,canvas)
    hand=construction(g)[3];_project,shape,_normal,scale,_center=transforms(g,canvas);world=shape(hand)
    hand_width=(hand.bounds[2]-hand.bounds[0])*scale
    centre=np.array(data.mounts['grip']['point'])
    extent=max(np.dot(np.array(p)-centre,-normal) for p in world.exterior.coords)
    desired=centre-normal*(max(extent,hand_width*.65)+hand_width*.22)
    mount=max(('handle_top','handle_bottom'),key=lambda name:np.dot(data.mounts[name]['normal'],-normal))
    source=data.mounts[mount];distance=float(np.dot(desired-np.array(source['point']),source['normal']))
    body.pop('at');body['attachment']=dict(to='carrying-hand',self='top',target=mount,inset=-distance/mount_scale(g,canvas))
    node_by_id(scene,'spout')['angle']=125
    reverse=np.dot(np.array(data.mounts['handle_right']['point'])-data.mounts['handle_left']['point'],body_axis)<0
    pairs=[('left','top@.8'),('right','top@.2')] if reverse else [('left','top@.2'),('right','top@.8')]
    for side,target in pairs:
        scene['nodes'].append(dict(id='handle-'+side,kind='stroke',intent='the '+side+' handle leg follows both the hand and vessel',
            depth=11,thickness=data.dimensions['handle_thickness']/unit,palette=dict(fill='#b18d3f'),bend=0,
            endpoints=dict(root=dict(to='carrying-hand',target='handle_'+side),tip=dict(to='can-body',target=target,inset=.01))))
    validate(scene);ready=resolve_scene(scene)
    legs=[]
    for side in ('left','right'):
        n=node_by_id(ready,'handle-'+side)
        legs.append(LineString([get_anchor(n,canvas,end)['point'] for end in ('root','tip')]))
    if legs[0].crosses(legs[1]):raise ValueError('handle topology is crossed; inspect rotated port pairing before painting')
    return scene

if __name__=='__main__':
    out=HERE/'native-watering-working.json'
    if out.exists():raise SystemExit('working scene exists; choose a fresh record before rebuilding')
    scene=build();write(out,scene)
    bundle(scene,HERE/'07-native-watering',select(scene,'carrying-hand',feature='thumb'))
    print(out,flush=True)
