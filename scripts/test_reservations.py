#!/usr/bin/env python3
"""Tests for advisory file reservations (collision prevention)."""
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import reservations as R  # noqa: E402


class ReservationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.root.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_basic_reserve_and_list(self):
        res = R.reserve(self.root, "agent-a", ["src/auth.py"])
        self.assertTrue(res["ok"])
        active = R.active_reservations(self.root)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["citizen"], "agent-a")

    def test_conflict_rejected_for_other_citizen(self):
        self.assertTrue(R.reserve(self.root, "agent-a", ["src/auth.py"])["ok"])
        res = R.reserve(self.root, "agent-b", ["src/auth.py"])
        self.assertFalse(res["ok"])
        self.assertEqual(res["conflicts"][0]["holder"], "agent-a")

    def test_same_citizen_can_re_reserve(self):
        self.assertTrue(R.reserve(self.root, "agent-a", ["src/auth.py"])["ok"])
        self.assertTrue(R.reserve(self.root, "agent-a", ["src/auth.py"])["ok"])

    def test_directory_reservation_blocks_child_file(self):
        self.assertTrue(R.reserve(self.root, "agent-a", ["src/auth"])["ok"])
        res = R.reserve(self.root, "agent-b", ["src/auth/login.py"])
        self.assertFalse(res["ok"])
        # ...and the reverse: a file held blocks reserving its parent dir
        self.assertTrue(R.reserve(self.root, "agent-c", ["lib/util.py"])["ok"])
        self.assertFalse(R.reserve(self.root, "agent-d", ["lib"])["ok"])

    def test_non_overlapping_paths_are_independent(self):
        self.assertTrue(R.reserve(self.root, "agent-a", ["src/auth.py"])["ok"])
        self.assertTrue(R.reserve(self.root, "agent-b", ["src/ui.py"])["ok"])

    def test_release_frees_the_path(self):
        R.reserve(self.root, "agent-a", ["src/auth.py"])
        removed = R.release(self.root, "agent-a", ["src/auth.py"])
        self.assertEqual(removed, 1)
        self.assertTrue(R.reserve(self.root, "agent-b", ["src/auth.py"])["ok"])

    def test_release_all_for_citizen(self):
        R.reserve(self.root, "agent-a", ["a.py", "b.py"])
        R.reserve(self.root, "agent-b", ["c.py"])
        R.release(self.root, "agent-a")
        active = R.active_reservations(self.root)
        self.assertEqual([r["citizen"] for r in active], ["agent-b"])

    def test_expired_reservation_does_not_conflict(self):
        # reserve with a TTL, then evaluate "now" well past expiry
        R.reserve(self.root, "agent-a", ["src/auth.py"], ttl_minutes=10)
        future = R._now() + timedelta(minutes=30)
        self.assertEqual(R.active_reservations(self.root, now=future), [])
        # a fresh reservation by another agent now succeeds
        res = R.reserve(self.root, "agent-b", ["src/auth.py"], now=future)
        self.assertTrue(res["ok"])

    def test_path_normalization(self):
        R.reserve(self.root, "agent-a", ["./src/auth.py"])
        res = R.reserve(self.root, "agent-b", ["src/auth.py"])
        self.assertFalse(res["ok"])


if __name__ == "__main__":
    unittest.main()
