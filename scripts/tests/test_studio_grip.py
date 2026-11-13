"""A bounded illustrative grip must be operable, relational and recoverable."""
import copy,json,math,subprocess,sys,tempfile,unittest
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import resvg_py
from shapely import Polygon
from scripts.studio.__main__ import default_scene
from scripts.studio.grip import grip_data
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.model import accept,fingerprint,node_by_id,parameter_preview,parameters_preview,read,select,undo,validate,write
from scripts.studio.render import drawing,bundle

ROOT=Path(__file__).resolve().parents[2]

def pixels(scene):return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(scene)))).convert('RGBA'))

class IllustrativeGrip(unittest.TestCase):
    def test_reference_free_in_fresh_directory(self):
        code="""import sys
sys.path[:0]=[sys.argv[1],sys.argv[1]+'/scripts']
def audit(event,args):
    if event=='open' and isinstance(args[0],str) and args[0].lower().endswith(('.jpg','.jpeg','.png','.svg','.glb')):
        raise RuntimeError('unexpected drawing/mesh input: '+args[0])
sys.addaudithook(audit)
import renderer,cv2
from PIL import Image
def forbidden(*a,**k):raise RuntimeError('unexpected browser or image input')
renderer.chrome_path=forbidden;cv2.imread=forbidden;Image.open=forbidden
from scripts.studio.__main__ import default_scene
from scripts.studio.render import drawing
s=drawing(default_scene('grip'))
assert '--thumb-material' in s and '<image' not in s
"""
        with tempfile.TemporaryDirectory() as folder:
            r=subprocess.run([sys.executable,'-c',code,str(ROOT)],cwd=folder,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)

    def test_thumb_refinement_preserves_mounts_materials_and_other_object(self):
        scene=default_scene('grip')
        scene['nodes'].append(dict(id='other',kind='shape',intent='a separate quiet mass',depth=-1,length=.12,at=dict(anchor='upper_left')))
        before=copy.deepcopy(scene);node=scene['nodes'][0];data=grip_data(node,scene['canvas'])
        candidate=parameter_preview(scene,select(scene,node['id'],feature='thumb'),'thumb_reach',.72,'tuck the thumb tip while keeping the wrist and handle')
        changed=grip_data(candidate['scene']['nodes'][0],scene['canvas'])
        self.assertEqual(data.mounts,changed.mounts)
        self.assertEqual(fingerprint(scene),fingerprint(before))
        self.assertEqual(scene['nodes'][1],candidate['scene']['nodes'][1])
        def materials(svg):
            root=ET.fromstring('<svg>'+svg+'</svg>')
            return {e.get('id'):e.get('d') for e in root.iter() if (e.get('id') or '').endswith('-material')}
        a,b=materials(data.svg),materials(changed.svg)
        for name in ('palm','little','ring','middle','index','handle'):
            self.assertEqual(a[node['id']+'--'+name+'-material'],b[node['id']+'--'+name+'-material'])
        self.assertNotEqual(a[node['id']+'--thumb-material'],b[node['id']+'--thumb-material'])
        diff=np.any(pixels(scene)!=pixels(candidate['scene']),axis=2)
        ys,xs=np.where(diff);self.assertGreater(len(xs),0)
        old=data.features['thumb']['bounds'];new=changed.features['thumb']['bounds']
        box=[min(old[0],new[0])-2,min(old[1],new[1])-2,max(old[2],new[2])+2,max(old[3],new[3])+2]
        self.assertTrue(xs.min()>=box[0] and xs.max()<=box[2] and ys.min()>=box[1] and ys.max()<=box[3])

    def test_rotation_mirror_and_real_footprint(self):
        scene=default_scene('grip');node=scene['nodes'][0];base=grip_data(node,[640,640]);center=np.array(base.center)
        rotated=grip_data(dict(node,angle=90),[640,640]);mirrored=grip_data(dict(node,thumb_side='left'),[640,640])
        for name in base.mounts:
            delta=np.array(base.mounts[name]['point'])-center
            self.assertTrue(np.allclose(rotated.mounts[name]['point'],center+[delta[1],-delta[0]]))
            self.assertTrue(np.allclose(mirrored.mounts[name]['point'],center+[-delta[0],delta[1]]))
        for data in (base,rotated,mirrored):
            shape=Polygon(data.outline);self.assertTrue(shape.is_valid and not shape.interiors)
            from shapely import Point
            self.assertLess(shape.boundary.distance(Point(data.mounts['wrist']['point'])),1e-6)
            for name in ('handle_left','handle_right'):self.assertTrue(shape.covers(Point(data.mounts[name]['point'])))

    def test_two_target_connection_follows_span_and_undo_restores_pixels(self):
        scene=default_scene('grip');scene['nodes'][0].update(length=.25,depth=2)
        scene['nodes'] += [dict(id='destination',kind='shape',intent='a support separate from the hand',length=.12,depth=0,at=dict(anchor='center',offset=[.25,.25])),
            dict(id='connector',kind='stroke',intent='connect the held segment to its support',depth=1,thickness=.012,
                 endpoints=dict(root=dict(to='carrying-grip',target='handle_right'),tip=dict(to='destination',target='top')))]
        validate(scene);before=resolve_scene(scene);image=pixels(scene)
        candidate=parameter_preview(scene,select(scene,'carrying-grip',feature='handle'),'handle_span',2.2,'extend the exposed handle while preserving its destination')
        after=resolve_scene(candidate['scene'])
        for placed in (before,after):
            root=get_anchor(node_by_id(placed,'connector'),scene['canvas'],'root')['point']
            target=get_anchor(node_by_id(placed,'carrying-grip'),scene['canvas'],'handle_right')['point']
            self.assertTrue(np.allclose(root,target))
        for name in ('wrist','grip'):
            self.assertEqual(get_anchor(node_by_id(before,'carrying-grip'),scene['canvas'],name),get_anchor(node_by_id(after,'carrying-grip'),scene['canvas'],name))
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'work.json';write(p,scene);candidate['status']='ready';accept(p,candidate);undo(p)
            self.assertEqual(read(p),scene);self.assertTrue(np.array_equal(pixels(read(p)),image))

    def test_palette_ids_and_depth_do_not_depend_on_author_order(self):
        scene=default_scene('grip');scene['nodes'][0].update(length=.21,depth=0,at=dict(anchor='center',offset=[-.22,0]))
        other=copy.deepcopy(scene['nodes'][0]);other.update(id='second',depth=1,thumb_side='left',at=dict(anchor='center',offset=[.22,0]),palette=dict(skin='#9b674c',handle='#4e879c'))
        scene['nodes'].append(other);svg=ET.fromstring(drawing(scene));ids=[e.get('id') for e in svg.iter() if e.get('id')]
        self.assertEqual(len(ids),len(set(ids)));image=pixels(scene)
        scene['nodes'].reverse();self.assertTrue(np.array_equal(image,pixels(scene)))
        colours=image[:,:,:3].reshape(-1,3)
        for colour in ((155,103,76),(78,135,156)):self.assertTrue(np.any(np.all(colours==colour,axis=1)))

    def test_invalid_controls_refuse_without_mutating_work(self):
        scene=default_scene('grip');original=fingerprint(scene);selection=select(scene,feature='thumb')
        for name,value in [('thumb_reach',False),('thumb_thickness',float('nan')),('handle_span',2.1)]:
            with self.assertRaises(ValueError):parameter_preview(scene,selection,name,value,'invalid control must not change work')
        self.assertEqual(fingerprint(scene),original)
        bad=copy.deepcopy(scene);bad['nodes'][0].update(width=1.25,handle_span=1.2)
        with self.assertRaisesRegex(ValueError,'expose both ends'):validate(bad)

    def test_public_cli_preview_accept_undo_and_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);scene=root/'work.json';view=root/'view';trial=root/'trial'
            def cli(*args):
                r=subprocess.run([sys.executable,'-m','scripts.studio',*map(str,args)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr);return r.stdout
            cli('new',scene,'--kind','grip');original=read(scene)
            cli('inspect',scene,'--feature','handle','--outdir',view)
            report=read(view/'report.json');info=report['nodes']['carrying-grip']
            self.assertAlmostEqual(info['dimensions_canvas']['handle_thickness']*640,info['dimensions_pixels']['handle_thickness'])
            cli('preview',scene,'--selection',view/'selection.json','--change','handle_span=2.1','--change','handle_color=#4e879c','--reason','extend and cool the held handle','--outdir',trial)
            self.assertEqual(read(trial/'candidate.json')['status'],'ready')
            cli('accept',scene,trial/'candidate.json');self.assertEqual(read(scene)['nodes'][0]['palette']['handle'],'#4e879c')
            cli('undo',scene);self.assertEqual(read(scene),original)

if __name__=='__main__':unittest.main()
