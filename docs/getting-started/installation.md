# Installation

## Requirements

- **Python 3.10** or higher (3.12+ recommended)
- **pip** (comes with Python)

## Install from PyPI (Recommended)

```bash
pip install mol-lang
```

## Verify Installation

```bash
mol version
# MOL v1.0.0
```

## Install from Source

```bash
# Clone the repository
git clone https://github.com/crux-ecosystem/mol-lang.git
cd mol-lang

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install MOL
pip install -e .
```

## VS Code Extension

MOL ships with a VS Code extension for syntax highlighting and snippets:

1. Open VS Code
2. Go to Extensions → `...` → Install from VSIX
3. Or symlink the extension folder:

```bash
ln -s $(pwd)/mol-vscode ~/.vscode/extensions/mol-lang
```

Restart VS Code. All `.mol` files will have syntax highlighting automatically.

## Dependencies

MOL has only one runtime dependency:

| Package | Version | Purpose |
|---------|---------|---------|
| [Lark](https://github.com/lark-parser/lark) | ≥ 1.1.0 | LALR parser for MOL grammar |

Development dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ≥ 7.0 | Test runner |
| mkdocs-material | latest | Documentation site |

## Updating

```bash
pip install --upgrade mol-lang
```
