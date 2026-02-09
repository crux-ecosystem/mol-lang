"""
MOL Standard Library
=====================

Built-in functions available to every MOL program.
Includes general utilities and IntraMind-specific functions.
"""

import time
import math
import json
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


def _create_document(source="", content=""):
    return Document(source=str(source), content=str(content))


def _create_embedding(text="", model="mol-sim-v1"):
    return Embedding(text=str(text), model=str(model))


def _create_chunk(content="", index=0, source=""):
    return Chunk(content=str(content), index=int(index), source=str(source))


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
}
