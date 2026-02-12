# MOL Roadmap — RAG Pipeline & Sovereign AI for IntraMind

## Vision

MOL becomes the **control language** for IntraMind's sovereign AI stack.
Instead of writing Python/JS glue code for RAG pipelines, you write MOL
and it compiles/transpiles to whatever runtime you need.

---

## Current Status (v0.1.0) — DONE

- [x] Grammar specification (Lark EBNF)
- [x] Lexer/Parser (LALR)
- [x] AST node system (30+ node types)
- [x] Interpreter (Visitor pattern, scoped environments)
- [x] Domain types: Thought, Memory, Node, Stream
- [x] Standard library (30+ functions)
- [x] Safety rails (SecurityContext, type enforcement)
- [x] Event system (trigger/listen)
- [x] Transpiler (Python, JavaScript)
- [x] CLI (run, parse, transpile, repl)
- [x] VS Code extension (syntax highlighting, snippets)
- [x] 21 passing tests, 6 example programs, 5 tutorials

---

## Phase 2: RAG Pipeline Native (v0.2.0)

**Goal:** MOL understands RAG pipelines as first-class constructs.

### New Types
```mol
-- Embedding: vector representation
let vec be Embedding("hello world", model: "bge-large")

-- Document: structured content with metadata
let doc be Document("content here", source: "wiki", score: 0.95)

-- Chunk: a piece of a document
let chunk be Chunk(doc, start: 0, end: 512, overlap: 50)

-- Prompt: template with variables
let prompt be Prompt("Answer {question} using {context}")

-- Agent: autonomous AI unit
let assistant be Agent("helper", model: "local-llm", tools: ["search", "calc"])
```

### New Pipeline Syntax
```mol
-- Declarative pipeline definition
pipeline RAGSearch
  stage embed    : Embedder(model: "bge-large")
  stage store    : VectorStore(engine: "faiss", dims: 1024)
  stage retrieve : Retriever(top_k: 5, threshold: 0.7)
  stage rerank   : Reranker(model: "cross-encoder")
  stage generate : Generator(model: "local-llm", max_tokens: 500)
  stage guard    : SafetyFilter(block: ["pii", "harmful"])

  flow: embed → store → retrieve → rerank → generate → guard
end

-- Run the pipeline
let result be RAGSearch.run("What is sovereign AI?")
show result.answer
show result.sources
show result.confidence
```

### New Built-in Functions
```mol
embed(text, model)          -- Generate embeddings
search(query, top_k)        -- Vector similarity search
chunk(document, size, overlap) -- Split document into chunks
rerank(docs, query)         -- Rerank by relevance
generate(prompt, context)   -- Generate LLM response
tokenize(text)              -- Count/split tokens
cosine_sim(vec_a, vec_b)    -- Vector similarity
```

---

## Phase 3: Sovereign AI Features (v0.3.0)

**Goal:** Full sovereign AI capabilities — no external API calls needed.

### Data Sovereignty
```mol
-- All data stays local
sovereign mode "strict"   -- No external API calls allowed

-- Local model registry
register_model "llm" at "/models/mistral-7b"
register_model "embedder" at "/models/bge-large"

-- Encrypted memory
let secret be SecureMemory("api_key", encrypted: true)
```

### Agent System
```mol
-- Define autonomous agents
agent DataCollector
  role: "Gather and index documents"
  tools: ["web_scrape", "file_read", "db_query"]
  memory: persistent
  
  on "new_document" do
    let doc be Document(event.data)
    let chunks be chunk(doc, 512, 50)
    for c in chunks do
      embed c
      store c
    end
  end
end

-- Multi-agent orchestration
agent Orchestrator
  role: "Route queries to specialized agents"
  agents: [DataCollector, Searcher, Responder]
  
  on "user_query" do
    let plan be think("Break down: " + event.data)
    for step in plan.steps do
      delegate step.agent, step.task
    end
  end
end
```

### Knowledge Graph
```mol
-- Native knowledge graph operations
let entity be Entity("IntraMind", type: "Product")
let relation be Relation(entity, "built_by", Entity("CruxLabx"))

graph.add(entity)
graph.add(relation)

-- Query the graph
let results be graph.query("Who built IntraMind?")
```

---

## Phase 4: Production Runtime (v0.4.0)

**Goal:** MOL programs run in production with real performance.

### Async/Concurrent Pipelines
```mol
-- Parallel execution
parallel do
  let docs1 be search("topic A", top_k: 10)
  let docs2 be search("topic B", top_k: 10)
end

-- Async stream processing
stream_process "incoming_queries" do
  let result be RAGSearch.run(event.data)
  emit result to "responses"
end
```

### Real Database Integration
```mol
-- Vector store backends
let store be VectorStore(
  engine: "faiss",      -- or "milvus", "chromadb", "qdrant"
  dims: 1024,
  index_type: "HNSW"
)

-- Document store
let docs be DocStore(
  engine: "sqlite",     -- or "postgres", "mongo"
  path: "./data/knowledge.db"
)
```

### HTTP API Server
```mol
-- Expose MOL pipelines as APIs
server "IntraMind API" on 8080

  route "/query" method "POST" do
    let query be request.body.query
    access "mind_core"
    let result be RAGSearch.run(query)
    respond 200 with to_json(result)
  end

  route "/health" method "GET" do
    respond 200 with {status: "ok", version: "0.4.0"}
  end

end
```

### Transpilation Targets
```mol
-- Compile to optimized targets
mol build app.mol --target python     -- FastAPI server
mol build app.mol --target javascript -- Node.js/Bun server
mol build app.mol --target rust       -- Native binary
mol build app.mol --target wasm       -- WebAssembly (browser)
```

---

## Phase 5: Ecosystem (v1.0.0)

- **mol package manager** — Share MOL modules (like npm/pip for MOL)
- **mol playground** — Browser-based IDE for MOL
- **mol notebook** — Jupyter-like notebooks for MOL
- **mol deploy** — One-command deployment to IntraMind cloud
- **mol test** — Built-in testing framework
- **mol docs** — Auto-generate docs from MOL code
- **mol debug** — Step-through debugger

---

## Why MOL Over Python for RAG?

| Aspect | Python | MOL |
|--------|--------|-----|
| RAG pipeline | 200+ lines of glue code | 10-line `pipeline...end` block |
| Security | Manual auth middleware | Built into `access` keyword |
| Type safety for AI | None (dicts everywhere) | `Thought`, `Document`, `Embedding` types |
| Node graph | NetworkX + custom code | Native `link`, `process`, `evolve` |
| Event system | Celery/RabbitMQ + config | Native `trigger`/`listen` |
| Portability | Rewrite for JS/Rust | `mol build --target js` |
| Data sovereignty | Manual enforcement | `sovereign mode "strict"` |

---

## Implementation Priority

1. **v0.2.0** — `Document`, `Embedding`, `Chunk` types + `pipeline` syntax
2. **v0.3.0** — `agent` blocks + local model integration
3. **v0.4.0** — Real vector DB + HTTP server + async
4. **v1.0.0** — Package manager + ecosystem

Each phase builds on the last. The foundation (v0.1.0) is complete and solid.
