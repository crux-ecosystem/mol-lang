# Why MOL?

## The Problem

Every AI pipeline today looks like this:

```python
# Python: 50+ lines of glue code
from langchain import ...
from chromadb import ...
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

loader = TextLoader("data.txt")
docs = loader.load()
logger.debug(f"Loaded {len(docs)} docs")

splitter = RecursiveCharacterTextSplitter(chunk_size=512)
chunks = splitter.split_documents(docs)
logger.debug(f"Split into {len(chunks)} chunks")

embeddings = OpenAIEmbeddings()
vectors = embeddings.embed_documents([c.page_content for c in chunks])
logger.debug(f"Embedded {len(vectors)} vectors")

db = Chroma.from_documents(chunks, embeddings)
results = db.similarity_search("query", k=5)
logger.debug(f"Found {len(results)} results")
```

You're writing **glue code**, not logic. And you added `logger.debug()` everywhere just to see what happened.

## The MOL Solution

```text
"data.txt"
  |> load_text
  |> chunk(512)
  |> embed
  |> store("index")
  |> retrieve("query", 5)
```

That's it. Five lines. **Auto-tracing** shows you every step automatically:

```text
┌─ Pipeline Trace ──────────────────────────────────────
│ 0.  input               ─  Text("data.txt")
│ 1.  load_text        0.1ms  → Document(...)
│ 2.  chunk(..)        0.0ms  → List<3 chunks>
│ 3.  embed            0.2ms  → List<3 embeddings>
│ 4.  store(..)        0.1ms  → VectorStore("index")
│ 5.  retrieve(..)     0.1ms  → List<5 docs>
└─ 5 steps · 0.5ms total ───────────────────────────
```

No logging setup. No debug prints. **It's built into the language.**

## How MOL Compares

| Feature | Python | Elixir | F# | Rust | **MOL** |
|---|---|---|---|---|---|
| Pipe operator `\|>` | No | Yes | Yes | No | **Yes** |
| Auto-tracing | No | No | No | No | **Yes** |
| AI domain types | No | No | No | No | **Yes** |
| RAG built-in | No | No | No | No | **Yes** |
| Reads like English | No | Partial | No | No | **Yes** |
| Transpiles to JS+Python | N/A | No | No | No | **Yes** |

## Key Advantages

### 1. Pipeline Visibility

Other languages with `|>` (Elixir, F#) still make you add logging manually. MOL auto-traces any pipe chain with 3+ stages.

### 2. English-Like Syntax

```text
let name be "MOL"
set version to 1.0
if name is "MOL" then
  show "Welcome!"
end
```

No curly braces. No semicolons. It reads like pseudocode.

### 3. AI-Native Types

```text
let thought be Thought("idea", confidence: 0.9)
let doc be Document("content", source: "wiki")
let vec be Embedding("hello", model: "default")
```

These aren't dicts or classes — they're **language-level types** with built-in behavior.

### 4. Safety Built In

```text
guard score >= 0 : "Score cannot be negative"
guard len(items) > 0 : "List must not be empty"
```

Guard assertions halt with clear messages. No unchecked nulls or silent failures.

### 5. Write Once, Run Anywhere

```bash
mol run app.mol              # Run directly
mol transpile app.mol -t py  # Generate Python
mol transpile app.mol -t js  # Generate JavaScript
mol build app.mol            # Compile to browser HTML
```

One `.mol` file targets three runtimes.

## Who Is MOL For?

- **AI engineers** building RAG pipelines who want visibility
- **Data scientists** who want readable data transformations
- **Educators** teaching programming with natural-syntax language
- **Startups** building AI products that need to move fast
- **Anyone** tired of writing logging boilerplate

## Try It Now

```bash
pipx install mol-lang
mol repl
```

Or visit the [online playground](https://mol.cruxlabx.in) — no installation required.
