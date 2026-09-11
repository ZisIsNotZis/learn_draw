# probe.py — per-round zone distance check
"""Round probe: render scene.yaml, print overall + zone distances."""
import cv2, numpy as np, subprocess, sys

SCENE = '.scratch/05-portrait-scene/work/scene.yaml'
OUT = '/tmp/gen_s.png'
ZONES = {"hat":(430,0,594,300),"face":(580,150,250,270),"ribbon":(0,380,560,450),
         "skirt":(400,640,500,384),"torso":(560,430,340,300),"curtain":(790,270,234,500)}

r = subprocess.run(['.venv/bin/python','scripts/scene_render.py',SCENE,'-o',OUT,'--ref','image.jpg'],
                   capture_output=True,text=True)
if r.returncode != 0:
    print("RENDER FAIL:"); print(r.stdout[-2000:]); print(r.stderr[-2000:]); sys.exit(1)
ref_img = cv2.imread('image.jpg')
dr_img = cv2.imread(OUT)
if ref_img is None or dr_img is None:
    raise RuntimeError("render failed: missing output image")
ref = ref_img.astype(int)
dr = dr_img.astype(int)
print("overall:", round(np.linalg.norm(ref-dr,axis=2).mean(),1))
for n,(x,y,w,h) in ZONES.items():
    v = np.linalg.norm(ref[y:y+h,x:x+w]-dr[y:y+h,x:x+w],axis=2).mean()
    print(f"  {n}: {v:.1f}")
