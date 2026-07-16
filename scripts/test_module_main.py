import subprocess
import sys
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

if __name__ == "__main__":
    unittest.main()
