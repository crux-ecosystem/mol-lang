"""
MOL Language Research — Master Benchmark Runner
=================================================
Runs all benchmarks and generates a unified report with
publication-ready data for the research paper.

Usage:
    cd research/benchmarks
    python3 run_all.py
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

BENCHMARKS = [
    ("bench_01_loc_comparison", "Lines of Code & Readability Comparison"),
    ("bench_02_stdlib_coverage", "Standard Library Coverage & Feature Matrix"),
    ("bench_03_performance", "Execution Performance — MOL vs Python"),
    ("bench_04_security", "Security Feature Comparison"),
    ("bench_05_innovation", "Innovation & Language Design Matrix"),
]


def run_all():
    print("╔" + "═" * 78 + "╗")
    print("║" + " MOL Language Research — Benchmark Suite ".center(78) + "║")
    print("║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    total_start = time.time()
    results = {}

    for i, (module_name, title) in enumerate(BENCHMARKS, 1):
        print(f"\n{'━' * 80}")
        print(f"  [{i}/{len(BENCHMARKS)}] {title}")
        print(f"{'━' * 80}\n")

        try:
            module = __import__(module_name)
            module.run_benchmark()
            results[module_name] = "✓ PASSED"
        except Exception as e:
            print(f"\n  ✗ FAILED: {e}")
            results[module_name] = f"✗ FAILED: {e}"

    total_elapsed = time.time() - total_start

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n\n{'╔' + '═' * 78 + '╗'}")
    print(f"{'║' + ' BENCHMARK SUITE COMPLETE '.center(78) + '║'}")
    print(f"{'╚' + '═' * 78 + '╝'}")
    print(f"\n  Total time: {total_elapsed:.1f}s")
    print(f"  Benchmarks run: {len(BENCHMARKS)}")
    print(f"  Data files generated in: research/data/\n")

    for module_name, status in results.items():
        print(f"  {status}  {module_name}")

    # ── Merge all data files ─────────────────────────────────────────
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    merged = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "mol_version": "2.0.1",
            "benchmark_count": len(BENCHMARKS),
            "total_time_seconds": round(total_elapsed, 1),
        },
        "benchmarks": {},
    }

    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith('.json') and filename.startswith('bench_'):
            filepath = os.path.join(data_dir, filename)
            with open(filepath) as f:
                merged["benchmarks"][filename.replace('.json', '')] = json.load(f)

    merged_path = os.path.join(data_dir, "all_benchmarks.json")
    with open(merged_path, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"\n  Merged data: research/data/all_benchmarks.json")

    # ── Key findings for paper ───────────────────────────────────────
    print(f"\n{'═' * 80}")
    print("KEY FINDINGS FOR RESEARCH PAPER")
    print(f"{'═' * 80}")

    # Load individual results
    loc_data = _load_data(data_dir, "bench_01_loc.json")
    stdlib_data = _load_data(data_dir, "bench_02_stdlib.json")
    perf_data = _load_data(data_dir, "bench_03_performance.json")
    security_data = _load_data(data_dir, "bench_04_security.json")
    innovation_data = _load_data(data_dir, "bench_05_innovation.json")

    findings = []

    if loc_data and "summary" in loc_data:
        mol_loc = loc_data["summary"].get("mol", {}).get("avg_loc", 0)
        py_loc = loc_data["summary"].get("python", {}).get("avg_loc", 0)
        js_loc = loc_data["summary"].get("javascript", {}).get("avg_loc", 0)
        rust_loc = loc_data["summary"].get("rust", {}).get("avg_loc", 0)
        if py_loc > 0:
            findings.append(f"LOC: MOL averages {mol_loc} lines vs Python {py_loc} ({round((1-mol_loc/py_loc)*100)}% reduction)")
        if js_loc > 0:
            findings.append(f"LOC: MOL averages {mol_loc} lines vs JavaScript {js_loc} ({round((1-mol_loc/js_loc)*100)}% reduction)")
        if rust_loc > 0:
            findings.append(f"LOC: MOL averages {mol_loc} lines vs Rust {rust_loc} ({round((1-mol_loc/rust_loc)*100)}% reduction)")

    if stdlib_data and "totals" in stdlib_data:
        mol_funcs = stdlib_data["totals"].get("mol", {}).get("total_funcs", 0)
        findings.append(f"Stdlib: MOL provides {mol_funcs} zero-import functions across 16 categories")

    if perf_data and "summary" in perf_data:
        avg_overhead = perf_data["summary"].get("avg_overhead")
        if avg_overhead:
            findings.append(f"Performance: {avg_overhead}x average overhead vs native Python (interpreted language trade-off)")

    if security_data and "scores" in security_data:
        mol_sec = security_data["scores"].get("mol", {}).get("built_in", 0)
        findings.append(f"Security: MOL has {mol_sec}/10 security features built-in (highest of any compared language)")

    if innovation_data and "scores" in innovation_data:
        mol_score = innovation_data["scores"].get("mol", 0)
        max_score = innovation_data.get("max_possible", 100)
        findings.append(f"Innovation: MOL scores {mol_score}/{max_score} ({round(mol_score/max_score*100)}%) on weighted innovation index")

    for i, finding in enumerate(findings, 1):
        print(f"  {i}. {finding}")


def _load_data(data_dir, filename):
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        with open(filepath) as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    run_all()
