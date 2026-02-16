# Generators & Iterators

Generators produce values lazily, one at a time, using `yield`.

## Basic Generator

```text
define countdown(n)
  while n > 0 do
    yield n
    set n to n - 1
  end
end

let gen be countdown(5)
show gen.next()    -- 5
show gen.next()    -- 4
show gen.next()    -- 3
```

## Materializing to a List

```text
let all be countdown(5).to_list()
show all    -- [5, 4, 3, 2, 1]
```

## Fibonacci Generator

```text
define fibonacci(n)
  let a be 0
  let b be 1
  for i in range(n) do
    yield a
    let temp be a + b
    set a to b
    set b to temp
  end
end

show fibonacci(10).to_list()
-- [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

## Generators in For Loops

```text
for val in fibonacci(8) do
  show f"fib: {val}"
end
```

## Filtered Generator

```text
define even_squares(limit)
  for i in range(limit) do
    let sq be i * i
    if sq % 2 is 0 then
      yield sq
    end
  end
end

show even_squares(10).to_list()
-- [0, 4, 16, 36, 64]
```

## Generators in Pipes

```text
fibonacci(10).to_list()
  |> filter(fn(x) -> x > 5)
  |> map(fn(x) -> x * 2)
  |> show
-- [16, 26, 42, 68]
```

## Infinite-Style Generators

Use generators to produce values on demand without precomputing:

```text
define naturals(start)
  let n be start
  while true do
    yield n
    set n to n + 1
  end
end

-- Take only what you need
let gen be naturals(1)
let first_five be []
for i in range(5) do
  push(first_five, gen.next())
end
show first_five    -- [1, 2, 3, 4, 5]
```

## Generator Pattern: File-Like Processing

```text
define words(text)
  let parts be split(text, " ")
  for part in parts do
    if len(trim(part)) > 0 then
      yield trim(part)
    end
  end
end

for word in words("  hello   world   from   MOL  ") do
  show word
end
-- hello
-- world
-- from
-- MOL
```
