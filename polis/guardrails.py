"""Guardrails — failures become checks (self-improvement Layer 2).

When a contract fails or is reworked, the team records a *guardrail*: a short,
must-pass criterion tagged by capability. Future contracts on those tags
auto-inherit the guardrail (via context packets and `open_contract`), so each
failure class can recur at most once before it becomes a standing check. The
team's definition of done tightens monotonically — compounding, like lessons.
"""
import re
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from ._io import atomic_write_text
from .routing import parse_frontmatter


def _dir(root) -> Path:
    return Path(root) / "guardrails"


def _slug(text: str) -> str:
    return (re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]) or "guardrail"


def add_guardrail(root, text, tags, source_contract=None) -> dict:
    d = _dir(root)
    d.mkdir(parents=True, exist_ok=True)
    gid = _slug(text)
    if (d / f"{gid}.md").exists():
        n = 2
        while (d / f"{gid}-{n}.md").exists():
            n += 1
        gid = f"{gid}-{n}"
    fm = {
        "guardrail_id": gid,
        "tags": list(tags or []),
        "status": "active",
        "source_contract": source_contract,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    out = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + text.strip() + "\n"
    atomic_write_text(d / f"{gid}.md", out)
    return {"guardrail_id": gid, "path": str(d / f"{gid}.md")}


def list_guardrails(root) -> list:
    d = _dir(root)
    out = []
    if not d.exists():
        return out
    for f in sorted(d.glob("*.md")):
        fm, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        if str(fm.get("status", "active")).lower() != "active":
            continue
        out.append({
            "guardrail_id": fm.get("guardrail_id", f.stem),
            "tags": fm.get("tags") or [],
            "text": body.strip(),
            "source_contract": fm.get("source_contract"),
        })
    return out


def matching_guardrails(root, tags) -> list:
    req = set(tags or [])
    out = []
    for g in list_guardrails(root):
        if req and not (set(g["tags"]) & req):
            continue
        out.append(g)
    return out
