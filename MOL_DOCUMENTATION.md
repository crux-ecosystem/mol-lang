<p align="center">
  <br>
  <strong style="font-size: 3em;">MOL</strong>
  <br>
  <em>The Cognitive Programming Language</em>
  <br><br>
  <img src="https://img.shields.io/badge/version-0.3.0-blue" alt="version">
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="license">
  <img src="https://img.shields.io/badge/python-3.10%2B-green" alt="python">
  <img src="https://img.shields.io/badge/tests-68%20passed-brightgreen" alt="tests">
  <img src="https://img.shields.io/badge/stdlib-90%2B%20functions-orange" alt="stdlib">
  <br><br>
  Built for <strong>IntraMind</strong> by <strong>CruxLabx</strong>
  <br>
  Author: <strong>Mounesh Kodi</strong>
</p>

---

# Table of Contents

1. [What is MOL?](#1-what-is-mol)
2. [Why MOL Exists](#2-why-mol-exists)
3. [The Killer Feature — `|>` with Auto-Tracing](#3-the-killer-feature---with-auto-tracing)
4. [Installation](#4-installation)
5. [Quick Start](#5-quick-start)
6. [Language Reference](#6-language-reference)
   - 6.1 [Variables & Types](#61-variables--types)
   - 6.2 [Control Flow](#62-control-flow)
   - 6.3 [Functions](#63-functions)
   - 6.4 [Pipeline Operator `|>`](#64-pipeline-operator-)
   - 6.5 [Domain Types](#65-domain-types)
   - 6.6 [Guard Assertions](#66-guard-assertions)
   - 6.7 [Domain Commands](#67-domain-commands)
7. [Standard Library — 90+ Functions](#7-standard-library--90-functions)
8. [CLI Reference](#8-cli-reference)
9. [Transpilation](#9-transpilation)
10. [VS Code Extension](#10-vs-code-extension)
11. [Complete Examples](#11-complete-examples)
12. [Architecture](#12-architecture)
13. [Version History](#13-version-history)
14. [Roadmap](#14-roadmap)

---

# 1. What is MOL?

**MOL** (Mind-Oriented Language) is the first programming language with **native pipeline operators and auto-tracing** — purpose-built for AI/RAG pipelines, cognitive computing, and data processing.

MOL is designed around three principles:

- **Pipelines are first-class** — the `|>` operator makes data flow visible, traceable, and debuggable
- **AI types are built-in** — `Document`, `Chunk`, `Embedding`, `VectorStore`, `Thought`, `Memory` are native
- **Safety is mandatory** — `guard` assertions, `access` control, and type enforcement at the language level

MOL runs on Python, transpiles to Python and JavaScript, and ships with a VS Code extension.

---

# 2. Why MOL Exists

Every AI pipeline today is glue code — Python scripts stitching together LangChain, LlamaIndex, vector DBs, and LLMs with **zero visibility** into what happens between steps.

| Problem | Python / JS | MOL |
|---|---|---|
| **Pipeline Debugging** | Add `print()` everywhere | `\|>` auto-traces every step — timing, types, values |
| **Data Flow Visibility** | No native pipe operator | `\|>` makes data flow left-to-right |
| **Type Safety for AI** | Generic dicts, no domain types | First-class: `Thought`, `Memory`, `Document`, `Embedding` |
| **RAG Boilerplate** | 50+ lines of setup code | `doc \|> chunk(512) \|> embed \|> store("index")` |
| **Safety Rails** | Hope for the best | `guard` assertions + `access` control |
| **Portability** | Rewrite per language | Transpiles to Python and JavaScript |

### Comparison with Other Languages

| Language | Pipe Operator | Auto-Tracing | AI Domain Types | RAG Built-in |
|---|---|---|---|---|
| Python | ✗ | ✗ | ✗ | ✗ |
| Elixir | `\|>` | ✗ | ✗ | ✗ |
| F# | `\|>` | ✗ | ✗ | ✗ |
| Rust | ✗ | ✗ | ✗ | ✗ |
| **MOL** | **`\|>`** | **✓** | **✓** | **✓** |

**No other language has this combination.**

---

# 3. The Killer Feature — `|>` with Auto-Tracing

When a pipe chain has **3 or more stages**, MOL automatically prints a full trace — every step **timed, typed, and displayed**:

```mol
let doc be Document("notes.txt", "MOL is built for IntraMind pipelines.")

let index be doc |> chunk(30) |> embed |> store("my_index")
```

**Output:**
```
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  <Document:a3f2 "notes.txt" 39B>
  │ 1.  chunk(..)           0.1ms  → List<2 Chunks>
  │ 2.  embed               0.2ms  → List<2 Embeddings>
  │ 3.  store(..)           0.0ms  → <VectorStore:b7c1 "my_index" 2 vectors>
  └─ 3 steps · 0.3ms total ───────────────────────────
<VectorStore:b7c1 "my_index" 2 vectors>
```

**Zero configuration. Zero setup. Every step tracked automatically.**

Disable with `--no-trace`:
```bash
mol run program.mol --no-trace
```

---

# 4. Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Install from Source

```bash
git clone https://github.com/crux-ecosystem/MOL.git
cd MOL
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify Installation

```bash
mol version
# MOL v0.3.0
```

### VS Code Extension

```bash
cp -r mol-vscode/ ~/.vscode/extensions/mol-language-0.3.0
# Restart VS Code
```

---

# 5. Quick Start

### Hello World

```mol
show "Hello from MOL!"
```

```bash
mol run hello.mol
```

### Variables

```mol
let name be "IntraMind"
let score be 42
let active be true
let items be [1, 2, 3]
let config be {"key": "value", "count": 10}
```

### Pipe a Value Through Functions

```mol
"  HELLO WORLD  " |> trim |> lower |> split(" ")
```

### A Full RAG Pipeline in One Expression

```mol
let doc be Document("kb.txt", "Machine learning enables computers to learn.")

doc |> chunk(50) |> embed |> store("knowledge")

let results be retrieve("What is ML?", "knowledge", 3)
let answer be results |> think("answer the query")

guard answer.confidence > 0.5 : "Low confidence"
show answer.content
```

---

# 6. Language Reference

## 6.1 Variables & Types

### Declaration
```mol
let name be "IntraMind"         -- type inferred
let count be 42
let flag be true
let nothing be null
```

### Typed Declarations
```mol
let x : Number be 10            -- type enforced at declaration
let msg : Text be "hello"
let active : Bool be true
```

Type mismatch throws `MOLTypeError`:
```mol
let x : Number be "hello"       -- 🚫 MOLTypeError
```

### Reassignment
```mol
set count to count + 1
```

### Supported Types

| Type | Examples |
|---|---|
| `Number` | `42`, `3.14`, `-7` |
| `Text` | `"hello"`, `"multi word"` |
| `Bool` | `true`, `false` |
| `null` | `null` |
| `List` | `[1, 2, 3]`, `["a", "b"]` |
| `Map` | `{"key": "value"}` |
| `Thought` | `Thought("idea", 0.9)` |
| `Memory` | `Memory("key", value)` |
| `Node` | `Node("label", 0.5)` |
| `Stream` | `Stream("feed")` |
| `Document` | `Document("file.txt", "content")` |
| `Chunk` | `Chunk("text", 0, "source")` |
| `Embedding` | `Embedding("text", "model")` |
| `VectorStore` | Created via `store()` |

### Operators

| Category | Operators |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `is`, `is not`, `>`, `<`, `>=`, `<=` |
| Logical | `and`, `or`, `not` |
| Pipeline | `\|>` |
| Access | `.field`, `[index]`, `.method()` |
| Comments | `-- comment` |

---

## 6.2 Control Flow

### If / Elif / Else
```mol
if score > 90 then
  show "excellent"
elif score > 70 then
  show "good"
else
  show "needs work"
end
```

### While Loop
```mol
let i be 0
while i < 5 do
  show to_text(i)
  set i to i + 1
end
```

### For Loop
```mol
for item in range(5) do
  show to_text(item)
end

let fruits be ["apple", "banana", "cherry"]
for fruit in fruits do
  show fruit
end
```

---

## 6.3 Functions

### Define and Call
```mol
define greet(name)
  return "Hello, " + name + "!"
end

show greet("Mounesh")    -- "Hello, Mounesh!"
```

### Recursion
```mol
define factorial(n)
  if n <= 1 then
    return 1
  end
  return n * factorial(n - 1)
end

show factorial(10)       -- 3628800
```

### Pipeline Definitions
Named, reusable pipelines:
```mol
pipeline preprocess(data)
  return data |> trim |> lower
end

let clean be "  RAW INPUT  " |> preprocess
show clean               -- "raw input"
```

### Functions as First-Class Values (v0.3.0)
User-defined functions can be passed to `map`, `filter`, `reduce`:
```mol
define double(x)
  return x * 2
end

let result be map([1, 2, 3], double)
show result              -- [2, 4, 6]
```

---

## 6.4 Pipeline Operator `|>`

Data flows **left → right** through functions:

```mol
-- Single stage
"hello" |> upper                     -- "HELLO"

-- With arguments
"a,b,c" |> split(",")               -- ["a", "b", "c"]

-- Multi-stage chain (auto-traced at 3+ stages)
"  HELLO  " |> trim |> lower |> split(" ")

-- With custom functions
define double(x)
  return x * 2
end
5 |> double |> to_text               -- "10"
```

### Auto-Tracing Output (3+ stages)
```
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  Text("  HELLO  ")
  │ 1.  trim                0.0ms  → Text("HELLO")
  │ 2.  lower               0.0ms  → Text("hello")
  │ 3.  split(..)           0.0ms  → List<1 strs>
  └─ 3 steps · 0.0ms total ───────────────────────────
```

---

## 6.5 Domain Types

### Core Types

| Type | Purpose | Constructor | Key Fields |
|---|---|---|---|
| **Thought** | Cognitive unit | `Thought("idea", 0.9)` | `content`, `confidence`, `tags`, `linked_thoughts` |
| **Memory** | Key-value with decay | `Memory("key", value)` | `key`, `value`, `strength`, `recall_count` |
| **Node** | Neural graph vertex | `Node("label", 0.5)` | `label`, `weight`, `connections`, `active`, `generation` |
| **Stream** | Real-time data buffer | `Stream("feed")` | `name`, `buffer`, `subscribers` |

### RAG Types

| Type | Purpose | Constructor | Key Fields |
|---|---|---|---|
| **Document** | Text document | `Document("file.txt", "content")` | `source`, `content`, `metadata` |
| **Chunk** | Text fragment | `Chunk("text", 0, "source")` | `content`, `index`, `source` |
| **Embedding** | 64-dim vector | `Embedding("text", "model")` | `text`, `model`, `dimensions`, `vector` |
| **VectorStore** | Vector index | Created via `store()` | `name`, `entries[]` with `search()` |

### Field and Method Access
```mol
let t be Thought("deep learning", 0.95)
show t.content           -- "deep learning"
show t.confidence         -- 0.95
t.tag("AI", "ML")
t.link(Thought("neural nets", 0.8))
```

---

## 6.6 Guard Assertions

Inline safety checks — halt execution on failure:

```mol
guard confidence > 0.8 : "Confidence too low"
guard len(data) > 0 : "Empty dataset"
guard answer |> assert_not_null
```

Throws `MOLGuardError` on failure.

---

## 6.7 Domain Commands

```mol
trigger "event_name"               -- Fire an event
listen "event_name" do ... end     -- Listen for events
link nodeA to nodeB                -- Connect graph nodes
process node with 0.3              -- Activate & adjust weight
evolve node                        -- Next generation
access "mind_core"                 -- Request resource (security-checked)
sync stream                        -- Synchronize data
emit "data"                        -- Emit to stream
```

### Access Control
```mol
access "mind_core"       -- ✅ Allowed
access "memory_bank"     -- ✅ Allowed
access "secret_vault"    -- 🔒 DENIED — MOLSecurityError
```

Default allowed resources: `mind_core`, `memory_bank`, `node_graph`, `data_stream`, `thought_pool`.

---

# 7. Standard Library — 90+ Functions

## General

| Function | Signature | Description |
|---|---|---|
| `len` | `len(x)` | Length of list, text, or map |
| `type_of` | `type_of(x)` | Return type name as text |
| `to_text` | `to_text(x)` | Convert to text |
| `to_number` | `to_number(x)` | Convert to number |
| `range` | `range(n)` | List from 0 to n-1 |
| `abs` | `abs(x)` | Absolute value |
| `round` | `round(x)` | Round to nearest integer |
| `sqrt` | `sqrt(x)` | Square root |
| `max` | `max(list)` | Maximum value |
| `min` | `min(list)` | Minimum value |
| `sum` | `sum(list)` | Sum of list |
| `print` | `print(x)` | Print to stdout |

## Functional Programming (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `map` | `map(list, fn)` | Apply function to each element |
| `filter` | `filter(list, fn)` | Keep elements where fn returns true |
| `reduce` | `reduce(list, fn, init)` | Fold list into single value |
| `flatten` | `flatten(list)` | Flatten nested lists |
| `unique` | `unique(list)` | Remove duplicates |
| `zip` | `zip(a, b)` | Pair elements from two lists |
| `enumerate` | `enumerate(list)` | List of [index, value] pairs |
| `count` | `count(list, value)` | Count occurrences of value |
| `find` | `find(list, fn)` | First element matching fn |
| `find_index` | `find_index(list, value)` | Index of first occurrence |
| `take` | `take(list, n)` | First n elements |
| `drop` | `drop(list, n)` | All except first n elements |
| `group_by` | `group_by(list, fn)` | Group elements by function result |
| `chunk_list` | `chunk_list(list, n)` | Split into chunks of size n |
| `every` | `every(list, fn)` | True if fn true for all elements |
| `some` | `some(list, fn)` | True if fn true for any element |

## Math (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `floor` | `floor(x)` | Round down |
| `ceil` | `ceil(x)` | Round up |
| `log` | `log(x)` | Natural logarithm |
| `sin` | `sin(x)` | Sine |
| `cos` | `cos(x)` | Cosine |
| `tan` | `tan(x)` | Tangent |
| `pi` | `pi()` | π (3.14159...) |
| `e` | `e()` | Euler's number (2.71828...) |
| `pow` | `pow(base, exp)` | Exponentiation |
| `clamp` | `clamp(x, lo, hi)` | Clamp value to range |
| `lerp` | `lerp(a, b, t)` | Linear interpolation |

## Statistics (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `mean` | `mean(list)` | Arithmetic mean |
| `median` | `median(list)` | Median value |
| `stdev` | `stdev(list)` | Standard deviation |
| `variance` | `variance(list)` | Variance |
| `percentile` | `percentile(list, p)` | p-th percentile |

## Collections

| Function | Signature | Description |
|---|---|---|
| `sort` | `sort(list)` | Sort ascending |
| `sort_by` | `sort_by(list, fn)` | Sort by function result |
| `sort_desc` | `sort_desc(list)` | Sort descending |
| `binary_search` | `binary_search(list, target)` | Binary search (returns index or -1) |
| `reverse` | `reverse(list)` | Reverse list |
| `push` | `push(list, item)` | Append item |
| `pop` | `pop(list)` | Remove last item |
| `keys` | `keys(map)` | Map keys |
| `values` | `values(map)` | Map values |
| `contains` | `contains(list, item)` | Check if item exists |
| `join` | `join(list, sep)` | Join with separator |
| `slice` | `slice(list, start, end)` | Sublist |

## Strings

| Function | Signature | Description |
|---|---|---|
| `split` | `split(text, sep)` | Split text |
| `upper` | `upper(text)` | Uppercase |
| `lower` | `lower(text)` | Lowercase |
| `trim` | `trim(text)` | Remove whitespace |
| `replace` | `replace(text, old, new)` | Replace substring |
| `starts_with` | `starts_with(text, prefix)` | Check prefix |
| `ends_with` | `ends_with(text, suffix)` | Check suffix |
| `pad_left` | `pad_left(text, width, char)` | Left-pad |
| `pad_right` | `pad_right(text, width, char)` | Right-pad |
| `repeat` | `repeat(text, n)` | Repeat text n times |
| `char_at` | `char_at(text, index)` | Character at index |
| `index_of` | `index_of(text, sub)` | Position of substring |
| `format` | `format(template, args...)` | Template formatting `{}` |

## Hashing & Encoding (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `hash` | `hash(text, algo)` | Hash (sha256, md5, sha1, sha512) |
| `uuid` | `uuid()` | Generate UUID v4 |
| `base64_encode` | `base64_encode(text)` | Encode to Base64 |
| `base64_decode` | `base64_decode(text)` | Decode from Base64 |

## Random (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `random` | `random()` | Random float 0.0–1.0 |
| `random_int` | `random_int(min, max)` | Random integer in range |
| `shuffle` | `shuffle(list)` | Shuffled copy |
| `sample` | `sample(list, n)` | Random n elements |
| `choice` | `choice(list)` | Random single element |

## Map Utilities (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `merge` | `merge(map1, map2)` | Merge two maps |
| `pick` | `pick(map, keys)` | Pick specific keys |
| `omit` | `omit(map, keys)` | Omit specific keys |

## Type Checks (v0.3.0)

| Function | Signature | Description |
|---|---|---|
| `is_null` | `is_null(x)` | True if null |
| `is_number` | `is_number(x)` | True if number |
| `is_text` | `is_text(x)` | True if text |
| `is_list` | `is_list(x)` | True if list |
| `is_map` | `is_map(x)` | True if map |

## RAG Pipeline

| Function | Signature | Description |
|---|---|---|
| `load_text` | `load_text(path)` | Load text from file |
| `chunk` | `chunk(doc_or_text, size)` | Split into chunks |
| `embed` | `embed(chunks, model?)` | Generate embeddings |
| `store` | `store(embeddings, name)` | Create VectorStore |
| `retrieve` | `retrieve(query, store, k)` | Similarity search |
| `cosine_sim` | `cosine_sim(a, b)` | Cosine similarity |

## Cognitive

| Function | Signature | Description |
|---|---|---|
| `think` | `think(input, prompt)` | Generate Thought |
| `recall` | `recall(query)` | Search Memory |
| `classify` | `classify(text, labels)` | Classify text |
| `summarize` | `summarize(text)` | Summarize text |

## Serialization & Debug

| Function | Signature | Description |
|---|---|---|
| `to_json` | `to_json(x)` | Serialize to JSON |
| `from_json` | `from_json(text)` | Parse JSON |
| `inspect` | `inspect(x)` | Debug representation |
| `display` | `display(x)` | Pretty-print in pipe |
| `tap` | `tap(x)` | Print and pass through (for debugging pipes) |
| `assert_min` | `assert_min(x, threshold)` | Assert minimum value |
| `assert_not_null` | `assert_not_null(x)` | Assert not null |
| `clock` | `clock()` | Current timestamp |
| `wait` | `wait(seconds)` | Sleep |

---

# 8. CLI Reference

```bash
mol run <file.mol>                     # Run a .mol program
mol run <file.mol> --no-trace          # Run without pipeline tracing
mol parse <file.mol>                   # Show AST (debug)
mol transpile <file.mol>               # Transpile to Python
mol transpile <file.mol> -t js         # Transpile to JavaScript
mol repl                               # Interactive REPL
mol version                            # Show version
```

### REPL
- Multi-line input: end a line with `\`
- Exit: type `exit`
- Colored ASCII banner on startup

---

# 9. Transpilation

MOL transpiles to **Python** and **JavaScript** from a single `.mol` source:

```bash
mol transpile program.mol --target python > output.py
mol transpile program.mol --target js > output.js
```

**MOL Source:**
```mol
"hello" |> upper |> split(" ")
```

**Python Output:**
```python
split(upper("hello"), " ")
```

**JavaScript Output:**
```javascript
split(upper("hello"), " ")
```

---

# 10. VS Code Extension

Included in `mol-vscode/`. Features:

- **Syntax highlighting** for all 30 keywords and 90+ built-in functions
- **Auto-closing** brackets, quotes, and `end` blocks
- **Code folding** for `if...end`, `define...end`, `pipeline...end`, `while...end`
- **20+ code snippets** (`let`, `if`, `for`, `define`, `pipeline`, `guard`, `show`, etc.)
- **File association** for `.mol` files

### Install
```bash
cp -r mol-vscode/ ~/.vscode/extensions/mol-language-0.3.0
# Restart VS Code
```

---

# 11. Complete Examples

### Example 1 — Hello World & Basics

```mol
show "Hello, World!"

let name be "IntraMind"
let score : Number be 42

if score > 40 then
  show "Score is excellent!"
end

let fruits be ["apple", "banana", "cherry"]
for fruit in fruits do
  show "  → " + fruit
end

define greet(person)
  show "Hello, " + person + "!"
  return "greeted " + person
end

show greet("Mounesh")
```

### Example 2 — Recursion & Domain Types

```mol
define gcd(a, b)
  if b is 0 then
    return a
  end
  return gcd(b, a % b)
end

show "GCD(48, 18) = " + to_text(gcd(48, 18))

-- Domain types
let thought be Thought("deep learning", 0.95)
let mem be Memory("test_key", "test_value")
let node be Node("test_node", 1.0)

-- Domain operations
link node to Node("target", 0.5)
process node with 0.2
evolve node

-- Events
listen "test_event" do
  show "Event received!"
end
trigger "test_event"
```

### Example 3 — Full RAG Pipeline

```mol
-- 1. Create a document
let doc be Document("kb.txt", "Machine learning is a subset of AI. Deep learning uses neural networks.")

-- 2. Ingest: chunk → embed → store (ONE expression, auto-traced)
let index be doc |> chunk(50) |> embed |> store("knowledge_base")

-- 3. Query with similarity search
let results be retrieve("What is deep learning?", "knowledge_base", 3)

-- 4. Generate answer from context
let answer be results |> think("answer the query")

-- 5. Validate quality
guard answer.confidence > 0.5 : "Answer confidence too low"
show answer.content

-- 6. Reusable pipeline
pipeline rag_query(question)
  let hits be retrieve(question, "knowledge_base", 3)
  let response be hits |> think(question)
  guard response.confidence > 0.4 : "Low confidence"
  return response
end

show rag_query("What is machine learning?")
```

### Example 4 — Data Processing with Algorithms (v0.3.0)

```mol
-- Functional programming
let numbers be [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

define is_even(n)
  return n % 2 is 0
end

define double(x)
  return x * 2
end

let evens be filter(numbers, is_even)
let doubled be map(evens, double)
show doubled                           -- [4, 8, 12, 16, 20]

-- Statistics
show "Mean: " + to_text(mean(numbers))
show "Median: " + to_text(median(numbers))
show "Stdev: " + to_text(stdev(numbers))

-- Hashing
let hashed be hash("IntraMind", "sha256")
show "SHA-256: " + hashed

-- String processing
let greeting be format("Hello, {}! You have {} messages.", "Mounesh", 5)
show greeting

-- Sorting
let sorted be sort_desc(numbers)
let found be binary_search(sort(numbers), 7)
show "Found 7 at index: " + to_text(found)

-- Type checks
show is_number(42)                     -- true
show is_text("hello")                  -- true
show is_list([1, 2])                   -- true
```

---

# 12. Architecture

```
                          MOL Architecture

 ┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
 │  .mol file  │ ──▶ │  Lark LALR   │ ──▶ │     AST     │ ──▶ │ Interpreter  │
 │  (source)   │     │  Parser      │     │  (33 node   │     │  (Visitor +  │
 │             │     │              │     │   types)    │     │  Auto-Trace) │
 └─────────────┘     └──────────────┘     └──────┬──────┘     └──────────────┘
                                                 │
                                     ┌───────────┼───────────┐
                                     ▼           ▼           ▼
                               ┌──────────┐ ┌──────────┐ ┌──────────┐
                               │  Python  │ │   JS     │ │  (more)  │
                               │  Output  │ │  Output  │ │          │
                               └──────────┘ └──────────┘ └──────────┘

 Components:
 ───────────
 Parser:      Lark 1.3.1 LALR grammar → 33 AST node types
 Interpreter: Tree-walking visitor with scope stack & closures
 Stdlib:      90+ built-in functions (Python implementations)
 Types:       8 domain types (Thought, Memory, Node, Stream,
              Document, Chunk, Embedding, VectorStore)
 Transpiler:  AST → Python / JavaScript source code
 CLI:         run, parse, transpile, repl, version
 Extension:   TextMate grammar, snippets, folding
```

### Project Structure
```
MOL/
├── mol/                        # Language implementation
│   ├── __init__.py             # Package metadata (v0.3.0)
│   ├── grammar.lark            # Lark EBNF grammar
│   ├── parser.py               # LALR parser + AST transformer
│   ├── ast_nodes.py            # 33 AST node dataclasses
│   ├── interpreter.py          # Visitor-pattern interpreter
│   ├── types.py                # 8 domain types
│   ├── stdlib.py               # 90+ built-in functions
│   ├── transpiler.py           # Python & JS transpiler
│   └── cli.py                  # CLI interface
├── examples/                   # 8 example programs
├── tutorial/                   # 6 tutorial files + cheatsheet
├── tests/test_mol.py           # 68 tests (all passing)
├── mol-vscode/                 # VS Code extension
├── pyproject.toml              # Python project config
├── LANGUAGE_SPEC.md            # Formal language specification
├── CHANGELOG.md                # Version history
└── LICENSE                     # Proprietary license
```

---

# 13. Version History

### v0.3.0 — Universal Algorithms (2026-02-10)
- **42 new stdlib functions** — functional programming (map/filter/reduce), math, statistics, string algorithms, hashing, sorting, random, map utilities, type checks
- User-defined functions are now **first-class callables** — pass to `map`, `filter`, `reduce`
- Total stdlib: **90+ functions**
- Tests: **68 passing** (25 new)

### v0.2.0 — The Pipeline Release (2026-02-09)
- **Pipeline operator `|>`** — data flows left-to-right through functions
- **Auto-tracing** — 3+ stages print timing, types, values automatically
- **`pipeline` keyword** — named, reusable pipelines
- **`guard` statement** — inline assertions with custom messages
- **4 new RAG types** — Document, Chunk, Embedding, VectorStore
- **15 RAG pipeline functions** — chunk, embed, store, retrieve, cosine_sim, think, etc.
- Tests: 21 → 43, Examples: 6 → 8

### v0.1.0 — Initial Release (2026-02-08)
- Lark EBNF grammar with LALR parser
- 30+ AST node types, visitor-pattern interpreter
- 4 domain types: Thought, Memory, Node, Stream
- 30+ stdlib functions
- Safety: access control, type enforcement, events
- CLI: run, parse, transpile (Python + JS), REPL
- VS Code extension with syntax highlighting and snippets
- 21 tests, 6 examples

---

# 14. Roadmap

| Version | Status | Focus |
|---|---|---|
| **v0.1.0** | ✅ Complete | Foundation — grammar, AST, interpreter, domain types, CLI |
| **v0.2.0** | ✅ Complete | Pipeline operator `\|>`, auto-tracing, RAG types, guard |
| **v0.3.0** | ✅ Complete | 42 universal algorithms, 90+ stdlib, callable functions |
| **v0.4.0** | 🔜 Next | Sovereign AI — agent blocks, local model registry, knowledge graph |
| **v0.5.0** | 📋 Planned | Production runtime — async pipelines, real DB integration, HTTP server |
| **v1.0.0** | 🎯 Vision | Full ecosystem — package manager, playground, debugger, cloud deploy |

**Vision:** MOL becomes the **control language** for IntraMind's sovereign AI stack — replacing Python/JS glue code for RAG pipelines with a compile/transpile target for any runtime.

---

<p align="center">
  <br>
  <strong>MOL v0.3.0</strong> — Built for <strong>IntraMind</strong> by <strong>CruxLabx</strong>
  <br>
  Creator: <strong>Mounesh Kodi</strong>
  <br><br>
  <em>© 2026 CruxLabx / IntraMind. All rights reserved.</em>
</p>
