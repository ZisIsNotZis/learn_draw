"""Visible gesture control, round paint and semantic joins must agree in actual scene space."""
import copy
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import numpy as np
from shapely import Polygon,Point

from scripts.studio.__main__ import default_scene
from scripts.studio.stroke import stroke_data,DEFAULT_THICKNESS
from scripts.studio.attachment import resolve_scene,anchors,get_anchor
from scripts.studio.model import select,preview,parameters_preview,attachment_preview,accept,undo,read,write,validate,node_by_id
from scripts.studio.render import drawing,bundle
from .test_studio_hand import pixels


class GestureMark(unittest.TestCase):
    def test_round_default_and_length_control_do_not_change_thickness(self):
        s=default_scene('stroke');a=stroke_data(s['nodes'][0],s['canvas']);r=DEFAULT_THICKNESS*640/2
        self.assertEqual(a.rows[0].spine,(320,192));self.assertEqual(a.rows[-1].spine,(320,448))
        box=Polygon(a.outline).bounds
        self.assertAlmostEqual(box[1],192-r);self.assertAlmostEqual(box[3],448+r)
        longer=parameters_preview(s,select(s,feature='object'),{'length':.6},'Extend the mark without thickening it')['scene']
        b=stroke_data(longer['nodes'][0],s['canvas'])
        for x,y in zip(a.rows,b.rows): self.assertAlmostEqual(math.dist(x.left,x.right),math.dist(y.left,y.right))
        s['nodes'][0].update(start_cap='flat',end_cap='flat')
        flat=stroke_data(s['nodes'][0],s['canvas']);self.assertEqual(Polygon(flat.outline).bounds[1::2],(192,448))

    def test_spine_push_preserves_width_terminals_and_every_unaffected_station(self):
        s=default_scene('stroke');s['canvas']=[960,540];s['nodes'][0].update(angle=35,bend=.2)
        a=stroke_data(s['nodes'][0],s['canvas']);selection=select(s,feature='spine',at=.5,radius=.25)
        trial=preview(s,selection,'left',.3,'Bow only the selected gesture interval')
        b=stroke_data(trial['scene']['nodes'][0],s['canvas'])
        for x,y in zip(a.rows,b.rows):
            self.assertAlmostEqual(math.dist(x.left,x.right),math.dist(y.left,y.right))
            if abs(x.t-.5)>=.25: self.assertEqual(x,y)
        self.assertAlmostEqual(b.rows[40].spine[0]-a.rows[40].spine[0],-.3*DEFAULT_THICKNESS*540)
        self.assertAlmostEqual(b.rows[40].spine[1],a.rows[40].spine[1])
        self.assertEqual(select(trial['scene'],feature='spine',at=.5,radius=.25)['locks'],selection['locks'])

    def test_sculpted_gesture_rotates_with_its_material(self):
        s=default_scene('stroke');s=preview(s,select(s,feature='spine',at=.5,radius=.3),'left',.4,'Refine this curve')['scene']
        a=stroke_data(s['nodes'][0],s['canvas']);turned=parameters_preview(s,select(s,feature='object'),{'angle':37},'Turn the whole painted gesture')['scene']
        b=stroke_data(turned['nodes'][0],s['canvas']);theta=math.radians(37);cx,cy=a.center
        for x,y in zip(a.rows,b.rows):
            for field in ('left','right','spine'):
                p=getattr(x,field);q=getattr(y,field);u,v=p[0]-cx,p[1]-cy
                self.assertAlmostEqual(q[0],cx+u*math.cos(theta)+v*math.sin(theta))
                self.assertAlmostEqual(q[1],cy-u*math.sin(theta)+v*math.cos(theta))

    def test_terminal_moves_preserve_the_other_terminal_under_bend_and_taper(self):
        for terminal in ('root','tip'):
            for direction,delta in [('left',(-32,0)),('down',(0,32))]:
                s=default_scene('stroke');s['nodes'][0].update(angle=26,bend=.2,start_width=.8,end_width=1.2)
                before=stroke_data(s['nodes'][0],s['canvas']);changed=preview(s,select(s,feature=terminal),direction,.05,'Aim this terminal without moving its other end')['scene']
                after=stroke_data(changed['nodes'][0],s['canvas']);i,j=(0,-1) if terminal=='root' else (-1,0)
                for k in (0,1):
                    self.assertAlmostEqual(after.rows[i].spine[k]-before.rows[i].spine[k],delta[k])
                    self.assertAlmostEqual(after.rows[j].spine[k],before.rows[j].spine[k])
                self.assertEqual(changed['nodes'][0].get('thickness',DEFAULT_THICKNESS),DEFAULT_THICKNESS)

    def test_pinned_root_and_positioned_shoulder_mount_are_exact_and_inspected(self):
        s=default_scene('shape');s['nodes'][0].update(id='shirt',length=.4,width=1.1,depth=0)
        mark=default_scene('stroke')['nodes'][0];mark.update(id='arm',length=.2,thickness=.035,depth=1);s['nodes'].append(mark)
        source=select(s,'arm',feature='anchors',anchor='root');target=select(s,'shirt',feature='anchors',anchor='right@.2')
        self.assertLess(target['focus'][1],get_anchor(s['nodes'][0],s['canvas'],'right')['point'][1])
        self.assertNotEqual(get_anchor(s['nodes'][0],s['canvas'],'right@.2')['point'],get_anchor(s['nodes'][0],s['canvas'],'right@.201')['point'])
        trial=attachment_preview(s,source,target,None,None,0,'Seat this gesture at the inspected upper shoulder')
        placed=resolve_scene(trial['scene']);arm=node_by_id(placed,'arm');shirt=node_by_id(placed,'shirt')
        self.assertTrue(np.allclose(get_anchor(arm,s['canvas'],'root')['point'],get_anchor(shirt,s['canvas'],'right@.2')['point']))
        changed=preview(trial['scene'],select(trial['scene'],'arm',feature='tip'),'up',.04,'Raise the free terminal while keeping the shoulder')['scene']
        newer=node_by_id(resolve_scene(changed),'arm');self.assertTrue(np.allclose(get_anchor(newer,s['canvas'],'root')['point'],get_anchor(arm,s['canvas'],'root')['point']))
        with self.assertRaisesRegex(ValueError,'attached pin'): preview(trial['scene'],select(trial['scene'],'arm',feature='root'),'left',.02,'Cannot move this fixed terminal')
        with self.assertRaisesRegex(ValueError,'exact'): attachment_preview(s,select(s,'arm',feature='anchors'),select(s,'shirt',feature='anchors'),'root','right@.2',0,'Uninspected custom location')
        for name in ('right@nan','right@2','center@.2'):
            with self.assertRaises(ValueError): select(s,'shirt',feature='anchors',anchor=name)

    def test_colour_planes_and_ink_follow_bent_round_and_flat_caps(self):
        for side in ('left','right'):
            s=default_scene('stroke');s['nodes'][0].update(bend=.25,start_width=.6,end_width=1.8,start_cap='flat',shade=side,ink_width=.003,palette={'fill':'#82b6bd','shade':'#315c66'})
            data=stroke_data(s['nodes'][0],s['canvas']);image=pixels(s);row=data.rows[40]
            for name,expected in [('left',(49,92,102) if side=='left' else (130,182,189)),('right',(49,92,102) if side=='right' else (130,182,189))]:
                edge=getattr(row,name);x,y=[(a+b)/2 for a,b in zip(row.spine,edge)]
                self.assertEqual(tuple(image[round(y),round(x),:3]),expected)
            self.assertTrue(Polygon(data.outline).is_valid)

    def test_invalid_gestures_are_refused_and_accepted_edits_undo_exactly(self):
        base=default_scene('stroke')
        for controls in ({'thickness':0},{'length':float('nan')},{'start_width':True},{'shade':'metal'},{'end_cap':'pointy'},{'start_width':0,'end_width':0},{'bend':.9,'thickness':.5}):
            bad=copy.deepcopy(base);bad['nodes'][0].update(controls)
            with self.assertRaises(ValueError): validate(bad)
        with self.assertRaises(ValueError): select(base,feature='spine',at=.1,radius=.3)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'working.json';write(path,base)
            trial=preview(base,select(base,feature='spine',at=.5,radius=.3),'left',.3,'Shape a bounded brush curve')
            accept(path,trial);undo(path);self.assertEqual(read(path),base)
            with self.assertRaisesRegex(ValueError,'stale'): preview(trial['scene'],select(base,feature='spine'),'left',.1,'An old view cannot guide a changed mark')

    def test_current_terminal_closeup_contains_the_landing_point(self):
        s=default_scene('stroke');selection=select(s,feature='tip');trial=preview(s,selection,'up',.15,'Bring the endpoint toward this current target')
        with tempfile.TemporaryDirectory() as directory:
            bundle(trial['scene'],directory,trial['selection'],s,png=False)
            root=ET.parse(Path(directory)/'edit-closeup.svg').getroot();x,y,w,h=map(float,root.get('viewBox').split())
            focus=select(trial['scene'],feature='tip')['focus']
            self.assertTrue(x<focus[0]<x+w and y<focus[1]<y+h)
            self.assertAlmostEqual(y+h/2,focus[1])

    def test_anatomical_mounts_follow_existing_head_and_hand_frames(self):
        head=default_scene('head');data=__import__('scripts.studio.head',fromlist=['head_data']).head_data(head['nodes'][0],head['canvas'])
        chin=get_anchor(head['nodes'][0],head['canvas'],'chin')
        self.assertAlmostEqual(chin['point'][0],data.center[0]);self.assertGreater(chin['point'][1],data.features['face']['bounds'][3])
        hand=default_scene('hand');before=get_anchor(hand['nodes'][0],hand['canvas'],'wrist')['point']
        changed=parameters_preview(hand,select(hand,feature='index'),{'finger_length':.94},'Change a digit without recentering its wrist')['scene']
        self.assertEqual(before,get_anchor(changed['nodes'][0],hand['canvas'],'wrist')['point'])
        self.assertTrue(Polygon(__import__('scripts.studio.hand',fromlist=['hand_data']).hand_data(hand['nodes'][0],hand['canvas']).outline).contains(Point(before)))

    def test_valid_free_intents_and_double_hyphen_names_stay_valid_svg(self):
        for kind in ('stroke','shape','head','hand','hair-lock','sky','hills','moon','sun'):
            s=default_scene(kind);s['nodes'][0].update(id='part--one',intent='root -- tip <paint> & more')
            ET.fromstring(drawing(s));self.assertEqual(s['nodes'][0]['intent'],'root -- tip <paint> & more')

    def test_sloping_stroke_still_hides_and_reappears_at_a_true_depth_crossing(self):
        s=default_scene('stroke');s['nodes'][0].update(depth=0,depth_slope=2)
        s['nodes'].append(dict(id='cover',kind='shape',intent='a flat cover crossing the sloped mark',length=.2,width=2,stroke=0,depth=1,palette={'fill':'#c46855'}))
        image=pixels(s)
        self.assertEqual(tuple(image[290,320,:3]),(196,104,85))
        self.assertEqual(tuple(image[350,320,:3]),(73,107,115))

    def test_stroke_compiles_without_a_reference_or_browser_in_a_fresh_directory(self):
        project=Path(__file__).resolve().parents[2]
        code="""import sys
sys.path[:0]=[sys.argv[1],sys.argv[1]+'/scripts']
import renderer
from PIL import Image
import cv2
def forbidden(*args,**kwargs): raise RuntimeError('unexpected browser or image access')
renderer.chrome_path=forbidden;Image.open=forbidden;cv2.imread=forbidden
from scripts.studio.__main__ import default_scene
from scripts.studio.render import drawing
assert 'gesture-paint' in drawing(default_scene('stroke'))
"""
        with tempfile.TemporaryDirectory() as directory:
            r=subprocess.run([sys.executable,'-c',code,str(project)],cwd=directory,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
