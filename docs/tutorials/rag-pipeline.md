# Tutorial: RAG Pipeline

Build a complete Retrieval-Augmented Generation pipeline in MOL.

## What You'll Build

A system that:

1. Loads a document
2. Chunks it into segments
3. Creates vector embeddings
4. Stores them in a searchable index
5. Retrieves relevant chunks for a query
6. Generates an answer with confidence scoring
7. Validates the result

## Step 1: Create a Document

```text
let content be "Machine learning is a subset of artificial intelligence. It enables computers to learn from data without explicit programming. Deep learning uses neural networks with many layers. Natural language processing helps machines understand human language. Retrieval augmented generation combines search with language models."

let doc be Document("knowledge.txt", content)
show doc
```

```text
<Document:a1b2c3d4 "knowledge.txt" 339B>
```

## Step 2: The Ingestion Pipeline

```text
-- One expression: Document → Chunks → Embeddings → VectorStore
let index be doc |> chunk(80) |> embed("mol-sim-v1") |> store("knowledge_base")
```

Auto-trace output:
```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  <Document "knowledge.txt" 339B>
  │ 1.  chunk(80)           0.1ms  → List<5 Chunks>
  │ 2.  embed("mol-sim-v1") 0.2ms  → List<5 Embeddings>
  │ 3.  store("kb")         0.0ms  → <VectorStore "kb" 5 vectors>
  └─ 3 steps · 0.4ms total ───────────────────────────
```

## Step 3: Query

```text
let query be "What is deep learning?"
let results be retrieve(query, "knowledge_base", 3)

show "Top results:"
for r in results do
  show "  Score: " + to_text(r.score) + " — " + r.text
end
```

## Step 4: Generate Answer

```text
let answer be results |> think("answer the query")

show "Answer: " + answer.content
show "Confidence: " + to_text(answer.confidence)
```

## Step 5: Validate

```text
guard answer.confidence > 0.5 : "Answer quality too low"
show "✓ Answer validated"
```

## Step 6: Make It Reusable

```text
pipeline rag_query(question)
  let hits be retrieve(question, "knowledge_base", 3)
  let response be hits |> think(question)
  guard response.confidence > 0.4 : "Low confidence"
  return response
end

-- Use it
let a1 be rag_query("What is deep learning?")
let a2 be rag_query("How do machines understand language?")
show a1.content
show a2.content
```

## Complete Program

```text
-- ═══ MOL RAG Pipeline ═══

-- Load knowledge
let doc be Document("knowledge.txt", "Machine learning is a subset of artificial intelligence. It enables computers to learn from data. Deep learning uses neural networks. NLP helps machines understand language. RAG combines search with language models.")

-- Ingest: chunk → embed → store
let index be doc |> chunk(80) |> embed("mol-sim-v1") |> store("kb")
show "Indexed " + to_text(len(index.entries)) + " vectors"

-- Query pipeline
pipeline ask(question)
  let hits be retrieve(question, "kb", 3)
  let answer be hits |> think(question)
  guard answer.confidence > 0.4 : "Low quality answer"
  return answer
end

-- Ask questions
let q1 be ask("What is deep learning?")
show "Q: What is deep learning?"
show "A: " + q1.content
show "Confidence: " + to_text(q1.confidence)
show ""

let q2 be ask("How do machines understand language?")
show "Q: How do machines understand language?"
show "A: " + q2.content
```

## Run It

```bash
mol run rag_pipeline.mol
```

## Key Takeaways

1. **Pipeline operator** `|>` chains operations cleanly
2. **Auto-tracing** shows what happened at each step
3. **Guard** validates quality before proceeding
4. **Named pipelines** make logic reusable
5. **Domain types** (Document, Chunk, Embedding, VectorStore) are first-class
