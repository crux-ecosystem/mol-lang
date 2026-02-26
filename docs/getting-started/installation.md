# Installation

## Requirements

- **Python 3.10** or higher (3.12+ recommended)
- **pip** (comes with Python)

---

## Quick Install (Recommended)

### Option A: `pipx` (Best for CLI tools)

`pipx` installs MOL in an isolated environment and makes the `mol` command available globally. **This is the recommended method** — it avoids permission errors and doesn't conflict with system Python.

```bash
# Install pipx if you don't have it
# Ubuntu/Debian:
sudo apt install pipx
pipx ensurepath

# macOS:
brew install pipx
pipx ensurepath

# Then install MOL:
pipx install mol-lang
```

### Option B: `pip` in a Virtual Environment

If you prefer `pip`, create a virtual environment first:

```bash
python3 -m venv mol-env
source mol-env/bin/activate    # Linux/macOS
# mol-env\Scripts\activate     # Windows

pip install mol-lang
```

!!! warning "Getting `externally-managed-environment` error?"
    Modern Python (3.12+ on Ubuntu/Debian/Fedora) blocks `pip install` system-wide (PEP 668).
    Use **`pipx install mol-lang`** instead — it handles isolation automatically.

### Option C: System-wide `pip` (Not Recommended)

If you understand the risks and want to install globally anyway:

```bash
pip install mol-lang
# If blocked, use:
pip install --user mol-lang
```

## Verify Installation

```bash
mol version
# MOL v1.1.0
```

If `mol` isn't found after installation:

```bash
# Check if it's in your PATH
which mol

# If using pipx, ensure PATH is set:
pipx ensurepath
# Then restart your terminal

# If using --user install, add to PATH:
export PATH="$HOME/.local/bin:$PATH"
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
