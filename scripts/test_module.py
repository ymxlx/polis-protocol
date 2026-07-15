#!/usr/bin/env python3
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class ModuleEntryPointTest(unittest.TestCase):
    def test_help_flag(self):
        result = subprocess.run([sys.executable, "-m", "polis", "--help"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: polis", result.stdout)
        
    def test_version_flag(self):
        result = subprocess.run([sys.executable, "-m", "polis", "version"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("polis", result.stdout.lower() + result.stderr.lower())

if __name__ == "__main__":
    unittest.main()
