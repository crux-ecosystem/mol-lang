# Frequently Asked Questions

## General

### What is MOL?

MOL is a programming language with native pipeline operators (`|>`) and auto-tracing, built for AI/RAG pipelines. It's developed by IntraMind / CruxLabx.

### Is MOL open source?

MOL is source-available on [GitHub](https://github.com/crux-ecosystem/mol-lang) under a proprietary license. You can read the code, contribute, and use it freely.

### What does MOL stand for?

MOL stands for **M**achine **O**rchestration **L**anguage.

### What Python version do I need?

Python 3.10 or higher. Python 3.12+ is recommended.

---

## Installation & Setup

### How do I install MOL?

```bash
pipx install mol-lang
```

### How do I run a MOL program?

```bash
mol run myfile.mol
```

### Does MOL have a REPL?

Yes:

```bash
mol repl
```

### Can I try MOL without installing?

Yes! Visit [mol.cruxlabx.in](https://mol.cruxlabx.in) — the online playground is free and sandboxed.

---

## Language

### Why `let ... be` instead of `=`?

MOL is designed to read like English. `let x be 10` is clearer than `x = 10` for beginners and in pipeline-heavy code where readability matters most.

### Why `show` instead of `print`?

Same reason — `show "hello"` reads naturally. It also doesn't need parentheses for simple values.

### Why `is` / `is not` instead of `==` / `!=`?

English readability: `if x is 5 then` reads like a sentence. This is a deliberate design choice for cognitive computing contexts.

### What types does MOL support?

- Primitives: `Number`, `Text`, `Bool`, `null`
- Collections: `List`, `Map`
- AI types: `Thought`, `Memory`, `Node`, `Stream`, `Document`, `Chunk`, `Embedding`, `VectorStore`
- User types: `struct`

### Does MOL support object-oriented programming?

MOL has structs with methods (`struct` + `impl`), but no inheritance. It favors composition and functional patterns through pipes.

### Does MOL have a type system?

MOL is dynamically typed with optional type annotations:

```text
let x be 10              -- inferred
let y : Number be 20     -- enforced at runtime
```

### Can I use MOL for web development?

MOL can transpile to JavaScript and compile to browser-ready HTML:

```bash
mol build app.mol            # Standalone HTML
mol build app.mol --target js  # JavaScript file
```

---

## Pipeline & Tracing

### When does auto-tracing activate?

Auto-tracing activates for pipe chains with **3 or more stages**. Two-stage pipes are considered simple transformations.

### Can I disable tracing?

```bash
mol run file.mol --no-trace
```

### Does tracing affect performance?

Minimally. Tracing captures timestamps and type info — negligible for most workloads.

---

## Ecosystem

### Is there a VS Code extension?

Yes! The extension provides syntax highlighting, snippets, autocomplete, hover docs, diagnostics, and go-to-definition. Install from the `mol-vscode/` directory.

### Does MOL have a package manager?

Yes:

```bash
mol init            # Create project
mol install math    # Install package
mol list            # List installed
```

### Can I use MOL with Docker?

```bash
docker run --rm -v "$(pwd)":/app ghcr.io/crux-ecosystem/mol run /app/hello.mol
```

---

## Contributing

### How do I contribute?

See [CONTRIBUTING.md](https://github.com/crux-ecosystem/mol-lang/blob/main/CONTRIBUTING.md) for the full guide. In short:

1. Fork the repo
2. Create a feature branch
3. Write tests
4. Submit a PR

### Where do I report bugs?

[GitHub Issues](https://github.com/crux-ecosystem/mol-lang/issues) using the bug report template.

### Where do I ask questions?

- [GitHub Discussions](https://github.com/crux-ecosystem/mol-lang/discussions)
- Discord server (link in README)
