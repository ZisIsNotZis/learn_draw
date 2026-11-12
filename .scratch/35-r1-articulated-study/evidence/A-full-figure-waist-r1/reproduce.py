"""CPU-only reproduction; no reference image required. Uses an isolated Edge profile."""
from pathlib import Path
import argparse, subprocess, sys, tempfile
p=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--edge', default='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
a=parser.parse_args()
subprocess.run([sys.executable,str(p/'source/build_full.py'),'--out',str(p/'artwork.svg'),'--report',str(p/'build-report.json')], check=True)
with tempfile.TemporaryDirectory(prefix='waist-cpu-') as profile:
    subprocess.run([a.edge,'--headless','--disable-gpu','--hide-scrollbars','--no-sandbox','--user-data-dir='+profile,'--screenshot='+str(p/'artwork.png'),'--window-size=1024,1024',(p/'artwork.svg').as_uri()],check=True,timeout=60)
