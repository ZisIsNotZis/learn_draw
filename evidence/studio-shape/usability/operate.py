import subprocess, sys, json, shlex
from pathlib import Path
ROOT=Path('evidence/studio-shape/usability')
SCENE=str(ROOT/'lamp-book.json')
PY=str(Path('.venv/Scripts/python.exe'))
def run(args):
    cmd=[PY,'-m','scripts.studio',*args]
    with (ROOT/'commands.log').open('a',encoding='utf8') as f: f.write(shlex.join(cmd)+'\n')
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
    with (ROOT/'commands.log').open('a',encoding='utf8') as f: f.write(r.stdout+r.stderr+'\nEXIT '+str(r.returncode)+'\n')
    if r.returncode: print(r.stdout,r.stderr);sys.exit(r.returncode)
    return r
obj=sys.argv[1]
from plans import plans; ops=plans[obj]; obj="book-pages" if obj=="book-pages-fix" else obj
if sys.argv[2:]==['add']:run(['add',SCENE,'--kind','shape','--id',obj])
for i,op in enumerate(ops):
    stem=ROOT/(obj+'-'+str(i).zfill(2))
    run(['inspect',SCENE,'--object',obj,'--feature','object','--outdir',str(stem)+'-inspect'])
    mode,key,val,reason=op
    args=['preview',SCENE,'--selection',str(stem)+'-inspect/selection.json','--outdir',str(stem)+'-preview','--reason',reason]
    args+=['--set',key,'--value',str(val)] if mode=='set' else ['--move',key,'--amount',str(val)]
    run(args)
    run(['accept',SCENE,str(stem)+'-preview/candidate.json'])
    print(obj,i,key,val,flush=True)


