"""Reproduce a head study; canonical drawing lives in scripts.studio.head.
Use scripts.studio new --kind head for revision-bound editing.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.studio.head import generate

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',required=True)
    parser.add_argument('--eye-scale',type=float,default=1)
    parser.add_argument('--jaw',type=float,default=.42)
    parser.add_argument('--hair',choices=('none','bob','side-part'),default='none')
    parser.add_argument('--svg-only',action='store_true')
    args=parser.parse_args()
    print(generate(args.outdir,args.eye_scale,args.jaw,args.hair,args.svg_only))
