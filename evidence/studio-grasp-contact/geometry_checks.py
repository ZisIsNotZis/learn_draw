"""Independent geometric checks for transverse skin self-intersection.

These checks do not certify contact pressure, coplanar overlap, enclosed volumes,
or visual quality. Topological neighbors and grazing contact are not crossings.
"""
import numpy as np

def transverse_crossing(a,b,tolerance=1e-7):
    ea=np.roll(a,-1,axis=0)-a;eb=np.roll(b,-1,axis=0)-b
    na=np.cross(ea[0],ea[1]);nb=np.cross(eb[0],eb[1])
    la,lb=np.linalg.norm(na),np.linalg.norm(nb)
    if min(la,lb)<1e-15:return False
    na/=la;nb/=lb
    da=(b-a[0])@na;db=(a-b[0])@nb
    if not (da.min()<-tolerance and da.max()>tolerance and db.min()<-tolerance and db.max()>tolerance):return False
    axes=np.vstack([na,nb,np.cross(ea[:,None,:],eb[None,:,:]).reshape(-1,3)])
    lengths=np.linalg.norm(axes,axis=1);axes=axes[lengths>1e-14]/lengths[lengths>1e-14,None]
    pa=a@axes.T;pb=b@axes.T
    return not np.any((pa.max(axis=0)<pb.min(axis=0)-tolerance)|(pb.max(axis=0)<pa.min(axis=0)-tolerance))

def skin_crossings(data,vertices,tolerance=1e-7):
    faces=data['faces'];triangles=vertices[faces]
    low=triangles.min(axis=1);high=triangles.max(axis=1)
    _,weld=np.unique(np.round(data['vertices'],9),axis=0,return_inverse=True)
    topology=weld[faces];crossings=[];candidates=0
    for i,tri in enumerate(triangles):
        possible=np.flatnonzero(np.all(high[i]>=low[i+1:]-tolerance,axis=1)&np.all(high[i+1:]>=low[i]-tolerance,axis=1))+i+1
        for j in possible:
            if np.isin(topology[i],topology[j]).any():continue
            candidates+=1
            if transverse_crossing(tri,triangles[j],tolerance):crossings.append((i,int(j)))
    return dict(transverse_pairs=crossings,candidate_pairs=candidates,tolerance_metres=tolerance,
        scope='Non-neighbor transverse skin-surface crossings only; coplanar/grazing contact and enclosed volumes are not certified.')
