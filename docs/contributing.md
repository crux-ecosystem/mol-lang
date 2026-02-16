# Contributing to MOL

See the full [CONTRIBUTING.md](https://github.com/crux-ecosystem/mol-lang/blob/main/CONTRIBUTING.md) on GitHub.

## Quick Setup

```bash
git clone https://github.com/crux-ecosystem/mol-lang.git
cd mol-lang
python -m venv .venv && source .venv/bin/activate
pip install -e .
python tests/test_mol.py   # 68 tests should pass
```

## Project Structure

```
MOL/
├── mol/                    # Core language implementation
│   ├── grammar.lark        # LALR grammar (Lark EBNF)
│   ├── parser.py           # Parser + AST transformer
│   ├── ast_nodes.py        # 28 AST node types
│   ├── interpreter.py      # Tree-walking interpreter
│   ├── types.py            # 8 domain types
│   ├── stdlib.py           # 90+ built-in functions
│   ├── transpiler.py       # Python & JS code generation
│   └── cli.py              # CLI entry point
├── tests/
│   └── test_mol.py         # 68 tests
├── examples/               # 8 example programs
├── tutorial/               # 6 tutorials
├── mol-vscode/             # VS Code extension
├── docs/                   # MkDocs documentation
├── mkdocs.yml              # Docs config
└── pyproject.toml          # Package config
```

## How to Add a New stdlib Function

1. Add the Python function to `mol/stdlib.py`
2. Register it in the `STDLIB` dict at the bottom
3. Add a test in `tests/test_mol.py`
4. Document it in `docs/reference/stdlib.md`
5. Update the VS Code extension syntax: `mol-vscode/syntaxes/mol.tmLanguage.json`
6. Run `python tests/test_mol.py` — all tests must pass
