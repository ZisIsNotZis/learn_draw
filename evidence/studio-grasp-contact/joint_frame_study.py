"""Retain actual WebXR palm directions while solving the same contact task."""
from contact import PREVIOUS,OUT,solve
from smooth_study import refine
from geometry_checks import skin_crossings
from render_contact import run
import numpy as np,json

if __name__=='__main__':
    data=refine(PREVIOUS['load']());result=solve(data)
    crossings=skin_crossings(data,result['vertices'])
    np.savez(OUT/'pose-07.npz',**{k:result[k] for k in ('vertices','normals','joints','axis','forward','palmar','center','radius','half_length')})
    (OUT/'pose-07.json').write_text(json.dumps(dict(refinement=data['refinement'],diagnostic=result['diagnostic'],thumb=result['thumb'],iterations=result['iterations'],self_contact=crossings),indent=2),encoding='utf8')
    print(json.dumps(dict(rod=result['diagnostic'],self_crossing_pairs=len(crossings['transverse_pairs'])),indent=2),flush=True)
    run(data,result,OUT/'07-actual-joint-frames')
