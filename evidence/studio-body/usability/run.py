import subprocess,sys,json,pathlib,datetime
r=pathlib.Path(__file__).resolve().parent
tag=sys.argv[1]; args=[sys.executable,'-m','scripts.studio',*sys.argv[2:]]
e={'command':args,'state':'intent','start':datetime.datetime.now(datetime.timezone.utc).isoformat()}
p=r/(tag+'.launch.json');p.write_text(json.dumps(e,indent=2))
with (r/(tag+'.stdout')).open('wb') as out,(r/(tag+'.stderr')).open('wb') as err:
 c=subprocess.Popen(args,stdout=out,stderr=err);e.update(state='spawned',pid=c.pid);p.write_text(json.dumps(e,indent=2));rc=c.wait()
raw=(r/(tag+'.stdout')).read_bytes();e.update(state='terminal',exit=rc,terminal=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout_bytes=len(raw));p.write_text(json.dumps(e,indent=2));print(json.dumps(e));print(raw.decode('utf-8'));print((r/(tag+'.stderr')).read_text());sys.exit(rc)
