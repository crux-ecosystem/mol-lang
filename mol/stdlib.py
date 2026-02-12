"""
MOL Standard Library
=====================

Built-in functions available to every MOL program.
Includes general utilities, algorithms, and IntraMind-specific functions.
"""

import time
import math
import json
import hashlib
import random
import statistics
from mol.types import (
    Thought, Memory, Node, Stream,
    Document, Chunk, Embedding, VectorStore,
)


class MOLSecurityError(Exception):
    """Raised when a MOL program attempts an unauthorized action."""
    pass


class MOLTypeError(Exception):
    """Raised when a MOL type constraint is violated."""
    pass


class MOLGuardError(Exception):
    """Raised when a guard assertion fails."""
    pass


# ── Security Context ─────────────────────────────────────────
class SecurityContext:
    """
    Enforces safety rails. Every access request is checked against
    an allow-list. This is how MOL prevents unauthorized data access *by design*.
    """

    def __init__(self):
        self._allowed_resources: set[str] = {
            "mind_core",
            "memory_bank",
            "node_graph",
            "data_stream",
            "thought_pool",
        }
        self._access_log: list[dict] = []

    def check_access(self, resource: str) -> bool:
        granted = resource in self._allowed_resources
        self._access_log.append({
            "resource": resource,
            "granted": granted,
            "time": time.time(),
        })
        if not granted:
            raise MOLSecurityError(
                f"Access denied: '{resource}' is not an authorized resource. "
                f"Allowed: {', '.join(sorted(self._allowed_resources))}"
            )
        return True

    def grant(self, resource: str):
        self._allowed_resources.add(resource)

    def revoke(self, resource: str):
        self._allowed_resources.discard(resource)


# ── Built-in Functions ───────────────────────────────────────
def _builtin_len(obj):
    return len(obj)


def _builtin_type_of(obj):
    type_map = {
        int: "Number",
        float: "Number",
        str: "Text",
        bool: "Bool",
        list: "List",
        dict: "Map",
        Thought: "Thought",
        Memory: "Memory",
        Node: "Node",
        Stream: "Stream",
    }
    return type_map.get(type(obj), type(obj).__name__)


def _builtin_to_text(obj):
    if isinstance(obj, (Thought, Memory, Node, Stream)):
        return obj.mol_repr()
    return str(obj)


def _builtin_to_number(obj):
    try:
        v = float(obj)
        return int(v) if v == int(v) else v
    except (ValueError, TypeError):
        raise MOLTypeError(f"Cannot convert '{obj}' to Number")


def _builtin_range_fn(*args):
    return list(range(*[int(a) for a in args]))


def _builtin_abs(x):
    return abs(x)


def _builtin_round(x, n=0):
    return round(x, int(n))


def _builtin_sqrt(x):
    return math.sqrt(x)


def _builtin_max_fn(*args):
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)


def _builtin_min_fn(*args):
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)


def _builtin_sum_fn(lst):
    return sum(lst)


def _builtin_sort(lst):
    return sorted(lst)


def _builtin_reverse(lst):
    return list(reversed(lst))


def _builtin_push(lst, item):
    lst.append(item)
    return lst


def _builtin_pop(lst):
    return lst.pop()


def _builtin_keys(d):
    return list(d.keys())


def _builtin_values(d):
    return list(d.values())


def _builtin_contains(collection, item):
    return item in collection


def _builtin_join(lst, sep=" "):
    return sep.join(str(x) for x in lst)


def _builtin_split(text, sep=" "):
    return text.split(sep)


def _builtin_upper(text):
    return text.upper()


def _builtin_lower(text):
    return text.lower()


def _builtin_trim(text):
    return text.strip()


def _builtin_replace(text, old, new):
    return text.replace(old, new)


def _builtin_slice(obj, start, end=None):
    if end is None:
        return obj[int(start):]
    return obj[int(start):int(end)]


def _builtin_clock():
    return time.time()


def _builtin_wait(seconds):
    time.sleep(seconds)
    return None


def _builtin_to_json(obj):
    if isinstance(obj, (Thought, Memory, Node, Stream)):
        return json.dumps(obj.to_dict(), indent=2)
    return json.dumps(obj, indent=2)


def _builtin_from_json(text):
    return json.loads(text)


# ── IntraMind Domain Functions ───────────────────────────────

def _create_thought(content="", confidence=1.0):
    return Thought(content=str(content), confidence=float(confidence))


def _create_memory(key="", value=None):
    return Memory(key=str(key), value=value)


def _create_node(label="", weight=0.0):
    return Node(label=str(label), weight=float(weight))


def _create_stream(name=""):
    return Stream(name=str(name))


def _builtin_inspect(obj):
    """Deep-inspect any MOL object."""
    if isinstance(obj, (Thought, Memory, Node, Stream,
                        Document, Chunk, Embedding, VectorStore)):
        return obj.to_dict()
    return {"type": type(obj).__name__, "value": obj}


# ── Pipeline & RAG Functions (v0.2.0) ────────────────────────

# Global vector store registry
_VECTOR_STORES: dict[str, VectorStore] = {}


def _builtin_load_text(path):
    """Load text from a file → Document."""
    path_str = str(path)
    try:
        with open(path_str, "r") as f:
            content = f.read()
        return Document(source=path_str, content=content)
    except FileNotFoundError:
        raise MOLTypeError(f"File not found: {path_str}")
    except Exception as e:
        raise MOLTypeError(f"Error loading file: {e}")


def _builtin_chunk(data, size=512):
    """Split text or Document into Chunk objects."""
    if isinstance(data, Document):
        text = data.content
        source = data.source
    elif isinstance(data, str):
        text = data
        source = "<string>"
    else:
        raise MOLTypeError(
            f"chunk() expects Text or Document, got {type(data).__name__}"
        )
    chunks = []
    words = text.split()
    current = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > int(size) and current:
            chunks.append(Chunk(
                content=" ".join(current),
                index=len(chunks),
                source=source,
            ))
            current = []
            current_len = 0
        current.append(word)
        current_len += len(word) + 1
    if current:
        chunks.append(Chunk(
            content=" ".join(current),
            index=len(chunks),
            source=source,
        ))
    return chunks


def _builtin_embed(data, model="mol-sim-v1"):
    """Create embedding(s) from text, Chunk, or list of Chunks."""
    if isinstance(data, str):
        return Embedding(text=data, model=str(model))
    if isinstance(data, Chunk):
        return Embedding(text=data.content, model=str(model))
    if isinstance(data, Document):
        return Embedding(text=data.content, model=str(model))
    if isinstance(data, list):
        return [
            Embedding(
                text=c.content if isinstance(c, Chunk) else str(c),
                model=str(model),
            )
            for c in data
        ]
    raise MOLTypeError(
        f"embed() expects Text, Chunk, Document, or List, got {type(data).__name__}"
    )


def _builtin_store(data, name="default"):
    """Store embeddings in a named VectorStore."""
    name = str(name)
    if name not in _VECTOR_STORES:
        _VECTOR_STORES[name] = VectorStore(name=name)
    vs = _VECTOR_STORES[name]

    if isinstance(data, Embedding):
        vs.add(data, text=data.text)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, Embedding):
                vs.add(item, text=item.text)
            elif isinstance(item, Chunk):
                emb = Embedding(text=item.content)
                vs.add(emb, chunk=item, text=item.content)
    return vs


def _builtin_retrieve(query, store_name="default", top_k=3):
    """Retrieve most similar entries from a VectorStore."""
    store_name = str(store_name)
    if store_name not in _VECTOR_STORES:
        raise MOLTypeError(f"Vector store '{store_name}' not found")
    vs = _VECTOR_STORES[store_name]
    query_str = query if isinstance(query, str) else str(query)
    query_emb = Embedding(text=query_str)
    return vs.search(query_emb, int(top_k))


def _builtin_cosine_sim(a, b):
    """Cosine similarity between two Embeddings or two lists."""
    if isinstance(a, Embedding):
        a = a.vector
    if isinstance(b, Embedding):
        b = b.vector
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return round(dot / (norm_a * norm_b), 4)


def _builtin_think(data, prompt=""):
    """Cognitive processing — synthesize a Thought from data."""
    if isinstance(data, list):
        parts = []
        for item in data:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, dict) and "chunk" in item:
                c = item["chunk"]
                parts.append(c.content if isinstance(c, Chunk) else str(c))
            elif isinstance(item, Chunk):
                parts.append(item.content)
            else:
                parts.append(str(item))
        context = " ".join(parts)
    elif isinstance(data, Document):
        context = data.content
    elif isinstance(data, Thought):
        context = data.content
    elif isinstance(data, str):
        context = data
    else:
        context = str(data)

    summary = context[:200] if len(context) > 200 else context
    confidence = min(0.95, 0.5 + len(context) / 1000.0)
    thought = Thought(content=summary, confidence=round(confidence, 2))
    thought.tag("synthesized", "pipeline")
    if prompt:
        thought.tag(f"prompt:{prompt}")
    return thought


def _builtin_recall(key_or_mem):
    """Recall a Memory value or pass through."""
    if isinstance(key_or_mem, Memory):
        return key_or_mem.recall()
    return key_or_mem


def _builtin_classify(text, *categories):
    """Classify text into categories (simulated keyword matching)."""
    if isinstance(text, (Thought, Document, Chunk)):
        text_str = text.content if hasattr(text, "content") else str(text)
    else:
        text_str = str(text)
    text_lower = text_str.lower()
    scores = {}
    for cat in categories:
        cat_str = str(cat)
        cat_words = cat_str.lower().split()
        score = sum(1 for w in cat_words if w in text_lower)
        scores[cat_str] = score
    if scores:
        best = max(scores, key=scores.get)
        return {"label": best, "scores": scores}
    return {"label": "unknown", "scores": {}}


def _builtin_summarize(text, max_len=100):
    """Summarize text (truncate to sentence boundary)."""
    if isinstance(text, (Document, Thought, Chunk)):
        text = text.content if hasattr(text, "content") else str(text)
    elif isinstance(text, list):
        text = " ".join(str(t) for t in text)
    text = str(text)
    max_len = int(max_len)
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_period = truncated.rfind(".")
    if last_period > max_len * 0.5:
        return truncated[:last_period + 1]
    return truncated + "..."


def _builtin_display(value):
    """Print value and pass it through (for use in pipes)."""
    if isinstance(value, (Thought, Memory, Node, Stream,
                          Document, Chunk, Embedding, VectorStore)):
        print(value.mol_repr())
    else:
        print(value)
    return value


def _builtin_tap(value, label="tap"):
    """Debug helper — print labeled value and pass through."""
    desc = value.mol_repr() if hasattr(value, "mol_repr") else str(value)
    print(f"[{label}] {desc}")
    return value


def _builtin_assert_min(value, threshold):
    """Assert a numeric value or confidence >= threshold. Pass through."""
    if isinstance(value, Thought):
        check_val = value.confidence
    elif isinstance(value, (int, float)):
        check_val = value
    else:
        check_val = len(value) if hasattr(value, "__len__") else 0
    if check_val < threshold:
        raise MOLGuardError(
            f"Guard: value {check_val} < minimum {threshold}"
        )
    return value


def _builtin_assert_not_null(value):
    """Assert value is not null. Pass through."""
    if value is None:
        raise MOLGuardError("Guard: value is null")
    return value


# ── Testing Assertions (v0.6.0) ─────────────────────────────
class MOLAssertionError(Exception):
    """Raised when a test assertion fails."""
    pass


def _builtin_assert_eq(actual, expected):
    """Assert two values are equal."""
    if actual != expected:
        raise MOLAssertionError(f"assert_eq failed: {actual!r} != {expected!r}")
    return True


def _builtin_assert_ne(actual, expected):
    """Assert two values are NOT equal."""
    if actual == expected:
        raise MOLAssertionError(f"assert_ne failed: {actual!r} == {expected!r}")
    return True


def _builtin_assert_true(value):
    """Assert value is truthy."""
    if not value:
        raise MOLAssertionError(f"assert_true failed: {value!r}")
    return True


def _builtin_assert_false(value):
    """Assert value is falsy."""
    if value:
        raise MOLAssertionError(f"assert_false failed: {value!r}")
    return True


def _create_document(source="", content=""):
    return Document(source=str(source), content=str(content))


def _create_embedding(text="", model="mol-sim-v1"):
    return Embedding(text=str(text), model=str(model))


def _create_chunk(content="", index=0, source=""):
    return Chunk(content=str(content), index=int(index), source=str(source))


# ── Algorithms & Functional Programming (v0.3.0) ─────────────

def _builtin_map(lst, func):
    """Apply function to each element: map([1,2,3], double) → [2,4,6]"""
    if callable(func):
        return [func(item) for item in lst]
    raise MOLTypeError("map requires a function as second argument")


def _builtin_filter(lst, func):
    """Keep elements where function returns true: filter([1,2,3,4], is_even) → [2,4]"""
    if callable(func):
        return [item for item in lst if func(item)]
    raise MOLTypeError("filter requires a function as second argument")


def _builtin_reduce(lst, func, initial=None):
    """Reduce list to single value: reduce([1,2,3], add, 0) → 6"""
    if not callable(func):
        raise MOLTypeError("reduce requires a function as second argument")
    if initial is not None:
        acc = initial
        for item in lst:
            acc = func(acc, item)
        return acc
    if len(lst) == 0:
        raise MOLTypeError("reduce on empty list without initial value")
    acc = lst[0]
    for item in lst[1:]:
        acc = func(acc, item)
    return acc


def _builtin_flatten(lst):
    """Flatten nested lists: flatten([[1,2],[3,[4,5]]]) → [1,2,3,4,5]"""
    result = []
    def _flatten(items):
        for item in items:
            if isinstance(item, list):
                _flatten(item)
            else:
                result.append(item)
    _flatten(lst)
    return result


def _builtin_unique(lst):
    """Remove duplicates preserving order: unique([1,2,2,3,1]) → [1,2,3]"""
    seen = set()
    result = []
    for item in lst:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _builtin_zip(a, b):
    """Pair elements: zip([1,2,3], ["a","b","c"]) → [[1,"a"],[2,"b"],[3,"c"]]"""
    return [list(pair) for pair in zip(a, b)]


def _builtin_enumerate(lst):
    """Add indices: enumerate(["a","b"]) → [[0,"a"],[1,"b"]]"""
    return [[i, v] for i, v in enumerate(lst)]


def _builtin_count(lst, item):
    """Count occurrences: count([1,2,1,3,1], 1) → 3"""
    return sum(1 for x in lst if x == item)


def _builtin_find(lst, func):
    """Find first matching element: find([1,2,3,4], is_even) → 2"""
    if callable(func):
        for item in lst:
            if func(item):
                return item
        return None
    raise MOLTypeError("find requires a function as second argument")


def _builtin_find_index(lst, item):
    """Find index of item: find_index([10,20,30], 20) → 1"""
    for i, v in enumerate(lst):
        if v == item:
            return i
    return -1


def _builtin_take(lst, n):
    """Take first n elements: take([1,2,3,4,5], 3) → [1,2,3]"""
    return lst[:int(n)]


def _builtin_drop(lst, n):
    """Drop first n elements: drop([1,2,3,4,5], 2) → [3,4,5]"""
    return lst[int(n):]


def _builtin_group_by(lst, func):
    """Group elements by function result: group_by([1,2,3,4], is_even) → {true:[2,4], false:[1,3]}"""
    if not callable(func):
        raise MOLTypeError("group_by requires a function as second argument")
    groups = {}
    for item in lst:
        key = str(func(item))
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def _builtin_chunk_list(lst, size):
    """Split list into chunks: chunk_list([1,2,3,4,5], 2) → [[1,2],[3,4],[5]]"""
    n = int(size)
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def _builtin_every(lst, func):
    """Check if all elements match: every([2,4,6], is_even) → true"""
    if callable(func):
        return all(func(item) for item in lst)
    raise MOLTypeError("every requires a function as second argument")


def _builtin_some(lst, func):
    """Check if any element matches: some([1,2,3], is_even) → true"""
    if callable(func):
        return any(func(item) for item in lst)
    raise MOLTypeError("some requires a function as second argument")


# ── Math & Statistics ─────────────────────────────────────────

def _builtin_floor(x):
    """Floor: floor(3.7) → 3"""
    return math.floor(float(x))


def _builtin_ceil(x):
    """Ceiling: ceil(3.2) → 4"""
    return math.ceil(float(x))


def _builtin_log(x, base=None):
    """Logarithm: log(100, 10) → 2.0, log(e) → 1.0"""
    if base is not None:
        return math.log(float(x), float(base))
    return math.log(float(x))


def _builtin_sin(x):
    return math.sin(float(x))


def _builtin_cos(x):
    return math.cos(float(x))


def _builtin_tan(x):
    return math.tan(float(x))


def _builtin_pi():
    return math.pi


def _builtin_e():
    return math.e


def _builtin_pow(base, exp):
    """Power: pow(2, 10) → 1024"""
    return float(base) ** float(exp)


def _builtin_clamp(value, lo, hi):
    """Clamp value to range: clamp(15, 0, 10) → 10"""
    return max(float(lo), min(float(hi), float(value)))


def _builtin_lerp(a, b, t):
    """Linear interpolation: lerp(0, 100, 0.5) → 50"""
    a, b, t = float(a), float(b), float(t)
    return a + (b - a) * t


def _builtin_mean(lst):
    """Arithmetic mean: mean([1,2,3,4,5]) → 3.0"""
    return statistics.mean([float(x) for x in lst])


def _builtin_median(lst):
    """Median: median([1,3,5,7]) → 4.0"""
    return statistics.median([float(x) for x in lst])


def _builtin_stdev(lst):
    """Standard deviation: stdev([1,2,3,4,5]) → 1.58..."""
    return statistics.stdev([float(x) for x in lst])


def _builtin_variance(lst):
    """Variance: variance([1,2,3,4,5]) → 2.5"""
    return statistics.variance([float(x) for x in lst])


def _builtin_percentile(lst, p):
    """Percentile: percentile([1,2,3,4,5,6,7,8,9,10], 90) → 9.1"""
    import bisect
    sorted_lst = sorted([float(x) for x in lst])
    k = (float(p) / 100.0) * (len(sorted_lst) - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_lst[int(k)]
    return sorted_lst[f] * (c - k) + sorted_lst[c] * (k - f)


# ── String Algorithms ─────────────────────────────────────────

def _builtin_starts_with(text, prefix):
    """Check prefix: starts_with("hello", "hel") → true"""
    return str(text).startswith(str(prefix))


def _builtin_ends_with(text, suffix):
    """Check suffix: ends_with("hello", "llo") → true"""
    return str(text).endswith(str(suffix))


def _builtin_pad_left(text, width, char=" "):
    """Pad left: pad_left("42", 5, "0") → "00042" """
    return str(text).rjust(int(width), str(char)[0])


def _builtin_pad_right(text, width, char=" "):
    """Pad right: pad_right("hi", 5) → "hi   " """
    return str(text).ljust(int(width), str(char)[0])


def _builtin_repeat(text, n):
    """Repeat string: repeat("ha", 3) → "hahaha" """
    return str(text) * int(n)


def _builtin_char_at(text, index):
    """Get character: char_at("hello", 1) → "e" """
    s = str(text)
    i = int(index)
    if 0 <= i < len(s):
        return s[i]
    return ""


def _builtin_index_of(text, sub):
    """Find substring: index_of("hello world", "world") → 6"""
    return str(text).find(str(sub))


def _builtin_format(template, *args):
    """Format string: format("Hello, {}!", "World") → "Hello, World!" """
    return str(template).format(*[str(a) for a in args])


# ── Hashing & Encoding ───────────────────────────────────────

def _builtin_hash(text, algo="sha256"):
    """Hash text: hash("hello") → "2cf24dba..." """
    algo = str(algo).lower()
    data = str(text).encode("utf-8")
    if algo == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algo == "md5":
        return hashlib.md5(data).hexdigest()
    elif algo == "sha1":
        return hashlib.sha1(data).hexdigest()
    elif algo == "sha512":
        return hashlib.sha512(data).hexdigest()
    return hashlib.sha256(data).hexdigest()


def _builtin_uuid():
    """Generate UUID v4: uuid() → "a1b2c3d4-..." """
    import uuid
    return str(uuid.uuid4())


def _builtin_base64_encode(text):
    """Base64 encode: base64_encode("hello") → "aGVsbG8=" """
    import base64
    return base64.b64encode(str(text).encode("utf-8")).decode("ascii")


def _builtin_base64_decode(text):
    """Base64 decode: base64_decode("aGVsbG8=") → "hello" """
    import base64
    return base64.b64decode(str(text)).decode("utf-8")


# ── Sorting Algorithms ───────────────────────────────────────

def _builtin_sort_by(lst, func):
    """Sort by function: sort_by(users, get_age) → sorted by age"""
    if not callable(func):
        raise MOLTypeError("sort_by requires a function as second argument")
    return sorted(lst, key=func)


def _builtin_sort_desc(lst):
    """Sort descending: sort_desc([3,1,2]) → [3,2,1]"""
    return sorted(lst, reverse=True)


def _builtin_binary_search(lst, target):
    """Binary search on sorted list: binary_search([1,2,3,4,5], 3) → 2"""
    import bisect
    sorted_lst = sorted(lst)
    i = bisect.bisect_left(sorted_lst, target)
    if i < len(sorted_lst) and sorted_lst[i] == target:
        return i
    return -1


# ── Random ────────────────────────────────────────────────────

def _builtin_random():
    """Random float 0-1: random() → 0.7234..."""
    return random.random()


def _builtin_random_int(lo, hi):
    """Random integer: random_int(1, 100) → 42"""
    return random.randint(int(lo), int(hi))


def _builtin_shuffle(lst):
    """Shuffle list: shuffle([1,2,3]) → [3,1,2] (random)"""
    result = list(lst)
    random.shuffle(result)
    return result


def _builtin_sample(lst, n):
    """Random sample: sample([1,2,3,4,5], 3) → [2,5,1]"""
    return random.sample(lst, int(n))


def _builtin_choice(lst):
    """Random choice: choice(["a","b","c"]) → "b" """
    return random.choice(lst)


# ── Utility ───────────────────────────────────────────────────

def _builtin_typeof(obj):
    """Alias for type_of"""
    return _builtin_type_of(obj)


def _builtin_print(*args):
    """Print multiple values: print("x =", 42)"""
    parts = [str(a) if not isinstance(a, str) else a for a in args]
    print(" ".join(parts))
    return None


def _builtin_merge(*dicts):
    """Merge maps: merge({"a":1}, {"b":2}) → {"a":1, "b":2}"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def _builtin_pick(d, *fields):
    """Pick fields from map: pick(user, "name", "age") → {"name":..., "age":...}"""
    if isinstance(d, dict):
        return {k: d[k] for k in fields if k in d}
    return {}


def _builtin_omit(d, *fields):
    """Omit fields from map: omit(user, "password") → user without password"""
    if isinstance(d, dict):
        return {k: v for k, v in d.items() if k not in fields}
    return {}


def _builtin_is_null(val):
    """Check null: is_null(null) → true"""
    return val is None


def _builtin_is_number(val):
    """Check number: is_number(42) → true"""
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _builtin_is_text(val):
    """Check text: is_text("hello") → true"""
    return isinstance(val, str)


def _builtin_is_list(val):
    """Check list: is_list([1,2]) → true"""
    return isinstance(val, list)


def _builtin_is_map(val):
    """Check map: is_map({"a":1}) → true"""
    return isinstance(val, dict)


# ── Standard Library Registry ────────────────────────────────
STDLIB: dict[str, callable] = {
    # General utilities
    "len": _builtin_len,
    "type_of": _builtin_type_of,
    "to_text": _builtin_to_text,
    "to_number": _builtin_to_number,
    "range": _builtin_range_fn,
    "abs": _builtin_abs,
    "round": _builtin_round,
    "sqrt": _builtin_sqrt,
    "max": _builtin_max_fn,
    "min": _builtin_min_fn,
    "sum": _builtin_sum_fn,
    "sort": _builtin_sort,
    "reverse": _builtin_reverse,
    "push": _builtin_push,
    "pop": _builtin_pop,
    "keys": _builtin_keys,
    "values": _builtin_values,
    "contains": _builtin_contains,
    "join": _builtin_join,
    "split": _builtin_split,
    "upper": _builtin_upper,
    "lower": _builtin_lower,
    "trim": _builtin_trim,
    "replace": _builtin_replace,
    "slice": _builtin_slice,
    "clock": _builtin_clock,
    "wait": _builtin_wait,
    "to_json": _builtin_to_json,
    "from_json": _builtin_from_json,
    "inspect": _builtin_inspect,

    # IntraMind constructors
    "Thought": _create_thought,
    "Memory": _create_memory,
    "Node": _create_node,
    "Stream": _create_stream,
    "Document": _create_document,
    "Embedding": _create_embedding,
    "Chunk": _create_chunk,

    # Pipeline / RAG functions (v0.2.0)
    "load_text": _builtin_load_text,
    "chunk": _builtin_chunk,
    "embed": _builtin_embed,
    "store": _builtin_store,
    "retrieve": _builtin_retrieve,
    "cosine_sim": _builtin_cosine_sim,
    "think": _builtin_think,
    "recall": _builtin_recall,
    "classify": _builtin_classify,
    "summarize": _builtin_summarize,
    "display": _builtin_display,
    "tap": _builtin_tap,
    "assert_min": _builtin_assert_min,
    "assert_not_null": _builtin_assert_not_null,

    # Functional programming (v0.3.0)
    "map": _builtin_map,
    "filter": _builtin_filter,
    "reduce": _builtin_reduce,
    "flatten": _builtin_flatten,
    "unique": _builtin_unique,
    "zip": _builtin_zip,
    "enumerate": _builtin_enumerate,
    "count": _builtin_count,
    "find": _builtin_find,
    "find_index": _builtin_find_index,
    "take": _builtin_take,
    "drop": _builtin_drop,
    "group_by": _builtin_group_by,
    "chunk_list": _builtin_chunk_list,
    "every": _builtin_every,
    "some": _builtin_some,

    # Math & Statistics
    "floor": _builtin_floor,
    "ceil": _builtin_ceil,
    "log": _builtin_log,
    "sin": _builtin_sin,
    "cos": _builtin_cos,
    "tan": _builtin_tan,
    "pi": _builtin_pi,
    "e": _builtin_e,
    "pow": _builtin_pow,
    "clamp": _builtin_clamp,
    "lerp": _builtin_lerp,
    "mean": _builtin_mean,
    "median": _builtin_median,
    "stdev": _builtin_stdev,
    "variance": _builtin_variance,
    "percentile": _builtin_percentile,

    # String algorithms
    "starts_with": _builtin_starts_with,
    "ends_with": _builtin_ends_with,
    "pad_left": _builtin_pad_left,
    "pad_right": _builtin_pad_right,
    "repeat": _builtin_repeat,
    "char_at": _builtin_char_at,
    "index_of": _builtin_index_of,
    "format": _builtin_format,

    # Hashing & Encoding
    "hash": _builtin_hash,
    "uuid": _builtin_uuid,
    "base64_encode": _builtin_base64_encode,
    "base64_decode": _builtin_base64_decode,

    # Sorting algorithms
    "sort_by": _builtin_sort_by,
    "sort_desc": _builtin_sort_desc,
    "binary_search": _builtin_binary_search,

    # Random
    "random": _builtin_random,
    "random_int": _builtin_random_int,
    "shuffle": _builtin_shuffle,
    "sample": _builtin_sample,
    "choice": _builtin_choice,

    # Utility
    "print": _builtin_print,
    "merge": _builtin_merge,
    "pick": _builtin_pick,
    "omit": _builtin_omit,
    "is_null": _builtin_is_null,
    "is_number": _builtin_is_number,
    "is_text": _builtin_is_text,
    "is_list": _builtin_is_list,
    "is_map": _builtin_is_map,

    # Testing assertions (v0.6.0)
    "assert_eq": _builtin_assert_eq,
    "assert_ne": _builtin_assert_ne,
    "assert_true": _builtin_assert_true,
    "assert_false": _builtin_assert_false,
}
