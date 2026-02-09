# MOL Language Specification v0.2.0

**Status:** Active Development
**Author:** Mounesh — CruxLabx / IntraMind
**File Extension:** `.mol`

---

## 1. Lexical Structure

### 1.1 Character Set

MOL source files are UTF-8 encoded text.

### 1.2 Comments

```ebnf
COMMENT ::= '--' <any character except newline>*
```

Comments begin with `--` and extend to the end of the line. There are no multi-line comments.

### 1.3 Keywords

The following identifiers are reserved and cannot be used as variable or function names:

```
if    then   elif   else    end     while   for    in
do    define return begin   let     be      set    to
show  and    or     not     is      true    false  null
trigger link process access sync   evolve  emit   listen
with  pipeline guard
```

### 1.4 Identifiers

```ebnf
NAME ::= [a-zA-Z_][a-zA-Z0-9_]*    (excluding keywords)
```

### 1.5 Literals

| Type | Pattern | Examples |
|---|---|---|
| Number | `[0-9]+` or `[0-9]+.[0-9]+` | `42`, `3.14` |
| String | `"<characters>"` with `\\` escapes | `"hello"`, `"line\n"` |
| Boolean | `true` or `false` | `true` |
| Null | `null` | `null` |
| List | `[expr, expr, ...]` | `[1, 2, 3]` |
| Map | `{key: expr, ...}` | `{name: "mol", v: 2}` |

### 1.6 Operators

| Category | Operators |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Comparison | `is`, `is not`, `>`, `<`, `>=`, `<=` |
| Logical | `and`, `or`, `not` |
| Pipe | `\|>` |
| Access | `.` (field), `[]` (index) |

---

## 2. Type System

### 2.1 Primitive Types

| Type Name | Values | Notes |
|---|---|---|
| `Number` | Integer or float | `42`, `3.14`. Integer arithmetic stays integer. |
| `Text` | String | `"hello"` |
| `Bool` | `true`, `false` | |
| `List` | Ordered collection | `[1, 2, 3]` |
| `Map` | Key-value pairs | `{a: 1, b: 2}` |
| `null` | Absence of value | |

### 2.2 Domain Types

| Type | Fields | Description |
|---|---|---|
| `Thought` | `content: Text`, `confidence: Number`, `tags: List` | Cognitive unit |
| `Memory` | `key: Text`, `value: any`, `strength: Number` | Persistent store |
| `Node` | `label: Text`, `weight: Number`, `connections: List`, `active: Bool`, `generation: Number` | Graph vertex |
| `Stream` | `name: Text`, `buffer: List` | Data flow |
| `Document` | `source: Text`, `content: Text`, `metadata: Map` | Text document |
| `Chunk` | `content: Text`, `index: Number`, `source: Text` | Text fragment |
| `Embedding` | `text: Text`, `model: Text`, `vector: List`, `dimensions: Number` | Vector representation |
| `VectorStore` | `name: Text`, `entries: List` | Vector index |

### 2.3 Type Annotations

Optional annotations enforce type at assignment:

```mol
let x : Number be 42       -- OK
let x : Number be "hello"  -- MOLTypeError
```

---

## 3. Grammar (EBNF)

### 3.1 Program

```ebnf
program     ::= (NL* statement)* NL*
```

### 3.2 Statements

```ebnf
statement   ::= show_stmt | declare_stmt | assign_stmt
              | if_stmt | while_stmt | for_stmt
              | func_def | return_stmt
              | trigger_stmt | link_stmt | process_stmt
              | access_stmt | sync_stmt | evolve_stmt
              | emit_stmt | listen_stmt
              | block_stmt | guard_stmt | pipeline_def
              | expr_stmt
```

### 3.3 Variable Declaration

```ebnf
declare_stmt ::= 'let' NAME 'be' expr
               | 'let' NAME ':' type_name 'be' expr
```

### 3.4 Assignment

```ebnf
assign_stmt  ::= 'set' NAME 'to' expr
```

### 3.5 Control Flow

```ebnf
if_stmt      ::= 'if' expr 'then' NL block elif* else? 'end'
elif         ::= 'elif' expr 'then' NL block
else         ::= 'else' NL block

while_stmt   ::= 'while' expr 'do' NL block 'end'
for_stmt     ::= 'for' NAME 'in' expr 'do' NL block 'end'
```

### 3.6 Functions

```ebnf
func_def     ::= 'define' NAME '(' param_list? ')' NL block 'end'
param_list   ::= param (',' param)*
param        ::= NAME (':' type_name)?
return_stmt  ::= 'return' expr?
```

### 3.7 Pipeline Definition

```ebnf
pipeline_def ::= 'pipeline' NAME '(' param_list? ')' NL block 'end'
```

Pipelines are syntactically identical to functions but semantically indicate auto-traced data processing.

### 3.8 Guard Statement

```ebnf
guard_stmt   ::= 'guard' expr
               | 'guard' expr ':' STRING
```

Halts execution with `MOLGuardError` if the expression is falsy. Optional message provides context.

### 3.9 Domain Statements

```ebnf
trigger_stmt ::= 'trigger' expr
link_stmt    ::= 'link' expr 'to' expr
process_stmt ::= 'process' expr ('with' expr)?
access_stmt  ::= 'access' expr
sync_stmt    ::= 'sync' expr
evolve_stmt  ::= 'evolve' expr
emit_stmt    ::= 'emit' expr
listen_stmt  ::= 'listen' expr 'do' NL block 'end'
```

### 3.10 Expressions

```ebnf
expr         ::= pipe_chain
pipe_chain   ::= or_expr ('|>' NL? or_expr)*

or_expr      ::= and_expr ('or' and_expr)*
and_expr     ::= not_expr ('and' not_expr)*
not_expr     ::= 'not' not_expr | comparison
comparison   ::= addition (comp_op addition)*
comp_op      ::= 'is' | 'is' 'not' | '>' | '<' | '>=' | '<='

addition     ::= multiplication (('+' | '-') multiplication)*
multiplication ::= unary (('*' | '/' | '%') unary)*
unary        ::= '-' unary | atom

atom         ::= NUMBER | STRING | 'true' | 'false' | 'null'
               | list_lit | map_lit
               | NAME '(' arg_list? ')'        -- function call
               | atom '.' NAME '(' arg_list? ')'  -- method call
               | atom '.' NAME                 -- field access
               | atom '[' expr ']'             -- index access
               | NAME                          -- variable ref
               | '(' expr ')'                 -- group
```

### 3.11 Operator Precedence (low → high)

| Level | Operator | Associativity |
|---|---|---|
| 1 | `\|>` | Left |
| 2 | `or` | Left |
| 3 | `and` | Left |
| 4 | `not` | Prefix |
| 5 | `is`, `is not`, `>`, `<`, `>=`, `<=` | Left |
| 6 | `+`, `-` | Left |
| 7 | `*`, `/`, `%` | Left |
| 8 | Unary `-` | Prefix |
| 9 | `.field`, `[index]`, `.method()`, `call()` | Left |

---

## 4. Semantics

### 4.1 Scoping

MOL uses lexical scoping with a parent-chain environment model. Each block (`if`, `while`, `for`, function body) creates a new scope. Variables are resolved by searching the current scope, then parent scopes.

### 4.2 Functions

Functions are first-class values. They capture their defining environment (closures). Recursion is supported.

```mol
define fact(n)
  if n <= 1 then return 1 end
  return n * fact(n - 1)
end
```

### 4.3 Pipe Semantics

The pipe operator `|>` passes the left-hand value as the **first argument** to the right-hand function:

```mol
x |> f          -- equivalent to f(x)
x |> f(a, b)    -- equivalent to f(x, a, b)
x |> f |> g     -- equivalent to g(f(x))
```

### 4.4 Auto-Tracing

When a pipe chain has 3 or more stages, the interpreter automatically:
1. Records the initial value type and description
2. Times each stage's execution
3. Records the output type and description
4. Prints a formatted trace table

Tracing can be disabled with `Interpreter(trace=False)` or `mol run --no-trace`.

### 4.5 Guard Semantics

`guard` evaluates its expression. If falsy, raises `MOLGuardError`. Execution halts immediately.

### 4.6 Access Control

The `access` statement checks a resource name against the `SecurityContext` allow-list. Unauthorized access raises `MOLSecurityError`.

Default allowed: `mind_core`, `memory_bank`, `node_graph`, `data_stream`, `thought_pool`.

### 4.7 Event System

`listen` registers a callback block for a named event. `trigger` fires all registered callbacks for that event.

### 4.8 Truthiness

| Value | Truthy? |
|---|---|
| `null` | No |
| `false` | No |
| `0`, `0.0` | No |
| `""` (empty string) | No |
| `[]` (empty list) | No |
| Everything else | Yes |

---

## 5. Error Types

| Error | When |
|---|---|
| `MOLRuntimeError` | Undefined variable, division by zero, type mismatch in operators |
| `MOLTypeError` | Type annotation violation, wrong argument type to built-in |
| `MOLSecurityError` | Unauthorized `access` statement |
| `MOLGuardError` | `guard` condition fails |
| Parse Error | Syntax error in `.mol` source |

---

## 6. Standard Library

### 6.1 General Utilities

| Function | Signature | Description |
|---|---|---|
| `len(obj)` | `any → Number` | Length of list, string, or map |
| `type_of(obj)` | `any → Text` | Type name as string |
| `to_text(obj)` | `any → Text` | Convert to string |
| `to_number(obj)` | `Text → Number` | Parse string to number |
| `range(n)` | `Number → List` | `[0, 1, ..., n-1]` |
| `abs(x)` | `Number → Number` | Absolute value |
| `round(x, n?)` | `Number → Number` | Round to n decimals |
| `sqrt(x)` | `Number → Number` | Square root |
| `max(...)` | `Number... → Number` | Maximum |
| `min(...)` | `Number... → Number` | Minimum |
| `sum(list)` | `List → Number` | Sum of list |

### 6.2 Collections

| Function | Description |
|---|---|
| `sort(list)` | Sorted copy |
| `reverse(list)` | Reversed copy |
| `push(list, item)` | Append (mutates) |
| `pop(list)` | Remove last (mutates) |
| `keys(map)` | List of map keys |
| `values(map)` | List of map values |
| `contains(col, item)` | Membership check |
| `join(list, sep?)` | Join to string |
| `slice(obj, start, end?)` | Subsequence |

### 6.3 Strings

| Function | Description |
|---|---|
| `split(text, sep?)` | Split string |
| `upper(text)` | Uppercase |
| `lower(text)` | Lowercase |
| `trim(text)` | Strip whitespace |
| `replace(text, old, new)` | Replace substring |

### 6.4 Serialization

| Function | Description |
|---|---|
| `to_json(obj)` | Serialize to JSON string |
| `from_json(text)` | Parse JSON string |
| `inspect(obj)` | Deep inspect (returns dict) |

### 6.5 Time

| Function | Description |
|---|---|
| `clock()` | Current timestamp (seconds) |
| `wait(seconds)` | Sleep |

### 6.6 RAG Pipeline (v0.2.0)

| Function | Signature | Description |
|---|---|---|
| `load_text(path)` | `Text → Document` | Load file as Document |
| `chunk(data, size?)` | `Document\|Text → List<Chunk>` | Split into chunks |
| `embed(data, model?)` | `Text\|Chunk\|List → Embedding\|List` | Create embeddings |
| `store(data, name?)` | `Embedding\|List → VectorStore` | Store in vector index |
| `retrieve(query, store?, k?)` | `Text → List<Map>` | Similarity search |
| `cosine_sim(a, b)` | `Embedding → Number` | Cosine similarity |

### 6.7 Cognitive (v0.2.0)

| Function | Description |
|---|---|
| `think(data, prompt?)` | Synthesize a Thought from data |
| `recall(memory)` | Recall memory value, strengthen |
| `classify(text, ...cats)` | Classify into categories |
| `summarize(text, max?)` | Summarize text |

### 6.8 Debug (v0.2.0)

| Function | Description |
|---|---|
| `display(value)` | Print and pass through |
| `tap(value, label?)` | Labeled debug print, pass through |
| `assert_min(value, threshold)` | Assert >= threshold, pass through |
| `assert_not_null(value)` | Assert not null, pass through |

---

## 7. Transpilation

MOL transpiles to Python and JavaScript. The transpiler converts AST nodes to host-language source code.

### 7.1 Pipe Chain Desugaring

```mol
a |> f |> g(x) |> h
```

Becomes:

```python
h(g(f(a), x))
```

### 7.2 Guard Desugaring

```mol
guard expr : "message"
```

```python
assert expr, "message"
```

```javascript
if (!(expr)) throw new Error("message");
```

---

## 8. Implementation Notes

- **Parser:** Lark LALR(1) with priority-based disambiguation
- **AST:** Python dataclasses with 35+ node types
- **Interpreter:** Visitor pattern with scoped environments and closures
- **Tracing:** Automatic for pipe chains ≥ 3 stages, zero overhead when disabled
- **Embedding:** Deterministic SHA-256 hash-based simulation (64 dimensions). Same text always produces the same vector.
- **Vector Search:** Cosine similarity over in-memory store. Production backends (FAISS, Milvus) planned for v0.4.0.
