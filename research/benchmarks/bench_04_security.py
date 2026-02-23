"""
Benchmark 04: Security Feature Comparison
===========================================
Compares built-in security features across languages.
This is a qualitative + quantitative assessment.
"""

import json
import os

# ── Security Feature Matrix ──────────────────────────────────────────────

SECURITY_FEATURES = {
    "Sandbox Mode": {
        "description": "Built-in sandbox that blocks dangerous operations",
        "mol":        {"supported": True,  "built_in": True,  "detail": "26 dangerous functions blocked, dunder access blocked, 5s timeout, rate limiting"},
        "python":     {"supported": False, "built_in": False, "detail": "No built-in sandbox. RestrictedPython is a third-party option with known bypasses"},
        "javascript": {"supported": True,  "built_in": False, "detail": "vm2 module (deprecated due to escapes), isolated-vm for V8 isolation"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "BEAM VM provides process isolation, but no function-level blocking"},
        "rust":       {"supported": False, "built_in": False, "detail": "No built-in sandbox. WASM sandboxing via wasmtime is an option"},
    },
    "Guard Assertions": {
        "description": "Language-level assertions with custom error messages",
        "mol":        {"supported": True,  "built_in": True,  "detail": "guard condition : 'message' — language keyword, not a function"},
        "python":     {"supported": True,  "built_in": True,  "detail": "assert statement — but can be disabled with -O flag"},
        "javascript": {"supported": False, "built_in": False, "detail": "No assert keyword. console.assert doesn't throw. Need if-throw pattern"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "Guard clauses on function definitions — pattern-matching based"},
        "rust":       {"supported": True,  "built_in": True,  "detail": "assert!, debug_assert! macros — debug_assert disabled in release"},
    },
    "Access Control": {
        "description": "Built-in access control at the language level",
        "mol":        {"supported": True,  "built_in": True,  "detail": "access(level) keyword — restrict API/function access by trust level"},
        "python":     {"supported": False, "built_in": False, "detail": "No access control. Convention-based (underscore prefix)"},
        "javascript": {"supported": True,  "built_in": True,  "detail": "Private fields (#field) in classes (ES2022)"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "Module attribute @moduledoc false, defp for private functions"},
        "rust":       {"supported": True,  "built_in": True,  "detail": "pub/pub(crate)/private visibility modifiers"},
    },
    "Memory Safety": {
        "description": "Protection against memory-related vulnerabilities",
        "mol":        {"supported": True,  "built_in": True,  "detail": "Borrow checker with ownership model (own/borrow/transfer/release), use-after-free detection"},
        "python":     {"supported": True,  "built_in": True,  "detail": "Garbage collected — no manual memory management"},
        "javascript": {"supported": True,  "built_in": True,  "detail": "Garbage collected — no manual memory management"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "BEAM VM manages memory — immutable data, no pointers"},
        "rust":       {"supported": True,  "built_in": True,  "detail": "Borrow checker — compile-time ownership verification"},
    },
    "Dunder/Internal Attribute Blocking": {
        "description": "Prevent access to language internals (__class__, __globals__, etc.)",
        "mol":        {"supported": True,  "built_in": True,  "detail": "All __-prefixed attribute/method access blocked (MOLSecurityError)"},
        "python":     {"supported": False, "built_in": False, "detail": "No blocking — __class__.__subclasses__() fully accessible, known RCE vector"},
        "javascript": {"supported": True,  "built_in": True,  "detail": "Prototype access restricted in strict mode, but not fully blocked"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "No class hierarchy to traverse — BEAM architecture"},
        "rust":       {"supported": True,  "built_in": True,  "detail": "No runtime reflection — compiled language with no class hierarchy"},
    },
    "Type Safety": {
        "description": "Type checking to prevent type-related bugs",
        "mol":        {"supported": True,  "built_in": True,  "detail": "Optional type annotations: let x: Number be 42 — checked at assignment"},
        "python":     {"supported": True,  "built_in": False, "detail": "Type hints are optional and not enforced at runtime (need mypy)"},
        "javascript": {"supported": False, "built_in": False, "detail": "No type system. Need TypeScript (separate language)"},
        "elixir":     {"supported": True,  "built_in": False, "detail": "Typespecs with @spec — checked by Dialyzer (external tool)"},
        "rust":       {"supported": True,  "built_in": True,  "detail": "Strong static type system — compile-time enforcement"},
    },
    "Execution Timeout": {
        "description": "Built-in execution timeout to prevent DoS",
        "mol":        {"supported": True,  "built_in": True,  "detail": "Configurable timeout (default 5s in sandbox) via threading"},
        "python":     {"supported": False, "built_in": False, "detail": "No built-in timeout. Need signal.alarm or threading"},
        "javascript": {"supported": False, "built_in": False, "detail": "No built-in timeout. Event loop prevents sync blocking"},
        "elixir":     {"supported": True,  "built_in": True,  "detail": "Task.await with timeout, process kill after deadline"},
        "rust":       {"supported": False, "built_in": False, "detail": "No built-in timeout. Need tokio::time::timeout"},
    },
    "Rate Limiting": {
        "description": "Built-in rate limiting for API/playground use",
        "mol":        {"supported": True,  "built_in": True,  "detail": "30 req/min per IP in playground, configurable"},
        "python":     {"supported": False, "built_in": False, "detail": "Need Flask-Limiter, Django-Ratelimit, etc."},
        "javascript": {"supported": False, "built_in": False, "detail": "Need express-rate-limit or similar"},
        "elixir":     {"supported": False, "built_in": False, "detail": "Need Hammer or PlugAttack library"},
        "rust":       {"supported": False, "built_in": False, "detail": "Need tower-ratelimit or governor crate"},
    },
    "Homomorphic Encryption": {
        "description": "Compute on encrypted data without decryption",
        "mol":        {"supported": True,  "built_in": True,  "detail": "Paillier scheme: he_encrypt, he_add, he_mul_scalar — zero imports"},
        "python":     {"supported": False, "built_in": False, "detail": "Need python-paillier or tenseal library"},
        "javascript": {"supported": False, "built_in": False, "detail": "Need node-seal or paillier-js"},
        "elixir":     {"supported": False, "built_in": False, "detail": "No HE library available"},
        "rust":       {"supported": False, "built_in": False, "detail": "Need concrete or tfhe crate"},
    },
    "Zero-Knowledge Proofs": {
        "description": "Prove knowledge without revealing the value",
        "mol":        {"supported": True,  "built_in": True,  "detail": "zk_commit, zk_verify, zk_prove — commitment-based proofs"},
        "python":     {"supported": False, "built_in": False, "detail": "Need py-ecc or custom implementation"},
        "javascript": {"supported": False, "built_in": False, "detail": "Need snarkjs or circomlibjs"},
        "elixir":     {"supported": False, "built_in": False, "detail": "No ZKP library available"},
        "rust":       {"supported": False, "built_in": False, "detail": "Need bellman or arkworks crate"},
    },
}


def run_benchmark():
    languages = ["mol", "python", "javascript", "elixir", "rust"]

    print("=" * 90)
    print("BENCHMARK 04: Security Feature Comparison")
    print("=" * 90)

    # ── Feature matrix ───────────────────────────────────────────────
    print(f"\n{'Feature':<36} ", end="")
    for lang in languages:
        print(f"{lang:>12}", end="")
    print()
    print("─" * 96)

    scores = {lang: {"supported": 0, "built_in": 0, "total": 0} for lang in languages}
    feature_data = {}

    for feat_name, feat in SECURITY_FEATURES.items():
        print(f"{feat_name:<36} ", end="")
        feat_row = {}
        for lang in languages:
            info = feat.get(lang, {"supported": False, "built_in": False})
            if info["supported"] and info["built_in"]:
                marker = "● built-in"
                scores[lang]["built_in"] += 1
                scores[lang]["supported"] += 1
            elif info["supported"]:
                marker = "○ external"
                scores[lang]["supported"] += 1
            else:
                marker = "✗ none"
            scores[lang]["total"] += 1
            print(f"{marker:>12}", end="")
            feat_row[lang] = {"supported": info["supported"], "built_in": info["built_in"]}
        print()
        feature_data[feat_name] = feat_row

    # ── Scores ───────────────────────────────────────────────────────
    print(f"\n{'=' * 96}")
    print("SECURITY SCORES")
    print(f"{'=' * 96}")

    total_features = len(SECURITY_FEATURES)
    print(f"\n{'Metric':<36} ", end="")
    for lang in languages:
        print(f"{lang:>12}", end="")
    print()
    print("─" * 96)

    print(f"{'Features supported':<36} ", end="")
    for lang in languages:
        print(f"{scores[lang]['supported']:>10}/{total_features}", end="")
    print()

    print(f"{'Built-in (zero config)':<36} ", end="")
    for lang in languages:
        print(f"{scores[lang]['built_in']:>10}/{total_features}", end="")
    print()

    print(f"{'Security score (built-in %)':<36} ", end="")
    for lang in languages:
        pct = round(scores[lang]["built_in"] / total_features * 100)
        print(f"{pct:>11}%", end="")
    print()

    # ── MOL unique security features ─────────────────────────────────
    print(f"\n{'=' * 96}")
    print("MOL UNIQUE SECURITY ADVANTAGE")
    print(f"{'=' * 96}")

    mol_unique = []
    for feat_name, feat in SECURITY_FEATURES.items():
        mol_info = feat.get("mol", {})
        if mol_info.get("built_in"):
            others_builtin = sum(
                1 for lang in ["python", "javascript", "elixir", "rust"]
                if feat.get(lang, {}).get("built_in", False)
            )
            if others_builtin == 0:
                mol_unique.append((feat_name, mol_info.get("detail", "")))

    print(f"\nFeatures ONLY MOL has built-in (no other language in comparison):")
    for name, detail in mol_unique:
        print(f"  ★ {name}")
        print(f"    └─ {detail}")

    # ── Save data ────────────────────────────────────────────────────
    output = {
        "benchmark": "04_security_features",
        "features": feature_data,
        "scores": scores,
        "mol_unique_features": [name for name, _ in mol_unique],
    }
    os.makedirs("../data", exist_ok=True)
    with open("../data/bench_04_security.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nData saved to research/data/bench_04_security.json")


if __name__ == "__main__":
    run_benchmark()
