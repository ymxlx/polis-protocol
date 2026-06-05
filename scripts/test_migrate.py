#!/usr/bin/env python3
"""Tests for reversible `polis migrate` (v1 -> v2)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from polis import config as cfg  # noqa: E402
from polis import integrity, migrate  # noqa: E402


def _v1_polis(root: Path):
    """A schema-v1 polis: constitution + one un-stamped card, no polis.yml."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "CONSTITUTION.md").write_text("# Constitution\n", encoding="utf-8")
    cdir = root / "citizens" / "agent-a"
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "capability_card.yml").write_text(
        "agent_id: agent-a\ncapability_tags:\n  py: {self_rating: 4}\n", encoding="utf-8"
    )
    return cdir / "capability_card.yml"


class MigrateTest(unittest.TestCase):
    def test_plan_lists_config_and_card(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            _v1_polis(root)
            actions = {a["action"] for a in migrate.plan_migration(root)}
            self.assertIn("write-config", actions)
            self.assertIn("stamp-card", actions)

    def test_apply_then_rollback_restores_exactly(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            card = _v1_polis(root)
            card_before = card.read_text(encoding="utf-8")

            res = migrate.apply_migration(root)
            # config now exists, card is stamped
            self.assertTrue(cfg.has_config(root))
            stamped = yaml.safe_load(card.read_text(encoding="utf-8"))
            self.assertEqual(integrity.verify_card(stamped)["state"], "ok")
            self.assertTrue(res["backup"])
            # re-planning shows nothing left to do
            self.assertEqual(migrate.plan_migration(root), [])

            # rollback: config (newly created) removed, card restored byte-for-byte
            migrate.rollback(root)
            self.assertFalse(cfg.has_config(root))
            self.assertEqual(card.read_text(encoding="utf-8"), card_before)

    def test_rollback_without_backup_is_graceful(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            _v1_polis(root)
            res = migrate.rollback(root)
            self.assertEqual(res["error"], "no backup found")


if __name__ == "__main__":
    unittest.main()
