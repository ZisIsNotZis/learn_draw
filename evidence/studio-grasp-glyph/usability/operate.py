"""Independent flag study. Public CLI only; all authored geometry is semantic."""
import json, pathlib, subprocess, sys, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
SCENE=ROOT/'working.json'
def run(*args):
    command=[sys.executable,'-m','scripts.studio',*map(str,args)]
    result=subprocess.run(command,capture_output=True,text=True)
    with (ROOT/'commands.jsonl').open('a',encoding='utf8') as f:
        f.write(json.dumps(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))+'\n')
    print(result.stdout,flush=True)
    if result.returncode: raise RuntimeError(result.stderr)
def inspect(obj,feature,out):
    run('inspect',SCENE,'--object',obj,'--feature',feature,'--outdir',ROOT/out)
    report=json.loads((ROOT/out/'report.json').read_text())
    assert report['engine']=='7e6b1a1d61cf8f2395ef547cb20d2cebd690627feb5415054d586189639f8648',report['engine']
def preview(view,out,*args):
    run('preview',SCENE,'--selection',ROOT/view/'selection.json',*args,'--outdir',ROOT/out)
def accept(out): run('accept',SCENE,ROOT/out/'candidate.json')
if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='place':
        (ROOT/'initial-default.json').write_bytes(SCENE.read_bytes())
        s=json.loads(SCENE.read_text())
        s['nodes'][0].update(intent='a raised closed hand gripping the flagpole through its owned handle',length=.24,angle=90,at={'anchor':'center','offset':[-.08,.13]},palette={'skin':'#edbd91','ink':'#4f3e37','handle':'#705041','handle_ink':'#4f3e37'})
        SCENE.write_text(json.dumps(s,indent=2)+'\n')
        inspect('carrying-grip','anchors','01-positioned')
    elif stage=='compose':
        s=json.loads(SCENE.read_text()); report=json.loads((ROOT/'01-positioned/report.json').read_text()); dims=report['nodes']['carrying-grip']['dimensions_canvas']
        pole=dims['handle_thickness']; wrist=dims['wrist_width']
        s['nodes'] += [
          dict(id='upper-pole',kind='stroke',intent='the upper flagpole continues the included gripped segment',length=.28,angle=180,thickness=pole,ink_width=0,palette={'fill':'#705041'},depth=-1,attachment={'to':'carrying-grip','self':'root','target':'handle_right'}),
          dict(id='lower-pole',kind='stroke',intent='the lower flagpole continues below the gripping hand',length=.08,angle=0,thickness=pole,ink_width=0,palette={'fill':'#705041'},depth=-1,attachment={'to':'carrying-grip','self':'root','target':'handle_left'}),
          dict(id='sleeve',kind='stroke',intent='a blue forearm enters the raised wrist',length=.32,angle=65,thickness=wrist,start_cap='flat',end_cap='flat',palette={'fill':'#284d68'},depth=-1,attachment={'to':'carrying-grip','self':'root','target':'wrist'}),
          dict(id='flag',kind='shape',intent='a bright coral rectangular banner extends right from the pole',length=.19,width=1.8,rounding=0,stroke=0,palette={'fill':'#d84e43'},depth=-2,attachment={'to':'upper-pole','self':'left','target':'tip','offset':[0,.085]}),
        ]
        SCENE.write_text(json.dumps(s,indent=2)+'\n')
        inspect('carrying-grip','anchors','02-composition')
    elif stage=='thumb':
        inspect('carrying-grip','thumb','03-thumb-before')
    elif stage=='refine':
        preview('03b-thumb-before','04-thumb-shorter','--set','thumb_reach','--value','.72','--reason','Shorten the long thumb crossbar so the stacked finger pads stay more legible in the raised-hand symbol; keep the wrist and pole mounts fixed')
    elif stage=='seat-sleeve':
        (ROOT/'first-composition.json').write_bytes(SCENE.read_bytes())
        s=json.loads(SCENE.read_text())
        next(n for n in s['nodes'] if n['id']=='sleeve')['angle']=90
        SCENE.write_text(json.dumps(s,indent=2)+'\n')
        inspect('carrying-grip','thumb','03b-thumb-before')
    elif stage=='accept':
        (ROOT/'before-refinement.json').write_bytes(SCENE.read_bytes())
        accept('04-thumb-shorter')
        (ROOT/'accepted-refinement.json').write_bytes(SCENE.read_bytes())
        inspect('carrying-grip','anchors','05-accepted')
    elif stage=='undo':
        run('undo',SCENE)
        (ROOT/'undo-restored.json').write_bytes(SCENE.read_bytes())
        inspect('carrying-grip','anchors','06-undone')
    elif stage=='reaccept':
        accept('04-thumb-shorter')
        inspect('carrying-grip','anchors','07-final')
