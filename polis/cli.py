#!/usr/bin/env python3
"""The ``polis`` command — unified entry point for the Polis control plane.

This is the v2 surface. It currently wraps the established init / route /
reconcile logic and adds a real ``status`` summary. Further lifecycle commands
(doctor, migrate, serve, contract, citizen, review, reserve, report) land in
later v2 increments — they are intentionally not advertised until implemented.
"""
import sys
from pathlib import Path

from . import __version__

USAGE = """polis {v} — local-first control plane for coding agents

usage: polis <command> [options]

commands:
  init        Scaffold or repair a _polis/ workspace and register an agent
  route       Recommend a citizen for an open contract (use --explain)
  reconcile   Rebuild routing_stats.yml from settled contracts
  status      Summarize the polis: citizens, open/settled contracts, routing
  doctor      Validate the polis (schema, cards, contracts, lessons)
  version     Print the polis version

Run `polis <command> --help` for command-specific options.
""".format(v=__version__)


def _find_polis_root(start=None):
    """Walk up from `start` (default cwd) looking for a _polis/ workspace."""
    p = Path(start or ".").resolve()
    for cand in [p, *p.parents]:
        if (cand / "_polis" / "CONSTITUTION.md").exists():
            return cand / "_polis"
    if p.name == "_polis" and (p / "CONSTITUTION.md").exists():
        return p
    return None


def cmd_status(argv):
    import argparse

    ap = argparse.ArgumentParser(prog="polis status")
    ap.add_argument("--polis-root", default=None,
                    help="Path to _polis/ (default: auto-detect from cwd)")
    args = ap.parse_args(argv)

    from . import routing

    root = Path(args.polis_root).resolve() if args.polis_root else _find_polis_root()
    if not root or not root.exists():
        raise SystemExit("No _polis/ found. Run `polis init` first (or pass --polis-root).")

    citizens = routing.load_citizens(root)
    stats = routing.load_routing_stats(root)
    open_dir = root / "contracts" / "open"
    settled_dir = root / "contracts" / "settled"
    n_open = len(list(open_dir.glob("*.md"))) if open_dir.exists() else 0
    n_settled = len(list(settled_dir.glob("*.md"))) if settled_dir.exists() else 0

    print(f"polis: {root}")
    print(f"  citizens          : {len(citizens)}")
    for cid in citizens:
        print(f"      - {cid}")
    print(f"  open contracts    : {n_open}")
    print(f"  settled contracts : {n_settled}")
    print(f"  explore_rate      : {stats.get('explore_rate', 0.15)}")
    tags = stats.get("tags", {})
    if tags:
        print("  routing by tag (leader / confidence):")
        for tag, ts in sorted(tags.items()):
            leader = ts.get("leader", "—")
            conf = ts.get("leader_confidence", 0.0)
            try:
                conf_s = f"{float(conf):.2f}"
            except (TypeError, ValueError):
                conf_s = str(conf)
            print(f"      {tag:22s} {leader}  (conf {conf_s})")
    return 0


def cmd_doctor(argv):
    import argparse

    ap = argparse.ArgumentParser(prog="polis doctor")
    ap.add_argument("--polis-root", default=None,
                    help="Path to _polis/ (default: auto-detect from cwd)")
    ap.add_argument("--write-config", action="store_true",
                    help="Create/update _polis/polis.yml from defaults, then validate")
    args = ap.parse_args(argv)

    root = Path(args.polis_root).resolve() if args.polis_root else _find_polis_root()
    if not root or not root.exists():
        raise SystemExit("No _polis/ found. Run `polis init` first (or pass --polis-root).")

    from . import doctor, config as _config

    if args.write_config:
        existing = _config.load_config(root) if _config.has_config(root) else None
        path = _config.write_config(root, existing)
        print(f"wrote {path}")

    result = doctor.run_doctor(root)
    for item in result["info"]:
        print(f"  info : {item}")
    for warning in result["warnings"]:
        print(f"  warn : {warning}")
    for error in result["errors"]:
        print(f"  ERROR: {error}")

    if result["ok"]:
        suffix = f" ({len(result['warnings'])} warning(s))" if result["warnings"] else ""
        print(f"\npolis doctor: OK{suffix}")
        return 0
    print(f"\npolis doctor: {len(result['errors'])} error(s)")
    return 1


def _delegate(module_name, argv, prepend=None):
    """Run a legacy module's main() by reconstructing sys.argv."""
    from . import routing, initializer  # noqa: F401

    mod = {"routing": routing, "initializer": initializer}[module_name]
    saved = sys.argv
    try:
        sys.argv = ["polis", *(prepend or []), *argv]
        return mod.main()
    finally:
        sys.argv = saved


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0

    cmd, rest = argv[0], argv[1:]
    if cmd in ("version", "-V", "--version"):
        print(f"polis {__version__}")
        return 0
    if cmd == "init":
        return _delegate("initializer", rest)
    if cmd == "route":
        return _delegate("routing", rest)
    if cmd == "reconcile":
        return _delegate("routing", rest, prepend=["--reconcile"])
    if cmd == "status":
        return cmd_status(rest)
    if cmd == "doctor":
        return cmd_doctor(rest)

    print(f"Unknown command: {cmd}\n")
    print(USAGE)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
