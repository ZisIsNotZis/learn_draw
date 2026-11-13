"""Compare a Loop-refined bind surface at the same contact construction.

Install the hash-pinned optional study dependency into .tmp/grasp-deps. No project
environment/lock or production mesh is changed. Trimesh supplies subdivision; the
same linear topology operator is applied to all skin weights, preserving all joints.
"""
from contact import ROOT,OUT,PREVIOUS,solve
from render_contact import run
import sys,json
import numpy as np
sys.path.insert(0,str(ROOT/'.tmp/grasp-deps'))
import trimesh
from trimesh.remesh import subdivide_loop

def refine(data):
    _,first,inverse=np.unique(np.round(data['vertices'],9),axis=0,return_index=True,return_inverse=True)
    v=data['vertices'][first];faces=inverse[data['faces']]
    weights=np.zeros((len(data['vertices']),25))
    for slot in range(data['indices'].shape[1]):
        weights[np.arange(len(weights)),data['indices'][:,slot]]+=data['weights'][:,slot]
    assert np.max(np.abs(weights-weights[first][inverse]))<1e-6
    weights=weights[first]
    refined,newfaces=subdivide_loop(v,faces,iterations=1)
    extended=np.pad(weights,((0,0),(0,2)))
    channels=[]
    for start in range(0,27,3):
        channel,checkfaces=subdivide_loop(extended[:,start:start+3],faces,iterations=1)
        assert np.array_equal(checkfaces,newfaces)
        channels.append(channel)
    weights=np.column_stack(channels)[:,:25]
    assert np.max(np.abs(weights.sum(axis=1)-1))<1e-6
    cross=np.cross(data['vertices'][data['faces'][:,1]]-data['vertices'][data['faces'][:,0]],data['vertices'][data['faces'][:,2]]-data['vertices'][data['faces'][:,0]])
    sign=1 if np.median(np.einsum('ij,ij->i',cross,data['normals'][data['faces']].mean(axis=1)))>0 else -1
    tri=refined[newfaces];normal=sign*np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals=np.zeros_like(refined)
    for slot in range(3):np.add.at(normals,newfaces[:,slot],normal)
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    updated=data|dict(vertices=refined,faces=newfaces,normals=normals,weights=weights,indices=np.tile(np.arange(25),(len(refined),1)))
    updated['refinement']=dict(method='trimesh.remesh.subdivide_loop',version=trimesh.__version__,iterations=1,
        original_vertices=len(data['vertices']),welded_vertices=len(v),vertices=len(refined),faces=len(newfaces),
        maximum_weight_sum_error=float(np.max(np.abs(weights.sum(axis=1)-1))),all_25_weights_preserved=True)
    return updated

if __name__=='__main__':
    data=refine(PREVIOUS['load']())
    result=solve(data)
    np.savez(OUT/'bind-06.npz',**{k:data[k] for k in ('vertices','normals','faces','weights','indices')})
    np.savez(OUT/'pose-06.npz',**{k:result[k] for k in ('vertices','normals','joints','axis','forward','palmar','center','radius','half_length')})
    (OUT/'pose-06.json').write_text(json.dumps(dict(refinement=data['refinement'],diagnostic=result['diagnostic'],thumb=result['thumb'],iterations=result['iterations']),indent=2),encoding='utf8')
    print(json.dumps(data['refinement']|dict(diagnostic=result['diagnostic']),indent=2),flush=True)
    run(data,result,OUT/'06-loop-surface')
