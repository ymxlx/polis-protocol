#!/usr/bin/env python3
"""Extension-bundled entry point: runs the bundled v2 `polis` package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from polis.routing import main

if __name__ == "__main__":
    main()
