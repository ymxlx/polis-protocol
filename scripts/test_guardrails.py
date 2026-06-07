#!/usr/bin/env python3
"""Tests for guardrails (failure->check) + their compounding into contracts/packets."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import bench, context, guardrails  # noqa: E402
from polis.contracts import open_contract  # noqa: E402
from polis.routing import parse_frontmatter  # noqa: E402


class GuardrailTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.root.mkdir(parents=True)
        (self.root / "CONSTITUTION.md").write_text("# c\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_add_and_match_by_tag(self):
        guardrails.add_guardrail(self.root, "Run axe-core; no a11y violations.", ["css"], "contract-1")
        self.assertEqual(len(guardrails.matching_guardrails(self.root, ["css"])), 1)
        self.assertEqual(guardrails.matching_guardrails(self.root, ["python"]), [])

    def test_new_contract_inherits_matching_guardrail(self):
        guardrails.add_guardrail(self.root, "Reset the DB fixture before tests.", ["python"], "c0")
        res = open_contract(self.root, "Add endpoint", ["python"], "alice")
        fm, _ = parse_frontmatter((Path(res["path"])).read_text(encoding="utf-8"))
        criteria = fm["acceptance_criteria"]
        self.assertTrue(any("Reset the DB fixture" in c for c in criteria))
        self.assertTrue(any(c.startswith("[guardrail]") for c in criteria))

    def test_unrelated_contract_does_not_inherit(self):
        guardrails.add_guardrail(self.root, "Only for CSS.", ["css"], "c0")
        res = open_contract(self.root, "Backend task", ["python"], "alice")
        fm, _ = parse_frontmatter((Path(res["path"])).read_text(encoding="utf-8"))
        self.assertFalse(any("[guardrail]" in c for c in fm["acceptance_criteria"]))

    def test_packet_shows_guardrails(self):
        cid = open_contract(self.root, "Style task", ["css"], "alice")["contract_id"]
        guardrails.add_guardrail(self.root, "Mobile-first; test at 320px.", ["css"], cid)
        out = context.format_packet(context.build_packet(self.root, cid))
        self.assertIn("Must-pass guardrails", out)
        self.assertIn("Mobile-first", out)


class LearningBenchTest(unittest.TestCase):
    def test_polis_beats_memoryless_on_repeat_errors(self):
        b = bench.run_learning_benchmark(n_contracts=180, seed=0)
        # Accumulating knowledge yields a strictly lower repeat-error rate.
        self.assertLess(b["polis_final"], b["memoryless_final"])
        # And the curve actually bends down over time (late < early).
        curve = b["polis_curve"]
        self.assertLess(curve[-1], curve[len(curve) // 5])

    def test_holds_across_seeds(self):
        for s in range(5):
            b = bench.run_learning_benchmark(n_contracts=150, seed=s)
            self.assertLess(b["polis_final"], b["memoryless_final"])


if __name__ == "__main__":
    unittest.main()
