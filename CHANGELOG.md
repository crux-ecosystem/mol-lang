# Changelog

All notable changes to MOL are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [2.0.3] — 2026-02-26

### Fixed

- Added Windows installation instructions (`pipx`, venv, PowerShell, CMD)
- Updated PyPI description with pipx-first install guide and PEP 668 warning
- Added platform-specific PATH troubleshooting (Linux, macOS, Windows)

---

## [2.0.2] — 2026-02-26

### Fixed

- Updated all install instructions to recommend `pipx install mol-lang` (fixes PEP 668 `externally-managed-environment` error on Python 3.12+)
- Updated sandbox error message to recommend `pipx` instead of `pip`
- Added installation troubleshooting guide with PATH fixes
- Added enterprise domain positioning: Use Cases page, 3 domain examples

---

## [2.0.1] — 2026-02-23

### 🔒 Security Patch

- **Fixed Full RCE vulnerability** — Python class hierarchy traversal via dunder attributes (`__class__.__subclasses__()`) allowed arbitrary command execution on the playground server. Blocked all `__`-prefixed attribute and method access in the interpreter. Applied in all modes (sandbox + local) for defense in depth.
- Added 11 security regression tests (213 total tests pass)

### Security Credits

- **[a11ce](https://github.com/a11ce)** — Reported the Full RCE vulnerability via responsible disclosure. Thank you for helping keep MOL safe.

---

## [1.1.0] — 2026-02-16

### 🧠 Smart Functions & Developer Experience

Making MOL easier to learn and use. Smart HOFs accept values, strings, and lambdas — no boilerplate needed.

### Added
- **`==` and `!=` operators** — Use familiar syntax alongside `is`/`is not`
- **Smart `filter()`** — Pass a value for equality match: `filter(30)`, a string for truthy property: `filter("active")`, or a lambda: `filter(fn(x) -> x > 5)`
- **Smart `map()`** — Pass a string to extract properties: `map("name")`
- **Smart `find()`** — `find(30)` for equality match
- **Smart `every()`/`some()`** — `every(3)` checks all equal 3
- **Smart `group_by()`** — `group_by("role")` groups by property
- **Smart `sort_by()`** — `sort_by("age")` sorts by property
- **`where()`** — Readable alias for `filter` in pipes
- **`select()`** — Readable alias for `map` in pipes
- **`reject()`** — Opposite of filter (remove matching elements)
- **`pluck()`** — Extract a property from list of objects
- **`each()`** — Execute side effects, return original list
- **`compact()`** — Remove null/false/0/empty values
- **`first()`/`last()`** — Get first/last element
- **`sum_list()`/`min_list()`/`max_list()`** — Aggregate functions
- **`contains()`** — Check list membership
- **Better error messages** — All HOFs now show hints with correct syntax

### Improved
- All HOF error messages include syntax hints (e.g., "Hint: use a lambda → filter(fn(x) -> x > 5)")
- Documentation rewritten with lambda-first examples
- 162 stdlib functions (up from 143)
- 202 tests (168 core + 34 sandbox), all passing

---

## [1.0.1] — 2025-06-14

### Fixed
- Fixed PyPI links pointing to private repository
- Fixed documentation site deployment
- Updated all docs to reference public `mol-lang` repo

---

## [1.0.0] — 2025-06-14

### 🎉 MOL 1.0 — First Stable Release

This is the first stable release of MOL, consolidating all features from v0.5.0 through v0.10.0 into a production-ready language. MOL 1.0 is the culmination of months of development — a complete programming language with 143 stdlib functions, native pipeline operators, auto-tracing, and a full ecosystem.

### Highlights

- **143 stdlib functions** — math, statistics, hashing, functional programming, file I/O, HTTP, concurrency
- **Native `|>` pipe operator** with auto-tracing (3+ stage chains automatically traced)
- **Structs with methods** — `struct`/`impl` for custom types with `self` binding
- **Pattern matching** — `match/with/when` expressions with guard clauses
- **Error handling** — `try/rescue/ensure` blocks
- **Generators** — `yield`-based lazy iterators with `.next()` and `.to_list()`
- **Concurrency** — `spawn/await`, channels, `parallel_map`, `wait_all`, `race`, mutex
- **Module system** — `use`/`export` with package manager (`mol init/install/publish`)
- **WASM compilation** — `mol build` to standalone HTML, JavaScript, or Node.js
- **File I/O** — 12 functions for reading, writing, and managing files
- **HTTP** — `fetch()` for HTTP requests, `serve()` for HTTP servers
- **Transpilation** — compile `.mol` to Python or JavaScript
- **AI domain types** — `Thought`, `Memory`, `Node`, `Stream`, `Document`, `Chunk`, `Embedding`, `VectorStore`
- **Docker support** — multi-mode image for run/repl/playground
- **VS Code extension** — full LSP server with autocomplete, hover docs, diagnostics, go-to-definition
- **Online playground** — [mol.cruxlabx.in](https://mol.cruxlabx.in) with HTTPS and sandbox security
- **181 tests** — comprehensive test suite covering all language features
- **Self-hosted codebase** — collections, algorithms, testing framework written in MOL itself

### Security (from v0.10.0)

- **Sandbox mode** — 26 dangerous functions blocked in playground
- **Execution timeout** — threaded 10-second kill switch
- **Rate limiting** — per-IP request throttling
- **Code size limits** — 50KB maximum
- **Restricted CORS** — only `mol.cruxlabx.in` origin allowed
- **Security endpoint** — `/api/security` for transparency

### Community Infrastructure

- `SECURITY.md` — vulnerability reporting policy
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `.github/ISSUE_TEMPLATE/bug_report.md` — structured bug reports
- `.github/ISSUE_TEMPLATE/feature_request.md` — feature proposals
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist

### Documentation

- **8 new guide pages**: Structs, Modules, Pattern Matching, Error Handling, Generators, Concurrency, Why MOL?, FAQ
- **Playground documentation** with API reference
- **Updated installation guide** with PyPI-first workflow
- **3 showcase examples**: Todo App, Data Pipeline, Chat Bot
- **20+ existing examples** updated and verified

### Changed

- Version: `0.10.0` → `1.0.0`
- PyPI status: `Beta` → `Production/Stable`
- Test suite: 181 tests (all passing)
- Stdlib: 143 built-in functions

---

## [0.10.0] — 2025-06-14

### Added — Playground Security Hardening

- **Sandbox mode** — 26 dangerous functions blocked when `sandbox=True`
- **Threaded execution timeout** — kills runaway programs after 10 seconds
- **Rate limiting** — per-IP request throttling (60/min run, 120/min general)
- **Code size limits** — maximum 50KB per submission
- **Restricted CORS** — locked to `https://mol.cruxlabx.in`
- **Security endpoint** — `GET /api/security` returns sandbox config
- **HTTPS deployment** — Let's Encrypt SSL via nginx reverse proxy
- **34 security tests** — comprehensive sandbox coverage

### Changed

- Test suite: 147 → 181 tests
- Playground URL: `https://mol.cruxlabx.in` (was HTTP)

---

## [0.9.1] — 2025-06-13

### Added — Power Features

- **Pattern Matching** (`match/with/when`):
  - `match expr with | pattern -> result end`
  - Guard clauses: `| pattern when condition -> result`
  - Wildcard: `_` matches anything
  - Multi-line arms with block syntax

- **Try/Rescue/Ensure** (error handling):
  - `try ... rescue err ... ensure ... end`
  - Named error binding
  - Ensure block always runs

- **Lambdas** (`fn`):
  - `fn(x) -> x * 2` — single-expression lambdas
  - Zero-arg: `fn() -> "hello"`
  - Works in `map`, `filter`, `sort_by`, and pipes

- **F-strings**:
  - `f"Hello {name}, you are {age} years old"`
  - Expression interpolation inside `{}`

- **Concurrency** (`spawn/await`):
  - `spawn do ... end` — run block in background thread
  - `await task` — wait for result
  - `wait_all(tasks)`, `race(tasks)`
  - `channel()`, `send(ch, val)`, `receive(ch)`
  - `parallel_map(list, func)`
  - `mutex()`, `lock_acquire()`, `lock_release()`

- **New stdlib** (23 new functions, ~143 total):
  - `sleep(ms)`, `spawn`, `await`, `wait_all`, `race`
  - `channel`, `send`, `receive`
  - `parallel_map`, `mutex`, `lock_acquire`, `lock_release`
  - `flatten`, `zip`, `enumerate`, `chunk_list`
  - `starts_with`, `ends_with`, `pad_left`, `pad_right`
  - `compose`, `pipe` (functional combinators)

### Changed

- Test suite: 147 → 147 tests (refactored, no regressions)
- Grammar: added `match`, `when`, `fn`, `spawn`, `await`, `try`, `rescue`, `ensure`

---

### Added — Self-Hosted Codebase, Web Server, AI Core

- **Field & Index Mutation** (`set obj.field to val`, `set list[i] to val`):
  - `set self.x to 10` — mutate struct fields inside methods
  - `set arr[0] to 99` — assign to list/dict by index
  - `set dict["key"] to val` — assign to dictionary entries
  - `set obj.items[i] to val` — field+index combo
  - `set list[i]["key"] to val` — double-index assignment

- **New Stdlib Functions** (5 new, ~120 total):
  - `chars(text)` — split string into character list
  - `panic(msg)` — raise a runtime error
  - `json_parse(text)` — parse JSON string to MOL value
  - `json_stringify(value)` — convert MOL value to JSON string
  - `serve(port, handler)` — full HTTP server with REST support

- **Self-Hosted Standard Library** (6 modules in `codebase/std/`):
  - `collections.mol` — Stack, Queue, MolSet, Pair, LinkedList, range_iter
  - `algorithms.mol` — 22 sorting/searching/graph/functional algorithms
  - `string_utils.mol` — 19 text processing functions
  - `math_ext.mol` — 24 statistics/vector/matrix/number theory functions
  - `result.mol` — Result/Option monadic types (Ok/Err, Some/None)
  - `testing.mol` — test runner with assertions and suite management

- **IntraMind AI Core** (4 modules in `codebase/intramind/`):
  - `memory.mol` — ShortTermMemory, LongTermMemory, WorkingMemory
  - `knowledge.mol` — KnowledgeGraph with BFS path finding
  - `reasoning.mol` — InferenceEngine (forward chaining), Decision trees, GoalStack
  - `agent.mol` — Agent with think-act-observe loop, tool registration

- **CLI Applications** (3 apps in `codebase/apps/`):
  - `todo.mol` — full todo manager with JSON file persistence
  - `data_pipeline.mol` — functional data processing pipeline
  - `http_client.mol` — HTTP client with GET/POST support

- **Web API Server** (in `codebase/server/`):
  - `router.mol` — route matching with `:param` patterns
  - `middleware.mol` — CORS headers, request logging
  - `main.mol` — full REST API with CRUD for users

### Fixed

- **Self binding in struct methods** — parameters no longer overwrite `self`
- **ReturnSignal in try/rescue** — `return` inside `try` no longer caught by `rescue`
- **Dict missing key** — returns `null` instead of throwing KeyError
- **Zero-arg lambdas** — `fn() -> expr` now parses correctly
- **Multi-line export** — newlines between exported names now allowed
- **type_of for structs** — returns struct name instead of "MOLStructInstance"
- **split("", "")** — empty separator splits into character list

### Changed

- Test suite: 123 → 147 tests (24 new v0.9.0 tests)
- Stdlib: ~115 → ~120 built-in functions

---

## [0.8.0] — 2025-02-12

### Added — Structs, Generators, File I/O, HTTP, Better Errors

- **Structs with methods** (`struct`/`impl`):
  - `struct Point do x, y end` — define user-defined types
  - Constructor-style: `Point(10, 20)` or literal-style: `Point { x: 10, y: 20 }`
  - `impl Point do define method() ... end end` — attach methods with `self` binding
  - Field access: `p.x`, method calls: `p.distance(other)`
  - Runtime classes: `MOLStructDef`, `MOLStructInstance`

- **Generators/Iterators** (`yield`):
  - `yield expr` inside functions creates lazy generators
  - `gen.to_list()` — materialize generator to list
  - `gen.next()` — get next value
  - For-loop iteration over generators
  - Proper step-by-step generator execution with nested control flow support

- **Module system** (`export`):
  - `export name1, name2` — explicitly control module exports
  - Without `export`, all user-defined symbols are exported (backward compatible)
  - Works with existing `use "file.mol"` import system

- **File I/O** (12 new stdlib functions):
  - `read_file(path)`, `write_file(path, content)`, `append_file(path, content)`
  - `file_exists(path)`, `file_size(path)`, `delete_file(path)`
  - `make_dir(path)`, `list_dir(path)`
  - `path_join(...)`, `path_dir(path)`, `path_base(path)`, `path_ext(path)`

- **HTTP** (2 new stdlib functions):
  - `fetch(url, options?)` — HTTP requests with method/headers/body support
  - `url_encode(params)` — URL-encode query parameters
  - Auto-parses JSON responses, returns `{status, body, headers, ok}` map

- **Better error messages**:
  - Line/column tracking from parser through to runtime errors
  - Error messages include file name and line number: `[main.mol:5] Division by zero`
  - AST nodes carry line/column info from Lark's position propagation

- **Transpiler support** for all v0.8.0 features (Python + JavaScript targets)
- 21 new tests (123 total), new example: `examples/19_structs_modules.mol`

---

## [0.5.0] — 2026-02-11

### Added — Package Manager & WASM Compilation

- **Package Manager** (`mol/package_manager.py`):
  - `mol init` — create `mol.pkg.json` project manifest
  - `mol install <pkg>` — install packages from registry or built-ins
  - `mol uninstall <pkg>` — remove installed packages
  - `mol list` — list installed packages
  - `mol search <query>` — search the registry
  - `mol publish` — package and prepare for publishing
  - 7 built-in packages: `std`, `math`, `text`, `collections`, `crypto`, `random`, `rag`
  - Dependency lockfile (`mol.lock.json`)
  - GitHub-based registry support with offline fallback

- **`use` statement** — Module import system:
  - `use "math"` — import all exports from a package
  - `use "math" : sin, cos` — import specific symbols
  - `use "pkg" as P` — import with namespace alias
  - `use "./file.mol"` — import local MOL files
  - New grammar rules, AST node (`UseStmt`), parser, interpreter, and transpiler support

- **WASM/Browser Compilation** (`mol/wasm_builder.py`):
  - `mol build file.mol` — compile to standalone HTML with embedded JS (default)
  - `mol build file.mol --target js` — standalone JavaScript file
  - `mol build file.mol --target node` — Node.js module
  - `--minify` flag for production builds
  - `--output/-o` for custom output path
  - Professional browser UI with dark terminal theme

- **MOL JavaScript Runtime** (`mol/runtime.js`):
  - Complete port of 90+ stdlib functions to JavaScript
  - Domain types: Thought, Memory, Node, Stream
  - Built-in module system (`__mol_require__`)
  - All math, text, collections, crypto, random, and RAG functions
  - Works in both browser and Node.js environments

- **JS Transpiler** — completed missing statement handlers:
  - `LinkStmt`, `ProcessStmt`, `AccessStmt`, `SyncStmt`
  - `EvolveStmt`, `EmitStmt`, `ListenStmt`, `BlockStmt`
  - `UseStmt` (maps to `__mol_require__`)

- **2 new examples:**
  - `15_packages.mol` — Package imports and modular code
  - `16_browser.mol` — Full browser-ready program demo

### Changed

- Grammar updated with `use` and `as` keywords
- `NAME` terminal regex excludes `use` and `as`
- Tests: 68 passing (no regressions)
- All 16 examples verified

---

## [0.4.0] — 2026-02-11

### Added — Docker, Examples, Distribution & LSP

- **Language Server Protocol (LSP):** Full LSP server (`mol/lsp_server.py`) with 6 capabilities:
  - **Autocomplete:** 112 stdlib functions, 35 keywords, user-defined symbols, 9 code snippets, pipe-aware suggestions
  - **Hover documentation:** Rich Markdown docs with parameters, return types, and code examples
  - **Diagnostics:** Real-time parse error reporting on open/change/save
  - **Signature help:** Active parameter tracking for all stdlib functions
  - **Go-to-definition:** Jump to user-defined variables and functions
  - **Document symbols:** Outline view of functions and variables
- **VS Code LSP client extension:** TypeScript extension (`mol-vscode/`) with server lifecycle management, restart command, and run-file command
- **CLI subcommand:** `mol lsp` starts the language server via stdio
- **Docker support:** Multi-mode Docker image (`docker run mol run program.mol`, `docker run mol` for playground)
- **5 new examples:** Data processing pipelines, functional programming patterns, full RAG workflow, math/stats/hashing showcase, LLM integration simulation
- **Demo GIF:** Terminal recording showcasing MOL features for README
- **Demo program:** `examples/demo.mol` — concise feature showcase

### Changed

- Dockerfile uses Python 3.12-slim (f-string backslash support)
- Docker entrypoint supports: `playground`, `run`, `repl`, `version`, `parse`, `transpile`, `help`
- Docker image size: ~144 MB
- All 14 example programs verified passing
- Tests: 68 passing (no regressions)
- VS Code extension updated from v0.1.0 to v0.4.0 with LSP client

### Dependencies

- Added optional LSP dependencies: `pygls>=2.0`, `lsprotocol>=2024.0.0` (`pipx install 'mol-lang[lsp]'`)
- VS Code extension: `vscode-languageclient ^9.0.1`

### Infrastructure

- Published to PyPI: `pipx install mol-lang`
- Online playground deployed at https://mol.cruxlabx.in
- Blog post and social media launch materials
- Strategy document for distribution

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
