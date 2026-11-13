# Independent pending-cover operator — 2026-11-13

Scope: public-tool operation only, using inputs/SKILL.md, inputs/seed.json, CLI help and actual outputs. No source, tests, other studies or external reference were read. Only this usability directory was written. No authored JSON was hand-edited. Source binding in every ready response: `9a610ba4951fd3dca30c01c4a05a23bb36d52e1d2b96555cafeb64b2090ab305`; CPU renderer `resvg-py-0.5.0-cpu`.

Final proposal: `08-refined/candidate.json`, artwork `08-refined/artwork.png`. Base revision `5770caaa0df432fd41ae9e42adfad40c26aaf803d72adb96a5036ee6a55c84e6`; proposed revision `6710283e9c72173d86045fc37cd6af7a13977018df48cf783bcabc63e1937cde`. This candidate can be adopted on the unchanged seed. The operator's independent working.json has been accepted, undone and reaccepted; parent scene was never touched.

The new cover stayed pending through separate root binding, tip binding and bend/thickness revision. Existing 23 nodes are unchanged. Cover depth 10 is below pages 11/12 and above sill 6/apron 7. Both exact positioned mounts were inspected independently and observed before binding: book-left.left@.1 and book-right.right@.9. Length and angle disappeared after the second binding. Object refinement preserved both contacts.

Observed images (each image-tool return preceded the following mutation): 02-left-map edit-closeup; 03-left-mount edit-closeup; 04-right-mount edit-closeup and artwork; 05-pending artwork and alignment; 06-root artwork and edit-closeup; 07-both artwork and edit-closeup; 08-refined artwork, object-closeup and alignment; 10-accepted artwork and edit-closeup; 14-undone artwork and 08-refined artwork before reacceptance; 16-reaccepted artwork.

Art finding: the first negative bow created a sagging bowl beneath the pages. A positive shallow bend follows the rising page bottoms toward the gutter. The final small dark support is subordinate, but round endpoint caps protrude as small lobes and the narrow center wedge does not establish realistic book-cover construction. This is bounded local operation evidence, not whole-artwork acceptance. No metric was used to select geometry.

Usability: positioned edge fractions need a preliminary map and visual confirmation; their direction is not obvious from names alone. The separate root/tip pending workflow worked without temporary paint insertion. Focused labels remained visible. CLI feedback clearly removed derived length/angle controls after both pins. A render exceeded the initial launch window (session 35623); two exact-handle polls reached actual exit 0 before any next launch. Stale target and stale candidate refused with explicit reinspection/preview guidance. No live process remains.

Recovery: recovery-proof.json records byte-identical seed/undo JSON and PNG, byte-identical first/reaccepted JSON and PNG, and original_nodes_unchanged=true. 11-result.txt is actual stale-target refusal; 12-result.txt is actual stale-candidate refusal. Neither changed working paint. Raw CLI outputs are NN-result.txt (help in 01-place-help.txt). PowerShell's NativeCommandError wrapper in refusal logs is actual host output.

## Actual CLI commands

Working directory was `D:/vibe/learn_draw_studio`; executable `.venv/Scripts/python.exe`. Each numbered command below launched independently as `& .venv/Scripts/python.exe -m scripts.studio ... 2>&1 | Tee-Object evidence/studio-window-cat/usability/NN-result.txt`. Output directories and paths below have the common prefix `evidence/studio-window-cat/usability/` (abbreviated U/ only in this record). Seed was copied byte-for-byte to working.json before command 01.

```text
01 place --help
02 inspect U/working.json --object book-left --feature anchors --outdir U/02-left-map
03 inspect U/working.json --object book-left --feature anchors --anchor left@.1 --outdir U/03-left-mount
04 inspect U/working.json --object book-right --feature anchors --anchor right@.9 --outdir U/04-right-mount
05 place U/working.json --kind stroke --id book-cover --change length=.20 --change angle=90 --change thickness=.014 --change bend=-.10 --change depth=10 --change fill_color=#685044 --reason "A dark curved supporting cover will unite the open pages above the sill" --outdir U/05-pending
06 place U/working.json --revise U/05-pending/candidate.json --feature root --bind-end U/03-left-mount/selection.json --reason "Seat the cover root on the observed lower outer left page edge" --outdir U/06-root
07 place U/working.json --revise U/06-root/candidate.json --feature tip --bind-end U/04-right-mount/selection.json --reason "Seat the cover tip on the independently observed lower outer right page edge" --outdir U/07-both
08 place U/working.json --revise U/07-both/candidate.json --feature object --change bend=.035 --change thickness=.018 --change intent="a dark curved supporting cover tucked beneath both cream page planes" --reason "The cover must rise toward the gutter with the page bottoms instead of sagging into a detached bowl" --outdir U/08-refined
09 accept U/working.json U/08-refined/candidate.json
10 inspect U/working.json --object book-cover --feature root --outdir U/10-accepted
11 preview U/working.json --selection U/10-accepted/selection.json --bind-end U/03-left-mount/selection.json --reason "Verify an obsolete target inspection cannot silently bind the current cover" --outdir U/11-stale-target
12 accept U/working.json U/08-refined/candidate.json
13 undo U/working.json
14 inspect U/working.json --object book-left --feature anchors --anchor left@.1 --outdir U/14-undone
15 accept U/working.json U/08-refined/candidate.json
16 inspect U/working.json --object book-cover --feature object --outdir U/16-reaccepted
```

Commands 11 and 12 exited 1 as intended; the rest exited 0. accepted-first.json was copied after 09; undone.json after 13. SHA256 and parsed unchanged-node comparisons were performed using PowerShell against only these actual output artifacts.
