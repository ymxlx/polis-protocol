#!/usr/bin/env python3
"""Tests that shipped example polises pass doctor validation."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from polis.doctor import run_doctor  # noqa: E402

class ExamplesDoctorTest(unittest.TestCase):
    def test_shipped_examples_pass_doctor(self):
        examples_dir = ROOT / "examples"
        self.assertTrue(examples_dir.is_dir(), "examples directory missing")
        
        found_examples = 0
        for example_path in examples_dir.iterdir():
            if example_path.is_dir():
                polis_dir = example_path / "_polis"
                if polis_dir.is_dir():
                    res = run_doctor(polis_dir)
                    self.assertTrue(res["ok"], f"Example {example_path.name} failed doctor validation: {res.get('errors')}")
                    found_examples += 1
                    
        self.assertGreater(found_examples, 0, "No examples with _polis found")

    def test_malformed_example_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "_polis"
            root.mkdir(parents=True)
            # Missing CONSTITUTION.md makes it malformed
            res = run_doctor(root)
            self.assertFalse(res["ok"])

if __name__ == "__main__":
    unittest.main()
