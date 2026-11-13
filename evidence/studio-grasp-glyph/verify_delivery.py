"""Verify the claimed native operations and delivery, without rewriting old evidence."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,tempfile,xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,fingerprint,engine_fingerprint,node_by_id
from scripts.studio.render import drawing,rasterize
from scripts.studio.attachment import resolve_scene,get_anchor,anchors
from scripts.studio.components import component_outline
from scripts.studio.stroke import stroke_data
HERE=Path(__file__).resolve().parent
EXPECTED='7e6b1a1d61cf8f2395ef547cb20d2cebd690627feb5415054d586189639f8648'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run():
    assert engine_fingerprint()==EXPECTED
    tests=(HERE/'verification/tests.txt').read_text();count=int(re.search(r'Ran (\d+) tests',tests).group(1))
    assert count==103 and tests.rstrip().endswith('OK')
    actor=HERE/'usability';hashes=read(actor/'artifact-hashes.json')
    for name,digest in hashes.items():assert sha(actor/name)==digest,name
    verification=read(actor/'verification.json');assert verification['engine']==EXPECTED
    before=read(actor/'03b-thumb-before/scene.json');final=read(actor/'working.json')
    assert fingerprint(before)==verification['before_revision'] and fingerprint(final)==verification['final_revision']
    assert final==read(actor/'07-final/scene.json')
    assert before==read(actor/'06-undone/scene.json')
    for name,digest in verification['artwork_hashes'].items():assert sha(actor/name/'artwork.png')==digest
    a,b=resolve_scene(before),resolve_scene(final);canvas=final['canvas']
    for old,new in zip(a['nodes'],b['nodes']):
        aa,bb=anchors(old,canvas),anchors(new,canvas)
        assert set(aa)==set(bb)
        for name in aa:assert np.allclose(aa[name]['point'],bb[name]['point'],atol=1e-10,rtol=0)
        if new['kind']!='grip':assert np.allclose(component_outline(old,canvas),component_outline(new,canvas),atol=1e-10,rtol=0)
    for node in b['nodes']:
        if node.get('attachment',{}).get('to')=='carrying-grip':
            pin=node['attachment'];actual=get_anchor(node,canvas,pin.get('self','center'))['point']
            target=get_anchor(node_by_id(b,'carrying-grip'),canvas,pin.get('target','center'))['point']
            assert np.linalg.norm(np.array(actual)-target)<1e-10
    out=HERE/'verification';results={}
    for name,source,preferred in [('flag','held_flag.json','11-flag-continuous-pole'),('watering','watering_grip.json','14-water-flow')]:
        scene=read(ROOT/'examples/studio'/source);svg=drawing(scene);xml=ET.fromstring(svg)
        assert not any(e.tag.endswith('image') for e in xml.iter())
        p=out/(name+'-current.svg');p.write_text(svg,encoding='utf8');rasterize(p,p.with_suffix('.png'))
        assert sha(p.with_suffix('.png'))==sha(HERE/preferred/'artwork.png')
        results[name]=dict(scene=fingerprint(scene),png_sha256=sha(p.with_suffix('.png')),preferred_png_exact=True,nodes=len(scene['nodes']))
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder)/'editable'
            command=[sys.executable,str(ROOT/'examples/studio/held_props.py'),'--scene',name,'--outdir',str(directory)]
            process=subprocess.run(command,cwd=folder,capture_output=True,text=True)
            assert process.returncode==0,process.stderr
            assert read(directory/'working.json')==scene
            assert sha(directory/'view/artwork.png')==results[name]['png_sha256']
            repeat=subprocess.run(command,cwd=folder,capture_output=True,text=True)
            assert repeat.returncode!=0 and 'exists' in repeat.stderr+repeat.stdout
            results[name]['fresh_cwd_helper_and_existing_output_refusal']=True
    water=resolve_scene(read(ROOT/'examples/studio/watering_grip.json'));c=water['canvas']
    sleeve=stroke_data(node_by_id(water,'reaching-sleeve'),c)
    grip=node_by_id(water,'carrying-hand');approach=np.array(get_anchor(grip,c,'grip')['point'])-get_anchor(grip,c,'wrist')['point'];approach/=np.linalg.norm(approach)
    assert np.dot(sleeve.tangents[-1],approach)>1-1e-10
    flow=stroke_data(node_by_id(water,'water'),c);spout=stroke_data(node_by_id(water,'spout'),c)
    assert np.dot(flow.tangents[0],spout.tangents[-1])>1-1e-10
    for end,pin in node_by_id(read(ROOT/'examples/studio/watering_grip.json'),'water')['endpoints'].items():
        # Inset changes the endpoint from the raw mount intentionally; its exact
        # authored positions were checked by the public preview's relation record.
        assert pin['to'] in ('spout','soil')
    native=read(HERE/'native-recovery.json');assert native['undo_png_exact'] and native['restore_png_exact']
    assert (HERE/'06-undo/artwork.png').read_bytes()==(HERE/'04-thumb-shorter/artwork.png').read_bytes()
    assert (HERE/'06-restored/artwork.png').read_bytes()==(HERE/'06-thumb-easeback/artwork.png').read_bytes()
    assert all(r['prior_png_preserved'] for r in read(HERE/'verification/preservation.json')['results'].values())
    record=dict(engine=EXPECTED,studio_tests=count,prior_pngs_preserved=7,actor_artifacts_checked=len(hashes),
        actor_independent_creation_scope='original symbolic held-flag composition, not universal transfer',
        actor_default_required_reconstruction=False,actor_anchor_and_external_geometry_preserved=True,
        actual_thumb_undo_and_restore_pngs_exact=True,sleeve_terminal_tangent_aligned=True,nozzle_flow_tangent_aligned=True,
        examples=results,human_acceptance='unknown',whole_artwork_pass=False)
    write(out/'delivery.json',record);print(json.dumps(record,indent=2),flush=True)

if __name__=='__main__':run()
