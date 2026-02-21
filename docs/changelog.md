# Changelog

All notable changes to MOL are documented here.

## [2.0.0] - 2026-02-21

### Added — Kernel-Grade Evolution (56 new functions, 5 new systems)

**🛡️ Memory Safety — Borrow Checker (`borrow_checker.py`)**

- Rust-inspired ownership model: `own`, `borrow`, `borrow_mut`, `transfer`, `release`
- Lifetime scopes with automatic resource cleanup
- Use-after-free detection, buffer overflow prevention
- AI-assisted safety analysis
- New AST nodes: `OwnDeclare`, `BorrowDeclare`, `BorrowMutDeclare`, `MoveOwnership`, `DropValue`, `LifetimeScope`

**📐 Native Vector Engine (`vector_engine.py`) — 25 functions**

- First-class `Vector` type backed by `array.array` for SIMD-like performance
- Arithmetic: `vec_add`, `vec_sub`, `vec_scale`, `vec_concat`
- Similarity: `vec_dot`, `vec_cosine`, `vec_distance`, `vec_normalize`
- Factory: `vec`, `vec_zeros`, `vec_ones`, `vec_rand`, `vec_from_text`
- ML: `vec_softmax`, `vec_relu`, `vec_quantize` (int8 compression)
- ANN search: `vec_index`, `vec_index_add`, `vec_index_search` with LSH bucketing
- Batch operations: `vec_batch_cosine`, `vec_top_k`

**🔐 Integrated Encryption (`encryption.py`) — 15 functions**

- Homomorphic encryption (Paillier scheme): `crypto_keygen`, `he_encrypt`, `he_decrypt`, `he_add`, `he_sub`, `he_mul_scalar`
- Symmetric encryption (HMAC-based): `sym_keygen`, `sym_encrypt`, `sym_decrypt`
- Zero-knowledge proofs: `zk_commit`, `zk_verify`, `zk_prove`
- Utilities: `secure_hash`, `secure_random`, `constant_time_compare`

**⚡ Self-Optimizing JIT Tracing (`jit_tracer.py`) — 7 functions**

- Hot-path detection with configurable thresholds (50/100 calls)
- Type profiling and specialization (Int, Float, String fast-paths)
- Inline caching and constant folding
- Functions: `jit_stats`, `jit_hot_paths`, `jit_profile`, `jit_reset`, `jit_warmup`, `jit_enabled`, `jit_toggle`

**🌐 Multi-Node Swarm Runtime (`swarm_runtime.py`) — 12 functions**

- Consistent hash ring for data distribution
- Functions: `swarm_init`, `swarm_shard`, `swarm_map`, `swarm_reduce`, `swarm_gather`
- Communication: `swarm_broadcast`, `swarm_scatter`
- Management: `swarm_health`, `swarm_nodes`, `swarm_rebalance`, `swarm_add_node`, `swarm_remove_node`
- ThreadPoolExecutor-based parallel execution with fault tolerance

**Infrastructure:**

- Grammar updated with ownership syntax rules
- Parser extended with 6 new transformer methods
- Interpreter extended with 7 new exec methods + JIT integration in all function calls
- Type system extended: `Vector`, `QuantizedVector`, `VectorIndex`, `EncryptedValue`, `EncryptedVector`, `EncryptedMemory`, `CryptoKeyPair`, `SwarmCluster`
- Total stdlib: **210 functions** (up from 162)
- 6 new examples: `20_vector_engine`, `21_encryption`, `22_memory_safety`, `23_jit_tracing`, `24_swarm_runtime`, `25_sovereign_pipeline`
- All 168 existing tests pass with zero regressions

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
