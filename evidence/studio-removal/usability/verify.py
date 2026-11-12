import json, hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
def report(stage): return json.loads((p/stage/'report.json').read_text())
a,b,c,d=[report(s) for s in ['01-old-pot','02-remove','04-remove-replay','11-final']]
checks={}
for node in ['body','arm']:
 for field in ['bounds','anchors','features']:
  checks[node+' '+field+' unchanged after removal']=a['nodes'][node][field]==b['nodes'][node][field]
  checks[node+' '+field+' unchanged finally']=a['nodes'][node][field]==d['nodes'][node][field]
checks['removal replay same revision']=b['revision']==c['revision']
checks['undo restored original render revision']=report('03-restored')['revision']==a['revision']
checks['undo restored original artwork bytes']=(p/'01-old-pot/artwork.png').read_bytes()==(p/'03-restored/artwork.png').read_bytes()
checks['source sha256']=hashlib.sha256((p/'source.json').read_bytes()).hexdigest()
checks['observed undo byte hash from shell']='9fd6a48d147305c3abc88375d5f4983105ddb5233a739204379d1afbbcc88b92'
checks['final bowl attachment']=d['nodes']['bowl']['attachment']
(p/'verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
