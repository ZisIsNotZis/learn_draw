"""Parent finishing, separate from the untouched independent operator's result."""
from cli_steps import Recorder
from pathlib import Path
import json,shutil
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    scene=HERE/'flag-finishing-working.json';view=HERE/'10-flag-handle-observe';trial=HERE/'11-flag-continuous-pole'
    if scene.exists() or view.exists() or trial.exists():raise SystemExit('flag finishing record already exists')
    shutil.copyfile(HERE/'usability/working.json',scene)
    data=json.loads(scene.read_text());grip=next(n for n in data['nodes'] if n['kind']=='grip')
    colour=grip['palette']['handle'];cli=Recorder(HERE/'flag-finishing-commands.json')
    cli.run('inspect',scene,'--object',grip['id'],'--feature','handle','--outdir',view)
    cli.run('preview',scene,'--selection',view/'selection.json','--set','handle_ink_color','--value',colour,
        '--reason','The pole changes outline treatment at the held segment; match its visible material to the plain extensions','--outdir',trial)
    before=json.loads((view/'report.json').read_text())['nodes'];after=json.loads((trial/'report.json').read_text())['nodes']
    for name in before:
        assert before[name]['anchors']==after[name]['anchors'] and before[name]['bounds']==after[name]['bounds']
    print('Pole material preview ready; every bound and mount is unchanged.',flush=True)
