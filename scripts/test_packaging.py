#!/usr/bin/env python3
"""Guards that bundled package data (polis/_data/) stays byte-identical to the
canonical repo-root files, so a pip / uvx / pipx install ships the same
templates and `polis init` works after install (no repo checkout required)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PAIRS = [
    ("SKILL.md", "polis/_data/SKILL.md"),
    ("templates/POLIS_CONSTITUTION.md", "polis/_data/templates/POLIS_CONSTITUTION.md"),
    ("templates/bridge_pointer.md", "polis/_data/templates/bridge_pointer.md"),
]


class PackagingSyncTest(unittest.TestCase):
    def test_bundled_files_exist(self):
        for _root, bundled in PAIRS:
            self.assertTrue((ROOT / bundled).exists(), f"missing bundled data: {bundled}")

    def test_bundled_data_in_sync(self):
        for root, bundled in PAIRS:
            self.assertEqual(
                (ROOT / root).read_text(encoding="utf-8"),
                (ROOT / bundled).read_text(encoding="utf-8"),
                f"{bundled} is out of sync with {root}; re-copy it into polis/_data/",
            )

    def test_initializer_resolves_to_bundled_data(self):
        from polis import initializer
        # data_path must point inside the package, not the repo root.
        self.assertTrue(str(initializer.data_path("SKILL.md")).endswith("polis/_data/SKILL.md"))
        self.assertTrue(initializer.data_path("templates").is_dir())


if __name__ == "__main__":
    unittest.main()
