#!/usr/bin/env python3
"""Tests for capability-card content-integrity hashes (tamper-evidence)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from polis import integrity  # noqa: E402

CARD = {
    "agent_id": "a",
    "capability_tags": {"py": {"self_rating": 4}},
    "cost_envelope": {"relative": "medium"},
}


class IntegrityTest(unittest.TestCase):
    def test_hash_deterministic_and_excludes_own_fields(self):
        h1 = integrity.content_hash(CARD)
        noisy = dict(CARD, content_hash="sha256:whatever", signature="x:y:z")
        self.assertEqual(h1, integrity.content_hash(noisy))
        self.assertEqual(len(h1), 64)

    def test_content_change_changes_hash(self):
        other = dict(CARD, capability_tags={"py": {"self_rating": 5}})
        self.assertNotEqual(integrity.content_hash(CARD), integrity.content_hash(other))

    def test_verify_states(self):
        self.assertEqual(integrity.verify_card(CARD)["state"], "unstamped")
        legacy = dict(CARD, signature="a:2026:sha256:deadbeef")
        self.assertEqual(integrity.verify_card(legacy)["state"], "legacy")
        good = dict(CARD, content_hash="sha256:" + integrity.content_hash(CARD))
        self.assertEqual(integrity.verify_card(good)["state"], "ok")
        bad = dict(CARD, content_hash="sha256:" + "0" * 64)
        self.assertEqual(integrity.verify_card(bad)["state"], "mismatch")

    def test_stamp_roundtrip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "capability_card.yml"
            p.write_text("agent_id: a\ncapability_tags:\n  py: {self_rating: 4}\n", encoding="utf-8")
            integrity.stamp_card_file(p)
            card = yaml.safe_load(p.read_text(encoding="utf-8"))
            self.assertEqual(integrity.verify_card(card)["state"], "ok")
            tampered = p.read_text(encoding="utf-8").replace("self_rating: 4", "self_rating: 5")
            p.write_text(tampered, encoding="utf-8")
            card2 = yaml.safe_load(p.read_text(encoding="utf-8"))
            self.assertEqual(integrity.verify_card(card2)["state"], "mismatch")

    def test_stamp_replaces_legacy_signature(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "capability_card.yml"
            p.write_text('agent_id: a\nsignature: "a:2026:sha256:dead"\n', encoding="utf-8")
            integrity.stamp_card_file(p)
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("signature:", text)
            self.assertIn("content_hash:", text)


if __name__ == "__main__":
    unittest.main()
