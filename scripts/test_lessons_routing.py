#!/usr/bin/env python3
"""Regression test for accepted-lesson effects on routing.

Proves the v2 verification criterion: an accepted lesson with a structured
routing_effect changes a later routing recommendation and is named in the
explanation — and that the effect is bounded and that un-accepted lessons are
ignored.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis.routing import (  # noqa: E402
    LESSON_CAP,
    WEIGHTS_DEFAULT,
    load_lessons,
    lessons_score,
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


if __name__ == "__main__":
    unittest.main()
