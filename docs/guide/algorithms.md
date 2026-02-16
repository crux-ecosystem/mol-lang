# Algorithms

MOL ships with built-in algorithms that make it useful for **everyone** — not just AI pipelines. These are available immediately, no imports needed.

## Functional Programming

!!! tip "Smart Functions"
    MOL's HOFs (Higher-Order Functions) are **smart** — they accept lambdas, named functions, values for equality matching, and strings for property access. No boilerplate needed.

### map / select

Apply a function to every element:

```text
-- With a lambda (inline function)
show map([1, 2, 3, 4], fn(x) -> x * 2)
-- [2, 4, 6, 8]

-- With a named function
define double(x)
  return x * 2
end
show map([1, 2, 3], double)
-- [2, 4, 6]

-- Smart mode: extract a property from objects
let users be [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
show users |> map("name")
-- ["Alice", "Bob"]

-- select is an alias for map (more readable for projections)
show users |> select("name")
-- ["Alice", "Bob"]
```

### filter / where

Keep elements that match a condition:

```text
-- With a lambda
show filter([1, 2, 3, 4, 5, 6], fn(x) -> x % 2 == 0)
-- [2, 4, 6]

-- Smart mode: equality matching (just pass the value!)
show filter([10, 20, 30, 40, 50], 30)
-- [30]

-- Smart mode: filter objects by truthy property
let items be [
  {"name": "A", "active": true},
  {"name": "B", "active": false},
  {"name": "C", "active": true}
]
show items |> filter("active") |> map("name")
-- ["A", "C"]

-- where is an alias for filter (more readable)
show [1, 2, 3, 4, 5] |> where(fn(x) -> x > 3)
-- [4, 5]
```

### reject

Opposite of filter — remove matching elements:

```text
show reject([1, 2, 3, 4, 5], fn(x) -> x > 3)
-- [1, 2, 3]

-- Smart mode: remove by value
show reject([1, 2, 3, 2, 1], 2)
-- [1, 3, 1]
```

### reduce

Reduce a list to a single value:

```text
show reduce([1, 2, 3, 4, 5], fn(a, b) -> a + b, 0)
-- 15
```

### find

Find the first matching element:

```text
show find([3, 7, 15, 22], fn(x) -> x > 10)
-- 15

-- Smart mode: find by value
show find([10, 20, 30], 20)
-- 20
```

### every / some

Check all or any elements:

```text
show every([2, 4, 6], fn(x) -> x % 2 == 0)     -- true
show some([1, 3, 4], fn(x) -> x % 2 == 0)       -- true

-- Smart mode: check with value
show every([3, 3, 3], 3)    -- true
show some([1, 2, 3], 2)     -- true
```

### group_by

Group elements by a function:

```text
show group_by([1, 2, 3, 4, 5, 6], fn(x) -> x % 2 == 0)
-- {"true": [2, 4, 6], "false": [1, 3, 5]}

-- Smart mode: group by property
let users be [
  {"name": "Alice", "dept": "eng"},
  {"name": "Bob", "dept": "sales"},
  {"name": "Charlie", "dept": "eng"}
]
show users |> group_by("dept")
-- {"eng": [...], "sales": [...]}
```

### each

Execute a function for each element (for side effects). Returns the original list:

```text
[1, 2, 3] |> each(fn(x) -> show(x))
-- prints 1, 2, 3 and returns [1, 2, 3]
```

### pluck

Extract a single property from each object:

```text
let users be [{"name": "Alice"}, {"name": "Bob"}]
show pluck(users, "name")
-- ["Alice", "Bob"]
```

## List Operations

| Function | Description | Example |
|----------|-------------|---------|
| `first(lst)` | Get first element | `first([10,20,30]) → 10` |
| `last(lst)` | Get last element | `last([10,20,30]) → 30` |
| `flatten(lst)` | Flatten nested lists | `flatten([[1,2],[3]]) → [1,2,3]` |
| `unique(lst)` | Remove duplicates | `unique([1,2,2,3]) → [1,2,3]` |
| `compact(lst)` | Remove null/false values | `compact([1,null,2,false]) → [1,2]` |
| `contains(lst, val)` | Check membership | `contains([1,2,3], 2) → true` |
| `zip(a, b)` | Pair elements | `zip([1,2],["a","b"]) → [[1,"a"],[2,"b"]]` |
| `enumerate(lst)` | Add indices | `enumerate(["x","y"]) → [[0,"x"],[1,"y"]]` |
| `count(lst, item)` | Count occurrences | `count([1,2,1], 1) → 2` |
| `find_index(lst, item)` | Index of item (-1 if not found) | `find_index([10,20,30], 20) → 1` |
| `take(lst, n)` | First n elements | `take([1,2,3,4], 2) → [1,2]` |
| `drop(lst, n)` | Skip first n | `drop([1,2,3,4], 2) → [3,4]` |
| `chunk_list(lst, n)` | Split into groups | `chunk_list([1,2,3,4,5], 2) → [[1,2],[3,4],[5]]` |
| `sum_list(lst)` | Sum all numbers | `sum_list([1,2,3,4,5]) → 15` |
| `min_list(lst)` | Get minimum | `min_list([3,1,4]) → 1` |
| `max_list(lst)` | Get maximum | `max_list([3,1,4]) → 4` |

## Sorting & Searching

```text
-- Sort ascending (default)
show sort([3, 1, 4, 1, 5])     -- [1, 1, 3, 4, 5]

-- Sort descending
show sort_desc([3, 1, 4, 1, 5])  -- [5, 4, 3, 1, 1]

-- Sort by custom function
show sort_by(["cat", "a", "elephant"], fn(s) -> len(s))
-- ["a", "cat", "elephant"]

-- Smart mode: sort by property name
let users be [
  {"name": "Charlie", "age": 35},
  {"name": "Alice", "age": 25},
  {"name": "Bob", "age": 30}
]
show users |> sort_by("age") |> map("name")
-- ["Alice", "Bob", "Charlie"]

-- Binary search (on sorted list)
show binary_search([1, 2, 3, 4, 5], 3)   -- 2
show binary_search([1, 2, 3, 4, 5], 99)  -- -1
```

## Math & Statistics

### Basic Math

| Function | Description | Example |
|----------|-------------|---------|
| `abs(x)` | Absolute value | `abs(-5) → 5` |
| `floor(x)` | Round down | `floor(3.7) → 3` |
| `ceil(x)` | Round up | `ceil(3.2) → 4` |
| `round(x, n)` | Round to n decimals | `round(3.14159, 2) → 3.14` |
| `pow(x, y)` | Exponentiation | `pow(2, 10) → 1024` |
| `sqrt(x)` | Square root | `sqrt(144) → 12` |
| `log(x, base)` | Logarithm | `log(100, 10) → 2.0` |
| `clamp(x, lo, hi)` | Clamp to range | `clamp(15, 0, 10) → 10` |
| `lerp(a, b, t)` | Linear interpolation | `lerp(0, 100, 0.5) → 50` |

### Trigonometry

```text
show sin(pi() / 2)    -- 1.0
show cos(0)            -- 1.0
show tan(pi() / 4)     -- ~1.0
```

### Statistics

```text
let scores be [85, 92, 78, 95, 88, 73, 91]

show mean(scores)        -- 86.0
show median(scores)      -- 88
show stdev(scores)       -- 7.94...
show variance(scores)    -- 63.0
show percentile(scores, 90)  -- 93.2
show min(scores)         -- 73
show max(scores)         -- 95
```

## String Algorithms

| Function | Description | Example |
|----------|-------------|---------|
| `starts_with(s, prefix)` | Check prefix | `starts_with("hello", "hel") → true` |
| `ends_with(s, suffix)` | Check suffix | `ends_with("hello", "llo") → true` |
| `pad_left(s, width, char)` | Left pad | `pad_left("42", 5, "0") → "00042"` |
| `pad_right(s, width, char)` | Right pad | `pad_right("hi", 5) → "hi   "` |
| `repeat(s, n)` | Repeat string | `repeat("ha", 3) → "hahaha"` |
| `char_at(s, i)` | Get character | `char_at("hello", 1) → "e"` |
| `index_of(s, sub)` | Find substring | `index_of("hello world", "world") → 6` |
| `format(template, ...)` | Format string | `format("Hello, {}!", "World") → "Hello, World!"` |

## Hashing & Encoding

```text
-- Cryptographic hashing
show hash("hello")                 -- SHA-256 hex (64 chars)
show hash("hello", "md5")         -- MD5 hex
show hash("hello", "sha512")      -- SHA-512 hex

-- UUID generation
show uuid()                        -- "a1b2c3d4-e5f6-..."

-- Base64
let encoded be base64_encode("Hello, World!")
show encoded                       -- "SGVsbG8sIFdvcmxkIQ=="
show base64_decode(encoded)        -- "Hello, World!"
```

## Random

```text
show random()                -- 0.0-1.0 float
show random_int(1, 100)      -- random integer
show shuffle([1, 2, 3, 4])   -- random order
show sample([1, 2, 3, 4, 5], 3)  -- 3 random items
show choice(["red", "blue", "green"])  -- random pick
```

## Map Operations

```text
let user be {"name": "Mounesh", "age": 25, "role": "builder", "password": "secret"}

-- Merge maps
show merge({"a": 1}, {"b": 2})  -- {"a": 1, "b": 2}

-- Pick specific fields
show pick(user, "name", "role")   -- {"name": "Mounesh", "role": "builder"}

-- Omit fields
show omit(user, "password")       -- user without password
```

## Type Checking Functions

```text
show is_number(42)       -- true
show is_text("hello")    -- true
show is_list([1, 2])     -- true
show is_map({"a": 1})    -- true
show is_null(null)       -- true
```

## Combining with Pipes

All algorithms work naturally with the pipe operator:

```text
let data be [3, -1, 4, -1, 5, 9, -2, 6]

-- Pipe-friendly data processing
let result be data |>
  where(fn(x) -> x > 0) |>
  sort |>
  unique

show result
-- [3, 4, 5, 6, 9]
```

### Real-World Example: Data Pipeline

```text
let students be [
  {"name": "Alice", "score": 95, "active": true},
  {"name": "Bob", "score": 60, "active": false},
  {"name": "Charlie", "score": 88, "active": true},
  {"name": "Diana", "score": 42, "active": true}
]

-- Get honor roll names (active + score >= 80)
let honor_roll be students |>
  filter("active") |>
  where(fn(s) -> s["score"] >= 80) |>
  select(fn(s) -> s["name"])

show honor_roll
-- ["Alice", "Charlie"]
```
