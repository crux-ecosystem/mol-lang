# Pattern Matching

MOL supports pattern matching with the `match` expression.

## Basic Matching

```text
let status be "ok"

let message be match status with
  | "ok" -> "All good"
  | "error" -> "Something failed"
  | "pending" -> "Still waiting"
end

show message    -- "All good"
```

## Matching Numbers

```text
define describe(n)
  return match n with
    | 0 -> "zero"
    | 1 -> "one"
    | 2 -> "two"
    | _ -> "many"
  end
end

show describe(0)    -- "zero"
show describe(5)    -- "many"
```

The `_` pattern matches anything (wildcard/default).

## Guards with `when`

Add conditions to match arms:

```text
define classify(score)
  return match score with
    | n when n >= 90 -> "A"
    | n when n >= 80 -> "B"
    | n when n >= 70 -> "C"
    | n when n >= 60 -> "D"
    | _ -> "F"
  end
end

show classify(95)    -- "A"
show classify(73)    -- "C"
show classify(42)    -- "F"
```

## Multi-Line Arms

For complex logic, use block syntax:

```text
let command be "deploy"

match command with
  | "build" then
    show "Compiling..."
    show "Build complete"
  | "test" then
    show "Running tests..."
    show "All passed"
  | "deploy" then
    show "Building first..."
    show "Deploying to production"
  | _ then
    show f"Unknown command: {command}"
end
```

## Match with Structs

```text
struct Shape do
  kind, width, height
end

define area(shape)
  return match shape.kind with
    | "circle" -> 3.14159 * shape.width * shape.width
    | "rectangle" -> shape.width * shape.height
    | "triangle" -> 0.5 * shape.width * shape.height
    | _ -> panic(f"Unknown shape: {shape.kind}")
  end
end

show area(Shape("circle", 5, 0))        -- 78.539...
show area(Shape("rectangle", 4, 6))     -- 24
```

## Match as Expression

`match` returns a value, so use it anywhere an expression is valid:

```text
let day be "Monday"
let mood be match day with
  | "Monday" -> "☕ Need coffee"
  | "Friday" -> "🎉 Almost weekend"
  | "Saturday" -> "😎 Weekend!"
  | "Sunday" -> "😎 Weekend!"
  | _ -> "📝 Working"
end

show mood
```

## Pattern: State Machine

```text
define next_state(current, event)
  return match current with
    | "idle" -> match event with
      | "start" -> "running"
      | _ -> "idle"
    end
    | "running" -> match event with
      | "pause" -> "paused"
      | "stop" -> "idle"
      | _ -> "running"
    end
    | "paused" -> match event with
      | "resume" -> "running"
      | "stop" -> "idle"
      | _ -> "paused"
    end
    | _ -> panic(f"Unknown state: {current}")
  end
end

let state be "idle"
set state to next_state(state, "start")
show state    -- "running"
set state to next_state(state, "pause")
show state    -- "paused"
set state to next_state(state, "resume")
show state    -- "running"
```
