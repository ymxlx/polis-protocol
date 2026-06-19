"""Polis Protocol — the local-first control plane for coding agents.

The package home for the routing and initialization logic. Backward-compatible
shims remain at ``scripts/route_contract.py`` and ``scripts/init_polis.py``.
"""

try:  # derive from installed distribution metadata so the banner can never drift
    from importlib.metadata import PackageNotFoundError, version as _version

    __version__ = _version("polis-protocol")
except (ImportError, PackageNotFoundError):  # running from a source tree / no metadata
    __version__ = "2.0.1"
