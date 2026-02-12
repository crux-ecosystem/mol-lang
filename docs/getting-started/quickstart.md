# Quick Start

Get up and running with MOL in 2 minutes.

## Hello World

Create a file `hello.mol`:

```text
show "Hello, World!"
```

Run it:

```bash
mol run hello.mol
```

Output:
```
Hello, World!
```

## Variables

```text
let name be "MOL"
let version be 0.2
let features be ["pipes", "guards", "types"]

show name + " v" + to_text(version)
show "Features: " + join(features, ", ")
```

## Pipe Operator

The killer feature — chain operations with `|>`:

```text
let result be "  Hello World  " |> trim |> upper |> split(" ")
show result
-- Output: ["HELLO", "WORLD"]
```

With 3+ stages, MOL **auto-traces** the pipeline:

```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  Text("  Hello World  ")
  │ 1.  trim                0.0ms  → Text("Hello World")
  │ 2.  upper               0.0ms  → Text("HELLO WORLD")
  │ 3.  split(" ")          0.0ms  → List<2 strs>
  └─ 3 steps · 0.0ms total ───────────────────────────
```

## Functions

```text
fn double(x)
  return x * 2
end

fn add_ten(x)
  return x + 10
end

show 5 |> double |> add_ten |> double
-- Output: 40
```

## REPL

Start an interactive session:

```bash
mol repl
```

```text
MOL v0.2.0 REPL
Type MOL code. Use \ for multi-line. Ctrl+C to exit.
mol> show "hello" |> upper
HELLO
mol> let x be 42
mol> show x * 2
84
```

## Next Steps

- [Variables & Types](../guide/variables.md) — Learn the type system
- [Pipe Operator](../guide/pipes.md) — Master MOL's killer feature
- [Algorithms](../guide/algorithms.md) — Built-in algorithms for everyone
- [RAG Pipeline Tutorial](../tutorials/rag-pipeline.md) — Build your first AI pipeline
