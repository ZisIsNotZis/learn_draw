#!/usr/bin/env python3
"""Emit only the exact neutral capability and formal-board payloads."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".scratch/28-local-art-identity"
EVIDENCE = SCRATCH / "evidence"
BOARD = ".scratch/28-local-art-identity/evidence/boards/comparison-unlabelled.png"
CONTROL = ".scratch/28-local-art-identity/evidence/review/precheck/control-01.png"
CAPABILITY_PROMPT = "Describe the visible forms and their positions."
REVIEW_PROMPT = "Describe what you see and what, if anything, is unclear."


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def capability_payload() -> dict:
    return {"schema": "local-art-identity-capability/v1", "images": [CONTROL],
            "prompt": CAPABILITY_PROMPT}


def formal_payload() -> dict:
    return {"schema": "local-art-identity-review/v1", "images": [BOARD],
            "prompt": REVIEW_PROMPT}


def report_text(payload: dict) -> str:
    if payload != formal_payload():
        raise ValueError("formal report accepts exactly the pinned one-board payload")
    return payload["images"][0] + "\n\n" + payload["prompt"] + "\n"


def payload_hash(payload: dict) -> str:
    return hashlib.sha256(canonical(payload)).hexdigest()


def _create_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)


def write_payloads() -> dict[str, str]:
    board = EVIDENCE / "boards/comparison-unlabelled.png"
    control = EVIDENCE / "review/precheck/control-01.png"
    if not board.is_file() or not control.is_file():
        raise RuntimeError("both local images must be built before pinning review payloads")
    capability, review = capability_payload(), formal_payload()
    cap_path = EVIDENCE / "review/precheck-payload.json"
    review_path = EVIDENCE / "review/payload.json"
    report_path = EVIDENCE / "review/report.txt"
    cap_hash_path = EVIDENCE / "review/precheck-payload.sha256"
    review_hash_path = EVIDENCE / "review/payload.sha256"
    _create_new(cap_path, (json.dumps(capability, indent=2, ensure_ascii=False) + "\n").encode())
    _create_new(review_path, (json.dumps(review, indent=2, ensure_ascii=False) + "\n").encode())
    _create_new(report_path, report_text(review).encode("utf-8"))
    cap_sha, review_sha = payload_hash(capability), payload_hash(review)
    _create_new(cap_hash_path, (cap_sha + "\n").encode())
    _create_new(review_hash_path, (review_sha + "\n").encode())
    return {"capability_payload_sha256": cap_sha, "formal_payload_sha256": review_sha,
            "formal_report_sha256": hashlib.sha256(report_text(review).encode()).hexdigest()}


if __name__ == "__main__":
    hashes = write_payloads()
    print(json.dumps(hashes, sort_keys=True))
