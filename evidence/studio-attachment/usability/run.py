import sys, subprocess, pathlib,json
root=pathlib.Path(__file__).resolve().parent
cmd=[sys.executable,'-m','scripts.studio',*sys.argv[1:]]
with (root/'commands.log').open('a',encoding='utf-8') as f:
 f.write('\n$ '+subprocess.list2cmdline(cmd)+'\n');f.flush()
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 f.write(p.stdout+'\nEXIT '+str(p.returncode)+'\n')
 try:
  d=json.loads(p.stdout); print(json.dumps({k:d[k] for k in ('status','revision','scene','images','error') if k in d}))
 except: print(p.stdout,end='')
sys.exit(p.returncode)
