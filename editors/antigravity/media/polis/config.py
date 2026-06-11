"""Polis workspace configuration — `_polis/polis.yml` (schema v2).

Centralizes the routing policy (weights, exploration rate, lesson cap) and the
schema/policy version so they live in one inspectable, Git-friendly file instead
of being scattered across code constants and routing_stats.yml.

Backward compatible: if no `polis.yml` exists, callers fall back to the legacy
behavior (module defaults + explore_rate from routing_stats.yml).
"""
import copy
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from ._io import atomic_write_text

SCHEMA_VERSION = 2

DEFAULT_CONFIG = {
    "schema_version": SCHEMA_VERSION,
    "policy_version": 1,
    "routing": {
        "explore_rate": 0.15,
        "lesson_cap": 0.15,
        "weights": {"history": 0.55, "self": 0.20, "cost": 0.15, "avail": 0.10},
    },
}


def config_path(polis_root) -> Path:
    return Path(polis_root) / "polis.yml"


def has_config(polis_root) -> bool:
    return config_path(polis_root).exists()


def _deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for key, val in (over or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_config(polis_root) -> dict:
    """Return the merged config (defaults overlaid with polis.yml, if present)."""
    path = config_path(polis_root)
    if not path.exists() or yaml is None:
        return copy.deepcopy(DEFAULT_CONFIG)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return copy.deepcopy(DEFAULT_CONFIG)
    return _deep_merge(DEFAULT_CONFIG, data)


def write_config(polis_root, config: dict = None) -> Path:
    """Materialize `_polis/polis.yml` (defaults merged with `config`), atomically."""
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML is required to write polis.yml")
    cfg = _deep_merge(DEFAULT_CONFIG, config or {})
    header = (
        f"# Polis configuration (schema v{SCHEMA_VERSION}).\n"
        "# Routing policy + weights live here. `polis doctor` validates this file.\n"
    )
    return atomic_write_text(config_path(polis_root), header + yaml.safe_dump(cfg, sort_keys=False))
