# Domain Types

MOL has 8 built-in domain types designed for cognitive computing and AI applications.

## Base: MolObject

Every domain type inherits from `MolObject`, which provides:

- `_id` — unique 8-character hex identifier
- `_created_at` — creation timestamp
- `_access_level` — security level (default: `"public"`)

## Thought

An idea with a confidence score.

```text
let idea be Thought("Neural networks learn patterns", 0.87)
show idea.content       -- "Neural networks learn patterns"
show idea.confidence    -- 0.87
show type_of(idea)      -- "Thought"
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | Text | The thought content |
| `confidence` | Number | 0.0 — 1.0 confidence score |
| `tags` | List | Tags (added via `.tag()`) |
| `linked_thoughts` | List | Linked thoughts |

**Operations:**

```text
-- Use in pipes with think()
let response be "AI is transforming healthcare"
  |> think("analyze this statement")
show response.confidence
```

## Memory

Labeled storage with strength decay.

```text
let mem be Memory("session_key", "important data")
show mem.key            -- "session_key"
show mem.value          -- "important data"
show mem.strength       -- 1.0 (initial)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `key` | Text | Memory label |
| `value` | any | Stored value |
| `strength` | Number | Recall strength (decays over time) |
| `recall_count` | Number | Times recalled |

**Operations:**

```text
let value be recall(mem)    -- Boosts strength by 0.1
```

## Node

A neural network node with connections.

```text
let neuron be Node("cortex", 0.75)
show neuron.label       -- "cortex"
show neuron.weight      -- 0.75
show neuron.generation  -- 0
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `label` | Text | Node name |
| `weight` | Number | Connection weight |
| `connections` | List | Connected nodes |
| `active` | Bool | Active state |
| `generation` | Number | Evolution generation |

**Operations:**

```text
let a be Node("input", 0.5)
let b be Node("hidden", 0.8)
link a to b              -- Connect nodes
evolve a                 -- weight *= 1.1, generation += 1
```

## Stream

Event stream with publish/subscribe.

```text
let s be Stream("data_feed")
listen "data_ready" do
  show "Data arrived!"
end
emit "data_ready"        -- Triggers listener
```

## Document

A source document for pipeline processing.

```text
let doc be Document("paper.txt", "Machine learning is...")
show doc.source          -- "paper.txt"
show doc.content         -- "Machine learning is..."
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `source` | Text | File name or URL |
| `content` | Text | Document text |
| `metadata` | Map | Additional metadata |

**Use in pipes:**

```text
let index be Document("data.txt", text)
  |> chunk(512)
  |> embed("model-v1")
  |> store("index")
```

## Chunk

A segment of a document.

```text
let chunks be chunk(doc, 100)
show len(chunks)
show chunks[0].content
show chunks[0].index     -- 0
show chunks[0].source    -- "paper.txt"
```

## Embedding

A vector representation of text.

```text
let emb be Embedding("hello world", "mol-sim-v1")
show emb.text            -- "hello world"
show emb.model           -- "mol-sim-v1"
show emb.dimensions      -- 64
```

!!! info "Deterministic Vectors"
    MOL generates deterministic 64-dimensional pseudo-embeddings using SHA-256 hashing. Same text always produces the same vector — useful for testing and reproducible pipelines.

## VectorStore

A searchable index of embeddings with cosine similarity search.

```text
-- Build an index
let index be doc |> chunk(100) |> embed("v1") |> store("kb")

-- Search
let results be retrieve("query text", "kb", 3)
for r in results do
  show r.text + " (score: " + to_text(r.score) + ")"
end
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | Text | Store name |
| `entries` | List | Stored vectors |

## Type Checking

```text
show type_of(Thought("x", 0.5))        -- "Thought"
show type_of(Document("f", "content"))  -- "Document"
show type_of(Node("n", 0.5))           -- "Node"

-- Type-annotated declarations
let t: Thought be Thought("idea", 0.9)  -- ✓
```
