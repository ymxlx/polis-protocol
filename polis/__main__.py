"""Allow `python -m polis` (issue module entry)."""

from __future__ import annotations

import sys

def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        from polis.cli import main as cli_main  # type: ignore
        result = cli_main(argv)
        return int(result or 0)
    except Exception:
        # minimal fallback
        print("polis: no cli module; package import OK")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
