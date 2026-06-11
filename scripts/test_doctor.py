#!/usr/bin/env python3
"""Tests for `polis doctor` validation and the schema-v2 polis.yml config."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import config as cfg  # noqa: E402
from polis.doctor import run_doctor  # noqa: E402


def _make_polis(root: Path, with_citizen=True):
    root.mkdir(parents=True, exist_ok=True)
    (root / "CONSTITUTION.md").write_text("# Constitution\n", encoding="utf-8")
    if with_citizen:
        cdir = root / "citizens" / "agent-a"
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "capability_card.yml").write_text(
            "agent_id: agent-a\ncapability_tags:\n  py: {self_rating: 4}\n", encoding="utf-8"
        )


class ConfigTest(unittest.TestCase):
    def test_defaults_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            root.mkdir()
            self.assertFalse(cfg.has_config(root))
            c = cfg.load_config(root)
            self.assertEqual(c["schema_version"], cfg.SCHEMA_VERSION)
            self.assertAlmostEqual(sum(c["routing"]["weights"].values()), 1.0, places=2)

    def test_write_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            root.mkdir()
            path = cfg.write_config(root)
            self.assertTrue(path.exists())
            self.assertTrue(cfg.has_config(root))
            c = cfg.load_config(root)
            self.assertEqual(c["schema_version"], 2)

    def test_override_merges_over_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            root.mkdir()
            cfg.write_config(root, {"routing": {"explore_rate": 0.42}})
            c = cfg.load_config(root)
            self.assertEqual(c["routing"]["explore_rate"], 0.42)
            # untouched keys keep defaults
            self.assertEqual(c["routing"]["weights"]["history"], 0.55)


class DoctorTest(unittest.TestCase):
    def test_clean_polis_ok_with_config_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            _make_polis(root)
            res = run_doctor(root)
            self.assertTrue(res["ok"])
            self.assertTrue(any("no polis.yml" in w for w in res["warnings"]))

    def test_missing_constitution_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            root.mkdir()
            res = run_doctor(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("CONSTITUTION" in e for e in res["errors"]))

    def test_lesson_unknown_citizen_warns(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            _make_polis(root)
            ldir = root / "lessons" / "x"
            ldir.mkdir(parents=True)
            (ldir / "l.md").write_text(
                "---\nlesson_id: L\nstatus: accepted\nrouting_effect:\n"
                "  - citizen: ghost\n    tags: [py]\n    delta: 0.1\n---\n",
                encoding="utf-8",
            )
            res = run_doctor(root)
            self.assertTrue(res["ok"])  # warning, not error
            self.assertTrue(any("unknown citizen 'ghost'" in w for w in res["warnings"]))

    def test_non_numeric_delta_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            _make_polis(root)
            ldir = root / "lessons" / "x"
            ldir.mkdir(parents=True)
            (ldir / "l.md").write_text(
                "---\nlesson_id: L\nstatus: accepted\nrouting_effect:\n"
                "  - citizen: agent-a\n    tags: [py]\n    delta: lots\n---\n",
                encoding="utf-8",
            )
            res = run_doctor(root)
            self.assertFalse(res["ok"])
            self.assertTrue(any("non-numeric" in e for e in res["errors"]))


if __name__ == "__main__":
    unittest.main()
