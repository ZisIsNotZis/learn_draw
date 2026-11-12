from pathlib import Path
import subprocess,sys,shlex
P=Path('evidence/studio-parameters/usability'); S=str(P/'rocket.json'); PY='.venv/Scripts/python.exe'
def run(args):
 cmd=[PY,'-m','scripts.studio',*args]
 r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
 with (P/'commands.log').open('a',encoding='utf8') as f:f.write(shlex.join(cmd)+'\n'+r.stdout+r.stderr+'\nEXIT '+str(r.returncode)+'\n')
 if r.returncode:print(r.stdout,r.stderr);sys.exit(r.returncode)
 print(args[0],args[-1],flush=True)
parts={
 'body':dict(intent='the cream main hull of a friendly toy rocket',length=.46,width=.5,rounding=.65,taper=.05,stroke=.012,fill_color='#ead8b5',ink_color='#76564a'),
 'nose':dict(intent='the warm red pointed nose cap of the toy rocket',length=.18,width=1.2,rounding=.03,taper=.96,stroke=0,fill_color='#bc6150'),
 'left-fin':dict(intent='the left stabilizing red fin of the toy rocket',length=.22,width=.8,rounding=.03,taper=.9,angle=-18,stroke=0,fill_color='#bc6150'),
 'right-fin':dict(intent='the right stabilizing red fin of the toy rocket',length=.22,width=.8,rounding=.03,taper=.9,angle=18,stroke=0,fill_color='#bc6150'),
 'porthole-rim':dict(intent='the round dark rim of the toy rocket porthole',length=.15,width=1,profile='oval',stroke=0,fill_color='#76564a'),
 'porthole-glass':dict(intent='the blue glass inset within the round porthole rim',length=.112,width=1,profile='oval',stroke=0,fill_color='#82b6bd'),
}
mode=sys.argv[1];obj=sys.argv[2] if len(sys.argv)>2 else 'body'; tag=sys.argv[3] if len(sys.argv)>3 else obj
if mode=='new':run(['new',S,'--kind','shape','--id','body','--size','640x640','--background','#f6ecdf'])
elif mode=='configure':
 if obj!='body':run(['add',S,'--kind','shape','--id',obj,'--depth','-1' if 'fin' in obj else '1' if obj=='nose' else '2' if obj=='porthole-rim' else '3'])
 run(['inspect',S,'--object',obj,'--feature','object','--outdir',str(P/(tag+'-inspect'))])
 args=['preview',S,'--selection',str(P/(tag+'-inspect/selection.json')),'--outdir',str(P/(tag+'-preview')),'--reason','Configure the complete '+obj+' as a coherent flat toy rocket part']
 for k,v in parts[obj].items():args+=['--change',str(k)+'='+str(v)]
 run(args)
elif mode=='accept':run(['accept',S,str(P/(tag+'-preview/candidate.json'))])
elif mode=='move':
 direction,amount=sys.argv[4:6]
 run(['inspect',S,'--object',obj,'--feature','object','--outdir',str(P/(tag+'-inspect'))])
 run(['preview',S,'--selection',str(P/(tag+'-inspect/selection.json')),'--move',direction,'--amount',amount,'--outdir',str(P/(tag+'-preview')),'--reason','Place the '+obj+' into the rocket silhouette'])
elif mode=='undo':run(['undo',S])
elif mode=='inspect':run(['inspect',S,'--object',obj,'--feature','object','--outdir',str(P/tag)])
