# VS Code Extension

MOL ships with a VS Code extension for syntax highlighting and code snippets.

## Installation

### From Source

```bash
# Symlink the extension
ln -s /path/to/MOL/mol-vscode ~/.vscode/extensions/mol-lang

# Or copy it
cp -r mol-vscode ~/.vscode/extensions/mol-lang
```

Restart VS Code. All `.mol` files will have syntax highlighting.

## Features

### Syntax Highlighting

The extension highlights:

- **Keywords** — `let`, `be`, `show`, `if`, `define`, `pipeline`, `guard`, etc.
- **Operators** — `|>`, `+`, `-`, `*`, `/`, `==`, `!=`, `and`, `or`, `not`
- **Types** — `Thought`, `Memory`, `Node`, `Document`, `Embedding`, etc.
- **Built-in functions** — All 90+ stdlib functions
- **Comments** — `-- comment`
- **Strings** — `"text"` with escape sequences
- **Numbers** — integers and floats

### Code Snippets

| Prefix | Snippet |
|--------|---------|
| `mol-let` | Variable declaration |
| `mol-fn` | Function definition |
| `mol-if` | If/else block |
| `mol-for` | For loop |
| `mol-while` | While loop |
| `mol-pipe` | Pipe chain |
| `mol-guard` | Guard assertion |
| `mol-pipeline` | Pipeline definition |
| `mol-thought` | Thought constructor |
| `mol-node` | Node constructor |
| `mol-rag` | RAG pipeline template |

### File Association

The extension associates `.mol` files with the MOL language, providing:

- Syntax-aware bracket matching
- Auto-closing pairs (`"`, `(`, `[`, `{`)
- Comment toggling (`--`)
- Folding markers (`if/end`, `define/end`, `for/end`, etc.)

## Extension Structure

```
mol-vscode/
├── package.json                 # Extension manifest
├── language-configuration.json  # Language settings
├── syntaxes/
│   └── mol.tmLanguage.json     # TextMate grammar
└── snippets/
    └── mol.json                # Code snippets
```
