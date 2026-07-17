#!/usr/bin/env python3
"""Regression test for routing-policy behavior.

Covers two policies:

* accepted-lesson effects on the epsilon-greedy scorer — an accepted lesson with
  a structured routing_effect changes a later recommendation and is named in the
  explanation, the effect is bounded, and un-accepted lessons are ignored; and
* the deterministic UCB1 variant — cold-start (unplayed arms first) and
  learned-history (mean + confidence bonus) selection, with no randomness.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis.routing import (  # noqa: E402
    LESSON_CAP,
    WEIGHTS_DEFAULT,
    citizen_sample_count,
    load_lessons,
    lessons_score,
    pick_ucb,
    score_citizen,
)

CONTRACT = {"required_tags": ["spanish-translation"], "cost_ceiling": "medium"}
CARD = {"capability_tags": {}, "cost_envelope": {"relative": "medium"}}
STATS = {"tags": {}}


class LessonRoutingTest(unittest.TestCase):
    def test_lesson_flips_recommendation_and_is_named(self):
        # With no lessons, the two identical citizens tie.
        a0 = score_citizen("a", CARD, {}, CONTRACT, STATS, WEIGHTS_DEFAULT, [])
        b0 = score_citizen("b", CARD, {}, CONTRACT, STATS, WEIGHTS_DEFAULT, [])
        self.assertAlmostEqual(a0["total"], b0["total"])
        self.assertEqual(a0["lessons"], 0.0)

        # An accepted lesson favouring "b" on this tag should flip the lead...
        lessons = [{
            "lesson_id": "L1",
            "routing_effect": [{"citizen": "b", "tags": ["spanish-translation"], "delta": 0.1}],
        }]
        a = score_citizen("a", CARD, {}, CONTRACT, STATS, WEIGHTS_DEFAULT, lessons)
        b = score_citizen("b", CARD, {}, CONTRACT, STATS, WEIGHTS_DEFAULT, lessons)
        self.assertGreater(b["total"], a["total"])
        # ...and the explanation must name the exact lesson that did it.
        self.assertEqual(b["applied_lessons"], ["L1"])
        self.assertAlmostEqual(b["lessons"], 0.1)
        self.assertEqual(a["applied_lessons"], [])

    def test_effect_is_bounded(self):
        lessons = [{"lesson_id": "big", "routing_effect": [{"citizen": "b", "tags": ["t"], "delta": 99.0}]}]
        bonus, applied = lessons_score("b", ["t"], lessons)
        self.assertEqual(bonus, LESSON_CAP)
        self.assertEqual(applied, ["big"])

    def test_tag_mismatch_does_not_apply(self):
        lessons = [{"lesson_id": "x", "routing_effect": [{"citizen": "b", "tags": ["other-tag"], "delta": 0.1}]}]
        bonus, applied = lessons_score("b", ["spanish-translation"], lessons)
        self.assertEqual((bonus, applied), (0.0, []))

    def test_proposed_lesson_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            (root / "lessons" / "x").mkdir(parents=True)
            (root / "lessons" / "x" / "l.md").write_text(
                "---\n"
                "lesson_id: P1\n"
                "status: proposed\n"
                "routing_effect:\n"
                "  - citizen: b\n"
                "    tags: [t]\n"
                "    delta: 0.1\n"
                "---\nbody\n",
                encoding="utf-8",
            )
            self.assertEqual(load_lessons(root), [])

    def test_prose_only_lesson_has_no_effect(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            (root / "lessons" / "x").mkdir(parents=True)
            (root / "lessons" / "x" / "l.md").write_text(
                "---\nlesson_id: PR1\nquality_impact: 4\n---\nprose only, no routing_effect\n",
                encoding="utf-8",
            )
            self.assertEqual(load_lessons(root), [])


class UCBRoutingTest(unittest.TestCase):
    """The optional UCB policy is deterministic and follows standard UCB1."""

    def test_sample_count_sums_across_required_tags(self):
        stats = {"tags": {
            "t1": {"citizens": {"a": {"contracts_completed": 3}}},
            "t2": {"citizens": {"a": {"contracts_completed": 4}}},
        }}
        self.assertEqual(citizen_sample_count("a", ["t1", "t2"], stats), 7)
        # A citizen with no history on the tags counts as unplayed.
        self.assertEqual(citizen_sample_count("z", ["t1", "t2"], stats), 0)

    def test_cold_start_picks_unplayed_arms_first_deterministically(self):
        # Every arm is unplayed (n == 0) -> all have infinite priority, so the
        # tie breaks on citizen id ascending. The higher mean does NOT win.
        scores = [{"citizen": "b", "total": 0.9}, {"citizen": "a", "total": 0.1}]
        counts = {"a": 0, "b": 0}
        chosen, is_exploration, score = pick_ucb(scores, counts)
        self.assertEqual(chosen, "a")
        self.assertTrue(is_exploration)  # differs from the exploit leader "b"
        self.assertEqual(score, 0.1)

    def test_cold_start_prefers_unplayed_over_high_mean_leader(self):
        # An untried citizen (n == 0) outranks a well-sampled high-mean citizen.
        scores = [{"citizen": "a", "total": 0.95}, {"citizen": "z", "total": 0.05}]
        counts = {"a": 10, "z": 0}
        chosen, is_exploration, _ = pick_ucb(scores, counts)
        self.assertEqual(chosen, "z")
        self.assertTrue(is_exploration)

    def test_learned_history_exploits_clear_leader(self):
        # Equal, ample samples -> identical confidence bonus, so the higher mean
        # wins and it matches the exploit pick.
        scores = [{"citizen": "a", "total": 0.9}, {"citizen": "b", "total": 0.5}]
        counts = {"a": 50, "b": 50}
        chosen, is_exploration, _ = pick_ucb(scores, counts)
        self.assertEqual(chosen, "a")
        self.assertFalse(is_exploration)

    def test_learned_history_bonus_flips_underexplored_arm(self):
        # b has a slightly lower mean but far fewer samples, so its wider
        # confidence interval lifts it above a over the exploit leader.
        scores = [{"citizen": "a", "total": 0.60}, {"citizen": "b", "total": 0.55}]
        counts = {"a": 100, "b": 1}
        chosen, is_exploration, _ = pick_ucb(scores, counts)
        self.assertEqual(chosen, "b")
        self.assertTrue(is_exploration)

    def test_choice_sits_on_the_exploration_constant_boundary(self):
        # A decision-boundary scenario that pins BOTH the exploration constant and
        # the sqrt in the UCB1 term by asserting which arm production actually
        # picks. a has the higher mean with plenty of samples; b trails on mean
        # but is under-sampled, so its confidence bonus only overtakes a once the
        # exploration term is large enough.
        #
        # Hand-computed with total_n = 125 (ln 125 = 4.8283):
        #   ucb(a) = 0.60 + c * sqrt(4.8283 / 100)
        #   ucb(b) = 0.35 + c * sqrt(4.8283 /  25)
        # b overtakes a only for c above ~1.14. So:
        #   * production c = sqrt(2) ≈ 1.414  -> b wins   (a=0.9108, b=0.9715)
        #   * a smaller constant  c = 1.0     -> a wins   (a=0.8197, b=0.7895)
        #   * dropping the sqrt   (ln/n)      -> a wins   (a=0.6683, b=0.6231)
        # so this asserted choice fails if the constant is shrunk or the sqrt is
        # removed, while never recomputing the expectation from UCB_EXPLORATION_C.
        scores = [{"citizen": "a", "total": 0.60}, {"citizen": "b", "total": 0.35}]
        counts = {"a": 100, "b": 25}
        chosen, is_exploration, score = pick_ucb(scores, counts)
        self.assertEqual(chosen, "b")
        self.assertTrue(is_exploration)  # a is the higher-mean (exploit) pick
        self.assertEqual(score, 0.35)

    def test_ties_break_by_citizen_id(self):
        scores = [{"citizen": "b", "total": 0.5}, {"citizen": "a", "total": 0.5}]
        counts = {"a": 5, "b": 5}
        chosen, is_exploration, _ = pick_ucb(scores, counts)
        self.assertEqual(chosen, "a")
        self.assertFalse(is_exploration)

    def test_deterministic_across_calls(self):
        scores = [{"citizen": "a", "total": 0.60}, {"citizen": "b", "total": 0.55}]
        counts = {"a": 100, "b": 1}
        first = pick_ucb(scores, counts)
        for _ in range(20):
            self.assertEqual(pick_ucb(scores, counts), first)

    def test_empty_scores_is_safe(self):
        self.assertEqual(pick_ucb([], {}), (None, False, 0.0))


if __name__ == "__main__":
    unittest.main()
