import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
cmd=[sys.executable,'-m','scripts.studio',*sys.argv[1:]]
r=subprocess.run(cmd,capture_output=True,text=True)
with (root/'commands.txt').open('a',encoding='utf8') as f:
 f.write('\nCOMMAND '+json.dumps(cmd)+'\n'+r.stdout+r.stderr+'\nEXIT '+str(r.returncode)+'\n')
print(r.stdout+r.stderr)
sys.exit(r.returncode)
