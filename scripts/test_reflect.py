#!/usr/bin/env python3
"""Tests for `polis reflect` (Layer 3 — evidence-mined self-amendments).

Builds a polis with planted pathologies and asserts reflect proposes the right
amendments, cites the right contracts, never ratifies, is idempotent, and does
not fire on a healthy history.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import reflect  # noqa: E402
from polis.routing import parse_frontmatter  # noqa: E402


def _make_polis(root: Path):
    root.mkdir(parents=True)
    (root / "CONSTITUTION.md").write_text("# c\n", encoding="utf-8")
    (root / "chronicle.md").write_text(
        "---\nfile_type: chronicle\n---\n\n- 2026-01-01 00:00 | founder | founded polis | - | -\n",
        encoding="utf-8")
    for cid in ("claude-dev", "codex-dev"):
        d = root / "citizens" / cid
        d.mkdir(parents=True)
        (d / "capability_card.yml").write_text(
            f"agent_id: {cid}\nvendor: x\ncapability_tags:\n  backend: {{self_rating: 4}}\n",
            encoding="utf-8")


def _settled(root: Path, cid, tag, owner, quality, *, recommended=None, stakes="medium"):
    d = root / "contracts" / "settled"
    d.mkdir(parents=True, exist_ok=True)
    routing = f"\n  recommended_by_router: {recommended}" if recommended else ""
    (d / f"{cid}.md").write_text(
        f"---\ncontract_id: {cid}\nstatus: settled\nowner: {owner}\n"
        f"required_tags: [{tag}]\nquality_score: {quality}\nstakes: {stakes}\n"
        f"review: {{required: false}}\nrouting:{routing or ' {}'}\n---\n# {cid}\n",
        encoding="utf-8")


class ReflectTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        _make_polis(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def _kinds(self, results):
        return {r["kind"] for r in results}

    def test_chronic_misroute_detected_with_citations(self):
        # Router favours claude-dev on `backend`, but codex-dev is far better.
        for i in range(3):
            _settled(self.root, f"bad-{i}", "backend", "claude-dev", 1, recommended="claude-dev")
        for i in range(3):
            _settled(self.root, f"good-{i}", "backend", "codex-dev", 5, recommended="claude-dev")
        results = reflect.reflect(self.root)
        misroute = [r for r in results if r["kind"] == "chronic-misroute"]
        self.assertEqual(len(misroute), 1, "expected exactly one misroute proposal")
        cited = set(misroute[0]["evidence_contracts"])
        self.assertIn("bad-0", cited)
        self.assertIn("good-0", cited)

    def test_recurring_low_quality_detected(self):
        for i in range(3):
            _settled(self.root, f"lq-{i}", "frontend", "claude-dev", 2)
        self.assertIn("recurring-low-quality", self._kinds(reflect.reflect(self.root)))

    def test_stakes_miscalibration_detected(self):
        for i in range(3):
            _settled(self.root, f"sk-{i}", "infra", "claude-dev", 1, stakes="medium")
        self.assertIn("stakes-miscalibration", self._kinds(reflect.reflect(self.root)))

    def test_healthy_history_proposes_nothing(self):
        for i in range(4):
            _settled(self.root, f"ok-{i}", "backend", "codex-dev", 5, recommended="codex-dev")
        self.assertEqual(reflect.reflect(self.root), [], "no false positives on healthy history")

    def test_below_min_evidence_proposes_nothing(self):
        # Only 2 low-quality contracts — under the default threshold of 3.
        for i in range(2):
            _settled(self.root, f"few-{i}", "backend", "claude-dev", 1)
        self.assertEqual(reflect.reflect(self.root), [])

    def test_apply_writes_proposed_not_ratified_and_is_idempotent(self):
        for i in range(3):
            _settled(self.root, f"lq-{i}", "frontend", "claude-dev", 2)
        first = reflect.reflect(self.root, apply=True)
        self.assertTrue(any(r["written"] for r in first))
        proposed = list((self.root / "amendments" / "proposed").glob("*.md"))
        self.assertTrue(proposed, "an amendment file was written")
        fm, _ = parse_frontmatter(proposed[0].read_text(encoding="utf-8"))
        self.assertEqual(fm["status"], "proposed")
        self.assertIsNone(fm["ratified_at"])
        self.assertEqual(fm["proposed_by"], "polis-reflector")
        # chronicle got a line
        self.assertIn("proposed amendment", (self.root / "chronicle.md").read_text(encoding="utf-8"))
        # second run writes nothing new
        second = reflect.reflect(self.root, apply=True)
        self.assertFalse(any(r["written"] for r in second), "idempotent on re-run")
        self.assertEqual(len(list((self.root / "amendments" / "proposed").glob("*.md"))), len(proposed))


if __name__ == "__main__":
    unittest.main()
