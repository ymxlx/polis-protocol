"""Contract lifecycle — the shared application layer behind `polis contract ...`.

Agents stop hand-editing `_polis/contracts/*.md`; the CLI (and later the MCP
server and dashboard) drive the same functions here. States:

    proposed --claim--> claimed --settle--> settled
                              \--abandon--> abandoned

Settled contracts feed routing via `--reconcile`; abandoned ones are moved to
`contracts/abandoned/` so they never pollute routing stats.
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

OPEN, SETTLED, ABANDONED = "open", "settled", "abandoned"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "contract"


def _scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if s == "" or re.search(r"[:#\[\]{}\"']|^\s|\s$", s):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def _update_frontmatter(text: str, updates: dict) -> str:
    """Replace top-level scalar keys inside the YAML frontmatter, preserving the rest."""
    m = re.match(r"^(---\s*\n)(.*?\n)(---\s*\n)(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("contract has no YAML frontmatter")
    head, fm, fence, body = m.groups()
    for key, val in updates.items():
        line = f"{key}: {_scalar(val)}"
        pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
        if pattern.search(fm):
            fm = pattern.sub(line, fm, count=1)
        else:
            fm = fm.rstrip("\n") + "\n" + line + "\n"
    return head + fm + fence + body


def _dir(root, state) -> Path:
    return Path(root) / "contracts" / state


def find_contract(root, contract_id):
    """Return (path, state) for a contract id, searching open/settled/abandoned."""
    for state in (OPEN, SETTLED, ABANDONED):
        p = _dir(root, state) / f"{contract_id}.md"
        if p.exists():
            return p, state
    return None, None


def list_contracts(root, state=OPEN) -> list:
    d = _dir(root, state)
    out = []
    if not d.exists():
        return out
    for f in sorted(d.glob("*.md")):
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        out.append({
            "contract_id": fm.get("contract_id", f.stem),
            "title": fm.get("title", ""),
            "status": fm.get("status", "?"),
            "owner": fm.get("owner"),
            "required_tags": fm.get("required_tags", []),
        })
    return out


def open_contract(root, title, required_tags, opened_by, stakes="medium",
                  cost_ceiling="medium", acceptance=None, deadline=None, contract_id=None) -> dict:
    root = Path(root)
    cid = contract_id or _slugify(title)
    open_dir = _dir(root, OPEN)
    open_dir.mkdir(parents=True, exist_ok=True)
    # Ensure a unique id.
    if (open_dir / f"{cid}.md").exists():
        n = 2
        while (open_dir / f"{cid}-{n}.md").exists():
            n += 1
        cid = f"{cid}-{n}"

    fm = {
        "contract_id": cid,
        "title": title,
        "opened_by": opened_by,
        "opened_at": _now(),
        "owner": None,
        "status": "proposed",
        "stakes": stakes,
        "required_tags": list(required_tags or []),
        "deadline": deadline,
        "cost_ceiling": cost_ceiling,
        "acceptance_criteria": list(acceptance or []),
        "routing": {"recommended_by_router": None, "recommendation_score": None,
                    "exploration": None, "override": None},
        "review": {"required": stakes == "high", "reviewer": None, "status": None},
        "settled_at": None,
        "quality_score": None,
        "actual_minutes": None,
    }
    body = (f"\n# {title}\n\n## Intent\n\n### Goal\n<what and why>\n\n"
            "### Acceptance criteria\n"
            + ("".join(f"- {c}\n" for c in (acceptance or [])) or "- <criterion>\n")
            + "\n### Notes for the executor\n<context>\n")
    text = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body
    path = open_dir / f"{cid}.md"
    atomic_write_text(path, text)
    return {"contract_id": cid, "path": str(path)}


def claim_contract(root, contract_id, citizen, force=False) -> dict:
    path, state = find_contract(root, contract_id)
    if not path:
        return {"ok": False, "reason": "contract not found"}
    if state != OPEN:
        return {"ok": False, "reason": f"contract is {state}, not open"}
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    owner = fm.get("owner")
    if owner and owner != citizen and not force:
        return {"ok": False, "reason": f"already owned by {owner} (use force to override)"}
    text = _update_frontmatter(path.read_text(encoding="utf-8"),
                               {"owner": citizen, "status": "claimed"})
    atomic_write_text(path, text)
    return {"ok": True, "contract_id": contract_id, "owner": citizen}


def settle_contract(root, contract_id, quality, minutes=None, by=None) -> dict:
    path, state = find_contract(root, contract_id)
    if not path:
        return {"ok": False, "reason": "contract not found"}
    if state != OPEN:
        return {"ok": False, "reason": f"contract is {state}, not open"}
    try:
        q = int(quality)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "quality must be an integer 1-5"}
    q = max(1, min(5, q))
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    updates = {"status": "settled", "settled_at": _now(), "quality_score": q}
    if minutes is not None:
        updates["actual_minutes"] = int(minutes)
    if by or fm.get("owner"):
        updates["owner"] = by or fm.get("owner")
    text = _update_frontmatter(path.read_text(encoding="utf-8"), updates)
    dest = _dir(root, SETTLED)
    dest.mkdir(parents=True, exist_ok=True)
    dest_path = dest / path.name
    atomic_write_text(dest_path, text)
    path.unlink()
    return {"ok": True, "contract_id": contract_id, "quality_score": q, "path": str(dest_path)}


def abandon_contract(root, contract_id, reason=None) -> dict:
    path, state = find_contract(root, contract_id)
    if not path:
        return {"ok": False, "reason": "contract not found"}
    if state != OPEN:
        return {"ok": False, "reason": f"contract is {state}, not open"}
    updates = {"status": "abandoned", "settled_at": _now()}
    if reason:
        updates["abandoned_reason"] = reason
    text = _update_frontmatter(path.read_text(encoding="utf-8"), updates)
    dest = _dir(root, ABANDONED)
    dest.mkdir(parents=True, exist_ok=True)
    dest_path = dest / path.name
    atomic_write_text(dest_path, text)
    path.unlink()
    return {"ok": True, "contract_id": contract_id, "path": str(dest_path)}
