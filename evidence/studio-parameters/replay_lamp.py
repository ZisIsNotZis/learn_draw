"""Controlled CLI replay of an existing construction, not an independent drawing verdict."""
import json,runpy,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import read,fingerprint,write
from scripts.studio.render import bundle
out=Path(sys.argv[1] if len(sys.argv)>1 else 'evidence/studio-parameters/lamp-replay');out.mkdir(parents=True,exist_ok=True)
scene=out/'working.json';calls=[];preview_count=0
plans=runpy.run_path('evidence/studio-shape/usability/plans.py')['plans']
original=read('evidence/studio-shape/usability/lamp-book.json')
def cli(*args):
    command=[sys.executable,'-m','scripts.studio',*map(str,args)]
    r=subprocess.run(command,capture_output=True,text=True,check=True)
    calls.append(dict(command=command,stdout=r.stdout))
    return r
cli('new',scene,'--kind','shape','--id','lamp-base','--size','900x600','--background','#f5eddf')
def apply(obj,operations):
    global preview_count
    step=out/(str(preview_count).zfill(2)+'-'+obj)
    cli('inspect',scene,'--object',obj,'--feature','object','--outdir',str(step)+'-view','--svg-only')
    args=['preview',scene,'--selection',str(step)+'-view/selection.json','--outdir',str(step)+'-try','--reason','Replay one coherent component decision without changing its final drawing','--svg-only']
    if operations[0][0]=='set':
        for mode,name,value,_reason in operations: args+=['--change',name+'='+str(value)]
    else:
        _mode,direction,amount,_reason=operations[0];args+=['--move',direction,'--amount',amount]
    cli(*args);cli('accept',scene,str(step)+'-try/candidate.json');preview_count+=1
for i,obj in enumerate(['lamp-base','lamp-stem','lamp-arm','lamp-shade','book-cover','book-pages','page-seam']):
    if i: cli('add',scene,'--kind','shape','--id',obj)
    operations=plans[obj]
    params=[op for op in operations if op[0]=='set']
    if obj=='page-seam': params=[('set','intent',original['nodes'][-1]['intent'],'retain exact original purpose')]+params
    apply(obj,params)
    for operation in operations:
        if operation[0]=='move': apply(obj,[operation])
    if obj=='book-pages': apply(obj,plans['book-pages-fix'])
actual=read(scene)
assert actual==original,(fingerprint(actual),fingerprint(original))
bundle(actual,out/'final')
import hashlib
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(out/'final/artwork.png')==sha('evidence/studio-shape/usability/final/artwork.png')
old_journal=read('evidence/studio-shape/usability/lamp-book.history/journal.json')
new_journal=read(out/'working.history/journal.json')
write(out/'commands.json',calls)
write(out/'comparison.json',dict(scene_exact=True,png_bytes_exact=True,scene_revision=fingerprint(actual),png_sha256=sha(out/'final/artwork.png'),original_accepted_edits=len(old_journal),grouped_accepted_edits=len(new_journal),grouped_preview_calls=preview_count,cli_calls=len(calls),limitation='controlled existing-plan replay; intermediate SVG-only, not a new creative usability trial or timing benchmark'))
print(json.dumps(read(out/'comparison.json'),indent=2))
