# Safety & Guards

MOL has built-in safety primitives — no external libraries needed.

## Guard Assertions

`guard` validates conditions at runtime. If the condition is false, execution halts with a clear error.

```text
let confidence be 0.85

guard confidence > 0.5 : "Confidence too low"
show "Passed!"  -- This runs

guard confidence > 0.9 : "Need higher confidence"
-- MOLGuardError: Guard failed: Need higher confidence
```

### Guard Syntax

```text
-- With message
guard condition : "error message"

-- Without message (generic error)
guard condition
```

### Guard in Pipelines

Guards are powerful inside pipeline definitions:

```text
pipeline safe_answer(question)
  let hits be retrieve(question, "kb", 3)
  let answer be hits |> think(question)
  guard answer.confidence > 0.5 : "Answer quality too low"
  guard len(answer.content) > 10 : "Answer too short"
  return answer
end
```

### Built-in Guard Functions

```text
-- Assert minimum value
assert_min(score, 0.7)           -- fails if score < 0.7

-- Assert not null
assert_not_null(data)            -- fails if data is null
```

## Access Control

MOL has a built-in security model for AI resource management:

```text
access "mind_core" with "admin"
-- [MOL] 🔓 Access granted: mind_core
```

### Protected Resources

| Resource | Description |
|----------|-------------|
| `mind_core` | Core cognitive system |
| `memory_bank` | Memory storage |
| `node_graph` | Neural graph |
| `data_stream` | Data pipelines |
| `thought_pool` | Thought collection |

### Access Denied

```text
access "secret_resource" with "guest"
-- MOLSecurityError: Access denied to: secret_resource
```

## Type Safety

Optional type annotations catch mismatches at declaration:

```text
let x: Number be 42        -- ✓
let y: Text be "hello"     -- ✓
let z: Number be "oops"    -- ✗ MOLTypeError
```

## Error Types

| Error | When |
|-------|------|
| `MOLRuntimeError` | Division by zero, undefined variable, general errors |
| `MOLTypeError` | Type annotation mismatch |
| `MOLGuardError` | Guard assertion failure |
| `MOLSecurityError` | Unauthorized resource access |

## Infinite Loop Protection

Loops are limited to 1,000,000 iterations:

```text
let i be 0
while true do
  set i to i + 1
  -- Automatically stops after 1M iterations
end
```

## Best Practices

!!! tip "Defense in Depth"
    1. Use **type annotations** for critical variables
    2. Use **guard** to validate pipeline outputs
    3. Use **access** to protect sensitive resources
    4. Use **assert_min** / **assert_not_null** in pipes
