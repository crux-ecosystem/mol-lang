# Your First Program

Let's build a complete MOL program step by step.

## Step 1: A Simple Calculator

Create `calculator.mol`:

```text
-- MOL Calculator

fn add(a, b)
  return a + b
end

fn multiply(a, b)
  return a * b
end

fn square(x)
  return x ^ 2
end

-- Use pipes to chain calculations
let result be 5 |> square |> to_text
show "5 squared = " + result

-- Multi-step pipeline
let answer be 3
  |> add(7)
  |> multiply(2)
  |> square

show "((3 + 7) * 2)² = " + to_text(answer)
```

```bash
mol run calculator.mol
```

```text
5 squared = 25
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  Number(3)
  │ 1.  add(7)              0.0ms  → Number(10)
  │ 2.  multiply(2)         0.0ms  → Number(20)
  │ 3.  square              0.0ms  → Number(400)
  └─ 3 steps · 0.0ms total ───────────────────────────
((3 + 7) * 2)² = 400
```

## Step 2: Working with Data

```text
-- Data processing with MOL

let names be ["Alice", "Bob", "Charlie", "Diana"]
let scores be [85, 92, 78, 95]

-- Find the highest scorer
let best be max(scores)
show "Highest score: " + to_text(best)

-- Process and display
for i in range(len(names)) do
  let name be names[i]
  let score be scores[i]
  show name + ": " + to_text(score)
end

-- Sort and show
let sorted_scores be sort(scores)
show "Sorted: " + to_text(sorted_scores)
```

## Step 3: Using Domain Types

```text
-- Create a thought with confidence
let idea be Thought("Machine learning transforms healthcare", 0.87)
show idea
show "Confidence: " + to_text(idea.confidence)

-- Create a memory
let mem be Memory("research", idea)
show mem

-- Guard the quality
guard idea.confidence > 0.7 : "Idea needs more evidence"
show "Idea is solid!"
```

## Step 4: Pipe Everything Together

```text
-- The MOL way: pipe data through transformations

fn format_name(name)
  return name |> trim |> upper
end

fn greet(name)
  return "Hello, " + name + "!"
end

let message be "  mounesh  "
  |> format_name
  |> greet

show message
-- Output: Hello, MOUNESH!
```

## What's Next

Now that you've built your first programs, explore:

- [Control Flow](../guide/control-flow.md) — Loops, conditionals, pattern matching
- [Pipe Operator](../guide/pipes.md) — Deep dive into MOL's killer feature
- [Standard Library](../reference/stdlib.md) — 50+ built-in functions
- [Algorithms](../guide/algorithms.md) — Sorting, searching, hashing and more
