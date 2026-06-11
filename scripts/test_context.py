#!/usr/bin/env python3
"""Tests for context packets — outcome-derived lessons auto-injected by tag match."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import context  # noqa: E402
from polis.contracts import open_contract  # noqa: E402


def _lesson(root, lid, tags, status="accepted", impact=3, title="A lesson"):
    d = root / "lessons" / lid
    d.mkdir(parents=True, exist_ok=True)
    tag_yaml = "[" + ", ".join(tags) + "]"
    (d / f"{lid}.md").write_text(
        f"---\nlesson_id: {lid}\nstatus: {status}\ncapability_tags: {tag_yaml}\n"
        f"quality_impact: {impact}\n---\n\n# {title}\n\nBody text explaining the lesson.\n",
        encoding="utf-8",
    )


class ContextPacketTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "_polis"
        self.root.mkdir(parents=True)
        (self.root / "CONSTITUTION.md").write_text("# c\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_only_matching_accepted_lessons_injected(self):
        cid = open_contract(self.root, "Build UI", ["react", "css"], "alice")["contract_id"]
        _lesson(self.root, "match", ["css"], title="CSS gotcha")
        _lesson(self.root, "nomatch", ["rust"], title="Rust thing")
        _lesson(self.root, "proposed", ["css"], status="proposed", title="Unratified")

        packet = context.build_packet(self.root, cid)
        ids = [l["lesson_id"] for l in packet["lessons"]]
        self.assertIn("match", ids)
        self.assertNotIn("nomatch", ids)       # tag mismatch
        self.assertNotIn("proposed", ids)      # not accepted

    def test_lessons_sorted_by_impact(self):
        cid = open_contract(self.root, "Task", ["py"], "alice")["contract_id"]
        _lesson(self.root, "low", ["py"], impact=2, title="Low")
        _lesson(self.root, "high", ["py"], impact=5, title="High")
        packet = context.build_packet(self.root, cid)
        self.assertEqual([l["lesson_id"] for l in packet["lessons"]], ["high", "low"])

    def test_format_packet_mentions_lessons_and_compounds(self):
        cid = open_contract(self.root, "Task", ["py"], "alice")["contract_id"]
        # cold: no lessons yet
        cold = context.format_packet(context.build_packet(self.root, cid))
        self.assertIn("No prior lessons", cold)
        # warm: a lesson exists now → it shows up (the compounding effect)
        _lesson(self.root, "l1", ["py"], title="Reset the fixture")
        warm = context.format_packet(context.build_packet(self.root, cid))
        self.assertIn("Reset the fixture", warm)
        self.assertNotIn("No prior lessons", warm)

    def test_missing_contract(self):
        self.assertFalse(context.build_packet(self.root, "ghost")["ok"])


if __name__ == "__main__":
    unittest.main()
