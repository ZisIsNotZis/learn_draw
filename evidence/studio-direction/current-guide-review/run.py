import sys,subprocess,json,datetime,pathlib,os
p=pathlib.Path(__file__).resolve().parent
args=[sys.executable,'-m','scripts.studio','inspect','evidence/studio-direction/usability/working.json','--object','flower-hand','--feature','anchors','--anchor','wrist','--outdir','evidence/studio-direction/current-guide-review/view']
log=p/'command.jsonl'
def rec(v):
 with log.open('a',encoding='utf-8') as f:f.write(json.dumps(v)+'\n')
rec({'event':'started','time':datetime.datetime.now().isoformat(),'command':args,'launcher_pid':os.getpid()})
r=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
rec({'event':'spawned','pid':r.pid})
out,_=r.communicate(); rec({'event':'terminal','pid':r.pid,'returncode':r.returncode,'output':out,'time':datetime.datetime.now().isoformat()})
print('terminal',r.returncode)
sys.exit(r.returncode)
