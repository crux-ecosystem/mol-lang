# Control Flow

## If / Elif / Else

```text
let score be 85

if score >= 90 then
  show "A"
elif score >= 80 then
  show "B"
elif score >= 70 then
  show "C"
else
  show "F"
end
```

## Comparison Operators

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater or equal |
| `<=` | Less or equal |
| `is` | Identity equal (same as `==`) |

```text
let x be 10
if x is 10 then
  show "x is ten"
end

if x != 5 then
  show "x is not five"
end
```

## Logical Operators

```text
let a be true
let b be false

if a and b then
  show "both"
end

if a or b then
  show "either"     -- prints
end

if not b then
  show "negated"    -- prints
end
```

## For Loops

Iterate over lists or ranges:

```text
-- Range-based
for i in range(5) do
  show i    -- 0, 1, 2, 3, 4
end

-- List iteration
let fruits be ["apple", "banana", "cherry"]
for fruit in fruits do
  show fruit
end

-- Range with start and end
for i in range(1, 4) do
  show i    -- 1, 2, 3
end
```

## While Loops

```text
let count be 0
while count < 5 do
  show count
  set count to count + 1
end
```

!!! warning "Infinite Loop Protection"
    MOL limits loops to 1,000,000 iterations. If exceeded, a `MOLRuntimeError` is raised.

## Blocks

Group statements in a scoped block:

```text
begin
  let x be 42
  show x      -- 42
end
-- x is not accessible here
```

## Truthiness

The following values are falsy in MOL:

- `false`
- `null`
- `0`
- `""` (empty string)
- `[]` (empty list)

Everything else is truthy.
