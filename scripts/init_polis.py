#!/usr/bin/env python3
"""Backward-compatible shim.

The implementation now lives in ``polis/initializer.py``. This shim keeps
existing references working (SKILL.md, docs, the smoke tests, and anyone calling
``python3 scripts/init_polis.py``).
"""
import sys
from pathlib import Path

# Make the `polis` package importable when this file is run directly from the repo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis.initializer import *  # noqa: F401,F403
from polis.initializer import main  # noqa: F401

if __name__ == "__main__":
    main()
