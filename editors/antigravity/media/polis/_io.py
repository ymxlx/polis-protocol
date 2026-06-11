"""Small filesystem helpers shared across the control plane.

Atomic writes prevent a crashed or concurrent run from leaving a half-written
YAML/Markdown file in `_polis/` — a real risk once multiple agents touch the
same workspace.
"""
import os
import tempfile
from pathlib import Path


def atomic_write_text(path, text: str) -> Path:
    """Write `text` to `path` atomically (write temp in the same dir, then rename)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return path
