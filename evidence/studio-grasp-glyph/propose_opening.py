"""Initial authoring of one new can interior, previewed before accepting the scene.

Uses the model/bundle authoring API, not a claim that public CLI has atomic insertion.
"""
from pathlib import Path
import sys,copy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,validate,fingerprint,engine_fingerprint,select,node_by_id
from scripts.studio.render import bundle
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    scene=read(HERE/'native-watering-working.json');out=HERE/'12-can-opening'
    if out.exists():raise SystemExit('opening proposal already exists')
    revised=copy.deepcopy(scene);body=node_by_id(scene,'can-body')
    revised['nodes'].append(dict(id='can-opening',kind='shape',intent='a dark oval interior makes the watering vessel opening explicit',
        profile='oval',length=.022,width=4.2,angle=body.get('angle',0),stroke=0,depth=10.5,
        palette=dict(fill='#89723c'),attachment=dict(to='can-body',self='center',target='top',inset=.10)))
    validate(revised)
    candidate=dict(status='preparing',base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(revised),scene=revised,
        operation=dict(action='authoring-insert',object='can-opening',reason='The reservoir reads as a flat yellow block; place its opening using the actual top mount'))
    write(out/'candidate.json',candidate)
    report=bundle(revised,out,select(revised,'can-opening',feature='object'))
    if report['status']!='ready':raise RuntimeError('opening did not finish rendering')
    candidate['status']='ready';write(out/'candidate.json',candidate)
    print('Can opening authoring preview ready; working scene has not changed.',flush=True)
