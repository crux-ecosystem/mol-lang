"""
Benchmark 03: Execution Performance — MOL vs Python
=====================================================
Measures actual execution time for equivalent programs.
MOL runs on a Python interpreter, so this tests interpreter overhead
and demonstrates where MOL's design choices trade off.

Key insight: MOL is NOT competing on raw speed — it competes on
developer productivity, pipeline visibility, and domain-specific power.
This benchmark is honest about that trade-off.
"""

import time
import json
import os
import io
import sys
from contextlib import redirect_stdout

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from mol.parser import parse
from mol.interpreter import Interpreter


def time_mol(code: str, iterations: int = 100) -> dict:
    """Time MOL code execution over multiple iterations."""
    ast = parse(code)
    times = []
    for _ in range(iterations):
        buf = io.StringIO()
        interp = Interpreter(trace=False, sandbox=False)
        start = time.perf_counter()
        with redirect_stdout(buf):
            interp.run(ast)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # ms
    return {
        "mean_ms": round(sum(times) / len(times), 3),
        "min_ms": round(min(times), 3),
        "max_ms": round(max(times), 3),
        "median_ms": round(sorted(times)[len(times) // 2], 3),
        "iterations": iterations,
    }


def time_python(code: str, iterations: int = 100) -> dict:
    """Time equivalent Python code execution."""
    compiled = compile(code, "<benchmark>", "exec")
    times = []
    for _ in range(iterations):
        buf = io.StringIO()
        start = time.perf_counter()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            exec(compiled, {"__builtins__": __builtins__})
        finally:
            sys.stdout = old_stdout
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)
    return {
        "mean_ms": round(sum(times) / len(times), 3),
        "min_ms": round(min(times), 3),
        "max_ms": round(max(times), 3),
        "median_ms": round(sorted(times)[len(times) // 2], 3),
        "iterations": iterations,
    }


# ── Test Programs ────────────────────────────────────────────────────────

BENCHMARKS = {
    "arithmetic_loop": {
        "description": "Sum numbers 1 to 1000 in a loop",
        "mol": '''let total be 0
for i in range(1000) do
  set total to total + i
end
show to_text(total)''',
        "python": '''total = 0
for i in range(1000):
    total += i
print(total)''',
    },

    "list_pipeline": {
        "description": "Filter + map + reduce on 100-element list",
        "mol": '''let nums be range(100)
let result be nums |> filter(fn(x) -> x % 3 is 0) |> map(fn(x) -> x * x) |> sum
show to_text(result)''',
        "python": '''nums = list(range(100))
result = sum(x * x for x in nums if x % 3 == 0)
print(result)''',
    },

    "string_operations": {
        "description": "String manipulation chain",
        "mol": '''let text be "  Hello World from MOL Language  "
let result be text |> trim |> lower |> split(" ") |> join("-")
show result''',
        "python": '''text = "  Hello World from MOL Language  "
result = "-".join(text.strip().lower().split(" "))
print(result)''',
    },

    "recursive_fibonacci": {
        "description": "Recursive Fibonacci(20)",
        "mol": '''define fib(n)
  if n <= 1 then
    return n
  end
  return fib(n - 1) + fib(n - 2)
end
show to_text(fib(20))''',
        "python": '''def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
print(fib(20))''',
    },

    "map_operations": {
        "description": "Create and access dictionaries",
        "mol": '''let data be {"name": "Alice", "age": 30, "score": 0.95}
show data["name"]
show to_text(data["age"])
show to_text(data["score"])''',
        "python": '''data = {"name": "Alice", "age": 30, "score": 0.95}
print(data["name"])
print(data["age"])
print(data["score"])''',
    },

    "function_calls": {
        "description": "Define and call functions 100 times",
        "mol": '''define square(x)
  return x * x
end

define cube(x)
  return x * x * x
end

let total be 0
for i in range(100) do
  set total to total + square(i) + cube(i)
end
show to_text(total)''',
        "python": '''def square(x):
    return x * x

def cube(x):
    return x * x * x

total = 0
for i in range(100):
    total += square(i) + cube(i)
print(total)''',
    },

    "list_comprehension_equiv": {
        "description": "Build list with functional operations",
        "mol": '''let data be range(50)
let evens be filter(data, fn(x) -> x % 2 is 0)
let squares be map(evens, fn(x) -> x * x)
let big be filter(squares, fn(x) -> x > 100)
show to_text(len(big))''',
        "python": '''data = list(range(50))
evens = [x for x in data if x % 2 == 0]
squares = [x * x for x in evens]
big = [x for x in squares if x > 100]
print(len(big))''',
    },

    "nested_data": {
        "description": "Work with nested data structures",
        "mol": '''let users be [
  {"name": "Alice", "scores": [90, 85, 92]},
  {"name": "Bob", "scores": [78, 82, 88]},
  {"name": "Charlie", "scores": [95, 91, 87]}
]
for user in users do
  let avg be mean(user["scores"])
  show user["name"] + ": " + to_text(avg)
end''',
        "python": '''import statistics
users = [
    {"name": "Alice", "scores": [90, 85, 92]},
    {"name": "Bob", "scores": [78, 82, 88]},
    {"name": "Charlie", "scores": [95, 91, 87]},
]
for user in users:
    avg = statistics.mean(user["scores"])
    print(f"{user['name']}: {avg}")''',
    },
}


def run_benchmark():
    print("=" * 80)
    print("BENCHMARK 03: Execution Performance — MOL vs Python")
    print("=" * 80)
    print("Note: MOL runs on a Python-based interpreter. This measures interpreter")
    print("overhead, NOT the language's theoretical performance ceiling.")
    print("MOL's value is in productivity and visibility, not raw speed.")
    print()

    results = {}
    iters = 50  # Reduced for faster benchmarking

    print(f"{'Test':<26} {'MOL (ms)':>10} {'Python (ms)':>12} {'Overhead':>10} {'Note':>20}")
    print("─" * 80)

    for name, bench in BENCHMARKS.items():
        try:
            mol_result = time_mol(bench["mol"], iterations=iters)
            py_result = time_python(bench["python"], iterations=iters)

            overhead = round(mol_result["mean_ms"] / max(py_result["mean_ms"], 0.001), 1)
            note = ""
            if overhead < 5:
                note = "✓ Low overhead"
            elif overhead < 20:
                note = "~ Acceptable"
            else:
                note = "⚡ Interpreter cost"

            results[name] = {
                "description": bench["description"],
                "mol": mol_result,
                "python": py_result,
                "overhead_factor": overhead,
            }

            print(f"{name:<26} {mol_result['mean_ms']:>10.3f} {py_result['mean_ms']:>12.3f} {overhead:>9}x {note:>20}")

        except Exception as e:
            print(f"{name:<26} ERROR: {e}")
            results[name] = {"error": str(e)}

    # ── Summary ──────────────────────────────────────────────────────
    valid = {k: v for k, v in results.items() if "overhead_factor" in v}
    if valid:
        overheads = [v["overhead_factor"] for v in valid.values()]
        avg_overhead = round(sum(overheads) / len(overheads), 1)
        min_overhead = min(overheads)
        max_overhead = max(overheads)

        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        print(f"  Average overhead:    {avg_overhead}x")
        print(f"  Best case:           {min_overhead}x")
        print(f"  Worst case:          {max_overhead}x")
        print(f"\n  Context: MOL is an interpreted language running on Python.")
        print(f"  The overhead is the cost of the visitor-pattern interpreter.")
        print(f"  MOL's value proposition is NOT raw speed — it's:")
        print(f"    • Auto-tracing: zero-config pipeline observability")
        print(f"    • Domain types: Thought, Memory, Document, Embedding")
        print(f"    • 210 stdlib functions: zero imports for AI/data work")
        print(f"    • Readability: 40-70% fewer lines than equivalent code")
        print(f"    • Safety: guard assertions + sandbox security model")

    # ── Save data ────────────────────────────────────────────────────
    output = {
        "benchmark": "03_execution_performance",
        "note": "MOL runs on Python interpreter — overhead is expected. Value is productivity, not speed.",
        "results": results,
        "summary": {
            "avg_overhead": avg_overhead if valid else None,
            "min_overhead": min_overhead if valid else None,
            "max_overhead": max_overhead if valid else None,
        },
    }
    os.makedirs("../data", exist_ok=True)
    with open("../data/bench_03_performance.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nData saved to research/data/bench_03_performance.json")


if __name__ == "__main__":
    run_benchmark()
