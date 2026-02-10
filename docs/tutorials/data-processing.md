# Tutorial: Data Processing

Use MOL's algorithms and pipe operator for general-purpose data processing.

## Working with Lists

### Transform Data

```text
define double(x)
  return x * 2
end

define is_even(x)
  return x % 2 == 0
end

let nums be [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

-- Map: transform each element
let doubled be map(nums, double)
show doubled  -- [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

-- Filter: keep matching elements
let evens be filter(nums, is_even)
show evens  -- [2, 4, 6, 8, 10]
```

### Aggregate Data

```text
define add(a, b)
  return a + b
end

let nums be [1, 2, 3, 4, 5]

show reduce(nums, add, 0)     -- 15
show mean(nums)                -- 3.0
show median(nums)              -- 3
show sum(nums)                 -- 15
show max(nums)                 -- 5
show min(nums)                 -- 1
```

### Clean & Deduplicate

```text
let raw be [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

let clean be raw
  |> unique
  |> sort
  |> to_text

show clean  -- [1, 2, 3, 4, 5, 6, 9]
```

## Working with Text

### String Processing Pipeline

```text
let raw_input be "  John Smith, jane DOE, Bob Jones  "

show raw_input
  |> trim
  |> lower
  |> split(",")
  |> to_text
```

### Text Analysis

```text
let text be "The quick brown fox jumps over the lazy dog"

show "Length: " + to_text(len(text))
show "Words: " + to_text(len(split(text, " ")))
show "Starts with 'The': " + to_text(starts_with(text, "The"))
show "Contains 'fox': " + to_text(contains(text, "fox"))
show "Index of 'fox': " + to_text(index_of(text, "fox"))
```

### Formatting

```text
-- Pad for aligned output
let items be ["Apple", "Banana", "Cherry"]
let prices be [1.5, 0.75, 2.25]

for i in range(len(items)) do
  let name be pad_right(items[i], 12)
  let price be pad_left(to_text(prices[i]), 6)
  show name + "$" + price
end
```

Output:
```text
Apple       $   1.5
Banana      $  0.75
Cherry      $  2.25
```

## Working with Maps

### Data Records

```text
let users be [
  {"name": "Alice", "age": 30, "role": "engineer"},
  {"name": "Bob", "age": 25, "role": "designer"},
  {"name": "Charlie", "age": 35, "role": "engineer"}
]

for user in users do
  show user.name + " (" + user.role + ")"
end
```

### Map Utilities

```text
let config be {"host": "localhost", "port": 8080, "debug": true, "secret": "abc123"}

-- Pick only safe fields
let safe_config be pick(config, "host", "port", "debug")
show to_json(safe_config)

-- Or omit sensitive ones
let public_config be omit(config, "secret")
show to_json(public_config)
```

## Statistics

```text
let scores be [85, 92, 78, 95, 88, 73, 91, 86, 79, 94]

show "Sample size: " + to_text(len(scores))
show "Mean: " + to_text(round(mean(scores), 1))
show "Median: " + to_text(median(scores))
show "Std Dev: " + to_text(round(stdev(scores), 2))
show "Min: " + to_text(min(scores))
show "Max: " + to_text(max(scores))
show "90th percentile: " + to_text(round(percentile(scores, 90), 1))
```

## Hashing & Security

```text
-- Hash passwords (never store plain text!)
let password be "my_secret_password"
let hashed be hash(password, "sha256")
show "Hashed: " + slice(hashed, 0, 16) + "..."

-- Generate unique IDs
let id be uuid()
show "User ID: " + id

-- Encode data for transport
let data be "Hello, World!"
let encoded be base64_encode(data)
show "Encoded: " + encoded
show "Decoded: " + base64_decode(encoded)
```

## Complete Example: Student Grade Analyzer

```text
-- MOL Data Processing: Student Grades

let students be ["Alice", "Bob", "Charlie", "Diana", "Eve"]
let grades be [92, 78, 85, 95, 88]

show "═══ Grade Report ═══"
show ""

-- Display each student
for i in range(len(students)) do
  let name be pad_right(students[i], 10)
  let grade be grades[i]
  let letter be "F"
  if grade >= 90 then
    set letter to "A"
  elif grade >= 80 then
    set letter to "B"
  elif grade >= 70 then
    set letter to "C"
  end
  show name + to_text(grade) + "  " + letter
end

-- Statistics
show ""
show "--- Statistics ---"
show "Average: " + to_text(round(mean(grades), 1))
show "Median:  " + to_text(median(grades))
show "Highest: " + to_text(max(grades))
show "Lowest:  " + to_text(min(grades))
show "Std Dev: " + to_text(round(stdev(grades), 2))
```
