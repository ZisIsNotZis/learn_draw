#!/usr/bin/env python3
"""Freeze file hashes and provenance for this one A construction candidate."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
CANDIDATE=Path(__file__).resolve().parents[1]
TEACHER=ROOT/".scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2"
OLD=ROOT/".scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1"
DESIGN=Path("/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/44f91cea-8b0f-4499-a2b3-3face9964238/r1/garment-family-design-correction.md")
SEMANTIC_REVIEW=Path("/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/25d155f0-05d4-41ea-8e72-d0c1929292cd/r1/teacher-v2-independent-semantic-review.md")
CHAIN_REVIEW=Path("/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/3b2bad58-e1ed-44cd-bd21-f1aba0b6b4ce/r1/teacher-output-guard-review.md")

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def named(path): return {"path":str(path),"sha256":digest(path)}

files=[]
for path in sorted(CANDIDATE.rglob("*")):
    if not path.is_file() or path.name in {"manifest.json","manifest.sha256"}: continue
    if "__pycache__" in path.parts: continue
    files.append({"path":path.relative_to(CANDIDATE).as_posix(),"sha256":digest(path),"bytes":path.stat().st_size})
inputs={
    "reference_source":named(ROOT/"image.jpg"),
    "registered_crop":named(TEACHER/"pristine-fullcrop.png"),
    "design_authority":named(DESIGN),
    "teacher_boundary":named(TEACHER/"fit-correction.md"),
    "teacher_topology":named(TEACHER/"topology-map.md"),
    "teacher_provenance":named(TEACHER/"provenance.json"),
    "teacher_landmark_table":named(TEACHER/"landmarks.csv"),
    "teacher_fitting_interface":named(TEACHER/"family-fitting-interface.md"),
    "teacher_semantic_review":named(SEMANTIC_REVIEW),
    "teacher_output_chain_review":named(CHAIN_REVIEW),
}
preserved={
    "issue45_artwork_png":named(OLD/"artwork-a.png"),
    "issue45_builder":named(OLD/"source/build_a.py"),
    "issue45_parameters":named(OLD/"source/semantic-parameters.json"),
}
manifest={
    "schema":"a-cloth-construction-v2-candidate-manifest",
    "status":"candidate emitted; not A-art PASS and not R1 PASS",
    "candidate":".scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2",
    "sourceBoundary":"A-only crop-local clothing/composition plus Main-approved curlband/right-shoulder-sheet and independent anonymous crop-exiting blue band; B v2 unchanged, sealed heldout unread",
    "authority":{"ticket":".scratch/35-r1-articulated-study/issues/46-a-cloth-construction-v2.md","designPath":str(DESIGN),"designSha256":digest(DESIGN)},
    "inputs":inputs,
    "teacherScope":{"semanticInputReview":"PASS only for corrected-v2 finite accepted/unknown source boundary; not an art verdict","outputChainReview":"PASS only for corrected-v2 output guard; not a fit/art verdict","whitelist":"corrected-v2 fit-correction.md only","forbidden":["N1/BD1/BD4/TD1 identities","LTI2 as pink interior","all leftward-tail-centerline stations as verified axis or width","DTO2 terminal","exact full boundaries/seams/armhole/hem/cuff circumference","blue identity","pink-to-blue attachment"]},
    "visibleContext":{"separateProvenance":"artist-visible_context; no change to teacher garment whitelist","authorizedRoles":["crop-local neck curlband","crop-local right-shoulder hair sheet"],"claim":"local appearance context only; hidden roots, ends, depth and full hairstyle unknown"},
    "artistHypotheses":["all family seed coordinates and scalar width/bend/fullness values","shared opening/collar fold geometry","bodice axis and continuation/waist band","bodice-sleeve attachment and support depths","gather/loop return folds and tail routes","anonymous blue band geometry/support/relative overlap","local hair geometry/support/relative overlap"],
    "implementation":{"parts":16,"generatedContourVertices":885,"projectedFaces":853,"familyRules":"source/family-rules.py","parameterSource":"source/semantic-parameters.json","builder":"source/build_a.py","maximumActualAuthoredCoordinatesPerPart":4,"actualCoordinateBudget":"tests/test_a_cloth_identity.py inspects FamilyGeometry.authored_inputs, not Component.anchors"},
    "outputs":{"svg":"artwork-a.svg","png":"artwork-a.png","sizePx":[400,480],"registeredCropComparison":"check-a/report.txt","reviewImageList":"review-image-list.txt","referenceAbsentRepeat":["reproduction/rebuilt.svg","reproduction/rebuilt.png"],"byteIdenticalRepeat":True},
    "commandsRun":[
        {"command":"timeout 115s python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/tests/test_a_cloth_identity.py","result":"passed","summary":"7 tests passed; identity/family, coordinate budget, attachment, depth/line, ref-absence and determinism checks"},
        {"command":"timeout 115s python3 -B .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/source/build_a.py --out .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg","result":"passed","summary":"16 parts, 885 contour vertices, 853 projected faces; 4-coordinate maximum"},
        {"command":"timeout 115s scripts/draw render .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg -o .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.png","result":"passed","summary":"400×480 actual PNG"},
        {"command":"timeout 115s scripts/draw check .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg --ref .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/pristine-fullcrop.png --outdir .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/check-a","result":"passed","summary":"registered 400×480 crop comparison and exact image list; metrics alarm-only, not used for parameter changes"},
        {"command":"timeout 115s python3 -B .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/source/build_a.py --out .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/reproduction/rebuilt.svg && timeout 115s scripts/draw render .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/reproduction/rebuilt.svg -o .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/reproduction/rebuilt.png && cmp .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/reproduction/rebuilt.svg && cmp .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.png .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/reproduction/rebuilt.png","result":"passed","summary":"SVG and PNG byte-identical"}
    ],
    "acceptance":{"sourceAndConstructionSelfChecks":"passed as writer checks","artistImageReview":"open; writer did not open/judge output","independentConstructionPhysicalIntersectionAndDepthReview":"open","BIntegration":"open; not touched","heldout":"open; sealed and unread","R1":"not accepted","humanUserGate":"open"},
    "preservedPriorCandidateHashes":preserved,
    "files":files,
    "metricsDisposition":"check bundle contains comparative alarm signals only; no metric-driven parameter edits"
}
(CANDIDATE/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
(CANDIDATE/"manifest.sha256").write_text(f"{digest(CANDIDATE/'manifest.json')}  manifest.json\n",encoding="utf-8")
print(json.dumps({"manifest":str(CANDIDATE/"manifest.json"),"listedFiles":len(files),"manifestSha256":digest(CANDIDATE/"manifest.json")},sort_keys=True))
