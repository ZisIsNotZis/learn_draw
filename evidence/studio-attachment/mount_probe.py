import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import write,select,attachment_preview,validate
from scripts.studio.render import bundle
from scripts.studio.attachment import resolve_scene,anchors
s=default_scene('shape');s['nodes'][0].update(id='base',length=.10,width=2.2,depth=0,profile='oval',at=dict(anchor='center',offset=[0,.24]))
s['nodes'].append(dict(id='stem',kind='shape',intent='a narrow support to seat on the base',length=.32,width=.09,depth=1,palette={'fill':'#705448'},stroke=0))
out=Path('evidence/studio-attachment/probe-labels');out.mkdir(exist_ok=True)
bundle(s,out/'before',select(s,'stem',feature='anchors'))
bundle(s,out/'target',select(s,'base',feature='anchors'))
c=attachment_preview(s,select(s,'stem',feature='anchors'),select(s,'base',feature='anchors'),'bottom','top',.02,'Seat the stem on the visible base and preserve its mount when resized')
bundle(c['scene'],out/'after',c['selection'],s)
write(out/'candidate.json',c)
resolved=resolve_scene(c['scene']);print([(n['id'],anchors(n,s['canvas'])) for n in resolved['nodes']])
