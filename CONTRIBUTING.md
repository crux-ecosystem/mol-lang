# Contributing to MOL

Thank you for your interest in contributing to MOL — The IntraMind Programming Language.

## Project Ownership

MOL is developed by **CruxLabx** for the **IntraMind** ecosystem. All contributions must align with the project's vision of providing a domain-specific language for AI pipelines, cognitive computing, and sovereign AI.

---

## Development Setup

### Prerequisites

- Python 3.10 or newer
- Git

### Clone & Install

```bash
git clone git@github.com:crux-ecosystem/MOL.git
cd MOL
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run Tests

```bash
python tests/test_mol.py
```

All 213 tests must pass before any PR is merged.

### Run Examples

```bash
mol run examples/07_pipeline.mol
mol run examples/08_rag_pipeline.mol
```

---

## Project Layout

| Directory | Purpose |
|---|---|
| `mol/` | Core language implementation |
| `mol/grammar.lark` | Lark EBNF grammar |
| `mol/parser.py` | LALR parser + AST transformer |
| `mol/ast_nodes.py` | AST node dataclasses |
| `mol/interpreter.py` | Visitor-pattern interpreter |
| `mol/types.py` | Domain types |
| `mol/stdlib.py` | Standard library functions |
| `mol/transpiler.py` | Python/JS transpiler |
| `mol/cli.py` | CLI interface |
| `examples/` | Example .mol programs |
| `tutorial/` | Tutorial .mol programs |
| `tests/` | Test suite |
| `mol-vscode/` | VS Code extension |

---

## Architecture

```
Source (.mol) → Lark LALR Parser → AST (dataclasses) → Interpreter (Visitor) → Output
                                        ↓
                                  Transpiler → Python / JavaScript
```

### Adding a New Language Feature

1. **Grammar** — Add the syntax rule to `mol/grammar.lark`
2. **AST Node** — Create a dataclass in `mol/ast_nodes.py`
3. **Parser Transformer** — Add a transformer method in `mol/parser.py`
4. **Interpreter** — Add `_exec_*` or `_eval_*` handler in `mol/interpreter.py`
5. **Transpiler** — Add `_emit_*` or `_expr_*` handlers in `mol/transpiler.py`
6. **Tests** — Add test(s) in `tests/test_mol.py`
7. **VS Code** — Update syntax highlighting in `mol-vscode/syntaxes/mol.tmLanguage.json`

### Adding a Built-in Function

1. Write the function in `mol/stdlib.py`
2. Add it to the `STDLIB` dictionary
3. Add a test in `tests/test_mol.py`
4. Update VS Code builtins regex in `mol.tmLanguage.json`

### Adding a New Domain Type

1. Create the class in `mol/types.py` (extend `MolObject`)
2. Add a constructor function in `mol/stdlib.py`
3. Register in `STDLIB` dictionary
4. Add type check in `interpreter.py` → `_check_type()`
5. Add to `type_of()` mapping in `stdlib.py`
6. Update `_to_string()` and `_describe_value()` in `interpreter.py`
7. Add tests

---

## Coding Standards

- **Python 3.10+** with type hints
- **Dataclasses** for AST nodes
- **Visitor pattern** for interpreter dispatch
- Functions should be small and focused
- All new features must have tests

---

## Commit Message Format

```
feat: add pipeline operator |> with auto-tracing
fix: resolve comment parsing with LALR priority
security: fix RCE via dunder attribute traversal
docs: update README with RAG pipeline examples
test: add pipe chain and guard test suite
refactor: centralize function invocation logic
```

---

## Contribution Tracks

MOL welcomes contributions across multiple tracks. Pick the one that fits your skills:

### 🔐 Security Researchers
Found a vulnerability? Report it privately via [SECURITY.md](SECURITY.md). Valid reports earn a spot in our **Security Hall of Fame** and release notes credit.

### 🧠 Language Developers
- Add new stdlib functions (see "Adding a Built-in Function" above)
- Implement new language features (see "Adding a New Language Feature" above)
- Improve the parser, interpreter, or transpiler
- Build tooling (LSP, formatter, linter, REPL improvements)

### 📝 Documentation & Tutorials
- Write tutorials for specific use cases (RAG, data pipelines, AI agents)
- Improve API reference documentation
- Create example `.mol` programs
- Translate docs to other languages

### 🧪 Testing & QA
- Expand the test suite (especially edge cases and security tests)
- Fuzzing the parser and interpreter
- Performance benchmarking
- Cross-platform testing

### 🌐 Community & Ecosystem
- Write blog posts about MOL
- Create video tutorials or demos
- Help answer questions in GitHub Discussions
- Build integrations with other tools (CI/CD, editors, etc.)
- Create MOL packages and share them

---

## Recognition

All contributors are recognized in:
- **CHANGELOG.md** — Your changes are documented in the release they ship with
- **Security Hall of Fame** (in SECURITY.md and README) — For vulnerability reporters
- **GitHub Contributors** — Automatically tracked by GitHub

---

## Roadmap Alignment

All features should align with the roadmap in [ROADMAP.md](ROADMAP.md):

- **v0.2.0** — Pipeline operator, RAG types (CURRENT)
- **v0.3.0** — Sovereign AI, agent blocks
- **v0.4.0** — Production runtime, async
- **v1.0.0** — Full ecosystem

---

## Questions?

Contact the project maintainer or open a GitHub issue.
