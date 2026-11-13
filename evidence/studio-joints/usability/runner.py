import sys, subprocess, pathlib, datetime, json, shutil
BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parents[2]
if sys.argv[1:]==['init']:
    shutil.copyfile(ROOT/'evidence/studio-joints/usability-inputs/flower.json', BASE/'initial.json')
    shutil.copyfile(BASE/'initial.json',BASE/'working.json')
    raise SystemExit(0)
args=sys.argv[1:]
log=BASE/'commands.jsonl'
number=len(log.read_text().splitlines())+1 if log.exists() else 1
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=subprocess.Popen([str(ROOT/'.venv/Scripts/python.exe'),'-m','scripts.studio',*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out,err=p.communicate()
record={'number':number,'command':[str(ROOT/'.venv/Scripts/python.exe'),'-m','scripts.studio',*args],'pid':p.pid,'start':start,'terminal':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit':p.returncode,'stdout':out.decode('utf-8',errors='replace'),'stderr':err.decode('utf-8',errors='replace')}
with log.open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(p.returncode)
