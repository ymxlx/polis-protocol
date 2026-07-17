import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class ModuleMainTest(unittest.TestCase):
    def test_module_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "polis", "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: polis <command>", result.stdout)

    def test_module_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "polis", "version"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("polis ", result.stdout)

    def test_module_missing_cli_fails_cleanly(self):
        # Build a throwaway `polis` package that reuses the REAL __main__.py but
        # ships no cli.py, so `from polis.cli import main` cannot resolve. The
        # entry point must exit non-zero with a clear message and NOT leak a
        # Python traceback.
        main_src = (ROOT / "polis" / "__main__.py").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "polis"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("")
            (pkg / "__main__.py").write_text(main_src)
            result = subprocess.run(
                [sys.executable, "-m", "polis"],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("could not load the command-line interface", result.stderr)

if __name__ == "__main__":
    unittest.main()
