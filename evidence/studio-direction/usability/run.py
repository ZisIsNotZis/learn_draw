import sys,subprocess,json,datetime,pathlib,hashlib,os
root=pathlib.Path(__file__).resolve().parent
args=[sys.executable,'-m','scripts.studio',*sys.argv[1:]]
log=root/'commands.jsonl'
def record(v):
 with log.open('a',encoding='utf-8') as f: f.write(json.dumps(v)+'\n')
record({'event':'started','time':datetime.datetime.now().isoformat(),'command':args,'launcher_pid':os.getpid()})
p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
record({'event':'spawned','pid':p.pid})
out,_=p.communicate()
record({'event':'terminal','pid':p.pid,'returncode':p.returncode,'output':out,'time':datetime.datetime.now().isoformat()})
print(out)
sys.exit(p.returncode)
