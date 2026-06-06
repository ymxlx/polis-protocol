"""Context packets — the compounding core of Polis self-improvement.

When a contract settles it can file a *lesson*. This module retrieves the
lessons that apply to a new contract (by capability-tag overlap) and assembles a
short "what the team already learned about this kind of work" packet that the
executing agent reads BEFORE starting. The effect compounds: the Nth contract on
a topic begins pre-loaded with all N-1 prior lessons, so the team stops
repeating its own mistakes — something a single agent or an unmanaged swarm
cannot do, because they never accumulate and re-inject outcome-derived knowledge.

This is deliberately not RAG-over-everything: it is *targeted* retrieval of
*outcome-derived, human-or-agent-ratified* lessons, tied to the task at hand.
"""
from pathlib import Path

from .routing import parse_frontmatter


def _lesson_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def _first_paragraph(body: str) -> str:
    chunk = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if not s:
            if chunk:
                break
            continue
        chunk.append(s)
    text = " ".join(chunk)
    return (text[:240] + "…") if len(text) > 240 else text


def matching_lessons(polis_root, required_tags) -> list:
    """Accepted lessons whose capability_tags overlap the contract's required_tags."""
    root = Path(polis_root)
    req = set(required_tags or [])
    lessons_dir = root / "lessons"
    out = []
    if not lessons_dir.exists():
        return out
    for path in sorted(lessons_dir.rglob("*.md")):
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm:
            continue
        if str(fm.get("status", "accepted")).lower() != "accepted":
            continue
        tags = set(fm.get("capability_tags") or [])
        overlap = sorted(tags & req)
        if req and not overlap:
            continue
        out.append({
            "lesson_id": fm.get("lesson_id", path.stem),
            "tags": overlap or sorted(tags),
            "title": _lesson_title(body, fm.get("lesson_id", path.stem)),
            "summary": _first_paragraph(body),
            "quality_impact": fm.get("quality_impact"),
        })
    # Strongest-impact lessons first.
    out.sort(key=lambda x: (x.get("quality_impact") or 0), reverse=True)
    return out


def build_packet(polis_root, contract_id) -> dict:
    from .contracts import find_contract

    path, _state = find_contract(polis_root, contract_id)
    if not path:
        return {"ok": False, "reason": "contract not found"}
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    required_tags = fm.get("required_tags") or []
    return {
        "ok": True,
        "contract_id": fm.get("contract_id", contract_id),
        "title": fm.get("title", ""),
        "required_tags": required_tags,
        "acceptance_criteria": fm.get("acceptance_criteria") or [],
        "lessons": matching_lessons(polis_root, required_tags),
    }


def format_packet(packet: dict) -> str:
    if not packet.get("ok"):
        return f"(no packet: {packet.get('reason')})"
    lines = [
        f"# Context packet — {packet['contract_id']}",
        f"_{packet['title']}_",
        "",
        f"**Required tags:** {', '.join(packet['required_tags']) or '—'}",
    ]
    if packet["acceptance_criteria"]:
        lines += ["", "**Acceptance criteria:**"]
        lines += [f"- {c}" for c in packet["acceptance_criteria"]]
    lessons = packet["lessons"]
    lines += ["", f"## What the team already learned ({len(lessons)} applicable lesson(s))"]
    if not lessons:
        lines.append("_No prior lessons match these tags yet — this task will help seed them._")
    for ln in lessons:
        impact = f" · impact {ln['quality_impact']}" if ln.get("quality_impact") else ""
        lines += ["", f"### {ln['title']}  `[{', '.join(ln['tags'])}]`{impact}", ln["summary"]]
    return "\n".join(lines)
