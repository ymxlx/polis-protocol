#!/usr/bin/env python3
"""Smoke tests for init_polis.py dry-run behavior."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "init_polis.py"


def run_init(project_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(project_root),
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


class InitPolisDryRunTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            result = run_init(
                project_root,
                "--agent-id",
                "codex-test-agent",
                "--project-name",
                "Dry Run Project",
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry run: Polis would be founded", result.stdout)
            self.assertIn("? CONSTITUTION.md", result.stdout)
            self.assertIn("? <root>/AGENTS.md", result.stdout)
            self.assertIn("No files or directories were created.", result.stdout)
            self.assertFalse((project_root / "_polis").exists())
            self.assertFalse((project_root / "CLAUDE.md").exists())
            self.assertFalse((project_root / "AGENTS.md").exists())
            self.assertFalse((project_root / "GEMINI.md").exists())
            self.assertFalse((project_root / ".agents").exists())

    def test_invalid_agent_id_still_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            result = run_init(
                project_root,
                "--agent-id",
                "bad",
                "--dry-run",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid agent-id", result.stderr)
            self.assertFalse((project_root / "_polis").exists())
            self.assertFalse((project_root / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
