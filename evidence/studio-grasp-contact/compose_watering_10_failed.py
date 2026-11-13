"""A real-scene prototype, not a new studio primitive or public atomic insertion.

The fixed hand/rod vector asset comes from the contact study. Its computed wrist
and rod mounts drive sleeve and handle geometry; the reservoir, spout and soil-bound
water remain native studio nodes. No image is read by this generator.
"""
from pathlib import Path
import sys,json,math,copy,xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,validate,node_by_id
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.components import component_data
from scripts.studio.render import drawing,rasterize

HERE=Path(__file__).resolve().parent
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

def place(node,canvas,target,self_anchor='center'):
    node.pop('attachment',None);node['at']=dict(anchor='center')
    current=get_anchor(node,canvas,self_anchor)['point']
    node['at']['offset']=[(target[0]-current[0])/canvas[0],(target[1]-current[1])/canvas[1]]

def chord(node,start,end,canvas):
    delta=np.array(end)-start
    node['length']=float(np.linalg.norm(delta)/min(canvas))
    node['angle']=math.degrees(math.atan2(delta[0],delta[1]))

def run(asset='09-thinner-handle',out='10-watering-first'):
    original=read(ROOT/'examples/studio/watering_bound.json')
    resolved=resolve_scene(original);canvas=original['canvas']
    old_grip=component_data(node_by_id(resolved,'carrying-hand'),canvas).center
    old_body=node_by_id(resolved,'can-body')
    top_left=get_anchor(old_body,canvas,'top@.2')['point'];top_right=get_anchor(old_body,canvas,'top@.8')['point']
    top_normal=np.array(get_anchor(old_body,canvas,'top')['normal'])
    meta=read(HERE/asset/'grasp-render.json');mounts={k:np.array(v) for k,v in meta['mounts'].items()}
    hand_box=meta['hand_bounds'];head=node_by_id(original,'gardener')
    hand_height=head['length']*min(canvas)*.36
    scale=hand_height/(hand_box[3]-hand_box[1])
    source=mounts['handle_right']-mounts['handle_left'];target=np.array(top_right)-top_left
    angle=math.atan2(target[1],target[0])-math.atan2(source[1],source[0])
    def matrix(a):return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
    if np.dot(matrix(angle)@(mounts['wrist']-mounts['grip']),top_normal)<0:angle+=math.pi
    rotate=matrix(angle)
    def point(p):return np.array(old_grip)+scale*rotate@(np.array(p)-mounts['grip'])
    ports={k:point(v) for k,v in mounts.items()}
    hand_width=(hand_box[2]-hand_box[0])*scale
    body_top=ports['grip']-top_normal*hand_width*.9
    scene=copy.deepcopy(original)
    scene['nodes']=[n for n in scene['nodes'] if n['id'] not in ('carrying-hand','grip-thumb','grip-fold','can-handle')]
    body=node_by_id(scene,'can-body');place(body,canvas,body_top,'top')
    # Cloth ends at the observed wrist. The actual sleeve root stays pinned to
    # its shoulder; length/angle are compiler values from these two relations.
    sleeve=node_by_id(scene,'reaching-sleeve')
    root=get_anchor(node_by_id(resolved,'reaching-sleeve'),canvas,'root')['point']
    chord(sleeve,root,ports['wrist'],canvas)
    sleeve['end_cap']='flat';sleeve['depth']=31
    placed=resolve_scene(scene)
    for side,anchor in [('left','top@.2'),('right','top@.8')]:
        end=np.array(get_anchor(node_by_id(placed,'can-body'),canvas,anchor)['point'])
        start=ports['handle_'+side]
        leg=dict(id='handle-'+side,kind='stroke',intent='the '+side+' leg connects the actual gripped bar to the vessel',
            depth=11,palette=dict(fill='#b18d3f'),thickness=.006*2*2400*scale/min(canvas),
            bend=.04 if side=='left' else -.04,
            attachment=dict(to='can-body',self='tip',target=anchor,inset=.01))
        chord(leg,start,end,canvas);scene['nodes'].append(leg)
    validate(scene)
    doc=ET.fromstring(drawing(scene))
    grip=ET.Element('{'+NS+'}g',dict(id='experimental-closed-grip'))
    grip.append(ET.Comment('closed-grip: computed hand/rod contact study, wrist meets sleeve and bar ends meet handle legs'))
    # SVG asset coordinates are compiled output, not an authoring interface.
    translate=np.array(old_grip)-scale*rotate@mounts['grip']
    grip.set('transform',f'matrix({scale*rotate[0,0]} {scale*rotate[1,0]} {scale*rotate[0,1]} {scale*rotate[1,1]} {translate[0]} {translate[1]})')
    asset_doc=ET.parse(HERE/asset/'grasp.svg').getroot()
    for element in list(asset_doc):
        if element.tag.endswith('rect'):continue
        element=copy.deepcopy(element)
        for part in element.iter():
            sid=part.get('id')
            if sid:
                if sid=='rod-material':part.set('fill','#b18d3f')
                if sid=='rod-exterior':part.set('stroke','#8f7232')
                part.set('id','carrying-grip--'+sid)
            for key,value in list(part.attrib.items()):
                if 'url(#' in value:part.set(key,value.replace('url(#','url(#carrying-grip--'))
        grip.append(element)
    cuff=next(e for e in doc if e.get('id')=='reaching-sleeve')
    doc.insert(list(doc).index(cuff),grip)
    out=HERE/out;out.mkdir(parents=True,exist_ok=True)
    (out/'artwork.svg').write_text(ET.tostring(doc,encoding='unicode'),encoding='utf8')
    rasterize(out/'artwork.svg',out/'artwork.png')
    write(out/'base.scene.json',scene)
    write(out/'construction.json',dict(status='composition prototype; macro not a shipped studio kind',asset=asset,
        hand_height=hand_height,hand_width=hand_width,ports={k:v.tolist() for k,v in ports.items()},body_top=body_top.tolist(),
        hand_matrix=dict(scale=scale,rotation_degrees=math.degrees(angle),translation=translate.tolist()),
        native_node_count=len(scene['nodes']),base_scene_alone_is_incomplete=True))
    print(out,flush=True)

if __name__=='__main__':run()
