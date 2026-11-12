"""A review must inspect the actual raster, not an unnecessary new PNG encoding."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import cv2
import numpy as np
from PIL import Image,PngImagePlugin


class ReviewRasterProvenance(unittest.TestCase):
    def run_check(self,source,directory,reference=None):
        command=[sys.executable,str(Path(__file__).resolve().parents[1]/'draw.py'),'check',str(source),'--outdir',str(directory)]
        if reference: command+=['--ref',str(reference)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_png_bytes_and_metadata_survive_reference_and_reference_free_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source.png'
            y,x=np.indices((128,192));pixels=np.stack((x%256,y%256,(x+y)%256,np.full_like(x,255)),axis=2).astype('uint8')
            info=PngImagePlugin.PngInfo();info.add_text('provenance','preserve this original PNG')
            Image.fromarray(pixels).save(source,pnginfo=info)
            original=source.read_bytes();digest=hashlib.sha256(original).hexdigest()
            for name,reference in (('original',None),('compared',source)):
                out=root/name;self.run_check(source,out,reference)
                full=out/'draft-fullres.png'
                self.assertEqual(full.read_bytes(),original)
                self.assertIn(digest,(out/'report.txt').read_text(encoding='utf-8'))
                self.assertEqual(source.read_bytes(),original)
            # Checking a bundle's own full-resolution file must not rewrite it.
            self.run_check(root/'original/draft-fullres.png',root/'original')
            self.assertEqual((root/'original/draft-fullres.png').read_bytes(),original)

    def test_non_png_input_is_converted_instead_of_renamed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source.jpg'
            y,x=np.indices((128,192));image=np.stack((x%256,y%256,(x+y)%256),axis=2).astype('uint8')
            Image.fromarray(image).save(source)
            self.run_check(source,root/'check')
            target=root/'check/draft-fullres.png'
            self.assertEqual(target.read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
            self.assertTrue(np.array_equal(cv2.imread(str(source)),cv2.imread(str(target))))


if __name__=='__main__': unittest.main()
