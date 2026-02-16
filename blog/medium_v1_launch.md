# MOL 1.0: Why We Built a Programming Language Where Pipelines Trace Themselves

*By the CruxLabx team*

---

## The Problem

Every AI pipeline looks the same. You load data, chunk it, embed it, store it, retrieve it. And between every step, you add logging:

```python
logger.debug(f"Loaded {len(docs)} documents")
logger.debug(f"Split into {len(chunks)} chunks")
logger.debug(f"Embedded {len(vectors)} vectors")
logger.debug(f"Retrieved {len(results)} results")
```

You're writing the same four characters of actual logic — load, chunk, embed, retrieve — buried in fifty lines of boilerplate. The logging code is longer than the pipeline itself. And when something goes wrong, you still don't know *which* step produced the bad data.

We asked: what if the language itself showed you what happened?

## The Answer: Auto-Tracing Pipes

MOL's pipe operator (`|>`) does something no other language does — it **automatically traces** every step:

```
"data.txt"
  |> load_text
  |> chunk(512)
  |> embed
  |> store("index")
```

Output:
```
┌─ Pipeline Trace ──────────────────────────────────────
│ 0.  input               ─  Text("data.txt")
│ 1.  load_text        0.1ms  → Document(...)
│ 2.  chunk(..)        0.0ms  → List<3 chunks>
│ 3.  embed            0.2ms  → List<3 embeddings>
│ 4.  store(..)        0.1ms  → VectorStore("index")
└─ 4 steps · 0.4ms total ───────────────────────────
```

No logging setup. No debug configuration. No print statements. You write the pipeline, and the language shows you exactly what happened — types, timing, values, everything.

This isn't a library feature. It's built into the parser and interpreter. Any pipe chain with 3 or more stages automatically traces itself. Two stages are considered simple enough to skip.

## Why This Matters

Elixir has `|>`. F# has `|>`. But neither traces automatically. In those languages, if you want to see what flows through a pipe, you still add logging or tap functions manually.

MOL's position: **if you're building a pipeline, you want to see what it does. Always.** Making this opt-out (use `--no-trace`) instead of opt-in is a fundamentally different design philosophy.

## Beyond Pipes: A Complete Language

MOL 1.0 isn't just a pipe operator. It's a complete programming language with:

**143 standard library functions** covering math, statistics, hashing, functional programming, file I/O, HTTP, and concurrency.

**English-like syntax** that reads naturally:

```
let name be "MOL"
set version to 1.0

if name is "MOL" then
  show "Welcome!"
end
```

No curly braces. No semicolons. `show` instead of `print()`. `let x be 10` instead of `x = 10`. `is` instead of `==`.

**Structs with methods:**

```
struct Point do
  x, y
end

impl Point do
  define distance(other)
    let dx be self.x - other.x
    let dy be self.y - other.y
    return sqrt(dx * dx + dy * dy)
  end
end
```

**Pattern matching:**

```
let tier be match score with
  | n when n >= 90 -> "Gold"
  | n when n >= 70 -> "Silver"
  | _ -> "Bronze"
end
```

**Concurrency:**

```
let t1 be spawn do
  fetch("https://api.example.com/data")
end

let t2 be spawn do
  read_file("local_data.txt")
end

let results be wait_all([t1, t2])
```

**Error handling, generators, modules, a package manager, and more.**

## The Ecosystem

MOL 1.0 ships with a complete ecosystem:

- **PyPI**: `pip install mol-lang`
- **Online playground**: [mol.cruxlabx.in](https://mol.cruxlabx.in) — no installation needed, sandboxed for safety
- **VS Code extension**: Full LSP with autocomplete, hover docs, diagnostics, go-to-definition
- **Transpilation**: Compile `.mol` to Python or JavaScript
- **WASM compilation**: `mol build` generates standalone HTML
- **Docker**: Multi-mode image for run/repl/playground
- **181 tests** covering every language feature

## What's Next

MOL is being developed as part of the IntraMind sovereign AI ecosystem at CruxLabx. Our roadmap includes:

- Real LLM integration (beyond the current simulation)
- Persistent vector store backends
- Visual pipeline debugger
- Community-contributed packages

## Try It

```bash
pip install mol-lang
mol repl
```

Or visit [mol.cruxlabx.in](https://mol.cruxlabx.in) to try it in your browser.

GitHub: [github.com/crux-ecosystem/mol-lang](https://github.com/crux-ecosystem/mol-lang)

---

*MOL is built by CruxLabx. If you believe in making AI pipelines visible by default, star the repo and join the community.*
