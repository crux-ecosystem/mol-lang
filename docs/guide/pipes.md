# Pipe Operator `|>`

The pipe operator is MOL's defining feature — **the only language with `|>` and auto-tracing**.

## Basic Syntax

```text
value |> function
```

The value on the left becomes the **first argument** of the function on the right:

```text
"hello" |> upper       -- same as upper("hello")
"hello" |> upper |> len  -- same as len(upper("hello"))
```

## Why Pipes?

=== "Without pipes"

    ```text
    -- Nested calls: read inside-out
    show len(split(upper(trim("  hello world  ")), " "))
    ```

=== "With pipes"

    ```text
    -- Pipes: read left-to-right
    show "  hello world  " |> trim |> upper |> split(" ") |> len
    ```

Pipes make data flow **visible** and **readable**.

## Extra Arguments

Pass additional arguments after the piped value:

```text
"hello world" |> split(" ")     -- split("hello world", " ")
"hello" |> replace("l", "L")   -- replace("hello", "l", "L")
42 |> add(8)                    -- add(42, 8)
```

## Auto-Tracing

!!! success "The Killer Feature"
    When a pipe chain has **3 or more stages**, MOL automatically prints a trace table showing the input, each stage's execution time, and output type.

```text
let result be "  Hello, IntraMind!  "
  |> trim
  |> lower
  |> split(" ")
```

Output:
```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  Text("  Hello, IntraMind!  ")
  │ 1.  trim                0.0ms  → Text("Hello, IntraMind!")
  │ 2.  lower               0.0ms  → Text("hello, intramind!")
  │ 3.  split(..)           0.0ms  → List<2 strs>
  └─ 3 steps · 0.0ms total ───────────────────────────
```

### Why 3+ Stages?

- **2 stages** = simple transformation, trace would be noise
- **3+ stages** = multi-step pipeline, visibility is valuable

### Disable Tracing

```bash
mol run program.mol --no-trace
```

Or in code, short chains (< 3 stages) never trace:

```text
"hello" |> upper       -- no trace (2 stages)
```

## User Functions in Pipes

Your functions work seamlessly in pipes:

```text
define double(x)
  return x * 2
end

define add_ten(x)
  return x + 10
end

show 5 |> double |> add_ten |> double
```

## Lambdas in Pipes

Use inline functions (`fn(x) -> expr`) directly in pipes — no separate function needed:

```text
let nums be [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

-- Filter, map, reduce — all inline
show nums |>
  filter(fn(x) -> x > 5) |>
  map(fn(x) -> x * 2) |>
  reduce(fn(a, b) -> a + b, 0)
-- 80
```

### Common Pipe Patterns

```text
let data be [10, 20, 30, 40, 50]

-- Get items > 25, doubled
show data |> where(fn(x) -> x > 25) |> select(fn(x) -> x * 2)
-- [60, 80, 100]

-- Find first item > 25
show data |> where(fn(x) -> x > 25) |> first
-- 30

-- Count matching items
show data |> where(fn(x) -> x > 25) |> len
-- 3

-- Sum of filtered items
show data |> where(fn(x) -> x > 25) |> sum_list
-- 120
```

### Working with Objects

```text
let users be [
  {"name": "Alice", "age": 25, "active": true},
  {"name": "Bob", "age": 35, "active": false},
  {"name": "Charlie", "age": 30, "active": true}
]

-- Smart mode: extract properties and filter by truthy fields
show users |> filter("active") |> pluck("name")
-- ["Alice", "Charlie"]

-- Sort by property
show users |> sort_by("age") |> map("name")
-- ["Alice", "Charlie", "Bob"]
```

```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  Number(5)
  │ 1.  double              0.0ms  → Number(10)
  │ 2.  add_ten             0.0ms  → Number(20)
  │ 3.  double              0.0ms  → Number(40)
  └─ 3 steps · 0.0ms total ───────────────────────────
```

## Named Pipelines

Define reusable pipeline blocks:

```text
pipeline clean_text(text)
  let result be text |> trim |> lower
  guard len(result) > 0 : "Empty after cleaning"
  return result
end

-- Use as regular function
show clean_text("  HELLO  ")  -- "hello"

-- Use in pipes
show "  WORLD  " |> clean_text
```

## Real-World: RAG Pipeline

```text
-- Full RAG pipeline in 4 lines
let doc be Document("knowledge.txt", content)
let index be doc |> chunk(512) |> embed("model-v1") |> store("kb")
let answer be retrieve("What is AI?", "kb", 3) |> think("answer")
guard answer.confidence > 0.5 : "Low confidence"
```

## Pipe + Debug

Use `tap` for debugging without breaking the chain:

```text
let result be "hello"
  |> upper
  |> tap("after upper")    -- prints: [after upper] HELLO
  |> split(" ")
```

Use `display` to print and pass through:

```text
let result be 42
  |> double
  |> display          -- prints the value, passes it along
  |> add_ten
```

## How It Works Internally

The pipe operator is parsed as a `PipeChain` AST node. At evaluation time:

1. The first expression is evaluated as the initial value
2. Each subsequent stage receives the previous result as its first argument
3. If stages ≥ 3, a trace buffer records timing and type info for each step
4. After execution, the trace is printed to stderr
5. The final value is returned

This means pipes have **zero overhead** when tracing is disabled — they desugar to nested function calls.
