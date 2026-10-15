from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import build_review_payload as payloads
import vision_control

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / ".scratch/28-local-art-identity/evidence"


class ReviewPayloadTests(unittest.TestCase):
    def test_exact_neutral_schema_and_one_image_paths(self):
        capability = payloads.capability_payload()
        formal = payloads.formal_payload()
        self.assertEqual(capability, {
            "schema": "local-art-identity-capability/v1",
            "images": [".scratch/28-local-art-identity/evidence/review/precheck/control-01.png"],
            "prompt": "Describe the visible forms and their positions.",
        })
        self.assertEqual(formal, {
            "schema": "local-art-identity-review/v1",
            "images": [".scratch/28-local-art-identity/evidence/boards/comparison-unlabelled.png"],
            "prompt": "Describe what you see and what, if anything, is unclear.",
        })
        self.assertEqual(set(capability), {"schema", "images", "prompt"})
        self.assertEqual(set(formal), {"schema", "images", "prompt"})
        self.assertNotIn("circle", capability["prompt"])
        self.assertNotIn("stripe", formal["prompt"])

    def test_formal_report_is_exact_and_rejects_extra_routes_or_coaching(self):
        payload = payloads.formal_payload()
        self.assertEqual(payloads.report_text(payload),
                         ".scratch/28-local-art-identity/evidence/boards/comparison-unlabelled.png\n\n"
                         "Describe what you see and what, if anything, is unclear.\n")
        for injected in (
            {**payload, "images": payload["images"] + ["raw-panel.png"]},
            {**payload, "case_id": "primary-dplus"},
            {**payload, "prompt": payload["prompt"] + " Compare the policies."},
        ):
            with self.subTest(injected=injected), self.assertRaises(ValueError):
                payloads.report_text(injected)

    def test_payload_hash_is_canonical_and_key_stays_evaluator_private(self):
        capability = payloads.capability_payload()
        self.assertEqual(payloads.payload_hash(capability), hashlib.sha256(
            payloads.canonical(capability)).hexdigest())
        key = vision_control.control_answer_key()
        self.assertEqual(set(key), {"schema", "facts"})
        self.assertEqual(len(key["facts"]), 4)
        self.assertNotIn("facts", capability)
        self.assertNotIn("answer", capability)

    def test_built_payloads_and_report_match_the_exact_pinned_objects(self):
        cap_path = EVIDENCE / "review/precheck-payload.json"
        review_path = EVIDENCE / "review/payload.json"
        report_path = EVIDENCE / "review/report.txt"
        self.assertEqual(json.loads(cap_path.read_text()), payloads.capability_payload())
        self.assertEqual(json.loads(review_path.read_text()), payloads.formal_payload())
        report = report_path.read_text()
        self.assertEqual(report, payloads.report_text(payloads.formal_payload()))
        self.assertEqual(report.splitlines(), [payloads.formal_payload()["images"][0], "",
                                               payloads.formal_payload()["prompt"]])
        self.assertEqual((EVIDENCE / "review/payload.sha256").read_text().strip(),
                         payloads.payload_hash(payloads.formal_payload()))
        self.assertEqual((EVIDENCE / "review/precheck-payload.sha256").read_text().strip(),
                         payloads.payload_hash(payloads.capability_payload()))

    def test_vision_control_matches_fixed_vector_source_without_text(self):
        source = vision_control.control_svg()
        vision_control.validate_control_svg(source)
        for clue in ("<text", "answer", "circle is", "upper-left"):
            self.assertNotIn(clue, source.lower())
        self.assertEqual(len(vision_control.control_answer_key()["facts"]), 4)

    def test_unlabelled_board_matches_private_balanced_mapping_without_routing_text(self):
        mapping_path = EVIDENCE / "private/mapping.json"
        board_path = EVIDENCE / "boards/comparison-unlabelled.png"
        audit_path = EVIDENCE / "provenance/board-audit.json"
        self.assertTrue(mapping_path.is_file() and board_path.is_file() and audit_path.is_file())
        audit = json.loads(audit_path.read_text())
        self.assertEqual((audit["width"], audit["height"]), (900, 1380))
        self.assertTrue(audit["panel_pixels_match_frozen_mapping"])
        self.assertTrue(audit["balanced_policy_columns"])
        self.assertFalse(audit["labels_or_text"])
        self.assertEqual(audit["nonblank_cells"], 8)
        formal = payloads.formal_payload()
        self.assertEqual(formal["images"], [
            ".scratch/28-local-art-identity/evidence/boards/comparison-unlabelled.png"])


if __name__ == "__main__":
    unittest.main()
