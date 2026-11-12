import sys, subprocess, pathlib, json
root=pathlib.Path(__file__).resolve().parent
args=[sys.executable,'-m','scripts.studio',*sys.argv[1:]]
p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
with (root/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps({'command':args,'exit_code':p.returncode,'output':p.stdout})+'\n')
print(p.stdout)
sys.exit(p.returncode)
