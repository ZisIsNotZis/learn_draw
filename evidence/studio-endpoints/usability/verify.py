import json, hashlib
from pathlib import Path
p=Path('evidence/studio-endpoints/usability')
h=lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
r={}
for label, folder in [('source','01-root'),('bound','04-bind-tip'),('gardener_left','06-gardener-left'),('planter_right','08-planter-right'),('released','11-released'),('final','final')]:
 report=json.loads((p/folder/'report.json').read_text())
 nodes=report['nodes']
 r[label]={k:{'anchors':nodes[k]['anchors'],'bounds':nodes[k]['bounds']} for k in ['water','spout','soil','plant-pot','sill']}
 r[label]['artwork_sha256']=h(p/folder/'artwork.png')
r['exact_scene_undo']= (p/'bound-before-release.json').read_bytes()==(p/'working.json').read_bytes()
r['release_exact_paint']=h(p/'09-bound-tip/artwork.png')==h(p/'11-released/artwork.png')
r['undo_exact_paint']=h(p/'09-bound-tip/artwork.png')==h(p/'final/artwork.png')
(p/'observations.json').write_text(json.dumps(r,indent=2))
print({k:v for k,v in r.items() if isinstance(v,bool)})
for stage in ['source','bound','gardener_left','planter_right','released','final']:
 print(stage, 'water',r[stage]['water']['anchors'],'soil',r[stage]['soil']['anchors'])
