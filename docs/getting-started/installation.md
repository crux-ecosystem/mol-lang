# Installation

## Requirements

- **Python 3.10** or higher
- **pip** (comes with Python)

## Install from Source

```bash
# Clone the repository
git clone https://github.com/crux-ecosystem/MOL.git
cd MOL

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install MOL
pip install -e .
```

## Verify Installation

```bash
mol version
# MOL v0.2.0
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
cd MOL
git pull
pip install -e .
```
