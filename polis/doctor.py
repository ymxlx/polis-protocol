"""`polis doctor` — validate a _polis/ workspace and report problems.

Returns a structured result so the CLI, MCP server, and dashboard can all reuse
the same checks. Errors fail the check (non-zero exit); warnings are advisory.
"""
from pathlib import Path

from . import config as _config
from . import integrity
from .routing import load_citizens, load_lessons, parse_frontmatter


def run_doctor(polis_root) -> dict:
    """Return {'errors': [...], 'warnings': [...], 'info': [...], 'ok': bool}."""
    root = Path(polis_root)
    errors, warnings, info = [], [], []

    if not root.exists():
        return {"errors": [f"polis root not found: {root}"], "warnings": [], "info": [], "ok": False}
    if not (root / "CONSTITUTION.md").exists():
        errors.append("missing CONSTITUTION.md (is this a _polis/ root?)")

    # Schema / config.
    if not _config.has_config(root):
        warnings.append("no polis.yml — using built-in defaults. Run `polis doctor --write-config`.")
    else:
        cfg = _config.load_config(root)
        sv = cfg.get("schema_version")
        if sv != _config.SCHEMA_VERSION:
            warnings.append(f"polis.yml schema_version={sv}, expected {_config.SCHEMA_VERSION}")
        weights = (cfg.get("routing") or {}).get("weights") or {}
        if weights and abs(sum(weights.values()) - 1.0) > 0.01:
            warnings.append(f"routing weights sum to {sum(weights.values()):.2f}, expected ~1.0")

    # Citizens.
    citizens = load_citizens(root)
    if not citizens:
        warnings.append("no registered citizens")
    for cid, card in citizens.items():
        if not card.get("capability_tags"):
            warnings.append(f"citizen {cid}: capability_card has no capability_tags")
        integ = integrity.verify_card(card)
        if integ["state"] == "mismatch":
            warnings.append(f"citizen {cid}: content_hash mismatch — card edited since stamped")
        elif integ["state"] == "legacy":
            info.append(f"citizen {cid}: legacy signature field — run `polis verify --fix`")
        elif integ["state"] == "unstamped":
            info.append(f"citizen {cid}: no content_hash — run `polis verify --fix`")

    # Contracts parse cleanly.
    for sub in ("open", "settled"):
        d = root / "contracts" / sub
        if d.exists():
            for f in sorted(d.glob("*.md")):
                fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
                if not fm:
                    warnings.append(f"contract {sub}/{f.name}: no YAML frontmatter")

    # Lessons: validate routing_effect references and deltas.
    known = set(citizens)
    for lesson in load_lessons(root):
        for eff in lesson.get("routing_effect", []) or []:
            citizen = eff.get("citizen")
            if citizen and known and citizen not in known:
                warnings.append(
                    f"lesson {lesson['lesson_id']}: routing_effect references unknown citizen '{citizen}'"
                )
            try:
                float(eff.get("delta", 0))
            except (TypeError, ValueError):
                errors.append(f"lesson {lesson['lesson_id']}: non-numeric routing_effect delta")

    # Amendments check.
    from datetime import datetime
    from .amendments import list_amendments
    try:
        all_amends = list_amendments(root)
        for am in all_amends:
            aid = am.get("amendment_id")
            if not aid:
                errors.append("found amendment with missing/null 'amendment_id'")
                continue
            status = am.get("status")
            if status not in ("proposed", "ratified", "rejected", "expired"):
                errors.append(f"amendment {aid}: invalid status '{status}'")
            quorum = am.get("quorum_required")
            if quorum is not None:
                try:
                    q_int = int(quorum)
                    if q_int <= 0:
                        errors.append(f"amendment {aid}: quorum_required must be a positive integer, got {quorum}")
                except (TypeError, ValueError):
                    errors.append(f"amendment {aid}: non-integer quorum_required '{quorum}'")
            votes = am.get("votes") or {}
            for cat, vlist in votes.items():
                if cat not in ("agree", "disagree", "abstain", "request_changes"):
                    warnings.append(f"amendment {aid}: unknown vote category '{cat}'")
                elif not isinstance(vlist, list):
                    errors.append(f"amendment {aid}: vote category '{cat}' must be a list")
                else:
                    for voter in vlist:
                        if known and voter not in known:
                            warnings.append(f"amendment {aid}: vote cast by unknown citizen '{voter}'")
            exp = am.get("expires_at")
            if exp:
                try:
                    datetime.strptime(str(exp).strip(), "%Y-%m-%d")
                except ValueError:
                    errors.append(f"amendment {aid}: invalid expires_at format '{exp}', expected YYYY-MM-DD")
    except Exception as e:
        errors.append(f"failed to load/check amendments: {e}")

    open_dir = root / "contracts" / "open"
    n_open = len(list(open_dir.glob("*.md"))) if open_dir.exists() else 0
    info.append(f"{len(citizens)} citizens, {n_open} open contracts")

    return {"errors": errors, "warnings": warnings, "info": info, "ok": not errors}
