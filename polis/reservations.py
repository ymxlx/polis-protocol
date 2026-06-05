"""Advisory file reservations — collision prevention for parallel agents.

A citizen reserves the files (or directories) it is about to edit; another
citizen's overlapping reservation is rejected through Polis surfaces before two
agents stomp the same code. Reservations are *advisory coordination*, not a
filesystem lock or a security boundary. State lives in `_polis/reservations.yml`.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from ._io import atomic_write_text

RES_FILE = "reservations.yml"


def _now():
    return datetime.now(timezone.utc)


def _path(polis_root) -> Path:
    return Path(polis_root) / RES_FILE


def _norm(p: str) -> str:
    return PurePosixPath(str(p).strip().lstrip("./")).as_posix()


def paths_conflict(a: str, b: str) -> bool:
    """True if two paths overlap: identical, or one contains the other."""
    pa, pb = PurePosixPath(_norm(a)), PurePosixPath(_norm(b))
    if pa == pb:
        return True
    return pa in pb.parents or pb in pa.parents


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def load_reservations(polis_root) -> list:
    path = _path(polis_root)
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    return data.get("reservations", []) or []


def active_reservations(polis_root, now=None) -> list:
    """Reservations whose expiry (if any) is still in the future."""
    now = now or _now()
    out = []
    for res in load_reservations(polis_root):
        exp = _parse_dt(res.get("expires_at"))
        if exp is not None and exp <= now:
            continue
        out.append(res)
    return out


def _save(polis_root, reservations) -> Path:
    payload = "# Advisory file reservations (collision prevention). Managed by `polis reserve/release`.\n"
    payload += yaml.safe_dump({"reservations": reservations}, sort_keys=False, allow_unicode=True)
    return atomic_write_text(_path(polis_root), payload)


def conflicts_for(polis_root, citizen, paths, now=None) -> list:
    """Return [{'path', 'holder', 'held_path'}] for requested paths held by *others*."""
    now = now or _now()
    requested = [_norm(p) for p in paths]
    found = []
    for res in active_reservations(polis_root, now=now):
        if res.get("citizen") == citizen:
            continue
        for held in res.get("paths", []):
            for req in requested:
                if paths_conflict(req, held):
                    found.append({"path": req, "holder": res.get("citizen"), "held_path": held})
    return found


def reserve(polis_root, citizen, paths, ttl_minutes=None, note=None, now=None) -> dict:
    """Reserve paths for a citizen. Rejected if any path conflicts with another citizen."""
    if not citizen:
        raise ValueError("citizen is required")
    if not paths:
        raise ValueError("at least one path is required")
    now = now or _now()
    conflicts = conflicts_for(polis_root, citizen, paths, now=now)
    if conflicts:
        return {"ok": False, "conflicts": conflicts, "reservation": None}

    reservation = {
        "citizen": citizen,
        "paths": [_norm(p) for p in paths],
        "reserved_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat() if ttl_minutes else None,
    }
    if note:
        reservation["note"] = note

    # Drop this citizen's now-expired rows while we are here; keep everyone else's.
    kept = [r for r in load_reservations(polis_root)
            if not (r.get("citizen") == citizen and (_parse_dt(r.get("expires_at")) or now + timedelta(days=1)) <= now)]
    kept.append(reservation)
    _save(polis_root, kept)
    return {"ok": True, "conflicts": [], "reservation": reservation}


def release(polis_root, citizen, paths=None, now=None) -> int:
    """Release a citizen's reservations (all, or only those overlapping `paths`)."""
    reservations = load_reservations(polis_root)
    targets = [_norm(p) for p in paths] if paths else None
    kept, removed = [], 0
    for res in reservations:
        if res.get("citizen") != citizen:
            kept.append(res)
            continue
        if targets is None:
            removed += 1
            continue
        remaining = [hp for hp in res.get("paths", [])
                     if not any(paths_conflict(hp, t) for t in targets)]
        if not remaining:
            removed += 1
        elif remaining != res.get("paths"):
            res = dict(res, paths=remaining)
            kept.append(res)
            removed += 1
        else:
            kept.append(res)
    _save(polis_root, kept)
    return removed
