#!/usr/bin/env bash
# Polis collision-prevention demo — the thing a single agent or an unmanaged
# swarm cannot do: guarantee that two agents never edit the same file at once.
set -e
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
cp -r examples/research-team/_polis "$TMP/_polis"
P="$TMP/_polis"
say() { printf '\n\033[1m%s\033[0m\n' "$1"; }

say "Two agents, one repo. Unmanaged, they both edit src/auth/login.py → merge conflict / lost work."
say "── With Polis ──"
echo "1) Claude reserves the auth module before touching it:"
python3 -m polis.cli reserve src/auth --as claude-research-pesaj --note "refactor login" --polis-root "$P"
echo
echo "2) Codex tries to edit a file INSIDE it — Polis blocks the collision:"
python3 -m polis.cli reserve src/auth/login.py --as codex-frontend-pesaj --polis-root "$P" || true
echo
echo "3) Codex works elsewhere instead (no overlap → allowed):"
python3 -m polis.cli reserve src/ui/button.tsx --as codex-frontend-pesaj --polis-root "$P"
echo
echo "4) Claude finishes and releases; Codex can now safely take the file:"
python3 -m polis.cli release src/auth --as claude-research-pesaj --polis-root "$P"
python3 -m polis.cli reserve src/auth/login.py --as codex-frontend-pesaj --polis-root "$P"
say "Guarantee: no two agents ever held the same path. Deterministic, no LLM judgement required."
rm -rf "$TMP"
