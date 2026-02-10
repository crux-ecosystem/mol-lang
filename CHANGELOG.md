# Changelog

All notable changes to MOL are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [0.3.0] — 2026-02-10

### Added — Universal Algorithms (42 new functions)

- **Functional programming:** `map`, `filter`, `reduce`, `find`, `every`, `some`, `group_by`
- **List operations:** `flatten`, `unique`, `zip`, `enumerate`, `count`, `find_index`, `take`, `drop`, `chunk_list`
- **Math:** `floor`, `ceil`, `log`, `sin`, `cos`, `tan`, `pow`, `clamp`, `lerp`, `pi`, `e`
- **Statistics:** `mean`, `median`, `stdev`, `variance`, `percentile`
- **String:** `starts_with`, `ends_with`, `pad_left`, `pad_right`, `repeat`, `char_at`, `index_of`, `format`
- **Hashing:** `hash` (SHA-256/MD5/SHA-1/SHA-512), `uuid`, `base64_encode`, `base64_decode`
- **Sorting:** `sort_by`, `sort_desc`, `binary_search`
- **Random:** `random`, `random_int`, `shuffle`, `sample`, `choice`
- **Maps:** `merge`, `pick`, `omit`
- **Type checks:** `is_null`, `is_number`, `is_text`, `is_list`, `is_map`
- **Output:** `print`

### Changed

- User-defined functions (`MOLFunction`) are now first-class Python callables
- Total stdlib: 90+ functions
- Tests: 68 passing (25 new)
- MkDocs Material documentation site with 20+ pages

---

## [0.2.0] — 2026-02-09

### Added — The Pipeline Release

**Pipeline Operator `|>`**
- Native pipe operator for left-to-right data flow
- Multi-stage chaining: `a |> f |> g |> h`
- Auto-tracing for chains with 3+ stages (timing, types, values)
- `--no-trace` CLI flag to disable tracing
- Pipe chains desugar to nested calls in transpiler output

**Pipeline Definitions**
- `pipeline name(params) ... end` — named, reusable data pipelines
- Functionally equivalent to `define` but signals intent for data processing

**Guard Assertions**
- `guard expr` — halt if falsy
- `guard expr : "message"` — halt with custom error message
- Raises `MOLGuardError` at runtime

**RAG Domain Types**
- `Document` — text document with source metadata
- `Chunk` — text fragment with index and source
- `Embedding` — 64-dimensional deterministic vector embedding
- `VectorStore` — in-memory vector index with cosine similarity search

**RAG Pipeline Functions (15 new)**
- `load_text(path)` — load file as Document
- `chunk(data, size)` — split text/Document into Chunks
- `embed(data, model)` — create Embedding(s) from text/Chunk/Document
- `store(data, name)` — store embeddings in named VectorStore
- `retrieve(query, store, top_k)` — similarity search
- `cosine_sim(a, b)` — cosine similarity between embeddings
- `think(data, prompt)` — synthesize Thought from data
- `recall(memory)` — recall Memory value
- `classify(text, ...cats)` — classify text into categories
- `summarize(text, max_len)` — summarize text
- `display(value)` — print and pass through for pipe chains
- `tap(value, label)` — labeled debug print, pass through
- `assert_min(value, threshold)` — assert value >= threshold
- `assert_not_null(value)` — assert not null

**New Keywords**
- `pipeline` — pipeline definition
- `guard` — guard assertion

**VS Code Extension Updates**
- Syntax highlighting for `pipeline`, `guard`, `|>` operator
- Highlighting for `Document`, `Chunk`, `Embedding`, `VectorStore` types
- Updated built-in function highlighting (15 new functions)

### Changed
- Version bumped to 0.2.0
- `pyproject.toml` — added `[tool.setuptools.packages.find]` to exclude `tutorial/` from package discovery
- Interpreter refactored — centralized `_invoke_callable()` for function calls
- Tests expanded from 21 to 43 (all passing)
- Examples expanded from 6 to 8

### Fixed
- Package discovery conflict with `tutorial/` directory

---

## [0.1.0] — 2026-02-08

### Added — Initial Release

**Core Language**
- Lark EBNF grammar with LALR parser
- AST with 30+ node types (dataclasses)
- Visitor-pattern interpreter with scoped environments
- Closures and recursion support
- Integer/float arithmetic with safe division

**Syntax**
- `show` — print statement
- `let name be value` — variable declaration (inferred type)
- `let name : Type be value` — typed declaration
- `set name to value` — assignment
- `if/elif/else/end`, `while/do/end`, `for/in/do/end` — control flow
- `define name(params) ... end` — function definition
- `return` — return statement
- `begin ... end` — block statement
- `-- comment` — single-line comments

**Domain Types**
- `Thought` — cognitive unit with confidence, tags, linking
- `Memory` — persistent key-value with strength and decay
- `Node` — neural graph vertex with weight, connections, evolution
- `Stream` — real-time data buffer with subscribe/emit

**Domain Commands**
- `trigger` — fire events
- `listen ... do ... end` — event listener
- `link A to B` — connect nodes/thoughts
- `process X with Y` — activate and adjust
- `access "resource"` — checked resource access
- `sync` — synchronize stream
- `evolve` — evolve node (weight * 1.1, generation + 1)
- `emit` — emit data

**Safety Rails**
- `SecurityContext` — allow-list based access control
- `MOLSecurityError` — unauthorized access
- `MOLTypeError` — type annotation violations
- Infinite loop detection (1M iteration cap)

**Standard Library (30+ functions)**
- General: `len`, `type_of`, `to_text`, `to_number`, `range`, `abs`, `round`, `sqrt`, `max`, `min`, `sum`
- Collections: `sort`, `reverse`, `push`, `pop`, `keys`, `values`, `contains`, `join`, `slice`
- Strings: `split`, `upper`, `lower`, `trim`, `replace`
- Serialization: `to_json`, `from_json`, `inspect`
- Time: `clock`, `wait`
- Constructors: `Thought()`, `Memory()`, `Node()`, `Stream()`

**CLI**
- `mol run <file>` — run a .mol program
- `mol parse <file>` — show AST
- `mol transpile <file> --target python|js` — transpile
- `mol repl` — interactive REPL
- `mol version` — show version
- ANSI-colored ASCII banner

**Transpiler**
- Python code generation
- JavaScript code generation
- All statement and expression types supported

**VS Code Extension**
- TextMate grammar for syntax highlighting
- Language configuration (folding, indentation, auto-close)
- 20+ code snippets

**Testing**
- 21 tests covering all language features
- 6 example programs

**Documentation**
- README with full language reference
- ROADMAP for v0.2.0–v1.0.0

### Fixed (during v0.1.0 development)
- Keywords being parsed as variable names (negative lookahead regex)
- `--` comments parsed as double-minus operator (LALR + priority `.2`)
- Multi-line list/map literals not parsing (added `_NL?` inside brackets)
- `setuptools.backends._legacy` error (switched to `setuptools.build_meta`)
