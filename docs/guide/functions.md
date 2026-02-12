# Functions

## Defining Functions

```text
fn greet(name)
  return "Hello, " + name + "!"
end

show greet("World")   -- "Hello, World!"
```

## Parameters

```text
fn add(a, b)
  return a + b
end

fn multiply(a, b)
  return a * b
end

show add(3, 4)        -- 7
show multiply(5, 6)   -- 30
```

## Return Values

Functions return the value of their `return` statement:

```text
fn factorial(n)
  if n <= 1 then
    return 1
  end
  return n * factorial(n - 1)
end

show factorial(5)     -- 120
```

## Functions in Pipes

Functions integrate naturally with the pipe operator:

```text
fn double(x)
  return x * 2
end

fn add_ten(x)
  return x + 10
end

-- Data flows left to right
show 5 |> double |> add_ten |> double
-- Trace shows: 5 → 10 → 20 → 40
```

!!! tip "Pipe Compatibility"
    In a pipe chain, the output of each stage becomes the **first argument** of the next function. Additional arguments are passed normally: `value |> func(extra_arg)`.

## Closures

Functions capture their enclosing scope:

```text
fn make_adder(n)
  fn adder(x)
    return x + n
  end
  return adder
end

let add5 be make_adder(5)
show add5(10)     -- 15
show add5(20)     -- 25
```

## Named Pipelines

`pipeline` is a specialized function for data processing chains:

```text
pipeline process_text(text)
  let cleaned be text |> trim |> lower
  guard len(cleaned) > 0 : "Empty input"
  return cleaned
end

show process_text("  HELLO  ")   -- "hello"
```

Pipelines can be used as pipe stages:

```text
pipeline normalize(text)
  return text |> trim |> lower
end

let result be "  HELLO WORLD  " |> normalize
show result   -- "hello world"
```

## Recursion

MOL supports full recursion:

```text
fn fibonacci(n)
  if n <= 1 then
    return n
  end
  return fibonacci(n - 1) + fibonacci(n - 2)
end

for i in range(10) do
  show fibonacci(i)
end
-- 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
```

## Higher-Order Patterns

Combine functions with pipes for functional-style programming:

```text
fn is_positive(x)
  return x > 0
end

fn square(x)
  return x ^ 2
end

-- Transform data through function chains
let data be [1, -2, 3, -4, 5]
for item in data do
  if is_positive(item) then
    show item |> square
  end
end
-- 1, 9, 25
```
