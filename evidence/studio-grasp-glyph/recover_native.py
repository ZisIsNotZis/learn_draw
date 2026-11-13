"""Undo and restore the actual observed thumb correction through public commands."""
from cli_steps import ROOT,Recorder
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    undo=HERE/'06-undo';restored=HERE/'06-restored'
    if undo.exists() or restored.exists():raise SystemExit('recovery outputs exist; preserve this run')
    cli=Recorder(HERE/'native-recovery-commands.json')
    scene=HERE/'native-working.json';candidate=HERE/'06-thumb-easeback/candidate.json'
    cli.run('undo',scene)
    cli.run('inspect',scene,'--feature','thumb','--outdir',undo)
    assert (undo/'artwork.png').read_bytes()==(HERE/'04-thumb-shorter/artwork.png').read_bytes()
    cli.run('accept',scene,candidate)
    cli.run('inspect',scene,'--feature','thumb','--outdir',restored)
    assert (restored/'artwork.png').read_bytes()==(HERE/'06-thumb-easeback/artwork.png').read_bytes()
    (HERE/'native-recovery.json').write_text(json.dumps(dict(undo_png_exact=True,restore_png_exact=True,
        restored_sha256=hashlib.sha256((restored/'artwork.png').read_bytes()).hexdigest()),indent=2),encoding='utf8')
    print('Observed thumb edit undoes and restores to exact prior PNGs.',flush=True)
