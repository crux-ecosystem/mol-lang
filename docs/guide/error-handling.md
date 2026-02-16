# Error Handling

MOL provides structured error handling with `try/rescue/ensure` — inspired by Ruby and Elixir.

## Try / Rescue

Catch errors and recover gracefully:

```text
try
  let result be 10 / 0
rescue err
  show f"Caught error: {err}"
end
```

The `rescue` block runs when any error occurs. The error variable (`err`) is optional:

```text
try
  let data be json_parse("{ invalid }")
rescue
  show "Failed to parse JSON"
end
```

## Ensure (Finally)

The `ensure` block **always** runs, whether an error occurred or not:

```text
try
  let content be read_file("data.txt")
  show content
rescue err
  show f"File error: {err}"
ensure
  show "Cleanup complete"
end
```

This is useful for closing resources, logging, or cleanup.

## Guard Assertions

Use `guard` for preconditions that **must** be true:

```text
define divide(a, b)
  guard b is not 0 : "Cannot divide by zero"
  return a / b
end

show divide(10, 2)    -- 5.0
show divide(10, 0)    -- MOLGuardError: Cannot divide by zero
```

Guards are **not** error handling — they halt execution immediately. Use them for:

- Input validation
- Preconditions
- Invariant checking

```text
define process_age(age)
  guard age >= 0 : "Age cannot be negative"
  guard age <= 150 : "Age seems unrealistic"
  return f"Processing age: {age}"
end
```

## panic()

Raise a runtime error manually:

```text
define validate(email)
  if not contains(email, "@") then
    panic("Invalid email: " + email)
  end
  return email
end
```

## Nested Try/Rescue

`try/rescue` blocks can be nested:

```text
try
  try
    panic("inner error")
  rescue inner_err
    show f"Inner caught: {inner_err}"
    panic("re-raised!")
  end
rescue outer_err
  show f"Outer caught: {outer_err}"
end
```

## Error Types

| Error | Cause |
|---|---|
| `MOLRuntimeError` | Undefined variable, division by zero, type mismatch |
| `MOLTypeError` | Type annotation violation |
| `MOLGuardError` | `guard` condition fails |
| `MOLSecurityError` | Unauthorized `access` statement |
| Parse Error | Invalid `.mol` syntax |

## Pattern: Safe Division

```text
define safe_divide(a, b)
  try
    return a / b
  rescue err
    return null
  end
end

show safe_divide(10, 3)   -- 3.333...
show safe_divide(10, 0)   -- null
```

## Pattern: Parse with Fallback

```text
define parse_number(text)
  try
    return to_number(text)
  rescue
    return 0
  end
end

show parse_number("42")     -- 42
show parse_number("hello")  -- 0
```

## Pattern: Retry Logic

```text
define retry(action, max_attempts)
  let attempt be 1
  while attempt <= max_attempts do
    try
      return action()
    rescue err
      show f"Attempt {attempt} failed: {err}"
      set attempt to attempt + 1
    end
  end
  panic("All attempts failed")
end
```
