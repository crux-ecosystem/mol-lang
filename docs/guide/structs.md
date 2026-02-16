# Structs & Methods

Structs let you define custom data types with named fields and methods.

## Defining Structs

```text
struct Point do
  x,
  y
end

struct User do
  name,
  email,
  age
end
```

## Creating Instances

Two styles — constructor and literal:

=== "Constructor style"

    ```text
    let p be Point(10, 20)
    let user be User("Alice", "alice@mol.dev", 30)
    ```

=== "Literal style"

    ```text
    let p be Point { x: 10, y: 20 }
    let user be User { name: "Alice", email: "alice@mol.dev", age: 30 }
    ```

Both are equivalent. Literal style is clearer when structs have many fields.

## Field Access

```text
let p be Point(10, 20)
show p.x       -- 10
show p.y       -- 20
```

## Field Mutation

```text
let p be Point(10, 20)
set p.x to 50
show p.x       -- 50
```

## Methods with `impl`

Attach methods to structs using `impl`:

```text
impl Point do
  define distance(other)
    let dx be self.x - other.x
    let dy be self.y - other.y
    return sqrt(dx * dx + dy * dy)
  end

  define translate(dx, dy)
    return Point(self.x + dx, self.y + dy)
  end

  define to_text()
    return f"({self.x}, {self.y})"
  end
end
```

!!! info "The `self` keyword"
    Inside `impl` methods, `self` refers to the instance the method is called on.

## Using Methods

```text
let a be Point(0, 0)
let b be Point(3, 4)

show a.distance(b)           -- 5.0
show a.translate(5, 5).to_text()  -- (5, 5)
```

## Multiple Impls

You can add methods in separate `impl` blocks:

```text
struct Color do
  r, g, b
end

impl Color do
  define hex()
    return f"rgb({self.r}, {self.g}, {self.b})"
  end
end

impl Color do
  define is_dark()
    return (self.r + self.g + self.b) / 3 < 128
  end
end

let red be Color(255, 0, 0)
show red.hex()        -- rgb(255, 0, 0)
show red.is_dark()    -- false
```

## Structs in Pipes

Structs work naturally with pipes:

```text
struct Record do
  name, score
end

let records be [
  Record("Alice", 95),
  Record("Bob", 82),
  Record("Carol", 91)
]

records
  |> sort_by(fn(r) -> r.score)
  |> reverse
  |> map(fn(r) -> f"{r.name}: {r.score}")
  |> join(", ")
  |> show
-- Alice: 95, Carol: 91, Bob: 82
```

## Real-World Example: Stack

```text
struct Stack do
  items
end

impl Stack do
  define push(value)
    push(self.items, value)
    return self
  end

  define pop()
    return pop(self.items)
  end

  define peek()
    return self.items[len(self.items) - 1]
  end

  define is_empty()
    return len(self.items) is 0
  end

  define size()
    return len(self.items)
  end
end

let stack be Stack { items: [] }
stack.push(1)
stack.push(2)
stack.push(3)
show stack.peek()    -- 3
show stack.pop()     -- 3
show stack.size()    -- 2
```

## type_of for Structs

```text
let p be Point(1, 2)
show type_of(p)      -- "Point"
```
