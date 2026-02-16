---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# MOL

**The pipeline language for AI, data, and automation — with auto-tracing built in.**

<div class="badge-row">
  <img src="https://img.shields.io/badge/version-1.1.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.12%2B-yellow?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/tests-202%20passing-brightgreen?style=flat-square" alt="tests">
</div>

[Get Started](getting-started/installation.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/crux-ecosystem/mol-lang){ .md-button }

</div>

---

## The Problem

Every pipeline — AI, data, or automation — is invisible glue code. You chain operations together, then add `print()` and logging everywhere to see what happened.

**MOL fixes this at the language level.**

## The Solution

```text
let index be doc |> chunk(512) |> embed("model-v1") |> store("kb")
let answer be retrieve(query, "kb", 3) |> think("answer this")
guard answer.confidence > 0.5 : "Low confidence"
```

Run it, and MOL automatically shows you:

```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  <Document "data.txt" 339B>
  │ 1.  chunk(512)          0.1ms  → List<5 Chunks>
  │ 2.  embed("model-v1")   0.2ms  → List<5 Embeddings>
  │ 3.  store("kb")         0.0ms  → <VectorStore "kb" 5 vectors>
  └─ 3 steps · 0.4ms total ───────────────────────────
```

**No print statements. No logging. Auto-tracing is built into `|>`.**

---

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### :material-pipe: Pipe Operator `|>`

Chain operations left-to-right with automatic execution tracing. Every stage is timed and typed.

```text
"hello" |> upper |> split(" ")
```

</div>

<div class="feature-card" markdown>

### :material-shield-check: Guard Assertions

Runtime validation built into the language. No try/catch boilerplate.

```text
guard confidence > 0.5 : "Too low"
```

</div>

<div class="feature-card" markdown>

### :material-brain: Domain Types

12 built-in types: `Thought`, `Memory`, `Node`, `Document`, `Chunk`, `Embedding`, `VectorStore`, and more.

</div>

<div class="feature-card" markdown>

### :material-function: 162 Stdlib Functions

Math, strings, lists, maps, sorting, searching, JSON, hashing, functional programming, statistics, and RAG operations.

</div>

<div class="feature-card" markdown>

### :material-translate: Transpiler

Write once in MOL, transpile to Python or JavaScript.

```bash
mol transpile app.mol --target python
```

</div>

<div class="feature-card" markdown>

### :material-security: Access Control

Built-in security model for AI resource management.

```text
access "mind_core" with "admin"
```

</div>

</div>

---

## Built For Real Domains

MOL is purpose-built for domains where pipeline visibility and readable code directly reduce debugging time.

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### :material-brain: AI & ML Pipelines

Build RAG pipelines in 3 lines. Every stage auto-traced with timing and type info. Built-in domain types: `Document`, `Chunk`, `Embedding`, `VectorStore`.

```text
doc |> chunk(512) |> embed |> store("kb")
```

</div>

<div class="feature-card" markdown>

### :material-chart-bar: Data Processing & ETL

Smart functions eliminate boilerplate. `filter("active")`, `sort_by("name")`, `pluck("id")` — no lambdas needed for common operations.

```text
sales |> filter("closed") |> sort_by("amount") |> pluck("rep")
```

</div>

<div class="feature-card" markdown>

### :material-server: DevOps & Automation

Log analysis, monitoring, SLA validation with `guard` assertions and built-in statistics (`mean`, `median`, `percentile`).

```text
logs |> pluck("latency") |> percentile(95)
```

</div>

</div>

[See All Use Cases](use-cases.md){ .md-button }

---

## What Makes MOL Different

| Feature | Python | Elixir | F# | **MOL** |
|:---|:---:|:---:|:---:|:---:|
| Pipe operator `\|>` | — | ✓ | ✓ | **✓** |
| **Auto-tracing** | — | — | — | **✓** |
| AI domain types | — | — | — | **✓** |
| RAG built-in | — | — | — | **✓** |
| Guard assertions | — | ✓ | — | **✓** |
| Transpiles to Python & JS | — | — | — | **✓** |
| Built-in algorithms | — | — | — | **✓** |

---

## Built By

**[CruxLabx](https://github.com/crux-ecosystem)** — Building the cognitive infrastructure for IntraMind.

<p style="text-align: center; font-size: 1.2rem; margin-top: 2rem;">
  <strong>MOL: Where pipelines think.</strong>
</p>
