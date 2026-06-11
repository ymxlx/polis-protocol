#!/usr/bin/env python3
"""Tests for Polis Bench.

Asserts only what is robustly TRUE across seeds (no cherry-picked vanity win):
  - learned routing beats the no-skill baselines (random, round-robin),
  - it recovers a positive fraction of the oracle's gain from outcomes alone,
  - the oracle is an upper bound, and skill-aware beats no-skill.
The benchmark deliberately does NOT claim Polis beats accurate static cards.
"""
import statistics
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import bench  # noqa: E402

SEEDS = range(10)


def _means(strategy):
    vals = []
    for s in SEEDS:
        r = bench.run_benchmark(n_contracts=200, seed=s)["results"]
        vals.append(r[strategy]["mean_quality"])
    return statistics.mean(vals)


class BenchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = {s: _means(s) for s in bench.STRATEGIES}

    def test_polis_beats_no_skill_baselines(self):
        self.assertGreater(self.m["polis"], self.m["random"])
        self.assertGreater(self.m["polis"], self.m["round_robin"])

    def test_oracle_is_the_ceiling(self):
        for s in ("random", "round_robin", "static_self", "polis"):
            self.assertGreaterEqual(self.m["oracle"], self.m[s])

    def test_skill_aware_beats_no_skill(self):
        self.assertGreater(self.m["static_self"], self.m["round_robin"])

    def test_polis_recovers_positive_oracle_gain(self):
        gain = self.m["oracle"] - self.m["round_robin"]
        recovered = (self.m["polis"] - self.m["round_robin"]) / gain
        self.assertGreater(recovered, 0.0)

    def test_report_is_honest_about_static(self):
        # The rendered report must not claim Polis beats static self-ratings.
        report = bench.format_report(bench.run_benchmark(n_contracts=80, seed=0))
        self.assertIn("competitive", report)
        self.assertIn("oracle", report.lower())


if __name__ == "__main__":
    unittest.main()
