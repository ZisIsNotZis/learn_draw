"""Use the inexpensive base mesh to discriminate enclosure views, not final finish."""
from contact import PREVIOUS,OUT,solve
from render_contact import run
import json

if __name__=='__main__':
    data=PREVIOUS['load']();result=solve(data,rod_radius=.006)
    (OUT/'13-proxy-camera-pose.json').write_text(json.dumps(dict(status='view-selection proxy; not a preset/quality pass',diagnostic=result['diagnostic']),indent=2),encoding='utf8')
    for name,yaw,pitch in [('under-palm',-30,-35),('thumb-side',-65,-15),('back',150,-15)]:
        run(data,result,OUT/'13-proxy-camera-views',name=name,yaw=yaw,pitch=pitch)
