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
from mol.vector_engine import (
    Vector, QuantizedVector, VectorIndex,
    create_vector, vec_zeros, vec_ones, vec_rand, vec_from_text,
    vec_dot, vec_cosine, vec_distance, vec_normalize,
    vec_add, vec_sub, vec_scale, vec_dim, vec_concat,
    vec_batch_cosine, vec_top_k, vec_quantize,
    create_vector_index, vec_index_add, vec_index_search,
    vec_softmax, vec_relu,
)
from mol.encryption import (
    EncryptedValue, EncryptedVector, EncryptedMemory, CryptoKeyPair,
    _builtin_crypto_keygen, _builtin_he_encrypt, _builtin_he_decrypt,
    _builtin_he_add, _builtin_he_sub, _builtin_he_mul_scalar,
    _builtin_sym_keygen, _builtin_sym_encrypt, _builtin_sym_decrypt,
    _builtin_zk_commit, _builtin_zk_verify, _builtin_zk_prove,
    _builtin_secure_hash, _builtin_secure_random,
    _builtin_constant_time_compare,
)
from mol.jit_tracer import (
    _builtin_jit_stats, _builtin_jit_hot_paths, _builtin_jit_profile,
    _builtin_jit_reset, _builtin_jit_warmup, _builtin_jit_enabled,
    _builtin_jit_toggle,
)
from mol.swarm_runtime import (
    SwarmCluster,
    _builtin_swarm_init, _builtin_swarm_shard, _builtin_swarm_map,
    _builtin_swarm_reduce, _builtin_swarm_gather, _builtin_swarm_broadcast,
    _builtin_swarm_health, _builtin_swarm_nodes, _builtin_swarm_rebalance,
    _builtin_swarm_add_node, _builtin_swarm_remove_node,
    _builtin_swarm_scatter,
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


# ── Sandbox Mode (v0.10.0) ──────────────────────────────────
# Functions blocked in playground/sandbox mode to prevent abuse
SANDBOX_BLOCKED_FUNCTIONS = {
    # File system — arbitrary read/write/delete on server
    "read_file", "write_file", "append_file", "delete_file",
    "file_exists", "list_dir", "make_dir", "file_size",
    "path_join", "path_dir", "path_base", "path_ext",
    # Network — SSRF, port scanning, data exfiltration
    "fetch", "url_encode",
    # Server — bind ports on the host machine
    "serve",
    # Concurrency — thread pool exhaustion, DoS
    "channel", "send", "receive", "parallel", "race", "wait_all", "task_done",
    # Dangerous utilities
    "sleep",   # block server threads
    "wait",    # block server threads
    "panic",   # crash the process
    # RAG pipeline (uses real file I/O)
    "load_text",
}


def _sandbox_blocked(name):
    """Return a function that raises SecurityError when called in sandbox."""
    def _blocked(*args, **kwargs):
        raise MOLSecurityError(
            f"'{name}()' is not available in the playground for security reasons. "
            f"Install MOL locally to use this function: pip install mol-lang"
        )
    _blocked.__name__ = name
    _blocked.__doc__ = f"[BLOCKED in playground] {name}"
    return _blocked


def get_sandbox_stdlib():
    """Return a copy of STDLIB with dangerous functions replaced by blockers."""
    safe = dict(STDLIB)
    for name in SANDBOX_BLOCKED_FUNCTIONS:
        if name in safe:
            safe[name] = _sandbox_blocked(name)
    return safe


# ── Built-in Functions ───────────────────────────────────────
def _builtin_len(obj):
    return len(obj)


def _builtin_type_of(obj):
    # Check for MOLStructInstance first (imported lazily to avoid circular import)
    if hasattr(obj, '_struct_def') and hasattr(obj._struct_def, 'name'):
        return obj._struct_def.name
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
        Vector: "Vector",
        QuantizedVector: "QuantizedVector",
        VectorIndex: "VectorIndex",
        EncryptedValue: "Encrypted",
        EncryptedVector: "EncryptedVector",
        EncryptedMemory: "EncryptedMemory",
        CryptoKeyPair: "CryptoKeyPair",
        SwarmCluster: "SwarmCluster",
    }
    return type_map.get(type(obj), type(obj).__name__)


def _builtin_to_text(obj):
    if isinstance(obj, (Thought, Memory, Node, Stream)):
        return obj.mol_repr()
    if isinstance(obj, Vector):
        return obj.mol_repr()
    if isinstance(obj, EncryptedValue):
        return obj.mol_repr()
    if isinstance(obj, SwarmCluster):
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
    if sep == "":
        return list(text)  # Split into individual characters
    return text.split(sep)


def _builtin_chars(text):
    """Split a string into a list of individual characters."""
    return list(str(text))


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


def _builtin_panic(msg="panic"):
    """Halt execution with error message."""
    from mol.interpreter import MOLRuntimeError
    raise MOLRuntimeError(str(msg))


def _create_document(source="", content=""):
    return Document(source=str(source), content=str(content))


def _create_embedding(text="", model="mol-sim-v1"):
    return Embedding(text=str(text), model=str(model))


def _create_chunk(content="", index=0, source=""):
    return Chunk(content=str(content), index=int(index), source=str(source))


# ── Concurrency Primitives (v0.7.0) ─────────────────────────
import threading
import queue as _queue
from concurrent.futures import ThreadPoolExecutor, Future, as_completed


class MOLTask:
    """Wraps a Future — the result of `spawn do ... end`."""
    def __init__(self, future: Future):
        self._future = future

    def result(self, timeout=None):
        return self._future.result(timeout=timeout)

    def done(self):
        return self._future.done()

    def __repr__(self):
        status = "done" if self.done() else "running"
        return f"<Task({status})>"


class MOLChannel:
    """Thread-safe channel for inter-task communication."""
    def __init__(self, capacity=0):
        self._queue = _queue.Queue(maxsize=capacity)

    def send(self, value):
        self._queue.put(value)

    def receive(self, timeout=None):
        try:
            return self._queue.get(timeout=timeout)
        except _queue.Empty:
            from mol.interpreter import MOLRuntimeError
            raise MOLRuntimeError("Channel receive timed out")

    def try_receive(self):
        """Non-blocking receive — returns null if empty."""
        try:
            return self._queue.get_nowait()
        except _queue.Empty:
            return None

    def __repr__(self):
        return f"<Channel(size={self._queue.qsize()})>"


# Global thread pool shared by all spawn calls
_THREAD_POOL = ThreadPoolExecutor(max_workers=32, thread_name_prefix="mol-spawn")


def _builtin_channel(capacity=0):
    """Create a new channel for inter-task communication."""
    return MOLChannel(capacity=int(capacity))


def _builtin_send(ch, value):
    """Send a value to a channel."""
    if not isinstance(ch, MOLChannel):
        raise MOLTypeError("send() expects a Channel as first argument")
    ch.send(value)
    return value


def _builtin_receive(ch, timeout=None):
    """Receive a value from a channel (blocks until available)."""
    if not isinstance(ch, MOLChannel):
        raise MOLTypeError("receive() expects a Channel as first argument")
    t = float(timeout) if timeout is not None else None
    return ch.receive(timeout=t)


def _builtin_sleep(ms):
    """Sleep for the given number of milliseconds."""
    import time
    time.sleep(float(ms) / 1000.0)
    return None


def _builtin_parallel(items, func):
    """Execute func on each item in parallel, return results in order."""
    if not isinstance(items, list):
        raise MOLTypeError("parallel() expects a list as first argument")
    if not callable(func):
        raise MOLTypeError("parallel() expects a function as second argument")
    futures = [_THREAD_POOL.submit(func, item) for item in items]
    return [f.result() for f in futures]


def _builtin_race(*args):
    """Return the result of whichever task finishes first."""
    tasks = args if not (len(args) == 1 and isinstance(args[0], list)) else args[0]
    if not tasks:
        from mol.interpreter import MOLRuntimeError
        raise MOLRuntimeError("race() requires at least one task")
    # Support both MOLTask objects and a list of tasks
    futures = {}
    for t in tasks:
        if isinstance(t, MOLTask):
            futures[t._future] = t
        else:
            raise MOLTypeError("race() expects Task objects")
    done_iter = as_completed(futures.keys())
    first = next(done_iter)
    return first.result()


def _builtin_wait_all(*args):
    """Wait for all tasks to complete and return their results."""
    tasks = args if not (len(args) == 1 and isinstance(args[0], list)) else args[0]
    results = []
    for t in tasks:
        if isinstance(t, MOLTask):
            results.append(t.result())
        else:
            raise MOLTypeError("wait_all() expects Task objects")
    return results


def _builtin_task_done(task):
    """Check if a task has completed."""
    if not isinstance(task, MOLTask):
        raise MOLTypeError("task_done() expects a Task")
    return task.done()


# ── Algorithms & Functional Programming (v0.3.0) ─────────────

def _builtin_map(lst, func):
    """Apply function to each element: map([1,2,3], double) → [2,4,6]
    Smart mode: map(users, "name") → extracts the 'name' field from each dict/struct."""
    if callable(func):
        return [func(item) for item in lst]
    # Smart mode: string → property extraction
    if isinstance(func, str):
        key = func
        return [item.get(key, None) if isinstance(item, dict) else getattr(item, key, None) for item in lst]
    raise MOLTypeError(
        f"map requires a function or property name, got {type(func).__name__}.\n"
        f"  Hint: use a lambda → map(fn(x) -> x * 2)\n"
        f"  Or extract a field  → map(\"name\")"
    )


def _builtin_filter(lst, func):
    """Keep elements where function returns true: filter([1,2,3,4], is_even) → [2,4]
    Smart modes:
      filter([1,2,3], fn(x) -> x > 2) → [3]       -- lambda
      filter([1,2,3,2], 2)            → [2, 2]     -- equality match
      filter(users, "active")          → active users -- truthy property"""
    if callable(func):
        return [item for item in lst if func(item)]
    # Smart mode: non-callable → equality matching
    if isinstance(func, str) and lst and isinstance(lst[0], dict):
        # String on list of dicts → filter where property is truthy
        key = func
        return [item for item in lst if item.get(key)]
    # Value → equality match
    return [item for item in lst if item == func]


def _builtin_reduce(lst, func, initial=None):
    """Reduce list to single value: reduce([1,2,3], add, 0) → 6"""
    if not callable(func):
        raise MOLTypeError(
            f"reduce requires a function, got {type(func).__name__}.\n"
            f"  Hint: reduce(fn(acc, x) -> acc + x)"
        )
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
    """Find first matching element: find([1,2,3,4], is_even) → 2
    Smart mode: find([1,2,3], 2) → 2 (equality match)"""
    if callable(func):
        for item in lst:
            if func(item):
                return item
        return None
    # Smart mode: value → equality match
    for item in lst:
        if item == func:
            return item
    return None


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
    """Group elements by function result: group_by([1,2,3,4], is_even) → {true:[2,4], false:[1,3]}
    Smart mode: group_by(users, "role") → groups by the 'role' property."""
    if isinstance(func, str):
        key = func
        groups = {}
        for item in lst:
            val = str(item.get(key, None) if isinstance(item, dict) else getattr(item, key, None))
            if val not in groups:
                groups[val] = []
            groups[val].append(item)
        return groups
    if not callable(func):
        raise MOLTypeError(
            f"group_by requires a function or property name, got {type(func).__name__}.\n"
            f"  Hint: group_by(fn(x) -> x > 10) or group_by(\"category\")"
        )
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
    # Smart mode: value → check all equal
    return all(item == func for item in lst)


def _builtin_some(lst, func):
    """Check if any element matches: some([1,2,3], is_even) → true"""
    if callable(func):
        return any(func(item) for item in lst)
    # Smart mode: value → check any equal
    return any(item == func for item in lst)


# ── Convenience Aliases & Extras (v1.1.0) ─────────────────────

def _builtin_where(lst, func):
    """Alias for filter — more readable in pipes: data |> where(fn(x) -> x > 5)
    Smart modes: where(30) → equality match, where("active") → truthy property."""
    return _builtin_filter(lst, func)


def _builtin_select(lst, func):
    """Alias for map — more readable for projections: users |> select("name")
    Smart modes: select(fn(x) -> x.name) or select("name")."""
    return _builtin_map(lst, func)


def _builtin_reject(lst, func):
    """Opposite of filter — keep elements where function returns false:
    reject([1,2,3,4,5], fn(x) -> x > 3) → [1,2,3]
    Smart mode: reject(3) → remove all 3s."""
    if callable(func):
        return [item for item in lst if not func(item)]
    # Smart mode: value → remove matching
    return [item for item in lst if item != func]


def _builtin_pluck(lst, key):
    """Extract a single property from each dict/struct: pluck(users, "name") → ["Alice","Bob"]"""
    if isinstance(key, str):
        return [item.get(key, None) if isinstance(item, dict) else getattr(item, key, None) for item in lst]
    raise MOLTypeError(
        f"pluck requires a property name (string), got {type(key).__name__}.\n"
        f"  Hint: pluck(\"name\")"
    )


def _builtin_each(lst, func):
    """Execute function for each element (side effects): each(items, fn(x) -> show(x))
    Returns the original list unchanged."""
    if callable(func):
        for item in lst:
            func(item)
        return lst
    raise MOLTypeError(
        f"each requires a function, got {type(func).__name__}.\n"
        f"  Hint: each(fn(x) -> show(x))"
    )


def _builtin_compact(lst):
    """Remove null/false values: compact([1, null, 2, false, 3, 0]) → [1, 2, 3]"""
    return [item for item in lst if item is not None and item is not False and item != 0 and item != ""]


def _builtin_first(lst):
    """Get first element: first([10,20,30]) → 10"""
    if not lst:
        return None
    return lst[0]


def _builtin_last(lst):
    """Get last element: last([10,20,30]) → 30"""
    if not lst:
        return None
    return lst[-1]


def _builtin_sum_list(lst):
    """Sum all numbers: sum_list([1,2,3,4,5]) → 15"""
    return sum(lst)


def _builtin_min_list(lst):
    """Get minimum: min_list([3,1,4,1,5]) → 1"""
    return min(lst)


def _builtin_max_list(lst):
    """Get maximum: max_list([3,1,4,1,5]) → 5"""
    return max(lst)


def _builtin_contains(lst, value):
    """Check if list contains value: contains([1,2,3], 2) → true"""
    return value in lst


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
    """Sort by function: sort_by(users, get_age) → sorted by age
    Smart mode: sort_by(users, "age") → sorted by the 'age' property."""
    if isinstance(func, str):
        key = func
        return sorted(lst, key=lambda item: item.get(key, 0) if isinstance(item, dict) else getattr(item, key, 0))
    if not callable(func):
        raise MOLTypeError(
            f"sort_by requires a function or property name, got {type(func).__name__}.\n"
            f"  Hint: sort_by(fn(x) -> x.age) or sort_by(\"age\")"
        )
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


# ── File I/O (v0.8.0) ───────────────────────────────────────
import os as _os

def _builtin_read_file(path):
    """Read file contents: read_file("data.txt") → "contents..." """
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise MOLSecurityError(f"File not found: {path}")
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")
    except Exception as e:
        raise MOLSecurityError(f"Cannot read file: {e}")


def _builtin_write_file(path, content):
    """Write to file: write_file("out.txt", "hello")"""
    try:
        with open(path, "w") as f:
            f.write(str(content))
        return True
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")
    except Exception as e:
        raise MOLSecurityError(f"Cannot write file: {e}")


def _builtin_append_file(path, content):
    """Append to file: append_file("log.txt", "new line\\n")"""
    try:
        with open(path, "a") as f:
            f.write(str(content))
        return True
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")
    except Exception as e:
        raise MOLSecurityError(f"Cannot append to file: {e}")


def _builtin_file_exists(path):
    """Check if file exists: file_exists("data.txt") → true"""
    return _os.path.exists(path)


def _builtin_list_dir(path="."):
    """List directory: list_dir("./src") → ["file1.mol", "file2.mol"]"""
    try:
        return sorted(_os.listdir(path))
    except FileNotFoundError:
        raise MOLSecurityError(f"Directory not found: {path}")
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")


def _builtin_delete_file(path):
    """Delete file: delete_file("temp.txt")"""
    try:
        _os.remove(path)
        return True
    except FileNotFoundError:
        raise MOLSecurityError(f"File not found: {path}")
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")


def _builtin_make_dir(path):
    """Create directory: make_dir("./output")"""
    try:
        _os.makedirs(path, exist_ok=True)
        return True
    except PermissionError:
        raise MOLSecurityError(f"Permission denied: {path}")


def _builtin_file_size(path):
    """Get file size in bytes: file_size("data.bin") → 1024"""
    try:
        return _os.path.getsize(path)
    except FileNotFoundError:
        raise MOLSecurityError(f"File not found: {path}")


def _builtin_path_join(*parts):
    """Join path components: path_join("src", "main.mol") → "src/main.mol" """
    return _os.path.join(*parts)


def _builtin_path_dir(path):
    """Get directory: path_dir("/a/b/c.txt") → "/a/b" """
    return _os.path.dirname(path)


def _builtin_path_base(path):
    """Get basename: path_base("/a/b/c.txt") → "c.txt" """
    return _os.path.basename(path)


def _builtin_path_ext(path):
    """Get extension: path_ext("file.mol") → ".mol" """
    return _os.path.splitext(path)[1]


# ── HTTP (v0.8.0) ───────────────────────────────────────────
import urllib.request as _urllib_req
import urllib.error as _urllib_err
import urllib.parse as _urllib_parse

def _builtin_fetch(url, options=None):
    """HTTP fetch: fetch("https://api.example.com/data") → response map
    Options: {"method": "POST", "headers": {...}, "body": "..."}"""
    if options is None:
        options = {}

    method = options.get("method", "GET") if isinstance(options, dict) else "GET"
    headers = options.get("headers", {}) if isinstance(options, dict) else {}
    body = options.get("body", None) if isinstance(options, dict) else None

    try:
        if body is not None:
            if isinstance(body, dict):
                body = json.dumps(body).encode("utf-8")
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
            elif isinstance(body, str):
                body = body.encode("utf-8")

        req = _urllib_req.Request(url, data=body, headers=headers, method=method.upper())
        with _urllib_req.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            # Try to parse JSON
            try:
                data = json.loads(resp_body)
            except (json.JSONDecodeError, ValueError):
                data = resp_body
            return {
                "status": resp.status,
                "body": data,
                "headers": dict(resp.getheaders()),
                "ok": 200 <= resp.status < 300,
            }
    except _urllib_err.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        return {
            "status": e.code,
            "body": resp_body,
            "headers": dict(e.headers),
            "ok": False,
        }
    except _urllib_err.URLError as e:
        return {"status": 0, "body": str(e.reason), "headers": {}, "ok": False}
    except Exception as e:
        return {"status": 0, "body": str(e), "headers": {}, "ok": False}


def _builtin_url_encode(params):
    """URL-encode a map: url_encode({"q": "hello world"}) → "q=hello+world" """
    if isinstance(params, dict):
        return _urllib_parse.urlencode(params)
    return str(params)


# ── HTTP Server (v0.9.0) ────────────────────────────────────

_active_server = None
_server_handler = None
_mol_interpreter = None


def _builtin_serve(port, handler):
    """Start an HTTP server: serve(8080, fn(req) -> response_map)

    handler receives a map: { method, path, headers, body, query }
    handler should return:  { status, body, headers? }
    """
    import http.server
    import json as _json_mod
    global _active_server, _server_handler, _mol_interpreter

    _server_handler = handler

    class MOLHandler(http.server.BaseHTTPRequestHandler):
        def _handle(self):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""

            # Parse query string
            query = {}
            for k, v in parse_qs(parsed.query).items():
                query[k] = v[0] if len(v) == 1 else v

            req = {
                "method": self.command,
                "path": parsed.path,
                "headers": dict(self.headers),
                "body": body,
                "query": query,
            }

            try:
                # Try parsing body as JSON
                if body and self.headers.get('Content-Type', '').startswith('application/json'):
                    req["json"] = _json_mod.loads(body)
            except Exception:
                pass

            try:
                if hasattr(_server_handler, '_interpreter') and _server_handler._interpreter is not None:
                    response = _server_handler._interpreter._invoke_callable(_server_handler, [req], getattr(_server_handler, 'name', '<handler>'))
                elif callable(_server_handler):
                    response = _server_handler(req)
                else:
                    response = {"status": 500, "body": "Invalid handler"}
            except Exception as e:
                response = {"status": 500, "body": f"Server error: {e}"}

            if not isinstance(response, dict):
                response = {"status": 200, "body": str(response)}

            status = int(response.get("status", 200))
            resp_body = response.get("body", "")
            resp_headers = response.get("headers", {})

            self.send_response(status)
            content_type = resp_headers.get("Content-Type", "application/json")
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            for k, v in resp_headers.items():
                if k != "Content-Type":
                    self.send_header(k, v)
            self.end_headers()

            if isinstance(resp_body, (dict, list)):
                self.wfile.write(_json_mod.dumps(resp_body).encode('utf-8'))
            else:
                self.wfile.write(str(resp_body).encode('utf-8'))

        def do_GET(self):
            self._handle()

        def do_POST(self):
            self._handle()

        def do_PUT(self):
            self._handle()

        def do_DELETE(self):
            self._handle()

        def do_PATCH(self):
            self._handle()

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()

        def log_message(self, fmt, *args):
            print(f"  {self.command} {self.path} → {args[1] if len(args) > 1 else '?'}")

    server = http.server.HTTPServer(("0.0.0.0", int(port)), MOLHandler)
    _active_server = server
    print(f"🚀 MOL server running on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()
    return None


def _builtin_json_parse(text):
    """Parse a JSON string into a MOL value."""
    import json as _j
    return _j.loads(text)


def _builtin_json_stringify(value):
    """Convert a MOL value to a JSON string."""
    import json as _j

    def _convert(v):
        if v is None:
            return None
        if isinstance(v, (int, float, str, bool)):
            return v
        if isinstance(v, list):
            return [_convert(i) for i in v]
        if isinstance(v, dict):
            return {str(k): _convert(val) for k, val in v.items()}
        if hasattr(v, '_fields'):
            return {k: _convert(val) for k, val in v._fields.items()}
        return str(v)

    return _j.dumps(_convert(value))


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
    "chars": _builtin_chars,
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

    # Convenience aliases & extras (v1.1.0)
    "where": _builtin_where,
    "select": _builtin_select,
    "reject": _builtin_reject,
    "pluck": _builtin_pluck,
    "each": _builtin_each,
    "compact": _builtin_compact,
    "first": _builtin_first,
    "last": _builtin_last,
    "sum_list": _builtin_sum_list,
    "min_list": _builtin_min_list,
    "max_list": _builtin_max_list,
    "contains": _builtin_contains,

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

    # Error handling
    "panic": _builtin_panic,
    # Concurrency (v0.7.0)
    "channel": _builtin_channel,
    "send": _builtin_send,
    "receive": _builtin_receive,
    "sleep": _builtin_sleep,
    "parallel": _builtin_parallel,
    "race": _builtin_race,
    "wait_all": _builtin_wait_all,
    "task_done": _builtin_task_done,

    # File I/O (v0.8.0)
    "read_file": _builtin_read_file,
    "write_file": _builtin_write_file,
    "append_file": _builtin_append_file,
    "file_exists": _builtin_file_exists,
    "list_dir": _builtin_list_dir,
    "delete_file": _builtin_delete_file,
    "make_dir": _builtin_make_dir,
    "file_size": _builtin_file_size,
    "path_join": _builtin_path_join,
    "path_dir": _builtin_path_dir,
    "path_base": _builtin_path_base,
    "path_ext": _builtin_path_ext,

    # HTTP (v0.8.0)
    "fetch": _builtin_fetch,
    "url_encode": _builtin_url_encode,

    # HTTP Server + JSON (v0.9.0)
    "serve": _builtin_serve,
    "json_parse": _builtin_json_parse,
    "json_stringify": _builtin_json_stringify,

    # ── Vector Engine (v2.0.0) ────────────────────────────────
    "vec": create_vector,
    "vec_zeros": vec_zeros,
    "vec_ones": vec_ones,
    "vec_rand": vec_rand,
    "vec_from_text": vec_from_text,
    "vec_dot": vec_dot,
    "vec_cosine": vec_cosine,
    "vec_distance": vec_distance,
    "vec_normalize": vec_normalize,
    "vec_add": vec_add,
    "vec_sub": vec_sub,
    "vec_scale": vec_scale,
    "vec_dim": vec_dim,
    "vec_concat": vec_concat,
    "vec_batch_cosine": vec_batch_cosine,
    "vec_top_k": vec_top_k,
    "vec_quantize": vec_quantize,
    "vec_softmax": vec_softmax,
    "vec_relu": vec_relu,
    "vec_index": create_vector_index,
    "vec_index_add": vec_index_add,
    "vec_index_search": vec_index_search,

    # ── Encryption Engine (v2.0.0) ────────────────────────────
    "crypto_keygen": _builtin_crypto_keygen,
    "he_encrypt": _builtin_he_encrypt,
    "he_decrypt": _builtin_he_decrypt,
    "he_add": _builtin_he_add,
    "he_sub": _builtin_he_sub,
    "he_mul_scalar": _builtin_he_mul_scalar,
    "sym_keygen": _builtin_sym_keygen,
    "sym_encrypt": _builtin_sym_encrypt,
    "sym_decrypt": _builtin_sym_decrypt,
    "zk_commit": _builtin_zk_commit,
    "zk_verify": _builtin_zk_verify,
    "zk_prove": _builtin_zk_prove,
    "secure_hash": _builtin_secure_hash,
    "secure_random": _builtin_secure_random,
    "constant_time_compare": _builtin_constant_time_compare,

    # ── JIT Tracer (v2.0.0) ──────────────────────────────────
    "jit_stats": _builtin_jit_stats,
    "jit_hot_paths": _builtin_jit_hot_paths,
    "jit_profile": _builtin_jit_profile,
    "jit_reset": _builtin_jit_reset,
    "jit_warmup": _builtin_jit_warmup,
    "jit_enabled": _builtin_jit_enabled,
    "jit_toggle": _builtin_jit_toggle,

    # ── Swarm Runtime (v2.0.0) ────────────────────────────────
    "swarm_init": _builtin_swarm_init,
    "swarm_shard": _builtin_swarm_shard,
    "swarm_map": _builtin_swarm_map,
    "swarm_reduce": _builtin_swarm_reduce,
    "swarm_gather": _builtin_swarm_gather,
    "swarm_broadcast": _builtin_swarm_broadcast,
    "swarm_health": _builtin_swarm_health,
    "swarm_nodes": _builtin_swarm_nodes,
    "swarm_rebalance": _builtin_swarm_rebalance,
    "swarm_add_node": _builtin_swarm_add_node,
    "swarm_remove_node": _builtin_swarm_remove_node,
    "swarm_scatter": _builtin_swarm_scatter,
}
