"""Content-integrity hashes for capability cards.

This is tamper-evidence, NOT cryptographic identity. A card's `content_hash` is a
SHA-256 over the card's semantic content (its parsed key/values, excluding the
hash field itself). It lets other citizens detect that a card was edited after it
was stamped. It does not prove *who* made the edit — real identity signing is out
of scope for a markdown protocol, so we deliberately avoid the word "signature".
"""
import hashlib
import re
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from ._io import atomic_write_text

# Fields that are not part of the hashed content.
_EXCLUDED = ("content_hash", "signature")


def content_hash(card: dict) -> str:
    """SHA-256 hex of the card's semantic content (excluding hash/signature fields).

    Hashing the *parsed* content (re-serialized canonically) means whitespace,
    comment, and key-order changes don't alter the hash — only real content edits do.
    """
    payload = {k: v for k, v in (card or {}).items() if k not in _EXCLUDED}
    canonical = yaml.safe_dump(payload, sort_keys=True, default_flow_style=False, allow_unicode=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_card(card: dict) -> dict:
    """Return {'state', 'computed', 'stored'} for a parsed card.

    state is one of: 'ok' (hash matches), 'mismatch' (edited since stamped),
    'legacy' (has the old `signature` field but no `content_hash`),
    'unstamped' (no integrity field at all).
    """
    computed = content_hash(card)
    raw = (card or {}).get("content_hash")
    if raw:
        stored = str(raw).split(":")[-1]  # tolerate an optional "sha256:" prefix
        return {"state": "ok" if stored == computed else "mismatch", "computed": computed, "stored": stored}
    if (card or {}).get("signature"):
        return {"state": "legacy", "computed": computed, "stored": None}
    return {"state": "unstamped", "computed": computed, "stored": None}


def stamp_card_file(path) -> str:
    """Compute and write the card's content_hash, preserving the file's formatting.

    Only the integrity line is touched: any existing `content_hash:` or legacy
    `signature:` line is removed and a fresh `content_hash:` is appended.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    digest = content_hash(data)
    kept = [ln for ln in text.splitlines() if not re.match(r"^\s*(content_hash|signature)\s*:", ln)]
    new_text = "\n".join(kept).rstrip() + f'\ncontent_hash: "sha256:{digest}"\n'
    atomic_write_text(path, new_text)
    return digest


def stored_digest(card: dict):
    """Return the bare hex digest stored on a card (stripping any 'sha256:' prefix), or None."""
    raw = (card or {}).get("content_hash")
    if not raw:
        return None
    return str(raw).split(":")[-1]
