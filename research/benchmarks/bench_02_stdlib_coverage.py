"""
Benchmark 02: Standard Library Coverage & Feature Matrix
=========================================================
Compares what's available out-of-the-box (no imports needed) across languages.
Measures: stdlib function count, domain categories covered, import requirements.
"""

import json
import os

# ── Feature Categories ───────────────────────────────────────────────────
# For each category, we count how many functions are available out-of-the-box
# (without importing external packages).

CATEGORIES = {
    "Math & Arithmetic": {
        "mol":        {"count": 15, "functions": "floor, ceil, log, sin, cos, tan, pow, clamp, lerp, pi, e, abs, min, max, round", "import_needed": False},
        "python":     {"count": 5,  "functions": "abs, min, max, round, pow", "import_needed": True, "note": "Need `import math` for sin/cos/floor/ceil/log"},
        "javascript": {"count": 20, "functions": "Math.floor, Math.ceil, Math.log, Math.sin, etc.", "import_needed": False, "note": "All via Math object"},
        "elixir":     {"count": 3,  "functions": "abs, min, max", "import_needed": True, "note": "Need :math module for trig"},
        "rust":       {"count": 0,  "functions": "None built-in", "import_needed": True, "note": "Need f64::sin() method syntax"},
    },
    "Statistics": {
        "mol":        {"count": 5, "functions": "mean, median, stdev, variance, percentile", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need `import statistics`"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need external library (lodash/simple-statistics)"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need Statistics library"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need statistical crate"},
    },
    "String Operations": {
        "mol":        {"count": 16, "functions": "upper, lower, trim, split, join, replace, contains, starts_with, ends_with, pad_left, pad_right, repeat, char_at, index_of, format, len", "import_needed": False},
        "python":     {"count": 15, "functions": "str methods: upper, lower, strip, split, join, replace, etc.", "import_needed": False},
        "javascript": {"count": 15, "functions": "String methods: toUpperCase, toLowerCase, trim, split, etc.", "import_needed": False},
        "elixir":     {"count": 20, "functions": "String module: upcase, downcase, trim, split, etc.", "import_needed": False},
        "rust":       {"count": 10, "functions": "str methods: to_uppercase, trim, split, etc.", "import_needed": False},
    },
    "List/Array Operations": {
        "mol":        {"count": 22, "functions": "map, filter, reduce, find, every, some, flatten, unique, zip, enumerate, count, take, drop, sort, sort_by, sort_desc, chunk_list, first, last, compact, reject, pluck", "import_needed": False},
        "python":     {"count": 8,  "functions": "map, filter, sorted, len, enumerate, zip, min, max", "import_needed": False, "note": "Some via functools"},
        "javascript": {"count": 15, "functions": "Array methods: map, filter, reduce, find, every, some, etc.", "import_needed": False},
        "elixir":     {"count": 25, "functions": "Enum module: map, filter, reduce, find, etc.", "import_needed": False},
        "rust":       {"count": 15, "functions": "Iterator methods: map, filter, fold, find, etc.", "import_needed": False},
    },
    "Hashing & Encoding": {
        "mol":        {"count": 6, "functions": "hash, uuid, base64_encode, base64_decode, secure_hash, secure_random", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need hashlib, uuid, base64"},
        "javascript": {"count": 1, "functions": "btoa/atob", "import_needed": True, "note": "Need crypto module"},
        "elixir":     {"count": 2, "functions": ":crypto, Base", "import_needed": False},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need sha2, uuid, base64 crates"},
    },
    "File I/O": {
        "mol":        {"count": 8, "functions": "read_file, write_file, append_file, delete_file, file_exists, list_dir, make_dir, file_size", "import_needed": False},
        "python":     {"count": 3, "functions": "open, os.path.exists (need import os)", "import_needed": True},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need fs module"},
        "elixir":     {"count": 5, "functions": "File.read, File.write, File.exists?, etc.", "import_needed": False},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need std::fs"},
    },
    "HTTP/Network": {
        "mol":        {"count": 2, "functions": "fetch, url_encode", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need requests/urllib"},
        "javascript": {"count": 1, "functions": "fetch (browser/Node 18+)", "import_needed": False},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need HTTPoison/Req"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need reqwest crate"},
    },
    "Concurrency": {
        "mol":        {"count": 7, "functions": "channel, send, receive, parallel, race, wait_all, spawn", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need threading/asyncio"},
        "javascript": {"count": 2, "functions": "Promise.all, Promise.race", "import_needed": False},
        "elixir":     {"count": 5, "functions": "spawn, send, receive, Task.async, Task.await", "import_needed": False},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need std::thread or tokio"},
    },
    "JSON Processing": {
        "mol":        {"count": 4, "functions": "to_json, from_json, json_parse, json_stringify", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need import json"},
        "javascript": {"count": 2, "functions": "JSON.parse, JSON.stringify", "import_needed": False},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need Jason library"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need serde_json crate"},
    },
    "AI/ML Domain Types": {
        "mol":        {"count": 8, "functions": "Thought, Memory, Node, Stream, Document, Chunk, Embedding, VectorStore", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need LangChain/custom classes"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need LangChain.js/custom"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "No standard AI types"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "No standard AI types"},
    },
    "RAG Pipeline": {
        "mol":        {"count": 6, "functions": "chunk, embed, store, retrieve, think, recall", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need LangChain (100+ deps)"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need LangChain.js"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "No RAG framework"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "No RAG framework"},
    },
    "Vector Operations": {
        "mol":        {"count": 25, "functions": "vec, vec_dot, vec_cosine, vec_normalize, vec_softmax, vec_relu, vec_quantize, vec_index_search, etc.", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need numpy"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need ml.js or tfjs"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need Nx library"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need ndarray crate"},
    },
    "Encryption": {
        "mol":        {"count": 15, "functions": "crypto_keygen, he_encrypt, he_decrypt, he_add, he_sub, he_mul_scalar, sym_encrypt, sym_decrypt, zk_commit, zk_verify, zk_prove, etc.", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need phe, cryptography"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need node-forge"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need :crypto"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need ring, paillier crates"},
    },
    "Pipeline Operator": {
        "mol":        {"count": 1, "functions": "|> with auto-tracing", "import_needed": False, "note": "Built into language with automatic performance tracing"},
        "python":     {"count": 0, "functions": "None", "import_needed": False, "note": "No pipe operator"},
        "javascript": {"count": 0, "functions": "None", "import_needed": False, "note": "TC39 Stage 2 proposal only"},
        "elixir":     {"count": 1, "functions": "|>", "import_needed": False, "note": "Pipe operator, but NO auto-tracing"},
        "rust":       {"count": 0, "functions": "None", "import_needed": False, "note": "Method chaining only"},
    },
    "Auto-Tracing": {
        "mol":        {"count": 1, "functions": "Built-in: 3+ stage pipes auto-traced with timing", "import_needed": False},
        "python":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need OpenTelemetry/custom decorators"},
        "javascript": {"count": 0, "functions": "None", "import_needed": True, "note": "Need OpenTelemetry"},
        "elixir":     {"count": 0, "functions": "None", "import_needed": True, "note": "Need Telemetry library"},
        "rust":       {"count": 0, "functions": "None", "import_needed": True, "note": "Need tracing crate"},
    },
    "Safety Guards": {
        "mol":        {"count": 2, "functions": "guard, access", "import_needed": False, "note": "Language-level assertions with custom messages"},
        "python":     {"count": 1, "functions": "assert", "import_needed": False},
        "javascript": {"count": 0, "functions": "None", "import_needed": False, "note": "Need if-throw pattern"},
        "elixir":     {"count": 1, "functions": "guard clauses", "import_needed": False},
        "rust":       {"count": 2, "functions": "assert!, debug_assert!", "import_needed": False},
    },
}


def run_benchmark():
    languages = ["mol", "python", "javascript", "elixir", "rust"]

    print("=" * 90)
    print("BENCHMARK 02: Standard Library Coverage & Feature Matrix")
    print("=" * 90)

    # ── Per-category breakdown ───────────────────────────────────────
    totals = {lang: {"total_funcs": 0, "categories_covered": 0, "no_import_needed": 0} for lang in languages}

    print(f"\n{'Category':<26} ", end="")
    for lang in languages:
        print(f"{lang:>12}", end="")
    print()
    print("─" * 86)

    category_data = {}
    for cat_name, cat in CATEGORIES.items():
        print(f"{cat_name:<26} ", end="")
        cat_row = {}
        for lang in languages:
            info = cat.get(lang, {"count": 0, "import_needed": True})
            count = info["count"]
            needs_import = info.get("import_needed", True)
            marker = "✓" if not needs_import else "⬇"
            print(f"{count:>8} {marker:>3}", end="")
            totals[lang]["total_funcs"] += count
            if count > 0:
                totals[lang]["categories_covered"] += 1
            if not needs_import and count > 0:
                totals[lang]["no_import_needed"] += 1
            cat_row[lang] = {"count": count, "import_needed": needs_import}
        print()
        category_data[cat_name] = cat_row

    print("─" * 86)
    print(f"{'✓ = no import needed, ⬇ = requires import/external package'}")

    # ── Totals ───────────────────────────────────────────────────────
    print(f"\n{'=' * 90}")
    print("TOTALS")
    print(f"{'=' * 90}")
    print(f"{'Metric':<35} ", end="")
    for lang in languages:
        print(f"{lang:>10}", end="")
    print()
    print("─" * 86)

    print(f"{'Total built-in functions':<35} ", end="")
    for lang in languages:
        print(f"{totals[lang]['total_funcs']:>10}", end="")
    print()

    print(f"{'Categories covered (out of 16)':<35} ", end="")
    for lang in languages:
        print(f"{totals[lang]['categories_covered']:>10}", end="")
    print()

    print(f"{'Zero-import categories':<35} ", end="")
    for lang in languages:
        print(f"{totals[lang]['no_import_needed']:>10}", end="")
    print()

    # ── MOL advantage ────────────────────────────────────────────────
    print(f"\n{'=' * 90}")
    print("MOL ADVANTAGE: Unique Capabilities")
    print(f"{'=' * 90}")

    unique_to_mol = []
    for cat_name, cat in CATEGORIES.items():
        mol_count = cat.get("mol", {}).get("count", 0)
        others_have = any(
            cat.get(lang, {}).get("count", 0) > 0 and not cat.get(lang, {}).get("import_needed", True)
            for lang in ["python", "javascript", "elixir", "rust"]
        )
        if mol_count > 0 and not others_have:
            unique_to_mol.append(cat_name)

    print(f"\nCategories where MOL has ZERO-IMPORT support and NO other language does:")
    for cat in unique_to_mol:
        mol_info = CATEGORIES[cat]["mol"]
        print(f"  ★ {cat}: {mol_info['count']} functions — {mol_info['functions']}")

    print(f"\n  Total unique advantage categories: {len(unique_to_mol)}/{len(CATEGORIES)}")

    # ── Save data ────────────────────────────────────────────────────
    output = {
        "benchmark": "02_stdlib_coverage",
        "categories": category_data,
        "totals": {lang: totals[lang] for lang in languages},
        "unique_to_mol": unique_to_mol,
    }
    os.makedirs("../data", exist_ok=True)
    with open("../data/bench_02_stdlib.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nData saved to research/data/bench_02_stdlib.json")


if __name__ == "__main__":
    run_benchmark()
