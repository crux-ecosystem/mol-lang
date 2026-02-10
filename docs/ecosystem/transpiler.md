# Transpiler

MOL can transpile `.mol` source code to Python or JavaScript.

## Usage

```bash
mol transpile <file.mol> --target <python|javascript|js>
```

## Python Target

```bash
mol transpile hello.mol --target python
```

### Example

**MOL source (`example.mol`):**
```text
let greeting be "Hello" |> upper
show greeting

define add(a, b)
  return a + b
end

show add(3, 4)

guard 7 > 5 : "Math is broken"
```

**Python output:**
```python
from mol.types import *

greeting = upper("Hello")
print(greeting)

def add(a, b):
    return a + b

print(add(3, 4))

assert 7 > 5, "Math is broken"
```

## JavaScript Target

```bash
mol transpile hello.mol --target javascript
```

**JavaScript output:**
```javascript
let greeting = upper("Hello");
console.log(greeting);

function add(a, b) {
    return a + b;
}

console.log(add(3, 4));

if (!(7 > 5)) { throw new Error("Math is broken"); }
```

## What Gets Transpiled

| MOL Feature | Python | JavaScript |
|-------------|--------|------------|
| `show` | `print()` | `console.log()` |
| `let x be v` | `x = v` | `let x = v` |
| `set x to v` | `x = v` | `x = v` |
| `if/elif/else/end` | `if/elif/else:` | `if/else if/else {}` |
| `while/do/end` | `while:` | `while {}` |
| `for/in/do/end` | `for in:` | `for of {}` |
| `define/end` | `def:` | `function {}` |
| `\|>` (pipe) | Nested calls | Nested calls |
| `guard` | `assert` | `if (!cond) throw` |
| `pipeline` | `def:` | `function {}` |
| `and/or/not` | `and/or/not` | `&&/\|\|/!` |
| `==` / `!=` | `==` / `!=` | `===` / `!==` |

## Pipe Chain Desugaring

The pipe operator is desugared into nested function calls:

**MOL:**
```text
"hello" |> upper |> split(" ") |> len
```

**Python:**
```python
len(split(upper("hello"), " "))
```

**JavaScript:**
```javascript
len(split(upper("hello"), " "))
```

## Limitations

- Domain-specific operations (`link`, `evolve`, `trigger`, `listen`, `emit`) generate placeholder comments
- `access` translates to a security check comment
- Auto-tracing is not reproduced in transpiled output
- Transpiled code may need MOL's type library for full functionality
