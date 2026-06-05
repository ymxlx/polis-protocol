"""`polis migrate` — reversible schema upgrades for a _polis/ workspace.

Replaces destructive in-place edits with a plan/apply/rollback flow. `--apply`
snapshots every file it will touch into `_polis/.polis-backups/<timestamp>/`
(plus a manifest of which files were newly created), so `--rollback` can restore
the previous state exactly — including deleting files the migration added.
"""
import shutil
import time
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from . import config as _config
from . import integrity
from ._io import atomic_write_text

BACKUP_DIR = ".polis-backups"


def _cards(root: Path):
    cdir = root / "citizens"
    return sorted(cdir.glob("*/capability_card.yml")) if cdir.exists() else []


def plan_migration(root) -> list:
    """Return a list of {action, detail, path} describing what `--apply` would do."""
    root = Path(root)
    actions = []

    # 1. Schema config.
    if not _config.has_config(root):
        actions.append({"action": "write-config",
                        "detail": "create polis.yml (schema v2)",
                        "path": str(_config.config_path(root))})
    else:
        cfg = _config.load_config(root)
        if cfg.get("schema_version") != _config.SCHEMA_VERSION:
            actions.append({"action": "update-config",
                            "detail": f"schema_version {cfg.get('schema_version')} -> {_config.SCHEMA_VERSION}",
                            "path": str(_config.config_path(root))})

    # 2. Stamp cards lacking a current content_hash.
    for card_path in _cards(root):
        try:
            card = yaml.safe_load(card_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        state = integrity.verify_card(card)["state"]
        if state in ("unstamped", "legacy", "mismatch"):
            actions.append({"action": "stamp-card",
                            "detail": f"{card_path.parent.name}: {state} -> content_hash",
                            "path": str(card_path)})
    return actions


def _make_backup(root: Path, actions: list) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    bdir = root / BACKUP_DIR / ts
    bdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for action in actions:
        p = Path(action["path"])
        rel = p.relative_to(root).as_posix()
        existed = p.exists()
        manifest.append({"path": rel, "existed_before": existed})
        if existed:
            dest = bdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
    atomic_write_text(bdir / "MANIFEST.yml", yaml.safe_dump(manifest, sort_keys=False))
    return bdir


def apply_migration(root, actions=None) -> dict:
    """Apply (or replay a given plan of) actions, after snapshotting for rollback."""
    root = Path(root)
    actions = plan_migration(root) if actions is None else actions
    if not actions:
        return {"applied": [], "backup": None}

    backup = _make_backup(root, actions)
    applied = []
    for action in actions:
        if action["action"] in ("write-config", "update-config"):
            existing = _config.load_config(root) if _config.has_config(root) else None
            _config.write_config(root, existing)
        elif action["action"] == "stamp-card":
            integrity.stamp_card_file(action["path"])
        applied.append(action)
    return {"applied": applied, "backup": str(backup)}


def latest_backup(root):
    bdir = Path(root) / BACKUP_DIR
    if not bdir.exists():
        return None
    backups = sorted(d for d in bdir.iterdir() if d.is_dir())
    return backups[-1] if backups else None


def rollback(root, backup=None) -> dict:
    """Restore the workspace from a backup (default: most recent)."""
    root = Path(root)
    bdir = Path(backup) if backup else latest_backup(root)
    if not bdir or not bdir.exists():
        return {"restored": [], "backup": None, "error": "no backup found"}

    manifest = yaml.safe_load((bdir / "MANIFEST.yml").read_text(encoding="utf-8")) or []
    restored = []
    for entry in manifest:
        rel = entry["path"]
        target = root / rel
        if entry.get("existed_before"):
            src = bdir / rel
            if src.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
                restored.append(rel)
        else:
            # Migration created this file; rolling back removes it.
            if target.exists():
                target.unlink()
                restored.append(f"removed {rel}")
    return {"restored": restored, "backup": str(bdir), "error": None}
