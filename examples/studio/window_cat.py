"""Open the revised dusk reading nook, or reproduce its explicitly labeled initial sketch.

This is an artwork recipe, not a new subject primitive. No raster/reference input,
hand-authored path vertices or automatic acceptance of later edits.
"""
from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import validate,write,select,read
from scripts.studio.render import bundle


def initial_scene():
 s=dict(format='learn-draw/studio-1',canvas=[960,720],background='#e6d6bd',nodes=[])
 def mass(name,intent,height,width,colour,depth,**kw):
  n=dict(id=name,kind='shape',intent=intent,length=height,width=width,stroke=0,
         palette=dict(fill=colour),depth=depth,**kw);s['nodes'].append(n);return n
 def mark(name,intent,length,thickness,colour,depth,**kw):
  n=dict(id=name,kind='stroke',intent=intent,length=length,thickness=thickness,
         palette=dict(fill=colour),depth=depth,**kw);s['nodes'].append(n);return n
 def pin(parent,own='center',target='center',x=0,y=0):
  return dict(to=parent,self=own,target=target,offset=[x,y])
 # Three composition anchors: window, resting cat and table lamp. Everything else
 # is sized from these masses or attached to a named edge/center, not SVG points.
 frame=mass('window-frame','a deep blue timber frame holds the night beyond the room',.66,1.12,'#40515a',0,
            rounding=.10,at=dict(anchor='center',offset=[-.13,-.11]))
 pane=mass('night-pane','one quiet dark pane, inset evenly inside its timber frame',frame['length']-.05,
           (frame['length']*frame['width']-.05)/(frame['length']-.05),'#253e55',1,
           rounding=.08,attachment=pin(frame['id']))
 moon=dict(id='outside-moon',kind='moon',intent='a small crescent makes the window unmistakably nocturnal',
           length=.11,fullness=.32,angle=-20,depth=2,palette=dict(fill='#f3d8a4'),
           attachment=pin(pane['id'],x=pane['length']*pane['width']*.23,y=-pane['length']*.25))
 s['nodes'].append(moon)
 for name,x,y,size in [('high-star',-.20,-.28,.008),('low-star',.02,-.06,.005)]:
  mass(name,'a restrained distant star subordinate to the crescent',size,1,'#d7cfad',2,
       profile='oval',attachment=pin(pane['id'],x=pane['length']*x,y=pane['length']*y))
 mark('window-mullion','a slim timber division keeps the view domestic',pane['length'],.012,'#40515a',3,
      attachment=pin(pane['id'],own='root',target='top',x=-pane['length']*.16),angle=0,start_cap='flat',end_cap='flat')
 # A horizontal rail uses a rotated tall mass, so thickness and span stay
 # independent within the existing shape contract. Its local right is screen top.
 sill=mass('window-sill','a broad warm sill supports the book and sleeping cat',1.08,.055/1.08,'#a67c5f',4,
           angle=90,rounding=.28,at=dict(anchor='center',offset=[-.02,.31]))
 mass('sill-apron','a dark front lip gives the resting surface a visible thickness',1.08,.022/1.08,'#7d5c4d',5,
      angle=90,rounding=.20,attachment=pin(sill['id'],own='right',target='left'))
 # The lamp is supported independently of the window; its base and shade share the stem.
 base=mass('lamp-base','a weighted shallow foot rests beside the cat',.027,4.2,'#596568',6,
           profile='oval',attachment=pin(sill['id'],own='bottom',target='right',x=.43))
 mark('lamp-stem','a slender upright joins the lamp base and shade',.42,.012,'#596568',6,
      angle=180,attachment=pin(base['id'],own='root',target='top'))
 mass('lamp-shade','a broad golden shade opens toward the sleeping cat and book',.17,1.45,'#dca64f',8,
      taper=.52,rounding=.30,attachment=pin('lamp-stem',target='tip',y=.025))
 mass('lamp-rim','a warm lower rim suggests the lit underside of the shade',.018,6,'#f4d891',9,
      profile='oval',attachment=pin('lamp-shade',target='bottom'))
 mass('warm-pool','a quiet warm patch ties the cat to the lamp without a hard beam',.025,6,'#d6ad72',6,
      profile='oval',attachment=pin(sill['id'],target='right',x=.32,y=-.004))
 body=mass('sleeping-body','a low oval back curls into a comfortable sleeping silhouette',.17,2.0,'#ba6f4d',8,
           profile='oval',angle=-5,attachment=pin(sill['id'],own='bottom',target='right',x=.10,y=.004))
 # Ears go behind the head. Their tapered colour masses express direction rather
 # than hand-drawn triangle vertices; local contour tools remain available.
 mass('far-ear','the farther tapered ear breaks the round feline head silhouette',.075,.65,'#9a563e',9,
      taper=.96,rounding=.36,angle=-18,attachment=pin('sleeping-head',own='bottom',target='top',x=-.025,y=.015))
 mass('near-ear','a forward ear gives the resting face a recognisable cat profile',.085,.67,'#c27b55',10,
      taper=.96,rounding=.36,angle=12,attachment=pin('sleeping-head',own='bottom',target='top',x=.035,y=.018))
 mass('sleeping-head','a rounded head settles low beside the curled body',.13,1.08,'#c27b55',11,
      profile='oval',angle=-12,attachment=pin(body['id'],own='left',target='right',x=-.055,y=0))
 mass('cat-muzzle','a small pale muzzle separates the face from the orange coat',.044,1.35,'#e4b487',12,
      profile='oval',attachment=pin('sleeping-head',target='right',x=-.027,y=.023))
 mass('cat-nose','a tiny dark nose finishes the quiet right-facing profile',.010,1.25,'#774735',13,
      profile='oval',attachment=pin('cat-muzzle',target='right',x=-.003,y=-.006))
 mark('closed-eye','one softly arched lid communicates sleep rather than a blank face',.038,.004,'#714633',13,
      angle=90,bend=-.20,start_width=.65,end_width=.65,
      attachment=pin('sleeping-head',own='root',x=.002,y=-.012))
 mark('curling-tail','the long tail wraps across the front of the tucked body',.27,.034,'#d28b5d',12,
      angle=-95,bend=.35,start_width=1.1,end_width=.35,
      attachment=pin(body['id'],own='root',target='right',x=-.018,y=.005))
 # Two facing planes are enough to propose an open book; inspect whether that
 # reading survives the cat/lamp hierarchy before adding decorative page lines.
 mass('book-left','the left cream page tilts upward from the resting book gutter',.090,1.18,'#f4e9cf',7,
      rounding=.12,angle=8,attachment=pin(sill['id'],own='bottom',target='right',x=-.27,y=-.010))
 mass('book-right','the second page mirrors its partner around an open gutter',.090,1.18,'#d9c6a5',7,
      rounding=.12,angle=-8,attachment=pin('book-left',own='left',target='right',y=.004))
 mark('book-gutter','a slim dark gutter identifies the two planes as one open book',.085,.003,'#9b805f',8,
      angle=0,attachment=pin('book-left',own='root',target='right',y=-.038))
 # This is a deliberately layered flat illustration. Shared family numbers above
 # organize the recipe; each authored paint layer gets a distinct support plane.
 # In particular the touching book pages are ordered, not ambiguous coplanar solids.
 for plane,n in enumerate(sorted(s['nodes'],key=lambda n:n['depth'])):n['depth']=plane
 validate(s);return s


def scene():
 """Current authored scene, kept in its one editable JSON home."""
 return validate(read(ROOT/'examples/studio/window_cat.json'))


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--outdir',required=True)
 p.add_argument('--initial-sketch',action='store_true',help='reproduce the earlier supported study, before observed CLI revisions')
 args=p.parse_args();out=Path(args.outdir)
 if out.exists():raise SystemExit('output exists; choose a fresh directory')
 s=initial_scene() if args.initial_sketch else scene();write(out/'working.json',s)
 r=bundle(s,out/'view',select(s,'curling-tail' if args.initial_sketch else 'tucked-tail',feature='object'))
 print('Original window-cat example:',r['revision'],r['renderer'],len(s['nodes']),'semantic nodes',
       '(initial sketch)' if args.initial_sketch else '(current study; art gate open)')
