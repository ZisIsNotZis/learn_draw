import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import read,select,attachment_preview,write,engine_fingerprint
from scripts.studio.render import bundle
s=read('evidence/studio-attachment/usability/working.json')
trial=attachment_preview(s,select(s,'tip',feature='anchors'),select(s,'arm',feature='anchors'),'bottom','top',.65,'Demonstrate the originally refused embedding as a whole preview, not an automatic art improvement')
out=Path('evidence/studio-attachment/inset-study');bundle(trial['scene'],out,trial['selection'],s)
write(out/'candidate.json',trial|dict(status='ready'))
write(out/'disposition.json',dict(engine=engine_fingerprint(),old_creator_inset=.5,permitted_probe_inset=.65,pre_fix_refused=True,now_rendered_ready=True,accepted=False,meaning='a separately labeled control-permission probe; no source/working scene or raw creator result changed; no art improvement claimed'))
print('originally refused .65 rendered as a separate unaccepted proposal')
