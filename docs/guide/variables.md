# Variables & Types

## Declaring Variables

Use `let ... be` to declare variables:

```text
let name be "MOL"
let age be 2
let active be true
let items be [1, 2, 3]
let config be {"debug": true, "version": 2}
```

## Reassigning Variables

Use `set ... to` to reassign:

```text
let count be 0
set count to count + 1
show count  -- 1
```

## Type Annotations

Add optional type constraints with `:`:

```text
let x: Number be 42         -- ✓
let name: Text be "hello"   -- ✓
let flag: Bool be true       -- ✓

let bad: Number be "oops"   -- ✗ MOLTypeError
```

### Supported Type Annotations

`Number`, `Text`, `Bool`, `List`, `Map`, `Thought`, `Memory`, `Node`, `Stream`

## Primitive Types

### Numbers

```text
let integer be 42
let decimal be 3.14
let negative be -17
let result be 2 ^ 10    -- 1024
```

All numbers are IEEE 754 floating-point internally.

### Text (Strings)

```text
let greeting be "Hello, World!"
let multiline be "Line 1
Line 2
Line 3"
```

**String operations:**

```text
let s be "hello world"
show upper(s)           -- "HELLO WORLD"
show lower("ABC")       -- "abc"
show trim("  hi  ")     -- "hi"
show len(s)             -- 11
show split(s, " ")      -- ["hello", "world"]
show replace(s, "world", "MOL")  -- "hello MOL"
show slice(s, 0, 5)     -- "hello"
show contains(s, "world")  -- true
```

### Booleans

```text
let yes be true
let no be false

-- Logical operators
show true and false     -- false
show true or false      -- true
show not true           -- false
```

### Null

```text
let empty be null
show type_of(empty)     -- "null"
```

### Lists

```text
let nums be [1, 2, 3, 4, 5]
show nums[0]            -- 1
show len(nums)          -- 5

-- List operations
push(nums, 6)           -- [1, 2, 3, 4, 5, 6]
let last be pop(nums)   -- 6
show sort(nums)         -- [1, 2, 3, 4, 5]
show reverse(nums)      -- [5, 4, 3, 2, 1]
show sum(nums)          -- 15
show contains(nums, 3)  -- true
show slice(nums, 1, 3)  -- [2, 3]
```

### Maps

```text
let user be {"name": "Mounesh", "role": "builder"}
show user.name          -- "Mounesh"
show user["role"]       -- "builder"
show keys(user)         -- ["name", "role"]
show values(user)       -- ["Mounesh", "builder"]
```

## Type Checking

```text
show type_of(42)            -- "Number"
show type_of("hello")       -- "Text"
show type_of(true)          -- "Bool"
show type_of([1, 2])        -- "List"
show type_of({"a": 1})      -- "Map"
show type_of(null)          -- "null"
show type_of(Thought("x", 0.5))  -- "Thought"
```

## Type Conversion

```text
show to_text(42)         -- "42"
show to_text(3.14)       -- "3.14"
show to_number("42")     -- 42
show to_number("3.14")   -- 3.14
```
