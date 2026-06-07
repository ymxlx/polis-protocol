#!/usr/bin/env python3
"""Polis Bench runner — `python3 scripts/benchmark.py [--contracts N] [--seed S] [--csv path]`.

Thin wrapper over polis.bench so the benchmark is runnable straight from a repo
checkout (no install). Honest by design: it runs the *real* router against
random / round-robin / static-self-rating baselines and an oracle ceiling.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from polis import bench  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Polis Bench — learned routing vs baselines.")
    ap.add_argument("--mode", choices=["routing", "learning"], default="routing")
    ap.add_argument("--contracts", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--citizens", type=int, default=4)
    ap.add_argument("--tags", type=int, default=5)
    ap.add_argument("--csv", default=None, help="Write per-contract learning curves to this CSV")
    args = ap.parse_args()

    if args.mode == "learning":
        print(bench.format_learning_report(bench.run_learning_benchmark(
            n_contracts=args.contracts, seed=args.seed)))
        return
    result = bench.run_benchmark(n_contracts=args.contracts, n_citizens=args.citizens,
                                 n_tags=args.tags, seed=args.seed)
    print(bench.format_report(result))
    if args.csv:
        print(f"\nwrote learning curves: {bench.write_csv(result, args.csv)}")


if __name__ == "__main__":
    main()
