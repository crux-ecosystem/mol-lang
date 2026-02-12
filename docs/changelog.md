# Changelog

All notable changes to MOL are documented here.

## [0.3.0] - 2026-02-10

### Added

**Universal Algorithms & Functions (42 new functions):**

- **Functional programming:** `map`, `filter`, `reduce`, `find`, `every`, `some`, `group_by`
- **List operations:** `flatten`, `unique`, `zip`, `enumerate`, `count`, `find_index`, `take`, `drop`, `chunk_list`
- **Math:** `floor`, `ceil`, `log`, `sin`, `cos`, `tan`, `pow`, `clamp`, `lerp`, `pi`, `e`
- **Statistics:** `mean`, `median`, `stdev`, `variance`, `percentile`
- **String algorithms:** `starts_with`, `ends_with`, `pad_left`, `pad_right`, `repeat`, `char_at`, `index_of`, `format`
- **Hashing & encoding:** `hash` (SHA-256/MD5/SHA-1/SHA-512), `uuid`, `base64_encode`, `base64_decode`
- **Sorting:** `sort_by`, `sort_desc`, `binary_search`
- **Random:** `random`, `random_int`, `shuffle`, `sample`, `choice`
- **Map utilities:** `merge`, `pick`, `omit`
- **Type checking:** `is_null`, `is_number`, `is_text`, `is_list`, `is_map`
- **Output:** `print` (multi-argument)

**Infrastructure:**

- User-defined functions (`MOLFunction`) are now first-class Python callables — can be passed to `map`, `filter`, `reduce`, etc.
- MkDocs Material documentation site with 20+ pages
- Total stdlib: 90+ functions
- Tests: 68 passing (25 new)

## [0.2.0] - 2026-02-09

### Added

- **Pipe operator `|>`** — chain operations left-to-right
- **Auto-tracing** — pipe chains of 3+ stages automatically print timing and type info
- **Guard assertions** — `guard condition : "message"`
- **Named pipelines** — `pipeline name(params) ... end`
- **RAG types:** `Document`, `Chunk`, `Embedding`, `VectorStore`
- **15 new functions:** `load_text`, `chunk`, `embed`, `store`, `retrieve`, `cosine_sim`, `think`, `recall`, `classify`, `summarize`, `display`, `tap`, `assert_min`, `assert_not_null`, `Chunk` constructor
- CLI flags: `--trace` / `--no-trace`
- New examples: `07_pipeline.mol`, `08_rag_pipeline.mol`
- VS Code extension updated with new keywords and functions
- Tests: 43 passing (22 new)

## [0.1.0] - 2026-02-08

### Added

- LALR parser with Lark grammar (131 rules)
- Core interpreter with visitor pattern
- Types: Number, Text, Bool, List, Map, null
- Domain types: Thought, Memory, Node, Stream
- Control flow: if/elif/else, while, for
- Functions with closures and recursion
- Event system: trigger, listen, emit
- Neural primitives: link, evolve, process
- Access control security model
- Type annotations: `let x: Type be value`
- Python transpiler
- JavaScript transpiler
- CLI: run, parse, transpile, repl, version
- VS Code extension with TextMate grammar + snippets
- 21 tests, 6 examples, 6 tutorials
- Comprehensive documentation
