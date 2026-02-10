# Standard Library Reference

MOL v0.3.0 includes **90+ built-in functions** available to every program without imports.

## General Utilities

| Function | Signature | Description |
|----------|-----------|-------------|
| `len(obj)` | `len(list\|text\|map) → Number` | Length of collection or string |
| `type_of(obj)` | `type_of(any) → Text` | MOL type name |
| `to_text(obj)` | `to_text(any) → Text` | Convert to string |
| `to_number(obj)` | `to_number(text\|number) → Number` | Convert to number |
| `range(...)` | `range(n)` or `range(start, end)` | Generate integer list |
| `inspect(obj)` | `inspect(any) → Text` | Deep inspection |
| `clock()` | `clock() → Number` | Current timestamp |
| `wait(s)` | `wait(seconds)` | Sleep |
| `to_json(obj)` | `to_json(any) → Text` | JSON encode |
| `from_json(text)` | `from_json(text) → any` | JSON decode |
| `print(...)` | `print(args...)` | Print multiple values |

## Math

| Function | Signature | Description |
|----------|-----------|-------------|
| `abs(x)` | `abs(number) → Number` | Absolute value |
| `round(x, n)` | `round(number, digits?) → Number` | Round |
| `floor(x)` | `floor(number) → Number` | Floor |
| `ceil(x)` | `ceil(number) → Number` | Ceiling |
| `sqrt(x)` | `sqrt(number) → Number` | Square root |
| `pow(x, y)` | `pow(number, number) → Number` | Power |
| `log(x, base)` | `log(number, base?) → Number` | Logarithm |
| `sin(x)` | `sin(number) → Number` | Sine |
| `cos(x)` | `cos(number) → Number` | Cosine |
| `tan(x)` | `tan(number) → Number` | Tangent |
| `pi()` | `pi() → Number` | π constant |
| `e()` | `e() → Number` | Euler's number |
| `max(...)` | `max(list\|args) → Number` | Maximum |
| `min(...)` | `min(list\|args) → Number` | Minimum |
| `sum(lst)` | `sum(list) → Number` | Sum |
| `clamp(x, lo, hi)` | `clamp(n, lo, hi) → Number` | Clamp to range |
| `lerp(a, b, t)` | `lerp(n, n, 0-1) → Number` | Linear interpolation |

## Statistics

| Function | Signature | Description |
|----------|-----------|-------------|
| `mean(lst)` | `mean(list) → Number` | Arithmetic mean |
| `median(lst)` | `median(list) → Number` | Median value |
| `stdev(lst)` | `stdev(list) → Number` | Standard deviation |
| `variance(lst)` | `variance(list) → Number` | Variance |
| `percentile(lst, p)` | `percentile(list, 0-100) → Number` | Percentile |

## String Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `upper(s)` | `upper(text) → Text` | Uppercase |
| `lower(s)` | `lower(text) → Text` | Lowercase |
| `trim(s)` | `trim(text) → Text` | Strip whitespace |
| `split(s, sep)` | `split(text, text) → List` | Split string |
| `join(lst, sep)` | `join(list, text) → Text` | Join list |
| `replace(s, old, new)` | `replace(text, text, text) → Text` | Replace |
| `slice(s, start, end)` | `slice(text, n, n) → Text` | Substring |
| `contains(s, sub)` | `contains(text, text) → Bool` | Contains check |
| `starts_with(s, pre)` | `starts_with(text, text) → Bool` | Prefix check |
| `ends_with(s, suf)` | `ends_with(text, text) → Bool` | Suffix check |
| `pad_left(s, w, c)` | `pad_left(text, n, char?) → Text` | Left pad |
| `pad_right(s, w, c)` | `pad_right(text, n, char?) → Text` | Right pad |
| `repeat(s, n)` | `repeat(text, n) → Text` | Repeat string |
| `char_at(s, i)` | `char_at(text, n) → Text` | Character at index |
| `index_of(s, sub)` | `index_of(text, text) → Number` | Find substring index |
| `format(t, ...)` | `format(template, args...) → Text` | String formatting |

## List Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `sort(lst)` | `sort(list) → List` | Sort ascending |
| `sort_desc(lst)` | `sort_desc(list) → List` | Sort descending |
| `sort_by(lst, fn)` | `sort_by(list, func) → List` | Sort by function |
| `reverse(lst)` | `reverse(list) → List` | Reverse |
| `push(lst, item)` | `push(list, any) → List` | Append (mutates) |
| `pop(lst)` | `pop(list) → any` | Remove last (mutates) |
| `flatten(lst)` | `flatten(list) → List` | Flatten nested |
| `unique(lst)` | `unique(list) → List` | Remove duplicates |
| `zip(a, b)` | `zip(list, list) → List` | Pair elements |
| `enumerate(lst)` | `enumerate(list) → List` | Add indices |
| `count(lst, item)` | `count(list, any) → Number` | Count occurrences |
| `find_index(lst, item)` | `find_index(list, any) → Number` | Find index |
| `take(lst, n)` | `take(list, n) → List` | First n elements |
| `drop(lst, n)` | `drop(list, n) → List` | Skip first n |
| `chunk_list(lst, n)` | `chunk_list(list, n) → List` | Split into chunks |
| `binary_search(lst, x)` | `binary_search(list, any) → Number` | Binary search |
| `sample(lst, n)` | `sample(list, n) → List` | Random sample |
| `shuffle(lst)` | `shuffle(list) → List` | Random order |
| `choice(lst)` | `choice(list) → any` | Random pick |

## Functional Programming

| Function | Signature | Description |
|----------|-----------|-------------|
| `map(lst, fn)` | `map(list, func) → List` | Apply to each |
| `filter(lst, fn)` | `filter(list, func) → List` | Keep matching |
| `reduce(lst, fn, init)` | `reduce(list, func, any?) → any` | Accumulate |
| `find(lst, fn)` | `find(list, func) → any\|null` | Find first matching |
| `every(lst, fn)` | `every(list, func) → Bool` | All match? |
| `some(lst, fn)` | `some(list, func) → Bool` | Any match? |
| `group_by(lst, fn)` | `group_by(list, func) → Map` | Group by result |

## Map Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `keys(m)` | `keys(map) → List` | Map keys |
| `values(m)` | `values(map) → List` | Map values |
| `merge(...)` | `merge(maps...) → Map` | Merge maps |
| `pick(m, ...)` | `pick(map, keys...) → Map` | Select fields |
| `omit(m, ...)` | `omit(map, keys...) → Map` | Exclude fields |

## Hashing & Encoding

| Function | Signature | Description |
|----------|-----------|-------------|
| `hash(text, algo)` | `hash(text, "sha256"\|"md5"\|"sha1"\|"sha512") → Text` | Cryptographic hash |
| `uuid()` | `uuid() → Text` | Generate UUID v4 |
| `base64_encode(s)` | `base64_encode(text) → Text` | Base64 encode |
| `base64_decode(s)` | `base64_decode(text) → Text` | Base64 decode |

## Random

| Function | Signature | Description |
|----------|-----------|-------------|
| `random()` | `random() → Number` | Random 0.0–1.0 |
| `random_int(lo, hi)` | `random_int(n, n) → Number` | Random integer |

## Type Checking

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_null(v)` | `is_null(any) → Bool` | Null check |
| `is_number(v)` | `is_number(any) → Bool` | Number check |
| `is_text(v)` | `is_text(any) → Bool` | Text check |
| `is_list(v)` | `is_list(any) → Bool` | List check |
| `is_map(v)` | `is_map(any) → Bool` | Map check |

## Domain Constructors

| Function | Signature | Description |
|----------|-----------|-------------|
| `Thought(content, conf)` | `Thought(text, 0-1) → Thought` | Create thought |
| `Memory(key, value)` | `Memory(text, any) → Memory` | Create memory |
| `Node(label, weight)` | `Node(text, number) → Node` | Create node |
| `Stream(name)` | `Stream(text) → Stream` | Create stream |
| `Document(source, content)` | `Document(text, text) → Document` | Create document |
| `Embedding(text, model)` | `Embedding(text, text) → Embedding` | Create embedding |
| `Chunk(content, index, source)` | `Chunk(text, n, text) → Chunk` | Create chunk |

## RAG Pipeline Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_text(path)` | `load_text(text) → Document` | Load file |
| `chunk(doc, size)` | `chunk(Document\|text, n) → List<Chunk>` | Split into chunks |
| `embed(data, model)` | `embed(any, text?) → Embedding\|List` | Create embeddings |
| `store(data, name)` | `store(list, text) → VectorStore` | Store in index |
| `retrieve(query, store, k)` | `retrieve(text, text, n) → List` | Similarity search |
| `cosine_sim(a, b)` | `cosine_sim(Embedding, Embedding) → Number` | Cosine similarity |
| `think(data, prompt)` | `think(any, text?) → Thought` | Synthesize thought |
| `recall(key)` | `recall(Memory\|text) → any` | Recall memory |
| `classify(text, ...)` | `classify(text, cats...) → Text` | Classify text |
| `summarize(text, n)` | `summarize(text, n?) → Text` | Summarize text |

## Pipeline Utilities

| Function | Signature | Description |
|----------|-----------|-------------|
| `display(value)` | `display(any) → any` | Print & pass through |
| `tap(value, label)` | `tap(any, text) → any` | Debug print |
| `assert_min(v, threshold)` | `assert_min(n, n)` | Guard minimum |
| `assert_not_null(v)` | `assert_not_null(any)` | Guard not null |
