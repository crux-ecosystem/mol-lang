# Roadmap

## ✅ v0.1.0 — Foundation (Complete)

- LALR parser with Lark grammar
- Core types: Number, Text, Bool, List, Map, null
- Domain types: Thought, Memory, Node, Stream
- Control flow: if/elif/else, while, for
- Functions with closures and recursion
- Safety: access control, type annotations
- Event system: trigger, listen, emit
- Neural primitives: link, evolve, process
- Python & JavaScript transpiler
- CLI: run, parse, transpile, repl, version
- VS Code extension with syntax highlighting
- 21 tests, 6 examples, 6 tutorials

## ✅ v0.2.0 — Pipeline Operator (Complete)

- **Pipe operator `|>`** with auto-tracing
- Guard assertions
- Named pipeline definitions
- RAG domain types: Document, Chunk, Embedding, VectorStore
- 15 new RAG/pipeline stdlib functions
- 43 tests, 8 examples

## ✅ v0.3.0 — Universal Algorithms (Complete)

- **90+ stdlib functions** — useful for everyone
- Functional programming: map, filter, reduce, find, every, some, group_by
- List algorithms: flatten, unique, zip, enumerate, take, drop, chunk_list
- Math: floor, ceil, log, sin, cos, tan, pow, clamp, lerp
- Statistics: mean, median, stdev, variance, percentile
- String algorithms: starts_with, ends_with, pad_left/right, repeat, format
- Hashing: SHA-256, MD5, SHA-1, SHA-512, UUID, Base64
- Sorting: sort_by, sort_desc, binary_search
- Random: random, random_int, shuffle, sample, choice
- Map utilities: merge, pick, omit
- Type checkers: is_null, is_number, is_text, is_list, is_map
- User-defined functions as first-class callable values
- **MkDocs Material documentation site**
- 68 tests

## 📋 v0.4.0 — Module System (Planned)

- `use` statements for importing modules
- `export` for public definitions
- Package registry (`mol install`)
- Standard module library
- Namespace scoping

## 📋 v0.5.0 — LSP & IDE (Planned)

- Language Server Protocol implementation
- Real-time error diagnostics
- Autocomplete for all functions and types
- Hover documentation
- Go-to-definition
- Find references

## 📋 v0.6.0 — Async & Parallel (Planned)

- `async` / `await` keywords
- Parallel pipeline stages
- Worker pools
- Channel-based communication

## 📋 v0.7.0 — Real Integrations (Planned)

- HTTP client/server
- File system operations
- Database connectors (SQLite, PostgreSQL)
- Real vector DBs (FAISS, Milvus, Qdrant)
- Real embedding models (OpenAI, HuggingFace)

## 📋 v0.8.0 — Compilation (Planned)

- WASM compilation target
- Rust transpiler
- Browser-based runtime
- AOT optimization

## 📋 v1.0.0 — Production Release (Planned)

- Stable API guarantee
- Package ecosystem
- Interactive playground
- Jupyter/notebook integration
- Testing framework
- Debugger
- Production deployment tools
- Comprehensive error messages
- Performance benchmarks
