"""Revision-local relation-grammar artwork renderer; never reads reference pixels."""
import argparse
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from scripts.articulated_construction import (Point, SupportFrame, Component, Camera,
    build_study_case, component_faces, _ellipse)
from scripts.vector_visibility import visible_regions
from scripts.articulated_line_visibility import transform_compound_path, visible_segment_spans

OUT = Path('.scratch/35-r1-articulated-study/evidence/artistic-replan-r1/source')
CAM = Camera()

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def quad(a,c,b,n=12):
    return tuple(Point((1-t)**2*a.u+2*(1-t)*t*c.u+t*t*b.u,(1-t)**2*a.v+2*(1-t)*t*c.v+t*t*b.v) for t in (i/n for i in range(n+1)))
def chain(*curves): return tuple(p for i,curve in enumerate(curves) for p in (curve if i==0 else curve[1:]))
def closed(*curves):
    pts=chain(*curves)
    return pts[:-1] if pts[0]==pts[-1] else pts

def observed_study():
    """Named clothing regions: relation-defined panel, asymmetric cap, sleeve, trim, bow."""
    bodice=SupportFrame('garment-panel-support','garment-panel-depth',(0,0,0),(1,0,.05),(0,1,0))
    sleeve=SupportFrame('sleeve-cap-support','sleeve-cap-depth',(.15,0,.12),(1,0,.02),(0,1,0))
    # Four semantic boundary anchors; curves generate panel shape, not a traced outline.
    left_neck=Point(-.30,.80); right_neck=Point(.36,.70); left_waist=Point(-.72,-1.0); right_waist=Point(.68,-.96)
    panel=closed(quad(left_neck,Point(-.50,.56),Point(-.72,.20)),quad(Point(-.72,.20),Point(-.84,-.52),left_waist),
      quad(left_waist,Point(-.02,-1.18),right_waist),quad(right_waist,Point(.73,-.32),Point(.66,.30)),quad(Point(.66,.30),Point(.50,.58),right_neck),quad(right_neck,Point(.04,.84),left_neck))
    torso=Component('observed-bodice','fitted light bodice panel from neckline/side/hem relations',bodice,panel,'#eee4d2')
    # Sloped shoulder-cap arc joins asymmetric neckline and outer sleeve attachment.
    cap=closed(quad(Point(-.30,.80),Point(-.64,1.10),Point(-1.12,.86)),quad(Point(-1.12,.86),Point(-1.32,.65),Point(-1.24,.36)),quad(Point(-1.24,.36),Point(-.88,.56),Point(-.58,.57)),quad(Point(-.58,.57),Point(-.42,.68),Point(-.30,.80)))
    shoulder=Component('observed-shoulder-cap','asymmetric sloped shoulder and curved sleeve-cap attachment',sleeve,cap,'#f4eddf')
    sleeve_outline=closed(quad(Point(-1.24,.36),Point(-1.22,-.04),Point(-1.12,-.46)),quad(Point(-1.12,-.46),Point(-1.10,-.66),Point(-1.18,-.78)),quad(Point(-1.18,-.78),Point(-.88,-.86),Point(-.68,-.72)),quad(Point(-.68,-.72),Point(-.72,-.31),Point(-.58,.57)),quad(Point(-.58,.57),Point(-.92,.48),Point(-1.24,.36)))
    side=Component('observed-sleeve','tapered sleeve ending in a shaped cuff edge',sleeve,sleeve_outline,'#e9dfcf')
    cuff=Component('observed-cuff','narrow contrasting sleeve opening band',sleeve,closed(quad(Point(-1.18,-.78),Point(-.94,-.85),Point(-.68,-.72)),quad(Point(-.68,-.72),Point(-.69,-.62),Point(-.72,-.55)),quad(Point(-.72,-.55),Point(-.96,-.66),Point(-1.17,-.67)),quad(Point(-1.17,-.67),Point(-1.20,-.72),Point(-1.18,-.78))),'#d4c7b4')
    neckline=Component('observed-neckline-trim','curved dark trim following neckline relation',bodice,closed(quad(left_neck,Point(-.06,.91),right_neck),quad(right_neck,Point(.29,.55),Point(.14,.52)),quad(Point(.14,.52),Point(-.08,.68),Point(-.38,.58)),quad(Point(-.38,.58),Point(-.42,.70),left_neck)),'#392a35')
    # Paired lobes and tails use anchors around the chest bow knot.
    bow_left=Component('observed-bow-left-lobe','left gathered bow loop',bodice,closed(quad(Point(-.10,.36),Point(-.52,.56),Point(-.58,.38)),quad(Point(-.58,.38),Point(-.48,.18),Point(-.12,.29)),quad(Point(-.12,.29),Point(-.04,.34),Point(-.10,.36))),'#48313c')
    bow_right=Component('observed-bow-right-lobe','right gathered bow loop',bodice,closed(quad(Point(.02,.36),Point(.40,.62),Point(.51,.45)),quad(Point(.51,.45),Point(.42,.22),Point(.10,.30)),quad(Point(.10,.30),Point(.02,.34),Point(.02,.36))),'#48313c')
    tails=Component('observed-bow-tails','two tapered bow tails descending from knot',bodice,closed(quad(Point(-.12,.29),Point(-.20,.02),Point(-.23,-.18)),quad(Point(-.23,-.18),Point(-.12,-.10),Point(-.04,-.18)),quad(Point(-.04,-.18),Point(.05,.03),Point(.10,.30)),quad(Point(.10,.30),Point(.0,.34),Point(-.12,.29))),'#533743')
    knot=Component('observed-bow-knot','small central gathered knot',bodice,_ellipse(Point(-.01,.34),.09,.075,20),'#76505a')
    return torso,shoulder,side,cuff,neckline,bow_left,bow_right,tails,knot

def panel_components(case):
    study=build_study_case(case)
    made=[]
    for part in study.components:
        if part.name=='torso':
            # Tailored torso contour generated from shoulder/waist/hem anchors and curved sides.
            p=closed(quad(Point(-.66,2.15),Point(-.35,2.46),Point(0,2.40)),quad(Point(0,2.40),Point(.48,2.46),Point(.66,2.15)),quad(Point(.66,2.15),Point(.78,1.15),Point(.72,.30)),quad(Point(.72,.30),Point(0,.12),Point(-.72,.30)),quad(Point(-.72,.30),Point(-.80,1.2),Point(-.66,2.15)))
            made.append(replace(part,intent='tailored torso panel with sloped shoulder and curved hem',outline=p))
        elif part.name=='hand':
            wrist=dict(part.anchors)['wrist']; touch=dict(part.anchors)['touch']
            dx=touch.u-wrist.u; dy=touch.v-wrist.v; length=(dx*dx+dy*dy)**.5; n=Point(-dy/length,dx/length)
            # Palm heel + opposing thumb + three grouped finger tips derive from wrist/grip axis.
            p=closed(quad(wrist,Point(wrist.u+.04,wrist.v+.20),Point(wrist.u+.24,wrist.v+.22)),quad(Point(wrist.u+.24,wrist.v+.22),Point(touch.u-.10,touch.v+.20),Point(touch.u,touch.v+.10)),quad(Point(touch.u,touch.v+.10),Point(touch.u+.02,touch.v+.04),touch),quad(touch,Point(touch.u-.02,touch.v-.08),Point(touch.u-.10,touch.v-.11)),quad(Point(touch.u-.10,touch.v-.11),Point(wrist.u+.16,wrist.v-.18),wrist))
            made.append(replace(part,intent='palm heel with opposing thumb and grouped gripping fingers',outline=p))
        else: made.append(part)
    return tuple(made)

def render_panel(parts,x,y,width,height,title,subtitle,case=None):
    projected=[CAM.project(c.support.local_to_world(p)) for c in parts for p in c.outline]
    xs=[p[0] for p in projected]; ys=[p[1] for p in projected]
    scale=min((width-34)/(max(xs)-min(xs)),(height-65)/(max(ys)-min(ys))); cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
    def px(u,v): return x+width/2+(u-cx)*scale,y+height/2-(v-cy)*scale
    pid=title.lower().replace(' ','-'); out=[f'<g id="panel-{esc(pid)}"><defs><clipPath id="clip-{esc(pid)}"><rect x="{x+8}" y="{y+66}" width="{width-16}" height="{height-74}"/></clipPath></defs>',f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#fffaf1" stroke="#d8cbbb" stroke-width="2"/>',f'<text x="{x+22}" y="{y+34}" font-family="sans-serif" font-size="22" font-weight="700" fill="#342d32">{esc(title)}</text>',f'<text x="{x+22}" y="{y+57}" font-family="sans-serif" font-size="12" fill="#746b68">{esc(subtitle)}</text>',f'<g clip-path="url(#{'clip-'+esc(pid)})">']
    faces=component_faces(parts,CAM)
    for d,fill,name in visible_regions(faces): out.append(f'<path id="{esc(name)}" d="{transform_compound_path(d,px)}" fill="{fill}"/>')
    def line(name,points,owner,color,sw):
        worlds=[CAM.project(owner.support.local_to_world(p)) for p in points]
        for si,(a,b) in enumerate(zip(worlds,worlds[1:])):
            for pi,(t0,t1) in enumerate(visible_segment_spans(a,b,faces,owner.name)):
                p0=px(a[0]+t0*(b[0]-a[0]),a[1]+t0*(b[1]-a[1])); p1=px(a[0]+t1*(b[0]-a[0]),a[1]+t1*(b[1]-a[1]))
                out.append(f'<path id="{name}-{si}-{pi}" d="M {p0[0]:.2f},{p0[1]:.2f} L {p1[0]:.2f},{p1[1]:.2f}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    if title.startswith('A —'):
        torso=next(c for c in parts if c.name=='observed-bodice')
        line('panel-tension-seam',quad(Point(-.52,.48),Point(-.42,.05),Point(-.35,-.38)),torso,'#c2ae9b',2)
        line('shoulder-seam',quad(Point(-.34,.77),Point(-.64,.92),Point(-.94,.77)),next(c for c in parts if c.name=='observed-shoulder-cap'),'#c9baa4',2)
    else:
        study=build_study_case(case); hand=next(c for c in parts if c.name=='hand'); wrist=dict(hand.anchors)['wrist']; touch=dict(hand.anchors)['touch']
        dx=touch.u-wrist.u; dy=touch.v-wrist.v; n=(dx*dx+dy*dy)**.5; perpendicular=Point(-dy/n,dx/n)
        # Explicit three grouped finger bands plus opposing-thumb crease, related to wrist/grip axis.
        for i,f in enumerate((.48,.62,.76)):
            start=Point(wrist.u+dx*f-perpendicular.u*.10,wrist.v+dy*f-perpendicular.v*.10); end=Point(start.u+perpendicular.u*.13,start.v+perpendicular.v*.13)
            line(f'finger-band-{i}',quad(start,Point((start.u+end.u)/2,(start.v+end.v)/2+.025),end),hand,'#754e48',1.8)
        fore=next(c for c in parts if c.name=='forearm'); e=study.elbow; t=study.hand_target
        # Intentional inner elbow fold and cuff turn follow elbow-to-wrist axis.
        line('inner-elbow-fold',quad(Point(e.u-.09,e.v+.08),Point(e.u+.02,e.v-.02),Point(e.u+.14,e.v-.08)),fore,'#647a8e',2)
        line('wrist-cuff-turn',quad(Point(t.u-.20,t.v+.14),Point(t.u-.08,t.v+.02),Point(t.u+.03,t.v-.10)),fore,'#647a8e',2.2)
        if case=='control': out.append(f'<text x="{x+width-20}" y="{y+30}" text-anchor="end" font-family="sans-serif" font-size="15" font-weight="700" fill="#a3343c">CONTROL — near miss</text>')
    out.extend(['</g></g>']); return '\n'.join(out)

def main(out=OUT):
    out.mkdir(parents=True,exist_ok=True); svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1180" viewBox="0 0 1400 1180"><rect width="1400" height="1180" fill="#e9e1d7"/>','<text x="42" y="48" font-family="sans-serif" font-size="27" font-weight="700" fill="#342d32">R1 / relation-based garment and articulated hand study</text>']
    a=render_panel(observed_study(),30,100,470,1020,'A — observed garment study','Shoulder / upper torso only • no hand pose inferred'); svg.append(a)
    cases=(('baseline','B — raised grip','Original construction • raised-prop-grip'),('variant','B — changed grip','Chest-rest target • shoulder width +8%'),('control','B — near miss','Baseline proportions • frozen short target'))
    ps=[]
    for (case,title,sub),(x,y) in zip(cases,((520,100),(970,100),(520,610))):
        p=render_panel(panel_components(case),x,y,410,480,title,sub,case); svg.append(p); ps.append(p)
    svg.append('</svg>'); (out/'artwork.svg').write_text('\n'.join(svg),encoding='utf-8')
    (out/'artwork-a.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="470" height="1020" viewBox="30 100 470 1020">{a}</svg>',encoding='utf-8')
    (out/'artwork-b.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="860" height="1000" viewBox="520 100 860 1000">'+''.join(ps)+'</svg>',encoding='utf-8')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--outdir',type=Path,default=OUT); main(ap.parse_args().outdir)
