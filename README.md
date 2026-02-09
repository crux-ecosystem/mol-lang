<p align="center">
  <img src="mol-banner.svg" alt="MOL Language" width="600">
</p>

<h1 align="center">MOL — The Cognitive Programming Language</h1>

<p align="center">
  <strong>Built for AI pipelines. Born from <a href="https://github.com/crux-ecosystem">IntraMind</a>.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.10%2B-yellow?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/tests-43%20passing-brightgreen?style=flat-square" alt="tests">
  <img src="https://img.shields.io/badge/pipe_operator-%7C%3E-purple?style=flat-square" alt="pipe">
</p>

<p align="center">
  <a href="#the-problem">Problem</a> •
  <a href="#the-solution">Solution</a> •
  <a href="#see-it-in-action">Demo</a> •
  <a href="#language-at-a-glance">Language</a> •
  <a href="#get-started">Get Started</a> •
  <a href="https://medium.com/@cruxlabx/introducing-mol">Blog Post</a>
</p>

---

## The Problem

Every AI pipeline today looks like this:

```python
# Python: 47 lines of glue code, zero visibility
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import logging

logging.basicConfig(level=logging.DEBUG)  # hope this helps

doc = load_document("knowledge.txt")
splitter = RecursiveCharacterTextSplitter(chunk_size=512)
chunks = splitter.split_documents([doc])
# print(f"DEBUG: {len(chunks)} chunks")  # <-- you'll add 20 of these
embeddings = OpenAIEmbeddings()
vectors = FAISS.from_documents(chunks, embeddings)
results = vectors.similarity_search(query, k=3)
# What happened between steps? Who knows.
```

**No visibility. No tracing. No domain types. Just glue.**

---

## The Solution

The same pipeline in MOL:

```
let index be doc |> chunk(512) |> embed("model-v1") |> store("kb")
let answer be retrieve(query, "kb", 3) |> think("answer this")
guard answer.confidence > 0.5 : "Low confidence"
```

**3 lines. Auto-traced. Type-safe. Done.**

When you run it, MOL automatically shows you what happened:

```
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  <Document "knowledge.txt" 339B>
  │ 1.  chunk(512)          0.1ms  → List<5 Chunks>
  │ 2.  embed("model-v1")   0.2ms  → List<5 Embeddings>
  │ 3.  store("kb")         0.0ms  → <VectorStore "kb" 5 vectors>
  └─ 3 steps · 0.4ms total ───────────────────────────
```

**No print statements. No logging setup. Auto-tracing is built into the language.**

---

## What Makes MOL Different

| Feature | Python | Elixir | F# | **MOL** |
|:---|:---:|:---:|:---:|:---:|
| Pipe operator `\|>` | — | ✓ | ✓ | **✓** |
| **Auto-tracing on pipes** | — | — | — | **✓** |
| AI domain types | — | — | — | **✓** |
| RAG primitives built-in | — | — | — | **✓** |
| Guard assertions | — | ✓ | — | **✓** |
| Transpiles to Python & JS | — | — | — | **✓** |

> **MOL is the only language where `|>` automatically traces execution** — timing, types, and data flow at every stage, with zero configuration.

---

## See It In Action

### Hello World
```
show "Hello, World!"
```

### Variables & Types
```
let name be "IntraMind"
let confidence be 0.95
let tags be ["ai", "rag", "cognitive"]
```

### Pipe Operator with Auto-Tracing
```
-- Every chain of 3+ pipes is automatically traced
let result be "  Hello World  "
  |> trim
  |> upper
  |> split(" ")

-- Output: ["HELLO", "WORLD"]
-- Plus a full trace table showing each step's timing and types
```

### Full RAG Pipeline
```
-- Load → Chunk → Embed → Store (one expression)
let index be Document("data.txt", content)
  |> chunk(512)
  |> embed("model-v1")
  |> store("knowledge_base")

-- Query → Retrieve → Think → Guard
let answer be retrieve("What is AI?", "knowledge_base", 3)
  |> think("answer the question")

guard answer.confidence > 0.5 : "Answer quality too low"
show answer.content
```

### Cognitive Types
```
let idea be Thought("Neural networks learn patterns", 0.87)
let memory be Memory("training_session", idea)
let neuron be Node("cortex", 0.75)

-- Link and evolve neural structures
link neuron to Node("synapse", 0.5)
evolve neuron
```

### Safety & Access Control
```
access "mind_core" with "admin"
guard len(data) > 0 : "Empty dataset"
```

---

## Language at a Glance

```
╔══════════════════════════════════════════════════════╗
║  MOL v0.2.0                                         ║
║                                                      ║
║  Keywords:    let, be, show, if/elif/else/end,       ║
║              for/in/do, while, fn/return,            ║
║              pipeline, guard                         ║
║                                                      ║
║  Operators:   |>  (pipe with auto-trace)             ║
║              +  -  *  /  %  ^                        ║
║              ==  !=  >  <  >=  <=  is                ║
║              and  or  not                            ║
║                                                      ║
║  Types:      Text, Number, Boolean, List, Map        ║
║              Thought, Memory, Node, Signal           ║
║              Document, Chunk, Embedding, VectorStore ║
║                                                      ║
║  Stdlib:     45+ built-in functions                  ║
║  Transpile:  Python & JavaScript                     ║
║  Extension:  VS Code syntax highlighting             ║
╚══════════════════════════════════════════════════════╝
```

---

## Get Started

```bash
# Clone and install
git clone https://github.com/crux-ecosystem/MOL.git
cd MOL
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Run your first program
echo 'show "Hello from MOL!"' > hello.mol
mol run hello.mol

# Run with auto-tracing
mol run examples/08_rag_pipeline.mol

# Run without traces
mol run examples/01_hello.mol --no-trace

# REPL
mol repl

# Transpile to Python
mol transpile my_program.mol --target python
```

---

## Project Status

| Component | Status |
|:---|:---:|
| LALR Parser (Lark) | ✅ Stable |
| Interpreter | ✅ 43 tests passing |
| Pipe `\|>` + Auto-Trace | ✅ Production ready |
| Domain Types (12 types) | ✅ Complete |
| Stdlib (45+ functions) | ✅ Complete |
| Guard Assertions | ✅ Complete |
| Python Transpiler | ✅ Complete |
| JS Transpiler | ✅ Complete |
| VS Code Extension | ✅ Syntax + Snippets |
| Package Manager | 🔜 v0.3.0 |
| LSP Server | 🔜 v0.4.0 |
| WASM Runtime | 🔜 v0.5.0 |

---

## Built By

**[CruxLabx](https://github.com/crux-ecosystem)** — Building the cognitive infrastructure for IntraMind.

MOL is the language layer of IntraMind, a cognitive computing platform that models thinking, memory, and reasoning as first-class computational primitives.

---

<p align="center">
  <strong>MOL: Where pipelines think.</strong>
</p>

<p align="center">
  <a href="https://github.com/crux-ecosystem/MOL">Source</a> •
  <a href="https://github.com/crux-ecosystem/MOL/blob/main/LANGUAGE_SPEC.md">Spec</a> •
  <a href="https://github.com/crux-ecosystem/MOL/blob/main/CHANGELOG.md">Changelog</a> •
  <a href="https://medium.com/@cruxlabx/introducing-mol">Blog</a>
</p>
