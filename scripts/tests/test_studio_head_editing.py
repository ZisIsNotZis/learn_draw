"""Exercise the head through the same scene/edit/depth contract as a simple lock."""
import copy
from io import BytesIO
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import resvg_py

from scripts.studio.__main__ import default_scene
from scripts.studio.head import head_data, rotate_point
from scripts.studio.model import accept, fingerprint, parameter_preview, preview, read, select, undo, validate, write
from scripts.studio.render import bundle, drawing, global_depth_order


def pixels(scene):
    raw=resvg_py.svg_to_bytes(svg_string=drawing(scene))
    return np.asarray(Image.open(BytesIO(raw)).convert('RGBA'))


class HeadEditing(unittest.TestCase):
    def setUp(self):
        self.scene=default_scene('head')

    def test_hair_recolor_covers_internal_marks_in_both_styles(self):
        from scripts.studio.head import compile_recipe
        for style in ('side-part','bob'):
            with self.subTest(style=style):
                before=compile_recipe(hair=style)['nodes']
                after=compile_recipe(hair=style,palette={'hair':'#b16e48'})['nodes']
                for old,new in zip(before,after):
                    if old['z'] in ('hair-back','hair-front','cap'):
                        for attr in ('fill','ink','stroke'):
                            if isinstance(old.get(attr),str) and old[attr].startswith('#'):
                                self.assertNotEqual(old[attr],new[attr],str((style,old,attr)))
                scene=copy.deepcopy(self.scene)
                scene['nodes'][0].update(hair=style,palette={'hair':'#b16e48'})
                image=pixels(scene)
                blue=(image[:,:,2]>image[:,:,0]) & (image[:,:,2]>image[:,:,1])
                # The deliberately purple pupils are a separate eye material.
                x0,y0,x1,y1=head_data(scene['nodes'][0],scene['canvas']).features['eyes']['bounds']
                blue[max(0,int(y0)-2):int(y1)+3,max(0,int(x0)-2):int(x1)+3]=False
                self.assertFalse(blue.any(),'warm hair must not retain default blue marks')

    def test_eye_parameter_changes_only_the_selected_eyes_in_actual_raster(self):
        selection=select(self.scene,feature='eyes')
        candidate=parameter_preview(self.scene,selection,'eye_scale',.92,'make the expression quieter')
        before,after=pixels(self.scene),pixels(candidate['scene'])
        different=np.any(before!=after,axis=2)
        self.assertGreater(int(different.sum()),0)
        x0,y0,x1,y1=selection['bounds']
        allowed=np.zeros(different.shape,dtype=bool)
        allowed[max(0,int(y0)-12):int(y1)+13,max(0,int(x0)-12):int(x1)+13]=True
        self.assertEqual(int((different&~allowed).sum()),0)
        self.assertNotIn('eye_scale',self.scene['nodes'][0], 'preview is not acceptance')

    def test_screen_push_respects_parent_tilt_and_protected_other_parts(self):
        self.scene['nodes'][0]['angle']=27
        selected=select(self.scene,feature='left-lock',at=.55,radius=.25)
        trial=preview(self.scene,selected,'right',.1,'ease the outer temple lock toward the face')
        old=head_data(self.scene['nodes'][0],self.scene['canvas'])
        new=head_data(trial['scene']['nodes'][0],self.scene['canvas'])
        a,b=old.locks['left'],new.locks['left']
        p=rotate_point(a['rows'][22].left,old.center,old.angle)
        q=rotate_point(b['rows'][22].left,new.center,new.angle)
        nominal=a['node']['length']*min(self.scene['canvas'])*a['node']['width']
        self.assertAlmostEqual(q[0]-p[0],nominal*.1,places=7)
        self.assertAlmostEqual(q[1]-p[1],0,places=7)
        self.assertEqual(a['rows'][0],b['rows'][0])
        self.assertEqual(a['rows'][-1],b['rows'][-1])
        self.assertEqual(old.locks['right'],new.locks['right'])
        old_xml={e.get('id'):e.attrib for e in ET.fromstring(old.svg).iter() if e.get('id')}
        new_xml={e.get('id'):e.attrib for e in ET.fromstring(new.svg).iter() if e.get('id')}
        for sid in ('portrait--head-contour','portrait--eye-left-sclera','portrait--eye-right-sclera'):
            self.assertEqual(old_xml[sid],new_xml[sid])

    def test_alignment_scope_refuses_an_unrelated_action(self):
        selected=select(self.scene,feature='eyes')
        with self.assertRaisesRegex(ValueError,'not exposed'):
            parameter_preview(self.scene,selected,'jaw',.5,'change the jaw')
        with self.assertRaisesRegex(ValueError,'semantic parameter'):
            preview(self.scene,selected,'right',.1,'move something')

    def test_mixed_parameter_and_local_edits_undo_to_exact_input(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'working.json'
            write(p,self.scene)
            original=p.read_bytes()
            eyes=parameter_preview(self.scene,select(self.scene,feature='eyes'),'eye_scale',.92,'quieter eyes')
            accept(p,eyes)
            lock=preview(read(p),select(read(p),feature='right-lock'),'left',.07,'reduce side fullness')
            accept(p,lock)
            undo(p)
            self.assertEqual(fingerprint(read(p)),eyes['result'])
            undo(p)
            self.assertEqual(p.read_bytes(),original)

    def test_multiple_heads_have_unique_clip_ids_and_depth_still_wins(self):
        second=copy.deepcopy(self.scene['nodes'][0])
        second.update(id='second',at=dict(anchor='center',offset=[.19,0]),length=.5,depth=.6,
                      palette=dict(skin='#f5b38a',hair='#915d41'))
        self.scene['nodes'].append(second)
        root=ET.fromstring(drawing(self.scene))
        ids=[e.get('id') for e in root.iter() if e.get('id')]
        self.assertEqual(len(ids),len(set(ids)))
        for element in root.iter():
            for value in element.attrib.values():
                for ref in re.findall(r'url\(#([^)]*)\)',value):
                    self.assertIn(ref,ids)
        forward=pixels(self.scene)
        self.scene['nodes'].reverse()
        reverse=pixels(self.scene)
        self.assertEqual(tuple(forward[380,415]),(245,179,138,255))
        self.assertEqual(tuple(reverse[380,415]),(245,179,138,255))

    def test_crossing_planes_refuse_the_global_order_shortcut(self):
        from scripts.studio.geometry import lock_rows, mix
        scene=default_scene()
        scene['nodes'][0].update(id='sloping',depth=-.5,depth_slope=1,palette=dict(fill='#dd6655'))
        flat=copy.deepcopy(scene['nodes'][0])
        flat.update(id='flat',depth=0,depth_slope=0,palette=dict(fill='#4477bb'))
        scene['nodes'].append(flat)
        self.assertIsNone(global_depth_order(scene))
        result=pixels(scene)
        rows=lock_rows(flat,scene['canvas'])
        for t,channel in ((.25,2),(.75,0)):
            r=min(rows,key=lambda r:abs(r.t-t))
            x,y=mix(r.left,r.right,.43)
            pixel=result[round(y),round(x),:3]
            self.assertGreater(int(pixel[channel]),int(pixel[0 if channel==2 else 2])+30)

    def test_failed_render_cannot_advertise_stale_images_as_ready(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            write(p/'report.json',dict(status='ready',images=['stale.png']))
            with patch('scripts.studio.render.rasterize',side_effect=RuntimeError('renderer failed')):
                with self.assertRaisesRegex(RuntimeError,'renderer failed'):
                    bundle(self.scene,p,select(self.scene,feature='eyes'))
            self.assertEqual(read(p/'report.json')['status'],'rendering')
            self.assertEqual(read(p/'report.json')['images'],[])
            self.assertEqual((p/'report.txt').read_text(), '')
            working=p/'working.json';write(working,self.scene)
            with self.assertRaisesRegex(ValueError,'not completed'):
                accept(working,dict(status='rendering'))
            self.assertEqual(read(working),self.scene)

    def test_geometry_import_and_head_compile_do_not_discover_a_browser(self):
        root=Path(__file__).resolve().parents[2]
        code="""import sys
sys.path.insert(0,'scripts')
import renderer
def forbidden():
    raise RuntimeError('pure geometry attempted browser discovery')
renderer.chrome_path=forbidden
import relate
from scripts.studio.head import head_data
assert head_data(dict(id='h',kind='head',intent='a face'),[640,640]).outline
"""
        subprocess.run([sys.executable,'-c',code],cwd=root,check=True,capture_output=True,text=True)


if __name__=='__main__':
    unittest.main()
