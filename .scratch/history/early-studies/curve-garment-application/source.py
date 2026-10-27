"""A single observed upper-garment construction using sparse R.smooth controls."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.articulated_construction import Point, SupportFrame, Component, Camera, component_faces, visible_scene
from scripts.articulated_line_visibility import visible_segment_spans
sys.path.insert(0,str(ROOT/'evidence/vendor-smooth-study'))
from study import smooth_path

OUT = Path(__file__).parent
# Four observed semantic landmarks seed scale/framing: neckline, two shoulder/cuff bounds,
# and lower torso hem. Reference is not loaded by this construction module.
ANCHORS = {"neckline": Point(0.0, 0.0), "shoulder": Point(-1.65, -0.35),
           "waist": Point(0.05, -3.45), "sleeve_cap": Point(-2.2, -1.6)}
SUPPORT = SupportFrame("front-cloth-support", "torso-front-depth", origin=(0,0,0.12))

def derive_controls():
    n,s,w,c=(ANCHORS[k] for k in ("neckline","shoulder","waist","sleeve_cap"))
    # Sparse controls derived from neckline/shoulder/waist relations; no dense traced contour.
    return (Point(n.u+.08,n.v-.04), Point(s.u,s.v), Point(c.u-.12,c.v-.22),
            Point(w.u-.05,w.v), Point(w.u+1.65,w.v+.10),
            Point(1.35,-1.0), Point(.72,-.18), Point(n.u+.30,n.v+.03))

def build():
    points=derive_controls()
    # R.smooth produces cubics; sample only to provide the existing polygon depth adapter.
    d=smooth_path([(p.u,p.v) for p in points], closed=True)
    import re
    vals=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',d)]
    # Parse each cubic segment's endpoint, with fixed subdivision on the authored curve.
    # Geometry definition remains the sparse controls; samples are compiler output.
    samples=[]
    for i in range(len(points)):
        p0,p1,p2,p3=(points[(i+j)%len(points)] for j in (-1,0,1,2))
        for j in range(1,7):
            t=j/6; k=.5/6
            a=(p1.u+(p2.u-p0.u)*k,p1.v+(p2.v-p0.v)*k)
            b=(p2.u-(p3.u-p1.u)*k,p2.v-(p3.v-p1.v)*k)
            q=1-t
            samples.append(Point(q**3*p1.u+3*q*q*t*a[0]+3*q*t*t*b[0]+t**3*p2.u,
                                 q**3*p1.v+3*q*q*t*a[1]+3*q*t*t*b[1]+t**3*p2.v))
    cloth=Component("observed-ivory-shoulder-cloth", "continuous shoulder-to-waist garment panel; dark neckline trim and seam", SUPPORT, tuple(samples), "#eee8d7")
    faces=component_faces((cloth,),Camera())
    assert faces and visible_scene((cloth,),Camera())
    # Semantic seam endpoints use shared neckline and sleeve-cap attachment landmarks.
    lines=( ("neckline-trim",ANCHORS["neckline"],ANCHORS["sleeve_cap"]),
            ("front-panel-seam",ANCHORS["sleeve_cap"],ANCHORS["waist"]) )
    return cloth,lines

def main():
    cloth,lines=build()
    controls=derive_controls()
    # view is a cropped garment-focused canvas, not a whole-portrait reconstruction.
    def xy(p): return (360+120*p.u, 260-120*p.v)
    outline=smooth_path([xy(p) for p in controls],closed=True)
    path=[f'<path id="{cloth.name}" d="{outline}" fill="{cloth.fill}" stroke="#354657" stroke-width="5"/>']
    for name,a,b in lines:
        x0,y0=xy(a); x1,y1=xy(b)
        path.append(f'<!-- {name}: garment attachment/structure boundary -->')
        path.append(f'<path id="{name}" d="M {x0},{y0} L {x1},{y1}" fill="none" stroke="#34485a" stroke-width="7" stroke-linecap="round"/>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="720" height="600" viewBox="0 0 720 600"><rect width="720" height="600" fill="#d9e5e4"/>'+''.join(path)+'</svg>'
    (OUT/'garment.svg').write_text(svg)
if __name__=='__main__': main()
