"""An original six-mass pinwheel whose placement is a mount graph, not per-part coordinates."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import write,read,select,parameters_preview,accept,undo,fingerprint,engine_fingerprint
from scripts.studio.render import bundle
from scripts.studio.attachment import resolve_scene,anchors
import argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--outdir',required=True)
args=parser.parse_args();out=Path(args.outdir)
if out.exists(): raise SystemExit('choose a fresh output directory; existing study records are preserved')
out.mkdir(parents=True)
s=dict(format='learn-draw/studio-1',canvas=[640,640],background='#f6ecdf',nodes=[])
def mass(sid,intent,length,width,colour,depth,**extra):
    s['nodes'].append(dict(id=sid,kind='shape',intent=intent,length=length,width=width,stroke=0,palette=dict(fill=colour),depth=depth,**extra))
mass('handle','a slim warm wooden handle below the paper wheel',.38,.055,'#936e54',0,at=dict(anchor='center',offset=[0,.15]),rounding=.8)
mass('hub','the small circular pin at the centre of the folded paper',.08,1,'#f3dbad',10,profile='oval',attachment=dict(to='handle',self='center',target='top'))
for i,(angle,colour) in enumerate(zip((45,135,-135,-45),('#679d9a','#d88567','#d6b86f','#7897aa'))):
    mass('blade-'+str(i+1),'one tapered folded-paper blade held at the common pin',.21,.62,colour,2+i,angle=angle,rounding=.12,taper=-.94,attachment=dict(to='hub',self='bottom',target='center'))
working=out/'working.json';write(working,s)
bundle(s,out/'00-short-handle',select(s,'handle',feature='object'))
trial=parameters_preview(s,select(s,'handle',feature='object'),dict(length=.48),'Lengthen the visible handle; retain the hub mount and all four blade roots')
bundle(trial['scene'],out/'01-longer-proposal',trial['selection'],s)
accept(working,trial);accepted=read(working)
undo(working);assert read(working)==s
accept(working,trial);assert read(working)==accepted
bundle(accepted,out/'02-accepted',select(accepted,'blade-1',feature='anchors'))
def point(scene,sid): return anchors(next(n for n in resolve_scene(scene)['nodes'] if n['id']==sid),scene['canvas'])['center']['point']
shift={sid:[b-a for a,b in zip(point(s,sid),point(accepted,sid))] for sid in ['hub','blade-1','blade-2','blade-3','blade-4']}
assert all(abs(delta[0])<1e-9 and abs(delta[1]+32)<1e-9 for delta in shift.values())
assert all(a==b for a,b in zip(s['nodes'][1:],accepted['nodes'][1:]))
write(out/'mechanics.json',dict(engine=engine_fingerprint(),before=fingerprint(s),after=fingerprint(accepted),only_authored_change='handle.length .38 -> .48',raw_descendant_nodes_exactly_unchanged=True,derived_descendant_center_shift=shift,undo_exact_scene=True,replay_exact_scene=True,scope='root-authored original six-shape drawing; one-point mount graph, not a rigid rotation or size rig'))
print(json.dumps(read(out/'mechanics.json'),indent=2))
