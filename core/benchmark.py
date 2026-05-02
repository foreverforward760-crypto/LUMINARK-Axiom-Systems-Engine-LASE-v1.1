"""
benchmark.py  –  Performance benchmark for all four LUMINARK builds.

Measures inference latency and memory usage for each build across
the full canonical NSDT vector set.

Usage:
    python benchmark.py              # quick run (N=100)
    python benchmark.py --n 500      # deeper run
    python benchmark.py --json       # output raw JSON for logging
"""

import sys
import os
import time
import json
import argparse
import tracemalloc
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luminark import create_engine, NSDTVector

# Canonical test vectors (same set as cross-build tests)
_VECTORS = [
    [0.0, 0.0, 0.0, 0.0, 0.0],
    [1.0, 8.0, 1.0, 1.0, 1.0],
    [2.0, 7.0, 2.0, 2.0, 2.0],
    [4.0, 7.0, 2.5, 3.0, 4.0],
    [3.5, 6.5, 3.0, 3.5, 5.0],
    [5.0, 4.0, 5.0, 5.0, 4.5],
    [6.0, 5.5, 4.0, 6.0, 6.5],
    [6.5, 3.0, 7.0, 7.0, 3.5],
    [7.5, 7.0, 8.0, 2.0, 2.0],
    [8.0, 2.0, 8.5, 1.5, 1.5],
    [5.0, 5.0, 5.0, 5.0, 5.0],
    [10.0, 10.0, 10.0, 10.0, 10.0],
    [0.1, 9.9, 0.1, 9.9, 0.1],
]

BUILDS = ["overwatch", "defense", "unified"]


def _benchmark_build(build: str, n: int) -> dict:
    """Run N inference passes for a build, return timing + memory stats."""
    engine = create_engine(build)
    nsdts = [NSDTVector.from_list(v) for v in _VECTORS]

    # Warm up (not counted)
    for nsdt in nsdts:
        engine.analyze(nsdt)

    # Timed run
    tracemalloc.start()
    latencies = []
    for _ in range(n):
        for nsdt in nsdts:
            t0 = time.perf_counter()
            engine.analyze(nsdt)
            latencies.append((time.perf_counter() - t0) * 1000)  # ms

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "build":        build,
        "n_calls":      len(latencies),
        "mean_ms":      round(statistics.mean(latencies), 4),
        "median_ms":    round(statistics.median(latencies), 4),
        "stdev_ms":     round(statistics.stdev(latencies), 4),
        "min_ms":       round(min(latencies), 4),
        "max_ms":       round(max(latencies), 4),
        "p95_ms":       round(sorted(latencies)[int(0.95 * len(latencies))], 4),
        "peak_mem_kb":  round(peak_mem / 1024, 1),
    }


def _print_table(results: list) -> None:
    header = f"{'Build':<12} {'N':<7} {'Mean ms':<10} {'Median ms':<11} {'p95 ms':<9} {'Min ms':<9} {'Max ms':<9} {'Peak KB':<9}"
    print("\n" + "=" * len(header))
    print("LUMINARK  –  Inference Benchmark")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['build']:<12} {r['n_calls']:<7} {r['mean_ms']:<10} "
            f"{r['median_ms']:<11} {r['p95_ms']:<9} {r['min_ms']:<9} "
            f"{r['max_ms']:<9} {r['peak_mem_kb']:<9}"
        )
    print("=" * len(header) + "\n")

    # Relative comparison
    base = next(r for r in results if r["build"] == "overwatch")
    print("Relative to overwatch (mean latency):")
    for r in results:
        ratio = r["mean_ms"] / base["mean_ms"]
        bar = "█" * int(ratio * 20)
        print(f"  {r['build']:<12}  {ratio:.2f}x  {bar}")
    print()


def main():
    parser = argparse.ArgumentParser(description="LUMINARK inference benchmark")
    parser.add_argument("--n", type=int, default=100, help="Repetitions per build (default 100)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of table")
    parser.add_argument("--builds", nargs="+", default=BUILDS, choices=BUILDS,
                        help="Which builds to benchmark")
    args = parser.parse_args()

    print(f"Benchmarking {args.builds} with N={args.n} passes × {len(_VECTORS)} vectors each…")
    results = []
    for build in args.builds:
        sys.stdout.write(f"  Running {build}…")
        sys.stdout.flush()
        r = _benchmark_build(build, args.n)
        results.append(r)
        print(f" done ({r['mean_ms']:.3f} ms mean)")

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        _print_table(results)


if __name__ == "__main__":
    main()
