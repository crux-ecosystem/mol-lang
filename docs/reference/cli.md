# CLI Reference

## Usage

```bash
mol <command> [options]
```

## Commands

### `mol run`

Execute a MOL program.

```bash
mol run <file.mol> [--trace | --no-trace]
```

| Flag | Description |
|------|-------------|
| `--trace` | Force auto-tracing on all pipe chains (default for 3+ stages) |
| `--no-trace` | Disable all pipe tracing |

**Examples:**
```bash
mol run hello.mol
mol run pipeline.mol --trace
mol run app.mol --no-trace
```

### `mol parse`

Display the AST (Abstract Syntax Tree) of a MOL program.

```bash
mol parse <file.mol>
```

Useful for debugging grammar and parser behavior.

### `mol transpile`

Convert MOL source to Python or JavaScript.

```bash
mol transpile <file.mol> --target <python|javascript|js>
```

| Target | Output |
|--------|--------|
| `python` | Python 3 source code |
| `javascript` or `js` | JavaScript (ES6+) |

**Examples:**
```bash
mol transpile app.mol --target python
mol transpile app.mol --target js
```

### `mol repl`

Start an interactive Read-Eval-Print Loop.

```bash
mol repl
```

**REPL Features:**

- Execute MOL code line by line
- Multi-line support with `\` continuation
- Persistent state between lines
- `Ctrl+C` to exit

```text
MOL v0.3.0 REPL
Type MOL code. Use \ for multi-line. Ctrl+C to exit.
mol> let x be 42
mol> show x * 2
84
mol> show "hello" |> upper
HELLO
```

### `mol version`

Print the current MOL version.

```bash
mol version
# MOL v0.3.0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime error, guard failure, or file not found |
