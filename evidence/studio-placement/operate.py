"""Actual public-CLI placement study; run one observed stage at a time."""
from pathlib import Path
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
WORK=HERE/'working.json'
def run(*args):
    command=[sys.executable,'-m','scripts.studio',*map(str,args)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    with (HERE/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(args=list(map(str,args)),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))+'\n')
    if result.returncode:raise RuntimeError(result.stderr)
def main(stage):
    if stage=='first':
        run('inspect',WORK,'--object','flag','--feature','anchors','--outdir',HERE/'00-flag-observe')
        run('place',WORK,'--kind','sun','--id','sun-badge','--at','upper_center','--offset','.03','.1','--change','length=.16','--change','intent=A warm sun emblem centered on the signal banner','--reason','Give the plain signal flag a single clear emblem','--outdir',HERE/'01-badge-default')
    elif stage=='quiet':
        run('place',WORK,'--revise',HERE/'01-badge-default/candidate.json','--change','rays=0','--change','length=.095','--reason','The sun crown crowds the banner; use a quieter smaller disc','--outdir',HERE/'02-badge-quiet')
    elif stage=='seat':
        run('place',WORK,'--revise',HERE/'02-badge-quiet/candidate.json','--attach',HERE/'00-flag-observe/selection.json','--self-anchor','center','--target-anchor','center','--reason','Center the observed disc on the actual banner so it follows the flag','--outdir',HERE/'03-badge-seated')
    elif stage=='accept':
        run('accept',WORK,HERE/'03-badge-seated/candidate.json')
        run('inspect',WORK,'--object','sun-badge','--outdir',HERE/'04-accepted')
    elif stage=='undo':
        run('undo',WORK);run('inspect',WORK,'--object','flag','--outdir',HERE/'05-undone')
    elif stage=='restore':
        run('accept',WORK,HERE/'03-badge-seated/candidate.json')
        run('inspect',WORK,'--object','sun-badge','--outdir',HERE/'06-restored')
    elif stage=='discard':
        run('place',WORK,'--kind','moon','--id','second-badge','--at','upper_center','--offset','.03','.1','--change','length=.12','--reason','Try whether a second crescent adds useful meaning','--outdir',HERE/'07-extra-emblem')
    else:raise ValueError(stage)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage');main(parser.parse_args().stage)
