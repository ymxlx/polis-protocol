#!/usr/bin/env bash
# Polis Bench — learned routing vs random / round-robin / static self-ratings / oracle.
# Honest by design: runs the real router, reports where it wins and where it doesn't.
set -e
cd "$(dirname "$0")/.."
python3 scripts/benchmark.py "$@"
