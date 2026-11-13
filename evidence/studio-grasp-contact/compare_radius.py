"""A meaningful semantic correction: thinner handle, fingers reconstructed to fit.

Both views use the same renderer/camera. Cached control data are not overwritten.
"""
from contact import PREVIOUS,OUT,solve
from render_contact import run
import numpy as np,json

if __name__=='__main__':
    data=PREVIOUS['load']()|dict(np.load(OUT/'bind-06.npz'))
    control=dict(np.load(OUT/'pose-07.npz'))
    run(data,control,OUT/'08-opaque-partition',pitch=35)
    result=solve(data,rod_radius=.006)
    np.savez(OUT/'pose-09.npz',**{k:result[k] for k in ('vertices','normals','joints','axis','forward','palmar','center','radius','half_length')})
    (OUT/'pose-09.json').write_text(json.dumps(dict(diagnostic=result['diagnostic'],thumb=result['thumb'],iterations=result['iterations']),indent=2),encoding='utf8')
    print(json.dumps(result['diagnostic']),flush=True)
    run(data,result,OUT/'09-thinner-handle',pitch=35)
