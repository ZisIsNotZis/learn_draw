"""Refine the visible flow gesture using actual nozzle and destination directions."""
from cli_steps import ROOT,Recorder
from pathlib import Path
import json,math,numpy as np
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    scene=HERE/'native-watering-working.json';view=HERE/'13-water-observe';trial=HERE/'14-water-flow'
    if view.exists() or trial.exists():raise SystemExit('water refinement outputs already exist')
    cli=Recorder(HERE/'water-commands.json')
    cli.run('inspect',scene,'--object','water','--feature','object','--outdir',view)
    nodes=json.loads((view/'report.json').read_text())['nodes'];raw=json.loads(scene.read_text())
    spout=next(n for n in raw['nodes'] if n['id']=='spout');a=math.radians(spout.get('angle',0))
    nozzle=np.array([math.sin(a),math.cos(a)])-4*spout.get('bend',0)*np.array([math.cos(a),-math.sin(a)])
    nozzle/=np.linalg.norm(nozzle)
    start=np.array(nodes['water']['anchors']['root']['point']);end=np.array(nodes['water']['anchors']['tip']['point'])
    direction=end-start;direction/=np.linalg.norm(direction);across=np.array([direction[1],-direction[0]])
    if np.dot(nozzle,direction)<=0:raise ValueError('nozzle points away from the destination; revise its pose first')
    bend=float(np.dot(nozzle,across)/(4*np.dot(nozzle,direction)))
    cli.run('preview',scene,'--selection',view/'selection.json','--change','bend='+str(bend),'--change','start_width=.85','--change','end_width=.45',
        '--change','fill_color=#78a9b5','--reason','The stream should leave along the spout and narrow as it falls into the soil','--outdir',trial)
    after=json.loads((trial/'report.json').read_text())['nodes']
    for end in ('root','tip'):assert nodes['water']['anchors'][end]==after['water']['anchors'][end]
    (trial/'relation-check.json').write_text(json.dumps(dict(proposed_bend=bend,water_terminals_preserved=True,
        scope='authored quadratic flow gesture, not fluid simulation'),indent=2),encoding='utf8')
    print('Flow preview ready; both endpoints preserved; bend '+str(bend),flush=True)
