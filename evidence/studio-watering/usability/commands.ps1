# Executed public CLI sequence (repository cwd; CPU renderer). Logs named by step.
# The fixture was copied unmodified to source.json and working.json before execution.
$py = '.venv/Scripts/python.exe'
$b = 'evidence/studio-watering/usability'
& $py -m scripts.studio --help
& $py -m scripts.studio inspect --help
& $py -m scripts.studio preview --help
& $py -m scripts.studio inspect $b/working.json --object gardener --feature object --outdir $b/01-gardener
& $py -m scripts.studio preview $b/working.json --selection $b/01-gardener/selection.json --move left --amount .05 --reason 'Give the window and watering action more room by shifting the connected gardener left' --outdir $b/02-left
& $py -m scripts.studio accept $b/working.json $b/02-left/candidate.json
& $py -m scripts.studio inspect $b/working.json --object water --feature tip --outdir $b/04-water-tip
& $py -m scripts.studio preview $b/working.json --selection $b/04-water-tip/selection.json --move right --amount .065 --reason 'Return the stream landing into the soil opening after moving the gardener left while keeping its source at the spout' --outdir $b/05-pour-correction
& $py -m scripts.studio accept $b/working.json $b/05-pour-correction/candidate.json
& $py -m scripts.studio inspect $b/working.json --object water --feature tip --outdir $b/07-tip-reinspect
& $py -m scripts.studio preview $b/working.json --selection $b/07-tip-reinspect/selection.json --move up --amount .008 --reason 'Lift the water landing away from the front rim into the soil opening' --outdir $b/08-landing-inset
& $py -m scripts.studio accept $b/working.json $b/08-landing-inset/candidate.json
& $py -m scripts.studio inspect $b/working.json --object water --feature tip --outdir $b/final
& $py scripts/draw.py check --help
& $py scripts/draw.py check $b/final/artwork.png --outdir $b/check
