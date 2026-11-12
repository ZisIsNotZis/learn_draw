"""Head-probe checks with actual native SVG rasterization and negative controls."""
import copy
import json
import math
import re
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import resvg_py

from examples.studio.head_probe import generate


NS = '{http://www.w3.org/2000/svg}'


def alpha(svg):
    raw = resvg_py.svg_to_bytes(svg_string=ET.tostring(svg, encoding='unicode'))
    return np.asarray(Image.open(BytesIO(raw)).convert('RGBA'))[:, :, 3]


class HeadProbe(unittest.TestCase):
    def test_eye_scale_preserves_head_hair_and_other_features(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'default', Path(d)/'large-eyes'
            generate(a, hair='side-part', svg_only=True)
            generate(b, eye_scale=1.12, hair='side-part', svg_only=True)
            first = {el.get('id'):el for el in ET.parse(a/'artwork.svg').getroot() if el.get('id')}
            second = {el.get('id'):el for el in ET.parse(b/'artwork.svg').getroot() if el.get('id')}
            for sid in ('head-contour','hair-front-union','bob-back','mouth','nose','ear-left','ear-right'):
                self.assertEqual(ET.tostring(first[sid]), ET.tostring(second[sid]), sid)
            self.assertNotEqual(first['eye-left-sclera'].get('d'), second['eye-left-sclera'].get('d'))
            self.assertNotIn('bob-left-left', first, 'root construction seams must not become contours')
            self.assertNotIn('bob-cap', first, 'front cap and side locks form one rendered region')

    def test_aperture_clip_really_prevents_escaped_catchlights(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            generate(directory, hair='side-part', svg_only=True)
            source = ET.parse(directory/'artwork.svg').getroot()
            by_id = {el.get('id'):el for el in source if el.get('id')}
            definitions = next(el for el in source if el.tag == NS+'defs')
            mask_svg = ET.Element(NS+'svg', width='640',height='640',viewBox='0 0 640 640')
            mask = copy.deepcopy(by_id['eye-left-sclera'])
            mask.set('fill','#ffffff')
            mask.attrib.pop('stroke', None)
            mask_svg.append(mask)
            aperture = alpha(mask_svg)
            positive = ET.Element(NS+'svg', width='640',height='640',viewBox='0 0 640 640')
            positive.append(copy.deepcopy(definitions))
            positive.append(copy.deepcopy(by_id['eye-left-glint1']))
            clipped = alpha(positive)
            negative = copy.deepcopy(positive)
            negative[-1].attrib.pop('clip-path')
            unclipped = alpha(negative)
            outside = aperture == 0
            self.assertEqual(np.count_nonzero((clipped > 0) & outside), 0)
            self.assertGreater(np.count_nonzero((unclipped > 0) & outside), 0,
                               'negative control must expose the original free-glint leak')

    def test_exact_hair_polygon_preserves_its_computed_corner_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            generate(directory, hair='side-part', svg_only=True)
            by_id={el.get('id'):el for el in ET.parse(directory/'artwork.svg').getroot() if el.get('id')}
            rear=ET.Element(NS+'svg',width='640',height='640',viewBox='0 0 640 640')
            part=copy.deepcopy(by_id['bob-back'])
            part.attrib.pop('stroke',None)
            rear.append(part)
            exact=alpha(rear)
            # Reintroducing a generic curve fit cuts into the computed corners.
            from scene_render import smooth_path
            values=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',part.get('d'))))
            points=list(zip(values[::2],values[1::2]))
            part.set('d',smooth_path(points,closed=True))
            rounded=alpha(rear)
            self.assertGreater(np.count_nonzero((exact>240)&(rounded==0)),0)


if __name__=='__main__':
    unittest.main()
