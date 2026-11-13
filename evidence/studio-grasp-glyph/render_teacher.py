"""Render the licensed teaching SVG; this is separate from the procedural candidate."""
from pathlib import Path
import sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.render import rasterize
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    source=next(HERE.glob('third-party/openmoji-*/270A.svg'))
    doc=ET.parse(source).getroot();doc.set('width','640');doc.set('height','640')
    out=HERE/'00-teaching-reference';out.mkdir(parents=True,exist_ok=True)
    doc.insert(0,ET.Comment('OpenMoji Raised Fist, CC BY-SA 4.0; see original source, attribution and license in ../third-party/. Size changed for study, paths unchanged.'))
    doc.insert(1,ET.Element('{http://www.w3.org/2000/svg}rect',dict(x='0',y='0',width='72',height='72',fill='#f6ecdf')))
    (out/'teacher.svg').write_text(ET.tostring(doc,encoding='unicode'),encoding='utf8')
    rasterize(out/'teacher.svg',out/'teacher.png')
