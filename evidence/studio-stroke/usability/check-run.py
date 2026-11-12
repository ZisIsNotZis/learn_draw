import subprocess,sys,json,pathlib
root=pathlib.Path('evidence/studio-stroke/usability')
args=[sys.executable,'scripts/draw.py','check',str(root/'final/artwork.png'),'--outdir',str(root/'check')]
p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
(root/'check-command.json').write_text(json.dumps({'command':args,'exit_code':p.returncode,'output':p.stdout},indent=2),encoding='utf8')
print(p.stdout)
sys.exit(p.returncode)
