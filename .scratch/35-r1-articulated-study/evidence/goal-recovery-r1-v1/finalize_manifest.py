"""Hash/freeze actual candidate and review bundles after the single structural preflight."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from r1_scene import _b_case


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_images(path: Path) -> list[str]:
    if not path.exists(): return []
    lines=path.read_text(encoding="utf-8").splitlines()
    selected=[]
    for line in lines:
        stripped=line.strip()
        if stripped.startswith(".") and (".png" in stripped or ".jpg" in stripped):
            selected.append(stripped.split()[0])
    return selected


def main():
    generated=(
      "rendered/A-observed-garment.svg","rendered/A-observed-garment.png",
      "rendered/B-baseline-support.svg","rendered/B-baseline-support.png",
      "rendered/B-variant-support.svg","rendered/B-variant-support.png",
      "rendered/B-near-miss-control.svg","rendered/B-near-miss-control.png",
      "rendered/B-original-support.svg","rendered/B-original-support.png",
    )
    for rel in generated:
        if not (ROOT/rel).is_file(): raise FileNotFoundError(ROOT/rel)
    check_reports={name:ROOT/"checks"/name/"report.txt" for name in ("A","B")}
    for path in check_reports.values():
        if not path.is_file(): raise FileNotFoundError(path)
    _,_,baseline=_b_case("baseline");_,_,variant=_b_case("variant");_,_,control=_b_case("control")
    evidence={"baseline":baseline,"variant":variant,"near_miss_control":control}
    source_files=("observe_teacher.py","shape-grammar.md","teacher-observations.json","spatial_adapter.py",
                  "r1_scene.py","run_r1.py","compose_b_sheet.py","finalize_manifest.py","test_goal_recovery_r1.py")
    source_hashes={name:sha(ROOT/name) for name in source_files}
    source_digest=hashlib.sha256("\n".join(f"{name}:{source_hashes[name]}" for name in sorted(source_hashes)).encode()).hexdigest()
    output_hashes={rel:sha(ROOT/rel) for rel in generated}
    teacher_files=("teacher-crop-registered.png","teacher-crop-focus.png","teacher-grid.png",
                   "teacher-region-windows.png","teacher-observations.json")
    teacher_hashes={name:sha(ROOT/name) for name in teacher_files}
    review_files={str(path.relative_to(ROOT)):sha(path) for path in sorted((ROOT/"checks").rglob("*"))
                  if path.is_file()}
    result={
      "revision":"goal-recovery-r1-v1",
      "status":"CANDIDATE_FROZEN_FOR_INDEPENDENT_REVIEW; no visual/art/R1 PASS claimed",
      "ticket":".scratch/35-r1-articulated-study/issues/24-goal-level-artistic-recovery.md",
      "source_set_sha256":source_digest,
      "source_sha256":source_hashes,
      "rendered_sha256":output_hashes,
      "teacher_evidence_sha256":teacher_hashes,
      "review_bundle_sha256":review_files,
      "teacher_observation":{
        "source_path":"image.jpg","source_sha256":"322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb",
        "crop_path":"teacher-crop-registered.png","crop_sha256":sha(ROOT/"teacher-crop-registered.png"),
        "crop_source_xyxy":[500,320,900,800],"crop_dimensions":[400,480],"resize":"none",
        "observed_only_windows_path":"teacher-region-windows.png","window_manifest_path":"teacher-observations.json",
        "engine_input":"none; scene/reproduction accepts semantic case only"
      },
      "artwork":{
        "A":{"svg":"rendered/A-observed-garment.svg","png":"rendered/A-observed-garment.png",
             "claim":"teacher-fitted shoulder/upper-torso bodice, visible right puff sleeve/cuff, layered collar/trim, bow lobes/tails/folds; no hair/hand/pose claim",
             "review_report":"checks/A/report.txt","review_image_list":report_images(check_reports["A"])},
        "B":{"svg_contact_sheet":"rendered/B-original-support.svg","png_contact_sheet":"rendered/B-original-support.png",
             "panels":[{"case":case,"svg":f"rendered/B-{case}-support.svg" if case!="control" else "rendered/B-near-miss-control.svg",
                        "png":f"rendered/B-{case}-support.png" if case!="control" else "rendered/B-near-miss-control.png"}
                       for case in ("baseline","variant","control")],
             "claim":"original bent-arm articulated hand supports shallow fruit dish; raised/wider support variant; unchanged-hand near-miss control",
             "review_report":"checks/B/report.txt","review_image_list":report_images(check_reports["B"])}
      },
      "case_geometry_evidence":evidence,
      "architecture":{
        "support_pipeline":"revision-local composition over existing smooth sampler/guard, SupportFrame/Camera/component faces, vector_visibility, visible_segment_spans, compound path mapping",
        "visibility":"depth-derived; no manually authored visibility intervals",
        "scene_collision_scope":"actual affine support footprints/declared contacts for each B case; no general volume-physics claim",
        "drawing_metrics":"draw check outputs are breakage alarms only; not tuned"
      },
      "gates_open":["independent image-only art/readability review","independent structural/depth review as assigned by Main",
                     "heldout compatibility/release and later distinct drawing","separate deterministic reproduction acceptance",
                     "user feedback","all R1 art/physical/depth/attachment gates"],
      "no_staging_or_commit":True
    }
    path=ROOT/"manifest.json"
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"manifest: {path}; source-set SHA-256 {source_digest}; {len(output_hashes)} rendered files hashed")

if __name__=="__main__": main()
