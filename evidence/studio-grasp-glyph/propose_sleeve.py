"""Align a drawn sleeve's terminal tangent with the observed wrist approach.

Only the existing stroke bend changes. Root/tip and the whole dependent hand/can
graph stay pinned. This is an authoring calculation, not automatic whole-body IK.
"""
from cli_steps import ROOT,Recorder
from pathlib import Path
import json,numpy as np
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    scene=HERE/'native-watering-working.json';view=HERE/'08-sleeve-observe';trial=HERE/'09-sleeve-tangent'
    if view.exists() or trial.exists():raise SystemExit('sleeve outputs exist; preserve this run')
    cli=Recorder(HERE/'sleeve-commands.json')
    cli.run('inspect',scene,'--object','reaching-sleeve','--feature','object','--outdir',view)
    report=json.loads((view/'report.json').read_text());nodes=report['nodes']
    root=np.array(nodes['reaching-sleeve']['anchors']['root']['point']);tip=np.array(nodes['reaching-sleeve']['anchors']['tip']['point'])
    wrist=np.array(nodes['carrying-hand']['anchors']['wrist']['point']);grip=np.array(nodes['carrying-hand']['anchors']['grip']['point'])
    assert np.allclose(tip,wrist)
    chord=tip-root;chord/=np.linalg.norm(chord);across=np.array([chord[1],-chord[0]])
    approach=grip-wrist;approach/=np.linalg.norm(approach)
    if np.dot(approach,chord)<=0:raise ValueError('this quadratic sleeve cannot turn back into its root; choose another gesture')
    bend=float(-np.dot(approach,across)/(4*np.dot(approach,chord)))
    cli.run('preview',scene,'--selection',view/'selection.json','--set','bend','--value',bend,
        '--reason','The cuff cuts across the wrist; turn the sleeve tangent into the hand while keeping both terminals fixed','--outdir',trial)
    after=json.loads((trial/'report.json').read_text())['nodes']
    for name in ('root','tip'):assert nodes['reaching-sleeve']['anchors'][name]==after['reaching-sleeve']['anchors'][name]
    for name in ('wrist','grip','handle_left','handle_right'):
        assert nodes['carrying-hand']['anchors'][name]==after['carrying-hand']['anchors'][name]
    (trial/'relation-check.json').write_text(json.dumps(dict(proposed_bend=bend,sleeve_terminals_preserved=True,grip_mounts_preserved=True),indent=2),encoding='utf8')
    print('Cuff tangent preview ready; bend '+str(bend),flush=True)
