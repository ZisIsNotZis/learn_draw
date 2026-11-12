"""Record the actual public-CLI revision, with compact terminal output."""
import json,pathlib,subprocess,sys
p=subprocess.run([sys.executable,'-m','scripts.studio',*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',errors='replace')
with (pathlib.Path(__file__).parent/'commands.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps(dict(argv=sys.argv[1:],exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))+'\n')
try:
    data=json.loads(p.stdout)
    print(json.dumps({k:v for k,v in data.items() if k in ('revision','scene','added','removal','status')}))
except (ValueError,AttributeError): print(p.stdout.strip())
if p.stderr: print(p.stderr.strip(),file=sys.stderr)
sys.exit(p.returncode)
