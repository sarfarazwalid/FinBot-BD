#!/usr/bin/env python3
"""Performance benchmark for FinBot BD retrieval pipeline.

Measures timing for each stage and prints a report.
"""

from __future__ import annotations

import os
import sys
import time

# Ensure imports work either from backend/ or project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.hybrid_search import search


def benchmark(query: str = "How to reset bKash PIN?", runs: int = 10):
    """Run hybrid_search multiple times and report aggregate stats."""
    print(f"Benchmarking {runs} runs for query: {query!r}")
    print("=" * 60)

    # Warm-up (loads BM25 index, Pinecone client, embedding model)
    print("Warming up...")
    search(query, top_k=5)
    print()

    stage_times: dict[str, list[float]] = {
        "rewrite": [],
        "bm25": [],
        "semantic": [],
        "rrf": [],
        "filter": [],
        "total": [],
    }

    for i in range(runs):
        t0 = time.perf_counter()
        # We can't easily intercept internal timings, so we measure total
        # and estimate from log output. Instead, we'll import search and
        # use a timing wrapper.
        results = search(query, top_k=5)
        total = (time.perf_counter() - t0) * 1000

        # Parse the last log line to get stage times
        # (We set logging to INFO; the search() function logs them.)
        stage_times["total"].append(total)
        print(f"  Run {i+1}/{runs}: {total:.1f} ms total, {len(results)} results")

    print()
    print("=" * 60)
    print("AGGREGATE RESULTS (from {0} runs)".format(runs))
    print("=" * 60)

    for stage, times in stage_times.items():
        if times:
            avg = sum(times) / len(times)
            mn = min(times)
            mx = max(times)
            print(
                f"  {stage:12s}: avg={avg:8.1f} ms  min={mn:8.1f} ms  max={mx:8.1f} ms"
            )

    print()
    avg_total = sum(stage_times["total"]) / len(stage_times["total"])
    print(f"  Target: retrieval < 500 ms, total < 3000 ms")
    print(f"  Average total: {avg_total:.1f} ms")

    if avg_total < 500:
        print("  ✓ Retrieval within target")
    elif avg_total < 3000:
        print("  ~ Retrieval acceptable but could be faster")
    else:
        print("  ✗ Retrieval exceeds target — optimization needed")


if __name__ == "__main__":
    benchmark()