"""Load the complete studio family with package names (tests use relative imports)."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
if __name__=='__main__':
    names=['scripts.tests.'+p.stem for p in sorted((ROOT/'scripts/tests').glob('test_studio*.py'))]
    print('Modules: '+', '.join(names),flush=True)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    raise SystemExit(0 if result.wasSuccessful() else 1)
