# Modules & Imports

MOL has a module system for organizing code across files.

## Importing Files

Use the `use` statement to import from other `.mol` files:

```text
-- Import everything from a file
use "./utils.mol"

-- Import specific names
use "./math_helpers.mol" : add, multiply

-- Import with a namespace alias
use "./config.mol" as Config
show Config.api_key
```

## Exporting

By default, **all** top-level names in a file are exported. Use `export` for explicit control:

```text
-- helpers.mol

-- Only these two will be importable
export greet, farewell

define greet(name)
  return "Hello, " + name
end

define farewell(name)
  return "Goodbye, " + name
end

-- This is private — not exported
define internal_helper()
  return "you can't import me"
end
```

## Package Imports

Import built-in packages by name (without `./`):

```text
-- Import a built-in package
use "math"
use "collections"
use "text"
```

### Available Packages

| Package | Contents |
|---|---|
| `std` | Core utilities |
| `math` | Extended math & statistics |
| `text` | String processing |
| `collections` | Stack, Queue, LinkedList |
| `crypto` | Hashing, encoding |
| `random` | Random number generation |
| `rag` | RAG pipeline helpers |

## Package Manager

### Initialize a Project

```bash
mol init
```

Creates a `mol.pkg.json` manifest:

```json
{
  "name": "my-project",
  "version": "0.1.0",
  "main": "main.mol",
  "dependencies": {}
}
```

### Install Packages

```bash
mol install math
mol install collections
```

### List Installed

```bash
mol list
```

### Search the Registry

```bash
mol search "vector"
```

## Module Patterns

### Config Module

```text
-- config.mol
export api_url, max_retries, timeout

let api_url be "https://api.example.com"
let max_retries be 3
let timeout be 5000
```

```text
-- main.mol
use "./config.mol" : api_url, timeout
show f"Connecting to {api_url} (timeout: {timeout}ms)"
```

### Utility Library

```text
-- string_utils.mol
export capitalize, slugify, truncate

define capitalize(text)
  let first be upper(slice(text, 0, 1))
  let rest be lower(slice(text, 1, len(text)))
  return first + rest
end

define slugify(text)
  return text |> lower |> replace(" ", "-")
end

define truncate(text, max_len)
  if len(text) <= max_len then
    return text
  end
  return slice(text, 0, max_len) + "..."
end
```

### Struct Library

```text
-- models.mol
export User, Post

struct User do
  name, email
end

struct Post do
  title, body, author
end

impl Post do
  define summary()
    return f"{self.title} by {self.author.name}"
  end
end
```

```text
-- app.mol
use "./models.mol" : User, Post

let author be User("Alice", "alice@mol.dev")
let post be Post("Hello MOL", "First post!", author)
show post.summary()
```
