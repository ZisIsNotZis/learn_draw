import subprocess, sys, json, datetime, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
tag=sys.argv[1]
args=[str(pathlib.Path(sys.executable)), '-m', 'scripts.studio', *sys.argv[2:]]
entry={'tag':tag,'command':args,'intent_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'intent'}
record=ROOT/(tag+'.launch.json')
record.write_text(json.dumps(entry,indent=2),encoding='utf-8')
with (ROOT/(tag+'.stdout.txt')).open('wb') as out, (ROOT/(tag+'.stderr.txt')).open('wb') as err:
    process=subprocess.Popen(args,stdout=out,stderr=err)
    entry.update(state='spawned',pid=process.pid)
    record.write_text(json.dumps(entry,indent=2),encoding='utf-8')
    result=process.wait()
entry.update(state='terminal',exit_code=result,terminal_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
raw=(ROOT/(tag+'.stdout.txt')).read_bytes()
entry.update(stdout_bytes=len(raw),stdout_chars=len(raw.decode('utf-8')))
record.write_text(json.dumps(entry,indent=2),encoding='utf-8')
print(json.dumps(entry))
print(raw.decode('utf-8'))
print((ROOT/(tag+'.stderr.txt')).read_text(encoding='utf-8'))
sys.exit(result)
