"""Reproduce a small original illustration using only public studio commands.

No path coordinates or reference inputs. Each operation has inspect, preview,
and acceptance artifacts; a Python wrapper only runs the documented CLI.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def compose(directory,theme='moonrise',refined=False):
    directory=Path(directory)
    if directory.exists(): raise ValueError('choose a fresh output directory')
    directory.mkdir(parents=True)
    working=directory/'working.json';commands=[]
    def run(*args):
        command=[sys.executable,'-m','scripts.studio',*map(str,args)]
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
        commands.append(dict(args=list(map(str,args)),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        (directory/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
        if result.returncode: raise RuntimeError(result.stderr)
    run('new',working,'--kind','landscape')
    celestial='moon' if theme=='moonrise' else 'sun'
    run('add',working,'--kind',celestial)
    run('inspect',working,'--object',celestial,'--outdir',directory/'01-default')
    def edit(index,object,reason,**operation):
        before=directory/(index+'-before');after=directory/index
        run('inspect',working,'--object',object,'--outdir',before)
        args=['preview',working,'--selection',before/'selection.json','--reason',reason,'--outdir',after]
        for key,value in operation.items(): args.extend(['--'+key,str(value)])
        run(*args);run('accept',working,after/'candidate.json')
    if theme=='moonrise':
        edit('02-lower-moon','moon','Bring the moon closer to the ridges so it belongs to the landscape',move='down',amount=.27)
        edit('03-shift-moon','moon','Leave more breathing room on the right and bring the focal point inward',move='left',amount=.08)
        edit('04-slim-crescent','moon','Use a quieter slender crescent instead of the broad default',set='fullness',value=.28)
    else:
        edit('02-daylight','sky','Choose an open daylight atmosphere; default dusk stars should disappear',set='style',value='day')
        edit('03-lower-sun','sun','Bring the sun towards the horizon while keeping it fully readable',move='down',amount=.18)
        edit('04-far-gold','ridges','Warm the distant ridge to match the clear daylight',set='far_color',value='#bda18c')
        edit('05-middle-rust','ridges','Separate the middle ridge with muted terracotta',set='middle_color',value='#aa7970')
        edit('06-near-plum','ridges','Give the near ridge a firm muted plum silhouette',set='near_color',value='#66576a')
    if refined and theme=='moonrise':
        edit('05-foreground-grove','ridges','Give the empty left side a subordinate group and a scale cue rooted on the ridge',set='trees',value=3)
        edit('06-tree-height','ridges','Let the foreground grove read clearly against the middle ridge',set='tree_scale',value=.21)
        edit('07-visible-stars','sky','Make the restrained star field survive the dark sky without competing with the moon',set='stars_color',value='#ffecc7')
    elif refined:
        edit('07-new-landform','ridges','Make daylight a different landform rather than a palette swap',set='seed',value=2)
        edit('08-left-sun','sun','Balance the rising terrain with a sun on the left',move='left',amount=.65)
        edit('09-soft-disc','sun','Use a quiet disc instead of a gear-like crown in this soft landscape',set='rays',value=0)
        edit('10-near-earth','ridges','Lighten the near ground into warm earth appropriate to daylight',set='near_color',value='#92745f')
        edit('11-middle-grass','ridges','Give the middle distance a warmer grassy tone',set='middle_color',value='#b7a077')
        edit('12-higher-ground','ridges','Reduce empty sky and let the changing landform occupy more of the composition',set='horizon',value=.54)
    run('inspect',working,'--object',celestial,'--outdir',directory/'final')
    (directory/'intent.json').write_text(json.dumps(dict(theme=theme,
        intent='A quiet graphic landscape with one celestial focal point and three receding ridges',
        reference=None,method='public CLI and semantic edits only',refined=refined,
        scope='a small flat-vector illustration; not portrait completion or universal drawing ability'),indent=2)+'\n',encoding='utf-8')
    return str(directory/'final/artwork.png')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',required=True)
    parser.add_argument('--theme',choices=('moonrise','daylight'),default='moonrise')
    parser.add_argument('--refined',action='store_true',help='include the concrete post-review composition changes')
    args=parser.parse_args()
    print(compose(args.outdir,args.theme,args.refined))
