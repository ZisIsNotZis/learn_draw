"""Render WP04 authored A/B study sheet with geometry-derived depth fills."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.articulated_construction import (Point, SupportFrame, Component, Camera,
    build_study_case, component_faces, _ellipse)
from scripts.vector_visibility import visible_regions
from scripts.articulated_line_visibility import transform_compound_path, visible_segment_spans

OUT = Path('.scratch/35-r1-articulated-study/evidence/coordinate-repair-v3/source')
W, H = 1400, 1180
CAM = Camera()

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def panel_components(case):
    return build_study_case(case).components

def observed_study():
    # Original compact interpretation of the frozen crop's shoulder/upper-torso clothing only.
    body = SupportFrame('observed-bodice-support','observed-bodice-depth',(0,0,0),(1,0,.05),(0,1,0))
    sleeve = SupportFrame('observed-sleeve-support','observed-sleeve-depth',(.15,0,.12),(1,0,.02),(0,1,0))
    torso = Component('observed-bodice','dark-trim light bodice mass, limited to visible upper torso',body,
        _ellipse(Point(0,0),1.0,1.08,48),'#f1e8d5')
    shoulder = Component('observed-shoulder','light garment shoulder mass, no inferred hand or pose',sleeve,
        _ellipse(Point(-.83,.72),.62,.35,40),'#f4eddf')
    side = Component('observed-sleeve','light sleeve mass at observed shoulder edge',sleeve,
        _ellipse(Point(-1.12,.32),.43,.66,40),'#eee5d5')
    trim = Component('observed-dark-trim','dark neckline framing over the bodice',body,
        (Point(-.56,.76),Point(0,.94),Point(.56,.76),Point(.40,.60),Point(0,.72),Point(-.40,.60)),'#392a35')
    bow = Component('observed-bow','compact dark garment bow at upper chest',body,
        (Point(-.08,.48),Point(-.50,.68),Point(-.44,.30),Point(-.07,.42)),'#48313c')
    knot = Component('observed-bow-knot','small central bow knot',body,
        _ellipse(Point(-.06,.48),.14,.12,24),'#76505a')
    return (torso,shoulder,side,trim,bow,knot)

def render_panel(parts, x, y, width, height, title, subtitle, case=None):
    projected=[]
    for c in parts:
        for point in c.outline:
            projected.append(CAM.project(c.support.local_to_world(point)))
    xs=[p[0] for p in projected]; ys=[p[1] for p in projected]
    scale=min((width-34)/(max(xs)-min(xs)),(height-65)/(max(ys)-min(ys)))
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    def px(u,v): return (x+width/2+(u-cx)*scale, y+height/2-(v-cy)*scale)
    panel_id=title.lower().replace(" ","-")
    out=[f'<g id="panel-{esc(panel_id)}">',
         f'<defs><clipPath id="clip-{esc(panel_id)}"><rect x="{x+8}" y="{y+66}" width="{width-16}" height="{height-74}"/></clipPath></defs>',
         f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#fffaf1" stroke="#d8cbbb" stroke-width="2"/>',
         f'<text x="{x+22}" y="{y+34}" font-family="sans-serif" font-size="22" font-weight="700" fill="#342d32">{esc(title)}</text>',
         f'<text x="{x+22}" y="{y+57}" font-family="sans-serif" font-size="12" fill="#746b68">{esc(subtitle)}</text>',
         f'<g clip-path="url(#clip-{esc(panel_id)})">']
    # Preserve backend compound subpaths while applying this panel's affine coordinate transform.
    faces=component_faces(parts,CAM)
    for d,fill,name in visible_regions(faces):
        path=transform_compound_path(d,px)
        out.append(f'<path id="{esc(name)}" d="{path}" fill="{fill}"/>')
    # Semantic strokes stay authored, but every segment is clipped against nearer support depth.
    def semantic_line(name, local_points, owner, color, sw):
        world_points=[CAM.project(owner.support.local_to_world(point)) for point in local_points]
        for segment_index,(q0,q1) in enumerate(zip(world_points,world_points[1:])):
            for part_index,(t0,t1) in enumerate(visible_segment_spans(q0,q1,faces,owner.name)):
                a=px(*((q0[k]+t0*(q1[k]-q0[k])) for k in (0,1)))
                b=px(*((q0[k]+t1*(q1[k]-q0[k])) for k in (0,1)))
                out.append(f'<path id="{esc(name)}-{segment_index}-{part_index}" d="M {a[0]:.2f},{a[1]:.2f} L {b[0]:.2f},{b[1]:.2f}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    def quadratic(start, control, end, steps=16):
        return tuple(Point((1-t)*(1-t)*start.u+2*(1-t)*t*control.u+t*t*end.u,
                           (1-t)*(1-t)*start.v+2*(1-t)*t*control.v+t*t*end.v)
                     for t in (i/steps for i in range(steps+1)))
    # Art contour decisions are named separately; no mesh edges are promoted automatically.
    if title.startswith('A —'):
        support_owner=next(c for c in parts if c.name=='observed-bodice')
        semantic_line('bodice-intent-contour',tuple(Point(a,b) for a,b in ((-.72,-.18),(-.58,-.82),(0,-1.0),(.60,-.82),(.74,-.18))),support_owner,'#493b43',2)
        semantic_line('neckline-art-line',tuple(Point(a,b) for a,b in ((-.58,.76),(0,.94),(.56,.76))),support_owner,'#2f2831',3)
        semantic_line('garment-seam-highlight',tuple(Point(a,b) for a,b in ((-.88,.84),(-.70,.98),(-.50,.99))),support_owner,'#c2ae9b',2)
    else:
        study=build_study_case(case)
        hand=next(c for c in parts if c.name=='hand')
        handcenter=Point(sum(p.u for p in hand.outline)/len(hand.outline),sum(p.v for p in hand.outline)/len(hand.outline))
        # Short, authored finger arcs communicate a hand without a contour traced from a reference.
        for idx,(du,dv) in enumerate(((.10,.10),(.17,.03),(.16,-.04))):
            start=Point(handcenter.u-.06,handcenter.v+dv)
            end=Point(handcenter.u+du,handcenter.v+dv-.025)
            control=Point((start.u+end.u)/2,(start.v+end.v)/2+3/scale)
            semantic_line(f'hand-finger-mark-{idx+1}',quadratic(start,control,end),hand,'#754e48',2.2)
        # Sleeve cuff and prop glint are semantic marks mapped by their own supports.
        arm=next(c for c in parts if c.name=='upper_arm')
        cuff_start=Point(study.elbow.u-8/scale,study.elbow.v)
        cuff_end=Point(study.hand_target.u-3/scale,study.hand_target.v-4/scale)
        cuff_control=Point((cuff_start.u+cuff_end.u)/2,(cuff_start.v+cuff_end.v)/2-8/scale)
        semantic_line('sleeve-cuff-art-line',quadratic(cuff_start,cuff_control,cuff_end),arm,'#647a8e',2)
        prop=next(c for c in parts if c.name=='prop')
        pcenter=Point(sum(p.u for p in prop.outline)/len(prop.outline),sum(p.v for p in prop.outline)/len(prop.outline))
        glint_start=Point(pcenter.u+.02-4/scale,pcenter.v+.20)
        glint_end=Point(pcenter.u+.02+4/scale,pcenter.v+.20+5/scale)
        semantic_line('prop-glint-art-line',(glint_start,glint_end),prop,'#fff1bd',3)
        if case=='control':
            out.append(f'<text x="{x+width-20}" y="{y+30}" text-anchor="end" font-family="sans-serif" font-size="15" font-weight="700" fill="#a3343c">CONTROL — near miss</text>')
    out.append('</g>')  # clipped artwork only; title/subtitle remain outside clip
    out.append('</g>')
    return '\n'.join(out)

def main(out=OUT):
    out.mkdir(parents=True,exist_ok=True)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1180" viewBox="0 0 1400 1180">',
         '<rect width="1400" height="1180" fill="#e9e1d7"/>',
         '<text x="42" y="48" font-family="sans-serif" font-size="27" font-weight="700" fill="#342d32">R1 / garment observation + articulated drawing study</text>',
         '<text x="42" y="73" font-family="sans-serif" font-size="14" fill="#6c6260">Original vector artwork • support-mapped fills • depth-derived visibility</text>']
    a_panel=render_panel(observed_study(),30,100,470,1020,'A — observed garment study','Shoulder / upper torso only • no hand pose inferred')
    svg.append(a_panel)
    cases=(('baseline','B — raised grip','Original construction • raised-prop-grip'),('variant','B — changed grip','Chest-rest target • shoulder width +8%'),('control','B — near miss','Baseline proportions • target short by frozen offset'))
    positions=((520,100),(970,100),(520,610))
    b_panels=[]
    for (case,title,sub),(x,y) in zip(cases,positions):
        panel=render_panel(panel_components(case),x,y,410,480,title,sub,case)
        svg.append(panel)
        b_panels.append(panel)
    svg.extend(['<text x="970" y="635" font-family="sans-serif" font-size="13" fill="#756a65">B cases share one authored camera</text>',
                '<text x="970" y="663" font-family="sans-serif" font-size="13" fill="#756a65">The control is intentionally not successful artwork.</text>',
                '<text x="970" y="710" font-family="sans-serif" font-size="13" fill="#756a65">A shows only frozen visible garment scope.</text>',
                '</svg>'])
    (out/'artwork.svg').write_text('\n'.join(svg),encoding='utf-8')
    (out/'artwork-a.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="470" height="1020" viewBox="30 100 470 1020">{a_panel}</svg>',encoding='utf-8')
    b_extra='<text x="970" y="635" font-family="sans-serif" font-size="13" fill="#756a65">B cases share one authored camera</text><text x="970" y="663" font-family="sans-serif" font-size="13" fill="#756a65">The control is intentionally not successful artwork.</text>'
    (out/'artwork-b.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="860" height="1000" viewBox="520 100 860 1000">'+''.join(b_panels)+b_extra+'</svg>',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,default=OUT)
    main(parser.parse_args().outdir)
